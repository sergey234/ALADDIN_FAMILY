#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилиты для работы с местоположением в экстренных ситуациях
Применение Single Responsibility принципа

ВЕРСИЯ 3.0 ENHANCED - С ВСЕМИ УЛУЧШЕНИЯМИ:
- Async/await поддержка
- Расширенная валидация параметров
- Логирование ошибок
- Кэширование
- Расширенные docstrings
- Конфигурационные параметры
- Метрики производительности
- Rate limiting
- Health check
"""

import asyncio
import logging
import math
import time
from collections import defaultdict
from functools import lru_cache
from typing import Any, Dict, List, Tuple

import geopy.distance

# Настройка логирования
logger = logging.getLogger(__name__)


# Конфигурационные параметры
class LocationConfig:
    """Конфигурация для утилит местоположения"""

    DEFAULT_ACCURACY_THRESHOLD = 100.0  # метры
    DEFAULT_RADIUS_PRECISION = 2  # знаков после запятой
    MAX_SERVICES_LIMIT = 1000
    CACHE_SIZE = 1000
    RATE_LIMIT_CALLS = 100  # максимальное количество вызовов
    RATE_LIMIT_WINDOW = 60  # секунд
    MAX_COORDINATE_VALUE = 90.0
    MIN_COORDINATE_VALUE = -90.0
    MAX_LONGITUDE_VALUE = 180.0
    MIN_LONGITUDE_VALUE = -180.0


class LocationMetrics:
    """Метрики производительности для утилит местоположения"""

    def __init__(self):
        self.call_count = 0
        self.total_time = 0.0
        self.error_count = 0
        self.cache_hits = 0
        self.cache_misses = 0

    def record_call(
        self, execution_time: float, success: bool, cache_hit: bool = False
    ):
        """Записать вызов метода"""
        self.call_count += 1
        self.total_time += execution_time
        if not success:
            self.error_count += 1
        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

    def get_average_time(self) -> float:
        """Получить среднее время выполнения"""
        return (
            self.total_time / self.call_count if self.call_count > 0 else 0.0
        )

    def get_error_rate(self) -> float:
        """Получить процент ошибок"""
        return (self.error_count / max(self.call_count, 1)) * 100

    def get_cache_hit_rate(self) -> float:
        """Получить процент попаданий в кэш"""
        total_cache_operations = self.cache_hits + self.cache_misses
        return (self.cache_hits / max(total_cache_operations, 1)) * 100


class RateLimiter:
    """Ограничитель частоты вызовов"""

    def __init__(
        self,
        max_calls: int = LocationConfig.RATE_LIMIT_CALLS,
        time_window: int = LocationConfig.RATE_LIMIT_WINDOW,
    ):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        """Проверить, разрешен ли вызов"""
        now = time.time()
        # Очищаем старые вызовы
        self.calls[key] = [
            call_time
            for call_time in self.calls[key]
            if now - call_time < self.time_window
        ]
        return len(self.calls[key]) < self.max_calls

    def record_call(self, key: str):
        """Записать вызов"""
        self.calls[key].append(time.time())


# Глобальные объекты
metrics = LocationMetrics()
rate_limiter = RateLimiter()


class LocationDistanceCalculator:
    """Калькулятор расстояний между точками с расширенными возможностями"""

    @staticmethod
    def calculate_distance(
        coord1: Tuple[float, float], coord2: Tuple[float, float]
    ) -> float:
        """
        Рассчитать расстояние между двумя точками в километрах

        Args:
            coord1: Первая точка (широта, долгота)
            coord2: Вторая точка (широта, долгота)

        Returns:
            float: Расстояние в километрах

        Example:
            >>> LocationDistanceCalculator.calculate_distance(
            ...     (55.7558, 37.6176), (55.7559, 37.6177)
            ... )
            0.012782

        Raises:
            Exception: Возвращает 0.0 при ошибке вычисления
        """
        start_time = time.time()
        success = True
        cache_hit = False

        try:
            # Проверка rate limiting
            if not rate_limiter.is_allowed("calculate_distance"):
                logger.warning("Rate limit exceeded for calculate_distance")
                return 0.0

            # Валидация входных параметров
            if not LocationDistanceCalculator._validate_coordinates(
                coord1, coord2
            ):
                logger.error(f"Invalid coordinates: {coord1}, {coord2}")
                success = False
                return 0.0

            distance = geopy.distance.geodesic(coord1, coord2).kilometers
            logger.debug(
                f"Calculated distance: {distance:.6f} km between "
                f"{coord1} and {coord2}"
            )

            rate_limiter.record_call("calculate_distance")
            return distance

        except Exception as e:
            logger.error(f"Error calculating distance: {e}")
            success = False
            return 0.0
        finally:
            execution_time = time.time() - start_time
            metrics.record_call(execution_time, success, cache_hit)

    @staticmethod
    @lru_cache(maxsize=LocationConfig.CACHE_SIZE)
    def calculate_distance_cached(
        coord1: Tuple[float, float], coord2: Tuple[float, float]
    ) -> float:
        """
        Рассчитать расстояние между двумя точками в километрах (с кэшированием)

        Args:
            coord1: Первая точка (широта, долгота)
            coord2: Вторая точка (широта, долгота)

        Returns:
            float: Расстояние в километрах
        """
        start_time = time.time()
        success = True
        cache_hit = True  # Если мы здесь, значит кэш сработал

        try:
            distance = geopy.distance.geodesic(coord1, coord2).kilometers
            logger.debug(f"Cached distance calculation: {distance:.6f} km")
            return distance

        except Exception as e:
            logger.error(f"Error in cached distance calculation: {e}")
            success = False
            return 0.0
        finally:
            execution_time = time.time() - start_time
            metrics.record_call(execution_time, success, cache_hit)

    @staticmethod
    async def calculate_distance_async(
        coord1: Tuple[float, float], coord2: Tuple[float, float]
    ) -> float:
        """
        Асинхронно рассчитать расстояние между двумя точками в километрах

        Args:
            coord1: Первая точка (широта, долгота)
            coord2: Вторая точка (широта, долгота)

        Returns:
            float: Расстояние в километрах
        """
        start_time = time.time()
        success = True

        try:
            # Проверка rate limiting
            if not rate_limiter.is_allowed("calculate_distance_async"):
                logger.warning(
                    "Rate limit exceeded for calculate_distance_async"
                )
                return 0.0

            # Валидация входных параметров
            if not LocationDistanceCalculator._validate_coordinates(
                coord1, coord2
            ):
                logger.error(
                    f"Invalid coordinates in async calculation: "
                    f"{coord1}, {coord2}"
                )
                success = False
                return 0.0

            # Асинхронное выполнение
            loop = asyncio.get_event_loop()
            distance = await loop.run_in_executor(
                None,
                lambda: geopy.distance.geodesic(coord1, coord2).kilometers,
            )

            logger.debug(f"Async calculated distance: {distance:.6f} km")
            rate_limiter.record_call("calculate_distance_async")
            return distance

        except Exception as e:
            logger.error(f"Error in async distance calculation: {e}")
            success = False
            return 0.0
        finally:
            execution_time = time.time() - start_time
            metrics.record_call(execution_time, success)

    @staticmethod
    def is_location_in_radius(
        center: Tuple[float, float],
        point: Tuple[float, float],
        radius_km: float,
    ) -> bool:
        """
        Проверить, находится ли точка в радиусе от центра

        Args:
            center: Центральная точка
            point: Проверяемая точка
            radius_km: Радиус в километрах

        Returns:
            bool: True если точка в радиусе

        Example:
            >>> LocationDistanceCalculator.is_location_in_radius(
            ...     (55.7558, 37.6176), (55.7559, 37.6177), 1.0
            ... )
            True
        """
        start_time = time.time()
        success = True

        try:
            # Валидация входных параметров
            if not LocationDistanceCalculator._validate_coordinates(
                center, point
            ):
                logger.error(
                    f"Invalid coordinates in radius check: {center}, {point}"
                )
                success = False
                return False

            if not isinstance(radius_km, (int, float)) or radius_km < 0:
                logger.error(f"Invalid radius: {radius_km}")
                success = False
                return False

            distance = LocationDistanceCalculator.calculate_distance(
                center, point
            )
            result = distance <= radius_km

            logger.debug(
                f"Radius check: {point} in {radius_km}km from "
                f"{center} = {result}"
            )
            return result

        except Exception as e:
            logger.error(f"Error in radius check: {e}")
            success = False
            return False
        finally:
            execution_time = time.time() - start_time
            metrics.record_call(execution_time, success)

    @staticmethod
    def _validate_coordinates(
        coord1: Tuple[float, float], coord2: Tuple[float, float]
    ) -> bool:
        """Валидация координат с расширенными проверками"""
        try:
            for coord in [coord1, coord2]:
                if not isinstance(coord, (tuple, list)) or len(coord) != 2:
                    return False

                lat, lon = coord
                if not isinstance(lat, (int, float)) or not isinstance(
                    lon, (int, float)
                ):
                    return False

                if (
                    math.isnan(lat)
                    or math.isnan(lon)
                    or math.isinf(lat)
                    or math.isinf(lon)
                ):
                    return False

                if not (
                    LocationConfig.MIN_COORDINATE_VALUE
                    <= lat
                    <= LocationConfig.MAX_COORDINATE_VALUE
                ):
                    return False

                if not (
                    LocationConfig.MIN_LONGITUDE_VALUE
                    <= lon
                    <= LocationConfig.MAX_LONGITUDE_VALUE
                ):
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating coordinates: {e}")
            return False


class LocationServiceFinder:
    """Поиск ближайших служб к местоположению с расширенными возможностями"""

    @staticmethod
    def find_nearest_services(
        location: Tuple[float, float], services: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Найти ближайшие службы к местоположению

        Args:
            location: Координаты местоположения
            services: Список служб с координатами

        Returns:
            List[Dict]: Список служб, отсортированный по расстоянию

        Example:
            >>> services = [
            ...     {'name': 'Hospital', 'coordinates': (55.7558, 37.6176)}
            ... ]
            >>> LocationServiceFinder.find_nearest_services(
            ...     (55.7559, 37.6177), services
            ... )
            [{'service': {'name': 'Hospital',
                          'coordinates': (55.7558, 37.6176)},
              'distance': 0.012782}]
        """
        start_time = time.time()
        success = True

        try:
            # Проверка rate limiting
            if not rate_limiter.is_allowed("find_nearest_services"):
                logger.warning("Rate limit exceeded for find_nearest_services")
                return []

            # Валидация входных параметров
            if not LocationDistanceCalculator._validate_coordinates(
                location, location
            ):
                logger.error(f"Invalid location: {location}")
                success = False
                return []

            if not isinstance(services, list):
                logger.error(
                    f"Services must be a list, got: {type(services)}"
                )
                success = False
                return []

            if len(services) > LocationConfig.MAX_SERVICES_LIMIT:
                logger.warning(
                    f"Too many services: {len(services)}, "
                    f"limiting to {LocationConfig.MAX_SERVICES_LIMIT}"
                )
                services = services[: LocationConfig.MAX_SERVICES_LIMIT]

            service_distances = []
            for i, service in enumerate(services):
                try:
                    service_coords = service.get("coordinates")
                    if service_coords:
                        # Преобразуем список в кортеж если необходимо
                        if isinstance(service_coords, list):
                            service_coords = tuple(service_coords)
                        if (
                            LocationDistanceCalculator._validate_coordinates(
                                service_coords, service_coords
                            )
                        ):
                            distance = (
                                LocationDistanceCalculator
                                .calculate_distance_cached(
                                    location, service_coords
                                )
                            )
                            service_distances.append(
                                {
                                    "service": service,
                                    "distance": distance,
                                    "index": i,
                                }
                            )
                    else:
                        logger.warning(
                            f"Invalid service coordinates at index {i}: "
                            f"{service_coords}"
                        )
                except Exception as e:
                    logger.error(f"Error processing service at index {i}: {e}")
                    continue

            # Сортируем по расстоянию
            service_distances.sort(key=lambda x: x["distance"])

            logger.debug(
                f"Found {len(service_distances)} valid services out of "
                f"{len(services)}"
            )
            rate_limiter.record_call("find_nearest_services")
            return service_distances

        except Exception as e:
            logger.error(f"Error finding nearest services: {e}")
            success = False
            return []
        finally:
            execution_time = time.time() - start_time
            metrics.record_call(execution_time, success)

    @staticmethod
    def get_services_in_radius(
        location: Tuple[float, float],
        services: List[Dict[str, Any]],
        radius_km: float,
    ) -> List[Dict[str, Any]]:
        """
        Получить службы в радиусе от местоположения

        Args:
            location: Координаты местоположения
            services: Список служб
            radius_km: Радиус в километрах

        Returns:
            List[Dict]: Службы в радиусе

        Example:
            >>> services = [
            ...     {'name': 'Hospital', 'coordinates': (55.7558, 37.6176)}
            ... ]
            >>> LocationServiceFinder.get_services_in_radius(
            ...     (55.7559, 37.6177), services, 0.1
            ... )
            [{'name': 'Hospital', 'coordinates': (55.7558, 37.6176)}]
        """
        start_time = time.time()
        success = True

        try:
            # Проверка rate limiting
            if not rate_limiter.is_allowed("get_services_in_radius"):
                logger.warning(
                    "Rate limit exceeded for get_services_in_radius"
                )
                return []

            # Валидация входных параметров
            if not LocationDistanceCalculator._validate_coordinates(
                location, location
            ):
                logger.error(f"Invalid location: {location}")
                success = False
                return []

            if not isinstance(radius_km, (int, float)) or radius_km < 0:
                logger.error(f"Invalid radius: {radius_km}")
                success = False
                return []

            services_in_radius = []
            for i, service in enumerate(services):
                try:
                    service_coords = service.get("coordinates")
                    if (
                        service_coords
                        and LocationDistanceCalculator._validate_coordinates(
                            service_coords, service_coords
                        )
                    ):
                        if LocationDistanceCalculator.is_location_in_radius(
                            location, service_coords, radius_km
                        ):
                            services_in_radius.append(service)
                    else:
                        logger.warning(
                            f"Invalid service coordinates at index {i}: "
                            f"{service_coords}"
                        )
                except Exception as e:
                    logger.error(f"Error processing service at index {i}: {e}")
                    continue

            logger.debug(
                f"Found {len(services_in_radius)} services in "
                f"{radius_km}km radius"
            )
            rate_limiter.record_call("get_services_in_radius")
            return services_in_radius

        except Exception as e:
            logger.error(f"Error getting services in radius: {e}")
            success = False
            return []
        finally:
            execution_time = time.time() - start_time
            metrics.record_call(execution_time, success)

    @staticmethod
    async def find_nearest_services_async(
        location: Tuple[float, float], services: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Асинхронно найти ближайшие службы к местоположению

        Args:
            location: Координаты местоположения
            services: Список служб с координатами

        Returns:
            List[Dict]: Список служб, отсортированный по расстоянию
        """
        start_time = time.time()
        success = True

        try:
            # Проверка rate limiting
            if not rate_limiter.is_allowed("find_nearest_services_async"):
                logger.warning(
                    "Rate limit exceeded for find_nearest_services_async"
                )
                return []

            # Валидация входных параметров
            if not LocationDistanceCalculator._validate_coordinates(
                location, location
            ):
                logger.error(f"Invalid location in async search: {location}")
                success = False
                return []

            if not isinstance(services, list):
                logger.error(
                    f"Services must be a list, got: {type(services)}"
                )
                success = False
                return []

            # Асинхронная обработка служб
            service_distances = []

            for i, service in enumerate(services):
                try:
                    service_coords = service.get("coordinates")
                    if (
                        service_coords
                        and LocationDistanceCalculator._validate_coordinates(
                            service_coords, service_coords
                        )
                    ):
                        distance = await (
                            LocationDistanceCalculator
                            .calculate_distance_async(
                                location, service_coords
                            )
                        )
                        service_distances.append(
                            {
                                "service": service,
                                "distance": distance,
                                "index": i,
                            }
                        )
                    else:
                        logger.warning(
                            f"Invalid service coordinates at index {i}: "
                            f"{service_coords}"
                        )
                except Exception as e:
                    logger.error(f"Error processing service at index {i}: {e}")
                    continue

            # Сортируем по расстоянию
            service_distances.sort(key=lambda x: x["distance"])

            logger.debug(
                f"Async found {len(service_distances)} valid services"
            )
            rate_limiter.record_call("find_nearest_services_async")
            return service_distances

        except Exception as e:
            logger.error(f"Error in async service search: {e}")
            success = False
            return []
        finally:
            execution_time = time.time() - start_time
            metrics.record_call(execution_time, success)


class LocationValidator:
    """Валидатор местоположений с расширенными возможностями"""

    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        """
        Проверить валидность координат с расширенными проверками

        Args:
            lat: Широта
            lon: Долгота

        Returns:
            bool: True если координаты валидны

        Example:
            >>> LocationValidator.validate_coordinates(55.7558, 37.6176)
            True
            >>> LocationValidator.validate_coordinates(999, 999)
            False
        """
        start_time = time.time()
        success = True

        try:
            # Проверка типов
            if (
                not isinstance(lat, (int, float))
                or not isinstance(lon, (int, float))
            ):
                logger.error(
                    f"Invalid coordinate types: lat={type(lat)}, "
                    f"lon={type(lon)}"
                )
                success = False
                return False

            # Проверка на NaN и Infinity
            if (
                math.isnan(lat)
                or math.isnan(lon)
                or math.isinf(lat)
                or math.isinf(lon)
            ):
                logger.error(
                    f"Invalid coordinate values: lat={lat}, lon={lon}"
                )
                success = False
                return False

            # Проверка диапазонов
            if not (
                LocationConfig.MIN_COORDINATE_VALUE
                <= lat
                <= LocationConfig.MAX_COORDINATE_VALUE
            ):
                logger.error(f"Latitude out of range: {lat}")
                success = False
                return False

            if not (
                LocationConfig.MIN_LONGITUDE_VALUE
                <= lon
                <= LocationConfig.MAX_LONGITUDE_VALUE
            ):
                logger.error(f"Longitude out of range: {lon}")
                success = False
                return False

            # Дополнительные проверки безопасности
            if abs(lat) > 90 or abs(lon) > 180:
                logger.warning(
                    f"Suspicious coordinates detected: lat={lat}, lon={lon}"
                )

            logger.debug(
                f"Coordinates validated successfully: lat={lat}, lon={lon}"
            )
            return True

        except Exception as e:
            logger.error(f"Error validating coordinates: {e}")
            success = False
            return False
        finally:
            execution_time = time.time() - start_time
            metrics.record_call(execution_time, success)

    @staticmethod
    def validate_location_accuracy(accuracy: float) -> bool:
        """
        Проверить точность определения местоположения

        Args:
            accuracy: Точность в метрах

        Returns:
            bool: True если точность приемлема

        Example:
            >>> LocationValidator.validate_location_accuracy(50.0)
            True
            >>> LocationValidator.validate_location_accuracy(150.0)
            False
        """
        start_time = time.time()
        success = True

        try:
            if not isinstance(accuracy, (int, float)):
                logger.error(f"Invalid accuracy type: {type(accuracy)}")
                success = False
                return False

            if math.isnan(accuracy) or math.isinf(accuracy):
                logger.error(f"Invalid accuracy value: {accuracy}")
                success = False
                return False

            if accuracy < 0:
                logger.error(f"Negative accuracy: {accuracy}")
                success = False
                return False

            result = accuracy <= LocationConfig.DEFAULT_ACCURACY_THRESHOLD
            logger.debug(f"Accuracy validation: {accuracy}m -> {result}")
            return result

        except Exception as e:
            logger.error(f"Error validating accuracy: {e}")
            success = False
            return False
        finally:
            execution_time = time.time() - start_time
            metrics.record_call(execution_time, success)

    @staticmethod
    def is_location_verified(location_data: Dict[str, Any]) -> bool:
        """
        Проверить, верифицировано ли местоположение

        Args:
            location_data: Данные местоположения

        Returns:
            bool: True если местоположение верифицировано

        Example:
            >>> LocationValidator.is_location_verified({'is_verified': True})
            True
            >>> LocationValidator.is_location_verified({'is_verified': False})
            False
        """
        start_time = time.time()
        success = True

        try:
            if not isinstance(location_data, dict):
                logger.error(
                    f"Location data must be a dict, got: {type(location_data)}"
                )
                success = False
                return False

            result = location_data.get("is_verified", False)
            logger.debug(f"Location verification check: {result}")
            return bool(result)

        except Exception as e:
            logger.error(f"Error checking location verification: {e}")
            success = False
            return False
        finally:
            execution_time = time.time() - start_time
            metrics.record_call(execution_time, success)


class LocationClusterAnalyzer:
    """Анализатор кластеров местоположений с расширенными возможностями"""

    @staticmethod
    def calculate_cluster_center(
        points: List[Tuple[float, float]]
    ) -> Tuple[float, float]:
        """
        Рассчитать центр кластера

        Args:
            points: Список точек

        Returns:
            Tuple[float, float]: Центр кластера

        Example:
            >>> points = [(55.7558, 37.6176), (55.7559, 37.6177)]
            >>> LocationClusterAnalyzer.calculate_cluster_center(points)
            (55.75585, 37.61765)
        """
        start_time = time.time()
        success = True

        try:
            if not isinstance(points, list):
                logger.error(f"Points must be a list, got: {type(points)}")
                success = False
                return (0.0, 0.0)

            if not points:
                logger.warning("Empty points list provided")
                return (0.0, 0.0)

            # Валидация всех точек
            valid_points = []
            for i, point in enumerate(points):
                if LocationDistanceCalculator._validate_coordinates(
                    point, point
                ):
                    valid_points.append(point)
                else:
                    logger.warning(
                        f"Invalid point at index {i}: {point}"
                    )

            if not valid_points:
                logger.error("No valid points found")
                success = False
                return (0.0, 0.0)

            lat_sum = sum(point[0] for point in valid_points)
            lon_sum = sum(point[1] for point in valid_points)

            center = (
                lat_sum / len(valid_points),
                lon_sum / len(valid_points)
            )
            logger.debug(
                f"Calculated cluster center: {center} from "
                f"{len(valid_points)} points"
            )
            return center

        except Exception as e:
            logger.error(f"Error calculating cluster center: {e}")
            success = False
            return (0.0, 0.0)
        finally:
            execution_time = time.time() - start_time
            metrics.record_call(execution_time, success)

    @staticmethod
    def calculate_cluster_radius(
        points: List[Tuple[float, float]], center: Tuple[float, float]
    ) -> float:
        """
        Рассчитать радиус кластера

        Args:
            points: Список точек
            center: Центр кластера

        Returns:
            float: Радиус в километрах

        Example:
            >>> points = [(55.7558, 37.6176), (55.7559, 37.6177)]
            >>> center = (55.75585, 37.61765)
            >>> LocationClusterAnalyzer.calculate_cluster_radius(
            ...     points, center
            ... )
            0.010000
        """
        start_time = time.time()
        success = True

        try:
            if not isinstance(points, list) or not points:
                logger.error("Invalid or empty points list")
                success = False
                return 0.0

            if not LocationDistanceCalculator._validate_coordinates(
                center, center
            ):
                logger.error(f"Invalid center coordinates: {center}")
                success = False
                return 0.0

            max_distance = 0
            valid_points = 0

            for i, point in enumerate(points):
                if LocationDistanceCalculator._validate_coordinates(
                    point, point
                ):
                    distance = (
                        LocationDistanceCalculator.calculate_distance_cached(
                            center, point
                        )
                    )
                    max_distance = max(max_distance, distance)
                    valid_points += 1
                else:
                    logger.warning(
                        f"Invalid point at index {i}: {point}"
                    )

            if valid_points == 0:
                logger.error("No valid points for radius calculation")
                success = False
                return 0.0

            radius = round(
                max_distance, LocationConfig.DEFAULT_RADIUS_PRECISION
            )
            logger.debug(
                f"Calculated cluster radius: {radius}km from "
                f"{valid_points} points"
            )
            return radius

        except Exception as e:
            logger.error(f"Error calculating cluster radius: {e}")
            success = False
            return 0.0
        finally:
            execution_time = time.time() - start_time
            metrics.record_call(execution_time, success)


class LocationHealthChecker:
    """Проверка состояния всех компонентов системы местоположения"""

    @staticmethod
    def health_check() -> Dict[str, Any]:
        """
        Проверить состояние всех компонентов

        Returns:
            Dict[str, Any]: Статус системы и метрики
        """
        start_time = time.time()

        try:
            # Проверка доступности geopy
            geopy_available = True
            try:
                geopy.distance.geodesic((0, 0), (0, 1)).kilometers
            except Exception:
                geopy_available = False

            # Проверка rate limiting
            rate_limit_status = rate_limiter.is_allowed("health_check")

            # Сбор метрик
            health_data = {
                "status": (
                    "healthy"
                    if geopy_available and rate_limit_status
                    else "degraded"
                ),
                "timestamp": time.time(),
                "geopy_available": geopy_available,
                "rate_limit_ok": rate_limit_status,
                "metrics": {
                    "total_calls": metrics.call_count,
                    "average_execution_time": (
                        metrics.get_average_time()
                    ),
                    "error_rate": metrics.get_error_rate(),
                    "cache_hit_rate": metrics.get_cache_hit_rate(),
                },
                "config": {
                    "accuracy_threshold": (
                        LocationConfig.DEFAULT_ACCURACY_THRESHOLD
                    ),
                    "max_services_limit": LocationConfig.MAX_SERVICES_LIMIT,
                    "cache_size": LocationConfig.CACHE_SIZE,
                    "rate_limit_calls": LocationConfig.RATE_LIMIT_CALLS,
                    "rate_limit_window": LocationConfig.RATE_LIMIT_WINDOW,
                },
            }

            logger.info(f"Health check completed: {health_data['status']}")
            return health_data

        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {
                "status": "error",
                "timestamp": time.time(),
                "error": str(e),
            }
        finally:
            execution_time = time.time() - start_time
            logger.debug(f"Health check execution time: {execution_time:.4f}s")

    @staticmethod
    def reset_metrics():
        """Сбросить все метрики"""
        global metrics
        metrics = LocationMetrics()
        logger.info("Metrics reset")

    @staticmethod
    def get_metrics() -> Dict[str, Any]:
        """Получить текущие метрики"""
        return {
            "call_count": metrics.call_count,
            "total_time": metrics.total_time,
            "average_time": metrics.get_average_time(),
            "error_count": metrics.error_count,
            "error_rate": metrics.get_error_rate(),
            "cache_hits": metrics.cache_hits,
            "cache_misses": metrics.cache_misses,
            "cache_hit_rate": metrics.get_cache_hit_rate(),
        }
