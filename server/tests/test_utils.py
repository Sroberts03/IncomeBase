import unittest
from pathlib import Path
from app.utils.document_parser import DocumentParser
from app.utils.data_preparer import DataPreparer
from models.extraction_schema import IndividualFileExtraction, DocumentData, TransactionLineItem
from datetime import date
import base64
import os

class TestDocumentParser(unittest.TestCase):
    def test_parse_image(self):
        dummy_bytes = b"dummy image data"
        result = DocumentParser.parse(dummy_bytes, "test.jpg")
        self.assertEqual(result["type"], "image")
        self.assertEqual(result["name"], "test.jpg")
        # Base64 of 'dummy image data' is 'ZHVtbXkgaW1hZ2UgZGF0YQ=='
        self.assertEqual(result["content"], base64.b64encode(dummy_bytes).decode("utf-8"))

    def test_parse_unsupported_extension(self):
        result = DocumentParser.parse(b"hello", "test.txt")
        self.assertIsNone(result)

    def test_parse_digital_pdf(self):
        # We need a real small PDF or a mock that fitz can read
        # Let's use a small valid PDF from the test_docs if it exists
        pdf_path = Path("tests/test_docs/digital_statement.pdf")
        if pdf_path.exists():
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            result = DocumentParser.parse(pdf_bytes, "digital_statement.pdf")
            self.assertIn(result["type"], ["text", "image"])
            self.assertEqual(result["name"], "digital_statement.pdf")

class TestDataPreparer(unittest.TestCase):
    def test_prepare_financial_context_success(self):
        line_item = TransactionLineItem(
            file_date=date(2023, 1, 1),
            description="Payroll",
            amount=1000.0,
            is_income=True
        )
        doc_data = DocumentData(
            account_holder="John Doe",
            institution="Chase",
            line_items=[line_item],
            total_deposits=1000.0,
            statement_period="Jan 2023"
        )
        extraction = IndividualFileExtraction(
            file_id="f1",
            file_name="stmt.pdf",
            extracted_data=doc_data,
            reasoning="Reason",
            confidence=0.9
        )
        
        summary = DataPreparer.prepare_financial_context([extraction])
        self.assertIn("John Doe", summary)
        self.assertIn("TOTAL_INCOME_SUM: $1000.00", summary)
        self.assertIn("File ID: f1", summary) # Check the fix we made earlier

if __name__ == "__main__":
    unittest.main()
