import asyncio
import os
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Standard path setup for Summit West project
import sys
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from models.extraction_schema import IndividualFileExtraction
from agents.analysis_agent import AnalysisAgent
from app.utils.data_preparer import DataPreparer
from models.analysis_schema import AnalysisResult

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def test_analysis_flow():
    # 1. Mock Data: Simulating 6 months of extraction results
    # We use 'file_date' to match the key fixed in your DataPreparer
    line_items = [
        {"file_date": "2025-10-15", "description": "Deposit paycheck", "amount": 3000.00, "is_income": True},
        {"file_date": "2025-10-20", "description": "Grocery Store", "amount": -150.00, "is_income": False},
        {"file_date": "2025-11-01", "description": "Deposit freelance", "amount": 1200.00, "is_income": True},
        {"file_date": "2025-11-05", "description": "Electric Bill", "amount": -100.00, "is_income": False},
        {"file_date": "2025-12-01", "description": "Deposit paycheck", "amount": 3000.00, "is_income": True},
        {"file_date": "2025-12-10", "description": "Rent Payment", "amount": -1200.00, "is_income": False},
        {"file_date": "2026-01-01", "description": "Deposit freelance", "amount": 1500.00, "is_income": True},
        {"file_date": "2026-01-15", "description": "Car Payment", "amount": -400.00, "is_income": False},
        {"file_date": "2026-02-01", "description": "Deposit paycheck", "amount": 3000.00, "is_income": True},
        {"file_date": "2026-02-20", "description": "Grocery Store", "amount": -200.00, "is_income": False},
        {"file_date": "2026-03-01", "description": "Deposit freelance", "amount": 1300.00, "is_income": True},
        {"file_date": "2026-03-10", "description": "Electric Bill", "amount": -110.00, "is_income": False},
    ]
    individual_file_extraction = {
        "file_index": 0,
        "extracted_data": {
            "account_holder": "John Doe",
            "institution": "Bank of Test",
            "line_items": line_items,
            "total_deposits": sum(item["amount"] for item in line_items if item["is_income"]),
            "statement_period": "Oct 2025 - Mar 2026"
        },
        "reasoning": "Mock data simulating 6 months of transactions with a mix of income and expenses.",
        "confidence": 0.95
    }

    individual_file_extraction = IndividualFileExtraction(**individual_file_extraction)

    # 2. CALL THE DATA PREPARER
    # This turns the list of dicts into the "Narrative" for gpt-4o
    print("🧹 Cleaning and grouping data...")
    context_str = DataPreparer.prepare_financial_context([individual_file_extraction])

    # 3. INITIALIZE AND RUN AGENT
    print("🤖 Sending to Analysis Agent (gpt-4o)...")
    agent = AnalysisAgent(client=client) 
    report: AnalysisResult = await agent.analyze(context_str)

    # 4. RESULTS FOR YOUR DASHBOARD
    print(f"\n" + "="*40)
    print(f"VERDICT: {report.income_trend} Trend")
    print(f"Monthly Average: ${report.monthly_average_income:,.2f}")
    print(f"Net Burn Rate: ${report.net_burn_rate:,.2f}")
    print(f"="*40)

    # Testing the new Time-Series Object (income_last_6)
    print("\n📈 6-MONTH CHART DATA:")
    for pt in report.income_last_6:
        print(f"  {pt.year} {pt.month:<10} | Income: ${pt.income:,.2f}")

    print("\n🚩 RISK ASSESSMENT:")
    print(f"  NSF Count: {report.nsf_count_total}")
    for risk in report.risk_factors:
        print(f"  - {risk}")

    if report.anomalous_deposits:
        print("\n🔍 ANOMALOUS DEPOSITS DETECTED:")
        for anomaly in report.anomalous_deposits:
            print(f"  - {anomaly}")

    print(f"\n📝 UNDERWRITER SUMMARY:\n{report.analysis_summary}")
    print("="*40)

if __name__ == "__main__":
    asyncio.run(test_analysis_flow())