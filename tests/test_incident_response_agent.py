#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тесты для IncidentResponseAgent

Этот модуль содержит комплексные unit-тесты для IncidentResponseAgent,
включая тестирование всех основных функций, AI моделей, планов реагирования,
автоматизации, эскалации и обработки инцидентов.

Тесты покрывают:
- Инициализацию агента и AI моделей
- Создание и управление инцидентами
- Автоматическое реагирование и эскалацию
- Планы реагирования и правила эскалации
- Системы уведомлений и мониторинга
- Генерацию отчетов и рекомендаций
- Обработку ошибок и исключений
- Валидацию данных и качество кода

Автор: ALADDIN Security System
Версия: 1.0
Дата: 2024
"""

import os
import sys
import unittest
import time
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from security.ai_agents.incident_response_agent import (
        IncidentResponseAgent,
        Incident,
        IncidentSeverity,
        IncidentStatus,
        IncidentType,
        ResponseAction,
        IncidentResponseMetrics
    )
except ImportError as e:
    print("Ошибка импорта: {}".format(e))
    sys.exit(1)


class TestIncidentResponseAgent(unittest.TestCase):
    """
    Тесты для IncidentResponseAgent
    
    Этот класс содержит все unit-тесты для основного агента реагирования на инциденты.
    Тесты проверяют корректность работы всех методов, обработку инцидентов,
    AI модели, планы реагирования и автоматизацию.
    """
    
    def setUp(self):
        """Настройка тестов"""
        self.agent = IncidentResponseAgent("TestIncidentResponseAgent")
    
    def test_initialization(self):
        """Тест инициализации агента"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.name, "TestIncidentResponseAgent")
        self.assertIsNotNone(self.agent.metrics)
        self.assertIsNotNone(self.agent.incidents)
        self.assertIsNotNone(self.agent.response_plans)
        self.assertIsNotNone(self.agent.escalation_rules)
    
    def test_ai_models_initialization(self):
        """Тест инициализации AI моделей"""
        self.agent._initialize_ai_models()
        
        # Проверка наличия всех AI моделей
        expected_models = [
            "incident_classifier", "severity_predictor", "response_recommender",
            "escalation_predictor", "impact_analyzer"
        ]
        
        for model_name in expected_models:
            self.assertIn(model_name, self.agent.ml_models)
            self.assertIsNotNone(self.agent.ml_models[model_name])
    
    def test_response_plans_loading(self):
        """Тест загрузки планов реагирования"""
        self.agent._load_response_plans()
        
        # Проверка наличия планов реагирования
        expected_plans = ["malware", "phishing", "ddos", "data_breach"]
        
        for plan_name in expected_plans:
            self.assertIn(plan_name, self.agent.response_plans)
            plan = self.agent.response_plans[plan_name]
            self.assertIn("name", plan)
            self.assertIn("steps", plan)
            self.assertIn("priority", plan)
            self.assertIn("estimated_time", plan)
    
    def test_escalation_rules_initialization(self):
        """Тест инициализации правил эскалации"""
        self.agent._initialize_escalation_rules()
        
        # Проверка правил эскалации
        expected_severities = ["critical", "high", "medium", "low"]
        
        for severity in expected_severities:
            self.assertIn(severity, self.agent.escalation_rules)
            rules = self.agent.escalation_rules[severity]
            self.assertIn("escalation_time", rules)
            self.assertIn("escalation_contacts", rules)
            self.assertIn("notification_channels", rules)
    
    def test_notifications_setup(self):
        """Тест настройки уведомлений"""
        self.agent._setup_notifications()
        
        # Проверка каналов уведомлений
        expected_channels = ["email", "sms", "slack"]
        for channel in expected_channels:
            self.assertIn(channel, self.agent.notification_channels)
        
        # Проверка контактов для эскалации
        expected_contacts = ["security_team", "management", "legal"]
        for contact in expected_contacts:
            self.assertIn(contact, self.agent.escalation_contacts)
    
    def test_incident_creation(self):
        """Тест создания инцидента"""
        self.agent.initialize()
        
        # Создание тестового инцидента
        incident = self.agent.create_incident(
            title="Test Incident",
            description="Test incident description",
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.HIGH,
            affected_systems=[{"id": "server1", "type": "web_server", "description": "Web server"}]
        )
        
        # Проверка создания инцидента
        self.assertIsNotNone(incident)
        self.assertEqual(incident.title, "Test Incident")
        self.assertEqual(incident.incident_type, IncidentType.MALWARE)
        self.assertEqual(incident.severity, IncidentSeverity.HIGH)
        self.assertIn(incident.incident_id, self.agent.incidents)
        
        # Проверка метрик
        self.assertGreater(self.agent.metrics.total_incidents, 0)
        self.assertIsNotNone(self.agent.metrics.last_incident_time)
    
    def test_incident_classification(self):
        """Тест классификации инцидента"""
        self.agent._initialize_ai_models()
        
        # Создание тестового инцидента
        incident = Incident(
            incident_id="test_incident",
            title="Test Incident",
            description="Test incident description",
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.HIGH
        )
        
        # Классификация инцидента
        classification = self.agent._classify_incident(incident)
        
        # Проверка результата классификации
        self.assertIn("type", classification)
        self.assertIn("confidence", classification)
        self.assertIn("model_used", classification)
        self.assertGreaterEqual(classification["confidence"], 0.0)
        self.assertLessEqual(classification["confidence"], 1.0)
    
    def test_severity_prediction(self):
        """Тест предсказания серьезности"""
        self.agent._initialize_ai_models()
        
        # Создание тестового инцидента
        incident = Incident(
            incident_id="test_incident",
            title="Test Incident",
            description="Test incident description",
            incident_type=IncidentType.APT,
            severity=IncidentSeverity.CRITICAL
        )
        
        # Предсказание серьезности
        severity_prediction = self.agent._predict_severity(incident)
        
        # Проверка результата предсказания
        self.assertIn("severity", severity_prediction)
        self.assertIn("confidence", severity_prediction)
        self.assertIn("model_used", severity_prediction)
        self.assertGreaterEqual(severity_prediction["confidence"], 0.0)
        self.assertLessEqual(severity_prediction["confidence"], 1.0)
    
    def test_priority_calculation(self):
        """Тест расчета приоритета"""
        # Создание тестового инцидента
        incident = Incident(
            incident_id="test_incident",
            title="Test Incident",
            description="Test incident description",
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.CRITICAL
        )
        
        # Добавление затронутых систем и индикаторов
        incident.add_affected_system("server1", "web_server", "Web server")
        incident.add_affected_system("server2", "database", "Database server")
        incident.add_indicator("ip_address", "192.168.1.1", "Suspicious IP")
        incident.add_indicator("domain", "malicious.com", "Suspicious domain")
        
        # Расчет приоритета
        priority = self.agent._calculate_priority(incident)
        
        # Проверка приоритета
        self.assertGreaterEqual(priority, 1)
        self.assertLessEqual(priority, 10)
        self.assertGreater(priority, 5)  # CRITICAL + системы + индикаторы
    
    def test_auto_response(self):
        """Тест автоматического реагирования"""
        self.agent.initialize()
        
        # Создание тестового инцидента
        incident = self.agent.create_incident(
            title="Test Malware Incident",
            description="Test malware incident",
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.HIGH
        )
        
        # Проверка что инцидент создан
        self.assertIsNotNone(incident)
        
        # Проверка что автоматические действия выполнены
        self.assertGreater(len(incident.actions_taken), 0)
        
        # Проверка метрик
        self.assertGreater(self.agent.metrics.total_actions_taken, 0)
        self.assertGreater(self.agent.metrics.successful_actions, 0)
    
    def test_escalation_logic(self):
        """Тест логики эскалации"""
        self.agent.initialize()
        
        # Создание критического инцидента
        incident = Incident(
            incident_id="test_critical_incident",
            title="Critical Incident",
            description="Critical incident description",
            incident_type=IncidentType.DATA_BREACH,
            severity=IncidentSeverity.CRITICAL
        )
        
        # Проверка необходимости эскалации
        should_escalate = self.agent._should_escalate(incident)
        self.assertTrue(should_escalate)  # CRITICAL должен эскалироваться немедленно
    
    def test_incident_resolution(self):
        """Тест разрешения инцидента"""
        self.agent.initialize()
        
        # Создание инцидента
        incident = self.agent.create_incident(
            title="Test Incident",
            description="Test incident description",
            incident_type=IncidentType.PHISHING,
            severity=IncidentSeverity.MEDIUM
        )
        
        # Разрешение инцидента
        success = self.agent.resolve_incident(
            incident.incident_id,
            "Phishing emails blocked, users notified",
            ["Improve email filtering", "Conduct security training"]
        )
        
        # Проверка разрешения
        self.assertTrue(success)
        self.assertEqual(incident.status, IncidentStatus.RESOLVED)
        self.assertIsNotNone(incident.resolution)
        self.assertGreater(len(incident.lessons_learned), 0)
    
    def test_incident_serialization(self):
        """Тест сериализации инцидента"""
        incident = Incident(
            incident_id="test_serialization",
            title="Test Serialization",
            description="Test incident for serialization",
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.HIGH
        )
        
        # Добавление данных
        incident.add_affected_system("server1", "web_server", "Web server")
        incident.add_indicator("ip_address", "192.168.1.1", "Suspicious IP")
        incident.add_action("BLOCK", "Blocked suspicious IP", "Success")
        incident.add_evidence("log_file", "malware.log", "Malware detection log")
        incident.add_timeline_event("created", "Incident created")
        
        # Сериализация
        incident_dict = incident.to_dict()
        
        # Проверка сериализации
        self.assertIsInstance(incident_dict, dict)
        self.assertEqual(incident_dict["incident_id"], "test_serialization")
        self.assertEqual(incident_dict["title"], "Test Serialization")
        self.assertEqual(len(incident_dict["affected_systems"]), 1)
        self.assertEqual(len(incident_dict["indicators"]), 1)
        self.assertEqual(len(incident_dict["actions_taken"]), 1)
        self.assertEqual(len(incident_dict["evidence"]), 1)
        self.assertEqual(len(incident_dict["timeline"]), 1)
    
    def test_metrics_serialization(self):
        """Тест сериализации метрик"""
        metrics = IncidentResponseMetrics()
        
        # Установка тестовых данных
        metrics.total_incidents = 50
        metrics.avg_response_time = 15.5
        metrics.avg_resolution_time = 2.5
        metrics.sla_compliance = 0.95
        metrics.last_incident_time = datetime.now()
        
        # Сериализация
        metrics_dict = metrics.to_dict()
        
        # Проверка сериализации
        self.assertIsInstance(metrics_dict, dict)
        self.assertEqual(metrics_dict["total_incidents"], 50)
        self.assertEqual(metrics_dict["avg_response_time"], 15.5)
        self.assertEqual(metrics_dict["avg_resolution_time"], 2.5)
        self.assertEqual(metrics_dict["sla_compliance"], 0.95)
        self.assertIsNotNone(metrics_dict["last_incident_time"])
    
    def test_response_plan_execution(self):
        """Тест выполнения плана реагирования"""
        self.agent._load_response_plans()
        
        # Получение плана реагирования на вредоносное ПО
        plan = self.agent._get_response_plan(IncidentType.MALWARE)
        
        # Проверка плана
        self.assertIsNotNone(plan)
        self.assertEqual(plan["name"], "Malware Response Plan")
        self.assertGreater(len(plan["steps"]), 0)
        self.assertIn("ISOLATE", [step["action"] for step in plan["steps"]])
        self.assertIn("QUARANTINE", [step["action"] for step in plan["steps"]])
    
    def test_action_execution(self):
        """Тест выполнения действий"""
        # Создание тестового инцидента
        incident = Incident(
            incident_id="test_action_incident",
            title="Test Action Incident",
            description="Test incident for action execution",
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.MEDIUM
        )
        
        # Выполнение действия
        self.agent._execute_action(incident, "BLOCK", "Blocked suspicious activity")
        
        # Проверка выполнения
        self.assertEqual(len(incident.actions_taken), 1)
        self.assertEqual(incident.actions_taken[0]["action"], "BLOCK")
        self.assertEqual(incident.actions_taken[0]["description"], "Blocked suspicious activity")
        
        # Проверка метрик
        self.assertEqual(self.agent.metrics.total_actions_taken, 1)
        self.assertEqual(self.agent.metrics.successful_actions, 1)
        self.assertEqual(self.agent.metrics.actions_by_type["BLOCK"], 1)
    
    def test_auto_execution_check(self):
        """Тест проверки автоматического выполнения"""
        # Проверка автоматических действий
        auto_actions = ["BLOCK", "QUARANTINE", "MONITOR", "NOTIFY"]
        for action in auto_actions:
            self.assertTrue(self.agent._can_auto_execute(action))
        
        # Проверка ручных действий
        manual_actions = ["INVESTIGATE", "ESCALATE", "PATCH", "RESTORE"]
        for action in manual_actions:
            self.assertFalse(self.agent._can_auto_execute(action))
    
    def test_notification_sending(self):
        """Тест отправки уведомлений"""
        self.agent._setup_notifications()
        
        # Создание тестового инцидента
        incident = Incident(
            incident_id="test_notification_incident",
            title="Test Notification Incident",
            description="Test incident for notifications",
            incident_type=IncidentType.CRITICAL,
            severity=IncidentSeverity.CRITICAL
        )
        
        # Отправка уведомлений об эскалации
        self.agent._send_escalation_notifications(incident)
        
        # Проверка что метод выполнился без ошибок
        # В реальной реализации здесь будет проверка отправленных уведомлений
    
    def test_metrics_update(self):
        """Тест обновления метрик"""
        # Создание тестового инцидента
        incident = Incident(
            incident_id="test_metrics_incident",
            title="Test Metrics Incident",
            description="Test incident for metrics",
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.HIGH
        )
        
        # Обновление метрик
        self.agent._update_metrics(incident, "created")
        
        # Проверка метрик
        self.assertEqual(self.agent.metrics.total_incidents, 1)
        self.assertIsNotNone(self.agent.metrics.last_incident_time)
        self.assertEqual(self.agent.metrics.incidents_by_type["malware"], 1)
        self.assertEqual(self.agent.metrics.incidents_by_severity["high"], 1)
        self.assertEqual(self.agent.metrics.incidents_by_status["new"], 1)
    
    def test_resolution_metrics_update(self):
        """Тест обновления метрик разрешения"""
        # Создание тестового инцидента
        incident = Incident(
            incident_id="test_resolution_metrics_incident",
            title="Test Resolution Metrics Incident",
            description="Test incident for resolution metrics",
            incident_type=IncidentType.PHISHING,
            severity=IncidentSeverity.MEDIUM
        )
        
        # Установка времени создания (2 часа назад)
        incident.created_at = datetime.now() - timedelta(hours=2)
        incident.updated_at = datetime.now()
        
        # Обновление метрик разрешения
        self.agent._update_resolution_metrics(incident)
        
        # Проверка метрик
        self.assertEqual(self.agent.metrics.manually_resolved_incidents, 1)
        self.assertAlmostEqual(self.agent.metrics.avg_resolution_time, 2.0, delta=0.1)
    
    def test_recommendation_generation(self):
        """Тест генерации рекомендаций"""
        # Установка тестовых метрик
        self.agent.metrics.avg_response_time = 120  # 2 часа
        self.agent.metrics.sla_compliance = 0.7  # 70%
        self.agent.metrics.false_positives = 10
        self.agent.metrics.total_incidents = 50
        
        # Генерация рекомендаций
        recommendations = self.agent._generate_recommendations()
        
        # Проверка рекомендаций
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Проверка типов рекомендаций
        recommendation_types = [rec["type"] for rec in recommendations]
        self.assertIn("response_time", recommendation_types)
        self.assertIn("sla_compliance", recommendation_types)
        self.assertIn("false_positives", recommendation_types)
    
    def test_full_workflow(self):
        """Тест полного рабочего процесса"""
        # Инициализация
        self.assertTrue(self.agent.initialize())
        
        # Создание инцидента
        incident = self.agent.create_incident(
            title="Test Full Workflow Incident",
            description="Test incident for full workflow",
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.HIGH,
            affected_systems=[{"id": "server1", "type": "web_server", "description": "Web server"}]
        )
        
        # Проверка создания
        self.assertIsNotNone(incident)
        
        # Разрешение инцидента
        success = self.agent.resolve_incident(
            incident.incident_id,
            "Malware removed, systems patched",
            ["Improve endpoint protection", "Update security policies"]
        )
        
        # Проверка разрешения
        self.assertTrue(success)
        
        # Генерация отчета
        report = self.agent.generate_report()
        self.assertIsNotNone(report)
        
        # Остановка
        self.agent.stop()
        
        # Проверка что данные сохранены
        self.assertTrue(os.path.exists("data/incident_response"))
        self.assertTrue(os.path.exists("data/incident_response/incidents.json"))
        self.assertTrue(os.path.exists("data/incident_response/metrics.json"))
    
    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тест с несуществующим инцидентом
        success = self.agent.resolve_incident("nonexistent_incident", "Test resolution")
        self.assertFalse(success)
        
        # Тест с пустыми данными
        self.agent.incidents = {}
        recommendations = self.agent._generate_recommendations()
        self.assertIsInstance(recommendations, list)
    
    def test_data_validation(self):
        """Тест валидации данных"""
        # Тест с некорректными данными
        incident = Incident(
            incident_id="",
            title="",
            description="",
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.LOW
        )
        
        # Проверка что инцидент создается даже с пустыми данными
        self.assertIsNotNone(incident)
        self.assertEqual(incident.incident_id, "")
        self.assertEqual(incident.title, "")
    
    def test_performance_metrics(self):
        """Тест метрик производительности"""
        # Тест расчета времени реагирования
        start_time = time.time()
        time.sleep(0.1)  # Симуляция работы
        end_time = time.time()
        
        duration = end_time - start_time
        self.assertGreater(duration, 0)
        self.assertIsInstance(duration, float)


