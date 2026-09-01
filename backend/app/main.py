"""
FastAPI application entry point.
Manages application lifespan (startup/shutdown) including
RabbitMQ consumer and database connections.
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.router import api_router
from app.api.websocket import websocket_router
from app.services.consumer import LogConsumer
from app.core.rabbitmq import RabbitMQConnection

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    - Startup: Connect to RabbitMQ, start consumer worker
    - Shutdown: Gracefully stop consumer, close connections
    """
    # === STARTUP ===
    print("🚀 Starting LogMoni backend...")

    # Initialize RabbitMQ connection
    rabbitmq = RabbitMQConnection()
    await rabbitmq.connect()
    app.state.rabbitmq = rabbitmq

    # Start background consumer
    consumer = LogConsumer(rabbitmq)
    consumer_task = asyncio.create_task(consumer.start())
    app.state.consumer_task = consumer_task

    print("✅ LogMoni backend ready!")

    yield

    # === SHUTDOWN ===
    print("🛑 Shutting down LogMoni backend...")

    # Stop consumer
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass

    # Close RabbitMQ connection
    await rabbitmq.close()

    print("👋 LogMoni backend stopped.")


# ============================================
# Create FastAPI Application
# ============================================
app = FastAPI(
    title="LogMoni - Log Monitoring & Alerting",
    description="Real-time log collection, analysis, and alerting system",
    version="1.0.0",
    lifespan=lifespan,
)

# ============================================
# CORS Middleware
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Register Routers
# ============================================
app.include_router(api_router, prefix="/api")
app.include_router(websocket_router)


# ============================================
# Health Check
# ============================================
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "logmoni-backend"}
