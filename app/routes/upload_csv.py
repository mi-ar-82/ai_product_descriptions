# File: app/routes/upload_csv.py
from fastapi import APIRouter, UploadFile, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from io import StringIO
import pandas as pd
import logging
from pydantic import ValidationError
from app.services.csv_validation import validate_csv_rows
from app.models import Product
from app.db import get_async_session
from ..services.csv_parser import parse_csv
from app.models import UploadedFile
from app.auth import basic_auth  # Missing import causing NameError
from app.models.user import User  # Required for type hinting



router = APIRouter()


@router.post("/upload-csv")
async def upload_csv(
        file: UploadFile,
        user: User = Depends(basic_auth),  # Add authenticated user dependency
        session: AsyncSession = Depends(get_async_session),
):
    print(f"Debug: Upload initiated by user {user.id}")
    print("Debug: CSV file upload endpoint accessed")
    try:
        # Create UploadedFile record first
        uploaded_file = UploadedFile(
            user_id = user.id,
            file_name = file.filename,
            status = "Processing",
        )
        session.add(uploaded_file)
        await session.commit()
        await session.refresh(uploaded_file)  # Get the generated ID

        print(f"Debug: Created UploadedFile ID {uploaded_file.id}")

        # Process CSV
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode("utf-8")),dtype=str)
        print("Debug: CSV read with string conversion")
        print(f"Data types after read:\n{df.dtypes}")  # Debug output
        print(f"Debug: CSV file read successfully with {len(df)} rows")
        parsed_df = parse_csv(df)
        # Convert to list of dicts and validate
        raw_data = df.replace({pd.NA: None}).to_dict("records")
        #print(raw_data)
        #validated_data = validate_csv_rows(raw_data)
        #print(f"Debug: CSV data validated successfully with {len(validated_data)} rows")

        # Create products
        products = [
            Product(
                uploadedfileid = uploaded_file.id,
                user_id = user.id,
                handle = row["Handle"],
                input_title = row["Title"],
                input_body = row["Body (HTML)"],
                input_image = row["Image Src"],
                input_seo_title = row["SEO Title"],
                input_seo_descr = row["SEO Description"],
                status = "Pending",
                created_at = datetime.now(timezone.utc)
            )
            for row in raw_data
        ]

        print(products[0].handle)
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
