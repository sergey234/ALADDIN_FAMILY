# -*- coding: utf-8 -*-
"""
Тесты для ParentalControlBotV2 с модульной архитектурой
Версия: 2.5
Дата: 2025-09-21
"""

import asyncio
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.bots.parental_control_bot_v2 import ParentalControlBotV2


class TestParentalControlBotV2:
    """Тесты для ParentalControlBotV2"""

    @pytest.fixture
    async def bot(self):
        """Фикстура для создания экземпляра бота"""
        bot = ParentalControlBotV2("TestBotV2")
        await bot.start()
        yield bot
        await bot.stop()

    @pytest.fixture
    def valid_child_data(self):
        """Валидные данные ребенка"""
        return {
            'name': 'Test Child V2',
            'age': 10,
            'parent_id': 'parent_123',
            'time_limits': {'mobile': 120, 'desktop': 180},
            'restrictions': {'social_media': True, 'gaming': False},
            'safe_zones': [{'name': 'Home', 'location': '123 Main St'}]
        }

    # ==================== ТЕСТЫ ИНИЦИАЛИЗАЦИИ ====================

    def test_bot_initialization(self):
        """Тест инициализации бота"""
        bot = ParentalControlBotV2("InitTestBot")
        
        assert bot.name == "InitTestBot"
        assert bot.version == "2.5"
        assert hasattr(bot, 'profile_manager')
        assert hasattr(bot, 'content_analyzer')
        assert hasattr(bot, 'time_monitor')
        assert hasattr(bot, 'notification_service')
        assert bot.running is False

    def test_bot_initialization_with_config(self):
        """Тест инициализации с конфигурацией"""
        config = {
            'log_level': 'DEBUG',
            'ml_enabled': False,
            'content_analysis_enabled': True
        }
        
        bot = ParentalControlBotV2("ConfigTestBot", config)
        
        assert bot.config['log_level'] == 'DEBUG'
        assert bot.config['ml_enabled'] is False
        assert bot.config['content_analysis_enabled'] is True

    # ==================== ТЕСТЫ УПРАВЛЕНИЯ ПРОФИЛЯМИ ====================

    @pytest.mark.asyncio
    async def test_add_child_profile_success(self, bot, valid_child_data):
        """Тест успешного создания профиля ребенка"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        assert child_id is not None
        assert child_id.startswith('CHILD_')
        
        # Проверка через profile_manager
        profile = await bot.get_child_profile(child_id)
        assert profile is not None
        assert profile.name == 'Test Child V2'
        assert profile.age == 10

    @pytest.mark.asyncio
    async def test_add_child_profile_validation_error(self, bot):
        """Тест ошибки валидации при создании профиля"""
        invalid_data = {
            'name': 'A',  # Слишком короткое
            'age': 25,    # Слишком большой
            'parent_id': 'p'  # Слишком короткий
        }
        
        with pytest.raises(Exception) as exc_info:
            await bot.add_child_profile(invalid_data)
        
        assert "ValidationError" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_child_profile(self, bot, valid_child_data):
        """Тест получения профиля ребенка"""
        child_id = await bot.add_child_profile(valid_child_data)
        profile = await bot.get_child_profile(child_id)
        
        assert profile is not None
        assert profile.name == 'Test Child V2'
        assert profile.age == 10

    @pytest.mark.asyncio
    async def test_update_child_profile(self, bot, valid_child_data):
        """Тест обновления профиля ребенка"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        updates = {'age': 11, 'name': 'Updated Child'}
        success = await bot.update_child_profile(child_id, updates)
        
        assert success is True
        
        profile = await bot.get_child_profile(child_id)
        assert profile.age == 11
        assert profile.name == 'Updated Child'

    @pytest.mark.asyncio
    async def test_delete_child_profile(self, bot, valid_child_data):
        """Тест удаления профиля ребенка"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        success = await bot.delete_child_profile(child_id)
        assert success is True
        
        profile = await bot.get_child_profile(child_id)
        assert profile is None

    @pytest.mark.asyncio
    async def test_get_all_profiles(self, bot, valid_child_data):
        """Тест получения всех профилей"""
        child_id1 = await bot.add_child_profile(valid_child_data)
        
        child_data2 = valid_child_data.copy()
        child_data2['name'] = 'Second Child'
        child_id2 = await bot.add_child_profile(child_data2)
        
        all_profiles = await bot.get_all_profiles()
        
        assert len(all_profiles) == 2
        assert child_id1 in all_profiles
        assert child_id2 in all_profiles

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

    # ==================== ТЕСТЫ МОНИТОРИНГА ВРЕМЕНИ ====================

    @pytest.mark.asyncio
    async def test_start_device_session(self, bot, valid_child_data):
        """Тест начала сессии устройства"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        success = await bot.start_device_session(child_id, 'mobile')
        assert success is True

    @pytest.mark.asyncio
    async def test_end_device_session(self, bot, valid_child_data):
        """Тест завершения сессии устройства"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        # Начинаем сессию
        await bot.start_device_session(child_id, 'mobile')
        
        # Ждем немного
        await asyncio.sleep(0.1)
        
        # Завершаем сессию
        duration = await bot.end_device_session(child_id, 'mobile')
        assert duration is not None
        assert duration >= 0

    @pytest.mark.asyncio
    async def test_set_time_limit(self, bot, valid_child_data):
        """Тест установки лимита времени"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        success = await bot.set_time_limit(child_id, 'mobile', 60)
        assert success is True

    @pytest.mark.asyncio
    async def test_set_time_limit_invalid_device(self, bot, valid_child_data):
        """Тест установки лимита для невалидного устройства"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        with pytest.raises(Exception) as exc_info:
            await bot.set_time_limit(child_id, 'invalid_device', 60)
        
        assert "Тип устройства должен быть одним из" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_usage_report(self, bot, valid_child_data):
        """Тест получения отчета об использовании"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        report = await bot.get_usage_report(child_id)
        
        assert report is not None
        assert report['child_id'] == child_id
        assert 'daily_usage' in report
        assert 'time_limits' in report
        assert 'active_sessions' in report

    # ==================== ТЕСТЫ УВЕДОМЛЕНИЙ ====================

    @pytest.mark.asyncio
    async def test_send_alert_success(self, bot, valid_child_data):
        """Тест успешной отправки алерта"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        alert_data = {
            'child_id': child_id,
            'alert_type': 'time_violation',
            'severity': 'medium',
            'message': 'Превышен лимит времени',
            'data': {'device_type': 'mobile'}
        }
        
        success = await bot.send_alert(alert_data)
        assert success is True

    @pytest.mark.asyncio
    async def test_send_alert_invalid_type(self, bot, valid_child_data):
        """Тест отправки алерта с невалидным типом"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        alert_data = {
            'child_id': child_id,
            'alert_type': 'invalid_type',
            'severity': 'medium',
            'message': 'Test message'
        }
        
        with pytest.raises(Exception) as exc_info:
            await bot.send_alert(alert_data)
        
        assert "Тип алерта должен быть одним из" in str(exc_info.value)

    # ==================== ТЕСТЫ СТАТУСА ====================

    @pytest.mark.asyncio
    async def test_get_child_status_success(self, bot, valid_child_data):
        """Тест успешного получения статуса ребенка"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        status = await bot.get_child_status(child_id)
        
        assert status is not None
        assert status['child_id'] == child_id
        assert status['name'] == 'Test Child V2'
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
        assert status['name'] == 'TestBotV2'
        assert status['version'] == '2.5'
        assert status['architecture'] == 'modular'
        assert status['status'] in ['running', 'stopped']
        assert 'component_stats' in status

    # ==================== ТЕСТЫ ВАЛИДАЦИИ ====================

    def test_validate_child_data_valid(self, bot):
        """Тест валидации валидных данных ребенка"""
        data = {
            'name': 'Test Child',
            'age': 10,
            'parent_id': 'parent_123'
        }
        
        is_valid, error = bot.validate_child_data(data)
        assert is_valid is True
        assert error is None

    def test_validate_child_data_invalid(self, bot):
        """Тест валидации невалидных данных ребенка"""
        data = {
            'name': 'A',
            'age': 25,
            'parent_id': 'p'
        }
        
        is_valid, error = bot.validate_child_data(data)
        assert is_valid is False
        assert error is not None

    def test_validate_content_request_valid(self, bot):
        """Тест валидации валидного запроса контента"""
        is_valid, error = bot.validate_content_request('https://youtube.com', 'child_123')
        assert is_valid is True
        assert error is None

    def test_validate_content_request_invalid(self, bot):
        """Тест валидации невалидного запроса контента"""
        is_valid, error = bot.validate_content_request('invalid-url', 'c')
        assert is_valid is False
        assert error is not None

    @pytest.mark.asyncio
    async def test_validate_time_limit_data_valid(self, bot):
        """Тест валидации валидных данных лимита времени"""
        is_valid, error = await bot.validate_time_limit_data('mobile', 120)
        assert is_valid is True
        assert error is None

    @pytest.mark.asyncio
    async def test_validate_time_limit_data_invalid(self, bot):
        """Тест валидации невалидных данных лимита времени"""
        is_valid, error = await bot.validate_time_limit_data('invalid_device', 2000)
        assert is_valid is False
        assert error is not None

    @pytest.mark.asyncio
    async def test_validate_alert_data_valid(self, bot):
        """Тест валидации валидных данных алерта"""
        alert_data = {
            'child_id': 'child_123',
            'alert_type': 'time_violation',
            'severity': 'medium',
            'message': 'Test message'
        }
        
        is_valid, error = await bot.validate_alert_data(alert_data)
        assert is_valid is True
        assert error is None

    @pytest.mark.asyncio
    async def test_validate_alert_data_invalid(self, bot):
        """Тест валидации невалидных данных алерта"""
        alert_data = {
            'child_id': 'c',
            'alert_type': 'invalid_type',
            'severity': 'invalid_severity',
            'message': 'Hi'
        }
        
        is_valid, error = await bot.validate_alert_data(alert_data)
        assert is_valid is False
        assert error is not None

    # ==================== ТЕСТЫ ПОИСКА ====================

    @pytest.mark.asyncio
    async def test_search_profiles(self, bot, valid_child_data):
        """Тест поиска профилей"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        # Поиск по имени
        results = await bot.search_profiles('Test Child')
        assert len(results) == 1
        assert results[0].name == 'Test Child V2'
        
        # Поиск по parent_id
        results = await bot.search_profiles('parent_123')
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_get_profiles_by_parent(self, bot, valid_child_data):
        """Тест получения профилей по родителю"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        profiles = await bot.get_profiles_by_parent('parent_123')
        assert len(profiles) == 1
        assert profiles[0].name == 'Test Child V2'

    @pytest.mark.asyncio
    async def test_get_profiles_by_age_group(self, bot, valid_child_data):
        """Тест получения профилей по возрастной группе"""
        child_id = await bot.add_child_profile(valid_child_data)
        
        profiles = await bot.get_profiles_by_age_group('elementary')
        assert len(profiles) == 1
        assert profiles[0].name == 'Test Child V2'

    # ==================== ТЕСТЫ ИНТЕГРАЦИИ ====================

    @pytest.mark.asyncio
    async def test_full_workflow(self, bot):
        """Тест полного рабочего процесса"""
        # 1. Создание профиля
        child_data = {
            'name': 'Integration Test Child V2',
            'age': 12,
            'parent_id': 'integration_parent',
            'time_limits': {'mobile': 90, 'desktop': 120}
        }
        child_id = await bot.add_child_profile(child_data)
        
        # 2. Установка лимитов времени
        await bot.set_time_limit(child_id, 'tablet', 60)
        
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
        success = await bot.send_alert(alert_data)
        
        # Проверки
        assert child_id is not None
        assert result.action.value in ['allow', 'block']
        assert status['name'] == 'Integration Test Child V2'
        assert success is True

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, bot):
        """Тест параллельных операций"""
        # Создаем несколько профилей параллельно
        tasks = []
        for i in range(5):
            child_data = {
                'name': f'Concurrent Child V2 {i}',
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

    # ==================== ТЕСТЫ ПРОИЗВОДИТЕЛЬНОСТИ ====================

    @pytest.mark.asyncio
    async def test_performance_multiple_profiles(self, bot):
        """Тест производительности при создании множества профилей"""
        start_time = datetime.now()
        
        # Создаем 10 профилей
        child_ids = []
        for i in range(10):
            child_data = {
                'name': f'Performance Child V2 {i}',
                'age': 5 + i,
                'parent_id': f'performance_parent_{i}'
            }
            child_id = await bot.add_child_profile(child_data)
            child_ids.append(child_id)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        assert len(child_ids) == 10
        assert execution_time < 5.0  # Должно выполняться менее чем за 5 секунд

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


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v", "--tb=short"])