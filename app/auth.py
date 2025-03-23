# File: app/auth.py
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.db import get_async_session
from app.models.user import User
from fastapi_users.password import PasswordHelper

security = HTTPBasic()
password_helper = PasswordHelper()

async def basic_auth(
    credentials: HTTPBasicCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session)
):
    print(f"Debug: Attempting basic authentication for user: {credentials.username}")
    stmt = select(User).where(User.email == credentials.username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    verified, _ = password_helper.verify_and_update(credentials.password, user.hashed_password)
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    print(f"Debug: Password verification successful for user: {user.email}")
    print(f"Debug: Authenticated user ID: {user.id}")
    print(f"Debug: Return type: {type(user)}")
    print(f"Debug: User object: {user}")
    return user
