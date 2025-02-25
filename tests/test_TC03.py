# File: test_TC03.py
import pytest
from fastapi.testclient import TestClient
# Adjust the import path to match your project structure.
# If your FastAPI app instance is defined in app/main.py, you should import it as shown below.
from app.main import app

client = TestClient(app)


def test_get_authme_with_invalid_credentials():
    """
    Test that GET /authme with an invalid or malformed token returns a 401 Unauthorized error.
    """
    # Send a GET request with an invalid Authorization header.
    response = client.get("/auth/me", headers = {"Authorization": "Bearer invalid-token"})

    # Assert that the response status code is 401 Unauthorized.
    assert response.status_code == 401, "Expected status code 401 for invalid credentials"

    # Verify that the response body includes a 'detail' key with an error message.
    data = response.json()
    assert "detail" in data, "Response should contain a 'detail' key with error information"

    # Optionally, check that the error message is one of the expected ones.
    expected_errors = ["Not authenticated", "Could not validate credentials"]
    assert data["detail"] in expected_errors, "Unexpected error message returned"
