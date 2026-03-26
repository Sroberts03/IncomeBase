from fastapi import APIRouter, Depends
from app.requests_responses.file_requests_responses import AnalyzeFilesRequest, SubmitFilesRequest
from app.handlers.file_handlers import FileHandler
from app.core.container import container
from app.handlers.lender_handler import LenderHandler
from app.requests_responses.lender_requests_responses import (
    CreateBorrowerRequest, 
    CreateBorrowerResponse,
    GenerateLinkRequest,
    GenerateLinkResponse,
    VerifyZipRequest,
    VerifyZipResponse,
    DashboardStatsResponse,
    GetBorrowersResponse
)
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

@router.post("/generate-link", response_model=GenerateLinkResponse)
async def generate_link(
    request: GenerateLinkRequest,
    current_user_id: str = Depends(get_current_user_id),
    handler: LenderHandler = Depends(get_lender_handler)
) -> GenerateLinkResponse:
    return await handler.generate_link(current_user_id, request)

@router.post("/verify-zip", response_model=VerifyZipResponse)
async def verify_zip(
    request: VerifyZipRequest,
    handler: LenderHandler = Depends(get_lender_handler)
) -> VerifyZipResponse:
    """Public endpoint for borrowers to verify their identity via zip code."""
    return await handler.verify_borrower_zip(request)

@router.get("/dashboard-stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user_id: str = Depends(get_current_user_id),
    handler: LenderHandler = Depends(get_lender_handler)
) -> DashboardStatsResponse:
    return await handler.get_dashboard_stats(current_user_id)

@router.get("/borrowers", response_model=GetBorrowersResponse)
async def get_borrowers(
    current_user_id: str = Depends(get_current_user_id),
    handler: LenderHandler = Depends(get_lender_handler)
) -> GetBorrowersResponse:
    return await handler.get_borrowers(current_user_id)