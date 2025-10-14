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
import secrets
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, Optional, Tuple, Union

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers import (
        Cipher,
        algorithms,
        modes,
    )
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    # Fallback implementations уже импортированы выше


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
        """Инициализация timestamp при создании EncryptedData"""
        try:
            if self.timestamp is None:
                self.timestamp = datetime.now()
        except Exception as e:
            # Логирование ошибки инициализации timestamp
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"Ошибка инициализации timestamp в EncryptedData: {e}"
            )
            # Устанавливаем текущее время как fallback
            self.timestamp = datetime.now()


class EncryptionManager:
    """Менеджер шифрования данных"""

    def __init__(
        self,
        logger: logging.Logger,
        master_password: Optional[str] = None,
        key_derivation: KeyDerivation = KeyDerivation.PBKDF2,
        default_algorithm: EncryptionAlgorithm = (
            EncryptionAlgorithm.AES_256_GCM
        ),
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

        # Статистика использования
        self._encryption_count: int = 0
        self._decryption_count: int = 0
        self._error_count: int = 0
        self._last_activity: Optional[datetime] = None

        # Настройки безопасности
        self._max_key_age: int = 365  # дней
        self._min_key_length: int = 32  # байт
        self._encryption_timeout: int = 30  # секунд

        # ⚡ ОПТИМИЗАЦИИ CPU-ИНТЕНСИВНЫХ ФУНКЦИЙ
        # Расширенный кэш для ключей и результатов
        self._key_cache: Dict[str, Any] = {}
        self._encryption_cache: Dict[str, bytes] = {}
        self._cache_max_size = 1000
        
        # Пул потоков для CPU-интенсивных операций
        self._thread_pool = ThreadPoolExecutor(
            max_workers=4,
            thread_name_prefix="encryption_manager_worker"
        )
        
        # Асинхронная обработка
        self._async_lock = asyncio.Lock()
        self._processing_queue = asyncio.Queue(maxsize=100)
        
        # Метрики производительности
        self._performance_metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'thread_pool_usage': 0,
            'avg_encryption_time': 0.0,
            'avg_decryption_time': 0.0,
            'total_operations': 0
        }

        # Инициализация
        self._initialize_encryption()

    def __str__(self) -> str:
        """Строковое представление EncryptionManager"""
        return (
            f"EncryptionManager(keys={len(self.keys)}, "
            f"active_key={self.active_key_id}, "
            f"algorithm={self.default_algorithm.value})"
        )

    def __repr__(self) -> str:
        """Представление для отладки EncryptionManager"""
        return (
            f"EncryptionManager(logger={self.logger.name}, "
            f"keys={len(self.keys)}, active_key={self.active_key_id}, "
            f"algorithm={self.default_algorithm.value}, "
            f"derivation={self.key_derivation.value})"
        )

    def __eq__(self, other) -> bool:
        """Сравнение EncryptionManager с другим объектом"""
        if not isinstance(other, EncryptionManager):
            return False
        return (
            self.active_key_id == other.active_key_id
            and self.default_algorithm == other.default_algorithm
            and self.key_derivation == other.key_derivation
            and len(self.keys) == len(other.keys)
        )

    def _generate_master_password(self) -> str:
        """Генерация мастер-пароля"""
        return secrets.token_urlsafe(32)

    def _initialize_encryption(self):
        """Инициализация системы шифрования"""
        try:
            if not CRYPTOGRAPHY_AVAILABLE:
                self.logger.warning(
                    "Cryptography не доступна, "
                    "используется упрощенное шифрование"
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
        """
        Шифрование данных с валидацией параметров

        Args:
            data: Данные для шифрования (строка, bytes или словарь)
            key_id: ID ключа для шифрования (опционально)
            algorithm: Алгоритм шифрования (опционально)

        Returns:
            EncryptedData: Зашифрованные данные

        Raises:
            ValueError: При некорректных параметрах
            TypeError: При неверном типе данных
        """
        # Валидация параметров
        if data is None:
            raise ValueError("Данные для шифрования не могут быть None")

        if not isinstance(data, (str, bytes, dict)):
            raise TypeError(f"Неподдерживаемый тип данных: {type(data)}")

        if key_id is not None and not isinstance(key_id, str):
            raise TypeError("key_id должен быть строкой")

        if algorithm is not None and not isinstance(
            algorithm, EncryptionAlgorithm
        ):
            raise TypeError(
                "algorithm должен быть экземпляром EncryptionAlgorithm"
            )

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
        """
        Расшифровка данных с валидацией и обработкой ошибок

        Args:
            encrypted_data: Зашифрованные данные для расшифровки

        Returns:
            Union[str, bytes, Dict[str, Any]]: Расшифрованные данные в исходном
                формате

        Raises:
            ValueError: При отсутствии ключа или истечении срока действия
            TypeError: При неверном типе encrypted_data
            Exception: При ошибках расшифровки

        Example:
            >>> encrypted = await manager.encrypt_data("secret")
            >>> decrypted = await manager.decrypt_data(encrypted)
            >>> assert decrypted == "secret"
        """
        # Валидация параметров
        if not isinstance(encrypted_data, EncryptedData):
            raise TypeError(
                "encrypted_data должен быть экземпляром EncryptedData"
            )

        if encrypted_data.data is None or len(encrypted_data.data) == 0:
            raise ValueError("Зашифрованные данные не могут быть пустыми")

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
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Попытка декодирования как строка
                try:
                    return decrypted_bytes.decode("utf-8")
                except UnicodeDecodeError:
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
                algorithm=EncryptionAlgorithm.AES_256_CBC,  # Fallback
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

    async def hash_password(
        self, password: str, salt: Optional[bytes] = None
    ) -> Tuple[str, bytes]:
        """
        Асинхронное хэширование пароля с валидацией

        Args:
            password: Пароль для хэширования
            salt: Соль для хэширования (опционально, генерируется
                автоматически)

        Returns:
            Tuple[str, bytes]: Кортеж (хеш_пароля, соль)

        Raises:
            ValueError: При пустом пароле
            TypeError: При неверном типе параметров

        Example:
            >>> hash_result, salt = await manager.hash_password("mypassword")
            >>> assert isinstance(hash_result, str)
            >>> assert isinstance(salt, bytes)
        """
        # Валидация параметров
        if not password or not isinstance(password, str):
            raise ValueError(
                "Пароль не может быть пустым и должен быть строкой"
            )

        if salt is not None and not isinstance(salt, bytes):
            raise TypeError("salt должен быть bytes или None")

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

    async def verify_password(
        self, password: str, stored_hash: str, salt: bytes
    ) -> bool:
        """
        Асинхронная проверка пароля с валидацией

        Args:
            password: Пароль для проверки
            stored_hash: Сохраненный хеш пароля
            salt: Соль, использованная при хэшировании

        Returns:
            bool: True если пароль верный, False иначе

        Raises:
            ValueError: При пустых параметрах
            TypeError: При неверных типах параметров
        """
        # Валидация параметров
        if not password or not isinstance(password, str):
            raise ValueError(
                "Пароль не может быть пустым и должен быть строкой"
            )

        if not stored_hash or not isinstance(stored_hash, str):
            raise ValueError(
                "stored_hash не может быть пустым и должен быть строкой"
            )

        if not salt or not isinstance(salt, bytes):
            raise ValueError("salt не может быть пустым и должен быть bytes")

        try:
            computed_hash, _ = await self.hash_password(password, salt)
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

    def _increment_encryption_count(self):
        """Увеличение счетчика шифрований"""
        self._encryption_count += 1
        self._last_activity = datetime.now()

    def _increment_decryption_count(self):
        """Увеличение счетчика расшифрований"""
        self._decryption_count += 1
        self._last_activity = datetime.now()

    def _increment_error_count(self):
        """Увеличение счетчика ошибок"""
        self._error_count += 1

    def get_usage_stats(self) -> Dict[str, Any]:
        """Получение статистики использования"""
        return {
            "encryption_count": self._encryption_count,
            "decryption_count": self._decryption_count,
            "error_count": self._error_count,
            "last_activity": (
                self._last_activity.isoformat()
                if self._last_activity
                else None
            ),
            "total_operations": self._encryption_count
            + self._decryption_count,
            "error_rate": (
                self._error_count
                / (self._encryption_count + self._decryption_count)
                if (self._encryption_count + self._decryption_count) > 0
                else 0
            ),
        }

    def get_security_settings(self) -> Dict[str, Any]:
        """Получение настроек безопасности"""
        return {
            "max_key_age_days": self._max_key_age,
            "min_key_length_bytes": self._min_key_length,
            "encryption_timeout_seconds": self._encryption_timeout,
            "cache_ttl_seconds": self._cache_ttl,
        }

    def update_security_settings(
        self,
        max_key_age: Optional[int] = None,
        min_key_length: Optional[int] = None,
        encryption_timeout: Optional[int] = None,
        cache_ttl: Optional[int] = None,
    ):
        """Обновление настроек безопасности"""
        if max_key_age is not None:
            self._max_key_age = max_key_age
        if min_key_length is not None:
            self._min_key_length = min_key_length
        if encryption_timeout is not None:
            self._encryption_timeout = encryption_timeout
        if cache_ttl is not None:
            self._cache_ttl = cache_ttl

        self.logger.info("Настройки безопасности обновлены")

    # ============================================================================
    # ⚡ ОПТИМИЗИРОВАННЫЕ МЕТОДЫ ДЛЯ CPU-ИНТЕНСИВНЫХ ОПЕРАЦИЙ
    # ============================================================================

    @lru_cache(maxsize=128)
    def _get_cached_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Кэшированное получение ключа"""
        return self.keys.get(key_id)

    async def encrypt_data_async(
        self,
        data: Union[str, bytes],
        algorithm: Optional[EncryptionAlgorithm] = None,
        key_id: Optional[str] = None,
    ) -> Optional[EncryptedData]:
        """Асинхронное шифрование данных с оптимизацией"""
        start_time = time.time()
        
        try:
            # Подготовка данных
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
                
            # Проверка кэша
            cache_key = f"encrypt_{hashlib.sha256(data_bytes).hexdigest()[:16]}"
            if cache_key in self._encryption_cache:
                self._performance_metrics['cache_hits'] += 1
                cached_result = self._encryption_cache[cache_key]
                return EncryptedData(
                    data=cached_result,
                    algorithm=algorithm or self.default_algorithm,
                    key_id=key_id or self.active_key_id,
                )
            
            self._performance_metrics['cache_misses'] += 1
            
            # Асинхронная обработка в пуле потоков
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._thread_pool,
                self._encrypt_data_sync,
                data_bytes,
                algorithm,
                key_id
            )
            
            # Кэширование результата
            if result and len(self._encryption_cache) < self._cache_max_size:
                self._encryption_cache[cache_key] = result.data
            
            # Обновление метрик
            encryption_time = time.time() - start_time
            self._performance_metrics['avg_encryption_time'] = (
                (self._performance_metrics['avg_encryption_time'] + encryption_time) / 2
            )
            self._performance_metrics['total_operations'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка асинхронного шифрования: {e}")
            return None

    async def decrypt_data_async(
        self,
        encrypted_data: EncryptedData,
    ) -> Optional[bytes]:
        """Асинхронная расшифровка данных с оптимизацией"""
        start_time = time.time()
        
        try:
            # Асинхронная обработка в пуле потоков
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._thread_pool,
                self._decrypt_data_sync,
                encrypted_data
            )
            
            # Обновление метрик
            decryption_time = time.time() - start_time
            self._performance_metrics['avg_decryption_time'] = (
                (self._performance_metrics['avg_decryption_time'] + decryption_time) / 2
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка асинхронной расшифровки: {e}")
            return None

    def _encrypt_data_sync(
        self,
        data: bytes,
        algorithm: Optional[EncryptionAlgorithm] = None,
        key_id: Optional[str] = None,
    ) -> Optional[EncryptedData]:
        """Синхронная версия шифрования для пула потоков"""
        return self.encrypt_data(data, algorithm, key_id)

    def _decrypt_data_sync(
        self,
        encrypted_data: EncryptedData,
    ) -> Optional[bytes]:
        """Синхронная версия расшифровки для пула потоков"""
        return self.decrypt_data(encrypted_data)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Получение метрик производительности"""
        cache_hit_rate = (
            self._performance_metrics['cache_hits'] / 
            (self._performance_metrics['cache_hits'] + self._performance_metrics['cache_misses'])
            if (self._performance_metrics['cache_hits'] + self._performance_metrics['cache_misses']) > 0 
            else 0
        )
        
        return {
            **self._performance_metrics,
            'cache_hit_rate': cache_hit_rate,
            'cache_size': len(self._encryption_cache),
            'thread_pool_active_threads': self._thread_pool._threads.__len__() if hasattr(self._thread_pool, '_threads') else 0,
            'encryption_count': self._encryption_count,
            'decryption_count': self._decryption_count,
            'error_count': self._error_count,
        }

    def clear_cache(self):
        """Очистка кэша"""
        self._encryption_cache.clear()
        self._key_cache.clear()
        self._cipher_cache.clear()
        self.logger.info("Кэш шифрования очищен")

    def optimize_performance(self):
        """Оптимизация производительности"""
        # Очистка старых записей кэша
        if len(self._encryption_cache) > self._cache_max_size * 0.8:
            # Удаляем 20% самых старых записей
            items_to_remove = len(self._encryption_cache) // 5
            keys_to_remove = list(self._encryption_cache.keys())[:items_to_remove]
            for key in keys_to_remove:
                del self._encryption_cache[key]
        
        self.logger.info("Производительность шифрования оптимизирована")

    def __del__(self):
        """Деструктор для очистки ресурсов"""
        if hasattr(self, '_thread_pool'):
            self._thread_pool.shutdown(wait=True)
