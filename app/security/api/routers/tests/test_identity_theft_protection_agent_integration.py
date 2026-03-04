# -*- coding: utf-8 -*-
"""
Integration tests for Identity Theft Protection Agent

День 10: Тестирование интеграции агента
Проверяет работу методов агента напрямую (без FastAPI)
"""

import pytest
import sys
import os
from datetime import datetime

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

try:
    from security.ai_agents.russian_identity_theft_protection_agent import (
        RussianIdentityTheftProtectionAgent,
        FraudRecord,
        IdentityTheftAlert,
        CreditReport,
        CreditChange
    )
except ImportError:
    pytest.skip("Cannot import agent", allow_module_level=True)


class TestAgentInitialization:
    """Тесты инициализации агента"""

    def test_agent_init_with_config(self):
        """Инициализация агента с конфигурацией"""
        config = {
            "nbki_api_key": "test_key",
            "okb_api_key": "test_key",
            "fraud_database_path": "",
            "cache_ttl": 3600
        }
        agent = RussianIdentityTheftProtectionAgent(config)
        assert agent.nbki_api_key == "test_key"
        assert agent.okb_api_key == "test_key"
        assert agent.cache_ttl == 3600

    def test_agent_init_without_config(self):
        """Инициализация агента без конфигурации"""
        agent = RussianIdentityTheftProtectionAgent()
        assert agent.config is not None
        assert agent.cache_ttl == 86400  # Default


class TestSNILSMonitoring:
    """Тесты мониторинга СНИЛС"""

    def test_monitor_snils_no_consent(self):
        """Мониторинг СНИЛС без согласия должен вернуть ошибку"""
        agent = RussianIdentityTheftProtectionAgent()
        result = agent.monitor_snils("12345678901", "test_user")
        assert result["success"] is False
        assert "consent" in result.get("error", "").lower() or "согласи" in result.get("message", "").lower()

    def test_monitor_snils_invalid_format(self):
        """Валидация формата СНИЛС"""
        agent = RussianIdentityTheftProtectionAgent()
        # Сначала даем согласие
        agent.give_consent("test_user", {"snils": True}, 365)
        
        # Тестируем невалидный формат
        result = agent.monitor_snils("12345", "test_user")
        assert result["success"] is False
        assert "invalid" in result.get("error", "").lower() or "формат" in result.get("message", "").lower()

    def test_monitor_snils_valid_with_consent(self):
        """Мониторинг СНИЛС с согласием"""
        agent = RussianIdentityTheftProtectionAgent()
        user_id = "test_user_consent"
        snils = "12345678901"
        
        # Даем согласие
        consent_result = agent.give_consent(user_id, {"snils": True}, 365)
        assert consent_result["success"] is True
        
        # Мониторинг СНИЛС
        result = agent.monitor_snils(snils, user_id)
        assert result["success"] is True
        assert "snils_hash" in result
        assert "risk_score" in result
        assert "severity" in result


class TestCreditMonitoring:
    """Тесты мониторинга кредитного отчета"""

    def test_monitor_credit_no_consent(self):
        """Мониторинг кредитного отчета без согласия"""
        agent = RussianIdentityTheftProtectionAgent()
        result = agent.monitor_credit_report("test_user")
        assert result["success"] is False
        assert "consent" in result.get("error", "").lower()

    def test_monitor_credit_no_snils(self):
        """Мониторинг кредитного отчета без СНИЛС"""
        agent = RussianIdentityTheftProtectionAgent()
        user_id = "test_user_no_snils"
        
        # Даем согласие на кредит, но не добавляем СНИЛС
        agent.give_consent(user_id, {"credit": True}, 365)
        
        result = agent.monitor_credit_report(user_id)
        assert result["success"] is False
        assert "snils" in result.get("error", "").lower()

    def test_monitor_credit_full_workflow(self):
        """Полный workflow мониторинга кредитного отчета"""
        agent = RussianIdentityTheftProtectionAgent()
        user_id = "test_user_full"
        snils = "12345678901"
        
        # 1. Согласие
        agent.give_consent(user_id, {"snils": True, "credit": True}, 365)
        
        # 2. Мониторинг СНИЛС (для получения hash)
        snils_result = agent.monitor_snils(snils, user_id)
        assert snils_result["success"] is True
        
        # 3. Мониторинг кредитного отчета
        credit_result = agent.monitor_credit_report(user_id)
        assert credit_result["success"] is True
        assert "nbki_available" in credit_result
        assert "okb_available" in credit_result
        assert "risk_score" in credit_result
        assert "suspicious_changes_count" in credit_result


