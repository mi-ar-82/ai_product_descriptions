# File: tests/test_TC08.py
import pytest
from html import unescape
from fastapi.testclient import TestClient
from app.main import app
from app.users import get_user_manager

client = TestClient(app)


# Dummy user manager that simulates the specific error when an invalid 'password' keyword is passed.
class DummyUserManagerWithPasswordError:
    async def create(self, user_create):
        # Simulate the bug by raising the specific exception.
        raise Exception("'password' is an invalid keyword argument for User")


# Dependency override for the get_user_manager dependency.
async def override_get_user_manager_with_error():
    return DummyUserManagerWithPasswordError()


def test_post_register_catches_password_field_error():
    """
    Test that POST /register catches the error when the production code passes
    the 'password' field directly to the User model. Instead of crashing, the endpoint
    should re-render the registration page with an appropriate error message.
    """
    # Override the dependency to simulate the error case.
    app.dependency_overrides[get_user_manager] = override_get_user_manager_with_error

    # Provide registration data with a valid email and password.
    registration_data = {
        "email": "erroruser@example.com",
        "password": "somepassword"
    }

    # Send a POST request to /register.
    response = client.post("/register", data = registration_data)

    # The endpoint should catch the exception and re-render the registration page.
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # Decode the HTML content to convert HTML entities to their literal characters.
    html_content = response.text
    decoded_content = unescape(html_content)

    # Check that the decoded HTML contains the expected error message.
    assert "'password' is an invalid keyword argument for User" in decoded_content, (
        "Expected error message not found in the registration page."
    )

    # Clean up the dependency override.
    app.dependency_overrides.pop(get_user_manager, None)
