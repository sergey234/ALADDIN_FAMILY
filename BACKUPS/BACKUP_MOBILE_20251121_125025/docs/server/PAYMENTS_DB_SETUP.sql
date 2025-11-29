-- ============================================
-- СИСТЕМА ОПЛАТЫ: Настройка базы данных
-- ============================================
-- Сервер: 149.154.65.180
-- Дата: 23 ноября 2024
-- ============================================

-- 1. Таблица для хранения платежей
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    payment_id VARCHAR(100) UNIQUE NOT NULL,
    user_id INTEGER,
    user_alias VARCHAR(100),
    tariff_id VARCHAR(50),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'RUB',
    payment_method VARCHAR(50),
    period_months INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, paid, failed, expired, cancelled
    referral_code VARCHAR(20),
    referral_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    paid_at TIMESTAMP NULL,
    expires_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (referral_id) REFERENCES referrals(id) ON DELETE SET NULL
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_payments_payment_id ON payments(payment_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_referral_code ON payments(referral_code);
CREATE INDEX IF NOT EXISTS idx_payments_referral_id ON payments(referral_id);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);

-- 2. Таблица для методов оплаты
CREATE TABLE IF NOT EXISTS payment_methods (
    id SERIAL PRIMARY KEY,
    method_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    config JSONB,  -- Конфигурация для каждого метода
    created_at TIMESTAMP DEFAULT NOW()
);

-- Вставить методы оплаты
INSERT INTO payment_methods (method_id, name, description) VALUES
('qr_sbp', 'QR / СБП', 'Система быстрых платежей'),
('card_sber', 'Карта Сбербанк', 'Интернет-эквайринг Сбербанка'),
('card_tinkoff', 'Карта Тинькофф', 'Оплата картой через Тинькофф'),
('card_alfa', 'Карта Альфа-Банк', 'Оплата картой через Альфа-Банк'),
('card_vtb', 'Карта ВТБ', 'Оплата картой через ВТБ'),
('card_gpb', 'Карта Газпромбанк', 'Оплата картой через Газпромбанк'),
('card_psb', 'Карта Промсвязьбанк', 'Оплата картой через ПСБ'),
('sberpay', 'SberPay', 'Официальная кнопка Сбербанка'),
('tinkoff_pay', 'Tinkoff Pay', 'Моментальная оплата через приложение Тинькофф'),
('manual_transfer', 'Ручной перевод', 'Банковский перевод по реквизитам')
ON CONFLICT (method_id) DO NOTHING;

-- 3. Таблица для кодов активации
CREATE TABLE IF NOT EXISTS activation_codes (
    id SERIAL PRIMARY KEY,
    activation_code VARCHAR(20) UNIQUE NOT NULL,  -- ALDN-XXXX-XXXX-XXXX
    payment_id VARCHAR(100) NOT NULL,
    user_alias VARCHAR(100),
    tariff_id VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',  -- active, used, expired
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,  -- 30 дней с момента создания
    used_at TIMESTAMP NULL,
    FOREIGN KEY (payment_id) REFERENCES payments(payment_id) ON DELETE CASCADE
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_activation_codes_code ON activation_codes(activation_code);
CREATE INDEX IF NOT EXISTS idx_activation_codes_payment_id ON activation_codes(payment_id);
CREATE INDEX IF NOT EXISTS idx_activation_codes_user_alias ON activation_codes(user_alias);
CREATE INDEX IF NOT EXISTS idx_activation_codes_status ON activation_codes(status);

-- Комментарии к таблицам
COMMENT ON TABLE payments IS 'Платежи пользователей. Связь с реферальной программой через referral_code и referral_id.';
COMMENT ON TABLE payment_methods IS 'Методы оплаты, доступные на сайте.';
COMMENT ON TABLE activation_codes IS 'Коды активации подписки. Формат: ALDN-XXXX-XXXX-XXXX. Действительны 30 дней.';

COMMENT ON COLUMN payments.payment_id IS 'Уникальный идентификатор платежа (например: PAY_20241123120000_ABCD1234)';
COMMENT ON COLUMN payments.user_id IS 'ID пользователя (может быть NULL для анонимных платежей)';
COMMENT ON COLUMN payments.user_alias IS 'Псевдоним пользователя (для восстановления кода активации)';
COMMENT ON COLUMN payments.tariff_id IS 'ID тарифа (free, personal, family, premium)';
COMMENT ON COLUMN payments.amount IS 'Сумма платежа в рублях';
COMMENT ON COLUMN payments.currency IS 'Валюта (обычно RUB)';
COMMENT ON COLUMN payments.payment_method IS 'Метод оплаты (qr_sbp, card_sber, и т.д.)';
COMMENT ON COLUMN payments.period_months IS 'Период подписки в месяцах';
COMMENT ON COLUMN payments.status IS 'Статус: pending (ожидает оплаты), paid (оплачен), failed (ошибка), expired (истек), cancelled (отменен)';
COMMENT ON COLUMN payments.referral_code IS 'Реферальный код, использованный при оплате';
COMMENT ON COLUMN payments.referral_id IS 'ID записи в referrals (связь с реферальной программой)';
COMMENT ON COLUMN payments.created_at IS 'Дата создания платежа';
COMMENT ON COLUMN payments.paid_at IS 'Дата оплаты (когда статус стал paid)';
COMMENT ON COLUMN payments.expires_at IS 'Дата истечения платежа (30 минут после создания)';

-- ============================================
-- ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
-- ============================================

-- Получить платеж по payment_id
-- SELECT * FROM payments WHERE payment_id = 'PAY_20241123120000_ABCD1234';

-- Получить все платежи пользователя
-- SELECT * FROM payments WHERE user_id = 100 ORDER BY created_at DESC;

-- Получить платежи со статусом pending
-- SELECT * FROM payments WHERE status = 'pending' AND expires_at > NOW();

-- Получить платежи с реферальным кодом
-- SELECT * FROM payments WHERE referral_code IS NOT NULL;

-- Получить все активные методы оплаты
-- SELECT * FROM payment_methods WHERE is_active = true;

