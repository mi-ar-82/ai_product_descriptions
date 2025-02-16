import uuid
from fastapi import Depends
from fastapi_users.manager import BaseUserManager
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users import FastAPIUsers
from fastapi_users import schemas
from fastapi_users.schemas import BaseUserCreate
from fastapi_users.password import PasswordHelper

from pydantic import BaseModel, EmailStr



from app.models.user import User  # Your custom user model
from app.db import get_user_db  # Function to get the user database

SECRET_KEY = "your-secret-key"  # Replace with a secure secret key

# JWT Strategy for authentication
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=3600)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# Define Pydantic schemas for user creation and representation
class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True  # Enable ORM mode for using from_orm

class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        orm_mode = True  # Enable ORM mode for using from_orm


password_helper = PasswordHelper()
# User Manager class
class UserManager(BaseUserManager[User, int]):
    async def create_user(self, user_create: UserCreate) -> User:
        hashed_password = password_helper.hash(user_create.password)  # Hash password
        user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
            is_verified=False,
        )
        self.user_db.session.add(user)
        await self.user_db.session.commit()
        return user


# Dependency to provide the UserManager instance
async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

# FastAPIUsers instance without unsupported arguments
fastapi_users = FastAPIUsers[User, int](
    get_user_manager=get_user_manager,
    auth_backends=[auth_backend],
)

current_user = fastapi_users.current_user()
