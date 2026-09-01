"""
Main API router aggregator.
Combines all sub-routers into a single router.
"""

from fastapi import APIRouter

from app.api.logs import router as logs_router
from app.api.dashboard import router as dashboard_router

api_router = APIRouter()

# Log ingestion endpoints
api_router.include_router(logs_router, prefix="/logs", tags=["Logs"])

# Dashboard data endpoints
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
