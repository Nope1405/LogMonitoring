"""
Dashboard API endpoints.
Provides aggregated metrics using SQL Window Functions.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.aggregation import AggregationService
from app.schemas.dashboard_schema import DashboardMetrics, AlertResponse

router = APIRouter()


@router.get(
    "/metrics",
    response_model=DashboardMetrics,
    summary="Get dashboard metrics for the last N minutes",
)
async def get_dashboard_metrics(
    minutes: int = Query(default=10, ge=1, le=60, description="Time window in minutes"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns aggregated metrics for the dashboard:
    - Time series data (requests per minute)
    - Total request/error counts
    - Error rate percentage
    - Unique IP count
    """
    service = AggregationService(db)
    return await service.get_dashboard_metrics(minutes)


@router.get(
    "/suspicious-ips",
    summary="Get suspicious IP addresses",
)
async def get_suspicious_ips(
    minutes: int = Query(default=5, ge=1, le=30),
    threshold: int = Query(default=50, ge=10),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns IPs with request counts exceeding the threshold,
    ranked by activity level using Window Functions.
    """
    service = AggregationService(db)
    return await service.get_suspicious_ips(minutes, threshold)


@router.get(
    "/alerts",
    response_model=list[AlertResponse],
    summary="Get recent alerts",
)
async def get_recent_alerts(
    limit: int = Query(default=20, ge=1, le=100),
    unresolved_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns recent alerts, optionally filtered to unresolved only.
    """
    service = AggregationService(db)
    return await service.get_recent_alerts(limit, unresolved_only)
