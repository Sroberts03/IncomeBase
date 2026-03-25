import fitz 
import os

def create_test_pdf():
    os.makedirs("tests/test_docs", exist_ok=True)
    doc = fitz.open()
    page = doc.new_page()
    
    text = """
    WELLS FARGO - BUSINESS CHECKING
    Account Holder: Summit West Technologies LLC
    Period: 02/01/2026 - 02/28/2026
    
    TRANSACTIONS:
    02/05/2026   STRIPE PAYOUT          $2,500.00
    02/10/2026   AWS BILLING            -$145.20
    02/15/2026   GUSTO PAYROLL          $4,200.00
    02/20/2026   VENMO FROM MOM         $50.00
    """
    
    page.insert_text((50, 50), text)
    doc.save("tests/test_docs/digital_statement.pdf")
    print("✅ Created digital_statement.pdf")

if __name__ == "__main__":
    create_test_pdf()