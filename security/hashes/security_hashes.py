#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Hashes System - Оптимизированная система хеширования безопасности
SHA-256, SHA-512, BLAKE2, и другие алгоритмы хеширования с кэшированием

Функция: Security Hashes System
Приоритет: ВЫСОКИЙ
Версия: 2.0 (Оптимизированная)
Дата: 2025-01-11
"""

import asyncio
import hashlib
import hmac
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, Optional, Tuple, Union

# Импорт базовых классов
from core.base import ComponentStatus, SecurityBase

logger = logging.getLogger(__name__)


class HashAlgorithm(Enum):
    """Алгоритмы хеширования"""
    
    SHA_256 = "sha256"
    SHA_512 = "sha512"
    BLAKE2B = "blake2b"
    BLAKE2S = "blake2s"
    SHA3_256 = "sha3_256"
    SHA3_512 = "sha3_512"
    MD5 = "md5"  # Только для совместимости


class HashPurpose(Enum):
    """Назначение хеша"""
    
    PASSWORD = "password"
    FILE_INTEGRITY = "file_integrity"
    DATA_VERIFICATION = "data_verification"
    SECURITY_TOKEN = "security_token"
    CACHE_KEY = "cache_key"


@dataclass
class HashResult:
    """Результат хеширования"""
    
    success: bool
    hash_value: Optional[str] = None
    algorithm: Optional[HashAlgorithm] = None
    salt: Optional[bytes] = None
    iterations: Optional[int] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None


class SecurityHashesSystem(SecurityBase):
    """Оптимизированная система хеширования безопасности"""

    def __init__(
        self,
        name: str = "SecurityHashesSystem",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Конфигурация хеширования
        self.default_algorithm = HashAlgorithm.SHA_256
        self.salt_length = config.get("salt_length", 32) if config else 32
        self.iterations = config.get("iterations", 100000) if config else 100000
        
        # Статистика
        self.total_hashes = 0
        self.hash_errors = 0
        self.algorithm_usage: Dict[HashAlgorithm, int] = {}

        # ⚡ ОПТИМИЗАЦИИ CPU-ИНТЕНСИВНЫХ ФУНКЦИЙ
        # Кэш для хешей и результатов
        self._hash_cache: Dict[str, str] = {}
        self._salt_cache: Dict[str, bytes] = {}
        self._cache_max_size = config.get("cache_max_size", 2000) if config else 2000
        
        # Пул потоков для CPU-интенсивных операций
        self._thread_pool = ThreadPoolExecutor(
            max_workers=config.get("max_workers", 6) if config else 6,
            thread_name_prefix="hash_worker"
        )
        
        # Асинхронная обработка
        self._async_lock = asyncio.Lock()
        self._processing_queue = asyncio.Queue(maxsize=200)
        
        # Метрики производительности
        self._performance_metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'thread_pool_usage': 0,
            'avg_hash_time': 0.0,
            'avg_verify_time': 0.0,
            'total_operations': 0
        }

        logger.info(f"Security Hashes System инициализирован: {name}")

    @lru_cache(maxsize=256)
    def _get_cached_hash(self, data: str, algorithm: str, salt: str = "") -> Optional[str]:
        """Кэшированное получение хеша"""
        cache_key = f"{algorithm}_{hashlib.sha256(f'{data}{salt}'.encode()).hexdigest()[:16]}"
        return self._hash_cache.get(cache_key)

    async def hash_data_async(
        self,
        data: Union[str, bytes],
        algorithm: Optional[HashAlgorithm] = None,
        salt: Optional[bytes] = None,
        iterations: Optional[int] = None,
        purpose: HashPurpose = HashPurpose.DATA_VERIFICATION,
    ) -> HashResult:
        """Асинхронное хеширование данных с оптимизацией"""
        start_time = time.time()
        
        try:
            # Подготовка данных
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
                
            algorithm = algorithm or self.default_algorithm
            iterations = iterations or self.iterations
            
            # Проверка кэша
            cache_key = f"hash_{algorithm.value}_{hashlib.sha256(data_bytes).hexdigest()[:16]}"
            if cache_key in self._hash_cache:
                self._performance_metrics['cache_hits'] += 1
                cached_hash = self._hash_cache[cache_key]
                return HashResult(
                    success=True,
                    hash_value=cached_hash,
                    algorithm=algorithm,
                    salt=salt,
                    iterations=iterations,
                    processing_time=time.time() - start_time,
                )
            
            self._performance_metrics['cache_misses'] += 1
            
            # Асинхронная обработка в пуле потоков
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._thread_pool,
                self._hash_data_sync,
                data_bytes,
                algorithm,
                salt,
                iterations,
                purpose
            )
            
            # Кэширование результата
            if result.success and len(self._hash_cache) < self._cache_max_size:
                self._hash_cache[cache_key] = result.hash_value
            
            # Обновление метрик
            hash_time = time.time() - start_time
            self._performance_metrics['avg_hash_time'] = (
                (self._performance_metrics['avg_hash_time'] + hash_time) / 2
            )
            self._performance_metrics['total_operations'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка асинхронного хеширования: {e}")
            return HashResult(success=False, error_message=str(e))

    async def verify_hash_async(
        self,
        data: Union[str, bytes],
        hash_value: str,
        algorithm: HashAlgorithm,
        salt: Optional[bytes] = None,
        iterations: Optional[int] = None,
    ) -> bool:
        """Асинхронная проверка хеша с оптимизацией"""
        start_time = time.time()
        
        try:
            # Подготовка данных
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
                
            iterations = iterations or self.iterations
            
            # Асинхронная обработка в пуле потоков
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._thread_pool,
                self._verify_hash_sync,
                data_bytes,
                hash_value,
                algorithm,
                salt,
                iterations
            )
            
            # Обновление метрик
            verify_time = time.time() - start_time
            self._performance_metrics['avg_verify_time'] = (
                (self._performance_metrics['avg_verify_time'] + verify_time) / 2
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка асинхронной проверки хеша: {e}")
            return False

    def _hash_data_sync(
        self,
        data: bytes,
        algorithm: HashAlgorithm,
        salt: Optional[bytes],
        iterations: int,
        purpose: HashPurpose,
    ) -> HashResult:
        """Синхронная версия хеширования для пула потоков"""
        start_time = time.time()
        
        try:
            # Генерация соли если не предоставлена
            if salt is None:
                salt = self._generate_salt()
            
            # Хеширование в зависимости от алгоритма и назначения
            if purpose == HashPurpose.PASSWORD:
                hash_value = self._hash_password(data, salt, algorithm, iterations)
            else:
                hash_value = self._hash_data(data, algorithm, salt)
            
            # Обновление статистики
            self.total_hashes += 1
            self.algorithm_usage[algorithm] = (
                self.algorithm_usage.get(algorithm, 0) + 1
            )
            
            return HashResult(
                success=True,
                hash_value=hash_value,
                algorithm=algorithm,
                salt=salt,
                iterations=iterations,
                processing_time=time.time() - start_time,
            )
            
        except Exception as e:
            self.hash_errors += 1
            logger.error(f"Ошибка хеширования: {e}")
            return HashResult(success=False, error_message=str(e))

    def _verify_hash_sync(
        self,
        data: bytes,
        hash_value: str,
        algorithm: HashAlgorithm,
        salt: Optional[bytes],
        iterations: int,
    ) -> bool:
        """Синхронная версия проверки хеша для пула потоков"""
        try:
            # Вычисление хеша для сравнения
            if salt is not None:
                computed_hash = self._hash_password(data, salt, algorithm, iterations)
            else:
                computed_hash = self._hash_data(data, algorithm, salt)
            
            # Безопасное сравнение хешей
            return hmac.compare_digest(computed_hash, hash_value)
            
        except Exception as e:
            logger.error(f"Ошибка проверки хеша: {e}")
            return False

    def _hash_data(self, data: bytes, algorithm: HashAlgorithm, salt: Optional[bytes]) -> str:
        """Базовое хеширование данных"""
        if algorithm == HashAlgorithm.SHA_256:
            hasher = hashlib.sha256()
        elif algorithm == HashAlgorithm.SHA_512:
            hasher = hashlib.sha512()
        elif algorithm == HashAlgorithm.BLAKE2B:
            hasher = hashlib.blake2b()
        elif algorithm == HashAlgorithm.BLAKE2S:
            hasher = hashlib.blake2s()
        elif algorithm == HashAlgorithm.SHA3_256:
            hasher = hashlib.sha3_256()
        elif algorithm == HashAlgorithm.SHA3_512:
            hasher = hashlib.sha3_512()
        elif algorithm == HashAlgorithm.MD5:
            hasher = hashlib.md5()
        else:
            raise ValueError(f"Неподдерживаемый алгоритм: {algorithm.value}")
        
        # Добавление соли если предоставлена
        if salt:
            hasher.update(salt)
        hasher.update(data)
        
        return hasher.hexdigest()

    def _hash_password(self, password: bytes, salt: bytes, algorithm: HashAlgorithm, iterations: int) -> str:
        """Хеширование пароля с солью и итерациями"""
        if algorithm == HashAlgorithm.SHA_256:
            return hashlib.pbkdf2_hmac('sha256', password, salt, iterations).hex()
        elif algorithm == HashAlgorithm.SHA_512:
            return hashlib.pbkdf2_hmac('sha512', password, salt, iterations).hex()
        else:
            # Fallback к базовому хешированию
            return self._hash_data(password, algorithm, salt)

    def _generate_salt(self) -> bytes:
        """Генерация криптографически стойкой соли"""
        return hashlib.sha256(str(time.time()).encode()).digest()[:self.salt_length]

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
            'cache_size': len(self._hash_cache),
            'thread_pool_active_threads': self._thread_pool._threads.__len__() if hasattr(self._thread_pool, '_threads') else 0,
            'total_hashes': self.total_hashes,
            'hash_errors': self.hash_errors,
        }

    def clear_cache(self):
        """Очистка кэша"""
        self._hash_cache.clear()
        self._salt_cache.clear()
        logger.info("Кэш хеширования очищен")

    def optimize_performance(self):
        """Оптимизация производительности"""
        # Очистка старых записей кэша
        if len(self._hash_cache) > self._cache_max_size * 0.8:
            # Удаляем 20% самых старых записей
            items_to_remove = len(self._hash_cache) // 5
            keys_to_remove = list(self._hash_cache.keys())[:items_to_remove]
            for key in keys_to_remove:
                del self._hash_cache[key]
        
        logger.info("Производительность хеширования оптимизирована")

    def get_hash_stats(self) -> Dict[str, Any]:
        """Получение статистики хеширования"""
        return {
            'total_hashes': self.total_hashes,
            'hash_errors': self.hash_errors,
            'algorithm_usage': {alg.value: count for alg, count in self.algorithm_usage.items()},
            'performance_metrics': self.get_performance_metrics(),
        }

    def __del__(self):
        """Деструктор для очистки ресурсов"""
        if hasattr(self, '_thread_pool'):
            self._thread_pool.shutdown(wait=True)


# ============================================================================
# ТЕСТИРОВАНИЕ СИСТЕМЫ ХЕШИРОВАНИЯ
# ============================================================================

if __name__ == "__main__":
    print("🔐 ТЕСТИРОВАНИЕ СИСТЕМЫ ХЕШИРОВАНИЯ БЕЗОПАСНОСТИ")
    print("=" * 60)
    
    # Создание системы хеширования
    hash_system = SecurityHashesSystem("TestHashSystem")
    
    # Тестовые данные
    test_data = "Это тестовые данные для хеширования"
    test_password = "SecurePassword123!"
    
    print(f"📊 Тестовые данные: {test_data}")
    print(f"🔑 Тестовый пароль: {test_password}")
    
    # Тест SHA-256
    print("\n1. Тест SHA-256:")
    result = hash_system._hash_data_sync(
        test_data.encode(),
        HashAlgorithm.SHA_256,
        None,
        100000,
        HashPurpose.DATA_VERIFICATION
    )
    if result.success:
        print(f"   ✅ Хеш: {result.hash_value}")
        print(f"   ⏱️ Время: {result.processing_time:.4f} сек")
    else:
        print(f"   ❌ Ошибка: {result.error_message}")
    
    # Тест хеширования пароля
    print("\n2. Тест хеширования пароля:")
    result = hash_system._hash_data_sync(
        test_password.encode(),
        HashAlgorithm.SHA_256,
        None,
        100000,
        HashPurpose.PASSWORD
    )
    if result.success:
        print(f"   ✅ Хеш пароля: {result.hash_value}")
        print(f"   🧂 Соль: {result.salt.hex()}")
        print(f"   🔄 Итерации: {result.iterations}")
    else:
        print(f"   ❌ Ошибка: {result.error_message}")
    
    # Статистика
    print("\n3. Статистика хеширования:")
    stats = hash_system.get_hash_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"   📊 {key}:")
            for sub_key, sub_value in value.items():
                print(f"      {sub_key}: {sub_value}")
        else:
            print(f"   📊 {key}: {value}")
    
    print("\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")