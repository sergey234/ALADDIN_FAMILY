# -*- coding: utf-8 -*-
"""
Тесты для MFAService
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from security.preliminary.mfa_service import (
    MFAService, MFAMethod, MFAStatus, UserRole,
    MFASession, MFACode, UserMFAProfile
)
from core.security_base import IncidentSeverity


class TestMFAService:
    """Тесты для MFAService"""
    
    @pytest.fixture
    def mfa_service(self):
        """Создание экземпляра MFAService"""
        return MFAService()
    
    def test_create_user_profile(self, mfa_service):
        """Тест создания профиля пользователя"""
        result = mfa_service.create_user_profile(
            user_id="test_user",
            role=UserRole.PARENT,
            phone_number="+1234567890",
            email="test@example.com"
        )
        
        assert result is True
        assert "test_user" in mfa_service.user_profiles
        
        profile = mfa_service.user_profiles["test_user"]
        assert profile.role == UserRole.PARENT
        assert profile.phone_number == "+1234567890"
        assert profile.email == "test@example.com"
        assert len(profile.backup_codes) == 10
    
    def test_create_duplicate_user_profile(self, mfa_service):
        """Тест создания дублирующегося профиля пользователя"""
        # Создаем первый профиль
        mfa_service.create_user_profile("test_user", UserRole.PARENT)
        
        # Пытаемся создать дублирующийся профиль
        result = mfa_service.create_user_profile("test_user", UserRole.CHILD)
        
        assert result is False
    
    def test_start_mfa_session(self, mfa_service):
        """Тест начала сессии MFA"""
        # Создаем профиль пользователя
        mfa_service.create_user_profile("test_user", UserRole.PARENT)
        
        # Начинаем сессию
        session_id = mfa_service.start_mfa_session(
            user_id="test_user",
            device_id="device_1",
            context={"ip_address": "192.168.1.100"}
        )
        
        assert session_id is not None
        assert session_id in mfa_service.active_sessions
        
        session = mfa_service.active_sessions[session_id]
        assert session.user_id == "test_user"
        assert session.device_id == "device_1"
        assert session.status == MFAStatus.PENDING
        assert len(session.methods) > 0
    
    def test_start_mfa_session_nonexistent_user(self, mfa_service):
        """Тест начала сессии MFA для несуществующего пользователя"""
        session_id = mfa_service.start_mfa_session(
            user_id="nonexistent_user",
            device_id="device_1",
            context={}
        )
        
        assert session_id is None
    
    def test_send_mfa_code(self, mfa_service):
        """Тест отправки кода MFA"""
        # Создаем профиль и сессию
        mfa_service.create_user_profile("test_user", UserRole.PARENT, phone_number="+1234567890")
        session_id = mfa_service.start_mfa_session("test_user", "device_1", {})
        
        # Отправляем код
        result = mfa_service.send_mfa_code(session_id, MFAMethod.SMS)
        
        assert result is True
        assert len(mfa_service.mfa_codes) > 0
    
    def test_send_mfa_code_nonexistent_session(self, mfa_service):
        """Тест отправки кода для несуществующей сессии"""
        result = mfa_service.send_mfa_code("nonexistent_session", MFAMethod.SMS)
        
        assert result is False
    
    def test_send_mfa_code_unsupported_method(self, mfa_service):
        """Тест отправки кода неподдерживаемым методом"""
        # Создаем профиль и сессию
        mfa_service.create_user_profile("test_user", UserRole.CHILD)
        session_id = mfa_service.start_mfa_session("test_user", "device_1", {})
        
        # Пытаемся отправить код неподдерживаемым методом
        result = mfa_service.send_mfa_code(session_id, MFAMethod.TOTP)
        
        assert result is False
    
    def test_verify_mfa_code_success(self, mfa_service):
        """Тест успешной проверки кода MFA"""
        # Создаем профиль и сессию
        mfa_service.create_user_profile("test_user", UserRole.PARENT, phone_number="+1234567890")
        session_id = mfa_service.start_mfa_session("test_user", "device_1", {})
        
        # Отправляем код
        mfa_service.send_mfa_code(session_id, MFAMethod.SMS)
        
        # Находим код
        code = None
        for mfa_code in mfa_service.mfa_codes.values():
            if mfa_code.session_id == session_id and mfa_code.method == MFAMethod.SMS:
                code = mfa_code.code
                break
        
        assert code is not None
        
        # Проверяем код
        success, message = mfa_service.verify_mfa_code(session_id, MFAMethod.SMS, code)
        
        assert success is True
        assert "подтвержден" in message
    
    def test_verify_mfa_code_wrong_code(self, mfa_service):
        """Тест проверки неверного кода MFA"""
        # Создаем профиль и сессию
        mfa_service.create_user_profile("test_user", UserRole.PARENT, phone_number="+1234567890")
        session_id = mfa_service.start_mfa_session("test_user", "device_1", {})
        
        # Отправляем код
        mfa_service.send_mfa_code(session_id, MFAMethod.SMS)
        
        # Проверяем неверный код
        success, message = mfa_service.verify_mfa_code(session_id, MFAMethod.SMS, "000000")
        
        assert success is False
        assert "Неверный" in message
    
    def test_verify_mfa_code_nonexistent_session(self, mfa_service):
        """Тест проверки кода для несуществующей сессии"""
        success, message = mfa_service.verify_mfa_code("nonexistent_session", MFAMethod.SMS, "123456")
        
        assert success is False
        assert "не найдена" in message
    
    def test_verify_mfa_code_expired_session(self, mfa_service):
        """Тест проверки кода для истекшей сессии"""
        # Создаем профиль и сессию
        mfa_service.create_user_profile("test_user", UserRole.PARENT, phone_number="+1234567890")
        session_id = mfa_service.start_mfa_session("test_user", "device_1", {})
        
        # Искусственно истекаем сессию
        session = mfa_service.active_sessions[session_id]
        session.expires_at = datetime.now() - timedelta(minutes=1)
        
        # Отправляем код
        mfa_service.send_mfa_code(session_id, MFAMethod.SMS)
        
        # Находим код
        code = None
        for mfa_code in mfa_service.mfa_codes.values():
            if mfa_code.session_id == session_id and mfa_code.method == MFAMethod.SMS:
                code = mfa_code.code
                break
        
        # Проверяем код
        success, message = mfa_service.verify_mfa_code(session_id, MFAMethod.SMS, code)
        
        assert success is False
        assert "истекла" in message
    
    def test_verify_mfa_code_max_attempts(self, mfa_service):
        """Тест превышения максимального количества попыток"""
        # Создаем профиль и сессию
        mfa_service.create_user_profile("test_user", UserRole.PARENT, phone_number="+1234567890")
        session_id = mfa_service.start_mfa_session("test_user", "device_1", {})
        
        # Отправляем код
        mfa_service.send_mfa_code(session_id, MFAMethod.SMS)
        
        # Делаем максимальное количество неверных попыток
        for _ in range(3):
            success, message = mfa_service.verify_mfa_code(session_id, MFAMethod.SMS, "000000")
            assert success is False
        
        # Проверяем, что сессия заблокирована
        session = mfa_service.active_sessions[session_id]
        assert session.status == MFAStatus.BLOCKED
        
        # Проверяем, что пользователь заблокирован
        profile = mfa_service.user_profiles["test_user"]
        assert profile.is_locked is True
    
    def test_get_session_status(self, mfa_service):
        """Тест получения статуса сессии"""
        # Создаем профиль и сессию
        mfa_service.create_user_profile("test_user", UserRole.PARENT)
        session_id = mfa_service.start_mfa_session("test_user", "device_1", {})
        
        # Получаем статус
        status = mfa_service.get_session_status(session_id)
        
        assert status is not None
        assert status["session_id"] == session_id
        assert status["user_id"] == "test_user"
        assert status["device_id"] == "device_1"
        assert status["status"] == MFAStatus.PENDING.value
        assert "methods" in status
        assert "verified_methods" in status
        assert "attempts" in status
        assert "is_expired" in status
    
    def test_get_session_status_nonexistent(self, mfa_service):
        """Тест получения статуса несуществующей сессии"""
        status = mfa_service.get_session_status("nonexistent_session")
        
        assert status is None
    
    def test_cleanup_expired_sessions(self, mfa_service):
        """Тест очистки истекших сессий"""
        # Создаем профиль и сессию
        mfa_service.create_user_profile("test_user", UserRole.PARENT, phone_number="+1234567890")
        session_id = mfa_service.start_mfa_session("test_user", "device_1", {})
        
        # Искусственно истекаем сессию
        session = mfa_service.active_sessions[session_id]
        session.expires_at = datetime.now() - timedelta(minutes=1)
        
        # Отправляем код и истекаем его
        mfa_service.send_mfa_code(session_id, MFAMethod.SMS)
        for code in mfa_service.mfa_codes.values():
            code.expires_at = datetime.now() - timedelta(minutes=1)
        
        # Очищаем истекшие сессии
        cleaned_count = mfa_service.cleanup_expired_sessions()
        
        assert cleaned_count == 1
        assert session_id not in mfa_service.active_sessions
        assert len(mfa_service.mfa_codes) == 0
    
    def test_default_methods_for_roles(self, mfa_service):
        """Тест методов по умолчанию для разных ролей"""
        # Создаем профили для разных ролей
        mfa_service.create_user_profile("child_user", UserRole.CHILD)
        mfa_service.create_user_profile("parent_user", UserRole.PARENT)
        mfa_service.create_user_profile("elderly_user", UserRole.ELDERLY)
        mfa_service.create_user_profile("admin_user", UserRole.ADMIN)
        
        # Проверяем методы для детей
        child_profile = mfa_service.user_profiles["child_user"]
        assert MFAMethod.PUSH in child_profile.enabled_methods
        assert MFAMethod.BIOMETRIC in child_profile.enabled_methods
        
        # Проверяем методы для родителей
        parent_profile = mfa_service.user_profiles["parent_user"]
        assert MFAMethod.SMS in parent_profile.enabled_methods
        assert MFAMethod.EMAIL in parent_profile.enabled_methods
        assert MFAMethod.TOTP in parent_profile.enabled_methods
        
        # Проверяем методы для пожилых
        elderly_profile = mfa_service.user_profiles["elderly_user"]
        assert MFAMethod.SMS in elderly_profile.enabled_methods
        assert MFAMethod.PUSH in elderly_profile.enabled_methods
        
        # Проверяем методы для администраторов
        admin_profile = mfa_service.user_profiles["admin_user"]
        assert MFAMethod.TOTP in admin_profile.enabled_methods
        assert MFAMethod.BIOMETRIC in admin_profile.enabled_methods
        assert MFAMethod.BACKUP_CODE in admin_profile.enabled_methods
    
    def test_required_methods_for_roles(self, mfa_service):
        """Тест требуемого количества методов для разных ролей"""
        # Создаем профили для разных ролей
        mfa_service.create_user_profile("child_user", UserRole.CHILD)
        mfa_service.create_user_profile("parent_user", UserRole.PARENT)
        mfa_service.create_user_profile("elderly_user", UserRole.ELDERLY)
        mfa_service.create_user_profile("admin_user", UserRole.ADMIN)
        
        # Проверяем требуемое количество методов
        assert mfa_service._get_required_methods("child_user") == 1
        assert mfa_service._get_required_methods("parent_user") == 2
        assert mfa_service._get_required_methods("elderly_user") == 1
        assert mfa_service._get_required_methods("admin_user") == 2
    
    def test_get_status(self, mfa_service):
        """Тест получения статуса сервиса"""
        # Создаем несколько профилей и сессий
        mfa_service.create_user_profile("user1", UserRole.PARENT, phone_number="+1234567890")
        mfa_service.create_user_profile("user2", UserRole.CHILD)
        
        session_id = mfa_service.start_mfa_session("user1", "device_1", {})
        mfa_service.send_mfa_code(session_id, MFAMethod.SMS)
        
        # Получаем статус
        status = mfa_service.get_status()
        
        assert "status" in status
        assert status["total_users"] >= 2  # Учитываем тестовые профили по умолчанию
        assert status["active_sessions"] == 1
        assert status["pending_sessions"] == 1
        assert status["verified_sessions"] == 0
        assert status["total_codes"] == 1
        assert status["blocked_users"] == 0
        assert status["locked_users"] == 0
        assert "users_by_role" in status
        assert "methods_usage" in status


if __name__ == "__main__":
    pytest.main([__file__])