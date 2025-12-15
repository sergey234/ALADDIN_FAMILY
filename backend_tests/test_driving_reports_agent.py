#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit-тесты для Driving Reports Agent

Дата создания: 12 декабря 2025
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import time

# Импорт агента
try:
    from security.ai_agents.driving_reports_agent import (
        DrivingReportsAgent,
        DrivingEvent,
        DrivingViolation,
        SafetyScore,
        SafetyRating
    )
except ImportError:
    # Для локальной разработки
    DrivingReportsAgent = None
    DrivingEvent = None
    DrivingViolation = None
    SafetyScore = None
    SafetyRating = None


@unittest.skipIf(DrivingReportsAgent is None, "DrivingReportsAgent не доступен")
class TestDrivingReportsAgent(unittest.TestCase):
    """Тесты для DrivingReportsAgent"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.config = {
            "speed_limit": 60.0,
            "hard_braking_threshold": 0.4,
            "hard_acceleration_threshold": 0.4,
            "sharp_turn_threshold": 0.5,
            "notify_parents": True
        }
        self.agent = DrivingReportsAgent(config=self.config)
        self.user_id = "test_user_123"

    def test_agent_initialization(self):
        """Тест инициализации агента"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.speed_limit, 60.0)
        self.assertEqual(self.agent.hard_braking_threshold, 0.4)
        self.assertTrue(self.agent.notify_parents)

    def test_start_monitoring(self):
        """Тест запуска мониторинга"""
        result = self.agent.start_monitoring(self.user_id)
        self.assertEqual(result["status"], "success")
        self.assertIn(self.user_id, self.agent.active_monitoring)
        self.assertEqual(self.agent.active_monitoring[self.user_id]["status"], "active")

    def test_start_monitoring_already_active(self):
        """Тест запуска мониторинга когда уже активен"""
        self.agent.start_monitoring(self.user_id)
        result = self.agent.start_monitoring(self.user_id)
        self.assertIn("error", result)

    def test_stop_monitoring(self):
        """Тест остановки мониторинга"""
        self.agent.start_monitoring(self.user_id)
        time.sleep(0.1)  # Небольшая задержка для расчета времени
        result = self.agent.stop_monitoring(self.user_id)
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.agent.active_monitoring[self.user_id]["status"], "stopped")

    def test_stop_monitoring_not_started(self):
        """Тест остановки мониторинга когда не запущен"""
        result = self.agent.stop_monitoring(self.user_id)
        self.assertIn("error", result)

    def test_record_driving_event(self):
        """Тест записи события вождения"""
        self.agent.start_monitoring(self.user_id)
        result = self.agent.record_driving_event(
            user_id=self.user_id,
            event_type="speed",
            speed=65.0
        )
        self.assertEqual(result["status"], "success")
        self.assertIn("event_id", result)
        self.assertEqual(len(self.agent.driving_events[self.user_id]), 2)  # start + speed

    def test_record_violation_event(self):
        """Тест записи события нарушения"""
        self.agent.start_monitoring(self.user_id)
        result = self.agent.record_driving_event(
            user_id=self.user_id,
            event_type="violation",
            speed=80.0,
            violation_type=DrivingViolation.SPEEDING
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(self.agent.violations[self.user_id]), 1)

    def test_generate_report_week(self):
        """Тест генерации недельного отчета"""
        self.agent.start_monitoring(self.user_id)
        self.agent.record_driving_event(
            user_id=self.user_id,
            event_type="speed",
            speed=65.0
        )
        self.agent.record_driving_event(
            user_id=self.user_id,
            event_type="violation",
            speed=80.0,
            violation_type=DrivingViolation.SPEEDING
        )
        self.agent.stop_monitoring(self.user_id)

        result = self.agent.generate_report(
            user_id=self.user_id,
            period="week"
        )
        self.assertEqual(result["status"], "success")
        self.assertIn("report_id", result)
        self.assertIn("report", result)
        report = result["report"]
        self.assertIn("total_violations", report)
        self.assertIn("safety_score", report)

    def test_generate_report_no_data(self):
        """Тест генерации отчета без данных"""
        result = self.agent.generate_report(
            user_id="nonexistent_user",
            period="week"
        )
        self.assertIn("error", result)

    def test_calculate_safety_score_no_violations(self):
        """Тест расчета оценки безопасности без нарушений"""
        self.agent.start_monitoring(self.user_id)
        self.agent.stop_monitoring(self.user_id)

        score = self.agent.calculate_safety_score(self.user_id)
        self.assertIsNotNone(score)
        self.assertEqual(score.score, 100)
        self.assertEqual(score.rating, SafetyRating.EXCELLENT)

    def test_calculate_safety_score_with_violations(self):
        """Тест расчета оценки безопасности с нарушениями"""
        self.agent.start_monitoring(self.user_id)
        # Добавляем несколько нарушений
        for _ in range(3):
            self.agent.record_driving_event(
                user_id=self.user_id,
                event_type="violation",
                speed=80.0,
                violation_type=DrivingViolation.SPEEDING
            )
        self.agent.stop_monitoring(self.user_id)

        score = self.agent.calculate_safety_score(self.user_id)
        self.assertIsNotNone(score)
        self.assertLess(score.score, 100)  # Должен быть меньше 100 из-за нарушений
        self.assertGreaterEqual(score.score, 0)

    def test_get_violations_statistics(self):
        """Тест получения статистики нарушений"""
        self.agent.start_monitoring(self.user_id)
        # Добавляем нарушения разных типов
        self.agent.record_driving_event(
            user_id=self.user_id,
            event_type="violation",
            violation_type=DrivingViolation.SPEEDING
        )
        self.agent.record_driving_event(
            user_id=self.user_id,
            event_type="violation",
            violation_type=DrivingViolation.PHONE_USE
        )
        self.agent.stop_monitoring(self.user_id)

        stats = self.agent.get_violations_statistics(self.user_id, period="week")
        self.assertNotIn("error", stats)
        self.assertEqual(stats["total_violations"], 2)
        self.assertIn("violations_by_type", stats)
        self.assertIn("speeding", stats["violations_by_type"])
        self.assertIn("phone_use", stats["violations_by_type"])

    def test_get_recommendations_no_violations(self):
        """Тест получения рекомендаций без нарушений"""
        self.agent.start_monitoring(self.user_id)
        self.agent.stop_monitoring(self.user_id)

        recommendations = self.agent.get_recommendations(self.user_id)
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

    def test_get_recommendations_with_violations(self):
        """Тест получения рекомендаций с нарушениями"""
        self.agent.start_monitoring(self.user_id)
        # Добавляем нарушения
        for _ in range(5):
            self.agent.record_driving_event(
                user_id=self.user_id,
                event_type="violation",
                violation_type=DrivingViolation.SPEEDING
            )
        self.agent.stop_monitoring(self.user_id)

        recommendations = self.agent.get_recommendations(self.user_id)
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        # Должна быть рекомендация о превышении скорости
        self.assertTrue(any("скорост" in rec.lower() for rec in recommendations))

    def test_collect_threats(self):
        """Тест сбора угроз"""
        self.agent.start_monitoring(self.user_id)
        self.agent.record_driving_event(
            user_id=self.user_id,
            event_type="violation",
            violation_type=DrivingViolation.SPEEDING
        )
        self.agent.stop_monitoring(self.user_id)

        threats = self.agent.collect_threats()
        self.assertIsInstance(threats, list)
        self.assertGreater(len(threats), 0)

    def test_analyze_threats(self):
        """Тест анализа угроз"""
        self.agent.start_monitoring(self.user_id)
        # Добавляем много нарушений за короткий период
        for _ in range(6):
            self.agent.record_driving_event(
                user_id=self.user_id,
                event_type="violation",
                violation_type=DrivingViolation.SPEEDING
            )
        self.agent.stop_monitoring(self.user_id)

        threats = self.agent.collect_threats()
        analyzed = self.agent.analyze_threats(threats)
        self.assertIsInstance(analyzed, list)
        # Проверяем, что некоторые угрозы получили повышенную серьезность
        high_severity = [t for t in analyzed if t.severity == "high"]
        self.assertGreater(len(high_severity), 0)

    def test_send_alert(self):
        """Тест отправки уведомления"""
        alert = {
            "user_id": self.user_id,
            "violation_type": "speeding"
        }
        result = self.agent.send_alert(alert)
        self.assertTrue(result)

    def test_multiple_users(self):
        """Тест работы с несколькими пользователями"""
        user1 = "user1"
        user2 = "user2"

        self.agent.start_monitoring(user1)
        self.agent.start_monitoring(user2)

        self.agent.record_driving_event(
            user_id=user1,
            event_type="violation",
            violation_type=DrivingViolation.SPEEDING
        )
        self.agent.record_driving_event(
            user_id=user2,
            event_type="violation",
            violation_type=DrivingViolation.PHONE_USE
        )

        # Проверяем, что данные разделены по пользователям
        self.assertEqual(len(self.agent.violations[user1]), 1)
        self.assertEqual(len(self.agent.violations[user2]), 1)
        self.assertNotEqual(
            self.agent.violations[user1][0].violation_type,
            self.agent.violations[user2][0].violation_type
        )


if __name__ == "__main__":
    unittest.main()
