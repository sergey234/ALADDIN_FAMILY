#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тесты производительности для Dark Web Monitoring Agent

Проверяет скорость работы, использование памяти, производительность кэша.

Запуск:
    pytest backend_tests/test_dark_web_monitoring_performance.py -v -s
"""

import pytest
import sys
import os
import time
from unittest.mock import Mock, patch
import tracemalloc

# Добавляем путь к security/ai_agents
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'security', 'ai_agents'))

from dark_web_monitoring_agent import DarkWebMonitoringAgent


class TestPerformance:
    """Тесты производительности"""

    @pytest.fixture
    def agent(self):
        """Создание экземпляра агента"""
        config = {
            "hibp_api_key": "test-key",
            "cache_ttl": 3600
        }
        return DarkWebMonitoringAgent(config)

    def test_cache_performance(self, agent):
        """Тест производительности кэша"""
        email = "test@example.com"

        # Заполняем кэш
        start_time = time.time()
        for i in range(100):
            agent._set_cache(f"test:key{i}", {"data": f"value{i}"})
        write_time = time.time() - start_time

        # Читаем из кэша
        start_time = time.time()
        for i in range(100):
            agent._check_cache(f"test:key{i}")
        read_time = time.time() - start_time

        print(f"\n📊 Кэш производительность:")
        print(f"   Запись 100 записей: {write_time:.4f}s")
        print(f"   Чтение 100 записей: {read_time:.4f}s")
        print(f"   Средняя скорость записи: {100/write_time:.0f} записей/с")
        print(f"   Средняя скорость чтения: {100/read_time:.0f} записей/с")

        # Проверяем что операции быстрые (< 0.1s для 100 операций)
        assert write_time < 0.1, "Запись в кэш слишком медленная"
        assert read_time < 0.1, "Чтение из кэша слишком медленное"

    def test_email_validation_performance(self, agent):
        """Тест производительности валидации email"""
        emails = [f"test{i}@example.com" for i in range(1000)]

        start_time = time.time()
        for email in emails:
            agent._default_validate_email(email)
        validation_time = time.time() - start_time

        print(f"\n📊 Email валидация:")
        print(f"   1000 email валидаций: {validation_time:.4f}s")
        print(f"   Средняя скорость: {1000/validation_time:.0f} валидаций/с")

        assert validation_time < 0.5, "Валидация email слишком медленная"

    def test_hash_performance(self, agent):
        """Тест производительности хеширования email"""
        emails = [f"test{i}@example.com" for i in range(1000)]

        start_time = time.time()
        for email in emails:
            agent._hash_email(email)
        hash_time = time.time() - start_time

        print(f"\n📊 Хеширование email:")
        print(f"   1000 хеширований: {hash_time:.4f}s")
        print(f"   Средняя скорость: {1000/hash_time:.0f} хешей/с")

        assert hash_time < 0.5, "Хеширование слишком медленное"

    @patch('dark_web_monitoring_agent.DarkWebMonitoringAgent._make_http_request')
    def test_check_breach_performance(self, mock_request, agent):
        """Тест производительности проверки утечек"""
        mock_request.return_value = {
            "status_code": 200,
            "data": []
        }

        emails = [f"test{i}@example.com" for i in range(10)]

        start_time = time.time()
        for email in emails:
            agent.check_email_breach(email, include_russian=False)
        check_time = time.time() - start_time

        print(f"\n📊 Проверка утечек:")
        print(f"   10 проверок: {check_time:.4f}s")
        print(f"   Средняя скорость: {10/check_time:.2f} проверок/с")

        # Проверка должна быть быстрой (мокированный запрос)
        assert check_time < 1.0, "Проверка утечек слишком медленная"

    def test_memory_usage(self, agent):
        """Тест использования памяти"""
        tracemalloc.start()

        # Заполняем кэш
        for i in range(1000):
            agent._set_cache(f"test:key{i}", {"data": f"value{i}" * 100})

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"\n📊 Использование памяти:")
        print(f"   Текущее: {current / 1024 / 1024:.2f} MB")
        print(f"   Пиковое: {peak / 1024 / 1024:.2f} MB")

        # Кэш с 1000 записей не должен занимать больше 50MB
        assert peak < 50 * 1024 * 1024, "Использование памяти слишком высокое"

    def test_concurrent_monitoring(self, agent):
        """Тест производительности при множественных мониторингах"""
        # Запускаем множество мониторингов
        start_time = time.time()
        for i in range(100):
            agent.start_monitoring(f"user{i}", email=f"user{i}@example.com")
        start_time = time.time() - start_time

        # Получаем статус всех
        status_start = time.time()
        status = agent.get_monitoring_status()
        status_time = time.time() - status_start

        print(f"\n📊 Множественные мониторинги:")
        print(f"   Запуск 100 мониторингов: {start_time:.4f}s")
        print(f"   Получение статуса всех: {status_time:.4f}s")

        assert status["total_active"] == 100
        assert start_time < 0.5, "Запуск мониторингов слишком медленный"

    def test_cache_statistics_performance(self, agent):
        """Тест производительности получения статистики кэша"""
        # Заполняем кэш
        for i in range(500):
            agent._set_cache(f"test:key{i}", {"data": f"value{i}"})

        start_time = time.time()
        for _ in range(100):
            stats = agent.get_cache_stats()
        stats_time = time.time() - start_time

        print(f"\n📊 Статистика кэша:")
        print(f"   100 запросов статистики: {stats_time:.4f}s")
        print(f"   Средняя скорость: {100/stats_time:.0f} запросов/с")

        assert stats_time < 1.0, "Получение статистики слишком медленное"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
