-- TEMPLATE: create missing domain tables for 42/138 coverage
-- Fill only after canonical endpoint->DB mapping is approved.

BEGIN;

-- Example:
-- CREATE SCHEMA IF NOT EXISTS driving;
-- CREATE TABLE IF NOT EXISTS driving.events (
--   id uuid PRIMARY KEY,
--   user_id uuid,
--   event_type text NOT NULL,
--   payload jsonb NOT NULL DEFAULT '{}'::jsonb,
--   created_at timestamptz NOT NULL DEFAULT now()
-- );
-- CREATE INDEX IF NOT EXISTS ix_driving_events_created_at ON driving.events(created_at DESC);

COMMIT;
