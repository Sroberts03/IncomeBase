import base64
from models.file_review_schema import BatchFileReview

class FileService:
    def __init__(self, file_dao, file_review_agent, classifier_agent):
        self.file_dao = file_dao
        self.file_review_agent = file_review_agent
        self.classifier_agent = classifier_agent

    async def batch_process_files(self, link_token: str) -> BatchFileReview:
        borrower_id = await self.file_dao.get_borrower_id_from_link_token(link_token)
        pending_records = await self.file_dao.get_pending_records(borrower_id)
        
        if not pending_records:
            return BatchFileReview(results=[], overall_summary="No pending files.")

        files = await self.file_dao.get_files([r["file_path"] for r in pending_records])
        files_base64 = [base64.b64encode(f).decode("utf-8") for f in files]
        
        review = await self.file_review_agent.review(files_base64)
        
        # Filter and Process
        for file_review in review.results:
            if file_review.status == "approved":
                idx = file_review.file_index
                file_id = pending_records[idx]["id"]
                
                target_b64 = files_base64[idx]
                
                classification = await self.classifier_agent.classify(target_b64)
                
                await self.file_dao.update_file_classification(borrower_id, classification, file_id)
                
        return review