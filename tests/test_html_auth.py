import unittest
from fastapi import status, Form, Request, Depends
from fastapi.testclient import TestClient
from app.main import app
from app.users import get_user_manager, UserCreate

# Dummy user manager to simulate a successful registration without external dependencies.
class DummyUserManager:
    async def create_user(self, user_create: UserCreate):
        # Return a dummy user record (you could add more properties if needed)
        return {"id": 1, "email": user_create.email}

class TestHTMLAuthRoutes(unittest.TestCase):
    def setUp(self):
        # Create a TestClient instance for the FastAPI app.
        self.client = TestClient(app)

    def test_get_login_page(self):
        # Verify that the login page renders correctly.
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Login", response.text)

    def test_get_register_page(self):
        # Verify that the register page renders correctly.
        response = self.client.get("/register")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Register", response.text)

    def test_post_register_success(self):
        # Override the dependency for user registration with a dummy manager.
        app.dependency_overrides[get_user_manager] = lambda: DummyUserManager()

        # Simulate a POST request for user registration.
        response = self.client.post(
            "/register",
            data={"email": "dummy@example.com", "password": "dummy123"},
            follow_redirects = False  # Prevent automatic redirection
        )
        # Expect a redirect to the login page indicating successful registration.
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.headers.get("location"), "/login")

        # Remove the override for subsequent tests.
        app.dependency_overrides.pop(get_user_manager)

    def test_post_login_redirect(self):
        # Test the login POST endpoint. This stub should redirect to the home page.
        response = self.client.post(
            "/login",
            data={"email": "dummy@example.com", "password": "dummy123"},
            follow_redirects = False  # Prevent automatic redirection
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.headers.get("location"), "/")

if __name__ == "__main__":
    unittest.main()
