# app/db.py
from app.models import Base

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi import Depends  # Import Depends from FastAPI
from app.config import settings
from sqlalchemy.orm import configure_mappers
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User



configure_mappers()  # Ensure all mappers are set up


# Create the async engine and session maker
engine = create_async_engine(settings.DATABASE_URL, future=True)
print(f"Debug: Engine URL: {engine.url}")  # Add after engine creation

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
print("Debug: Async database engine created")

# Dependency to get an async session
async def get_async_session() -> AsyncSession:
    print("Debug: Creating new async database session")
    async with async_session_maker() as session:
        print("Debug: Async session type:", type(session))
        yield session

# Dependency to get the user database
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    from app.models.user import User  # Lazy import to avoid circular dependency
    yield SQLAlchemyUserDatabase(session, User)


async def init_db():
    print("Debug: Initializing database tables")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
