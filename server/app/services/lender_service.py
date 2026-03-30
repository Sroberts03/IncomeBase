import logging
import secrets
from datetime import datetime, timezone, timedelta
from app.requests_responses.lender_requests_responses import (
    CreateBorrowerRequest, 
    CreateBorrowerResponse,
    GenerateLinkRequest,
    GenerateLinkResponse,
    GetBorrowerResponse,
    VerifyZipRequest,
    VerifyZipResponse,
    DashboardStatsResponse,
    GetBorrowersResponse,
    GetBorrowersResponse,
    BorrowerSummary,
    GetLenderInfoResponse,
    SendEmailRequest,
    SendEmailResponse
)
import resend
import os

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

    async def generate_borrower_link(self, current_user_id: str, request: GenerateLinkRequest) -> GenerateLinkResponse:
        """Generates a unique, expiring link for a borrower."""
        # Security Check
        is_owner = await self.lender_dao.check_borrower_ownership(request.borrower_id, current_user_id)
        if not is_owner:
            raise Exception("Unauthorized: This borrower record does not belong to you.")

        link_token = secrets.token_urlsafe(32)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

        await self.lender_dao.create_file_link(request.borrower_id, link_token, expires_at)
        await self.lender_dao.update_borrower_status(request.borrower_id, "Link Created")

        return GenerateLinkResponse(link_token=link_token, expires_at=expires_at)

    async def verify_borrower_zip(self, request: VerifyZipRequest) -> VerifyZipResponse:
        """Verifies a zip code against a link token to grant document upload access."""
        borrower_data = await self.lender_dao.get_borrower_by_link_token(request.link_token)
        
        if not borrower_data:
            return VerifyZipResponse(valid=False, message="Invalid or expired link.")

        # In Supabase/PostgREST, nested joins return a dict
        borrower_info = borrower_data.get("borrowers")
        if not borrower_info or borrower_info.get("zip_code") != request.zip_code:
            logger.warning(f"Zip verification failed for token {request.link_token[:8]}")
            return VerifyZipResponse(valid=False, message="Verification failed. Please check your zip code.")

        return VerifyZipResponse(
            valid=True, 
            borrower_name=borrower_info.get("full_name"),
            message="Verification successful."
        )

    async def get_dashboard_data(self, current_user_id: str) -> DashboardStatsResponse:
        """Fetches aggregated statistics for the lender's dashboard."""
        org_id = await self.lender_dao.get_org_id_for_lender(current_user_id)
        if not org_id:
            raise Exception("Lender is not associated with an organization.")
        
        stats_dict = await self.lender_dao.get_dashboard_stats(org_id)
        return DashboardStatsResponse(**stats_dict)

    async def get_borrowers(self, current_user_id: str) -> GetBorrowersResponse:
        """Fetches a list of all borrowers for the lender's organization."""
        org_id = await self.lender_dao.get_org_id_for_lender(current_user_id)
        if not org_id:
            raise Exception("Lender is not associated with an organization.")

        borrowers_list = await self.lender_dao.get_borrowers_for_org(org_id)
        summaries = [BorrowerSummary(**b) for b in borrowers_list]
        return GetBorrowersResponse(borrowers=summaries)
    
    async def get_borrower_details(self, current_user_id: str, borrower_id: str) -> GetBorrowerResponse:
        """Fetches detailed information for a specific borrower."""
        # Security Check
        is_owner = await self.lender_dao.check_borrower_ownership(borrower_id, current_user_id)
        if not is_owner:
            raise Exception("Unauthorized: This borrower record does not belong to you.")

        borrower_details = await self.lender_dao.get_borrower_details(borrower_id)
        if not borrower_details:
            raise Exception("Borrower not found.")
        
        doc_link_data = await self.lender_dao.get_active_document_link(borrower_id)
        if isinstance(doc_link_data, dict):
            borrower_details["document_link"] = doc_link_data.get("link_token")
        else:
            borrower_details["document_link"] = doc_link_data
        
        analysis_details = await self.lender_dao.get_borrower_analysis(borrower_id)
        borrower_details["analysis"] = analysis_details 

        return GetBorrowerResponse(**borrower_details)

    async def get_lender_info(self, current_user_id: str) -> GetLenderInfoResponse:
        """Fetches the lender's role and organization name."""
        info = await self.lender_dao.get_lender_info(current_user_id)
        if not info:
            return GetLenderInfoResponse(role="", organization="")
        
        role = info.get("role", "")
        orgs = info.get("organizations", {})
        
        if isinstance(orgs, list):
            org_name = orgs[0].get("org_name", "") if len(orgs) > 0 else ""
        elif isinstance(orgs, dict):
            org_name = orgs.get("org_name", "")
        else:
            org_name = ""
            
        return GetLenderInfoResponse(role=role, organization=org_name)

    async def send_email(self, current_user_id: str, request: SendEmailRequest) -> SendEmailResponse:
        # Security Check
        is_owner = await self.lender_dao.check_borrower_ownership(request.borrower_id, current_user_id)
        if not is_owner:
            raise Exception("Unauthorized: This borrower record does not belong to you.")
        
        borrower_details = await self.lender_dao.get_borrower_details(request.borrower_id)
        if not borrower_details or not borrower_details.get("email"):
            raise Exception("Borrower email not found.")

        # Note: By default resend enforces testing domain use for free accounts
        # "onboarding@resend.dev" can only send to the signup email.
        try:
            resend.api_key = os.getenv("RESEND_API_KEY")
            r = resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": borrower_details["email"],
                "subject": request.subject,
                "html": request.html_content
            })
            logger.info(f"Email sent successfully to {borrower_details['email']}")
            return SendEmailResponse(success=True, message="Email sent successfully")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}", exc_info=True)
            raise Exception("Failed to send email.")