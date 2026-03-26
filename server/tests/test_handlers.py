import unittest
from unittest.mock import AsyncMock, MagicMock
from fastapi import BackgroundTasks
from app.handlers.file_handlers import FileHandler
from app.handlers.lender_handler import LenderHandler
from app.requests_responses.file_requests_responses import AnalyzeFilesRequest, SubmitFilesRequest
from app.requests_responses.lender_requests_responses import CreateBorrowerRequest

class TestFileHandler(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_service = MagicMock()
        self.handler = FileHandler(self.mock_service)

    async def test_handle_submit_files(self):
        request = SubmitFilesRequest(link_token="token123", zip_code="12345")
        expected_response = {"status": "success", "message": "Ok"}
        self.mock_service.submit_files = AsyncMock(return_value=expected_response)
        
        result = await self.handler.handle_submit_files(request)
        self.assertEqual(result, expected_response)
        self.mock_service.submit_files.assert_awaited_with(request)

    async def test_handle_analyze_files(self):
        request = AnalyzeFilesRequest(borrower_id="b123")
        expected_response = {"status": "accepted", "message": "Analysis started"}
        self.mock_service.analyze_files = AsyncMock(return_value=expected_response)
        
        mock_bg = MagicMock(spec=BackgroundTasks)
        
        result = await self.handler.handle_analyze_files(request, "u123", mock_bg)
        self.assertEqual(result, expected_response)
        self.mock_service.analyze_files.assert_awaited_with("b123", "u123")
        mock_bg.add_task.assert_called_once()

class TestLenderHandler(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_service = MagicMock()
        self.handler = LenderHandler(self.mock_service)

    async def test_create_borrower(self):
        request = CreateBorrowerRequest(email="test@email.com", full_name="Test User", zip_code="12345")
        expected_response = MagicMock()
        self.mock_service.create_borrower = AsyncMock(return_value=expected_response)
        
        result = await self.handler.create_borrower("u123", request)
        self.assertEqual(result, expected_response)
        self.mock_service.create_borrower.assert_awaited_with("u123", request)

    async def test_generate_link(self):
        from app.requests_responses.lender_requests_responses import GenerateLinkRequest
        request = GenerateLinkRequest(borrower_id="b123")
        self.mock_service.generate_borrower_link = AsyncMock(return_value={"link": "ok"})
        result = await self.handler.generate_link("u123", request)
        self.assertEqual(result["link"], "ok")

    async def test_verify_borrower_zip(self):
        from app.requests_responses.lender_requests_responses import VerifyZipRequest
        request = VerifyZipRequest(link_token="t1", zip_code="123")
        self.mock_service.verify_borrower_zip = AsyncMock(return_value={"valid": True})
        result = await self.handler.verify_borrower_zip(request)
        self.assertTrue(result["valid"])

    async def test_get_dashboard_stats(self):
        self.mock_service.get_dashboard_data = AsyncMock(return_value={"stats": "ok"})
        result = await self.handler.get_dashboard_stats("u123")
        self.assertEqual(result["stats"], "ok")

    async def test_get_borrowers(self):
        self.mock_service.get_borrowers = AsyncMock(return_value={"borrowers": []})
        result = await self.handler.get_borrowers("u123")
        self.assertEqual(len(result["borrowers"]), 0)

if __name__ == "__main__":
    unittest.main()
