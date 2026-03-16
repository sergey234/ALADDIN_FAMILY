-- ============================================
-- МИГРАЦИЯ: Создание таблицы crash_detection_alerts
-- Дата: 2026-03-14
-- Компонент: crash_detection_agent
-- ============================================

-- Создание таблицы для хранения алертов о ДТП
CREATE TABLE IF NOT EXISTS crash_detection_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    accelerometer_data JSONB,
    gyroscope_data JSONB,
    speed DECIMAL(10, 2),
    g_force DECIMAL(10, 2),
    crash_detected BOOLEAN NOT NULL DEFAULT FALSE,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_crash_detection_alerts_user_id ON crash_detection_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_crash_detection_alerts_session_id ON crash_detection_alerts(session_id);
CREATE INDEX IF NOT EXISTS idx_crash_detection_alerts_timestamp ON crash_detection_alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_crash_detection_alerts_severity ON crash_detection_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_crash_detection_alerts_crash_detected ON crash_detection_alerts(crash_detected);

-- Комментарии к таблице и колонкам
COMMENT ON TABLE crash_detection_alerts IS 'Таблица для хранения алертов о ДТП от crash_detection_agent';
COMMENT ON COLUMN crash_detection_alerts.id IS 'Уникальный идентификатор алерта';
COMMENT ON COLUMN crash_detection_alerts.user_id IS 'ID пользователя';
COMMENT ON COLUMN crash_detection_alerts.session_id IS 'ID сессии мониторинга';
COMMENT ON COLUMN crash_detection_alerts.latitude IS 'Широта места обнаружения';
COMMENT ON COLUMN crash_detection_alerts.longitude IS 'Долгота места обнаружения';
COMMENT ON COLUMN crash_detection_alerts.severity IS 'Уровень серьезности (low, medium, high, critical)';
COMMENT ON COLUMN crash_detection_alerts.accelerometer_data IS 'Данные акселерометра (JSON)';
COMMENT ON COLUMN crash_detection_alerts.gyroscope_data IS 'Данные гироскопа (JSON)';
COMMENT ON COLUMN crash_detection_alerts.speed IS 'Скорость в момент обнаружения';
COMMENT ON COLUMN crash_detection_alerts.g_force IS 'G-сила в момент обнаружения';
COMMENT ON COLUMN crash_detection_alerts.crash_detected IS 'Флаг обнаружения ДТП';
COMMENT ON COLUMN crash_detection_alerts.timestamp IS 'Время обнаружения';
COMMENT ON COLUMN crash_detection_alerts.created_at IS 'Время создания записи';
COMMENT ON COLUMN crash_detection_alerts.updated_at IS 'Время последнего обновления';

-- Триггер для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_crash_detection_alerts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_crash_detection_alerts_updated_at
    BEFORE UPDATE ON crash_detection_alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_crash_detection_alerts_updated_at();
