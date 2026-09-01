-- ============================================
-- LogMoni - Initial Database Schema
-- ============================================

-- Extension for IP address operations
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- Core Table: log_entries
-- ============================================
CREATE TABLE IF NOT EXISTS log_entries (
    id              BIGSERIAL PRIMARY KEY,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    method          VARCHAR(10) NOT NULL,
    path            VARCHAR(500) NOT NULL,
    status_code     SMALLINT NOT NULL,
    ip_address      INET NOT NULL,
    user_agent      TEXT,
    response_time   INTEGER,                -- milliseconds
    request_body    JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- BRIN index: optimal for time-series append-only data
-- Much smaller than B-tree, perfect for timestamp columns
CREATE INDEX idx_log_entries_timestamp_brin
    ON log_entries USING BRIN (timestamp);

-- B-tree for status code filtering (small cardinality)
CREATE INDEX idx_log_entries_status
    ON log_entries (status_code);

-- Composite index for dashboard time-range + status queries
CREATE INDEX idx_log_entries_ts_status
    ON log_entries (timestamp, status_code);

-- IP address index for spam detection queries
CREATE INDEX idx_log_entries_ip
    ON log_entries (ip_address);

-- ============================================
-- Table: alerts
-- ============================================
CREATE TABLE IF NOT EXISTS alerts (
    id              BIGSERIAL PRIMARY KEY,
    alert_type      VARCHAR(50) NOT NULL,   -- 'high_error_rate', 'spam_ip', 'server_error'
    severity        VARCHAR(20) NOT NULL DEFAULT 'warning', -- 'info', 'warning', 'critical'
    message         TEXT NOT NULL,
    metadata        JSONB,                  -- Additional context data
    is_resolved     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ
);

CREATE INDEX idx_alerts_created_at
    ON alerts USING BRIN (created_at);

CREATE INDEX idx_alerts_type_resolved
    ON alerts (alert_type, is_resolved);

-- ============================================
-- Comments for documentation
-- ============================================
COMMENT ON TABLE log_entries IS 'Stores all ingested log events from web applications';
COMMENT ON TABLE alerts IS 'Stores generated alerts from log analysis rules';
COMMENT ON INDEX idx_log_entries_timestamp_brin IS 'BRIN index for efficient time-range scans on append-only data';
