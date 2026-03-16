-- ═══════════════════════════════════════════════════════════════
-- МИГРАЦИЯ: Создание таблиц для компонентов защиты
-- Дата: 2026-03-14
-- Описание: Создает таблицы для Dark Web, Identity Theft, Location Bubble,
--           Data Cleanup, Anti Tracker, AI Categories
-- ═══════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════
-- 1. DARK WEB MONITORING
-- ═══════════════════════════════════════════════════════════════

-- Таблица утечек Dark Web
CREATE TABLE IF NOT EXISTS dark_web_leaks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    data_type VARCHAR(50) NOT NULL, -- email, password, phone, bank, passport, snils
    value TEXT NOT NULL,
    full_value TEXT,
    leak_date TIMESTAMP NOT NULL,
    discovery_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(255) NOT NULL,
    severity VARCHAR(20) NOT NULL, -- critical, high, medium, low
    status VARCHAR(20) NOT NULL DEFAULT 'new', -- new, in_progress, resolved, ignored
    recommendations TEXT[],
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dark_web_leaks_user_id ON dark_web_leaks(user_id);
CREATE INDEX IF NOT EXISTS idx_dark_web_leaks_status ON dark_web_leaks(status);
CREATE INDEX IF NOT EXISTS idx_dark_web_leaks_severity ON dark_web_leaks(severity);
CREATE INDEX IF NOT EXISTS idx_dark_web_leaks_discovery_date ON dark_web_leaks(discovery_date);

-- Таблица сканирований Dark Web
CREATE TABLE IF NOT EXISTS dark_web_scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    scan_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    databases_scanned INTEGER NOT NULL DEFAULT 0,
    new_leaks_found INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'completed', -- completed, in_progress, failed
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dark_web_scans_user_id ON dark_web_scans(user_id);
CREATE INDEX IF NOT EXISTS idx_dark_web_scans_scan_date ON dark_web_scans(scan_date);

-- ═══════════════════════════════════════════════════════════════
-- 2. IDENTITY THEFT PROTECTION
-- ═══════════════════════════════════════════════════════════════

-- Таблица попыток кражи личности
CREATE TABLE IF NOT EXISTS identity_theft_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    data_type VARCHAR(50) NOT NULL, -- passport, snils, bank, other
    request_source VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    action VARCHAR(20) NOT NULL, -- blocked, allowed, suspicious, requires_review
    severity VARCHAR(20) NOT NULL, -- critical, high, medium, low
    details TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_identity_theft_attempts_user_id ON identity_theft_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_identity_theft_attempts_action ON identity_theft_attempts(action);
CREATE INDEX IF NOT EXISTS idx_identity_theft_attempts_timestamp ON identity_theft_attempts(timestamp);

-- ═══════════════════════════════════════════════════════════════
-- 3. LOCATION BUBBLE
-- ═══════════════════════════════════════════════════════════════

-- Таблица запросов местоположения
CREATE TABLE IF NOT EXISTS location_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    app_name VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    action VARCHAR(20) NOT NULL, -- blocked, allowed, modified
    accuracy VARCHAR(20), -- high, medium, low
    real_latitude DECIMAL(10, 8),
    real_longitude DECIMAL(11, 8),
    bubble_latitude DECIMAL(10, 8),
    bubble_longitude DECIMAL(11, 8),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_location_requests_user_id ON location_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_location_requests_timestamp ON location_requests(timestamp);
CREATE INDEX IF NOT EXISTS idx_location_requests_action ON location_requests(action);

-- ═══════════════════════════════════════════════════════════════
-- 4. DATA CLEANUP
-- ═══════════════════════════════════════════════════════════════

-- Таблица записей очистки данных
CREATE TABLE IF NOT EXISTS data_cleanup_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    cleanup_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    freed_space BIGINT NOT NULL DEFAULT 0, -- байты
    categories JSONB, -- [{name: "cache", size: 1000000}, ...]
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_data_cleanup_records_user_id ON data_cleanup_records(user_id);
CREATE INDEX IF NOT EXISTS idx_data_cleanup_records_cleanup_date ON data_cleanup_records(cleanup_date);

-- ═══════════════════════════════════════════════════════════════
-- 5. ANTI TRACKER
-- ═══════════════════════════════════════════════════════════════

-- Таблица блокировок трекеров
CREATE TABLE IF NOT EXISTS tracker_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    tracker_name VARCHAR(255) NOT NULL,
    blocked_count INTEGER NOT NULL DEFAULT 0,
    last_blocked TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, tracker_name)
);

CREATE INDEX IF NOT EXISTS idx_tracker_blocks_user_id ON tracker_blocks(user_id);
CREATE INDEX IF NOT EXISTS idx_tracker_blocks_tracker_name ON tracker_blocks(tracker_name);
CREATE INDEX IF NOT EXISTS idx_tracker_blocks_last_blocked ON tracker_blocks(last_blocked);

-- ═══════════════════════════════════════════════════════════════
-- 6. AI CATEGORIES
-- ═══════════════════════════════════════════════════════════════

-- Таблица отчетов по категориям AI
CREATE TABLE IF NOT EXISTS ai_category_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    child_id UUID,
    child_name VARCHAR(255),
    category VARCHAR(50) NOT NULL, -- education, games, entertainment, adult, violence, other
    sites_count INTEGER NOT NULL DEFAULT 0,
    blocked_count INTEGER NOT NULL DEFAULT 0,
    report_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_category_reports_user_id ON ai_category_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_category_reports_child_id ON ai_category_reports(child_id);
CREATE INDEX IF NOT EXISTS idx_ai_category_reports_category ON ai_category_reports(category);

-- ═══════════════════════════════════════════════════════════════
-- КОММЕНТАРИИ
-- ═══════════════════════════════════════════════════════════════

-- Все таблицы созданы с индексами для оптимизации запросов
-- Используется UUID для идентификаторов (совместимо с iOS)
-- JSONB используется для гибкого хранения категорий очистки данных
-- Все таблицы имеют created_at для отслеживания времени создания
