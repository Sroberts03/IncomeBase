from pydantic import BaseModel, Field
from typing import Literal

class SingleClassifyFile(BaseModel):
    file_id: str = Field(..., description="the uuid of the file being classified")
    file_name: str = Field(..., description="Name based off the file content, not necessarily the original file name")
    classification: Literal["w2", "1099", "bank_statement", "institution_report"]
    source: Literal["stripe", "plaid", "shopify", "paypal", "amazon_seller", "upwork/fiverr", "bank", "other"]
    reasoning: str = Field(..., description="The reasoning behind the classification decision")
    confidence: float = Field(..., description="The confidence level of the classification decision, between 0 and 1")
    agent_name: str = Field(default="classifier_agent_v1")

class BatchClassifyFile(BaseModel):
    files: list[SingleClassifyFile]
