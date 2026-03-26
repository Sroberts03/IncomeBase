from pydantic import BaseModel
from datetime import datetime
from pyparsing import Literal

class Borrower(BaseModel):
    borrower_id: str
    lender_id: str
    full_name: str
    email: str
    org_id: str
    zip_code: str
    status: Literal["Needs Link Creation", "Link Created", "Docs Not Submitted", "Docs Submitted", "Analysis Complete"]
    created_at: str
    updated_at: str
    link_token: str
    link_token_expiration: datetime
