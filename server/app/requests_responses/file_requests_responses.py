from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from models.file_review_schema import IndividualFileResult

class SubmitFilesRequest(BaseModel):
    link_token: str 

class AnalyzeFilesRequest(BaseModel):
    borrower_id: str

class SubmitFilesStats(BaseModel):
    total_received: int
    approved: int
    rejected: int
    successfully_classified: int

class SubmitFilesResponse(BaseModel):
    status: str
    review_results: List[IndividualFileResult]
    stats: SubmitFilesStats
    overall_summary: str
    message: Optional[str] = None

class GenericMessageResponse(BaseModel):
    status: str
    message: str
    approved: bool
    borrower_id: Optional[str] = None
    retries: Optional[int] = None