-- Batch-1 migration (safe create if not exists)
BEGIN;
CREATE SCHEMA IF NOT EXISTS secops;

-- endpoint_family: /api/activation/retrieve
CREATE TABLE IF NOT EXISTS secops.events_activation_retrieve (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_activation_retrieve_created_at ON secops.events_activation_retrieve(created_at DESC);

-- endpoint_family: /api/ai-categories/age-restriction
CREATE TABLE IF NOT EXISTS secops.events_ai_categories_age_restriction (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_ai_categories_age_restriction_created_at ON secops.events_ai_categories_age_restriction(created_at DESC);

-- endpoint_family: /api/ai-categories/allow
CREATE TABLE IF NOT EXISTS secops.events_ai_categories_allow (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_ai_categories_allow_created_at ON secops.events_ai_categories_allow(created_at DESC);

-- endpoint_family: /api/ai-categories/block
CREATE TABLE IF NOT EXISTS secops.events_ai_categories_block (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_ai_categories_block_created_at ON secops.events_ai_categories_block(created_at DESC);

-- endpoint_family: /api/ai-categories/check
CREATE TABLE IF NOT EXISTS secops.events_ai_categories_check (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_ai_categories_check_created_at ON secops.events_ai_categories_check(created_at DESC);

-- endpoint_family: /api/ai/assistant
CREATE TABLE IF NOT EXISTS secops.events_ai_assistant (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_ai_assistant_created_at ON secops.events_ai_assistant(created_at DESC);

-- endpoint_family: /api/anti-tracker/block
CREATE TABLE IF NOT EXISTS secops.events_anti_tracker_block (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_anti_tracker_block_created_at ON secops.events_anti_tracker_block(created_at DESC);

-- endpoint_family: /api/anti-tracker/check
CREATE TABLE IF NOT EXISTS secops.events_anti_tracker_check (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_anti_tracker_check_created_at ON secops.events_anti_tracker_check(created_at DESC);

-- endpoint_family: /api/anti-tracker/settings
CREATE TABLE IF NOT EXISTS secops.events_anti_tracker_settings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_anti_tracker_settings_created_at ON secops.events_anti_tracker_settings(created_at DESC);

-- endpoint_family: /api/anti-tracker/unblock
CREATE TABLE IF NOT EXISTS secops.events_anti_tracker_unblock (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_anti_tracker_unblock_created_at ON secops.events_anti_tracker_unblock(created_at DESC);

-- endpoint_family: /api/auth/login
CREATE TABLE IF NOT EXISTS secops.events_auth_login (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_auth_login_created_at ON secops.events_auth_login(created_at DESC);

-- endpoint_family: /api/auth/login-by-recovery-code
CREATE TABLE IF NOT EXISTS secops.events_auth_login_by_recovery_code (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_auth_login_by_recovery_code_created_at ON secops.events_auth_login_by_recovery_code(created_at DESC);

-- endpoint_family: /api/auth/logout
CREATE TABLE IF NOT EXISTS secops.events_auth_logout (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_auth_logout_created_at ON secops.events_auth_logout(created_at DESC);

-- endpoint_family: /api/auth/refresh
CREATE TABLE IF NOT EXISTS secops.events_auth_refresh (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_auth_refresh_created_at ON secops.events_auth_refresh(created_at DESC);

-- endpoint_family: /api/auth/register
CREATE TABLE IF NOT EXISTS secops.events_auth_register (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_auth_register_created_at ON secops.events_auth_register(created_at DESC);

-- endpoint_family: /api/auth/register-device
CREATE TABLE IF NOT EXISTS secops.events_auth_register_device (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_auth_register_device_created_at ON secops.events_auth_register_device(created_at DESC);

-- endpoint_family: /api/auth/register-device-trial
CREATE TABLE IF NOT EXISTS secops.events_auth_register_device_trial (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_auth_register_device_trial_created_at ON secops.events_auth_register_device_trial(created_at DESC);

-- endpoint_family: /api/chat/offline-messages
CREATE TABLE IF NOT EXISTS secops.events_chat_offline_messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_chat_offline_messages_created_at ON secops.events_chat_offline_messages(created_at DESC);

-- endpoint_family: /api/components/batch
CREATE TABLE IF NOT EXISTS secops.events_components_batch (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_components_batch_created_at ON secops.events_components_batch(created_at DESC);

-- endpoint_family: /api/components/config
CREATE TABLE IF NOT EXISTS secops.events_components_config (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NULL,
  endpoint text NOT NULL,
  method text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NULL,
  status text NOT NULL DEFAULT 'new',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_components_config_created_at ON secops.events_components_config(created_at DESC);

COMMIT;
