from app.requests_responses.lender_requests_responses import (
    CreateBorrowerRequest, 
    CreateBorrowerResponse,
    DashboardStatsResponse,
    GenerateLinkRequest,
    GenerateLinkResponse,
    GetBorrowersResponse,
    VerifyZipRequest,
    VerifyZipResponse
)


class LenderHandler:
    def __init__(self, lender_service):
        self.lender_service = lender_service

    async def create_borrower(self, current_user_id: str, create_borrower_request: CreateBorrowerRequest) -> CreateBorrowerResponse:
        return await self.lender_service.create_borrower(current_user_id, create_borrower_request)

    async def generate_link(self, current_user_id: str, request: GenerateLinkRequest) -> GenerateLinkResponse:
        return await self.lender_service.generate_borrower_link(current_user_id, request)

    async def verify_borrower_zip(self, request: VerifyZipRequest) -> VerifyZipResponse:
        return await self.lender_service.verify_borrower_zip(request)

    async def get_dashboard_stats(self, current_user_id: str) -> DashboardStatsResponse:
        return await self.lender_service.get_dashboard_data(current_user_id)

    async def get_borrowers(self, current_user_id: str) -> GetBorrowersResponse:
        return await self.lender_service.get_borrowers(current_user_id)
    
    async def get_borrower_details(self, current_user_id: str, borrower_id: str) -> GetBorrowersResponse:
        return await self.lender_service.get_borrower_details(current_user_id, borrower_id)