import logging
from datetime import datetime, timezone
from app.requests_responses.lender_requests_responses import CreateBorrowerRequest, CreateBorrowerResponse

logger = logging.getLogger(__name__)

class LenderService:
    def __init__(self, lender_dao):
        self.lender_dao = lender_dao

    async def create_borrower(self, current_user_id: str, create_borrower_request: CreateBorrowerRequest) -> CreateBorrowerResponse:
        logger.info(f"Lender {current_user_id} attempting to create borrower for email: {create_borrower_request.email}")
        try:
            # 1. Look up Organization (Authorization Check)
            org_id = await self.lender_dao.get_org_id_for_lender(current_user_id)
            if not org_id:
                logger.warning(f"Unauthorized: Lender {current_user_id} has no associated organization.")
                raise Exception("Lender is not authorized to create borrowers.")

            # 2. Create Borrower
            status = "Needs Link Creation"
            now_iso = datetime.now(timezone.utc).isoformat()
            
            borrower_id = await self.lender_dao.create_borrower(
                lender_id=current_user_id,
                email=create_borrower_request.email,
                full_name=create_borrower_request.full_name,
                zip_code=create_borrower_request.zip_code,
                org_id=org_id,
                status=status,
                created_at=now_iso,
                updated_at=now_iso
            )
            
            logger.info(f"Successfully created borrower {borrower_id} for org {org_id}")
            return CreateBorrowerResponse(borrower_id=borrower_id)

        except Exception as e:
            logger.error(f"Failed to create borrower: {str(e)}", exc_info=True)
            if "authorized" in str(e).lower():
                raise
            raise Exception("Failed to create borrower due to an internal error.")
        