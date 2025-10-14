# -*- coding: utf-8 -*-
"""
Unit тесты для Service Mesh Manager (упрощенная версия)

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
    # Исключения
    ServiceMeshError,
    ServiceNotFoundError,
    ServiceAlreadyRegisteredError,
    InvalidServiceConfigurationError
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
        assert hasattr(manager, 'services')
        assert hasattr(manager, 'service_endpoints')
        assert hasattr(manager, 'service_health')
        assert hasattr(manager, 'service_metrics')
        assert hasattr(manager, 'mesh_config')
        assert hasattr(manager, 'thread_pool')
        assert hasattr(manager, 'event_manager')
        assert hasattr(manager, 'cache')
        assert hasattr(manager, 'async_manager')
        assert hasattr(manager, 'structured_logger')
        assert hasattr(manager, 'prometheus_metrics')
    
    def test_initialize(self, manager):
        """Тест инициализации системы"""
        manager.initialize()
        assert hasattr(manager, 'monitoring_thread')
        assert manager.monitoring_thread is not None
        assert manager.monitoring_thread.is_alive()
    
    def test_stop(self, manager):
        """Тест остановки системы"""
        manager.initialize()
        assert manager.monitoring_thread is not None
        
        manager.stop()
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
            "discovery_interval": 60,
            "health_check_interval": 120
        }
        
        manager.update_mesh_config(new_config)
        updated_config = manager.get_mesh_config()
        
        assert updated_config["discovery_interval"] == 60
        assert updated_config["health_check_interval"] == 120
    
    def test_context_manager(self, manager, sample_service):
        """Тест использования как контекстного менеджера"""
        with manager as mgr:
            assert mgr.monitoring_thread is not None
            mgr.register_service(sample_service)
            assert mgr.is_service_registered("test_service")
        
        # После выхода из контекста система должна быть остановлена
        assert manager.monitoring_thread is None or not manager.monitoring_thread.is_alive()
    
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


if __name__ == "__main__":
    pytest.main([__file__])
