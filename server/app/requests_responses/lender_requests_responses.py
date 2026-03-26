from pydantic import BaseModel
from typing import Optional, List

class CreateBorrowerRequest(BaseModel):
    full_name: str
    email: str
    zip_code: str

class CreateBorrowerResponse(BaseModel):
    borrower_id: str

class GenerateLinkRequest(BaseModel):
    borrower_id: str

class GenerateLinkResponse(BaseModel):
    link_token: str
    expires_at: str

class VerifyZipRequest(BaseModel):
    link_token: str
    zip_code: str

class VerifyZipResponse(BaseModel):
    valid: bool
    borrower_name: Optional[str] = None
    message: str

class BorrowerSummary(BaseModel):
    borrower_id: str
    full_name: str
    email: str
    status: str
    created_at: str

class GetBorrowersResponse(BaseModel):
    borrowers: List[BorrowerSummary]

class DashboardStatsResponse(BaseModel):
    total_borrowers: int
    needs_link_creation: int
    link_created: int
    docs_submitted: int
    completed: int