# File: tests/test_TC01.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    # Send a GET request to the root endpoint
    response = client.get("/")
    # Assert that the response status code is 200
    assert response.status_code == 200
    # Assert that the response contains the expected welcome message
    data = response.json()
    assert "message" in data
    assert data["message"] == "Welcome to the AI Product Descriptions App"
