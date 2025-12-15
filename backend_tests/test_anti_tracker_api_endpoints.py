#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Интеграционные тесты для Anti-Tracker API endpoints

Дата создания: 12 декабря 2025
"""

import unittest
from fastapi.testclient import TestClient

# Импорт router
try:
    from security.api.routers.anti_tracker_router import router
    from fastapi import FastAPI
except ImportError:
    router = None
    FastAPI = None


@unittest.skipIf(router is None, "Anti-Tracker Router не доступен")
class TestAntiTrackerAPIEndpoints(unittest.TestCase):
    """Тесты для API endpoints Anti-Tracker Agent"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
        if FastAPI is None:
            self.skipTest("FastAPI не доступен")

        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)

    def test_check_endpoint_analytics_tracker(self):
        """Тест POST /api/anti-tracker/check с аналитическим трекером"""
        response = self.client.post(
            "/api/anti-tracker/check",
            json={"url": "https://google-analytics.com/collect"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["data"]["blocked"])
        self.assertEqual(data["data"]["tracker_type"], "analytics")

    def test_check_endpoint_social_tracker(self):
        """Тест POST /api/anti-tracker/check с социальным трекером"""
        response = self.client.post(
            "/api/anti-tracker/check",
            json={"url": "https://vk.com/rtrg"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["data"]["blocked"])
        self.assertEqual(data["data"]["tracker_type"], "social")

    def test_check_endpoint_safe_url(self):
        """Тест POST /api/anti-tracker/check с безопасным URL"""
        response = self.client.post(
            "/api/anti-tracker/check",
            json={"url": "https://example.com/page"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertFalse(data["data"]["blocked"])

    def test_check_endpoint_invalid_request(self):
        """Тест POST /api/anti-tracker/check с невалидными данными"""
        response = self.client.post(
            "/api/anti-tracker/check",
            json={}  # Отсутствует url
        )
        self.assertEqual(response.status_code, 422)  # Validation error

    def test_stats_endpoint(self):
        """Тест GET /api/anti-tracker/stats"""
        # Сначала делаем несколько проверок для статистики
        self.client.post(
            "/api/anti-tracker/check",
            json={"url": "https://google-analytics.com/collect"}
        )

        response = self.client.get("/api/anti-tracker/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("total_blocked", data["data"])
        self.assertIn("blocked_by_type", data["data"])

    def test_trackers_endpoint(self):
        """Тест GET /api/anti-tracker/trackers"""
        response = self.client.get("/api/anti-tracker/trackers")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("analytics", data["data"])
        self.assertIn("advertising", data["data"])
        self.assertIn("social", data["data"])
        self.assertIn("patterns", data["data"])
        self.assertIn("all", data["data"])

        # Проверяем наличие известных трекеров
        self.assertIn("google-analytics.com", data["data"]["analytics"])
        self.assertIn("vk.com/rtrg", data["data"]["social"])
        self.assertIn("ok.ru/js/sdk", data["data"]["social"])
        self.assertIn("max.ru/pixel", data["data"]["social"])

    def test_block_endpoint(self):
        """Тест POST /api/anti-tracker/block"""
        response = self.client.post(
            "/api/anti-tracker/block",
            json={
                "domain": "test-tracker.com",
                "tracker_type": "analytics",
                "reason": "Test block"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("message", data)

    def test_block_endpoint_invalid_tracker_type(self):
        """Тест POST /api/anti-tracker/block с невалидным типом трекера"""
        response = self.client.post(
            "/api/anti-tracker/block",
            json={
                "domain": "test-tracker.com",
                "tracker_type": "invalid_type"
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_unblock_endpoint(self):
        """Тест POST /api/anti-tracker/unblock"""
        # Сначала блокируем
        self.client.post(
            "/api/anti-tracker/block",
            json={
                "domain": "test-tracker.com",
                "tracker_type": "analytics"
            }
        )

        # Затем разблокируем
        response = self.client.post(
            "/api/anti-tracker/unblock",
            json={"domain": "test-tracker.com"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")

    def test_status_endpoint_blocked(self):
        """Тест GET /api/anti-tracker/status для заблокированного домена"""
        # Сначала блокируем
        self.client.post(
            "/api/anti-tracker/block",
            json={
                "domain": "blocked.com",
                "tracker_type": "advertising"
            }
        )

        response = self.client.get("/api/anti-tracker/status?domain=blocked.com")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["data"]["blocked"])

    def test_status_endpoint_not_blocked(self):
        """Тест GET /api/anti-tracker/status для незаблокированного домена"""
        response = self.client.get("/api/anti-tracker/status?domain=safe.com")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertFalse(data["data"]["blocked"])

    def test_get_settings_endpoint(self):
        """Тест GET /api/anti-tracker/settings"""
        response = self.client.get("/api/anti-tracker/settings")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("strict_mode", data["data"])
        self.assertIn("enable_analytics_blocking", data["data"])
        self.assertIn("enable_advertising_blocking", data["data"])
        self.assertIn("enable_social_blocking", data["data"])

    def test_update_settings_endpoint(self):
        """Тест POST /api/anti-tracker/settings"""
        response = self.client.post(
            "/api/anti-tracker/settings",
            json={
                "strict_mode": False,
                "enable_analytics_blocking": True
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")

        # Проверяем, что настройки обновились
        get_response = self.client.get("/api/anti-tracker/settings")
        settings = get_response.json()["data"]
        self.assertFalse(settings["strict_mode"])

    def test_health_endpoint(self):
        """Тест GET /api/anti-tracker/health"""
        response = self.client.get("/api/anti-tracker/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["agent_initialized"])
        self.assertGreater(data["trackers_count"], 0)

    def test_check_endpoint_with_headers(self):
        """Тест POST /api/anti-tracker/check с заголовками"""
        response = self.client.post(
            "/api/anti-tracker/check",
            json={
                "url": "https://google-analytics.com/collect",
                "headers": {
                    "User-Agent": "Mozilla/5.0",
                    "Referer": "https://example.com"
                }
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")

    def test_check_endpoint_with_user_id(self):
        """Тест POST /api/anti-tracker/check с user_id"""
        response = self.client.post(
            "/api/anti-tracker/check",
            json={
                "url": "https://vk.com/rtrg",
                "user_id": "test_user_123"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["data"]["blocked"])

    def test_multiple_checks_statistics(self):
        """Тест множественных проверок и статистики"""
        urls = [
            "https://google-analytics.com/collect",
            "https://vk.com/rtrg",
            "https://yandex.ru/ads",
            "https://example.com/safe"
        ]

        for url in urls:
            self.client.post(
                "/api/anti-tracker/check",
                json={"url": url}
            )

        response = self.client.get("/api/anti-tracker/stats")
        stats = response.json()["data"]
        self.assertGreaterEqual(stats["total_blocked"], 3)


if __name__ == "__main__":
    unittest.main()
