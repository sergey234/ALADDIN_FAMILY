#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль кэширования для Crash Detection API
Обеспечивает Redis кэширование для оптимизации производительности
"""

import json
import logging
import time
from typing import Optional, Any, Dict
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)

# Попытка импорта Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis не установлен, используется in-memory кэш")

# In-memory кэш как fallback
_memory_cache: Dict[str, Dict[str, Any]] = {}
_cache_timestamps: Dict[str, float] = {}

# Глобальный Redis клиент (инициализируется при первом использовании)
_redis_client: Optional[Any] = None
_redis_pool: Optional[Any] = None


def get_redis_client():
    """Получение Redis клиента с connection pooling"""
    global _redis_client, _redis_pool
    
    if not REDIS_AVAILABLE:
        return None
    
    if _redis_client is None:
        try:
            # Создаем connection pool для переиспользования соединений
            _redis_pool = redis.ConnectionPool(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                max_connections=int(os.getenv("REDIS_POOL_SIZE", 10)),
                decode_responses=True
            )
            _redis_client = redis.Redis(connection_pool=_redis_pool)
            
            # Проверка соединения
            _redis_client.ping()
            logger.info("✅ Redis подключен для кэширования Crash Detection")
            return _redis_client
        except Exception as e:
            logger.warning(f"⚠️ Redis недоступен, используется in-memory кэш: {e}")
            return None
    
    return _redis_client


def get_cache_key(endpoint: str, **kwargs) -> str:
    """Генерация ключа кэша"""
    if kwargs:
        # Создаем хэш из параметров для уникальности
        params_hash = hash(tuple(sorted(kwargs.items())))
        return f"crash_detection:{endpoint}:{params_hash}"
    return f"crash_detection:{endpoint}"


def get_cached(key: str, ttl: int = 2) -> Optional[Any]:
    """
    Получение значения из кэша
    
    Args:
        key: Ключ кэша
        ttl: Время жизни кэша в секундах
    
    Returns:
        Кэшированное значение или None
    """
    redis_client = get_redis_client()
    
    # Пробуем Redis
    if redis_client:
        try:
            cached_data = redis_client.get(key)
            if cached_data:
                logger.debug(f"✅ Cache HIT (Redis): {key}")
                return json.loads(cached_data)
            else:
                logger.debug(f"❌ Cache MISS (Redis): {key}")
        except Exception as e:
            logger.warning(f"Ошибка чтения из Redis: {e}")
    
    # Fallback на in-memory кэш
    if key in _memory_cache:
        cache_time = _cache_timestamps.get(key, 0)
        if time.time() - cache_time < ttl:
            logger.debug(f"✅ Cache HIT (Memory): {key}")
            return _memory_cache[key]
        else:
            # Удаляем устаревший кэш
            del _memory_cache[key]
            del _cache_timestamps[key]
    
    logger.debug(f"❌ Cache MISS (Memory): {key}")
    return None


def set_cached(key: str, value: Any, ttl: int = 2) -> None:
    """
    Сохранение значения в кэш
    
    Args:
        key: Ключ кэша
        value: Значение для кэширования
        ttl: Время жизни кэша в секундах
    """
    redis_client = get_redis_client()
    
    # Пробуем Redis
    if redis_client:
        try:
            redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str)  # default=str для datetime
            )
            logger.debug(f"✅ Cache SET (Redis): {key} (TTL: {ttl}s)")
            return
        except Exception as e:
            logger.warning(f"Ошибка записи в Redis: {e}")
    
    # Fallback на in-memory кэш
    _memory_cache[key] = value
    _cache_timestamps[key] = time.time()
    logger.debug(f"✅ Cache SET (Memory): {key} (TTL: {ttl}s)")


def invalidate_cache(pattern: str = None) -> None:
    """
    Инвалидация кэша
    
    Args:
        pattern: Паттерн для удаления (например, "crash_detection:status:*")
    """
    redis_client = get_redis_client()
    
    # Пробуем Redis
    if redis_client:
        try:
            if pattern:
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
                    logger.info(f"✅ Инвалидирован кэш Redis: {pattern} ({len(keys)} ключей)")
            else:
                # Удаляем все ключи crash_detection
                keys = redis_client.keys("crash_detection:*")
                if keys:
                    redis_client.delete(*keys)
                    logger.info(f"✅ Инвалидирован весь кэш Crash Detection ({len(keys)} ключей)")
        except Exception as e:
            logger.warning(f"Ошибка инвалидации Redis кэша: {e}")
    
    # Очищаем in-memory кэш
    if pattern:
        keys_to_delete = [k for k in _memory_cache.keys() if pattern.replace("*", "") in k]
        for key in keys_to_delete:
            del _memory_cache[key]
            if key in _cache_timestamps:
                del _cache_timestamps[key]
        logger.info(f"✅ Инвалидирован in-memory кэш: {pattern} ({len(keys_to_delete)} ключей)")
    else:
        _memory_cache.clear()
        _cache_timestamps.clear()
        logger.info("✅ Инвалидирован весь in-memory кэш Crash Detection")


def cache_result(ttl: int = 2, key_prefix: str = None):
    """
    Декоратор для автоматического кэширования результатов функции
    
    Args:
        ttl: Время жизни кэша в секундах
        key_prefix: Префикс для ключа кэша (по умолчанию имя функции)
    
    Usage:
        @cache_result(ttl=2)
        async def get_status():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Генерируем ключ кэша
            prefix = key_prefix or func.__name__
            cache_key = get_cache_key(prefix, **kwargs)
            
            # Пробуем получить из кэша
            cached_value = get_cached(cache_key, ttl)
            if cached_value is not None:
                return cached_value
            
            # Выполняем функцию
            result = await func(*args, **kwargs)
            
            # Сохраняем в кэш
            set_cached(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Импорт os для переменных окружения
import os
