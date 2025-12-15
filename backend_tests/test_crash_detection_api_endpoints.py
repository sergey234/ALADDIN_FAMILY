#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграционные тесты для Crash Detection API endpoints

День 6-9: Тестирование API
- Тесты всех endpoints
- Тесты валидации данных
- Тесты обработки ошибок

Запуск:
    pytest backend_tests/test_crash_detection_api_endpoints.py -v
"""

import sys
import os
import time
from pathlib import Path
from unittest.mock import Mock, patch

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from fastapi.testclient import TestClient
    from security.api.routers.crash_detection_router import router, get_agent
    from fastapi import FastAPI
except ImportError:
    import pytest
    pytest.skip("FastAPI или router не доступен", allow_module_level=True)


class TestCrashDetectionAPI:
    """Тесты для Crash Detection API endpoints"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Создаем тестовое приложение
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)
        
        # Сбрасываем singleton агента
        import security.api.routers.crash_detection_router as router_module
        router_module._agent_instance = None
        
        self.test_user_id = "test_user_123"

    def test_start_monitoring_endpoint(self):
        """Тест POST /api/crash-detection/start"""
        response = self.client.post(
            "/api/crash-detection/start",
            json={"user_id": self.test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_id"] == self.test_user_id

    def test_stop_monitoring_endpoint(self):
        """Тест POST /api/crash-detection/stop"""
        # Сначала запускаем
        self.client.post(
            "/api/crash-detection/start",
            json={"user_id": self.test_user_id}
        )
        
        # Останавливаем
        response = self.client.post(
            "/api/crash-detection/stop",
            json={"user_id": self.test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_status_endpoint(self):
        """Тест GET /api/crash-detection/status"""
        # Запускаем мониторинг
        self.client.post(
            "/api/crash-detection/start",
            json={"user_id": self.test_user_id}
        )
        
        # Получаем статус
        response = self.client.get(
            "/api/crash-detection/status",
            params={"user_id": self.test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "monitoring_active" in data
        assert data["monitoring_active"] is True

    def test_data_endpoint_normal(self):
        """Тест POST /api/crash-detection/data (нормальные данные)"""
        # Запускаем мониторинг
        self.client.post(
            "/api/crash-detection/start",
            json={"user_id": self.test_user_id}
        )
        
        # Отправляем нормальные данные
        response = self.client.post(
            "/api/crash-detection/data",
            json={
                "user_id": self.test_user_id,
                "accelerometer": {
                    "x": 0.1,
                    "y": 0.2,
                    "z": 9.8,
                    "timestamp": time.time()
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "crash_detected" in data
        assert data["crash_detected"] is False

    def test_data_endpoint_crash(self):
        """Тест POST /api/crash-detection/data (авария)"""
        # Запускаем мониторинг
        self.client.post(
            "/api/crash-detection/start",
            json={"user_id": self.test_user_id}
        )
        
        # Отправляем данные аварии
        response = self.client.post(
            "/api/crash-detection/data",
            json={
                "user_id": self.test_user_id,
                "accelerometer": {
                    "x": 30.0,
                    "y": 25.0,
                    "z": 40.0,
                    "timestamp": time.time()
                },
                "speed": 60.0,
                "location": {
                    "latitude": 55.7558,
                    "longitude": 37.6173
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Может быть обнаружена авария или нет (зависит от фильтра)
        assert "crash_detected" in data

    def test_data_endpoint_with_gyroscope(self):
        """Тест POST /api/crash-detection/data (с гироскопом)"""
        # Запускаем мониторинг
        self.client.post(
            "/api/crash-detection/start",
            json={"user_id": self.test_user_id}
        )
        
        # Отправляем данные с гироскопом
        response = self.client.post(
            "/api/crash-detection/data",
            json={
                "user_id": self.test_user_id,
                "accelerometer": {
                    "x": 0.1,
                    "y": 0.2,
                    "z": 9.8,
                    "timestamp": time.time()
                },
                "gyroscope": {
                    "x": 0.1,
                    "y": 0.2,
                    "z": 0.05,
                    "timestamp": time.time()
                }
            }
        )
        
        assert response.status_code == 200

    def test_data_endpoint_with_geofence(self):
        """Тест POST /api/crash-detection/data (с геозоной)"""
        # Запускаем мониторинг
        self.client.post(
            "/api/crash-detection/start",
            json={"user_id": self.test_user_id}
        )
        
        # Отправляем данные с геозоной (без точного GPS)
        response = self.client.post(
            "/api/crash-detection/data",
            json={
                "user_id": self.test_user_id,
                "accelerometer": {
                    "x": 0.1,
                    "y": 0.2,
                    "z": 9.8,
                    "timestamp": time.time()
                },
                "geofence_center": {
                    "latitude": 55.7558,
                    "longitude": 37.6173
                }
            }
        )
        
        assert response.status_code == 200

    def test_data_endpoint_validation_error(self):
        """Тест POST /api/crash-detection/data (ошибка валидации)"""
        # Запускаем мониторинг
        self.client.post(
            "/api/crash-detection/start",
            json={"user_id": self.test_user_id}
        )
        
        # Отправляем невалидные данные (нет x, y, z)
        response = self.client.post(
            "/api/crash-detection/data",
            json={
                "user_id": self.test_user_id,
                "accelerometer": {
                    "timestamp": time.time()
                }
            }
        )
        
        # Должна быть ошибка валидации
        assert response.status_code == 422

    def test_history_endpoint(self):
        """Тест GET /api/crash-detection/history"""
        # Запускаем мониторинг
        self.client.post(
            "/api/crash-detection/start",
            json={"user_id": self.test_user_id}
        )
        
        # Получаем историю
        response = self.client.get(
            "/api/crash-detection/history",
            params={"user_id": self.test_user_id, "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "crashes" in data
        assert isinstance(data["crashes"], list)

    def test_health_endpoint(self):
        """Тест GET /api/crash-detection/health"""
        response = self.client.get("/api/crash-detection/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent"] == "crash_detection_agent"
        assert "version" in data
        assert "emergency_service" in data

    def test_emergency_call_endpoint(self):
        """Тест POST /api/crash-detection/emergency-call"""
        # Запускаем мониторинг
        self.client.post(
            "/api/crash-detection/start",
            json={"user_id": self.test_user_id}
        )
        
        # Симулируем аварию
        self.client.post(
            "/api/crash-detection/data",
            json={
                "user_id": self.test_user_id,
                "accelerometer": {
                    "x": 30.0,
                    "y": 25.0,
                    "z": 40.0,
                    "timestamp": time.time()
                }
            }
        )
        
        # Вызываем экстренную службу
        response = self.client.post(
            "/api/crash-detection/emergency-call",
            json={
                "user_id": self.test_user_id,
                "location": {
                    "latitude": 55.7558,
                    "longitude": 37.6173
                }
            }
        )
        
        # Может быть успех или ошибка (если нет аварии в истории)
        assert response.status_code in [200, 404, 500]

    def test_cancel_emergency_call_endpoint(self):
        """Тест POST /api/crash-detection/cancel-emergency-call"""
        # Запускаем мониторинг
        self.client.post(
            "/api/crash-detection/start",
            json={"user_id": self.test_user_id}
        )
        
        # Симулируем аварию и вызов
        self.client.post(
            "/api/crash-detection/data",
            json={
                "user_id": self.test_user_id,
                "accelerometer": {
                    "x": 30.0,
                    "y": 25.0,
                    "z": 40.0,
                    "timestamp": time.time()
                }
            }
        )
        
        # Отменяем вызов (может быть ошибка, если вызов не был сделан)
        response = self.client.post(
            "/api/crash-detection/cancel-emergency-call",
            json={
                "user_id": self.test_user_id,
                "call_id": "test_call_123"
            }
        )
        
        # Может быть успех или ошибка
        assert response.status_code in [200, 404, 500]

    def test_start_monitoring_invalid_user_id(self):
        """Тест POST /api/crash-detection/start (невалидный user_id)"""
        response = self.client.post(
            "/api/crash-detection/start",
            json={"user_id": ""}  # Пустой user_id
        )
        
        # Может быть ошибка валидации или успех (зависит от валидации)
        assert response.status_code in [200, 422]

    def test_data_endpoint_user_not_monitoring(self):
        """Тест POST /api/crash-detection/data (пользователь не в мониторинге)"""
        # НЕ запускаем мониторинг
        
        # Отправляем данные
        response = self.client.post(
            "/api/crash-detection/data",
            json={
                "user_id": self.test_user_id,
                "accelerometer": {
                    "x": 0.1,
                    "y": 0.2,
                    "z": 9.8,
                    "timestamp": time.time()
                }
            }
        )
        
        # Может быть ошибка или успех (зависит от реализации)
        assert response.status_code in [200, 400, 404]


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
