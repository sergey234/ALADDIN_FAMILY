-- Per-user scope for cleanup.cleanup_records (B1-04)
ALTER TABLE cleanup.cleanup_records
    ADD COLUMN IF NOT EXISTS user_id BIGINT NULL;

CREATE INDEX IF NOT EXISTS idx_cleanup_records_user_id
    ON cleanup.cleanup_records(user_id);
