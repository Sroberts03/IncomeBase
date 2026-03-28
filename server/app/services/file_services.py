import asyncio
import base64
import logging
from typing import Dict, Any, List
from models.file_review_schema import BatchFileReview
from models.extraction_schema import IndividualFileExtraction
from app.requests_responses.file_requests_responses import SubmitFilesRequest

# Configure logging
logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, file_dao, file_review_agent, 
                 classifier_agent, extractor_agent, 
                 analyzer_agent, review_agent, 
                 parser, data_preparer, lender_dao):
        self.file_dao = file_dao
        self.file_review_agent = file_review_agent
        self.classifier_agent = classifier_agent
        self.extractor_agent = extractor_agent
        self.analyzer_agent = analyzer_agent
        self.review_agent = review_agent
        self.parser = parser
        self.data_preparer = data_preparer
        self.lender_dao = lender_dao

    async def submit_files(self, request: SubmitFilesRequest) -> Dict[str, Any]:
        """
        Submits files for review and then classification.
        Returns a detailed summary of the batch processing.
        """
        logger.info(f"Starting file submission for token: {request.link_token[:8]}...")

        borrower_data = await self.file_dao.get_borrower_data_from_link_token(request.link_token)

        borrower_id = borrower_data["borrower_id"]
        
        # Zip Code Verification (Final Security Check)
        if borrower_data["zip_code"] != request.zip_code:
            logger.warning(f"Security Alert: Zip verification failed during file submission for borrower {borrower_id}")
            raise Exception("Unauthorized: Zip code verification failed.")
        
        pending_records = await self.file_dao.get_pending_records(borrower_id)
        
        if not pending_records:
            return {
                "status": "success",
                "message": "No pending files.",
                "review_results": [],
                "stats": {
                    "total_received": 0,
                    "approved": 0,
                    "rejected": 0,
                    "successfully_classified": 0
                },
                "overall_summary": ""
            }

        try:
            files = await self.file_dao.get_files([r["file_path"] for r in pending_records])
            files_base64 = [base64.b64encode(f).decode("utf-8") for f in files]
            # 1. Batch Review
            review = await self.file_review_agent.review(files_base64, [r["id"] for r in pending_records])
        except Exception as e:
            logger.error(f"Error during file review: {str(e)}")
            raise Exception("Failed to process file review. Please try again later.")
        
        # Filter and Process
        approved_results = [r for r in review.results if r.status == "approved"]
        approved_ids = [r.file_id for r in approved_results]
        
        files_to_classify = []
        file_ids_to_classify = []
        for i, record in enumerate(pending_records):
            if record["id"] in approved_ids:
                files_to_classify.append(files_base64[i])
                file_ids_to_classify.append(record["id"])

        classified_count = 0
        if files_to_classify:
            try:
                classification_results = await self.classifier_agent.classify(files_to_classify, file_ids_to_classify)
                for classification in classification_results.files:
                    await self.file_dao.update_file_classification(
                        borrower_id, 
                        classification, 
                        classification.file_id
                    )
                    classified_count += 1
            except Exception as e:
                logger.warning(f"Classification failed but review succeeded: {str(e)}")
                # We don't raise here because the review results are still valuable to the UI

        await self.lender_dao.update_borrower_status(borrower_id, "Docs Submitted")     
        return {
            "status": "success",
            "review_results": review.results,
            "stats": {
                "total_received": len(pending_records),
                "approved": len(approved_ids),
                "rejected": len(pending_records) - len(approved_ids),
                "successfully_classified": classified_count
            },
            "overall_summary": review.overall_summary
        }
    
    async def analyze_files(self, borrower_id: str, lender_id: str) -> dict:
        """
        Public trigger for the analysis pipeline. 
        Perform security checks and then return quickly, letting the 
        background task do the heavy lifting.
        """
        logger.info(f"Analysis trigger received for borrower: {borrower_id} from lender: {lender_id}")
        
        # 1. Security Check (Ownership Verification)
        is_owner = await self.lender_dao.check_borrower_ownership(borrower_id, lender_id)
        if not is_owner:
            logger.warning(f"Security Alert: Lender {lender_id} tried to analyze unauthorized borrower {borrower_id}")
            raise Exception("Unauthorized: This borrower does not belong to you.")

        # 2. Update status to 'Analyzing' to inform the UI
        await self.lender_dao.update_borrower_status(borrower_id, "Analyzing")

        # Note: The caller (the route) will handle the BackgroundTask registration
        return {
            "status": "accepted",
            "message": "Analysis started in background. Monitor borrower status for completion.",
            "borrower_id": borrower_id,
            "approved": False,
        }

    async def run_analysis_pipeline(self, borrower_id: str):
        """
        The background worker that actually runs the LLM logic with 
        Rate Limit protection and Parser safety.
        """
        try:
            logger.info(f"Background analysis pipeline started for borrower: {borrower_id}")
            
            # 1. Fetch File Records
            processed_files = await self.file_dao.get_files_for_borrower(borrower_id)
            if not processed_files:
                logger.info(f"No files to analyze for {borrower_id}. Stopping pipeline.")
                await self.lender_dao.update_borrower_status(borrower_id, "No Files")
                return

            # 2. Download Binary Data
            file_paths = [f["file_path"] for f in processed_files]
            files = await self.file_dao.get_files(file_paths)
            
            # 3. Build Extraction Tasks (with Parser Guard)
            extraction_tasks = []
            for file_record, file_bytes in zip(processed_files, files):
                parsed = self.parser.parse(file_bytes, file_record["file_name"])   
                
                if not parsed:
                    logger.warning(f"Skipping {file_record['file_name']}: Parser returned None.")
                    continue

                # We create the coroutine but DON'T await it yet
            # ...existing code for extraction, analysis, etc...
            # At the end, set status to 'Completed'
            await self.lender_dao.update_borrower_status(borrower_id, "Completed")
            task = self.extractor_agent.extract_single_file(
                parsed, 
                file_id=file_record["id"], 
                file_name=file_record["file_name"]
            )
            extraction_tasks.append(task)

            if not extraction_tasks:
                logger.error(f"No valid files could be parsed for {borrower_id}.")
                await self.lender_dao.update_borrower_status(borrower_id, "Analysis Failed")
                return

            # 4. Execute Tasks in Chunks (Rate Limit Protection)
            extraction_results = []
            chunk_size = 3 # Process 3 Vision requests at a time
            
            for i in range(0, len(extraction_tasks), chunk_size):
                chunk = extraction_tasks[i : i + chunk_size]
                logger.info(f"Processing chunk {i//chunk_size + 1} for {borrower_id}...")
                
                # Run the current batch
                results = await asyncio.gather(*chunk)
                extraction_results.extend(results)
                
                # Pause to let OpenAI TPM (Tokens Per Minute) bucket refill
                if i + chunk_size < len(extraction_tasks):
                    await asyncio.sleep(4) 
            
            # 5. Save Extractions to Database
            await self.process_and_save_extractions(borrower_id, extraction_results)
            
            # 6. Prepare and Analyze (The Multi-Agent Review Loop)
            prepared_data = self.data_preparer.prepare_financial_context(extraction_results)
            
            analysis_approved = False
            corrections = None
            final_report = None
            retries = 0
            MAX_RETRIES = 3
            
            while not analysis_approved and retries < MAX_RETRIES:
                retries += 1
                logger.info(f"Attempting analysis for {borrower_id} (Attempt {retries})")
                
                final_report = await self.analyzer_agent.analyze(prepared_data, corrections)
                
                # Second agent reviews the first agent's work
                review_results = await self.review_agent.review_analysis(
                    prepared_data, 
                    final_report.model_dump_json()
                )
                
                analysis_approved = review_results.is_approved
                if not analysis_approved:
                    logger.info(f"Review failed for {borrower_id} (Attempt {retries}). Feedback: {review_results.corrections}")
                    corrections = review_results.corrections
                
            # 7. Finalize Status
            if final_report and analysis_approved:
                await self.file_dao.save_analysis_results(final_report.model_dump(), borrower_id)
                await self.lender_dao.update_borrower_status(borrower_id, "Analysis Completed")
                logger.info(f"Analysis completed successfully for {borrower_id}")
            else:
                await self.file_dao.save_analysis_results(final_report.model_dump(), borrower_id)
                await self.lender_dao.update_borrower_status(borrower_id, "Analysis Flagged For Review")
                logger.error(f"Analysis pipeline failed to reach approval after {retries} retries.")

        except Exception as e:
            logger.error(f"Critical failure in background pipeline for {borrower_id}: {str(e)}", exc_info=True)
            await self.lender_dao.update_borrower_status(borrower_id, "Analysis Failed")

    async def process_and_save_extractions(self, borrower_id: str, extraction_results: list[IndividualFileExtraction]):
        try:
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

            total_saved = await self.file_dao.bulk_insert_line_items(generate_db_records())
            return {"message": f"Successfully inserted {total_saved} line items."}
        except Exception as e:
            logger.error(f"Database error during bulk insert: {str(e)}")
            return {"error": str(e)}
        
    async def get_files_for_borrower(self, borrower_id: str, lender_id: str):
        """
        Fetches the list of files associated with a borrower, along with their analysis status.
        """
        # Security Check
        is_owner = await self.lender_dao.check_borrower_ownership(borrower_id, lender_id)
        if not is_owner:
            logger.warning(f"Security Alert: Lender {lender_id} tried to access files of unauthorized borrower {borrower_id}")
            raise Exception("Unauthorized: This borrower does not belong to you.")
        
        files = await self.file_dao.get_files_for_borrower(borrower_id)
        return {"files": files}