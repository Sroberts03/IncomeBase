from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import List
from datetime import date

class BaseConfigModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

# 1. This defines EXACTLY what a transaction looks like
class TransactionLineItem(BaseConfigModel):
    file_date: date = Field(..., description="The date of the transaction (YYYY-MM-DD)")
    description: str = Field(..., description="Cleaned merchant or payer name")
    amount: float = Field(..., description="Positive for deposits/income, negative for expenses")
    is_income: bool = Field(..., description="True if this is recurring/qualifying income (Payroll, Payouts, etc.)")

# 2. This defines the summary data for the whole document
class DocumentData(BaseConfigModel):
    account_holder: str = Field(..., description="Name found on the statement")
    institution: str = Field(..., description="Bank or Platform name")
    line_items: List[TransactionLineItem]
    total_deposits: float
    statement_period: str = Field(..., description="e.g., 'Jan 2025' or '01/01/25 - 01/31/25'")

# 3. This integrates into your Batch result
class IndividualFileExtraction(BaseConfigModel):
    file_id: str = Field(..., description="the uuid of the file being extracted")
    file_name: str = Field(..., description="the original name of the file being extracted")
    extracted_data: DocumentData
    reasoning: str
    confidence: float