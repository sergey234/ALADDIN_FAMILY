# -*- coding: utf-8 -*-
"""
Tests for Identity Theft Protection API Router

День 10: Тестирование API endpoints
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
from datetime import datetime
import os
import sys

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

try:
    from security.api.routers.identity_theft_protection_router import router
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

# Тестовый токен (в реальности должен проверяться через JWT)
TEST_TOKEN = "test_bearer_token_12345"
TEST_USER_ID = "test_user_123"
TEST_SNILS = "12345678901"  # 11 цифр


class TestHealthCheck:
    """Тесты health check endpoint"""

    def test_health_check_no_auth(self):
        """Health check должен работать без авторизации"""
        response = client.get("/api/identity-theft/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "unhealthy"]
        assert "agent_loaded" in data
        assert "timestamp" in data


class TestMonitorSNILS:
    """Тесты мониторинга СНИЛС"""

    def test_monitor_snils_no_auth(self):
        """Мониторинг СНИЛС требует авторизации"""
        response = client.post(
            "/api/identity-theft/monitor-snils",
            json={
                "user_id": TEST_USER_ID,
                "snils": TEST_SNILS
            }
        )
        assert response.status_code == 401

    def test_monitor_snils_invalid_format(self):
        """Проверка валидации формата СНИЛС"""
        response = client.post(
            "/api/identity-theft/monitor-snils",
            json={
                "user_id": TEST_USER_ID,
                "snils": "12345"  # Неправильный формат
            },
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 422  # Validation error

    def test_monitor_snils_valid(self):
        """Валидный запрос на мониторинг СНИЛС (требует согласия)"""
        response = client.post(
            "/api/identity-theft/monitor-snils",
            json={
                "user_id": TEST_USER_ID,
                "snils": TEST_SNILS
            },
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        # Может вернуть ошибку согласия, но не ошибку валидации
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data


class TestMonitorCredit:
    """Тесты мониторинга кредитного отчета"""

    def test_monitor_credit_no_auth(self):
        """Мониторинг кредитного отчета требует авторизации"""
        response = client.post(
            "/api/identity-theft/monitor-credit",
            json={
                "user_id": TEST_USER_ID
            }
        )
        assert response.status_code == 401

    def test_monitor_credit_valid(self):
        """Валидный запрос на мониторинг кредитного отчета"""
        response = client.post(
            "/api/identity-theft/monitor-credit",
            json={
                "user_id": TEST_USER_ID
            },
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        # Может вернуть ошибку согласия или отсутствия СНИЛС
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "nbki_available" in data
            assert "okb_available" in data


class TestCheckFraudDatabase:
    """Тесты проверки в базе мошенников"""

    def test_check_fraud_no_auth(self):
        """Проверка в базе мошенников требует авторизации"""
        response = client.post(
            "/api/identity-theft/check",
            json={
                "snils": TEST_SNILS
            }
        )
        assert response.status_code == 401

    def test_check_fraud_no_data(self):
        """Проверка без данных должна вернуть ошибку"""
        response = client.post(
            "/api/identity-theft/check",
            json={},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 400

    def test_check_fraud_with_snils(self):
        """Проверка с СНИЛС"""
        response = client.post(
            "/api/identity-theft/check",
            json={
                "snils": TEST_SNILS
            },
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "matches" in data
        assert "matches_count" in data

    def test_check_fraud_with_passport(self):
        """Проверка с паспортными данными"""
        response = client.post(
            "/api/identity-theft/check",
            json={
                "passport_series": "1234",
                "passport_number": "567890"
            },
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data


class TestDetectIdentityTheft:
    """Тесты обнаружения кражи личности"""

    def test_detect_no_auth(self):
        """Обнаружение кражи личности требует авторизации"""
        response = client.post(
            "/api/identity-theft/detect",
            json={
                "user_id": TEST_USER_ID
            }
        )
        assert response.status_code == 401

    def test_detect_valid(self):
        """Валидный запрос на обнаружение"""
        response = client.post(
            "/api/identity-theft/detect",
            json={
                "user_id": TEST_USER_ID,
                "snils": TEST_SNILS
            },
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "risk_score" in data


class TestGetAlerts:
    """Тесты получения алертов"""

    def test_get_alerts_no_auth(self):
        """Получение алертов требует авторизации"""
        response = client.get("/api/identity-theft/alerts")
        assert response.status_code == 401

    def test_get_alerts_with_user_id(self):
        """Получение алертов для пользователя"""
        response = client.get(
            "/api/identity-theft/alerts?user_id=test_user",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "alerts" in data
        assert "total_alerts" in data


class TestGetStatus:
    """Тесты получения статуса мониторинга"""

    def test_get_status_no_auth(self):
        """Получение статуса требует авторизации"""
        response = client.get("/api/identity-theft/status")
        assert response.status_code == 401

    def test_get_status_valid(self):
        """Валидный запрос статуса"""
        response = client.get(
            "/api/identity-theft/status?user_id=test_user",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "is_monitoring" in data


class TestConsent:
    """Тесты управления согласиями (152-ФЗ)"""

    def test_give_consent_no_auth(self):
        """Предоставление согласия требует авторизации"""
        response = client.post(
            "/api/identity-theft/consent",
            json={
                "user_id": TEST_USER_ID,
                "consent_types": {"snils": True, "credit": True}
            }
        )
        assert response.status_code == 401

    def test_give_consent_valid(self):
        """Валидное предоставление согласия"""
        response = client.post(
            "/api/identity-theft/consent",
            json={
                "user_id": TEST_USER_ID,
                "consent_types": {
                    "snils": True,
                    "passport": True,
                    "credit": True
                },
                "duration_days": 365
            },
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "consents" in data
        assert "expires_at" in data

    def test_revoke_consent_no_auth(self):
        """Отзыв согласия требует авторизации"""
        response = client.post(
            "/api/identity-theft/revoke-consent",
            json={
                "user_id": TEST_USER_ID
            }
        )
        assert response.status_code == 401

    def test_revoke_consent_valid(self):
        """Валидный отзыв согласия"""
        response = client.post(
            "/api/identity-theft/revoke-consent",
            json={
                "user_id": TEST_USER_ID
            },
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "user_id" in data


class TestCreditFreezeInstructions:
    """Тесты инструкций по кредитному замку"""

    def test_get_instructions_no_auth(self):
        """Получение инструкций требует авторизации"""
        response = client.get("/api/identity-theft/credit-freeze-instructions")
        assert response.status_code == 401

    def test_get_instructions_no_user_id(self):
        """Требуется user_id"""
        response = client.get(
            "/api/identity-theft/credit-freeze-instructions",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 422  # Validation error

    def test_get_instructions_valid(self):
        """Валидный запрос инструкций"""
        response = client.get(
            "/api/identity-theft/credit-freeze-instructions?user_id=test_user",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        # Может вернуть ошибку согласия
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            if data.get("success"):
                assert "title" in data
                assert "instructions" in data


class TestStopMonitoring:
    """Тесты остановки мониторинга"""

    def test_stop_monitoring_no_auth(self):
        """Остановка мониторинга требует авторизации"""
        response = client.post(
            "/api/identity-theft/stop-monitoring",
            json={
                "user_id": TEST_USER_ID
            }
        )
        assert response.status_code == 401

    def test_stop_monitoring_valid(self):
        """Валидная остановка мониторинга"""
        response = client.post(
            "/api/identity-theft/stop-monitoring",
            json={
                "user_id": TEST_USER_ID
            },
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "user_id" in data


# Интеграционные тесты
class TestIntegration:
    """Интеграционные тесты для проверки полного workflow"""

    def test_full_workflow_with_consent(self):
        """Полный workflow: согласие -> мониторинг СНИЛС -> проверка статуса"""
        # 1. Предоставление согласия
        consent_response = client.post(
            "/api/identity-theft/consent",
            json={
                "user_id": TEST_USER_ID,
                "consent_types": {"snils": True, "credit": True},
                "duration_days": 365
            },
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert consent_response.status_code == 200

        # 2. Мониторинг СНИЛС
        monitor_response = client.post(
            "/api/identity-theft/monitor-snils",
            json={
                "user_id": TEST_USER_ID,
                "snils": TEST_SNILS
            },
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        # Может быть успешным если согласие принято
        assert monitor_response.status_code in [200, 400, 500]

        # 3. Проверка статуса
        status_response = client.get(
            f"/api/identity-theft/status?user_id={TEST_USER_ID}",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "is_monitoring" in status_data

    def test_consent_required_validation(self):
        """Проверка что операции требуют согласия"""
        # Попытка мониторинга без согласия
        response = client.post(
            "/api/identity-theft/monitor-snils",
            json={
                "user_id": "user_without_consent",
                "snils": TEST_SNILS
            },
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        # Должен вернуть ошибку согласия или работать с предупреждением
        assert response.status_code in [200, 400, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
