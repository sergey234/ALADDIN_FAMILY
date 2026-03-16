-- ============================================
-- МИГРАЦИЯ: Создание таблицы roadside_assistance_requests
-- Дата: 2026-03-14
-- Компонент: roadside_assistance_agent
-- ============================================

-- Создание таблицы для хранения запросов помощи на дороге
CREATE TABLE IF NOT EXISTS roadside_assistance_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    request_id VARCHAR(255) NOT NULL UNIQUE,
    problem_type VARCHAR(50) NOT NULL CHECK (problem_type IN ('flat_tire', 'battery', 'out_of_gas', 'engine', 'accident', 'lockout', 'other')),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    address TEXT,
    description TEXT,
    vehicle_make VARCHAR(100),
    vehicle_model VARCHAR(100),
    vehicle_year INTEGER,
    vehicle_color VARCHAR(50),
    license_plate VARCHAR(50),
    vin VARCHAR(50),
    partner VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'in_progress', 'completed', 'cancelled', 'failed')),
    estimated_arrival TIMESTAMP,
    actual_arrival TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_roadside_assistance_requests_user_id ON roadside_assistance_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_roadside_assistance_requests_request_id ON roadside_assistance_requests(request_id);
CREATE INDEX IF NOT EXISTS idx_roadside_assistance_requests_status ON roadside_assistance_requests(status);
CREATE INDEX IF NOT EXISTS idx_roadside_assistance_requests_created_at ON roadside_assistance_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_roadside_assistance_requests_problem_type ON roadside_assistance_requests(problem_type);

-- Комментарии к таблице и колонкам
COMMENT ON TABLE roadside_assistance_requests IS 'Таблица для хранения запросов помощи на дороге от roadside_assistance_agent';
COMMENT ON COLUMN roadside_assistance_requests.id IS 'Уникальный идентификатор запроса';
COMMENT ON COLUMN roadside_assistance_requests.user_id IS 'ID пользователя';
COMMENT ON COLUMN roadside_assistance_requests.request_id IS 'Уникальный ID запроса (для внешних систем)';
COMMENT ON COLUMN roadside_assistance_requests.problem_type IS 'Тип проблемы (flat_tire, battery, out_of_gas, engine, accident, lockout, other)';
COMMENT ON COLUMN roadside_assistance_requests.latitude IS 'Широта места проблемы';
COMMENT ON COLUMN roadside_assistance_requests.longitude IS 'Долгота места проблемы';
COMMENT ON COLUMN roadside_assistance_requests.address IS 'Адрес места проблемы';
COMMENT ON COLUMN roadside_assistance_requests.description IS 'Описание проблемы';
COMMENT ON COLUMN roadside_assistance_requests.status IS 'Статус запроса (pending, accepted, in_progress, completed, cancelled, failed)';
COMMENT ON COLUMN roadside_assistance_requests.partner IS 'Партнер, который принял запрос';
COMMENT ON COLUMN roadside_assistance_requests.created_at IS 'Время создания запроса';
COMMENT ON COLUMN roadside_assistance_requests.updated_at IS 'Время последнего обновления';

-- Триггер для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_roadside_assistance_requests_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_roadside_assistance_requests_updated_at
    BEFORE UPDATE ON roadside_assistance_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_roadside_assistance_requests_updated_at();
