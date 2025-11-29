#!/bin/bash
# Скрипт для создания таблицы activation_codes

DB_PASSWORD="AladdinSecure2024!"
DB_USER="aladdin_user"
DB_NAME="aladdin_db"

export PGPASSWORD="$DB_PASSWORD"

echo "🔧 Создание таблицы activation_codes..."
psql -h localhost -U "$DB_USER" -d "$DB_NAME" <<EOF
CREATE TABLE IF NOT EXISTS activation_codes (
    id SERIAL PRIMARY KEY,
    activation_code VARCHAR(20) UNIQUE NOT NULL,
    payment_id VARCHAR(100) NOT NULL,
    user_alias VARCHAR(100),
    tariff_id VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP NULL
);

CREATE INDEX IF NOT EXISTS idx_activation_codes_code ON activation_codes(activation_code);
CREATE INDEX IF NOT EXISTS idx_activation_codes_payment_id ON activation_codes(payment_id);
CREATE INDEX IF NOT EXISTS idx_activation_codes_user_alias ON activation_codes(user_alias);
CREATE INDEX IF NOT EXISTS idx_activation_codes_status ON activation_codes(status);

-- Внешний ключ (если таблица payments существует)
DO \$\$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'payments') THEN
        ALTER TABLE activation_codes 
        ADD CONSTRAINT fk_activation_codes_payment 
        FOREIGN KEY (payment_id) REFERENCES payments(payment_id) ON DELETE CASCADE;
    END IF;
END\$\$;

EOF

echo "✅ Проверка создания таблицы..."
psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "\d activation_codes"

echo "✅ Готово!"


