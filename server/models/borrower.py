from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from datetime import datetime
from typing import Literal

class BaseConfigModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

class Borrower(BaseConfigModel):
    borrower_id: str
    lender_id: str
    full_name: str
    email: str
    org_id: str
    zip_code: str
    status: Literal["Needs Link Creation", "Link Created", "Docs Not Submitted", "Docs Submitted", "Analysis Complete", "Analyzing", "Analysis Failed", "Analysis Flagged For Review"]
    created_at: str
    updated_at: str
    link_token: str
    link_token_expiration: datetime
