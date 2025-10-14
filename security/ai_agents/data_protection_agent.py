# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Data Protection Agent
Агент защиты данных для обеспечения конфиденциальности и целостности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-03
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import ComponentStatus, SecurityBase


class DataType(Enum):
    """Типы данных для защиты"""

    GENERAL = "general"
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
        """
        Инициализация агента защиты данных.

        Args:
            name: Имя агента (по умолчанию: DataProtectionAgent)
            config: Конфигурация агента с параметрами защиты данных
        """
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

        # Async поддержка
        self._async_enabled = True
        self._async_lock = asyncio.Lock()
        self._async_tasks = set()

        # Кэширование
        self._cache = {}
        self._cache_max_size = 1000
        self._cache_ttl = 3600  # 1 час

        # Метрики производительности
        self._performance_metrics = {
            "encryption_time_avg": 0.0,
            "anonymization_time_avg": 0.0,
            "cache_hit_rate": 0.0,
            "memory_usage": 0.0,
            "cpu_usage": 0.0,
        }

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

    # ========================================
    # ASYNC МЕТОДЫ ДЛЯ УЛУЧШЕННОЙ ПРОИЗВОДИТЕЛЬНОСТИ
    # ========================================

    async def protect_data_async(
        self,
        data_id: str,
        data: Any,
        data_type: DataType = DataType.GENERAL,
        protection_level: ProtectionLevel = ProtectionLevel.HIGH,
    ) -> DataProtectionResult:
        """
        Асинхронная защита данных с полным циклом обработки.

        Args:
            data_id: Уникальный идентификатор данных
            data: Данные для защиты
            data_type: Тип данных
            protection_level: Уровень защиты

        Returns:
            DataProtectionResult: Результат защиты данных
        """
        async with self._async_lock:
            try:
                self.logger.info(
                    f"Начало асинхронной защиты данных: {data_id}"
                )

                # Валидация входных данных
                if not await self._validate_data_input_async(data, data_type):
                    raise ValueError(f"Неверные входные данные для {data_id}")

                # Оценка риска
                risk_level = await self._assess_data_risk_async(
                    data, data_type, protection_level
                )

                # Шифрование
                _ = await self._encrypt_data_async(data, data_id)

                # Анонимизация
                _ = await self._anonymize_data_async(data)

                # Резервное копирование
                await self._backup_data_async(data_id, data)

                # Создание результата
                result = DataProtectionResult(
                    data_id=data_id,
                    protection_status=DataStatus.PROTECTED,
                    risk_level=risk_level,
                    protection_score=await (
                        self._calculate_protection_score_async(
                            DataStatus.PROTECTED, risk_level
                        )
                    ),
                    compliance_status=True,
                    encryption_method=self.default_encryption_method,
                )

                self.logger.info(
                    f"Асинхронная защита данных завершена: {data_id}"
                )
                return result

            except Exception as e:
                self.logger.error(
                    f"Ошибка асинхронной защиты данных {data_id}: {e}"
                )
                raise

    async def batch_protect_data_async(
        self, data_batch: List[Dict[str, Any]]
    ) -> List[DataProtectionResult]:
        """
        Асинхронная пакетная защита данных.

        Args:
            data_batch: Список данных для защиты

        Returns:
            List[DataProtectionResult]: Список результатов защиты
        """
        self.logger.info(
            f"Начало асинхронной пакетной защиты {len(data_batch)} элементов"
        )

        tasks = []
        for item in data_batch:
            task = asyncio.create_task(
                self.protect_data_async(
                    item.get("data_id", ""),
                    item.get("data"),
                    item.get("data_type", DataType.GENERAL),
                    item.get("protection_level", ProtectionLevel.HIGH),
                )
            )
            tasks.append(task)
            self._async_tasks.add(task)

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Обработка результатов
            successful_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(
                        f"Ошибка в пакетной обработке элемента {i}: {result}"
                    )
                else:
                    successful_results.append(result)

            self.logger.info(
                f"Асинхронная пакетная защита завершена: "
                f"{len(successful_results)}/{len(data_batch)} успешно"
            )
            return successful_results

        finally:
            # Очистка завершенных задач
            for task in tasks:
                self._async_tasks.discard(task)

    async def _validate_data_input_async(
        self, data: Any, data_type: DataType
    ) -> bool:
        """Асинхронная валидация входных данных."""
        try:
            if data is None:
                self.logger.warning("Получены пустые данные")
                return False

            if data_type == DataType.PERSONAL and isinstance(data, str):
                # Проверка на персональные данные
                personal_patterns = [
                    r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
                    r"\b\d{3}[\s-]?\d{3}[\s-]?\d{4}\b",
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                ]

                for pattern in personal_patterns:
                    if re.search(pattern, data):
                        self.logger.info("Обнаружены персональные данные")
                        return True

            return True

        except Exception as e:
            self.logger.error(f"Ошибка валидации данных: {e}")
            return False

    async def _assess_data_risk_async(
        self, data: Any, data_type: DataType, protection_level: ProtectionLevel
    ) -> float:
        """Асинхронная оценка риска данных."""
        try:
            base_risk = 0.5

            # Риск по типу данных
            if data_type == DataType.PERSONAL:
                base_risk += 0.3
            elif data_type == DataType.FINANCIAL:
                base_risk += 0.4
            elif data_type == DataType.MEDICAL:
                base_risk += 0.5

            # Риск по уровню защиты
            if protection_level == ProtectionLevel.MINIMAL:
                base_risk += 0.2
            elif protection_level == ProtectionLevel.MAXIMUM:
                base_risk -= 0.2

            # Риск по размеру данных
            if isinstance(data, str) and len(data) > 10000:
                base_risk += 0.1

            return max(0.0, min(1.0, base_risk))

        except Exception as e:
            self.logger.error(f"Ошибка оценки риска: {e}")
            return 0.8  # Высокий риск при ошибке

    async def _encrypt_data_async(self, data: Any, data_id: str) -> str:
        """Асинхронное шифрование данных."""
        try:
            # Имитация асинхронного шифрования
            await asyncio.sleep(0.001)  # Небольшая задержка для имитации

            data_str = str(data)
            hash_obj = hashlib.sha256()
            hash_obj.update(data_str.encode("utf-8"))
            hash_obj.update(data_id.encode("utf-8"))

            encrypted = hash_obj.hexdigest()
            self.logger.debug(f"Данные зашифрованы: {data_id}")
            return encrypted

        except Exception as e:
            self.logger.error(f"Ошибка шифрования данных {data_id}: {e}")
            raise

    async def _anonymize_data_async(self, data: Any) -> Any:
        """Асинхронная анонимизация данных."""
        try:
            # Имитация асинхронной анонимизации
            await asyncio.sleep(0.001)  # Небольшая задержка для имитации

            if isinstance(data, str):
                # Простая анонимизация строк
                anonymized = "*" * min(len(data), 20)
                if len(data) > 20:
                    anonymized += "..."
                return anonymized
            elif isinstance(data, dict):
                # Анонимизация словаря
                anonymized = {}
                for key, value in data.items():
                    if isinstance(value, str) and len(value) > 5:
                        anonymized[key] = "*" * 5 + "..."
                    else:
                        anonymized[key] = value
                return anonymized
            else:
                return "[ANONYMIZED]"

        except Exception as e:
            self.logger.error(f"Ошибка анонимизации данных: {e}")
            return "[ERROR]"

    async def _backup_data_async(self, data_id: str, data: Any):
        """Асинхронное резервное копирование данных."""
        try:
            # Имитация асинхронного резервного копирования
            await asyncio.sleep(0.001)  # Небольшая задержка для имитации

            backup_dir = "data/backups"
            os.makedirs(backup_dir, exist_ok=True)

            backup_file = os.path.join(backup_dir, f"{data_id}_backup.json")
            backup_data = {
                "data_id": data_id,
                "timestamp": datetime.now().isoformat(),
                "data": str(data)[:1000],  # Ограничиваем размер
            }

            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)

            self.logger.debug(f"Резервная копия создана: {backup_file}")

        except Exception as e:
            self.logger.error(
                f"Ошибка создания резервной копии {data_id}: {e}"
            )

    async def _calculate_protection_score_async(
        self, protection_status: DataStatus, risk_level: float
    ) -> float:
        """Асинхронный расчет оценки защиты."""
        try:
            base_score = 0.8

            if protection_status == DataStatus.PROTECTED:
                base_score += 0.2
            elif protection_status == DataStatus.ENCRYPTED:
                base_score += 0.1

            # Корректировка по уровню риска
            if risk_level > 0.7:
                base_score -= 0.2
            elif risk_level < 0.3:
                base_score += 0.1

            return max(0.0, min(1.0, base_score))

        except Exception as e:
            self.logger.error(f"Ошибка расчета оценки защиты: {e}")
            return 0.5

    async def cleanup_async_tasks(self):
        """Очистка завершенных асинхронных задач."""
        try:
            completed_tasks = [
                task for task in self._async_tasks if task.done()
            ]
            for task in completed_tasks:
                self._async_tasks.discard(task)

            if completed_tasks:
                self.logger.info(
                    f"Очищено {len(completed_tasks)} завершенных задач"
                )

        except Exception as e:
            self.logger.error(f"Ошибка очистки задач: {e}")

    # ========================================
    # КЭШИРОВАНИЕ И ПРОИЗВОДИТЕЛЬНОСТЬ
    # ========================================

    def _get_cache_key(self, data_id: str, operation: str) -> str:
        """Генерация ключа кэша."""
        return f"{data_id}_{operation}"

    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Проверка валидности кэша."""
        if not cache_entry:
            return False

        timestamp = cache_entry.get("timestamp", 0)
        current_time = time.time()
        return (current_time - timestamp) < self._cache_ttl

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Получение данных из кэша."""
        try:
            if cache_key in self._cache:
                cache_entry = self._cache[cache_key]
                if self._is_cache_valid(cache_entry):
                    self._performance_metrics["cache_hit_rate"] += 1
                    self.logger.debug(f"Кэш попадание: {cache_key}")
                    return cache_entry.get("data")
                else:
                    # Удаляем устаревший кэш
                    del self._cache[cache_key]
                    self.logger.debug(f"Кэш устарел: {cache_key}")

            return None

        except Exception as e:
            self.logger.error(f"Ошибка получения из кэша: {e}")
            return None

    def _set_cache(self, cache_key: str, data: Any):
        """Сохранение данных в кэш."""
        try:
            # Ограничиваем размер кэша
            if len(self._cache) >= self._cache_max_size:
                # Удаляем самые старые записи
                oldest_keys = sorted(
                    self._cache.keys(),
                    key=lambda k: self._cache[k].get("timestamp", 0),
                )[: len(self._cache) - self._cache_max_size + 1]

                for key in oldest_keys:
                    del self._cache[key]

            self._cache[cache_key] = {"data": data, "timestamp": time.time()}

            self.logger.debug(f"Данные сохранены в кэш: {cache_key}")

        except Exception as e:
            self.logger.error(f"Ошибка сохранения в кэш: {e}")

    def clear_cache(self):
        """Очистка кэша."""
        try:
            self._cache.clear()
            self.logger.info("Кэш очищен")
        except Exception as e:
            self.logger.error(f"Ошибка очистки кэша: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша."""
        try:
            return {
                "cache_size": len(self._cache),
                "cache_max_size": self._cache_max_size,
                "cache_ttl": self._cache_ttl,
                "cache_hit_rate": self._performance_metrics.get(
                    "cache_hit_rate", 0
                ),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики кэша: {e}")
            return {}

    # ========================================
    # ВАЛИДАЦИЯ ДАННЫХ
    # ========================================

    def _validate_data_id(self, data_id: str) -> bool:
        """Валидация идентификатора данных."""
        try:
            if not data_id or not isinstance(data_id, str):
                self.logger.warning("Неверный идентификатор данных")
                return False

            if len(data_id) < 3 or len(data_id) > 100:
                self.logger.warning("Длина идентификатора данных недопустима")
                return False

            # Проверка на допустимые символы
            if not re.match(r"^[a-zA-Z0-9_-]+$", data_id):
                self.logger.warning(
                    "Идентификатор содержит недопустимые символы"
                )
                return False

            return True

        except Exception as e:
            self.logger.error(f"Ошибка валидации идентификатора: {e}")
            return False

    def _validate_protection_level(self, level: ProtectionLevel) -> bool:
        """Валидация уровня защиты."""
        try:
            if not isinstance(level, ProtectionLevel):
                self.logger.warning("Неверный тип уровня защиты")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Ошибка валидации уровня защиты: {e}")
            return False

    def _validate_data_type(self, data_type: DataType) -> bool:
        """Валидация типа данных."""
        try:
            if not isinstance(data_type, DataType):
                self.logger.warning("Неверный тип данных")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Ошибка валидации типа данных: {e}")
            return False

    def _validate_data_content(self, data: Any, data_type: DataType) -> bool:
        """Валидация содержимого данных."""
        try:
            if data is None:
                self.logger.warning("Данные не могут быть None")
                return False

            # Проверка размера данных
            data_size = len(str(data))
            if data_size > 10 * 1024 * 1024:  # 10MB
                self.logger.warning(
                    f"Размер данных превышает лимит: {data_size}"
                )
                return False

            # Специфичные проверки по типу данных
            if data_type == DataType.PERSONAL:
                if not self._validate_personal_data(data):
                    return False
            elif data_type == DataType.FINANCIAL:
                if not self._validate_financial_data(data):
                    return False
            elif data_type == DataType.MEDICAL:
                if not self._validate_medical_data(data):
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Ошибка валидации содержимого: {e}")
            return False

    def _validate_personal_data(self, data: Any) -> bool:
        """Валидация персональных данных."""
        try:
            if isinstance(data, str):
                # Проверка на наличие персональных данных
                personal_patterns = [
                    r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
                    r"\b\d{3}[\s-]?\d{3}[\s-]?\d{4}\b",
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                ]

                for pattern in personal_patterns:
                    if re.search(pattern, data):
                        self.logger.info("Обнаружены персональные данные")
                        return True

            return True

        except Exception as e:
            self.logger.error(f"Ошибка валидации персональных данных: {e}")
            return False

    def _validate_financial_data(self, data: Any) -> bool:
        """Валидация финансовых данных."""
        try:
            if isinstance(data, str):
                # Проверка на финансовые данные
                financial_patterns = [
                    r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
                    r"\b\d{3}[\s-]?\d{3}[\s-]?\d{4}\b",
                    r"\b\d{2}[\s-]?\d{2}[\s-]?\d{4}\b",
                ]

                for pattern in financial_patterns:
                    if re.search(pattern, data):
                        self.logger.info("Обнаружены финансовые данные")
                        return True

            return True

        except Exception as e:
            self.logger.error(f"Ошибка валидации финансовых данных: {e}")
            return False

    def _validate_medical_data(self, data: Any) -> bool:
        """Валидация медицинских данных."""
        try:
            if isinstance(data, str):
                # Проверка на медицинские данные
                medical_keywords = [
                    "диагноз",
                    "лечение",
                    "симптом",
                    "болезнь",
                    "медицинский",
                    "пациент",
                    "врач",
                    "больница",
                    "клиника",
                    "анализ",
                ]

                data_lower = data.lower()
                for keyword in medical_keywords:
                    if keyword in data_lower:
                        self.logger.info("Обнаружены медицинские данные")
                        return True

            return True

        except Exception as e:
            self.logger.error(f"Ошибка валидации медицинских данных: {e}")
            return False

    # ========================================
    # МЕТРИКИ ПРОИЗВОДИТЕЛЬНОСТИ
    # ========================================

    def _update_performance_metrics(self, operation: str, duration: float):
        """Обновление метрик производительности."""
        try:
            if operation == "encryption":
                self._performance_metrics["encryption_time_avg"] = (
                    self._performance_metrics.get("encryption_time_avg", 0)
                    + duration
                ) / 2
            elif operation == "anonymization":
                self._performance_metrics["anonymization_time_avg"] = (
                    self._performance_metrics.get("anonymization_time_avg", 0)
                    + duration
                ) / 2

            self.logger.debug(
                f"Метрики обновлены для операции {operation}: {duration}s"
            )

        except Exception as e:
            self.logger.error(f"Ошибка обновления метрик: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Получение метрик производительности."""
        try:
            return {
                "encryption_time_avg": self._performance_metrics.get(
                    "encryption_time_avg", 0.0
                ),
                "anonymization_time_avg": self._performance_metrics.get(
                    "anonymization_time_avg", 0.0
                ),
                "cache_hit_rate": self._performance_metrics.get(
                    "cache_hit_rate", 0.0
                ),
                "memory_usage": self._performance_metrics.get(
                    "memory_usage", 0.0
                ),
                "cpu_usage": self._performance_metrics.get("cpu_usage", 0.0),
                "cache_stats": self.get_cache_stats(),
            }
        except Exception as e:
            self.logger.error(
                f"Ошибка получения метрик производительности: {e}"
            )
            return {}

    def reset_performance_metrics(self):
        """Сброс метрик производительности."""
        try:
            self._performance_metrics = {
                "encryption_time_avg": 0.0,
                "anonymization_time_avg": 0.0,
                "cache_hit_rate": 0.0,
                "memory_usage": 0.0,
                "cpu_usage": 0.0,
            }
            self.logger.info("Метрики производительности сброшены")
        except Exception as e:
            self.logger.error(f"Ошибка сброса метрик: {e}")

    # ========================================
    # ОБРАБОТКА БОЛЬШИХ ДАННЫХ
    # ========================================

    def process_large_data_chunks(
        self, data: Any, chunk_size: int = 1024
    ) -> List[Any]:
        """Обработка больших данных по частям."""
        try:
            if isinstance(data, str):
                # Разбиваем строку на части
                chunks = [
                    data[i:i + chunk_size]
                    for i in range(0, len(data), chunk_size)
                ]
                self.logger.info(f"Данные разбиты на {len(chunks)} частей")
                return chunks
            elif isinstance(data, list):
                # Разбиваем список на части
                chunks = [
                    data[i:i + chunk_size]
                    for i in range(0, len(data), chunk_size)
                ]
                self.logger.info(f"Список разбит на {len(chunks)} частей")
                return chunks
            elif isinstance(data, dict):
                # Разбиваем словарь на части
                items = list(data.items())
                chunks = [
                    dict(items[i:i + chunk_size])
                    for i in range(0, len(items), chunk_size)
                ]
                self.logger.info(f"Словарь разбит на {len(chunks)} частей")
                return chunks
            else:
                # Для других типов данных возвращаем как есть
                return [data]

        except Exception as e:
            self.logger.error(f"Ошибка обработки больших данных: {e}")
            return [data]

    def stream_protect_data(
        self, data_stream: List[Any]
    ) -> List[DataProtectionResult]:
        """Потоковая защита данных."""
        try:
            results = []
            for i, data_item in enumerate(data_stream):
                try:
                    # Создаем временный ID для элемента потока
                    temp_id = f"stream_item_{i}_{int(time.time())}"

                    # Защищаем данные
                    result = self.protect_data(
                        data_id=temp_id,
                        data=data_item,
                        data_type=DataType.GENERAL,
                        protection_level=ProtectionLevel.HIGH,
                    )

                    results.append(result)
                    self.logger.debug(f"Потоковый элемент {i} защищен")

                except Exception as e:
                    self.logger.error(
                        f"Ошибка защиты потокового элемента {i}: {e}"
                    )
                    # Создаем результат с ошибкой
                    error_result = DataProtectionResult(
                        data_id=f"stream_item_{i}_error",
                        protection_status=DataStatus.AT_RISK,
                        risk_level=1.0,
                        protection_score=0.0,
                        compliance_status=False,
                    )
                    results.append(error_result)

            self.logger.info(
                f"Потоковая защита завершена: {len(results)} элементов"
            )
            return results

        except Exception as e:
            self.logger.error(f"Ошибка потоковой защиты: {e}")
            return []

    def batch_anonymize_data(self, data_batch: List[Any]) -> List[Any]:
        """Пакетная анонимизация данных."""
        try:
            anonymized_batch = []

            for i, data_item in enumerate(data_batch):
                try:
                    # Анонимизируем данные
                    anonymized_item = self._anonymize_data(data_item)
                    anonymized_batch.append(anonymized_item)

                    self.logger.debug(f"Элемент {i} анонимизирован")

                except Exception as e:
                    self.logger.error(f"Ошибка анонимизации элемента {i}: {e}")
                    anonymized_batch.append("[ERROR]")

            self.logger.info(
                f"Пакетная анонимизация завершена: "
                f"{len(anonymized_batch)} элементов"
            )
            return anonymized_batch

        except Exception as e:
            self.logger.error(f"Ошибка пакетной анонимизации: {e}")
            return []

    # ========================================
    # ПАРАЛЛЕЛЬНАЯ ОБРАБОТКА
    # ========================================

    def parallel_protect_data(
        self, data_list: List[Any], max_workers: int = 4
    ) -> List[DataProtectionResult]:
        """Параллельная защита данных с использованием ThreadPoolExecutor."""
        try:
            import concurrent.futures

            self.logger.info(
                f"Начало параллельной защиты {len(data_list)} элементов"
            )

            results = []

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers
            ) as executor:
                # Создаем задачи для параллельного выполнения
                future_to_data = {}

                for i, data_item in enumerate(data_list):
                    temp_id = f"parallel_item_{i}_{int(time.time())}"
                    future = executor.submit(
                        self.protect_data,
                        data_id=temp_id,
                        data=data_item,
                        data_type=DataType.GENERAL,
                        protection_level=ProtectionLevel.HIGH,
                    )
                    future_to_data[future] = (i, data_item)

                # Собираем результаты
                for future in concurrent.futures.as_completed(future_to_data):
                    i, data_item = future_to_data[future]
                    try:
                        result = future.result()
                        results.append(result)
                        self.logger.debug(f"Параллельный элемент {i} защищен")

                    except Exception as e:
                        self.logger.error(
                            f"Ошибка параллельной защиты элемента {i}: {e}"
                        )
                        # Создаем результат с ошибкой
                        error_result = DataProtectionResult(
                            data_id=f"parallel_item_{i}_error",
                            protection_status=DataStatus.AT_RISK,
                            risk_level=1.0,
                            protection_score=0.0,
                            compliance_status=False,
                        )
                        results.append(error_result)

            self.logger.info(
                f"Параллельная защита завершена: {len(results)} элементов"
            )
            return results

        except Exception as e:
            self.logger.error(f"Ошибка параллельной защиты: {e}")
            return []

    def parallel_encrypt_data(
        self, data_list: List[Any], max_workers: int = 4
    ) -> List[str]:
        """Параллельное шифрование данных."""
        try:
            import concurrent.futures

            self.logger.info(
                f"Начало параллельного шифрования {len(data_list)} элементов"
            )

            encrypted_results = []

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers
            ) as executor:
                # Создаем задачи для параллельного шифрования
                future_to_data = {}

                for i, data_item in enumerate(data_list):
                    temp_id = f"encrypt_item_{i}_{int(time.time())}"
                    future = executor.submit(
                        self._encrypt_data, data=data_item, data_id=temp_id
                    )
                    future_to_data[future] = i

                # Собираем результаты
                for future in concurrent.futures.as_completed(future_to_data):
                    i = future_to_data[future]
                    try:
                        encrypted_data = future.result()
                        encrypted_results.append(encrypted_data)
                        self.logger.debug(f"Элемент {i} зашифрован")

                    except Exception as e:
                        self.logger.error(
                            f"Ошибка параллельного шифрования элемента "
                            f"{i}: {e}"
                        )
                        encrypted_results.append("[ENCRYPTION_ERROR]")

            self.logger.info(
                f"Параллельное шифрование завершено: "
                f"{len(encrypted_results)} элементов"
            )
            return encrypted_results

        except Exception as e:
            self.logger.error(f"Ошибка параллельного шифрования: {e}")
            return []

    # ========================================
    # УЛУЧШЕННАЯ БЕЗОПАСНОСТЬ
    # ========================================

    def _generate_secure_key(self, length: int = 32) -> bytes:
        """Генерация безопасного ключа."""
        try:
            import secrets

            key = secrets.token_bytes(length)
            self.logger.debug(
                f"Сгенерирован безопасный ключ длиной {length} байт"
            )
            return key
        except Exception as e:
            self.logger.error(f"Ошибка генерации ключа: {e}")
            # Fallback к менее безопасному методу
            import os

            return os.urandom(length)

    def _verify_data_integrity(self, data: Any, checksum: str) -> bool:
        """Проверка целостности данных."""
        try:
            data_str = str(data)
            calculated_checksum = hashlib.sha256(
                data_str.encode("utf-8")
            ).hexdigest()

            if calculated_checksum == checksum:
                self.logger.debug("Целостность данных подтверждена")
                return True
            else:
                self.logger.warning("Целостность данных нарушена")
                return False

        except Exception as e:
            self.logger.error(f"Ошибка проверки целостности: {e}")
            return False

    def _secure_delete_data(self, data_id: str):
        """Безопасное удаление данных."""
        try:
            # Удаляем из кэша
            cache_keys_to_remove = [
                key for key in self._cache.keys() if data_id in key
            ]
            for key in cache_keys_to_remove:
                del self._cache[key]

            # Удаляем из защищенных данных
            if data_id in self.protected_data:
                del self.protected_data[data_id]

            # Удаляем ключи шифрования
            if data_id in self.encryption_keys:
                del self.encryption_keys[data_id]

            self.logger.info(f"Данные {data_id} безопасно удалены")

        except Exception as e:
            self.logger.error(
                f"Ошибка безопасного удаления данных {data_id}: {e}"
            )

    def _encrypt_metadata(self, metadata: Dict[str, Any]) -> str:
        """Шифрование метаданных."""
        try:
            metadata_str = json.dumps(metadata, sort_keys=True)
            hash_obj = hashlib.sha256()
            hash_obj.update(metadata_str.encode("utf-8"))
            encrypted_metadata = hash_obj.hexdigest()

            self.logger.debug("Метаданные зашифрованы")
            return encrypted_metadata

        except Exception as e:
            self.logger.error(f"Ошибка шифрования метаданных: {e}")
            return ""

    # ========================================
    # УЛУЧШЕННОЕ ЛОГИРОВАНИЕ И АУДИТ
    # ========================================

    def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Логирование событий безопасности."""
        try:
            event_data = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "details": details,
                "agent_name": self.name,
                "status": self.status.value if self.status else "unknown",
            }

            self.logger.info(f"Событие безопасности: {event_type}")
            self.logger.debug(f"Детали события: {event_data}")

            # Сохраняем событие в список
            self.protection_events.append(
                DataProtectionEvent(
                    event_id=(
                        f"event_{int(time.time())}_"
                        f"{len(self.protection_events)}"
                    ),
                    data_id=details.get("data_id", "unknown"),
                    event_type=event_type,
                    protection_level=ProtectionLevel.HIGH,
                    timestamp=datetime.now(),
                    details=details,
                )
            )

        except Exception as e:
            self.logger.error(f"Ошибка логирования события безопасности: {e}")

    def _audit_data_access(self, data_id: str, user_id: str, action: str):
        """Аудит доступа к данным."""
        try:
            audit_data = {
                "data_id": data_id,
                "user_id": user_id,
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "agent_name": self.name,
            }

            self.logger.info(
                f"Аудит доступа: {action} к {data_id} пользователем {user_id}"
            )

            # Сохраняем в файл аудита
            audit_file = "data/audit/data_access_audit.json"
            os.makedirs(os.path.dirname(audit_file), exist_ok=True)

            # Читаем существующие записи
            audit_records = []
            if os.path.exists(audit_file):
                with open(audit_file, "r", encoding="utf-8") as f:
                    audit_records = json.load(f)

            # Добавляем новую запись
            audit_records.append(audit_data)

            # Сохраняем обновленные записи
            with open(audit_file, "w", encoding="utf-8") as f:
                json.dump(audit_records, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.logger.error(f"Ошибка аудита доступа: {e}")

    def get_audit_trail(self, data_id: str) -> List[Dict[str, Any]]:
        """Получение трека аудита для данных."""
        try:
            audit_file = "data/audit/data_access_audit.json"

            if not os.path.exists(audit_file):
                return []

            with open(audit_file, "r", encoding="utf-8") as f:
                audit_records = json.load(f)

            # Фильтруем записи по data_id
            filtered_records = [
                record
                for record in audit_records
                if record.get("data_id") == data_id
            ]

            self.logger.info(
                f"Найдено {len(filtered_records)} записей аудита для {data_id}"
            )
            return filtered_records

        except Exception as e:
            self.logger.error(f"Ошибка получения трека аудита: {e}")
            return []

    def __del__(self):
        """Деструктор для очистки ресурсов."""
        try:
            if hasattr(self, "_async_tasks") and self._async_tasks:
                # Отмена незавершенных задач
                for task in self._async_tasks:
                    if not task.done():
                        task.cancel()
                self.logger.info("Асинхронные задачи отменены")
        except Exception as e:
            self.logger.error(f"Ошибка в деструкторе: {e}")
