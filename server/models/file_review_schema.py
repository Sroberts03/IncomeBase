from pydantic import BaseModel, Field
from typing import List, Literal

class IndividualFileResult(BaseModel):
    file_id: str = Field(..., description="the uuid of the file being reviewed")
    status: Literal["approved", "rejected"]
    borrower_message: str = Field(..., description="Helpful message for the user")
    reasoning: str = Field(..., description="Internal technical reasoning")
    confidence: float = Field(..., ge=0, le=1)

class BatchFileReview(BaseModel):
    results: List[IndividualFileResult]
    overall_summary: str = Field(..., description="Summary of the entire batch for the underwriter")
    agent_name: str = Field(default="file_review_batch_agent_v1")