# -*- coding: utf-8 -*-
"""
Тесты для ZeroTrustService
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from security.preliminary.zero_trust_service import (
    ZeroTrustService, TrustLevel, AccessDecision, DeviceType, NetworkType,
    DeviceProfile, AccessRequest, AccessPolicy
)
from core.security_base import IncidentSeverity


class TestZeroTrustService:
    """Тесты для ZeroTrustService"""
    
    @pytest.fixture
    def zero_trust_service(self):
        """Создание экземпляра ZeroTrustService"""
        return ZeroTrustService()
    
    def test_register_device(self, zero_trust_service):
        """Тест регистрации устройства"""
        result = zero_trust_service.register_device(
            device_id="device_1",
            device_name="iPhone 12",
            device_type=DeviceType.MOBILE,
            user_id="user_1",
            family_id="family_1",
            mac_address="00:11:22:33:44:55",
            ip_address="192.168.1.100",
            os_version="iOS 15.0",
            app_version="1.0.0"
        )
        
        assert result is True
        assert "device_1" in zero_trust_service.device_profiles
        
        device = zero_trust_service.device_profiles["device_1"]
        assert device.device_name == "iPhone 12"
        assert device.device_type == DeviceType.MOBILE
        assert device.user_id == "user_1"
        assert device.trust_score == 0.5
    
    def test_register_blocked_device(self, zero_trust_service):
        """Тест регистрации заблокированного устройства"""
        # Блокируем устройство
        zero_trust_service.block_device("device_1", "Подозрительная активность")
        
        # Пытаемся зарегистрировать заблокированное устройство
        result = zero_trust_service.register_device(
            device_id="device_1",
            device_name="iPhone 12",
            device_type=DeviceType.MOBILE,
            user_id="user_1",
            family_id="family_1",
            mac_address="00:11:22:33:44:55",
            ip_address="192.168.1.100",
            os_version="iOS 15.0",
            app_version="1.0.0"
        )
        
        assert result is False
    
    def test_update_device_trust(self, zero_trust_service):
        """Тест обновления уровня доверия устройства"""
        # Регистрируем устройство
        zero_trust_service.register_device(
            device_id="device_1",
            device_name="iPhone 12",
            device_type=DeviceType.MOBILE,
            user_id="user_1",
            family_id="family_1",
            mac_address="00:11:22:33:44:55",
            ip_address="192.168.1.100",
            os_version="iOS 15.0",
            app_version="1.0.0"
        )
        
        # Обновляем уровень доверия
        result = zero_trust_service.update_device_trust(
            device_id="device_1",
            trust_score=0.8,
            reason="Успешная аутентификация"
        )
        
        assert result is True
        device = zero_trust_service.device_profiles["device_1"]
        assert device.trust_score == 0.8
        assert device.is_trusted is True
    
    def test_update_device_trust_bounds(self, zero_trust_service):
        """Тест обновления уровня доверия с граничными значениями"""
        # Регистрируем устройство
        zero_trust_service.register_device(
            device_id="device_1",
            device_name="iPhone 12",
            device_type=DeviceType.MOBILE,
            user_id="user_1",
            family_id="family_1",
            mac_address="00:11:22:33:44:55",
            ip_address="192.168.1.100",
            os_version="iOS 15.0",
            app_version="1.0.0"
        )
        
        # Тестируем превышение верхней границы
        zero_trust_service.update_device_trust("device_1", 1.5, "Тест")
        device = zero_trust_service.device_profiles["device_1"]
        assert device.trust_score == 1.0
        
        # Тестируем превышение нижней границы
        zero_trust_service.update_device_trust("device_1", -0.5, "Тест")
        device = zero_trust_service.device_profiles["device_1"]
        assert device.trust_score == 0.0
    
    def test_evaluate_access_request_trusted_device(self, zero_trust_service):
        """Тест оценки запроса на доступ с доверенного устройства"""
        # Регистрируем доверенное устройство
        zero_trust_service.register_device(
            device_id="device_1",
            device_name="iPhone 12",
            device_type=DeviceType.MOBILE,
            user_id="user_1",
            family_id="family_1",
            mac_address="00:11:22:33:44:55",
            ip_address="192.168.1.100",
            os_version="iOS 15.0",
            app_version="1.0.0"
        )
        
        # Повышаем уровень доверия
        zero_trust_service.update_device_trust("device_1", 0.9, "Высокое доверие")
        
        # Оцениваем запрос на доступ
        decision, reason, risk = zero_trust_service.evaluate_access_request(
            user_id="user_1",
            device_id="device_1",
            resource="family/photos",
            action="read",
            context={"ip_address": "192.168.1.100"}
        )
        
        assert decision in [AccessDecision.ALLOW, AccessDecision.MONITOR]
        assert risk < 0.5
        assert len(zero_trust_service.access_history) == 1
    
    def test_evaluate_access_request_unregistered_device(self, zero_trust_service):
        """Тест оценки запроса на доступ с незарегистрированного устройства"""
        decision, reason, risk = zero_trust_service.evaluate_access_request(
            user_id="user_1",
            device_id="unknown_device",
            resource="family/photos",
            action="read",
            context={"ip_address": "192.168.1.100"}
        )
        
        assert decision == AccessDecision.DENY
        assert "не зарегистрировано" in reason
        assert risk == 1.0
    
    def test_evaluate_access_request_blocked_device(self, zero_trust_service):
        """Тест оценки запроса на доступ с заблокированного устройства"""
        # Регистрируем устройство
        zero_trust_service.register_device(
            device_id="device_1",
            device_name="iPhone 12",
            device_type=DeviceType.MOBILE,
            user_id="user_1",
            family_id="family_1",
            mac_address="00:11:22:33:44:55",
            ip_address="192.168.1.100",
            os_version="iOS 15.0",
            app_version="1.0.0"
        )
        
        # Блокируем устройство
        zero_trust_service.block_device("device_1", "Подозрительная активность")
        
        # Оцениваем запрос на доступ
        decision, reason, risk = zero_trust_service.evaluate_access_request(
            user_id="user_1",
            device_id="device_1",
            resource="family/photos",
            action="read",
            context={"ip_address": "192.168.1.100"}
        )
        
        assert decision == AccessDecision.DENY
        assert "заблокировано" in reason
        assert risk == 1.0
    
    def test_evaluate_access_request_low_trust_device(self, zero_trust_service):
        """Тест оценки запроса на доступ с устройства с низким доверием"""
        # Регистрируем устройство
        zero_trust_service.register_device(
            device_id="device_1",
            device_name="iPhone 12",
            device_type=DeviceType.MOBILE,
            user_id="user_1",
            family_id="family_1",
            mac_address="00:11:22:33:44:55",
            ip_address="192.168.1.100",
            os_version="iOS 15.0",
            app_version="1.0.0"
        )
        
        # Снижаем уровень доверия
        zero_trust_service.update_device_trust("device_1", 0.2, "Низкое доверие")
        
        # Оцениваем запрос на доступ
        decision, reason, risk = zero_trust_service.evaluate_access_request(
            user_id="user_1",
            device_id="device_1",
            resource="family/photos",
            action="read",
            context={"ip_address": "192.168.1.100"}
        )
        
        assert decision == AccessDecision.DENY
        assert "доверия" in reason
        assert risk == 0.2  # Риск равен уровню доверия устройства
    
    def test_block_device(self, zero_trust_service):
        """Тест блокировки устройства"""
        result = zero_trust_service.block_device("device_1", "Подозрительная активность")
        
        assert result is True
        assert "device_1" in zero_trust_service.blocked_devices
    
    def test_unblock_device(self, zero_trust_service):
        """Тест разблокировки устройства"""
        # Блокируем устройство
        zero_trust_service.block_device("device_1", "Тест")
        
        # Разблокируем устройство
        result = zero_trust_service.unblock_device("device_1", "Ошибка была исправлена")
        
        assert result is True
        assert "device_1" not in zero_trust_service.blocked_devices
    
    def test_unblock_nonexistent_device(self, zero_trust_service):
        """Тест разблокировки несуществующего устройства"""
        result = zero_trust_service.unblock_device("nonexistent_device", "Тест")
        
        assert result is False
    
    def test_get_device_trust_report(self, zero_trust_service):
        """Тест получения отчета о доверии устройства"""
        # Регистрируем устройство
        zero_trust_service.register_device(
            device_id="device_1",
            device_name="iPhone 12",
            device_type=DeviceType.MOBILE,
            user_id="user_1",
            family_id="family_1",
            mac_address="00:11:22:33:44:55",
            ip_address="192.168.1.100",
            os_version="iOS 15.0",
            app_version="1.0.0"
        )
        
        # Обновляем уровень доверия
        zero_trust_service.update_device_trust("device_1", 0.8, "Тест")
        
        # Получаем отчет
        report = zero_trust_service.get_device_trust_report("device_1")
        
        assert report is not None
        assert report["device_id"] == "device_1"
        assert report["device_name"] == "iPhone 12"
        assert report["current_trust_score"] == 0.8
        assert report["is_trusted"] is True
        assert report["is_blocked"] is False
        assert "trust_history" in report
        assert "access_stats" in report
    
    def test_get_device_trust_report_nonexistent(self, zero_trust_service):
        """Тест получения отчета о доверии несуществующего устройства"""
        report = zero_trust_service.get_device_trust_report("nonexistent_device")
        
        assert report is None
    
    def test_determine_network_type(self, zero_trust_service):
        """Тест определения типа сети"""
        # Домашняя сеть
        network_type = zero_trust_service._determine_network_type("192.168.1.100")
        assert network_type == NetworkType.HOME
        
        # Публичная сеть
        network_type = zero_trust_service._determine_network_type("8.8.8.8")
        assert network_type == NetworkType.PUBLIC
        
        # Неизвестная сеть
        network_type = zero_trust_service._determine_network_type("1.2.3.4")
        assert network_type == NetworkType.UNKNOWN
    
    def test_calculate_risk(self, zero_trust_service):
        """Тест вычисления уровня риска"""
        # Создаем тестовые данные
        device = DeviceProfile(
            device_id="device_1",
            device_name="iPhone 12",
            device_type=DeviceType.MOBILE,
            user_id="user_1",
            family_id="family_1",
            mac_address="00:11:22:33:44:55",
            ip_address="192.168.1.100",
            os_version="iOS 15.0",
            app_version="1.0.0",
            trust_score=0.8
        )
        
        request = AccessRequest(
            request_id="req_1",
            user_id="user_1",
            device_id="device_1",
            resource="family/photos",
            action="read",
            context={"ip_address": "192.168.1.100"},
            network_type=NetworkType.HOME
        )
        
        policy = AccessPolicy(
            policy_id="test_policy",
            name="Test Policy",
            description="Test",
            resource_pattern="*",
            user_conditions={},
            device_conditions={},
            network_conditions={},
            time_conditions={},
            trust_requirements=TrustLevel.MEDIUM,
            action=AccessDecision.ALLOW
        )
        
        # Вычисляем риск
        risk = zero_trust_service._calculate_risk(request, device, policy)
        
        assert 0.0 <= risk <= 1.0
        assert risk < 0.5  # Доверенное устройство в домашней сети
    
    def test_get_status(self, zero_trust_service):
        """Тест получения статуса сервиса"""
        # Регистрируем несколько устройств
        zero_trust_service.register_device(
            device_id="device_1",
            device_name="iPhone 12",
            device_type=DeviceType.MOBILE,
            user_id="user_1",
            family_id="family_1",
            mac_address="00:11:22:33:44:55",
            ip_address="192.168.1.100",
            os_version="iOS 15.0",
            app_version="1.0.0"
        )
        
        zero_trust_service.register_device(
            device_id="device_2",
            device_name="iPad Pro",
            device_type=DeviceType.TABLET,
            user_id="user_2",
            family_id="family_1",
            mac_address="00:11:22:33:44:66",
            ip_address="192.168.1.101",
            os_version="iPadOS 15.0",
            app_version="1.0.0"
        )
        
        # Блокируем одно устройство
        zero_trust_service.block_device("device_2", "Тест")
        
        # Получаем статус
        status = zero_trust_service.get_status()
        
        assert "status" in status
        assert status["total_devices"] == 2
        assert status["trusted_devices"] == 0  # device_1 с trust_score=0.5 < 0.7 (default_trust_threshold)
        assert status["blocked_devices"] == 1
        assert status["total_policies"] >= 3  # Политики по умолчанию
        assert status["active_policies"] >= 3
        assert "device_types" in status
        assert "average_trust_score" in status


if __name__ == "__main__":
    pytest.main([__file__])