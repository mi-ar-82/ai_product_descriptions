# File: test_TC05.py
import datetime
import pytest
from fastapi.testclient import TestClient
from app.main import app  # Adjust the import as needed
from app.users import get_user_manager
from app.models.user import User


# Create a dummy user manager to simulate a successful login
class DummyUserManager:
    async def authenticate(self, credentials: dict):
        # Return a dummy user object with minimal required attributes
        return User(
            id = 1,
            email = credentials["email"],
            hashed_password = "dummy",  # This value is irrelevant for the test
            is_active = True,
            is_superuser = False,
            is_verified = True,
            created_at = datetime.datetime.utcnow(),
            updated_at = datetime.datetime.utcnow()
        )


# Override the dependency to always return our dummy manager
async def override_get_user_manager():
    return DummyUserManager()


client = TestClient(app)


def test_post_login_with_valid_credentials():
    """
    Test that POST /login with valid credentials logs in the user
    and results in an appropriate redirect.
    """
    # Override the real user manager with our dummy manager for the duration of this test.
    app.dependency_overrides[get_user_manager] = override_get_user_manager

    login_data = {
        "email": "valid@example.com",
        "password": "validpassword"
    }
    # Send the POST request with follow_redirects disabled
    response = client.post("/login", data = login_data, follow_redirects = False)

    # Verify the response is a redirect, either 302 or 303.
    assert response.status_code in (302, 303), (
        f"Expected a redirect status code (302/303) but got {response.status_code}"
    )

    # Ensure a Location header is present indicating the redirect target.
    assert "location" in response.headers, "Expected a Location header for redirect."

    # Optionally, check for a session cookie if set by your auth system.
    # For example, if your implementation sets a cookie named 'session':
    # assert response.cookies.get("session"), "Expected a 'session' cookie after login"

    # Clean up the dependency override
    app.dependency_overrides.pop(get_user_manager, None)
