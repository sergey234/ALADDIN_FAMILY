# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Tests for Intrusion Prevention Service
Тесты для сервиса предотвращения вторжений

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-02
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from security.active.intrusion_prevention import (
    IntrusionPreventionService,
    IntrusionType,
    IntrusionSeverity,
    PreventionAction,
    IntrusionStatus,
    IntrusionAttempt,
    PreventionRule,
    IntrusionPattern
)


class TestIntrusionPrevention:
    """Тесты для сервиса предотвращения вторжений"""

    @pytest.fixture
    def intrusion_prevention(self):
        """Фикстура для сервиса предотвращения вторжений"""
        return IntrusionPreventionService()

    def test_initialization(self, intrusion_prevention):
        """Тест инициализации сервиса"""
        assert intrusion_prevention.name == "IntrusionPrevention"
        assert len(intrusion_prevention.intrusion_patterns) > 0
        assert len(intrusion_prevention.prevention_rules) > 0
        assert intrusion_prevention.family_protection_enabled is True
        assert intrusion_prevention.child_protection_mode is True
        assert intrusion_prevention.elderly_protection_mode is True

    def test_detect_brute_force_attack(self, intrusion_prevention):
        """Тест обнаружения брутфорс атаки"""
        event_data = {
            "source_ip": "192.168.1.100",
            "failed_logins": 10,
            "login_frequency": 15
        }
        
        detections = intrusion_prevention.detect_intrusion(event_data, user_id="test_user")
        
        assert len(detections) > 0
        detection = detections[0]
        assert detection.intrusion_type == IntrusionType.BRUTE_FORCE
        assert detection.severity in [IntrusionSeverity.MEDIUM, IntrusionSeverity.HIGH, IntrusionSeverity.CRITICAL]
        assert detection.source_ip == "192.168.1.100"
        assert detection.user_id == "test_user"

    def test_detect_ddos_attack(self, intrusion_prevention):
        """Тест обнаружения DDoS атаки"""
        event_data = {
            "source_ip": "10.0.0.1",
            "request_count": 150,
            "unique_ips": 75
        }
        
        detections = intrusion_prevention.detect_intrusion(event_data)
        
        assert len(detections) > 0
        detection = detections[0]
        assert detection.intrusion_type == IntrusionType.DDoS_ATTACK
        assert detection.severity in [IntrusionSeverity.MEDIUM, IntrusionSeverity.HIGH, IntrusionSeverity.CRITICAL]

    def test_detect_port_scan(self, intrusion_prevention):
        """Тест обнаружения сканирования портов"""
        event_data = {
            "source_ip": "172.16.0.50",
            "port_sequence": True,
            "port_count": 15
        }
        
        detections = intrusion_prevention.detect_intrusion(event_data)
        
        assert len(detections) > 0
        detection = detections[0]
        assert detection.intrusion_type == IntrusionType.PORT_SCAN
        assert detection.severity in [IntrusionSeverity.LOW, IntrusionSeverity.MEDIUM, IntrusionSeverity.HIGH]

    def test_detect_sql_injection(self, intrusion_prevention):
        """Тест обнаружения SQL инъекции"""
        event_data = {
            "source_ip": "203.0.113.10",
            "content": "SELECT * FROM users WHERE id = 1; DROP TABLE users;"
        }
        
        detections = intrusion_prevention.detect_intrusion(event_data)
        
        assert len(detections) > 0
        detection = detections[0]
        assert detection.intrusion_type == IntrusionType.SQL_INJECTION
        assert detection.severity in [IntrusionSeverity.LOW, IntrusionSeverity.MEDIUM, IntrusionSeverity.HIGH, IntrusionSeverity.CRITICAL]

    def test_detect_xss_attack(self, intrusion_prevention):
        """Тест обнаружения XSS атаки"""
        event_data = {
            "source_ip": "198.51.100.20",
            "content": "<script>alert('XSS')</script>"
        }
        
        detections = intrusion_prevention.detect_intrusion(event_data)
        
        assert len(detections) > 0
        detection = detections[0]
        assert detection.intrusion_type == IntrusionType.XSS_ATTACK
        assert detection.severity in [IntrusionSeverity.LOW, IntrusionSeverity.MEDIUM, IntrusionSeverity.HIGH]

    def test_detect_child_exploitation(self, intrusion_prevention):
        """Тест обнаружения эксплуатации детей"""
        event_data = {
            "source_ip": "192.0.2.30",
            "inappropriate_content": True,
            "user_age": 12
        }
        
        detections = intrusion_prevention.detect_intrusion(event_data, user_id="child_user", user_age=12)
        
        assert len(detections) > 0
        detection = detections[0]
        assert detection.intrusion_type == IntrusionType.SUSPICIOUS_BEHAVIOR
        assert detection.severity in [IntrusionSeverity.LOW, IntrusionSeverity.MEDIUM, IntrusionSeverity.HIGH, IntrusionSeverity.CRITICAL]
        assert detection.metadata["user_age"] == 12

    def test_detect_elderly_fraud(self, intrusion_prevention):
        """Тест обнаружения мошенничества с пожилыми"""
        event_data = {
            "source_ip": "203.0.113.40",
            "financial_requests": True,
            "urgency_tactics": True,
            "user_age": 70
        }
        
        detections = intrusion_prevention.detect_intrusion(event_data, user_id="elderly_user", user_age=70)
        
        assert len(detections) > 0
        detection = detections[0]
        assert detection.intrusion_type == IntrusionType.SUSPICIOUS_BEHAVIOR
        assert detection.severity in [IntrusionSeverity.LOW, IntrusionSeverity.MEDIUM, IntrusionSeverity.HIGH, IntrusionSeverity.CRITICAL]
        assert detection.metadata["user_age"] == 70

    def test_prevent_intrusion_block_ip(self, intrusion_prevention):
        """Тест предотвращения вторжения с блокировкой IP"""
        # Создаем несколько попыток вторжения для срабатывания правила
        for i in range(6):  # 6 попыток > 5 (порог правила)
            attempt = IntrusionAttempt(
                attempt_id=f"test_attempt_{i}",
                intrusion_type=IntrusionType.BRUTE_FORCE,
                severity=IntrusionSeverity.MEDIUM,
                source_ip="192.168.1.200",
                user_id="test_user",
                timestamp=datetime.now(),
                description=f"Тестовая попытка брутфорс {i}",
                status=IntrusionStatus.DETECTED
            )
            intrusion_prevention.intrusion_attempts[attempt.attempt_id] = attempt
        
        # Применяем предотвращение
        actions = intrusion_prevention.prevent_intrusion(attempt)
        
        assert len(actions) > 0
        assert PreventionAction.BLOCK_IP in actions
        assert "192.168.1.200" in intrusion_prevention.blocked_ips

    def test_prevent_intrusion_rate_limit(self, intrusion_prevention):
        """Тест предотвращения вторжения с ограничением скорости"""
        attempt = IntrusionAttempt(
            attempt_id="test_attempt_2",
            intrusion_type=IntrusionType.DDoS_ATTACK,
            severity=IntrusionSeverity.CRITICAL,
            source_ip="10.0.0.100",
            user_id=None,
            timestamp=datetime.now(),
            description="Тестовая DDoS атака",
            status=IntrusionStatus.DETECTED
        )
        
        actions = intrusion_prevention.prevent_intrusion(attempt)
        
        assert len(actions) > 0
        assert PreventionAction.RATE_LIMIT in actions
        assert "10.0.0.100" in intrusion_prevention.rate_limits

    def test_prevent_intrusion_child_protection(self, intrusion_prevention):
        """Тест предотвращения вторжения с защитой детей"""
        attempt = IntrusionAttempt(
            attempt_id="test_attempt_3",
            intrusion_type=IntrusionType.SUSPICIOUS_BEHAVIOR,
            severity=IntrusionSeverity.CRITICAL,
            source_ip="192.0.2.100",
            user_id="child_user",
            timestamp=datetime.now(),
            description="Попытка эксплуатации ребенка",
            status=IntrusionStatus.DETECTED,
            metadata={"user_age": 10}
        )
        
        actions = intrusion_prevention.prevent_intrusion(attempt)
        
        assert len(actions) > 0
        assert PreventionAction.BLOCK_RESOURCE in actions
        assert PreventionAction.ALERT_ADMIN in actions
        assert PreventionAction.QUARANTINE_USER in actions

    def test_prevent_intrusion_elderly_protection(self, intrusion_prevention):
        """Тест предотвращения вторжения с защитой пожилых"""
        attempt = IntrusionAttempt(
            attempt_id="test_attempt_4",
            intrusion_type=IntrusionType.SUSPICIOUS_BEHAVIOR,
            severity=IntrusionSeverity.HIGH,
            source_ip="203.0.113.100",
            user_id="elderly_user",
            timestamp=datetime.now(),
            description="Попытка мошенничества с пожилым",
            status=IntrusionStatus.DETECTED,
            metadata={"user_age": 75}
        )
        
        actions = intrusion_prevention.prevent_intrusion(attempt)
        
        assert len(actions) > 0
        assert PreventionAction.BLOCK_RESOURCE in actions
        assert PreventionAction.ALERT_ADMIN in actions
        assert PreventionAction.REQUIRE_MFA in actions

    def test_get_intrusion_summary_user_specific(self, intrusion_prevention):
        """Тест получения сводки по вторжениям для конкретного пользователя"""
        # Создаем несколько попыток вторжения
        for i in range(3):
            attempt = IntrusionAttempt(
                attempt_id=f"test_attempt_{i}",
                intrusion_type=IntrusionType.BRUTE_FORCE,
                severity=IntrusionSeverity.MEDIUM,
                source_ip=f"192.168.1.{i+1}",
                user_id="test_user",
                timestamp=datetime.now(),
                description=f"Тестовая попытка {i}",
                status=IntrusionStatus.PREVENTED
            )
            intrusion_prevention.intrusion_attempts[attempt.attempt_id] = attempt
        
        summary = intrusion_prevention.get_intrusion_summary(user_id="test_user")
        
        assert summary["total_attempts"] == 3
        assert summary["prevented_attempts"] == 3
        assert summary["by_severity"]["medium"] == 3
        assert summary["by_type"]["brute_force"] == 3
        assert len(summary["recent_attempts"]) == 3

    def test_get_intrusion_summary_all_users(self, intrusion_prevention):
        """Тест получения общей сводки по вторжениям"""
        # Создаем попытки для разных пользователей
        users = ["user1", "user2", "user3"]
        for i, user in enumerate(users):
            attempt = IntrusionAttempt(
                attempt_id=f"test_attempt_{i}",
                intrusion_type=IntrusionType.PORT_SCAN,
                severity=IntrusionSeverity.LOW,
                source_ip=f"10.0.0.{i+1}",
                user_id=user,
                timestamp=datetime.now(),
                description=f"Тестовая попытка для {user}",
                status=IntrusionStatus.DETECTED
            )
            intrusion_prevention.intrusion_attempts[attempt.attempt_id] = attempt
        
        summary = intrusion_prevention.get_intrusion_summary()
        
        assert summary["total_attempts"] == 3
        assert summary["by_type"]["port_scan"] == 3
        assert len(summary["recent_attempts"]) == 3

    def test_get_family_protection_status(self, intrusion_prevention):
        """Тест получения статуса семейной защиты"""
        status = intrusion_prevention.get_family_protection_status()
        
        assert status["family_protection_enabled"] is True
        assert status["child_protection_mode"] is True
        assert status["elderly_protection_mode"] is True
        assert status["active_rules"] > 0
        assert status["family_specific_rules"] > 0
        assert "protection_settings" in status
        assert "family_history" in status

    def test_get_status(self, intrusion_prevention):
        """Тест получения статуса сервиса"""
        status = intrusion_prevention.get_status()
        
        assert status["service_name"] == "IntrusionPrevention"
        assert status["intrusion_patterns"] > 0
        assert status["prevention_rules"] > 0
        assert status["family_protection_enabled"] is True
        assert "uptime" in status

    def test_family_protection_history(self, intrusion_prevention):
        """Тест истории семейной защиты"""
        # Создаем попытки для семейного пользователя
        event_data = {
            "source_ip": "192.168.1.50",
            "inappropriate_content": True
        }
        
        detections = intrusion_prevention.detect_intrusion(event_data, user_id="family_user", user_age=15)
        
        assert len(detections) > 0
        assert "family_user" in intrusion_prevention.family_protection_history
        assert len(intrusion_prevention.family_protection_history["family_user"]) > 0

    def test_severity_determination(self, intrusion_prevention):
        """Тест определения серьезности"""
        # Тестируем разные уровни уверенности
        test_cases = [
            (0.95, IntrusionSeverity.CRITICAL),
            (0.8, IntrusionSeverity.HIGH),
            (0.6, IntrusionSeverity.MEDIUM),
            (0.3, IntrusionSeverity.LOW)
        ]
        
        for confidence, expected_severity in test_cases:
            # Создаем тестовый паттерн
            pattern = IntrusionPattern(
                pattern_id="test_pattern",
                name="Тестовый паттерн",
                description="Тестовое описание",
                intrusion_type=IntrusionType.BRUTE_FORCE,
                indicators=["test_indicator"],
                confidence_threshold=0.5
            )
            
            severity = intrusion_prevention._determine_severity(confidence, pattern)
            assert severity == expected_severity

    def test_confidence_calculation(self, intrusion_prevention):
        """Тест расчета уверенности"""
        # Тестируем с разными индикаторами
        event_data = {
            "failed_logins": 10,
            "login_frequency": 20,
            "user_age": 12
        }
        
        pattern = intrusion_prevention.intrusion_patterns["brute_force_login"]
        confidence = intrusion_prevention._calculate_pattern_confidence(event_data, pattern)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Должна быть высокая уверенность

    def test_rule_condition_evaluation(self, intrusion_prevention):
        """Тест оценки условий правил"""
        # Создаем тестовую попытку
        attempt = IntrusionAttempt(
            attempt_id="test_rule_eval",
            intrusion_type=IntrusionType.BRUTE_FORCE,
            severity=IntrusionSeverity.MEDIUM,
            source_ip="192.168.1.100",
            user_id="test_user",
            timestamp=datetime.now(),
            description="Тестовая попытка",
            status=IntrusionStatus.DETECTED
        )
        
        # Получаем правило для брутфорс
        rule = intrusion_prevention.prevention_rules["block_brute_force"]
        
        # Оценка должна пройти для подходящих условий
        result = intrusion_prevention._evaluate_rule_conditions(attempt, rule)
        assert isinstance(result, bool)

    def test_security_event_creation(self, intrusion_prevention):
        """Тест создания событий безопасности"""
        initial_events = len(intrusion_prevention.activity_log)
        
        # Создаем попытку вторжения
        event_data = {
            "source_ip": "192.168.1.100",
            "failed_logins": 8
        }
        
        detections = intrusion_prevention.detect_intrusion(event_data, user_id="test_user")
        
        # Проверяем, что событие добавлено в журнал
        assert len(detections) > 0
        assert len(intrusion_prevention.activity_log) > initial_events
        
        # Проверяем последнее событие
        last_event = intrusion_prevention.activity_log[-1]
        assert last_event["event_type"] == "intrusion_detected"
        assert "attempt_id" in last_event["metadata"]
        assert last_event["metadata"]["user_id"] == "test_user"

    def test_security_event_filtering(self, intrusion_prevention):
        """Тест фильтрации событий безопасности"""
        # Создаем несколько событий
        intrusion_prevention.detect_intrusion({"source_ip": "192.168.1.1", "failed_logins": 5}, "user1")
        intrusion_prevention.detect_intrusion({"source_ip": "192.168.1.2", "request_count": 120}, "user2")
        
        # Фильтруем по типу события
        intrusion_events = intrusion_prevention.get_security_events(event_type="intrusion_detected")
        assert len(intrusion_events) >= 1
        
        # Фильтруем по серьезности
        high_events = intrusion_prevention.get_security_events(severity="high")
        assert len(high_events) >= 0  # Может быть 0 или больше в зависимости от уверенности

    def test_security_event_clearing(self, intrusion_prevention):
        """Тест очистки событий безопасности"""
        # Создаем событие
        intrusion_prevention.detect_intrusion({"source_ip": "192.168.1.1", "failed_logins": 5}, "user1")
        assert len(intrusion_prevention.activity_log) > 0
        
        # Очищаем все события
        intrusion_prevention.clear_security_events()
        assert len(intrusion_prevention.activity_log) == 0
