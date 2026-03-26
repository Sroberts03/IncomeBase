import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from main import app
from app.api.v1.file_routes import get_file_handler

client = TestClient(app)

# 1. Create the Mock Handler
mock_handler = MagicMock()

# FIX 1: Change to handle_submit_files to match your route's internal call
mock_handler.handle_submit_files = AsyncMock()
mock_handler.handle_analyze_files = AsyncMock()

# 2. Apply Dependency Override
app.dependency_overrides[get_file_handler] = lambda: mock_handler


def test_submit_files_success():
    """
    Test the /file/submit_files route with a valid link token.
    """
    # Good practice: reset the mock in case tests run out of order
    mock_handler.handle_submit_files.reset_mock()

    # Setup the mock behavior to return a BatchFileReview-like dict
    mock_response = {
        "results": [
            {
                # FIX 2: Updated from 'file_index' to 'file_id' to match your schema
                "file_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "approved",
                "borrower_message": "Perfect",
                "reasoning": "Clear document",
                "confidence": 0.98
            }
        ],
        "overall_summary": "All documents processed successfully",
        "agent_name": "file_review_v1"
    }
    
    # FIX 3: Attach the return value to the correct method
    mock_handler.handle_submit_files.return_value = mock_response

    # Payload matching your SubmitFilesRequest DTO
    payload = {"link_token": "test-token-123"}
    
    response = client.post("/file/submit_files", json=payload)
    
    assert response.status_code == 200
    assert response.json()["overall_summary"] == "All documents processed successfully"
    
    # FIX 4: Assert on the correct method
    mock_handler.handle_submit_files.assert_called_once()


def test_submit_files_invalid_token():
    """
    Test that the route handles a missing link token (Pydantic validation).
    """
    payload = {} # Missing 'link_token'
    response = client.post("/file/submit_files", json=payload)
    
    # FastAPI/Pydantic returns 422 for missing required fields
    assert response.status_code == 422


def test_analyze_files_success():
    """
    Test the /file/analyze_files route with a valid borrower_id.
    """
    mock_handler.handle_analyze_files.reset_mock()

    mock_response = {
        "message": "Analysis complete",
        "approved": True,
        "retries": 1
    }
    mock_handler.handle_analyze_files.return_value = mock_response

    payload = {"borrower_id": "borrower-123"}
    response = client.post("/file/analyze_files", json=payload)

    assert response.status_code == 200
    assert response.json()["message"] == "Analysis complete"
    assert response.json()["approved"] is True
    assert response.json()["retries"] == 1
    mock_handler.handle_analyze_files.assert_called_once()


def test_analyze_files_no_files():
    """
    Test the /file/analyze_files route when no files are available for analysis.
    """
    mock_handler.handle_analyze_files.reset_mock()

    mock_response = {"message": "No processed files to analyze."}
    mock_handler.handle_analyze_files.return_value = mock_response

    payload = {"borrower_id": "borrower-empty"}
    response = client.post("/file/analyze_files", json=payload)

    assert response.status_code == 200
    assert response.json()["message"] == "No processed files to analyze."
    mock_handler.handle_analyze_files.assert_called_once()


def test_analyze_files_invalid_payload():
    """
    Test that the route handles a missing borrower_id (Pydantic validation).
    """
    payload = {} # Missing 'borrower_id'
    response = client.post("/file/analyze_files", json=payload)
    
    # FastAPI/Pydantic returns 422 for missing required fields
    assert response.status_code == 422

def test_analyze_files_wrong_type():
    """
    Test that the route handles an invalid type for borrower_id.
    """
    # To truly test validation, we send a complex object.
    payload = {"borrower_id": {"nested": "value"}}
    response = client.post("/file/analyze_files", json=payload)
    assert response.status_code == 422

def test_analyze_files_empty_string():
    """
    Test the /file/analyze_files route with an empty string as borrower_id.
    Pydantic will accept this as a valid string unless restricted.
    """
    mock_handler.handle_analyze_files.reset_mock()
    mock_handler.handle_analyze_files.return_value = {"message": "Invalid borrower ID"}
    
    payload = {"borrower_id": ""}
    response = client.post("/file/analyze_files", json=payload)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Invalid borrower ID"
    mock_handler.handle_analyze_files.assert_called_once()
