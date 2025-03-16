# File: app/routes/process_products.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_async_session
from app.auth import basic_auth
from app.models import Product, Setting
from app.services.openai_service import generate_product_description
from fastapi.responses import RedirectResponse
from urllib.parse import quote

router = APIRouter()


@router.post("/process-products")
async def process_products(
        user = Depends(basic_auth),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        # Fetch user's latest settings
        settings_result = await session.execute(
            select(Setting).where(Setting.user_id == user.id).order_by(Setting.updated_at.desc())
        )
        user_settings = settings_result.scalar_one_or_none()

        if not user_settings:
            return RedirectResponse(
                url = "/dashboard?error=User settings not configured.",
                status_code = 303
            )

        # Fetch products needing processing (status='Pending')
        products_result = await session.execute(
            select(Product).where(Product.status == "Pending")
        )
        products_to_process = products_result.scalars().all()
        print("Debug: Number of pending products:", len(products_to_process))
        print("Debug: Pending products data type:", type(products_to_process))

        if not products_to_process:
            return RedirectResponse(
                url = "/dashboard?message=No products pending processing.",
                status_code = 303
            )

        for product in products_to_process:
            print("Debug: Processing product with handle:", product.handle)
            print("Debug: Product data type:", type(product))

            # Create properly formatted messages for OpenAI
            if product.input_image:
                # Properly structure multimodal content
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_settings.base_default_prompt},
                            {"type": "text", "text": f"Product Title: {product.input_title}"},
                            {"type": "text", "text": f"Existing Description: {product.input_body}"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": product.input_image,
                                    "detail": "low"
                                }
                            }
                        ]
                    }
                ]
            else:
                # For text-only products
                messages = [
                    {
                        "role": "user",
                        "content": f"{user_settings.base_default_prompt}\n\nProduct Title: {product.input_title}\n\nExisting Description: {product.input_body}"
                    }
                ]

            print("Debug: Messages prepared for OpenAI:", messages)
            print("Debug: Data type of messages:", type(messages))

            # Generate description using OpenAI API
            generated_description = await generate_product_description(
                messages = messages,
                model = user_settings.model,
                temperature = float(user_settings.temperature),
                max_tokens = user_settings.max_tokens,
            )

            # Update product fields
            product.output_body = generated_description
            product.output_seo_title = product.input_title  # Using input title as SEO title
            product.output_seo_descr = generated_description[
                                       :160] if generated_description else ""  # First 160 chars for SEO description
            product.status = "Completed"
            session.add(product)

        await session.commit()
        print("Debug: Commit successful after processing products.")

        # Redirect to dashboard with success message instead of returning JSON
        success_message = f"Successfully processed {len(products_to_process)} products."
        return RedirectResponse(
            url = f"/dashboard?message={quote(success_message)}",
            status_code = 303
        )

    except Exception as e:
        print(f"Error processing products: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(
            url = f"/dashboard?error={quote(str(e))}",
            status_code = 303
        )
