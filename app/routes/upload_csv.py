# File: app/routes/upload_csv.py
from fastapi import APIRouter, UploadFile, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from io import StringIO
import pandas as pd
import logging
from pydantic import ValidationError
from app.services.csv_validation import validate_csv_rows
from app.models import Product
from app.db import get_async_session

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload-csv")
async def upload_csv(
        file: UploadFile,
        session: AsyncSession = Depends(get_async_session),
):
    print("Debug: CSV file upload endpoint accessed")
    try:
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode("utf-8")))
        print(f"Debug: CSV file read successfully with {len(df)} rows")

        # Convert to list of dicts and validate
        raw_data = df.replace({pd.NA: None}).to_dict("records")
        validated_data = validate_csv_rows(raw_data)
        print(f"Debug: CSV data validated successfully with {len(validated_data)} rows")

        # Create products
        products = [
            Product(
                handle = row.handle,
                input_title = row.input_title,
                input_body = row.input_body,
                input_image = row.input_image,
                input_seo_title = row.input_seo_title,
                input_seo_descr = row.input_seo_descr,
                status = "Pending",
                created_at = datetime.utcnow()
            )
            for row in validated_data
        ]

        session.add_all(products)
        await session.commit()
        print(f"Debug: {len(products)} products added to the database")

        return {"message": f"Successfully processed {len(products)} products"}

    except ValidationError as e:
        logger.error(f"CSV validation failed: {e}")
        raise HTTPException(422, detail = e.errors())
    except pd.errors.EmptyDataError:
        raise HTTPException(400, "Empty CSV file")
    except Exception as e:
        logger.exception("CSV processing error")
        raise HTTPException(500, str(e))
