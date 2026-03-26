from pydantic import BaseModel

class CreateBorrowerRequest(BaseModel):
    full_name: str
    email: str
    zip_code: str

class CreateBorrowerResponse(BaseModel):
    borrower_id: str