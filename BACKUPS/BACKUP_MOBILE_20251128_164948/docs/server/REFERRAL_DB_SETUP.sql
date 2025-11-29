-- ============================================
-- РЕФЕРАЛЬНАЯ ПРОГРАММА: Настройка базы данных
-- ============================================
-- Сервер: 149.154.65.180
-- Дата: 21 ноября 2024
-- ============================================

-- 1. Таблица для хранения реферальных кодов пользователей
CREATE TABLE IF NOT EXISTS referral_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_referral_codes_code ON referral_codes(code);
CREATE INDEX IF NOT EXISTS idx_referral_codes_user_id ON referral_codes(user_id);
CREATE INDEX IF NOT EXISTS idx_referral_codes_created_at ON referral_codes(created_at);

-- 2. Таблица для хранения записей о приглашениях
CREATE TABLE IF NOT EXISTS referrals (
    id SERIAL PRIMARY KEY,
    referrer_id INTEGER NOT NULL,
    invited_user_id INTEGER NOT NULL,
    referral_code VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'completed', 'cancelled'
    created_at TIMESTAMP DEFAULT NOW(),
    converted_at TIMESTAMP NULL,
    discount_applied DECIMAL(10,2) DEFAULT 0,
    reward_amount DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (referrer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (referral_code) REFERENCES referral_codes(code) ON DELETE CASCADE,
    CONSTRAINT unique_referral UNIQUE (referrer_id, invited_user_id)
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_referrals_referrer_id ON referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_referrals_invited_user_id ON referrals(invited_user_id);
CREATE INDEX IF NOT EXISTS idx_referrals_status ON referrals(status);
CREATE INDEX IF NOT EXISTS idx_referrals_code ON referrals(referral_code);
CREATE INDEX IF NOT EXISTS idx_referrals_created_at ON referrals(created_at);
CREATE INDEX IF NOT EXISTS idx_referrals_converted_at ON referrals(converted_at);

-- 3. ✅ НОВОЕ: Таблица для хранения скидок реферера
-- Скидка -20% на следующий месяц после того, как приглашенный оплатит
CREATE TABLE IF NOT EXISTS referral_discounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    discount_percent DECIMAL(5,2) NOT NULL DEFAULT 20.0,
    discount_type VARCHAR(50) NOT NULL DEFAULT 'referral_reward',
    valid_from TIMESTAMP NOT NULL,
    valid_until TIMESTAMP NOT NULL,
    used_at TIMESTAMP NULL,
    referral_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (referral_id) REFERENCES referrals(id) ON DELETE SET NULL
);

-- Индексы для быстрого поиска активных скидок
CREATE INDEX IF NOT EXISTS idx_referral_discounts_user_id ON referral_discounts(user_id);
CREATE INDEX IF NOT EXISTS idx_referral_discounts_valid ON referral_discounts(valid_until, used_at);
CREATE INDEX IF NOT EXISTS idx_referral_discounts_referral_id ON referral_discounts(referral_id);
CREATE INDEX IF NOT EXISTS idx_referral_discounts_active ON referral_discounts(user_id, valid_until, used_at) WHERE used_at IS NULL;

-- Комментарии к таблицам
COMMENT ON TABLE referral_codes IS 'Реферальные коды пользователей. У каждого пользователя один уникальный код.';
COMMENT ON TABLE referrals IS 'Записи о приглашениях. Статус: pending (зарегистрировался), completed (оплатил), cancelled (отменил).';
COMMENT ON TABLE referral_discounts IS 'Скидки для рефереров. Скидка -20% на следующий месяц после оплаты приглашенным.';

COMMENT ON COLUMN referral_codes.user_id IS 'ID пользователя, который приглашает';
COMMENT ON COLUMN referral_codes.code IS 'Уникальный реферальный код (например: ABC123)';
COMMENT ON COLUMN referrals.referrer_id IS 'ID пользователя, который пригласил';
COMMENT ON COLUMN referrals.invited_user_id IS 'ID приглашенного пользователя';
COMMENT ON COLUMN referrals.referral_code IS 'Код, по которому пригласили';
COMMENT ON COLUMN referrals.status IS 'Статус: pending (зарегистрировался), completed (оплатил), cancelled (отменил)';
COMMENT ON COLUMN referrals.converted_at IS 'Дата оплаты (когда статус стал completed)';
COMMENT ON COLUMN referrals.discount_applied IS 'Размер скидки, примененной к приглашенному';
COMMENT ON COLUMN referrals.reward_amount IS 'Размер награды рефереру';
COMMENT ON COLUMN referral_discounts.user_id IS 'ID реферера, которому начислена скидка';
COMMENT ON COLUMN referral_discounts.discount_percent IS 'Процент скидки (обычно 20.0)';
COMMENT ON COLUMN referral_discounts.valid_from IS 'Дата начала действия скидки';
COMMENT ON COLUMN referral_discounts.valid_until IS 'Дата окончания действия скидки';
COMMENT ON COLUMN referral_discounts.used_at IS 'Дата использования скидки (NULL = не использована)';
COMMENT ON COLUMN referral_discounts.referral_id IS 'Связь с записью в referrals';

-- ============================================
-- ФУНКЦИИ ДЛЯ РАБОТЫ С РЕФЕРАЛЬНЫМИ КОДАМИ
-- ============================================

-- Функция для генерации уникального кода
CREATE OR REPLACE FUNCTION generate_referral_code() RETURNS VARCHAR(20) AS $$
DECLARE
    new_code VARCHAR(20);
    code_exists BOOLEAN;
BEGIN
    LOOP
        -- Генерируем случайный код из 6 символов (буквы и цифры)
        new_code := UPPER(
            SUBSTRING(MD5(RANDOM()::TEXT || CLOCK_TIMESTAMP()::TEXT) FROM 1 FOR 6)
        );
        
        -- Проверяем уникальность
        SELECT EXISTS(SELECT 1 FROM referral_codes WHERE code = new_code) INTO code_exists;
        
        -- Если код уникален, выходим из цикла
        EXIT WHEN NOT code_exists;
    END LOOP;
    
    RETURN new_code;
END;
$$ LANGUAGE plpgsql;

-- Функция для получения или создания реферального кода
CREATE OR REPLACE FUNCTION get_or_create_referral_code(p_user_id INTEGER) 
RETURNS VARCHAR(20) AS $$
DECLARE
    existing_code VARCHAR(20);
    new_code VARCHAR(20);
BEGIN
    -- Проверяем, есть ли уже код у пользователя
    SELECT code INTO existing_code 
    FROM referral_codes 
    WHERE user_id = p_user_id;
    
    -- Если код есть, возвращаем его
    IF existing_code IS NOT NULL THEN
        RETURN existing_code;
    END IF;
    
    -- Если кода нет, создаем новый
    new_code := generate_referral_code();
    
    INSERT INTO referral_codes (user_id, code)
    VALUES (p_user_id, new_code)
    ON CONFLICT (user_id) DO NOTHING;
    
    -- Если вставка не удалась (конфликт), получаем существующий код
    IF NOT FOUND THEN
        SELECT code INTO existing_code 
        FROM referral_codes 
        WHERE user_id = p_user_id;
        RETURN existing_code;
    END IF;
    
    RETURN new_code;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
-- ============================================

-- Получить или создать код для пользователя
-- SELECT get_or_create_referral_code(100);

-- Получить код пользователя
-- SELECT code FROM referral_codes WHERE user_id = 100;

-- Получить статистику реферальной программы
-- SELECT 
--     COUNT(*) as total_referrals,
--     COUNT(*) FILTER (WHERE status = 'completed') as converted_referrals,
--     COUNT(*) FILTER (WHERE status = 'pending') as pending_referrals,
--     COALESCE(SUM(reward_amount), 0) as total_rewards
-- FROM referrals
-- WHERE referrer_id = 100;

