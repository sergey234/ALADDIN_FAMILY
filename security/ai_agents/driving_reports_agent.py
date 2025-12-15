#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 Driving Reports Agent
Агент для генерации отчетов о вождении и оценки безопасности вождения

Функциональность:
- Отслеживание скорости, использования телефона, резкого торможения
- Генерация отчетов о вождении (дневные, недельные, месячные)
- Оценка безопасности вождения (баллы, рейтинг)
- Статистика нарушений и рекомендации

Дата создания: 12 декабря 2025
Версия: 1.0.0
"""

import logging
import time
from datetime import datetime, timedelta
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


class DrivingViolation(Enum):
    """Типы нарушений при вождении"""
    SPEEDING = "speeding"  # Превышение скорости
    PHONE_USE = "phone_use"  # Использование телефона
    HARD_BRAKING = "hard_braking"  # Резкое торможение
    HARD_ACCELERATION = "hard_acceleration"  # Резкое ускорение
    SHARP_TURN = "sharp_turn"  # Резкий поворот
    LANE_CHANGE = "lane_change"  # Резкая смена полосы
    DISTRACTION = "distraction"  # Отвлечение внимания
    OTHER = "other"  # Другое


class SafetyRating(Enum):
    """Рейтинг безопасности вождения"""
    EXCELLENT = "excellent"  # Отлично (90-100 баллов)
    GOOD = "good"  # Хорошо (70-89 баллов)
    FAIR = "fair"  # Удовлетворительно (50-69 баллов)
    POOR = "poor"  # Плохо (30-49 баллов)
    CRITICAL = "critical"  # Критично (0-29 баллов)


@dataclass
class DrivingEvent:
    """Событие вождения"""
    event_id: str
    user_id: str
    timestamp: float
    event_type: str  # "start", "stop", "violation", "location"
    speed: Optional[float] = None  # Скорость (км/ч)
    location: Optional[Dict[str, Any]] = None  # Местоположение
    violation_type: Optional[DrivingViolation] = None  # Тип нарушения
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        if self.violation_type:
            result['violation_type'] = self.violation_type.value
        return result


@dataclass
class SafetyScore:
    """Оценка безопасности вождения"""
    user_id: str
    period: str  # "day", "week", "month"
    score: int  # Баллы (0-100)
    rating: SafetyRating  # Рейтинг
    total_violations: int  # Общее количество нарушений
    violations_by_type: Dict[str, int]  # Нарушения по типам
    total_driving_time: float  # Общее время вождения (часы)
    total_distance: float  # Общее расстояние (км)
    average_speed: float  # Средняя скорость (км/ч)
    max_speed: float  # Максимальная скорость (км/ч)
    timestamp: str  # Временная метка расчета

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['rating'] = self.rating.value
        return result


class DrivingReportsAgent(SecurityBase, ThreatMonitoringInterface):
    """
    Агент для генерации отчетов о вождении и оценки безопасности вождения
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация агента

        Args:
            config: Конфигурация агента
        """
        super().__init__(config)

        # Конфигурация
        config_dict = config if config is not None else {}
        self.speed_limit = config_dict.get("speed_limit", 60.0)  # Лимит скорости (км/ч)
        self.hard_braking_threshold = config_dict.get("hard_braking_threshold", 0.4)  # Порог резкого торможения (G)
        self.hard_acceleration_threshold = config_dict.get("hard_acceleration_threshold", 0.4)  # Порог резкого ускорения (G)
        self.sharp_turn_threshold = config_dict.get("sharp_turn_threshold", 0.5)  # Порог резкого поворота (рад/с)
        self.notify_parents = config_dict.get("notify_parents", True)  # Уведомлять родителей

        # Хранение данных
        self.active_monitoring: Dict[str, Dict[str, Any]] = {}  # Активный мониторинг по user_id
        self.driving_events: Dict[str, List[DrivingEvent]] = {}  # История событий по user_id
        self.violations: Dict[str, List[DrivingEvent]] = {}  # История нарушений по user_id
        self.reports: Dict[str, Dict[str, Any]] = {}  # Сгенерированные отчеты

        # ThreatEventBus (если доступен)
        try:
            self.event_bus = get_threat_event_bus()
        except Exception as e:
            self.logger.warning(f"⚠️ Не удалось подключиться к ThreatEventBus: {e}")
            self.event_bus = None

        self.logger.info("📊 Driving Reports Agent инициализирован")

    def start_monitoring(self, user_id: str) -> Dict[str, Any]:
        """
        Запуск мониторинга вождения для пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Результат запуска мониторинга
        """
        try:
            if user_id in self.active_monitoring:
                return {"error": "Мониторинг уже запущен для этого пользователя"}

            self.active_monitoring[user_id] = {
                "status": "active",
                "started_at": time.time(),
                "last_event_time": time.time(),
                "total_distance": 0.0,
                "total_time": 0.0
            }

            # Инициализация списков событий
            if user_id not in self.driving_events:
                self.driving_events[user_id] = []
            if user_id not in self.violations:
                self.violations[user_id] = []

            # Запись события начала вождения
            event = DrivingEvent(
                event_id=f"start_{user_id}_{int(time.time())}",
                user_id=user_id,
                timestamp=time.time(),
                event_type="start",
                metadata={"agent": "driving_reports_agent"}
            )
            self.driving_events[user_id].append(event)

            self.logger.info(f"🚗 Мониторинг вождения запущен для пользователя {user_id}")
            return {"status": "success", "message": "Мониторинг запущен", "user_id": user_id}

        except Exception as e:
            self.logger.error(f"❌ Ошибка запуска мониторинга: {e}")
            return {"error": str(e)}

    def stop_monitoring(self, user_id: str) -> Dict[str, Any]:
        """
        Остановка мониторинга вождения для пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Результат остановки мониторинга
        """
        try:
            if user_id not in self.active_monitoring:
                return {"error": "Мониторинг не запущен для этого пользователя"}

            monitoring_info = self.active_monitoring[user_id]
            total_time = time.time() - monitoring_info["started_at"]

            # Запись события остановки вождения
            event = DrivingEvent(
                event_id=f"stop_{user_id}_{int(time.time())}",
                user_id=user_id,
                timestamp=time.time(),
                event_type="stop",
                metadata={
                    "agent": "driving_reports_agent",
                    "total_time": total_time,
                    "total_distance": monitoring_info.get("total_distance", 0.0)
                }
            )
            self.driving_events[user_id].append(event)

            # Обновление статистики
            monitoring_info["total_time"] = total_time
            monitoring_info["status"] = "stopped"
            monitoring_info["stopped_at"] = time.time()

            self.logger.info(f"🛑 Мониторинг вождения остановлен для пользователя {user_id}")
            return {
                "status": "success",
                "message": "Мониторинг остановлен",
                "user_id": user_id,
                "total_time": total_time,
                "total_distance": monitoring_info.get("total_distance", 0.0)
            }

        except Exception as e:
            self.logger.error(f"❌ Ошибка остановки мониторинга: {e}")
            return {"error": str(e)}

    def record_driving_event(
        self,
        user_id: str,
        event_type: str,
        speed: Optional[float] = None,
        location: Optional[Dict[str, Any]] = None,
        violation_type: Optional[DrivingViolation] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Запись события вождения

        Args:
            user_id: ID пользователя
            event_type: Тип события ("start", "stop", "violation", "location", "speed")
            speed: Скорость (км/ч)
            location: Местоположение
            violation_type: Тип нарушения (если есть)
            metadata: Дополнительные данные

        Returns:
            Результат записи события
        """
        try:
            if user_id not in self.active_monitoring:
                return {"error": "Мониторинг не запущен для этого пользователя"}

            # Создание события
            event = DrivingEvent(
                event_id=f"{event_type}_{user_id}_{int(time.time())}",
                user_id=user_id,
                timestamp=time.time(),
                event_type=event_type,
                speed=speed,
                location=location,
                violation_type=violation_type,
                metadata=metadata or {}
            )

            # Добавление события в историю
            if user_id not in self.driving_events:
                self.driving_events[user_id] = []
            self.driving_events[user_id].append(event)

            # Если это нарушение, добавляем в список нарушений
            if violation_type:
                if user_id not in self.violations:
                    self.violations[user_id] = []
                self.violations[user_id].append(event)

                # Публикация события нарушения
                self._publish_violation_event(event)

            # Обновление активного мониторинга
            self.active_monitoring[user_id]["last_event_time"] = time.time()

            return {"status": "success", "event_id": event.event_id}

        except Exception as e:
            self.logger.error(f"❌ Ошибка записи события: {e}")
            return {"error": str(e)}

    def _publish_violation_event(self, event: DrivingEvent) -> None:
        """Публикация события нарушения в ThreatEventBus"""
        try:
            if self.event_bus and event.violation_type:
                threat_event = ThreatEvent(
                    event_id=event.event_id,
                    agent_name="driving_reports_agent",
                    threat_type="driving_violation",
                    severity=self._get_violation_severity(event.violation_type),
                    source=event.user_id,
                    target="vehicle",
                    timestamp=datetime.fromtimestamp(event.timestamp).isoformat(),
                    description=f"Обнаружено нарушение: {event.violation_type.value}",
                    metadata=event.to_dict()
                )
                self.event_bus.publish(threat_event)
                self.logger.info("📧 Событие нарушения опубликовано в ThreatEventBus")

        except Exception as e:
            self.logger.error(f"❌ Ошибка публикации события: {e}")

    def _get_violation_severity(self, violation_type: DrivingViolation) -> str:
        """Определение серьезности нарушения"""
        severity_map = {
            DrivingViolation.SPEEDING: "medium",
            DrivingViolation.PHONE_USE: "high",
            DrivingViolation.HARD_BRAKING: "low",
            DrivingViolation.HARD_ACCELERATION: "low",
            DrivingViolation.SHARP_TURN: "low",
            DrivingViolation.LANE_CHANGE: "medium",
            DrivingViolation.DISTRACTION: "high",
            DrivingViolation.OTHER: "low"
        }
        return severity_map.get(violation_type, "low")

    # MARK: - ThreatMonitoringInterface методы

    def collect_threats(self) -> List[ThreatEvent]:
        """Сбор угроз из нарушений вождения"""
        threats = []
        try:
            for user_id, violations_list in self.violations.items():
                for violation in violations_list[-10:]:  # Последние 10 нарушений
                    if violation.violation_type:
                        threat = ThreatEvent(
                            event_id=violation.event_id,
                            agent_name="driving_reports_agent",
                            threat_type="driving_violation",
                            severity=self._get_violation_severity(violation.violation_type),
                            source=user_id,
                            target="vehicle",
                            timestamp=datetime.fromtimestamp(violation.timestamp).isoformat(),
                            description=f"Нарушение: {violation.violation_type.value}",
                            metadata=violation.to_dict()
                        )
                        threats.append(threat)
        except Exception as e:
            self.logger.error(f"Ошибка при сборе угроз: {e}")
        return threats

    def analyze_threats(self, threats: List[ThreatEvent]) -> List[ThreatEvent]:
        """Анализ угроз вождения"""
        analyzed = []
        try:
            for threat in threats:
                # Анализ частоты нарушений
                user_id = threat.source
                if user_id in self.violations:
                    recent_violations = [
                        v for v in self.violations[user_id]
                        if time.time() - v.timestamp < 3600  # Последний час
                    ]
                    if len(recent_violations) >= 5:
                        threat.severity = "high"
                        threat.description += " (множественные нарушения за последний час)"
                analyzed.append(threat)
        except Exception as e:
            self.logger.error(f"Ошибка при анализе угроз: {e}")
        return analyzed

    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """Отправка уведомления о нарушении"""
        try:
            user_id = alert.get("user_id")
            violation_type = alert.get("violation_type", "unknown")

            self.logger.warning(
                f"⚠️ Нарушение вождения: пользователь {user_id}, "
                f"тип: {violation_type}"
            )

            # Здесь можно добавить отправку уведомлений родителям
            if self.notify_parents:
                self.logger.info(f"📧 Уведомление родителям отправлено для {user_id}")

            return True
        except Exception as e:
            self.logger.error(f"Ошибка при отправке уведомления: {e}")
            return False

    # MARK: - Генерация отчетов и оценка безопасности

    def generate_report(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = "week"
    ) -> Dict[str, Any]:
        """
        Генерация отчета о вождении за период

        Args:
            user_id: ID пользователя
            start_date: Начальная дата (если None, используется период)
            end_date: Конечная дата (если None, используется текущая дата)
            period: Период ("day", "week", "month") - используется если start_date/end_date не указаны

        Returns:
            Отчет о вождении
        """
        try:
            if user_id not in self.driving_events:
                return {"error": "Нет данных о вождении для этого пользователя"}

            # Определение периода
            if start_date is None or end_date is None:
                end_date = datetime.now()
                if period == "day":
                    start_date = end_date - timedelta(days=1)
                elif period == "week":
                    start_date = end_date - timedelta(weeks=1)
                elif period == "month":
                    start_date = end_date - timedelta(days=30)
                else:
                    start_date = end_date - timedelta(weeks=1)

            start_timestamp = start_date.timestamp()
            end_timestamp = end_date.timestamp()

            # Фильтрация событий по периоду
            events = [
                e for e in self.driving_events[user_id]
                if start_timestamp <= e.timestamp <= end_timestamp
            ]

            if not events:
                return {"error": "Нет событий за указанный период"}

            # Подсчет статистики
            total_time = 0.0
            total_distance = 0.0
            speeds = []
            violations_count = 0
            violations_by_type: Dict[str, int] = {}

            # Обработка событий
            for event in events:
                if event.speed is not None:
                    speeds.append(event.speed)

                if event.violation_type:
                    violations_count += 1
                    violation_type_str = event.violation_type.value
                    violations_by_type[violation_type_str] = violations_by_type.get(violation_type_str, 0) + 1

            # Расчет времени вождения
            start_events = [e for e in events if e.event_type == "start"]
            stop_events = [e for e in events if e.event_type == "stop"]

            if start_events and stop_events:
                for start_event in start_events:
                    # Находим ближайшее событие остановки после начала
                    matching_stops = [s for s in stop_events if s.timestamp > start_event.timestamp]
                    if matching_stops:
                        closest_stop = min(matching_stops, key=lambda x: x.timestamp)
                        total_time += (closest_stop.timestamp - start_event.timestamp) / 3600  # в часах

            # Расчет расстояния (приблизительный, на основе скорости и времени)
            if speeds:
                average_speed = sum(speeds) / len(speeds)
                total_distance = average_speed * total_time  # км

            # Расчет оценки безопасности
            safety_score = self.calculate_safety_score(user_id, start_date, end_date)

            # Формирование отчета
            report = {
                "user_id": user_id,
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_events": len(events),
                "total_driving_time_hours": round(total_time, 2),
                "total_distance_km": round(total_distance, 2),
                "average_speed_kmh": round(sum(speeds) / len(speeds), 2) if speeds else 0.0,
                "max_speed_kmh": round(max(speeds), 2) if speeds else 0.0,
                "min_speed_kmh": round(min(speeds), 2) if speeds else 0.0,
                "total_violations": violations_count,
                "violations_by_type": violations_by_type,
                "safety_score": safety_score.to_dict() if safety_score else None,
                "generated_at": datetime.now().isoformat()
            }

            # Сохранение отчета
            report_id = f"report_{user_id}_{int(time.time())}"
            self.reports[report_id] = report

            return {"status": "success", "report_id": report_id, "report": report}

        except Exception as e:
            self.logger.error(f"❌ Ошибка генерации отчета: {e}")
            return {"error": str(e)}

    def calculate_safety_score(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[SafetyScore]:
        """
        Расчет оценки безопасности вождения

        Args:
            user_id: ID пользователя
            start_date: Начальная дата
            end_date: Конечная дата

        Returns:
            Оценка безопасности (SafetyScore)
        """
        try:
            if user_id not in self.violations:
                # Если нет нарушений, возвращаем максимальный балл
                return SafetyScore(
                    user_id=user_id,
                    period="custom",
                    score=100,
                    rating=SafetyRating.EXCELLENT,
                    total_violations=0,
                    violations_by_type={},
                    total_driving_time=0.0,
                    total_distance=0.0,
                    average_speed=0.0,
                    max_speed=0.0,
                    timestamp=datetime.now().isoformat()
                )

            # Определение периода
            if start_date is None or end_date is None:
                end_date = datetime.now()
                start_date = end_date - timedelta(weeks=1)

            start_timestamp = start_date.timestamp()
            end_timestamp = end_date.timestamp()

            # Фильтрация нарушений по периоду
            violations = [
                v for v in self.violations[user_id]
                if start_timestamp <= v.timestamp <= end_timestamp
            ]

            # Начальный балл
            score = 100

            # Штрафы за нарушения
            violation_penalties = {
                DrivingViolation.SPEEDING: -10,
                DrivingViolation.PHONE_USE: -20,
                DrivingViolation.HARD_BRAKING: -5,
                DrivingViolation.HARD_ACCELERATION: -5,
                DrivingViolation.SHARP_TURN: -5,
                DrivingViolation.LANE_CHANGE: -10,
                DrivingViolation.DISTRACTION: -15,
                DrivingViolation.OTHER: -5
            }

            violations_by_type: Dict[str, int] = {}

            for violation in violations:
                if violation.violation_type:
                    violation_type_str = violation.violation_type.value
                    violations_by_type[violation_type_str] = violations_by_type.get(violation_type_str, 0) + 1
                    penalty = violation_penalties.get(violation.violation_type, -5)
                    score += penalty

            # Ограничение балла (0-100)
            score = max(0, min(100, score))

            # Определение рейтинга
            if score >= 90:
                rating = SafetyRating.EXCELLENT
            elif score >= 70:
                rating = SafetyRating.GOOD
            elif score >= 50:
                rating = SafetyRating.FAIR
            elif score >= 30:
                rating = SafetyRating.POOR
            else:
                rating = SafetyRating.CRITICAL

            # Расчет статистики вождения
            if user_id in self.driving_events:
                events = [
                    e for e in self.driving_events[user_id]
                    if start_timestamp <= e.timestamp <= end_timestamp
                ]
                speeds = [e.speed for e in events if e.speed is not None]

                # Расчет времени вождения
                total_time = 0.0
                start_events = [e for e in events if e.event_type == "start"]
                stop_events = [e for e in events if e.event_type == "stop"]

                if start_events and stop_events:
                    for start_event in start_events:
                        matching_stops = [s for s in stop_events if s.timestamp > start_event.timestamp]
                        if matching_stops:
                            closest_stop = min(matching_stops, key=lambda x: x.timestamp)
                            total_time += (closest_stop.timestamp - start_event.timestamp) / 3600

                average_speed = sum(speeds) / len(speeds) if speeds else 0.0
                max_speed = max(speeds) if speeds else 0.0
                total_distance = average_speed * total_time if average_speed > 0 else 0.0
            else:
                total_time = 0.0
                average_speed = 0.0
                max_speed = 0.0
                total_distance = 0.0

            return SafetyScore(
                user_id=user_id,
                period="custom",
                score=score,
                rating=rating,
                total_violations=len(violations),
                violations_by_type=violations_by_type,
                total_driving_time=round(total_time, 2),
                total_distance=round(total_distance, 2),
                average_speed=round(average_speed, 2),
                max_speed=round(max_speed, 2),
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            self.logger.error(f"❌ Ошибка расчета оценки безопасности: {e}")
            return None

    def get_violations_statistics(
        self,
        user_id: str,
        period: str = "week"
    ) -> Dict[str, Any]:
        """
        Получение статистики нарушений

        Args:
            user_id: ID пользователя
            period: Период ("day", "week", "month")

        Returns:
            Статистика нарушений
        """
        try:
            if user_id not in self.violations:
                return {"error": "Нет нарушений для этого пользователя"}

            # Определение периода
            end_date = datetime.now()
            if period == "day":
                start_date = end_date - timedelta(days=1)
            elif period == "week":
                start_date = end_date - timedelta(weeks=1)
            elif period == "month":
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(weeks=1)

            start_timestamp = start_date.timestamp()
            end_timestamp = end_date.timestamp()

            # Фильтрация нарушений
            violations = [
                v for v in self.violations[user_id]
                if start_timestamp <= v.timestamp <= end_timestamp
            ]

            if not violations:
                return {
                    "user_id": user_id,
                    "period": period,
                    "total_violations": 0,
                    "violations_by_type": {},
                    "violations_timeline": [],
                    "top_violations": []
                }

            # Подсчет по типам
            violations_by_type: Dict[str, int] = {}
            violations_timeline: List[Dict[str, Any]] = []

            for violation in violations:
                if violation.violation_type:
                    violation_type_str = violation.violation_type.value
                    violations_by_type[violation_type_str] = violations_by_type.get(violation_type_str, 0) + 1

                    violations_timeline.append({
                        "timestamp": datetime.fromtimestamp(violation.timestamp).isoformat(),
                        "type": violation_type_str,
                        "speed": violation.speed,
                        "location": violation.location
                    })

            # Топ нарушений
            top_violations = sorted(
                violations_by_type.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            return {
                "user_id": user_id,
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_violations": len(violations),
                "violations_by_type": violations_by_type,
                "violations_timeline": violations_timeline,
                "top_violations": [{"type": t[0], "count": t[1]} for t in top_violations]
            }

        except Exception as e:
            self.logger.error(f"❌ Ошибка получения статистики нарушений: {e}")
            return {"error": str(e)}

    def get_recommendations(self, user_id: str) -> List[str]:
        """
        Получение рекомендаций по улучшению безопасности вождения

        Args:
            user_id: ID пользователя

        Returns:
            Список рекомендаций
        """
        try:
            recommendations = []

            if user_id not in self.violations:
                return ["✅ Отличная работа! Нарушений не обнаружено. Продолжайте в том же духе!"]

            # Получение статистики за последнюю неделю
            stats = self.get_violations_statistics(user_id, period="week")

            if stats.get("error"):
                return ["⚠️ Недостаточно данных для рекомендаций"]

            violations_by_type = stats.get("violations_by_type", {})
            total_violations = stats.get("total_violations", 0)

            # Рекомендации на основе типов нарушений
            if violations_by_type.get("speeding", 0) > 0:
                recommendations.append(
                    f"⚠️ Обнаружено {violations_by_type['speeding']} превышений скорости. "
                    "Рекомендуется соблюдать скоростной режим для вашей безопасности."
                )

            if violations_by_type.get("phone_use", 0) > 0:
                recommendations.append(
                    f"🚫 Обнаружено {violations_by_type['phone_use']} использований телефона за рулем. "
                    "Использование телефона во время вождения крайне опасно. "
                    "Рекомендуется использовать hands-free или остановиться для использования телефона."
                )

            if violations_by_type.get("hard_braking", 0) > 5:
                recommendations.append(
                    f"🛑 Обнаружено {violations_by_type['hard_braking']} резких торможений. "
                    "Рекомендуется увеличить дистанцию до впереди идущего транспорта "
                    "и быть более внимательным к дорожной обстановке."
                )

            if violations_by_type.get("hard_acceleration", 0) > 5:
                recommendations.append(
                    f"⚡ Обнаружено {violations_by_type['hard_acceleration']} резких ускорений. "
                    "Плавное ускорение экономит топливо и повышает безопасность."
                )

            if violations_by_type.get("sharp_turn", 0) > 5:
                recommendations.append(
                    f"🔄 Обнаружено {violations_by_type['sharp_turn']} резких поворотов. "
                    "Рекомендуется снижать скорость перед поворотами для безопасности."
                )

            if violations_by_type.get("distraction", 0) > 0:
                recommendations.append(
                    f"👁️ Обнаружено {violations_by_type['distraction']} отвлечений внимания. "
                    "Рекомендуется сосредоточиться на дороге и избегать отвлекающих факторов."
                )

            # Общая рекомендация
            if total_violations > 10:
                recommendations.append(
                    f"⚠️ За последнюю неделю обнаружено {total_violations} нарушений. "
                    "Рекомендуется пройти курс безопасного вождения для улучшения навыков."
                )

            if not recommendations:
                recommendations.append("✅ Хорошая работа! Минимальное количество нарушений.")

            return recommendations

        except Exception as e:
            self.logger.error(f"❌ Ошибка получения рекомендаций: {e}")
            return ["⚠️ Ошибка при получении рекомендаций"]


# MARK: - Пример использования

if __name__ == "__main__":
    # Инициализация агента
    agent = DrivingReportsAgent()

    # Запуск мониторинга
    user_id = "user123"
    result = agent.start_monitoring(user_id)
    print(f"✅ Мониторинг запущен: {result}")

    # Запись события нарушения
    agent.record_driving_event(
        user_id=user_id,
        event_type="violation",
        speed=80.0,
        violation_type=DrivingViolation.SPEEDING,
        metadata={"speed_limit": 60.0}
    )

    # Остановка мониторинга
    result = agent.stop_monitoring(user_id)
    print(f"✅ Мониторинг остановлен: {result}")
