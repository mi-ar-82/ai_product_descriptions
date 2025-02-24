# File: app/routes/download.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/download/products_output.csv")
async def download_products_output():
    # Stub for providing a downloadable CSV of successfully processed product descriptions
    pass

@router.get("/download/products_not_processed.csv")
async def download_products_not_processed():
    # Stub for providing a downloadable CSV of products that failed processing
    pass