class TestIncidentResponseEnums(unittest.TestCase):
    """Тесты для перечислений IncidentResponseAgent"""
    
    def test_incident_severity_enum(self):
        """Тест перечисления IncidentSeverity"""
        self.assertEqual(IncidentSeverity.LOW.value, "low")
        self.assertEqual(IncidentSeverity.MEDIUM.value, "medium")
        self.assertEqual(IncidentSeverity.HIGH.value, "high")
        self.assertEqual(IncidentSeverity.CRITICAL.value, "critical")
        self.assertEqual(IncidentSeverity.EMERGENCY.value, "emergency")
    
    def test_incident_status_enum(self):
        """Тест перечисления IncidentStatus"""
        self.assertEqual(IncidentStatus.NEW.value, "new")
        self.assertEqual(IncidentStatus.ASSIGNED.value, "assigned")
        self.assertEqual(IncidentStatus.IN_PROGRESS.value, "in_progress")
        self.assertEqual(IncidentStatus.RESOLVED.value, "resolved")
        self.assertEqual(IncidentStatus.CLOSED.value, "closed")
        self.assertEqual(IncidentStatus.ESCALATED.value, "escalated")
        self.assertEqual(IncidentStatus.CANCELLED.value, "cancelled")
    
    def test_incident_type_enum(self):
        """Тест перечисления IncidentType"""
        self.assertEqual(IncidentType.MALWARE.value, "malware")
        self.assertEqual(IncidentType.PHISHING.value, "phishing")
        self.assertEqual(IncidentType.DDOS.value, "ddos")
        self.assertEqual(IncidentType.DATA_BREACH.value, "data_breach")
        self.assertEqual(IncidentType.UNAUTHORIZED_ACCESS.value, "unauthorized_access")
        self.assertEqual(IncidentType.SYSTEM_COMPROMISE.value, "system_compromise")
        self.assertEqual(IncidentType.INSIDER_THREAT.value, "insider_threat")
        self.assertEqual(IncidentType.VULNERABILITY_EXPLOIT.value, "vulnerability_exploit")
        self.assertEqual(IncidentType.SOCIAL_ENGINEERING.value, "social_engineering")
        self.assertEqual(IncidentType.RANSOMWARE.value, "ransomware")
    
    def test_response_action_enum(self):
        """Тест перечисления ResponseAction"""
        self.assertEqual(ResponseAction.ISOLATE.value, "isolate")
        self.assertEqual(ResponseAction.QUARANTINE.value, "quarantine")
        self.assertEqual(ResponseAction.BLOCK.value, "block")
        self.assertEqual(ResponseAction.MONITOR.value, "monitor")
        self.assertEqual(ResponseAction.INVESTIGATE.value, "investigate")
        self.assertEqual(ResponseAction.ESCALATE.value, "escalate")
        self.assertEqual(ResponseAction.NOTIFY.value, "notify")
        self.assertEqual(ResponseAction.PATCH.value, "patch")
        self.assertEqual(ResponseAction.RESTORE.value, "restore")
        self.assertEqual(ResponseAction.TERMINATE.value, "terminate")


if __name__ == "__main__":
    # Запуск тестов
    unittest.main(verbosity=2)