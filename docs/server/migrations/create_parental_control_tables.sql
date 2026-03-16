-- ============================================
-- МИГРАЦИЯ: Создание таблиц для родительского контроля
-- Дата: 2026-03-14
-- Компонент: parental_control_bot
-- ============================================

-- Таблица статистики родительского контроля
CREATE TABLE IF NOT EXISTS parental_control_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    child_id UUID NOT NULL,
    child_name VARCHAR(255),
    websites_blocked INTEGER NOT NULL DEFAULT 0,
    apps_blocked INTEGER NOT NULL DEFAULT 0,
    search_queries_blocked INTEGER NOT NULL DEFAULT 0,
    active_filters INTEGER NOT NULL DEFAULT 0,
    today_usage VARCHAR(50),
    today_limit VARCHAR(50),
    remaining VARCHAR(50),
    schedules_count INTEGER NOT NULL DEFAULT 0,
    current_location VARCHAR(255),
    geofences_count INTEGER NOT NULL DEFAULT 0,
    events_today INTEGER NOT NULL DEFAULT 0,
    sites_tracked INTEGER NOT NULL DEFAULT 0,
    apps_tracked INTEGER NOT NULL DEFAULT 0,
    contacts_tracked INTEGER NOT NULL DEFAULT 0,
    messages_monitored BOOLEAN NOT NULL DEFAULT FALSE,
    last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, child_id)
);

-- Таблица статистики обхода родительского контроля
CREATE TABLE IF NOT EXISTS parental_bypass_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    child_id UUID NOT NULL,
    today INTEGER NOT NULL DEFAULT 0,
    week INTEGER NOT NULL DEFAULT 0,
    blocked INTEGER NOT NULL DEFAULT 0,
    incognito INTEGER NOT NULL DEFAULT 0,
    tor INTEGER NOT NULL DEFAULT 0,
    proxy INTEGER NOT NULL DEFAULT 0,
    message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, child_id)
);

-- Индексы для parental_control_stats
CREATE INDEX IF NOT EXISTS idx_parental_control_stats_user_id ON parental_control_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_parental_control_stats_child_id ON parental_control_stats(child_id);
CREATE INDEX IF NOT EXISTS idx_parental_control_stats_user_child ON parental_control_stats(user_id, child_id);
CREATE INDEX IF NOT EXISTS idx_parental_control_stats_last_update ON parental_control_stats(last_update);

-- Индексы для parental_bypass_stats
CREATE INDEX IF NOT EXISTS idx_parental_bypass_stats_user_id ON parental_bypass_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_parental_bypass_stats_child_id ON parental_bypass_stats(child_id);
CREATE INDEX IF NOT EXISTS idx_parental_bypass_stats_user_child ON parental_bypass_stats(user_id, child_id);
CREATE INDEX IF NOT EXISTS idx_parental_bypass_stats_updated_at ON parental_bypass_stats(updated_at);

-- Комментарии к таблицам
COMMENT ON TABLE parental_control_stats IS 'Таблица для хранения статистики родительского контроля от parental_control_bot';
COMMENT ON TABLE parental_bypass_stats IS 'Таблица для хранения статистики обхода родительского контроля от parental_control_bot';

-- Триггеры для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_parental_control_stats_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_parental_control_stats_updated_at
    BEFORE UPDATE ON parental_control_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_parental_control_stats_updated_at();

CREATE TRIGGER trigger_update_parental_bypass_stats_updated_at
    BEFORE UPDATE ON parental_bypass_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_parental_control_stats_updated_at();
