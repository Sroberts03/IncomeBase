from fastapi import APIRouter, Depends
from app.requests_responses.file_requests_responses import UploadFileRequest
from app.handlers.file_handlers import FileHandler
from app.core.container import container

router = APIRouter(
    prefix="/file",
    tags=["File Upload"]
)

# 1. This helper function tells FastAPI how to create the handler
def get_file_handler() -> FileHandler:
    return container.file_handler

@router.post("/upload")
async def upload_file(
    request: UploadFileRequest, 
    handler: FileHandler = Depends(get_file_handler)
):
    """
    Triggers the document review and classification pipeline for a borrower.
    """
    return await handler.handle_upload_file(request)