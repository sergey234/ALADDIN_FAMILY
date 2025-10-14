"""
Тесты для function_37: ForensicsService
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from security.reactive.forensics_service import (
    ForensicsService,
    EvidenceType,
    InvestigationStatus,
    IncidentType,
    EvidencePriority,
    AgeGroup,
    Evidence,
    Investigation,
    ForensicsReport,
)


class TestForensicsService:
    """Тесты для ForensicsService"""

    def setup_method(self):
        """Настройка для каждого теста"""
        self.forensics = ForensicsService()

    def test_initialization(self):
        """Тест инициализации"""
        assert self.forensics.service_name == "ForensicsService"
        assert self.forensics.investigation_timeout == 3600
        assert self.forensics.auto_investigation_enabled is True
        assert self.forensics.evidence_retention_days == 90
        assert self.forensics.family_notification_enabled is True

    def test_forensics_rules_initialization(self):
        """Тест инициализации правил расследования"""
        assert "investigation" in self.forensics.forensics_rules
        assert "family_protection" in self.forensics.forensics_rules
        assert "evidence_collection" in self.forensics.forensics_rules

        # Проверка настроек расследования
        investigation = self.forensics.forensics_rules["investigation"]
        assert investigation["enabled"] is True
        assert investigation["auto_start"] is True
        assert investigation["timeout"] == 3600

    def test_family_protection_setup(self):
        """Тест настройки семейной защиты"""
        assert "age_groups" in self.forensics.family_protection
        assert "incident_types" in self.forensics.family_protection

        # Проверка возрастных групп
        age_groups = self.forensics.family_protection["age_groups"]
        assert AgeGroup.CHILDREN in age_groups
        assert AgeGroup.TEENAGERS in age_groups
        assert AgeGroup.ADULTS in age_groups
        assert AgeGroup.ELDERLY in age_groups

        # Проверка типов инцидентов
        incident_types = self.forensics.family_protection["incident_types"]
        assert "malware_infection" in incident_types
        assert "data_breach" in incident_types
        assert "phishing_attempt" in incident_types

    def test_start_investigation(self):
        """Тест начала расследования"""
        incident_data = {"source": "test_system", "severity": "high"}
        
        investigation = self.forensics.start_investigation(
            IncidentType.MALWARE_INFECTION, 
            incident_data
        )

        assert isinstance(investigation, Investigation)
        assert investigation.incident_type == IncidentType.MALWARE_INFECTION
        assert investigation.status == InvestigationStatus.IN_PROGRESS
        assert investigation.investigation_id in self.forensics.active_investigations
        assert "семьи" in investigation.family_impact_assessment

    def test_assess_family_impact(self):
        """Тест оценки воздействия на семью"""
        incident_data = {"source": "test_system"}
        
        # Тест для malware
        impact = self.forensics._assess_family_impact(IncidentType.MALWARE_INFECTION, incident_data)
        assert "семьи" in impact
        assert "заразить" in impact

        # Тест для data breach
        impact = self.forensics._assess_family_impact(IncidentType.DATA_BREACH, incident_data)
        assert "семьи" in impact
        assert "данных" in impact

        # Тест для phishing
        impact = self.forensics._assess_family_impact(IncidentType.PHISHING_ATTEMPT, incident_data)
        assert "семьи" in impact
        assert "обмана" in impact

    def test_collect_evidence(self):
        """Тест сбора доказательств"""
        # Создаем расследование
        investigation = self.forensics.start_investigation(
            IncidentType.MALWARE_INFECTION, 
            {"source": "test_system"}
        )

        # Собираем доказательство
        evidence_data = {"file_path": "/tmp/suspicious.exe", "size": 1024}
        evidence = self.forensics.collect_evidence(
            investigation.investigation_id,
            EvidenceType.MEMORY_DUMP,
            "test_system",
            evidence_data
        )

        assert isinstance(evidence, Evidence)
        assert evidence.evidence_type == EvidenceType.MEMORY_DUMP
        assert evidence.source == "test_system"
        assert evidence.data == evidence_data
        assert evidence.evidence_id in self.forensics.evidence_storage

    def test_determine_evidence_priority(self):
        """Тест определения приоритета доказательства"""
        # Высокий приоритет
        priority = self.forensics._determine_evidence_priority(EvidenceType.MEMORY_DUMP, {})
        assert priority == EvidencePriority.HIGH

        # Средний приоритет
        priority = self.forensics._determine_evidence_priority(EvidenceType.LOG_FILE, {})
        assert priority == EvidencePriority.MEDIUM

        # Низкий приоритет
        priority = self.forensics._determine_evidence_priority(EvidenceType.BROWSER_HISTORY, {})
        assert priority == EvidencePriority.LOW

    def test_assess_evidence_family_impact(self):
        """Тест оценки воздействия доказательства на семью"""
        # Тест для memory dump
        impact = self.forensics._assess_evidence_family_impact(EvidenceType.MEMORY_DUMP, {})
        assert "семьи" in impact
        assert "информацию" in impact

        # Тест для user activity
        impact = self.forensics._assess_evidence_family_impact(EvidenceType.USER_ACTIVITY, {})
        assert "семьи" in impact
        assert "активность" in impact

    def test_generate_evidence_explanations(self):
        """Тест генерации объяснений доказательств"""
        explanations = self.forensics._generate_evidence_explanations(EvidenceType.MEMORY_DUMP, {})

        # Проверка всех возрастных групп
        assert AgeGroup.CHILDREN in explanations
        assert AgeGroup.TEENAGERS in explanations
        assert AgeGroup.ADULTS in explanations
        assert AgeGroup.ELDERLY in explanations

        # Проверка содержания объяснений
        assert "семью" in explanations[AgeGroup.CHILDREN]
        assert "доказательства" in explanations[AgeGroup.TEENAGERS]
        assert "приоритет" in explanations[AgeGroup.ADULTS]
        assert "киберугроз" in explanations[AgeGroup.ELDERLY]

    def test_analyze_evidence(self):
        """Тест анализа доказательств"""
        # Создаем расследование и добавляем доказательства
        investigation = self.forensics.start_investigation(
            IncidentType.MALWARE_INFECTION, 
            {"source": "test_system"}
        )

        # Добавляем доказательства
        self.forensics.collect_evidence(
            investigation.investigation_id,
            EvidenceType.MEMORY_DUMP,
            "test_system",
            {"data": "test"}
        )

        # Анализируем доказательства
        findings = self.forensics.analyze_evidence(investigation.investigation_id)

        assert isinstance(findings, list)
        assert len(findings) > 0
        assert any("памяти" in finding for finding in findings)

    def test_analyze_single_evidence(self):
        """Тест анализа отдельного доказательства"""
        evidence = Evidence(
            evidence_id="test_evidence",
            evidence_type=EvidenceType.MEMORY_DUMP,
            source="test_system",
            timestamp=datetime.now(),
            description="Test evidence",
            priority=EvidencePriority.HIGH,
            data={"test": "data"},
            family_impact="Test impact",
        )

        finding = self.forensics._analyze_single_evidence(evidence)
        assert "памяти" in finding
        assert "test_system" in finding

    def test_complete_investigation(self):
        """Тест завершения расследования"""
        # Создаем расследование
        investigation = self.forensics.start_investigation(
            IncidentType.MALWARE_INFECTION, 
            {"source": "test_system"}
        )

        # Добавляем доказательства
        self.forensics.collect_evidence(
            investigation.investigation_id,
            EvidenceType.MEMORY_DUMP,
            "test_system",
            {"data": "test"}
        )

        # Анализируем доказательства
        self.forensics.analyze_evidence(investigation.investigation_id)

        # Завершаем расследование
        completed_investigation = self.forensics.complete_investigation(investigation.investigation_id)

        assert completed_investigation.status == InvestigationStatus.COMPLETED
        assert completed_investigation.end_time is not None
        assert len(completed_investigation.recommendations) > 0
        assert len(completed_investigation.age_appropriate_summary) > 0
        assert investigation.investigation_id in self.forensics.completed_investigations

    def test_generate_recommendations(self):
        """Тест генерации рекомендаций"""
        investigation = Investigation(
            investigation_id="test_investigation",
            incident_type=IncidentType.MALWARE_INFECTION,
            status=InvestigationStatus.COMPLETED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            evidence=[],
            findings=[],
            recommendations=[],
            family_impact_assessment="Test impact",
        )

        recommendations = self.forensics._generate_recommendations(investigation)

        assert len(recommendations) > 0
        assert any("мониторинг" in rec for rec in recommendations)
        assert any("антивирусное" in rec for rec in recommendations)
        assert any("сканирование" in rec for rec in recommendations)

    def test_generate_age_summaries(self):
        """Тест генерации возрастных сводок"""
        investigation = Investigation(
            investigation_id="test_investigation",
            incident_type=IncidentType.MALWARE_INFECTION,
            status=InvestigationStatus.COMPLETED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            evidence=[],
            findings=[],
            recommendations=[],
            family_impact_assessment="Test impact",
        )

        summaries = self.forensics._generate_age_summaries(investigation)

        # Проверка всех возрастных групп
        assert AgeGroup.CHILDREN in summaries
        assert AgeGroup.TEENAGERS in summaries
        assert AgeGroup.ADULTS in summaries
        assert AgeGroup.ELDERLY in summaries

        # Проверка содержания сводок
        assert "семью" in summaries[AgeGroup.CHILDREN]
        assert "Расследование" in summaries[AgeGroup.TEENAGERS]
        assert "доказательств" in summaries[AgeGroup.ADULTS]
        assert "безопасности" in summaries[AgeGroup.ELDERLY]

    def test_generate_forensics_report(self):
        """Тест генерации отчета расследования"""
        # Создаем и завершаем расследование
        investigation = self.forensics.start_investigation(
            IncidentType.MALWARE_INFECTION, 
            {"source": "test_system"}
        )

        self.forensics.collect_evidence(
            investigation.investigation_id,
            EvidenceType.MEMORY_DUMP,
            "test_system",
            {"data": "test"}
        )

        self.forensics.analyze_evidence(investigation.investigation_id)
        self.forensics.complete_investigation(investigation.investigation_id)

        # Генерируем отчет
        report = self.forensics.generate_forensics_report(investigation.investigation_id)

        assert report is not None
        assert isinstance(report, ForensicsReport)
        assert report.investigation_id == investigation.investigation_id
        assert report.incident_type == IncidentType.MALWARE_INFECTION
        assert report.evidence_collected > 0
        assert len(report.executive_summary) > 0
        assert len(report.technical_details) > 0
        assert len(report.family_summary) > 0

    def test_determine_family_impact_level(self):
        """Тест определения уровня воздействия на семью"""
        investigation = Investigation(
            investigation_id="test_investigation",
            incident_type=IncidentType.MALWARE_INFECTION,
            status=InvestigationStatus.COMPLETED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            evidence=[],
            findings=[],
            recommendations=[],
            family_impact_assessment="Критическое воздействие на семью",
        )

        impact_level = self.forensics._determine_family_impact_level(investigation)
        assert impact_level == "critical"

    def test_generate_executive_summary(self):
        """Тест генерации исполнительного резюме"""
        investigation = Investigation(
            investigation_id="test_investigation",
            incident_type=IncidentType.MALWARE_INFECTION,
            status=InvestigationStatus.COMPLETED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            evidence=[Mock(), Mock()],
            findings=["finding1", "finding2"],
            recommendations=["rec1", "rec2", "rec3"],
            family_impact_assessment="Test impact",
        )

        summary = self.forensics._generate_executive_summary(investigation)
        assert "malware_infection" in summary
        assert "2 доказательств" in summary
        assert "2 проблем" in summary
        assert "3 мер" in summary

    def test_generate_technical_details(self):
        """Тест генерации технических деталей"""
        investigation = Investigation(
            investigation_id="test_investigation",
            incident_type=IncidentType.MALWARE_INFECTION,
            status=InvestigationStatus.COMPLETED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            evidence=[Mock(), Mock()],
            findings=["finding1"],
            recommendations=["rec1"],
            family_impact_assessment="Test impact",
        )

        details = self.forensics._generate_technical_details(investigation)
        assert "test_investigation" in details
        assert "malware_infection" in details
        assert "2" in details  # evidence count
        assert "1" in details  # findings count

    def test_generate_family_summary(self):
        """Тест генерации семейной сводки"""
        investigation = Investigation(
            investigation_id="test_investigation",
            incident_type=IncidentType.MALWARE_INFECTION,
            status=InvestigationStatus.COMPLETED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            evidence=[],
            findings=[],
            recommendations=["rec1", "rec2"],
            family_impact_assessment="Test impact",
        )

        summary = self.forensics._generate_family_summary(investigation)
        assert "malware_infection" in summary
        assert "Test impact" in summary
        assert "2 мер" in summary

    def test_generate_age_reports(self):
        """Тест генерации возрастных отчетов"""
        investigation = Investigation(
            investigation_id="test_investigation",
            incident_type=IncidentType.MALWARE_INFECTION,
            status=InvestigationStatus.COMPLETED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            evidence=[Mock()],
            findings=["finding1"],
            recommendations=[],
            family_impact_assessment="Test impact",
        )

        reports = self.forensics._generate_age_reports(investigation)
        
        # Проверка всех возрастных групп
        assert AgeGroup.CHILDREN in reports
        assert AgeGroup.TEENAGERS in reports
        assert AgeGroup.ADULTS in reports
        assert AgeGroup.ELDERLY in reports

        # Проверка содержания отчетов
        assert "безопасности" in reports[AgeGroup.CHILDREN]
        assert "malware_infection" in reports[AgeGroup.TEENAGERS]
        assert "доказательств" in reports[AgeGroup.ADULTS]
        assert "безопасности" in reports[AgeGroup.ELDERLY]

    def test_get_family_incident_summary(self):
        """Тест получения семейной сводки инцидентов"""
        # Добавляем семейные инциденты
        family_investigation = Investigation(
            investigation_id="family_investigation",
            incident_type=IncidentType.MALWARE_INFECTION,
            status=InvestigationStatus.COMPLETED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            evidence=[],
            findings=[],
            recommendations=[],
            family_impact_assessment="Воздействие на семью",
            age_appropriate_summary={AgeGroup.CHILDREN: "Test summary"},
        )

        self.forensics.completed_investigations["family_investigation"] = family_investigation

        summary = self.forensics.get_family_incident_summary()

        assert "total_family_incidents" in summary
        assert "critical_family_incidents" in summary
        assert "age_group_statistics" in summary
        assert "recommendations" in summary
        assert summary["total_family_incidents"] >= 0

    def test_generate_family_recommendations(self):
        """Тест генерации семейных рекомендаций"""
        # Тест без инцидентов
        recommendations = self.forensics._generate_family_recommendations([])
        assert len(recommendations) == 1
        assert "норме" in recommendations[0]

        # Тест с инцидентами
        family_incidents = [
            Investigation(
                investigation_id="test1",
                incident_type=IncidentType.MALWARE_INFECTION,
                status=InvestigationStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                evidence=[],
                findings=[],
                recommendations=[],
                family_impact_assessment="Test impact",
            ),
            Investigation(
                investigation_id="test2",
                incident_type=IncidentType.DATA_BREACH,
                status=InvestigationStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                evidence=[],
                findings=[],
                recommendations=[],
                family_impact_assessment="Test impact",
            ),
        ]

        recommendations = self.forensics._generate_family_recommendations(family_incidents)

        assert len(recommendations) > 1
        assert any("вредоносных программ" in rec for rec in recommendations)
        assert any("личных данных" in rec for rec in recommendations)

    def test_get_forensics_summary(self):
        """Тест получения сводки расследований"""
        summary = self.forensics.get_forensics_summary()

        assert "total_investigations" in summary
        assert "active_investigations" in summary
        assert "completed_investigations" in summary
        assert "evidence_collected" in summary
        assert "family_incidents" in summary
        assert "auto_investigation_enabled" in summary
        assert "evidence_retention_days" in summary

    def test_get_status(self):
        """Тест получения статуса сервиса"""
        status = self.forensics.get_status()

        assert "service_name" in status
        assert "status" in status
        assert "active_investigations" in status
        assert "completed_investigations" in status
        assert "evidence_collected" in status
        assert "family_protection_enabled" in status
        assert status["service_name"] == "ForensicsService"

    def test_error_handling_start_investigation(self):
        """Тест обработки ошибок при начале расследования"""
        with patch.object(self.forensics, 'add_security_event') as mock_event:
            # Симулируем ошибку
            with patch('security.reactive.forensics_service.datetime') as mock_datetime:
                mock_datetime.now.side_effect = Exception("Test error")
                
                with pytest.raises(Exception):
                    self.forensics.start_investigation(IncidentType.MALWARE_INFECTION, {})
                
                mock_event.assert_called()

    def test_error_handling_collect_evidence(self):
        """Тест обработки ошибок при сборе доказательств"""
        with patch.object(self.forensics, 'add_security_event') as mock_event:
            # Симулируем ошибку
            with patch('security.reactive.forensics_service.datetime') as mock_datetime:
                mock_datetime.now.side_effect = Exception("Test error")
                
                with pytest.raises(Exception):
                    self.forensics.collect_evidence("nonexistent", EvidenceType.MEMORY_DUMP, "source", {})
                
                mock_event.assert_called()

    def test_error_handling_analyze_evidence(self):
        """Тест обработки ошибок при анализе доказательств"""
        with patch.object(self.forensics, 'add_security_event') as mock_event:
            # Симулируем ошибку
            with patch.object(self.forensics, '_analyze_single_evidence', side_effect=Exception("Test error")):
                with pytest.raises(Exception):
                    self.forensics.analyze_evidence("nonexistent")
                
                mock_event.assert_called()

    def test_error_handling_complete_investigation(self):
        """Тест обработки ошибок при завершении расследования"""
        with patch.object(self.forensics, 'add_security_event') as mock_event:
            # Симулируем ошибку
            with patch('security.reactive.forensics_service.datetime') as mock_datetime:
                mock_datetime.now.side_effect = Exception("Test error")
                
                with pytest.raises(Exception):
                    self.forensics.complete_investigation("nonexistent")
                
                mock_event.assert_called()

    def test_error_handling_generate_report(self):
        """Тест обработки ошибок при генерации отчета"""
        with patch.object(self.forensics, 'add_security_event') as mock_event:
            # Симулируем ошибку
            with patch('security.reactive.forensics_service.datetime') as mock_datetime:
                mock_datetime.now.side_effect = Exception("Test error")
                
                report = self.forensics.generate_forensics_report("nonexistent")
                
                assert report is None
                mock_event.assert_called()

    def test_error_handling_family_summary(self):
        """Тест обработки ошибок при получении семейной сводки"""
        # Тест что метод работает без ошибок
        summary = self.forensics.get_family_incident_summary()
        
        assert isinstance(summary, dict)
        assert "total_family_incidents" in summary
        assert "age_group_statistics" in summary

    def test_error_handling_summary(self):
        """Тест обработки ошибок при получении сводки"""
        # Тест что метод работает без ошибок
        summary = self.forensics.get_forensics_summary()
        
        assert isinstance(summary, dict)
        assert "total_investigations" in summary
        assert "active_investigations" in summary

    def test_error_handling_status(self):
        """Тест обработки ошибок при получении статуса"""
        # Тест что метод работает без ошибок
        status = self.forensics.get_status()
        
        assert isinstance(status, dict)
        assert "service_name" in status
        assert "status" in status