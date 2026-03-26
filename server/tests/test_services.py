import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.file_services import FileService
from app.services.lender_service import LenderService
from models.file_review_schema import BatchFileReview, IndividualFileResult
from models.classifier_schema import SingleClassifyFile, BatchClassifyFile
from app.requests_responses.lender_requests_responses import CreateBorrowerRequest, CreateBorrowerResponse

class TestFileService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_file_dao = MagicMock()
        self.mock_file_review_agent = MagicMock()
        self.mock_classifier_agent = MagicMock()
        self.mock_extractor_agent = MagicMock()
        self.mock_analyzer_agent = MagicMock()
        self.mock_review_agent = MagicMock()
        self.mock_parser = MagicMock()
        self.mock_data_preparer = MagicMock()
        self.mock_lender_dao = MagicMock()

        self.service = FileService(
            self.mock_file_dao,
            self.mock_file_review_agent,
            self.mock_classifier_agent,
            self.mock_extractor_agent,
            self.mock_analyzer_agent,
            self.mock_review_agent,
            self.mock_parser,
            self.mock_data_preparer,
            self.mock_lender_dao
        )

    async def test_submit_files_no_pending(self):
        self.mock_file_dao.get_borrower_id_from_link_token = AsyncMock(return_value="b123")
        self.mock_file_dao.get_pending_records = AsyncMock(return_value=[])
        
        result = await self.service.submit_files("token123")
        self.assertEqual(result["message"], "No pending files.")
        self.mock_file_dao.get_pending_records.assert_awaited_with("b123")

    async def test_submit_files_with_review_and_classification(self):
        self.mock_file_dao.get_borrower_id_from_link_token = AsyncMock(return_value="b123")
        self.mock_file_dao.get_pending_records = AsyncMock(return_value=[{"id": "f1", "file_path": "path1"}])
        self.mock_file_dao.get_files = AsyncMock(return_value=[b"bytes1"])
        
        # Mocking review results
        review_result = IndividualFileResult(
            file_id="f1", 
            status="approved", 
            borrower_message="Good", 
            reasoning="Passed", 
            confidence=0.9
        )
        self.mock_file_review_agent.review = AsyncMock(return_value=BatchFileReview(results=[review_result], overall_summary="Ok"))
        
        # Mocking classification results
        class_result = SingleClassifyFile(
            classification="w2", 
            source="bank", 
            file_name="w2.pdf", 
            reasoning="R", 
            file_id="f1", 
            confidence=0.9
        )
        self.mock_classifier_agent.classify = AsyncMock(return_value=BatchClassifyFile(files=[class_result]))
        
        self.mock_file_dao.update_file_classification = AsyncMock()

        result = await self.service.submit_files("token123")
        
        self.assertEqual(len(result["review_results"]), 1)
        self.assertEqual(result["stats"]["successfully_classified"], 1)
        self.mock_classifier_agent.classify.assert_awaited()
        self.mock_file_dao.update_file_classification.assert_awaited()

    async def test_analyze_files_unauthorized(self):
        self.mock_lender_dao.check_borrower_ownership = AsyncMock(return_value=False)
        with self.assertRaises(Exception) as cm:
            await self.service.analyze_files("b123", "u123")
        self.assertIn("Unauthorized", str(cm.exception))

    async def test_analyze_files_no_files_trigger(self):
        # Even if there are no files, the trigger should succeed if owner is verified
        self.mock_lender_dao.check_borrower_ownership = AsyncMock(return_value=True)
        self.mock_lender_dao.update_borrower_status = AsyncMock()
        
        result = await self.service.analyze_files("b123", "u123")
        self.assertEqual(result["status"], "accepted")
        self.mock_lender_dao.update_borrower_status.assert_awaited_with("b123", "Analyzing")

    async def test_run_analysis_pipeline_success(self):
        self.mock_file_dao.get_files_for_borrower = AsyncMock(return_value=[{"id": "f1", "file_name": "f1.pdf", "file_path": "p1"}])
        self.mock_file_dao.get_files = AsyncMock(return_value=[b"bytes1"])
        self.mock_parser.parse = MagicMock(return_value="parsed_data")
        self.mock_lender_dao.update_borrower_status = AsyncMock()
        
        # Mock extraction result
        from models.extraction_schema import IndividualFileExtraction, DocumentData
        extraction_result = IndividualFileExtraction(
            file_id="f1", 
            file_name="f1.pdf", 
            extracted_data=DocumentData(
                account_holder="Test", 
                institution="Bank", 
                line_items=[], 
                total_deposits=0, 
                statement_period="Jan 2023"
            ),
            reasoning="R",
            confidence=0.9
        )
        self.mock_extractor_agent.extract_single_file = AsyncMock(return_value=extraction_result)
        self.mock_file_dao.bulk_insert_line_items = AsyncMock(return_value=0)
        
        self.mock_data_preparer.prepare_financial_context = MagicMock(return_value="context")
        
        # Mock analyzer results
        mock_report = MagicMock()
        mock_report.model_dump.return_value = {"report": "data"}
        mock_report.model_dump_json.return_value = '{"report": "data"}'
        self.mock_analyzer_agent.analyze = AsyncMock(return_value=mock_report)
        
        # Mock review agent result
        review_result = MagicMock()
        review_result.is_approved = True
        self.mock_review_agent.review_analysis = AsyncMock(return_value=review_result)
        
        self.mock_file_dao.save_analysis_results = AsyncMock()
        
        # Run the internal background pipeline
        await self.service.run_analysis_pipeline("b123")
        
        self.mock_lender_dao.update_borrower_status.assert_any_call("b123", "Completed")
        self.mock_parser.parse.assert_called_with(b"bytes1", "f1.pdf")
        self.mock_file_dao.save_analysis_results.assert_awaited()

    async def test_process_and_save_extractions(self):
        from models.extraction_schema import IndividualFileExtraction, DocumentData, TransactionLineItem
        from datetime import date
        line_item = TransactionLineItem(amount=100.0, file_date=date(2023, 1, 1), is_income=True, description="test")
        extraction_result = IndividualFileExtraction(
            file_id="f1", 
            file_name="f1.pdf", 
            extracted_data=DocumentData(
                account_holder="Test", 
                institution="Bank", 
                line_items=[line_item], 
                total_deposits=100.0, 
                statement_period="Jan 2023"
            ),
            reasoning="R",
            confidence=0.9
        )
        
        self.mock_file_dao.bulk_insert_line_items = AsyncMock(return_value=1)
        
        result = await self.service.process_and_save_extractions("b123", [extraction_result])
        
        self.assertEqual(result["message"], "Successfully inserted 1 line items.")
        self.mock_file_dao.bulk_insert_line_items.assert_awaited()


class TestLenderService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_lender_dao = MagicMock()
        self.service = LenderService(self.mock_lender_dao)

    async def test_create_borrower_success(self):
        self.mock_lender_dao.get_org_id_for_lender = AsyncMock(return_value="org123")
        self.mock_lender_dao.create_borrower = AsyncMock(return_value="b123")
        
        request = CreateBorrowerRequest(email="test@email.com", full_name="Test User", zip_code="12345")
        result = await self.service.create_borrower("u123", request)
        
        self.assertEqual(result.borrower_id, "b123")
        self.mock_lender_dao.get_org_id_for_lender.assert_awaited_with("u123")

    async def test_create_borrower_failure(self):
        self.mock_lender_dao.get_org_id_for_lender = AsyncMock(side_effect=Exception("DB Error"))
        
        request = CreateBorrowerRequest(email="test@email.com", full_name="Test User", zip_code="12345")
        with self.assertRaises(Exception) as cm:
            await self.service.create_borrower("u123", request)
        self.assertEqual(str(cm.exception), "Failed to create borrower due to an internal error.")

if __name__ == "__main__":
    unittest.main()
