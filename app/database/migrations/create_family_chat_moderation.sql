BEGIN;

CREATE TABLE IF NOT EXISTS family_chat_reports (
    id TEXT PRIMARY KEY,
    family_id TEXT NOT NULL,
    reporter_user_id INTEGER NOT NULL,
    reported_user_id INTEGER NOT NULL,
    message_id TEXT NOT NULL,
    message_envelope_version INTEGER,
    category TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'reviewed', 'actioned', 'dismissed')),
    created_at TEXT NOT NULL,
    reviewed_at TEXT,
    resolution TEXT
);

CREATE TABLE IF NOT EXISTS family_chat_restrictions (
    family_id TEXT NOT NULL,
    target_user_id INTEGER NOT NULL,
    restricted_by_user_id INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (family_id, target_user_id)
);

CREATE TABLE IF NOT EXISTS family_chat_moderation_audit (
    id TEXT PRIMARY KEY,
    family_id TEXT NOT NULL,
    report_id TEXT,
    actor_user_id INTEGER NOT NULL,
    target_user_id INTEGER,
    target_message_id TEXT,
    action TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS family_chat_media_files (
    filename TEXT PRIMARY KEY,
    family_id TEXT NOT NULL,
    uploaded_by_user_id INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_family_chat_reports_status_created
    ON family_chat_reports (status, created_at);
CREATE INDEX IF NOT EXISTS idx_family_chat_reports_family
    ON family_chat_reports (family_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_family_chat_moderation_audit_family
    ON family_chat_moderation_audit (family_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_family_chat_media_family
    ON family_chat_media_files (family_id);

COMMIT;
