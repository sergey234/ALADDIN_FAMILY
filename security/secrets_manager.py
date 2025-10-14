#!/usr/bin/env python3
"""
ALADDIN Security System - Secrets Manager
Централизованное управление секретами

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-26
"""

import base64
import hashlib
import json
import secrets
import threading
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet

from core.security_base import ComponentStatus, SecurityBase


class SecretType(Enum):
    """Типы секретов"""

    PASSWORD = "password"
    API_KEY = "api_key"
    JWT_TOKEN = "jwt_token"
    ENCRYPTION_KEY = "encryption_key"
    DATABASE_CREDENTIALS = "database_credentials"
    EXTERNAL_SERVICE_TOKEN = "external_service_token"
    SSH_KEY = "ssh_key"
    CERTIFICATE = "certificate"
    CONFIG_SECRET = "config_secret"
    CUSTOM = "custom"


class SecretStatus(Enum):
    """Статусы секретов"""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING_ROTATION = "pending_rotation"
    ERROR = "error"


class SecretMetadata:
    """Метаданные секрета"""

    def __init__(
        self,
        secret_id: str,
        name: str,
        secret_type: SecretType,
        created_at: datetime,
        expires_at: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        owner: Optional[str] = None,
        access_count: int = 0,
        last_accessed: Optional[datetime] = None,
    ):
        self.secret_id = secret_id
        self.name = name
        self.secret_type = secret_type
        self.created_at = created_at
        self.expires_at = expires_at
        self.tags = tags or {}
        self.description = description
        self.owner = owner
        self.access_count = access_count
        self.last_accessed = last_accessed
        self.status = SecretStatus.ACTIVE
        self.rotation_schedule = None
        self.version = 1

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "secret_id": self.secret_id,
            "name": self.name,
            "secret_type": self.secret_type.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": (
                self.expires_at.isoformat() if self.expires_at else None
            ),
            "tags": self.tags,
            "description": self.description,
            "owner": self.owner,
            "access_count": self.access_count,
            "last_accessed": (
                self.last_accessed.isoformat() if self.last_accessed else None
            ),
            "status": self.status.value,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecretMetadata":
        """Создание из словаря"""
        metadata = cls(
            secret_id=data["secret_id"],
            name=data["name"],
            secret_type=SecretType(data["secret_type"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=(
                datetime.fromisoformat(data["expires_at"])
                if data.get("expires_at")
                else None
            ),
            tags=data.get("tags", {}),
            description=data.get("description"),
            owner=data.get("owner"),
            access_count=data.get("access_count", 0),
            last_accessed=(
                datetime.fromisoformat(data["last_accessed"])
                if data.get("last_accessed")
                else None
            ),
        )
        metadata.status = SecretStatus(data.get("status", "active"))
        metadata.version = data.get("version", 1)
        return metadata


class ExternalSecretProvider:
    """Базовый класс для внешних провайдеров секретов"""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.connected = False

    def connect(self) -> bool:
        """Подключение к внешней системе"""
        raise NotImplementedError

    def get_secret(self, key: str) -> Optional[str]:
        """Получение секрета"""
        raise NotImplementedError

    def set_secret(
        self, key: str, value: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Сохранение секрета"""
        raise NotImplementedError

    def delete_secret(self, key: str) -> bool:
        """Удаление секрета"""
        raise NotImplementedError

    def list_secrets(self) -> List[str]:
        """Список секретов"""
        raise NotImplementedError

    def health_check(self) -> bool:
        """Проверка здоровья"""
        raise NotImplementedError


class HashiCorpVaultProvider(ExternalSecretProvider):
    """Провайдер для HashiCorp Vault"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("HashiCorp Vault", config)
        self.vault_url = config.get("vault_url")
        self.token = config.get("token")
        self.mount_point = config.get("mount_point", "secret")
        self.client = None

    def connect(self) -> bool:
        """Подключение к Vault"""
        try:
            # Импорт hvac только при необходимости
            import hvac

            self.client = hvac.Client(url=self.vault_url, token=self.token)
            self.connected = self.client.is_authenticated()
            return self.connected
        except ImportError:
            self.log_activity(
                "hvac не установлен. Установите: pip install hvac", "warning"
            )
            return False
        except Exception as e:
            self.log_activity(f"Ошибка подключения к Vault: {e}", "error")
            return False

    def get_secret(self, key: str) -> Optional[str]:
        """Получение секрета из Vault"""
        if not self.connected:
            return None

        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=key, mount_point=self.mount_point
            )
            return response["data"]["data"].get("value")
        except Exception as e:
            self.log_activity(
                f"Ошибка получения секрета {key} из Vault: {e}", "error"
            )
            return None

    def set_secret(
        self, key: str, value: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Сохранение секрета в Vault"""
        if not self.connected:
            return False

        try:
            secret_data = {"value": value}
            if metadata:
                secret_data.update(metadata)

            self.client.secrets.kv.v2.create_or_update_secret(
                path=key, secret=secret_data, mount_point=self.mount_point
            )
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка сохранения секрета {key} в Vault: {e}", "error"
            )
            return False

    def delete_secret(self, key: str) -> bool:
        """Удаление секрета из Vault"""
        if not self.connected:
            return False

        try:
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=key, mount_point=self.mount_point
            )
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка удаления секрета {key} из Vault: {e}", "error"
            )
            return False

    def list_secrets(self) -> List[str]:
        """Список секретов в Vault"""
        if not self.connected:
            return []

        try:
            response = self.client.secrets.kv.v2.list_secrets(
                path="", mount_point=self.mount_point
            )
            return response.get("data", {}).get("keys", [])
        except Exception as e:
            self.log_activity(
                f"Ошибка получения списка секретов из Vault: {e}", "error"
            )
            return []

    def health_check(self) -> bool:
        """Проверка здоровья Vault"""
        if not self.connected:
            return False

        try:
            return self.client.is_authenticated()
        except Exception:
            return False


class AWSSecretsManagerProvider(ExternalSecretProvider):
    """Провайдер для AWS Secrets Manager"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("AWS Secrets Manager", config)
        self.region = config.get("region", "us-east-1")
        self.client = None

    def connect(self) -> bool:
        """Подключение к AWS Secrets Manager"""
        try:
            import boto3

            self.client = boto3.client(
                "secretsmanager", region_name=self.region
            )
            # Проверка подключения
            self.client.list_secrets(MaxResults=1)
            self.connected = True
            return True
        except ImportError:
            self.log_activity(
                "boto3 не установлен. Установите: pip install boto3", "warning"
            )
            return False
        except Exception as e:
            self.log_activity(
                f"Ошибка подключения к AWS Secrets Manager: {e}", "error"
            )
            return False

    def get_secret(self, key: str) -> Optional[str]:
        """Получение секрета из AWS Secrets Manager"""
        if not self.connected:
            return None

        try:
            response = self.client.get_secret_value(SecretId=key)
            return response["SecretString"]
        except Exception as e:
            self.log_activity(
                f"Ошибка получения секрета {key} из AWS: {e}", "error"
            )
            return None

    def set_secret(
        self, key: str, value: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Сохранение секрета в AWS Secrets Manager"""
        if not self.connected:
            return False

        try:
            self.client.create_secret(
                Name=key,
                SecretString=value,
                Description=(
                    metadata.get("description", "") if metadata else ""
                ),
            )
            return True
        except self.client.exceptions.ResourceExistsException:
            # Секрет уже существует, обновляем
            try:
                self.client.update_secret(
                    SecretId=key,
                    SecretString=value,
                    Description=(
                        metadata.get("description", "") if metadata else ""
                    ),
                )
                return True
            except Exception as e:
                self.log_activity(
                    f"Ошибка обновления секрета {key} в AWS: {e}", "error"
                )
                return False
        except Exception as e:
            self.log_activity(
                f"Ошибка сохранения секрета {key} в AWS: {e}", "error"
            )
            return False

    def delete_secret(self, key: str) -> bool:
        """Удаление секрета из AWS Secrets Manager"""
        if not self.connected:
            return False

        try:
            self.client.delete_secret(
                SecretId=key, ForceDeleteWithoutRecovery=True
            )
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка удаления секрета {key} из AWS: {e}", "error"
            )
            return False

    def list_secrets(self) -> List[str]:
        """Список секретов в AWS Secrets Manager"""
        if not self.connected:
            return []

        try:
            response = self.client.list_secrets()
            return [
                secret["Name"] for secret in response.get("SecretList", [])
            ]
        except Exception as e:
            self.log_activity(
                f"Ошибка получения списка секретов из AWS: {e}", "error"
            )
            return []

    def health_check(self) -> bool:
        """Проверка здоровья AWS Secrets Manager"""
        if not self.connected:
            return False

        try:
            self.client.list_secrets(MaxResults=1)
            return True
        except Exception:
            return False


class SecretsManager(SecurityBase):
    """Централизованный менеджер секретов"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Инициализация менеджера секретов"""
        super().__init__("SecretsManager", config)

        # Конфигурация
        self.config = config or {}
        self.storage_path = Path(
            self.config.get("storage_path", "data/secrets")
        )
        self.encryption_key = self._generate_or_load_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)

        # Хранилище секретов
        self.secrets: Dict[str, str] = {}
        self.metadata: Dict[str, SecretMetadata] = {}
        self.lock = threading.RLock()

        # Внешние провайдеры
        self.external_providers: Dict[str, ExternalSecretProvider] = {}
        self.primary_provider = None

        # Настройки ротации
        self.auto_rotation_enabled = self.config.get("auto_rotation", True)
        self.rotation_interval = self.config.get(
            "rotation_interval", 30
        )  # дни
        self.rotation_thread = None
        self.rotation_running = False

        # Метрики
        self.metrics = {
            "secrets_count": 0,
            "access_count": 0,
            "rotation_count": 0,
            "error_count": 0,
            "external_sync_count": 0,
        }

        self.log_activity("SecretsManager инициализирован")

    def _generate_or_load_encryption_key(self) -> bytes:
        """Генерация или загрузка ключа шифрования"""
        key_file = self.storage_path / "encryption.key"

        if key_file.exists():
            try:
                with open(key_file, "rb") as f:
                    return f.read()
            except Exception as e:
                self.log_activity(
                    f"Ошибка загрузки ключа шифрования: {e}", "error"
                )

        # Генерация нового ключа
        key = Fernet.generate_key()

        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            with open(key_file, "wb") as f:
                f.write(key)
            self.log_activity("Новый ключ шифрования сгенерирован")
        except Exception as e:
            self.log_activity(
                f"Ошибка сохранения ключа шифрования: {e}", "error"
            )

        return key

    def _encrypt_secret(self, secret: str) -> str:
        """Шифрование секрета"""
        try:
            encrypted = self.cipher_suite.encrypt(secret.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            self.log_activity(f"Ошибка шифрования секрета: {e}", "error")
            raise

    def _decrypt_secret(self, encrypted_secret: str) -> str:
        """Расшифровка секрета"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_secret.encode())
            decrypted = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            self.log_activity(f"Ошибка расшифровки секрета: {e}", "error")
            raise

    def _generate_secret_id(self, name: str) -> str:
        """Генерация уникального ID секрета"""
        timestamp = datetime.now().isoformat()
        data = f"{name}_{timestamp}_{secrets.token_hex(8)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def initialize(self) -> bool:
        """Инициализация менеджера секретов"""
        try:
            self.log_activity("Инициализация SecretsManager...")

            # Создание директории для хранения
            self.storage_path.mkdir(parents=True, exist_ok=True)

            # Загрузка существующих секретов
            self._load_secrets()

            # Инициализация внешних провайдеров
            self._initialize_external_providers()

            # Запуск ротации секретов
            if self.auto_rotation_enabled:
                self._start_rotation_thread()

            self.status = ComponentStatus.RUNNING
            self.log_activity("SecretsManager инициализирован успешно")
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации SecretsManager: {e}", "error"
            )
            self.status = ComponentStatus.ERROR
            return False

    def _load_secrets(self) -> None:
        """Загрузка секретов из файлового хранилища"""
        try:
            secrets_file = self.storage_path / "secrets.json"
            metadata_file = self.storage_path / "metadata.json"

            if secrets_file.exists():
                with open(secrets_file, "r", encoding="utf-8") as f:
                    self.secrets = json.load(f)

            if metadata_file.exists():
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata_data = json.load(f)
                    for secret_id, meta_data in metadata_data.items():
                        self.metadata[secret_id] = SecretMetadata.from_dict(
                            meta_data
                        )

            self.metrics["secrets_count"] = len(self.secrets)
            self.log_activity(f"Загружено {len(self.secrets)} секретов")

        except Exception as e:
            self.log_activity(f"Ошибка загрузки секретов: {e}", "error")

    def _save_secrets(self) -> None:
        """Сохранение секретов в файловое хранилище"""
        try:
            with self.lock:
                secrets_file = self.storage_path / "secrets.json"
                metadata_file = self.storage_path / "metadata.json"

                with open(secrets_file, "w", encoding="utf-8") as f:
                    json.dump(self.secrets, f, ensure_ascii=False, indent=2)

                metadata_data = {
                    secret_id: metadata.to_dict()
                    for secret_id, metadata in self.metadata.items()
                }

                with open(metadata_file, "w", encoding="utf-8") as f:
                    json.dump(metadata_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.log_activity(f"Ошибка сохранения секретов: {e}", "error")

    def _initialize_external_providers(self) -> None:
        """Инициализация внешних провайдеров"""
        providers_config = self.config.get("external_providers", {})

        for provider_name, provider_config in providers_config.items():
            try:
                if provider_name == "vault":
                    provider = HashiCorpVaultProvider(provider_config)
                elif provider_name == "aws":
                    provider = AWSSecretsManagerProvider(provider_config)
                else:
                    self.log_activity(
                        f"Неизвестный провайдер: {provider_name}", "warning"
                    )
                    continue

                if provider.connect():
                    self.external_providers[provider_name] = provider
                    if not self.primary_provider:
                        self.primary_provider = provider
                    self.log_activity(f"Провайдер {provider_name} подключен")
                else:
                    self.log_activity(
                        f"Ошибка подключения провайдера {provider_name}",
                        "error",
                    )

            except Exception as e:
                self.log_activity(
                    f"Ошибка инициализации провайдера {provider_name}: {e}",
                    "error",
                )

    def store_secret(
        self,
        name: str,
        value: str,
        secret_type: SecretType = SecretType.CUSTOM,
        expires_at: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        owner: Optional[str] = None,
        sync_to_external: bool = True,
    ) -> str:
        """Сохранение секрета"""
        try:
            with self.lock:
                # Генерация ID секрета
                secret_id = self._generate_secret_id(name)

                # Шифрование секрета
                encrypted_value = self._encrypt_secret(value)

                # Создание метаданных
                metadata = SecretMetadata(
                    secret_id=secret_id,
                    name=name,
                    secret_type=secret_type,
                    created_at=datetime.now(),
                    expires_at=expires_at,
                    tags=tags,
                    description=description,
                    owner=owner,
                )

                # Сохранение
                self.secrets[secret_id] = encrypted_value
                self.metadata[secret_id] = metadata

                # Синхронизация с внешними системами
                if sync_to_external and self.primary_provider:
                    try:
                        self.primary_provider.set_secret(
                            name, value, metadata.to_dict()
                        )
                        self.metrics["external_sync_count"] += 1
                    except Exception as e:
                        self.log_activity(
                            f"Ошибка синхронизации с внешней системой: {e}",
                            "warning",
                        )

                # Сохранение в файл
                self._save_secrets()

                self.metrics["secrets_count"] = len(self.secrets)
                self.log_activity(f"Секрет {name} сохранен с ID {secret_id}")

                return secret_id

        except Exception as e:
            self.log_activity(
                f"Ошибка сохранения секрета {name}: {e}", "error"
            )
            self.metrics["error_count"] += 1
            raise

    def get_secret(self, secret_id: str) -> Optional[str]:
        """Получение секрета по ID"""
        try:
            with self.lock:
                if secret_id not in self.secrets:
                    self.log_activity(
                        f"Секрет {secret_id} не найден", "warning"
                    )
                    return None

                # Проверка срока действия
                metadata = self.metadata.get(secret_id)
                if (
                    metadata
                    and metadata.expires_at
                    and metadata.expires_at < datetime.now()
                ):
                    metadata.status = SecretStatus.EXPIRED
                    self.log_activity(f"Секрет {secret_id} истек", "warning")
                    return None

                # Расшифровка секрета
                encrypted_value = self.secrets[secret_id]
                decrypted_value = self._decrypt_secret(encrypted_value)

                # Обновление метаданных
                if metadata:
                    metadata.access_count += 1
                    metadata.last_accessed = datetime.now()

                self.metrics["access_count"] += 1
                self.log_activity(f"Секрет {secret_id} получен")

                return decrypted_value

        except Exception as e:
            self.log_activity(
                f"Ошибка получения секрета {secret_id}: {e}", "error"
            )
            self.metrics["error_count"] += 1
            return None

    def get_secret_by_name(self, name: str) -> Optional[str]:
        """Получение секрета по имени"""
        try:
            with self.lock:
                for secret_id, metadata in self.metadata.items():
                    if metadata.name == name:
                        return self.get_secret(secret_id)
                return None
        except Exception as e:
            self.log_activity(
                f"Ошибка поиска секрета по имени {name}: {e}", "error"
            )
            return None

    def delete_secret(self, secret_id: str) -> bool:
        """Удаление секрета"""
        try:
            with self.lock:
                if secret_id not in self.secrets:
                    self.log_activity(
                        f"Секрет {secret_id} не найден", "warning"
                    )
                    return False

                # Получение метаданных для синхронизации
                metadata = self.metadata.get(secret_id)

                # Удаление из локального хранилища
                del self.secrets[secret_id]
                if metadata:
                    del self.metadata[secret_id]

                # Синхронизация с внешними системами
                if metadata and self.primary_provider:
                    try:
                        self.primary_provider.delete_secret(metadata.name)
                    except Exception as e:
                        self.log_activity(
                            f"Ошибка удаления из внешней системы: {e}",
                            "warning",
                        )

                # Сохранение изменений
                self._save_secrets()

                self.metrics["secrets_count"] = len(self.secrets)
                self.log_activity(f"Секрет {secret_id} удален")

                return True

        except Exception as e:
            self.log_activity(
                f"Ошибка удаления секрета {secret_id}: {e}", "error"
            )
            self.metrics["error_count"] += 1
            return False

    def rotate_secret(
        self, secret_id: str, new_value: Optional[str] = None
    ) -> bool:
        """Ротация секрета"""
        try:
            with self.lock:
                if secret_id not in self.secrets:
                    self.log_activity(
                        f"Секрет {secret_id} не найден", "warning"
                    )
                    return False

                metadata = self.metadata.get(secret_id)
                if not metadata:
                    return False

                # Генерация нового значения если не предоставлено
                if new_value is None:
                    new_value = self._generate_new_secret_value(
                        metadata.secret_type
                    )

                # Шифрование нового значения
                encrypted_value = self._encrypt_secret(new_value)

                # Обновление секрета
                self.secrets[secret_id] = encrypted_value
                metadata.version += 1
                metadata.status = SecretStatus.ACTIVE

                # Синхронизация с внешними системами
                if self.primary_provider:
                    try:
                        self.primary_provider.set_secret(
                            metadata.name, new_value, metadata.to_dict()
                        )
                    except Exception as e:
                        self.log_activity(
                            f"Ошибка синхронизации ротации: {e}", "warning"
                        )

                # Сохранение изменений
                self._save_secrets()

                self.metrics["rotation_count"] += 1
                self.log_activity(
                    f"Секрет {secret_id} ротирован (версия {metadata.version})"
                )

                return True

        except Exception as e:
            self.log_activity(
                f"Ошибка ротации секрета {secret_id}: {e}", "error"
            )
            self.metrics["error_count"] += 1
            return False

    def _generate_new_secret_value(self, secret_type: SecretType) -> str:
        """Генерация нового значения секрета"""
        if secret_type == SecretType.PASSWORD:
            return self._generate_password()
        elif secret_type == SecretType.API_KEY:
            return self._generate_api_key()
        elif secret_type == SecretType.ENCRYPTION_KEY:
            return base64.b64encode(Fernet.generate_key()).decode()
        else:
            return secrets.token_urlsafe(32)

    def _generate_password(self, length: int = 16) -> str:
        """Генерация пароля"""
        import string

        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(chars) for _ in range(length))

    def _generate_api_key(self, length: int = 32) -> str:
        """Генерация API ключа"""
        return secrets.token_urlsafe(length)

    def list_secrets(
        self, secret_type: Optional[SecretType] = None
    ) -> List[Dict[str, Any]]:
        """Список секретов"""
        try:
            with self.lock:
                result = []
                for secret_id, metadata in self.metadata.items():
                    if (
                        secret_type is None
                        or metadata.secret_type == secret_type
                    ):
                        result.append(
                            {
                                "secret_id": secret_id,
                                "name": metadata.name,
                                "type": metadata.secret_type.value,
                                "status": metadata.status.value,
                                "created_at": metadata.created_at.isoformat(),
                                "expires_at": (
                                    metadata.expires_at.isoformat()
                                    if metadata.expires_at
                                    else None
                                ),
                                "access_count": metadata.access_count,
                                "version": metadata.version,
                            }
                        )
                return result
        except Exception as e:
            self.log_activity(
                f"Ошибка получения списка секретов: {e}", "error"
            )
            return []

    def get_secret_metadata(self, secret_id: str) -> Optional[Dict[str, Any]]:
        """Получение метаданных секрета"""
        try:
            with self.lock:
                metadata = self.metadata.get(secret_id)
                if metadata:
                    return metadata.to_dict()
                return None
        except Exception as e:
            self.log_activity(
                f"Ошибка получения метаданных секрета {secret_id}: {e}",
                "error",
            )
            return None

    def _start_rotation_thread(self) -> None:
        """Запуск потока ротации секретов"""
        if self.rotation_thread and self.rotation_thread.is_alive():
            return

        self.rotation_running = True
        self.rotation_thread = threading.Thread(
            target=self._rotation_worker, daemon=True
        )
        self.rotation_thread.start()
        self.log_activity("Поток ротации секретов запущен")

    def _rotation_worker(self) -> None:
        """Рабочий поток ротации секретов"""
        while self.rotation_running:
            try:
                current_time = datetime.now()

                with self.lock:
                    for secret_id, metadata in self.metadata.items():
                        if (
                            metadata.expires_at
                            and metadata.expires_at <= current_time
                        ):
                            # Секрет истек, помечаем для ротации
                            metadata.status = SecretStatus.PENDING_ROTATION
                            self.log_activity(
                                f"Секрет {secret_id} помечен для ротации"
                            )

                        # Автоматическая ротация по расписанию
                        if (
                            metadata.rotation_schedule
                            and current_time >= metadata.rotation_schedule
                        ):
                            self.rotate_secret(secret_id)

                # Проверка каждые 6 часов
                time.sleep(6 * 60 * 60)

            except Exception as e:
                self.log_activity(f"Ошибка в потоке ротации: {e}", "error")
                time.sleep(60)  # Пауза при ошибке

    def stop(self) -> bool:
        """Остановка менеджера секретов"""
        try:
            self.log_activity("Остановка SecretsManager...")

            # Остановка потока ротации
            self.rotation_running = False
            if self.rotation_thread and self.rotation_thread.is_alive():
                self.rotation_thread.join(timeout=5)

            # Сохранение секретов
            self._save_secrets()

            self.status = ComponentStatus.STOPPED
            self.log_activity("SecretsManager остановлен")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка остановки SecretsManager: {e}", "error")
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Получение метрик"""
        return {
            "secrets_count": self.metrics["secrets_count"],
            "access_count": self.metrics["access_count"],
            "rotation_count": self.metrics["rotation_count"],
            "error_count": self.metrics["error_count"],
            "external_sync_count": self.metrics["external_sync_count"],
            "external_providers": len(self.external_providers),
            "primary_provider": (
                self.primary_provider.name if self.primary_provider else None
            ),
            "auto_rotation_enabled": self.auto_rotation_enabled,
        }

    def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья"""
        health_status = {
            "status": "healthy",
            "secrets_count": len(self.secrets),
            "external_providers": {},
            "rotation_thread": (
                self.rotation_thread.is_alive()
                if self.rotation_thread
                else False
            ),
            "storage_path": str(self.storage_path),
            "storage_writable": self.storage_path.is_dir()
            and self.storage_path.exists(),
        }

        # Проверка внешних провайдеров
        for name, provider in self.external_providers.items():
            health_status["external_providers"][name] = provider.health_check()

        # Общая оценка здоровья
        if not health_status["storage_writable"]:
            health_status["status"] = "unhealthy"
        elif not all(health_status["external_providers"].values()):
            health_status["status"] = "degraded"

        return health_status


# Глобальный экземпляр менеджера секретов
_secrets_manager_instance = None


def get_secrets_manager() -> SecretsManager:
    """Получение глобального экземпляра менеджера секретов"""
    global _secrets_manager_instance
    if _secrets_manager_instance is None:
        _secrets_manager_instance = SecretsManager()
        _secrets_manager_instance.initialize()
    return _secrets_manager_instance


def initialize_secrets_manager(
    config: Optional[Dict[str, Any]] = None
) -> SecretsManager:
    """Инициализация глобального менеджера секретов"""
    global _secrets_manager_instance
    _secrets_manager_instance = SecretsManager(config)
    _secrets_manager_instance.initialize()
    return _secrets_manager_instance


# Декоратор для автоматического управления секретами
def with_secret(secret_name: str, secret_type: SecretType = SecretType.CUSTOM):
    """Декоратор для автоматического получения секрета"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            secrets_manager = get_secrets_manager()
            secret_value = secrets_manager.get_secret_by_name(secret_name)
            if secret_value is None:
                raise ValueError(f"Секрет {secret_name} не найден")
            return func(*args, secret=secret_value, **kwargs)

        return wrapper

    return decorator


if __name__ == "__main__":
    # Пример использования
    config = {
        "storage_path": "data/secrets",
        "auto_rotation": True,
        "rotation_interval": 30,
        "external_providers": {
            "vault": {
                "vault_url": "http://localhost:8200",
                "token": "your-vault-token",
                "mount_point": "secret",
            }
        },
    }

    # Инициализация
    secrets_manager = initialize_secrets_manager(config)

    # Сохранение секрета
    secret_id = secrets_manager.store_secret(
        name="database_password",
        value="super_secret_password",
        secret_type=SecretType.PASSWORD,
        description="Пароль для базы данных",
        tags={"environment": "production", "service": "database"},
    )

    # Получение секрета
    password = secrets_manager.get_secret(secret_id)
    print(f"Получен пароль: {password}")

    # Список секретов
    secrets_list = secrets_manager.list_secrets()
    print(f"Всего секретов: {len(secrets_list)}")

    # Метрики
    metrics = secrets_manager.get_metrics()
    print(f"Метрики: {metrics}")

    # Проверка здоровья
    health = secrets_manager.health_check()
    print(f"Состояние: {health}")
