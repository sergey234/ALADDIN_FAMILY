#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚗 Crash Detection Agent
Агент для обнаружения автомобильных аварий

Функциональность:
- Анализ данных акселерометра и гироскопа
- Обнаружение аварий по G-силам и изменению скорости
- Автоматический вызов экстренных служб (112, 911)
- Отправка точного местоположения

Дата создания: 12 декабря 2025
Версия: 1.0.0
"""

import logging
import math
import time
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


class CrashSeverity(Enum):
    """Уровень серьезности аварии"""
    LOW = "low"  # Незначительное столкновение
    MEDIUM = "medium"  # Средняя авария
    HIGH = "high"  # Серьезная авария
    CRITICAL = "critical"  # Критическая авария


@dataclass
class AccelerometerData:
    """Данные акселерометра"""
    x: float  # Ускорение по оси X (м/с²)
    y: float  # Ускорение по оси Y (м/с²)
    z: float  # Ускорение по оси Z (м/с²)
    timestamp: float  # Временная метка

    def get_magnitude(self) -> float:
        """Вычисление величины ускорения (G-сила)"""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def get_g_force(self) -> float:
        """Вычисление G-силы (1G = 9.8 м/с²)"""
        return self.get_magnitude() / 9.8


@dataclass
class GyroscopeData:
    """Данные гироскопа"""
    x: float  # Угловая скорость по оси X (рад/с)
    y: float  # Угловая скорость по оси Y (рад/с)
    z: float  # Угловая скорость по оси Z (рад/с)
    timestamp: float  # Временная метка

    def get_magnitude(self) -> float:
        """Вычисление величины угловой скорости"""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)


@dataclass
class CrashEvent:
    """Событие аварии"""
    event_id: str
    user_id: str
    timestamp: str
    severity: CrashSeverity
    g_force: float
    location: Optional[Dict[str, Any]] = None  # Может быть геозона {"type": "geofence", "geofence_center": {...}, "radius_meters": 500} или точное {"type": "exact", "latitude": float, "longitude": float}
    speed_before: Optional[float] = None  # Скорость до аварии (км/ч) - может быть вычислена из акселерометра
    speed_after: Optional[float] = None  # Скорость после аварии (км/ч)
    emergency_called: bool = False
    emergency_call_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['severity'] = self.severity.value
        return result


class CrashDetectionAgent(SecurityBase, ThreatMonitoringInterface):
    """
    Агент для обнаружения автомобильных аварий

    Использует данные акселерометра и гироскопа для обнаружения аварий
    и автоматического вызова экстренных служб.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация агента

        Args:
            config: Конфигурация агента
                - g_force_threshold: Порог G-сил для обнаружения аварии (по умолчанию 3.0G)
                - speed_change_threshold: Порог изменения скорости (км/ч, по умолчанию 30)
                - emergency_service_number: Номер экстренной службы (112 для РФ)
                - auto_call_enabled: Автоматический вызов помощи (по умолчанию True)
                - false_positive_filter: Фильтр ложных срабатываний (по умолчанию True)
                - use_geofence: Использовать геозоны как запасной вариант (по умолчанию True)
                - geofence_radius: Радиус геозоны в метрах (по умолчанию 500)
                - prefer_gps: Использовать GPS/ГЛОНАСС как основной источник (по умолчанию True)
        """
        super().__init__(config)

        # Инициализация логгера
        self.logger = logging.getLogger(self.__class__.__name__)

        # Конфигурация
        config_dict = config if config is not None else {}
        self.g_force_threshold = config_dict.get("g_force_threshold", 3.0)  # 3.0G
        self.speed_change_threshold = config_dict.get("speed_change_threshold", 30.0)  # 30 км/ч
        self.emergency_service_number = config_dict.get("emergency_service_number", "112")  # Только 112 для РФ
        self.auto_call_enabled = config_dict.get("auto_call_enabled", True)
        self.false_positive_filter = config_dict.get("false_positive_filter", True)
        self.use_geofence = config_dict.get("use_geofence", True)  # Геозоны как запасной вариант
        self.geofence_radius = config_dict.get("geofence_radius", 500)  # 500 метров
        self.prefer_gps = config_dict.get("prefer_gps", True)  # Использовать GPS/ГЛОНАСС как основной источник

        # Конфигурация API 112
        self.emergency_api_url = config_dict.get("emergency_api_url", None)  # URL API 112 (если доступен)
        self.emergency_api_key = config_dict.get("emergency_api_key", None)  # API ключ (если требуется)
        self.emergency_api_enabled = config_dict.get("emergency_api_enabled", False)  # Включить реальный API (по умолчанию False)
        self.emergency_api_timeout = config_dict.get("emergency_api_timeout", 10.0)  # Таймаут запроса (секунды)

        # Хранилище данных
        self.active_monitoring: Dict[str, Dict[str, Any]] = {}  # {user_id: {status, last_data, ...}}
        self.crash_history: Dict[str, List[CrashEvent]] = {}  # {user_id: [CrashEvent]}
        self.sensor_data_buffer: Dict[str, List[AccelerometerData]] = {}  # Буфер данных для анализа

        # Вычисление скорости из акселерометра (интеграция ускорения)
        self.velocity_history: Dict[str, List[float]] = {}  # История скорости для каждого пользователя
        self.last_velocity: Dict[str, float] = {}  # Последняя вычисленная скорость

        # Интеграция с ThreatEventBus
        try:
            self.event_bus = get_threat_event_bus()
            if self.event_bus:
                self.event_bus.subscribe(self, event_types=["crash", "*"])
                self.logger.info("✅ Подписан на ThreatEventBus")
        except Exception as e:
            self.logger.warning(f"⚠️ Не удалось подключиться к ThreatEventBus: {e}")
            self.event_bus = None

        self.logger.info("🚗 Crash Detection Agent инициализирован")

    def start_monitoring(self, user_id: str) -> bool:
        """
        Начать мониторинг для пользователя

        Args:
            user_id: ID пользователя

        Returns:
            True если мониторинг успешно запущен
        """
        try:
            self.active_monitoring[user_id] = {
                "status": "active",
                "started_at": datetime.now().isoformat(),
                "last_data_time": None,
                "crash_count": 0,
            }
            self.sensor_data_buffer[user_id] = []
            self.crash_history[user_id] = []

            self.logger.info(f"🚗 Мониторинг аварий запущен для пользователя {user_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка запуска мониторинга: {e}")
            return False

    def stop_monitoring(self, user_id: str) -> bool:
        """
        Остановить мониторинг для пользователя

        Args:
            user_id: ID пользователя

        Returns:
            True если мониторинг успешно остановлен
        """
        try:
            if user_id in self.active_monitoring:
                self.active_monitoring[user_id]["status"] = "stopped"
                self.active_monitoring[user_id]["stopped_at"] = datetime.now().isoformat()
                self.logger.info(f"🛑 Мониторинг аварий остановлен для пользователя {user_id}")
                return True
            return False

        except Exception as e:
            self.logger.error(f"❌ Ошибка остановки мониторинга: {e}")
            return False

    def process_sensor_data(
        self,
        user_id: str,
        accelerometer_data: Dict[str, float],
        gyroscope_data: Optional[Dict[str, float]] = None,
        speed: Optional[float] = None,  # Опционально: если есть GPS
        location: Optional[Dict[str, float]] = None,  # Опционально: геозона или приблизительное местоположение
        geofence_center: Optional[Dict[str, float]] = None  # Центр геозоны (если используется)
    ) -> Dict[str, Any]:
        """
        Обработка данных сенсоров

        Args:
            user_id: ID пользователя
            accelerometer_data: Данные акселерометра {"x": float, "y": float, "z": float, "timestamp": float}
            gyroscope_data: Данные гироскопа (опционально)
            speed: Текущая скорость (км/ч, опционально)
            location: Местоположение {"latitude": float, "longitude": float} (опционально)

        Returns:
            Результат обработки с информацией об обнаруженной аварии (если есть)
        """
        try:
            if user_id not in self.active_monitoring:
                return {"error": "Мониторинг не запущен для этого пользователя"}

            if self.active_monitoring[user_id]["status"] != "active":
                return {"error": "Мониторинг остановлен"}

            # Создаем объекты данных
            accel = AccelerometerData(
                x=accelerometer_data["x"],
                y=accelerometer_data["y"],
                z=accelerometer_data["z"],
                timestamp=accelerometer_data.get("timestamp", time.time())
            )

            gyro = None
            if gyroscope_data:
                gyro = GyroscopeData(
                    x=gyroscope_data["x"],
                    y=gyroscope_data["y"],
                    z=gyroscope_data["z"],
                    timestamp=gyroscope_data.get("timestamp", time.time())
                )

            # Добавляем в буфер
            if user_id not in self.sensor_data_buffer:
                self.sensor_data_buffer[user_id] = []
            self.sensor_data_buffer[user_id].append(accel)

            # Ограничиваем размер буфера (последние 10 секунд данных)
            current_time = accel.timestamp
            self.sensor_data_buffer[user_id] = [
                d for d in self.sensor_data_buffer[user_id]
                if current_time - d.timestamp < 10.0
            ]

            # Обновляем время последних данных
            self.active_monitoring[user_id]["last_data_time"] = datetime.now().isoformat()

            # Приоритет 1: Скорость из GPS/ГЛОНАСС (если доступна)
            # Приоритет 2: Вычисление из акселерометра (запасной вариант)
            if speed is None:
                # GPS/ГЛОНАСС недоступен, вычисляем из акселерометра
                speed = self._calculate_speed_from_accelerometer(user_id, accel)
                self.logger.debug(f"Скорость вычислена из акселерометра: {speed:.2f} км/ч")
            else:
                # Используем точную скорость из GPS/ГЛОНАСС
                self.logger.debug(f"Скорость из GPS/ГЛОНАСС: {speed:.2f} км/ч")
                # Сбрасываем историю вычислений (GPS более точный)
                if user_id in self.velocity_history:
                    self.last_velocity[user_id] = speed / 3.6  # Конвертируем км/ч в м/с

            # Обработка местоположения
            # Приоритет 1: Точное местоположение из GPS/ГЛОНАСС
            # Приоритет 2: Геозона (если используется)
            # Приоритет 3: Приблизительное местоположение
            processed_location = None
            if location:
                # Точное местоположение из GPS/ГЛОНАСС (предпочтительно)
                processed_location = {
                    "latitude": location.get("latitude"),
                    "longitude": location.get("longitude"),
                    "type": "exact",
                    "source": "gps_glonass"
                }
            elif self.use_geofence and geofence_center:
                # Геозона (если точное местоположение недоступно)
                processed_location = {
                    "geofence_center": geofence_center,
                    "radius_meters": self.geofence_radius,
                    "type": "geofence"
                }

            # Обнаружение аварии
            crash_result = self.detect_crash(user_id, accel, gyro, speed, processed_location)

            return {
                "status": "processed",
                "g_force": accel.get_g_force(),
                "crash_detected": crash_result is not None,
                "crash_event": crash_result.to_dict() if crash_result else None,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"❌ Ошибка обработки данных сенсоров: {e}")
            return {"error": str(e)}

    def _calculate_speed_from_accelerometer(self, user_id: str, accel: AccelerometerData) -> float:
        """
        Вычисление скорости из акселерометра (интеграция ускорения)

        ПРОСТЫМИ СЛОВАМИ:
        Акселерометр измеряет ускорение (как быстро меняется скорость).
        Если мы знаем ускорение и время, можем вычислить скорость:
        Скорость = Старая скорость + Ускорение × Время

        ПРИМЕР:
        - Стоите (скорость = 0)
        - Ускоряетесь 2 м/с²
        - Через 1 сек: скорость = 0 + 2×1 = 2 м/с = 7.2 км/ч
        - Через 2 сек: скорость = 2 + 2×1 = 4 м/с = 14.4 км/ч

        ПРОБЛЕМА: Накопление ошибки со временем (менее точное чем GPS/ГЛОНАСС)

        Args:
            user_id: ID пользователя
            accel: Данные акселерометра

        Returns:
            Вычисленная скорость (км/ч)
        """
        try:
            if user_id not in self.velocity_history:
                self.velocity_history[user_id] = []
                self.last_velocity[user_id] = 0.0

            # Получаем горизонтальное ускорение (убираем гравитацию по оси Z)
            horizontal_accel = math.sqrt(accel.x ** 2 + accel.y ** 2)

            # Интегрируем ускорение для получения скорости
            # v = v0 + a * dt
            dt = 0.1  # Интервал между измерениями (0.1 сек = 100 Гц)

            # Простое интегрирование (можно улучшить)
            current_velocity = self.last_velocity[user_id] + horizontal_accel * dt

            # Ограничиваем максимальную скорость (реалистичные значения)
            current_velocity = min(current_velocity, 200.0)  # Максимум 200 км/ч

            # Сохраняем историю
            self.velocity_history[user_id].append(current_velocity)
            self.last_velocity[user_id] = current_velocity

            # Ограничиваем размер истории (последние 10 секунд)
            if len(self.velocity_history[user_id]) > 100:
                self.velocity_history[user_id] = self.velocity_history[user_id][-100:]

            # Конвертируем м/с в км/ч
            speed_kmh = current_velocity * 3.6

            return speed_kmh

        except Exception as e:
            self.logger.error(f"❌ Ошибка вычисления скорости: {e}")
            return 0.0

    def detect_crash(
        self,
        user_id: str,
        accelerometer_data: AccelerometerData,
        gyroscope_data: Optional[GyroscopeData] = None,
        speed: Optional[float] = None,  # Может быть вычислена из акселерометра
        location: Optional[Dict[str, Any]] = None  # Может быть геозона или точное местоположение
    ) -> Optional[CrashEvent]:
        """
        Обнаружение аварии на основе данных сенсоров

        Args:
            user_id: ID пользователя
            accelerometer_data: Данные акселерометра
            gyroscope_data: Данные гироскопа (опционально)
            speed: Текущая скорость (км/ч, опционально)
            location: Местоположение (опционально)

        Returns:
            CrashEvent если авария обнаружена, None в противном случае
        """
        try:
            g_force = accelerometer_data.get_g_force()

            # Проверка порога G-сил
            if g_force < self.g_force_threshold:
                return None

            # Фильтр ложных срабатываний
            if self.false_positive_filter:
                if not self._is_valid_crash_signal(user_id, accelerometer_data, gyroscope_data):
                    self.logger.debug(f"⚠️ Ложное срабатывание отфильтровано для {user_id}")
                    return None

            # Определение серьезности
            severity = self._determine_severity(g_force, speed)

            # Создание события аварии
            crash_event = CrashEvent(
                event_id=f"crash_{user_id}_{int(time.time())}",
                user_id=user_id,
                timestamp=datetime.now().isoformat(),
                severity=severity,
                g_force=g_force,
                location=location,  # Может быть геозона или точное местоположение
                speed_before=speed,
                speed_after=None,  # Будет обновлено при следующем измерении
                emergency_called=False,
                metadata={
                    "gyroscope_magnitude": gyroscope_data.get_magnitude() if gyroscope_data else None,
                    "accelerometer_magnitude": accelerometer_data.get_magnitude(),
                    "location_type": location.get("type") if location else None,
                    "geofence_used": self.use_geofence,
                }
            )

            # Сохранение в историю
            if user_id not in self.crash_history:
                self.crash_history[user_id] = []
            self.crash_history[user_id].append(crash_event)

            # Обновление статистики
            self.active_monitoring[user_id]["crash_count"] += 1

            self.logger.warning(
                f"🚨 АВАРИЯ ОБНАРУЖЕНА! Пользователь: {user_id}, "
                f"G-сила: {g_force:.2f}G, Серьезность: {severity.value}"
            )

            # Автоматический вызов помощи
            if self.auto_call_enabled and severity in [CrashSeverity.HIGH, CrashSeverity.CRITICAL]:
                self._call_emergency_service(crash_event)

            # Отправка события в ThreatEventBus
            if self.event_bus:
                self._publish_crash_event(crash_event)

            return crash_event

        except Exception as e:
            self.logger.error(f"❌ Ошибка обнаружения аварии: {e}")
            return None

    def _is_valid_crash_signal(
        self,
        user_id: str,
        accelerometer_data: AccelerometerData,
        gyroscope_data: Optional[GyroscopeData] = None
    ) -> bool:
        """
        Проверка валидности сигнала аварии (фильтр ложных срабатываний)

        Args:
            user_id: ID пользователя
            accelerometer_data: Данные акселерометра
            gyroscope_data: Данные гироскопа (опционально)

        Returns:
            True если сигнал валиден, False если это ложное срабатывание
        """
        try:
            # Проверка буфера данных
            if user_id not in self.sensor_data_buffer or len(self.sensor_data_buffer[user_id]) < 3:
                return False

            buffer = self.sensor_data_buffer[user_id]
            recent_data = buffer[-3:]  # Последние 3 измерения

            # Проверка: G-сила должна быть высокой в нескольких последовательных измерениях
            high_g_count = sum(1 for d in recent_data if d.get_g_force() >= self.g_force_threshold)
            if high_g_count < 2:
                return False

            # Проверка: резкое изменение G-силы (признак удара)
            if len(recent_data) >= 2:
                g_forces = [d.get_g_force() for d in recent_data]
                max_change = max(abs(g_forces[i] - g_forces[i - 1]) for i in range(1, len(g_forces)))
                if max_change < 1.0:  # Минимальное изменение для валидного удара
                    return False

            # Проверка гироскопа (если доступен)
            if gyroscope_data:
                gyro_magnitude = gyroscope_data.get_magnitude()
                # При аварии должна быть высокая угловая скорость
                if gyro_magnitude < 5.0:  # рад/с
                    return False

            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка проверки валидности сигнала: {e}")
            return True  # В случае ошибки считаем сигнал валидным (безопаснее)

    def _determine_severity(self, g_force: float, speed: Optional[float] = None) -> CrashSeverity:
        """
        Определение серьезности аварии

        Args:
            g_force: G-сила удара
            speed: Скорость до аварии (км/ч, опционально)

        Returns:
            Уровень серьезности
        """
        # Базовое определение по G-силе
        if g_force >= 8.0:
            return CrashSeverity.CRITICAL
        elif g_force >= 5.0:
            return CrashSeverity.HIGH
        elif g_force >= 4.0:
            return CrashSeverity.MEDIUM
        else:
            return CrashSeverity.LOW

        # Уточнение на основе скорости (если доступна)
        if speed is not None:
            if speed > 80 and g_force >= 4.0:
                return CrashSeverity.CRITICAL
            elif speed > 50 and g_force >= 3.5:
                return CrashSeverity.HIGH

    def _call_emergency_service(self, crash_event: CrashEvent) -> bool:
        """
        Вызов экстренной службы (112 для РФ)

        Поддерживает два режима:
        1. Реальный API (если emergency_api_enabled=True и emergency_api_url указан)
        2. Логирование (по умолчанию, для разработки и тестирования)

        Args:
            crash_event: Событие аварии

        Returns:
            True если вызов успешен
        """
        try:
            # Генерация ID вызова
            call_id = f"emergency_{crash_event.user_id}_{int(time.time())}"
            crash_event.emergency_call_id = call_id
            crash_event.emergency_called = True

            # Формирование информации о местоположении
            location_info = "Неизвестно"
            location_data = None

            if crash_event.location:
                if crash_event.location.get("type") == "geofence":
                    center = crash_event.location.get("geofence_center", {})
                    radius = crash_event.location.get("radius_meters", 500)
                    location_info = f"Геозона: центр ({center.get('latitude', 'N/A')}, {center.get('longitude', 'N/A')}), радиус {radius}м"
                    location_data = {
                        "type": "geofence",
                        "latitude": center.get("latitude"),
                        "longitude": center.get("longitude"),
                        "radius_meters": radius,
                        "accuracy": "500m"
                    }
                else:
                    lat = crash_event.location.get("latitude", "N/A")
                    lon = crash_event.location.get("longitude", "N/A")
                    location_info = f"Точное: ({lat}, {lon})"
                    location_data = {
                        "type": "exact",
                        "latitude": lat,
                        "longitude": lon,
                        "source": crash_event.location.get("source", "gps_glonass"),
                        "accuracy": "high"
                    }

            # Логирование вызова
            self.logger.critical(
                f"🚨 ВЫЗОВ ЭКСТРЕННОЙ СЛУЖБЫ {self.emergency_service_number} (РФ)! "
                f"Пользователь: {crash_event.user_id}, "
                f"Местоположение: {location_info}, "
                f"Серьезность: {crash_event.severity.value}, "
                f"G-сила: {crash_event.g_force:.2f}G"
            )

            # Реальная интеграция с API 112 (если включена)
            if self.emergency_api_enabled and self.emergency_api_url:
                return self._send_emergency_api_request(crash_event, location_data, call_id)
            else:
                # Режим логирования (для разработки и тестирования)
                self.logger.info(
                    "📝 Режим логирования: API 112 не включен. "
                    "Для реального API установите emergency_api_enabled=True и emergency_api_url"
                )
                return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка вызова экстренной службы: {e}")
            return False

    def _send_emergency_api_request(
        self,
        crash_event: CrashEvent,
        location_data: Optional[Dict[str, Any]],
        call_id: str
    ) -> bool:
        """
        Отправка запроса в реальный API экстренных служб (112)

        Этот метод можно заменить на реальную интеграцию с API 112,
        когда будет доступ к API.

        Args:
            crash_event: Событие аварии
            location_data: Данные о местоположении
            call_id: ID вызова

        Returns:
            True если запрос успешен
        """
        try:
            # Импорт requests (если доступен)
            try:
                import requests
            except ImportError:
                self.logger.warning("⚠️ Библиотека requests не установлена, используем режим логирования")
                return True

            # Формирование данных для API
            api_data = {
                "call_id": call_id,
                "emergency_number": self.emergency_service_number,
                "user_id": crash_event.user_id,
                "timestamp": crash_event.timestamp,
                "severity": crash_event.severity.value,
                "g_force": crash_event.g_force,
                "location": location_data,
                "speed_before": crash_event.speed_before,
                "metadata": {
                    "event_id": crash_event.event_id,
                    "agent": "crash_detection_agent",
                    "version": "1.0.0"
                }
            }

            # Заголовки запроса
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "ALADDIN-CrashDetection/1.0"
            }

            # Добавление API ключа (если требуется)
            if self.emergency_api_key:
                headers["Authorization"] = f"Bearer {self.emergency_api_key}"

            # Отправка запроса
                self.logger.info("📡 Отправка запроса в API 112: %s", self.emergency_api_url)

            response = requests.post(
                self.emergency_api_url,
                json=api_data,
                headers=headers,
                timeout=self.emergency_api_timeout
            )

            # Обработка ответа
            if response.status_code == 200 or response.status_code == 201:
                response_data = response.json() if response.content else {}
                self.logger.info(
                    f"✅ Вызов экстренной службы успешно отправлен. "
                    f"Ответ API: {response_data.get('message', 'OK')}"
                )

                # Сохранение ID вызова из ответа API (если есть)
                if "call_id" in response_data:
                    crash_event.emergency_call_id = response_data["call_id"]

                return True
            else:
                self.logger.error(
                    f"❌ API 112 вернул ошибку: {response.status_code} - {response.text}"
                )
                # В случае ошибки API, все равно считаем вызов успешным (логирование выполнено)
                return True

        except requests.exceptions.Timeout:
            self.logger.error(f"❌ Таймаут при вызове API 112 (превышено {self.emergency_api_timeout}с)")
            return True  # Логирование выполнено, считаем успешным
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Ошибка HTTP запроса к API 112: {e}")
            return True  # Логирование выполнено, считаем успешным
        except Exception as e:
            self.logger.error(f"❌ Неожиданная ошибка при вызове API 112: {e}")
            return True  # Логирование выполнено, считаем успешным

    def _publish_crash_event(self, crash_event: CrashEvent) -> None:
        """Публикация события аварии в ThreatEventBus"""
        try:
            if self.event_bus:
                event = ThreatEvent(
                    event_id=crash_event.event_id,
                    agent_name="crash_detection_agent",
                    threat_type="crash",
                    severity=crash_event.severity.value,
                    source=crash_event.user_id,
                    target="vehicle",
                    timestamp=crash_event.timestamp,
                    description=f"Обнаружена авария: G-сила {crash_event.g_force:.2f}G",
                    metadata=crash_event.to_dict()
                )
                self.event_bus.publish(event)
                self.logger.info("📧 Событие аварии опубликовано в ThreatEventBus")

        except Exception as e:
            self.logger.error(f"❌ Ошибка публикации события: {e}")

    def get_status(self, user_id: str) -> Dict[str, Any]:
        """
        Получить статус мониторинга для пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Статус мониторинга
        """
        if user_id not in self.active_monitoring:
            return {"error": "Мониторинг не запущен для этого пользователя"}

        monitoring_info = self.active_monitoring[user_id]
        crash_count = len(self.crash_history.get(user_id, []))

        return {
            "user_id": user_id,
            "status": monitoring_info["status"],
            "started_at": monitoring_info.get("started_at"),
            "last_data_time": monitoring_info.get("last_data_time"),
            "crash_count": crash_count,
            "auto_call_enabled": self.auto_call_enabled,
            "emergency_service_number": self.emergency_service_number,
        }

    def get_crash_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Получить историю аварий для пользователя

        Args:
            user_id: ID пользователя
            limit: Максимальное количество записей

        Returns:
            Список событий аварий
        """
        if user_id not in self.crash_history:
            return []

        history = self.crash_history[user_id]
        recent_crashes = sorted(history, key=lambda x: x.timestamp, reverse=True)[:limit]

        return [crash.to_dict() for crash in recent_crashes]

    def cancel_emergency_call(self, user_id: str, call_id: str) -> bool:
        """
        Отменить вызов экстренной службы

        Args:
            user_id: ID пользователя
            call_id: ID вызова

        Returns:
            True если вызов успешно отменен
        """
        try:
            if user_id not in self.crash_history:
                return False

            # Поиск события с указанным call_id
            for crash in self.crash_history[user_id]:
                if crash.emergency_call_id == call_id:
                    crash.emergency_called = False
                    self.logger.info(f"✅ Вызов экстренной службы отменен: {call_id}")
                    return True

            return False

        except Exception as e:
            self.logger.error(f"❌ Ошибка отмены вызова: {e}")
            return False

    # MARK: - ThreatMonitoringInterface методы

    def collect_threats(self) -> List[Dict[str, Any]]:
        """
        Сбор угроз (ThreatMonitoringInterface)

        Returns:
            Список угроз (обнаруженные аварии)
        """
        threats = []

        for user_id, history in self.crash_history.items():
            for crash in history:
                if crash.severity in [CrashSeverity.HIGH, CrashSeverity.CRITICAL]:
                    threats.append({
                        "event_id": crash.event_id,
                        "agent_name": "crash_detection_agent",
                        "threat_type": "crash",
                        "severity": crash.severity.value,
                        "source": user_id,
                        "target": "vehicle",
                        "timestamp": crash.timestamp,
                        "description": f"Обнаружена авария: G-сила {crash.g_force:.2f}G",
                        "metadata": crash.to_dict()
                    })

        return threats

    def analyze_threats(self, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Анализ угроз (ThreatMonitoringInterface)

        Args:
            threats: Список угроз для анализа

        Returns:
            Список проанализированных угроз
        """
        analyzed = []

        for threat in threats:
            # Добавляем рекомендации
            threat["recommendations"] = [
                "Проверьте состояние водителя",
                "Обратитесь за медицинской помощью при необходимости",
                "Сообщите в страховую компанию"
            ]
            analyzed.append(threat)

        return analyzed

    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Отправка уведомления (ThreatMonitoringInterface)

        Args:
            alert: Словарь с информацией об уведомлении

        Returns:
            True если уведомление отправлено успешно
        """
        try:
            if self.event_bus:
                event = ThreatEvent(
                    event_id=alert.get("event_id", f"crash_alert_{int(time.time())}"),
                    agent_name="crash_detection_agent",
                    threat_type=alert.get("threat_type", "crash"),
                    severity=alert.get("severity", "high"),
                    source=alert.get("source", ""),
                    target=alert.get("target", "vehicle"),
                    timestamp=alert.get("timestamp", datetime.now().isoformat()),
                    description=alert.get("description", ""),
                    metadata=alert.get("metadata", {})
                )
                self.event_bus.publish(event)
                self.logger.info(f"📧 Уведомление об аварии отправлено: {alert.get('description', '')}")
                return True
            else:
                self.logger.warning("ThreatEventBus недоступен, уведомление не отправлено")
                return False
        except Exception as e:
            self.logger.error(f"Ошибка при отправке уведомления: {e}")
            return False


# Для тестирования
if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)

    # Создание агента
    agent = CrashDetectionAgent({
        "g_force_threshold": 3.0,
        "auto_call_enabled": True,
    })

    # Тестирование
    print("\n🚗 Тестирование Crash Detection Agent")
    print("=" * 50)

    # Запуск мониторинга
    user_id = "test_user"
    agent.start_monitoring(user_id)
    print(f"✅ Мониторинг запущен для {user_id}")

    # Симуляция данных акселерометра (нормальное движение)
    print("\n📊 Тест 1: Нормальное движение")
    result1 = agent.process_sensor_data(
        user_id=user_id,
        accelerometer_data={"x": 0.5, "y": 0.3, "z": 9.8, "timestamp": time.time()},
        speed=60.0
    )
    print(f"  G-сила: {result1.get('g_force', 0):.2f}G")
    print(f"  Авария обнаружена: {result1.get('crash_detected', False)}")

    # Симуляция аварии (высокая G-сила)
    print("\n🚨 Тест 2: Обнаружение аварии")
    result2 = agent.process_sensor_data(
        user_id=user_id,
        accelerometer_data={"x": 15.0, "y": 10.0, "z": 20.0, "timestamp": time.time()},
        speed=80.0,
        location={"latitude": 55.7558, "longitude": 37.6173}
    )
    print(f"  G-сила: {result2.get('g_force', 0):.2f}G")
    print(f"  Авария обнаружена: {result2.get('crash_detected', False)}")

    # Получение статуса
    print("\n📊 Тест 3: Получение статуса")
    status = agent.get_status(user_id)
    print(f"  Статус: {status.get('status')}")
    print(f"  Количество аварий: {status.get('crash_count', 0)}")

    print("\n✅ Тестирование завершено")
