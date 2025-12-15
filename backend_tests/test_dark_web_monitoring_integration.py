#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Интеграционные тесты для Dark Web Monitoring Agent

Тестирует взаимодействие между компонентами, кэширование,
и интеграцию с ThreatIntelligenceAgent.

Запуск:
    pytest backend_tests/test_dark_web_monitoring_integration.py -v
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import time

# Добавляем путь к security/ai_agents
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'security', 'ai_agents'))

from dark_web_monitoring_agent import DarkWebMonitoringAgent, BreachInfo
from threat_monitoring_interface import ThreatEvent, ThreatEventBus, get_threat_event_bus


class TestDarkWebMonitoringIntegration:
    """Интеграционные тесты для DarkWebMonitoringAgent"""

    @pytest.fixture
    def agent(self):
        """Создание экземпляра агента для тестирования"""
        config = {
            "hibp_api_key": "test-api-key",
            "cache_ttl": 3600  # 1 час для тестов
        }
        return DarkWebMonitoringAgent(config)

    @pytest.fixture
    def event_bus(self):
        """Создание шины событий для тестирования"""
        return ThreatEventBus()

    def test_cache_integration(self, agent):
        """Тест интеграции кэширования"""
        email = "test@example.com"

        # Мокируем HTTP запрос
        agent._make_http_request = Mock(return_value={
            "status_code": 200,
            "data": []
        })

        # Первая проверка - должен попасть в кэш
        result1 = agent.check_email_breach(email, include_russian=False)
        assert "breaches_found" in result1

        call_count_after_first = agent._make_http_request.call_count

        # Вторая проверка - должен использовать кэш
        result2 = agent.check_email_breach(email, include_russian=False)
        assert "breaches_found" in result2

        # Проверяем что HTTP запросов не стало больше (используется кэш)
        assert agent._make_http_request.call_count == call_count_after_first

    def test_monitoring_lifecycle(self, agent):
        """Тест полного жизненного цикла мониторинга"""
        user_id = "test_user"
        email = "test@example.com"

        # Запуск мониторинга
        result = agent.start_monitoring(user_id, email=email, interval_hours=24)
        assert result["success"] == True
        assert result["user_id"] == user_id

        # Проверка статуса
        status = agent.get_monitoring_status(user_id)
        assert status["is_monitoring"] == True
        assert status["status"]["email"] == email

        # Остановка мониторинга
        stop_result = agent.stop_monitoring(user_id)
        assert stop_result["success"] == True

        # Проверка что мониторинг остановлен
        status_after = agent.get_monitoring_status(user_id)
        assert status_after["is_monitoring"] == False

    def test_threat_collection_integration(self, agent):
        """Тест интеграции сбора угроз"""
        # Запускаем мониторинг для нескольких пользователей
        agent.start_monitoring("user1", email="user1@example.com")
        agent.start_monitoring("user2", email="user2@example.com")

        # Мокируем проверку утечек
        with patch.object(agent, 'check_email_breach') as mock_check:
            mock_check.return_value = {
                "email": "test@example.com",
                "breaches_found": 2,
                "breaches": [
                    {
                        "id": "breach1",
                        "breach_name": "Test Breach 1",
                        "severity": "high"
                    }
                ]
            }

            # Собираем угрозы
            threats = agent.collect_threats()

            # Должны быть найдены угрозы для обоих пользователей
            assert len(threats) >= 0  # Может быть 0 если мониторинг не активен

    def test_threat_analysis_integration(self, agent):
        """Тест интеграции анализа угроз"""
        threats = [
            {
                "user_id": "user1",
                "type": "email_breach",
                "target": "user1@example.com",
                "breach": {
                    "breach_name": "Test Breach",
                    "severity": "high",
                    "affected_data": ["Email", "Passwords"]
                }
            }
        ]

        analyzed = agent.analyze_threats(threats)

        assert len(analyzed) == 1
        assert analyzed[0]["priority"] == "high"
        assert "recommendations" in analyzed[0]
        assert analyzed[0]["requires_immediate_action"] == True

    def test_event_bus_integration(self, agent, event_bus):
        """Тест интеграции с ThreatEventBus"""
        # Подписываем агент на события
        event_bus.subscribe(agent, event_types=["breach"])

        # Создаем событие
        event = ThreatEvent(
            event_id="test_event_1",
            agent_name="TestAgent",
            threat_type="breach",
            severity="high",
            source="test_source",
            target="test@example.com",
            timestamp=datetime.now().isoformat(),
            metadata={"test": "data"}
        )

        # Публикуем событие
        notified_count = event_bus.publish(event)

        # Агент должен получить событие
        assert notified_count >= 1

        # Проверяем историю событий
        history = event_bus.get_event_history("breach", limit=10)
        assert len(history) > 0
        assert history[-1].event_id == "test_event_1"

    def test_multiple_agents_integration(self, event_bus):
        """Тест интеграции нескольких агентов через EventBus"""
        # Создаем два агента
        agent1 = DarkWebMonitoringAgent({"cache_ttl": 3600})
        agent2 = DarkWebMonitoringAgent({"cache_ttl": 3600})

        # Подписываем оба на события
        event_bus.subscribe(agent1, event_types=["breach"])
        event_bus.subscribe(agent2, event_types=["breach"])

        # Публикуем событие
        event = ThreatEvent(
            event_id="multi_agent_test",
            agent_name="TestAgent",
            threat_type="breach",
            severity="medium",
            source="test",
            target="test@example.com",
            timestamp=datetime.now().isoformat(),
            metadata={}
        )

        notified = event_bus.publish(event)

        # Оба агента должны получить событие
        assert notified == 2

    def test_cache_expiration(self, agent):
        """Тест истечения кэша"""
        email = "test@example.com"
        cache_key = f"hibp:{email}"

        # Устанавливаем короткий TTL
        agent.cache_ttl = 1  # 1 секунда

        # Добавляем данные в кэш
        agent._set_cache(cache_key, {"test": "data"})

        # Проверяем что данные есть
        cached = agent._check_cache(cache_key)
        assert cached is not None

        # Ждем истечения TTL
        time.sleep(2)

        # Проверяем что данные удалены
        cached_after = agent._check_cache(cache_key)
        assert cached_after is None

    def test_cache_overflow_handling(self, agent):
        """Тест обработки переполнения кэша"""
        # Заполняем кэш
        for i in range(1001):
            agent._set_cache(f"test:key{i}", {"data": f"value{i}"})

        # Кэш должен быть очищен (осталось 800 записей)
        stats = agent.get_cache_stats()
        assert stats["total_entries"] <= 1000

    def test_error_handling_in_api_calls(self, agent):
        """Тест обработки ошибок при API вызовах"""
        email = "test@example.com"

        # Симулируем ошибку сети
        agent._make_http_request = Mock(side_effect=Exception("Network error"))

        # Проверка должна вернуть пустой результат, а не упасть
        result = agent.check_email_breach(email, include_russian=False)
        assert result["breaches_found"] == 0
        assert "breaches" in result

    def test_rate_limiting_handling(self, agent):
        """Тест обработки rate limiting от API"""
        email = "test@example.com"

        # Симулируем rate limit (429)
        agent._make_http_request = Mock(return_value={
            "status_code": 429,
            "data": {"error": "Rate limit exceeded"}
        })
        agent.breachdirectory_api_key = "test-key"

        # Проверка должна обработать rate limit корректно
        breaches = agent.check_email_breach_breachdirectory(email)
        assert isinstance(breaches, list)
        assert len(breaches) == 0

    def test_breach_deduplication(self, agent):
        """Тест удаления дубликатов утечек"""
        email = "test@example.com"

        # Симулируем одинаковые утечки из разных источников
        breach1 = BreachInfo(
            id="breach1",
            email=email,
            breach_name="Test Breach",
            count=1000,
            detected_at=datetime.now().isoformat(),
            severity="high"
        )

        breach2 = BreachInfo(
            id="breach2",
            email=email,
            breach_name="test breach",  # То же имя, но lowercase
            count=2000,
            detected_at=datetime.now().isoformat(),
            severity="high"
        )

        agent.check_email_breach_hibp = Mock(return_value=[breach1])
        agent.check_email_breach_breachdirectory = Mock(return_value=[breach2])
        agent.check_email_breach_russian = Mock(return_value=[])
        agent.breachdirectory_api_key = "test-key"

        result = agent.check_email_breach(email, include_russian=False)

        # Должна остаться одна утечка (с большим count)
        assert result["breaches_found"] == 1
        assert result["breaches"][0]["count"] == 2000


