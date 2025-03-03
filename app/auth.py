# File: app/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_async_session
from app.models.user import User
from fastapi_users.password import PasswordHelper
import secrets

security = HTTPBasic()
password_helper = PasswordHelper()

async def basic_auth(
    credentials: HTTPBasicCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session)
) -> User:
    print(f"Debug: Attempting basic authentication for user: {credentials.username}")
    # Query the database for a user with an email matching the provided username.
    stmt = select(User).where(User.email == credentials.username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    # Verify the password using the password helper (this compares a plain password with the hashed password)
    verified, _ = password_helper.verify_and_update(credentials.password, user.hashed_password)
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    print(f"Debug: Password verification {'successful' if verified else 'failed'} for user: {user.email}")
    print(f"Debug: Authenticated user ID: {user.id}")
    return user
