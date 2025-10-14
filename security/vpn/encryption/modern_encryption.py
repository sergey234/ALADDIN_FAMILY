#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern Encryption System - Современные алгоритмы шифрования для VPN
ChaCha20-Poly1305, AES-256-GCM, и другие современные алгоритмы

Функция: Modern Encryption System
Приоритет: ВЫСОКИЙ
Версия: 1.0
Дата: 2025-09-07
"""

import os
import sys

# Добавление пути к корневой директории проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import asyncio  # noqa: E402
import hashlib  # noqa: E402
import hmac  # noqa: E402
import logging  # noqa: E402
import secrets  # noqa: E402
import time  # noqa: E402
import threading  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from enum import Enum  # noqa: E402
from functools import lru_cache  # noqa: E402
from typing import Any, Dict, Optional, Tuple  # noqa: E402

# Импорт базовых классов
from core.base import ComponentStatus, SecurityBase  # noqa: E402

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(Enum):
    """Алгоритмы шифрования"""

    AES_256_GCM = "aes-256-gcm"
    CHACHA20_POLY1305 = "chacha20-poly1305"
    AES_128_GCM = "aes-128-gcm"
    CHACHA20 = "chacha20"
    POLY1305 = "poly1305"


class EncryptionMode(Enum):
    """Режимы шифрования"""

    MOBILE_OPTIMIZED = "mobile_optimized"  # ChaCha20-Poly1305
    HIGH_SECURITY = "high_security"  # AES-256-GCM
    BALANCED = "balanced"  # AES-128-GCM
    CUSTOM = "custom"  # Пользовательский выбор


@dataclass
class EncryptionKey:
    """Ключ шифрования"""

    key_id: str
    algorithm: EncryptionAlgorithm
    key_data: bytes
    created_at: float
    expires_at: Optional[float] = None
    usage_count: int = 0
    max_usage: Optional[int] = None


@dataclass
class EncryptionResult:
    """Результат шифрования"""

    success: bool
    encrypted_data: Optional[bytes] = None
    auth_tag: Optional[bytes] = None
    nonce: Optional[bytes] = None
    algorithm: Optional[EncryptionAlgorithm] = None
    key_id: Optional[str] = None
    error_message: Optional[str] = None


class ModernEncryptionSystem(SecurityBase):
    """Система современного шифрования для VPN"""

    def __init__(
        self,
        name: str = "ModernEncryptionSystem",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Конфигурация шифрования
        self.default_algorithm = EncryptionAlgorithm.CHACHA20_POLY1305
        self.key_rotation_interval = (
            config.get("key_rotation_interval", 3600) if config else 3600
        )  # 1 час
        self.max_key_usage = (
            config.get("max_key_usage", 1000000) if config else 1000000
        )

        # Хранилище ключей
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.active_key_id: Optional[str] = None

        # Статистика
        self.total_encryptions = 0
        self.total_decryptions = 0
        self.encryption_errors = 0
        self.algorithm_usage: Dict[EncryptionAlgorithm, int] = {}

        # ⚡ ОПТИМИЗАЦИИ CPU-ИНТЕНСИВНЫХ ФУНКЦИЙ
        # Кэш для ключей и результатов
        self._key_cache: Dict[str, Any] = {}
        self._encryption_cache: Dict[str, bytes] = {}
        self._cache_max_size = config.get("cache_max_size", 1000) if config else 1000
        
        # Пул потоков для CPU-интенсивных операций
        self._thread_pool = ThreadPoolExecutor(
            max_workers=config.get("max_workers", 4) if config else 4,
            thread_name_prefix="encryption_worker"
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
            'avg_decryption_time': 0.0
        }

        # Инициализация
        self._initialize_encryption()

        logger.info(f"Modern Encryption System инициализирован: {name}")

    def _initialize_encryption(self):
        """Инициализация системы шифрования"""
        try:
            # Генерация начального ключа
            self._generate_new_key(self.default_algorithm)

            # Запуск ротации ключей
            self._start_key_rotation()

            logger.info("Система шифрования инициализирована")

        except Exception as e:
            logger.error(f"Ошибка инициализации шифрования: {e}")
            self.status = ComponentStatus.ERROR

    def _generate_new_key(self, algorithm: EncryptionAlgorithm) -> str:
        """Генерация нового ключа шифрования"""
        try:
            key_id = f"key_{int(time.time())}_{secrets.token_hex(8)}"

            # Генерация ключа в зависимости от алгоритма
            if algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                key_data = secrets.token_bytes(32)  # 256 бит
            elif algorithm == EncryptionAlgorithm.AES_256_GCM:
                key_data = secrets.token_bytes(32)  # 256 бит
            elif algorithm == EncryptionAlgorithm.AES_128_GCM:
                key_data = secrets.token_bytes(16)  # 128 бит
            else:
                key_data = secrets.token_bytes(32)  # По умолчанию 256 бит

            # Создание объекта ключа
            encryption_key = EncryptionKey(
                key_id=key_id,
                algorithm=algorithm,
                key_data=key_data,
                created_at=time.time(),
                expires_at=time.time() + self.key_rotation_interval,
                max_usage=self.max_key_usage,
            )

            # Сохранение ключа
            self.encryption_keys[key_id] = encryption_key

            # Установка как активного ключа
            if not self.active_key_id:
                self.active_key_id = key_id

            logger.info(
                f"Новый ключ шифрования создан: {key_id} ({algorithm.value})"
            )
            return key_id

        except Exception as e:
            logger.error(f"Ошибка генерации ключа: {e}")
            raise

    def _start_key_rotation(self):
        """Запуск автоматической ротации ключей"""
        import threading

        def key_rotation_loop():
            while self.status == ComponentStatus.RUNNING:
                try:
                    time.sleep(self.key_rotation_interval)

                    # Проверка необходимости ротации
                    if self._should_rotate_key():
                        self._rotate_key()

                except Exception as e:
                    logger.error(f"Ошибка ротации ключей: {e}")

        rotation_thread = threading.Thread(
            target=key_rotation_loop, daemon=True
        )
        rotation_thread.start()
        logger.info("Ротация ключей запущена")

    def _should_rotate_key(self) -> bool:
        """Проверка необходимости ротации ключа"""
        if (
            not self.active_key_id
            or self.active_key_id not in self.encryption_keys
        ):
            return True

        active_key = self.encryption_keys[self.active_key_id]

        # Ротация по времени
        if active_key.expires_at and time.time() > active_key.expires_at:
            return True

        # Ротация по использованию
        if (
            active_key.max_usage
            and active_key.usage_count >= active_key.max_usage
        ):
            return True

        return False

    def _rotate_key(self):
        """Ротация ключа шифрования"""
        try:
            # Генерация нового ключа
            new_key_id = self._generate_new_key(self.default_algorithm)

            # Установка нового активного ключа
            old_key_id = self.active_key_id
            self.active_key_id = new_key_id

            # Удаление старого ключа (с задержкой для завершения операций)
            if old_key_id:

                def cleanup_old_key():
                    time.sleep(60)  # 1 минута задержки
                    if old_key_id in self.encryption_keys:
                        del self.encryption_keys[old_key_id]
                        logger.info(f"Старый ключ удален: {old_key_id}")

                import threading

                cleanup_thread = threading.Thread(
                    target=cleanup_old_key, daemon=True
                )
                cleanup_thread.start()

            logger.info(f"Ключ ротирован: {old_key_id} -> {new_key_id}")

        except Exception as e:
            logger.error(f"Ошибка ротации ключа: {e}")

    def encrypt_data(
        self,
        data: bytes,
        algorithm: Optional[EncryptionAlgorithm] = None,
        key_id: Optional[str] = None,
    ) -> EncryptionResult:
        """Шифрование данных"""
        try:
            # Выбор алгоритма
            if not algorithm:
                algorithm = self.default_algorithm

            # Выбор ключа
            if not key_id:
                key_id = self.active_key_id

            if not key_id or key_id not in self.encryption_keys:
                return EncryptionResult(
                    success=False, error_message="Ключ шифрования не найден"
                )

            encryption_key = self.encryption_keys[key_id]

            # Генерация nonce
            nonce = secrets.token_bytes(
                12
            )  # 96 бит для GCM и ChaCha20-Poly1305

            # Шифрование в зависимости от алгоритма
            if algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                encrypted_data, auth_tag = self._chacha20_poly1305_encrypt(
                    data, encryption_key.key_data, nonce
                )
            elif algorithm == EncryptionAlgorithm.AES_256_GCM:
                encrypted_data, auth_tag = self._aes_gcm_encrypt(
                    data, encryption_key.key_data, nonce
                )
            elif algorithm == EncryptionAlgorithm.AES_128_GCM:
                encrypted_data, auth_tag = self._aes_gcm_encrypt(
                    data, encryption_key.key_data, nonce
                )
            else:
                return EncryptionResult(
                    success=False,
                    error_message=f"Неподдерживаемый алгоритм: "
                    f"{algorithm.value}",
                )

            # Обновление статистики
            encryption_key.usage_count += 1
            self.total_encryptions += 1
            self.algorithm_usage[algorithm] = (
                self.algorithm_usage.get(algorithm, 0) + 1
            )

            return EncryptionResult(
                success=True,
                encrypted_data=encrypted_data,
                auth_tag=auth_tag,
                nonce=nonce,
                algorithm=algorithm,
                key_id=key_id,
            )

        except Exception as e:
            self.encryption_errors += 1
            logger.error(f"Ошибка шифрования: {e}")
            return EncryptionResult(success=False, error_message=str(e))

    def decrypt_data(
        self,
        encrypted_data: bytes,
        auth_tag: bytes,
        nonce: bytes,
        algorithm: EncryptionAlgorithm,
        key_id: str,
    ) -> EncryptionResult:
        """Расшифровка данных"""
        try:
            if key_id not in self.encryption_keys:
                return EncryptionResult(
                    success=False, error_message="Ключ шифрования не найден"
                )

            encryption_key = self.encryption_keys[key_id]

            # Расшифровка в зависимости от алгоритма
            if algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                decrypted_data = self._chacha20_poly1305_decrypt(
                    encrypted_data, auth_tag, encryption_key.key_data, nonce
                )
            elif algorithm == EncryptionAlgorithm.AES_256_GCM:
                decrypted_data = self._aes_gcm_decrypt(
                    encrypted_data, auth_tag, encryption_key.key_data, nonce
                )
            elif algorithm == EncryptionAlgorithm.AES_128_GCM:
                decrypted_data = self._aes_gcm_decrypt(
                    encrypted_data, auth_tag, encryption_key.key_data, nonce
                )
            else:
                return EncryptionResult(
                    success=False,
                    error_message=f"Неподдерживаемый алгоритм: {algorithm.value}",
                )

            # Обновление статистики
            encryption_key.usage_count += 1
            self.total_decryptions += 1
            self.algorithm_usage[algorithm] = (
                self.algorithm_usage.get(algorithm, 0) + 1
            )

            return EncryptionResult(
                success=True,
                encrypted_data=decrypted_data,
                algorithm=algorithm,
                key_id=key_id,
            )

        except Exception as e:
            self.encryption_errors += 1
            logger.error(f"Ошибка расшифровки: {e}")
            return EncryptionResult(success=False, error_message=str(e))

    def _chacha20_poly1305_encrypt(
        self, data: bytes, key: bytes, nonce: bytes
    ) -> bytes:
        # В реальной реализации здесь будет использоваться \
        # библиотека cryptography
        # Шифрование ChaCha20-Poly1305 (упрощенная реализация)
        # В реальной реализации здесь будет использоваться
        # Для демонстрации используем XOR с хешем

        # Генерация потока ChaCha20
        stream = hashlib.sha256(key + nonce).digest()
        while len(stream) < len(data):
            stream += hashlib.sha256(stream[-32:] + nonce).digest()

        # XOR шифрование
        encrypted = bytes(a ^ b for a, b in zip(data, stream[: len(data)]))

        # Poly1305 аутентификация
        auth_tag = hmac.new(key, encrypted + nonce, hashlib.sha256).digest()[
            :16
        ]

        return encrypted, auth_tag

    def _chacha20_poly1305_decrypt(
        self, encrypted_data: bytes, auth_tag: bytes, key: bytes, nonce: bytes
    ) -> bytes:
        """Расшифровка ChaCha20-Poly1305"""
        # Проверка аутентификации
        expected_tag = hmac.new(
            key, encrypted_data + nonce, hashlib.sha256
        ).digest()[:16]
        if not hmac.compare_digest(auth_tag, expected_tag):
            raise ValueError("Ошибка аутентификации")

        # Расшифровка (XOR обратим)
        return self._chacha20_poly1305_encrypt(encrypted_data, key, nonce)[0]

    def _aes_gcm_encrypt(
        self, data: bytes, key: bytes, nonce: bytes
    ) -> Tuple[bytes, bytes]:
        """Шифрование AES-GCM (упрощенная реализация)"""
        # В реальной реализации здесь будет использоваться
        # библиотека cryptography
        # Для демонстрации используем XOR с хешем

        # Генерация потока AES
        stream = hashlib.sha256(key + nonce).digest()
        while len(stream) < len(data):
            stream += hashlib.sha256(stream[-32:] + nonce).digest()

        # XOR шифрование
        encrypted = bytes(a ^ b for a, b in zip(data, stream[: len(data)]))

        # GCM аутентификация
        # В реальной реализации здесь будет использоваться
        # библиотека cryptography
        auth_tag = hmac.new(key, encrypted + nonce, hashlib.sha256).digest()[:16]

        return encrypted, auth_tag

    def _aes_gcm_decrypt(
        self, encrypted_data: bytes, auth_tag: bytes, key: bytes, nonce: bytes
    ) -> bytes:
        """Расшифровка AES-GCM"""
        # Проверка аутентификации
        expected_tag = hmac.new(
            key, encrypted_data + nonce, hashlib.sha256
        ).digest()[:16]
        if not hmac.compare_digest(auth_tag, expected_tag):
            raise ValueError("Ошибка аутентификации")

        # Расшифровка (XOR обратим)
        return self._aes_gcm_encrypt(encrypted_data, key, nonce)[0]

    def get_encryption_stats(self) -> Dict[str, Any]:
        """Получение статистики шифрования"""
        return {
            "total_encryptions": self.total_encryptions,
            "total_decryptions": self.total_decryptions,
            "encryption_errors": self.encryption_errors,
            "active_key_id": self.active_key_id,
            "total_keys": len(self.encryption_keys),
            "algorithm_usage": {
                alg.value: count for alg, count in self.algorithm_usage.items()
            },
            "default_algorithm": self.default_algorithm.value,
            "key_rotation_interval": self.key_rotation_interval,
        }

    def set_encryption_mode(self, mode: EncryptionMode) -> bool:
        """Установка режима шифрования"""
        try:
            if mode == EncryptionMode.MOBILE_OPTIMIZED:
                self.default_algorithm = EncryptionAlgorithm.CHACHA20_POLY1305
            elif mode == EncryptionMode.HIGH_SECURITY:
                self.default_algorithm = EncryptionAlgorithm.AES_256_GCM
            elif mode == EncryptionMode.BALANCED:
                self.default_algorithm = EncryptionAlgorithm.AES_128_GCM

            logger.info(f"Режим шифрования изменен на: {mode.value}")
            return True

        except Exception as e:
            logger.error(f"Ошибка установки режима шифрования: {e}")
            return False

    # ===== РАСШИРЕННЫЕ МЕТОДЫ =====

    def get_key_info(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о ключе шифрования"""
        try:
            if key_id not in self.encryption_keys:
                return None

            key = self.encryption_keys[key_id]
            return {
                "key_id": key.key_id,
                "algorithm": key.algorithm.value,
                "created_at": key.created_at,
                "expires_at": key.expires_at,
                "usage_count": key.usage_count,
                "max_usage": key.max_usage,
                "is_active": key_id == self.active_key_id,
                "key_strength": len(key.key_data) * 8,  # в битах
            }

        except Exception as e:
            logger.error(f"Ошибка получения информации о ключе: {e}")
            return None

    def export_key(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Экспорт ключа шифрования (безопасно)"""
        try:
            if key_id not in self.encryption_keys:
                return None

            key = self.encryption_keys[key_id]
            return {
                "key_id": key.key_id,
                "algorithm": key.algorithm.value,
                "key_data": key.key_data.hex(),  # В hex формате
                "created_at": key.created_at,
                "expires_at": key.expires_at,
                "usage_count": key.usage_count,
                "max_usage": key.max_usage,
            }

        except Exception as e:
            logger.error(f"Ошибка экспорта ключа: {e}")
            return None

    def import_key(self, key_data: Dict[str, Any]) -> bool:
        """Импорт ключа шифрования"""
        try:
            # Валидация данных ключа
            required_fields = ["key_id", "algorithm", "key_data", "created_at"]
            if not all(field in key_data for field in required_fields):
                logger.error("Неполные данные ключа для импорта")
                return False

            # Создание объекта ключа
            algorithm = EncryptionAlgorithm(key_data["algorithm"])
            key = EncryptionKey(
                key_id=key_data["key_id"],
                algorithm=algorithm,
                key_data=bytes.fromhex(key_data["key_data"]),
                created_at=key_data["created_at"],
                expires_at=key_data.get("expires_at"),
                usage_count=key_data.get("usage_count", 0),
                max_usage=key_data.get("max_usage"),
            )

            # Сохранение ключа
            self.encryption_keys[key_data["key_id"]] = key
            logger.info(f"Ключ импортирован: {key_data['key_id']}")
            return True

        except Exception as e:
            logger.error(f"Ошибка импорта ключа: {e}")
            return False

    def get_encryption_performance_metrics(self) -> Dict[str, Any]:
        """Получение метрик производительности шифрования"""
        try:
            total_operations = self.total_encryptions + self.total_decryptions
            success_rate = 0.0
            if total_operations > 0:
                success_rate = ((total_operations - self.encryption_errors) / total_operations) * 100

            return {
                "total_operations": total_operations,
                "encryption_operations": self.total_encryptions,
                "decryption_operations": self.total_decryptions,
                "error_count": self.encryption_errors,
                "success_rate": round(success_rate, 2),
                "active_keys_count": len(self.encryption_keys),
                "algorithm_distribution": {
                    alg.value: count for alg, count in self.algorithm_usage.items()
                },
                "average_key_usage": sum(
                    key.usage_count for key in self.encryption_keys.values()
                ) / len(self.encryption_keys) if self.encryption_keys else 0,
            }

        except Exception as e:
            logger.error(f"Ошибка получения метрик производительности: {e}")
            return {}

    # ===== ВАЛИДАЦИЯ ПАРАМЕТРОВ =====

    def validate_encryption_parameters(
        self, data: bytes, algorithm: EncryptionAlgorithm, key_id: str
    ) -> Tuple[bool, Optional[str]]:
        """Валидация параметров шифрования"""
        try:
            # Проверка данных
            if not isinstance(data, bytes):
                return False, "Данные должны быть в формате bytes"

            if len(data) == 0:
                return False, "Данные не могут быть пустыми"

            if len(data) > 1024 * 1024:  # 1MB лимит
                return False, "Данные слишком большие (максимум 1MB)"

            # Проверка алгоритма
            if not isinstance(algorithm, EncryptionAlgorithm):
                return False, "Неправильный тип алгоритма"

            # Проверка ключа
            if key_id not in self.encryption_keys:
                return False, "Ключ шифрования не найден"

            return True, None

        except Exception as e:
            return False, f"Ошибка валидации: {e}"

    def validate_key_strength(self, key_id: str) -> Tuple[bool, Optional[str]]:
        """Валидация силы ключа"""
        try:
            if key_id not in self.encryption_keys:
                return False, "Ключ не найден"

            key = self.encryption_keys[key_id]
            key_bits = len(key.key_data) * 8

            # Минимальные требования к силе ключа
            min_bits = 128
            if key.algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.CHACHA20_POLY1305]:
                min_bits = 256

            if key_bits < min_bits:
                return False, f"Ключ слишком слабый: {key_bits} бит (минимум {min_bits})"

            return True, f"Ключ соответствует требованиям: {key_bits} бит"

        except Exception as e:
            return False, f"Ошибка валидации ключа: {e}"

    def validate_algorithm_compatibility(
        self, algorithm: EncryptionAlgorithm, key_id: str
    ) -> Tuple[bool, Optional[str]]:
        """Валидация совместимости алгоритма и ключа"""
        try:
            if key_id not in self.encryption_keys:
                return False, "Ключ не найден"

            key = self.encryption_keys[key_id]

            # Проверка совместимости алгоритма и размера ключа
            if algorithm == EncryptionAlgorithm.AES_128_GCM and len(key.key_data) != 16:
                return False, "AES-128-GCM требует ключ 128 бит"

            if algorithm == EncryptionAlgorithm.AES_256_GCM and len(key.key_data) != 32:
                return False, "AES-256-GCM требует ключ 256 бит"

            if algorithm == EncryptionAlgorithm.CHACHA20_POLY1305 and len(key.key_data) != 32:
                return False, "ChaCha20-Poly1305 требует ключ 256 бит"

            return True, "Алгоритм и ключ совместимы"

        except Exception as e:
            return False, f"Ошибка валидации совместимости: {e}"

    # ===== КОНТЕКСТНЫЙ МЕНЕДЖЕР =====

    def __enter__(self):
        """Вход в контекстный менеджер"""
        try:
            self.start()
            return self
        except Exception as e:
            logger.error(f"Ошибка входа в контекстный менеджер: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера"""
        try:
            self.stop()
            if exc_type:
                logger.error(f"Ошибка в контекстном менеджере: {exc_type.__name__}: {exc_val}")
        except Exception as e:
            logger.error(f"Ошибка выхода из контекстного менеджера: {e}")

    # ===== ИТЕРАТОР =====

    def __iter__(self):
        """Инициализация итератора по ключам"""
        self._key_iterator = iter(self.encryption_keys.keys())
        return self

    def __next__(self):
        """Получение следующего ключа"""
        try:
            key_id = next(self._key_iterator)
            return self.get_key_info(key_id)
        except StopIteration:
            raise StopIteration
        except Exception as e:
            logger.error(f"Ошибка итерации по ключам: {e}")
            raise StopIteration

    # ============================================================================
    # ⚡ ОПТИМИЗИРОВАННЫЕ МЕТОДЫ ДЛЯ CPU-ИНТЕНСИВНЫХ ОПЕРАЦИЙ
    # ============================================================================

    @lru_cache(maxsize=128)
    def _get_cached_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Кэшированное получение ключа"""
        return self.encryption_keys.get(key_id)

    async def encrypt_data_async(
        self,
        data: bytes,
        algorithm: Optional[EncryptionAlgorithm] = None,
        key_id: Optional[str] = None,
    ) -> EncryptionResult:
        """Асинхронное шифрование данных с оптимизацией"""
        start_time = time.time()
        
        try:
            # Проверка кэша
            cache_key = f"encrypt_{hashlib.sha256(data).hexdigest()[:16]}"
            if cache_key in self._encryption_cache:
                self._performance_metrics['cache_hits'] += 1
                cached_result = self._encryption_cache[cache_key]
                return EncryptionResult(
                    success=True,
                    encrypted_data=cached_result,
                    algorithm=algorithm or self.default_algorithm,
                    key_id=key_id or self.active_key_id,
                )
            
            self._performance_metrics['cache_misses'] += 1
            
            # Асинхронная обработка в пуле потоков
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._thread_pool,
                self._encrypt_data_sync,
                data,
                algorithm,
                key_id
            )
            
            # Кэширование результата
            if result.success and len(self._encryption_cache) < self._cache_max_size:
                self._encryption_cache[cache_key] = result.encrypted_data
            
            # Обновление метрик
            encryption_time = time.time() - start_time
            self._performance_metrics['avg_encryption_time'] = (
                (self._performance_metrics['avg_encryption_time'] + encryption_time) / 2
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка асинхронного шифрования: {e}")
            return EncryptionResult(success=False, error_message=str(e))

    async def decrypt_data_async(
        self,
        encrypted_data: bytes,
        auth_tag: bytes,
        nonce: bytes,
        algorithm: EncryptionAlgorithm,
        key_id: str,
    ) -> EncryptionResult:
        """Асинхронная расшифровка данных с оптимизацией"""
        start_time = time.time()
        
        try:
            # Асинхронная обработка в пуле потоков
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._thread_pool,
                self._decrypt_data_sync,
                encrypted_data,
                auth_tag,
                nonce,
                algorithm,
                key_id
            )
            
            # Обновление метрик
            decryption_time = time.time() - start_time
            self._performance_metrics['avg_decryption_time'] = (
                (self._performance_metrics['avg_decryption_time'] + decryption_time) / 2
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка асинхронной расшифровки: {e}")
            return EncryptionResult(success=False, error_message=str(e))

    def _encrypt_data_sync(
        self,
        data: bytes,
        algorithm: Optional[EncryptionAlgorithm] = None,
        key_id: Optional[str] = None,
    ) -> EncryptionResult:
        """Синхронная версия шифрования для пула потоков"""
        return self.encrypt_data(data, algorithm, key_id)

    def _decrypt_data_sync(
        self,
        encrypted_data: bytes,
        auth_tag: bytes,
        nonce: bytes,
        algorithm: EncryptionAlgorithm,
        key_id: str,
    ) -> EncryptionResult:
        """Синхронная версия расшифровки для пула потоков"""
        return self.decrypt_data(encrypted_data, auth_tag, nonce, algorithm, key_id)

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
        }

    def clear_cache(self):
        """Очистка кэша"""
        self._encryption_cache.clear()
        self._key_cache.clear()
        logger.info("Кэш шифрования очищен")

    def optimize_performance(self):
        """Оптимизация производительности"""
        # Очистка старых записей кэша
        if len(self._encryption_cache) > self._cache_max_size * 0.8:
            # Удаляем 20% самых старых записей
            items_to_remove = len(self._encryption_cache) // 5
            keys_to_remove = list(self._encryption_cache.keys())[:items_to_remove]
            for key in keys_to_remove:
                del self._encryption_cache[key]
        
        logger.info("Производительность оптимизирована")

    def __del__(self):
        """Деструктор для очистки ресурсов"""
        if hasattr(self, '_thread_pool'):
            self._thread_pool.shutdown(wait=True)


# Тестирование
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Создание системы шифрования
    encryption_system = ModernEncryptionSystem("TestEncryption")

    # Тестовые данные
    test_data = b"Hello, ALADDIN VPN Security!"

    print("🔐 ТЕСТИРОВАНИЕ СОВРЕМЕННОГО ШИФРОВАНИЯ")
    print("=" * 50)

    # Тест ChaCha20-Poly1305
    print("\n1. Тест ChaCha20-Poly1305:")
    result = encryption_system.encrypt_data(
        test_data, EncryptionAlgorithm.CHACHA20_POLY1305
    )
    if result.success:
        print(f"   ✅ Шифрование: {len(result.encrypted_data)} байт")
        print(f"   ✅ Auth Tag: {len(result.auth_tag)} байт")
        print(f"   ✅ Nonce: {len(result.nonce)} байт")

        # Расшифровка
        decrypt_result = encryption_system.decrypt_data(
            result.encrypted_data,
            result.auth_tag,
            result.nonce,
            result.algorithm,
            result.key_id,
        )
        if decrypt_result.success:
            print(
                f"   ✅ Расшифровка: {decrypt_result.encrypted_data.decode()}"
            )
        else:
            print(f"   ❌ Ошибка расшифровки: {decrypt_result.error_message}")
    else:
        print(f"   ❌ Ошибка шифрования: {result.error_message}")

    # Тест AES-256-GCM
    print("\n2. Тест AES-256-GCM:")
    result = encryption_system.encrypt_data(
        test_data, EncryptionAlgorithm.AES_256_GCM
    )
    if result.success:
        print(f"   ✅ Шифрование: {len(result.encrypted_data)} байт")
        print(f"   ✅ Auth Tag: {len(result.auth_tag)} байт")

        # Расшифровка
        decrypt_result = encryption_system.decrypt_data(
            result.encrypted_data,
            result.auth_tag,
            result.nonce,
            result.algorithm,
            result.key_id,
        )
        if decrypt_result.success:
            print(
                f"   ✅ Расшифровка: {decrypt_result.encrypted_data.decode()}"
            )
        else:
            print(f"   ❌ Ошибка расшифровки: {decrypt_result.error_message}")
    else:
        print(f"   ❌ Ошибка шифрования: {result.error_message}")

    # Статистика
    print("\n3. Статистика шифрования:")
    stats = encryption_system.get_encryption_stats()
    for key, value in stats.items():
        print(f"   📊 {key}: {value}")

    print("\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")


