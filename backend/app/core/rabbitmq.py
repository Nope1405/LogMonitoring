"""
RabbitMQ connection manager.
Handles connection lifecycle, channel creation, and queue declaration.
"""

import json
from typing import Optional

import aio_pika
from aio_pika import Message, DeliveryMode

from app.config import get_settings

settings = get_settings()


class RabbitMQConnection:
    """
    Manages RabbitMQ connection and provides publish/consume capabilities.

    Usage:
        rabbitmq = RabbitMQConnection()
        await rabbitmq.connect()
        await rabbitmq.publish({"event": "data"})
        await rabbitmq.close()
    """

    def __init__(self):
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.queue: Optional[aio_pika.Queue] = None
        self.queue_name = settings.RABBITMQ_QUEUE_NAME

    async def connect(self):
        """Establish connection to RabbitMQ and declare queue."""
        self.connection = await aio_pika.connect_robust(
            settings.RABBITMQ_URL,
            timeout=10,
        )
        self.channel = await self.connection.channel()

        # Set prefetch count for fair dispatch
        await self.channel.set_qos(prefetch_count=10)

        # Declare durable queue (survives broker restart)
        self.queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True,
        )

        print(f"📨 Connected to RabbitMQ, queue: {self.queue_name}")

    async def publish(self, data: dict):
        """
        Publish a message to the log events queue.

        Args:
            data: Dictionary to serialize as JSON message body
        """
        if not self.channel:
            raise RuntimeError("RabbitMQ channel not initialized. Call connect() first.")

        message = Message(
            body=json.dumps(data).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,  # Survive broker restart
            content_type="application/json",
        )

        await self.channel.default_exchange.publish(
            message,
            routing_key=self.queue_name,
        )

    async def close(self):
        """Gracefully close RabbitMQ connection."""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            print("📨 RabbitMQ connection closed.")
