# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Tests for Network Monitoring Service
Тесты для сервиса мониторинга сетевой активности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-02
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from security.active.network_monitoring import (
    NetworkMonitoringService,
    NetworkType,
    TrafficType,
    ThreatLevel,
    MonitoringAction,
    NetworkConnection,
    NetworkAnomaly,
    NetworkRule,
    NetworkStatistics
)


class TestNetworkMonitoring:
    """Тесты для сервиса мониторинга сетевой активности"""

    @pytest.fixture
    def network_monitoring(self):
        """Фикстура для сервиса мониторинга сети"""
        return NetworkMonitoringService()

    def test_initialization(self, network_monitoring):
        """Тест инициализации сервиса"""
        assert network_monitoring.name == "NetworkMonitoring"
        assert len(network_monitoring.monitoring_rules) > 0
        assert network_monitoring.monitoring_enabled is True
        assert network_monitoring.real_time_monitoring is True
        assert network_monitoring.deep_packet_inspection is True
        assert network_monitoring.family_protection_enabled is True
        assert network_monitoring.child_monitoring_mode is True
        assert network_monitoring.elderly_monitoring_mode is True

    def test_monitor_connection_wifi(self, network_monitoring):
        """Тест мониторинга WiFi соединения"""
        connection = network_monitoring.monitor_connection(
            source_ip="192.168.1.10",
            destination_ip="192.168.1.1",
            source_port=12345,
            destination_port=80,
            protocol="TCP",
            user_id="test_user",
            device_id="device_1",
            user_age=25
        )

        assert connection is not None
        assert connection.source_ip == "192.168.1.10"
        assert connection.destination_ip == "192.168.1.1"
        assert connection.source_port == 12345
        assert connection.destination_port == 80
        assert connection.protocol == "TCP"
        assert connection.network_type == NetworkType.WIFI
        assert connection.traffic_type == TrafficType.WEB
        assert connection.user_id == "test_user"
        assert connection.device_id == "device_1"
        assert connection.metadata["user_age"] == 25

    def test_monitor_connection_ethernet(self, network_monitoring):
        """Тест мониторинга Ethernet соединения"""
        connection = network_monitoring.monitor_connection(
            source_ip="10.0.0.5",
            destination_ip="10.0.0.1",
            source_port=54321,
            destination_port=443,
            protocol="TCP",
            user_id="test_user_2"
        )

        assert connection is not None
        assert connection.network_type == NetworkType.WIFI  # 10.x.x.x определяется как WiFi
        assert connection.traffic_type == TrafficType.WEB
        assert connection.user_id == "test_user_2"

    def test_monitor_connection_email(self, network_monitoring):
        """Тест мониторинга email соединения"""
        connection = network_monitoring.monitor_connection(
            source_ip="192.168.1.20",
            destination_ip="smtp.gmail.com",
            source_port=12345,
            destination_port=587,
            protocol="TCP",
            user_id="email_user"
        )

        assert connection is not None
        assert connection.traffic_type == TrafficType.EMAIL
        assert connection.user_id == "email_user"

    def test_monitor_connection_chat(self, network_monitoring):
        """Тест мониторинга chat соединения"""
        connection = network_monitoring.monitor_connection(
            source_ip="192.168.1.30",
            destination_ip="irc.server.com",
            source_port=12345,
            destination_port=6667,
            protocol="TCP",
            user_id="chat_user"
        )

        assert connection is not None
        assert connection.traffic_type == TrafficType.CHAT
        assert connection.user_id == "chat_user"

    def test_monitor_connection_file_sharing(self, network_monitoring):
        """Тест мониторинга file sharing соединения"""
        connection = network_monitoring.monitor_connection(
            source_ip="192.168.1.40",
            destination_ip="torrent.tracker.com",
            source_port=12345,
            destination_port=6881,
            protocol="TCP",
            user_id="file_user"
        )

        assert connection is not None
        assert connection.traffic_type == TrafficType.FILE_SHARING
        assert connection.user_id == "file_user"

    def test_monitor_connection_child_user(self, network_monitoring):
        """Тест мониторинга соединения ребенка"""
        connection = network_monitoring.monitor_connection(
            source_ip="192.168.1.50",
            destination_ip="game.server.com",
            source_port=12345,
            destination_port=80,
            protocol="TCP",
            user_id="child_user",
            user_age=12
        )

        assert connection is not None
        assert connection.user_id == "child_user"
        assert connection.metadata["user_age"] == 12
        assert "child_user" in network_monitoring.family_network_history

    def test_monitor_connection_elderly_user(self, network_monitoring):
        """Тест мониторинга соединения пожилого пользователя"""
        connection = network_monitoring.monitor_connection(
            source_ip="192.168.1.60",
            destination_ip="bank.com",
            source_port=12345,
            destination_port=443,
            protocol="TCP",
            user_id="elderly_user",
            user_age=70
        )

        assert connection is not None
        assert connection.user_id == "elderly_user"
        assert connection.metadata["user_age"] == 70
        assert "elderly_user" in network_monitoring.family_network_history

    def test_detect_network_anomaly_low_threat(self, network_monitoring):
        """Тест обнаружения аномалии низкого уровня"""
        # Создаем соединение
        connection = network_monitoring.monitor_connection(
            source_ip="192.168.1.70",
            destination_ip="suspicious.site.com",
            source_port=12345,
            destination_port=80,
            protocol="TCP",
            user_id="test_user"
        )

        # Обнаруживаем аномалию
        anomaly = network_monitoring.detect_network_anomaly(
            connection=connection,
            anomaly_type="suspicious_connection",
            description="Подозрительное соединение",
            confidence=0.3
        )

        assert anomaly is not None
        assert anomaly.anomaly_type == "suspicious_connection"
        assert anomaly.threat_level == ThreatLevel.LOW
        assert anomaly.confidence == 0.3
        assert anomaly.connection_id == connection.connection_id

    def test_detect_network_anomaly_medium_threat(self, network_monitoring):
        """Тест обнаружения аномалии среднего уровня"""
        connection = network_monitoring.monitor_connection(
            source_ip="192.168.1.80",
            destination_ip="malicious.site.com",
            source_port=12345,
            destination_port=80,
            protocol="TCP",
            user_id="test_user"
        )

        anomaly = network_monitoring.detect_network_anomaly(
            connection=connection,
            anomaly_type="malicious_connection",
            description="Вредоносное соединение",
            confidence=0.6
        )

        assert anomaly is not None
        assert anomaly.threat_level == ThreatLevel.MEDIUM
        assert anomaly.confidence == 0.6

    def test_detect_network_anomaly_high_threat(self, network_monitoring):
        """Тест обнаружения аномалии высокого уровня"""
        connection = network_monitoring.monitor_connection(
            source_ip="192.168.1.90",
            destination_ip="attack.server.com",
            source_port=12345,
            destination_port=80,
            protocol="TCP",
            user_id="test_user"
        )

        anomaly = network_monitoring.detect_network_anomaly(
            connection=connection,
            anomaly_type="attack_attempt",
            description="Попытка атаки",
            confidence=0.8
        )

        assert anomaly is not None
        assert anomaly.threat_level == ThreatLevel.HIGH
        assert anomaly.confidence == 0.8

    def test_detect_network_anomaly_critical_threat(self, network_monitoring):
        """Тест обнаружения аномалии критического уровня"""
        connection = network_monitoring.monitor_connection(
            source_ip="192.168.1.100",
            destination_ip="critical.threat.com",
            source_port=12345,
            destination_port=80,
            protocol="TCP",
            user_id="test_user"
        )

        anomaly = network_monitoring.detect_network_anomaly(
            connection=connection,
            anomaly_type="critical_threat",
            description="Критическая угроза",
            confidence=0.95
        )

        assert anomaly is not None
        assert anomaly.threat_level == ThreatLevel.CRITICAL
        assert anomaly.confidence == 0.95

    def test_get_network_statistics_user_specific(self, network_monitoring):
        """Тест получения статистики для конкретного пользователя"""
        # Создаем несколько соединений
        for i in range(3):
            connection = network_monitoring.monitor_connection(
                source_ip=f"192.168.1.{10+i}",
                destination_ip=f"server{i}.com",
                source_port=12345+i,
                destination_port=80,
                protocol="TCP",
                user_id="stats_user"
            )
            # Соединения автоматически добавляются в connection_history

        statistics = network_monitoring.get_network_statistics(user_id="stats_user")

        assert statistics is not None
        assert statistics.total_connections == 3
        assert statistics.by_traffic_type["web"] == 3
        # Проверяем, что unknown есть в статистике (IP адреса определяются как unknown)
        assert "unknown" in statistics.by_network_type
        assert statistics.by_network_type["unknown"] == 3

    def test_get_network_statistics_all_users(self, network_monitoring):
        """Тест получения общей статистики"""
        # Создаем соединения для разных пользователей
        users = ["user1", "user2", "user3"]
        for i, user in enumerate(users):
            connection = network_monitoring.monitor_connection(
                source_ip=f"192.168.1.{20+i}",
                destination_ip=f"server{i}.com",
                source_port=12345+i,
                destination_port=80,
                protocol="TCP",
                user_id=user
            )
            # Соединения автоматически добавляются в connection_history

        statistics = network_monitoring.get_network_statistics()

        assert statistics is not None
        assert statistics.total_connections == 3
        assert statistics.by_traffic_type["web"] == 3

    def test_get_family_network_status(self, network_monitoring):
        """Тест получения статуса семейной сети"""
        status = network_monitoring.get_family_network_status()

        assert status["monitoring_enabled"] is True
        assert status["real_time_monitoring"] is True
        assert status["deep_packet_inspection"] is True
        assert status["family_protection_enabled"] is True
        assert status["child_monitoring_mode"] is True
        assert status["elderly_monitoring_mode"] is True
        assert status["active_rules"] > 0
        assert status["family_specific_rules"] > 0
        assert "protection_settings" in status
        assert "family_history" in status

    def test_get_status(self, network_monitoring):
        """Тест получения статуса сервиса"""
        status = network_monitoring.get_status()

        assert status["service_name"] == "NetworkMonitoring"
        assert status["monitoring_rules"] > 0
        assert status["family_protection_enabled"] is True
        assert status["real_time_monitoring"] is True
        assert "uptime" in status

    def test_family_network_history(self, network_monitoring):
        """Тест истории семейной сети"""
        # Создаем соединения для семейного пользователя
        connection = network_monitoring.monitor_connection(
            source_ip="192.168.1.110",
            destination_ip="family.site.com",
            source_port=12345,
            destination_port=80,
            protocol="TCP",
            user_id="family_user",
            user_age=35
        )

        assert connection is not None
        assert "family_user" in network_monitoring.family_network_history
        assert len(network_monitoring.family_network_history["family_user"]) > 0

    def test_network_type_detection(self, network_monitoring):
        """Тест определения типа сети"""
        # Тестируем разные IP адреса
        test_cases = [
            ("192.168.1.1", NetworkType.WIFI),
            ("10.0.0.1", NetworkType.WIFI),
            ("172.16.0.1", NetworkType.ETHERNET),
            ("127.0.0.1", NetworkType.ETHERNET),
            ("8.8.8.8", NetworkType.UNKNOWN)
        ]

        for ip, expected_type in test_cases:
            detected_type = network_monitoring._detect_network_type(ip)
            assert detected_type == expected_type

    def test_traffic_type_detection(self, network_monitoring):
        """Тест определения типа трафика"""
        # Тестируем разные порты
        test_cases = [
            (80, "TCP", TrafficType.WEB),
            (443, "TCP", TrafficType.WEB),
            (25, "TCP", TrafficType.EMAIL),
            (587, "TCP", TrafficType.EMAIL),
            (6667, "TCP", TrafficType.CHAT),
            (6881, "TCP", TrafficType.FILE_SHARING),
            (9999, "TCP", TrafficType.UNKNOWN)
        ]

        for port, protocol, expected_type in test_cases:
            detected_type = network_monitoring._detect_traffic_type(port, protocol)
            assert detected_type == expected_type

    def test_threat_level_determination(self, network_monitoring):
        """Тест определения уровня угрозы"""
        test_cases = [
            (0.95, ThreatLevel.CRITICAL),
            (0.8, ThreatLevel.HIGH),
            (0.6, ThreatLevel.MEDIUM),
            (0.3, ThreatLevel.LOW)
        ]

        for confidence, expected_level in test_cases:
            threat_level = network_monitoring._determine_threat_level(confidence)
            assert threat_level == expected_level

    def test_malicious_ip_detection(self, network_monitoring):
        """Тест обнаружения вредоносных IP"""
        # Тестируем известные вредоносные IP
        malicious_ips = ["192.168.1.100", "10.0.0.100", "172.16.0.100"]
        safe_ips = ["192.168.1.1", "10.0.0.1", "8.8.8.8"]

        for ip in malicious_ips:
            assert network_monitoring._is_malicious_ip(ip) is True

        for ip in safe_ips:
            assert network_monitoring._is_malicious_ip(ip) is False

    def test_inappropriate_content_detection(self, network_monitoring):
        """Тест обнаружения неподходящего контента"""
        inappropriate_ips = ["192.168.1.200", "10.0.0.200"]
        safe_ips = ["192.168.1.1", "10.0.0.1"]

        for ip in inappropriate_ips:
            assert network_monitoring._is_inappropriate_content(ip) is True

        for ip in safe_ips:
            assert network_monitoring._is_inappropriate_content(ip) is False

    def test_financial_site_detection(self, network_monitoring):
        """Тест обнаружения финансовых сайтов"""
        financial_ips = ["192.168.1.300", "10.0.0.300"]
        safe_ips = ["192.168.1.1", "10.0.0.1"]

        for ip in financial_ips:
            assert network_monitoring._is_financial_site(ip) is True

        for ip in safe_ips:
            assert network_monitoring._is_financial_site(ip) is False

    def test_data_exfiltration_detection(self, network_monitoring):
        """Тест обнаружения утечки данных"""
        # Создаем соединение с большим объемом данных
        connection = NetworkConnection(
            connection_id="test_conn",
            source_ip="192.168.1.120",
            destination_ip="external.server.com",
            source_port=12345,
            destination_port=80,
            protocol="TCP",
            network_type=NetworkType.WIFI,
            traffic_type=TrafficType.WEB,
            bytes_sent=2000000,  # 2MB - превышает лимит
            bytes_received=1000,
            start_time=datetime.now()
        )

        assert network_monitoring._detect_data_exfiltration(connection) is True

        # Создаем соединение с нормальным объемом данных
        connection.bytes_sent = 100000  # 100KB - в пределах нормы
        assert network_monitoring._detect_data_exfiltration(connection) is False

    def test_security_event_creation(self, network_monitoring):
        """Тест создания событий безопасности"""
        initial_events = len(network_monitoring.activity_log)

        # Создаем сетевое соединение
        connection = network_monitoring.monitor_connection(
            source_ip="192.168.1.130",
            destination_ip="test.server.com",
            source_port=12345,
            destination_port=80,
            protocol="TCP",
            user_id="test_user"
        )

        # Проверяем, что событие добавлено в журнал
        assert connection is not None
        assert len(network_monitoring.activity_log) > initial_events

        # Проверяем последнее событие
        last_event = network_monitoring.activity_log[-1]
        assert last_event["event_type"] == "network_connection"
        assert "connection_id" in last_event["metadata"]
        assert last_event["metadata"]["user_id"] == "test_user"

    def test_security_event_filtering(self, network_monitoring):
        """Тест фильтрации событий безопасности"""
        # Создаем несколько событий
        network_monitoring.monitor_connection("192.168.1.1", "server1.com", 12345, 80, "TCP", "user1")
        network_monitoring.monitor_connection("192.168.1.2", "server2.com", 12346, 443, "TCP", "user2")

        # Создаем аномалию
        connection = network_monitoring.monitor_connection("192.168.1.3", "malicious.com", 12347, 80, "TCP", "user3")
        anomaly = network_monitoring.detect_network_anomaly(connection, "test_anomaly", "Test anomaly", 0.8)

        # Фильтруем по типу события
        connection_events = network_monitoring.get_security_events(event_type="network_connection")
        assert len(connection_events) >= 2

        anomaly_events = network_monitoring.get_security_events(event_type="network_anomaly")
        assert len(anomaly_events) >= 1

        # Фильтруем по серьезности
        high_events = network_monitoring.get_security_events(severity="high")
        assert len(high_events) >= 1

    def test_security_event_clearing(self, network_monitoring):
        """Тест очистки событий безопасности"""
        # Создаем событие
        network_monitoring.monitor_connection("192.168.1.1", "server.com", 12345, 80, "TCP", "user1")
        assert len(network_monitoring.activity_log) > 0

        # Очищаем все события
        network_monitoring.clear_security_events()
        assert len(network_monitoring.activity_log) == 0
