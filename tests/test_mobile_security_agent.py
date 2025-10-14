#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тесты для MobileSecurityAgent
"""

import unittest
import sys
import os
import time
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'security', 'ai_agents'))

from mobile_security_agent import (
    MobileSecurityAgent, MobilePlatform, DeviceType, ThreatType, 
    SecurityStatus, AppPermission, MobileDevice, MobileApp, MobileThreat
)


class TestMobileSecurityAgent(unittest.TestCase):
    """Тесты для MobileSecurityAgent"""
    
    def setUp(self):
        """Настройка тестов"""
        self.agent = MobileSecurityAgent("TestMobileSecurityAgent")
        self.test_device_id = "test_device_001"
        self.test_app_id = "test_app_001"
    
    def test_agent_initialization(self):
        """Тест инициализации агента"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.name, "TestMobileSecurityAgent")
        self.assertIsNotNone(self.agent.ml_models)
        self.assertIsNotNone(self.agent.metrics)
    
    def test_agent_initialize(self):
        """Тест инициализации агента"""
        result = self.agent.initialize()
        self.assertTrue(result)
        self.assertEqual(self.agent.status.value, "running")
    
    def test_register_device(self):
        """Тест регистрации устройства"""
        self.agent.initialize()
        
        result = self.agent.register_device(
            self.test_device_id,
            MobilePlatform.IOS,
            DeviceType.PHONE,
            "iPhone 14",
            "16.0"
        )
        
        self.assertTrue(result)
        self.assertIn(self.test_device_id, self.agent.devices)
        
        device = self.agent.devices[self.test_device_id]
        self.assertEqual(device.platform, MobilePlatform.IOS)
        self.assertEqual(device.device_type, DeviceType.PHONE)
        self.assertEqual(device.model, "iPhone 14")
        self.assertEqual(device.os_version, "16.0")
    
    def test_scan_device(self):
        """Тест сканирования устройства"""
        self.agent.initialize()
        self.agent.register_device(
            self.test_device_id,
            MobilePlatform.IOS,
            DeviceType.PHONE,
            "iPhone 14",
            "16.0"
        )
        
        result = self.agent.scan_device(self.test_device_id)
        self.assertTrue(result)
        
        device = self.agent.devices[self.test_device_id]
        self.assertIsNotNone(device.last_seen)
        self.assertGreaterEqual(device.security_score, 0.0)
        self.assertLessEqual(device.security_score, 100.0)
    
    def test_device_security_report(self):
        """Тест получения отчета о безопасности"""
        self.agent.initialize()
        self.agent.register_device(
            self.test_device_id,
            MobilePlatform.IOS,
            DeviceType.PHONE,
            "iPhone 14",
            "16.0"
        )
        self.agent.scan_device(self.test_device_id)
        
        report = self.agent.get_device_security_report(self.test_device_id)
        self.assertIsNotNone(report)
        
        self.assertIn("device", report)
        self.assertIn("threats", report)
        self.assertIn("apps", report)
        self.assertIn("security_recommendations", report)
        self.assertIn("scan_timestamp", report)
        
        self.assertEqual(report["device"]["device_id"], self.test_device_id)
        self.assertIsInstance(report["threats"], list)
        self.assertIsInstance(report["apps"], list)
        self.assertIsInstance(report["security_recommendations"], list)
    
    def test_system_metrics(self):
        """Тест получения системных метрик"""
        self.agent.initialize()
        
        metrics = self.agent.get_system_metrics()
        self.assertIsNotNone(metrics)
        
        self.assertIn("total_devices", metrics)
        self.assertIn("secure_devices", metrics)
        self.assertIn("warning_devices", metrics)
        self.assertIn("critical_devices", metrics)
        self.assertIn("total_apps_scanned", metrics)
        self.assertIn("malicious_apps_detected", metrics)
        self.assertIn("threats_blocked", metrics)
        self.assertIn("security_score_average", metrics)
    
    def test_mobile_device_creation(self):
        """Тест создания мобильного устройства"""
        device = MobileDevice(
            device_id="test_device",
            platform=MobilePlatform.ANDROID,
            device_type=DeviceType.TABLET,
            model="Samsung Galaxy Tab",
            os_version="13.0"
        )
        
        self.assertEqual(device.device_id, "test_device")
        self.assertEqual(device.platform, MobilePlatform.ANDROID)
        self.assertEqual(device.device_type, DeviceType.TABLET)
        self.assertEqual(device.model, "Samsung Galaxy Tab")
        self.assertEqual(device.os_version, "13.0")
        self.assertIsNotNone(device.last_seen)
        self.assertEqual(device.security_status, SecurityStatus.UNKNOWN)
        self.assertEqual(device.security_score, 0.0)
    
    def test_mobile_app_creation(self):
        """Тест создания мобильного приложения"""
        app = MobileApp(
            app_id="test_app",
            name="Test App",
            package_name="com.test.app",
            version="1.0.0",
            platform=MobilePlatform.IOS
        )
        
        self.assertEqual(app.app_id, "test_app")
        self.assertEqual(app.name, "Test App")
        self.assertEqual(app.package_name, "com.test.app")
        self.assertEqual(app.version, "1.0.0")
        self.assertEqual(app.platform, MobilePlatform.IOS)
        self.assertEqual(app.security_rating, 0.0)
        self.assertEqual(app.threat_level, ThreatType.UNKNOWN)
    
    def test_mobile_threat_creation(self):
        """Тест создания мобильной угрозы"""
        threat = MobileThreat(
            threat_id="test_threat",
            threat_type=ThreatType.MALWARE,
            severity="high",
            description="Test malware threat",
            device_id="test_device"
        )
        
        self.assertEqual(threat.threat_id, "test_threat")
        self.assertEqual(threat.threat_type, ThreatType.MALWARE)
        self.assertEqual(threat.severity, "high")
        self.assertEqual(threat.description, "Test malware threat")
        self.assertEqual(threat.device_id, "test_device")
        self.assertIsNotNone(threat.detected_at)
        self.assertFalse(threat.is_resolved)
    
    def test_device_to_dict(self):
        """Тест преобразования устройства в словарь"""
        device = MobileDevice(
            device_id="test_device",
            platform=MobilePlatform.IOS,
            device_type=DeviceType.PHONE,
            model="iPhone 14",
            os_version="16.0"
        )
        
        device_dict = device.to_dict()
        self.assertIsInstance(device_dict, dict)
        self.assertEqual(device_dict["device_id"], "test_device")
        self.assertEqual(device_dict["platform"], "ios")
        self.assertEqual(device_dict["device_type"], "phone")
        self.assertEqual(device_dict["model"], "iPhone 14")
        self.assertEqual(device_dict["os_version"], "16.0")
    
    def test_app_to_dict(self):
        """Тест преобразования приложения в словарь"""
        app = MobileApp(
            app_id="test_app",
            name="Test App",
            package_name="com.test.app",
            version="1.0.0",
            platform=MobilePlatform.ANDROID
        )
        
        app_dict = app.to_dict()
        self.assertIsInstance(app_dict, dict)
        self.assertEqual(app_dict["app_id"], "test_app")
        self.assertEqual(app_dict["name"], "Test App")
        self.assertEqual(app_dict["package_name"], "com.test.app")
        self.assertEqual(app_dict["version"], "1.0.0")
        self.assertEqual(app_dict["platform"], "android")
    
    def test_threat_to_dict(self):
        """Тест преобразования угрозы в словарь"""
        threat = MobileThreat(
            threat_id="test_threat",
            threat_type=ThreatType.PHISHING,
            severity="medium",
            description="Test phishing threat",
            device_id="test_device"
        )
        
        threat_dict = threat.to_dict()
        self.assertIsInstance(threat_dict, dict)
        self.assertEqual(threat_dict["threat_id"], "test_threat")
        self.assertEqual(threat_dict["threat_type"], "phishing")
        self.assertEqual(threat_dict["severity"], "medium")
        self.assertEqual(threat_dict["description"], "Test phishing threat")
        self.assertEqual(threat_dict["device_id"], "test_device")
    
    def test_agent_stop(self):
        """Тест остановки агента"""
        self.agent.initialize()
        
        result = self.agent.stop()
        self.assertTrue(result)
        self.assertEqual(self.agent.status.value, "stopped")
    
    def test_multiple_devices(self):
        """Тест работы с несколькими устройствами"""
        self.agent.initialize()
        
        # Регистрация нескольких устройств
        devices = [
            ("device_1", MobilePlatform.IOS, DeviceType.PHONE, "iPhone 14", "16.0"),
            ("device_2", MobilePlatform.ANDROID, DeviceType.PHONE, "Samsung Galaxy S23", "13.0"),
            ("device_3", MobilePlatform.IOS, DeviceType.TABLET, "iPad Pro", "16.0")
        ]
        
        for device_id, platform, device_type, model, os_version in devices:
            result = self.agent.register_device(device_id, platform, device_type, model, os_version)
            self.assertTrue(result)
        
        # Проверка количества устройств
        self.assertEqual(len(self.agent.devices), 3)
        self.assertEqual(self.agent.metrics.total_devices, 3)
        
        # Сканирование всех устройств
        for device_id, _, _, _, _ in devices:
            result = self.agent.scan_device(device_id)
            self.assertTrue(result)
    
    def test_security_recommendations(self):
        """Тест генерации рекомендаций по безопасности"""
        self.agent.initialize()
        
        # Создание устройства с низким баллом безопасности
        device = MobileDevice(
            device_id="low_security_device",
            platform=MobilePlatform.ANDROID,
            device_type=DeviceType.PHONE,
            model="Test Phone",
            os_version="10.0"
        )
        device.security_score = 50.0  # Низкий балл
        device.is_encrypted = False
        device.is_rooted = True
        
        self.agent.devices["low_security_device"] = device
        
        recommendations = self.agent._generate_security_recommendations(device)
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Проверка наличия ожидаемых рекомендаций
        recommendation_texts = " ".join(recommendations).lower()
        self.assertIn("encryption", recommendation_texts)
        self.assertIn("root", recommendation_texts)


def run_tests():
    """Запуск всех тестов"""
    print("🧪 Запуск тестов MobileSecurityAgent...")
    
    # Создание тестового набора
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestMobileSecurityAgent)
    
    # Запуск тестов
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Вывод результатов
    print("\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("✅ Успешных тестов: {}".format(result.testsRun - len(result.failures) - len(result.errors)))
    print("❌ Неудачных тестов: {}".format(len(result.failures)))
    print("💥 Ошибок: {}".format(len(result.errors)))
    print("📈 Процент успеха: {:.1f}%".format((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100))
    
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)