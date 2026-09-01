"""
Pydantic schemas for dashboard aggregation responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TimeBucket(BaseModel):
    """Single time bucket in the line chart data."""

    time_bucket: datetime
    total_requests: int
    error_count: int
    not_found_count: int
    server_error_count: int
    avg_response_time: Optional[float]


class DashboardMetrics(BaseModel):
    """Response schema for dashboard metrics endpoint."""

    time_series: list[TimeBucket]
    total_requests_10m: int
    total_errors_10m: int
    error_rate: float
    unique_ips_10m: int


class SuspiciousIP(BaseModel):
    """Schema for suspicious IP detection results."""

    ip_address: str
    request_count: int
    error_count: int
    error_rate_pct: float
    activity_rank: int


class AlertResponse(BaseModel):
    """Schema for alert API response."""

    id: int
    alert_type: str
    severity: str
    message: str
    metadata: Optional[dict]
    is_resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True
