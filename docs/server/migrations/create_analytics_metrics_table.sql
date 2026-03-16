-- ============================================
-- МИГРАЦИЯ: Создание таблицы analytics_metrics
-- Дата: 2026-03-14
-- Компонент: analytics_manager
-- ============================================

-- Создание таблицы для хранения метрик аналитики
CREATE TABLE IF NOT EXISTS analytics_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    device_id VARCHAR(255) NOT NULL,
    app_version VARCHAR(50),
    platform VARCHAR(50),
    metric_type VARCHAR(50) NOT NULL CHECK (metric_type IN ('event', 'api_call', 'alert', 'system_health', 'component_status')),
    timestamp TIMESTAMP NOT NULL,
    action VARCHAR(255),
    parameters JSONB,
    endpoint VARCHAR(255),
    method VARCHAR(10),
    response_time DECIMAL(10, 3),
    status_code INTEGER,
    success BOOLEAN,
    error_type VARCHAR(100),
    error_message TEXT,
    context JSONB,
    alert_id VARCHAR(255),
    alert_type VARCHAR(100),
    severity VARCHAR(50),
    message TEXT,
    status VARCHAR(50),
    uptime DECIMAL(10, 2),
    active_components INTEGER,
    total_components INTEGER,
    issues TEXT[],
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_user_id ON analytics_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_device_id ON analytics_metrics(device_id);
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_metric_type ON analytics_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_timestamp ON analytics_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_created_at ON analytics_metrics(created_at);
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_success ON analytics_metrics(success);

-- Композитный индекс для частых запросов
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_user_timestamp ON analytics_metrics(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_device_timestamp ON analytics_metrics(device_id, timestamp);

-- Комментарии к таблице и колонкам
COMMENT ON TABLE analytics_metrics IS 'Таблица для хранения метрик аналитики от analytics_manager';
COMMENT ON COLUMN analytics_metrics.id IS 'Уникальный идентификатор метрики';
COMMENT ON COLUMN analytics_metrics.user_id IS 'ID пользователя (может быть NULL для системных метрик)';
COMMENT ON COLUMN analytics_metrics.device_id IS 'ID устройства';
COMMENT ON COLUMN analytics_metrics.metric_type IS 'Тип метрики (event, api_call, alert, system_health, component_status)';
COMMENT ON COLUMN analytics_metrics.timestamp IS 'Время события';
COMMENT ON COLUMN analytics_metrics.parameters IS 'Дополнительные параметры (JSON)';
COMMENT ON COLUMN analytics_metrics.context IS 'Контекст события (JSON)';
COMMENT ON COLUMN analytics_metrics.created_at IS 'Время создания записи';
