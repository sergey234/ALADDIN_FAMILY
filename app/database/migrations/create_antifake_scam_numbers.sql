-- C-01: fraud numbers for Call Directory sync
CREATE TABLE IF NOT EXISTS antifake_scam_numbers (
    id BIGSERIAL PRIMARY KEY,
    phone_e164 VARCHAR(20) NOT NULL UNIQUE,
    label VARCHAR(128),
    source VARCHAR(32) NOT NULL DEFAULT 'manual',
    confidence SMALLINT NOT NULL DEFAULT 80,
    block BOOLEAN NOT NULL DEFAULT FALSE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_antifake_scam_numbers_active
    ON antifake_scam_numbers (active, updated_at);
