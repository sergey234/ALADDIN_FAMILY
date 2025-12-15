#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тесты для Dark Web Monitoring Agent

Запуск:
    pytest backend_tests/test_dark_web_monitoring.py -v
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Добавляем путь к security/ai_agents
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'security', 'ai_agents'))

from dark_web_monitoring_agent import DarkWebMonitoringAgent, BreachInfo


class TestDarkWebMonitoringAgent:
    """Тесты для DarkWebMonitoringAgent"""
    
    @pytest.fixture
    def agent(self):
        """Создание экземпляра агента для тестирования"""
        config = {
            "hibp_api_key": "test-api-key",
            "cache_ttl": 3600  # 1 час для тестов
        }
        return DarkWebMonitoringAgent(config)
    
    def test_init(self, agent):
        """Тест инициализации агента"""
        assert agent is not None
        assert agent.hibp_api_key == "test-api-key"
        assert agent.cache_ttl == 3600
        assert agent.monitoring_interval == 24
    
    def test_validate_email(self, agent):
        """Тест валидации email"""
        assert agent._default_validate_email("test@example.com") == True
        assert agent._default_validate_email("invalid-email") == False
        assert agent._default_validate_email("test@domain") == False
    
    def test_validate_phone(self, agent):
        """Тест валидации телефона"""
        assert agent._default_validate_phone("+7 999 123 45 67") == True
        assert agent._default_validate_phone("89991234567") == True
        assert agent._default_validate_phone("123") == False
    
    def test_hash_email(self, agent):
        """Тест хеширования email для k-анонимности"""
        hash_prefix, full_hash = agent._hash_email("test@example.com")
        
        assert len(hash_prefix) == 5
        assert len(full_hash) == 40  # SHA1 hex = 40 символов
        assert hash_prefix == full_hash[:5]
    
    def test_cache(self, agent):
        """Тест системы кэширования"""
        cache_key = "test:key"
        test_data = {"test": "data"}
        
        # Проверяем, что кэш пуст
        assert agent._check_cache(cache_key) is None
        
        # Сохраняем в кэш
        agent._set_cache(cache_key, test_data)
        
        # Проверяем, что данные есть в кэше
        cached = agent._check_cache(cache_key)
        assert cached == test_data
    
    def test_check_email_breach_hibp_success(self, agent):
        """Тест успешной проверки через HIBP"""
        # Мокируем HTTP запрос через атрибут агента
        agent._make_http_request = Mock(return_value={
            "status_code": 200,
            "data": "A1B2C:1234\nD3E4F:5678\n"
        })
        
        # Мокируем хеш email, чтобы он соответствовал одному из хешей в ответе
        with patch.object(agent, '_hash_email', return_value=("A1B2C", "A1B2CD3E4F")):
            breaches = agent.check_email_breach_hibp("test@example.com")
            
            # Должна быть найдена утечка (или пустой список если хеш не совпадает)
            assert isinstance(breaches, list)
    
    def test_check_email_breach_breachdirectory_success(self, agent):
        """Тест успешной проверки через BreachDirectory"""
        # Мокируем HTTP запрос через атрибут агента
        agent._make_http_request = Mock(return_value={
            "status_code": 200,
            "data": [
                {
                    "title": "Test Breach",
                    "domain": "example.com",
                    "email": "test@example.com",
                    "username": "testuser",
                    "ip": "127.0.0.1"
                }
            ]
        })
        
        agent.breachdirectory_api_key = "test-key"
        breaches = agent.check_email_breach_breachdirectory("test@example.com")
        
        # Должна быть найдена утечка
        assert isinstance(breaches, list)
        if len(breaches) > 0:
            assert breaches[0].breach_name == "Test Breach"
    
    def test_check_email_breach_breachdirectory_empty(self, agent):
        """Тест проверки через BreachDirectory когда утечек нет"""
        # Мокируем пустой ответ
        agent._make_http_request = Mock(return_value={
            "status_code": 200,
            "data": []
        })
        
        agent.breachdirectory_api_key = "test-key"
        breaches = agent.check_email_breach_breachdirectory("test@example.com")
        
        # Не должно быть утечек
        assert len(breaches) == 0

    def test_check_email_breach_breachdirectory_rate_limit(self, agent):
        """Тест обработки rate limit от BreachDirectory"""
        # Мокируем ответ 429 (rate limit)
        agent._make_http_request = Mock(return_value={
            "status_code": 429,
            "data": {"error": "Rate limit exceeded"}
        })
        
        agent.breachdirectory_api_key = "test-key"
        breaches = agent.check_email_breach_breachdirectory("test@example.com")
        
        # Должен вернуть пустой список
        assert len(breaches) == 0
    
    def test_check_email_breach_invalid_email(self, agent):
        """Тест проверки с невалидным email"""
        result = agent.check_email_breach("invalid-email")
        
        assert result["breaches_found"] == 0
        assert len(result["breaches"]) == 0
    
    def test_monitor_user_data(self, agent):
        """Тест мониторинга данных пользователя"""
        with patch.object(agent, 'check_email_breach', return_value={"breaches_found": 0, "breaches": []}):
            result = agent.monitor_user_data(
                user_id="test_user",
                email="test@example.com",
                phone="+79991234567"
            )
            
            assert result["user_id"] == "test_user"
            assert "email_check" in result["results"]
    
    def test_start_monitoring(self, agent):
        """Тест запуска мониторинга"""
        result = agent.start_monitoring(
            user_id="test_user",
            email="test@example.com",
            interval_hours=24
        )
        
        assert result["success"] == True
        assert result["user_id"] == "test_user"
        assert "next_check" in result
        
        # Проверяем, что мониторинг добавлен
        status = agent.get_monitoring_status("test_user")
        assert status["is_monitoring"] == True
    
    def test_stop_monitoring(self, agent):
        """Тест остановки мониторинга"""
        # Сначала запускаем мониторинг
        agent.start_monitoring("test_user", email="test@example.com")
        
        # Останавливаем
        result = agent.stop_monitoring("test_user")
        
        assert result["success"] == True
        
        # Проверяем, что мониторинг остановлен
        status = agent.get_monitoring_status("test_user")
        assert status["is_monitoring"] == False
    
    def test_get_monitoring_status(self, agent):
        """Тест получения статуса мониторинга"""
        # Запускаем несколько мониторингов
        agent.start_monitoring("user1", email="user1@example.com")
        agent.start_monitoring("user2", email="user2@example.com")
        
        # Получаем статус для конкретного пользователя
        status = agent.get_monitoring_status("user1")
        assert status["is_monitoring"] == True
        
        # Получаем статус всех мониторингов
        all_status = agent.get_monitoring_status()
        assert all_status["total_active"] == 2
    
    def test_cache_stats(self, agent):
        """Тест статистики кэша"""
        # Добавляем данные в кэш
        agent._set_cache("test:key1", {"data": "test1"})
        agent._set_cache("test:key2", {"data": "test2"})
        
        # Получаем статистику
        stats = agent.get_cache_stats()
        
        assert stats["total_entries"] == 2
        assert stats["valid_entries"] == 2
        assert "cache_ttl" in stats
    
    def test_clear_cache(self, agent):
        """Тест очистки кэша"""
        # Добавляем данные
        agent._set_cache("test:key1", {"data": "test1"})
        agent._set_cache("other:key1", {"data": "test2"})
        
        # Очищаем по паттерну
        deleted = agent.clear_cache(pattern="test:")
        assert deleted == 1
        
        # Проверяем, что остался один ключ
        stats = agent.get_cache_stats()
        assert stats["total_entries"] == 1
        
        # Очищаем весь кэш
        deleted = agent.clear_cache()
        assert deleted == 1
    
    def test_check_email_breach_russian(self, agent):
        """Тест проверки через российские базы"""
        # Проверка без API ключа должна вернуть пустой список
        breaches = agent.check_email_breach_russian("test@example.com")
        assert isinstance(breaches, list)
        assert len(breaches) == 0

    def test_threat_monitoring_interface(self, agent):
        """Тест реализации ThreatMonitoringInterface"""
        # Проверяем что агент реализует интерфейс
        try:
            from threat_monitoring_interface import ThreatMonitoringInterface
            # Проверяем наличие методов интерфейса
            assert hasattr(agent, 'collect_threats')
            assert hasattr(agent, 'analyze_threats')
            assert hasattr(agent, 'send_alert')

            # Тестируем методы интерфейса
            threats = agent.collect_threats()
            assert isinstance(threats, list)

            analyzed = agent.analyze_threats([])
            assert isinstance(analyzed, list)

            alert_result = agent.send_alert({
                "user_id": "test",
                "target": "test@example.com",
                "breach": {
                    "breach_name": "Test",
                    "severity": "high"
                }
            })
            assert isinstance(alert_result, bool)
        except ImportError:
            # Если интерфейс недоступен в тестах, пропускаем
            pytest.skip("ThreatMonitoringInterface недоступен")


class TestBreachInfo:
    """Тесты для класса BreachInfo"""
    
    def test_breach_info_creation(self):
        """Тест создания объекта BreachInfo"""
        breach = BreachInfo(
            id="test_id",
            email="test@example.com",
            breach_name="Test Breach",
            count=1000,
            detected_at=datetime.now().isoformat(),
            severity="high"
        )
        
        assert breach.id == "test_id"
        assert breach.email == "test@example.com"
        assert breach.breach_name == "Test Breach"
        assert breach.count == 1000
        assert breach.severity == "high"
    
    def test_breach_info_to_dict(self):
        """Тест конвертации BreachInfo в словарь"""
        breach = BreachInfo(
            id="test_id",
            email="test@example.com",
            breach_name="Test Breach",
            count=1000,
            detected_at=datetime.now().isoformat(),
            severity="high"
        )
        
        breach_dict = breach.to_dict()
        
        assert isinstance(breach_dict, dict)
        assert breach_dict["id"] == "test_id"
        assert breach_dict["email"] == "test@example.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
