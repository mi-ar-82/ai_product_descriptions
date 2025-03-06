# File: app/models/user.py
from app.models import Base

from sqlalchemy import Column, String, Boolean, DateTime, Integer
from datetime import datetime
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy.orm import relationship
from pydantic import ConfigDict


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    model_config = ConfigDict(from_attributes = True)

    id = Column(Integer, primary_key = True)
    email = Column(String(320), unique = True, index = True)
    hashed_password = Column(String(1024))
    is_active = Column(Boolean, default = True)
    is_superuser = Column(Boolean, default = False)
    is_verified = Column(Boolean, default = False)
    created_at = Column(DateTime, default = datetime.utcnow)
    updated_at = Column(DateTime, default = datetime.utcnow, onupdate = datetime.utcnow)

    settings = relationship("Setting", back_populates = "user")

print("Debug: User model defined")
