# File: test_TC04.py
import pytest
from fastapi.testclient import TestClient
from app.main import app  # Adjust the import to match your project structure

client = TestClient(app)


def test_get_login_page():
    """
    Test that GET /login properly renders the login page with the expected HTML content.
    """
    # Send a GET request to the login page endpoint.
    response = client.get("/login")

    # Verify that the status code is 200 (OK).
    assert response.status_code == 200, "Expected status code 200 for GET /login"

    # Check that the Content-Type header reflects HTML content.
    content_type = response.headers.get("content-type", "")
    assert "text/html" in content_type, "Expected content-type header to indicate HTML"

    # Verify that the HTML content contains key elements for a login page.
    html_content = response.text
    assert "<form" in html_content, "Expected a <form> tag in the login page HTML"
    assert (
                "Login" in html_content or "Sign In" in html_content), "Expected 'Login' or 'Sign In' text in the login page"
