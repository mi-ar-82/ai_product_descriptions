# app/db.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi import Depends  # Import Depends from FastAPI
from app.config import settings
from app.models.user import User
from app.models import Base


# Create the async engine and session maker
engine = create_async_engine(settings.DATABASE_URL, future=True)
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency to get an async session
async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

# Dependency to get the user database
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
