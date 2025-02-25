# File: tests/test_TC02.py

from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.auth import basic_auth

# Create an async override for the basic_auth dependency.
async def fake_basic_auth_override():
    return User(
        id=1,
        email="test@example.com",
        hashed_password="dummy-hash",
        is_active=True,
        is_superuser=False,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

# Override the basic_auth dependency with the async override.
app.dependency_overrides[basic_auth] = fake_basic_auth_override

client = TestClient(app)

def test_read_current_user_valid_credentials():
    # Send a GET request to the /auth/me endpoint.
    response = client.get("/auth/me")
    # Validate that the response status code is 200.
    assert response.status_code == 200
    data = response.json()
    # Validate that the response contains the expected dummy user details.
    assert "id" in data
    assert "email" in data
    assert data["id"] == 1
    assert data["email"] == "test@example.com"
