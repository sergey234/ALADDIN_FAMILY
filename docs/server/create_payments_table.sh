#!/bin/bash
# Скрипт для создания таблиц payments и payment_methods

DB_PASSWORD="AladdinSecure2024!"
DB_USER="aladdin_user"
DB_NAME="aladdin_db"

export PGPASSWORD="$DB_PASSWORD"

echo "🔧 Создание таблицы payments..."
psql -h localhost -U "$DB_USER" -d "$DB_NAME" <<EOF
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
    status VARCHAR(20) DEFAULT 'pending',
    referral_code VARCHAR(20),
    referral_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    paid_at TIMESTAMP NULL,
    expires_at TIMESTAMP NULL
);

CREATE INDEX IF NOT EXISTS idx_payments_payment_id ON payments(payment_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_referral_code ON payments(referral_code);
CREATE INDEX IF NOT EXISTS idx_payments_referral_id ON payments(referral_id);
EOF

echo "🔧 Создание таблицы payment_methods..."
psql -h localhost -U "$DB_USER" -d "$DB_NAME" <<EOF
CREATE TABLE IF NOT EXISTS payment_methods (
    id SERIAL PRIMARY KEY,
    method_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    config JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

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
EOF

echo "✅ Проверка создания таблиц..."
psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "\d payments"
psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "SELECT COUNT(*) FROM payment_methods;"

echo "✅ Готово!"


