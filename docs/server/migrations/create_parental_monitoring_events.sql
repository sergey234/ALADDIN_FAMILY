-- События мониторинга (детское устройство → POST /api/parental-control/monitoring/events)
-- GET /api/parental-control/monitoring/detail объединяет parental_reports.content и эту таблицу.

CREATE TABLE IF NOT EXISTS parental_monitoring_events (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    kind VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_parental_monitoring_events_user_created
    ON parental_monitoring_events (user_id, created_at DESC);
