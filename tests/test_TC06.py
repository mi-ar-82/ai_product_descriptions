# File: test_TC06.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.users import get_user_manager

client = TestClient(app)


def test_post_login_with_invalid_credentials():
    """
    Test that POST /login with invalid credentials returns an error message indicating "Invalid credentials".
    """

    # Define a dummy user manager that always fails authentication.
    class DummyUserManagerInvalid:
        async def authenticate(self, credentials: dict):
            # Simulate failed authentication by always returning None.
            return None

    async def override_get_user_manager_invalid():
        return DummyUserManagerInvalid()

    # Override the dependency with our dummy manager for this test.
    app.dependency_overrides[get_user_manager] = override_get_user_manager_invalid

    # Provide invalid login credentials.
    login_data = {
        "email": "invalid@example.com",
        "password": "wrongpassword"
    }

    # Send a POST request to the login endpoint.
    response = client.post("/login", data = login_data)

    # Verify that the response status code is 200 since the page re-renders with an error message.
    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"

    # Check that the rendered HTML contains the expected error message.
    html_content = response.text
    assert "Invalid credentials" in html_content, "Expected error message 'Invalid credentials' not found in response"

    # Clean up the dependency override.
    app.dependency_overrides.pop(get_user_manager, None)
