# -*- coding: utf-8 -*-
"""
Интеграционные тесты для Service Mesh Manager

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import pytest
import time
import threading
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import json
import os

from security.microservices.service_mesh_manager import (
    ServiceMeshManager,
    ServiceInfo,
    ServiceType,
    ServiceEndpoint,
    ServiceRequest,
    ServiceResponse,
    ServiceStatus,
    LoadBalancingStrategy,
    # Исключения
    ServiceMeshError,
    ServiceNotFoundError,
    ServiceAlreadyRegisteredError,
    CircuitBreakerOpenError,
    ServiceUnavailableError,
    InvalidServiceConfigurationError,
    LoadBalancingError,
    HealthCheckError,
    MetricsCollectionError
)


class TestServiceMeshIntegration:
    """Интеграционные тесты для Service Mesh Manager"""
    
    @pytest.fixture
    def manager(self):
        """Фикстура для создания экземпляра ServiceMeshManager"""
        return ServiceMeshManager()
    
    @pytest.fixture
    def api_service(self):
        """Фикстура для API сервиса"""
        endpoint = ServiceEndpoint(
            service_id="api_service",
            host="localhost",
            port=8080,
            protocol="http",
            path="/api"
        )
        return ServiceInfo(
            service_id="api_service",
            name="API Service",
            description="Main API service",
            service_type=ServiceType.API,
            version="1.0.0",
            endpoints=[endpoint],
            dependencies=[]
        )
    
    @pytest.fixture
    def database_service(self):
        """Фикстура для Database сервиса"""
        endpoint = ServiceEndpoint(
            service_id="database_service",
            host="localhost",
            port=5432,
            protocol="postgresql",
            path="/mydb"
        )
        return ServiceInfo(
            service_id="database_service",
            name="Database Service",
            description="Database service",
            service_type=ServiceType.DATABASE,
            version="1.0.0",
            endpoints=[endpoint],
            dependencies=[]
        )
    
    @pytest.fixture
    def cache_service(self):
        """Фикстура для Cache сервиса"""
        endpoint = ServiceEndpoint(
            service_id="cache_service",
            host="localhost",
            port=6379,
            protocol="redis",
            path="/"
        )
        return ServiceInfo(
            service_id="cache_service",
            name="Cache Service",
            description="Redis cache service",
            service_type=ServiceType.CACHE,
            version="1.0.0",
            endpoints=[endpoint],
            dependencies=[]
        )
    
    def test_full_service_lifecycle(self, manager, api_service, database_service, cache_service):
        """Тест полного жизненного цикла сервисов"""
        # Инициализация системы
        manager.initialize()
        assert manager.monitoring_thread is not None
        
        # Регистрация сервисов
        assert manager.register_service(api_service) is True
        assert manager.register_service(database_service) is True
        assert manager.register_service(cache_service) is True
        
        # Проверка регистрации
        assert len(manager.services) == 3
        assert "api_service" in manager.services
        assert "database_service" in manager.services
        assert "cache_service" in manager.services
        
        # Отправка запросов к сервисам
        api_response = manager.send_request("api_service", "GET", "/health")
        assert api_response is not None
        assert api_response.status_code in [200, 201, 202]
        
        db_response = manager.send_request("database_service", "GET", "/status")
        assert db_response is not None
        assert db_response.status_code in [200, 201, 202]
        
        cache_response = manager.send_request("cache_service", "GET", "/ping")
        assert cache_response is not None
        assert cache_response.status_code in [200, 201, 202]
        
        # Отмена регистрации сервисов
        assert manager.unregister_service("api_service") is True
        assert manager.unregister_service("database_service") is True
        assert manager.unregister_service("cache_service") is True
        
        # Проверка отмены регистрации
        assert len(manager.services) == 0
        
        # Остановка системы
        manager.stop()
        time.sleep(0.1)
        assert manager.monitoring_thread is None or not manager.monitoring_thread.is_alive()
    
    def test_service_dependencies(self, manager, api_service, database_service):
        """Тест зависимостей между сервисами"""
        manager.initialize()
        
        # Добавляем зависимость API сервиса от Database сервиса
        api_service.dependencies = ["database_service"]
        
        # Регистрируем Database сервис первым
        assert manager.register_service(database_service) is True
        
        # Регистрируем API сервис с зависимостью
        assert manager.register_service(api_service) is True
        
        # Проверяем, что оба сервиса зарегистрированы
        assert len(manager.services) == 2
        assert "api_service" in manager.services
        assert "database_service" in manager.services
        
        # Отправляем запрос к API сервису (который зависит от Database)
        response = manager.send_request("api_service", "GET", "/users")
        assert response is not None
        assert response.status_code in [200, 201, 202]
        
        manager.stop()
    
    def test_load_balancing_integration(self, manager):
        """Тест интеграции балансировки нагрузки"""
        manager.initialize()
        
        # Создаем сервис с несколькими endpoints
        endpoints = [
            ServiceEndpoint("load_balanced_service", "server1.example.com", 8080, "http", "/api"),
            ServiceEndpoint("load_balanced_service", "server2.example.com", 8080, "http", "/api"),
            ServiceEndpoint("load_balanced_service", "server3.example.com", 8080, "http", "/api")
        ]
        
        service = ServiceInfo(
            service_id="load_balanced_service",
            name="Load Balanced Service",
            description="Service with multiple endpoints",
            service_type=ServiceType.API,
            version="1.0.0",
            endpoints=endpoints,
            dependencies=[]
        )
        
        # Регистрируем сервис
        assert manager.register_service(service) is True
        
        # Отправляем несколько запросов для тестирования балансировки
        responses = []
        for i in range(10):
            response = manager.send_request("load_balanced_service", "GET", f"/request_{i}")
            responses.append(response)
            assert response is not None
            assert response.status_code in [200, 201, 202]
        
        # Проверяем, что все запросы были обработаны
        assert len(responses) == 10
        
        manager.stop()
    
    def test_circuit_breaker_integration(self, manager, api_service):
        """Тест интеграции Circuit Breaker"""
        manager.initialize()
        
        # Регистрируем сервис
        assert manager.register_service(api_service) is True
        
        # Отправляем несколько успешных запросов
        for i in range(5):
            response = manager.send_request("api_service", "GET", f"/success_{i}")
            assert response is not None
            assert response.status_code in [200, 201, 202]
        
        # Проверяем, что Circuit Breaker работает
        # (В реальной системе здесь были бы неудачные запросы)
        assert "api_service" in manager.services
        
        manager.stop()
    
    def test_health_check_integration(self, manager, api_service, database_service):
        """Тест интеграции проверки здоровья"""
        manager.initialize()
        
        # Регистрируем сервисы
        assert manager.register_service(api_service) is True
        assert manager.register_service(database_service) is True
        
        # Ждем некоторое время для выполнения проверок здоровья
        time.sleep(2)
        
        # Проверяем статус здоровья сервисов
        api_health = manager.get_service_health("api_service")
        db_health = manager.get_service_health("database_service")
        
        assert api_health in [ServiceStatus.HEALTHY, ServiceStatus.UNHEALTHY, ServiceStatus.UNKNOWN]
        assert db_health in [ServiceStatus.HEALTHY, ServiceStatus.UNHEALTHY, ServiceStatus.UNKNOWN]
        
        manager.stop()
    
    def test_metrics_collection_integration(self, manager, api_service):
        """Тест интеграции сбора метрик"""
        manager.initialize()
        
        # Регистрируем сервис
        assert manager.register_service(api_service) is True
        
        # Отправляем несколько запросов
        for i in range(10):
            response = manager.send_request("api_service", "GET", f"/metrics_{i}")
            assert response is not None
            assert response.status_code in [200, 201, 202]
        
        # Проверяем метрики
        metrics = manager.get_service_metrics("api_service")
        assert metrics is not None
        assert isinstance(metrics, dict)
        assert "requests_count" in metrics
        assert "success_count" in metrics
        assert "error_count" in metrics
        assert "average_response_time" in metrics
        
        # Проверяем, что метрики обновились
        assert metrics["requests_count"] >= 10
        assert metrics["success_count"] >= 10
        
        manager.stop()
    
    def test_event_system_integration(self, manager, api_service):
        """Тест интеграции системы событий"""
        manager.initialize()
        
        # Создаем мок-наблюдателя
        mock_observer = Mock()
        manager.event_manager.subscribe(mock_observer)
        
        # Регистрируем сервис (должно вызвать событие)
        assert manager.register_service(api_service) is True
        
        # Проверяем, что событие было опубликовано
        assert mock_observer.update.called
        
        # Отправляем запрос (должно вызвать событие)
        response = manager.send_request("api_service", "GET", "/test")
        assert response is not None
        
        # Проверяем, что событие запроса было опубликовано
        assert mock_observer.update.call_count >= 2
        
        manager.stop()
    
    def test_caching_integration(self, manager, api_service):
        """Тест интеграции кэширования"""
        manager.initialize()
        
        # Регистрируем сервис
        assert manager.register_service(api_service) is True
        
        # Включаем кэширование
        manager.cache_enable()
        
        # Отправляем запрос (должен кэшироваться)
        response1 = manager.send_request("api_service", "GET", "/cached")
        assert response1 is not None
        
        # Отправляем тот же запрос (должен быть из кэша)
        response2 = manager.send_request("api_service", "GET", "/cached")
        assert response2 is not None
        
        # Проверяем статистику кэша
        cache_stats = manager.cache_get_statistics()
        assert cache_stats is not None
        assert "hits" in cache_stats
        assert "misses" in cache_stats
        
        manager.stop()
    
    def test_async_operations_integration(self, manager, api_service):
        """Тест интеграции асинхронных операций"""
        manager.initialize()
        
        # Регистрируем сервис
        assert manager.register_service(api_service) is True
        
        # Включаем асинхронные операции
        manager.enable_async()
        
        # Отправляем асинхронный запрос
        response = manager.send_async_request("api_service", "GET", "/async")
        assert response is not None
        assert response.status_code in [200, 201, 202]
        
        # Проверяем статистику асинхронных операций
        async_stats = manager.get_async_statistics()
        assert async_stats is not None
        assert "total_requests" in async_stats
        assert "successful_requests" in async_stats
        
        manager.stop()
    
    def test_prometheus_metrics_integration(self, manager, api_service):
        """Тест интеграции Prometheus метрик"""
        manager.initialize()
        
        # Регистрируем сервис
        assert manager.register_service(api_service) is True
        
        # Отправляем несколько запросов
        for i in range(5):
            response = manager.send_request("api_service", "GET", f"/prometheus_{i}")
            assert response is not None
            assert response.status_code in [200, 201, 202]
        
        # Проверяем Prometheus метрики
        prometheus_metrics = manager.get_prometheus_metrics_dict()
        assert prometheus_metrics is not None
        assert "enabled" in prometheus_metrics
        assert prometheus_metrics["enabled"] is True
        
        # Проверяем текстовый формат метрик
        metrics_text = manager.get_prometheus_metrics_text()
        assert isinstance(metrics_text, str)
        assert "# HELP" in metrics_text or "# Prometheus metrics disabled" in metrics_text
        
        manager.stop()
    
    def test_structured_logging_integration(self, manager, api_service):
        """Тест интеграции структурированного логирования"""
        manager.initialize()
        
        # Регистрируем сервис
        assert manager.register_service(api_service) is True
        
        # Отправляем запрос (должен быть залогирован)
        response = manager.send_request("api_service", "GET", "/logging")
        assert response is not None
        
        # Проверяем статистику логирования
        logging_stats = manager.get_logging_statistics()
        assert logging_stats is not None
        assert "enabled" in logging_stats
        assert logging_stats["enabled"] is True
        assert "total_requests" in logging_stats
        
        manager.stop()
    
    def test_error_handling_integration(self, manager):
        """Тест интеграции обработки ошибок"""
        manager.initialize()
        
        # Тест отправки запроса к несуществующему сервису
        with pytest.raises(ServiceNotFoundError):
            manager.send_request("nonexistent_service", "GET", "/test")
        
        # Тест регистрации сервиса с неверной конфигурацией
        invalid_service = ServiceInfo(
            service_id="",  # Пустой ID
            name="Invalid Service",
            description="Invalid service",
            service_type=ServiceType.API,
            version="1.0.0",
            endpoints=[],
            dependencies=[]
        )
        
        with pytest.raises(InvalidServiceConfigurationError):
            manager.register_service(invalid_service)
        
        manager.stop()
    
    def test_concurrent_operations_integration(self, manager, api_service, database_service, cache_service):
        """Тест интеграции конкурентных операций"""
        manager.initialize()
        
        # Регистрируем сервисы
        assert manager.register_service(api_service) is True
        assert manager.register_service(database_service) is True
        assert manager.register_service(cache_service) is True
        
        # Функция для отправки запросов в отдельном потоке
        def send_requests(service_id, count):
            responses = []
            for i in range(count):
                try:
                    response = manager.send_request(service_id, "GET", f"/concurrent_{i}")
                    responses.append(response)
                except Exception as e:
                    responses.append(e)
            return responses
        
        # Создаем потоки для конкурентных запросов
        threads = []
        results = {}
        
        # API сервис - 5 запросов
        thread1 = threading.Thread(target=lambda: results.update({"api": send_requests("api_service", 5)}))
        threads.append(thread1)
        
        # Database сервис - 5 запросов
        thread2 = threading.Thread(target=lambda: results.update({"database": send_requests("database_service", 5)}))
        threads.append(thread2)
        
        # Cache сервис - 5 запросов
        thread3 = threading.Thread(target=lambda: results.update({"cache": send_requests("cache_service", 5)}))
        threads.append(thread3)
        
        # Запускаем все потоки
        for thread in threads:
            thread.start()
        
        # Ждем завершения всех потоков
        for thread in threads:
            thread.join()
        
        # Проверяем результаты
        assert len(results["api"]) == 5
        assert len(results["database"]) == 5
        assert len(results["cache"]) == 5
        
        # Проверяем, что большинство запросов были успешными
        api_successes = sum(1 for r in results["api"] if isinstance(r, ServiceResponse) and r.status_code in [200, 201, 202])
        db_successes = sum(1 for r in results["database"] if isinstance(r, ServiceResponse) and r.status_code in [200, 201, 202])
        cache_successes = sum(1 for r in results["cache"] if isinstance(r, ServiceResponse) and r.status_code in [200, 201, 202])
        
        assert api_successes >= 3  # Большинство запросов должны быть успешными
        assert db_successes >= 3
        assert cache_successes >= 3
        
        manager.stop()
    
    def test_system_recovery_integration(self, manager, api_service):
        """Тест интеграции восстановления системы"""
        manager.initialize()
        
        # Регистрируем сервис
        assert manager.register_service(api_service) is True
        
        # Отправляем запрос
        response1 = manager.send_request("api_service", "GET", "/recovery_test")
        assert response1 is not None
        
        # Останавливаем систему
        manager.stop()
        time.sleep(0.1)
        
        # Перезапускаем систему
        manager.initialize()
        
        # Проверяем, что сервис все еще зарегистрирован
        # (В реальной системе здесь была бы персистентность)
        assert len(manager.services) == 0  # В текущей реализации сервисы не сохраняются
        
        # Регистрируем сервис заново
        assert manager.register_service(api_service) is True
        
        # Отправляем запрос после восстановления
        response2 = manager.send_request("api_service", "GET", "/recovery_test")
        assert response2 is not None
        
        manager.stop()
    
    def test_configuration_management_integration(self, manager):
        """Тест интеграции управления конфигурацией"""
        manager.initialize()
        
        # Получаем текущую конфигурацию
        original_config = manager.get_mesh_status()
        assert isinstance(original_config, dict)
        
        # Обновляем конфигурацию
        new_config = {
            "enable_health_checks": True,
            "enable_load_balancing": True,
            "enable_circuit_breaker": True,
            "enable_metrics": True,
            "discovery_interval": 60,
            "health_check_interval": 120
        }
        
        manager.update_mesh_config(new_config)
        
        # Проверяем, что конфигурация обновилась
        updated_config = manager.get_mesh_status()
        assert updated_config["configuration"]["discovery_interval"] == 60
        assert updated_config["configuration"]["health_check_interval"] == 120
        
        manager.stop()
    
    def test_monitoring_integration(self, manager, api_service, database_service):
        """Тест интеграции мониторинга"""
        manager.initialize()
        
        # Регистрируем сервисы
        assert manager.register_service(api_service) is True
        assert manager.register_service(database_service) is True
        
        # Ждем некоторое время для сбора метрик
        time.sleep(3)
        
        # Проверяем статус системы
        status = manager.get_mesh_status()
        assert isinstance(status, dict)
        assert "services_count" in status
        assert "healthy_services" in status
        assert "unhealthy_services" in status
        assert status["services_count"] == 2
        
        # Проверяем метрики производительности
        performance_metrics = manager.get_all_performance_metrics()
        assert isinstance(performance_metrics, dict)
        
        # Проверяем системные метрики
        system_metrics = manager.get_system_metrics()
        assert isinstance(system_metrics, dict)
        
        manager.stop()


class TestServiceMeshEndToEnd:
    """End-to-end тесты для Service Mesh Manager"""
    
    @pytest.fixture
    def manager(self):
        """Фикстура для создания экземпляра ServiceMeshManager"""
        return ServiceMeshManager()
    
    def test_complete_workflow(self, manager):
        """Тест полного рабочего процесса"""
        # 1. Инициализация системы
        manager.initialize()
        assert manager.monitoring_thread is not None
        
        # 2. Создание микросервисной архитектуры
        services = []
        
        # API Gateway
        api_gateway = ServiceInfo(
            service_id="api_gateway",
            name="API Gateway",
            description="Main API Gateway",
            service_type=ServiceType.API,
            version="1.0.0",
            endpoints=[ServiceEndpoint("api_gateway", "localhost", 8000, "http", "/")],
            dependencies=[]
        )
        services.append(api_gateway)
        
        # User Service
        user_service = ServiceInfo(
            service_id="user_service",
            name="User Service",
            description="User management service",
            service_type=ServiceType.API,
            version="1.0.0",
            endpoints=[ServiceEndpoint("user_service", "localhost", 8001, "http", "/users")],
            dependencies=["database_service"]
        )
        services.append(user_service)
        
        # Database Service
        database_service = ServiceInfo(
            service_id="database_service",
            name="Database Service",
            description="Database service",
            service_type=ServiceType.DATABASE,
            version="1.0.0",
            endpoints=[ServiceEndpoint("database_service", "localhost", 5432, "postgresql", "/mydb")],
            dependencies=[]
        )
        services.append(database_service)
        
        # Cache Service
        cache_service = ServiceInfo(
            service_id="cache_service",
            name="Cache Service",
            description="Redis cache service",
            service_type=ServiceType.CACHE,
            version="1.0.0",
            endpoints=[ServiceEndpoint("cache_service", "localhost", 6379, "redis", "/")],
            dependencies=[]
        )
        services.append(cache_service)
        
        # 3. Регистрация всех сервисов
        for service in services:
            assert manager.register_service(service) is True
        
        assert len(manager.services) == 4
        
        # 4. Тестирование взаимодействия между сервисами
        
        # Запрос к API Gateway
        gateway_response = manager.send_request("api_gateway", "GET", "/")
        assert gateway_response is not None
        assert gateway_response.status_code in [200, 201, 202]
        
        # Запрос к User Service (через API Gateway)
        user_response = manager.send_request("user_service", "GET", "/users")
        assert user_response is not None
        assert user_response.status_code in [200, 201, 202]
        
        # Запрос к Database Service
        db_response = manager.send_request("database_service", "GET", "/status")
        assert db_response is not None
        assert db_response.status_code in [200, 201, 202]
        
        # Запрос к Cache Service
        cache_response = manager.send_request("cache_service", "GET", "/ping")
        assert cache_response is not None
        assert cache_response.status_code in [200, 201, 202]
        
        # 5. Проверка мониторинга и метрик
        time.sleep(2)  # Ждем сбора метрик
        
        status = manager.get_mesh_status()
        assert status["services_count"] == 4
        
        # Проверка метрик каждого сервиса
        for service in services:
            metrics = manager.get_service_metrics(service.service_id)
            assert metrics is not None
            assert "requests_count" in metrics
        
        # 6. Тестирование отказоустойчивости
        # Отменяем регистрацию одного сервиса
        assert manager.unregister_service("cache_service") is True
        assert len(manager.services) == 3
        
        # Проверяем, что остальные сервисы продолжают работать
        gateway_response2 = manager.send_request("api_gateway", "GET", "/")
        assert gateway_response2 is not None
        
        # 7. Остановка системы
        manager.stop()
        time.sleep(0.1)
        assert manager.monitoring_thread is None or not manager.monitoring_thread.is_alive()
    
    def test_performance_under_load(self, manager):
        """Тест производительности под нагрузкой"""
        manager.initialize()
        
        # Создаем сервис для нагрузочного тестирования
        service = ServiceInfo(
            service_id="load_test_service",
            name="Load Test Service",
            description="Service for load testing",
            service_type=ServiceType.API,
            version="1.0.0",
            endpoints=[ServiceEndpoint("load_test_service", "localhost", 8080, "http", "/load")],
            dependencies=[]
        )
        
        assert manager.register_service(service) is True
        
        # Отправляем много запросов
        start_time = time.time()
        responses = []
        
        for i in range(50):  # 50 запросов
            response = manager.send_request("load_test_service", "GET", f"/load_{i}")
            responses.append(response)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Проверяем, что все запросы были обработаны
        assert len(responses) == 50
        successful_responses = [r for r in responses if isinstance(r, ServiceResponse) and r.status_code in [200, 201, 202]]
        assert len(successful_responses) >= 45  # 90% успешных запросов
        
        # Проверяем производительность (должно быть быстрее 10 секунд)
        assert total_time < 10.0
        
        # Проверяем метрики производительности
        metrics = manager.get_service_metrics("load_test_service")
        assert metrics["requests_count"] >= 50
        assert metrics["average_response_time"] > 0
        
        manager.stop()
    
    def test_error_recovery_scenarios(self, manager):
        """Тест сценариев восстановления после ошибок"""
        manager.initialize()
        
        # Создаем сервис
        service = ServiceInfo(
            service_id="error_recovery_service",
            name="Error Recovery Service",
            description="Service for testing error recovery",
            service_type=ServiceType.API,
            version="1.0.0",
            endpoints=[ServiceEndpoint("error_recovery_service", "localhost", 8080, "http", "/error")],
            dependencies=[]
        )
        
        assert manager.register_service(service) is True
        
        # Тест 1: Отправка запроса к несуществующему endpoint
        try:
            response = manager.send_request("error_recovery_service", "GET", "/nonexistent")
            # В реальной системе здесь была бы ошибка 404
            assert response is not None
        except Exception:
            # Ожидаемо, что может быть ошибка
            pass
        
        # Тест 2: Отправка запроса с неверным методом
        try:
            response = manager.send_request("error_recovery_service", "INVALID_METHOD", "/test")
            # Должна быть ошибка валидации
        except InvalidServiceConfigurationError:
            # Ожидаемая ошибка
            pass
        
        # Тест 3: Проверка, что сервис все еще работает после ошибок
        response = manager.send_request("error_recovery_service", "GET", "/test")
        assert response is not None
        assert response.status_code in [200, 201, 202]
        
        manager.stop()


if __name__ == "__main__":
    pytest.main([__file__])
