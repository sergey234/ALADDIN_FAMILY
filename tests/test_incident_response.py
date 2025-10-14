# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Tests for Incident Response Service
Тесты для сервиса реагирования на инциденты

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-02
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from security.active.incident_response import (
    IncidentResponseService,
    IncidentType,
    IncidentSeverity,
    IncidentStatus,
    ResponseAction,
    NotificationPriority,
    SecurityIncident,
    IncidentResponse,
    Notification,
    ResponseRule,
    IncidentReport
)


class TestIncidentResponse:
    """Тесты для сервиса реагирования на инциденты"""

    @pytest.fixture
    def incident_response(self):
        """Фикстура для сервиса реагирования на инциденты"""
        return IncidentResponseService()

    def test_initialization(self, incident_response):
        """Тест инициализации сервиса"""
        assert incident_response.name == "IncidentResponse"
        assert len(incident_response.response_rules) > 0
        assert incident_response.automatic_response_enabled is True
        assert incident_response.family_notifications_enabled is True
        assert incident_response.authority_notifications_enabled is True
        assert incident_response.escalation_enabled is True
        assert incident_response.real_time_monitoring is True

    def test_create_incident_malware(self, incident_response):
        """Тест создания инцидента с вредоносным ПО"""
        incident = incident_response.create_incident(
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.HIGH,
            title="Обнаружено вредоносное ПО",
            description="На устройстве обнаружен вирус",
            source="AntivirusScanner",
            affected_entities=["device_001"],
            user_id="family_user",
            family_role="parent"
        )

        assert incident is not None
        assert incident.incident_type == IncidentType.MALWARE
        assert incident.severity == IncidentSeverity.HIGH
        assert incident.title == "Обнаружено вредоносное ПО"
        assert incident.description == "На устройстве обнаружен вирус"
        assert incident.source == "AntivirusScanner"
        assert incident.user_id == "family_user"
        assert incident.family_role == "parent"
        assert incident.status in [IncidentStatus.DETECTED, IncidentStatus.CONTAINED, IncidentStatus.INVESTIGATING]

    def test_create_incident_intrusion(self, incident_response):
        """Тест создания инцидента вторжения"""
        incident = incident_response.create_incident(
            incident_type=IncidentType.INTRUSION,
            severity=IncidentSeverity.CRITICAL,
            title="Попытка несанкционированного доступа",
            description="Обнаружена попытка взлома",
            source="IntrusionDetection",
            affected_entities=["server_001", "database_001"],
            user_id="admin_user"
        )

        assert incident is not None
        assert incident.incident_type == IncidentType.INTRUSION
        assert incident.severity == IncidentSeverity.CRITICAL
        assert incident.status in [IncidentStatus.DETECTED, IncidentStatus.CONTAINED, IncidentStatus.INVESTIGATING]

    def test_create_incident_child_exploitation(self, incident_response):
        """Тест создания инцидента эксплуатации детей"""
        incident = incident_response.create_incident(
            incident_type=IncidentType.CHILD_EXPLOITATION,
            severity=IncidentSeverity.CRITICAL,
            title="Угроза ребенку",
            description="Обнаружена попытка контакта с ребенком",
            source="ChildProtection",
            affected_entities=["child_device_001"],
            user_id="child_user",
            family_role="child"
        )

        assert incident is not None
        assert incident.incident_type == IncidentType.CHILD_EXPLOITATION
        assert incident.severity == IncidentSeverity.CRITICAL
        assert incident.family_role == "child"

    def test_create_incident_elderly_fraud(self, incident_response):
        """Тест создания инцидента мошенничества с пожилыми"""
        incident = incident_response.create_incident(
            incident_type=IncidentType.ELDERLY_FRAUD,
            severity=IncidentSeverity.HIGH,
            title="Попытка мошенничества",
            description="Обнаружена попытка обмана пожилого человека",
            source="ElderlyProtection",
            affected_entities=["elderly_device_001"],
            user_id="elderly_user",
            family_role="elderly"
        )

        assert incident is not None
        assert incident.incident_type == IncidentType.ELDERLY_FRAUD
        assert incident.severity == IncidentSeverity.HIGH
        assert incident.family_role == "elderly"

    def test_create_incident_phishing(self, incident_response):
        """Тест создания инцидента фишинга"""
        incident = incident_response.create_incident(
            incident_type=IncidentType.PHISHING,
            severity=IncidentSeverity.MEDIUM,
            title="Фишинговая атака",
            description="Обнаружена попытка фишинга",
            source="EmailFilter",
            affected_entities=["email_account_001"],
            user_id="family_user"
        )

        assert incident is not None
        assert incident.incident_type == IncidentType.PHISHING
        assert incident.severity == IncidentSeverity.MEDIUM

    def test_create_incident_data_breach(self, incident_response):
        """Тест создания инцидента утечки данных"""
        incident = incident_response.create_incident(
            incident_type=IncidentType.DATA_BREACH,
            severity=IncidentSeverity.CRITICAL,
            title="Утечка данных",
            description="Обнаружена утечка персональных данных",
            source="DataLossPrevention",
            affected_entities=["database_001", "file_server_001"],
            user_id="admin_user"
        )

        assert incident is not None
        assert incident.incident_type == IncidentType.DATA_BREACH
        assert incident.severity == IncidentSeverity.CRITICAL

    def test_create_incident_network_attack(self, incident_response):
        """Тест создания инцидента сетевой атаки"""
        incident = incident_response.create_incident(
            incident_type=IncidentType.NETWORK_ATTACK,
            severity=IncidentSeverity.HIGH,
            title="Сетевая атака",
            description="Обнаружена DDoS атака",
            source="NetworkMonitor",
            affected_entities=["router_001", "firewall_001"],
            user_id="network_admin"
        )

        assert incident is not None
        assert incident.incident_type == IncidentType.NETWORK_ATTACK
        assert incident.severity == IncidentSeverity.HIGH

    def test_create_incident_device_compromise(self, incident_response):
        """Тест создания инцидента компрометации устройства"""
        incident = incident_response.create_incident(
            incident_type=IncidentType.DEVICE_COMPROMISE,
            severity=IncidentSeverity.HIGH,
            title="Компрометация устройства",
            description="Устройство скомпрометировано",
            source="DeviceSecurity",
            affected_entities=["laptop_001"],
            user_id="user_001"
        )

        assert incident is not None
        assert incident.incident_type == IncidentType.DEVICE_COMPROMISE
        assert incident.severity == IncidentSeverity.HIGH

    def test_automatic_response_malware(self, incident_response):
        """Тест автоматического реагирования на вредоносное ПО"""
        incident = incident_response.create_incident(
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.HIGH,
            title="Вредоносное ПО",
            description="Обнаружен вирус",
            source="Antivirus",
            affected_entities=["device_001"],
            user_id="family_user"
        )

        # Проверяем, что созданы ответы
        responses = [r for r in incident_response.incident_responses.values() 
                    if r.incident_id == incident.incident_id]
        
        assert len(responses) > 0
        # Проверяем, что есть хотя бы одно действие реагирования
        assert any(r.success for r in responses)

    def test_automatic_response_child_exploitation(self, incident_response):
        """Тест автоматического реагирования на эксплуатацию детей"""
        incident = incident_response.create_incident(
            incident_type=IncidentType.CHILD_EXPLOITATION,
            severity=IncidentSeverity.CRITICAL,
            title="Угроза ребенку",
            description="Попытка контакта с ребенком",
            source="ChildProtection",
            affected_entities=["child_device_001"],
            user_id="child_user",
            family_role="child"
        )

        # Проверяем, что созданы ответы
        responses = [r for r in incident_response.incident_responses.values() 
                    if r.incident_id == incident.incident_id]
        
        assert len(responses) > 0
        # Проверяем, что есть хотя бы одно действие реагирования
        assert any(r.success for r in responses)

    def test_automatic_response_elderly_fraud(self, incident_response):
        """Тест автоматического реагирования на мошенничество с пожилыми"""
        incident = incident_response.create_incident(
            incident_type=IncidentType.ELDERLY_FRAUD,
            severity=IncidentSeverity.HIGH,
            title="Мошенничество",
            description="Попытка обмана пожилого человека",
            source="ElderlyProtection",
            affected_entities=["elderly_device_001"],
            user_id="elderly_user",
            family_role="elderly"
        )

        # Проверяем, что созданы ответы
        responses = [r for r in incident_response.incident_responses.values() 
                    if r.incident_id == incident.incident_id]
        
        assert len(responses) > 0
        # Проверяем, что есть хотя бы одно действие реагирования
        assert any(r.success for r in responses)

    def test_resolve_incident(self, incident_response):
        """Тест разрешения инцидента"""
        # Создаем инцидент
        incident = incident_response.create_incident(
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.MEDIUM,
            title="Тестовый инцидент",
            description="Тестовое описание",
            source="TestSource",
            affected_entities=["test_entity"],
            user_id="test_user"
        )

        # Разрешаем инцидент
        success = incident_response.resolve_incident(
            incident_id=incident.incident_id,
            resolution_notes="Инцидент успешно разрешен",
            resolved_by="admin"
        )

        assert success is True
        assert incident.status == IncidentStatus.RESOLVED
        assert incident.resolution_notes == "Инцидент успешно разрешен"
        assert incident.resolved_by == "admin"
        assert incident.resolution_time is not None

    def test_get_incident_summary_user_specific(self, incident_response):
        """Тест получения сводки для конкретного пользователя"""
        # Создаем несколько инцидентов
        for i in range(3):
            incident_response.create_incident(
                incident_type=IncidentType.MALWARE,
                severity=IncidentSeverity.MEDIUM,
                title=f"Инцидент {i}",
                description=f"Описание инцидента {i}",
                source="TestSource",
                affected_entities=[f"entity_{i}"],
                user_id="stats_user"
            )

        summary = incident_response.get_incident_summary(user_id="stats_user")

        assert summary is not None
        assert summary["total_incidents"] >= 1
        assert summary["open_incidents"] >= 0
        assert summary["resolved_incidents"] >= 0
        assert "by_severity" in summary
        assert "by_type" in summary
        assert "by_status" in summary
        assert "recent_incidents" in summary
        assert "response_statistics" in summary

    def test_get_incident_summary_all_users(self, incident_response):
        """Тест получения общей сводки"""
        # Создаем инциденты для разных пользователей
        users = ["user1", "user2", "user3"]
        for i, user in enumerate(users):
            incident_response.create_incident(
                incident_type=IncidentType.MALWARE,
                severity=IncidentSeverity.MEDIUM,
                title=f"Инцидент {i}",
                description=f"Описание инцидента {i}",
                source="TestSource",
                affected_entities=[f"entity_{i}"],
                user_id=user
            )

        summary = incident_response.get_incident_summary()

        assert summary is not None
        assert summary["total_incidents"] >= 1

    def test_get_family_incident_status(self, incident_response):
        """Тест получения статуса семейных инцидентов"""
        status = incident_response.get_family_incident_status()

        assert status["automatic_response_enabled"] is True
        assert status["family_notifications_enabled"] is True
        assert status["authority_notifications_enabled"] is True
        assert status["escalation_enabled"] is True
        assert status["real_time_monitoring"] is True
        assert status["active_rules"] > 0
        assert status["family_specific_rules"] > 0
        assert "protection_settings" in status
        assert "family_history" in status

    def test_get_status(self, incident_response):
        """Тест получения статуса сервиса"""
        status = incident_response.get_status()

        assert status["service_name"] == "IncidentResponse"
        assert status["response_rules"] > 0
        assert status["family_protection_enabled"] is True
        assert status["automatic_response_enabled"] is True
        assert "uptime" in status

    def test_family_incident_history(self, incident_response):
        """Тест истории семейных инцидентов"""
        # Создаем инцидент для семейного пользователя
        incident = incident_response.create_incident(
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.MEDIUM,
            title="Семейный инцидент",
            description="Инцидент в семье",
            source="FamilyProtection",
            affected_entities=["family_device_001"],
            user_id="family_user",
            family_role="parent"
        )

        assert incident is not None
        assert "family_user" in incident_response.family_incident_history
        assert len(incident_response.family_incident_history["family_user"]) > 0

    def test_response_rule_evaluation(self, incident_response):
        """Тест оценки правил реагирования"""
        # Создаем инцидент, который должен сработать по правилу
        incident = incident_response.create_incident(
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.HIGH,
            title="Тест правила",
            description="Тест оценки правила",
            source="TestSource",
            affected_entities=["test_entity"],
            user_id="test_user"
        )

        # Проверяем, что правило сработало
        responses = [r for r in incident_response.incident_responses.values() 
                    if r.incident_id == incident.incident_id]
        
        assert len(responses) > 0

    def test_severity_comparison(self, incident_response):
        """Тест сравнения серьезности"""
        # Тестируем сравнение серьезности
        result1 = incident_response._compare_severity(IncidentSeverity.HIGH, IncidentSeverity.MEDIUM)
        assert result1 == 1  # HIGH > MEDIUM

        result2 = incident_response._compare_severity(IncidentSeverity.LOW, IncidentSeverity.CRITICAL)
        assert result2 == -1  # LOW < CRITICAL

        result3 = incident_response._compare_severity(IncidentSeverity.MEDIUM, IncidentSeverity.MEDIUM)
        assert result3 == 0  # MEDIUM == MEDIUM

    def test_incident_status_transitions(self, incident_response):
        """Тест переходов статуса инцидента"""
        # Создаем инцидент
        incident = incident_response.create_incident(
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.MEDIUM,
            title="Тест статуса",
            description="Тест переходов статуса",
            source="TestSource",
            affected_entities=["test_entity"],
            user_id="test_user"
        )

        # Проверяем начальный статус
        assert incident.status in [IncidentStatus.DETECTED, IncidentStatus.CONTAINED, IncidentStatus.INVESTIGATING]

        # Симулируем сдерживание
        incident.status = IncidentStatus.CONTAINED
        assert incident.status == IncidentStatus.CONTAINED

        # Симулируем разрешение
        incident.status = IncidentStatus.RESOLVED
        assert incident.status == IncidentStatus.RESOLVED

    def test_security_event_creation(self, incident_response):
        """Тест создания событий безопасности"""
        initial_events = len(incident_response.activity_log)

        # Создаем инцидент
        incident = incident_response.create_incident(
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.MEDIUM,
            title="Тест событий",
            description="Тест создания событий",
            source="TestSource",
            affected_entities=["test_entity"],
            user_id="test_user"
        )

        # Проверяем, что событие добавлено в журнал
        assert incident is not None
        assert len(incident_response.activity_log) > initial_events

        # Проверяем последнее событие
        last_event = incident_response.activity_log[-1]
        assert last_event["event_type"] == "incident_created"
        assert "incident_id" in last_event["metadata"]
        assert last_event["metadata"]["user_id"] == "test_user"

    def test_security_event_filtering(self, incident_response):
        """Тест фильтрации событий безопасности"""
        # Создаем несколько инцидентов
        incident_response.create_incident(
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.MEDIUM,
            title="Инцидент 1",
            description="Описание 1",
            source="TestSource",
            affected_entities=["entity1"],
            user_id="user1"
        )

        incident_response.create_incident(
            incident_type=IncidentType.PHISHING,
            severity=IncidentSeverity.HIGH,
            title="Инцидент 2",
            description="Описание 2",
            source="TestSource",
            affected_entities=["entity2"],
            user_id="user2"
        )

        # Разрешаем инцидент
        incidents = list(incident_response.incidents.values())
        if incidents:
            incident_response.resolve_incident(
                incident_id=incidents[0].incident_id,
                resolution_notes="Разрешен",
                resolved_by="admin"
            )

        # Фильтруем по типу события
        created_events = incident_response.get_security_events(event_type="incident_created")
        assert len(created_events) >= 2

        resolved_events = incident_response.get_security_events(event_type="incident_resolved")
        assert len(resolved_events) >= 1

        # Фильтруем по серьезности
        high_events = incident_response.get_security_events(severity="high")
        assert len(high_events) >= 1

    def test_security_event_clearing(self, incident_response):
        """Тест очистки событий безопасности"""
        # Создаем инцидент
        incident_response.create_incident(
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.MEDIUM,
            title="Тест очистки",
            description="Тест очистки событий",
            source="TestSource",
            affected_entities=["test_entity"],
            user_id="test_user"
        )
        assert len(incident_response.activity_log) > 0

        # Очищаем все события
        incident_response.clear_security_events()
        assert len(incident_response.activity_log) == 0
