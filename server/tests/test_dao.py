import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from app.dao.file_dao import FileDao
from app.dao.lender_dao import LenderDao
from models.classifier_schema import SingleClassifyFile

class MockSupabase:
    """Helper to mock Supabase's chained calls more cleanly."""
    def __init__(self):
        self.table = MagicMock()
        self.storage = MagicMock()
        
        # Setup chainable table methods
        self.table_return = MagicMock()
        self.table.return_value = self.table_return
        self.table_return.select.return_value = self.table_return
        self.table_return.insert.return_value = self.table_return
        self.table_return.update.return_value = self.table_return
        self.table_return.upsert.return_value = self.table_return
        self.table_return.order.return_value = self.table_return
        self.table_return.eq.return_value = self.table_return
        self.table_return.single = AsyncMock()
        self.table_return.execute = AsyncMock()

class TestFileDao(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_supabase = MockSupabase()
        self.dao = FileDao(self.mock_supabase)

    async def test_get_borrower_data_from_link_token_success(self):
        self.mock_supabase.table_return.execute.return_value = MagicMock(data=[
            {"borrower_id": "b123", "borrowers": {"zip_code": "12345"}}
        ])
        
        result = await self.dao.get_borrower_data_from_link_token("token123")
        
        self.assertEqual(result["borrower_id"], "b123")
        self.assertEqual(result["zip_code"], "12345")
        self.mock_supabase.table.assert_called_with("file_links")

    async def test_get_pending_records(self):
        expected_data = [{"id": "f1", "file_path": "path1"}]
        self.mock_supabase.table_return.execute.return_value = MagicMock(data=expected_data)
        
        result = await self.dao.get_pending_records("b123")
        
        self.assertEqual(result, expected_data)
        self.mock_supabase.table.assert_called_with("files")

    async def test_get_files(self):
        mock_download = AsyncMock(return_value=MagicMock(content=b"file_bytes"))
        self.mock_supabase.storage.from_.return_value.download = mock_download
        
        result = await self.dao.get_files(["path1"])
        
        self.assertEqual(result, [b"file_bytes"])
        self.mock_supabase.storage.from_.assert_called_with("borrower-files")

    async def test_update_file_classification(self):
        classification = SingleClassifyFile(
            classification="w2",
            source="bank",
            file_name="w2.pdf",
            reasoning="Looks like a W2",
            file_id="f1",
            confidence=0.9
        )
        
        await self.dao.update_file_classification("b123", classification, "f1")
        self.assertEqual(self.mock_supabase.table.call_count, 2)

class TestLenderDao(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_supabase = MockSupabase()
        self.dao = LenderDao(self.mock_supabase)

    async def test_get_org_id_for_lender(self):
        self.mock_supabase.table_return.execute.return_value = MagicMock(data=[{"org_id": "org123"}])
        
        result = await self.dao.get_org_id_for_lender("l123")
        
        self.assertEqual(result, "org123")
        self.mock_supabase.table.assert_called_with("organization_members")

    async def test_create_borrower(self):
        self.mock_supabase.table_return.execute.return_value = MagicMock(data=[{"borrower_id": "b123"}])
        
        result = await self.dao.create_borrower(
            "l123", "test@email.com", "Test User", "12345", "org123", "status", "now", "now"
        )
        
        self.assertEqual(result, "b123")
        self.mock_supabase.table.assert_called_with("borrowers")

    async def test_create_file_link(self):
        await self.dao.create_file_link("b123", "token123", "expires")
        self.mock_supabase.table.assert_called_with("file_links")
        self.mock_supabase.table_return.upsert.assert_called()

    async def test_get_borrower_by_link_token(self):
        self.mock_supabase.table_return.execute.return_value = MagicMock(data=[
            {"borrower_id": "b123", "borrowers": {"full_name": "Test"}}
        ])
        result = await self.dao.get_borrower_by_link_token("token123")
        self.assertEqual(result["borrower_id"], "b123")

    async def test_get_borrowers_for_org(self):
        self.mock_supabase.table_return.execute.return_value = MagicMock(data=[{"borrower_id": "b1"}])
        result = await self.dao.get_borrowers_for_org("org123")
        self.assertEqual(len(result), 1)

    async def test_get_dashboard_stats(self):
        self.mock_supabase.table_return.execute.return_value = MagicMock(data=[
            {"status": "Needs Link Creation"},
            {"status": "Completed"}
        ])
        result = await self.dao.get_dashboard_stats("org123")
        self.assertEqual(result["total_borrowers"], 2)
        self.assertEqual(result["needs_link_creation"], 1)
        self.assertEqual(result["completed"], 1)

if __name__ == "__main__":
    unittest.main()
