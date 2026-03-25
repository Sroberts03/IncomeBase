import asyncio
import os
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv
import sys
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from agents.analysis_agent import AnalysisAgent
from app.utils.data_preparer import DataPreparer
from models.analysis_schema import AnalysisResult

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def run_stress_test():
    # 1. MOCK DATA: A "High Risk" Borrower
    # - Declining income
    # - High expenses (Burn rate)
    # - NSF fees
    # - One massive "Anomalous" deposit
    high_risk_items = [
        {"file_date": "2025-11-05", "description": "STRIPE PAYOUT", "amount": 8000.0, "is_income": True},
        {"file_date": "2025-12-05", "description": "STRIPE PAYOUT", "amount": 4000.0, "is_income": True},
        {"file_date": "2026-01-05", "description": "STRIPE PAYOUT", "amount": 2000.0, "is_income": True},
        {"file_date": "2026-01-10", "description": "NSF FEE: OVERDRAFT", "amount": -35.0, "is_income": False},
        {"file_date": "2026-01-15", "description": "OFFICE RENT", "amount": -5000.0, "is_income": False},
        {"file_date": "2026-01-20", "description": "TRANSFER FROM UNKNOWN", "amount": 15000.0, "is_income": True},
    ]

    print("🚨 Running Stress Test on High-Risk Borrower...")
    context = DataPreparer.prepare_financial_context(high_risk_items)
    
    agent = AnalysisAgent(client=client)
    report = await agent.analyze(context)

    # 2. VERIFYING THE AI'S "SKEPTICISM"
    print(f"\n[Verdict] Trend: {report.income_trend}")
    print(f"[Burn Rate] Net Burn: ${report.net_burn_rate}")
    print(f"[NSF Check] Count: {report.nsf_count_total}")
    
    print("\n🚩 Risk Factors Found:")
    for risk in report.risk_factors:
        print(f"  - {risk}")

    print("\n🔍 Anomalous Deposits:")
    for anomaly in report.anomalous_deposits:
        print(f"  - {anomaly}")

    print(f"\n📝 Summary: {report.analysis_summary}")

if __name__ == "__main__":
    asyncio.run(run_stress_test())