-- ============================================
-- ТЕСТИРОВАНИЕ ВСЕХ СОЗДАННЫХ ТАБЛИЦ
-- Дата: 2026-03-14
-- Операции: INSERT, SELECT, UPDATE, DELETE
-- ============================================

-- Тестовые данные
DO $$
DECLARE
    test_user_id UUID := gen_random_uuid();
    test_child_id UUID := gen_random_uuid();
    test_session_id VARCHAR(255) := 'test_session_' || extract(epoch from now())::text;
    test_request_id VARCHAR(255) := 'test_request_' || extract(epoch from now())::text;
    inserted_id UUID;
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'НАЧАЛО ТЕСТИРОВАНИЯ ТАБЛИЦ';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';

    -- ============================================
    -- ТЕСТ 1: crash_detection_alerts
    -- ============================================
    RAISE NOTICE 'ТЕСТ 1: crash_detection_alerts';
    RAISE NOTICE '----------------------------------------';
    
    -- INSERT
    INSERT INTO crash_detection_alerts (
        user_id, session_id, latitude, longitude, severity,
        accelerometer_data, gyroscope_data, speed, g_force, crash_detected
    ) VALUES (
        test_user_id, test_session_id, 55.7558, 37.6173, 'high',
        '{"x": 1.5, "y": 2.3, "z": 0.8}'::jsonb,
        '{"x": 0.1, "y": 0.2, "z": 0.3}'::jsonb,
        60.5, 2.5, TRUE
    ) RETURNING id INTO inserted_id;
    
    RAISE NOTICE '✅ INSERT: Успешно создан алерт с ID: %', inserted_id;
    
    -- SELECT
    IF EXISTS (SELECT 1 FROM crash_detection_alerts WHERE id = inserted_id) THEN
        RAISE NOTICE '✅ SELECT: Алерт найден';
    ELSE
        RAISE EXCEPTION '❌ SELECT: Алерт не найден';
    END IF;
    
    -- UPDATE
    UPDATE crash_detection_alerts
    SET severity = 'critical', speed = 80.0
    WHERE id = inserted_id;
    
    IF EXISTS (SELECT 1 FROM crash_detection_alerts WHERE id = inserted_id AND severity = 'critical') THEN
        RAISE NOTICE '✅ UPDATE: Алерт обновлен';
    ELSE
        RAISE EXCEPTION '❌ UPDATE: Алерт не обновлен';
    END IF;
    
    -- DELETE
    DELETE FROM crash_detection_alerts WHERE id = inserted_id;
    
    IF NOT EXISTS (SELECT 1 FROM crash_detection_alerts WHERE id = inserted_id) THEN
        RAISE NOTICE '✅ DELETE: Алерт удален';
    ELSE
        RAISE EXCEPTION '❌ DELETE: Алерт не удален';
    END IF;
    
    RAISE NOTICE '';

    -- ============================================
    -- ТЕСТ 2: roadside_assistance_requests
    -- ============================================
    RAISE NOTICE 'ТЕСТ 2: roadside_assistance_requests';
    RAISE NOTICE '----------------------------------------';
    
    -- INSERT
    INSERT INTO roadside_assistance_requests (
        user_id, request_id, problem_type, latitude, longitude,
        address, description, vehicle_make, vehicle_model, status
    ) VALUES (
        test_user_id, test_request_id, 'flat_tire', 55.7558, 37.6173,
        'Москва, Красная площадь', 'Прокол колеса', 'Toyota', 'Camry', 'pending'
    ) RETURNING id INTO inserted_id;
    
    RAISE NOTICE '✅ INSERT: Успешно создан запрос с ID: %', inserted_id;
    
    -- SELECT
    IF EXISTS (SELECT 1 FROM roadside_assistance_requests WHERE id = inserted_id) THEN
        RAISE NOTICE '✅ SELECT: Запрос найден';
    ELSE
        RAISE EXCEPTION '❌ SELECT: Запрос не найден';
    END IF;
    
    -- UPDATE
    UPDATE roadside_assistance_requests
    SET status = 'accepted', estimated_arrival = CURRENT_TIMESTAMP + INTERVAL '30 minutes'
    WHERE id = inserted_id;
    
    IF EXISTS (SELECT 1 FROM roadside_assistance_requests WHERE id = inserted_id AND status = 'accepted') THEN
        RAISE NOTICE '✅ UPDATE: Запрос обновлен';
    ELSE
        RAISE EXCEPTION '❌ UPDATE: Запрос не обновлен';
    END IF;
    
    -- DELETE
    DELETE FROM roadside_assistance_requests WHERE id = inserted_id;
    
    IF NOT EXISTS (SELECT 1 FROM roadside_assistance_requests WHERE id = inserted_id) THEN
        RAISE NOTICE '✅ DELETE: Запрос удален';
    ELSE
        RAISE EXCEPTION '❌ DELETE: Запрос не удален';
    END IF;
    
    RAISE NOTICE '';

    -- ============================================
    -- ТЕСТ 3: parental_control_stats
    -- ============================================
    RAISE NOTICE 'ТЕСТ 3: parental_control_stats';
    RAISE NOTICE '----------------------------------------';
    
    -- INSERT
    INSERT INTO parental_control_stats (
        user_id, child_id, child_name, websites_blocked, apps_blocked,
        search_queries_blocked, active_filters, today_usage, today_limit,
        remaining, schedules_count, geofences_count, events_today
    ) VALUES (
        test_user_id, test_child_id, 'Тестовый ребенок', 15, 8,
        5, 3, '2:30', '3:00', '0:30', 2, 1, 5
    ) RETURNING id INTO inserted_id;
    
    RAISE NOTICE '✅ INSERT: Успешно создана статистика с ID: %', inserted_id;
    
    -- SELECT
    IF EXISTS (SELECT 1 FROM parental_control_stats WHERE id = inserted_id) THEN
        RAISE NOTICE '✅ SELECT: Статистика найдена';
    ELSE
        RAISE EXCEPTION '❌ SELECT: Статистика не найдена';
    END IF;
    
    -- UPDATE
    UPDATE parental_control_stats
    SET websites_blocked = 20, apps_blocked = 10, events_today = 7
    WHERE id = inserted_id;
    
    IF EXISTS (SELECT 1 FROM parental_control_stats WHERE id = inserted_id AND websites_blocked = 20) THEN
        RAISE NOTICE '✅ UPDATE: Статистика обновлена';
    ELSE
        RAISE EXCEPTION '❌ UPDATE: Статистика не обновлена';
    END IF;
    
    -- DELETE
    DELETE FROM parental_control_stats WHERE id = inserted_id;
    
    IF NOT EXISTS (SELECT 1 FROM parental_control_stats WHERE id = inserted_id) THEN
        RAISE NOTICE '✅ DELETE: Статистика удалена';
    ELSE
        RAISE EXCEPTION '❌ DELETE: Статистика не удалена';
    END IF;
    
    RAISE NOTICE '';

    -- ============================================
    -- ТЕСТ 4: parental_bypass_stats
    -- ============================================
    RAISE NOTICE 'ТЕСТ 4: parental_bypass_stats';
    RAISE NOTICE '----------------------------------------';
    
    -- INSERT
    INSERT INTO parental_bypass_stats (
        user_id, child_id, today, week, blocked, incognito, tor, proxy, message
    ) VALUES (
        test_user_id, test_child_id, 3, 12, 2, 1, 0, 1, 'Обнаружены попытки обхода'
    ) RETURNING id INTO inserted_id;
    
    RAISE NOTICE '✅ INSERT: Успешно создана статистика обхода с ID: %', inserted_id;
    
    -- SELECT
    IF EXISTS (SELECT 1 FROM parental_bypass_stats WHERE id = inserted_id) THEN
        RAISE NOTICE '✅ SELECT: Статистика обхода найдена';
    ELSE
        RAISE EXCEPTION '❌ SELECT: Статистика обхода не найдена';
    END IF;
    
    -- UPDATE
    UPDATE parental_bypass_stats
    SET today = 5, week = 15, blocked = 3
    WHERE id = inserted_id;
    
    IF EXISTS (SELECT 1 FROM parental_bypass_stats WHERE id = inserted_id AND today = 5) THEN
        RAISE NOTICE '✅ UPDATE: Статистика обхода обновлена';
    ELSE
        RAISE EXCEPTION '❌ UPDATE: Статистика обхода не обновлена';
    END IF;
    
    -- DELETE
    DELETE FROM parental_bypass_stats WHERE id = inserted_id;
    
    IF NOT EXISTS (SELECT 1 FROM parental_bypass_stats WHERE id = inserted_id) THEN
        RAISE NOTICE '✅ DELETE: Статистика обхода удалена';
    ELSE
        RAISE EXCEPTION '❌ DELETE: Статистика обхода не удалена';
    END IF;
    
    RAISE NOTICE '';

    -- ============================================
    -- ТЕСТ 5: analytics_metrics
    -- ============================================
    RAISE NOTICE 'ТЕСТ 5: analytics_metrics';
    RAISE NOTICE '----------------------------------------';
    
    -- INSERT (event)
    INSERT INTO analytics_metrics (
        user_id, device_id, app_version, platform, metric_type,
        timestamp, action, parameters, success
    ) VALUES (
        test_user_id, 'test_device_123', '1.0.0', 'iOS', 'event',
        CURRENT_TIMESTAMP, 'screen_view', '{"screen": "main"}'::jsonb, TRUE
    ) RETURNING id INTO inserted_id;
    
    RAISE NOTICE '✅ INSERT: Успешно создана метрика события с ID: %', inserted_id;
    
    -- SELECT
    IF EXISTS (SELECT 1 FROM analytics_metrics WHERE id = inserted_id) THEN
        RAISE NOTICE '✅ SELECT: Метрика найдена';
    ELSE
        RAISE EXCEPTION '❌ SELECT: Метрика не найдена';
    END IF;
    
    -- UPDATE
    UPDATE analytics_metrics
    SET success = FALSE, error_message = 'Test error', response_time = 150.5
    WHERE id = inserted_id;
    
    IF EXISTS (SELECT 1 FROM analytics_metrics WHERE id = inserted_id AND success = FALSE) THEN
        RAISE NOTICE '✅ UPDATE: Метрика обновлена';
    ELSE
        RAISE EXCEPTION '❌ UPDATE: Метрика не обновлена';
    END IF;
    
    -- INSERT (api_call)
    INSERT INTO analytics_metrics (
        device_id, metric_type, timestamp, endpoint, method,
        response_time, status_code, success
    ) VALUES (
        'test_device_123', 'api_call', CURRENT_TIMESTAMP,
        '/api/components/status', 'GET', 45.2, 200, TRUE
    ) RETURNING id INTO inserted_id;
    
    RAISE NOTICE '✅ INSERT: Успешно создана метрика API вызова с ID: %', inserted_id;
    
    -- DELETE
    DELETE FROM analytics_metrics WHERE id = inserted_id;
    
    IF NOT EXISTS (SELECT 1 FROM analytics_metrics WHERE id = inserted_id) THEN
        RAISE NOTICE '✅ DELETE: Метрика удалена';
    ELSE
        RAISE EXCEPTION '❌ DELETE: Метрика не удалена';
    END IF;
    
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО! ✅';
    RAISE NOTICE '========================================';
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'ОШИБКА ТЕСТИРОВАНИЯ: %', SQLERRM;
END $$;

