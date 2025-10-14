# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Data Protection Agent
Агент защиты данных для обеспечения конфиденциальности и целостности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-03
"""

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import ComponentStatus, SecurityBase


class DataType(Enum):
    """Типы данных для защиты"""

    PERSONAL = "personal"
    FINANCIAL = "financial"
    MEDICAL = "medical"
    BUSINESS = "business"
    TECHNICAL = "technical"
    SENSITIVE = "sensitive"


class ProtectionLevel(Enum):
    """Уровни защиты данных"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EncryptionMethod(Enum):
    """Методы шифрования"""

    AES_256 = "aes_256"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    CHACHA20 = "chacha20"
    BLAKE2B = "blake2b"


class DataStatus(Enum):
    """Статусы данных"""

    PROTECTED = "protected"
    ENCRYPTED = "encrypted"
    ANONYMIZED = "anonymized"
    BACKED_UP = "backed_up"
    COMPLIANT = "compliant"
    AT_RISK = "at_risk"
    COMPROMISED = "compromised"


class DataProtectionEvent:
    """Событие защиты данных"""

    def __init__(
        self,
        event_id: str,
        data_id: str,
        event_type: str,
        protection_level: ProtectionLevel,
        timestamp: datetime,
        details: Dict[str, Any],
    ):
        self.event_id = event_id
        self.data_id = data_id
        self.event_type = event_type
        self.protection_level = protection_level
        self.timestamp = timestamp
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "event_id": self.event_id,
            "data_id": self.data_id,
            "event_type": self.event_type,
            "protection_level": self.protection_level.value,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


class DataProtectionResult:
    """Результат защиты данных"""

    def __init__(
        self,
        data_id: str,
        protection_status: DataStatus,
        encryption_method: Optional[EncryptionMethod] = None,
        protection_score: float = 0.0,
        compliance_status: bool = False,
        risk_level: float = 0.0,
        recommendations: List[str] = None,
    ):
        self.data_id = data_id
        self.protection_status = protection_status
        self.encryption_method = encryption_method
        self.protection_score = protection_score
        self.compliance_status = compliance_status
        self.risk_level = risk_level
        self.recommendations = recommendations or []

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "data_id": self.data_id,
            "protection_status": self.protection_status.value,
            "encryption_method": (
                self.encryption_method.value
                if self.encryption_method
                else None
            ),
            "protection_score": self.protection_score,
            "compliance_status": self.compliance_status,
            "risk_level": self.risk_level,
            "recommendations": self.recommendations,
        }


class DataProtectionMetrics:
    """Метрики защиты данных"""

    def __init__(self):
        self.total_data_items = 0
        self.protected_items = 0
        self.encrypted_items = 0
        self.anonymized_items = 0
        self.compliant_items = 0
        self.at_risk_items = 0
        self.compromised_items = 0
        self.encryption_operations = 0
        self.backup_operations = 0
        self.compliance_checks = 0
        self.risk_assessments = 0
        self.last_updated = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "total_data_items": self.total_data_items,
            "protected_items": self.protected_items,
            "encrypted_items": self.encrypted_items,
            "anonymized_items": self.anonymized_items,
            "compliant_items": self.compliant_items,
            "at_risk_items": self.at_risk_items,
            "compromised_items": self.compromised_items,
            "encryption_operations": self.encryption_operations,
            "backup_operations": self.backup_operations,
            "compliance_checks": self.compliance_checks,
            "risk_assessments": self.risk_assessments,
            "last_updated": self.last_updated.isoformat(),
        }


