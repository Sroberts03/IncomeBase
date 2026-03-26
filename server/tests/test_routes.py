import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from main import app
from app.api.v1.file_routes import get_file_handler
from app.api.v1.lender_routes import get_lender_handler
from app.requests_responses.lender_requests_responses import CreateBorrowerRequest, CreateBorrowerResponse
from app.core.get_current_user_id import get_current_user_id

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

    # Setup the mock behavior to return a SubmitFilesResponse-like dict
    mock_response = {
        "status": "success",
        "review_results": [
            {
                "file_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "approved",
                "borrower_message": "Perfect",
                "reasoning": "Clear document",
                "confidence": 0.98
            }
        ],
        "stats": {
            "total_received": 1,
            "approved": 1,
            "rejected": 0,
            "successfully_classified": 1
        },
        "overall_summary": "All documents processed successfully"
    }
    
    # FIX 3: Attach the return value to the correct method
    mock_handler.handle_submit_files.return_value = mock_response

    # Payload matching your SubmitFilesRequest DTO
    payload = {"link_token": "test-token-123", "zip_code": "12345"}
    
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
    app.dependency_overrides[get_current_user_id] = lambda: "lender-123"

    mock_response = {
        "status": "accepted",
        "message": "Analysis started in background.",
        "borrower_id": "borrower-123",
        "approved": True # Added for GenericMessageResponse validation
    }
    mock_handler.handle_analyze_files.return_value = mock_response

    payload = {"borrower_id": "borrower-123"}
    response = client.post("/file/analyze_files", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    mock_handler.handle_analyze_files.assert_called_once()


def test_analyze_files_no_files():
    """
    Test the /file/analyze_files route when no files are available for analysis.
    The trigger should still return 'accepted' if authorized.
    """
    mock_handler.handle_analyze_files.reset_mock()
    app.dependency_overrides[get_current_user_id] = lambda: "lender-123"

    mock_response = {
        "status": "accepted", 
        "message": "Analysis started.",
        "approved": True
    }
    mock_handler.handle_analyze_files.return_value = mock_response

    payload = {"borrower_id": "borrower-empty"}
    response = client.post("/file/analyze_files", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
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
    """
    mock_handler.handle_analyze_files.reset_mock()
    mock_handler.handle_analyze_files.return_value = {
        "status": "error", 
        "message": "Invalid borrower ID", 
        "approved": False
    }
    
    payload = {"borrower_id": ""}
    response = client.post("/file/analyze_files", json=payload)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Invalid borrower ID"
    mock_handler.handle_analyze_files.assert_called_once()


def test_create_borrower_success():
    """
    Test the /lender/create-borrower route with valid input.
    """
    test_user_id = "lender-123"
    mock_lender_handler = MagicMock()
    mock_lender_handler.create_borrower = AsyncMock(return_value=CreateBorrowerResponse(borrower_id="borrower-456"))
    app.dependency_overrides[get_lender_handler] = lambda: mock_lender_handler
    app.dependency_overrides[get_current_user_id] = lambda: test_user_id
    
    payload = {
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "zip_code": "12345"
    }
    response = client.post("/lender/create-borrower", json=payload)
    
    assert response.status_code == 200
    assert response.json()["borrower_id"] == "borrower-456"

def test_generate_link_success():
    mock_lender_handler = MagicMock()
    mock_lender_handler.generate_link = AsyncMock(return_value={"link_token": "t1", "expires_at": "now"})
    app.dependency_overrides[get_lender_handler] = lambda: mock_lender_handler
    app.dependency_overrides[get_current_user_id] = lambda: "l1"
    
    payload = {"borrower_id": "b1"}
    response = client.post("/lender/generate-link", json=payload)
    assert response.status_code == 200
    assert response.json()["link_token"] == "t1"

def test_verify_zip_success():
    mock_lender_handler = MagicMock()
    mock_lender_handler.verify_borrower_zip = AsyncMock(return_value={"valid": True, "message": "Ok"})
    app.dependency_overrides[get_lender_handler] = lambda: mock_lender_handler
    
    payload = {"link_token": "t1", "zip_code": "12345"}
    response = client.post("/lender/verify-zip", json=payload)
    assert response.status_code == 200
    assert response.json()["valid"] is True

def test_dashboard_stats_success():
    mock_lender_handler = MagicMock()
    mock_lender_handler.get_dashboard_stats = AsyncMock(return_value={
        "total_borrowers": 1, "needs_link_creation": 0, "link_created": 0, "docs_submitted": 0, "completed": 1
    })
    app.dependency_overrides[get_lender_handler] = lambda: mock_lender_handler
    app.dependency_overrides[get_current_user_id] = lambda: "l1"
    
    response = client.get("/lender/dashboard-stats")
    assert response.status_code == 200
    assert response.json()["total_borrowers"] == 1

def test_get_borrowers_success():
    mock_lender_handler = MagicMock()
    mock_lender_handler.get_borrowers = AsyncMock(return_value={"borrowers": []})
    app.dependency_overrides[get_lender_handler] = lambda: mock_lender_handler
    app.dependency_overrides[get_current_user_id] = lambda: "l1"
    
    response = client.get("/lender/borrowers")
    assert response.status_code == 200
    assert "borrowers" in response.json()
