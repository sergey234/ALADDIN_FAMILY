-- B-05: persistent async job rows (no raw media, verdict JSON only)
CREATE TABLE IF NOT EXISTS antifake_jobs (
    id UUID PRIMARY KEY,
    user_id BIGINT NOT NULL,
    job_type VARCHAR(32) NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'queued',
    verdict JSONB,
    latency_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_antifake_jobs_user_created
    ON antifake_jobs (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_antifake_jobs_status_updated
    ON antifake_jobs (status, updated_at DESC);
