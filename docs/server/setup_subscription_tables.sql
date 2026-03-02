-- ALADDIN SUBSCRIPTION SYSTEM - DATABASE TABLES
-- Версия: 1.0
-- Дата создания: 2 марта 2026
-- Цель: Создание таблиц для системы подписок

-- =============================================================================
-- ОСНОВНАЯ ТАБЛИЦА ПОДПИСОК
-- =============================================================================

CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    device_id VARCHAR(255) NOT NULL,
    level VARCHAR(50) NOT NULL CHECK (level IN ('free', 'trial', 'personal', 'family', 'premium')),
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'expired', 'cancelled', 'pending', 'trial')),
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    trial_end_date TIMESTAMP,
    auto_renew BOOLEAN DEFAULT FALSE,
    limits JSONB DEFAULT '{
        "devices": 1,
        "scans_per_day": 10,
        "ai_messages_per_day": 0,
        "reports_per_month": 3,
        "storage_gb": 1
    }',
    features TEXT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,

    UNIQUE(user_id, device_id)
);

-- Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_device_id ON subscriptions(device_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_level ON subscriptions(level);
CREATE INDEX IF NOT EXISTS idx_subscriptions_end_date ON subscriptions(end_date);
CREATE INDEX IF NOT EXISTS idx_subscriptions_trial_end_date ON subscriptions(trial_end_date);

-- =============================================================================
-- ТАБЛИЦА ОТСЛЕЖИВАНИЯ ИСПОЛЬЗОВАНИЯ РЕСУРСОВ
-- =============================================================================

CREATE TABLE IF NOT EXISTS usage_tracking (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    resource_type VARCHAR(100) NOT NULL CHECK (resource_type IN ('ai_messages', 'scans', 'reports', 'devices', 'storage', 'bandwidth')),
    amount INTEGER NOT NULL DEFAULT 0,
    period_start DATE NOT NULL, -- начало периода (день/месяц)
    period_end DATE NOT NULL,   -- конец периода (день/месяц)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(subscription_id, resource_type, period_start)
);

-- Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_usage_subscription_id ON usage_tracking(subscription_id);
CREATE INDEX IF NOT EXISTS idx_usage_resource_type ON usage_tracking(resource_type);
CREATE INDEX IF NOT EXISTS idx_usage_period ON usage_tracking(period_start, period_end);

-- =============================================================================
-- ТАБЛИЦА АУДИТА ИЗМЕНЕНИЙ ПОДПИСОК
-- =============================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER REFERENCES subscriptions(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL CHECK (action IN ('created', 'updated', 'cancelled', 'upgraded', 'expired', 'trial_started', 'trial_expired', 'payment_failed', 'payment_success', 'feature_accessed', 'limit_exceeded')),
    old_values JSONB,
    new_values JSONB,
    user_id VARCHAR(255),
    device_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для аудита
CREATE INDEX IF NOT EXISTS idx_audit_subscription_id ON audit_log(subscription_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_log(user_id);

-- =============================================================================
-- ДОПОЛНИТЕЛЬНЫЕ ТАБЛИЦЫ ДЛЯ РАСШИРЕННОЙ ФУНКЦИОНАЛЬНОСТИ
-- =============================================================================

-- Таблица платежей
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER REFERENCES subscriptions(id) ON DELETE SET NULL,
    user_id VARCHAR(255) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    payment_method VARCHAR(100),
    transaction_id VARCHAR(255) UNIQUE,
    external_transaction_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- Индексы для платежей
CREATE INDEX IF NOT EXISTS idx_payments_subscription_id ON payments(subscription_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);

-- Таблица промокодов и скидок
CREATE TABLE IF NOT EXISTS promo_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    discount_type VARCHAR(50) NOT NULL CHECK (discount_type IN ('percentage', 'fixed_amount')),
    discount_value DECIMAL(10,2) NOT NULL,
    max_uses INTEGER,
    used_count INTEGER DEFAULT 0,
    valid_from TIMESTAMP,
    valid_until TIMESTAMP,
    applicable_plans TEXT[], -- для каких планов применим
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Индексы для промокодов
CREATE INDEX IF NOT EXISTS idx_promo_codes_code ON promo_codes(code);
CREATE INDEX IF NOT EXISTS idx_promo_codes_valid_until ON promo_codes(valid_until);

-- =============================================================================
-- ФУНКЦИИ ДЛЯ АВТОМАТИЗАЦИИ
-- =============================================================================

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггеры для автоматического обновления updated_at
CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_usage_tracking_updated_at BEFORE UPDATE ON usage_tracking
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- ПРЕДСТАВЛЕНИЯ ДЛЯ АНАЛИТИКИ
-- =============================================================================

-- Представление активных подписок с использованием
CREATE OR REPLACE VIEW active_subscriptions_view AS
SELECT
    s.id,
    s.user_id,
    s.device_id,
    s.level,
    s.start_date,
    s.end_date,
    s.limits,
    COALESCE(SUM(CASE WHEN ut.resource_type = 'ai_messages' THEN ut.amount ELSE 0 END), 0) as ai_messages_used,
    COALESCE(SUM(CASE WHEN ut.resource_type = 'scans' THEN ut.amount ELSE 0 END), 0) as scans_used,
    COALESCE(SUM(CASE WHEN ut.resource_type = 'reports' THEN ut.amount ELSE 0 END), 0) as reports_used
FROM subscriptions s
LEFT JOIN usage_tracking ut ON s.id = ut.subscription_id
    AND ut.period_start >= CURRENT_DATE - INTERVAL '30 days'
WHERE s.status = 'active'
GROUP BY s.id, s.user_id, s.device_id, s.level, s.start_date, s.end_date, s.limits;

-- =============================================================================
-- КОММЕНТАРИИ К ТАБЛИЦАМ
-- =============================================================================

COMMENT ON TABLE subscriptions IS 'Основная таблица подписок пользователей';
COMMENT ON TABLE usage_tracking IS 'Отслеживание использования ресурсов по подпискам';
COMMENT ON TABLE audit_log IS 'Лог всех изменений в подписках для аудита';
COMMENT ON TABLE payments IS 'История платежей по подпискам';
COMMENT ON TABLE promo_codes IS 'Промокоды и скидки для подписок';

-- =============================================================================
-- ПЕРМИШЕНЫ И БЕЗОПАСНОСТЬ
-- =============================================================================

-- Предоставление прав на таблицы (для aladdin_user)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO aladdin_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO aladdin_user;

-- =============================================================================
-- ПРОВЕРКА СОЗДАНИЯ ТАБЛИЦ
-- =============================================================================

-- Вывод информации о созданных таблицах
DO $$
BEGIN
    RAISE NOTICE 'Subscription tables created successfully:';
    RAISE NOTICE '- subscriptions: %', (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'subscriptions');
    RAISE NOTICE '- usage_tracking: %', (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'usage_tracking');
    RAISE NOTICE '- audit_log: %', (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'audit_log');
    RAISE NOTICE '- payments: %', (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'payments');
    RAISE NOTICE '- promo_codes: %', (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'promo_codes');
END $$;