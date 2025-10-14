# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Tests for Device Security Service
Тесты для сервиса безопасности устройств

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-02
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from security.active.device_security import (
    DeviceSecurityService,
    DeviceType,
    SecurityStatus,
    ThreatLevel,
    SecurityAction,
    DeviceProfile,
    SecurityVulnerability,
    SecurityRule,
    DeviceSecurityReport
)


class TestDeviceSecurity:
    """Тесты для сервиса безопасности устройств"""

    @pytest.fixture
    def device_security(self):
        """Фикстура для сервиса безопасности устройств"""
        return DeviceSecurityService()

    def test_initialization(self, device_security):
        """Тест инициализации сервиса"""
        assert device_security.name == "DeviceSecurity"
        assert len(device_security.security_rules) > 0
        assert device_security.security_scanning_enabled is True
        assert device_security.automatic_updates is True
        assert device_security.family_protection_enabled is True
        assert device_security.child_device_monitoring is True
        assert device_security.elderly_device_monitoring is True
        assert device_security.real_time_monitoring is True

    def test_register_device_desktop(self, device_security):
        """Тест регистрации настольного устройства"""
        device_profile = device_security.register_device(
            device_name="Family Desktop",
            device_type=DeviceType.DESKTOP,
            operating_system="Windows 10",
            os_version="10.0.19041",
            user_id="family_user",
            family_role="parent"
        )

        assert device_profile is not None
        assert device_profile.device_name == "Family Desktop"
        assert device_profile.device_type == DeviceType.DESKTOP
        assert device_profile.operating_system == "Windows 10"
        assert device_profile.os_version == "10.0.19041"
        assert device_profile.user_id == "family_user"
        assert device_profile.family_role == "parent"
        assert device_profile.security_status == SecurityStatus.UNKNOWN
        assert device_profile.security_score >= 0.5

    def test_register_device_laptop(self, device_security):
        """Тест регистрации ноутбука"""
        device_profile = device_security.register_device(
            device_name="Work Laptop",
            device_type=DeviceType.LAPTOP,
            operating_system="macOS",
            os_version="12.0",
            user_id="work_user"
        )

        assert device_profile is not None
        assert device_profile.device_type == DeviceType.LAPTOP
        assert device_profile.operating_system == "macOS"
        assert device_profile.user_id == "work_user"

    def test_register_device_mobile(self, device_security):
        """Тест регистрации мобильного устройства"""
        device_profile = device_security.register_device(
            device_name="Child Phone",
            device_type=DeviceType.MOBILE,
            operating_system="Android",
            os_version="11.0",
            user_id="child_user",
            family_role="child"
        )

        assert device_profile is not None
        assert device_profile.device_type == DeviceType.MOBILE
        assert device_profile.operating_system == "Android"
        assert device_profile.family_role == "child"

    def test_register_device_tablet(self, device_security):
        """Тест регистрации планшета"""
        device_profile = device_security.register_device(
            device_name="Elderly Tablet",
            device_type=DeviceType.TABLET,
            operating_system="iOS",
            os_version="15.0",
            user_id="elderly_user",
            family_role="elderly"
        )

        assert device_profile is not None
        assert device_profile.device_type == DeviceType.TABLET
        assert device_profile.operating_system == "iOS"
        assert device_profile.family_role == "elderly"

    def test_register_device_iot(self, device_security):
        """Тест регистрации IoT устройства"""
        device_profile = device_security.register_device(
            device_name="Smart Camera",
            device_type=DeviceType.IOT,
            operating_system="Linux",
            os_version="4.19.0",
            user_id="family_user"
        )

        assert device_profile is not None
        assert device_profile.device_type == DeviceType.IOT
        assert device_profile.operating_system == "Linux"

    def test_register_device_router(self, device_security):
        """Тест регистрации роутера"""
        device_profile = device_security.register_device(
            device_name="Home Router",
            device_type=DeviceType.ROUTER,
            operating_system="OpenWrt",
            os_version="21.02.0",
            user_id="admin_user"
        )

        assert device_profile is not None
        assert device_profile.device_type == DeviceType.ROUTER
        assert device_profile.operating_system == "OpenWrt"

    def test_scan_device_security(self, device_security):
        """Тест сканирования безопасности устройства"""
        # Регистрируем устройство
        device_profile = device_security.register_device(
            device_name="Test Device",
            device_type=DeviceType.DESKTOP,
            operating_system="Windows 10",
            os_version="10.0.19041",
            user_id="test_user"
        )

        # Сканируем безопасность
        report = device_security.scan_device_security(device_profile.device_id)

        assert report is not None
        assert report.device_id == device_profile.device_id
        assert report.security_score >= 0.0
        assert report.security_score <= 1.0
        assert report.vulnerabilities_found >= 0
        assert report.vulnerabilities_critical >= 0
        assert report.vulnerabilities_high >= 0
        assert report.vulnerabilities_medium >= 0
        assert report.vulnerabilities_low >= 0
        assert isinstance(report.recommendations, list)
        assert report.compliance_status in ["compliant", "mostly_compliant", "partially_compliant", "non_compliant"]

    def test_scan_device_security_child_device(self, device_security):
        """Тест сканирования детского устройства"""
        device_profile = device_security.register_device(
            device_name="child_device_with_bad_content",
            device_type=DeviceType.MOBILE,
            operating_system="Android",
            os_version="11.0",
            user_id="child_user",
            family_role="child"
        )

        report = device_security.scan_device_security(device_profile.device_id)

        assert report is not None
        assert report.vulnerabilities_found > 0
        assert report.vulnerabilities_critical > 0

    def test_scan_device_security_elderly_device(self, device_security):
        """Тест сканирования устройства пожилого человека"""
        device_profile = device_security.register_device(
            device_name="elderly_device_suspicious",
            device_type=DeviceType.DESKTOP,
            operating_system="Windows 10",
            os_version="10.0.19041",
            user_id="elderly_user",
            family_role="elderly"
        )

        report = device_security.scan_device_security(device_profile.device_id)

        assert report is not None
        assert report.vulnerabilities_found > 0
        assert report.vulnerabilities_high > 0

    def test_scan_device_security_outdated_software(self, device_security):
        """Тест сканирования устройства с устаревшим ПО"""
        device_profile = device_security.register_device(
            device_name="device_needs_update",
            device_type=DeviceType.DESKTOP,
            operating_system="Windows 10",
            os_version="10.0.19041",
            user_id="test_user"
        )

        # Добавляем устаревшее ПО
        device_profile.installed_software = ["python2", "java8", "flash"]

        report = device_security.scan_device_security(device_profile.device_id)

        assert report is not None
        assert report.vulnerabilities_found > 0
        assert report.vulnerabilities_medium > 0

    def test_scan_device_security_critical_vulnerability(self, device_security):
        """Тест сканирования устройства с критической уязвимостью"""
        device_profile = device_security.register_device(
            device_name="device_critical_vuln",
            device_type=DeviceType.DESKTOP,
            operating_system="Windows 10",
            os_version="10.0.19041",
            user_id="test_user"
        )

        report = device_security.scan_device_security(device_profile.device_id)

        assert report is not None
        assert report.vulnerabilities_found > 0
        assert report.vulnerabilities_high > 0

    def test_get_device_security_summary_user_specific(self, device_security):
        """Тест получения сводки для конкретного пользователя"""
        # Регистрируем несколько устройств
        for i in range(3):
            device_security.register_device(
                device_name=f"Device {i}",
                device_type=DeviceType.DESKTOP,
                operating_system="Windows 10",
                os_version="10.0.19041",
                user_id="stats_user"
            )

        summary = device_security.get_device_security_summary(user_id="stats_user")

        assert summary is not None
        assert summary["total_devices"] >= 1  # Минимум одно устройство должно быть зарегистрировано
        assert summary["average_security_score"] >= 0.0
        assert summary["average_security_score"] <= 1.0
        assert "by_device_type" in summary
        assert "by_security_status" in summary
        assert "recent_scans" in summary

    def test_get_device_security_summary_all_users(self, device_security):
        """Тест получения общей сводки"""
        # Регистрируем устройства для разных пользователей
        users = ["user1", "user2", "user3"]
        for i, user in enumerate(users):
            device_security.register_device(
                device_name=f"Device {i}",
                device_type=DeviceType.DESKTOP,
                operating_system="Windows 10",
                os_version="10.0.19041",
                user_id=user
            )

        summary = device_security.get_device_security_summary()

        assert summary is not None
        assert summary["total_devices"] >= 2  # Минимум 2 устройства должны быть зарегистрированы

    def test_get_family_device_status(self, device_security):
        """Тест получения статуса семейных устройств"""
        status = device_security.get_family_device_status()

        assert status["security_scanning_enabled"] is True
        assert status["automatic_updates"] is True
        assert status["family_protection_enabled"] is True
        assert status["child_device_monitoring"] is True
        assert status["elderly_device_monitoring"] is True
        assert status["real_time_monitoring"] is True
        assert status["active_rules"] > 0
        assert status["family_specific_rules"] > 0
        assert "protection_settings" in status
        assert "family_history" in status

    def test_get_status(self, device_security):
        """Тест получения статуса сервиса"""
        status = device_security.get_status()

        assert status["service_name"] == "DeviceSecurity"
        assert status["security_rules"] > 0
        assert status["family_protection_enabled"] is True
        assert status["security_scanning_enabled"] is True
        assert "uptime" in status

    def test_family_device_history(self, device_security):
        """Тест истории семейных устройств"""
        # Регистрируем устройство для семейного пользователя
        device_profile = device_security.register_device(
            device_name="Family Device",
            device_type=DeviceType.DESKTOP,
            operating_system="Windows 10",
            os_version="10.0.19041",
            user_id="family_user",
            family_role="parent"
        )

        assert device_profile is not None
        assert "family_user" in device_security.family_device_history
        assert len(device_security.family_device_history["family_user"]) > 0

    def test_device_type_detection(self, device_security):
        """Тест определения типа устройства"""
        # Тестируем системное устройство
        device_info = device_security._get_system_device_info()
        
        assert device_info is not None
        assert "device_id" in device_info
        assert "device_name" in device_info
        assert "device_type" in device_info
        assert "os" in device_info
        assert "os_version" in device_info

    def test_security_score_calculation(self, device_security):
        """Тест расчета балла безопасности"""
        # Создаем тестовое устройство
        device_profile = DeviceProfile(
            device_id="test_device",
            device_name="Test Device",
            device_type=DeviceType.DESKTOP,
            operating_system="Windows 10",
            os_version="10.0.19041",
            hardware_info={},
            network_interfaces=[],
            installed_software=[],
            security_status=SecurityStatus.SECURE,
            family_role="child"
        )

        # Создаем уязвимости
        vulnerabilities = [
            SecurityVulnerability(
                vulnerability_id="vuln1",
                device_id="test_device",
                vulnerability_type="test_vuln",
                severity=ThreatLevel.CRITICAL,
                description="Test critical vulnerability"
            ),
            SecurityVulnerability(
                vulnerability_id="vuln2",
                device_id="test_device",
                vulnerability_type="test_vuln",
                severity=ThreatLevel.MEDIUM,
                description="Test medium vulnerability"
            )
        ]

        score = device_security._calculate_security_score(device_profile, vulnerabilities)

        assert 0.0 <= score <= 1.0
        assert score < 1.0  # Должен быть снижен из-за уязвимостей

    def test_recommendations_generation(self, device_security):
        """Тест генерации рекомендаций"""
        device_profile = DeviceProfile(
            device_id="test_device",
            device_name="Test Device",
            device_type=DeviceType.DESKTOP,
            operating_system="Windows 10",
            os_version="10.0.19041",
            hardware_info={},
            network_interfaces=[],
            installed_software=[],
            security_status=SecurityStatus.SECURE,
            family_role="child"
        )

        vulnerabilities = [
            SecurityVulnerability(
                vulnerability_id="vuln1",
                device_id="test_device",
                vulnerability_type="test_vuln",
                severity=ThreatLevel.HIGH,
                description="Test vulnerability",
                remediation="Fix the vulnerability"
            )
        ]

        recommendations = device_security._generate_recommendations(device_profile, vulnerabilities)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert "Fix the vulnerability" in recommendations
        assert "Включить родительский контроль" in recommendations

    def test_compliance_status_check(self, device_security):
        """Тест проверки статуса соответствия"""
        device_profile = DeviceProfile(
            device_id="test_device",
            device_name="Test Device",
            device_type=DeviceType.DESKTOP,
            operating_system="Windows 10",
            os_version="10.0.19041",
            hardware_info={},
            network_interfaces=[],
            installed_software=[],
            security_status=SecurityStatus.SECURE,
            security_score=0.9
        )

        compliance = device_security._check_compliance_status(device_profile)

        assert compliance == "compliant"

    def test_family_protection_status(self, device_security):
        """Тест статуса семейной защиты"""
        device_profile = DeviceProfile(
            device_id="test_device",
            device_name="Test Device",
            device_type=DeviceType.DESKTOP,
            operating_system="Windows 10",
            os_version="10.0.19041",
            hardware_info={},
            network_interfaces=[],
            installed_software=[],
            security_status=SecurityStatus.SECURE,
            user_id="test_user",
            family_role="child"
        )

        status = device_security._get_family_protection_status(device_profile)

        assert status["family_protection_enabled"] is True
        assert status["user_id"] == "test_user"
        assert status["family_role"] == "child"
        assert status["child_protection"] is True
        assert status["elderly_protection"] is False

    def test_security_event_creation(self, device_security):
        """Тест создания событий безопасности"""
        initial_events = len(device_security.activity_log)

        # Регистрируем устройство
        device_profile = device_security.register_device(
            device_name="Test Device",
            device_type=DeviceType.DESKTOP,
            operating_system="Windows 10",
            os_version="10.0.19041",
            user_id="test_user"
        )

        # Проверяем, что событие добавлено в журнал
        assert device_profile is not None
        assert len(device_security.activity_log) > initial_events

        # Проверяем последнее событие
        last_event = device_security.activity_log[-1]
        assert last_event["event_type"] == "device_registered"
        assert "device_id" in last_event["metadata"]
        assert last_event["metadata"]["user_id"] == "test_user"

    def test_security_event_filtering(self, device_security):
        """Тест фильтрации событий безопасности"""
        # Создаем несколько событий
        device_security.register_device("Device 1", DeviceType.DESKTOP, "Windows 10", "10.0.19041", "user1")
        device_security.register_device("Device 2", DeviceType.LAPTOP, "macOS", "12.0", "user2")

        # Сканируем устройство
        device_profile = device_security.register_device("Device 3", DeviceType.MOBILE, "Android", "11.0", "user3")
        report = device_security.scan_device_security(device_profile.device_id)

        # Фильтруем по типу события
        registration_events = device_security.get_security_events(event_type="device_registered")
        assert len(registration_events) >= 2

        scan_events = device_security.get_security_events(event_type="device_scan_completed")
        assert len(scan_events) >= 1

        # Фильтруем по серьезности
        info_events = device_security.get_security_events(severity="info")
        assert len(info_events) >= 3

    def test_security_event_clearing(self, device_security):
        """Тест очистки событий безопасности"""
        # Создаем событие
        device_security.register_device("Test Device", DeviceType.DESKTOP, "Windows 10", "10.0.19041", "user1")
        assert len(device_security.activity_log) > 0

        # Очищаем все события
        device_security.clear_security_events()
        assert len(device_security.activity_log) == 0
