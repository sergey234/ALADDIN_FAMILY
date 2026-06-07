-- Batch E follow-up: scan audit separate from breach rows (darkweb.darkweb_leaks)
-- Apply: sudo -u postgres psql -d aladdin_db -f create_darkweb_scan_events.sql

CREATE TABLE IF NOT EXISTS darkweb.scan_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL,
    method TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'completed',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_darkweb_scan_events_user_id
    ON darkweb.scan_events(user_id);

CREATE INDEX IF NOT EXISTS idx_darkweb_scan_events_created_at
    ON darkweb.scan_events(created_at DESC);

GRANT SELECT, INSERT ON TABLE darkweb.scan_events TO aladdin_user;
