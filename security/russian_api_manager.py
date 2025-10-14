#!/usr/bin/env python3
"""
Российский API Manager для ALADDIN Security System
Интеграция с Яндекс Картами, ГЛОНАСС и другими российскими сервисами
"""

import hashlib
import json
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp

from core.base import ComponentStatus, SecurityLevel
from core.logging_module import LoggingManager
from core.security_base import SecurityBase


class RussianAPIType(Enum):
    """Типы российских API"""

    YANDEX_MAPS = "yandex_maps"
    YANDEX_GEOCODER = "yandex_geocoder"
    YANDEX_ROUTING = "yandex_routing"
    GLONASS_FREE = "glonass_free"
    ALTOX_SERVER = "altox_server"
    WIALON = "wialon"
    TWOGIS = "2gis"
    VK_API = "vk_api"
    RUSSIAN_BANKS = "russian_banks"


@dataclass
class RussianAPIResponse:
    """Ответ от российского API"""

    success: bool
    data: Dict[str, Any]
    api_name: str
    response_time: float
    error: Optional[str] = None
    cached: bool = False


@dataclass
class GeocodingResult:
    """Результат геокодирования"""

    address: str
    coordinates: List[float]  # [latitude, longitude]
    country: str
    city: str
    region: str
    precision: str
    api_source: str


@dataclass
class RoutingResult:
    """Результат построения маршрута"""

    from_point: str
    to_point: str
    distance: float  # в метрах
    duration: float  # в секундах
    route_type: str
    api_source: str


