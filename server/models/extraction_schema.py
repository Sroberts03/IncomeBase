from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

# 1. This defines EXACTLY what a transaction looks like
class TransactionLineItem(BaseModel):
    file_date: date = Field(..., description="The date of the transaction (YYYY-MM-DD)")
    description: str = Field(..., description="Cleaned merchant or payer name")
    amount: float = Field(..., description="Positive for deposits/income, negative for expenses")
    is_income: bool = Field(..., description="True if this is recurring/qualifying income (Payroll, Payouts, etc.)")

# 2. This defines the summary data for the whole document
class DocumentData(BaseModel):
    account_holder: str = Field(..., description="Name found on the statement")
    institution: str = Field(..., description="Bank or Platform name")
    line_items: List[TransactionLineItem]
    total_deposits: float
    statement_period: str = Field(..., description="e.g., 'Jan 2025' or '01/01/25 - 01/31/25'")

# 3. This integrates into your Batch result
class IndividualFileExtraction(BaseModel):
    file_index: int
    extracted_data: DocumentData
    reasoning: str
    confidence: float

class BatchExtractionResult(BaseModel):
    results: List[IndividualFileExtraction]
    overall_summary: str
    agent_name: str = Field(default="extraction_agent_v1")