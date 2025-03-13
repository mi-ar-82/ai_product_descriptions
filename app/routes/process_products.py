# File: app/routes/process_products.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_async_session
from app.auth import basic_auth
from app.models import Product, Setting
from app.services.openai_service import generate_product_description

router = APIRouter()


@router.post("/process-products")
async def process_products(
    user=Depends(basic_auth),
    session: AsyncSession=Depends(get_async_session)
):
    try:
        # Fetch user's latest settings
        settings_result = await session.execute(
            select(Setting).where(Setting.user_id == user.id).order_by(Setting.updated_at.desc())
        )
        user_settings = settings_result.scalar_one_or_none()

        if not user_settings:
            raise HTTPException(status_code=400, detail="User settings not configured.")

        # Fetch products needing processing (status='Pending')
        products_result = await session.execute(
            select(Product).where(Product.status == "Pending")
        )
        products_to_process = products_result.scalars().all()
        print("Debug: Number of pending products:", len(products_to_process))
        print("Debug: Pending products data type:", type(products_to_process))

        if not products_to_process:
            return {"message": "No products pending processing."}

        for product in products_to_process:
            print("Debug: Processing product with handle:", product.handle)
            print("Debug: Product data type:", type(product))
            # Construct messages array with detail: low for images
            messages = [
                {"role": "user", "content": user_settings.base_default_prompt},
                {"role": "user", "content": f"Product Title: {product.input_title}"},
                {"role": "user", "content": f"Existing Description: {product.input_body}"}
            ]

            # Include image with hardcoded detail: low
            if product.input_image:
                messages_with_image = {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Analyze the following product image and generate a description."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": product.input_image,
                                "detail": "low"
                            }
                        }
                    ]
                }
                messages = messages_with_image
            else:
                messages_with_image = {"role": "user", "content": prompt}

            print("Debug: Messages prepared for OpenAI:", messages_with_image)
            print("Debug: Data type of messages_with_image:", type(messages_with_image))

            # Generate description using OpenAI API
            generated_description = await generate_product_description(
                prompt=messages_with_image,
                model=user_settings.model,
                temperature=float(user_settings.temperature),
                max_tokens=user_settings.max_tokens,
            )

            # Update product with generated description and mark as completed
            product.output_body = generated_description
            product.status = "Completed"
            session.add(product)

        await session.commit()
        print("Debug: Commit successful after processing products.")
        return {"message": f"Successfully processed {len(products_to_process)} products."}

    except Exception as e:
        print(f"Error processing products: {e}")
        raise HTTPException(status_code=500, detail=str(e))
