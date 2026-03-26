from fastapi import APIRouter, Depends
from app.requests_responses.file_requests_responses import AnalyzeFilesRequest, SubmitFilesRequest
from app.handlers.file_handlers import FileHandler
from app.core.container import container

router = APIRouter(
    prefix="/file",
    tags=["File Upload"]
)

# 1. This helper function tells FastAPI how to create the handler
def get_file_handler() -> FileHandler:
    return container.file_handler

@router.post("/submit_files")
async def submit_files(
    request: SubmitFilesRequest, 
    handler: FileHandler = Depends(get_file_handler)
):
    """
    Triggers the document review and classification pipeline for a borrower.
    """
    return await handler.handle_submit_files(request)

@router.post("/analyze_files")
async def analyze_files(
    request: AnalyzeFilesRequest, 
    handler: FileHandler = Depends(get_file_handler)
):
    """
    Endpoint to trigger analysis of already classified files. This is separate from submit_files because analysis can be a longer-running process that we might want to trigger independently.
    """
    return await handler.handle_analyze_files(request)

