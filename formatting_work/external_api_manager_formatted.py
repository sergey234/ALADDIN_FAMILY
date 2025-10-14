#!/usr/bin/env python3
"""
External API Manager для ALADDIN Security System
Управляет интеграцией с бесплатными внешними API сервисами
"""

import asyncio
import json
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import aiohttp

from core.base import ComponentStatus, SecurityLevel
from core.security_base import SecurityBase


class APIType(Enum):
    """Типы внешних API"""

    THREAT_INTELLIGENCE = "threat_intelligence"
    IP_GEOLOCATION = "ip_geolocation"
    EMAIL_VALIDATION = "email_validation"


class APIStatus(Enum):
    """Статус API"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


@dataclass
class APIEndpoint:
    """Конфигурация API endpoint"""

    name: str
    url: str
    api_type: APIType
    rate_limit: int  # запросов в минуту
    timeout: int = 10
    retry_attempts: int = 3
    requires_auth: bool = False
    auth_key: Optional[str] = None
    headers: Optional[Dict[str, str]] = None


@dataclass
class APIResponse:
    """Ответ от внешнего API"""

    success: bool
    data: Dict[str, Any]
    status_code: int
    response_time: float
    api_name: str
    timestamp: datetime
    error_message: Optional[str] = None


class ExternalAPIManager(SecurityBase):
    """Менеджер внешних API для ALADDIN Security System"""

    def __init__(self):
        super().__init__("ExternalAPIManager")
        self.status = ComponentStatus.RUNNING
        self.security_level = SecurityLevel.HIGH

        # Конфигурация API endpoints
        self.api_endpoints = self._initialize_api_endpoints()

        # Кэш для результатов
        self.cache = {}
        self.cache_ttl = 300  # 5 минут

        # Статистика использования
        self.usage_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "rate_limited_requests": 0,
            "cache_hits": 0,
        }

        # Rate limiting
        self.rate_limits = {}
        self.last_request_time = {}

        # Thread pool для асинхронных запросов
        self.executor = ThreadPoolExecutor(max_workers=10)

        # Логгер
        self.logger = logging.getLogger("ExternalAPIManager")

        # Инициализация rate limits
        self._initialize_rate_limits()

    def _initialize_api_endpoints(self) -> Dict[str, APIEndpoint]:
        """Инициализация конфигурации API endpoints"""
        return {
            # Threat Intelligence APIs
            "scumware": APIEndpoint(
                name="SCUMWARE.org",
                url="https://scumware.org/api/check",
                api_type=APIType.THREAT_INTELLIGENCE,
                rate_limit=60,  # 1 запрос в секунду
                timeout=15,
                retry_attempts=3,
                requires_auth=False,
            ),
            "otx": APIEndpoint(
                name="Open Threat Exchange",
                url="https://otx.alienvault.com/api/v1/indicators",
                api_type=APIType.THREAT_INTELLIGENCE,
                rate_limit=30,  # 30 запросов в минуту
                timeout=10,
                retry_attempts=2,
                requires_auth=False,
            ),
            # IP Geolocation APIs
            "apip": APIEndpoint(
                name="APIP.cc",
                url="https://apip.cc/api-json",
                api_type=APIType.IP_GEOLOCATION,
                rate_limit=20,  # 20 запросов в секунду
                timeout=5,
                retry_attempts=2,
                requires_auth=False,
            ),
            "reallyfreegeoip": APIEndpoint(
                name="ReallyFreeGeoIP",
                url="https://reallyfreegeoip.org/json",
                api_type=APIType.IP_GEOLOCATION,
                rate_limit=100,  # без ограничений, но будем вежливыми
                timeout=5,
                retry_attempts=2,
                requires_auth=False,
            ),
            # Email Validation APIs
            "rapid_email": APIEndpoint(
                name="Rapid Email Verifier",
                url="https://rapid-email-verifier.fly.dev/verify",
                api_type=APIType.EMAIL_VALIDATION,
                rate_limit=100,  # 100 запросов в минуту
                timeout=10,
                retry_attempts=2,
                requires_auth=False,
            ),
            "noparam": APIEndpoint(
                name="NoParam Email Validator",
                url="https://noparam.com/api/v1/validate",
                api_type=APIType.EMAIL_VALIDATION,
                rate_limit=10,  # 10 запросов в минуту
                timeout=10,
                retry_attempts=2,
                requires_auth=False,
            ),
        }

    def _initialize_rate_limits(self):
        """Инициализация rate limits для каждого API"""
        for api_name in self.api_endpoints:
            self.rate_limits[api_name] = {
                "requests_count": 0,
                "window_start": time.time(),
                "status": APIStatus.ACTIVE,
            }
            self.last_request_time[api_name] = 0

    async def _check_rate_limit(self, api_name: str) -> bool:
        """Проверка rate limit для API"""
        if api_name not in self.rate_limits:
            return True

        current_time = time.time()
        rate_data = self.rate_limits[api_name]
        endpoint = self.api_endpoints[api_name]

        # Сброс счетчика если прошла минута
        if current_time - rate_data["window_start"] >= 60:
            rate_data["requests_count"] = 0
            rate_data["window_start"] = current_time
            rate_data["status"] = APIStatus.ACTIVE

        # Проверка лимита
        if rate_data["requests_count"] >= endpoint.rate_limit:
            rate_data["status"] = APIStatus.RATE_LIMITED
            return False

        return True

    async def _make_api_request(
        self, api_name: str, params: Dict[str, Any]
    ) -> APIResponse:
        """Выполнение запроса к внешнему API"""
        if api_name not in self.api_endpoints:
            return APIResponse(
                success=False,
                data={},
                status_code=0,
                response_time=0,
                api_name=api_name,
                timestamp=datetime.now(),
                error_message=f"API {api_name} не найден",
            )

        endpoint = self.api_endpoints[api_name]
        start_time = time.time()

        try:
            # Проверка rate limit
            if not await self._check_rate_limit(api_name):
                return APIResponse(
                    success=False,
                    data={},
                    status_code=429,
                    response_time=time.time() - start_time,
                    api_name=api_name,
                    timestamp=datetime.now(),
                    error_message="Rate limit exceeded",
                )

            # Подготовка URL
            if api_name == "apip":
                url = f"{endpoint.url}/{params.get('ip', '')}"
            elif api_name == "reallyfreegeoip":
                url = f"{endpoint.url}/{params.get('ip', '')}"
            else:
                url = endpoint.url

            # Подготовка headers
            headers = endpoint.headers or {}
            headers.update(
                {
                    "User-Agent": "ALADDIN-Security-System/1.0",
                    "Accept": "application/json",
                }
            )

            # Выполнение запроса
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=endpoint.timeout)
            ) as session:
                if api_name in ["scumware", "otx"]:
                    # POST запрос для threat intelligence
                    async with session.post(
                        url, json=params, headers=headers
                    ) as response:
                        data = await response.json()
                        status_code = response.status
                else:
                    # GET запрос для остальных API
                    async with session.get(
                        url, params=params, headers=headers
                    ) as response:
                        data = await response.json()
                        status_code = response.status

            # Обновление статистики
            self.rate_limits[api_name]["requests_count"] += 1
            self.last_request_time[api_name] = time.time()

            response_time = time.time() - start_time

            return APIResponse(
                success=status_code == 200,
                data=data,
                status_code=status_code,
                response_time=response_time,
                api_name=api_name,
                timestamp=datetime.now(),
            )

        except asyncio.TimeoutError:
            return APIResponse(
                success=False,
                data={},
                status_code=408,
                response_time=time.time() - start_time,
                api_name=api_name,
                timestamp=datetime.now(),
                error_message="Request timeout",
            )
        except Exception as e:
            return APIResponse(
                success=False,
                data={},
                status_code=0,
                response_time=time.time() - start_time,
                api_name=api_name,
                timestamp=datetime.now(),
                error_message=str(e),
            )

    async def check_threat_intelligence(
        self, indicator: str, indicator_type: str = "ip"
    ) -> Dict[str, Any]:
        """Проверка индикатора угрозы"""
        # Проверка кэша
        cache_key = f"threat_{indicator_type}_{indicator}"
        if cache_key in self.cache:
            cache_data = self.cache[cache_key]
            if datetime.now() - cache_data["timestamp"] < timedelta(
                seconds=self.cache_ttl
            ):
                self.usage_stats["cache_hits"] += 1
                return cache_data["data"]

        results = {}

        # SCUMWARE.org
        try:
            scumware_response = await self._make_api_request(
                "scumware", {"indicator": indicator, "type": indicator_type}
            )
            if scumware_response.success:
                results["scumware"] = scumware_response.data
        except Exception as e:
            self.logger.error(f"SCUMWARE API error: {e}")

        # OTX
        try:
            otx_response = await self._make_api_request(
                "otx", {"indicator": indicator, "type": indicator_type}
            )
            if otx_response.success:
                results["otx"] = otx_response.data
        except Exception as e:
            self.logger.error(f"OTX API error: {e}")

        # Сохранение в кэш
        self.cache[cache_key] = {"data": results, "timestamp": datetime.now()}

        self.usage_stats["total_requests"] += 1
        if results:
            self.usage_stats["successful_requests"] += 1
        else:
            self.usage_stats["failed_requests"] += 1

        return results

    async def get_ip_geolocation(self, ip_address: str) -> Dict[str, Any]:
        """Получение геолокации IP адреса"""
        # Проверка кэша
        cache_key = f"geo_{ip_address}"
        if cache_key in self.cache:
            cache_data = self.cache[cache_key]
            if datetime.now() - cache_data["timestamp"] < timedelta(
                seconds=self.cache_ttl
            ):
                self.usage_stats["cache_hits"] += 1
                return cache_data["data"]

        results = {}

        # APIP.cc
        try:
            apip_response = await self._make_api_request(
                "apip", {"ip": ip_address}
            )
            if apip_response.success:
                results["apip"] = apip_response.data
        except Exception as e:
            self.logger.error(f"APIP API error: {e}")

        # ReallyFreeGeoIP
        try:
            rfgi_response = await self._make_api_request(
                "reallyfreegeoip", {"ip": ip_address}
            )
            if rfgi_response.success:
                results["reallyfreegeoip"] = rfgi_response.data
        except Exception as e:
            self.logger.error(f"ReallyFreeGeoIP API error: {e}")

        # Сохранение в кэш
        self.cache[cache_key] = {"data": results, "timestamp": datetime.now()}

        self.usage_stats["total_requests"] += 1
        if results:
            self.usage_stats["successful_requests"] += 1
        else:
            self.usage_stats["failed_requests"] += 1

        return results

    async def validate_email(self, email_address: str) -> Dict[str, Any]:
        """Валидация email адреса"""
        # Проверка кэша
        cache_key = f"email_{email_address}"
        if cache_key in self.cache:
            cache_data = self.cache[cache_key]
            if datetime.now() - cache_data["timestamp"] < timedelta(
                seconds=self.cache_ttl
            ):
                self.usage_stats["cache_hits"] += 1
                return cache_data["data"]

        results = {}

        # Rapid Email Verifier
        try:
            rapid_response = await self._make_api_request(
                "rapid_email", {"email": email_address}
            )
            if rapid_response.success:
                results["rapid_email"] = rapid_response.data
        except Exception as e:
            self.logger.error(f"Rapid Email API error: {e}")

        # NoParam
        try:
            noparam_response = await self._make_api_request(
                "noparam", {"email": email_address}
            )
            if noparam_response.success:
                results["noparam"] = noparam_response.data
        except Exception as e:
            self.logger.error(f"NoParam API error: {e}")

        # Сохранение в кэш
        self.cache[cache_key] = {"data": results, "timestamp": datetime.now()}

        self.usage_stats["total_requests"] += 1
        if results:
            self.usage_stats["successful_requests"] += 1
        else:
            self.usage_stats["failed_requests"] += 1

        return results

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Получение статистики использования API"""
        return {
            "usage_stats": self.usage_stats.copy(),
            "rate_limits": {
                name: {
                    "requests_count": data["requests_count"],
                    "window_start": data["window_start"],
                    "status": data["status"].value,
                }
                for name, data in self.rate_limits.items()
            },
            "cache_size": len(self.cache),
            "active_apis": len([api for api in self.api_endpoints.keys()]),
            "timestamp": datetime.now().isoformat(),
        }

    def clear_cache(self):
        """Очистка кэша"""
        self.cache.clear()
        self.logger.info("API cache cleared")

    def get_api_status(self) -> Dict[str, Any]:
        """Получение статуса всех API"""
        status = {}
        for api_name, endpoint in self.api_endpoints.items():
            rate_data = self.rate_limits.get(api_name, {})
            status[api_name] = {
                "name": endpoint.name,
                "type": endpoint.api_type.value,
                "rate_limit": endpoint.rate_limit,
                "status": rate_data.get("status", APIStatus.INACTIVE).value,
                "requests_count": rate_data.get("requests_count", 0),
                "last_request": self.last_request_time.get(api_name, 0),
            }
        return status


# Глобальный экземпляр менеджера
external_api_manager = ExternalAPIManager()
