# File: app/routes/__init__.py
from fastapi import APIRouter



# Import routers lazily to avoid circular dependencies
router = APIRouter()

def include_routers():
    from app.routes.html_auth import router as auth_router
    from app.routes.upload_csv import router as upload_csv_router
    from app.routes.dashboard import router as dashboard_router
    from app.routes.download import router as download_router
    from app.routes.process_products import router as process_products_router

    # Include all routers here
    router.include_router(auth_router, tags=["Authentication"])
    router.include_router(upload_csv_router, tags=["CSV Upload"])
    router.include_router(dashboard_router, tags=["Dashboard"])
    router.include_router(download_router, tags=["Download"])
    router.include_router(process_products_router, tags=["Process Products"])

include_routers()
