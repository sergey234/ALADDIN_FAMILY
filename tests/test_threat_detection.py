"""
Тесты для системы обнаружения угроз
ALADDIN Security System - Уровень 2: Активная защита
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from security.active.threat_detection import (
    ThreatDetectionService, ThreatType, ThreatSeverity, ThreatSource,
    DetectionMethod, ThreatIndicator, ThreatDetection, ThreatPattern
)


class TestThreatDetection:
    """Тесты для ThreatDetectionService"""

    @pytest.fixture
    def threat_detection(self):
        """Фикстура для ThreatDetectionService"""
        return ThreatDetectionService()

    def test_initialization(self, threat_detection):
        """Тест инициализации сервиса"""
        assert threat_detection.name == "ThreatDetection"
        assert len(threat_detection.threat_patterns) > 0
        assert len(threat_detection.security_rules) > 0
        assert threat_detection.detection_thresholds is not None

    def test_analyze_content_child_exploitation(self, threat_detection):
        """Тест обнаружения угроз для детей"""
        content = "встретимся наедине, не говори родителям, это наш секрет"
        detections = threat_detection.analyze_content(
            content=content,
            source=ThreatSource.SOCIAL_MEDIA,
            user_id="child_user",
            user_age=12
        )
        
        assert len(detections) > 0
        assert any(detection.threat_type == ThreatType.CHILD_EXPLOITATION for detection in detections)
        assert any(detection.severity == ThreatSeverity.CRITICAL for detection in detections)

    def test_analyze_content_elderly_fraud(self, threat_detection):
        """Тест обнаружения мошенничества против пожилых"""
        content = "ваш компьютер заражен, срочно установите программу для разблокировки"
        detections = threat_detection.analyze_content(
            content=content,
            source=ThreatSource.PHONE,
            user_id="elderly_user",
            user_age=70
        )
        
        assert len(detections) > 0
        assert any(detection.threat_type == ThreatType.ELDERLY_FRAUD for detection in detections)
        assert any(detection.severity == ThreatSeverity.HIGH for detection in detections)

    def test_analyze_content_phishing(self, threat_detection):
        """Тест обнаружения фишинга"""
        content = "подтвердите данные ребенка в школьном кабинете"
        detections = threat_detection.analyze_content(
            content=content,
            source=ThreatSource.EMAIL,
            user_id="parent_user",
            user_age=35
        )
        
        assert len(detections) > 0
        assert any(detection.threat_type == ThreatType.PHISHING for detection in detections)

    def test_analyze_content_malware(self, threat_detection):
        """Тест обнаружения попыток загрузки вредоносного ПО"""
        content = "скачай бесплатную игру.exe и получи кряк программы"
        detections = threat_detection.analyze_content(
            content=content,
            source=ThreatSource.WEBSITE,
            user_id="teen_user",
            user_age=16
        )
        
        assert len(detections) > 0
        assert any(detection.threat_type == ThreatType.MALWARE for detection in detections)

    def test_analyze_content_no_threats(self, threat_detection):
        """Тест анализа безопасного контента"""
        content = "привет, как дела? сегодня хорошая погода"
        detections = threat_detection.analyze_content(
            content=content,
            source=ThreatSource.SOCIAL_MEDIA,
            user_id="user",
            user_age=25
        )
        
        assert len(detections) == 0

    def test_analyze_file_known_malware(self, threat_detection):
        """Тест анализа известного вредоносного файла"""
        file_path = "malware.exe"
        file_hash = "d41d8cd98f00b204e9800998ecf8427e"
        
        detections = threat_detection.analyze_file(
            file_path=file_path,
            file_hash=file_hash,
            user_id="user"
        )
        
        assert len(detections) > 0
        assert any(detection.threat_type == ThreatType.MALWARE for detection in detections)
        assert any(detection.severity == ThreatSeverity.CRITICAL for detection in detections)

    def test_analyze_file_suspicious_extension(self, threat_detection):
        """Тест анализа файла с подозрительным расширением"""
        file_path = "game.exe"
        file_hash = "unknown_hash"
        
        detections = threat_detection.analyze_file(
            file_path=file_path,
            file_hash=file_hash,
            user_id="user"
        )
        
        assert len(detections) > 0
        assert any(detection.threat_type == ThreatType.SUSPICIOUS_ACTIVITY for detection in detections)

    def test_analyze_file_safe_file(self, threat_detection):
        """Тест анализа безопасного файла"""
        file_path = "document.pdf"
        file_hash = "safe_hash"
        
        detections = threat_detection.analyze_file(
            file_path=file_path,
            file_hash=file_hash,
            user_id="user"
        )
        
        assert len(detections) == 0

    def test_analyze_network_activity_suspicious_ip(self, threat_detection):
        """Тест анализа подозрительной сетевой активности"""
        detections = threat_detection.analyze_network_activity(
            source_ip="192.168.1.100",
            destination_ip="8.8.8.8",
            port=80,
            protocol="TCP",
            user_id="user"
        )
        
        assert len(detections) > 0
        assert any(detection.threat_type == ThreatType.SUSPICIOUS_ACTIVITY for detection in detections)

    def test_analyze_network_activity_suspicious_port(self, threat_detection):
        """Тест анализа подозрительного порта"""
        detections = threat_detection.analyze_network_activity(
            source_ip="192.168.1.1",
            destination_ip="192.168.1.2",
            port=22,  # SSH порт
            protocol="TCP",
            user_id="user"
        )
        
        assert len(detections) > 0
        assert any(detection.threat_type == ThreatType.UNAUTHORIZED_ACCESS for detection in detections)

    def test_analyze_network_activity_safe(self, threat_detection):
        """Тест анализа безопасной сетевой активности"""
        detections = threat_detection.analyze_network_activity(
            source_ip="192.168.1.1",
            destination_ip="8.8.8.8",
            port=80,  # HTTP порт
            protocol="TCP",
            user_id="user"
        )
        
        assert len(detections) == 0

    def test_get_threat_summary_user_specific(self, threat_detection):
        """Тест получения сводки по угрозам для конкретного пользователя"""
        # Создаем тестовые угрозы
        threat_detection.analyze_content(
            "встретимся наедине",
            ThreatSource.SOCIAL_MEDIA,
            user_id="test_user",
            user_age=12
        )
        
        summary = threat_detection.get_threat_summary(user_id="test_user")
        
        assert "total_threats" in summary
        assert "threats_by_type" in summary
        assert "threats_by_severity" in summary
        assert "threats_by_source" in summary
        assert "recent_threats" in summary

    def test_get_threat_summary_all_users(self, threat_detection):
        """Тест получения сводки по всем угрозам"""
        # Создаем тестовые угрозы
        threat_detection.analyze_content(
            "встретимся наедине",
            ThreatSource.SOCIAL_MEDIA,
            user_id="user1",
            user_age=12
        )
        threat_detection.analyze_content(
            "ваш компьютер заражен",
            ThreatSource.PHONE,
            user_id="user2",
            user_age=70
        )
        
        summary = threat_detection.get_threat_summary()
        
        assert summary["total_threats"] >= 2
        assert "child_exploitation" in summary["threats_by_type"]
        assert "elderly_fraud" in summary["threats_by_type"]

    def test_get_family_protection_status(self, threat_detection):
        """Тест получения статуса семейной защиты"""
        # Создаем тестовые семейные угрозы
        threat_detection.analyze_content(
            "встретимся наедине",
            ThreatSource.SOCIAL_MEDIA,
            user_id="child_user",
            user_age=12
        )
        threat_detection.analyze_content(
            "ваш компьютер заражен",
            ThreatSource.PHONE,
            user_id="elderly_user",
            user_age=70
        )
        
        status = threat_detection.get_family_protection_status()
        
        assert status["family_protection_active"] is True
        assert "total_family_threats" in status
        assert "threats_by_age_group" in status
        assert "active_patterns" in status
        assert "protection_rules" in status

    def test_get_status(self, threat_detection):
        """Тест получения общего статуса"""
        status = threat_detection.get_status()
        
        assert status["service_name"] == "ThreatDetection"
        assert status["status"] == "active"
        assert "total_threats_detected" in status
        assert "active_patterns" in status
        assert "protection_rules" in status
        assert "family_protection" in status
        assert "threat_summary" in status

    def test_age_group_filtering(self, threat_detection):
        """Тест фильтрации по возрастным группам"""
        # Тест для ребенка
        child_detections = threat_detection.analyze_content(
            "встретимся наедине",
            ThreatSource.SOCIAL_MEDIA,
            user_id="child",
            user_age=12
        )
        
        # Тест для взрослого (должен быть отфильтрован)
        adult_detections = threat_detection.analyze_content(
            "встретимся наедине",
            ThreatSource.SOCIAL_MEDIA,
            user_id="adult",
            user_age=25
        )
        
        assert len(child_detections) > 0
        assert len(adult_detections) == 0  # Паттерн для детей не должен срабатывать для взрослых

    def test_confidence_calculation(self, threat_detection):
        """Тест расчета уверенности в обнаружении"""
        # Контент с множественными совпадениями
        content = "встретимся наедине, не говори родителям, это наш секрет, пришли фото"
        detections = threat_detection.analyze_content(
            content=content,
            source=ThreatSource.SOCIAL_MEDIA,
            user_id="child",
            user_age=12
        )
        
        assert len(detections) > 0
        # Уверенность должна быть высокой из-за множественных совпадений
        assert any(detection.confidence > 0.7 for detection in detections)

    def test_threat_indicator_creation(self, threat_detection):
        """Тест создания индикаторов угроз"""
        detections = threat_detection.analyze_content(
            "встретимся наедине",
            ThreatSource.SOCIAL_MEDIA,
            user_id="child",
            user_age=12
        )
        
        assert len(detections) > 0
        detection = detections[0]
        assert len(detection.indicators) > 0
        
        indicator = detection.indicators[0]
        assert indicator.indicator_type == "pattern_match"
        assert indicator.confidence > 0
        assert indicator.source == ThreatSource.SOCIAL_MEDIA

    def test_security_event_creation(self, threat_detection):
        """Тест создания событий безопасности"""
        detections = threat_detection.analyze_content(
            "встретимся наедине",
            ThreatSource.SOCIAL_MEDIA,
            user_id="child",
            user_age=12
        )
        
        # Проверяем, что обнаружения созданы
        assert len(detections) > 0
        
        # Проверяем детали обнаружения
        detection = detections[0]
        assert detection.threat_type == ThreatType.CHILD_EXPLOITATION
        assert detection.severity == ThreatSeverity.CRITICAL

    def test_security_event_filtering(self, threat_detection):
        """Тест фильтрации событий безопасности"""
        # Создаем событие
        threat_detection.analyze_content("встретимся наедине", ThreatSource.SOCIAL_MEDIA, "child", 12)
        
        # Фильтруем по типу события
        threat_events = threat_detection.get_security_events(event_type="threat_detected")
        assert len(threat_events) >= 1
        
        # Фильтруем по серьезности
        critical_events = threat_detection.get_security_events(severity="critical")
        assert len(critical_events) >= 1
        
        # Проверяем структуру события
        event = threat_events[0]
        assert "timestamp" in event
        assert "event_type" in event
        assert "severity" in event
        assert "description" in event
        assert "source" in event
        assert "metadata" in event

    def test_security_event_clearing(self, threat_detection):
        """Тест очистки событий безопасности"""
        # Создаем событие
        threat_detection.analyze_content("встретимся наедине", ThreatSource.SOCIAL_MEDIA, "child", 12)
        assert len(threat_detection.activity_log) > 0
        
        # Очищаем все события
        threat_detection.clear_security_events()
        assert len(threat_detection.activity_log) == 0
