# File: app/routes/download.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
from io import StringIO
from app.models import Product
from app.db import get_async_session
from app.auth import basic_auth


router = APIRouter()

@router.get("/download/products_output.csv")
async def download_products_output(
    user=Depends(basic_auth),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Fetch processed products for the current user (status='Completed')
        result = await session.execute(
            select(Product).where(Product.status == "Completed")
        )
        print("Debug: Product query result type:", type(result))
        products = result.scalars().all()
        print("Debug: Retrieved products count:", len(products))
        print("Debug: Products type:", type(products))

        if not products:
            raise HTTPException(status_code=404, detail="No processed products found.")

        # Debug prints
        print(f"Debug: Retrieved {len(products)} processed products from DB.")
        print(type(products))

        # Prepare data for CSV export, replacing input fields with output fields
        data = []
        for product in products:
            data.append({
                "Handle": product.handle,
                "Title": product.input_title,
                "Body HTML": product.output_body,  # replaced from input_body
                "Image Src": product.input_image,
                "SEO Title": product.output_seo_title,  # replaced from input_seo_title
                "SEO Description": product.output_seo_descr  # replaced from input_seo_descr
            })

        print("Debug: Data prepared for CSV:", data[:3])  # print first 3 rows for debug
        print(type(data))

        # Convert to DataFrame and then to CSV string
        df = pd.DataFrame(data)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)

        csv_buffer.seek(0)
        headers = {
            'Content-Disposition': f'attachment; filename="products_output_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        }

        return StreamingResponse(csv_buffer, media_type="text/csv", headers=headers)

    except Exception as e:
        print(f"Error generating CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))
