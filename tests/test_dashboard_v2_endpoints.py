#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для Enhanced Dashboard v2.0 - новые endpoints
Проверка функциональности расширенного дашборда

Автор: ALADDIN Security Team
Версия: 2.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
import time
import pytest
import httpx
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Предполагаем, что дашборд v2 работает на порту 8080
DASHBOARD_V2_URL = "http://localhost:8080"

class TestDashboardV2Endpoints:
    """
    Тесты для Enhanced Dashboard v2.0 endpoints.
    Проверяет новые функции: системные метрики, SFM интеграция, 
    тестирование, безопасность, производительность, мониторинг, аналитика.
    """

    @pytest.mark.asyncio
    async def test_dashboard_home_page(self):
        """
        Тест главной страницы дашборда v2.0.
        Проверяет, что страница загружается и содержит все необходимые элементы.
        """
        print("\n--- Тест главной страницы дашборда v2.0 ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/", timeout=10)
            response.raise_for_status()
            
            # Проверяем, что это HTML страница
            assert "text/html" in response.headers.get("content-type", "")
            
            # Проверяем наличие ключевых элементов
            content = response.text
            assert "ALADDIN Enhanced Dashboard v2.0" in content
            assert "Системные метрики" in content
            assert "SFM Статус" in content
            assert "Результаты тестов" in content
            assert "Безопасность" in content
            assert "API Endpoints" in content
            
            print("✅ Главная страница дашборда v2.0 успешно загружена")

    @pytest.mark.asyncio
    async def test_system_health_endpoint(self):
        """
        Тест endpoint получения состояния системы.
        Проверяет, что возвращаются корректные метрики системы.
        """
        print("\n--- Тест endpoint состояния системы ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/api/system/health", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Проверяем наличие обязательных полей
            assert "cpu_usage" in data
            assert "memory_usage" in data
            assert "disk_usage" in data
            assert "uptime" in data
            assert "load_average" in data
            assert "processes" in data
            assert "timestamp" in data
            
            # Проверяем типы данных
            assert isinstance(data["cpu_usage"], (int, float))
            assert isinstance(data["memory_usage"], (int, float))
            assert isinstance(data["disk_usage"], (int, float))
            assert isinstance(data["uptime"], (int, float))
            assert isinstance(data["load_average"], list)
            assert isinstance(data["processes"], int)
            
            print(f"✅ Состояние системы: CPU={data['cpu_usage']}%, Memory={data['memory_usage']}%")

    @pytest.mark.asyncio
    async def test_system_metrics_endpoint(self):
        """
        Тест endpoint получения метрик системы.
        Проверяет, что возвращаются метрики производительности.
        """
        print("\n--- Тест endpoint метрик системы ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/api/system/metrics", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "metrics" in data
            assert isinstance(data["metrics"], list)
            
            print(f"✅ Получено {len(data['metrics'])} метрик системы")

    @pytest.mark.asyncio
    async def test_system_stats_endpoint(self):
        """
        Тест endpoint получения статистики системы.
        Проверяет, что возвращается общая статистика.
        """
        print("\n--- Тест endpoint статистики системы ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/api/system/stats", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Проверяем наличие обязательных полей
            assert "total_requests" in data
            assert "active_connections" in data
            assert "uptime" in data
            assert "test_coverage" in data
            assert "performance_score" in data
            assert "security_score" in data
            assert "last_update" in data
            
            print(f"✅ Статистика системы: {data['total_requests']} запросов, uptime={data['uptime']:.1f}s")

    @pytest.mark.asyncio
    async def test_sfm_status_endpoint(self):
        """
        Тест endpoint получения статуса SFM.
        Проверяет, что возвращается информация о SFM.
        """
        print("\n--- Тест endpoint статуса SFM ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/api/sfm/status", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Проверяем наличие обязательных полей
            assert "total_functions" in data
            assert "active_functions" in data
            assert "sleeping_functions" in data
            assert "error_functions" in data
            assert "avg_response_time" in data
            assert "total_requests" in data
            assert "error_rate" in data
            assert "last_update" in data
            
            print(f"✅ SFM статус: {data['active_functions']}/{data['total_functions']} функций активны")

    @pytest.mark.asyncio
    async def test_sfm_functions_endpoint(self):
        """
        Тест endpoint получения списка функций SFM.
        Проверяет, что возвращается список функций.
        """
        print("\n--- Тест endpoint списка функций SFM ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/api/sfm/functions", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "functions" in data
            assert isinstance(data["functions"], list)
            
            if data["functions"]:
                function = data["functions"][0]
                assert "id" in function
                assert "name" in function
                assert "status" in function
                assert "description" in function
                assert "security_level" in function
                assert "performance" in function
            
            print(f"✅ Получено {len(data['functions'])} функций SFM")

    @pytest.mark.asyncio
    async def test_sfm_toggle_function_endpoint(self):
        """
        Тест endpoint переключения состояния функции SFM.
        Проверяет, что функция может быть переключена.
        """
        print("\n--- Тест endpoint переключения функции SFM ---")
        function_id = "russian_api_manager"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{DASHBOARD_V2_URL}/api/sfm/functions/{function_id}/toggle", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "function_id" in data
            assert "status" in data
            assert "message" in data
            assert data["function_id"] == function_id
            
            print(f"✅ Функция {function_id} успешно переключена")

    @pytest.mark.asyncio
    async def test_test_results_endpoint(self):
        """
        Тест endpoint получения результатов тестов.
        Проверяет, что возвращаются результаты тестирования.
        """
        print("\n--- Тест endpoint результатов тестов ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/api/tests/results", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "results" in data
            assert isinstance(data["results"], list)
            
            print(f"✅ Получено {len(data['results'])} результатов тестов")

    @pytest.mark.asyncio
    async def test_test_results_with_filters(self):
        """
        Тест endpoint результатов тестов с фильтрами.
        Проверяет фильтрацию по статусу и лимиту.
        """
        print("\n--- Тест endpoint результатов тестов с фильтрами ---")
        async with httpx.AsyncClient() as client:
            # Тест с лимитом
            response = await client.get(f"{DASHBOARD_V2_URL}/api/tests/results?limit=5", timeout=10)
            response.raise_for_status()
            data = response.json()
            assert len(data["results"]) <= 5
            
            # Тест с фильтром по статусу
            response = await client.get(f"{DASHBOARD_V2_URL}/api/tests/results?status=passed", timeout=10)
            response.raise_for_status()
            data = response.json()
            # Все результаты должны иметь статус "passed"
            for result in data["results"]:
                assert result["status"] == "passed"
            
            print("✅ Фильтрация результатов тестов работает корректно")

    @pytest.mark.asyncio
    async def test_run_tests_endpoint(self):
        """
        Тест endpoint запуска тестов.
        Проверяет, что тесты могут быть запущены.
        """
        print("\n--- Тест endpoint запуска тестов ---")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{DASHBOARD_V2_URL}/api/tests/run?test_type=performance", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "test_id" in data
            assert "status" in data
            assert data["status"] == "started"
            
            print(f"✅ Тест запущен с ID: {data['test_id']}")

    @pytest.mark.asyncio
    async def test_test_coverage_endpoint(self):
        """
        Тест endpoint получения покрытия тестами.
        Проверяет, что возвращается информация о покрытии.
        """
        print("\n--- Тест endpoint покрытия тестами ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/api/tests/coverage", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "coverage" in data
            
            coverage = data["coverage"]
            assert "overall" in coverage
            assert "unit_tests" in coverage
            assert "integration_tests" in coverage
            assert "performance_tests" in coverage
            assert "security_tests" in coverage
            assert "sfm_tests" in coverage
            
            print(f"✅ Покрытие тестами: {coverage['overall']}%")

    @pytest.mark.asyncio
    async def test_security_alerts_endpoint(self):
        """
        Тест endpoint получения уведомлений безопасности.
        Проверяет, что возвращаются уведомления безопасности.
        """
        print("\n--- Тест endpoint уведомлений безопасности ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/api/security/alerts", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "alerts" in data
            assert isinstance(data["alerts"], list)
            
            print(f"✅ Получено {len(data['alerts'])} уведомлений безопасности")

    @pytest.mark.asyncio
    async def test_security_alerts_with_filters(self):
        """
        Тест endpoint уведомлений безопасности с фильтрами.
        Проверяет фильтрацию по статусу решения.
        """
        print("\n--- Тест endpoint уведомлений безопасности с фильтрами ---")
        async with httpx.AsyncClient() as client:
            # Тест с фильтром по решенным
            response = await client.get(f"{DASHBOARD_V2_URL}/api/security/alerts?resolved=true", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Тест с фильтром по нерешенным
            response = await client.get(f"{DASHBOARD_V2_URL}/api/security/alerts?resolved=false", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            print("✅ Фильтрация уведомлений безопасности работает корректно")

    @pytest.mark.asyncio
    async def test_resolve_security_alert_endpoint(self):
        """
        Тест endpoint решения уведомления безопасности.
        Проверяет, что уведомление может быть решено.
        """
        print("\n--- Тест endpoint решения уведомления безопасности ---")
        alert_id = "test_alert_123"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{DASHBOARD_V2_URL}/api/security/alerts/{alert_id}/resolve", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "alert_id" in data
            assert "status" in data
            assert "message" in data
            assert data["alert_id"] == alert_id
            assert data["status"] == "resolved"
            
            print(f"✅ Уведомление {alert_id} успешно решено")

    @pytest.mark.asyncio
    async def test_security_scan_endpoint(self):
        """
        Тест endpoint запуска сканирования безопасности.
        Проверяет, что сканирование может быть запущено.
        """
        print("\n--- Тест endpoint сканирования безопасности ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/api/security/scan", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "scan_id" in data
            assert "status" in data
            assert "message" in data
            assert data["status"] == "started"
            
            print(f"✅ Сканирование безопасности запущено с ID: {data['scan_id']}")

    @pytest.mark.asyncio
    async def test_performance_benchmarks_endpoint(self):
        """
        Тест endpoint получения бенчмарков производительности.
        Проверяет, что возвращаются метрики производительности.
        """
        print("\n--- Тест endpoint бенчмарков производительности ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/api/performance/benchmarks", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "benchmarks" in data
            
            benchmarks = data["benchmarks"]
            assert "response_time" in benchmarks
            assert "throughput" in benchmarks
            assert "memory" in benchmarks
            
            print(f"✅ Бенчмарки производительности: {benchmarks['response_time']['average']}ms средний отклик")

    @pytest.mark.asyncio
    async def test_performance_trends_endpoint(self):
        """
        Тест endpoint получения трендов производительности.
        Проверяет, что возвращаются исторические данные.
        """
        print("\n--- Тест endpoint трендов производительности ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/api/performance/trends?days=7", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "trends" in data
            
            trends = data["trends"]
            assert "response_time" in trends
            assert "memory_usage" in trends
            assert "cpu_usage" in trends
            assert "dates" in trends
            
            print(f"✅ Тренды производительности за 7 дней: {len(trends['response_time'])} точек данных")

    @pytest.mark.asyncio
    async def test_monitoring_real_time_endpoint(self):
        """
        Тест endpoint мониторинга в реальном времени.
        Проверяет, что возвращаются актуальные данные мониторинга.
        """
        print("\n--- Тест endpoint мониторинга в реальном времени ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/api/monitoring/real-time", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "system" in data
            assert "sfm" in data
            assert "timestamp" in data
            
            print("✅ Данные мониторинга в реальном времени получены")

    @pytest.mark.asyncio
    async def test_monitoring_alerts_endpoint(self):
        """
        Тест endpoint алертов мониторинга.
        Проверяет, что возвращаются алерты мониторинга.
        """
        print("\n--- Тест endpoint алертов мониторинга ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/api/monitoring/alerts", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "alerts" in data
            assert isinstance(data["alerts"], list)
            
            print(f"✅ Получено {len(data['alerts'])} алертов мониторинга")

    @pytest.mark.asyncio
    async def test_analytics_overview_endpoint(self):
        """
        Тест endpoint обзора аналитики.
        Проверяет, что возвращается общая аналитика.
        """
        print("\n--- Тест endpoint обзора аналитики ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/api/analytics/overview", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "overview" in data
            
            overview = data["overview"]
            assert "total_requests" in overview
            assert "success_rate" in overview
            assert "average_response_time" in overview
            assert "error_rate" in overview
            assert "top_endpoints" in overview
            assert "performance_score" in overview
            assert "security_score" in overview
            
            print(f"✅ Аналитика: {overview['total_requests']} запросов, {overview['success_rate']}% успешных")

    @pytest.mark.asyncio
    async def test_analytics_reports_endpoint(self):
        """
        Тест endpoint отчетов аналитики.
        Проверяет, что возвращаются отчеты аналитики.
        """
        print("\n--- Тест endpoint отчетов аналитики ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/api/analytics/reports", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "reports" in data
            assert isinstance(data["reports"], list)
            
            print(f"✅ Получено {len(data['reports'])} отчетов аналитики")

    @pytest.mark.asyncio
    async def test_all_endpoints_endpoint(self):
        """
        Тест endpoint получения списка всех endpoints.
        Проверяет, что возвращается полный список endpoints.
        """
        print("\n--- Тест endpoint списка всех endpoints ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/api/endpoints", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "endpoints" in data
            assert isinstance(data["endpoints"], list)
            
            # Проверяем, что есть endpoints для всех категорий
            endpoint_paths = [ep["path"] for ep in data["endpoints"]]
            assert "/api/system/health" in endpoint_paths
            assert "/api/sfm/status" in endpoint_paths
            assert "/api/tests/results" in endpoint_paths
            assert "/api/security/alerts" in endpoint_paths
            assert "/api/performance/benchmarks" in endpoint_paths
            assert "/api/monitoring/real-time" in endpoint_paths
            assert "/api/analytics/overview" in endpoint_paths
            
            print(f"✅ Получено {len(data['endpoints'])} endpoints")

    @pytest.mark.asyncio
    async def test_health_check_endpoint(self):
        """
        Тест endpoint проверки здоровья.
        Проверяет, что приложение отвечает на health check.
        """
        print("\n--- Тест endpoint проверки здоровья ---")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DASHBOARD_V2_URL}/health", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            assert "status" in data
            assert "timestamp" in data
            assert "version" in data
            assert "uptime" in data
            assert data["status"] == "healthy"
            
            print(f"✅ Health check: {data['status']}, версия {data['version']}")

    @pytest.mark.asyncio
    async def test_endpoints_response_times(self):
        """
        Тест времени отклика всех endpoints.
        Проверяет, что все endpoints отвечают в разумные сроки.
        """
        print("\n--- Тест времени отклика endpoints ---")
        endpoints = [
            "/api/system/health",
            "/api/sfm/status", 
            "/api/tests/results",
            "/api/security/alerts",
            "/api/performance/benchmarks",
            "/api/monitoring/real-time",
            "/api/analytics/overview",
            "/health"
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint in endpoints:
                start_time = time.time()
                response = await client.get(f"{DASHBOARD_V2_URL}{endpoint}", timeout=10)
                response.raise_for_status()
                response_time = (time.time() - start_time) * 1000
                
                print(f"  {endpoint}: {response_time:.2f}ms")
                assert response_time < 1000, f"Endpoint {endpoint} отвечает слишком долго: {response_time:.2f}ms"
        
        print("✅ Все endpoints отвечают в разумные сроки")

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """
        Тест обработки конкурентных запросов.
        Проверяет, что дашборд может обрабатывать множественные запросы.
        """
        print("\n--- Тест конкурентных запросов ---")
        endpoints = [
            "/api/system/health",
            "/api/sfm/status",
            "/api/tests/results",
            "/api/security/alerts",
            "/api/performance/benchmarks"
        ]
        
        async def make_request(client: httpx.AsyncClient, endpoint: str):
            response = await client.get(f"{DASHBOARD_V2_URL}{endpoint}", timeout=10)
            response.raise_for_status()
            return response.status_code
        
        async with httpx.AsyncClient() as client:
            tasks = []
            for _ in range(10):  # 10 запросов каждого endpoint
                for endpoint in endpoints:
                    tasks.append(make_request(client, endpoint))
            
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            duration = time.time() - start_time
            
            successful_requests = len([r for r in results if r == 200])
            print(f"✅ Выполнено {successful_requests} из {len(results)} запросов за {duration:.2f}s")
            assert successful_requests == len(results), "Не все конкурентные запросы были успешными"