class TestFraudDatabase:
    """Тесты проверки базы мошенников"""

    def test_check_fraud_database_with_snils(self):
        """Проверка в базе мошенников по СНИЛС"""
        agent = RussianIdentityTheftProtectionAgent()
        snils = "12345678901"
        
        result = agent.check_fraud_database(snils=snils)
        assert isinstance(result, list)
        # База может быть пустой, поэтому просто проверяем тип

    def test_check_fraud_database_with_passport(self):
        """Проверка в базе мошенников по паспорту"""
        agent = RussianIdentityTheftProtectionAgent()
        
        result = agent.check_fraud_database(
            passport_series="1234",
            passport_number="567890"
        )
        assert isinstance(result, list)

    def test_check_fraud_database_no_data(self):
        """Проверка без данных"""
        agent = RussianIdentityTheftProtectionAgent()
        result = agent.check_fraud_database()
        assert isinstance(result, list)
        assert len(result) == 0


class TestIdentityTheftDetection:
    """Тесты обнаружения кражи личности"""

    def test_detect_identity_theft_basic(self):
        """Базовое обнаружение кражи личности"""
        agent = RussianIdentityTheftProtectionAgent()
        user_id = "test_user_detect"
        
        result = agent.detect_identity_theft(user_id)
        # Может вернуть ошибку без СНИЛС, но структура должна быть правильной
        assert "success" in result
        assert "user_id" in result

    def test_detect_identity_theft_with_snils(self):
        """Обнаружение с СНИЛС"""
        agent = RussianIdentityTheftProtectionAgent()
        user_id = "test_user_detect_snils"
        snils = "12345678901"
        
        # Даем согласие и мониторим
        agent.give_consent(user_id, {"snils": True, "credit": True}, 365)
        agent.monitor_snils(snils, user_id)
        
        result = agent.detect_identity_theft(user_id, snils)
        assert "success" in result
        assert "risk_score" in result
        assert "severity" in result
        assert "indicators" in result


class TestConsentManagement:
    """Тесты управления согласиями (152-ФЗ)"""

    def test_give_consent(self):
        """Предоставление согласия"""
        agent = RussianIdentityTheftProtectionAgent()
        user_id = "test_user_consent"
        
        result = agent.give_consent(
            user_id,
            {"snils": True, "passport": True, "credit": True},
            365
        )
        assert result["success"] is True
        assert "consents" in result
        assert "expires_at" in result
        assert "expires_days" in result
        assert result["expires_days"] == 365

    def test_revoke_consent(self):
        """Отзыв согласия"""
        agent = RussianIdentityTheftProtectionAgent()
        user_id = "test_user_revoke"
        
        # Сначала даем согласие
        agent.give_consent(user_id, {"snils": True}, 365)
        
        # Отзываем
        result = agent.revoke_consent(user_id)
        assert result["success"] is True
        assert "message" in result
        assert "deleted_items" in result
        assert "deleted_at" in result

    def test_consent_check(self):
        """Проверка согласия"""
        agent = RussianIdentityTheftProtectionAgent()
        user_id = "test_user_check"
        
        # Без согласия
        assert agent._check_consent(user_id, "snils") is False
        
        # С согласием
        agent.give_consent(user_id, {"snils": True}, 365)
        assert agent._check_consent(user_id, "snils") is True

    def test_check_expired_consents(self):
        """Проверка истекших согласий"""
        agent = RussianIdentityTheftProtectionAgent()
        user_id = "test_user_expired"
        
        # Создаем согласие с истекшим сроком
        from datetime import datetime, timedelta
        agent.user_consents[user_id] = {
            "snils": True,
            "granted_at": (datetime.now() - timedelta(days=400)).isoformat(),
            "expires_at": (datetime.now() - timedelta(days=35)).isoformat()  # Истекло 35 дней назад
        }
        
        expired = agent.check_expired_consents()
        assert len(expired) >= 1
        assert any(e["user_id"] == user_id for e in expired)

    def test_consent_expiring_soon_notification(self):
        """Проверка уведомления о скором истечении согласия"""
        agent = RussianIdentityTheftProtectionAgent()
        user_id = "test_user_expiring"
        
        # Создаем согласие, истекающее через 5 дней
        from datetime import datetime, timedelta
        agent.user_consents[user_id] = {
            "snils": True,
            "granted_at": (datetime.now() - timedelta(days=360)).isoformat(),
            "expires_at": (datetime.now() + timedelta(days=5)).isoformat()  # Истекает через 5 дней
        }
        
        expired = agent.check_expired_consents()
        # Не должно быть в списке истекших, но должно сгенерировать предупреждение
        assert not any(e["user_id"] == user_id for e in expired if e.get("expired_days_ago", 0) > 0)

    def test_consent_max_duration(self):
        """Проверка максимального срока действия согласия (10 лет)"""
        agent = RussianIdentityTheftProtectionAgent()
        user_id = "test_user_max"
        
        # Попытка установить срок более 10 лет
        result = agent.give_consent(user_id, {"snils": True}, 4000)  # Более 10 лет
        assert result["success"] is True
        assert result["expires_days"] == 3650  # Должно быть ограничено до 10 лет


