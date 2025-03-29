# File: app/routes/process_products.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_async_session
from app.auth import basic_auth
from app.models import Product, Setting
from app.services.openai_service import generate_product_description
from app.services.text_utils import convert_markdown_to_html, convert_markdown_to_plain_text
from fastapi.responses import RedirectResponse
from urllib.parse import quote


router = APIRouter()




@router.post("/process-products")
async def start_ai_product_description_generation(
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

        # Fetch products needing processing
        products_result = await session.execute(
            select(Product).where(Product.status == "Pending")
        )
        products_to_process = products_result.scalars().all()
        print(f"Debug: Number of pending products: {len(products_to_process)}")

        if not products_to_process:
            return RedirectResponse(
                url = "/dashboard?message=No products pending processing.",
                status_code = 303
            )

        for product in products_to_process:
            print(f"Debug: Processing product with handle: {product.handle}")
            print(f"Debug: Product data type: {type(product)}")

            # Prepare product info
            product_info = {
                "title": product.input_title,
                "description": product.input_body,
                "image_url": product.input_image
            }

            # Generate content using updated service
            generated_content = await generate_product_description(
                product_info = product_info,
                ai_model = user_settings.ai_model,
                temperature = float(user_settings.temperature),
                max_tokens = user_settings.max_tokens,
                prompt_type = user_settings.base_prompt_type,
                use_base64_image = user_settings.use_base64_image
            )

            ## Convert content and log results for debugging
            html_body = convert_markdown_to_html(generated_content["body_html"])
            print(f"Debug: Converted body_html to HTML: {html_body[:100]}...")  # Log first 100 characters for brevity

            seo_title = convert_markdown_to_plain_text(generated_content["seo_title"])
            print(f"Debug: Converted seo_title to plain text: {seo_title}")

            seo_description = convert_markdown_to_plain_text(generated_content["seo_description"])
            print(f"Debug: Converted seo_description to plain text: {seo_description}")

            # Update product fields
            product.output_body = html_body
            product.output_seo_title = seo_title
            product.output_seo_descr = seo_description
            product.status = "Completed"
            session.add(product)

        await session.commit()

        # Redirect with success message
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
