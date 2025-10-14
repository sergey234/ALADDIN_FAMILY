"""
Тесты для ElderlyProtection
"""

import pytest
from datetime import datetime
from security.family.elderly_protection import (
    ElderlyProtection,
    ThreatType,
    RiskLevel,
    ProtectionAction,
    FamilyContact
)


class TestElderlyProtection:
    """Тесты для ElderlyProtection"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.protection = ElderlyProtection()
        self.elderly_id = "elderly_001"
    
    def test_analyze_phone_call_safe(self):
        """Тест анализа безопасного звонка"""
        risk, action, reason = self.protection.analyze_phone_call(
            self.elderly_id, "+7-123-456-78-90", "Иван", "Привет, как дела?"
        )
        
        assert risk == RiskLevel.LOW
        assert action == ProtectionAction.ALLOW
        assert "безопасен" in reason.lower()
    
    def test_analyze_phone_call_scam(self):
        """Тест анализа мошеннического звонка"""
        risk, action, reason = self.protection.analyze_phone_call(
            self.elderly_id, "+7-999-888-77-66", "Банк", 
            "Вы выиграли приз! Срочно переведите деньги для получения!"
        )
        
        assert risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert action in [ProtectionAction.BLOCK, ProtectionAction.NOTIFY_FAMILY]
        assert "угроза" in reason.lower() or "риск" in reason.lower()
    
    def test_analyze_email_safe(self):
        """Тест анализа безопасного email"""
        risk, action, reason = self.protection.analyze_email(
            self.elderly_id, "friend@example.com", "Привет", "Как дела?"
        )
        
        assert risk == RiskLevel.LOW
        assert action == ProtectionAction.ALLOW
        assert "безопасен" in reason.lower()
    
    def test_analyze_email_phishing(self):
        """Тест анализа фишингового email"""
        risk, action, reason = self.protection.analyze_email(
            self.elderly_id, "noreply@bank.ru", "СРОЧНО! Блокировка карты!",
            "Немедленно подтвердите данные карты для разблокировки!"
        )
        
        assert risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert action in [ProtectionAction.BLOCK, ProtectionAction.NOTIFY_FAMILY]
        assert "угроза" in reason.lower() or "риск" in reason.lower()
    
    def test_analyze_website_safe(self):
        """Тест анализа безопасного сайта"""
        risk, action, reason = self.protection.analyze_website(
            self.elderly_id, "https://google.com", "Поисковая система"
        )
        
        assert risk == RiskLevel.LOW
        assert action == ProtectionAction.ALLOW
        assert "безопасен" in reason.lower()
    
    def test_analyze_website_suspicious(self):
        """Тест анализа подозрительного сайта"""
        risk, action, reason = self.protection.analyze_website(
            self.elderly_id, "http://fake-bank.tk", "Бесплатные деньги! Выигрыш!"
        )
        
        assert risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert action in [ProtectionAction.BLOCK, ProtectionAction.NOTIFY_FAMILY]
        assert "угроза" in reason.lower() or "риск" in reason.lower()
    
    def test_block_contact(self):
        """Тест блокировки контакта"""
        phone_number = "+7-999-888-77-66"
        result = self.protection.block_contact(phone_number, "phone")
        
        assert result is True
        assert phone_number in self.protection.blocked_numbers
        
        # Проверяем, что звонок блокируется
        risk, action, reason = self.protection.analyze_phone_call(
            self.elderly_id, phone_number, "Тест", "Любое сообщение"
        )
        
        assert risk == RiskLevel.CRITICAL
        assert action == ProtectionAction.BLOCK
        assert "заблокирован" in reason.lower()
    
    def test_add_trusted_contact(self):
        """Тест добавления доверенного контакта"""
        phone_number = "+7-123-456-78-90"
        result = self.protection.add_trusted_contact(phone_number, "phone")
        
        assert result is True
        assert phone_number in self.protection.trusted_contacts
        
        # Проверяем, что звонок разрешается
        risk, action, reason = self.protection.analyze_phone_call(
            self.elderly_id, phone_number, "Тест", "Любое сообщение"
        )
        
        assert risk == RiskLevel.LOW
        assert action == ProtectionAction.ALLOW
        assert "доверенный" in reason.lower()
    
    def test_add_family_contact(self):
        """Тест добавления контакта семьи"""
        contact = FamilyContact(
            contact_id="contact_001",
            name="Сын",
            phone="+7-111-222-33-44",
            email="son@example.com",
            relationship="son",
            priority=1
        )
        
        result = self.protection.add_family_contact(self.elderly_id, contact)
        
        assert result is True
        assert self.elderly_id in self.protection.family_contacts
        assert len(self.protection.family_contacts[self.elderly_id]) == 1
    
    def test_notify_family(self):
        """Тест уведомления семьи"""
        # Добавляем контакт семьи
        contact = FamilyContact(
            contact_id="contact_001",
            name="Дочь",
            phone="+7-111-222-33-44",
            email="daughter@example.com",
            relationship="daughter",
            priority=1
        )
        self.protection.add_family_contact(self.elderly_id, contact)
        
        result = self.protection.notify_family(
            self.elderly_id, "Обнаружена подозрительная активность", 1
        )
        
        assert result is True
    
    def test_get_elderly_activity_report(self):
        """Тест получения отчета об активности"""
        # Создаем тестовую активность
        self.protection.analyze_phone_call(
            self.elderly_id, "+7-999-888-77-66", "Мошенник", 
            "Вы выиграли приз! Срочно переведите деньги!"
        )
        
        report = self.protection.get_elderly_activity_report(self.elderly_id)
        
        assert "elderly_id" in report
        assert report["elderly_id"] == self.elderly_id
        assert "total_activities" in report
        assert "threats_detected" in report
        assert "threat_statistics" in report
        assert "risk_statistics" in report
    
    def test_get_status(self):
        """Тест получения статуса системы"""
        status = self.protection.get_status()
        
        assert status["status"] == "active"
        assert "total_elderly" in status
        assert "total_activities" in status
        assert "scam_patterns_count" in status
        assert "blocked_numbers_count" in status
        assert "trusted_contacts_count" in status


if __name__ == "__main__":
    pytest.main([__file__])