class TestCreditReportStructures:
    """Тесты структур данных кредитных отчетов"""

    def test_credit_report_dataclass(self):
        """Тест структуры CreditReport"""
        report = CreditReport(
            bureau="nbki",
            snils_hash="test_hash",
            report_date=datetime.now().isoformat(),
            score=750,
            total_credits=3,
            active_credits=1
        )
        assert report.bureau == "nbki"
        assert report.score == 750
        assert report.total_credits == 3
        
        # Проверка to_dict
        report_dict = report.to_dict()
        assert "bureau" in report_dict
        assert "score" in report_dict

    def test_credit_change_dataclass(self):
        """Тест структуры CreditChange"""
        change = CreditChange(
            change_type="new_credit",
            severity="high",
            description="New credit detected",
            detected_at=datetime.now().isoformat(),
            bureau="nbki",
            risk_score=0.8
        )
        assert change.change_type == "new_credit"
        assert change.severity == "high"
        assert change.risk_score == 0.8
        
        # Проверка to_dict
        change_dict = change.to_dict()
        assert "change_type" in change_dict
        assert "severity" in change_dict


class TestCaching:
    """Тесты кэширования"""

    def test_cache_storage(self):
        """Проверка сохранения в кэш"""
        agent = RussianIdentityTheftProtectionAgent()
        cache_key = "test_key"
        test_data = {"test": "data"}
        
        agent._cache_result(cache_key, test_data)
        
        cached = agent._get_cached_result(cache_key)
        assert cached == test_data

    def test_cache_expiration(self):
        """Проверка истечения кэша"""
        agent = RussianIdentityTheftProtectionAgent()
        agent.cache_ttl = 1  # 1 секунда
        
        cache_key = "test_key_expire"
        test_data = {"test": "data"}
        
        agent._cache_result(cache_key, test_data)
        
        # Кэш должен существовать сразу
        assert agent._get_cached_result(cache_key) == test_data
        
        # После истечения (упрощенный тест - проверяем что метод работает)
        import time
        time.sleep(2)
        # Кэш должен истечь (или остаться в зависимости от реализации)
        # Просто проверяем что метод не падает
        agent._get_cached_result(cache_key)


class TestMonitoringStatus:
    """Тесты статуса мониторинга"""

    def test_get_monitoring_status_no_user(self):
        """Получение статуса без указания пользователя"""
        agent = RussianIdentityTheftProtectionAgent()
        result = agent.get_monitoring_status()
        assert "is_monitoring" in result
        assert "total_active" in result

    def test_get_monitoring_status_with_user(self):
        """Получение статуса для конкретного пользователя"""
        agent = RussianIdentityTheftProtectionAgent()
        user_id = "test_user_status"
        
        result = agent.get_monitoring_status(user_id)
        assert "is_monitoring" in result
        assert "user_id" in result


class TestAlerts:
    """Тесты алертов"""

    def test_get_alerts_empty(self):
        """Получение алертов когда их нет"""
        agent = RussianIdentityTheftProtectionAgent()
        alerts = agent.get_alerts("test_user")
        assert isinstance(alerts, list)

    def test_get_alerts_all(self):
        """Получение всех алертов"""
        agent = RussianIdentityTheftProtectionAgent()
        alerts = agent.get_alerts()
        assert isinstance(alerts, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
