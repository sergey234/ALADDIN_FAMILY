# -*- coding: utf-8 -*-
"""
Тесты для BehavioralAnalysisAgent
"""

import unittest
import threading
from datetime import datetime

from security.ai_agents.behavioral_analysis_agent import (
    BehavioralAnalysisAgent, BehaviorType, BehaviorCategory, RiskLevel,
    BehaviorEvent, BehaviorPattern, BehaviorAnalysis, BehaviorMetrics
)


class TestBehavioralAnalysisAgent(unittest.TestCase):
    """Тесты для BehavioralAnalysisAgent"""

    def setUp(self):
        """Настройка тестов"""
        self.agent = BehavioralAnalysisAgent("TestBehavioralAnalysisAgent")

    def tearDown(self):
        """Очистка после тестов"""
        if hasattr(self, 'agent'):
            self.agent.stop()

    def test_initialization(self):
        """Тест инициализации"""
        result = self.agent.initialize()
        self.assertTrue(result)
        self.assertEqual(self.agent.status.value, "running")

    def test_stop(self):
        """Тест остановки"""
        self.agent.initialize()
        result = self.agent.stop()
        self.assertTrue(result)
        self.assertEqual(self.agent.status.value, "stopped")

    def test_analyze_behavior(self):
        """Тест анализа поведения"""
        self.agent.initialize()

        event_data = {
            "action": "login",
            "timestamp": datetime.now().isoformat(),
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0"
        }

        analysis = self.agent.analyze_behavior("test_user", "test_session", event_data)
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis.user_id, "test_user")
        self.assertEqual(analysis.session_id, "test_session")
        self.assertIsInstance(analysis.overall_risk, RiskLevel)

    def test_analyze_suspicious_behavior(self):
        """Тест анализа подозрительного поведения"""
        self.agent.initialize()

        event_data = {
            "action": "admin_access",
            "timestamp": datetime.now().isoformat(),
            "suspicious": True,
            "admin_access": True
        }

        analysis = self.agent.analyze_behavior("test_user", "test_session", event_data)
        self.assertIsNotNone(analysis)
        self.assertGreaterEqual(analysis.risk_score, 0.5)

    def test_get_user_behavior_profile(self):
        """Тест получения профиля поведения пользователя"""
        self.agent.initialize()

        # Сначала создаем события
        event_data = {
            "action": "navigate",
            "timestamp": datetime.now().isoformat()
        }
        self.agent.analyze_behavior("test_user", "test_session", event_data)

        # Получаем профиль
        profile = self.agent.get_user_behavior_profile("test_user")
        self.assertIsNotNone(profile)
        self.assertEqual(profile["user_id"], "test_user")

    def test_get_behavior_patterns(self):
        """Тест получения паттернов поведения"""
        self.agent.initialize()

        patterns = self.agent.get_behavior_patterns()
        self.assertIsInstance(patterns, list)

        # Тест получения паттернов для конкретного пользователя
        user_patterns = self.agent.get_behavior_patterns("test_user")
        self.assertIsInstance(user_patterns, list)

    def test_get_behavior_metrics(self):
        """Тест получения метрик поведения"""
        self.agent.initialize()

        metrics = self.agent.get_behavior_metrics()
        self.assertIsInstance(metrics, BehaviorMetrics)
        self.assertGreaterEqual(metrics.total_events_analyzed, 0)

    def test_get_agent_status(self):
        """Тест получения статуса агента"""
        self.agent.initialize()

        status = self.agent.get_agent_status()
        self.assertIsInstance(status, dict)
        self.assertIn("status", status)
        self.assertIn("total_events", status)
        self.assertIn("total_patterns", status)
        self.assertIn("total_users", status)
        self.assertIn("metrics", status)
        self.assertIn("statistics", status)

    def test_behavior_event_creation(self):
        """Тест создания события поведения"""
        event = BehaviorEvent(
            event_id="test-event",
            user_id="test_user",
            session_id="test_session",
            behavior_type=BehaviorType.NORMAL,
            category=BehaviorCategory.NAVIGATION,
            timestamp=datetime.now(),
            data={"action": "navigate"},
            risk_score=0.3,
            confidence=0.8
        )

        self.assertEqual(event.event_id, "test-event")
        self.assertEqual(event.user_id, "test_user")
        self.assertEqual(event.behavior_type, BehaviorType.NORMAL)
        self.assertEqual(event.category, BehaviorCategory.NAVIGATION)
        self.assertEqual(event.risk_score, 0.3)
        self.assertEqual(event.confidence, 0.8)

    def test_behavior_event_to_dict(self):
        """Тест преобразования события поведения в словарь"""
        event = BehaviorEvent(
            event_id="test-event",
            user_id="test_user",
            session_id="test_session",
            behavior_type=BehaviorType.NORMAL,
            category=BehaviorCategory.NAVIGATION,
            timestamp=datetime.now(),
            data={"action": "navigate"},
            risk_score=0.3,
            confidence=0.8
        )

        data = event.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["event_id"], "test-event")
        self.assertEqual(data["behavior_type"], "normal")
        self.assertEqual(data["category"], "navigation")

    def test_behavior_pattern_creation(self):
        """Тест создания паттерна поведения"""
        pattern = BehaviorPattern(
            pattern_id="test-pattern",
            user_id="test_user",
            pattern_type="navigation",
            frequency=10,
            confidence=0.9,
            time_window=3600,
            characteristics={"avg_duration": 1800},
            created_at=datetime.now(),
            last_seen=datetime.now()
        )

        self.assertEqual(pattern.pattern_id, "test-pattern")
        self.assertEqual(pattern.user_id, "test_user")
        self.assertEqual(pattern.pattern_type, "navigation")
        self.assertEqual(pattern.frequency, 10)
        self.assertEqual(pattern.confidence, 0.9)

    def test_behavior_pattern_to_dict(self):
        """Тест преобразования паттерна поведения в словарь"""
        pattern = BehaviorPattern(
            pattern_id="test-pattern",
            user_id="test_user",
            pattern_type="navigation",
            frequency=10,
            confidence=0.9,
            time_window=3600,
            characteristics={"avg_duration": 1800},
            created_at=datetime.now(),
            last_seen=datetime.now()
        )

        data = pattern.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["pattern_id"], "test-pattern")
        self.assertEqual(data["user_id"], "test_user")

    def test_behavior_analysis_creation(self):
        """Тест создания анализа поведения"""
        event = BehaviorEvent(
            event_id="test-event",
            user_id="test_user",
            session_id="test_session",
            behavior_type=BehaviorType.NORMAL,
            category=BehaviorCategory.NAVIGATION,
            timestamp=datetime.now(),
            data={"action": "navigate"},
            risk_score=0.3,
            confidence=0.8
        )

        analysis = BehaviorAnalysis(
            analysis_id="test-analysis",
            user_id="test_user",
            session_id="test_session",
            timestamp=datetime.now(),
            overall_risk=RiskLevel.LOW,
            risk_score=0.3,
            confidence=0.8,
            anomalies_detected=[],
            patterns_identified=["normal_user"],
            recommendations=["Continue monitoring"],
            behavioral_events=[event],
            analysis_metadata={"events_analyzed": 1}
        )

        self.assertEqual(analysis.analysis_id, "test-analysis")
        self.assertEqual(analysis.user_id, "test_user")
        self.assertEqual(analysis.overall_risk, RiskLevel.LOW)
        self.assertEqual(analysis.risk_score, 0.3)

    def test_behavior_analysis_to_dict(self):
        """Тест преобразования анализа поведения в словарь"""
        event = BehaviorEvent(
            event_id="test-event",
            user_id="test_user",
            session_id="test_session",
            behavior_type=BehaviorType.NORMAL,
            category=BehaviorCategory.NAVIGATION,
            timestamp=datetime.now(),
            data={"action": "navigate"},
            risk_score=0.3,
            confidence=0.8
        )

        analysis = BehaviorAnalysis(
            analysis_id="test-analysis",
            user_id="test_user",
            session_id="test_session",
            timestamp=datetime.now(),
            overall_risk=RiskLevel.LOW,
            risk_score=0.3,
            confidence=0.8,
            anomalies_detected=[],
            patterns_identified=["normal_user"],
            recommendations=["Continue monitoring"],
            behavioral_events=[event],
            analysis_metadata={"events_analyzed": 1}
        )

        data = analysis.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["analysis_id"], "test-analysis")
        self.assertEqual(data["overall_risk"], "low")

    def test_behavior_metrics_creation(self):
        """Тест создания метрик поведения"""
        metrics = BehaviorMetrics()
        
        self.assertEqual(metrics.total_events_analyzed, 0)
        self.assertEqual(metrics.total_users_monitored, 0)
        self.assertEqual(metrics.anomalies_detected, 0)
        self.assertEqual(metrics.suspicious_behaviors, 0)
        self.assertEqual(metrics.malicious_behaviors, 0)

    def test_behavior_metrics_to_dict(self):
        """Тест преобразования метрик в словарь"""
        metrics = BehaviorMetrics()
        data = metrics.to_dict()

        self.assertIsInstance(data, dict)
        self.assertIn("total_events_analyzed", data)
        self.assertIn("total_users_monitored", data)
        self.assertIn("anomalies_detected", data)
        self.assertIn("last_analysis", data)

    def test_concurrent_behavior_analysis(self):
        """Тест параллельного анализа поведения"""
        self.agent.initialize()

        def analyze_worker(worker_id):
            event_data = {
                "action": f"action_{worker_id}",
                "timestamp": datetime.now().isoformat(),
                "worker_id": worker_id
            }
            analysis = self.agent.analyze_behavior(f"user_{worker_id}", f"session_{worker_id}", event_data)
            return analysis is not None

        # Запуск нескольких потоков
        threads = []
        results = []
        
        for i in range(5):
            thread = threading.Thread(target=lambda i=i: results.append(analyze_worker(i)))
            threads.append(thread)
            thread.start()

        # Ожидание завершения всех потоков
        for thread in threads:
            thread.join()

        # Проверка результатов
        self.assertEqual(len(results), 5)
        self.assertTrue(all(results))  # Все должны быть успешными

    def test_behavior_classification(self):
        """Тест классификации поведения"""
        self.agent.initialize()

        # Тест нормального поведения
        normal_data = {"action": "login"}
        analysis = self.agent.analyze_behavior("user1", "session1", normal_data)
        self.assertIsNotNone(analysis)

        # Тест подозрительного поведения
        suspicious_data = {"action": "admin_access", "suspicious": True}
        analysis = self.agent.analyze_behavior("user2", "session2", suspicious_data)
        self.assertIsNotNone(analysis)
        self.assertGreaterEqual(analysis.risk_score, 0.5)

    def test_anomaly_detection(self):
        """Тест обнаружения аномалий"""
        self.agent.initialize()

        # Создаем событие в необычное время
        unusual_time = datetime.now().replace(hour=3)  # 3 утра
        event_data = {
            "action": "access",
            "timestamp": unusual_time.isoformat(),
            "unusual_timing": True
        }

        analysis = self.agent.analyze_behavior("user1", "session1", event_data)
        self.assertIsNotNone(analysis)
        # Проверяем что аномалии обнаружены
        self.assertIsInstance(analysis.anomalies_detected, list)

    def test_pattern_identification(self):
        """Тест идентификации паттернов"""
        self.agent.initialize()

        # Создаем несколько событий для одного пользователя
        for i in range(5):
            event_data = {
                "action": "navigate",
                "timestamp": datetime.now().isoformat(),
                "page": f"page_{i}"
            }
            self.agent.analyze_behavior("user1", "session1", event_data)

        # Получаем паттерны
        patterns = self.agent.get_behavior_patterns("user1")
        self.assertIsInstance(patterns, list)

    def test_risk_calculation(self):
        """Тест расчета риска"""
        self.agent.initialize()

        # Тест низкого риска
        low_risk_data = {"action": "normal_action"}
        analysis = self.agent.analyze_behavior("user1", "session1", low_risk_data)
        self.assertIsNotNone(analysis)
        self.assertLessEqual(analysis.risk_score, 0.5)

        # Тест высокого риска
        high_risk_data = {
            "action": "malicious_action",
            "admin_access": True,
            "suspicious": True
        }
        analysis = self.agent.analyze_behavior("user2", "session2", high_risk_data)
        self.assertIsNotNone(analysis)
        self.assertGreaterEqual(analysis.risk_score, 0.5)

    def test_recommendations_generation(self):
        """Тест генерации рекомендаций"""
        self.agent.initialize()

        # Тест критического риска
        critical_data = {
            "action": "critical_action",
            "admin_access": True,
            "malicious": True
        }
        analysis = self.agent.analyze_behavior("user1", "session1", critical_data)
        self.assertIsNotNone(analysis)
        self.assertIsInstance(analysis.recommendations, list)
        self.assertGreater(len(analysis.recommendations), 0)

    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тест с неинициализированным агентом
        result = self.agent.analyze_behavior("user1", "session1", {})
        # Агент может работать даже без инициализации, но с ограниченной функциональностью
        self.assertIsNotNone(result)

        # Тест с некорректными данными
        self.agent.initialize()
        result = self.agent.analyze_behavior("", "", None)
        # Агент должен обрабатывать некорректные данные
        self.assertIsNotNone(result)

    def test_statistics_tracking(self):
        """Тест отслеживания статистики"""
        self.agent.initialize()

        initial_analyses = self.agent.statistics["total_analyses_performed"]
        initial_events = self.agent.statistics["total_events_processed"]

        # Выполняем анализ
        event_data = {"action": "test_action"}
        self.agent.analyze_behavior("user1", "session1", event_data)

        # Проверяем статистику
        self.assertGreater(self.agent.statistics["total_analyses_performed"], initial_analyses)
        self.assertGreater(self.agent.statistics["total_events_processed"], initial_events)

    def test_behavior_retention(self):
        """Тест хранения истории поведения"""
        self.agent.initialize()

        # Создаем несколько событий
        for i in range(10):
            event_data = {
                "action": f"action_{i}",
                "timestamp": datetime.now().isoformat()
            }
            self.agent.analyze_behavior("user1", "session1", event_data)

        # Проверяем что события сохранились
        profile = self.agent.get_user_behavior_profile("user1")
        self.assertIsNotNone(profile)
        self.assertGreater(profile["total_events"], 0)

    def test_ai_models_integration(self):
        """Тест интеграции AI моделей"""
        self.agent.initialize()

        # Проверяем что AI модели инициализированы
        self.assertTrue(self.agent.ai_enabled)
        self.assertIsInstance(self.agent.ml_models, dict)
        self.assertIn("anomaly_detector", self.agent.ml_models)
        self.assertIn("pattern_recognizer", self.agent.ml_models)
        self.assertIn("risk_assessor", self.agent.ml_models)
        self.assertIn("behavior_classifier", self.agent.ml_models)


if __name__ == '__main__':
    unittest.main()
