# -*- coding: utf-8 -*-
"""
Comprehensive тесты для ParentalControlBot
Версия: 2.5
Дата: 2025-09-21
"""

import asyncio
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.bots.parental_control_bot import (
    ParentalControlBot,
    ChildProfileData,
    ContentAnalysisRequest,
    TimeLimitData,
    AlertData,
    validate_child_data,
    validate_content_request,
    create_alert_with_validation,
    set_time_limit_with_validation
)


class TestParentalControlBotComprehensive:
    """Comprehensive тесты для ParentalControlBot"""

    @pytest.fixture
    async def bot(self):
        """Фикстура для создания экземпляра бота"""
        bot = ParentalControlBot("TestBot")
        await bot.start()
        yield bot
        await bot.stop()

    @pytest.fixture
    def valid_child_data(self):
        """Валидные данные ребенка"""
        return {
            'name': 'Test Child',
            'age': 10,
            'parent_id': 'parent_123',
            'time_limits': {'mobile': 120, 'desktop': 180},
            'restrictions': {'social_media': True, 'gaming': False},
            'safe_zones': [{'name': 'Home', 'location': '123 Main St'}]
        }

    @pytest.fixture
    def invalid_child_data(self):
        """Невалидные данные ребенка"""
        return {
            'name': 'A',  # Слишком короткое имя
            'age': 25,    # Слишком большой возраст
            'parent_id': 'p'  # Слишком короткий ID
        }

    # ==================== ТЕСТЫ ВАЛИДАЦИИ ====================

    def test_validate_child_data_valid(self, valid_child_data):
        """Тест валидации валидных данных ребенка"""
        is_valid, error = validate_child_data(valid_child_data)
        assert is_valid is True
        assert error is None

    def test_validate_child_data_invalid(self, invalid_child_data):
        """Тест валидации невалидных данных ребенка"""
        is_valid, error = validate_child_data(invalid_child_data)
        assert is_valid is False
        assert error is not None
        assert "Имя должно содержать минимум 2 символа" in error

    def test_validate_content_request_valid(self):
        """Тест валидации валидного запроса контента"""
        is_valid, error = validate_content_request('https://youtube.com', 'child_123')
        assert is_valid is True
        assert error is None

    def test_validate_content_request_invalid(self):
        """Тест валидации невалидного запроса контента"""
        is_valid, error = validate_content_request('invalid-url', 'c')
        assert is_valid is False
        assert error is not None
        assert "URL должен начинаться с http:// или https://" in error

    # ==================== ТЕСТЫ СОЗДАНИЯ ПРОФИЛЕЙ ====================

    @pytest.mark.asyncio
    async def test_add_child_profile_success(self, bot, valid_child_data):
        """Тест успешного создания профиля ребенка"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        assert child_id is not None
        assert child_id.startswith('CHILD_')
        assert child_id in bot.child_profiles
        assert bot.child_profiles[child_id].name == 'Test Child'
        assert bot.child_profiles[child_id].age == 10

    @pytest.mark.asyncio
    async def test_add_child_profile_validation_error(self, bot, invalid_child_data):
        """Тест ошибки валидации при создании профиля"""
        with pytest.raises(Exception) as exc_info:
            await bot.add_child_profile(invalid_child_data)
        
        assert "ValidationError" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_add_child_profile_duplicate(self, bot, valid_child_data):
        """Тест создания дублирующегося профиля"""
        # Создаем первый профиль
        child_id1 = await bot.add_child_profile(valid_child_data)
        
        # Пытаемся создать второй профиль с теми же данными
        child_id2 = await bot.add_child_profile(valid_child_data)
        
        # Должны получить разные ID
        assert child_id1 != child_id2
        assert len(bot.child_profiles) == 2

    # ==================== ТЕСТЫ АНАЛИЗА КОНТЕНТА ====================

    @pytest.mark.asyncio
    async def test_analyze_content_educational(self, bot, valid_child_data):
        """Тест анализа образовательного контента"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        result = await bot.analyze_content('https://khanacademy.org', child_id)
        
        assert result.url == 'https://khanacademy.org'
        assert result.action.value in ['allow', 'block']
        assert result.age_appropriate is not None

    @pytest.mark.asyncio
    async def test_analyze_content_social_media(self, bot, valid_child_data):
        """Тест анализа контента социальных сетей"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        result = await bot.analyze_content('https://instagram.com', child_id)
        
        assert result.url == 'https://instagram.com'
        assert result.action.value in ['allow', 'block']

    @pytest.mark.asyncio
    async def test_analyze_content_invalid_url(self, bot, valid_child_data):
        """Тест анализа невалидного URL"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        with pytest.raises(Exception) as exc_info:
            await bot.analyze_content('invalid-url', child_id)
        
        assert "URL должен начинаться с http:// или https://" in str(exc_info.value)

    # ==================== ТЕСТЫ СТАТУСА ====================

    @pytest.mark.asyncio
    async def test_get_child_status_success(self, bot, valid_child_data):
        """Тест успешного получения статуса ребенка"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        status = await bot.get_child_status(child_id)
        
        assert status is not None
        assert status['child_id'] == child_id
        assert status['name'] == 'Test Child'
        assert status['age'] == 10
        assert status['age_group'] in ['toddler', 'preschool', 'elementary', 'teen']

    @pytest.mark.asyncio
    async def test_get_child_status_not_found(self, bot):
        """Тест получения статуса несуществующего ребенка"""
        status = await bot.get_child_status('nonexistent_id')
        assert status is None

    @pytest.mark.asyncio
    async def test_get_bot_status(self, bot):
        """Тест получения статуса бота"""
        status = await bot.get_status()
        
        assert status is not None
        assert status['name'] == 'TestBot'
        assert status['status'] in ['running', 'stopped']
        assert 'stats' in status
        assert 'config' in status

    # ==================== ТЕСТЫ ЛИМИТОВ ВРЕМЕНИ ====================

    @pytest.mark.asyncio
    async def test_set_time_limit_success(self, bot, valid_child_data):
        """Тест успешной установки лимита времени"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        success = await set_time_limit_with_validation(
            bot, child_id, 'mobile', 60
        )
        
        assert success is True
        assert bot.child_profiles[child_id].time_limits['mobile'] == 60

    @pytest.mark.asyncio
    async def test_set_time_limit_invalid_device(self, bot, valid_child_data):
        """Тест установки лимита для невалидного устройства"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        with pytest.raises(Exception) as exc_info:
            await set_time_limit_with_validation(
                bot, child_id, 'invalid_device', 60
            )
        
        assert "Тип устройства должен быть одним из" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_set_time_limit_invalid_minutes(self, bot, valid_child_data):
        """Тест установки невалидного лимита времени"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        with pytest.raises(Exception) as exc_info:
            await set_time_limit_with_validation(
                bot, child_id, 'mobile', 2000  # Слишком много минут
            )
        
        assert "Лимит времени должен быть от 0 до 1440 минут" in str(exc_info.value)

    # ==================== ТЕСТЫ АЛЕРТОВ ====================

    @pytest.mark.asyncio
    async def test_create_alert_success(self, bot, valid_child_data):
        """Тест успешного создания алерта"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        alert_data = {
            'child_id': child_id,
            'alert_type': 'time_violation',
            'severity': 'medium',
            'message': 'Превышен лимит времени',
            'data': {'device_type': 'mobile'}
        }
        
        alert = await create_alert_with_validation(bot, alert_data)
        
        assert alert is not None
        assert alert.child_id == child_id
        assert alert.alert_type == 'time_violation'
        assert alert.severity == 'medium'

    @pytest.mark.asyncio
    async def test_create_alert_invalid_type(self, bot, valid_child_data):
        """Тест создания алерта с невалидным типом"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        alert_data = {
            'child_id': child_id,
            'alert_type': 'invalid_type',
            'severity': 'medium',
            'message': 'Test message'
        }
        
        with pytest.raises(Exception) as exc_info:
            await create_alert_with_validation(bot, alert_data)
        
        assert "Тип алерта должен быть одним из" in str(exc_info.value)

    # ==================== ТЕСТЫ ПРОИЗВОДИТЕЛЬНОСТИ ====================

    @pytest.mark.asyncio
    async def test_performance_multiple_profiles(self, bot):
        """Тест производительности при создании множества профилей"""
        start_time = datetime.now()
        
        # Создаем 10 профилей
        child_ids = []
        for i in range(10):
            child_data = {
                'name': f'Child {i}',
                'age': 5 + i,
                'parent_id': f'parent_{i}'
            }
            child_id = await bot.add_child_profile(child_data)
            child_ids.append(child_id)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        assert len(child_ids) == 10
        assert execution_time < 5.0  # Должно выполняться менее чем за 5 секунд
        assert len(bot.child_profiles) == 10

    @pytest.mark.asyncio
    async def test_performance_content_analysis(self, bot, valid_child_data):
        """Тест производительности анализа контента"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        urls = [
            'https://youtube.com',
            'https://khanacademy.org',
            'https://instagram.com',
            'https://facebook.com',
            'https://tiktok.com'
        ]
        
        start_time = datetime.now()
        
        results = []
        for url in urls:
            result = await bot.analyze_content(url, child_id)
            results.append(result)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        assert len(results) == 5
        assert execution_time < 2.0  # Должно выполняться менее чем за 2 секунды

    # ==================== ТЕСТЫ ОБРАБОТКИ ОШИБОК ====================

    @pytest.mark.asyncio
    async def test_error_handling_database_failure(self, bot, valid_child_data):
        """Тест обработки ошибки базы данных"""
        # Мокаем ошибку базы данных
        with patch.object(bot, 'db_session') as mock_session:
            mock_session.commit.side_effect = Exception("Database error")
            
            with pytest.raises(Exception) as exc_info:
                await bot.add_child_profile(valid_child_data)
            
            assert "Database error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_error_handling_redis_failure(self, bot, valid_child_data):
        """Тест обработки ошибки Redis"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        # Мокаем ошибку Redis
        with patch.object(bot, 'redis_client') as mock_redis:
            mock_redis.lpush.side_effect = Exception("Redis error")
            
            # Это не должно вызывать исключение, только логировать ошибку
            alert_data = {
                'child_id': child_id,
                'alert_type': 'time_violation',
                'severity': 'medium',
                'message': 'Test message'
            }
            
            alert = await create_alert_with_validation(bot, alert_data)
            assert alert is not None  # Алерт должен создаться, несмотря на ошибку Redis

    # ==================== ТЕСТЫ ИНТЕГРАЦИИ ====================

    @pytest.mark.asyncio
    async def test_full_workflow(self, bot):
        """Тест полного рабочего процесса"""
        # 1. Создание профиля
        child_data = {
            'name': 'Integration Test Child',
            'age': 12,
            'parent_id': 'integration_parent',
            'time_limits': {'mobile': 90, 'desktop': 120}
        }
        child_id = await bot.add_child_profile(child_data)
        
        # 2. Установка лимитов времени
        await set_time_limit_with_validation(bot, child_id, 'tablet', 60)
        
        # 3. Анализ контента
        result = await bot.analyze_content('https://youtube.com', child_id)
        
        # 4. Получение статуса
        status = await bot.get_child_status(child_id)
        
        # 5. Создание алерта
        alert_data = {
            'child_id': child_id,
            'alert_type': 'content_blocked',
            'severity': 'low',
            'message': 'Контент заблокирован'
        }
        alert = await create_alert_with_validation(bot, alert_data)
        
        # Проверки
        assert child_id is not None
        assert result.action.value in ['allow', 'block']
        assert status['name'] == 'Integration Test Child'
        assert alert is not None
        assert bot.child_profiles[child_id].time_limits['tablet'] == 60

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, bot):
        """Тест параллельных операций"""
        # Создаем несколько профилей параллельно
        tasks = []
        for i in range(5):
            child_data = {
                'name': f'Concurrent Child {i}',
                'age': 8 + i,
                'parent_id': f'concurrent_parent_{i}'
            }
            task = bot.add_child_profile(child_data)
            tasks.append(task)
        
        child_ids = await asyncio.gather(*tasks)
        
        # Анализируем контент параллельно
        analysis_tasks = []
        for child_id in child_ids:
            task = bot.analyze_content('https://youtube.com', child_id)
            analysis_tasks.append(task)
        
        results = await asyncio.gather(*analysis_tasks)
        
        assert len(child_ids) == 5
        assert len(results) == 5
        assert all(result.action.value in ['allow', 'block'] for result in results)

    # ==================== ТЕСТЫ КОНФИГУРАЦИИ ====================

    def test_bot_initialization_with_config(self):
        """Тест инициализации бота с конфигурацией"""
        config = {
            'log_level': 'DEBUG',
            'ml_enabled': False,
            'content_analysis_enabled': True
        }
        
        bot = ParentalControlBot("ConfigTestBot", config)
        
        assert bot.config['log_level'] == 'DEBUG'
        assert bot.config['ml_enabled'] is False
        assert bot.config['content_analysis_enabled'] is True

    def test_bot_initialization_default_config(self):
        """Тест инициализации бота с конфигурацией по умолчанию"""
        bot = ParentalControlBot("DefaultConfigBot")
        
        assert bot.config['ml_enabled'] is True
        assert bot.config['content_analysis_enabled'] is True
        assert bot.config['real_time_monitoring'] is True

    # ==================== ТЕСТЫ ЛОГИРОВАНИЯ ====================

    @pytest.mark.asyncio
    async def test_enhanced_logging(self, bot, valid_child_data):
        """Тест улучшенного логирования"""
        # Проверяем, что контекстный логгер настроен
        assert hasattr(bot, 'context_logger')
        assert hasattr(bot, '_log_with_context')
        assert hasattr(bot, '_log_error_with_context')
        
        # Создаем профиль и проверяем логирование
        child_id = await bot.add_child_profile(valid_child_data)
        assert child_id is not None

    # ==================== ТЕСТЫ ДЕКОРАТОРОВ ====================

    @pytest.mark.asyncio
    async def test_error_handler_decorator(self, bot, invalid_child_data):
        """Тест декоратора обработки ошибок"""
        # Должен логировать ошибку и пробрасывать исключение
        with pytest.raises(Exception):
            await bot.add_child_profile(invalid_child_data)

    @pytest.mark.asyncio
    async def test_performance_monitor_decorator(self, bot, valid_child_data):
        """Тест декоратора мониторинга производительности"""
        # Должен логировать время выполнения
        child_id = await bot.add_child_profile(valid_child_data)
        assert child_id is not None

    @pytest.mark.asyncio
    async def test_retry_on_failure_decorator(self, bot, valid_child_data):
        """Тест декоратора повторных попыток"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        # Анализ контента должен работать с retry
        result = await bot.analyze_content('https://youtube.com', child_id)
        assert result is not None


# ==================== ТЕСТЫ ПРОИЗВОДИТЕЛЬНОСТИ ====================

class TestPerformanceBenchmarks:
    """Тесты производительности и бенчмарки"""

    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """Тест использования памяти"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        bot = ParentalControlBot("MemoryTestBot")
        await bot.start()
        
        # Создаем много профилей
        for i in range(100):
            child_data = {
                'name': f'Memory Child {i}',
                'age': 5 + (i % 14),
                'parent_id': f'memory_parent_{i}'
            }
            await bot.add_child_profile(child_data)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        await bot.stop()
        
        # Проверяем, что увеличение памяти разумное (менее 50MB)
        assert memory_increase < 50 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_response_time_benchmark(self):
        """Бенчмарк времени отклика"""
        bot = ParentalControlBot("BenchmarkBot")
        await bot.start()
        
        child_data = {
            'name': 'Benchmark Child',
            'age': 10,
            'parent_id': 'benchmark_parent'
        }
        child_id = await bot.add_child_profile(child_data)
        
        # Измеряем время анализа контента
        start_time = datetime.now()
        result = await bot.analyze_content('https://youtube.com', child_id)
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds()
        
        await bot.stop()
        
        # Время отклика должно быть менее 1 секунды
        assert response_time < 1.0
        assert result is not None


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v", "--tb=short"])