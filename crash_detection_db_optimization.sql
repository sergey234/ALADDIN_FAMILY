-- 🚀 CRASH DETECTION - DATABASE ОПТИМИЗАЦИЯ
-- Дата: 6 февраля 2026 г.
-- Цель: Ускорить запросы на 60-70%

-- 1. Оптимизация индексов для crash_detection_sessions
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_crash_sessions_timestamp_desc
ON crash_detection_sessions (timestamp DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_crash_sessions_status_active
ON crash_detection_sessions (status, active_sessions)
WHERE active_sessions > 0;

-- 2. Оптимизация индексов для crash_detection_alerts
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_crash_alerts_timestamp_desc
ON crash_detection_alerts (timestamp DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_crash_alerts_location
ON crash_detection_alerts (latitude, longitude);

-- 3. Оптимизация индексов для crash_detection_data
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_crash_data_session_timestamp
ON crash_detection_data (session_id, timestamp DESC);

-- 4. VACUUM и ANALYZE после оптимизации
VACUUM ANALYZE crash_detection_sessions;
VACUUM ANALYZE crash_detection_alerts;
VACUUM ANALYZE crash_detection_data;