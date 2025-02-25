# File: test_TC09.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.users import get_user_manager

client = TestClient(app)


# Dummy user manager that simulates a duplicate email error.
class DummyUserManagerDuplicate:
    async def create(self, user_create):
        raise Exception("User with this email already exists")


# Override for get_user_manager that returns the dummy manager.
async def override_get_user_manager_duplicate():
    return DummyUserManagerDuplicate()


def test_post_register_duplicate_email():
    """
    Test that POST /register with a duplicate email fails gracefully
    by re-rendering the registration page with the appropriate error message.
    """
    # Override the dependency to simulate a duplicate email scenario.
    app.dependency_overrides[get_user_manager] = override_get_user_manager_duplicate

    # Provide registration data with a duplicate email.
    registration_data = {
        "email": "duplicate@example.com",
        "password": "anyPassword"
    }

    # Send a POST request to /register.
    response = client.post("/register", data = registration_data)

    # Since the creation fails, expect a 200 status code and the registration page rendered with an error message.
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # Verify that the error message is present in the returned HTML.
    html_content = response.text
    assert "User with this email already exists" in html_content, "Expected duplicate email error message not found"

    # Clean up the dependency override.
    app.dependency_overrides.pop(get_user_manager, None)
