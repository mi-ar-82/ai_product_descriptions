# File: app/users.py

from fastapi import Depends
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from pydantic import EmailStr, BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.models.user import User
from fastapi_users.password import PasswordHelper

password_helper = PasswordHelper()

# Schemas for user creation, reading, and updating
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    model_config = ConfigDict(from_attributes=True)

class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None

# User Manager class that handles authentication and user creation.
class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    async def authenticate(self, credentials: dict) -> User | None:
        print(f"Debug: Authenticating user with email: {credentials['email']}")
        user = await self.get_by_email(credentials["email"])
        if user is None:
            return None
        verified, _ = password_helper.verify_and_update(
            credentials["password"],
            user.hashed_password
        )
        if not verified:
            return None
        return user

    async def create(self, user_create: UserCreate) -> User:
        print(f"Debug: Creating new user with email: {user_create.email}")
        hashed_password = password_helper.hash(user_create.password)
        user_dict = user_create.model_dump(exclude={"password"})
        user_dict["hashed_password"] = hashed_password
        return await self.user_db.create(user_dict)

# Dependency to get the user database instance using SQLAlchemy.
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

# Dependency to get the UserManager.
async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)
