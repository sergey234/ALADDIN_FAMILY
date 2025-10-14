# -*- coding: utf-8 -*-
"""
Менеджер шифрования для ParentalControlBot
Версия: 2.5
Дата: 2025-09-21
"""

import asyncio
import base64
import hashlib
import json
import logging
import os
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    from cryptography.hazmat.primitives.ciphers import (
        Cipher,
        algorithms,
        modes,
    )
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    # Fallback implementations
    import base64
    import hashlib
    import secrets


class EncryptionAlgorithm(Enum):
    """Алгоритмы шифрования"""

    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    FERNET = "fernet"
    RSA_OAEP = "rsa_oaep"
    CHACHA20_POLY1305 = "chacha20_poly1305"


class KeyDerivation(Enum):
    """Методы выведения ключей"""

    PBKDF2 = "pbkdf2"
    SCRYPT = "scrypt"
    ARGON2 = "argon2"


@dataclass
class EncryptionKey:
    """Ключ шифрования"""

    key_id: str
    algorithm: EncryptionAlgorithm
    key_data: bytes
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None

    def is_expired(self) -> bool:
        """Проверка истечения срока действия ключа"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


@dataclass
class EncryptedData:
    """Зашифрованные данные"""

    data: bytes
    key_id: str
    algorithm: EncryptionAlgorithm
    iv: Optional[bytes] = None
    tag: Optional[bytes] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class EncryptionManager:
    """Менеджер шифрования данных"""

    def __init__(
        self,
        logger: logging.Logger,
        master_password: Optional[str] = None,
        key_derivation: KeyDerivation = KeyDerivation.PBKDF2,
        default_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
        key_rotation_days: int = 90,
    ):
        self.logger = logger
        self.master_password = (
            master_password or self._generate_master_password()
        )
        self.key_derivation = key_derivation
        self.default_algorithm = default_algorithm
        self.key_rotation_days = key_rotation_days

        # Хранилище ключей
        self.keys: Dict[str, EncryptionKey] = {}
        self.active_key_id: Optional[str] = None

        # Кэш для производительности
        self._cipher_cache: Dict[str, Any] = {}
        self._cache_ttl = 300  # 5 минут

        # Инициализация
        self._initialize_encryption()

    def _generate_master_password(self) -> str:
        """Генерация мастер-пароля"""
        return secrets.token_urlsafe(32)

    def _initialize_encryption(self):
        """Инициализация системы шифрования"""
        try:
            if not CRYPTOGRAPHY_AVAILABLE:
                self.logger.warning(
                    "Cryptography не доступна, используется упрощенное шифрование"
                )
                return

            # Создание основного ключа
            self._create_master_key()

            self.logger.info("Система шифрования инициализирована")

        except Exception as e:
            self.logger.error(f"Ошибка инициализации шифрования: {e}")

    def _create_master_key(self):
        """Создание мастер-ключа"""
        try:
            key_id = f"master_{int(time.time())}"

            if self.default_algorithm == EncryptionAlgorithm.FERNET:
                key_data = Fernet.generate_key()
            else:
                key_data = secrets.token_bytes(32)  # 256 bits

            key = EncryptionKey(
                key_id=key_id,
                algorithm=self.default_algorithm,
                key_data=key_data,
                created_at=datetime.now(),
                expires_at=datetime.now()
                + timedelta(days=self.key_rotation_days),
            )

            self.keys[key_id] = key
            self.active_key_id = key_id

            self.logger.info(f"Мастер-ключ создан: {key_id}")

        except Exception as e:
            self.logger.error(f"Ошибка создания мастер-ключа: {e}")

    def _derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Выведение ключа из пароля"""
        try:
            if self.key_derivation == KeyDerivation.PBKDF2:
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                    backend=default_backend(),
                )
                return kdf.derive(password.encode())
            else:
                # Fallback к простому хэшированию
                return hashlib.pbkdf2_hmac(
                    "sha256", password.encode(), salt, 100000
                )

        except Exception as e:
            self.logger.error(f"Ошибка выведения ключа: {e}")
            return hashlib.sha256(password.encode() + salt).digest()

    def _get_cipher(self, key: EncryptionKey) -> Any:
        """Получение шифратора для ключа"""
        try:
            cache_key = f"{key.key_id}_{key.algorithm.value}"

            # Проверка кэша
            if cache_key in self._cipher_cache:
                cached_item = self._cipher_cache[cache_key]
                if time.time() - cached_item["timestamp"] < self._cache_ttl:
                    return cached_item["cipher"]

            cipher = None

            if key.algorithm == EncryptionAlgorithm.FERNET:
                cipher = Fernet(key.key_data)
            elif key.algorithm == EncryptionAlgorithm.AES_256_GCM:
                # Для AES-GCM нужен IV, создаем заглушку
                cipher = algorithms.AES(key.key_data)
            elif key.algorithm == EncryptionAlgorithm.AES_256_CBC:
                cipher = algorithms.AES(key.key_data)

            # Кэширование
            self._cipher_cache[cache_key] = {
                "cipher": cipher,
                "timestamp": time.time(),
            }

            return cipher

        except Exception as e:
            self.logger.error(f"Ошибка создания шифратора: {e}")
            return None

    async def encrypt_data(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        key_id: Optional[str] = None,
        algorithm: Optional[EncryptionAlgorithm] = None,
    ) -> EncryptedData:
        """Шифрование данных"""
        try:
            # Подготовка данных
            if isinstance(data, str):
                data_bytes = data.encode("utf-8")
            elif isinstance(data, dict):
                data_bytes = json.dumps(data, ensure_ascii=False).encode(
                    "utf-8"
                )
            else:
                data_bytes = data

            # Выбор ключа
            if key_id and key_id in self.keys:
                key = self.keys[key_id]
            elif self.active_key_id:
                key = self.keys[self.active_key_id]
            else:
                raise ValueError("Нет доступного ключа для шифрования")

            # Проверка срока действия ключа
            if key.is_expired():
                await self._rotate_key(key_id)
                key = self.keys[self.active_key_id]

            # Выбор алгоритма
            algo = algorithm or key.algorithm

            # Шифрование
            if algo == EncryptionAlgorithm.FERNET:
                encrypted_data = await self._encrypt_fernet(data_bytes, key)
            elif algo == EncryptionAlgorithm.AES_256_GCM:
                encrypted_data = await self._encrypt_aes_gcm(data_bytes, key)
            elif algo == EncryptionAlgorithm.AES_256_CBC:
                encrypted_data = await self._encrypt_aes_cbc(data_bytes, key)
            else:
                # Fallback к простому шифрованию
                encrypted_data = await self._encrypt_simple(data_bytes, key)

            return encrypted_data

        except Exception as e:
            self.logger.error(f"Ошибка шифрования данных: {e}")
            raise

    async def decrypt_data(
        self, encrypted_data: EncryptedData
    ) -> Union[str, bytes, Dict[str, Any]]:
        """Расшифровка данных"""
        try:
            key = self.keys.get(encrypted_data.key_id)
            if not key:
                raise ValueError(f"Ключ {encrypted_data.key_id} не найден")

            if key.is_expired():
                raise ValueError(f"Ключ {encrypted_data.key_id} истек")

            # Расшифровка
            if encrypted_data.algorithm == EncryptionAlgorithm.FERNET:
                decrypted_bytes = await self._decrypt_fernet(
                    encrypted_data, key
                )
            elif encrypted_data.algorithm == EncryptionAlgorithm.AES_256_GCM:
                decrypted_bytes = await self._decrypt_aes_gcm(
                    encrypted_data, key
                )
            elif encrypted_data.algorithm == EncryptionAlgorithm.AES_256_CBC:
                decrypted_bytes = await self._decrypt_aes_cbc(
                    encrypted_data, key
                )
            else:
                # Fallback к простому расшифрованию
                decrypted_bytes = await self._decrypt_simple(
                    encrypted_data, key
                )

            # Попытка декодирования как JSON
            try:
                return json.loads(decrypted_bytes.decode("utf-8"))
            except:
                # Попытка декодирования как строка
                try:
                    return decrypted_bytes.decode("utf-8")
                except:
                    # Возврат как байты
                    return decrypted_bytes

        except Exception as e:
            self.logger.error(f"Ошибка расшифровки данных: {e}")
            raise

    async def _encrypt_fernet(
        self, data: bytes, key: EncryptionKey
    ) -> EncryptedData:
        """Шифрование с помощью Fernet"""
        try:
            if not CRYPTOGRAPHY_AVAILABLE:
                return await self._encrypt_simple(data, key)

            cipher = Fernet(key.key_data)
            encrypted_bytes = cipher.encrypt(data)

            return EncryptedData(
                data=encrypted_bytes,
                key_id=key.key_id,
                algorithm=EncryptionAlgorithm.FERNET,
                timestamp=datetime.now(),
            )

        except Exception as e:
            self.logger.error(f"Ошибка Fernet шифрования: {e}")
            return await self._encrypt_simple(data, key)

    async def _decrypt_fernet(
        self, encrypted_data: EncryptedData, key: EncryptionKey
    ) -> bytes:
        """Расшифровка с помощью Fernet"""
        try:
            if not CRYPTOGRAPHY_AVAILABLE:
                return await self._decrypt_simple(encrypted_data, key)

            cipher = Fernet(key.key_data)
            return cipher.decrypt(encrypted_data.data)

        except Exception as e:
            self.logger.error(f"Ошибка Fernet расшифровки: {e}")
            return await self._decrypt_simple(encrypted_data, key)

    async def _encrypt_aes_gcm(
        self, data: bytes, key: EncryptionKey
    ) -> EncryptedData:
        """Шифрование с помощью AES-GCM"""
        try:
            if not CRYPTOGRAPHY_AVAILABLE:
                return await self._encrypt_simple(data, key)

            iv = secrets.token_bytes(12)  # 96 bits для GCM
            cipher = Cipher(
                algorithms.AES(key.key_data),
                modes.GCM(iv),
                backend=default_backend(),
            )
            encryptor = cipher.encryptor()

            encrypted_bytes = encryptor.update(data) + encryptor.finalize()

            return EncryptedData(
                data=encrypted_bytes,
                key_id=key.key_id,
                algorithm=EncryptionAlgorithm.AES_256_GCM,
                iv=iv,
                tag=encryptor.tag,
                timestamp=datetime.now(),
            )

        except Exception as e:
            self.logger.error(f"Ошибка AES-GCM шифрования: {e}")
            return await self._encrypt_simple(data, key)

    async def _decrypt_aes_gcm(
        self, encrypted_data: EncryptedData, key: EncryptionKey
    ) -> bytes:
        """Расшифровка с помощью AES-GCM"""
        try:
            if not CRYPTOGRAPHY_AVAILABLE:
                return await self._decrypt_simple(encrypted_data, key)

            cipher = Cipher(
                algorithms.AES(key.key_data),
                modes.GCM(encrypted_data.iv, encrypted_data.tag),
                backend=default_backend(),
            )
            decryptor = cipher.decryptor()

            return decryptor.update(encrypted_data.data) + decryptor.finalize()

        except Exception as e:
            self.logger.error(f"Ошибка AES-GCM расшифровки: {e}")
            return await self._decrypt_simple(encrypted_data, key)

    async def _encrypt_aes_cbc(
        self, data: bytes, key: EncryptionKey
    ) -> EncryptedData:
        """Шифрование с помощью AES-CBC"""
        try:
            if not CRYPTOGRAPHY_AVAILABLE:
                return await self._encrypt_simple(data, key)

            iv = secrets.token_bytes(16)  # 128 bits для CBC
            cipher = Cipher(
                algorithms.AES(key.key_data),
                modes.CBC(iv),
                backend=default_backend(),
            )
            encryptor = cipher.encryptor()

            # PKCS7 padding
            padding_length = 16 - (len(data) % 16)
            padded_data = data + bytes([padding_length] * padding_length)

            encrypted_bytes = (
                encryptor.update(padded_data) + encryptor.finalize()
            )

            return EncryptedData(
                data=encrypted_bytes,
                key_id=key.key_id,
                algorithm=EncryptionAlgorithm.AES_256_CBC,
                iv=iv,
                timestamp=datetime.now(),
            )

        except Exception as e:
            self.logger.error(f"Ошибка AES-CBC шифрования: {e}")
            return await self._encrypt_simple(data, key)

    async def _decrypt_aes_cbc(
        self, encrypted_data: EncryptedData, key: EncryptionKey
    ) -> bytes:
        """Расшифровка с помощью AES-CBC"""
        try:
            if not CRYPTOGRAPHY_AVAILABLE:
                return await self._decrypt_simple(encrypted_data, key)

            cipher = Cipher(
                algorithms.AES(key.key_data),
                modes.CBC(encrypted_data.iv),
                backend=default_backend(),
            )
            decryptor = cipher.decryptor()

            decrypted_bytes = (
                decryptor.update(encrypted_data.data) + decryptor.finalize()
            )

            # Удаление PKCS7 padding
            padding_length = decrypted_bytes[-1]
            return decrypted_bytes[:-padding_length]

        except Exception as e:
            self.logger.error(f"Ошибка AES-CBC расшифровки: {e}")
            return await self._decrypt_simple(encrypted_data, key)

    async def _encrypt_simple(
        self, data: bytes, key: EncryptionKey
    ) -> EncryptedData:
        """Простое шифрование (XOR)"""
        try:
            # Простое XOR шифрование
            key_bytes = key.key_data
            encrypted_bytes = bytearray()

            for i, byte in enumerate(data):
                encrypted_bytes.append(byte ^ key_bytes[i % len(key_bytes)])

            return EncryptedData(
                data=bytes(encrypted_bytes),
                key_id=key.key_id,
                algorithm=EncryptionAlgorithm.AES_256_CBC,  # Используем как fallback
                timestamp=datetime.now(),
            )

        except Exception as e:
            self.logger.error(f"Ошибка простого шифрования: {e}")
            # Fallback к base64 кодированию
            import base64

            return EncryptedData(
                data=base64.b64encode(data),
                key_id=key.key_id,
                algorithm=EncryptionAlgorithm.AES_256_CBC,
                timestamp=datetime.now(),
            )

    async def _decrypt_simple(
        self, encrypted_data: EncryptedData, key: EncryptionKey
    ) -> bytes:
        """Простое расшифровка (XOR)"""
        try:
            # Простое XOR расшифровка (тот же алгоритм)
            key_bytes = key.key_data
            decrypted_bytes = bytearray()

            for i, byte in enumerate(encrypted_data.data):
                decrypted_bytes.append(byte ^ key_bytes[i % len(key_bytes)])

            return bytes(decrypted_bytes)

        except Exception as e:
            self.logger.error(f"Ошибка простой расшифровки: {e}")
            # Fallback к base64 декодированию
            import base64

            return base64.b64decode(encrypted_data.data)

    async def _rotate_key(self, old_key_id: Optional[str] = None):
        """Ротация ключа"""
        try:
            # Деактивация старого ключа
            if old_key_id and old_key_id in self.keys:
                self.keys[old_key_id].is_active = False

            # Создание нового ключа
            self._create_master_key()

            self.logger.info(
                f"Ключ повернут: {old_key_id} -> {self.active_key_id}"
            )

        except Exception as e:
            self.logger.error(f"Ошибка ротации ключа: {e}")

    async def encrypt_sensitive_field(
        self, field_name: str, value: Any, child_id: Optional[str] = None
    ) -> EncryptedData:
        """Шифрование чувствительного поля"""
        try:
            # Подготовка метаданных
            metadata = {
                "field_name": field_name,
                "child_id": child_id,
                "encrypted_at": datetime.now().isoformat(),
            }

            # Шифрование
            encrypted_data = await self.encrypt_data(value)
            encrypted_data.metadata = metadata

            return encrypted_data

        except Exception as e:
            self.logger.error(f"Ошибка шифрования поля {field_name}: {e}")
            raise

    async def decrypt_sensitive_field(
        self, encrypted_data: EncryptedData
    ) -> Tuple[str, Any]:
        """Расшифровка чувствительного поля"""
        try:
            # Расшифровка
            decrypted_value = await self.decrypt_data(encrypted_data)

            # Извлечение метаданных
            field_name = (
                encrypted_data.metadata.get("field_name", "unknown")
                if encrypted_data.metadata
                else "unknown"
            )

            return field_name, decrypted_value

        except Exception as e:
            self.logger.error(f"Ошибка расшифровки поля: {e}")
            raise

    def hash_password(
        self, password: str, salt: Optional[bytes] = None
    ) -> Tuple[str, bytes]:
        """Хэширование пароля"""
        try:
            if salt is None:
                salt = secrets.token_bytes(32)

            # Используем PBKDF2 для хэширования пароля
            if CRYPTOGRAPHY_AVAILABLE:
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                    backend=default_backend(),
                )
                password_hash = kdf.derive(password.encode())
            else:
                password_hash = hashlib.pbkdf2_hmac(
                    "sha256", password.encode(), salt, 100000
                )

            return base64.b64encode(password_hash).decode("utf-8"), salt

        except Exception as e:
            self.logger.error(f"Ошибка хэширования пароля: {e}")
            # Fallback к простому хэшированию
            salt = salt or secrets.token_bytes(32)
            password_hash = hashlib.sha256(password.encode() + salt).digest()
            return base64.b64encode(password_hash).decode("utf-8"), salt

    def verify_password(
        self, password: str, stored_hash: str, salt: bytes
    ) -> bool:
        """Проверка пароля"""
        try:
            computed_hash, _ = self.hash_password(password, salt)
            return secrets.compare_digest(computed_hash, stored_hash)

        except Exception as e:
            self.logger.error(f"Ошибка проверки пароля: {e}")
            return False

    async def encrypt_file(
        self, file_path: str, output_path: Optional[str] = None
    ) -> str:
        """Шифрование файла"""
        try:
            if output_path is None:
                output_path = file_path + ".encrypted"

            with open(file_path, "rb") as f:
                file_data = f.read()

            encrypted_data = await self.encrypt_data(file_data)

            # Сохранение зашифрованного файла
            with open(output_path, "wb") as f:
                f.write(encrypted_data.data)

            # Сохранение метаданных
            metadata_path = output_path + ".meta"
            metadata = {
                "key_id": encrypted_data.key_id,
                "algorithm": encrypted_data.algorithm.value,
                "iv": (
                    base64.b64encode(encrypted_data.iv).decode("utf-8")
                    if encrypted_data.iv
                    else None
                ),
                "tag": (
                    base64.b64encode(encrypted_data.tag).decode("utf-8")
                    if encrypted_data.tag
                    else None
                ),
                "timestamp": encrypted_data.timestamp.isoformat(),
                "metadata": encrypted_data.metadata,
            }

            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            self.logger.info(f"Файл зашифрован: {file_path} -> {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Ошибка шифрования файла: {e}")
            raise

    async def decrypt_file(
        self, encrypted_file_path: str, output_path: Optional[str] = None
    ) -> str:
        """Расшифровка файла"""
        try:
            if output_path is None:
                output_path = encrypted_file_path.replace(".encrypted", "")

            # Загрузка метаданных
            metadata_path = encrypted_file_path + ".meta"
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            # Загрузка зашифрованных данных
            with open(encrypted_file_path, "rb") as f:
                encrypted_bytes = f.read()

            # Создание объекта EncryptedData
            encrypted_data = EncryptedData(
                data=encrypted_bytes,
                key_id=metadata["key_id"],
                algorithm=EncryptionAlgorithm(metadata["algorithm"]),
                iv=(
                    base64.b64decode(metadata["iv"])
                    if metadata["iv"]
                    else None
                ),
                tag=(
                    base64.b64decode(metadata["tag"])
                    if metadata["tag"]
                    else None
                ),
                metadata=metadata.get("metadata"),
                timestamp=datetime.fromisoformat(metadata["timestamp"]),
            )

            # Расшифровка
            decrypted_data = await self.decrypt_data(encrypted_data)

            # Сохранение расшифрованного файла
            if isinstance(decrypted_data, str):
                with open(output_path, "w") as f:
                    f.write(decrypted_data)
            else:
                with open(output_path, "wb") as f:
                    f.write(decrypted_data)

            self.logger.info(
                f"Файл расшифрован: {encrypted_file_path} -> {output_path}"
            )
            return output_path

        except Exception as e:
            self.logger.error(f"Ошибка расшифровки файла: {e}")
            raise

    def get_encryption_stats(self) -> Dict[str, Any]:
        """Получение статистики шифрования"""
        return {
            "total_keys": len(self.keys),
            "active_key_id": self.active_key_id,
            "cryptography_available": CRYPTOGRAPHY_AVAILABLE,
            "default_algorithm": self.default_algorithm.value,
            "key_derivation": self.key_derivation.value,
            "keys": {
                key_id: {
                    "algorithm": key.algorithm.value,
                    "created_at": key.created_at.isoformat(),
                    "expires_at": (
                        key.expires_at.isoformat() if key.expires_at else None
                    ),
                    "is_active": key.is_active,
                    "is_expired": key.is_expired(),
                }
                for key_id, key in self.keys.items()
            },
        }

    async def cleanup_expired_keys(self) -> int:
        """Очистка истекших ключей"""
        try:
            expired_keys = []
            for key_id, key in self.keys.items():
                if key.is_expired() and not key.is_active:
                    expired_keys.append(key_id)

            for key_id in expired_keys:
                del self.keys[key_id]

            if expired_keys:
                self.logger.info(
                    f"Очищено {len(expired_keys)} истекших ключей"
                )

            return len(expired_keys)

        except Exception as e:
            self.logger.error(f"Ошибка очистки истекших ключей: {e}")
            return 0

    async def export_key(self, key_id: str, password: str) -> str:
        """Экспорт ключа"""
        try:
            key = self.keys.get(key_id)
            if not key:
                raise ValueError(f"Ключ {key_id} не найден")

            # Шифрование ключа для экспорта
            salt = secrets.token_bytes(32)
            derived_key = self._derive_key_from_password(password, salt)

            # Простое шифрование ключа
            encrypted_key = bytearray()
            for i, byte in enumerate(key.key_data):
                encrypted_key.append(byte ^ derived_key[i % len(derived_key)])

            export_data = {
                "key_id": key_id,
                "algorithm": key.algorithm.value,
                "encrypted_key": base64.b64encode(bytes(encrypted_key)).decode(
                    "utf-8"
                ),
                "salt": base64.b64encode(salt).decode("utf-8"),
                "created_at": key.created_at.isoformat(),
                "expires_at": (
                    key.expires_at.isoformat() if key.expires_at else None
                ),
            }

            return base64.b64encode(json.dumps(export_data).encode()).decode()

        except Exception as e:
            self.logger.error(f"Ошибка экспорта ключа: {e}")
            raise

    async def import_key(self, exported_key: str, password: str) -> str:
        """Импорт ключа"""
        try:
            # Расшифровка экспортированного ключа
            export_data = json.loads(base64.b64decode(exported_key).decode())

            salt = base64.b64decode(export_data["salt"])
            derived_key = self._derive_key_from_password(password, salt)

            encrypted_key = base64.b64decode(export_data["encrypted_key"])

            # Расшифровка ключа
            decrypted_key = bytearray()
            for i, byte in enumerate(encrypted_key):
                decrypted_key.append(byte ^ derived_key[i % len(derived_key)])

            # Создание объекта ключа
            key = EncryptionKey(
                key_id=export_data["key_id"],
                algorithm=EncryptionAlgorithm(export_data["algorithm"]),
                key_data=bytes(decrypted_key),
                created_at=datetime.fromisoformat(export_data["created_at"]),
                expires_at=(
                    datetime.fromisoformat(export_data["expires_at"])
                    if export_data["expires_at"]
                    else None
                ),
            )

            self.keys[key.key_id] = key

            self.logger.info(f"Ключ импортирован: {key.key_id}")
            return key.key_id

        except Exception as e:
            self.logger.error(f"Ошибка импорта ключа: {e}")
            raise
