from app.requests_responses.file_requests_responses import BatchProcessRequest
from models.file_review_schema import BatchFileReview


class FileHandler:
    def __init__(self, file_service):
        self.file_service = file_service

    async def handle_batch_process(self, request: BatchProcessRequest) -> BatchFileReview:
        return await self.file_service.batch_process_files(request.link_token)
