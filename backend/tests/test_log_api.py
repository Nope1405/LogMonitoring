"""
Basic API tests for the log ingestion endpoints.
"""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Test the health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "logmoni-backend"


@pytest.mark.asyncio
async def test_ingest_log_validation(client):
    """Test log ingestion with invalid data."""
    # Missing required fields
    response = await client.post("/api/logs/", json={})
    assert response.status_code == 422  # Validation error
