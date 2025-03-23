from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

# Define SQLAlchemy Base only once in this module
Base = declarative_base()

from .user import User




# UploadedFiles table
class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.now(timezone.utc))
    status = Column(String)

# Products table
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    uploaded_file_id = Column(Integer, ForeignKey("uploaded_files.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Add this line
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    handle = Column(String)
    input_title = Column(String)
    input_body = Column(Text)
    input_image = Column(String)
    input_seo_title = Column(String)
    input_seo_descr = Column(Text)
    base64_filepath = Column(String)
    cleaned_body = Column(Text)
    output_body = Column(Text)
    output_seo_title = Column(String)
    output_seo_descr = Column(Text)

    uploaded_file = relationship("UploadedFile")

# Settings table
class Setting(Base):
    __tablename__ = "settings"
    __table_args__ = (UniqueConstraint("user_id", name = "uq_user_settings"),)

    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    model = Column(String, default = "gpt-4o-mini")
    tone = Column(String)
    temperature = Column(String)
    max_tokens = Column(Integer)
    response_max_length = Column(String)
    base_prompt_type = Column(String, default = "conversion")
    base_default_prompt = Column(Text)
    created_at = Column(DateTime, default = datetime.utcnow)
    updated_at = Column(DateTime, default = datetime.utcnow, onupdate = datetime.utcnow)
    use_base64_image = Column(Boolean, default = False)

    # Relationship to User model
    user = relationship("User", back_populates="settings")


# FailedEntries table
class FailedEntry(Base):
    __tablename__ = "failed_entries"
    id = Column(Integer, primary_key=True)
    uploadedfileid = Column(Integer, ForeignKey("uploaded_files.id"), nullable=False)
    product_title = Column(String)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Logs table
class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String)
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
