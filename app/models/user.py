from sqlalchemy import Column, String, Boolean, DateTime, Integer
from datetime import datetime
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable  # Using the integer-based base
from app.models import Base

class User(SQLAlchemyBaseUserTable[int], Base):  # This is the sole definition of User
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
