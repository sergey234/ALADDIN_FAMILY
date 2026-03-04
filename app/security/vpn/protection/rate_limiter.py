#!/usr/bin/env python3
"""
ALADDIN VPN - Advanced Rate Limiting System
Улучшенная система ограничения скорости запросов

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import hashlib
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional, Tuple, Union

import asyncio
import redis

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Стратегии ограничения скорости"""

    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitAction(Enum):
    """Действия при превышении лимита"""

    ALLOW = "allow"
    BLOCK = "block"
    DELAY = "delay"
    CAPTCHA = "captcha"
    REDIRECT = "redirect"


@dataclass
class RateLimitRule:
    """Правило ограничения скорости"""

    name: str
    pattern: str  # Паттерн для сопоставления эндпоинтов
    max_requests: int
    time_window: int  # в секундах
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    action: RateLimitAction = RateLimitAction.BLOCK
    message: str = "Rate limit exceeded"
    burst_size: int = None  # Для token bucket
    refill_rate: float = None  # Для token bucket
    delay_seconds: float = 0.0  # Для delay action
    redirect_url: str = None  # Для redirect action
    headers: Dict[str, str] = None  # Дополнительные заголовки

    def __post_init__(self):
        if self.headers is None:
            self.headers = {}

        # Настройки по умолчанию для token bucket
        if self.strategy == RateLimitStrategy.TOKEN_BUCKET:
            if self.burst_size is None:
                self.burst_size = self.max_requests
            if self.refill_rate is None:
                self.refill_rate = self.max_requests / self.time_window


@dataclass
class RateLimitResult:
    """Результат проверки rate limit"""

    allowed: bool
    remaining: int
    reset_time: datetime
    retry_after: Optional[int] = None
    action: RateLimitAction = RateLimitAction.ALLOW
    message: str = "OK"
    headers: Dict[str, str] = None

    def __post_init__(self):
        if self.headers is None:
            self.headers = {}


