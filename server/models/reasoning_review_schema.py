from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import List, Literal

class BaseConfigModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

class FinalReview(BaseConfigModel):
    # The Verdict
    is_approved: bool = Field(..., description="True if the analysis math and logic are 100% sound")
    audit_verdict: Literal["Pass", "Pass with Notes", "Fail/Re-run"] = Field(..., description="High-level status for the dashboard")
    
    # The Details
    corrections: List[str] = Field(..., description="Specific logical or mathematical errors identified")
    auditor_notes: str = Field(..., description="Internal narrative for the lender's eyes only")
    
    # Quantitative Quality Check
    logic_accuracy_score: float = Field(..., ge=0, le=1, description="Confidence in the Analysis Agent's reasoning")
    flagged_inconsistencies: bool = Field(..., description="True if the AI found a mismatch between raw data and the summary")