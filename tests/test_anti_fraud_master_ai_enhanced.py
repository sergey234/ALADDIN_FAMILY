"""
Комплексные тесты для AntiFraudMasterAI с улучшениями
Включает Unit тесты и Integration тесты
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.ai_agents.anti_fraud_master_ai import (
    AntiFraudMasterAI,
    AntiFraudConfig,
    ValidationResult,
    FraudType,
    RiskLevel,
    ProtectionAction
)


class TestAntiFraudConfig:
    """Тесты для конфигурации AntiFraudMasterAI."""
    
    def test_default_config_creation(self):
        """Тест создания конфигурации по умолчанию."""
        config = AntiFraudConfig()
        
        assert config.emergency_threshold == 0.9
        assert config.family_notification_threshold == 0.7
        assert config.max_risk_threshold == 0.8
        assert config.encryption_enabled is True
        assert config.cache_enabled is True
        assert config.max_concurrent_tasks == 10
    
    def test_custom_config_creation(self):
        """Тест создания кастомной конфигурации."""
        config = AntiFraudConfig(
            emergency_threshold=0.95,
            max_concurrent_tasks=20,
            encryption_enabled=False
        )
        
        assert config.emergency_threshold == 0.95
        assert config.max_concurrent_tasks == 20
        assert config.encryption_enabled is False
    
    def test_config_validation_success(self):
        """Тест успешной валидации конфигурации."""
        config = AntiFraudConfig()
        result = config.validate()
        
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_config_validation_failure(self):
        """Тест неуспешной валидации конфигурации."""
        config = AntiFraudConfig(emergency_threshold=1.5)  # Невалидное значение
        result = config.validate()
        
        assert result.is_valid is False
        assert "emergency_threshold" in result.error_message


class TestValidationResult:
    """Тесты для ValidationResult."""
    
    def test_valid_result(self):
        """Тест валидного результата."""
        result = ValidationResult(True)
        
        assert result.is_valid is True
        assert result.error_message is None
        assert bool(result) is True
    
    def test_invalid_result(self):
        """Тест невалидного результата."""
        result = ValidationResult(False, "Test error")
        
        assert result.is_valid is False
        assert result.error_message == "Test error"
        assert bool(result) is False


class TestAntiFraudMasterAIUnit:
    """Unit тесты для AntiFraudMasterAI."""
    
    @pytest.fixture
    def agent(self):
        """Фикстура агента."""
        config = AntiFraudConfig(log_level="DEBUG")
        return AntiFraudMasterAI(config)
    
    def test_agent_initialization(self, agent):
        """Тест инициализации агента."""
        assert agent.name == "AntiFraudMasterAI"
        assert agent.emergency_threshold == 0.9
        assert agent.max_risk_threshold == 0.8
        assert agent.fraud_detections == 0
        assert agent.blocked_attempts == 0
    
    def test_property_decorators(self, agent):
        """Тест property декораторов."""
        # Тестируем все property
        assert isinstance(agent.fraud_detection_count, int)
        assert isinstance(agent.blocked_attempts_count, int)
        assert isinstance(agent.security_status, str)
        assert isinstance(agent.is_encryption_enabled, bool)
        assert isinstance(agent.uptime_seconds, float)
        
        # Тестируем сложные property
        metrics_summary = agent.security_metrics_summary
        assert isinstance(metrics_summary, dict)
        assert "fraud_detections" in metrics_summary
        
        health_status = agent.system_health_status
        assert isinstance(health_status, dict)
        assert "agent_status" in health_status
    
    def test_validate_phone_number_valid(self, agent):
        """Тест валидации валидного номера телефона."""
        result = agent.validate_phone_number("+7-999-123-45-67")
        assert result is True
    
    def test_validate_phone_number_invalid(self, agent):
        """Тест валидации невалидного номера телефона."""
        test_cases = [
            "invalid_phone",
            "123",
            "",
            "+12345678901234567890"  # Слишком длинный
        ]
        
        for phone in test_cases:
            result = agent.validate_phone_number(phone)
            assert result is False
        
        # Тест с None - должен вызывать исключение или возвращать False
        result = agent.validate_phone_number(None)
        assert result is False
    
    def test_validate_transaction_data_valid(self, agent):
        """Тест валидации валидных данных транзакции."""
        transaction = {
            "amount": 1000,
            "recipient": "Test User",
            "description": "Test transaction"
        }
        
        result = agent.validate_transaction_data(transaction)
        assert result is True
    
    def test_validate_transaction_data_invalid(self, agent):
        """Тест валидации невалидных данных транзакции."""
        test_cases = [
            {"amount": -100, "recipient": "User", "description": "Test"},  # Отрицательная сумма
            {"amount": 2000000, "recipient": "User", "description": "Test"},  # Слишком большая сумма
            {"recipient": "User", "description": "Test"},  # Отсутствует amount
            "invalid_data",  # Неправильный тип
            None
        ]
        
        for transaction in test_cases:
            result = agent.validate_transaction_data(transaction)
            assert result is False
    
    def test_get_fraud_patterns(self, agent):
        """Тест получения паттернов мошенничества."""
        patterns = agent.get_fraud_patterns()
        
        assert isinstance(patterns, dict)
        assert "phone_scam" in patterns
        assert "deepfake_video" in patterns
        # Проверяем существующие паттерны
        assert len(patterns) >= 2
    
    def test_cache_functionality(self, agent):
        """Тест функциональности кэширования."""
        # Очищаем кэш
        agent.clear_cache()
        
        # Первый вызов - должен быть MISS
        result1 = agent.validate_phone_number("+7-999-123-45-67")
        
        # Второй вызов - должен быть HIT
        result2 = agent.validate_phone_number("+7-999-123-45-67")
        
        assert result1 == result2
        
        # Проверяем статистику кэша
        cache_stats = agent.get_cache_stats()
        assert cache_stats["size"] > 0
        assert cache_stats["valid_entries"] > 0
    
    def test_metrics_collection(self, agent):
        """Тест сбора метрик."""
        # Выполняем несколько операций
        agent.validate_phone_number("+7-999-123-45-67")
        agent.validate_phone_number("invalid")
        agent.validate_transaction_data({"amount": 1000, "recipient": "User", "description": "Test"})
        
        # Получаем отчет по метрикам
        metrics_report = agent.get_metrics_report()
        
        assert isinstance(metrics_report, dict)
        # Должны быть метрики времени выполнения
        assert any("execution_time" in key for key in metrics_report.keys())


@pytest.mark.asyncio
class TestAntiFraudMasterAIAsync:
    """Асинхронные тесты для AntiFraudMasterAI."""
    
    @pytest.fixture
    async def agent(self):
        """Асинхронная фикстура агента."""
        config = AntiFraudConfig(
            max_concurrent_tasks=5,
            batch_size=3,
            log_level="DEBUG"
        )
        agent = AntiFraudMasterAI(config)
        yield agent
        # Очистка после тестов
        await agent.shutdown() if hasattr(agent, 'shutdown') else None
    
    async def test_batch_validate_phone_numbers(self, agent):
        """Тест пакетной валидации номеров телефонов."""
        phone_numbers = [
            "+7-999-123-45-67",
            "+7-888-111-22-33",
            "invalid_phone",
            "+7-777-444-55-66"
        ]
        
        results = await agent.batch_validate_phone_numbers(phone_numbers)
        
        assert len(results) == len(phone_numbers)
        assert results["+7-999-123-45-67"] is True
        assert results["invalid_phone"] is False
    
    async def test_batch_validate_transactions(self, agent):
        """Тест пакетной валидации транзакций."""
        transactions = [
            {"amount": 1000, "recipient": "User1", "description": "Test1"},
            {"amount": -100, "recipient": "User2", "description": "Test2"},  # Невалидная
            {"amount": 2000, "recipient": "User3", "description": "Test3"}
        ]
        
        results = await agent.batch_validate_transactions(transactions)
        
        assert len(results) == len(transactions)
        assert results["transaction_0"] is True
        assert results["transaction_1"] is False
        assert results["transaction_2"] is True
    
    async def test_concurrent_analysis(self, agent):
        """Тест конкурентного анализа."""
        analysis_tasks = [
            {"id": "task_1", "type": "phone_analysis"},
            {"id": "task_2", "type": "transaction_analysis"},
            {"id": "task_3", "type": "deepfake_analysis"}
        ]
        
        results = await agent.concurrent_analysis(analysis_tasks)
        
        assert len(results) == len(analysis_tasks)
        for result in results:
            assert result["status"] == "completed"
            assert "task_id" in result


class TestAntiFraudMasterAIIntegration:
    """Integration тесты для AntiFraudMasterAI."""
    
    @pytest.fixture
    def agent(self):
        """Фикстура агента для интеграционных тестов."""
        config = AntiFraudConfig(
            cache_enabled=True,
            metrics_collection_enabled=True,
            log_level="INFO"
        )
        return AntiFraudMasterAI(config)
    
    def test_full_workflow_phone_validation(self, agent):
        """Тест полного рабочего процесса валидации телефонов."""
        test_phones = [
            "+7-999-123-45-67",
            "+7-888-111-22-33",
            "invalid_phone",
            "+7-777-444-55-66",
            "another_invalid"
        ]
        
        results = []
        for phone in test_phones:
            result = agent.validate_phone_number(phone)
            results.append((phone, result))
        
        # Проверяем результаты
        valid_count = sum(1 for _, is_valid in results if is_valid)
        assert valid_count == 3  # 3 валидных номера
        
        # Проверяем кэш
        cache_stats = agent.get_cache_stats()
        assert cache_stats["size"] > 0
        
        # Проверяем метрики
        metrics = agent.get_metrics_report()
        assert len(metrics) > 0
    
    def test_full_workflow_transaction_validation(self, agent):
        """Тест полного рабочего процесса валидации транзакций."""
        transactions = [
            {"amount": 1000, "recipient": "User1", "description": "Valid transaction"},
            {"amount": -100, "recipient": "User2", "description": "Invalid amount"},
            {"amount": 2000, "recipient": "User3", "description": "Another valid"},
            {"recipient": "User4", "description": "Missing amount"},  # Отсутствует amount
            {"amount": 3000000, "recipient": "User5", "description": "Too large amount"}
        ]
        
        results = []
        for transaction in transactions:
            result = agent.validate_transaction_data(transaction)
            results.append((transaction, result))
        
        # Проверяем результаты
        valid_count = sum(1 for _, is_valid in results if is_valid)
        assert valid_count == 2  # 2 валидные транзакции
    
    @pytest.mark.asyncio
    async def test_full_async_workflow(self, agent):
        """Тест полного асинхронного рабочего процесса."""
        # Тест пакетной валидации
        phone_numbers = ["+7-999-123-45-67", "+7-888-111-22-33", "invalid"]
        phone_results = await agent.batch_validate_phone_numbers(phone_numbers)
        
        transactions = [
            {"amount": 1000, "recipient": "User1", "description": "Test1"},
            {"amount": 2000, "recipient": "User2", "description": "Test2"}
        ]
        transaction_results = await agent.batch_validate_transactions(transactions)
        
        # Тест конкурентного анализа
        analysis_tasks = [
            {"id": "task_1", "type": "analysis1"},
            {"id": "task_2", "type": "analysis2"}
        ]
        analysis_results = await agent.concurrent_analysis(analysis_tasks)
        
        # Проверяем все результаты
        assert len(phone_results) == 3
        assert len(transaction_results) == 2
        assert len(analysis_results) == 2
        
        # Проверяем метрики
        metrics = agent.get_metrics_report()
        assert len(metrics) > 0
        
        # Проверяем кэш
        cache_stats = agent.get_cache_stats()
        assert cache_stats["size"] > 0
    
    def test_error_handling_and_recovery(self, agent):
        """Тест обработки ошибок и восстановления."""
        # Тест с некорректными данными
        invalid_inputs = [
            None,
            123,
            [],
            {"invalid": "data"}
        ]
        
        for invalid_input in invalid_inputs:
            # Не должно вызывать исключений
            try:
                if isinstance(invalid_input, str):
                    result = agent.validate_phone_number(invalid_input)
                else:
                    result = agent.validate_transaction_data(invalid_input)
                assert result is False  # Все должны возвращать False
            except Exception as e:
                pytest.fail(f"Неожиданное исключение: {e}")
        
        # Агент должен продолжать работать
        valid_result = agent.validate_phone_number("+7-999-123-45-67")
        assert valid_result is True
    
    def test_performance_metrics(self, agent):
        """Тест метрик производительности."""
        # Выполняем множество операций
        start_time = time.time()
        
        for i in range(100):
            agent.validate_phone_number(f"+7-999-{i:03d}-{i:02d}-{i:02d}")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Проверяем, что операции выполняются достаточно быстро
        assert execution_time < 5.0  # Менее 5 секунд для 100 операций
        
        # Проверяем метрики
        metrics = agent.get_metrics_report()
        assert len(metrics) > 0
        
        # Проверяем кэш
        cache_stats = agent.get_cache_stats()
        assert cache_stats["size"] > 0


class TestAntiFraudMasterAIPerformance:
    """Тесты производительности для AntiFraudMasterAI."""
    
    @pytest.fixture
    def agent(self):
        """Фикстура агента для тестов производительности."""
        config = AntiFraudConfig(
            cache_enabled=True,
            metrics_collection_enabled=True
        )
        return AntiFraudMasterAI(config)
    
    def test_cache_performance(self, agent):
        """Тест производительности кэширования."""
        phone_number = "+7-999-123-45-67"
        
        # Первый вызов (должен быть медленнее)
        start_time = time.time()
        result1 = agent.validate_phone_number(phone_number)
        time1 = time.time() - start_time
        
        # Второй вызов (должен быть быстрее из-за кэша)
        start_time = time.time()
        result2 = agent.validate_phone_number(phone_number)
        time2 = time.time() - start_time
        
        assert result1 == result2
        assert time2 <= time1  # Второй вызов не должен быть медленнее
    
    def test_batch_processing_performance(self, agent):
        """Тест производительности пакетной обработки."""
        phone_numbers = [f"+7-999-{i:03d}-{i:02d}-{i:02d}" for i in range(50)]
        
        start_time = time.time()
        
        # Обрабатываем по одному
        single_results = []
        for phone in phone_numbers:
            single_results.append(agent.validate_phone_number(phone))
        
        single_time = time.time() - start_time
        
        # Проверяем, что все результаты корректны
        assert len(single_results) == 50
        assert all(single_results)  # Все должны быть валидными


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v", "--tb=short"])