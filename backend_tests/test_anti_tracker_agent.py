#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit-тесты для Anti-Tracker Agent

Дата создания: 12 декабря 2025
"""

import unittest
from unittest.mock import Mock, patch
import time

# Импорт агента
try:
    from security.ai_agents.anti_tracker_agent import (
        AntiTrackerAgent,
        TrackerType,
        BlockedRequest
    )
except ImportError:
    # Для локальной разработки
    AntiTrackerAgent = None
    TrackerType = None
    BlockedRequest = None


@unittest.skipIf(AntiTrackerAgent is None, "AntiTrackerAgent не доступен")
class TestAntiTrackerAgent(unittest.TestCase):
    """Тесты для AntiTrackerAgent"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.config = {
            "strict_mode": True,
            "enable_analytics_blocking": True,
            "enable_advertising_blocking": True,
            "enable_social_blocking": True,
            "whitelist": [],
            "blacklist": []
        }
        self.agent = AntiTrackerAgent(config=self.config)

    def test_agent_initialization(self):
        """Тест инициализации агента"""
        self.assertIsNotNone(self.agent)
        self.assertTrue(self.agent.strict_mode)
        self.assertTrue(self.agent.enable_analytics_blocking)
        self.assertTrue(self.agent.enable_advertising_blocking)
        self.assertTrue(self.agent.enable_social_blocking)
        self.assertIsInstance(self.agent.whitelist, set)
        self.assertIsInstance(self.agent.blacklist, set)

    def test_check_request_analytics_tracker(self):
        """Тест проверки запроса с аналитическим трекером"""
        url = "https://google-analytics.com/collect"
        result = self.agent.check_request(url)

        self.assertTrue(result["blocked"])
        self.assertEqual(result["tracker_type"], "analytics")
        self.assertIn("reason", result)

    def test_check_request_advertising_tracker(self):
        """Тест проверки запроса с рекламным трекером"""
        url = "https://googleadservices.com/pagead"
        result = self.agent.check_request(url)

        self.assertTrue(result["blocked"])
        self.assertEqual(result["tracker_type"], "advertising")
        self.assertIn("reason", result)

    def test_check_request_social_tracker(self):
        """Тест проверки запроса с социальным трекером"""
        url = "https://vk.com/rtrg"
        result = self.agent.check_request(url)

        self.assertTrue(result["blocked"])
        self.assertEqual(result["tracker_type"], "social")
        self.assertIn("reason", result)

    def test_check_request_yandex_metrica(self):
        """Тест проверки запроса с Yandex Metrica"""
        url = "https://mc.yandex.ru/watch"
        result = self.agent.check_request(url)

        self.assertTrue(result["blocked"])
        self.assertEqual(result["tracker_type"], "analytics")

    def test_check_request_vk_pixel(self):
        """Тест проверки запроса с VK Pixel"""
        url = "https://vk.com/rtrg?id=123"
        result = self.agent.check_request(url)

        self.assertTrue(result["blocked"])
        self.assertEqual(result["tracker_type"], "social")

    def test_check_request_ok_pixel(self):
        """Тест проверки запроса с Одноклассники Pixel"""
        url = "https://ok.ru/js/sdk"
        result = self.agent.check_request(url)

        self.assertTrue(result["blocked"])
        self.assertEqual(result["tracker_type"], "social")

    def test_check_request_max_pixel(self):
        """Тест проверки запроса с MAX Pixel"""
        url = "https://max.ru/pixel"
        result = self.agent.check_request(url)

        self.assertTrue(result["blocked"])
        self.assertEqual(result["tracker_type"], "social")

    def test_check_request_pattern_tracker(self):
        """Тест проверки запроса с паттерном трекера"""
        url = "https://example.com/api/analytics/track"
        result = self.agent.check_request(url)

        self.assertTrue(result["blocked"])
        self.assertEqual(result["tracker_type"], "pattern")

    def test_check_request_safe_url(self):
        """Тест проверки безопасного URL"""
        url = "https://example.com/page"
        result = self.agent.check_request(url)

        self.assertFalse(result["blocked"])

    def test_check_request_whitelisted(self):
        """Тест проверки URL из белого списка"""
        self.agent.whitelist.add("example.com")
        url = "https://example.com/tracker"
        result = self.agent.check_request(url)

        self.assertFalse(result["blocked"])
        self.assertEqual(result.get("reason"), "Whitelisted domain")

    def test_check_request_blacklisted(self):
        """Тест проверки URL из черного списка"""
        self.agent.blacklist.add("malicious.com")
        url = "https://malicious.com/page"
        result = self.agent.check_request(url)

        self.assertTrue(result["blocked"])
        self.assertEqual(result["tracker_type"], "blacklist")

    def test_is_tracker_domain_analytics(self):
        """Тест проверки домена аналитики"""
        tracker_type = self.agent.is_tracker_domain("google-analytics.com")
        self.assertEqual(tracker_type, TrackerType.ANALYTICS)

    def test_is_tracker_domain_advertising(self):
        """Тест проверки домена рекламы"""
        tracker_type = self.agent.is_tracker_domain("googleadservices.com")
        self.assertEqual(tracker_type, TrackerType.ADVERTISING)

    def test_is_tracker_domain_social(self):
        """Тест проверки домена социального трекера"""
        tracker_type = self.agent.is_tracker_domain("vk.com/rtrg")
        self.assertEqual(tracker_type, TrackerType.SOCIAL)

    def test_is_tracker_domain_safe(self):
        """Тест проверки безопасного домена"""
        tracker_type = self.agent.is_tracker_domain("example.com")
        self.assertIsNone(tracker_type)

    def test_matches_tracker_pattern(self):
        """Тест проверки паттерна трекера"""
        url = "https://example.com/api/track"
        result = self.agent.matches_tracker_pattern(url)
        self.assertTrue(result)

    def test_matches_tracker_pattern_analytics(self):
        """Тест проверки паттерна аналитики"""
        url = "https://example.com/analytics/collect"
        result = self.agent.matches_tracker_pattern(url)
        self.assertTrue(result)

    def test_matches_tracker_pattern_pixel(self):
        """Тест проверки паттерна пикселя"""
        url = "https://example.com/pixel/track"
        result = self.agent.matches_tracker_pattern(url)
        self.assertTrue(result)

    def test_matches_tracker_pattern_safe(self):
        """Тест проверки безопасного URL"""
        url = "https://example.com/page"
        result = self.agent.matches_tracker_pattern(url)
        self.assertFalse(result)

    def test_block_tracker(self):
        """Тест блокировки трекера"""
        result = self.agent.block_tracker(
            domain="test-tracker.com",
            tracker_type=TrackerType.ANALYTICS,
            reason="Test block"
        )

        self.assertTrue(result)
        self.assertTrue(self.agent.is_blocked("test-tracker.com"))
        self.assertIn("test-tracker.com", self.agent.blocked_trackers)

    def test_unblock_tracker(self):
        """Тест разблокировки трекера"""
        # Сначала блокируем
        self.agent.block_tracker(
            domain="test-tracker.com",
            tracker_type=TrackerType.ANALYTICS
        )

        # Затем разблокируем
        result = self.agent.unblock_tracker("test-tracker.com")

        self.assertTrue(result)
        self.assertFalse(self.agent.is_blocked("test-tracker.com"))
        self.assertNotIn("test-tracker.com", self.agent.blocked_trackers)

    def test_is_blocked(self):
        """Тест проверки блокировки домена"""
        self.agent.block_tracker(
            domain="blocked.com",
            tracker_type=TrackerType.ADVERTISING
        )

        self.assertTrue(self.agent.is_blocked("blocked.com"))
        self.assertFalse(self.agent.is_blocked("not-blocked.com"))

    def test_record_blocked_request(self):
        """Тест записи заблокированного запроса"""
        initial_count = self.agent.stats.total_blocked

        self.agent.record_blocked_request(
            url="https://tracker.com/collect",
            tracker_type=TrackerType.ANALYTICS,
            user_id="test_user",
            reason="Test"
        )

        self.assertEqual(self.agent.stats.total_blocked, initial_count + 1)
        self.assertEqual(len(self.agent.blocked_requests), 1)
        self.assertEqual(self.agent.blocked_requests[0].tracker_type, TrackerType.ANALYTICS)

    def test_get_statistics(self):
        """Тест получения статистики"""
        # Записываем несколько блокировок
        self.agent.record_blocked_request(
            url="https://tracker1.com",
            tracker_type=TrackerType.ANALYTICS
        )
        self.agent.record_blocked_request(
            url="https://tracker2.com",
            tracker_type=TrackerType.ADVERTISING
        )

        stats = self.agent.get_statistics()

        self.assertGreater(stats["total_blocked"], 0)
        self.assertIn("blocked_by_type", stats)
        self.assertIn("top_blocked_domains", stats)
        self.assertIn("analytics", stats["blocked_by_type"])

    def test_get_tracker_lists(self):
        """Тест получения списков трекеров"""
        lists = self.agent.get_tracker_lists()

        self.assertIn("analytics", lists)
        self.assertIn("advertising", lists)
        self.assertIn("social", lists)
        self.assertIn("patterns", lists)
        self.assertIn("all", lists)

        # Проверяем наличие известных трекеров
        self.assertIn("google-analytics.com", lists["analytics"])
        self.assertIn("mc.yandex.ru", lists["analytics"])
        self.assertIn("vk.com/rtrg", lists["social"])
        self.assertIn("ok.ru/js/sdk", lists["social"])
        self.assertIn("max.ru/pixel", lists["social"])

    def test_collect_threats(self):
        """Тест сбора угроз"""
        # Записываем несколько блокировок
        self.agent.record_blocked_request(
            url="https://tracker.com",
            tracker_type=TrackerType.ANALYTICS
        )

        threats = self.agent.collect_threats()

        self.assertIsInstance(threats, list)
        if len(threats) > 0:
            self.assertEqual(threats[0].threat_type, "tracker")

    def test_analyze_threats(self):
        """Тест анализа угроз"""
        # Создаем тестовые угрозы
        from security.ai_agents.threat_monitoring_interface import ThreatEvent
        from datetime import datetime

        threats = [
            ThreatEvent(
                event_id="test1",
                agent_name="AntiTrackerAgent",
                threat_type="tracker",
                severity="low",
                source="tracker.com",
                target="https://tracker.com",
                timestamp=datetime.now().isoformat(),
                metadata={"tracker_type": "analytics"}
            )
        ]

        result = self.agent.analyze_threats(threats)

        self.assertEqual(result["status"], "analyzed")
        self.assertEqual(result["total_threats"], 1)
        self.assertIn("by_type", result)

    def test_send_alert(self):
        """Тест отправки уведомления"""
        from security.ai_agents.threat_monitoring_interface import ThreatEvent
        from datetime import datetime

        threat = ThreatEvent(
            event_id="test1",
            agent_name="AntiTrackerAgent",
            threat_type="tracker",
            severity="low",
            source="tracker.com",
            target="https://tracker.com",
            timestamp=datetime.now().isoformat(),
            metadata={},
            description="Test threat"
        )

        result = self.agent.send_alert(threat)

        self.assertTrue(result)

    def test_extract_domain(self):
        """Тест извлечения домена из URL"""
        domain = self.agent._extract_domain("https://example.com/path?query=1")
        self.assertEqual(domain, "example.com")

    def test_extract_domain_with_port(self):
        """Тест извлечения домена с портом"""
        domain = self.agent._extract_domain("https://example.com:8080/path")
        self.assertEqual(domain, "example.com")

    def test_multiple_blocked_requests(self):
        """Тест множественных блокировок"""
        urls = [
            "https://google-analytics.com/collect",
            "https://vk.com/rtrg",
            "https://yandex.ru/ads"
        ]

        for url in urls:
            result = self.agent.check_request(url)
            self.assertTrue(result["blocked"])

        stats = self.agent.get_statistics()
        self.assertGreaterEqual(stats["total_blocked"], 3)


if __name__ == "__main__":
    unittest.main()
