"""
Alert Engine service.
Rule-based alert detection for log anomalies.
"""

from datetime import datetime, timezone

from sqlalchemy import insert, text

from app.database import async_session_factory
from app.models.alert import Alert
from app.config import get_settings

settings = get_settings()


class AlertEngine:
    """
    Detects anomalies in log events and creates alerts.

    Rules:
    1. Server errors (5xx) → immediate alert
    2. High error rate → alert when threshold exceeded
    3. Spam IP → alert when IP request count exceeds threshold
    """

    def __init__(self):
        # In-memory counters for fast detection (reset periodically)
        self._error_counter: dict[str, int] = {}  # minute_key → error_count
        self._ip_counter: dict[str, int] = {}     # ip_address → request_count
        self._last_reset = datetime.now(timezone.utc)

    async def check_and_create_alert(self, log_data: dict) -> dict | None:
        """
        Check log data against alert rules.
        Returns alert dict if triggered, None otherwise.
        """
        self._maybe_reset_counters()

        status_code = log_data["status_code"]
        ip_address = log_data["ip_address"]

        # Rule 1: Server Error (5xx)
        if status_code >= 500:
            return await self._create_alert(
                alert_type="server_error",
                severity="critical",
                message=f"Server error {status_code} on {log_data['method']} {log_data['path']}",
                metadata={
                    "status_code": status_code,
                    "path": log_data["path"],
                    "method": log_data["method"],
                    "ip_address": ip_address,
                },
            )

        # Rule 2: Track error rate
        minute_key = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M")
        self._error_counter[minute_key] = self._error_counter.get(minute_key, 0) + 1

        if self._error_counter[minute_key] == settings.ALERT_ERROR_RATE_THRESHOLD:
            return await self._create_alert(
                alert_type="high_error_rate",
                severity="warning",
                message=f"High error rate detected: {self._error_counter[minute_key]} errors in current minute",
                metadata={
                    "error_count": self._error_counter[minute_key],
                    "window": minute_key,
                },
            )

        # Rule 3: Track IP spam
        self._ip_counter[ip_address] = self._ip_counter.get(ip_address, 0) + 1

        if self._ip_counter[ip_address] == settings.ALERT_SPAM_IP_THRESHOLD:
            return await self._create_alert(
                alert_type="spam_ip",
                severity="warning",
                message=f"Suspicious activity from IP {ip_address}: {self._ip_counter[ip_address]} requests",
                metadata={
                    "ip_address": ip_address,
                    "request_count": self._ip_counter[ip_address],
                },
            )

        return None

    async def _create_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        metadata: dict | None = None,
    ) -> dict:
        """Create and persist an alert, then return it for broadcasting."""
        alert_data = {
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "metadata": metadata,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Persist to database
        try:
            async with async_session_factory() as session:
                stmt = insert(Alert).values(
                    alert_type=alert_type,
                    severity=severity,
                    message=message,
                    metadata=metadata,
                )
                result = await session.execute(stmt)
                await session.commit()
                alert_data["id"] = result.inserted_primary_key[0]
        except Exception as e:
            print(f"⚠️ Failed to persist alert: {e}")

        print(f"🚨 Alert [{severity.upper()}]: {message}")
        return alert_data

    def _maybe_reset_counters(self):
        """Reset in-memory counters every 5 minutes."""
        now = datetime.now(timezone.utc)
        elapsed = (now - self._last_reset).total_seconds()

        if elapsed > settings.ALERT_WINDOW_MINUTES * 60:
            self._error_counter.clear()
            self._ip_counter.clear()
            self._last_reset = now
