from fastapi import APIRouter
from app.http.endpoints import pnn, tenant, reviews

router = APIRouter()
router.include_router(pnn.router)
router.include_router(tenant.router)
router.include_router(reviews.router)