"""
Aggregation service.
Uses native SQL with Window Functions for time-bucket analysis.
"""

from datetime import datetime, timezone, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.dashboard_schema import (
    DashboardMetrics,
    TimeBucket,
    SuspiciousIP,
    AlertResponse,
)


class AggregationService:
    """
    Executes aggregation queries against PostgreSQL using
    Window Functions, FILTER clauses, and time-bucket grouping.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_metrics(self, minutes: int = 10) -> DashboardMetrics:
        """
        Get time-series metrics for the dashboard line chart.
        Uses date_trunc for time-bucket aggregation and
        FILTER clause for conditional counting.
        """
        query = text("""
            SELECT
                date_trunc('minute', timestamp) AS time_bucket,
                COUNT(*) AS total_requests,
                COUNT(*) FILTER (WHERE status_code >= 400) AS error_count,
                COUNT(*) FILTER (WHERE status_code = 404) AS not_found_count,
                COUNT(*) FILTER (WHERE status_code >= 500) AS server_error_count,
                ROUND(AVG(response_time)::numeric, 2) AS avg_response_time
            FROM log_entries
            WHERE timestamp >= :since
            GROUP BY date_trunc('minute', timestamp)
            ORDER BY time_bucket
        """)

        since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        result = await self.db.execute(query, {"since": since})
        rows = result.fetchall()

        time_series = [
            TimeBucket(
                time_bucket=row.time_bucket,
                total_requests=row.total_requests,
                error_count=row.error_count,
                not_found_count=row.not_found_count,
                server_error_count=row.server_error_count,
                avg_response_time=float(row.avg_response_time) if row.avg_response_time else None,
            )
            for row in rows
        ]

        # Summary stats
        total_requests = sum(b.total_requests for b in time_series)
        total_errors = sum(b.error_count for b in time_series)
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0.0

        # Unique IPs count
        ip_query = text("""
            SELECT COUNT(DISTINCT ip_address) AS unique_ips
            FROM log_entries
            WHERE timestamp >= :since
        """)
        ip_result = await self.db.execute(ip_query, {"since": since})
        unique_ips = ip_result.scalar() or 0

        return DashboardMetrics(
            time_series=time_series,
            total_requests_10m=total_requests,
            total_errors_10m=total_errors,
            error_rate=round(error_rate, 2),
            unique_ips_10m=unique_ips,
        )

    async def get_suspicious_ips(
        self, minutes: int = 5, threshold: int = 50
    ) -> list[SuspiciousIP]:
        """
        Detect suspicious IPs using RANK() Window Function.
        Returns IPs with request count exceeding threshold.
        """
        query = text("""
            SELECT
                ip_address::text,
                request_count,
                error_count,
                RANK() OVER (ORDER BY request_count DESC) AS activity_rank,
                ROUND(
                    (error_count::numeric / NULLIF(request_count, 0)) * 100, 2
                ) AS error_rate_pct
            FROM (
                SELECT
                    ip_address,
                    COUNT(*) AS request_count,
                    COUNT(*) FILTER (WHERE status_code >= 400) AS error_count
                FROM log_entries
                WHERE timestamp >= :since
                GROUP BY ip_address
                HAVING COUNT(*) > :threshold
            ) ip_stats
            ORDER BY activity_rank
            LIMIT 20
        """)

        since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        result = await self.db.execute(
            query, {"since": since, "threshold": threshold}
        )
        rows = result.fetchall()

        return [
            SuspiciousIP(
                ip_address=row.ip_address,
                request_count=row.request_count,
                error_count=row.error_count,
                error_rate_pct=float(row.error_rate_pct) if row.error_rate_pct else 0.0,
                activity_rank=row.activity_rank,
            )
            for row in rows
        ]

    async def get_recent_alerts(
        self, limit: int = 20, unresolved_only: bool = False
    ) -> list[AlertResponse]:
        """Get recent alerts from the database."""
        if unresolved_only:
            query = text("""
                SELECT id, alert_type, severity, message, metadata,
                       is_resolved, created_at
                FROM alerts
                WHERE is_resolved = FALSE
                ORDER BY created_at DESC
                LIMIT :limit
            """)
        else:
            query = text("""
                SELECT id, alert_type, severity, message, metadata,
                       is_resolved, created_at
                FROM alerts
                ORDER BY created_at DESC
                LIMIT :limit
            """)

        result = await self.db.execute(query, {"limit": limit})
        rows = result.fetchall()

        return [
            AlertResponse(
                id=row.id,
                alert_type=row.alert_type,
                severity=row.severity,
                message=row.message,
                metadata=row.metadata,
                is_resolved=row.is_resolved,
                created_at=row.created_at,
            )
            for row in rows
        ]
