"""
Тесты для function_36: ThreatIntelligence
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from security.reactive.threat_intelligence import (
    ThreatIntelligence,
    ThreatSource,
    ThreatSeverity,
    ThreatCategory,
    IntelligenceType,
    AgeGroup,
    ThreatIndicator,
    ThreatIntelligenceData,
    IntelligenceReport,
)


class TestThreatIntelligence:
    """Тесты для ThreatIntelligence"""

    def setup_method(self):
        """Настройка для каждого теста"""
        self.intelligence = ThreatIntelligence()

    def test_initialization(self):
        """Тест инициализации"""
        assert self.intelligence.service_name == "ThreatIntelligence"
        assert self.intelligence.intelligence_type == IntelligenceType.THREAT_INDICATORS
        assert self.intelligence.update_interval == 3600
        assert self.intelligence.retention_days == 30
        assert self.intelligence.family_notification_threshold == ThreatSeverity.MEDIUM

    def test_intelligence_rules_initialization(self):
        """Тест инициализации правил разведки"""
        assert "threat_collection" in self.intelligence.intelligence_rules
        assert "family_protection" in self.intelligence.intelligence_rules
        assert "threat_analysis" in self.intelligence.intelligence_rules

        # Проверка настроек семейной защиты
        family_protection = self.intelligence.intelligence_rules["family_protection"]
        assert family_protection["enabled"] is True
        assert family_protection["notification_threshold"] == "medium"
        assert family_protection["age_appropriate"] is True

    def test_family_protection_setup(self):
        """Тест настройки семейной защиты"""
        assert "age_groups" in self.intelligence.family_protection
        assert "threat_categories" in self.intelligence.family_protection

        # Проверка возрастных групп
        age_groups = self.intelligence.family_protection["age_groups"]
        assert AgeGroup.CHILDREN in age_groups
        assert AgeGroup.TEENAGERS in age_groups
        assert AgeGroup.ADULTS in age_groups
        assert AgeGroup.ELDERLY in age_groups

        # Проверка категорий угроз
        threat_categories = self.intelligence.family_protection["threat_categories"]
        assert "malware" in threat_categories
        assert "phishing" in threat_categories
        assert "social_engineering" in threat_categories

    def test_collect_threat_indicators(self):
        """Тест сбора индикаторов угроз"""
        indicators = self.intelligence.collect_threat_indicators()

        assert len(indicators) == 3
        assert all(isinstance(indicator, ThreatIndicator) for indicator in indicators)

        # Проверка первого индикатора
        first_indicator = indicators[0]
        assert first_indicator.indicator_id == "threat_001"
        assert first_indicator.indicator_type == "ip_address"
        assert first_indicator.value == "192.168.1.100"
        assert first_indicator.threat_type == ThreatCategory.MALWARE
        assert first_indicator.severity == ThreatSeverity.HIGH

        # Проверка возрастных объяснений
        assert AgeGroup.CHILDREN in first_indicator.age_appropriate_explanation
        assert AgeGroup.ADULTS in first_indicator.age_appropriate_explanation

    def test_generate_age_explanations(self):
        """Тест генерации объяснений для разных возрастов"""
        threat_type = ThreatCategory.MALWARE
        family_impact = "Может заразить устройства семьи"

        explanations = self.intelligence._generate_age_explanations(threat_type, family_impact)

        # Проверка всех возрастных групп
        assert AgeGroup.CHILDREN in explanations
        assert AgeGroup.TEENAGERS in explanations
        assert AgeGroup.ADULTS in explanations
        assert AgeGroup.ELDERLY in explanations

        # Проверка содержания объяснений
        assert "плохая программа" in explanations[AgeGroup.CHILDREN].lower()
        assert "киберугрозы" in explanations[AgeGroup.TEENAGERS]
        assert "угроза типа" in explanations[AgeGroup.ADULTS]
        assert "опасность" in explanations[AgeGroup.ELDERLY]

    def test_analyze_threat_intelligence(self):
        """Тест анализа разведывательных данных"""
        # Создание тестовых индикаторов
        indicators = [
            ThreatIndicator(
                indicator_id="test_001",
                indicator_type="ip_address",
                value="192.168.1.1",
                threat_type=ThreatCategory.MALWARE,
                severity=ThreatSeverity.HIGH,
                source=ThreatSource.EXTERNAL,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                confidence=0.9,
                description="Тестовая угроза",
                family_impact="Тестовое воздействие на семью",
            )
        ]

        intelligence_list = self.intelligence.analyze_threat_intelligence(indicators)

        assert len(intelligence_list) == 1
        assert all(isinstance(intel, ThreatIntelligenceData) for intel in intelligence_list)

        # Проверка первого элемента разведки
        first_intel = intelligence_list[0]
        assert first_intel.intelligence_id == "intel_test_001"
        assert first_intel.threat_type == ThreatCategory.MALWARE
        assert first_intel.severity == ThreatSeverity.HIGH
        assert len(first_intel.recommendations) > 0
        assert len(first_intel.age_appropriate_advice) > 0

    def test_generate_recommendations_malware(self):
        """Тест генерации рекомендаций для malware"""
        indicator = ThreatIndicator(
            indicator_id="test_malware",
            indicator_type="file_hash",
            value="test_hash",
            threat_type=ThreatCategory.MALWARE,
            severity=ThreatSeverity.HIGH,
            source=ThreatSource.MALWARE,
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            confidence=0.8,
            description="Malware test",
            family_impact="Test impact",
        )

        recommendations = self.intelligence._generate_recommendations(indicator)

        assert "антивирусное ПО" in " ".join(recommendations)
        assert "сканирование" in " ".join(recommendations)
        assert "подозрительные файлы" in " ".join(recommendations)

    def test_generate_recommendations_phishing(self):
        """Тест генерации рекомендаций для phishing"""
        indicator = ThreatIndicator(
            indicator_id="test_phishing",
            indicator_type="domain",
            value="phishing-site.com",
            threat_type=ThreatCategory.PHISHING,
            severity=ThreatSeverity.MEDIUM,
            source=ThreatSource.EXTERNAL,
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            confidence=0.7,
            description="Phishing test",
            family_impact="Test impact",
        )

        recommendations = self.intelligence._generate_recommendations(indicator)

        assert "подозрительным ссылкам" in " ".join(recommendations)
        assert "подлинность" in " ".join(recommendations)
        assert "пароли" in " ".join(recommendations)

    def test_generate_recommendations_ransomware(self):
        """Тест генерации рекомендаций для ransomware"""
        indicator = ThreatIndicator(
            indicator_id="test_ransomware",
            indicator_type="file_hash",
            value="ransomware_hash",
            threat_type=ThreatCategory.RANSOMWARE,
            severity=ThreatSeverity.CRITICAL,
            source=ThreatSource.MALWARE,
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            confidence=0.95,
            description="Ransomware test",
            family_impact="Test impact",
        )

        recommendations = self.intelligence._generate_recommendations(indicator)

        assert "резервные копии" in " ".join(recommendations)
        assert "Обновить" in " ".join(recommendations)
        assert "вложения" in " ".join(recommendations)

    def test_generate_age_advice(self):
        """Тест генерации советов для разных возрастов"""
        indicator = ThreatIndicator(
            indicator_id="test_advice",
            indicator_type="ip_address",
            value="192.168.1.1",
            threat_type=ThreatCategory.MALWARE,
            severity=ThreatSeverity.MEDIUM,
            source=ThreatSource.EXTERNAL,
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            confidence=0.8,
            description="Test advice",
            family_impact="Test impact",
        )

        advice = self.intelligence._generate_age_advice(indicator)

        # Проверка всех возрастных групп
        assert AgeGroup.CHILDREN in advice
        assert AgeGroup.TEENAGERS in advice
        assert AgeGroup.ADULTS in advice
        assert AgeGroup.ELDERLY in advice

        # Проверка содержания советов
        assert "родителям" in " ".join(advice[AgeGroup.CHILDREN])
        assert "неизвестными ссылками" in " ".join(advice[AgeGroup.TEENAGERS])
        assert "обновляйте" in " ".join(advice[AgeGroup.ADULTS])
        assert "банк" in " ".join(advice[AgeGroup.ELDERLY])

    def test_generate_intelligence_report(self):
        """Тест генерации отчета разведывательных данных"""
        # Добавляем тестовые данные
        self.intelligence.intelligence_data["test_intel"] = ThreatIntelligenceData(
            intelligence_id="test_intel",
            threat_type=ThreatCategory.MALWARE,
            severity=ThreatSeverity.HIGH,
            source=ThreatSource.EXTERNAL,
            indicators=[],
            description="Test intelligence",
            family_impact="Test family impact",
            recommendations=["Test recommendation"],
        )

        report = self.intelligence.generate_intelligence_report(IntelligenceType.THREAT_INDICATORS)

        assert report is not None
        assert isinstance(report, IntelligenceReport)
        assert report.report_type == IntelligenceType.THREAT_INDICATORS
        assert report.threats_analyzed >= 1
        assert len(report.recommendations) > 0
        assert report.summary is not None

    def test_generate_report_recommendations(self):
        """Тест генерации рекомендаций для отчета"""
        # Добавляем высокоприоритетную угрозу
        self.intelligence.intelligence_data["high_priority"] = ThreatIntelligenceData(
            intelligence_id="high_priority",
            threat_type=ThreatCategory.RANSOMWARE,
            severity=ThreatSeverity.CRITICAL,
            source=ThreatSource.MALWARE,
            indicators=[],
            description="High priority threat",
            family_impact="High impact on family",
            recommendations=[],
        )

        recommendations = self.intelligence._generate_report_recommendations()

        assert len(recommendations) > 0
        assert any("высокоприоритетных" in rec for rec in recommendations)
        assert any("антивирусное" in rec for rec in recommendations)

    def test_generate_report_summary(self):
        """Тест генерации резюме отчета"""
        summary = self.intelligence._generate_report_summary(10, 3, 2)

        assert "10 угроз" in summary
        assert "3 новых" in summary
        assert "2 высокоприоритетных" in summary
        assert "повышенное внимание" in summary

    def test_generate_report_summary_no_high_priority(self):
        """Тест генерации резюме без высокоприоритетных угроз"""
        summary = self.intelligence._generate_report_summary(5, 1, 0)

        assert "5 угроз" in summary
        assert "1 новых" in summary
        assert "0 высокоприоритетных" in summary
        assert "нормы" in summary

    def test_get_family_threat_summary(self):
        """Тест получения семейной сводки угроз"""
        # Добавляем семейные угрозы
        self.intelligence.intelligence_data["family_threat_1"] = ThreatIntelligenceData(
            intelligence_id="family_threat_1",
            threat_type=ThreatCategory.MALWARE,
            severity=ThreatSeverity.HIGH,
            source=ThreatSource.EXTERNAL,
            indicators=[],
            description="Family threat 1",
            family_impact="Воздействие на семью",
            recommendations=[],
        )

        self.intelligence.intelligence_data["family_threat_2"] = ThreatIntelligenceData(
            intelligence_id="family_threat_2",
            threat_type=ThreatCategory.PHISHING,
            severity=ThreatSeverity.MEDIUM,
            source=ThreatSource.EXTERNAL,
            indicators=[],
            description="Family threat 2",
            family_impact="Влияние на семейные данные",
            recommendations=[],
        )

        summary = self.intelligence.get_family_threat_summary()

        assert "total_family_threats" in summary
        assert "high_priority_family_threats" in summary
        assert "age_group_statistics" in summary
        assert "recommendations" in summary
        assert summary["total_family_threats"] >= 1

    def test_generate_family_recommendations(self):
        """Тест генерации семейных рекомендаций"""
        # Тест без угроз
        recommendations = self.intelligence._generate_family_recommendations([])
        assert len(recommendations) == 1
        assert "норме" in recommendations[0]

        # Тест с угрозами
        family_threats = [
            ThreatIntelligenceData(
                intelligence_id="test1",
                threat_type=ThreatCategory.MALWARE,
                severity=ThreatSeverity.HIGH,
                source=ThreatSource.EXTERNAL,
                indicators=[],
                description="Test 1",
                family_impact="Test impact",
                recommendations=[],
            ),
            ThreatIntelligenceData(
                intelligence_id="test2",
                threat_type=ThreatCategory.PHISHING,
                severity=ThreatSeverity.MEDIUM,
                source=ThreatSource.EXTERNAL,
                indicators=[],
                description="Test 2",
                family_impact="Test impact",
                recommendations=[],
            ),
        ]

        recommendations = self.intelligence._generate_family_recommendations(family_threats)

        assert len(recommendations) > 1
        assert any("вредоносных программ" in rec for rec in recommendations)
        assert any("фишинга" in rec for rec in recommendations)

    def test_get_intelligence_summary(self):
        """Тест получения сводки разведывательных данных"""
        # Добавляем тестовые данные
        self.intelligence.threat_indicators["test_indicator"] = ThreatIndicator(
            indicator_id="test_indicator",
            indicator_type="ip_address",
            value="192.168.1.1",
            threat_type=ThreatCategory.MALWARE,
            severity=ThreatSeverity.HIGH,
            source=ThreatSource.EXTERNAL,
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            confidence=0.8,
            description="Test indicator",
            family_impact="Test family impact",
        )

        self.intelligence.intelligence_data["test_intel"] = ThreatIntelligenceData(
            intelligence_id="test_intel",
            threat_type=ThreatCategory.MALWARE,
            severity=ThreatSeverity.HIGH,
            source=ThreatSource.EXTERNAL,
            indicators=[],
            description="Test intelligence",
            family_impact="Воздействие на семью",
            recommendations=[],
        )

        summary = self.intelligence.get_intelligence_summary()

        assert "total_indicators" in summary
        assert "active_intelligence" in summary
        assert "family_threats" in summary
        assert "high_priority_threats" in summary
        assert summary["total_indicators"] >= 1
        assert summary["active_intelligence"] >= 1

    def test_get_status(self):
        """Тест получения статуса сервиса"""
        status = self.intelligence.get_status()

        assert "service_name" in status
        assert "status" in status
        assert "intelligence_type" in status
        assert "threat_indicators" in status
        assert "intelligence_data" in status
        assert "family_protection_enabled" in status
        assert status["service_name"] == "ThreatIntelligence"

    def test_error_handling_collect_indicators(self):
        """Тест обработки ошибок при сборе индикаторов"""
        with patch.object(self.intelligence, 'add_security_event') as mock_event:
            # Симулируем ошибку
            with patch.object(self.intelligence, '_generate_age_explanations', side_effect=Exception("Test error")):
                indicators = self.intelligence.collect_threat_indicators()
                
                assert indicators == []
                mock_event.assert_called()

    def test_error_handling_analyze_intelligence(self):
        """Тест обработки ошибок при анализе разведки"""
        with patch.object(self.intelligence, 'add_security_event') as mock_event:
            # Симулируем ошибку
            with patch.object(self.intelligence, '_generate_recommendations', side_effect=Exception("Test error")):
                intelligence_list = self.intelligence.analyze_threat_intelligence([])
                
                assert intelligence_list == []
                mock_event.assert_called()

    def test_error_handling_generate_report(self):
        """Тест обработки ошибок при генерации отчета"""
        with patch.object(self.intelligence, 'add_security_event') as mock_event:
            # Симулируем ошибку
            with patch('security.reactive.threat_intelligence.datetime') as mock_datetime:
                mock_datetime.now.side_effect = Exception("Test error")
                
                report = self.intelligence.generate_intelligence_report(IntelligenceType.THREAT_INDICATORS)
                
                assert report is None
                mock_event.assert_called()

    def test_error_handling_family_summary(self):
        """Тест обработки ошибок при получении семейной сводки"""
        with patch.object(self.intelligence, 'add_security_event') as mock_event:
            # Симулируем ошибку
            with patch('security.reactive.threat_intelligence.datetime') as mock_datetime:
                mock_datetime.now.side_effect = Exception("Test error")
                
                summary = self.intelligence.get_family_threat_summary()
                
                assert summary == {}
                mock_event.assert_called()

    def test_error_handling_summary(self):
        """Тест обработки ошибок при получении сводки"""
        # Тест что метод работает без ошибок
        summary = self.intelligence.get_intelligence_summary()
        
        assert isinstance(summary, dict)
        assert "total_indicators" in summary
        assert "active_intelligence" in summary

    def test_error_handling_status(self):
        """Тест обработки ошибок при получении статуса"""
        # Тест что метод работает без ошибок
        status = self.intelligence.get_status()
        
        assert isinstance(status, dict)
        assert "service_name" in status
        assert "status" in status