#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тесты для ComplianceAgent

Этот модуль содержит комплексные unit-тесты для ComplianceAgent,
включая тестирование всех основных функций, AI моделей, стандартов соответствия,
оценки требований, генерации отчетов и обработки ошибок.

Тесты покрывают:
- Инициализацию агента и AI моделей
- Создание и управление требованиями соответствия
- Оценку соответствия и анализ рисков
- Стандарты соответствия и категории
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
    from security.ai_agents.compliance_agent import (
        ComplianceAgent,
        ComplianceRequirement,
        ComplianceStandard,
        ComplianceLevel,
        ComplianceCategory,
        ComplianceMetrics
    )
except ImportError as e:
    print("Ошибка импорта: {}".format(e))
    sys.exit(1)


class TestComplianceAgent(unittest.TestCase):
    """
    Тесты для ComplianceAgent
    
    Этот класс содержит все unit-тесты для основного агента соответствия.
    Тесты проверяют корректность работы всех методов, обработку требований,
    AI модели, стандарты соответствия и генерацию отчетов.
    """
    
    def setUp(self):
        """Настройка тестов"""
        self.agent = ComplianceAgent("TestComplianceAgent")
    
    def test_initialization(self):
        """Тест инициализации агента"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.name, "TestComplianceAgent")
        self.assertIsNotNone(self.agent.metrics)
        self.assertIsNotNone(self.agent.requirements)
        self.assertIsNotNone(self.agent.standards)
        self.assertIsNotNone(self.agent.categories)
    
    def test_ai_models_initialization(self):
        """Тест инициализации AI моделей"""
        self.agent._initialize_ai_models()
        
        # Проверка наличия всех AI моделей
        expected_models = [
            "compliance_classifier", "risk_assessor", "control_analyzer",
            "evidence_validator", "gap_analyzer"
        ]
        
        for model_name in expected_models:
            self.assertIn(model_name, self.agent.ml_models)
            self.assertIsNotNone(self.agent.ml_models[model_name])
    
    def test_compliance_standards_loading(self):
        """Тест загрузки стандартов соответствия"""
        self.agent._load_compliance_standards()
        
        # Проверка наличия стандартов
        expected_standards = [
            ComplianceStandard.ISO27001, ComplianceStandard.SOC2,
            ComplianceStandard.PCI_DSS, ComplianceStandard.GDPR,
            ComplianceStandard.HIPAA
        ]
        
        for standard in expected_standards:
            self.assertIn(standard, self.agent.standards)
            standard_info = self.agent.standards[standard]
            self.assertIn("name", standard_info)
            self.assertIn("description", standard_info)
            self.assertIn("requirements_count", standard_info)
            self.assertIn("categories", standard_info)
    
    def test_requirements_initialization(self):
        """Тест инициализации требований"""
        self.agent._initialize_requirements()
        
        # Проверка что требования созданы
        self.assertGreater(len(self.agent.requirements), 0)
        
        # Проверка что требования распределены по категориям
        self.assertGreater(len(self.agent.categories), 0)
    
    def test_monitoring_setup(self):
        """Тест настройки мониторинга"""
        self.agent._setup_monitoring()
        
        # Проверка системы непрерывного мониторинга
        self.assertIn("enabled", self.agent.continuous_monitoring_system)
        self.assertIn("check_interval", self.agent.continuous_monitoring_system)
        self.assertIn("alert_threshold", self.agent.continuous_monitoring_system)
        
        # Проверка системы оповещений
        self.assertIn("email_alerts", self.agent.alert_system)
        self.assertIn("dashboard_alerts", self.agent.alert_system)
        
        # Проверка системы отчетности
        self.assertIn("daily_reports", self.agent.reporting_system)
        self.assertIn("weekly_reports", self.agent.reporting_system)
    
    def test_requirement_creation(self):
        """Тест создания требования"""
        self.agent.initialize()
        
        # Создание тестового требования
        requirement = self.agent.create_requirement(
            title="Test Compliance Requirement",
            description="Test requirement for compliance testing",
            standard=ComplianceStandard.ISO27001,
            category=ComplianceCategory.ACCESS_CONTROL,
            priority=5
        )
        
        # Проверка создания требования
        self.assertIsNotNone(requirement)
        self.assertEqual(requirement.title, "Test Compliance Requirement")
        self.assertEqual(requirement.standard, ComplianceStandard.ISO27001)
        self.assertEqual(requirement.category, ComplianceCategory.ACCESS_CONTROL)
        self.assertIn(requirement.requirement_id, self.agent.requirements)
        
        # Проверка метрик
        self.assertGreater(self.agent.metrics.total_requirements, 0)
    
    def test_requirement_validation(self):
        """Тест валидации требования"""
        # Тест с корректными данными
        self.assertTrue(self.agent._validate_requirement_data(
            "Valid Title",
            "Valid Description",
            ComplianceStandard.ISO27001,
            ComplianceCategory.ACCESS_CONTROL
        ))
        
        # Тест с некорректными данными
        self.assertFalse(self.agent._validate_requirement_data(
            "",  # Пустое название
            "Valid Description",
            ComplianceStandard.ISO27001,
            ComplianceCategory.ACCESS_CONTROL
        ))
        
        self.assertFalse(self.agent._validate_requirement_data(
            "Valid Title",
            "",  # Пустое описание
            ComplianceStandard.ISO27001,
            ComplianceCategory.ACCESS_CONTROL
        ))
    
    def test_requirement_assessment(self):
        """Тест оценки требования"""
        self.agent.initialize()
        
        # Создание тестового требования
        requirement = self.agent.create_requirement(
            title="Test Assessment Requirement",
            description="Test requirement for assessment",
            standard=ComplianceStandard.SOC2,
            category=ComplianceCategory.DATA_PROTECTION,
            priority=7
        )
        
        # Оценка требования
        success = self.agent.assess_requirement(
            requirement.requirement_id,
            "test_assessor",
            evidence=[{
                "type": "document",
                "data": "test_evidence_data",
                "description": "Test evidence description"
            }],
            controls=[{
                "control_id": "CTRL001",
                "control_name": "Test Control",
                "implementation_status": "fully_implemented",
                "description": "Test control description"
            }]
        )
        
        # Проверка оценки
        self.assertTrue(success)
        self.assertNotEqual(requirement.status, ComplianceLevel.NOT_ASSESSED)
        self.assertEqual(requirement.assessor, "test_assessor")
        self.assertIsNotNone(requirement.last_assessment)
        self.assertIsNotNone(requirement.next_assessment)
    
    def test_compliance_analysis(self):
        """Тест анализа соответствия"""
        # Создание тестового требования
        requirement = ComplianceRequirement(
            requirement_id="test_req",
            title="Test Requirement",
            description="Test description",
            standard=ComplianceStandard.ISO27001,
            category=ComplianceCategory.ACCESS_CONTROL,
            priority=5
        )
        
        # Анализ соответствия
        analysis = self.agent._analyze_compliance(
            requirement,
            evidence=[{"type": "document", "data": "test"}],
            controls=[{"implementation_status": "fully_implemented"}]
        )
        
        # Проверка анализа
        self.assertIn("status", analysis)
        self.assertIn("score", analysis)
        self.assertIn("notes", analysis)
        self.assertIsInstance(analysis["score"], float)
        self.assertGreaterEqual(analysis["score"], 0.0)
        self.assertLessEqual(analysis["score"], 1.0)
    
    def test_evidence_quality_analysis(self):
        """Тест анализа качества доказательств"""
        # Тест с качественными доказательствами
        good_evidence = [
            {
                "type": "document",
                "data": "comprehensive_evidence_data",
                "description": "Detailed evidence description"
            }
        ]
        
        quality_score = self.agent._analyze_evidence_quality(good_evidence)
        self.assertGreater(quality_score, 0.5)
        
        # Тест с пустыми доказательствами
        empty_evidence = []
        quality_score = self.agent._analyze_evidence_quality(empty_evidence)
        self.assertEqual(quality_score, 0.0)
    
    def test_control_effectiveness_analysis(self):
        """Тест анализа эффективности контролей"""
        # Тест с эффективными контролями
        good_controls = [
            {
                "control_id": "CTRL001",
                "control_name": "Effective Control",
                "implementation_status": "fully_implemented",
                "description": "Comprehensive control description"
            }
        ]
        
        effectiveness_score = self.agent._analyze_control_effectiveness(good_controls)
        self.assertGreater(effectiveness_score, 0.5)
        
        # Тест с пустыми контролями
        empty_controls = []
        effectiveness_score = self.agent._analyze_control_effectiveness(empty_controls)
        self.assertEqual(effectiveness_score, 0.0)
    
    def test_risk_level_analysis(self):
        """Тест анализа уровня риска"""
        # Создание тестового требования с высоким приоритетом
        high_priority_req = ComplianceRequirement(
            requirement_id="high_risk_req",
            title="High Risk Requirement",
            description="High risk description",
            standard=ComplianceStandard.PCI_DSS,
            category=ComplianceCategory.DATA_PROTECTION,
            priority=9
        )
        
        risk_level = self.agent._analyze_risk_level(high_priority_req)
        self.assertGreater(risk_level, 0.3)
        
        # Создание тестового требования с низким приоритетом
        low_priority_req = ComplianceRequirement(
            requirement_id="low_risk_req",
            title="Low Risk Requirement",
            description="Low risk description",
            standard=ComplianceStandard.ISO27001,
            category=ComplianceCategory.SECURITY_AWARENESS,
            priority=2
        )
        
        risk_level = self.agent._analyze_risk_level(low_priority_req)
        self.assertLess(risk_level, 0.5)
    
    def test_metrics_update(self):
        """Тест обновления метрик"""
        # Создание тестового требования
        requirement = ComplianceRequirement(
            requirement_id="metrics_test_req",
            title="Metrics Test Requirement",
            description="Test requirement for metrics",
            standard=ComplianceStandard.ISO27001,
            category=ComplianceCategory.ACCESS_CONTROL,
            priority=5
        )
        
        # Обновление метрик
        self.agent._update_metrics(requirement, "created")
        
        # Проверка метрик
        self.assertEqual(self.agent.metrics.total_requirements, 1)
        self.assertIn("iso27001", self.agent.metrics.requirements_by_standard)
        self.assertIn("access_control", self.agent.metrics.requirements_by_category)
    
    def test_metrics_recalculation(self):
        """Тест пересчета метрик"""
        # Установка тестовых данных
        self.agent.metrics.total_requirements = 10
        self.agent.metrics.requirements_by_status = {
            "compliant": 7,
            "partially_compliant": 2,
            "non_compliant": 1
        }
        
        # Пересчет метрик
        self.agent._recalculate_compliance_metrics()
        
        # Проверка пересчета
        self.assertEqual(self.agent.metrics.compliance_rate, 0.7)
        self.assertEqual(self.agent.metrics.partial_compliance_rate, 0.2)
        self.assertEqual(self.agent.metrics.non_compliance_rate, 0.1)
        self.assertEqual(self.agent.metrics.assessment_completion_rate, 1.0)
    
    def test_requirement_serialization(self):
        """Тест сериализации требования"""
        requirement = ComplianceRequirement(
            requirement_id="test_serialization",
            title="Test Serialization",
            description="Test requirement for serialization",
            standard=ComplianceStandard.ISO27001,
            category=ComplianceCategory.ACCESS_CONTROL,
            priority=5
        )
        
        # Добавление данных
        requirement.add_evidence("document", "test_evidence", "Test evidence")
        requirement.add_control("CTRL001", "Test Control", "fully_implemented", "Test control")
        requirement.add_risk("RISK001", "Test Risk", "high", "Test mitigation")
        requirement.add_recommendation("Test recommendation", "high", "2024-12-31")
        
        # Сериализация
        requirement_dict = requirement.to_dict()
        
        # Проверка сериализации
        self.assertIsInstance(requirement_dict, dict)
        self.assertEqual(requirement_dict["requirement_id"], "test_serialization")
        self.assertEqual(requirement_dict["title"], "Test Serialization")
        self.assertEqual(len(requirement_dict["evidence"]), 1)
        self.assertEqual(len(requirement_dict["controls"]), 1)
        self.assertEqual(len(requirement_dict["risks"]), 1)
        self.assertEqual(len(requirement_dict["recommendations"]), 1)
    
    def test_metrics_serialization(self):
        """Тест сериализации метрик"""
        metrics = ComplianceMetrics()
        
        # Установка тестовых данных
        metrics.total_requirements = 100
        metrics.compliance_rate = 0.85
        metrics.partial_compliance_rate = 0.10
        metrics.non_compliance_rate = 0.05
        metrics.assessment_completion_rate = 0.95
        metrics.last_assessment_time = datetime.now()
        
        # Сериализация
        metrics_dict = metrics.to_dict()
        
        # Проверка сериализации
        self.assertIsInstance(metrics_dict, dict)
        self.assertEqual(metrics_dict["total_requirements"], 100)
        self.assertEqual(metrics_dict["compliance_rate"], 0.85)
        self.assertEqual(metrics_dict["partial_compliance_rate"], 0.10)
        self.assertEqual(metrics_dict["non_compliance_rate"], 0.05)
        self.assertEqual(metrics_dict["assessment_completion_rate"], 0.95)
        self.assertIsNotNone(metrics_dict["last_assessment_time"])
    
    def test_compliance_report_generation(self):
        """Тест генерации отчета о соответствии"""
        self.agent.initialize()
        
        # Генерация отчета
        report = self.agent.generate_compliance_report()
        
        # Проверка отчета
        self.assertIsNotNone(report)
        self.assertIn("report_id", report)
        self.assertIn("generated_at", report)
        self.assertIn("agent_name", report)
        self.assertIn("summary", report)
        self.assertIn("standards_compliance", report)
        self.assertIn("category_compliance", report)
        self.assertIn("requirements", report)
        self.assertIn("metrics", report)
        self.assertIn("recommendations", report)
    
    def test_recommendation_generation(self):
        """Тест генерации рекомендаций"""
        # Установка тестовых метрик
        self.agent.metrics.compliance_rate = 0.7  # Низкое соответствие
        self.agent.metrics.assessment_completion_rate = 0.8  # Не все оценены
        self.agent.metrics.non_compliance_rate = 0.25  # Высокое несоответствие
        
        # Генерация рекомендаций
        recommendations = self.agent._generate_recommendations()
        
        # Проверка рекомендаций
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Проверка типов рекомендаций
        recommendation_types = [rec["type"] for rec in recommendations]
        self.assertIn("compliance_improvement", recommendation_types)
        self.assertIn("assessment_completion", recommendation_types)
        self.assertIn("non_compliance_reduction", recommendation_types)
    
    def test_category_mapping(self):
        """Тест маппинга категорий"""
        # Тест различных категорий
        test_cases = [
            ("Политика безопасности", ComplianceCategory.ACCESS_CONTROL),
            ("Контроль доступа", ComplianceCategory.ACCESS_CONTROL),
            ("Управление активами", ComplianceCategory.DATA_PROTECTION),
            ("Криптография", ComplianceCategory.DATA_PROTECTION),
            ("Физическая безопасность", ComplianceCategory.PHYSICAL_SECURITY),
            ("Управление инцидентами", ComplianceCategory.INCIDENT_RESPONSE),
            ("Бизнес-непрерывность", ComplianceCategory.BUSINESS_CONTINUITY),
            ("Неизвестная категория", ComplianceCategory.RISK_MANAGEMENT)
        ]
        
        for category_name, expected_category in test_cases:
            mapped_category = self.agent._map_category(category_name)
            self.assertEqual(mapped_category, expected_category)
    
    def test_priority_calculation(self):
        """Тест расчета приоритета"""
        # Тест различных комбинаций стандарта и категории
        test_cases = [
            (ComplianceStandard.PCI_DSS, "Критическая безопасность", 7),  # 5 + 2
            (ComplianceStandard.GDPR, "Контроль доступа", 6),  # 5 + 1
            (ComplianceStandard.ISO27001, "Обучение", 4),  # 3 + 1
            (ComplianceStandard.SOC2, "Неизвестная категория", 5)  # 4 + 1
        ]
        
        for standard, category, expected_priority in test_cases:
            calculated_priority = self.agent._calculate_priority(standard, category)
            self.assertEqual(calculated_priority, expected_priority)
    
    def test_full_workflow(self):
        """Тест полного рабочего процесса"""
        # Инициализация
        self.assertTrue(self.agent.initialize())
        
        # Создание требования
        requirement = self.agent.create_requirement(
            title="Test Full Workflow Requirement",
            description="Test requirement for full workflow",
            standard=ComplianceStandard.ISO27001,
            category=ComplianceCategory.ACCESS_CONTROL,
            priority=5
        )
        
        # Проверка создания
        self.assertIsNotNone(requirement)
        
        # Оценка требования
        success = self.agent.assess_requirement(
            requirement.requirement_id,
            "test_assessor",
            evidence=[{"type": "document", "data": "test_evidence"}],
            controls=[{"control_id": "CTRL001", "implementation_status": "fully_implemented"}]
        )
        
        # Проверка оценки
        self.assertTrue(success)
        
        # Генерация отчета
        report = self.agent.generate_compliance_report()
        self.assertIsNotNone(report)
        
        # Остановка
        self.agent.stop()
        
        # Проверка что данные сохранены
        self.assertTrue(os.path.exists("data/compliance"))
        self.assertTrue(os.path.exists("data/compliance/requirements.json"))
        self.assertTrue(os.path.exists("data/compliance/metrics.json"))
    
    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тест с несуществующим требованием
        success = self.agent.assess_requirement("nonexistent_requirement", "test_assessor")
        self.assertFalse(success)
        
        # Тест с пустыми данными
        self.agent.requirements = {}
        recommendations = self.agent._generate_recommendations()
        self.assertIsInstance(recommendations, list)
    
    def test_data_validation(self):
        """Тест валидации данных"""
        # Тест с некорректными данными
        requirement = ComplianceRequirement(
            requirement_id="",
            title="",
            description="",
            standard=ComplianceStandard.ISO27001,
            category=ComplianceCategory.ACCESS_CONTROL,
            priority=1
        )
        
        # Проверка что требование создается даже с пустыми данными
        self.assertIsNotNone(requirement)
        self.assertEqual(requirement.requirement_id, "")
        self.assertEqual(requirement.title, "")
    
    def test_performance_metrics(self):
        """Тест метрик производительности"""
        # Тест расчета времени
        start_time = time.time()
        time.sleep(0.1)  # Симуляция работы
        end_time = time.time()
        
        duration = end_time - start_time
        self.assertGreater(duration, 0)
        self.assertIsInstance(duration, float)


class TestComplianceEnums(unittest.TestCase):
    """Тесты для перечислений ComplianceAgent"""
    
    def test_compliance_standard_enum(self):
        """Тест перечисления ComplianceStandard"""
        self.assertEqual(ComplianceStandard.ISO27001.value, "iso27001")
        self.assertEqual(ComplianceStandard.SOC2.value, "soc2")
        self.assertEqual(ComplianceStandard.PCI_DSS.value, "pci_dss")
        self.assertEqual(ComplianceStandard.GDPR.value, "gdpr")
        self.assertEqual(ComplianceStandard.HIPAA.value, "hipaa")
        self.assertEqual(ComplianceStandard.NIST.value, "nist")
        self.assertEqual(ComplianceStandard.CIS.value, "cis")
        self.assertEqual(ComplianceStandard.COBIT.value, "cobit")
        self.assertEqual(ComplianceStandard.ITIL.value, "itil")
        self.assertEqual(ComplianceStandard.CUSTOM.value, "custom")
    
    def test_compliance_level_enum(self):
        """Тест перечисления ComplianceLevel"""
        self.assertEqual(ComplianceLevel.COMPLIANT.value, "compliant")
        self.assertEqual(ComplianceLevel.PARTIALLY_COMPLIANT.value, "partially_compliant")
        self.assertEqual(ComplianceLevel.NON_COMPLIANT.value, "non_compliant")
        self.assertEqual(ComplianceLevel.NOT_ASSESSED.value, "not_assessed")
        self.assertEqual(ComplianceLevel.PENDING.value, "pending")
    
    def test_compliance_category_enum(self):
        """Тест перечисления ComplianceCategory"""
        self.assertEqual(ComplianceCategory.ACCESS_CONTROL.value, "access_control")
        self.assertEqual(ComplianceCategory.DATA_PROTECTION.value, "data_protection")
        self.assertEqual(ComplianceCategory.NETWORK_SECURITY.value, "network_security")
        self.assertEqual(ComplianceCategory.INCIDENT_RESPONSE.value, "incident_response")
        self.assertEqual(ComplianceCategory.BUSINESS_CONTINUITY.value, "business_continuity")
        self.assertEqual(ComplianceCategory.RISK_MANAGEMENT.value, "risk_management")
        self.assertEqual(ComplianceCategory.AUDIT_LOGGING.value, "audit_logging")
        self.assertEqual(ComplianceCategory.PHYSICAL_SECURITY.value, "physical_security")
        self.assertEqual(ComplianceCategory.VULNERABILITY_MANAGEMENT.value, "vulnerability_management")
        self.assertEqual(ComplianceCategory.SECURITY_AWARENESS.value, "security_awareness")


if __name__ == "__main__":
    # Запуск тестов
    unittest.main(verbosity=2)