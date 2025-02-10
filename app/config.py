# app/config.py
import os

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_product_descriptions.db")

settings = Settings()
