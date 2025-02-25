# File: test_TC07.py
import pytest
from fastapi.testclient import TestClient
from app.main import app  # Adjust the import to match your project structure

client = TestClient(app)


def test_get_register_page():
    """
    Test that GET /register correctly renders the registration page.
    """
    # Send a GET request to the register endpoint.
    response = client.get("/register")

    # Verify that the response status code is 200 (OK).
    assert response.status_code == 200, "Expected status code 200 for GET /register"

    # Check that the Content-Type header indicates HTML content.
    content_type = response.headers.get("content-type", "")
    assert "text/html" in content_type, "Expected content type to include 'text/html'"

    # Verify that the rendered HTML contains key elements for a registration page.
    html_content = response.text
    assert "<form" in html_content, "Expected a <form> tag in the registration page HTML"
    assert "Register" in html_content or "Sign Up" in html_content, "Expected 'Register' or 'Sign Up' text in the registration page HTML"
