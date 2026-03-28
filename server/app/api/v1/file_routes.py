from fastapi import APIRouter, Depends, BackgroundTasks
from app.requests_responses.file_requests_responses import (
    AnalyzeFilesRequest,
    GetFilesResponse, 
    SubmitFilesRequest, 
    SubmitFilesResponse,
    GenericMessageResponse
)
from app.handlers.file_handlers import FileHandler
from app.core.container import container
from app.core.get_current_user_id import get_current_user_id

router = APIRouter(
    prefix="/file",
    tags=["File Upload"]
)

# 1. This helper function tells FastAPI how to create the handler
def get_file_handler() -> FileHandler:
    return container.file_handler

@router.post("/submit-files", response_model=SubmitFilesResponse)
async def submit_files(
    request: SubmitFilesRequest, 
    background_tasks: BackgroundTasks,
    handler: FileHandler = Depends(get_file_handler),
):
    """
    Triggers the document review and classification pipeline for a borrower.
    """
    return await handler.handle_submit_files(request, background_tasks)

@router.post("/analyze-files", response_model=GenericMessageResponse)
async def analyze_files(
    request: AnalyzeFilesRequest,
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user_id),
    handler: FileHandler = Depends(get_file_handler)
):
    """
    Endpoint to trigger analysis of already classified files. 
    Returns immediately and runs the heavy LLM logic in the background.
    """
    return await handler.handle_analyze_files(request, current_user_id, background_tasks)

@router.get("/borrower/{borrower_id}/files", response_model=GetFilesResponse)
async def get_borrower_files(
    borrower_id: str,
    current_user_id: str = Depends(get_current_user_id),
    handler: FileHandler = Depends(get_file_handler)
):
    """
    Fetches the list of files associated with a borrower, along with their analysis status.
    """
    return await handler.get_files_for_borrower(borrower_id, current_user_id)

