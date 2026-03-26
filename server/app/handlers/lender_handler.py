from app.requests_responses.lender_requests_responses import CreateBorrowerRequest, CreateBorrowerResponse


class LenderHandler:
    def __init__(self, lender_service):
        self.lender_service = lender_service

    async def create_borrower(self, current_user_id: str, create_borrower_request: CreateBorrowerRequest) -> CreateBorrowerResponse:
        return await self.lender_service.create_borrower(current_user_id, create_borrower_request)