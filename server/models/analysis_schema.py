from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import List, Literal

class BaseConfigModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

class MonthlyPoint(BaseConfigModel):
    year: int
    month: str = Field(..., description="Full month name, e.g., 'January'")
    income: float = Field(..., description="Total qualifying income for this specific month")

class AnalysisResult(BaseConfigModel):
    # Core Averages & Qualitative Assessment
    monthly_average_income: float = Field(..., description="Average monthly income over the last 12 months")
    income_stability_score: float = Field(..., ge=0, le=1)
    recurring_income_percentage: float = Field(..., ge=0, le=1)
    income_trend: Literal["Increasing", "Stable", "Declining", "Volatile"] = Field(..., description="Trend of income over the last 12 months")
    largest_deposit_source: Literal["stripe", "plaid", "shopify", "paypal", "amazon_seller", "upwork/fiverr", "bank", "other"] = Field(..., description="Source of the largest deposit in the provided financial data")
    expense_to_income_ratio: float = Field(..., ge=0, le=1)
    net_burn_rate: float = Field(..., description="Monthly Net Cash Flow. Calculation: (Total Income + Total Expenses) / Number of Months. A positive number means the borrower saved money; a negative number means they overspent.")    
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

    def __str__(self):
        # 1. Helper logic to format lists into clean bullet points
        risks_str = "\n  - ".join(self.risk_factors) if self.risk_factors else "None identified."
        anomalies_str = "\n  - ".join(self.anomalous_deposits) if self.anomalous_deposits else "None identified."
        
        # 2. Build the Markdown report
        return f"""
            ### FINANCIAL ANALYSIS REPORT
            **AI Confidence Score:** {self.confidence_score * 100:.1f}%

            #### 1. Core Cash Flow Metrics
            - **Monthly Average Income:** ${self.monthly_average_income:,.2f}
            - **Net Burn Rate:** ${self.net_burn_rate:,.2f}/mo
            - **Expense-to-Income Ratio:** {self.expense_to_income_ratio * 100:.1f}%
            - **Income Stability Score:** {self.income_stability_score * 100:.1f}%
            - **Recurring Income:** {self.recurring_income_percentage * 100:.1f}%

            #### 2. Trends & Sourcing
            - **Income Trend:** {self.income_trend}
            - **Largest Deposit Source:** {self.largest_deposit_source.title()}

            #### 3. Risk Assessment
            - **Total NSF Count:** {self.nsf_count_total}
            - **Risk Factors:**
            - {risks_str}
            - **Anomalous Deposits:**
            - {anomalies_str}

            #### 4. Analyst Summary
            {self.analysis_summary}
            """
