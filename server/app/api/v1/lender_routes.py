from fastapi import APIRouter, Depends
from app.requests_responses.file_requests_responses import AnalyzeFilesRequest, SubmitFilesRequest
from app.handlers.file_handlers import FileHandler
from app.core.container import container
from app.handlers.lender_handler import LenderHandler
from app.requests_responses.lender_requests_responses import CreateBorrowerRequest, CreateBorrowerResponse
from app.core.get_current_user_id import get_current_user_id

router = APIRouter(
    prefix="/lender",
    tags=["Lender Management"]
)

# 1. This helper function tells FastAPI how to create the handler
def get_lender_handler() -> LenderHandler:
    return container.lender_handler

@router.post("/create-borrower", response_model=CreateBorrowerResponse)
async def create_borrower(
    create_borrower_request: CreateBorrowerRequest,
    current_user_id: str = Depends(get_current_user_id),  
    handler: LenderHandler = Depends(get_lender_handler)
) -> CreateBorrowerResponse:
    return await handler.create_borrower(current_user_id, create_borrower_request)