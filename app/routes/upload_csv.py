# File: app/routes/upload_csv.py
from fastapi import APIRouter, UploadFile, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from io import StringIO
import pandas as pd
import os
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


# File: app/routes/upload_csv.py

@router.post("/upload-csv")
async def upload_csv(
        file: UploadFile,
        user: User = Depends(basic_auth),
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
        csv_content = contents.decode("utf-8")

        # Save original file for later retrieval
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp")
        os.makedirs(temp_dir, exist_ok = True)
        file_path = os.path.join(temp_dir, f"{uploaded_file.id}_{file.filename}")

        print(f"Debug: Saving original file to {file_path}")
        with open(file_path, "w", encoding = "utf-8") as f:
            f.write(csv_content)

        # Continue processing as before
        df = pd.read_csv(StringIO(csv_content), dtype = str)
        print("Debug: CSV read with string conversion")
        print(f"Data types after read:\n{df.dtypes}")
        print(f"Debug: CSV file read successfully with {len(df)} rows")

        # Filter for rows with non-null Titles (actual products, not variants)
        total_rows = len(df)
        product_df = df[df["Title"].notna() & (df["Title"] != "")]
        product_count = len(product_df)
        variant_count = total_rows - product_count

        print(f"Debug: Found {product_count} products and {variant_count} variants in CSV")

        # Convert only products to list of dicts
        raw_data = product_df.replace({pd.NA: None}).to_dict("records")
        print(f"Debug: Processing {len(raw_data)} product rows (excluding variants)")

        # Create products (only for rows with Title values)
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

        print(f"Debug: Products to add: {len(products)}")
        if products:
            print(f"Debug: First product handle: {products[0].handle}")
        session.add_all(products)
        await session.commit()
        print(f"Debug: {len(products)} products added to the database")

        # Store success message in session or use query parameter for redirect
        from fastapi.responses import RedirectResponse
        from urllib.parse import quote

        success_message = f"Successfully processed {len(products)} products (excluded {variant_count} variants)"
        return RedirectResponse(
            url = f"/dashboard?message={quote(success_message)}",
            status_code = 303
        )

    except ValidationError as e:
        print(f"Debug: CSV validation failed: {e}")
        from fastapi.responses import RedirectResponse
        return RedirectResponse(
            url = "/dashboard?error=CSV validation failed",
            status_code = 303
        )
    except pd.errors.EmptyDataError:
        print("Debug: Empty CSV file detected")
        from fastapi.responses import RedirectResponse
        return RedirectResponse(
            url = "/dashboard?error=Empty CSV file",
            status_code = 303
        )
    except Exception as e:
        print(f"Debug: CSV processing error: {e}")
        import traceback
        traceback.print_exc()
        from fastapi.responses import RedirectResponse
        return RedirectResponse(
            url = f"/dashboard?error={quote(str(e))}",
            status_code = 303
        )
