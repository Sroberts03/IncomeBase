from pydantic import BaseModel, Field

class SubmitFilesRequest(BaseModel):
    link_token: str 

class AnalyzeFilesRequest(BaseModel):
    borrower_id: str