-- Проверка индексов
DO $$
DECLARE
    index_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'ПРОВЕРКА ИНДЕКСОВ';
    RAISE NOTICE '========================================';
    
    -- Проверка индексов для crash_detection_alerts
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE tablename = 'crash_detection_alerts';
    RAISE NOTICE 'crash_detection_alerts: % индексов', index_count;
    
    -- Проверка индексов для roadside_assistance_requests
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE tablename = 'roadside_assistance_requests';
    RAISE NOTICE 'roadside_assistance_requests: % индексов', index_count;
    
    -- Проверка индексов для parental_control_stats
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE tablename = 'parental_control_stats';
    RAISE NOTICE 'parental_control_stats: % индексов', index_count;
    
    -- Проверка индексов для parental_bypass_stats
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE tablename = 'parental_bypass_stats';
    RAISE NOTICE 'parental_bypass_stats: % индексов', index_count;
    
    -- Проверка индексов для analytics_metrics
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE tablename = 'analytics_metrics';
    RAISE NOTICE 'analytics_metrics: % индексов', index_count;
    
    RAISE NOTICE '========================================';
END $$;

-- Проверка триггеров
DO $$
DECLARE
    trigger_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'ПРОВЕРКА ТРИГГЕРОВ';
    RAISE NOTICE '========================================';
    
    -- Проверка триггеров для crash_detection_alerts
    SELECT COUNT(*) INTO trigger_count
    FROM pg_trigger
    WHERE tgrelid = 'crash_detection_alerts'::regclass AND tgisinternal = FALSE;
    RAISE NOTICE 'crash_detection_alerts: % триггеров', trigger_count;
    
    -- Проверка триггеров для roadside_assistance_requests
    SELECT COUNT(*) INTO trigger_count
    FROM pg_trigger
    WHERE tgrelid = 'roadside_assistance_requests'::regclass AND tgisinternal = FALSE;
    RAISE NOTICE 'roadside_assistance_requests: % триггеров', trigger_count;
    
    -- Проверка триггеров для parental_control_stats
    SELECT COUNT(*) INTO trigger_count
    FROM pg_trigger
    WHERE tgrelid = 'parental_control_stats'::regclass AND tgisinternal = FALSE;
    RAISE NOTICE 'parental_control_stats: % триггеров', trigger_count;
    
    -- Проверка триггеров для parental_bypass_stats
    SELECT COUNT(*) INTO trigger_count
    FROM pg_trigger
    WHERE tgrelid = 'parental_bypass_stats'::regclass AND tgisinternal = FALSE;
    RAISE NOTICE 'parental_bypass_stats: % триггеров', trigger_count;
    
    RAISE NOTICE '========================================';
END $$;
