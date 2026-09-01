"""
Log Consumer service.
Consumes log events from RabbitMQ and persists them to PostgreSQL.
Also triggers alert detection after each message.
"""

import json
from datetime import datetime, timezone

from aio_pika import IncomingMessage
from sqlalchemy import insert

from app.core.rabbitmq import RabbitMQConnection
from app.core.websocket_manager import ws_manager
from app.database import async_session_factory
from app.models.log_entry import LogEntry
from app.services.alert_engine import AlertEngine


class LogConsumer:
    """
    Background worker that:
    1. Consumes messages from RabbitMQ queue
    2. Inserts log entries into PostgreSQL
    3. Runs alert detection rules
    4. Broadcasts alerts via WebSocket
    """

    def __init__(self, rabbitmq: RabbitMQConnection):
        self.rabbitmq = rabbitmq
        self.alert_engine = AlertEngine()
        self._processed_count = 0

    async def start(self):
        """Start consuming messages from the queue."""
        if not self.rabbitmq.queue:
            raise RuntimeError("RabbitMQ queue not initialized.")

        print("🔄 Consumer started. Waiting for messages...")

        async with self.rabbitmq.queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await self._process_message(message)

    async def _process_message(self, message: IncomingMessage):
        """
        Process a single message from the queue:
        1. Deserialize JSON payload
        2. Insert into database
        3. Check alert rules
        """
        try:
            data = json.loads(message.body.decode())

            # Parse timestamp or use current time
            timestamp = data.get("timestamp")
            if timestamp and isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            else:
                timestamp = datetime.now(timezone.utc)

            # Insert into PostgreSQL
            async with async_session_factory() as session:
                stmt = insert(LogEntry).values(
                    timestamp=timestamp,
                    method=data["method"],
                    path=data["path"],
                    status_code=data["status_code"],
                    ip_address=data["ip_address"],
                    user_agent=data.get("user_agent"),
                    response_time=data.get("response_time"),
                    request_body=data.get("request_body"),
                )
                await session.execute(stmt)
                await session.commit()

            self._processed_count += 1

            # Check for alerts on error status codes
            if data["status_code"] >= 400:
                alert = await self.alert_engine.check_and_create_alert(data)
                if alert:
                    # Broadcast alert to all connected dashboard clients
                    await ws_manager.broadcast({
                        "type": "alert",
                        "data": alert,
                    })

            # Periodic status log
            if self._processed_count % 100 == 0:
                print(f"📊 Processed {self._processed_count} messages")

        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON message: {message.body[:100]}")
        except Exception as e:
            print(f"❌ Error processing message: {e}")