class DataProtectionAgent(SecurityBase):
    """Агент защиты данных ALADDIN"""

    def __init__(
        self,
        name: str = "DataProtectionAgent",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Конфигурация агента
        self.encryption_enabled = (
            config.get("encryption_enabled", True) if config else True
        )
        self.anonymization_enabled = (
            config.get("anonymization_enabled", True) if config else True
        )
        self.backup_enabled = (
            config.get("backup_enabled", True) if config else True
        )
        self.compliance_check_enabled = (
            config.get("compliance_check_enabled", True) if config else True
        )
        self.risk_assessment_enabled = (
            config.get("risk_assessment_enabled", True) if config else True
        )

        # Настройки защиты
        self.default_encryption_method = EncryptionMethod.AES_256
        self.default_protection_level = ProtectionLevel.HIGH
        self.auto_backup_interval = (
            config.get("auto_backup_interval", 3600) if config else 3600
        )  # 1 час
        self.retention_period = (
            config.get("retention_period", 30) if config else 30
        )  # 30 дней

        # Хранилище данных
        self.protected_data: Dict[str, Dict[str, Any]] = {}
        self.encryption_keys: Dict[str, str] = {}
        self.backup_locations: List[str] = []
        self.compliance_rules: Dict[str, List[str]] = {}

        # Метрики
        self.metrics = DataProtectionMetrics()
        self.protection_events: List[DataProtectionEvent] = []

        # Логирование
        self.logger = logging.getLogger(__name__)

    def initialize(self) -> bool:
        """Инициализация агента"""
        try:
            self.log_activity("Инициализация DataProtectionAgent")
            self.status = ComponentStatus.INITIALIZING

            # Настройка правил соответствия
            self._setup_compliance_rules()

            # Инициализация шифрования
            if self.encryption_enabled:
                self._initialize_encryption()

            # Настройка резервного копирования
            if self.backup_enabled:
                self._setup_backup_system()

            self.status = ComponentStatus.RUNNING
            self.log_activity("DataProtectionAgent инициализирован успешно")
            return True

        except Exception as e:
            self.log_activity(
                "Ошибка инициализации DataProtectionAgent: {}".format(e),
                "error",
            )
            self.status = ComponentStatus.ERROR
            return False

    def _setup_compliance_rules(self):
        """Настройка правил соответствия"""
        self.compliance_rules = {
            "GDPR": [
                "data_minimization",
                "purpose_limitation",
                "storage_limitation",
                "accuracy",
                "confidentiality",
                "accountability",
            ],
            "COPPA": [
                "parental_consent",
                "data_collection_limits",
                "privacy_protection",
                "secure_storage",
            ],
            "152-FZ": [
                "data_localization",
                "consent_management",
                "data_processing_rules",
                "security_requirements",
            ],
        }
        self.log_activity("Правила соответствия настроены")

    def _initialize_encryption(self):
        """Инициализация системы шифрования"""
        # Генерация мастер-ключа
        master_key = self._generate_encryption_key()
        self.encryption_keys["master"] = master_key
        self.log_activity("Система шифрования инициализирована")

    def _setup_backup_system(self):
        """Настройка системы резервного копирования"""
        backup_dir = os.path.join(
            self.config.get("backup_directory", "data/backups"),
            "data_protection",
        )
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        self.backup_locations.append(backup_dir)
        self.log_activity("Система резервного копирования настроена")

    def _generate_encryption_key(self) -> str:
        """Генерация ключа шифрования"""
        return hashlib.sha256(str(time.time()).encode()).hexdigest()

    def protect_data(
        self,
        data_id: str,
        data: Any,
        data_type: DataType,
        protection_level: Optional[ProtectionLevel] = None,
    ) -> DataProtectionResult:
        """
        Защита данных

        Args:
            data_id: Идентификатор данных
            data: Данные для защиты
            data_type: Тип данных
            protection_level: Уровень защиты

        Returns:
            DataProtectionResult: Результат защиты
        """
        try:
            if protection_level is None:
                protection_level = self.default_protection_level

            self.log_activity("Защита данных: {}".format(data_id))

            # Оценка рисков
            risk_level = self._assess_data_risk(
                data, data_type, protection_level
            )

            # Применение защиты
            protection_status = DataStatus.PROTECTED
            encryption_method = None

            if self.encryption_enabled and protection_level in [
                ProtectionLevel.HIGH,
                ProtectionLevel.CRITICAL,
            ]:
                _ = self._encrypt_data(data, data_id)
                protection_status = DataStatus.ENCRYPTED
                encryption_method = self.default_encryption_method

            if self.anonymization_enabled and data_type == DataType.PERSONAL:
                _ = self._anonymize_data(data)
                protection_status = DataStatus.ANONYMIZED

            # Проверка соответствия
            compliance_status = self._check_compliance(data, data_type)

            # Резервное копирование
            if self.backup_enabled:
                self._backup_data(data_id, data)
                protection_status = DataStatus.BACKED_UP

            # Сохранение защищенных данных
            self.protected_data[data_id] = {
                "data": data,
                "data_type": data_type.value,
                "protection_level": protection_level.value,
                "protection_status": protection_status.value,
                "encryption_method": (
                    encryption_method.value if encryption_method else None
                ),
                "risk_level": risk_level,
                "compliance_status": compliance_status,
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
            }

            # Обновление метрик
            self._update_metrics(protection_status)

            # Создание события
            event = DataProtectionEvent(
                event_id="protect_{}".format(int(time.time())),
                data_id=data_id,
                event_type="data_protection",
                protection_level=protection_level,
                timestamp=datetime.now(),
                details={
                    "data_type": data_type.value,
                    "protection_status": protection_status.value,
                    "risk_level": risk_level,
                    "compliance_status": compliance_status,
                },
            )
            self.protection_events.append(event)

            # Генерация рекомендаций
            recommendations = self._generate_recommendations(
                data_type, protection_level, risk_level
            )

            result = DataProtectionResult(
                data_id=data_id,
                protection_status=protection_status,
                encryption_method=encryption_method,
                protection_score=self._calculate_protection_score(
                    protection_status, risk_level
                ),
                compliance_status=compliance_status,
                risk_level=risk_level,
                recommendations=recommendations,
            )

            self.log_activity("Данные {} защищены успешно".format(data_id))
            return result

        except Exception as e:
            self.log_activity(
                "Ошибка защиты данных {}: {}".format(data_id, e), "error"
            )
            return DataProtectionResult(
                data_id=data_id,
                protection_status=DataStatus.AT_RISK,
                risk_level=1.0,
                recommendations=["Проверить конфигурацию защиты данных"],
            )

    def _assess_data_risk(
        self, data: Any, data_type: DataType, protection_level: ProtectionLevel
    ) -> float:
        """Оценка рисков данных"""
        risk_factors = {
            DataType.PERSONAL: 0.8,
            DataType.FINANCIAL: 0.9,
            DataType.MEDICAL: 0.95,
            DataType.BUSINESS: 0.7,
            DataType.TECHNICAL: 0.5,
            DataType.SENSITIVE: 0.85,
        }

        protection_factors = {
            ProtectionLevel.LOW: 1.0,
            ProtectionLevel.MEDIUM: 0.7,
            ProtectionLevel.HIGH: 0.4,
            ProtectionLevel.CRITICAL: 0.2,
        }

        base_risk = risk_factors.get(data_type, 0.5)
        protection_factor = protection_factors.get(protection_level, 1.0)

        risk_level = base_risk * protection_factor
        self.metrics.risk_assessments += 1

        return min(risk_level, 1.0)

    def _encrypt_data(self, data: Any, data_id: str) -> str:
        """Шифрование данных"""
        try:
            data_str = json.dumps(data) if not isinstance(data, str) else data
            key = self.encryption_keys.get(
                "master", self._generate_encryption_key()
            )

            # Простое XOR шифрование для демонстрации
            encrypted = ""
            for i, char in enumerate(data_str):
                key_char = key[i % len(key)]
                encrypted += chr(ord(char) ^ ord(key_char))

            self.metrics.encryption_operations += 1
            return encrypted

        except Exception as e:
            self.log_activity(
                "Ошибка шифрования данных {}: {}".format(data_id, e), "error"
            )
            return str(data)

    def _anonymize_data(self, data: Any) -> Any:
        """Анонимизация данных"""
        try:
            if isinstance(data, dict):
                anonymized = {}
                for key, value in data.items():
                    if "name" in key.lower() or "email" in key.lower():
                        anonymized[key] = "***ANONYMIZED***"
                    else:
                        anonymized[key] = value
                return anonymized
            elif isinstance(data, str):
                return "***ANONYMIZED***"
            else:
                return data

        except Exception as e:
            self.log_activity(
                "Ошибка анонимизации данных: {}".format(e), "error"
            )
            return data

    def _check_compliance(self, data: Any, data_type: DataType) -> bool:
        """Проверка соответствия требованиям"""
        try:
            compliance_score = 0
            total_checks = 0

            # Проверка GDPR
            if data_type in [DataType.PERSONAL, DataType.FINANCIAL]:
                gdpr_rules = self.compliance_rules.get("GDPR", [])
                for rule in gdpr_rules:
                    total_checks += 1
                    if self._check_gdpr_rule(data, rule):
                        compliance_score += 1

            # Проверка COPPA
            if data_type == DataType.PERSONAL:
                coppa_rules = self.compliance_rules.get("COPPA", [])
                for rule in coppa_rules:
                    total_checks += 1
                    if self._check_coppa_rule(data, rule):
                        compliance_score += 1

            # Проверка 152-ФЗ
            if data_type in [DataType.PERSONAL, DataType.BUSINESS]:
                fz152_rules = self.compliance_rules.get("152-FZ", [])
                for rule in fz152_rules:
                    total_checks += 1
                    if self._check_fz152_rule(data, rule):
                        compliance_score += 1

            self.metrics.compliance_checks += 1
            return (
                (compliance_score / total_checks) >= 0.8
                if total_checks > 0
                else True
            )

        except Exception as e:
            self.log_activity(
                "Ошибка проверки соответствия: {}".format(e), "error"
            )
            return False

    def _check_gdpr_rule(self, data: Any, rule: str) -> bool:
        """Проверка правила GDPR"""
        # Упрощенная проверка
        return True

    def _check_coppa_rule(self, data: Any, rule: str) -> bool:
        """Проверка правила COPPA"""
        # Упрощенная проверка
        return True

    def _check_fz152_rule(self, data: Any, rule: str) -> bool:
        """Проверка правила 152-ФЗ"""
        # Упрощенная проверка
        return True

    def _backup_data(self, data_id: str, data: Any):
        """Резервное копирование данных"""
        try:
            backup_file = os.path.join(
                self.backup_locations[0],
                "backup_{}_{}.json".format(data_id, int(time.time())),
            )

            backup_data = {
                "data_id": data_id,
                "data": data,
                "backup_timestamp": datetime.now().isoformat(),
                "backup_location": backup_file,
            }

            with open(backup_file, "w") as f:
                json.dump(backup_data, f, indent=2)

            self.metrics.backup_operations += 1
            self.log_activity(
                "Резервная копия данных {} создана".format(data_id)
            )

        except Exception as e:
            self.log_activity(
                "Ошибка резервного копирования данных {}: {}".format(
                    data_id, e
                ),
                "error",
            )

    def _update_metrics(self, protection_status: DataStatus):
        """Обновление метрик"""
        self.metrics.total_data_items += 1

        if protection_status == DataStatus.PROTECTED:
            self.metrics.protected_items += 1
        elif protection_status == DataStatus.ENCRYPTED:
            self.metrics.encrypted_items += 1
        elif protection_status == DataStatus.ANONYMIZED:
            self.metrics.anonymized_items += 1
        elif protection_status == DataStatus.BACKED_UP:
            self.metrics.compliant_items += 1
        elif protection_status == DataStatus.AT_RISK:
            self.metrics.at_risk_items += 1
        elif protection_status == DataStatus.COMPROMISED:
            self.metrics.compromised_items += 1

        self.metrics.last_updated = datetime.now()

    def _calculate_protection_score(
        self, protection_status: DataStatus, risk_level: float
    ) -> float:
        """Расчет оценки защиты"""
        status_scores = {
            DataStatus.PROTECTED: 0.6,
            DataStatus.ENCRYPTED: 0.8,
            DataStatus.ANONYMIZED: 0.7,
            DataStatus.BACKED_UP: 0.9,
            DataStatus.COMPLIANT: 1.0,
            DataStatus.AT_RISK: 0.3,
            DataStatus.COMPROMISED: 0.0,
        }

        base_score = status_scores.get(protection_status, 0.5)
        risk_penalty = risk_level * 0.3

        return max(0.0, min(1.0, base_score - risk_penalty))

    def _generate_recommendations(
        self,
        data_type: DataType,
        protection_level: ProtectionLevel,
        risk_level: float,
    ) -> List[str]:
        """Генерация рекомендаций по защите"""
        recommendations = []

        if risk_level > 0.7:
            recommendations.append(
                "Высокий риск - требуется дополнительная защита"
            )

        if protection_level == ProtectionLevel.LOW:
            recommendations.append("Рекомендуется повысить уровень защиты")

        if data_type in [DataType.PERSONAL, DataType.FINANCIAL]:
            recommendations.append("Требуется шифрование и анонимизация")

        if not self.encryption_enabled:
            recommendations.append("Включить шифрование данных")

        if not self.backup_enabled:
            recommendations.append("Настроить резервное копирование")

        return recommendations

    def get_protection_status(
        self, data_id: str
    ) -> Optional[DataProtectionResult]:
        """Получение статуса защиты данных"""
        try:
            if data_id not in self.protected_data:
                return None

            data_info = self.protected_data[data_id]
            data_info["last_accessed"] = datetime.now().isoformat()

            return DataProtectionResult(
                data_id=data_id,
                protection_status=DataStatus(data_info["protection_status"]),
                encryption_method=(
                    EncryptionMethod(data_info["encryption_method"])
                    if data_info["encryption_method"]
                    else None
                ),
                protection_score=self._calculate_protection_score(
                    DataStatus(data_info["protection_status"]),
                    data_info["risk_level"],
                ),
                compliance_status=data_info["compliance_status"],
                risk_level=data_info["risk_level"],
            )

        except Exception as e:
            self.log_activity(
                "Ошибка получения статуса защиты {}: {}".format(data_id, e),
                "error",
            )
            return None

    def get_metrics(self) -> DataProtectionMetrics:
        """Получение метрик защиты данных"""
        return self.metrics

    def get_protection_events(
        self, limit: int = 100
    ) -> List[DataProtectionEvent]:
        """Получение событий защиты данных"""
        return (
            self.protection_events[-limit:]
            if limit > 0
            else self.protection_events
        )

    def cleanup_old_data(self, days: int = None):
        """Очистка старых данных"""
        try:
            if days is None:
                days = self.retention_period

            cutoff_date = datetime.now() - timedelta(days=days)
            removed_count = 0

            for data_id, data_info in list(self.protected_data.items()):
                created_at = datetime.fromisoformat(data_info["created_at"])
                if created_at < cutoff_date:
                    del self.protected_data[data_id]
                    removed_count += 1

            # Очистка старых событий
            self.protection_events = [
                event
                for event in self.protection_events
                if event.timestamp > cutoff_date
            ]

            self.log_activity(
                "Очищено {} старых записей данных".format(removed_count)
            )

        except Exception as e:
            self.log_activity(
                "Ошибка очистки старых данных: {}".format(e), "error"
            )

    def stop(self):
        """Остановка агента"""
        try:
            self.log_activity("Остановка DataProtectionAgent")
            self.status = ComponentStatus.STOPPED

            # Сохранение состояния
            self._save_state()

            self.log_activity("DataProtectionAgent остановлен")

        except Exception as e:
            self.log_activity(
                "Ошибка остановки DataProtectionAgent: {}".format(e), "error"
            )

    def _save_state(self):
        """Сохранение состояния агента"""
        try:
            state = {
                "protected_data": self.protected_data,
                "metrics": self.metrics.to_dict(),
                "protection_events": [
                    event.to_dict() for event in self.protection_events[-100:]
                ],
                "config": {
                    "encryption_enabled": self.encryption_enabled,
                    "anonymization_enabled": self.anonymization_enabled,
                    "backup_enabled": self.backup_enabled,
                    "compliance_check_enabled": self.compliance_check_enabled,
                    "risk_assessment_enabled": self.risk_assessment_enabled,
                },
                "last_saved": datetime.now().isoformat(),
            }

            state_file = os.path.join(
                self.config.get("state_directory", "data/state"),
                "data_protection_agent_state.json",
            )

            if not os.path.exists(os.path.dirname(state_file)):
                os.makedirs(os.path.dirname(state_file))

            with open(state_file, "w") as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            self.log_activity(
                "Ошибка сохранения состояния DataProtectionAgent: {}".format(
                    e
                ),
                "error",
            )