class TokenBucket:
    """Реализация алгоритма Token Bucket"""

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Попытка потребить токены"""
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self):
        """Пополнение токенов"""
        now = time.time()
        time_passed = now - self.last_refill
        tokens_to_add = time_passed * self.refill_rate

        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def get_tokens(self) -> float:
        """Получение текущего количества токенов"""
        self._refill()
        return self.tokens


class LeakyBucket:
    """Реализация алгоритма Leaky Bucket"""

    def __init__(self, capacity: int, leak_rate: float):
        self.capacity = capacity
        self.tokens = 0
        self.leak_rate = leak_rate
        self.last_leak = time.time()

    def add(self, tokens: int = 1) -> bool:
        """Добавление токенов в bucket"""
        self._leak()

        if self.tokens + tokens <= self.capacity:
            self.tokens += tokens
            return True
        return False

    def _leak(self):
        """Утечка токенов"""
        now = time.time()
        time_passed = now - self.last_leak
        tokens_to_remove = time_passed * self.leak_rate

        self.tokens = max(0, self.tokens - tokens_to_remove)
        self.last_leak = now

    def get_tokens(self) -> float:
        """Получение текущего количества токенов"""
        self._leak()
        return self.tokens


class AdvancedRateLimiter:
    """
    Продвинутая система ограничения скорости

    Функции:
    - Множественные стратегии (Fixed Window, Sliding Window, Token Bucket, Leaky Bucket)
    - Redis поддержка для распределенных систем
    - Гибкие правила по эндпоинтам
    - Burst handling
    - Graceful degradation
    - Мониторинг и метрики
    """

    def __init__(self, redis_url: str = None, config_file: str = "config/rate_limiting.json"):
        self.config_file = config_file
        self.config = self._load_config()

        # Redis подключение
        self.redis_client = None
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()
                logger.info("Connected to Redis for rate limiting")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                self.redis_client = None

        # Локальное хранилище (fallback)
        self.local_storage: Dict[str, Any] = defaultdict(dict)
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.leaky_buckets: Dict[str, LeakyBucket] = {}

        # Правила
        self.rules: List[RateLimitRule] = []
        self._load_rules()

        # Метрики
        self.metrics = {
            "total_requests": 0,
            "blocked_requests": 0,
            "rate_limited_requests": 0,
            "captcha_requests": 0,
            "redirect_requests": 0,
        }

        logger.info("Advanced Rate Limiter initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        default_config = {
            "default_strategy": "sliding_window",
            "default_action": "block",
            "redis_enabled": True,
            "redis_ttl": 3600,
            "cleanup_interval": 300,
            "max_local_entries": 100000,
            "burst_handling": True,
            "graceful_degradation": True,
            "monitoring_enabled": True,
        }

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                default_config.update(config)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_file} not found, using defaults")
            self._save_config(default_config)

        return default_config

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Сохранение конфигурации"""
        import os

        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _load_rules(self) -> None:
        """Загрузка правил rate limiting"""
        default_rules = [
            RateLimitRule(
                name="general",
                pattern=".*",
                max_requests=1000,
                time_window=3600,
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                action=RateLimitAction.BLOCK,
            ),
            RateLimitRule(
                name="api",
                pattern="/api/.*",
                max_requests=500,
                time_window=3600,
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                action=RateLimitAction.BLOCK,
            ),
            RateLimitRule(
                name="login",
                pattern="/(login|auth|signin).*",
                max_requests=5,
                time_window=300,
                strategy=RateLimitStrategy.FIXED_WINDOW,
                action=RateLimitAction.BLOCK,
            ),
            RateLimitRule(
                name="admin",
                pattern="/admin/.*",
                max_requests=20,
                time_window=60,
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                action=RateLimitAction.CAPTCHA,
            ),
            RateLimitRule(
                name="vpn_connect",
                pattern="/vpn/connect.*",
                max_requests=10,
                time_window=60,
                strategy=RateLimitStrategy.TOKEN_BUCKET,
                action=RateLimitAction.DELAY,
                delay_seconds=1.0,
            ),
            RateLimitRule(
                name="vpn_config",
                pattern="/vpn/config.*",
                max_requests=5,
                time_window=300,
                strategy=RateLimitStrategy.LEAKY_BUCKET,
                action=RateLimitAction.CAPTCHA,
            ),
        ]

        self.rules = default_rules.copy()

        # Загружаем кастомные правила из конфига
        if "custom_rules" in self.config:
            for rule_data in self.config["custom_rules"]:
                rule = RateLimitRule(
                    name=rule_data["name"],
                    pattern=rule_data["pattern"],
                    max_requests=rule_data["max_requests"],
                    time_window=rule_data["time_window"],
                    strategy=RateLimitStrategy(rule_data.get("strategy", "sliding_window")),
                    action=RateLimitAction(rule_data.get("action", "block")),
                    message=rule_data.get("message", "Rate limit exceeded"),
                    burst_size=rule_data.get("burst_size"),
                    refill_rate=rule_data.get("refill_rate"),
                    delay_seconds=rule_data.get("delay_seconds", 0.0),
                    redirect_url=rule_data.get("redirect_url"),
                    headers=rule_data.get("headers", {}),
                )
                self.rules.append(rule)

    def _get_rule_for_endpoint(self, endpoint: str) -> Optional[RateLimitRule]:
        """Получение правила для эндпоинта"""
        import re

        for rule in self.rules:
            if re.match(rule.pattern, endpoint):
                return rule

        return None

    def _get_key(self, identifier: str, rule: RateLimitRule) -> str:
        """Генерация ключа для хранения"""
        return f"rate_limit:{rule.name}:{identifier}"

    async def check_rate_limit(self, identifier: str, endpoint: str, tokens: int = 1) -> RateLimitResult:  # noqa: C901
        """
        Проверка rate limit для запроса

        Args:
            identifier: Уникальный идентификатор (IP, user_id, etc.)
            endpoint: Эндпоинт запроса
            tokens: Количество токенов для потребления

        Returns:
            RateLimitResult: Результат проверки
        """
        try:
            # Обновляем метрики
            self.metrics["total_requests"] += 1

            # Находим подходящее правило
            rule = self._get_rule_for_endpoint(endpoint)
            if not rule:
                return RateLimitResult(
                    allowed=True,
                    remaining=999999,
                    reset_time=datetime.now() + timedelta(hours=1),
                    action=RateLimitAction.ALLOW,
                )

            # Проверяем rate limit в зависимости от стратегии
            if rule.strategy == RateLimitStrategy.FIXED_WINDOW:
                result = await self._check_fixed_window(identifier, rule, tokens)
            elif rule.strategy == RateLimitStrategy.SLIDING_WINDOW:
                result = await self._check_sliding_window(identifier, rule, tokens)
            elif rule.strategy == RateLimitStrategy.TOKEN_BUCKET:
                result = await self._check_token_bucket(identifier, rule, tokens)
            elif rule.strategy == RateLimitStrategy.LEAKY_BUCKET:
                result = await self._check_leaky_bucket(identifier, rule, tokens)
            else:
                result = RateLimitResult(
                    allowed=True,
                    remaining=999999,
                    reset_time=datetime.now() + timedelta(hours=1),
                    action=RateLimitAction.ALLOW,
                )

            # Обновляем метрики
            if not result.allowed:
                self.metrics["blocked_requests"] += 1
                if result.action == RateLimitAction.CAPTCHA:
                    self.metrics["captcha_requests"] += 1
                elif result.action == RateLimitAction.REDIRECT:
                    self.metrics["redirect_requests"] += 1
                else:
                    self.metrics["rate_limited_requests"] += 1

            return result

        except Exception as e:
            logger.error(f"Error in check_rate_limit: {e}")
            # Graceful degradation - разрешаем запрос при ошибке
            if self.config.get("graceful_degradation", True):
                return RateLimitResult(
                    allowed=True,
                    remaining=999999,
                    reset_time=datetime.now() + timedelta(hours=1),
                    action=RateLimitAction.ALLOW,
                    message="Rate limiter error, allowing request",
                )
            else:
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=datetime.now() + timedelta(minutes=1),
                    action=RateLimitAction.BLOCK,
                    message="Rate limiter error",
                )

    async def _check_fixed_window(self, identifier: str, rule: RateLimitRule, tokens: int) -> RateLimitResult:
        """Проверка Fixed Window стратегии"""
        now = datetime.now()
        window_start = now.replace(second=0, microsecond=0)

        if now.second >= rule.time_window:
            window_start = window_start.replace(minute=now.minute - (now.second // rule.time_window))

        key = f"{self._get_key(identifier, rule)}:{window_start.timestamp()}"

        if self.redis_client:
            # Redis реализация
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, rule.time_window)
            pipe.get(key)
            results = pipe.execute()

            current_count = int(results[0])
            remaining = max(0, rule.max_requests - current_count)
            reset_time = window_start + timedelta(seconds=rule.time_window)

        else:
            # Локальная реализация
            if key not in self.local_storage:
                self.local_storage[key] = {"count": 0, "expires": window_start + timedelta(seconds=rule.time_window)}

            storage = self.local_storage[key]

            # Очистка истекших записей
            if now > storage["expires"]:
                storage["count"] = 0
                storage["expires"] = window_start + timedelta(seconds=rule.time_window)

            storage["count"] += tokens
            current_count = storage["count"]
            remaining = max(0, rule.max_requests - current_count)
            reset_time = storage["expires"]

        allowed = current_count <= rule.max_requests

        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_time=reset_time,
            action=rule.action if not allowed else RateLimitAction.ALLOW,
            message=rule.message if not allowed else "OK",
        )

    async def _check_sliding_window(self, identifier: str, rule: RateLimitRule, tokens: int) -> RateLimitResult:
        """Проверка Sliding Window стратегии"""
        now = datetime.now()
        window_start = now - timedelta(seconds=rule.time_window)

        key = self._get_key(identifier, rule)

        if self.redis_client:
            # Redis реализация с использованием sorted set
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start.timestamp())
            pipe.zadd(key, {str(now.timestamp()): now.timestamp()})
            pipe.zcard(key)
            pipe.expire(key, rule.time_window)
            results = pipe.execute()

            current_count = results[2]
            remaining = max(0, rule.max_requests - current_count)
            reset_time = now + timedelta(seconds=rule.time_window)

        else:
            # Локальная реализация
            if key not in self.local_storage:
                self.local_storage[key] = deque()

            timestamps = self.local_storage[key]

            # Удаляем старые записи
            while timestamps and timestamps[0] < window_start:
                timestamps.popleft()

            timestamps.append(now)
            current_count = len(timestamps)
            remaining = max(0, rule.max_requests - current_count)
            reset_time = now + timedelta(seconds=rule.time_window)

        allowed = current_count <= rule.max_requests

        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_time=reset_time,
            action=rule.action if not allowed else RateLimitAction.ALLOW,
            message=rule.message if not allowed else "OK",
        )

    async def _check_token_bucket(self, identifier: str, rule: RateLimitRule, tokens: int) -> RateLimitResult:
        """Проверка Token Bucket стратегии"""
        key = self._get_key(identifier, rule)

        if key not in self.token_buckets:
            self.token_buckets[key] = TokenBucket(capacity=rule.burst_size, refill_rate=rule.refill_rate)

        bucket = self.token_buckets[key]
        allowed = bucket.consume(tokens)
        remaining = int(bucket.get_tokens())

        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_time=datetime.now() + timedelta(seconds=rule.time_window),
            action=rule.action if not allowed else RateLimitAction.ALLOW,
            message=rule.message if not allowed else "OK",
        )

    async def _check_leaky_bucket(self, identifier: str, rule: RateLimitRule, tokens: int) -> RateLimitResult:
        """Проверка Leaky Bucket стратегии"""
        key = self._get_key(identifier, rule)

        if key not in self.leaky_buckets:
            self.leaky_buckets[key] = LeakyBucket(
                capacity=rule.max_requests, leak_rate=rule.max_requests / rule.time_window
            )

        bucket = self.leaky_buckets[key]
        allowed = bucket.add(tokens)
        remaining = int(rule.max_requests - bucket.get_tokens())

        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_time=datetime.now() + timedelta(seconds=rule.time_window),
            action=rule.action if not allowed else RateLimitAction.ALLOW,
            message=rule.message if not allowed else "OK",
        )

    def add_rule(self, rule: RateLimitRule) -> None:
        """Добавление нового правила"""
        self.rules.append(rule)
        logger.info(f"Added rate limit rule: {rule.name}")

    def remove_rule(self, rule_name: str) -> bool:
        """Удаление правила"""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                del self.rules[i]
                logger.info(f"Removed rate limit rule: {rule_name}")
                return True
        return False

    def get_metrics(self) -> Dict[str, Any]:
        """Получение метрик"""
        return {
            **self.metrics,
            "rules_count": len(self.rules),
            "redis_connected": self.redis_client is not None,
            "local_entries": len(self.local_storage),
            "token_buckets": len(self.token_buckets),
            "leaky_buckets": len(self.leaky_buckets),
        }

    def reset_metrics(self) -> None:
        """Сброс метрик"""
        self.metrics = {
            "total_requests": 0,
            "blocked_requests": 0,
            "rate_limited_requests": 0,
            "captcha_requests": 0,
            "redirect_requests": 0,
        }

    async def cleanup(self) -> None:
        """Очистка устаревших данных"""
        now = datetime.now()

        # Очистка локального хранилища
        keys_to_remove = []
        for key, data in self.local_storage.items():
            if isinstance(data, dict) and "expires" in data:
                if now > data["expires"]:
                    keys_to_remove.append(key)
            elif isinstance(data, deque) and len(data) > 0:
                # Очистка sliding window данных старше 1 часа
                cutoff = now - timedelta(hours=1)
                while data and data[0] < cutoff:
                    data.popleft()

        for key in keys_to_remove:
            del self.local_storage[key]

        logger.info(f"Cleaned up {len(keys_to_remove)} expired entries")


