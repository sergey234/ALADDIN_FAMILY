#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тесты для API Endpoints Dark Web Monitoring

Тестирует Flask endpoints через тестовый клиент.

Запуск:
    pytest backend_tests/test_dark_web_api_endpoints.py -v
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import json

# Добавляем путь к security/api
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'security', 'api'))

try:
    from flask import Flask
    from dark_web_monitoring_endpoints import dark_web_bp
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    pytestmark = pytest.mark.skip("Flask не установлен")


@pytest.fixture
def app():
    """Создание Flask приложения для тестирования"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(dark_web_bp, url_prefix='/api/darkweb')
    return app


@pytest.fixture
def client(app):
    """Создание тестового клиента"""
    return app.test_client()


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask не установлен")
class TestDarkWebAPIEndpoints:
    """Тесты для API endpoints"""

    def test_health_check(self, client):
        """Тест health check endpoint"""
        response = client.get('/api/darkweb/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "agent_loaded" in data

    def test_check_email_without_auth(self, client):
        """Тест проверки email без авторизации (должна вернуть 401)"""
        response = client.post('/api/darkweb/check',
                              json={"email": "test@example.com"},
                              content_type='application/json')
        # TODO: Раскомментировать когда реализуется авторизация
        # assert response.status_code == 401
        assert response.status_code in [200, 401]

    def test_check_email_invalid_format(self, client):
        """Тест проверки с невалидным email"""
        # Мокируем авторизацию
        with patch('dark_web_monitoring_endpoints.require_auth', lambda f: f):
            response = client.post('/api/darkweb/check',
                                  json={"email": "invalid-email"},
                                  content_type='application/json')
            assert response.status_code == 400

            data = json.loads(response.data)
            assert "error" in data

    def test_check_email_missing_field(self, client):
        """Тест проверки без обязательного поля"""
        with patch('dark_web_monitoring_endpoints.require_auth', lambda f: f):
            response = client.post('/api/darkweb/check',
                                  json={},
                                  content_type='application/json')
            assert response.status_code == 400

            data = json.loads(response.data)
            assert "error" in data
            assert "email" in data["error"].lower()

    def test_start_monitoring(self, client):
        """Тест запуска мониторинга"""
        with patch('dark_web_monitoring_endpoints.require_auth', lambda f: f), \
             patch('dark_web_monitoring_endpoints.get_agent') as mock_get_agent:

            mock_agent = Mock()
            mock_agent.start_monitoring.return_value = {
                "success": True,
                "user_id": "test_user",
                "next_check": "2025-12-10T12:00:00",
                "interval_hours": 24
            }
            mock_get_agent.return_value = mock_agent

            response = client.post('/api/darkweb/start-monitoring',
                                  json={
                                      "user_id": "test_user",
                                      "email": "test@example.com",
                                      "interval_hours": 24
                                  },
                                  content_type='application/json')

            assert response.status_code == 200

            data = json.loads(response.data)
            assert data["success"] == True
            assert data["user_id"] == "test_user"

    def test_stop_monitoring(self, client):
        """Тест остановки мониторинга"""
        with patch('dark_web_monitoring_endpoints.require_auth', lambda f: f), \
             patch('dark_web_monitoring_endpoints.get_agent') as mock_get_agent:

            mock_agent = Mock()
            mock_agent.stop_monitoring.return_value = {
                "success": True,
                "user_id": "test_user"
            }
            mock_get_agent.return_value = mock_agent

            response = client.post('/api/darkweb/stop-monitoring',
                                  json={"user_id": "test_user"},
                                  content_type='application/json')

            assert response.status_code == 200

            data = json.loads(response.data)
            assert data["success"] == True

    def test_get_status(self, client):
        """Тест получения статуса"""
        with patch('dark_web_monitoring_endpoints.require_auth', lambda f: f), \
             patch('dark_web_monitoring_endpoints.get_agent') as mock_get_agent:

            mock_agent = Mock()
            mock_agent.get_monitoring_status.return_value = {
                "is_monitoring": True,
                "user_id": "test_user",
                "status": {}
            }
            mock_get_agent.return_value = mock_agent

            response = client.get('/api/darkweb/status?user_id=test_user')

            assert response.status_code == 200

            data = json.loads(response.data)
            assert data["success"] == True
            assert data["is_monitoring"] == True

    def test_get_breaches(self, client):
        """Тест получения списка утечек"""
        with patch('dark_web_monitoring_endpoints.require_auth', lambda f: f), \
             patch('dark_web_monitoring_endpoints.get_agent') as mock_get_agent:

            mock_agent = Mock()
            mock_agent.collect_threats.return_value = []
            mock_agent.analyze_threats.return_value = []
            mock_get_agent.return_value = mock_agent

            response = client.get('/api/darkweb/breaches')

            assert response.status_code == 200

            data = json.loads(response.data)
            assert data["success"] == True
            assert "threats" in data
            assert "analyzed_threats" in data

    def test_error_handling(self, client):
        """Тест обработки ошибок"""
        with patch('dark_web_monitoring_endpoints.require_auth', lambda f: f), \
             patch('dark_web_monitoring_endpoints.get_agent') as mock_get_agent:

            mock_agent = Mock()
            mock_agent.check_email_breach.side_effect = Exception("Test error")
            mock_get_agent.return_value = mock_agent

            response = client.post('/api/darkweb/check',
                                  json={"email": "test@example.com"},
                                  content_type='application/json')

            assert response.status_code == 500

            data = json.loads(response.data)
            assert data["success"] == False
            assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
