#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Интеграционные тесты для Driving Reports API endpoints

Дата создания: 12 декабря 2025
"""

import unittest
from fastapi.testclient import TestClient
from datetime import datetime

# Импорт router
try:
    from security.api.routers.driving_reports_router import router
    from fastapi import FastAPI
except ImportError:
    router = None
    FastAPI = None


@unittest.skipIf(router is None, "Driving Reports Router не доступен")
class TestDrivingReportsAPIEndpoints(unittest.TestCase):
    """Тесты для API endpoints Driving Reports Agent"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
        if FastAPI is None:
            self.skipTest("FastAPI не доступен")

        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)
        self.user_id = "test_user_api_123"

    def test_start_monitoring_endpoint(self):
        """Тест POST /api/driving-reports/start"""
        response = self.client.post(
            "/api/driving-reports/start",
            json={"user_id": self.user_id}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)

    def test_start_monitoring_invalid_request(self):
        """Тест POST /api/driving-reports/start с невалидными данными"""
        response = self.client.post(
            "/api/driving-reports/start",
            json={}  # Отсутствует user_id
        )
        self.assertEqual(response.status_code, 422)  # Validation error

    def test_stop_monitoring_endpoint(self):
        """Тест POST /api/driving-reports/stop"""
        # Сначала запускаем мониторинг
        self.client.post(
            "/api/driving-reports/start",
            json={"user_id": self.user_id}
        )

        response = self.client.post(
            "/api/driving-reports/stop",
            json={"user_id": self.user_id}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")

    def test_record_event_endpoint(self):
        """Тест POST /api/driving-reports/event"""
        # Запускаем мониторинг
        self.client.post(
            "/api/driving-reports/start",
            json={"user_id": self.user_id}
        )

        response = self.client.post(
            "/api/driving-reports/event",
            json={
                "user_id": self.user_id,
                "event_type": "speed",
                "speed": 65.0
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")

    def test_record_violation_event_endpoint(self):
        """Тест POST /api/driving-reports/event с нарушением"""
        # Запускаем мониторинг
        self.client.post(
            "/api/driving-reports/start",
            json={"user_id": self.user_id}
        )

        response = self.client.post(
            "/api/driving-reports/event",
            json={
                "user_id": self.user_id,
                "event_type": "violation",
                "speed": 80.0,
                "violation_type": "speeding"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")

    def test_record_event_invalid_violation_type(self):
        """Тест POST /api/driving-reports/event с невалидным типом нарушения"""
        self.client.post(
            "/api/driving-reports/start",
            json={"user_id": self.user_id}
        )

        response = self.client.post(
            "/api/driving-reports/event",
            json={
                "user_id": self.user_id,
                "event_type": "violation",
                "violation_type": "invalid_type"
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_generate_report_endpoint(self):
        """Тест POST /api/driving-reports/generate"""
        # Создаем данные для отчета
        self.client.post(
            "/api/driving-reports/start",
            json={"user_id": self.user_id}
        )
        self.client.post(
            "/api/driving-reports/event",
            json={
                "user_id": self.user_id,
                "event_type": "speed",
                "speed": 65.0
            }
        )
        self.client.post(
            "/api/driving-reports/stop",
            json={"user_id": self.user_id}
        )

        response = self.client.post(
            "/api/driving-reports/generate",
            json={
                "user_id": self.user_id,
                "period": "week"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)
        self.assertIn("report_id", data["data"])

    def test_get_weekly_report_endpoint(self):
        """Тест GET /api/driving-reports/weekly/{user_id}"""
        # Создаем данные
        self.client.post(
            "/api/driving-reports/start",
            json={"user_id": self.user_id}
        )
        self.client.post(
            "/api/driving-reports/stop",
            json={"user_id": self.user_id}
        )

        response = self.client.get(f"/api/driving-reports/weekly/{self.user_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")

    def test_get_monthly_report_endpoint(self):
        """Тест GET /api/driving-reports/monthly/{user_id}"""
        # Создаем данные
        self.client.post(
            "/api/driving-reports/start",
            json={"user_id": self.user_id}
        )
        self.client.post(
            "/api/driving-reports/stop",
            json={"user_id": self.user_id}
        )

        response = self.client.get(f"/api/driving-reports/monthly/{self.user_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")

    def test_get_safety_score_endpoint(self):
        """Тест GET /api/driving-reports/safety-score/{user_id}"""
        # Создаем данные
        self.client.post(
            "/api/driving-reports/start",
            json={"user_id": self.user_id}
        )
        self.client.post(
            "/api/driving-reports/stop",
            json={"user_id": self.user_id}
        )

        response = self.client.get(f"/api/driving-reports/safety-score/{self.user_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)
        self.assertIn("score", data["data"])

    def test_get_violations_statistics_endpoint(self):
        """Тест GET /api/driving-reports/violations/{user_id}"""
        # Создаем нарушения
        self.client.post(
            "/api/driving-reports/start",
            json={"user_id": self.user_id}
        )
        self.client.post(
            "/api/driving-reports/event",
            json={
                "user_id": self.user_id,
                "event_type": "violation",
                "violation_type": "speeding"
            }
        )
        self.client.post(
            "/api/driving-reports/stop",
            json={"user_id": self.user_id}
        )

        response = self.client.get(
            f"/api/driving-reports/violations/{self.user_id}",
            params={"period": "week"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)
        self.assertIn("total_violations", data["data"])

    def test_get_recommendations_endpoint(self):
        """Тест GET /api/driving-reports/recommendations/{user_id}"""
        # Создаем данные
        self.client.post(
            "/api/driving-reports/start",
            json={"user_id": self.user_id}
        )
        self.client.post(
            "/api/driving-reports/stop",
            json={"user_id": self.user_id}
        )

        response = self.client.get(f"/api/driving-reports/recommendations/{self.user_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)
        self.assertIn("recommendations", data["data"])

    def test_health_check_endpoint(self):
        """Тест GET /api/driving-reports/health"""
        response = self.client.get("/api/driving-reports/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")

    def test_get_report_by_id_endpoint(self):
        """Тест GET /api/driving-reports/report/{report_id}"""
        # Создаем отчет
        self.client.post(
            "/api/driving-reports/start",
            json={"user_id": self.user_id}
        )
        self.client.post(
            "/api/driving-reports/stop",
            json={"user_id": self.user_id}
        )

        generate_response = self.client.post(
            "/api/driving-reports/generate",
            json={
                "user_id": self.user_id,
                "period": "week"
            }
        )
        report_id = generate_response.json()["data"]["report_id"]

        # Получаем отчет по ID
        response = self.client.get(f"/api/driving-reports/report/{report_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")

    def test_get_report_by_id_not_found(self):
        """Тест GET /api/driving-reports/report/{report_id} с несуществующим ID"""
        response = self.client.get("/api/driving-reports/report/nonexistent_id")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
