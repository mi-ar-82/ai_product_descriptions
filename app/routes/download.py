# File: app/routes/download.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
from io import StringIO
from datetime import datetime
import os
from app.models import Product, UploadedFile
from app.db import get_async_session
from app.auth import basic_auth

router = APIRouter()


@router.get("/download/products_output/{uploaded_file_id}.csv", name="download_products_output")
async def download_products_output(
        uploaded_file_id: int,
        user = Depends(basic_auth),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        # Verify the file belongs to this user and get filename
        file_result = await session.execute(
            select(UploadedFile).where(
                (UploadedFile.id == uploaded_file_id) &
                (UploadedFile.user_id == user.id)
            )
        )
        uploaded_file = file_result.scalar_one_or_none()

        if not uploaded_file:
            raise HTTPException(status_code = 404, detail = "File not found or access denied.")

        # Fetch processed products for this specific file only
        result = await session.execute(
            select(Product).where(
                (Product.uploaded_file_id == uploaded_file_id) &
                (Product.status == "Completed")
            )
        )
        processed_products = result.scalars().all()
        print(f"Debug: Retrieved {len(processed_products)} processed products")

        if not processed_products:
            raise HTTPException(status_code=404, detail="No processed products found.")

        # Get the uploaded file ID from the first product
        uploaded_file_id = processed_products[0].uploaded_file_id

        # Query the UploadedFile to get the filename
        file_result = await session.execute(
            select(UploadedFile).where(UploadedFile.id == uploaded_file_id)
        )
        uploaded_file = file_result.scalar_one_or_none()
        print(f"Debug: UploadedFile retrieved: {uploaded_file.file_name if uploaded_file else 'None'}")

        if not uploaded_file:
            raise HTTPException(status_code=404, detail="Original file information not found.")

        # Define temporary storage path
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        original_file_path = os.path.join(temp_dir, f"{uploaded_file.id}_{uploaded_file.file_name}")
        print(f"Debug: Looking for original file at {original_file_path}")




        # Try to load the original file if it exists
        original_df = None
        if os.path.exists(original_file_path):
            try:
                print(f"Debug: Found original file at {original_file_path}")
                original_df = pd.read_csv(original_file_path, encoding = "utf-8")
                print(
                    f"Debug: Original CSV loaded with UTF-8 encoding, {len(original_df)} rows and {len(original_df.columns)} columns")
            except Exception as e:
                print(f"Debug: Error reading original file with UTF-8: {e}")
                # Try with different encoding as fallback
                try:
                    print("Debug: Retrying with 'latin-1' encoding")
                    original_df = pd.read_csv(original_file_path, encoding = "latin-1")
                    print(f"Debug: Original CSV loaded with latin-1 encoding")
                except Exception as retry_e:
                    print(f"Debug: Retry also failed: {retry_e}")

        # If original file not found, create dataframe from database
        if original_df is None:
            print("Debug: Original file not found, fetching all products from database")
            all_products_result = await session.execute(
                select(Product).where(Product.uploaded_file_id == uploaded_file_id)
            )
            all_products = all_products_result.scalars().all()
            print(f"Debug: Retrieved {len(all_products)} total products from database")

            # Create dataframe with available columns
            data = []
            for product in all_products:
                data.append({
                    "Handle": product.handle,
                    "Title": product.input_title,
                    "Body HTML": product.input_body,
                    "Image Src": product.input_image,
                    "SEO Title": product.input_seo_title,
                    "SEO Description": product.input_seo_descr
                })
            original_df = pd.DataFrame(data)
            print(f"Debug: Created dataframe from database with {len(original_df)} rows")

        # Create mapping of handles to processed content
        processed_data_map = {
            p.handle: {
                "Body HTML": p.output_body,
                "SEO Title": p.output_seo_title,
                "SEO Description": p.output_seo_descr
            } for p in processed_products
        }
        print(f"Debug: Created mapping for {len(processed_data_map)} processed products")

        # Update the original dataframe with processed content
        # Handle different possible column names (Body HTML vs Body (HTML))
        body_column = None
        if "Body HTML" in original_df.columns:
            body_column = "Body HTML"
        elif "Body (HTML)" in original_df.columns:
            body_column = "Body (HTML)"

        updated_count = 0
        for idx, row in original_df.iterrows():
            handle = row.get("Handle")
            # Only update rows that have non-empty Title (actual products, not variants)
            title = row.get("Title")
            has_title = pd.notna(title) and str(title).strip() != ""

            if handle in processed_data_map and has_title:
                # Update the body column if it exists
                if body_column:
                    original_df.at[idx, body_column] = processed_data_map[handle]["Body HTML"]

                # Update SEO columns if they exist
                if "SEO Title" in original_df.columns:
                    original_df.at[idx, "SEO Title"] = processed_data_map[handle]["SEO Title"]

                if "SEO Description" in original_df.columns:
                    original_df.at[idx, "SEO Description"] = processed_data_map[handle]["SEO Description"]

                updated_count += 1

        print(f"Debug: Updated {updated_count} product rows in the dataframe (skipped variants)")

        # Convert to CSV
        csv_buffer = StringIO()
        # Add UTF-8 BOM to help Excel recognize the encoding
        csv_buffer.write('\ufeff')
        original_df.to_csv(csv_buffer, index = False, encoding = "utf-8")

        csv_buffer.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        headers = {
            'Content-Disposition': f'attachment; filename="products_output_{timestamp}.csv"',
            'Content-Type': 'text/csv; charset=utf-8'  # Explicitly set UTF-8 in Content-Type
        }

        print("Debug: Returning CSV response with UTF-8 encoding and BOM")
        return StreamingResponse(csv_buffer, media_type = "text/csv", headers = headers)

    except Exception as e:
        print(f"Debug: Error generating CSV: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