class RussianAPIManager(SecurityBase):
    """Менеджер российских API для геолокации и маршрутизации"""

    def __init__(self) -> None:
        super().__init__("RussianAPIManager")
        self.status = ComponentStatus.INITIALIZING
        self.security_level = SecurityLevel.HIGH
        self.logger = LoggingManager(name="RussianAPIManager")

        # Загружаем конфигурацию
        self.config_file = "config/russian_apis_config.json"
        self._load_config()

        # Конфигурация российских API
        self.api_configs = {
            RussianAPIType.YANDEX_MAPS: {
                "name": "Яндекс Карты",
                "base_url": "https://api-maps.yandex.ru/2.1/",
                "geocoder_url": "https://geocode-maps.yandex.ru/1.x/",
                "routing_url": "https://api.routing.yandex.net/v2/",
                "api_key": self.config.get("yandex_maps", {}).get(
                    "api_key", "YOUR_YANDEX_API_KEY"
                ),
                "free_tier_limit": 25000,  # запросов в день
                "rate_limit": 50,  # запросов в секунду
                "supports_glonass": True,
                "supports_gps": True,
            },
            RussianAPIType.GLONASS_FREE: {
                "name": "Открытый ГЛОНАСС",
                "base_url": "https://free-gps.ru/api/",
                "api_key": None,  # Бесплатный без ключа
                "free_tier_limit": 1000000,  # Практически без лимитов
                "rate_limit": 100,
                "supports_glonass": True,
                "supports_gps": True,
            },
            RussianAPIType.ALTOX_SERVER: {
                "name": "ALTOX Server",
                "base_url": "https://altox.ru/api/",
                "api_key": None,
                "free_tier_limit": 1000,  # 1 объект бесплатно
                "rate_limit": 10,
                "supports_glonass": True,
                "supports_gps": True,
            },
            RussianAPIType.TWOGIS: {
                "name": "2GIS",
                "base_url": "https://catalog.api.2gis.com/",
                "search_url": "https://catalog.api.2gis.com/3.0/items",
                "geocoder_url": "https://catalog.api.2gis.com/3.0/items/geocode",
                "api_key": self.config.get("2gis", {}).get("api_key", "YOUR_2GIS_API_KEY"),
                "free_tier_limit": 10000,  # запросов в день
                "rate_limit": 20,
                "supports_glonass": False,
                "supports_gps": True,
            },
            RussianAPIType.VK_API: {
                "name": "VK API",
                "base_url": "https://api.vk.com/method/",
                "api_key": self.config.get("vk", {}).get("api_key", "YOUR_VK_API_KEY"),
                "free_tier_limit": 1000,  # запросов в день
                "rate_limit": 3,
                "supports_glonass": False,
                "supports_gps": False,
            },
            RussianAPIType.RUSSIAN_BANKS: {
                "name": "Российские банки",
                "base_url": "https://api.bank.gov.ru/",
                "api_key": self.config.get("russian_banks", {}).get("api_key", "YOUR_BANK_API_KEY"),
                "free_tier_limit": 1000,
                "rate_limit": 10,
                "supports_glonass": False,
                "supports_gps": False,
            },
        }

        # Кэш для результатов
        self.cache = {}
        self.cache_ttl = 300  # 5 минут

        # Статистика использования
        self.usage_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "api_usage": {api_type.value: 0 for api_type in RussianAPIType},
        }

        # Rate limiting
        self.rate_limits = {
            api_type.value: {"count": 0, "last_reset": time.time()}
            for api_type in RussianAPIType
        }

        self.logger.log(
            "INFO",
            f"RussianAPIManager инициализирован с {len(self.api_configs)} API",
        )

    def _load_config(self) -> None:
        """Загрузка конфигурации из файла"""
        try:
            import json
            import os

            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), self.config_file
            )

            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                self.logger.log(
                    "INFO", f"Конфигурация загружена из {config_path}"
                )
            else:
                self.config = {}
                self.logger.log(
                    "WARNING", f"Файл конфигурации не найден: {config_path}"
                )
        except Exception as e:
            self.config = {}
            self.logger.log("ERROR", f"Ошибка загрузки конфигурации: {e}")

    def _get_cache_key(
        self, api_type: RussianAPIType, params: Dict[str, Any]
    ) -> str:
        """Генерация ключа кэша"""
        key_data = f"{api_type.value}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Проверка валидности кэша"""
        if cache_key not in self.cache:
            return False

        cache_time = self.cache[cache_key].get("timestamp", 0)
        return time.time() - cache_time < self.cache_ttl

    def _check_rate_limit(self, api_type: RussianAPIType) -> bool:
        """Проверка rate limit"""
        config = self.api_configs.get(api_type, {})
        rate_limit = config.get("rate_limit", 10)

        current_time = time.time()
        api_key = api_type.value

        if (
            current_time - self.rate_limits[api_key]["last_reset"] > 60
        ):  # Сброс каждую минуту
            self.rate_limits[api_key]["count"] = 0
            self.rate_limits[api_key]["last_reset"] = current_time

        if self.rate_limits[api_key]["count"] >= rate_limit:
            self.logger.log(
                "WARNING", f"Rate limit превышен для {api_type.value}"
            )
            return False

        self.rate_limits[api_key]["count"] += 1
        return True

    async def _make_request(
        self,
        api_type: RussianAPIType,
        url: str,
        params: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
    ) -> RussianAPIResponse:
        """Выполнение HTTP запроса к российскому API"""
        start_time = time.time()

        try:
            config = self.api_configs.get(api_type, {})
            api_name = config.get("name", "Unknown")

            # Добавляем API ключ если нужен
            if config.get("api_key") and params:
                params["apikey"] = config["api_key"]

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, params=params, headers=headers, timeout=10
                ) as response:
                    response_time = time.time() - start_time

                    if response.status == 200:
                        data = await response.json()
                        self.usage_stats["successful_requests"] += 1
                        self.usage_stats["api_usage"][api_type.value] += 1

                        return RussianAPIResponse(
                            success=True,
                            data=data,
                            api_name=api_name,
                            response_time=response_time,
                        )
                    else:
                        error_text = await response.text()
                        self.usage_stats["failed_requests"] += 1

                        return RussianAPIResponse(
                            success=False,
                            data={},
                            api_name=api_name,
                            response_time=response_time,
                            error=f"HTTP {response.status}: {error_text}",
                        )

        except Exception as e:
            response_time = time.time() - start_time
            self.usage_stats["failed_requests"] += 1

            return RussianAPIResponse(
                success=False,
                data={},
                api_name=api_name,
                response_time=response_time,
                error=str(e),
            )

    async def geocode_address(
        self,
        address: str,
        api_type: RussianAPIType = RussianAPIType.YANDEX_GEOCODER,
    ) -> GeocodingResult:
        """Геокодирование адреса в координаты"""
        self.logger.log("INFO", f"Геокодирование адреса: {address}")

        # Проверяем кэш
        cache_key = self._get_cache_key(api_type, {"address": address})
        if self._is_cache_valid(cache_key):
            self.usage_stats["cache_hits"] += 1
            cached_data = self.cache[cache_key]["data"]
            return GeocodingResult(**cached_data)

        # Проверяем rate limit
        if not self._check_rate_limit(api_type):
            raise Exception(f"Rate limit превышен для {api_type.value}")

        config = self.api_configs.get(api_type, {})
        url = config.get("geocoder_url", config.get("base_url", ""))

        params = {"geocode": address, "format": "json", "results": 1}

        if api_type == RussianAPIType.YANDEX_GEOCODER:
            params["apikey"] = config.get("api_key", "")

        response = await self._make_request(api_type, url, params)

        if response.success:
            # Парсим ответ в зависимости от API
            if api_type == RussianAPIType.YANDEX_GEOCODER:
                result = self._parse_yandex_geocoder_response(
                    response.data, address
                )
            else:
                result = self._parse_generic_geocoder_response(
                    response.data, address, api_type
                )

            # Сохраняем в кэш
            self.cache[cache_key] = {
                "data": result.__dict__,
                "timestamp": time.time(),
            }

            return result
        else:
            raise Exception(f"Ошибка геокодирования: {response.error}")

    def _parse_yandex_geocoder_response(
        self, data: Dict[str, Any], address: str
    ) -> GeocodingResult:
        """Парсинг ответа Яндекс Геокодера"""
        try:
            geo_objects = (
                data.get("response", {})
                .get("GeoObjectCollection", {})
                .get("featureMember", [])
            )

            if not geo_objects:
                raise Exception("Адрес не найден")

            geo_object = geo_objects[0]["GeoObject"]
            coords = geo_object["Point"]["pos"].split()
            longitude, latitude = float(coords[0]), float(coords[1])

            meta_data = geo_object.get("metaDataProperty", {}).get(
                "GeocoderMetaData", {}
            )
            address_details = meta_data.get("Address", {})

            return GeocodingResult(
                address=address,
                coordinates=[latitude, longitude],
                country=address_details.get("country_code", ""),
                city=address_details.get("locality", {}).get(
                    "LocalityName", ""
                ),
                region=address_details.get("AdministrativeArea", {}).get(
                    "AdministrativeAreaName", ""
                ),
                precision=meta_data.get("precision", "unknown"),
                api_source="Яндекс Геокодер",
            )
        except Exception as e:
            raise Exception(f"Ошибка парсинга ответа Яндекс: {e}")

    def _parse_generic_geocoder_response(
        self, data: Dict[str, Any], address: str, api_type: RussianAPIType
    ) -> GeocodingResult:
        """Парсинг ответа других API"""
        # Базовая реализация для других API
        return GeocodingResult(
            address=address,
            coordinates=[0.0, 0.0],  # Заглушка
            country="RU",
            city="Unknown",
            region="Unknown",
            precision="unknown",
            api_source=api_type.value,
        )

    async def build_route(
        self,
        from_point: str,
        to_point: str,
        route_type: str = "auto",
        api_type: RussianAPIType = RussianAPIType.YANDEX_ROUTING,
    ) -> RoutingResult:
        """Построение маршрута между точками"""
        self.logger.log(
            "INFO", f"Построение маршрута: {from_point} -> {to_point}"
        )

        # Проверяем кэш
        cache_key = self._get_cache_key(
            api_type, {"from": from_point, "to": to_point, "type": route_type}
        )

        if self._is_cache_valid(cache_key):
            self.usage_stats["cache_hits"] += 1
            cached_data = self.cache[cache_key]["data"]
            return RoutingResult(**cached_data)

        # Проверяем rate limit
        if not self._check_rate_limit(api_type):
            raise Exception(f"Rate limit превышен для {api_type.value}")

        config = self.api_configs.get(api_type, {})
        url = config.get("routing_url", config.get("base_url", ""))

        params = {
            "waypoints": f"{from_point}|{to_point}",
            "mode": route_type,
            "format": "json",
        }

        if api_type == RussianAPIType.YANDEX_ROUTING:
            params["apikey"] = config.get("api_key", "")

        response = await self._make_request(api_type, url, params)

        if response.success:
            # Парсим ответ
            if api_type == RussianAPIType.YANDEX_ROUTING:
                result = self._parse_yandex_routing_response(
                    response.data, from_point, to_point, route_type
                )
            else:
                result = self._parse_generic_routing_response(
                    response.data, from_point, to_point, route_type, api_type
                )

            # Сохраняем в кэш
            self.cache[cache_key] = {
                "data": result.__dict__,
                "timestamp": time.time(),
            }

            return result
        else:
            raise Exception(f"Ошибка построения маршрута: {response.error}")

    def _parse_yandex_routing_response(
        self,
        data: Dict[str, Any],
        from_point: str,
        to_point: str,
        route_type: str,
    ) -> RoutingResult:
        """Парсинг ответа Яндекс Маршрутизации"""
        try:
            route = data.get("route", {})
            distance = route.get("distance", {}).get("value", 0)
            duration = route.get("duration", {}).get("value", 0)

            return RoutingResult(
                from_point=from_point,
                to_point=to_point,
                distance=float(distance),
                duration=float(duration),
                route_type=route_type,
                api_source="Яндекс Маршрутизация",
            )
        except Exception as e:
            raise Exception(f"Ошибка парсинга маршрута Яндекс: {e}")

    def _parse_generic_routing_response(
        self,
        data: Dict[str, Any],
        from_point: str,
        to_point: str,
        route_type: str,
        api_type: RussianAPIType,
    ) -> RoutingResult:
        """Парсинг ответа других API маршрутизации"""
        return RoutingResult(
            from_point=from_point,
            to_point=to_point,
            distance=0.0,
            duration=0.0,
            route_type=route_type,
            api_source=api_type.value,
        )

    async def get_glonass_coordinates(
        self, device_id: str
    ) -> Optional[List[float]]:
        """Получение координат через ГЛОНАСС"""
        self.logger.log(
            "INFO", f"Получение ГЛОНАСС координат для устройства: {device_id}"
        )

        # Здесь можно интегрировать с реальными ГЛОНАСС API
        # Пока возвращаем заглушку
        return [55.7558, 37.6176]  # Москва

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Получение статистики использования"""
        return {
            "usage_stats": self.usage_stats,
            "cache_size": len(self.cache),
            "api_configs": {
                api_type.value: {
                    "name": config["name"],
                    "free_tier_limit": config["free_tier_limit"],
                    "supports_glonass": config["supports_glonass"],
                }
                for api_type, config in self.api_configs.items()
            },
            "rate_limits": self.rate_limits,
        }

    def clear_cache(self) -> None:
        """Очистка кэша"""
        self.cache.clear()
        self.logger.log("INFO", "Кэш российских API очищен")

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса менеджера"""
        return {
            "component_name": self.name,
            "status": self.status.name,
            "security_level": self.security_level.name,
            "api_count": len(self.api_configs),
            "cache_size": len(self.cache),
            "usage_stats": self.usage_stats,
        }

    def start_api(self) -> bool:
        """Запуск российских API"""
        try:
            self.status = ComponentStatus.RUNNING
            self.log_activity("Российские API запущены")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка запуска российских API: {e}", "error")
            return False

    def stop_api(self) -> bool:
        """Остановка российских API"""
        try:
            self.status = ComponentStatus.STOPPED
            self.log_activity("Российские API остановлены")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка остановки российских API: {e}", "error")
            return False

    def get_api_info(self) -> Dict[str, Any]:
        """Получение информации о российских API"""
        try:
            return {
                "is_running": self.status == ComponentStatus.RUNNING,
                "component_name": self.name,
                "api_count": len(self.api_configs),
                "api_types": len(RussianAPIType),
                "cache_size": len(self.cache),
                "security_level": self.security_level.name,
                "usage_stats": self.usage_stats,
                "supported_apis": [api_type.value for api_type in RussianAPIType],
                "last_activity": getattr(self, 'last_activity', None),
            }
        except Exception as e:
            self.log_activity(f"Ошибка получения информации о российских API: {e}", "error")
            return {
                "is_running": False,
                "component_name": self.name,
                "api_count": 0,
                "api_types": 0,
                "cache_size": 0,
                "security_level": "unknown",
                "usage_stats": {},
                "supported_apis": [],
                "last_activity": None,
                "error": str(e),
            }


# Создаем глобальный экземпляр
russian_api_manager = RussianAPIManager()
