#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты расширенного логирования для ParentalControlBot
Версия: 2.5
Дата: 2025-09-21
"""

import asyncio
import pytest
import tempfile
import os
from datetime import datetime
from unittest.mock import Mock, patch

# Добавляем путь к модулям
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.bots.parental_control_bot import ParentalControlBot
from security.bots.components.advanced_logger import AdvancedLogger, LogContext, LogLevel


class TestParentalControlBotAdvancedLogging:
    """Тесты расширенного логирования ParentalControlBot"""

    @pytest.fixture
    async def bot(self):
        """Создание экземпляра бота для тестов"""
        # Создаем временный файл для логов
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            log_file = f.name
        
        config = {
            "log_file": log_file,
            "log_level": "DEBUG"
        }
        
        bot = ParentalControlBot("TestBot", config)
        await bot.start()
        yield bot, log_file
        await bot.stop()
        
        # Удаляем временный файл
        try:
            os.unlink(log_file)
        except:
            pass

    async def test_advanced_logger_initialization(self, bot):
        """Тест инициализации расширенного логгера"""
        bot_instance, _ = bot
        
        assert hasattr(bot_instance, 'advanced_logger')
        assert isinstance(bot_instance.advanced_logger, AdvancedLogger)
        assert bot_instance.advanced_logger.name == "parental_control_bot_TestBot"

    async def test_log_operation_start_end(self, bot):
        """Тест логирования начала и завершения операции"""
        bot_instance, _ = bot
        
        # Логирование начала операции
        context = bot_instance.log_operation_start("test_operation", "child_123")
        assert isinstance(context, LogContext)
        assert context.operation == "test_operation"
        assert context.child_id == "child_123"
        
        # Логирование завершения операции
        bot_instance.log_operation_end(context, 1.5, success=True)

    async def test_log_security_event(self, bot):
        """Тест логирования событий безопасности"""
        bot_instance, _ = bot
        
        # Логирование события безопасности
        bot_instance.log_security_event(
            "content_block",
            "high",
            child_id="child_123",
            url="https://example.com",
            reason="inappropriate_content"
        )

    async def test_log_user_action(self, bot):
        """Тест логирования действий пользователя"""
        bot_instance, _ = bot
        
        # Логирование действия пользователя
        bot_instance.log_user_action(
            "add_child",
            "child_123",
            "parent_456",
            child_name="Test Child",
            age=10
        )

    async def test_log_performance_metric(self, bot):
        """Тест логирования метрик производительности"""
        bot_instance, _ = bot
        
        # Логирование метрики производительности
        bot_instance.log_performance_metric(
            "content_analysis",
            0.5,
            child_id="child_123",
            url="https://youtube.com"
        )

    async def test_log_content_analysis(self, bot):
        """Тест логирования анализа контента"""
        bot_instance, _ = bot
        
        # Логирование анализа контента
        bot_instance.log_content_analysis(
            "https://youtube.com",
            "child_123",
            "allowed",
            category="entertainment",
            risk_score=0.3
        )

    async def test_log_time_violation(self, bot):
        """Тест логирования нарушения времени"""
        bot_instance, _ = bot
        
        # Логирование нарушения времени
        bot_instance.log_time_violation(
            "child_123",
            "mobile",
            120,  # 2 часа
            60    # лимит 1 час
        )

    async def test_log_content_block(self, bot):
        """Тест логирования блокировки контента"""
        bot_instance, _ = bot
        
        # Логирование блокировки контента
        bot_instance.log_content_block(
            "child_123",
            "https://inappropriate.com",
            "adult_content",
            "Возрастные ограничения"
        )

    async def test_log_suspicious_activity(self, bot):
        """Тест логирования подозрительной активности"""
        bot_instance, _ = bot
        
        # Логирование подозрительной активности
        bot_instance.log_suspicious_activity(
            "child_123",
            "unusual_browsing_pattern",
            {
                "urls_visited": 50,
                "time_period": "1_hour",
                "risk_score": 0.8
            }
        )

    async def test_log_emergency_alert(self, bot):
        """Тест логирования экстренного алерта"""
        bot_instance, _ = bot
        
        # Логирование экстренного алерта
        bot_instance.log_emergency_alert(
            "child_123",
            "location_alert",
            "Ребенок покинул безопасную зону",
            location="unknown",
            timestamp=datetime.now().isoformat()
        )

    async def test_log_system_health(self, bot):
        """Тест логирования состояния системы"""
        bot_instance, _ = bot
        
        # Логирование состояния системы
        bot_instance.log_system_health(
            "database",
            "healthy",
            response_time=0.1,
            connections=5
        )

    async def test_log_cache_operation(self, bot):
        """Тест логирования операций кэша"""
        bot_instance, _ = bot
        
        # Логирование операции кэша
        bot_instance.log_cache_operation(
            "get",
            "content_analysis|https://youtube.com|child_123",
            hit=True,
            ttl=1800
        )

    async def test_log_database_operation(self, bot):
        """Тест логирования операций базы данных"""
        bot_instance, _ = bot
        
        # Логирование операции базы данных
        bot_instance.log_database_operation(
            "select",
            "child_profiles",
            0.05,
            rows_returned=1
        )

    async def test_log_api_request(self, bot):
        """Тест логирования API запросов"""
        bot_instance, _ = bot
        
        # Логирование API запроса
        bot_instance.log_api_request(
            "/api/analyze-content",
            "POST",
            200,
            0.3,
            user_agent="Mobile App 1.0"
        )

    async def test_log_ml_prediction(self, bot):
        """Тест логирования ML предсказаний"""
        bot_instance, _ = bot
        
        # Логирование ML предсказания
        bot_instance.log_ml_prediction(
            "content_classifier",
            {"url": "https://youtube.com", "text": "funny video"},
            "entertainment",
            0.95
        )

    async def test_log_configuration_change(self, bot):
        """Тест логирования изменений конфигурации"""
        bot_instance, _ = bot
        
        # Логирование изменения конфигурации
        bot_instance.log_configuration_change(
            "max_daily_hours",
            "8",
            "6",
            "parent_456"
        )

    async def test_get_logging_metrics(self, bot):
        """Тест получения метрик логирования"""
        bot_instance, _ = bot
        
        # Получение метрик логирования
        metrics = bot_instance.get_logging_metrics()
        
        assert "logger_name" in metrics
        assert "log_level" in metrics
        assert "log_format" in metrics
        assert "buffer_size" in metrics
        assert "metrics" in metrics
        
        assert metrics["logger_name"] == "parental_control_bot_TestBot"

    async def test_export_logs(self, bot):
        """Тест экспорта логов"""
        bot_instance, _ = bot
        
        # Экспорт логов
        logs = await bot_instance.export_logs()
        
        # В текущей реализации возвращается пустой список
        assert isinstance(logs, list)

    async def test_cleanup_logs(self, bot):
        """Тест очистки логов"""
        bot_instance, _ = bot
        
        # Очистка логов
        await bot_instance.cleanup_logs(days=30)

    async def test_set_log_level(self, bot):
        """Тест изменения уровня логирования"""
        bot_instance, _ = bot
        
        # Изменение уровня логирования
        bot_instance.set_log_level(LogLevel.DEBUG)
        
        # Проверяем, что уровень изменился
        assert bot_instance.advanced_logger.log_level == LogLevel.DEBUG

    async def test_log_file_creation(self, bot):
        """Тест создания файла логов"""
        bot_instance, log_file = bot
        
        # Проверяем, что файл логов создан
        assert os.path.exists(log_file)
        
        # Проверяем, что файл не пустой
        assert os.path.getsize(log_file) > 0

    async def test_log_buffer_processing(self, bot):
        """Тест обработки буфера логов"""
        bot_instance, _ = bot
        
        # Запуск обработчика буфера
        await bot_instance.start_advanced_logging()
        
        # Логируем несколько сообщений
        for i in range(5):
            bot_instance.log_operation_start(f"test_operation_{i}")
        
        # Останавливаем обработчик буфера
        await bot_instance.stop_advanced_logging()

    async def test_log_context_creation(self, bot):
        """Тест создания контекста логирования"""
        bot_instance, _ = bot
        
        # Создание контекста
        context = bot_instance._create_log_context(
            "test_operation",
            child_id="child_123",
            user_id="parent_456"
        )
        
        assert isinstance(context, LogContext)
        assert context.component == "parental_control_bot"
        assert context.operation == "test_operation"
        assert context.child_id == "child_123"

    async def test_logging_integration_with_main_functions(self, bot):
        """Тест интеграции логирования с основными функциями"""
        bot_instance, _ = bot
        
        # Добавляем ребенка (должно логироваться)
        child_data = {
            "name": "Test Child",
            "age": 10,
            "parent_id": "parent_123"
        }
        child_id = await bot_instance.add_child_profile(child_data)
        
        # Анализируем контент (должно логироваться)
        result = await bot_instance.analyze_content("https://youtube.com", child_id)
        
        # Получаем статус (должно логироваться)
        status = await bot_instance.get_child_status(child_id)
        
        # Проверяем, что все операции выполнились
        assert child_id is not None
        assert result is not None
        assert status is not None

    async def test_logging_metrics_accumulation(self, bot):
        """Тест накопления метрик логирования"""
        bot_instance, _ = bot
        
        # Выполняем несколько операций
        for i in range(10):
            bot_instance.log_operation_start(f"operation_{i}")
            bot_instance.log_operation_end(
                bot_instance._create_log_context(f"operation_{i}"),
                0.1,
                success=True
            )
        
        # Получаем метрики
        metrics = bot_instance.get_logging_metrics()
        
        # Проверяем, что метрики накопились
        assert metrics["metrics"]["total_logs"] > 0
        assert metrics["metrics"]["logs_by_level"]["INFO"] > 0

    async def test_error_logging(self, bot):
        """Тест логирования ошибок"""
        bot_instance, _ = bot
        
        # Логируем ошибку
        try:
            raise ValueError("Test error")
        except Exception as e:
            context = bot_instance._create_log_context("error_test")
            bot_instance.advanced_logger.error("Test error occurred", context, exception=e)
        
        # Проверяем метрики
        metrics = bot_instance.get_logging_metrics()
        assert metrics["metrics"]["logs_by_level"]["ERROR"] > 0


# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v"])