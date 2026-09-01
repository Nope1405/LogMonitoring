"""
LogEntry model - stores all ingested log events.
Optimized with BRIN index for time-series data.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    DateTime,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LogEntry(Base):
    """
    Represents a single log event from a monitored web application.

    Attributes:
        id: Auto-incrementing primary key
        timestamp: When the event occurred
        method: HTTP method (GET, POST, PUT, DELETE)
        path: Request path (/api/users, /login)
        status_code: HTTP status code (200, 404, 500)
        ip_address: Client IP address
        user_agent: Browser/bot user agent string
        response_time: Response time in milliseconds
        request_body: Optional request payload as JSON
        created_at: When the record was inserted
    """

    __tablename__ = "log_entries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    status_code: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    ip_address: Mapped[str] = mapped_column(INET, nullable=False)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    request_body: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ============================================
    # Index Definitions
    # ============================================
    __table_args__ = (
        # BRIN index for time-series queries (much smaller than B-tree)
        Index("idx_log_entries_timestamp_brin", "timestamp", postgresql_using="brin"),
        # B-tree for status code filtering
        Index("idx_log_entries_status", "status_code"),
        # Composite for dashboard queries
        Index("idx_log_entries_ts_status", "timestamp", "status_code"),
        # IP address for spam detection
        Index("idx_log_entries_ip", "ip_address"),
    )

    def __repr__(self) -> str:
        return (
            f"<LogEntry(id={self.id}, method={self.method}, "
            f"path={self.path}, status={self.status_code})>"
        )
