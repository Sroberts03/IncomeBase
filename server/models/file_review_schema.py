from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import List, Literal, Optional

class BaseConfigModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

class IndividualFileResult(BaseConfigModel):
    file_id: str = Field(..., description="the uuid of the file being reviewed")
    file_name: Optional[str] = None
    status: Literal["approved", "rejected"]
    borrower_message: str = Field(..., description="Helpful message for the user")
    reasoning: str = Field(..., description="Internal technical reasoning")
    confidence: float = Field(..., ge=0, le=1)

class BatchFileReview(BaseConfigModel):
    results: List[IndividualFileResult]
    overall_summary: str = Field(..., description="Summary of the entire batch for the underwriter")
    agent_name: str = Field(default="file_review_batch_agent_v1")