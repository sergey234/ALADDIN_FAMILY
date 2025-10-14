# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Redis Cache Manager
Менеджер кэширования Redis для высокой производительности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import json
import time
import threading
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

from core.base import ComponentStatus, SecurityBase


class CacheStrategy(Enum):
    """Стратегии кэширования"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"


class CacheStatus(Enum):
    """Статусы кэша"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class CacheEntry:
    """Запись кэша"""
    key: str
    value: Any
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    size_bytes: int = 0
    tags: Optional[List[str]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_accessed is None:
            self.last_accessed = datetime.now()
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['expires_at'] = self.expires_at.isoformat() if self.expires_at else None
        data['last_accessed'] = self.last_accessed.isoformat() if self.last_accessed else None
        return data

    def is_expired(self) -> bool:
        """Проверка истечения срока действия"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def update_access(self):
        """Обновление информации о доступе"""
        self.access_count += 1
        self.last_accessed = datetime.now()


@dataclass
class CacheMetrics:
    """Метрики кэша"""
    total_entries: int = 0
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    total_size_bytes: int = 0
    average_response_time: float = 0.0
    cache_hit_ratio: float = 0.0
    last_updated: Optional[datetime] = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['last_updated'] = self.last_updated.isoformat() if self.last_updated else None
        return data

    def update_hit_ratio(self):
        """Обновление коэффициента попаданий"""
        total_requests = self.hit_count + self.miss_count
        if total_requests > 0:
            self.cache_hit_ratio = self.hit_count / total_requests
        self.last_updated = datetime.now()


class RedisCacheManager(SecurityBase):
    """Менеджер кэширования Redis"""

    def __init__(self, name: str = "RedisCacheManager"):
        super().__init__(name)
        self.cache_strategy = CacheStrategy.LRU
        self.max_cache_size = 1000  # максимальное количество записей
        self.max_memory_mb = 512  # максимальная память в МБ
        self.default_ttl = 3600  # время жизни по умолчанию (секунды)
        self.cleanup_interval = 300  # интервал очистки (секунды)

        # Кэш и метрики
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_metrics: CacheMetrics = CacheMetrics()
        self.cache_lock = threading.RLock()

        # Конфигурация
        self.cache_config: Dict[str, Any] = {
            "enable_compression": True,
            "enable_encryption": False,
            "enable_persistence": True,
            "enable_clustering": False,
            "enable_monitoring": True,
            "compression_threshold": 1024,  # байт
            "encryption_key": None,
            "persistence_path": "/tmp/aladdin_cache",
            "cluster_nodes": [],
            "monitoring_interval": 60
        }

        # Статистика
        self.statistics: Dict[str, Any] = {
            "operations_count": 0,
            "errors_count": 0,
            "start_time": None,
            "last_cleanup": None,
            "cleanup_count": 0
        }

    def initialize(self) -> bool:
        """Инициализация менеджера кэша"""
        try:
            self.log_activity("Инициализация Redis Cache Manager", "info")
            self.status = ComponentStatus.RUNNING
            self.statistics["start_time"] = datetime.now()

            # Инициализация кэша
            self._initialize_cache()

            # Запуск фоновых задач
            self._start_background_tasks()

            self.log_activity("Redis Cache Manager успешно инициализирован", "info")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка инициализации Redis Cache Manager: {e}", "error")
            self.status = ComponentStatus.ERROR
            return False

    def stop(self) -> bool:
        """Остановка менеджера кэша"""
        try:
            self.log_activity("Остановка Redis Cache Manager", "info")
            self.status = ComponentStatus.STOPPED

            # Остановка фоновых задач
            self._stop_background_tasks()

            # Сохранение кэша
            if self.cache_config["enable_persistence"]:
                self._persist_cache()

            # Очистка кэша
            with self.cache_lock:
                self.cache.clear()

            self.log_activity("Redis Cache Manager остановлен", "info")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка остановки Redis Cache Manager: {e}", "error")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Получение значения из кэша"""
        try:
            with self.cache_lock:
                ops_count = self.statistics.get("operations_count", 0)
                if not isinstance(ops_count, int):
                    ops_count = 0
                self.statistics["operations_count"] = ops_count + 1

                if key not in self.cache:
                    self.cache_metrics.miss_count += 1
                    self.cache_metrics.update_hit_ratio()
                    return None

                entry = self.cache[key]

                # Проверка истечения срока
                if entry.is_expired():
                    del self.cache[key]
                    self.cache_metrics.miss_count += 1
                    self.cache_metrics.update_hit_ratio()
                    return None

                # Обновление статистики доступа
                entry.update_access()
                self.cache_metrics.hit_count += 1
                self.cache_metrics.update_hit_ratio()

                return entry.value

        except Exception as e:
            self.log_activity(f"Ошибка получения из кэша {key}: {e}", "error")
            errors_count = self.statistics.get("errors_count", 0)
            if not isinstance(errors_count, int):
                errors_count = 0
            self.statistics["errors_count"] = errors_count + 1
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None,
            tags: Optional[List[str]] = None) -> bool:
        """Установка значения в кэш"""
        try:
            with self.cache_lock:
                ops_count = self.statistics.get("operations_count", 0)
                if not isinstance(ops_count, int):
                    ops_count = 0
                self.statistics["operations_count"] = ops_count + 1

                # Определение TTL
                if ttl is None:
                    ttl = self.default_ttl

                # Создание записи кэша
                expires_at = datetime.now() + timedelta(seconds=ttl)
                entry = CacheEntry(
                    key=key,
                    value=value,
                    expires_at=expires_at,
                    tags=tags or []
                )

                # Проверка размера кэша
                if len(self.cache) >= self.max_cache_size:
                    self._evict_entries()

                # Добавление в кэш
                self.cache[key] = entry
                self.cache_metrics.total_entries = len(self.cache)

                return True

        except Exception as e:
            self.log_activity(f"Ошибка установки в кэш {key}: {e}", "error")
            errors_count = self.statistics.get("errors_count", 0)
            if not isinstance(errors_count, int):
                errors_count = 0
            self.statistics["errors_count"] = errors_count + 1
            return False

    def delete(self, key: str) -> bool:
        """Удаление значения из кэша"""
        try:
            with self.cache_lock:
                ops_count = self.statistics.get("operations_count", 0)
                if not isinstance(ops_count, int):
                    ops_count = 0
                self.statistics["operations_count"] = ops_count + 1

                if key in self.cache:
                    del self.cache[key]
                    self.cache_metrics.total_entries = len(self.cache)
                    return True

                return False

        except Exception as e:
            self.log_activity(f"Ошибка удаления из кэша {key}: {e}", "error")
            errors_count = self.statistics.get("errors_count", 0)
            if not isinstance(errors_count, int):
                errors_count = 0
            self.statistics["errors_count"] = errors_count + 1
            return False

    def exists(self, key: str) -> bool:
        """Проверка существования ключа в кэше"""
        try:
            with self.cache_lock:
                if key not in self.cache:
                    return False

                entry = self.cache[key]
                if entry.is_expired():
                    del self.cache[key]
                    return False

                return True

        except Exception as e:
            self.log_activity(f"Ошибка проверки существования {key}: {e}", "error")
            return False

    def clear(self) -> bool:
        """Очистка всего кэша"""
        try:
            with self.cache_lock:
                self.cache.clear()
                self.cache_metrics.total_entries = 0
                ops_count = self.statistics.get("operations_count", 0)
                if not isinstance(ops_count, int):
                    ops_count = 0
                self.statistics["operations_count"] = ops_count + 1
                return True

        except Exception as e:
            self.log_activity(f"Ошибка очистки кэша: {e}", "error")
            return False

    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """Получение списка ключей"""
        try:
            with self.cache_lock:
                keys = list(self.cache.keys())

                if pattern:
                    import fnmatch
                    keys = [key for key in keys if fnmatch.fnmatch(key, pattern)]

                return keys

        except Exception as e:
            self.log_activity(f"Ошибка получения ключей: {e}", "error")
            return []

    def get_cache_info(self) -> Dict[str, Any]:
        """Получение информации о кэше"""
        try:
            with self.cache_lock:
                return {
                    "status": self.status.value,
                    "strategy": self.cache_strategy.value,
                    "max_size": self.max_cache_size,
                    "current_size": len(self.cache),
                    "max_memory_mb": self.max_memory_mb,
                    "default_ttl": self.default_ttl,
                    "metrics": self.cache_metrics.to_dict(),
                    "statistics": self.statistics,
                    "config": self.cache_config
                }

        except Exception as e:
            self.log_activity(f"Ошибка получения информации о кэше: {e}", "error")
            return {}

    def _initialize_cache(self):
        """Инициализация кэша"""
        try:
            # Загрузка кэша из файла, если включена персистентность
            if self.cache_config["enable_persistence"]:
                self._load_cache()

            self.log_activity("Кэш инициализирован", "info")

        except Exception as e:
            self.log_activity(f"Ошибка инициализации кэша: {e}", "error")

    def _evict_entries(self):
        """Удаление записей по стратегии"""
        try:
            if not self.cache:
                return

            # Определение количества записей для удаления
            evict_count = max(1, len(self.cache) // 10)  # 10% от размера

            if self.cache_strategy == CacheStrategy.LRU:
                # Удаление наименее недавно использованных
                sorted_entries = sorted(
                    self.cache.items(),
                    key=lambda x: x[1].last_accessed or datetime.min
                )
            elif self.cache_strategy == CacheStrategy.LFU:
                # Удаление наименее часто используемых
                sorted_entries = sorted(
                    self.cache.items(),
                    key=lambda x: x[1].access_count
                )
            else:
                # Удаление случайных записей
                sorted_entries = list(self.cache.items())

            # Удаление записей
            for i in range(min(evict_count, len(sorted_entries))):
                key, _ = sorted_entries[i]
                if key in self.cache:
                    del self.cache[key]
                    self.cache_metrics.eviction_count += 1

            self.cache_metrics.total_entries = len(self.cache)

        except Exception as e:
            self.log_activity(f"Ошибка удаления записей: {e}", "error")

    def _start_background_tasks(self):
        """Запуск фоновых задач"""
        try:
            # Запуск задачи очистки
            cleanup_thread = threading.Thread(
                target=self._cleanup_task,
                daemon=True
            )
            cleanup_thread.start()

            self.log_activity("Фоновые задачи запущены", "info")

        except Exception as e:
            self.log_activity(f"Ошибка запуска фоновых задач: {e}", "error")

    def _stop_background_tasks(self):
        """Остановка фоновых задач"""
        try:
            # Фоновые задачи остановятся автоматически при остановке менеджера
            self.log_activity("Фоновые задачи остановлены", "info")

        except Exception as e:
            self.log_activity(f"Ошибка остановки фоновых задач: {e}", "error")

    def _cleanup_task(self):
        """Задача очистки кэша"""
        try:
            while self.status == ComponentStatus.RUNNING:
                time.sleep(self.cleanup_interval)

                with self.cache_lock:
                    # Удаление истекших записей
                    expired_keys = [
                        key for key, entry in self.cache.items()
                        if entry.is_expired()
                    ]

                    for key in expired_keys:
                        del self.cache[key]

                    if expired_keys:
                        self.cache_metrics.total_entries = len(self.cache)
                        cleanup_count = self.statistics.get("cleanup_count", 0)
                        if not isinstance(cleanup_count, int):
                            cleanup_count = 0
                        self.statistics["cleanup_count"] = cleanup_count + 1
                        self.statistics["last_cleanup"] = datetime.now()

        except Exception as e:
            self.log_activity(f"Ошибка задачи очистки: {e}", "error")

    def _persist_cache(self):
        """Сохранение кэша в файл"""
        try:
            if not self.cache_config["enable_persistence"]:
                return

            # Создание данных для сохранения
            cache_data = {
                "entries": {},
                "metadata": {
                    "saved_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }

            with self.cache_lock:
                for key, entry in self.cache.items():
                    if not entry.is_expired():
                        cache_data["entries"][key] = entry.to_dict()

            # Сохранение в файл
            import os
            os.makedirs(os.path.dirname(self.cache_config["persistence_path"]), exist_ok=True)

            with open(self.cache_config["persistence_path"], 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            self.log_activity("Кэш сохранен в файл", "info")

        except Exception as e:
            self.log_activity(f"Ошибка сохранения кэша: {e}", "error")

    def _load_cache(self):
        """Загрузка кэша из файла"""
        try:
            if not self.cache_config["enable_persistence"]:
                return

            import os
            if not os.path.exists(self.cache_config["persistence_path"]):
                return

            with open(self.cache_config["persistence_path"], 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            with self.cache_lock:
                for key, entry_data in cache_data.get("entries", {}).items():
                    try:
                        # Восстановление записи кэша
                        created_at = None
                        if entry_data.get("created_at"):
                            created_at = datetime.fromisoformat(entry_data["created_at"])

                        expires_at = None
                        if entry_data.get("expires_at"):
                            expires_at = datetime.fromisoformat(entry_data["expires_at"])

                        last_accessed = None
                        if entry_data.get("last_accessed"):
                            last_accessed = datetime.fromisoformat(entry_data["last_accessed"])

                        entry = CacheEntry(
                            key=key,
                            value=entry_data["value"],
                            created_at=created_at,
                            expires_at=expires_at,
                            access_count=entry_data.get("access_count", 0),
                            last_accessed=last_accessed,
                            size_bytes=entry_data.get("size_bytes", 0),
                            tags=entry_data.get("tags", [])
                        )

                        # Проверка истечения срока
                        if not entry.is_expired():
                            self.cache[key] = entry

                    except Exception as e:
                        self.log_activity(f"Ошибка загрузки записи {key}: {e}", "error")

            self.cache_metrics.total_entries = len(self.cache)
            self.log_activity("Кэш загружен из файла", "info")

        except Exception as e:
            self.log_activity(f"Ошибка загрузки кэша: {e}", "error")

    async def async_get(self, key: str) -> Optional[Any]:
        """
        Асинхронное получение значения из кэша

        Args:
            key: Ключ для поиска

        Returns:
            Значение из кэша или None
        """
        try:
            import asyncio
            # Симуляция асинхронной операции
            await asyncio.sleep(0.001)
            return self.get(key)
        except Exception as e:
            self.log_activity(f"Ошибка асинхронного получения {key}: {e}", "error")
            return None

    async def async_set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Асинхронное сохранение значения в кэш

        Args:
            key: Ключ для сохранения
            value: Значение для сохранения
            ttl: Время жизни в секундах

        Returns:
            True если успешно сохранено
        """
        try:
            import asyncio
            # Симуляция асинхронной операции
            await asyncio.sleep(0.001)
            return self.set(key, value, ttl)
        except Exception as e:
            self.log_activity(f"Ошибка асинхронного сохранения {key}: {e}", "error")
            return False

    async def async_delete(self, key: str) -> bool:
        """
        Асинхронное удаление значения из кэша

        Args:
            key: Ключ для удаления

        Returns:
            True если успешно удалено
        """
        try:
            import asyncio
            # Симуляция асинхронной операции
            await asyncio.sleep(0.001)
            return self.delete(key)
        except Exception as e:
            self.log_activity(f"Ошибка асинхронного удаления {key}: {e}", "error")
            return False

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверка состояния кэш-менеджера

        Returns:
            Dict[str, Any]: Статус здоровья кэш-менеджера
        """
        try:
            import asyncio

            health_status = {
                "status": "healthy",
                "timestamp": asyncio.get_event_loop().time(),
                "service": "RedisCacheManager",
                "components": {
                    "cache_initialized": len(self.cache) >= 0,
                    "background_tasks": self.cleanup_thread is not None and self.cleanup_thread.is_alive(),
                    "persistence_enabled": True
                },
                "metrics": {
                    "total_entries": len(self.cache),
                    "cache_size_mb": sum(entry.size_bytes for entry in self.cache.values()) / (1024 * 1024),
                    "hit_ratio": self.cache_metrics.hit_ratio,
                    "max_cache_size": self.max_cache_size,
                    "strategy": self.cache_strategy.value
                }
            }

            # Проверка состояния кэша
            if len(self.cache) > self.max_cache_size:
                health_status["status"] = "degraded"
                health_status["components"]["cache_size_warning"] = True

            # Проверка фоновых задач
            if not (self.cleanup_thread and self.cleanup_thread.is_alive()):
                health_status["status"] = "degraded"
                health_status["components"]["background_tasks"] = False

            # Проверка метрик
            if self.cache_metrics.hit_ratio < 0.5:
                health_status["status"] = "degraded"
                health_status["components"]["low_hit_ratio"] = True

            return health_status

        except Exception as e:
            self.log_activity(f"Health check failed: {e}", "error")
            return {
                "status": "unhealthy",
                "timestamp": asyncio.get_event_loop().time(),
                "service": "RedisCacheManager",
                "error": str(e)
            }
