-- Wellness Postgres schema (p3-11) — mirrors companion_store SQLite wellness tables

CREATE TABLE IF NOT EXISTS wellness_checkins (
    user_id TEXT NOT NULL,
    day TEXT NOT NULL,
    mood_emoji TEXT,
    mood_score INTEGER,
    sleep_hours REAL,
    stress_level INTEGER,
    energy_level INTEGER,
    notes TEXT,
    source TEXT NOT NULL DEFAULT 'app',
    age_band TEXT,
    created_at TEXT NOT NULL,
    PRIMARY KEY (user_id, day)
);

CREATE TABLE IF NOT EXISTS wellness_assessments (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    assessment_type TEXT NOT NULL,
    answers_json TEXT NOT NULL,
    score INTEGER NOT NULL,
    severity TEXT NOT NULL,
    suggest_professional INTEGER NOT NULL DEFAULT 0,
    disclaimer_version TEXT NOT NULL DEFAULT 'v1',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS wellness_exercises (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    pillar TEXT NOT NULL,
    exercise_type TEXT NOT NULL,
    state_json TEXT NOT NULL DEFAULT '{}',
    step_index INTEGER NOT NULL DEFAULT 0,
    completed INTEGER NOT NULL DEFAULT 0,
    thread_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS wellness_settings (
    user_id TEXT PRIMARY KEY,
    settings_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS wellness_outcomes (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    pillar TEXT NOT NULL,
    helpful INTEGER NOT NULL,
    note TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS wellness_dreams (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    dream_text TEXT NOT NULL,
    mood_tag TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS wellness_crisis_log (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    level TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_wellness_checkins_user_day ON wellness_checkins (user_id, day DESC);
CREATE INDEX IF NOT EXISTS idx_wellness_assessments_user ON wellness_assessments (user_id, created_at DESC);
