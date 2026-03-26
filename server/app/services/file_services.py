import base64
from models.file_review_schema import BatchFileReview

class FileService:
    def __init__(self, file_dao, file_review_agent, classifier_agent):
        self.file_dao = file_dao
        self.file_review_agent = file_review_agent
        self.classifier_agent = classifier_agent

    async def upload_files(self, file_paths: list[str]) -> BatchFileReview:
        # 1. Get raw bytes from Supabase via DAO
        files_bytes = await self.file_dao.get_files(file_paths)
        
        # 2. Convert raw bytes to base64 strings
        base64_files = []
        for content in files_bytes:
            # We don't need 'open()', content is already the bytes!
            encoded = base64.b64encode(content).decode("utf-8")
            base64_files.append(encoded)
            
        # 3. Pass to the Agent
        review_result = await self.file_review_agent.review(base64_files)
        return review_result