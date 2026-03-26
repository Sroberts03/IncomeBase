from app.requests_responses.file_requests_responses import AnalyzeFilesRequest, SubmitFilesRequest
from models.file_review_schema import BatchFileReview


class FileHandler:
    def __init__(self, file_service):
        self.file_service = file_service

    async def handle_submit_files(self, request: SubmitFilesRequest) -> BatchFileReview:
        return await self.file_service.submit_files(request.link_token)
    
    async def handle_analyze_files(self, request: AnalyzeFilesRequest):
        return await self.file_service.analyze_files(request.borrower_id)
