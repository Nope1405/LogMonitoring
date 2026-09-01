-- ============================================
-- LogMoni - Aggregation Queries Reference
-- Window Functions & Time-Bucket Aggregation
-- ============================================

-- ============================================
-- 1. Requests per minute (last 10 minutes)
--    Used by: Dashboard Line Chart
-- ============================================
SELECT
    time_bucket,
    total_requests,
    error_count,
    not_found_count,
    server_error_count,
    avg_response_time,
    -- Window Function: running total
    SUM(total_requests) OVER (ORDER BY time_bucket) AS cumulative_requests,
    -- Window Function: moving average of response time
    AVG(avg_response_time) OVER (
        ORDER BY time_bucket
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg_response_time
FROM (
    SELECT
        date_trunc('minute', timestamp) AS time_bucket,
        COUNT(*) AS total_requests,
        COUNT(*) FILTER (WHERE status_code >= 400) AS error_count,
        COUNT(*) FILTER (WHERE status_code = 404) AS not_found_count,
        COUNT(*) FILTER (WHERE status_code >= 500) AS server_error_count,
        ROUND(AVG(response_time)::numeric, 2) AS avg_response_time
    FROM log_entries
    WHERE timestamp >= NOW() - INTERVAL '10 minutes'
    GROUP BY date_trunc('minute', timestamp)
) bucketed
ORDER BY time_bucket;


-- ============================================
-- 2. Top IPs with suspicious activity
--    Used by: Spam Detection / Alert Engine
-- ============================================
SELECT
    ip_address,
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
    WHERE timestamp >= NOW() - INTERVAL '5 minutes'
    GROUP BY ip_address
    HAVING COUNT(*) > 50  -- Minimum threshold
) ip_stats
ORDER BY activity_rank
LIMIT 20;


-- ============================================
-- 3. Error rate trend with lag comparison
--    Used by: Alert Engine (detect spikes)
-- ============================================
SELECT
    time_bucket,
    error_count,
    total_requests,
    error_rate,
    -- Compare with previous bucket
    LAG(error_rate) OVER (ORDER BY time_bucket) AS prev_error_rate,
    -- Detect spike: current rate vs previous rate
    CASE
        WHEN error_rate > 2 * COALESCE(
            LAG(error_rate) OVER (ORDER BY time_bucket), error_rate
        ) THEN TRUE
        ELSE FALSE
    END AS is_spike
FROM (
    SELECT
        date_trunc('minute', timestamp) AS time_bucket,
        COUNT(*) AS total_requests,
        COUNT(*) FILTER (WHERE status_code >= 400) AS error_count,
        ROUND(
            COUNT(*) FILTER (WHERE status_code >= 400)::numeric
            / NULLIF(COUNT(*), 0) * 100,
            2
        ) AS error_rate
    FROM log_entries
    WHERE timestamp >= NOW() - INTERVAL '30 minutes'
    GROUP BY date_trunc('minute', timestamp)
) bucketed
ORDER BY time_bucket;


-- ============================================
-- 4. Status code distribution (last hour)
--    Used by: Dashboard Pie/Donut Chart
-- ============================================
SELECT
    status_code,
    COUNT(*) AS count,
    ROUND(
        COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 2
    ) AS percentage
FROM log_entries
WHERE timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY status_code
ORDER BY count DESC;


-- ============================================
-- 5. Hourly summary with running statistics
--    Used by: Dashboard Summary Cards
-- ============================================
SELECT
    date_trunc('hour', timestamp) AS hour_bucket,
    COUNT(*) AS total_requests,
    COUNT(DISTINCT ip_address) AS unique_ips,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time) AS p95_response_time,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time) AS p99_response_time
FROM log_entries
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY date_trunc('hour', timestamp)
ORDER BY hour_bucket;
