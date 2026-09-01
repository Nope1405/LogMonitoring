"""
Log Producer service.
Publishes log events to RabbitMQ queue.
"""

from app.core.rabbitmq import RabbitMQConnection


class LogProducer:
    """
    Publishes log events to RabbitMQ for async processing.
    Used by the API layer to decouple ingestion from processing.
    """

    def __init__(self, rabbitmq: RabbitMQConnection):
        self.rabbitmq = rabbitmq

    async def publish_event(self, event_data: dict):
        """Publish a single log event to the queue."""
        await self.rabbitmq.publish(event_data)

    async def publish_batch(self, events: list[dict]):
        """Publish multiple log events to the queue."""
        for event in events:
            await self.rabbitmq.publish(event)
