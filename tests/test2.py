import unittest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import get_async_session
from app.models import Base

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create a test-specific async engine and session maker
test_engine = create_async_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession
)

# Override dependency to use the test database session
async def override_get_async_session():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session

class TestAPI(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Set up the database before each test
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        self.client = TestClient(app)

    async def asyncTearDown(self):
        # Clean up the database after each test
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Welcome to the AI Product Descriptions App"})

    async def test_user_registration(self):
        test_user = {"email": "test@example.com", "password": "testpass123"}
        response = self.client.post("/auth/register", json=test_user)
        self.assertEqual(response.status_code, 201)

        # Check if the user can register again with the same email
        response = self.client.post("/auth/register", json=test_user)
        self.assertEqual(response.status_code, 400)

    async def test_login(self):
        test_user = {"email": "test@example.com", "password": "testpass123"}
        self.client.post("/auth/register", json=test_user)

        # Correct login credentials
        login_response = self.client.post("/auth/jwt/login", data={
            "username": test_user["email"],
            "password": test_user["password"]
        })
        self.assertEqual(login_response.status_code, 200)

        # Incorrect password
        login_response = self.client.post("/auth/jwt/login", data={
            "username": test_user["email"],
            "password": "wrongpassword"
        })
        self.assertEqual(login_response.status_code, 400)

    async def test_upload_csv(self):
        # Register and login a user to get an access token
        test_user = {"email": "test@example.com", "password": "testpass123"}
        self.client.post("/auth/register", json=test_user)
        login_response = self.client.post("/auth/jwt/login", data={
            "username": test_user["email"],
            "password": test_user["password"]
        })
        access_token = login_response.json()["access_token"]

        # Valid CSV upload
        with open("valid.csv", "rb") as f:
            response = self.client.post("/upload-csv", files={"file": ("valid.csv", f, "text/csv")}, headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(response.status_code, 200)

        # Invalid file format
        with open("invalid.txt", "rb") as f:
            response = self.client.post("/upload-csv", files={"file": ("invalid.txt", f, "text/plain")}, headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(response.status_code, 400)

        # Missing required columns
        with open("missing_columns.csv", "rb") as f:
            response = self.client.post("/upload-csv", files={"file": ("missing_columns.csv", f, "text/csv")}, headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
