#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
💭 Location Bubble Agent
Агент для генерации приблизительного местоположения (Bubbles Feature)

Функциональность:
- Показ приблизительного местоположения вместо точного
- Настройки радиуса (100м, 500м, 1км)
- Настройки для разных людей
- Настройки времени (разные радиусы в разное время)

Дата создания: 12 декабря 2025
Версия: 1.0.0
"""

import logging
import time
import math
import random
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

# Импорты (будут доступны на сервере)
try:
    from security.base import SecurityBase
    from security.ai_agents.threat_monitoring_interface import (
        ThreatMonitoringInterface,
        ThreatEvent,
        get_threat_event_bus
    )
except ImportError:
    # Для локальной разработки создаем заглушки
    class SecurityBase:
        def __init__(self, config: Optional[Dict[str, Any]] = None):
            config_dict = config if config is not None else {}
            self.config = config_dict
            self.logger = logging.getLogger(self.__class__.__name__)

    class ThreatMonitoringInterface:
        pass

    @dataclass
    class ThreatEvent:
        event_id: str = ""
        agent_name: str = ""
        threat_type: str = ""
        severity: str = ""
        source: str = ""
        target: str = ""
        timestamp: str = ""
        metadata: Dict[str, Any] = None
        description: Optional[str] = None

    def get_threat_event_bus():
        return None


class BubbleRadius(Enum):
    """Радиусы приблизительного местоположения"""
    SMALL = 100  # 100 метров
    MEDIUM = 500  # 500 метров
    LARGE = 1000  # 1 километр
    CUSTOM = 0  # Пользовательский радиус (задается в метрах)


@dataclass
class LocationCoordinates:
    """Координаты местоположения"""
    latitude: float
    longitude: float
    accuracy: Optional[float] = None  # Точность в метрах
    timestamp: Optional[float] = None  # Unix timestamp

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BubbleLocation:
    """Приблизительное местоположение (пузырь)"""
    approximate_latitude: float  # Приблизительная широта
    approximate_longitude: float  # Приблизительная долгота
    radius: int  # Радиус в метрах
    center_latitude: float  # Точная широта (не передается пользователю)
    center_longitude: float  # Точная долгота (не передается пользователю)
    generated_at: float  # Unix timestamp генерации
    accuracy: float  # Точность в метрах (равна радиусу)

    def to_dict(self) -> Dict[str, Any]:
        """Возвращает только приблизительные координаты (без точных)"""
        return {
            "approximate_latitude": self.approximate_latitude,
            "approximate_longitude": self.approximate_longitude,
            "radius": self.radius,
            "accuracy": self.accuracy,
            "generated_at": self.generated_at
        }

    def to_dict_full(self) -> Dict[str, Any]:
        """Возвращает полную информацию (включая точные координаты)"""
        return asdict(self)


@dataclass
class TimeBasedSettings:
    """Настройки по времени"""
    start_time: str  # "HH:MM" формат, например "09:00"
    end_time: str  # "HH:MM" формат, например "18:00"
    radius: BubbleRadius  # Радиус для этого времени
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['radius'] = self.radius.value
        return result


@dataclass
class PersonBubbleSettings:
    """Настройки пузыря для конкретного человека"""
    person_id: str  # ID человека
    default_radius: BubbleRadius  # Радиус по умолчанию
    time_based_settings: List[TimeBasedSettings] = None  # Настройки по времени
    enabled: bool = True  # Включен ли пузырь для этого человека

    def __post_init__(self):
        if self.time_based_settings is None:
            self.time_based_settings = []

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['default_radius'] = self.default_radius.value
        if self.time_based_settings:
            result['time_based_settings'] = [tbs.to_dict() for tbs in self.time_based_settings]
        return result


class LocationBubbleAgent(SecurityBase, ThreatMonitoringInterface):
    """
    Агент для генерации приблизительного местоположения (Bubbles Feature)

    Функциональность:
    - Генерация приблизительного местоположения с заданным радиусом
    - Настройки радиуса для разных людей
    - Настройки по времени (разные радиусы в разное время)
    - Хранение настроек пользователей
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация агента

        Args:
            config: Конфигурация агента
                - default_radius: Радиус по умолчанию (100, 500, 1000 метров)
                - enable_time_based: Включить ли настройки по времени (по умолчанию True)
        """
        super().__init__(config)

        # Инициализация логгера
        self.logger = logging.getLogger(self.__class__.__name__)

        # Конфигурация
        config_dict = config if config is not None else {}
        default_radius_value = config_dict.get("default_radius", 500)
        self.default_radius = BubbleRadius.MEDIUM
        if default_radius_value == 100:
            self.default_radius = BubbleRadius.SMALL
        elif default_radius_value == 500:
            self.default_radius = BubbleRadius.MEDIUM
        elif default_radius_value == 1000:
            self.default_radius = BubbleRadius.LARGE

        self.enable_time_based = config_dict.get("enable_time_based", True)

        # Словарь настроек для людей: {user_id: {person_id: PersonBubbleSettings}}
        self.user_person_settings: Dict[str, Dict[str, PersonBubbleSettings]] = {}

        # История генераций: {user_id: [BubbleLocation]}
        self.generation_history: Dict[str, List[BubbleLocation]] = {}

        # Интеграция с ThreatEventBus для уведомлений
        try:
            self.event_bus = get_threat_event_bus()
            if self.event_bus:
                self.event_bus.subscribe(self, event_types=["location_bubble", "*"])
                self.logger.info("✅ Подписан на ThreatEventBus")
        except Exception as e:
            self.logger.warning(f"⚠️ Не удалось подключиться к ThreatEventBus: {e}")
            self.event_bus = None

        self.logger.info("💭 LocationBubbleAgent инициализирован")

    def get_bubble_location(
        self,
        user_id: str,
        person_id: str,
        exact_latitude: float,
        exact_longitude: float,
        radius: Optional[int] = None,
        accuracy: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Генерация приблизительного местоположения (пузыря)

        Args:
            user_id: ID пользователя (родителя)
            person_id: ID человека, для которого генерируется пузырь
            exact_latitude: Точная широта
            exact_longitude: Точная долгота
            radius: Радиус в метрах (опционально, если не указан - используется настройка)
            accuracy: Точность исходных координат в метрах (опционально)

        Returns:
            Словарь с приблизительным местоположением:
            {
                "approximate_latitude": float,
                "approximate_longitude": float,
                "radius": int,
                "accuracy": float,
                "generated_at": float
            }
        """
        try:
            # Определяем радиус
            bubble_radius = self._get_radius_for_person(user_id, person_id, radius)

            # Генерируем приблизительное местоположение
            bubble_location = self._generate_bubble_location(
                exact_latitude,
                exact_longitude,
                bubble_radius
            )

            # Сохраняем в историю
            if user_id not in self.generation_history:
                self.generation_history[user_id] = []
            self.generation_history[user_id].append(bubble_location)

            # Ограничиваем историю (последние 100 записей)
            if len(self.generation_history[user_id]) > 100:
                self.generation_history[user_id] = self.generation_history[user_id][-100:]

            self.logger.info(
                f"✅ Сгенерирован пузырь для person_id={person_id}, "
                f"radius={bubble_radius}м, "
                f"смещение={self._calculate_distance(exact_latitude, exact_longitude, bubble_location.approximate_latitude, bubble_location.approximate_longitude):.1f}м"
            )

            # Возвращаем только приблизительные координаты (без точных)
            return bubble_location.to_dict()

        except Exception as e:
            self.logger.error(f"❌ Ошибка генерации пузыря: {e}")
            raise

    def _generate_bubble_location(
        self,
        center_latitude: float,
        center_longitude: float,
        radius_meters: int
    ) -> BubbleLocation:
        """
        Генерация приблизительного местоположения в пределах радиуса

        Args:
            center_latitude: Точная широта центра
            center_longitude: Точная долгота центра
            radius_meters: Радиус в метрах

        Returns:
            BubbleLocation с приблизительными координатами
        """
        # Генерируем случайное расстояние от центра (0 до radius)
        distance = random.uniform(0, radius_meters)

        # Генерируем случайный угол (0 до 2π)
        angle = random.uniform(0, 2 * math.pi)

        # Вычисляем смещение в метрах
        # 1 градус широты ≈ 111 км
        # 1 градус долготы ≈ 111 км * cos(широта)
        lat_offset = (distance * math.cos(angle)) / 111000.0
        lon_offset = (distance * math.sin(angle)) / (111000.0 * math.cos(math.radians(center_latitude)))

        # Вычисляем приблизительные координаты
        approximate_latitude = center_latitude + lat_offset
        approximate_longitude = center_longitude + lon_offset

        return BubbleLocation(
            approximate_latitude=approximate_latitude,
            approximate_longitude=approximate_longitude,
            radius=radius_meters,
            center_latitude=center_latitude,
            center_longitude=center_longitude,
            generated_at=time.time(),
            accuracy=float(radius_meters)
        )

    def _get_radius_for_person(
        self,
        user_id: str,
        person_id: str,
        requested_radius: Optional[int] = None
    ) -> int:
        """
        Получить радиус для конкретного человека

        Args:
            user_id: ID пользователя
            person_id: ID человека
            requested_radius: Запрошенный радиус (если указан, используется он)

        Returns:
            Радиус в метрах
        """
        # Если радиус указан явно, используем его
        if requested_radius is not None:
            return requested_radius

        # Получаем настройки для этого человека
        settings = self.get_person_settings(user_id, person_id)

        # Если настройки по времени включены, проверяем текущее время
        if self.enable_time_based and settings.time_based_settings:
            current_time = datetime.now().time()
            for time_setting in settings.time_based_settings:
                if not time_setting.enabled:
                    continue

                try:
                    start = datetime.strptime(time_setting.start_time, "%H:%M").time()
                    end = datetime.strptime(time_setting.end_time, "%H:%M").time()

                    # Проверяем, попадает ли текущее время в диапазон
                    if start <= end:
                        # Обычный диапазон (например, 09:00-18:00)
                        if start <= current_time <= end:
                            return time_setting.radius.value
                    else:
                        # Диапазон через полночь (например, 22:00-06:00)
                        if current_time >= start or current_time <= end:
                            return time_setting.radius.value
                except Exception as e:
                    self.logger.warning(f"⚠️ Ошибка парсинга времени: {e}")
                    continue

        # Используем радиус по умолчанию
        return settings.default_radius.value

    def set_person_settings(
        self,
        user_id: str,
        person_id: str,
        default_radius: BubbleRadius,
        time_based_settings: Optional[List[TimeBasedSettings]] = None,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Установить настройки пузыря для конкретного человека

        Args:
            user_id: ID пользователя
            person_id: ID человека
            default_radius: Радиус по умолчанию
            time_based_settings: Настройки по времени (опционально)
            enabled: Включен ли пузырь

        Returns:
            Словарь с настройками
        """
        if user_id not in self.user_person_settings:
            self.user_person_settings[user_id] = {}

        settings = PersonBubbleSettings(
            person_id=person_id,
            default_radius=default_radius,
            time_based_settings=time_based_settings or [],
            enabled=enabled
        )

        self.user_person_settings[user_id][person_id] = settings

        self.logger.info(
            f"✅ Настройки пузыря установлены для person_id={person_id}, "
            f"default_radius={default_radius.value}м, enabled={enabled}"
        )

        return settings.to_dict()

    def get_person_settings(
        self,
        user_id: str,
        person_id: str
    ) -> PersonBubbleSettings:
        """
        Получить настройки пузыря для конкретного человека

        Args:
            user_id: ID пользователя
            person_id: ID человека

        Returns:
            PersonBubbleSettings (если нет настроек - возвращает настройки по умолчанию)
        """
        if user_id in self.user_person_settings:
            if person_id in self.user_person_settings[user_id]:
                return self.user_person_settings[user_id][person_id]

        # Возвращаем настройки по умолчанию
        return PersonBubbleSettings(
            person_id=person_id,
            default_radius=self.default_radius,
            time_based_settings=[],
            enabled=True
        )

    def get_all_person_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Получить все настройки пузырей для пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Словарь {person_id: settings}
        """
        if user_id not in self.user_person_settings:
            return {}

        return {
            person_id: settings.to_dict()
            for person_id, settings in self.user_person_settings[user_id].items()
        }

    def get_generation_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Получить историю генераций пузырей

        Args:
            user_id: ID пользователя
            limit: Максимальное количество записей

        Returns:
            Список словарей с историей
        """
        if user_id not in self.generation_history:
            return []

        history = self.generation_history[user_id][-limit:]
        return [bubble.to_dict() for bubble in history]

    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Вычислить расстояние между двумя точками (формула гаверсинуса)

        Args:
            lat1, lon1: Координаты первой точки
            lat2, lon2: Координаты второй точки

        Returns:
            Расстояние в метрах
        """
        R = 6371000  # Радиус Земли в метрах

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    # Реализация ThreatMonitoringInterface
    def collect_threats(self) -> List[Dict[str, Any]]:
        """Сбор угроз (не используется для этого агента)"""
        return []

    def analyze_threats(self, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Анализ угроз (не используется для этого агента)"""
        return []

    def send_alert(self, alert: Dict[str, Any]):
        """Отправка алерта (не используется для этого агента)"""
        pass
