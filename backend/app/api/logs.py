"""
Log ingestion API endpoints.
Receives log events and publishes them to RabbitMQ for async processing.
"""

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.log_schema import LogEventCreate, LogEventBatch

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest a single log event",
)
async def ingest_log(event: LogEventCreate, request: Request):
    """
    Receive a single log event and publish it to the message queue.
    Returns 202 Accepted immediately (async processing).
    """
    try:
        rabbitmq = request.app.state.rabbitmq
        await rabbitmq.publish(event.model_dump(mode="json"))
        return {"status": "accepted", "message": "Log event queued for processing"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to queue log event: {str(e)}",
        )


@router.post(
    "/batch",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest a batch of log events",
)
async def ingest_log_batch(batch: LogEventBatch, request: Request):
    """
    Receive multiple log events and publish each to the message queue.
    More efficient for high-volume log ingestion.
    """
    try:
        rabbitmq = request.app.state.rabbitmq
        for event in batch.events:
            await rabbitmq.publish(event.model_dump(mode="json"))
        return {
            "status": "accepted",
            "message": f"{len(batch.events)} log events queued for processing",
            "count": len(batch.events),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to queue log events: {str(e)}",
        )
