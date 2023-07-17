from fastapi import APIRouter
from app.http.endpoints import pnn, tenant

router = APIRouter()
router.include_router(pnn.router)
router.include_router(tenant.router)