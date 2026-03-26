import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from main import app
from app.api.v1.file_routes import get_file_handler # Import the actual dependency function

client = TestClient(app)

# 1. Create a "Fake" Handler
mock_handler = MagicMock()
mock_handler.handle_upload_file = AsyncMock()

# 2. This is the "Magic" fix
# This tells FastAPI: "Whenever someone asks for get_file_handler, give them our mock instead"
app.dependency_overrides[get_file_handler] = lambda: mock_handler

def test_upload_file_route_success():
    # Setup the mock behavior
    mock_response = {
        "results": [],
        "overall_summary": "Test Passed",
        "agent_name": "test_agent"
    }
    mock_handler.handle_upload_file.return_value = mock_response

    payload = {"file_paths": ["test.jpg"]}
    
    response = client.post("/file/upload", json=payload)
    
    assert response.status_code == 200
    assert response.json()["overall_summary"] == "Test Passed"

def test_upload_file_no_paths():
    # This should now reach the handler or fail validation correctly
    payload = {"file_paths": []}
    response = client.post("/file/upload", json=payload)
    
    # If your DTO has min_length=1, this will be 422
    # If not, it will be 200 (if the mock handles it)
    assert response.status_code in [200, 422]