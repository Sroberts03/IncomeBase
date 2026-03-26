from pydantic import BaseModel, Field

class BatchProcessRequest(BaseModel):
    link_token: str  