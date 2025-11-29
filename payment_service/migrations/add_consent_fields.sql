-- Миграция: Добавление полей согласия на обработку ПДн (152-ФЗ)
-- Дата: 19 ноября 2025

ALTER TABLE payments 
ADD COLUMN personal_data_consent BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN consent_timestamp DATETIME,
ADD COLUMN consent_ip VARCHAR(45);


