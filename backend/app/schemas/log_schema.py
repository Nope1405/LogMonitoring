"""
Pydantic schemas for log event data validation.
Used for API request/response serialization.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class LogEventCreate(BaseModel):
    """Schema for incoming log events (from simulator/client)."""

    timestamp: Optional[datetime] = None
    method: str = Field(..., max_length=10, examples=["GET", "POST"])
    path: str = Field(..., max_length=500, examples=["/api/users", "/login"])
    status_code: int = Field(..., ge=100, le=599, examples=[200, 404, 500])
    ip_address: str = Field(..., examples=["192.168.1.100"])
    user_agent: Optional[str] = Field(None, examples=["Mozilla/5.0"])
    response_time: Optional[int] = Field(None, ge=0, examples=[150])
    request_body: Optional[dict] = None

    @field_validator("method")
    @classmethod
    def validate_method(cls, v: str) -> str:
        allowed = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
        if v.upper() not in allowed:
            raise ValueError(f"Method must be one of {allowed}")
        return v.upper()


class LogEventBatch(BaseModel):
    """Schema for batch log ingestion."""

    events: list[LogEventCreate] = Field(..., min_length=1, max_length=1000)


class LogEventResponse(BaseModel):
    """Schema for log event API response."""

    id: int
    timestamp: datetime
    method: str
    path: str
    status_code: int
    ip_address: str
    user_agent: Optional[str]
    response_time: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
