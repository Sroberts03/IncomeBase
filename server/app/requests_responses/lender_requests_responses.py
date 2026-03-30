from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional, List
from models.analysis_schema import AnalysisResult

class BaseConfigModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

class CreateBorrowerRequest(BaseConfigModel):
    full_name: str
    email: str
    zip_code: str

class CreateBorrowerResponse(BaseConfigModel):
    borrower_id: str

class GenerateLinkRequest(BaseConfigModel):
    borrower_id: str

class GenerateLinkResponse(BaseConfigModel):
    link_token: str
    expires_at: str

class VerifyZipRequest(BaseConfigModel):
    link_token: str
    zip_code: str

class VerifyZipResponse(BaseConfigModel):
    valid: bool
    borrower_name: Optional[str] = None
    message: str

class BorrowerSummary(BaseConfigModel):
    borrower_id: str
    full_name: str
    email: str
    status: str
    created_at: str

class GetBorrowersResponse(BaseConfigModel):
    borrowers: List[BorrowerSummary]

class DashboardStatsResponse(BaseConfigModel):
    total_borrowers: int
    needs_link_creation: int
    link_created: int
    docs_submitted: int
    completed: int

class GetBorrowerResponse(BaseConfigModel):
    borrower_id: str
    full_name: str
    email: str
    zip_code: str
    status: str
    created_at: str
    updated_at: str
    analysis: Optional[AnalysisResult] = None
    document_link: Optional[str] = None

class GetLenderInfoResponse(BaseConfigModel):
    role: str
    organization: str