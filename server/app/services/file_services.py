import asyncio
import base64
from models.file_review_schema import BatchFileReview
from models.extraction_schema import IndividualFileExtraction

class FileService:
    def __init__(self, file_dao, file_review_agent, 
                 classifier_agent, extractor_agent, 
                 analyzer_agent, review_agent, 
                 parser, data_preparer):
        self.file_dao = file_dao
        self.file_review_agent = file_review_agent
        self.classifier_agent = classifier_agent
        self.extractor_agent = extractor_agent
        self.analyzer_agent = analyzer_agent
        self.review_agent = review_agent
        self.parser = parser
        self.data_preparer = data_preparer

    async def submit_files(self, link_token: str) -> BatchFileReview:
        borrower_id = await self.file_dao.get_borrower_id_from_link_token(link_token)
        pending_records = await self.file_dao.get_pending_records(borrower_id)
        
        if not pending_records:
            return BatchFileReview(results=[], overall_summary="No pending files.")

        files = await self.file_dao.get_files([r["file_path"] for r in pending_records])
        files_base64 = [base64.b64encode(f).decode("utf-8") for f in files]
        
        review = await self.file_review_agent.review(files_base64, [r["id"] for r in pending_records])
        
        # Filter and Process
        approved_ids ={
            result.file_id 
            for result in review.results 
            if result.status == "approved"
        }

        files_to_classify = []
        file_ids_to_classify = []
        for i, record in enumerate(pending_records):
            if record["id"] in approved_ids:
                files_to_classify.append(files_base64[i])
                file_ids_to_classify.append(record["id"])

        if files_to_classify:
            classification_results = await self.classifier_agent.classify(files_to_classify, file_ids_to_classify)
            for classification in classification_results.results:
                await self.file_dao.update_file_classification(
                    borrower_id, 
                    classification, 
                    classification.file_id
                )
                
        return review
    
    async def analyze_files(self, borrower_id: str) -> dict:
        # get all processed files records for borrower
        processed_files = await self.file_dao.get_files_for_borrower(borrower_id)
        if not processed_files:
            return {"message": "No processed files to analyze."}

        # download files from storage and convert to base64 for parser
        file_paths = [f["file_path"] for f in processed_files]
        files = await self.file_dao.get_files(file_paths)
        # parse files for extractor agent
        extraction_tasks = []
        for file_record, file_bytes in zip(processed_files, files):
            parsed = self.parser.parse(file_bytes)   
            # run extractor agent
            extraction_task = self.extractor_agent.extract_single_file(parsed, file_id=file_record["id"], file_name=file_record["file_name"])
            extraction_tasks.append(extraction_task)

        extraction_results = await asyncio.gather(*extraction_tasks)
        # save extraction results to database
        await self.process_and_save_extractions(borrower_id, extraction_results)
        # prepare data for analyzer agent
        prepared_data = self.data_preparer.prepare_financial_context(extraction_results)
        # analisis loop with review
        analysis_approved = False
        corrections = None
        final_report = None
        retries = 0
        MAX_RETRIES = 3
        while not analysis_approved and retries < MAX_RETRIES:
            retries += 1
            final_report = await self.analyzer_agent.analyze(prepared_data, corrections)
            # run review agent for final reasoning and insights
            review_results = await self.review_agent.review_analysis(prepared_data, final_report.model_dump_json())
            analysis_approved = review_results.is_approved
            if not analysis_approved:
                corrections = review_results.corrections
            else:
                corrections = None
        # save final analysis results to database
        await self.file_dao.save_analysis_results(final_report.model_dump(), borrower_id)
        return {
            "message": "Analysis complete", 
            "approved": analysis_approved,
            "retries": retries,
        }
    
    async def process_and_save_extractions(self, borrower_id: str, extraction_results: list[IndividualFileExtraction]):
        # 1. The Data Transformation (Generator)
        def generate_db_records():
            for result in extraction_results:
                for line_item in result.extracted_data.line_items:
                    yield {
                        "borrower_id": borrower_id,
                        "file_id": result.file_id,
                        "file_name": result.file_name,
                        "amount": line_item.amount,
                        "date": line_item.file_date.isoformat(),
                        "category": "income" if line_item.is_income else "expense",
                    }

        # 2. Pass the generator directly to the DAO
        # The DAO will consume the generator lazily, preserving your O(K) space complexity!
        total_saved = await self.file_dao.bulk_insert_line_items(generate_db_records())
        
        return {"message": f"Successfully inserted {total_saved} line items."}