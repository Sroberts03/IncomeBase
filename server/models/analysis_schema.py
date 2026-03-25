from pydantic import BaseModel, Field
from typing import List, Literal

class MonthlyPoint(BaseModel):
    year: int
    month: str = Field(..., description="Full month name, e.g., 'January'")
    income: float = Field(..., description="Total qualifying income for this specific month")

class AnalysisResult(BaseModel):
    # Core Averages & Qualitative Assessment
    monthly_average_income: float = Field(..., description="Average monthly income over the last 12 months")
    income_stability_score: float = Field(..., ge=0, le=1)
    recurring_income_percentage: float = Field(..., ge=0, le=1)
    income_trend: Literal["Increasing", "Stable", "Declining", "Volatile"] = Field(..., description="Trend of income over the last 12 months")
    largest_deposit_source: Literal["stripe", "plaid", "shopify", "paypal", "amazon_seller", "upwork/fiverr", "bank", "other"] = Field(..., description="Source of the largest deposit in the provided financial data")
    expense_to_income_ratio: float = Field(..., ge=0, le=1)
    net_burn_rate: float = Field(..., description="Net burn rate calculated as total expenses minus total income over the last 12 months, expressed as a positive number if expenses exceed income, or negative if income exceeds expenses")
    
    # Historical Totals (Keep these for the "Quick Stat" cards on your UI)
    income_ytd: List[MonthlyPoint] = Field(..., description="List of monthly income points for the year-to-date period")
    income_last_6: List[MonthlyPoint] = Field(..., description="List of monthly income points for the last 6 months")
    income_last_12: List[MonthlyPoint] = Field(..., description="List of monthly income points for the last 12 months")
    income_last_24: List[MonthlyPoint] = Field(..., description="List of monthly income points for the last 24 months")

    # Risk & Summary
    nsf_count_total: int = Field(..., description="Total count of Non-Sufficient Funds (NSF) occurrences in the provided financial data")
    risk_factors: List[str] = Field(..., description="List of identified risk factors")
    anomalous_deposits: List[str] = Field(..., description="List of any anomalous deposits identified in the financial data, including source and amount")
    confidence_score: float = Field(..., ge=0, le=1)
    analysis_summary: str = Field(..., description="Summary of the financial analysis")