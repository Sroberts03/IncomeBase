from app.requests_responses.file_requests_responses import UploadFileRequest
from models.file_review_schema import BatchFileReview


class FileHandler:
    def __init__(self, file_service):
        self.file_service = file_service

    async def handle_upload_file(self, request: UploadFileRequest) -> BatchFileReview:
        self.file_service.upload_files(request.file_paths)
