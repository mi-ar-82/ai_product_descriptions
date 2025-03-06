from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
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
    uploadedfileid = Column(Integer, ForeignKey("uploaded_files.id"), nullable=False)
    status = Column(String)  # Status of processing (e.g., Success, Failed)
    created_at = Column(DateTime, default=datetime.utcnow)
    handle = Column(String)  # New field for product handle
    input_title = Column(String)  # Original title of the product
    input_body = Column(Text)  # Original body content (HTML)
    input_image = Column(String)  # URL of the input image
    input_seo_title = Column(String)  # Original SEO title
    input_seo_descr = Column(Text)  # Original SEO description
    base64_filepath = Column(String)  # Path to Base64-encoded image
    cleaned_body = Column(Text)  # Cleaned body content (plain text)
    output_body = Column(Text)  # Processed product description
    output_seo_title = Column(String)  # Processed SEO title
    output_seo_descr = Column(Text)  # Processed SEO description

    uploaded_file = relationship("UploadedFile")

# Settings table
class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    photo_resolution = Column(String)
    file_size_limit = Column(String)
    openai_prompt_base = Column(Text)
    tone = Column(String)
    length = Column(String)
    created_at = Column(DateTime, default = datetime.utcnow)
    updated_at = Column(DateTime, default = datetime.utcnow, onupdate = datetime.utcnow)

    # Relationship to User model
    user = relationship("User", back_populates = "settings")

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
