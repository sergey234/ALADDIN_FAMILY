-- ============================================
-- МИГРАЦИЯ: Создание всех таблиц для компонентов ЭТАП 2
-- Дата: 2026-03-14
-- Описание: Создает таблицы для crash_detection_agent, roadside_assistance_agent,
--           parental_control_bot, analytics_manager
-- ============================================

-- ═══════════════════════════════════════════════════════════════
-- 1. CRASH DETECTION ALERTS
-- ═══════════════════════════════════════════════════════════════

\i create_crash_detection_alerts_table.sql

-- ═══════════════════════════════════════════════════════════════
-- 2. ROADSIDE ASSISTANCE REQUESTS
-- ═══════════════════════════════════════════════════════════════

\i create_roadside_assistance_requests_table.sql

-- ═══════════════════════════════════════════════════════════════
-- 3. PARENTAL CONTROL TABLES
-- ═══════════════════════════════════════════════════════════════

\i create_parental_control_tables.sql

-- ═══════════════════════════════════════════════════════════════
-- 4. ANALYTICS METRICS
-- ═══════════════════════════════════════════════════════════════

\i create_analytics_metrics_table.sql

-- ═══════════════════════════════════════════════════════════════
-- ПРОВЕРКА СОЗДАНИЯ ВСЕХ ТАБЛИЦ
-- ═══════════════════════════════════════════════════════════════

DO $$
BEGIN
    -- Проверка создания таблиц
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'crash_detection_alerts') THEN
        RAISE EXCEPTION 'Таблица crash_detection_alerts не создана';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'roadside_assistance_requests') THEN
        RAISE EXCEPTION 'Таблица roadside_assistance_requests не создана';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'parental_control_stats') THEN
        RAISE EXCEPTION 'Таблица parental_control_stats не создана';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'parental_bypass_stats') THEN
        RAISE EXCEPTION 'Таблица parental_bypass_stats не создана';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'analytics_metrics') THEN
        RAISE EXCEPTION 'Таблица analytics_metrics не создана';
    END IF;
    
    RAISE NOTICE '✅ Все таблицы успешно созданы!';
END $$;
