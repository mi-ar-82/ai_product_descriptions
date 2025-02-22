# Filename: app/routes/upload_csv.py

from fastapi import APIRouter, UploadFile, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from io import StringIO
import pandas as pd
from app.db import get_async_session
from app.models import Product  # Assuming Product is your SQLAlchemy model

router = APIRouter()


@router.post("/upload-csv")
async def upload_csv(
        file: UploadFile,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Endpoint to upload and process a CSV file.

    Args:
        file (UploadFile): The uploaded CSV file.
        session (AsyncSession): Database session dependency.

    Returns:
        dict: Success message with details about processed rows.

    Raises:
        HTTPException: If required columns are missing or validation fails.
    """
    try:
        # Read the uploaded file
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode("utf-8")))

        # Validate required columns
        required_columns = {"Handle", "Title", "Body (HTML)", "Image Src", "SEO Title", "SEO Description"}
        if not required_columns.issubset(df.columns):
            missing_columns = required_columns - set(df.columns)
            raise HTTPException(status_code = 400, detail = f"Missing required columns: {missing_columns}")

        # Prepare products for database insertion
        products = []
        for _, row in df.iterrows():
            # Validate each row (optional)
            if pd.isnull(row["Handle"]) or pd.isnull(row["Title"]):
                continue  # Skip rows with missing critical data

            product = Product(
                handle = row["Handle"],
                input_title = row["Title"],
                input_body = row["Body (HTML)"],
                input_image = row["Image Src"],
                input_seo_title = row["SEO Title"],
                input_seo_descr = row["SEO Description"],
                status = "Pending",
                created_at = datetime.utcnow(),
            )
            products.append(product)

        # Add all products to the database in bulk
        session.add_all(products)
        await session.commit()

        return {"message": f"CSV processed successfully. {len(products)} rows added."}

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"An error occurred while processing the file: {str(e)}")
