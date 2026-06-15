-- L-batch: family moat (push tokens, CD status, shared reports)
CREATE TABLE IF NOT EXISTS antifake_user_push_tokens (
    user_id BIGINT NOT NULL,
    token_hex VARCHAR(128) NOT NULL,
    platform VARCHAR(16) NOT NULL DEFAULT 'ios',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, token_hex)
);

CREATE TABLE IF NOT EXISTS antifake_family_cd_status (
    user_id BIGINT PRIMARY KEY,
    family_id VARCHAR(64) NOT NULL,
    extension_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    synced_count INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_antifake_family_cd_family ON antifake_family_cd_status (family_id, updated_at DESC);

ALTER TABLE antifake_reports ADD COLUMN IF NOT EXISTS family_id VARCHAR(64);
CREATE INDEX IF NOT EXISTS idx_antifake_reports_family ON antifake_reports (family_id, created_at DESC);
