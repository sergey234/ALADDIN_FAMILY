# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Universal Privacy Manager
Универсальный менеджер приватности для соответствия международным стандартам

Автор: ALADDIN Security Team
Версия: 3.0
Дата: 2025-01-06
"""

import logging
import time
from datetime import datetime
from enum import Enum
from typing import List

from core.base import ComponentStatus, SecurityBase

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PrivacyStandard(Enum):
    """Стандарты приватности"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    FZ152 = "fz152"
    PIPEDA = "pipeda"
    LGPD = "lgpd"
    PDPA = "pdpa"


class DataCategory(Enum):
    """Категории данных"""
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    FINANCIAL = "financial"
    HEALTH = "health"
    BIOMETRIC = "biometric"
    LOCATION = "location"
    BEHAVIORAL = "behavioral"


class ConsentType(Enum):
    """Типы согласия"""
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    OPT_IN = "opt_in"
    OPT_OUT = "opt_out"
    GRANULAR = "granular"


class PrivacyAction(Enum):
    """Действия с приватностью"""
    COLLECT = "collect"
    PROCESS = "process"
    STORE = "store"
    SHARE = "share"
    DELETE = "delete"
    ANONYMIZE = "anonymize"
    PORT = "port"


class PrivacyStatus(Enum):
    """Статус приватности"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


class PrivacyEvent:
    """Событие приватности"""

    def __init__(self, event_id: str, user_id: str, action: PrivacyAction,
                 data_category: DataCategory, timestamp: datetime = None):
        self.event_id = event_id
        self.user_id = user_id
        self.action = action
        self.data_category = data_category
        self.timestamp = timestamp or datetime.now()
        self.details = {}
        self.compliance_status = {}

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "user_id": self.user_id,
            "action": self.action.value,
            "data_category": self.data_category.value,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "compliance_status": self.compliance_status
        }


class ConsentRecord:
    """Запись согласия"""

    def __init__(self, user_id: str, consent_type: ConsentType,
                 data_category: DataCategory, granted: bool = False,
                 timestamp: datetime = None, expires_at: datetime = None):
        self.user_id = user_id
        self.consent_type = consent_type
        self.data_category = data_category
        self.granted = granted
        self.timestamp = timestamp or datetime.now()
        self.expires_at = expires_at
        self.legal_basis = ""
        self.withdrawal_method = ""

    def is_valid(self) -> bool:
        """Проверка валидности согласия"""
        if not self.granted:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "consent_type": self.consent_type.value,
            "data_category": self.data_category.value,
            "granted": self.granted,
            "timestamp": self.timestamp.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "legal_basis": self.legal_basis,
            "withdrawal_method": self.withdrawal_method
        }


class DataSubject:
    """Субъект данных"""

    def __init__(self, user_id: str, email: str = None, phone: str = None):
        self.user_id = user_id
        self.email = email
        self.phone = phone
        self.consents = []
        self.data_categories = set()
        self.privacy_preferences = {}

    def add_consent(self, consent: ConsentRecord):
        """Добавление согласия"""
        self.consents.append(consent)
        if consent.granted:
            self.data_categories.add(consent.data_category)

    def has_consent_for(self, data_category: DataCategory) -> bool:
        """Проверка наличия согласия для категории данных"""
        for consent in self.consents:
            if (consent.data_category == data_category and
                consent.is_valid()):
                return True
        return False

    def revoke_consent(self, data_category: DataCategory) -> bool:
        """Отзыв согласия"""
        revoked = False
        for consent in self.consents:
            if consent.data_category == data_category:
                consent.granted = False
                revoked = True
        if revoked:
            self.data_categories.discard(data_category)
        return revoked

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "phone": self.phone,
            "consents": [c.to_dict() for c in self.consents],
            "data_categories": [dc.value for dc in self.data_categories],
            "privacy_preferences": self.privacy_preferences
        }


class PrivacyComplianceChecker:
    """Проверка соответствия стандартам приватности"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def check_gdpr_compliance(self, event: PrivacyEvent) -> dict:
        """Проверка соответствия GDPR"""
        compliance = {
            "standard": "GDPR",
            "compliant": True,
            "issues": [],
            "recommendations": []
        }

        # Проверка правовой основы
        if not event.details.get("legal_basis"):
            compliance["compliant"] = False
            compliance["issues"].append("Отсутствует правовая основа")
            compliance["recommendations"].append(
                "Указать правовую основу обработки данных"
            )

        # Проверка уведомления о целях
        if not event.details.get("purpose"):
            compliance["compliant"] = False
            compliance["issues"].append("Не указана цель обработки")
            compliance["recommendations"].append(
                "Указать четкую цель обработки данных"
            )

        return compliance

    def check_ccpa_compliance(self, event: PrivacyEvent) -> dict:
        """Проверка соответствия CCPA"""
        compliance = {
            "standard": "CCPA",
            "compliant": True,
            "issues": [],
            "recommendations": []
        }

        # Проверка уведомления о продаже данных
        if event.action == PrivacyAction.SHARE:
            if not event.details.get("sale_notice"):
                compliance["compliant"] = False
                compliance["issues"].append(
                    "Отсутствует уведомление о продаже данных"
                )
                compliance["recommendations"].append(
                    "Уведомить о продаже персональных данных"
                )

        return compliance

    def check_fz152_compliance(self, event: PrivacyEvent) -> dict:
        """Проверка соответствия 152-ФЗ"""
        compliance = {
            "standard": "FZ152",
            "compliant": True,
            "issues": [],
            "recommendations": []
        }

        # Проверка согласия на обработку
        if not event.details.get("consent"):
            compliance["compliant"] = False
            compliance["issues"].append("Отсутствует согласие на обработку")
            compliance["recommendations"].append(
                "Получить согласие субъекта данных"
            )

        return compliance


