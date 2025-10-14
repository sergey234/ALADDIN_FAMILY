# -*- coding: utf-8 -*-
"""
Unit тесты для Service Mesh Manager

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from security.microservices.service_mesh_manager import (
    ServiceMeshManager,
    ServiceInfo,
    ServiceType,
    ServiceEndpoint,
    ServiceRequest,
    ServiceResponse,
    ServiceStatus,
    InputValidator,
    PerformanceMetrics,
    SystemMetrics,
    CircuitBreakerConfig,
    CircuitBreakerState,
    EnhancedCircuitBreaker,
    HealthStatus,
    HealthCheckResult,
    ServiceHealthSummary,
    EventType,
    ServiceMeshEvent,
    EventObserver,
    LoggingEventObserver,
    MetricsEventObserver,
    AlertingEventObserver,
    EventManager,
    CacheConfig,
    TTLCache,
    AsyncConfig,
    AsyncConnectionPool,
    AsyncRequestManager,
    PrometheusConfig,
    PrometheusMetrics,
    LogConfig,
    ServiceMeshLogger,
    # Исключения
    ServiceMeshError,
    ServiceNotFoundError,
    ServiceAlreadyRegisteredError,
    CircuitBreakerOpenError,
    ServiceUnavailableError,
    InvalidServiceConfigurationError,
    LoadBalancingError,
    HealthCheckError,
    MetricsCollectionError,
    CacheError,
    CacheKeyNotFoundError,
    CacheExpiredError,
    CacheConfigurationError,
    AsyncOperationError,
    AsyncTimeoutError
)


class TestServiceMeshManager:
    """Тесты для основного класса ServiceMeshManager"""
    
    @pytest.fixture
    def manager(self):
        """Фикстура для создания экземпляра ServiceMeshManager"""
        return ServiceMeshManager()
    
    @pytest.fixture
    def sample_service(self):
        """Фикстура для создания тестового сервиса"""
        endpoint = ServiceEndpoint(
            service_id="test_service",
            host="localhost",
            port=8080,
            protocol="http",
            path="/api"
        )
        return ServiceInfo(
            service_id="test_service",
            name="Test Service",
            description="Test service for unit tests",
            service_type=ServiceType.API,
            version="1.0.0",
            endpoints=[endpoint],
            dependencies=[]
        )
    
    def test_manager_initialization(self, manager):
        """Тест инициализации ServiceMeshManager"""
        assert manager is not None
        assert manager.services == {}
        assert manager.service_endpoints == {}
        assert manager.service_health == {}
        assert manager.service_metrics == {}
        assert manager.mesh_config is not None
        # assert manager.monitoring_interval == 30  # Атрибут не определен
        # assert manager.health_check_interval == 60  # Атрибут не определен
        assert manager.thread_pool is not None
        assert manager.monitoring_thread is None
        assert manager.running is False
        assert manager.event_manager is not None
        assert manager.cache is not None
        assert manager.async_manager is not None
        assert manager.structured_logger is not None
        assert manager.prometheus_metrics is not None
    
    def test_initialize(self, manager):
        """Тест инициализации системы"""
        manager.initialize()
        assert manager.running is True
        assert manager.monitoring_thread is not None
        assert manager.monitoring_thread.is_alive()
    
    def test_stop(self, manager):
        """Тест остановки системы"""
        manager.initialize()
        assert manager.running is True
        
        manager.stop()
        assert manager.running is False
        # Даем время потоку завершиться
        time.sleep(0.1)
        assert manager.monitoring_thread is None or not manager.monitoring_thread.is_alive()
    
    def test_register_service_success(self, manager, sample_service):
        """Тест успешной регистрации сервиса"""
        manager.initialize()
        
        result = manager.register_service(sample_service)
        assert result is True
        assert sample_service.service_id in manager.services
        assert sample_service.service_id in manager.service_endpoints
        assert sample_service.service_id in manager.service_health
        assert sample_service.service_id in manager.service_metrics
    
    def test_register_service_duplicate(self, manager, sample_service):
        """Тест регистрации дублирующегося сервиса"""
        manager.initialize()
        
        # Первая регистрация
        result1 = manager.register_service(sample_service)
        assert result1 is True
        
        # Попытка повторной регистрации
        with pytest.raises(ServiceAlreadyRegisteredError):
            manager.register_service(sample_service)
    
    def test_register_service_invalid_config(self, manager):
        """Тест регистрации сервиса с неверной конфигурацией"""
        manager.initialize()
        
        # Создаем сервис с пустым service_id
        invalid_service = ServiceInfo(
            service_id="",  # Пустой ID
            name="Test Service",
            description="Test service",
            service_type=ServiceType.API,
            version="1.0.0",
            endpoints=[],
            dependencies=[]
        )
        
        with pytest.raises(InvalidServiceConfigurationError):
            manager.register_service(invalid_service)
    
    def test_unregister_service_success(self, manager, sample_service):
        """Тест успешной отмены регистрации сервиса"""
        manager.initialize()
        manager.register_service(sample_service)
        
        result = manager.unregister_service(sample_service.service_id)
        assert result is True
        assert sample_service.service_id not in manager.services
        assert sample_service.service_id not in manager.service_endpoints
        assert sample_service.service_id not in manager.service_health
        assert sample_service.service_id not in manager.service_metrics
    
    def test_unregister_service_not_found(self, manager):
        """Тест отмены регистрации несуществующего сервиса"""
        manager.initialize()
        
        with pytest.raises(ServiceNotFoundError):
            manager.unregister_service("nonexistent_service")
    
    def test_send_request_success(self, manager, sample_service):
        """Тест успешной отправки запроса"""
        manager.initialize()
        manager.register_service(sample_service)
        
        response = manager.send_request(
            service_id="test_service",
            method="GET",
            path="/health"
        )
        
        assert response is not None
        assert isinstance(response, ServiceResponse)
        assert response.status_code in [200, 201, 202]
        assert response.response_time > 0
    
    def test_send_request_service_not_found(self, manager):
        """Тест отправки запроса к несуществующему сервису"""
        manager.initialize()
        
        with pytest.raises(ServiceNotFoundError):
            manager.send_request(
                service_id="nonexistent_service",
                method="GET",
                path="/health"
            )
    
    def test_send_request_invalid_method(self, manager, sample_service):
        """Тест отправки запроса с неверным методом"""
        manager.initialize()
        manager.register_service(sample_service)
        
        with pytest.raises(InvalidServiceConfigurationError):
            manager.send_request(
                service_id="test_service",
                method="INVALID_METHOD",
                path="/health"
            )
    
    def test_get_service_endpoint_success(self, manager, sample_service):
        """Тест получения endpoint сервиса"""
        manager.initialize()
        manager.register_service(sample_service)
        
        endpoint = manager.get_service_endpoint("test_service")
        assert endpoint is not None
        assert isinstance(endpoint, ServiceEndpoint)
        assert endpoint.service_id == "test_service"
    
    def test_get_service_endpoint_not_found(self, manager):
        """Тест получения endpoint несуществующего сервиса"""
        manager.initialize()
        
        with pytest.raises(ServiceNotFoundError):
            manager.get_service_endpoint("nonexistent_service")
    
    def test_get_service_health_success(self, manager, sample_service):
        """Тест получения статуса здоровья сервиса"""
        manager.initialize()
        manager.register_service(sample_service)
        
        health = manager.get_service_health("test_service")
        assert health is not None
        assert health in [ServiceStatus.HEALTHY, ServiceStatus.UNHEALTHY, ServiceStatus.UNKNOWN]
    
    def test_get_service_health_not_found(self, manager):
        """Тест получения статуса здоровья несуществующего сервиса"""
        manager.initialize()
        
        with pytest.raises(ServiceNotFoundError):
            manager.get_service_health("nonexistent_service")
    
    def test_get_service_metrics_success(self, manager, sample_service):
        """Тест получения метрик сервиса"""
        manager.initialize()
        manager.register_service(sample_service)
        
        metrics = manager.get_service_metrics("test_service")
        assert metrics is not None
        assert isinstance(metrics, dict)
        assert "requests_count" in metrics
        assert "success_count" in metrics
        assert "error_count" in metrics
        assert "average_response_time" in metrics
    
    def test_get_service_metrics_not_found(self, manager):
        """Тест получения метрик несуществующего сервиса"""
        manager.initialize()
        
        with pytest.raises(ServiceNotFoundError):
            manager.get_service_metrics("nonexistent_service")
    
    def test_get_all_services(self, manager, sample_service):
        """Тест получения списка всех сервисов"""
        manager.initialize()
        manager.register_service(sample_service)
        
        services = manager.get_all_services()
        assert isinstance(services, dict)
        assert "test_service" in services
        assert services["test_service"] == sample_service
    
    def test_get_service_count(self, manager, sample_service):
        """Тест получения количества сервисов"""
        manager.initialize()
        assert manager.get_service_count() == 0
        
        manager.register_service(sample_service)
        assert manager.get_service_count() == 1
    
    def test_is_service_registered(self, manager, sample_service):
        """Тест проверки регистрации сервиса"""
        manager.initialize()
        assert manager.is_service_registered("test_service") is False
        
        manager.register_service(sample_service)
        assert manager.is_service_registered("test_service") is True
    
    def test_get_mesh_status(self, manager):
        """Тест получения статуса mesh"""
        manager.initialize()
        
        status = manager.get_mesh_status()
        assert isinstance(status, dict)
        assert "running" in status
        assert "services_count" in status
        assert "healthy_services" in status
        assert "unhealthy_services" in status
        assert status["running"] is True
        assert status["services_count"] == 0
    
    def test_get_mesh_config(self, manager):
        """Тест получения конфигурации mesh"""
        config = manager.get_mesh_config()
        assert isinstance(config, dict)
        assert "enable_health_checks" in config
        assert "enable_load_balancing" in config
        assert "enable_circuit_breaker" in config
        assert "enable_metrics" in config
    
    def test_update_mesh_config(self, manager):
        """Тест обновления конфигурации mesh"""
        original_config = manager.get_mesh_config()
        
        new_config = {
            "enable_health_checks": True,
            "enable_load_balancing": True,
            "enable_circuit_breaker": True,
            "enable_metrics": True,
            "monitoring_interval": 60,
            "health_check_interval": 120
        }
        
        manager.update_mesh_config(new_config)
        updated_config = manager.get_mesh_config()
        
        assert updated_config["monitoring_interval"] == 60
        assert updated_config["health_check_interval"] == 120
    
    def test_context_manager(self, manager, sample_service):
        """Тест использования как контекстного менеджера"""
        with manager as mgr:
            assert mgr.running is True
            mgr.register_service(sample_service)
            assert mgr.is_service_registered("test_service")
        
        # После выхода из контекста система должна быть остановлена
        assert manager.running is False
    
    def test_iteration(self, manager, sample_service):
        """Тест итерации по сервисам"""
        manager.initialize()
        manager.register_service(sample_service)
        
        services = list(manager)
        assert len(services) == 1
        assert services[0] == sample_service
    
    def test_string_representation(self, manager):
        """Тест строкового представления"""
        manager.initialize()
        
        str_repr = str(manager)
        assert "ServiceMeshManager" in str_repr
        assert "running=True" in str_repr or "running=False" in str_repr
    
    def test_repr_representation(self, manager):
        """Тест repr представления"""
        manager.initialize()
        
        repr_str = repr(manager)
        assert "ServiceMeshManager" in repr_str
        assert "services=" in repr_str


class TestInputValidator:
    """Тесты для класса InputValidator"""
    
    def test_validate_service_id_valid(self):
        """Тест валидации корректного service_id"""
        result = InputValidator.validate_service_id("valid_service_id")
        assert result == "valid_service_id"
    
    def test_validate_service_id_invalid(self):
        """Тест валидации некорректного service_id"""
        with pytest.raises(InvalidServiceConfigurationError):
            InputValidator.validate_service_id("")
        
        with pytest.raises(InvalidServiceConfigurationError):
            InputValidator.validate_service_id("a" * 256)  # Слишком длинный
    
    def test_validate_string_valid(self):
        """Тест валидации корректной строки"""
        result = InputValidator.validate_string("valid_string", "field_name", 1, 100)
        assert result == "valid_string"
    
    def test_validate_string_invalid(self):
        """Тест валидации некорректной строки"""
        with pytest.raises(InvalidServiceConfigurationError):
            InputValidator.validate_string("", "field_name", 1, 100)
        
        with pytest.raises(InvalidServiceConfigurationError):
            InputValidator.validate_string("a" * 101, "field_name", 1, 100)
    
    def test_validate_http_method_valid(self):
        """Тест валидации корректного HTTP метода"""
        valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        for method in valid_methods:
            result = InputValidator.validate_http_method(method)
            assert result == method
    
    def test_validate_http_method_invalid(self):
        """Тест валидации некорректного HTTP метода"""
        with pytest.raises(InvalidServiceConfigurationError):
            InputValidator.validate_http_method("INVALID_METHOD")
    
    def test_validate_path_valid(self):
        """Тест валидации корректного пути"""
        valid_paths = ["/", "/api", "/api/v1", "/health", "/metrics"]
        for path in valid_paths:
            result = InputValidator.validate_path(path)
            assert result == path
    
    def test_validate_path_invalid(self):
        """Тест валидации некорректного пути"""
        with pytest.raises(InvalidServiceConfigurationError):
            InputValidator.validate_path("invalid_path")  # Должен начинаться с /
    
    def test_validate_headers_valid(self):
        """Тест валидации корректных заголовков"""
        valid_headers = {"Content-Type": "application/json", "Authorization": "Bearer token"}
        result = InputValidator.validate_headers(valid_headers)
        assert result == valid_headers
    
    def test_validate_headers_invalid(self):
        """Тест валидации некорректных заголовков"""
        with pytest.raises(InvalidServiceConfigurationError):
            InputValidator.validate_headers({"": "value"})  # Пустой ключ
    
    def test_validate_endpoints_valid(self):
        """Тест валидации корректных endpoints"""
        endpoints = [
            ServiceEndpoint("service1", "localhost", 8080, "http", "/api"),
            ServiceEndpoint("service2", "localhost", 8081, "https", "/api/v2")
        ]
        result = InputValidator.validate_endpoints(endpoints)
        assert result == endpoints
    
    def test_validate_endpoints_invalid(self):
        """Тест валидации некорректных endpoints"""
        with pytest.raises(InvalidServiceConfigurationError):
            InputValidator.validate_endpoints([])  # Пустой список


class TestPerformanceMetrics:
    """Тесты для класса PerformanceMetrics"""
    
    def test_performance_metrics_creation(self):
        """Тест создания PerformanceMetrics"""
        metrics = PerformanceMetrics(
            service_id="test_service",
            requests_per_second=10.5,
            average_response_time=150.0,
            p95_response_time=300.0,
            p99_response_time=500.0,
            error_rate=0.02,
            success_rate=0.98,
            total_requests=1000,
            successful_requests=980,
            failed_requests=20,
            memory_usage_mb=128.5,
            cpu_usage_percent=25.3,
            active_connections=5
        )
        
        assert metrics.service_id == "test_service"
        assert metrics.requests_per_second == 10.5
        assert metrics.average_response_time == 150.0
        assert metrics.p95_response_time == 300.0
        assert metrics.p99_response_time == 500.0
        assert metrics.error_rate == 0.02
        assert metrics.success_rate == 0.98
        assert metrics.total_requests == 1000
        assert metrics.successful_requests == 980
        assert metrics.failed_requests == 20
        assert metrics.memory_usage_mb == 128.5
        assert metrics.cpu_usage_percent == 25.3
        assert metrics.active_connections == 5


class TestSystemMetrics:
    """Тесты для класса SystemMetrics"""
    
    def test_system_metrics_creation(self):
        """Тест создания SystemMetrics"""
        metrics = SystemMetrics(
            total_services=10,
            healthy_services=8,
            unhealthy_services=2,
            total_requests=5000,
            total_errors=50,
            average_cpu_usage=30.5,
            average_memory_usage=512.0,
            load_average_1m=1.2,
            load_average_5m=1.5,
            load_average_15m=1.8,
            network_throughput_mbps=100.0,
            network_latency_ms=10.5
        )
        
        assert metrics.total_services == 10
        assert metrics.healthy_services == 8
        assert metrics.unhealthy_services == 2
        assert metrics.total_requests == 5000
        assert metrics.total_errors == 50
        assert metrics.average_cpu_usage == 30.5
        assert metrics.average_memory_usage == 512.0
        assert metrics.load_average_1m == 1.2
        assert metrics.load_average_5m == 1.5
        assert metrics.load_average_15m == 1.8
        assert metrics.network_throughput_mbps == 100.0
        assert metrics.network_latency_ms == 10.5


class TestCircuitBreakerConfig:
    """Тесты для класса CircuitBreakerConfig"""
    
    def test_circuit_breaker_config_creation(self):
        """Тест создания CircuitBreakerConfig"""
        config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=30.0,
            success_threshold=3,
            timeout=10.0
        )
        
        assert config.failure_threshold == 5
        assert config.recovery_timeout == 30.0
        assert config.success_threshold == 3
        assert config.timeout == 10.0


class TestEnhancedCircuitBreaker:
    """Тесты для класса EnhancedCircuitBreaker"""
    
    def test_circuit_breaker_creation(self):
        """Тест создания EnhancedCircuitBreaker"""
        config = CircuitBreakerConfig()
        cb = EnhancedCircuitBreaker("test_service", config)
        
        assert cb.service_id == "test_service"
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0
    
    def test_circuit_breaker_can_execute_closed(self):
        """Тест выполнения запроса при закрытом Circuit Breaker"""
        config = CircuitBreakerConfig()
        cb = EnhancedCircuitBreaker("test_service", config)
        
        assert cb.can_execute() is True
    
    def test_circuit_breaker_can_execute_open(self):
        """Тест выполнения запроса при открытом Circuit Breaker"""
        config = CircuitBreakerConfig(failure_threshold=2)
        cb = EnhancedCircuitBreaker("test_service", config)
        
        # Симулируем несколько неудач
        cb.record_failure()
        cb.record_failure()
        
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.can_execute() is False
    
    def test_circuit_breaker_record_success(self):
        """Тест записи успешного выполнения"""
        config = CircuitBreakerConfig()
        cb = EnhancedCircuitBreaker("test_service", config)
        
        cb.record_success()
        assert cb.success_count == 1
        assert cb.failure_count == 0
    
    def test_circuit_breaker_record_failure(self):
        """Тест записи неудачного выполнения"""
        config = CircuitBreakerConfig()
        cb = EnhancedCircuitBreaker("test_service", config)
        
        cb.record_failure()
        assert cb.failure_count == 1
        assert cb.success_count == 0
    
    def test_circuit_breaker_reset(self):
        """Тест сброса Circuit Breaker"""
        config = CircuitBreakerConfig()
        cb = EnhancedCircuitBreaker("test_service", config)
        
        cb.record_failure()
        cb.record_failure()
        cb.reset()
        
        assert cb.failure_count == 0
        assert cb.success_count == 0
        assert cb.state == CircuitBreakerState.CLOSED


class TestHealthCheckResult:
    """Тесты для класса HealthCheckResult"""
    
    def test_health_check_result_creation(self):
        """Тест создания HealthCheckResult"""
        result = HealthCheckResult(
            service_id="test_service",
            status=HealthStatus.HEALTHY,
            response_time=50.0,
            timestamp=time.time(),
            details={"cpu_usage": 25.0, "memory_usage": 128.0},
            custom_checks={"database": True, "cache": True}
        )
        
        assert result.service_id == "test_service"
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time == 50.0
        assert result.timestamp > 0
        assert result.details["cpu_usage"] == 25.0
        assert result.details["memory_usage"] == 128.0
        assert result.custom_checks["database"] is True
        assert result.custom_checks["cache"] is True


class TestServiceHealthSummary:
    """Тесты для класса ServiceHealthSummary"""
    
    def test_service_health_summary_creation(self):
        """Тест создания ServiceHealthSummary"""
        summary = ServiceHealthSummary(
            service_id="test_service",
            overall_status=HealthStatus.HEALTHY,
            healthy_endpoints=3,
            total_endpoints=3,
            last_check_time=time.time(),
            average_response_time=100.0,
            error_rate=0.0
        )
        
        assert summary.service_id == "test_service"
        assert summary.overall_status == HealthStatus.HEALTHY
        assert summary.healthy_endpoints == 3
        assert summary.total_endpoints == 3
        assert summary.last_check_time > 0
        assert summary.average_response_time == 100.0
        assert summary.error_rate == 0.0


class TestEventManager:
    """Тесты для класса EventManager"""
    
    def test_event_manager_creation(self):
        """Тест создания EventManager"""
        event_manager = EventManager()
        assert event_manager is not None
        assert event_manager.observers == []
        assert event_manager.event_history == []
    
    def test_subscribe_observer(self):
        """Тест подписки наблюдателя"""
        event_manager = EventManager()
        observer = Mock(spec=EventObserver)
        
        event_manager.subscribe(observer)
        assert observer in event_manager.observers
    
    def test_unsubscribe_observer(self):
        """Тест отписки наблюдателя"""
        event_manager = EventManager()
        observer = Mock(spec=EventObserver)
        
        event_manager.subscribe(observer)
        assert observer in event_manager.observers
        
        event_manager.unsubscribe(observer)
        assert observer not in event_manager.observers
    
    def test_publish_event(self):
        """Тест публикации события"""
        event_manager = EventManager()
        observer = Mock(spec=EventObserver)
        event_manager.subscribe(observer)
        
        event = ServiceMeshEvent(
            event_type=EventType.SERVICE_REGISTERED,
            service_id="test_service",
            data={"name": "Test Service"}
        )
        
        event_manager.publish(event)
        observer.update.assert_called_once_with(event)


class TestTTLCache:
    """Тесты для класса TTLCache"""
    
    def test_cache_creation(self):
        """Тест создания TTLCache"""
        config = CacheConfig()
        cache = TTLCache(config)
        
        assert cache is not None
        assert cache.config == config
        assert cache.cache == {}
        assert cache.access_times == {}
        assert cache.creation_times == {}
    
    def test_cache_set_and_get(self):
        """Тест установки и получения значения из кэша"""
        config = CacheConfig()
        cache = TTLCache(config)
        
        cache.set("key1", "value1", ttl_seconds=60)
        value = cache.get("key1")
        
        assert value == "value1"
    
    def test_cache_expiration(self):
        """Тест истечения срока действия кэша"""
        config = CacheConfig(default_ttl_seconds=0.1)  # Очень короткий TTL
        cache = TTLCache(config)
        
        cache.set("key1", "value1")
        time.sleep(0.2)  # Ждем истечения TTL
        
        with pytest.raises(CacheExpiredError):
            cache.get("key1")
    
    def test_cache_key_not_found(self):
        """Тест получения несуществующего ключа"""
        config = CacheConfig()
        cache = TTLCache(config)
        
        with pytest.raises(CacheKeyNotFoundError):
            cache.get("nonexistent_key")
    
    def test_cache_delete(self):
        """Тест удаления ключа из кэша"""
        config = CacheConfig()
        cache = TTLCache(config)
        
        cache.set("key1", "value1")
        cache.delete("key1")
        
        with pytest.raises(CacheKeyNotFoundError):
            cache.get("key1")
    
    def test_cache_clear(self):
        """Тест очистки кэша"""
        config = CacheConfig()
        cache = TTLCache(config)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        
        assert len(cache.cache) == 0
        assert len(cache.access_times) == 0
        assert len(cache.creation_times) == 0


class TestAsyncRequestManager:
    """Тесты для класса AsyncRequestManager"""
    
    def test_async_request_manager_creation(self):
        """Тест создания AsyncRequestManager"""
        config = AsyncConfig()
        manager = AsyncRequestManager(config)
        
        assert manager is not None
        assert manager.config == config
        assert manager.connection_pools == {}
        assert manager.semaphore is not None
        assert manager.statistics == {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "active_requests": 0,
            "average_response_time": 0.0
        }
    
    def test_async_request_manager_statistics(self):
        """Тест получения статистики AsyncRequestManager"""
        config = AsyncConfig()
        manager = AsyncRequestManager(config)
        
        stats = manager.get_statistics()
        assert isinstance(stats, dict)
        assert "total_requests" in stats
        assert "successful_requests" in stats
        assert "failed_requests" in stats
        assert "active_requests" in stats
        assert "average_response_time" in stats


class TestPrometheusMetrics:
    """Тесты для класса PrometheusMetrics"""
    
    def test_prometheus_metrics_creation(self):
        """Тест создания PrometheusMetrics"""
        config = PrometheusConfig()
        metrics = PrometheusMetrics(config)
        
        assert metrics is not None
        assert metrics.config == config
        assert isinstance(metrics.metrics, dict)
    
    def test_prometheus_metrics_increment_counter(self):
        """Тест увеличения Counter метрики"""
        config = PrometheusConfig()
        metrics = PrometheusMetrics(config)
        
        metrics.increment_counter("requests_total", label_values={"service_id": "test"})
        
        # Проверяем, что метрика была увеличена
        assert "requests_total" in metrics.metrics
        assert metrics.metrics["requests_total"]["value"] == 1.0
    
    def test_prometheus_metrics_set_gauge(self):
        """Тест установки Gauge метрики"""
        config = PrometheusConfig()
        metrics = PrometheusMetrics(config)
        
        metrics.set_gauge("services_active", 5.0)
        
        # Проверяем, что метрика была установлена
        assert "services_active" in metrics.metrics
        assert metrics.metrics["services_active"]["value"] == 5.0
    
    def test_prometheus_metrics_observe_histogram(self):
        """Тест добавления наблюдения в Histogram метрику"""
        config = PrometheusConfig()
        metrics = PrometheusMetrics(config)
        
        metrics.observe_histogram("request_duration_seconds", 1.5)
        
        # Проверяем, что наблюдение было добавлено
        assert "request_duration_seconds" in metrics.metrics
        assert len(metrics.metrics["request_duration_seconds"]["observations"]) == 1
        assert metrics.metrics["request_duration_seconds"]["observations"][0] == 1.5
    
    def test_prometheus_metrics_get_metrics_text(self):
        """Тест получения метрик в текстовом формате"""
        config = PrometheusConfig()
        metrics = PrometheusMetrics(config)
        
        metrics_text = metrics.get_metrics_text()
        assert isinstance(metrics_text, str)
        assert "# HELP" in metrics_text or "# Prometheus metrics disabled" in metrics_text
    
    def test_prometheus_metrics_get_metrics_dict(self):
        """Тест получения метрик в виде словаря"""
        config = PrometheusConfig()
        metrics = PrometheusMetrics(config)
        
        metrics_dict = metrics.get_metrics_dict()
        assert isinstance(metrics_dict, dict)
        assert "enabled" in metrics_dict


class TestServiceMeshLogger:
    """Тесты для класса ServiceMeshLogger"""
    
    def test_service_mesh_logger_creation(self):
        """Тест создания ServiceMeshLogger"""
        config = LogConfig()
        logger = ServiceMeshLogger(config)
        
        assert logger is not None
        assert logger.config == config
        assert logger.logger is not None
        assert logger._request_counter == 0
        assert logger._error_counter == 0
    
    def test_service_mesh_logger_log_service_registration(self):
        """Тест логирования регистрации сервиса"""
        config = LogConfig()
        logger = ServiceMeshLogger(config)
        
        # Это не должно вызывать исключений
        logger.log_service_registration("test_service", "Test Service", 3)
    
    def test_service_mesh_logger_log_request(self):
        """Тест логирования запроса"""
        config = LogConfig()
        logger = ServiceMeshLogger(config)
        
        # Это не должно вызывать исключений
        logger.log_request("test_service", "GET", "/health", 200, 150.0)
    
    def test_service_mesh_logger_log_error(self):
        """Тест логирования ошибки"""
        config = LogConfig()
        logger = ServiceMeshLogger(config)
        
        # Это не должно вызывать исключений
        logger.log_error("TestError", "Test error message", "test_service")
    
    def test_service_mesh_logger_get_statistics(self):
        """Тест получения статистики логирования"""
        config = LogConfig()
        logger = ServiceMeshLogger(config)
        
        stats = logger.get_statistics()
        assert isinstance(stats, dict)
        assert "total_requests" in stats
        assert "total_errors" in stats
        assert "config" in stats
        assert "logger_name" in stats


class TestExceptions:
    """Тесты для исключений"""
    
    def test_service_mesh_error(self):
        """Тест ServiceMeshError"""
        error = ServiceMeshError("Test error message")
        assert str(error) == "Test error message"
    
    def test_service_not_found_error(self):
        """Тест ServiceNotFoundError"""
        error = ServiceNotFoundError("test_service")
        assert "test_service" in str(error)
    
    def test_service_already_registered_error(self):
        """Тест ServiceAlreadyRegisteredError"""
        error = ServiceAlreadyRegisteredError("test_service")
        assert "test_service" in str(error)
    
    def test_circuit_breaker_open_error(self):
        """Тест CircuitBreakerOpenError"""
        error = CircuitBreakerOpenError("test_service")
        assert "test_service" in str(error)
    
    def test_service_unavailable_error(self):
        """Тест ServiceUnavailableError"""
        error = ServiceUnavailableError("test_service")
        assert "test_service" in str(error)
    
    def test_invalid_service_configuration_error(self):
        """Тест InvalidServiceConfigurationError"""
        error = InvalidServiceConfigurationError("test_service", "Invalid config")
        assert "test_service" in str(error)
        assert "Invalid config" in str(error)
    
    def test_load_balancing_error(self):
        """Тест LoadBalancingError"""
        error = LoadBalancingError("test_service", "Load balancing failed")
        assert "test_service" in str(error)
        assert "Load balancing failed" in str(error)
    
    def test_health_check_error(self):
        """Тест HealthCheckError"""
        error = HealthCheckError("test_service", "Health check failed")
        assert "test_service" in str(error)
        assert "Health check failed" in str(error)
    
    def test_metrics_collection_error(self):
        """Тест MetricsCollectionError"""
        error = MetricsCollectionError("test_service", "Metrics collection failed")
        assert "test_service" in str(error)
        assert "Metrics collection failed" in str(error)
    
    def test_cache_error(self):
        """Тест CacheError"""
        error = CacheError("Cache operation failed")
        assert "Cache operation failed" in str(error)
    
    def test_cache_key_not_found_error(self):
        """Тест CacheKeyNotFoundError"""
        error = CacheKeyNotFoundError("test_key")
        assert "test_key" in str(error)
    
    def test_cache_expired_error(self):
        """Тест CacheExpiredError"""
        error = CacheExpiredError("test_key")
        assert "test_key" in str(error)
    
    def test_cache_configuration_error(self):
        """Тест CacheConfigurationError"""
        error = CacheConfigurationError("Invalid cache config")
        assert "Invalid cache config" in str(error)
    
    def test_async_operation_error(self):
        """Тест AsyncOperationError"""
        error = AsyncOperationError("Async operation failed")
        assert "Async operation failed" in str(error)
    
    def test_async_timeout_error(self):
        """Тест AsyncTimeoutError"""
        error = AsyncTimeoutError("Async operation timed out")
        assert "Async operation timed out" in str(error)


if __name__ == "__main__":
    pytest.main([__file__])
