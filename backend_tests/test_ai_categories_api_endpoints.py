#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграционные тесты для AI Categories API Router

День 5-6: Тестирование API endpoints
"""

import pytest
try:
    from fastapi.testclient import TestClient
except ImportError:
    try:
        from starlette.testclient import TestClient
    except ImportError:
        pytest.skip("TestClient not available", allow_module_level=True)

from fastapi import FastAPI
import os
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from security.api.routers.ai_categories_router import router
except ImportError as e:
    pytest.skip(f"Cannot import router: {e}", allow_module_level=True)

# Создаем тестовое приложение
app = FastAPI()
app.include_router(router)

try:
    client = TestClient(app)
except TypeError:
    # Для старых версий starlette
    client = TestClient(app=app)

# Тестовые данные
TEST_USER_ID = "test_user_123"


class TestHealthCheck:
    """Тесты health check endpoint"""

    def test_health_check(self):
        """Health check должен работать без авторизации"""
        response = client.get("/api/ai-categories/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "agent" in data
        assert data["agent"] == "ai_categories_agent"
        assert "sites_count" in data
        assert data["sites_count"] == 9


class TestGetSites:
    """Тесты получения списка AI-сайтов"""

    def test_get_sites(self):
        """Получение списка всех AI-сайтов"""
        response = client.get("/api/ai-categories/sites")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "sites" in data
        assert len(data["sites"]) == 9
        assert data["total"] == 9
        
        # Проверяем структуру первого сайта
        first_site = data["sites"][0]
        assert "id" in first_site
        assert "name" in first_site
        assert "domain" in first_site
        assert "category" in first_site


class TestBlockSites:
    """Тесты блокировки AI-сайтов"""

    def test_block_sites_basic(self):
        """Базовая блокировка сайтов"""
        response = client.post(
            "/api/ai-categories/block",
            json={
                "user_id": TEST_USER_ID,
                "site_ids": ["chatgpt", "claude"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["blocked"]) == 2
        assert "chatgpt" in data["blocked"]
        assert "claude" in data["blocked"]

    def test_block_sites_with_time_restriction(self):
        """Блокировка с ограничением по времени"""
        response = client.post(
            "/api/ai-categories/block",
            json={
                "user_id": TEST_USER_ID,
                "site_ids": ["chatgpt"],
                "time_restriction": {
                    "start_time": "09:00",
                    "end_time": "18:00",
                    "days_of_week": [0, 1, 2, 3, 4],
                    "enabled": True
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_block_sites_invalid_time_format(self):
        """Проверка валидации формата времени"""
        response = client.post(
            "/api/ai-categories/block",
            json={
                "user_id": TEST_USER_ID,
                "site_ids": ["chatgpt"],
                "time_restriction": {
                    "start_time": "25:00",  # Неверный формат
                    "end_time": "18:00",
                    "days_of_week": [0, 1, 2, 3, 4],
                    "enabled": True
                }
            }
        )
        assert response.status_code == 422  # Validation error

    def test_block_sites_empty_list(self):
        """Блокировка с пустым списком сайтов"""
        response = client.post(
            "/api/ai-categories/block",
            json={
                "user_id": TEST_USER_ID,
                "site_ids": []
            }
        )
        assert response.status_code == 422  # Validation error

    def test_block_sites_nonexistent(self):
        """Блокировка несуществующего сайта"""
        response = client.post(
            "/api/ai-categories/block",
            json={
                "user_id": TEST_USER_ID,
                "site_ids": ["nonexistent", "chatgpt"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "nonexistent" in data["not_found"]
        assert "chatgpt" in data["blocked"]


class TestAllowSites:
    """Тесты разрешения доступа к AI-сайтам"""

    def test_allow_sites_basic(self):
        """Базовое разрешение доступа"""
        # Сначала блокируем
        client.post(
            "/api/ai-categories/block",
            json={
                "user_id": TEST_USER_ID,
                "site_ids": ["chatgpt"]
            }
        )
        
        # Затем разрешаем
        response = client.post(
            "/api/ai-categories/allow",
            json={
                "user_id": TEST_USER_ID,
                "site_ids": ["chatgpt"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "chatgpt" in data["allowed"]

    def test_allow_sites_empty_list(self):
        """Разрешение с пустым списком"""
        response = client.post(
            "/api/ai-categories/allow",
            json={
                "user_id": TEST_USER_ID,
                "site_ids": []
            }
        )
        assert response.status_code == 422  # Validation error


class TestCheckAccess:
    """Тесты проверки доступа"""

    def test_check_access_blocked(self):
        """Проверка доступа к заблокированному сайту"""
        # Блокируем сайт
        client.post(
            "/api/ai-categories/block",
            json={
                "user_id": TEST_USER_ID,
                "site_ids": ["chatgpt"]
            }
        )
        
        # Проверяем доступ
        response = client.post(
            "/api/ai-categories/check",
            json={
                "user_id": TEST_USER_ID,
                "site_id": "chatgpt"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["allowed"] is False
        assert data["blocked"] is True
        assert "reason" in data

    def test_check_access_allowed(self):
        """Проверка доступа к разрешенному сайту"""
        # Разрешаем сайт
        client.post(
            "/api/ai-categories/allow",
            json={
                "user_id": TEST_USER_ID,
                "site_ids": ["alice"]
            }
        )
        
        # Проверяем доступ
        response = client.post(
            "/api/ai-categories/check",
            json={
                "user_id": TEST_USER_ID,
                "site_id": "alice"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["allowed"] is True
        assert data["blocked"] is False

    def test_check_access_with_age(self):
        """Проверка доступа с указанием возраста"""
        response = client.post(
            "/api/ai-categories/check",
            json={
                "user_id": TEST_USER_ID,
                "site_id": "chatgpt",
                "user_age": 15
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "allowed" in data
        assert "blocked" in data

    def test_check_access_nonexistent_site(self):
        """Проверка доступа к несуществующему сайту"""
        response = client.post(
            "/api/ai-categories/check",
            json={
                "user_id": TEST_USER_ID,
                "site_id": "nonexistent"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["blocked"] is True
        assert data["reason"] == "site_not_found"


class TestGetStatus:
    """Тесты получения статуса"""

    def test_get_status(self):
        """Получение статуса всех сайтов"""
        # Блокируем несколько сайтов
        client.post(
            "/api/ai-categories/block",
            json={
                "user_id": TEST_USER_ID,
                "site_ids": ["chatgpt", "claude"]
            }
        )
        
        response = client.get(
            f"/api/ai-categories/status?user_id={TEST_USER_ID}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == TEST_USER_ID
        assert data["total_sites"] == 9
        assert "blocked_count" in data
        assert "allowed_count" in data
        assert len(data["sites"]) == 9

    def test_get_status_missing_user_id(self):
        """Получение статуса без user_id"""
        response = client.get("/api/ai-categories/status")
        assert response.status_code == 422  # Validation error


class TestGetAccessHistory:
    """Тесты получения истории доступа"""

    def test_get_access_history(self):
        """Получение истории попыток доступа"""
        # Делаем несколько попыток доступа
        client.post(
            "/api/ai-categories/check",
            json={
                "user_id": TEST_USER_ID,
                "site_id": "chatgpt"
            }
        )
        client.post(
            "/api/ai-categories/check",
            json={
                "user_id": TEST_USER_ID,
                "site_id": "alice"
            }
        )
        
        response = client.get(
            f"/api/ai-categories/history?user_id={TEST_USER_ID}&limit=10"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_id"] == TEST_USER_ID
        assert "history" in data
        assert len(data["history"]) >= 2

    def test_get_access_history_limit(self):
        """Получение истории с ограничением"""
        response = client.get(
            f"/api/ai-categories/history?user_id={TEST_USER_ID}&limit=5"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["history"]) <= 5


class TestSetAgeRestriction:
    """Тесты установки ограничения по возрасту"""

    def test_set_age_restriction(self):
        """Установка ограничения по возрасту"""
        response = client.post(
            "/api/ai-categories/age-restriction",
            json={
                "user_id": TEST_USER_ID,
                "site_id": "chatgpt",
                "age_restriction": {
                    "min_age": 16,
                    "require_parental_approval": True,
                    "block_completely": False
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_set_age_restriction_invalid_age(self):
        """Установка ограничения с невалидным возрастом"""
        response = client.post(
            "/api/ai-categories/age-restriction",
            json={
                "user_id": TEST_USER_ID,
                "site_id": "chatgpt",
                "age_restriction": {
                    "min_age": 25,  # Больше 18 (максимум)
                    "require_parental_approval": True,
                    "block_completely": False
                }
            }
        )
        assert response.status_code == 422  # Validation error

    def test_set_age_restriction_nonexistent_site(self):
        """Установка ограничения для несуществующего сайта"""
        response = client.post(
            "/api/ai-categories/age-restriction",
            json={
                "user_id": TEST_USER_ID,
                "site_id": "nonexistent",
                "age_restriction": {
                    "min_age": 13,
                    "require_parental_approval": True,
                    "block_completely": False
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "не найден" in data["message"]


# Для запуска тестов напрямую
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
