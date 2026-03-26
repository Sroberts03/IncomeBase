from collections import defaultdict
from datetime import datetime
from models.extraction_schema import IndividualFileExtraction

class DataPreparer:
    @staticmethod
    def prepare_financial_context(extractions: list[IndividualFileExtraction]) -> str:
        """
        Groups transactions by month and calculates aggregate stats for the AI.
        """
        summary = "BORROWER FINANCIAL PROFILE (AGGREGATED)\n"
        summary += "========================================\n"

        monthly_data = defaultdict(lambda: {"income": 0, "expenses": 0, "tx_count": 0, "details": []})
        total_income = 0.0
        total_expenses = 0.0
        
        for extraction in extractions:
            summary += f"File index: {extraction.file_index}\n"
            summary += f"Account Holder: {extraction.extracted_data.account_holder}\n"
            summary += f"Institution: {extraction.extracted_data.institution}\n"
            summary += f"Statement Period: {extraction.extracted_data.statement_period}\n"
            summary += f"Total Deposits: ${extraction.extracted_data.total_deposits:.2f}\n"
            summary += "Transactions:\n"
            for line_item in extraction.extracted_data.line_items:
                summary += f" Data: {line_item.file_date}"
                summary += f"  - {line_item.description}: ${line_item.amount:.2f}\n"
                summary += f"(Income: {line_item.is_income})\n"
                
                # Use strftime since we know it's a date object now
                month_key = line_item.file_date.strftime("%Y-%m")                
                
                if line_item.is_income:
                    monthly_data[month_key]["income"] += line_item.amount
                    total_income += line_item.amount
                else:
                    # Keep expenses negative as they appear in your data
                    monthly_data[month_key]["expenses"] += line_item.amount
                    total_expenses += line_item.amount
                
                monthly_data[month_key]["tx_count"] += 1
                monthly_data[month_key]["details"].append(line_item)
        
        summary += "\n\nAGGREGATED MONTHLY VIEW\n"
        summary += "========================================\n"
        for month, data in sorted(monthly_data.items()):
            summary += f"{month}: Income=${data['income']:.2f}, Expenses=${data['expenses']:.2f}, Transactions={data['tx_count']}\n"
            for detail in data["details"]:
                summary += f"  - {detail.file_date}: {detail.description} | Amount: ${detail.amount:.2f} | Income: {detail.is_income}\n" 

        # --- ADDED: HARD CALCULATIONS FOR THE AGENT ---
        num_months = len(monthly_data) if monthly_data else 1
        avg_income = total_income / num_months
        # Formula: ((expenses - income) / months) per your Pydantic description
        # Note: total_expenses is already negative, so we add it or use its absolute value
        net_burn = (abs(total_expenses) - total_income) / num_months

        summary += "\n\nFINAL AUDITED TOTALS (USE THESE FOR YOUR ANALYSIS)\n"
        summary += "========================================\n"
        summary += f"TOTAL_MONTHS_ANALYZED: {num_months}\n"
        summary += f"TOTAL_INCOME_SUM: ${total_income:.2f}\n"
        summary += f"TOTAL_EXPENSES_SUM: ${total_expenses:.2f}\n"
        summary += f"CALCULATED_MONTHLY_AVERAGE: ${avg_income:.2f}\n"
        summary += f"CALCULATED_NET_BURN_RATE: ${net_burn:.2f}\n"
        
        print(summary) 
        return summary