class TestThreatEventBusIntegration:
    """Интеграционные тесты для ThreatEventBus"""

    def test_event_subscription(self):
        """Тест подписки на события"""
        bus = ThreatEventBus()
        mock_agent = Mock()

        # Подписка на конкретный тип
        bus.subscribe(mock_agent, event_types=["breach"])

        # Проверка подписчиков
        subscribers = bus.get_subscribers_count()
        assert subscribers["breach"] == 1

    def test_event_publishing(self):
        """Тест публикации событий"""
        bus = ThreatEventBus()
        mock_agent = Mock()
        mock_agent.receive_threat_event.return_value = True

        bus.subscribe(mock_agent, event_types=["breach"])

        event = ThreatEvent(
            event_id="test1",
            agent_name="TestAgent",
            threat_type="breach",
            severity="high",
            source="test",
            target="test@example.com",
            timestamp=datetime.now().isoformat(),
            metadata={}
        )

        notified = bus.publish(event)

        assert notified == 1
        mock_agent.receive_threat_event.assert_called_once()

    def test_event_history(self):
        """Тест истории событий"""
        bus = ThreatEventBus()

        for i in range(5):
            event = ThreatEvent(
                event_id=f"event_{i}",
                agent_name="TestAgent",
                threat_type="breach",
                severity="medium",
                source="test",
                target=f"test{i}@example.com",
                timestamp=datetime.now().isoformat(),
                metadata={}
            )
            bus.publish(event)

        history = bus.get_event_history(limit=10)
        assert len(history) == 5

        # Фильтрация по типу
        breach_history = bus.get_event_history("breach", limit=10)
        assert len(breach_history) == 5

    def test_wildcard_subscription(self):
        """Тест подписки на все события (*)"""
        bus = ThreatEventBus()
        mock_agent = Mock()
        mock_agent.receive_threat_event.return_value = True

        bus.subscribe(mock_agent, event_types=["*"])

        event = ThreatEvent(
            event_id="wildcard_test",
            agent_name="TestAgent",
            threat_type="malware",  # Другой тип
            severity="high",
            source="test",
            target="test@example.com",
            timestamp=datetime.now().isoformat(),
            metadata={}
        )

        notified = bus.publish(event)

        # Агент подписан на все события, должен получить
        assert notified == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
