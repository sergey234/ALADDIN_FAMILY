"""
Unit-тесты для улучшенного API Gateway
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Импортируем классы из API Gateway
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.microservices.api_gateway import (
    APIGateway,
    RouteConfig,
    APIRequest,
    APIResponse,
    AuthenticationInterface,
    RouteStatus,
    AuthMethod
)


class TestAPIGatewayEnhanced:
    """Тесты для улучшенного API Gateway"""

    @pytest.fixture
    def api_gateway(self):
        """Фикстура для создания экземпляра API Gateway"""
        return APIGateway(
            database_url="sqlite:///:memory:",
            redis_url="redis://localhost:6379/0",
            jwt_secret="test-secret-key-12345",
            jwt_algorithm="HS256"
        )

    def test_str_representation(self, api_gateway):
        """Тест строкового представления"""
        str_repr = str(api_gateway)
        assert "APIGateway" in str_repr
        assert "active_routes=0" in str_repr
        assert "connections=0" in str_repr
        assert "running=False" in str_repr

    def test_repr_representation(self, api_gateway):
        """Тест repr представления"""
        repr_str = repr(api_gateway)
        assert "APIGateway" in repr_str
        assert "sqlite:///:memory:" in repr_str
        assert "redis://localhost:6379/0" in repr_str
        assert "HS256" in repr_str

    def test_to_dict(self, api_gateway):
        """Тест конвертации в словарь"""
        data = api_gateway.to_dict()
        
        assert isinstance(data, dict)
        assert data["database_url"] == "sqlite:///:memory:"
        assert data["redis_url"] == "redis://localhost:6379/0"
        assert data["jwt_secret"] == "***"  # Секрет скрыт
        assert data["jwt_algorithm"] == "HS256"
        assert data["active_routes"] == 0
        assert data["active_connections"] == 0
        assert data["is_running"] is False
        assert "queue_size" in data

    def test_from_dict(self):
        """Тест создания из словаря"""
        data = {
            "database_url": "sqlite:///test.db",
            "redis_url": "redis://test:6379/0",
            "jwt_secret": "test-secret",
            "jwt_algorithm": "HS256",
            "active_connections": 5,
            "is_running": True
        }
        
        gateway = APIGateway.from_dict(data)
        
        assert gateway.database_url == "sqlite:///test.db"
        assert gateway.redis_url == "redis://test:6379/0"
        assert gateway.jwt_secret == "test-secret"
        assert gateway.jwt_algorithm == "HS256"
        assert gateway.active_connections == 5
        assert gateway.is_running is True

    def test_validate_config_success(self, api_gateway):
        """Тест успешной валидации конфигурации"""
        assert api_gateway.validate_config() is True

    def test_validate_config_failure(self):
        """Тест неуспешной валидации конфигурации"""
        # Тест с коротким JWT секретом
        gateway = APIGateway(jwt_secret="short")
        assert gateway.validate_config() is False
        
        # Тест с пустыми значениями
        gateway = APIGateway(database_url="", redis_url="")
        assert gateway.validate_config() is False

    def test_context_manager(self, api_gateway):
        """Тест контекстного менеджера"""
        with patch.object(api_gateway.logger, 'info') as mock_info:
            with api_gateway as gateway:
                assert gateway is api_gateway
            # Проверяем что были вызовы info для входа и выхода
            assert mock_info.call_count == 2
            calls = [call[0][0] for call in mock_info.call_args_list]
            assert "Entering API Gateway context" in calls
            assert "Exiting API Gateway context successfully" in calls

    def test_context_manager_with_exception(self, api_gateway):
        """Тест контекстного менеджера с исключением"""
        with patch.object(api_gateway.logger, 'error') as mock_error:
            try:
                with api_gateway:
                    raise ValueError("Test error")
            except ValueError:
                pass
            mock_error.assert_called()

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, api_gateway):
        """Тест health check в здоровом состоянии"""
        # Мокаем компоненты как инициализированные
        api_gateway.engine = Mock()
        api_gateway.redis_client = Mock()
        api_gateway.routes = {"test": Mock()}
        
        health = await api_gateway.health_check()
        
        assert health["status"] == "healthy"
        assert health["database"] == "connected"
        assert health["redis"] == "connected"
        assert health["routes"] == 1
        assert "timestamp" in health

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, api_gateway):
        """Тест health check в нездоровом состоянии"""
        # Все компоненты не инициализированы
        api_gateway.engine = None
        api_gateway.redis_client = None
        api_gateway.routes = {}
        
        health = await api_gateway.health_check()
        
        assert health["status"] == "unhealthy"
        assert health["database"] == "disconnected"
        assert health["redis"] == "disconnected"
        assert health["routes"] == 0

    @pytest.mark.asyncio
    async def test_health_check_with_exception(self, api_gateway):
        """Тест health check с исключением"""
        with patch.object(api_gateway, 'engine', side_effect=Exception("Test error")):
            health = await api_gateway.health_check()
            
            assert health["status"] == "unhealthy"
            assert "error" in health
            assert health["error"] == "Test error"

    @pytest.mark.asyncio
    async def test_performance_metrics(self, api_gateway):
        """Тест метрик производительности"""
        # Устанавливаем некоторые значения
        api_gateway.active_connections = 10
        api_gateway.routes = {"route1": Mock(), "route2": Mock()}
        api_gateway.is_running = True
        
        metrics = await api_gateway.performance_metrics()
        
        assert metrics["active_connections"] == 10
        assert metrics["total_routes"] == 2
        assert metrics["is_running"] is True
        assert "uptime" in metrics
        assert "timestamp" in metrics
        assert metrics["memory_usage"] == "N/A"
        assert metrics["cpu_usage"] == "N/A"

    @pytest.mark.asyncio
    async def test_performance_metrics_with_exception(self, api_gateway):
        """Тест метрик производительности с исключением"""
        with patch.object(api_gateway, 'request_queue', side_effect=Exception("Test error")):
            metrics = await api_gateway.performance_metrics()
            
            assert "error" in metrics
            assert metrics["error"] == "Test error"
            assert "timestamp" in metrics

    def test_start_time_initialization(self, api_gateway):
        """Тест инициализации времени старта"""
        assert hasattr(api_gateway, '_start_time')
        assert hasattr(api_gateway, '_request_count')
        assert hasattr(api_gateway, '_error_count')
        
        # Время старта должно быть близко к текущему времени
        current_time = time.time()
        assert abs(api_gateway._start_time - current_time) < 1.0

    def test_metrics_counters_initialization(self, api_gateway):
        """Тест инициализации счетчиков метрик"""
        assert api_gateway._request_count == 0
        assert api_gateway._error_count == 0

    @pytest.mark.asyncio
    async def test_initialize_success(self, api_gateway):
        """Тест успешной инициализации"""
        with patch('security.microservices.api_gateway.create_engine') as mock_engine, \
             patch('security.microservices.api_gateway.Base.metadata.create_all'), \
             patch('security.microservices.api_gateway.sessionmaker') as mock_session, \
             patch('security.microservices.api_gateway.redis.from_url') as mock_redis:
            
            mock_engine.return_value = Mock()
            mock_session.return_value = Mock()
            mock_redis.return_value = Mock()
            
            result = await api_gateway.initialize()
            
            assert result is True
            assert api_gateway.engine is not None
            assert api_gateway.session_factory is not None
            assert api_gateway.redis_client is not None

    @pytest.mark.asyncio
    async def test_initialize_failure(self, api_gateway):
        """Тест неуспешной инициализации"""
        with patch('security.microservices.api_gateway.create_engine', 
                   side_effect=Exception("Database error")):
            
            result = await api_gateway.initialize()
            
            assert result is False
            assert api_gateway.engine is None

    def test_route_config_creation(self):
        """Тест создания конфигурации маршрута"""
        route = RouteConfig(
            path="/test",
            method="GET",
            target_service="test-service",
            target_url="http://localhost:8000",
            rate_limit=100,
            timeout=30,
            is_active=True
        )
        
        assert route.path == "/test"
        assert route.method == "GET"
        assert route.target_service == "test-service"
        assert route.target_url == "http://localhost:8000"
        assert route.rate_limit == 100
        assert route.timeout == 30
        assert route.is_active is True

    def test_api_request_creation(self):
        """Тест создания API запроса"""
        from datetime import datetime
        
        request = APIRequest(
            request_id="test-request-123",
            user_id="user-456",
            method="POST",
            path="/api/test",
            headers={"Content-Type": "application/json"},
            query_params={"param": "value"},
            body='{"test": "data"}',
            ip_address="127.0.0.1",
            user_agent="test-agent",
            timestamp=datetime.now()
        )
        
        assert request.method == "POST"
        assert request.path == "/api/test"
        assert request.headers == {"Content-Type": "application/json"}
        assert request.body == '{"test": "data"}'
        assert request.query_params == {"param": "value"}
        assert request.request_id == "test-request-123"
        assert request.user_id == "user-456"

    def test_api_response_creation(self):
        """Тест создания API ответа"""
        from datetime import datetime
        
        response = APIResponse(
            request_id="test-request-123",
            status_code=200,
            headers={"Content-Type": "application/json"},
            body='{"result": "success"}',
            response_time=123,
            timestamp=datetime.now()
        )
        
        assert response.status_code == 200
        assert response.headers == {"Content-Type": "application/json"}
        assert response.body == '{"result": "success"}'
        assert response.response_time == 123
        assert response.request_id == "test-request-123"

    def test_route_status_enum(self):
        """Тест перечисления статусов маршрутов"""
        assert RouteStatus.ACTIVE.value == "active"
        assert RouteStatus.INACTIVE.value == "inactive"
        assert RouteStatus.MAINTENANCE.value == "maintenance"

    def test_auth_method_enum(self):
        """Тест перечисления методов аутентификации"""
        assert AuthMethod.JWT.value == "jwt"
        assert AuthMethod.API_KEY.value == "api_key"
        assert AuthMethod.OAUTH2.value == "oauth2"
        assert AuthMethod.NONE.value == "none"


class TestAuthenticationInterface:
    """Тесты для интерфейса аутентификации"""

    def test_abstract_methods(self):
        """Тест абстрактных методов"""
        # AuthenticationInterface - абстрактный класс
        # Нельзя создать экземпляр напрямую
        with pytest.raises(TypeError):
            AuthenticationInterface()

    def test_abstract_method_signatures(self):
        """Тест сигнатур абстрактных методов"""
        # Проверяем что методы определены как абстрактные
        assert hasattr(AuthenticationInterface, 'authenticate')
        assert hasattr(AuthenticationInterface, 'authorize')


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"])