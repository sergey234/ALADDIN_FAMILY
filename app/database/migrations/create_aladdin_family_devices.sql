-- Таблица устройств семьи для iOS: GET/POST /api/devices (см. app/routers/misc_other_compat.py).
-- Применение (пример): psql -d aladdin_db -v ON_ERROR_STOP=1 -f create_aladdin_family_devices.sql

CREATE TABLE IF NOT EXISTS aladdin_family_devices (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    owner_label TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'protected',
    last_active TEXT NOT NULL DEFAULT '',
    pairing_token TEXT,
    short_pin TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_aladdin_family_devices_user_id
    ON aladdin_family_devices(user_id);
