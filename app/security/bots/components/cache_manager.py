# -*- coding: utf-8 -*-
"""
Менеджер кэширования для ParentalControlBot
Версия: 2.5
Дата: 2025-09-21
"""

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class CacheStrategy(Enum):
    """Стратегии кэширования"""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    FIFO = "fifo"  # First In First Out


@dataclass
class CacheEntry:
    """Запись кэша"""

    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl: Optional[timedelta] = None
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Проверка истечения срока действия"""
        if self.ttl is None:
            return False
        return datetime.now() - self.created_at > self.ttl

    def update_access(self):
        """Обновление информации о доступе"""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class CacheStats:
    """Статистика кэша"""

    total_entries: int = 0
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    total_size_bytes: int = 0
    hit_ratio: float = 0.0

    def calculate_hit_ratio(self):
        """Расчет коэффициента попаданий"""
        total_requests = self.hit_count + self.miss_count
        if total_requests > 0:
            self.hit_ratio = self.hit_count / total_requests
        else:
            self.hit_ratio = 0.0


class CacheManager:
    """Менеджер кэширования"""

    def __init__(
        self,
        logger: logging.Logger,
        max_size: int = 1000,
        max_memory_mb: int = 100,
        strategy: CacheStrategy = CacheStrategy.LRU,
        default_ttl: Optional[timedelta] = None,
    ):
        self.logger = logger
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.strategy = strategy
        self.default_ttl = default_ttl

        self.cache: Dict[str, CacheEntry] = {}
        self.stats = CacheStats()
        self._lock = asyncio.Lock()

        # Для LRU/LFU стратегий
        self._access_order: List[str] = []
        self._frequency: Dict[str, int] = {}

    async def get(self, key: str) -> Optional[Any]:
        """Получение значения из кэша"""
        try:
            async with self._lock:
                if key not in self.cache:
                    self.stats.miss_count += 1
                    return None

                entry = self.cache[key]

                # Проверка истечения срока
                if entry.is_expired():
                    await self._remove_entry(key)
                    self.stats.miss_count += 1
                    return None

                # Обновление информации о доступе
                entry.update_access()
                self._update_access_tracking(key)

                self.stats.hit_count += 1
                self.stats.calculate_hit_ratio()

                return entry.value

        except Exception as e:
            self.logger.error(f"Ошибка получения из кэша: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None,
        size_bytes: Optional[int] = None,
    ) -> bool:
        """Установка значения в кэш"""
        try:
            async with self._lock:
                # Расчет размера
                if size_bytes is None:
                    size_bytes = self._calculate_size(value)

                # Проверка лимитов
                if not await self._check_limits(key, size_bytes):
                    return False

                # Создание записи
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=datetime.now(),
                    last_accessed=datetime.now(),
                    ttl=ttl or self.default_ttl,
                    size_bytes=size_bytes,
                )

                # Удаление существующей записи если есть
                if key in self.cache:
                    await self._remove_entry(key)

                # Добавление новой записи
                self.cache[key] = entry
                self._update_access_tracking(key)

                # Обновление статистики
                self.stats.total_entries = len(self.cache)
                self.stats.total_size_bytes += size_bytes

                return True

        except Exception as e:
            self.logger.error(f"Ошибка установки в кэш: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Удаление значения из кэша"""
        try:
            async with self._lock:
                if key in self.cache:
                    await self._remove_entry(key)
                    return True
                return False

        except Exception as e:
            self.logger.error(f"Ошибка удаления из кэша: {e}")
            return False

    async def clear(self) -> bool:
        """Очистка всего кэша"""
        try:
            async with self._lock:
                self.cache.clear()
                self._access_order.clear()
                self._frequency.clear()

                # Сброс статистики
                self.stats = CacheStats()

                self.logger.info("Кэш очищен")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка очистки кэша: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Проверка существования ключа в кэше"""
        try:
            async with self._lock:
                if key not in self.cache:
                    return False

                entry = self.cache[key]
                if entry.is_expired():
                    await self._remove_entry(key)
                    return False

                return True

        except Exception as e:
            self.logger.error(f"Ошибка проверки существования в кэше: {e}")
            return False

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[timedelta] = None,
    ) -> Any:
        """Получение значения или создание через фабрику"""
        try:
            # Попытка получить из кэша
            value = await self.get(key)
            if value is not None:
                return value

            # Создание нового значения
            value = factory()

            # Сохранение в кэш
            await self.set(key, value, ttl)

            return value

        except Exception as e:
            self.logger.error(f"Ошибка get_or_set: {e}")
            return factory()

    async def invalidate_pattern(self, pattern: str) -> int:
        """Инвалидация ключей по паттерну"""
        try:
            async with self._lock:
                import fnmatch

                keys_to_remove = []
                for key in self.cache.keys():
                    if fnmatch.fnmatch(key, pattern):
                        keys_to_remove.append(key)

                for key in keys_to_remove:
                    await self._remove_entry(key)

                self.logger.info(
                    f"Инвалидировано {len(keys_to_remove)} ключей "
                    f"по паттерну: {pattern}"
                )
                return len(keys_to_remove)

        except Exception as e:
            self.logger.error(f"Ошибка инвалидации по паттерну: {e}")
            return 0

    async def get_stats(self) -> CacheStats:
        """Получение статистики кэша"""
        self.stats.total_entries = len(self.cache)
        self.stats.calculate_hit_ratio()
        return self.stats

    async def cleanup_expired(self) -> int:
        """Очистка истекших записей"""
        try:
            async with self._lock:
                expired_keys = []
                for key, entry in self.cache.items():
                    if entry.is_expired():
                        expired_keys.append(key)

                for key in expired_keys:
                    await self._remove_entry(key)

                if expired_keys:
                    self.logger.info(
                        f"Очищено {len(expired_keys)} истекших записей"
                    )

                return len(expired_keys)

        except Exception as e:
            self.logger.error(f"Ошибка очистки истекших записей: {e}")
            return 0

    def _calculate_size(self, value: Any) -> int:
        """Расчет размера значения в байтах"""
        try:
            if isinstance(value, str):
                return len(value.encode("utf-8"))
            elif isinstance(value, (int, float, bool)):
                return 8  # Примерный размер
            elif isinstance(value, (list, dict)):
                return len(
                    json.dumps(value, ensure_ascii=False).encode("utf-8")
                )
            else:
                return len(str(value).encode("utf-8"))
        except Exception:
            return 1024  # Размер по умолчанию

    async def _check_limits(self, key: str, size_bytes: int) -> bool:
        """Проверка лимитов кэша"""
        # Проверка лимита по количеству записей
        if len(self.cache) >= self.max_size:
            await self._evict_entries()

        # Проверка лимита по памяти
        if self.stats.total_size_bytes + size_bytes > self.max_memory_bytes:
            await self._evict_entries()

        return True

    async def _evict_entries(self):
        """Вытеснение записей из кэша"""
        if not self.cache:
            return

        if self.strategy == CacheStrategy.LRU:
            await self._evict_lru()
        elif self.strategy == CacheStrategy.LFU:
            await self._evict_lfu()
        elif self.strategy == CacheStrategy.FIFO:
            await self._evict_fifo()
        else:  # TTL
            await self._evict_ttl()

    async def _evict_lru(self):
        """Вытеснение по LRU"""
        # Сортируем по времени последнего доступа
        sorted_entries = sorted(
            self.cache.items(), key=lambda x: x[1].last_accessed
        )

        # Удаляем 10% самых старых записей
        to_remove = max(1, len(sorted_entries) // 10)
        for key, _ in sorted_entries[:to_remove]:
            await self._remove_entry(key)

    async def _evict_lfu(self):
        """Вытеснение по LFU"""
        # Сортируем по частоте доступа
        sorted_entries = sorted(
            self.cache.items(), key=lambda x: x[1].access_count
        )

        # Удаляем 10% самых редко используемых записей
        to_remove = max(1, len(sorted_entries) // 10)
        for key, _ in sorted_entries[:to_remove]:
            await self._remove_entry(key)

    async def _evict_fifo(self):
        """Вытеснение по FIFO"""
        # Удаляем самые старые записи
        sorted_entries = sorted(
            self.cache.items(), key=lambda x: x[1].created_at
        )

        to_remove = max(1, len(sorted_entries) // 10)
        for key, _ in sorted_entries[:to_remove]:
            await self._remove_entry(key)

    async def _evict_ttl(self):
        """Вытеснение по TTL"""
        # Удаляем истекшие записи
        expired_keys = []
        for key, entry in self.cache.items():
            if entry.is_expired():
                expired_keys.append(key)

        for key in expired_keys:
            await self._remove_entry(key)

    async def _remove_entry(self, key: str):
        """Удаление записи из кэша"""
        if key in self.cache:
            entry = self.cache[key]
            self.stats.total_size_bytes -= entry.size_bytes
            del self.cache[key]

            # Удаление из отслеживания доступа
            if key in self._access_order:
                self._access_order.remove(key)
            if key in self._frequency:
                del self._frequency[key]

            self.stats.eviction_count += 1

    def _update_access_tracking(self, key: str):
        """Обновление отслеживания доступа"""
        # Для LRU
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        # Для LFU
        self._frequency[key] = self._frequency.get(key, 0) + 1

    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Генерация ключа кэша"""
        # Создание строки из аргументов
        key_parts = [prefix]

        for arg in args:
            if isinstance(arg, (dict, list)):
                key_parts.append(json.dumps(arg, sort_keys=True))
            else:
                key_parts.append(str(arg))

        for k, v in sorted(kwargs.items()):
            if isinstance(v, (dict, list)):
                key_parts.append(f"{k}={json.dumps(v, sort_keys=True)}")
            else:
                key_parts.append(f"{k}={v}")

        # Создание хэша
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    async def get_memory_usage(self) -> Dict[str, Any]:
        """Получение информации об использовании памяти"""
        return {
            "total_entries": len(self.cache),
            "total_size_bytes": self.stats.total_size_bytes,
            "max_memory_bytes": self.max_memory_bytes,
            "memory_usage_percent": (
                self.stats.total_size_bytes / self.max_memory_bytes
            )
            * 100,
            "average_entry_size": self.stats.total_size_bytes
            / max(1, len(self.cache)),
        }
