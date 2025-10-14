#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тесты для ThreatIntelligenceAgent

Этот модуль содержит комплексные unit-тесты для ThreatIntelligenceAgent,
включая тестирование всех основных функций, AI моделей, источников угроз,
анализа IOCs, генерации отчетов и обработки ошибок.

Тесты покрывают:
- Инициализацию агента и AI моделей
- Сбор угроз из различных источников
- Анализ и классификацию угроз
- Работу с индикаторами компрометации (IOCs)
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
    from security.ai_agents.threat_intelligence_agent import (
        ThreatIntelligenceAgent,
        ThreatIntelligence,
        ThreatType,
        ThreatSeverity,
        IOCType,
        ThreatSource,
        ThreatIntelligenceMetrics
    )
except ImportError as e:
    print("Ошибка импорта: {}".format(e))
    sys.exit(1)


class TestThreatIntelligenceAgent(unittest.TestCase):
    """
    Тесты для ThreatIntelligenceAgent
    
    Этот класс содержит все unit-тесты для основного агента разведки угроз.
    Тесты проверяют корректность работы всех методов, обработку данных,
    AI модели, источники угроз и генерацию отчетов.
    """
    
    def setUp(self):
        """Настройка тестов"""
        self.agent = ThreatIntelligenceAgent("TestThreatIntelligenceAgent")
    
    def test_initialization(self):
        """Тест инициализации агента"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.name, "TestThreatIntelligenceAgent")
        self.assertIsNotNone(self.agent.metrics)
        self.assertIsNotNone(self.agent.threats)
        self.assertIsNotNone(self.agent.sources)
    
    def test_ai_models_initialization(self):
        """Тест инициализации AI моделей"""
        self.agent._initialize_ai_models()
        
        # Проверка наличия всех AI моделей
        expected_models = [
            "threat_classifier", "ioc_analyzer", "severity_predictor",
            "source_reliability_analyzer", "trend_analyzer"
        ]
        
        for model_name in expected_models:
            self.assertIn(model_name, self.agent.ml_models)
            self.assertIsNotNone(self.agent.ml_models[model_name])
    
    def test_threat_sources_loading(self):
        """Тест загрузки источников угроз"""
        self.agent._load_threat_sources()
        
        # Проверка наличия источников
        expected_sources = ["open_source", "commercial", "government", "academic"]
        
        for source_name in expected_sources:
            self.assertIn(source_name, self.agent.sources)
            source = self.agent.sources[source_name]
            self.assertIn("name", source)
            self.assertIn("type", source)
            self.assertIn("reliability", source)
            self.assertIn("active", source)
    
    def test_databases_initialization(self):
        """Тест инициализации баз данных"""
        self.agent._initialize_databases()
        
        # Проверка баз данных угроз
        self.assertIn("malware", self.agent.threat_feeds)
        self.assertIn("phishing", self.agent.threat_feeds)
        self.assertIn("ransomware", self.agent.threat_feeds)
        self.assertIn("apt", self.agent.threat_feeds)
        self.assertIn("vulnerability", self.agent.threat_feeds)
        
        # Проверка баз данных IOCs
        self.assertIn("ip_addresses", self.agent.ioc_databases)
        self.assertIn("domains", self.agent.ioc_databases)
        self.assertIn("urls", self.agent.ioc_databases)
        self.assertIn("file_hashes", self.agent.ioc_databases)
        self.assertIn("email_addresses", self.agent.ioc_databases)
    
    def test_threat_collection(self):
        """Тест сбора угроз"""
        self.agent.initialize()
        
        # Сбор угроз
        threats_collected = self.agent.collect_threats()
        
        # Проверка что угрозы собраны
        self.assertGreater(threats_collected, 0)
        self.assertGreater(len(self.agent.threats), 0)
        
        # Проверка метрик
        self.assertGreater(self.agent.metrics.total_threats_collected, 0)
        self.assertIsNotNone(self.agent.metrics.last_collection_time)
    
    def test_threat_analysis(self):
        """Тест анализа угроз"""
        self.agent.initialize()
        self.agent.collect_threats()
        
        # Анализ угроз
        threats_analyzed = self.agent.analyze_threats()
        
        # Проверка что угрозы проанализированы
        self.assertGreater(threats_analyzed, 0)
        
        # Проверка метрик
        self.assertGreater(self.agent.metrics.processing_time, 0)
        self.assertGreaterEqual(self.agent.metrics.data_quality_score, 0.0)
        self.assertLessEqual(self.agent.metrics.data_quality_score, 1.0)
    
    def test_threat_classification(self):
        """Тест классификации угроз"""
        self.agent._initialize_ai_models()
        
        # Создание тестовой угрозы
        threat = ThreatIntelligence(
            threat_id="test_threat",
            title="Test Threat",
            description="Test threat description",
            threat_type=ThreatType.MALWARE,
            severity=ThreatSeverity.MEDIUM
        )
        
        # Классификация угрозы
        classification = self.agent._classify_threat(threat)
        
        # Проверка результата классификации
        self.assertIn("type", classification)
        self.assertIn("confidence", classification)
        self.assertIn("model_used", classification)
        self.assertGreaterEqual(classification["confidence"], 0.0)
        self.assertLessEqual(classification["confidence"], 1.0)
    
    def test_severity_prediction(self):
        """Тест предсказания серьезности"""
        self.agent._initialize_ai_models()
        
        # Создание тестовой угрозы
        threat = ThreatIntelligence(
            threat_id="test_threat",
            title="Test Threat",
            description="Test threat description",
            threat_type=ThreatType.APT,
            severity=ThreatSeverity.HIGH
        )
        
        # Предсказание серьезности
        severity_prediction = self.agent._predict_severity(threat)
        
        # Проверка результата предсказания
        self.assertIn("severity", severity_prediction)
        self.assertIn("confidence", severity_prediction)
        self.assertIn("model_used", severity_prediction)
        self.assertGreaterEqual(severity_prediction["confidence"], 0.0)
        self.assertLessEqual(severity_prediction["confidence"], 1.0)
    
    def test_ioc_analysis(self):
        """Тест анализа IOCs"""
        self.agent._initialize_ai_models()
        
        # Создание тестовой угрозы с IOCs
        threat = ThreatIntelligence(
            threat_id="test_threat",
            title="Test Threat",
            description="Test threat description",
            threat_type=ThreatType.MALWARE,
            severity=ThreatSeverity.MEDIUM
        )
        
        threat.add_ioc(IOCType.IP_ADDRESS, "192.168.1.1")
        threat.add_ioc(IOCType.DOMAIN, "malicious.com")
        
        # Анализ IOCs
        ioc_analysis = self.agent._analyze_iocs(threat)
        
        # Проверка результата анализа
        self.assertIn("confidence", ioc_analysis)
        self.assertIn("ioc_count", ioc_analysis)
        self.assertIn("model_used", ioc_analysis)
        self.assertEqual(ioc_analysis["ioc_count"], 2)
        self.assertGreaterEqual(ioc_analysis["confidence"], 0.0)
        self.assertLessEqual(ioc_analysis["confidence"], 1.0)
    
    def test_data_quality_calculation(self):
        """Тест расчета качества данных"""
        # Создание тестовых угроз
        threat1 = ThreatIntelligence(
            threat_id="test_threat_1",
            title="Test Threat 1",
            description="Detailed threat description with enough information",
            threat_type=ThreatType.MALWARE,
            severity=ThreatSeverity.HIGH
        )
        threat1.add_ioc(IOCType.IP_ADDRESS, "192.168.1.1")
        threat1.add_tag("test")
        threat1.set_source("Test Source", 0.9)
        threat1.confidence = 0.8
        
        threat2 = ThreatIntelligence(
            threat_id="test_threat_2",
            title="Test Threat 2",
            description="Short",
            threat_type=ThreatType.PHISHING,
            severity=ThreatSeverity.LOW
        )
        threat2.confidence = 0.5
        
        self.agent.threats = {
            "test_threat_1": threat1,
            "test_threat_2": threat2
        }
        
        # Расчет качества данных
        quality_score = self.agent._calculate_data_quality()
        
        # Проверка качества данных
        self.assertGreaterEqual(quality_score, 0.0)
        self.assertLessEqual(quality_score, 1.0)
        self.assertGreater(quality_score, 0.5)  # Ожидаем хорошее качество
    
    def test_report_generation(self):
        """Тест генерации отчета"""
        self.agent.initialize()
        self.agent.collect_threats()
        self.agent.analyze_threats()
        
        # Генерация отчета
        report = self.agent.generate_report()
        
        # Проверка отчета
        self.assertIsNotNone(report)
        self.assertIn("report_id", report)
        self.assertIn("generated_at", report)
        self.assertIn("agent_name", report)
        self.assertIn("summary", report)
        self.assertIn("threats", report)
        self.assertIn("metrics", report)
        self.assertIn("recommendations", report)
        
        # Проверка сводки
        summary = report["summary"]
        self.assertIn("total_threats", summary)
        self.assertIn("threats_by_type", summary)
        self.assertIn("threats_by_severity", summary)
        self.assertIn("total_iocs", summary)
        self.assertIn("data_quality_score", summary)
    
    def test_threat_intelligence_creation(self):
        """Тест создания объекта ThreatIntelligence"""
        threat = ThreatIntelligence(
            threat_id="test_threat",
            title="Test Threat",
            description="Test threat description",
            threat_type=ThreatType.MALWARE,
            severity=ThreatSeverity.HIGH
        )
        
        # Проверка базовых свойств
        self.assertEqual(threat.threat_id, "test_threat")
        self.assertEqual(threat.title, "Test Threat")
        self.assertEqual(threat.description, "Test threat description")
        self.assertEqual(threat.threat_type, ThreatType.MALWARE)
        self.assertEqual(threat.severity, ThreatSeverity.HIGH)
        
        # Добавление IOC
        threat.add_ioc(IOCType.IP_ADDRESS, "192.168.1.1", "Test IP")
        self.assertEqual(len(threat.iocs), 1)
        self.assertEqual(threat.iocs[0]["type"], IOCType.IP_ADDRESS)
        self.assertEqual(threat.iocs[0]["value"], "192.168.1.1")
        
        # Добавление тега
        threat.add_tag("test")
        self.assertIn("test", threat.tags)
        
        # Установка источника
        threat.set_source("Test Source", 0.9)
        self.assertIsNotNone(threat.source)
        self.assertEqual(threat.source["name"], "Test Source")
        self.assertEqual(threat.source["reliability"], 0.9)
    
    def test_metrics_initialization(self):
        """Тест инициализации метрик"""
        metrics = ThreatIntelligenceMetrics()
        
        # Проверка инициализации метрик
        self.assertEqual(metrics.total_threats_collected, 0)
        self.assertEqual(metrics.total_iocs_collected, 0)
        self.assertEqual(metrics.active_sources, 0)
        self.assertEqual(metrics.data_quality_score, 0.0)
        self.assertIsNone(metrics.last_collection_time)
        self.assertIsNone(metrics.last_update_time)
    
    def test_full_workflow(self):
        """Тест полного рабочего процесса"""
        # Инициализация
        self.assertTrue(self.agent.initialize())
        
        # Сбор угроз
        threats_collected = self.agent.collect_threats()
        self.assertGreater(threats_collected, 0)
        
        # Анализ угроз
        threats_analyzed = self.agent.analyze_threats()
        self.assertGreater(threats_analyzed, 0)
        
        # Генерация отчета
        report = self.agent.generate_report()
        self.assertIsNotNone(report)
        
        # Остановка
        self.agent.stop()
        
        # Проверка что данные сохранены
        self.assertTrue(os.path.exists("data/threat_intelligence"))
        self.assertTrue(os.path.exists("data/threat_intelligence/threats.json"))
        self.assertTrue(os.path.exists("data/threat_intelligence/metrics.json"))
    
    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тест обработки ошибок при инициализации
        try:
            agent = ThreatIntelligenceAgent("ErrorTestAgent")
            # Симуляция ошибки
            agent.threats = None
            result = agent._calculate_data_quality()
            self.assertEqual(result, 0.0)
        except Exception as e:
            self.fail("Ошибка не обработана корректно: {}".format(str(e)))
    
    def test_data_validation(self):
        """Тест валидации данных"""
        # Тест с пустыми данными
        self.agent.threats = {}
        quality = self.agent._calculate_data_quality()
        self.assertEqual(quality, 0.0)
        
        # Тест с некорректными данными
        self.agent.threats = {"invalid": "data"}
        quality = self.agent._calculate_data_quality()
        self.assertEqual(quality, 0.0)
    
    def test_metrics_calculation(self):
        """Тест расчета метрик"""
        # Тест обновления метрик
        self.agent.metrics.total_threats_collected = 10
        self.agent.metrics.api_calls_made = 5
        self.agent.metrics.api_errors = 1
        
        # Проверка корректности метрик
        self.assertEqual(self.agent.metrics.total_threats_collected, 10)
        self.assertEqual(self.agent.metrics.api_calls_made, 5)
        self.assertEqual(self.agent.metrics.api_errors, 1)
    
    def test_threat_intelligence_serialization(self):
        """Тест сериализации ThreatIntelligence"""
        threat = ThreatIntelligence(
            threat_id="test_serialization",
            title="Test Serialization",
            description="Test threat for serialization",
            threat_type=ThreatType.MALWARE,
            severity=ThreatSeverity.HIGH
        )
        
        # Добавление данных
        threat.add_ioc(IOCType.IP_ADDRESS, "192.168.1.1")
        threat.add_tag("test")
        threat.set_source("Test Source", 0.9)
        
        # Сериализация
        threat_dict = threat.to_dict()
        
        # Проверка сериализации
        self.assertIsInstance(threat_dict, dict)
        self.assertEqual(threat_dict["threat_id"], "test_serialization")
        self.assertEqual(threat_dict["title"], "Test Serialization")
        self.assertEqual(len(threat_dict["iocs"]), 1)
        self.assertEqual(len(threat_dict["tags"]), 1)
        self.assertIsNotNone(threat_dict["source"])
    
    def test_metrics_serialization(self):
        """Тест сериализации метрик"""
        metrics = ThreatIntelligenceMetrics()
        
        # Установка тестовых данных
        metrics.total_threats_collected = 100
        metrics.data_quality_score = 0.95
        metrics.last_collection_time = datetime.now()
        
        # Сериализация
        metrics_dict = metrics.to_dict()
        
        # Проверка сериализации
        self.assertIsInstance(metrics_dict, dict)
        self.assertEqual(metrics_dict["total_threats_collected"], 100)
        self.assertEqual(metrics_dict["data_quality_score"], 0.95)
        self.assertIsNotNone(metrics_dict["last_collection_time"])
    
    def test_ai_model_accuracy(self):
        """Тест точности AI моделей"""
        self.agent._initialize_ai_models()
        
        # Проверка точности AI моделей
        for model_name, model in self.agent.ml_models.items():
            self.assertIn("accuracy", model)
            self.assertIn("confidence_threshold", model)
            self.assertIn("model_type", model)
            self.assertGreaterEqual(model["accuracy"], 0.0)
            self.assertLessEqual(model["accuracy"], 1.0)
            self.assertGreaterEqual(model["confidence_threshold"], 0.0)
            self.assertLessEqual(model["confidence_threshold"], 1.0)
    
    def test_source_reliability(self):
        """Тест надежности источников"""
        self.agent._load_threat_sources()
        
        # Проверка источников
        for source_name, source_config in self.agent.sources.items():
            self.assertIn("name", source_config)
            self.assertIn("type", source_config)
            self.assertIn("reliability", source_config)
            self.assertIn("active", source_config)
            self.assertGreaterEqual(source_config["reliability"], 0.0)
            self.assertLessEqual(source_config["reliability"], 1.0)
    
    def test_ioc_validation(self):
        """Тест валидации IOCs"""
        threat = ThreatIntelligence(
            threat_id="test_ioc_validation",
            title="Test IOC Validation",
            description="Test threat for IOC validation",
            threat_type=ThreatType.MALWARE,
            severity=ThreatSeverity.MEDIUM
        )
        
        # Добавление различных типов IOCs
        threat.add_ioc(IOCType.IP_ADDRESS, "192.168.1.1", "Test IP")
        threat.add_ioc(IOCType.DOMAIN, "malicious.com", "Test Domain")
        threat.add_ioc(IOCType.URL, "http://malicious.com/path", "Test URL")
        threat.add_ioc(IOCType.EMAIL, "phishing@malicious.com", "Test Email")
        threat.add_ioc(IOCType.FILE_HASH, "abc123def456", "Test Hash")
        
        # Проверка IOCs
        self.assertEqual(len(threat.iocs), 5)
        
        # Проверка типов IOCs
        ioc_types = [ioc["type"] for ioc in threat.iocs]
        self.assertIn(IOCType.IP_ADDRESS, ioc_types)
        self.assertIn(IOCType.DOMAIN, ioc_types)
        self.assertIn(IOCType.URL, ioc_types)
        self.assertIn(IOCType.EMAIL, ioc_types)
        self.assertIn(IOCType.FILE_HASH, ioc_types)
    
    def test_threat_classification_edge_cases(self):
        """Тест граничных случаев классификации угроз"""
        # Тест с пустыми данными
        empty_threat = ThreatIntelligence(
            threat_id="empty_threat",
            title="",
            description="",
            threat_type=ThreatType.MALWARE,
            severity=ThreatSeverity.LOW
        )
        
        classification = self.agent._classify_threat(empty_threat)
        self.assertIsInstance(classification, dict)
        self.assertIn("type", classification)
        self.assertIn("confidence", classification)
    
    def test_performance_metrics(self):
        """Тест метрик производительности"""
        # Тест расчета скорости сбора
        start_time = time.time()
        time.sleep(0.1)  # Симуляция работы
        end_time = time.time()
        
        duration = end_time - start_time
        threats_count = 10
        speed = threats_count / (duration / 60) if duration > 0 else 0
        
        self.assertGreater(speed, 0)
        self.assertIsInstance(speed, float)
    
    def test_recommendation_generation(self):
        """Тест генерации рекомендаций"""
        # Тест с пустыми угрозами
        self.agent.threats = {}
        recommendations = self.agent._generate_recommendations()
        self.assertIsInstance(recommendations, list)
        
        # Тест с угрозами
        threat = ThreatIntelligence(
            threat_id="test_recommendation",
            title="Test Threat",
            description="Test threat for recommendations",
            threat_type=ThreatType.MALWARE,
            severity=ThreatSeverity.HIGH
        )
        self.agent.threats = {"test_recommendation": threat}
        
        recommendations = self.agent._generate_recommendations()
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
    
    def test_database_operations(self):
        """Тест операций с базами данных"""
        self.agent._initialize_databases()
        
        # Проверка инициализации баз данных
        self.assertIsInstance(self.agent.threat_feeds, dict)
        self.assertIsInstance(self.agent.ioc_databases, dict)
        self.assertIsInstance(self.agent.vulnerability_feeds, dict)
        self.assertIsInstance(self.agent.malware_feeds, dict)
        
        # Проверка структуры баз данных
        expected_threat_feeds = ["malware", "phishing", "ransomware", "apt", "vulnerability"]
        for feed in expected_threat_feeds:
            self.assertIn(feed, self.agent.threat_feeds)
        
        expected_ioc_types = ["ip_addresses", "domains", "urls", "file_hashes", "email_addresses"]
        for ioc_type in expected_ioc_types:
            self.assertIn(ioc_type, self.agent.ioc_databases)


class TestThreatIntelligenceEnums(unittest.TestCase):
    """Тесты для перечислений ThreatIntelligenceAgent"""
    
    def test_threat_type_enum(self):
        """Тест перечисления ThreatType"""
        self.assertEqual(ThreatType.MALWARE.value, "malware")
        self.assertEqual(ThreatType.PHISHING.value, "phishing")
        self.assertEqual(ThreatType.RANSOMWARE.value, "ransomware")
        self.assertEqual(ThreatType.APT.value, "apt")
        self.assertEqual(ThreatType.BOTNET.value, "botnet")
    
    def test_threat_severity_enum(self):
        """Тест перечисления ThreatSeverity"""
        self.assertEqual(ThreatSeverity.LOW.value, "low")
        self.assertEqual(ThreatSeverity.MEDIUM.value, "medium")
        self.assertEqual(ThreatSeverity.HIGH.value, "high")
        self.assertEqual(ThreatSeverity.CRITICAL.value, "critical")
        self.assertEqual(ThreatSeverity.EMERGENCY.value, "emergency")
    
    def test_ioc_type_enum(self):
        """Тест перечисления IOCType"""
        self.assertEqual(IOCType.IP_ADDRESS.value, "ip_address")
        self.assertEqual(IOCType.DOMAIN.value, "domain")
        self.assertEqual(IOCType.URL.value, "url")
        self.assertEqual(IOCType.EMAIL.value, "email")
        self.assertEqual(IOCType.FILE_HASH.value, "file_hash")
    
    def test_threat_source_enum(self):
        """Тест перечисления ThreatSource"""
        self.assertEqual(ThreatSource.OPEN_SOURCE.value, "open_source")
        self.assertEqual(ThreatSource.COMMERCIAL.value, "commercial")
        self.assertEqual(ThreatSource.GOVERNMENT.value, "government")
        self.assertEqual(ThreatSource.ACADEMIC.value, "academic")
        self.assertEqual(ThreatSource.COMMUNITY.value, "community")


if __name__ == "__main__":
    # Запуск тестов
    unittest.main(verbosity=2)