-- Per-user scope for location.location_requests (B1-05)
ALTER TABLE location.location_requests
    ADD COLUMN IF NOT EXISTS user_id BIGINT NULL;

CREATE INDEX IF NOT EXISTS idx_location_requests_user_id
    ON location.location_requests(user_id);
