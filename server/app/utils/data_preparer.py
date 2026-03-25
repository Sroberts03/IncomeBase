from collections import defaultdict
from datetime import datetime

class DataPreparer:
    @staticmethod
    def prepare_financial_context(line_items: list):
        """
        Groups transactions by month to give the AI a clear, high-level timeline.
        """
        monthly_data = defaultdict(lambda: {"income": 0, "expenses": 0, "tx_count": 0, "details": []})
        
        for item in line_items:
            # Create a key like "2026-02"
            dt = datetime.strptime(str(item['file_date']), '%Y-%m-%d')            
            month_key = dt.strftime('%Y-%m')
            amount = float(item['amount'])
            monthly_data[month_key]["tx_count"] += 1
            
            if item['is_income']:
                monthly_data[month_key]["income"] += amount
                monthly_data[month_key]["details"].append(f"[INCOME] {item['description']}: ${amount}")
            else:
                monthly_data[month_key]["expenses"] += abs(amount)
                # We only include large expenses to save on "tokens"
                if abs(amount) > 100:
                    monthly_data[month_key]["details"].append(f"[LARGE EXPENSE] {item['description']}: ${amount}")

        # Build the string for the AI
        summary = "BORROWER FINANCIAL PROFILE (AGGREGATED)\n"
        summary += "========================================\n"
        
        # Sort months chronologically
        for month in sorted(monthly_data.keys()):
            m = monthly_data[month]
            summary += f"\nMONTH: {month}\n"
            summary += f"--- Total Income:   ${m['income']:.2f}\n"
            summary += f"--- Total Expenses: ${m['expenses']:.2f}\n"
            summary += f"--- Transaction Count: {m['tx_count']}\n"
            summary += "--- Key Transactions:\n    " + "\n    ".join(m['details'][-10:]) + "\n" # Show last 10 transactions for the month
            
        return summary