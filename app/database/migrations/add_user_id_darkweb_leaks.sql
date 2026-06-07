-- Batch E: per-user scope for darkweb.darkweb_leaks (prod aladdin_db)
-- Applied on server 2026-06-07 via: sudo -u postgres psql -d aladdin_db -f ...

ALTER TABLE darkweb.darkweb_leaks
    ADD COLUMN IF NOT EXISTS user_id INTEGER NULL;

CREATE INDEX IF NOT EXISTS idx_darkweb_leaks_user_id
    ON darkweb.darkweb_leaks(user_id);

-- Existing rows (scan_* audit + orphan HIBP) keep user_id NULL → excluded from per-user API.
-- Next: set user_id on INSERT from JWT in reports_router scan paths and dark_web_monitoring_router.