# Глобальный экземпляр rate limiter
rate_limiter = AdvancedRateLimiter()


def rate_limit(rule_name: str = None, tokens: int = 1):
    """Декоратор для rate limiting"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Извлекаем IP из запроса (предполагаем Flask)
            request = kwargs.get("request") or (args[0] if args else None)
            if hasattr(request, "remote_addr"):
                identifier = request.remote_addr
            else:
                identifier = "unknown"

            # Получаем эндпоинт
            endpoint = getattr(request, "path", "/") if request else "/"

            # Проверяем rate limit
            result = await rate_limiter.check_rate_limit(identifier, endpoint, tokens)

            if not result.allowed:
                if result.action == RateLimitAction.BLOCK:
                    return {"error": result.message, "retry_after": result.retry_after}, 429
                elif result.action == RateLimitAction.CAPTCHA:
                    return {"error": "CAPTCHA required", "captcha_url": "/captcha"}, 429
                elif result.action == RateLimitAction.REDIRECT:
                    return {"redirect": result.redirect_url}, 302
                elif result.action == RateLimitAction.DELAY:
                    await asyncio.sleep(result.retry_after or 1.0)

            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def check_rate_limit(identifier: str, endpoint: str, tokens: int = 1) -> RateLimitResult:
    """Глобальная функция проверки rate limit"""
    return await rate_limiter.check_rate_limit(identifier, endpoint, tokens)


def get_rate_limit_metrics() -> Dict[str, Any]:
    """Получение метрик rate limiting"""
    return rate_limiter.get_metrics()


if __name__ == "__main__":
    # Тестирование системы
    async def test_rate_limiter():
        print("🧪 Testing Advanced Rate Limiter...")

        # Тестовые запросы
        test_cases = [
            ("192.168.1.1", "/api/v1/status", 1),
            ("192.168.1.1", "/login", 1),
            ("192.168.1.1", "/admin/dashboard", 1),
            ("192.168.1.2", "/vpn/connect", 1),
            ("192.168.1.2", "/vpn/config", 1),
        ]

        for i in range(15):
            for identifier, endpoint, tokens in test_cases:
                result = await check_rate_limit(identifier, endpoint, tokens)
                print(
                    f"IP: {identifier}, Endpoint: {endpoint}, Allowed: {result.allowed}, "
                    f"Remaining: {result.remaining}, Action: {result.action.value}"
                )

        # Метрики
        metrics = get_rate_limit_metrics()
        print(f"\n📊 Metrics: {json.dumps(metrics, indent=2)}")

        print("✅ Advanced Rate Limiter test completed")

    # Запуск тестов
    asyncio.run(test_rate_limiter())
