from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import List, Dict, Any, Optional
from models.file_review_schema import IndividualFileResult
from models.file_record import BorrowerFileRecord

class BaseConfigModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

class SubmitFilesRequest(BaseConfigModel):
    link_token: str 
    zip_code: str
    
class AnalyzeFilesRequest(BaseConfigModel):
    borrower_id: str

class SubmitFilesStats(BaseConfigModel):
    total_received: int
    approved: int
    rejected: int
    classification_status: str

class SubmitFilesResponse(BaseConfigModel):
    status: str
    review_results: List[IndividualFileResult]
    stats: SubmitFilesStats
    overall_summary: str
    message: Optional[str] = None

class GenericMessageResponse(BaseConfigModel):
    status: str
    message: str
    approved: bool
    borrower_id: Optional[str] = None
    retries: Optional[int] = None

class GetFilesResponse(BaseConfigModel):
    files: List[BorrowerFileRecord]