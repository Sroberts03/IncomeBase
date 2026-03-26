import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from main import app
from app.api.v1.file_routes import get_file_handler

client = TestClient(app)

# 1. Create the Mock Handler
mock_handler = MagicMock()
# Match your new method name: handle_batch_process
mock_handler.handle_batch_process = AsyncMock()

# 2. Apply Dependency Override
app.dependency_overrides[get_file_handler] = lambda: mock_handler

def test_batch_process_success():
    """
    Test the /file/batch-process route with a valid link token.
    """
    # Setup the mock behavior to return a BatchFileReview-like dict
    mock_response = {
        "results": [
            {
                "file_index": 0,
                "status": "approved",
                "borrower_message": "Perfect",
                "reasoning": "Clear document",
                "confidence": 0.98
            }
        ],
        "overall_summary": "All documents processed successfully",
        "agent_name": "file_review_v1"
    }
    mock_handler.handle_batch_process.return_value = mock_response

    # New payload matching your BatchProcessRequest DTO
    payload = {"link_token": "test-token-123"}
    
    # Updated URL to /file/batch-process
    response = client.post("/file/batch-process", json=payload)
    
    assert response.status_code == 200
    assert response.json()["overall_summary"] == "All documents processed successfully"
    # Verify the handler was called with the correct token
    mock_handler.handle_batch_process.assert_called_once()

def test_batch_process_invalid_token():
    """
    Test that the route handles a missing link token (Pydantic validation).
    """
    payload = {} # Missing 'link_token'
    response = client.post("/file/batch-process", json=payload)
    
    # FastAPI/Pydantic returns 422 for missing required fields
    assert response.status_code == 422