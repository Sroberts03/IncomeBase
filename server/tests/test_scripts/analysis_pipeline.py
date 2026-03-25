import asyncio
import os
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Standard path setup for Summit West project
import sys
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from agents.analysis_agent import AnalysisAgent
from app.utils.data_preparer import DataPreparer
from models.analysis_schema import AnalysisResult

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def test_analysis_flow():
    # 1. Mock Data: Simulating 6 months of extraction results
    # We use 'file_date' to match the key fixed in your DataPreparer
    extracted_items = [
        {"file_date": "2025-10-05", "description": "STRIPE PAYOUT", "amount": 3000.0, "is_income": True},
        {"file_date": "2025-11-05", "description": "STRIPE PAYOUT", "amount": 3200.0, "is_income": True},
        {"file_date": "2025-12-05", "description": "STRIPE PAYOUT", "amount": 3500.0, "is_income": True},
        {"file_date": "2026-01-05", "description": "STRIPE PAYOUT", "amount": 3800.0, "is_income": True},
        {"file_date": "2026-02-05", "description": "STRIPE PAYOUT", "amount": 4200.0, "is_income": True},
        {"file_date": "2026-02-12", "description": "OVERDRAFT FEE", "amount": -35.0, "is_income": False},
        {"file_date": "2026-03-05", "description": "STRIPE PAYOUT", "amount": 4500.0, "is_income": True},
        {"file_date": "2026-03-10", "description": "AMAZON SALES DISBURSEMENT", "amount": 12000.0, "is_income": True} # Anomalous?
    ]

    # 2. CALL THE DATA PREPARER
    # This turns the list of dicts into the "Narrative" for gpt-4o
    print("🧹 Cleaning and grouping data...")
    context_str = DataPreparer.prepare_financial_context(extracted_items)

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