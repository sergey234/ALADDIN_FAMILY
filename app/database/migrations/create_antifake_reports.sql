-- I-02: user scam reports + appeals moderation queue
CREATE TABLE IF NOT EXISTS antifake_reports (
    id UUID PRIMARY KEY,
    user_id BIGINT NOT NULL,
    job_id UUID,
    phone_e164 VARCHAR(20) NOT NULL,
    label VARCHAR(128),
    note TEXT,
    report_type VARCHAR(16) NOT NULL DEFAULT 'scam',
    status VARCHAR(16) NOT NULL DEFAULT 'pending',
    job_verdict VARCHAR(32),
    job_confidence SMALLINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    moderated_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_antifake_reports_status ON antifake_reports (status, created_at);
CREATE INDEX IF NOT EXISTS idx_antifake_reports_user ON antifake_reports (user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS antifake_whitelist (
    user_id BIGINT NOT NULL,
    phone_e164 VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, phone_e164)
);
