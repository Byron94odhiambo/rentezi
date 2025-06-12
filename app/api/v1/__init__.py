# app/api/v1/__init__.py
from fastapi import APIRouter
from .auth import router as auth_router
from .properties import router as properties_router
from .units import router as units_router
from .assignments import router as assignments_router
from .payments import router as payments_router
from .maintenance import router as maintenance_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(properties_router, prefix="/properties", tags=["Properties"])
api_router.include_router(units_router, prefix="", tags=["Units"])  # Combined with properties
api_router.include_router(assignments_router, prefix="/assignments", tags=["Assignments"])
api_router.include_router(payments_router, prefix="/payments", tags=["Payments"])
api_router.include_router(maintenance_router, prefix="/maintenance", tags=["Maintenance"])