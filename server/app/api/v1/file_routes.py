from fastapi import APIRouter, Depends
from app.requests_responses.file_requests_responses import BatchProcessRequest
from app.handlers.file_handlers import FileHandler
from app.core.container import container

router = APIRouter(
    prefix="/file",
    tags=["File Upload"]
)

# 1. This helper function tells FastAPI how to create the handler
def get_file_handler() -> FileHandler:
    return container.file_handler

@router.post("/batch-process")
async def batch_process(
    request: BatchProcessRequest, 
    handler: FileHandler = Depends(get_file_handler)
):
    """
    Triggers the document review and classification pipeline for a borrower.
    """
    return await handler.handle_batch_process(request)