class UniversalPrivacyManager(SecurityBase):
    """Универсальный менеджер приватности"""

    def __init__(self, name: str = "UniversalPrivacyManager"):
        super().__init__(name)
        self.data_subjects = {}
        self.privacy_events = []
        self.compliance_checker = PrivacyComplianceChecker()
        self.logger = logging.getLogger(__name__)

    def register_data_subject(self, user_id: str, email: str = None,
                             phone: str = None) -> bool:
        """Регистрация субъекта данных"""
        try:
            if user_id in self.data_subjects:
                self.logger.warning(
                    f"Субъект данных уже зарегистрирован: {user_id}"
                )
                return False

            data_subject = DataSubject(user_id, email, phone)
            self.data_subjects[user_id] = data_subject

            self.logger.info(f"Субъект данных зарегистрирован: {user_id}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка регистрации субъекта данных: {e}")
            return False

    def add_consent(self, user_id: str, consent_type: ConsentType,
                    data_category: DataCategory, granted: bool = True,
                    expires_at: datetime = None) -> bool:
        """Добавление согласия"""
        try:
            if user_id not in self.data_subjects:
                self.logger.error(f"Субъект данных не найден: {user_id}")
                return False

            consent = ConsentRecord(
                user_id=user_id,
                consent_type=consent_type,
                data_category=data_category,
                granted=granted,
                expires_at=expires_at
            )

            self.data_subjects[user_id].add_consent(consent)

            # Логирование события
            event = PrivacyEvent(
                event_id=f"consent_{int(time.time())}",
                user_id=user_id,
                action=PrivacyAction.COLLECT,
                data_category=data_category
            )
            event.details = {
                "consent_type": consent_type.value,
                "granted": granted,
                "expires_at": expires_at.isoformat() if expires_at else None
            }
            self.privacy_events.append(event)

            self.logger.info(
                f"Согласие добавлено: {user_id} - {data_category.value}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка добавления согласия: {e}")
            return False

    def check_consent(self, user_id: str, data_category: DataCategory) -> bool:
        """Проверка согласия"""
        try:
            if user_id not in self.data_subjects:
                self.logger.warning(f"Субъект данных не найден: {user_id}")
                return False

            return self.data_subjects[user_id].has_consent_for(data_category)

        except Exception as e:
            self.logger.error(f"Ошибка проверки согласия: {e}")
            return False

    def revoke_consent(self, user_id: str, data_category: DataCategory) -> bool:
        """Отзыв согласия"""
        try:
            if user_id not in self.data_subjects:
                self.logger.error(f"Субъект данных не найден: {user_id}")
                return False

            success = self.data_subjects[user_id].revoke_consent(data_category)

            if success:
                # Логирование события
                event = PrivacyEvent(
                    event_id=f"revoke_{int(time.time())}",
                    user_id=user_id,
                    action=PrivacyAction.DELETE,
                    data_category=data_category
                )
                event.details = {"revoked": True}
                self.privacy_events.append(event)

                self.logger.info(f"Согласие отозвано: {user_id} - {data_category.value}")

            return success

        except Exception as e:
            self.logger.error(f"Ошибка отзыва согласия: {e}")
            return False

    def process_data_action(self, user_id: str, action: PrivacyAction,
                           data_category: DataCategory,
                           details: dict = None) -> bool:
        """Обработка действия с данными"""
        try:
            # Проверка согласия
            if not self.check_consent(user_id, data_category):
                self.logger.warning(
                    f"Нет согласия для действия: {user_id} - {action.value}"
                )
                return False

            # Создание события
            event = PrivacyEvent(
                event_id=f"action_{int(time.time())}",
                user_id=user_id,
                action=action,
                data_category=data_category
            )
            event.details = details or {}

            # Проверка соответствия стандартам
            event.compliance_status = self._check_compliance(event)

            self.privacy_events.append(event)

            self.logger.info(f"Действие обработано: {user_id} - {action.value}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка обработки действия: {e}")
            return False

    def _check_compliance(self, event: PrivacyEvent) -> dict:
        """Проверка соответствия стандартам"""
        compliance_results = {}

        # Проверка GDPR
        compliance_results["gdpr"] = (
            self.compliance_checker.check_gdpr_compliance(event)
        )

        # Проверка CCPA
        compliance_results["ccpa"] = (
            self.compliance_checker.check_ccpa_compliance(event)
        )

        # Проверка 152-ФЗ
        compliance_results["fz152"] = (
            self.compliance_checker.check_fz152_compliance(event)
        )

        return compliance_results

    def get_data_subject_info(self, user_id: str) -> dict:
        """Получение информации о субъекте данных"""
        try:
            if user_id not in self.data_subjects:
                return {"error": "Субъект данных не найден"}

            return self.data_subjects[user_id].to_dict()

        except Exception as e:
            self.logger.error(f"Ошибка получения информации: {e}")
            return {"error": str(e)}

    def get_privacy_events(self, user_id: str = None, limit: int = 100) -> List[dict]:
        """Получение событий приватности"""
        try:
            events = self.privacy_events

            if user_id:
                events = [e for e in events if e.user_id == user_id]

            # Ограничение количества
            if limit > 0:
                events = events[-limit:]

            return [event.to_dict() for event in events]

        except Exception as e:
            self.logger.error(f"Ошибка получения событий: {e}")
            return []

    def get_compliance_report(self) -> dict:
        """Получение отчета о соответствии"""
        try:
            total_events = len(self.privacy_events)
            compliant_events = 0
            standards_compliance = {}

            for event in self.privacy_events:
                if event.compliance_status:
                    for standard, compliance in event.compliance_status.items():
                        if standard not in standards_compliance:
                            standards_compliance[standard] = {
                                "total": 0,
                                "compliant": 0,
                                "issues": []
                            }

                        standards_compliance[standard]["total"] += 1
                        if compliance.get("compliant", False):
                            standards_compliance[standard]["compliant"] += 1
                            compliant_events += 1

                        # Сбор проблем
                        issues = compliance.get("issues", [])
                        standards_compliance[standard]["issues"].extend(issues)

            return {
                "total_events": total_events,
                "compliant_events": compliant_events,
                "compliance_rate": (compliant_events / total_events * 100) if total_events > 0 else 0,
                "standards": standards_compliance,
                "data_subjects_count": len(self.data_subjects),
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Ошибка генерации отчета: {e}")
            return {"error": str(e)}

    def export_data(self, user_id: str) -> dict:
        """Экспорт данных субъекта"""
        try:
            if user_id not in self.data_subjects:
                return {"error": "Субъект данных не найден"}

            data_subject = self.data_subjects[user_id]
            events = self.get_privacy_events(user_id)

            return {
                "data_subject": data_subject.to_dict(),
                "privacy_events": events,
                "exported_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Ошибка экспорта данных: {e}")
            return {"error": str(e)}

    def delete_data(self, user_id: str) -> bool:
        """Удаление данных субъекта"""
        try:
            if user_id not in self.data_subjects:
                self.logger.warning(f"Субъект данных не найден: {user_id}")
                return False

            # Удаление субъекта данных
            del self.data_subjects[user_id]

            # Удаление связанных событий
            self.privacy_events = [
                e for e in self.privacy_events if e.user_id != user_id
            ]

            # Логирование события удаления
            event = PrivacyEvent(
                event_id=f"delete_{int(time.time())}",
                user_id=user_id,
                action=PrivacyAction.DELETE,
                data_category=DataCategory.PERSONAL
            )
            event.details = {"deleted": True}
            self.privacy_events.append(event)

            self.logger.info(f"Данные субъекта удалены: {user_id}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка удаления данных: {e}")
            return False

    def get_status(self) -> ComponentStatus:
        """Получение статуса компонента"""
        try:
            return ComponentStatus(
                status="active",
                health_score=95.0,
                last_update=datetime.now(),
                details={
                    "data_subjects_count": len(self.data_subjects),
                    "privacy_events_count": len(self.privacy_events),
                    "compliance_checker_active": True
                }
            )
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return ComponentStatus(
                status="error",
                health_score=0.0,
                last_update=datetime.now(),
                details={"error": str(e)}
            )


# Пример использования
def main():
    """Пример использования UniversalPrivacyManager"""
    # Создаем менеджер приватности
    manager = UniversalPrivacyManager()

    # Регистрируем субъекта данных
    manager.register_data_subject("user123", "user@example.com", "+1234567890")

    # Добавляем согласие
    manager.add_consent(
        user_id="user123",
        consent_type=ConsentType.EXPLICIT,
        data_category=DataCategory.PERSONAL,
        granted=True
    )

    # Проверяем согласие
    has_consent = manager.check_consent("user123", DataCategory.PERSONAL)
    print(f"Есть согласие: {has_consent}")

    # Обрабатываем действие с данными
    manager.process_data_action(
        user_id="user123",
        action=PrivacyAction.PROCESS,
        data_category=DataCategory.PERSONAL,
        details={"purpose": "аналитика", "legal_basis": "согласие"}
    )

    # Получаем отчет о соответствии
    report = manager.get_compliance_report()
    print(f"Отчет о соответствии: {report}")

    # Экспортируем данные
    export_data = manager.export_data("user123")
    print(f"Экспорт данных: {export_data}")


if __name__ == "__main__":
    main()
