#!/usr/bin/env python3
"""
DataProtectionManager - P0 критический компонент
Управление защитой данных и соответствием стандартам
"""

import base64
import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from core.base import ComponentStatus, SecurityBase


class DataClassification(Enum):
    """Классификация данных"""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


class DataType(Enum):
    """Типы данных"""

    PERSONAL = "personal"
    FINANCIAL = "financial"
    MEDICAL = "medical"
    BIOMETRIC = "biometric"
    LOCATION = "location"
    COMMUNICATION = "communication"
    BEHAVIORAL = "behavioral"


class ProtectionLevel(Enum):
    """Уровни защиты"""

    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"


@dataclass
class DataRecord:
    """Запись данных"""

    id: str
    data_type: DataType
    classification: DataClassification
    content: str
    owner_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_encrypted: bool = True
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataPolicy:
    """Политика защиты данных"""

    id: str
    name: str
    data_types: Set[DataType]
    classification: DataClassification
    protection_level: ProtectionLevel
    retention_days: int
    encryption_required: bool = True
    access_controls: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class DataProtectionManager(SecurityBase):
    """Менеджер защиты данных - P0 критический компонент"""

    def __init__(
        self,
        name: str = "DataProtectionManager",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Хранилище данных
        self.data_records: Dict[str, DataRecord] = {}
        self.data_policies: Dict[str, DataPolicy] = {}

        # Шифрование
        self.encryption_key = (
            config.get("encryption_key", "default_key_12345")
            if config
            else "default_key_12345"
        )
        self.enable_encryption = (
            config.get("enable_encryption", True) if config else True
        )

        # Аудит
        self.access_logs: List[Dict[str, Any]] = []
        self.retention_policies: Dict[DataType, int] = {
            DataType.PERSONAL: 2555,  # 7 лет
            DataType.FINANCIAL: 1825,  # 5 лет
            DataType.MEDICAL: 2555,  # 7 лет
            DataType.BIOMETRIC: 365,  # 1 год
            DataType.LOCATION: 90,  # 3 месяца
            DataType.COMMUNICATION: 365,  # 1 год
            DataType.BEHAVIORAL: 90,  # 3 месяца
        }

        # Статистика
        self.total_records = 0
        self.encrypted_records = 0
        self.expired_records = 0
        self.access_attempts = 0
        self.successful_access = 0

    def initialize(self) -> bool:
        """Инициализация менеджера защиты данных"""
        try:
            self.log_activity(
                f"Инициализация DataProtectionManager {self.name}"
            )
            self.status = ComponentStatus.INITIALIZING

            # Создание политик защиты
            self._create_default_policies()

            # Очистка устаревших данных
            self._cleanup_expired_data()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"DataProtectionManager {self.name} успешно инициализирован"
            )
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации DataProtectionManager: {e}", "error"
            )
            self.status = ComponentStatus.ERROR
            return False

    def _create_default_policies(self):
        """Создание политик защиты по умолчанию"""
        # Политика для персональных данных
        personal_policy = DataPolicy(
            id="personal_data_policy",
            name="Политика персональных данных",
            data_types={DataType.PERSONAL, DataType.BIOMETRIC},
            classification=DataClassification.CONFIDENTIAL,
            protection_level=ProtectionLevel.HIGH,
            retention_days=2555,
            encryption_required=True,
        )
        self.data_policies["personal_data_policy"] = personal_policy

        # Политика для финансовых данных
        financial_policy = DataPolicy(
            id="financial_data_policy",
            name="Политика финансовых данных",
            data_types={DataType.FINANCIAL},
            classification=DataClassification.SECRET,
            protection_level=ProtectionLevel.MAXIMUM,
            retention_days=1825,
            encryption_required=True,
        )
        self.data_policies["financial_data_policy"] = financial_policy

    def _encrypt_data(self, data: str) -> str:
        """Шифрование данных"""
        if not self.enable_encryption:
            return data

        try:
            # Простое шифрование для демонстрации
            key = hashlib.sha256(self.encryption_key.encode()).digest()
            data_bytes = data.encode()
            encrypted = bytearray()

            for i, byte in enumerate(data_bytes):
                encrypted.append(byte ^ key[i % len(key)])

            return base64.b64encode(encrypted).decode()
        except Exception as e:
            self.log_activity(f"Ошибка шифрования: {e}", "error")
            return data

    def _decrypt_data(self, encrypted_data: str) -> str:
        """Расшифровка данных"""
        if not self.enable_encryption:
            return encrypted_data

        try:
            key = hashlib.sha256(self.encryption_key.encode()).digest()
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted = bytearray()

            for i, byte in enumerate(encrypted_bytes):
                decrypted.append(byte ^ key[i % len(key)])

            return decrypted.decode()
        except Exception as e:
            self.log_activity(f"Ошибка расшифровки: {e}", "error")
            return encrypted_data

    def store_data(
        self,
        data_type: DataType,
        content: str,
        owner_id: str,
        classification: DataClassification = DataClassification.INTERNAL,
        expires_in_days: Optional[int] = None,
    ) -> Optional[str]:
        """Сохранение данных с защитой"""
        try:
            record_id = (
                f"data_{int(datetime.now().timestamp())}_"
                f"{hashlib.md5(content.encode()).hexdigest()[:8]}"
            )

            # Определение срока хранения
            if expires_in_days is None:
                expires_in_days = self.retention_policies.get(data_type, 365)

            expires_at = datetime.now() + timedelta(days=expires_in_days)

            # Шифрование данных
            encrypted_content = (
                self._encrypt_data(content)
                if self.enable_encryption
                else content
            )

            record = DataRecord(
                id=record_id,
                data_type=data_type,
                classification=classification,
                content=encrypted_content,
                owner_id=owner_id,
                created_at=datetime.now(),
                expires_at=expires_at,
                is_encrypted=self.enable_encryption,
            )

            self.data_records[record_id] = record
            self.total_records += 1

            if self.enable_encryption:
                self.encrypted_records += 1

            self.log_activity(
                f"Данные сохранены: {record_id} (тип: {data_type.value})"
            )
            return record_id

        except Exception as e:
            self.log_activity(f"Ошибка сохранения данных: {e}", "error")
            return None

    def retrieve_data(
        self, record_id: str, requester_id: str
    ) -> Optional[str]:
        """Получение данных с проверкой доступа"""
        try:
            if record_id not in self.data_records:
                self.log_activity(
                    f"Запись данных {record_id} не найдена", "warning"
                )
                return None

            record = self.data_records[record_id]
            self.access_attempts += 1

            # Проверка срока действия
            if record.expires_at and datetime.now() > record.expires_at:
                self.expired_records += 1
                self.log_activity(
                    f"Запись данных {record_id} истекла", "warning"
                )
                return None

            # Проверка владельца (упрощенная проверка)
            if record.owner_id != requester_id:
                self.log_activity(
                    f"Отказано в доступе к записи {record_id} "
                    f"для {requester_id}",
                    "warning",
                )
                return None

            # Обновление статистики доступа
            record.access_count += 1
            record.last_accessed = datetime.now()

            # Логирование доступа
            self.access_logs.append(
                {
                    "record_id": record_id,
                    "requester_id": requester_id,
                    "timestamp": datetime.now(),
                    "data_type": record.data_type.value,
                    "classification": record.classification.value,
                }
            )

            self.successful_access += 1

            # Расшифровка данных
            if record.is_encrypted:
                return self._decrypt_data(record.content)
            else:
                return record.content

        except Exception as e:
            self.log_activity(f"Ошибка получения данных: {e}", "error")
            return None

    def delete_data(self, record_id: str, requester_id: str) -> bool:
        """Удаление данных"""
        try:
            if record_id not in self.data_records:
                return False

            record = self.data_records[record_id]

            # Проверка владельца
            if record.owner_id != requester_id:
                self.log_activity(
                    f"Отказано в удалении записи {record_id} "
                    f"для {requester_id}",
                    "warning",
                )
                return False

            del self.data_records[record_id]
            self.total_records -= 1

            if record.is_encrypted:
                self.encrypted_records -= 1

            self.log_activity(f"Данные удалены: {record_id}")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка удаления данных: {e}", "error")
            return False

    def _cleanup_expired_data(self):
        """Очистка устаревших данных"""
        try:
            current_time = datetime.now()
            expired_records = []

            for record_id, record in self.data_records.items():
                if record.expires_at and current_time > record.expires_at:
                    expired_records.append(record_id)

            for record_id in expired_records:
                del self.data_records[record_id]
                self.expired_records += 1

            if expired_records:
                self.log_activity(
                    f"Очищено {len(expired_records)} устаревших записей"
                )

        except Exception as e:
            self.log_activity(f"Ошибка очистки данных: {e}", "error")

    def get_data_statistics(self) -> Dict[str, Any]:
        """Получение статистики данных"""
        return {
            "total_records": self.total_records,
            "encrypted_records": self.encrypted_records,
            "expired_records": self.expired_records,
            "access_attempts": self.access_attempts,
            "successful_access": self.successful_access,
            "encryption_rate": (
                self.encrypted_records / max(self.total_records, 1)
            )
            * 100,
            "access_success_rate": (
                self.successful_access / max(self.access_attempts, 1)
            )
            * 100,
        }

    def get_compliance_report(self) -> Dict[str, Any]:
        """Получение отчета о соответствии"""
        return {
            "total_policies": len(self.data_policies),
            "data_classifications": {
                classification.value: sum(
                    1
                    for r in self.data_records.values()
                    if r.classification == classification
                )
                for classification in DataClassification
            },
            "retention_compliance": {
                data_type.value: sum(
                    1
                    for r in self.data_records.values()
                    if r.data_type == data_type
                    and (not r.expires_at or r.expires_at > datetime.now())
                )
                for data_type in DataType
            },
            "encryption_compliance": (
                self.encrypted_records / max(self.total_records, 1)
            )
            * 100,
        }

    def shutdown(self) -> bool:
        """Остановка менеджера защиты данных"""
        try:
            self.log_activity("Остановка DataProtectionManager...")

            # Очистка устаревших данных перед остановкой
            self._cleanup_expired_data()

            self.status = ComponentStatus.STOPPED
            self.log_activity("DataProtectionManager остановлен")
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка остановки DataProtectionManager: {e}", "error"
            )
            return False

    def start_protection(self) -> bool:
        """Запуск защиты данных"""
        try:
            self.log_activity("Запуск защиты данных...")
            self.status = ComponentStatus.RUNNING
            self.log_activity("Защита данных запущена")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка запуска защиты данных: {e}", "error")
            return False

    def stop_protection(self) -> bool:
        """Остановка защиты данных"""
        try:
            self.log_activity("Остановка защиты данных...")
            self.status = ComponentStatus.STOPPED
            self.log_activity("Защита данных остановлена")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка остановки защиты данных: {e}", "error")
            return False

    def get_protection_level(self) -> str:
        """Получение уровня защиты данных"""
        try:
            if self.status == ComponentStatus.RUNNING:
                return "high"
            elif self.status == ComponentStatus.INITIALIZED:
                return "medium"
            else:
                return "low"
        except Exception as e:
            self.log_activity(f"Ошибка получения уровня защиты: {e}", "error")
            return "unknown"


# Тестирование
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    manager = DataProtectionManager()
    if manager.initialize():
        print("✅ DataProtectionManager инициализирован")

        # Тест сохранения данных
        record_id = manager.store_data(
            DataType.PERSONAL,
            "Тестовые персональные данные",
            "user_001",
            DataClassification.CONFIDENTIAL,
        )

        if record_id:
            print(f"✅ Данные сохранены: {record_id}")

            # Тест получения данных
            data = manager.retrieve_data(record_id, "user_001")
            if data:
                print(f"✅ Данные получены: {data}")

            # Статистика
            stats = manager.get_data_statistics()
            print(f"📊 Статистика: {stats}")

            # Отчет о соответствии
            compliance = manager.get_compliance_report()
            print(f"📋 Соответствие: {compliance}")

        manager.shutdown()
    else:
        print("❌ Ошибка инициализации DataProtectionManager")
