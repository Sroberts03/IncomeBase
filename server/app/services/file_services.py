import asyncio
import base64
import logging
import openai  # <--- Required for catching the RateLimitError
from typing import Dict, Any, List
from fastapi import BackgroundTasks
from models.file_review_schema import BatchFileReview
from models.extraction_schema import IndividualFileExtraction
from app.requests_responses.file_requests_responses import SubmitFilesRequest

# Configure logging
logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, file_dao, file_review_agent, 
                 classifier_agent, extractor_agent, 
                 analyzer_agent, review_agent, 
                 parser, data_preparer, lender_dao, lender_service=None):
        self.file_dao = file_dao
        self.file_review_agent = file_review_agent
        self.classifier_agent = classifier_agent
        self.extractor_agent = extractor_agent
        self.analyzer_agent = analyzer_agent
        self.review_agent = review_agent
        self.parser = parser
        self.data_preparer = data_preparer
        self.lender_dao = lender_dao
        self.lender_service = lender_service

    async def submit_files(self, request: SubmitFilesRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
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
        
        pending_records = await self.file_dao.get_pending_records(request.link_token)
        print(f"Found {len(pending_records)} pending files: {pending_records}.")
        
        if not pending_records:
            logger.info(f"No pending files found for borrower {borrower_id}.")
            return {
                "status": "success",
                "message": "No pending files.",
                "review_results": [],
                "stats": {
                    "total_received": 0,
                    "approved": 0,
                    "rejected": 0,
                    "classification_status": "none"
                },
                "overall_summary": ""
            }

        try:
            files = await self.file_dao.get_files([r["file_path"] for r in pending_records])
            files_base64 = [base64.b64encode(f).decode("utf-8") for f in files]
            
            # 1. BATCHED REVIEW LOOP (Protects OpenAI limits)
            BATCH_SIZE = 2  # Reduced to prevent TPM spikes
            all_review_results = []
            overall_summaries = []
            
            for i in range(0, len(files_base64), BATCH_SIZE):
                batch_files = files_base64[i : i + BATCH_SIZE]
                batch_records = pending_records[i : i + BATCH_SIZE]
                batch_ids = [r["id"] for r in batch_records]
                
                # RETRY LOGIC FOR RATE LIMITS
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # Process the chunk
                        batch_review = await self.file_review_agent.review(batch_files, batch_ids)
                        all_review_results.extend(batch_review.results)
                        
                        # Log reasoning for each reviewed file
                        for result in batch_review.results:
                            asyncio.ensure_future(self.file_dao.log_reasoning(
                                borrower_id=borrower_id,
                                agent="file_review",
                                raw_reasoning=result.reasoning,
                                file_id=result.file_id,
                            ))
                        
                        if hasattr(batch_review, 'overall_summary') and batch_review.overall_summary:
                            overall_summaries.append(batch_review.overall_summary)
                            
                        break  # Break out of the retry loop on success
                        
                    except openai.RateLimitError as e:
                        if attempt == max_retries - 1:
                            logger.error("Max retries reached. OpenAI rate limit is still blocking.")
                            raise e
                        
                        wait_time = 4 ** attempt # Waits 1s, then 4s, then 16s
                        logger.warning(f"Rate limit hit during review! Sleeping for {wait_time}s before retrying...")
                        await asyncio.sleep(wait_time)
                
                # Standard pause between successful chunks
                if i + BATCH_SIZE < len(files_base64):
                    await asyncio.sleep(3) 

            print(f"Completed review for all files. Results: {all_review_results}")
            
        except Exception as e:
            logger.error(f"Error during file review: {str(e)}")
            raise Exception("Failed to process file review. Please try again later.")
            
        # Add file_name to each result so the client knows which file is which
        for result in all_review_results:
            matched_record = next((r for r in pending_records if r["id"] == result.file_id), None)
            if matched_record:
                path = matched_record.get("file_path", "")
                result.file_name = path.split('/')[-1] if '/' in path else path

        # Filter and Process Rejections
        unapproved_files = [r for r in all_review_results if r.status == "rejected"]
        if unapproved_files:
            file_paths = []            
            for record in pending_records:
                if record["id"] in [f.file_id for f in unapproved_files]:
                    file_paths.append(record["file_path"])
                    
            logger.info(f"{len(unapproved_files)} files were rejected during review for borrower {borrower_id}.")
            await self.file_dao.remove_files(
                file_ids=[r.file_id for r in unapproved_files],
                file_paths=file_paths
            )
            print(f"Removed unapproved files: {file_paths}")
            
        # Filter Approved
        approved_results = [r for r in all_review_results if r.status == "approved"]
        approved_ids = [r.file_id for r in approved_results]
        
        files_to_classify = []
        file_ids_to_classify = []
        for i, record in enumerate(pending_records):
            if record["id"] in approved_ids:
                files_to_classify.append(files_base64[i])
                file_ids_to_classify.append(record["id"])

        # 2. TRIGGER BACKGROUND CLASSIFICATION
        if files_to_classify:
            background_tasks.add_task(
                self._background_classify_files,
                borrower_id=borrower_id,
                files_base64=files_to_classify,
                file_ids=file_ids_to_classify
            )

        await self.lender_dao.update_borrower_status(borrower_id, "Docs Submitted")     
        
        # 3. NOTIFY LENDER
        if self.lender_service:
            background_tasks.add_task(
                self.lender_service.notify_lender_docs_submitted,
                borrower_id=borrower_id
            )
        
        return {
            "status": "success",
            "review_results": all_review_results,
            "stats": {
                "total_received": len(pending_records),
                "approved": len(approved_ids),
                "rejected": len(pending_records) - len(approved_ids),
                "classification_status": "processing_in_background" 
            },
            "overall_summary": " ".join(overall_summaries) 
        }

    async def _background_classify_files(self, borrower_id: str, files_base64: list, file_ids: list):
        """
        Background worker that processes approved files in batches to respect rate limits.
        """
        BATCH_SIZE = 2 # Reduced for rate limiting
        classified_count = 0
        logger.info(f"Starting background classification for borrower {borrower_id}. Total files: {len(files_base64)}")
        
        try:
            for i in range(0, len(files_base64), BATCH_SIZE):
                batch_files = files_base64[i : i + BATCH_SIZE]
                batch_ids = file_ids[i : i + BATCH_SIZE]
                
                # RETRY LOGIC FOR RATE LIMITS
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        classification_results = await self.classifier_agent.classify(batch_files, batch_ids)
                        
                        for classification in classification_results.files:
                            await self.file_dao.update_file_classification(
                                borrower_id, 
                                classification, 
                                classification.file_id
                            )
                            classified_count += 1
                        break # Break out on success
                        
                    except openai.RateLimitError as e:
                        if attempt == max_retries - 1:
                            logger.error("Max retries reached during classification. OpenAI rate limit blocking.")
                            raise e
                        
                        wait_time = 4 ** attempt
                        logger.warning(f"Rate limit hit during classification! Sleeping for {wait_time}s...")
                        await asyncio.sleep(wait_time)
                
                # Standard pause between chunks
                if i + BATCH_SIZE < len(files_base64):
                    await asyncio.sleep(3)
                    
            logger.info(f"Successfully classified {classified_count} files for borrower {borrower_id}.")
            
        except Exception as e:
            logger.error(f"Background classification failed for borrower {borrower_id}: {str(e)}")
    
    async def analyze_files(self, borrower_id: str, lender_id: str) -> dict:
        """
        Public trigger for the analysis pipeline. 
        """
        logger.info(f"Analysis trigger received for borrower: {borrower_id} from lender: {lender_id}")
        
        # 1. Security Check (Ownership Verification)
        is_owner = await self.lender_dao.check_borrower_ownership(borrower_id, lender_id)
        if not is_owner:
            logger.warning(f"Security Alert: Lender {lender_id} tried to analyze unauthorized borrower {borrower_id}")
            raise Exception("Unauthorized: This borrower does not belong to you.")

        # 2. Update status to 'Analyzing' to inform the UI
        await self.lender_dao.update_borrower_status(borrower_id, "Analyzing")

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
            chunk_size = 2 # Process 2 Vision requests at a time to be safe
            
            for i in range(0, len(extraction_tasks), chunk_size):
                chunk = extraction_tasks[i : i + chunk_size]
                logger.info(f"Processing chunk {i//chunk_size + 1} for {borrower_id}...")
                
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # Run the current batch
                        results = await asyncio.gather(*chunk)
                        extraction_results.extend(results)
                        break
                    except openai.RateLimitError as e:
                        if attempt == max_retries - 1:
                            logger.error("Extraction rate limit blocked.")
                            raise e
                        wait_time = 4 ** attempt
                        logger.warning(f"Extraction Rate Limit Hit! Sleeping {wait_time}s...")
                        await asyncio.sleep(wait_time)
                
                # Pause to let OpenAI TPM (Tokens Per Minute) bucket refill
                if i + chunk_size < len(extraction_tasks):
                    await asyncio.sleep(4) 
            
            # 5. Log extraction reasoning, then save to database
            for result in extraction_results:
                asyncio.ensure_future(self.file_dao.log_reasoning(
                    borrower_id=borrower_id,
                    agent="extractor",
                    raw_reasoning=result.reasoning,
                    file_id=result.file_id,
                ))
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
                print(f"Prepared data for analysis: {prepared_data}")
                
                final_report = await self.analyzer_agent.analyze(prepared_data, corrections)
                asyncio.ensure_future(self.file_dao.log_reasoning(
                    borrower_id=borrower_id,
                    agent="analyzer",
                    raw_reasoning=final_report.analysis_summary,
                    file_id=None,
                ))
                
                # Second agent reviews the first agent's work
                review_results = await self.review_agent.review_analysis(
                    prepared_data, 
                    final_report.model_dump_json()
                )
                asyncio.ensure_future(self.file_dao.log_reasoning(
                    borrower_id=borrower_id,
                    agent="reasoning_review",
                    raw_reasoning=review_results.auditor_notes,
                    file_id=None,
                ))
                print(f"Review results: {review_results}")
                analysis_approved = review_results.is_approved
                if not analysis_approved:
                    logger.info(f"Review failed for {borrower_id} (Attempt {retries}). Feedback: {review_results.corrections}")
                    print(f"Review failed for {borrower_id} (Attempt {retries}). Feedback: {review_results.corrections}")
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
        is_owner = await self.lender_dao.check_borrower_ownership(borrower_id, lender_id)
        if not is_owner:
            logger.warning(f"Security Alert: Lender {lender_id} tried to access files of unauthorized borrower {borrower_id}")
            raise Exception("Unauthorized: This borrower does not belong to you.")
        
        files = await self.file_dao.get_files_for_borrower(borrower_id)
        return {"files": files}