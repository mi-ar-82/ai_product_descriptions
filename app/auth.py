# app/auth.py
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend, BearerTransport

SECRET_KEY = "your-secret-key"  # Use environment variables in production
ACCESS_TOKEN_EXPIRE_MINUTES = 3600

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=SECRET_KEY,
        lifetime_seconds=ACCESS_TOKEN_EXPIRE_MINUTES
    )

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy
)
