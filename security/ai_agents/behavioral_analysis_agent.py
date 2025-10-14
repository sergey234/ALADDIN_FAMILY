# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Behavioral Analysis Agent
AI агент анализа поведения для системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import json
import time
import threading
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import random
import statistics


from core.base import ComponentStatus, SecurityBase


class BehaviorType(Enum):
    """Типы поведения"""
    NORMAL = "normal"
    SUSPICIOUS = "suspicious"
    ANOMALOUS = "anomalous"
    MALICIOUS = "malicious"
    UNKNOWN = "unknown"


class BehaviorCategory(Enum):
    """Категории поведения"""
    NAVIGATION = "navigation"
    INTERACTION = "interaction"
    COMMUNICATION = "communication"
    DATA_ACCESS = "data_access"
    SYSTEM_USAGE = "system_usage"
    SECURITY_ACTIONS = "security_actions"


class RiskLevel(Enum):
    """Уровни риска"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BehaviorEvent:
    """Событие поведения"""
    event_id: str
    user_id: str
    session_id: str
    behavior_type: BehaviorType
    category: BehaviorCategory
    timestamp: datetime
    data: Dict[str, Any]
    risk_score: float
    confidence: float
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['behavior_type'] = self.behavior_type.value
        data['category'] = self.category.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class BehaviorPattern:
    """Паттерн поведения"""
    pattern_id: str
    user_id: str
    pattern_type: str
    frequency: int
    confidence: float
    time_window: int  # секунды
    characteristics: Dict[str, Any]
    created_at: datetime
    last_seen: datetime
    anomaly_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_seen'] = self.last_seen.isoformat()
        return data


@dataclass
class BehaviorAnalysis:
    """Результат анализа поведения"""
    analysis_id: str
    user_id: str
    session_id: str
    timestamp: datetime
    overall_risk: RiskLevel
    risk_score: float
    confidence: float
    anomalies_detected: List[str]
    patterns_identified: List[str]
    recommendations: List[str]
    behavioral_events: List[BehaviorEvent]
    analysis_metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['overall_risk'] = self.overall_risk.value
        data['timestamp'] = self.timestamp.isoformat()
        data['behavioral_events'] = [
            event.to_dict() for event in self.behavioral_events
        ]
        return data


@dataclass
class BehaviorMetrics:
    """Метрики анализа поведения"""
    total_events_analyzed: int = 0
    total_users_monitored: int = 0
    total_sessions_tracked: int = 0
    anomalies_detected: int = 0
    suspicious_behaviors: int = 0
    malicious_behaviors: int = 0
    patterns_learned: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    average_analysis_time: float = 0.0
    last_analysis: Optional[datetime] = None

    def __post_init__(self):
        if self.last_analysis is None:
            self.last_analysis = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['last_analysis'] = (
            self.last_analysis.isoformat() if self.last_analysis else None
        )
        return data


class BehavioralAnalysisAgent(SecurityBase):
    """AI агент анализа поведения для ALADDIN Security System"""

    def __init__(self, name: str = "BehavioralAnalysisAgent"):
        super().__init__(name)

        # Конфигурация агента
        self.analysis_interval = 30  # секунды
        self.pattern_learning_window = 3600  # 1 час
        self.anomaly_threshold = 0.7
        self.risk_threshold = 0.8
        self.max_events_per_session = 1000
        self.behavior_retention_hours = 24

        # Хранилище данных
        self.behavior_events: Dict[str, List[BehaviorEvent]] = {}
        self.behavior_patterns: Dict[str, List[BehaviorPattern]] = {}
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.behavior_metrics: BehaviorMetrics = BehaviorMetrics()
        self.analysis_lock = threading.RLock()

        # AI компоненты для анализа
        self.ai_enabled = True
        self.ml_models = {
            "anomaly_detector": None,
            "pattern_recognizer": None,
            "risk_assessor": None,
            "behavior_classifier": None
        }

        # Статистика
        self.statistics: Dict[str, Any] = {
            "total_analyses_performed": 0,
            "total_events_processed": 0,
            "total_patterns_learned": 0,
            "start_time": None,
            "last_analysis": None,
            "average_analysis_time": 0.0,
            "accuracy_rate": 0.0
        }

    def initialize(self) -> bool:
        """Инициализация агента анализа поведения"""
        try:
            self.log_activity(
                "Инициализация Behavioral Analysis Agent", "info"
            )
            self.status = ComponentStatus.RUNNING
            self.statistics["start_time"] = datetime.now()

            # Инициализация AI моделей
            self._initialize_ai_models()

            # Загрузка существующих паттернов
            self._load_behavior_patterns()

            # Запуск фоновых задач
            self._start_background_tasks()

            self.log_activity(
                "Behavioral Analysis Agent успешно инициализирован", "info"
            )
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации Behavioral Analysis Agent: {e}", "error"
            )
            self.status = ComponentStatus.ERROR
            return False

    def stop(self) -> bool:
        """Остановка агента анализа поведения"""
        try:
            self.log_activity("Остановка Behavioral Analysis Agent", "info")
            self.status = ComponentStatus.STOPPED

            # Остановка фоновых задач
            self._stop_background_tasks()

            # Сохранение состояния
            self._save_behavior_state()

            # Очистка данных
            with self.analysis_lock:
                self.behavior_events.clear()
                self.behavior_patterns.clear()
                self.user_profiles.clear()

            self.log_activity("Behavioral Analysis Agent остановлен", "info")
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка остановки Behavioral Analysis Agent: {e}", "error"
            )
            return False

    def analyze_behavior(
        self, user_id: str, session_id: str, event_data: Dict[str, Any]
    ) -> Optional[BehaviorAnalysis]:
        """Анализ поведения пользователя"""
        try:
            with self.analysis_lock:
                start_time = time.time()

                # Создание события поведения
                behavior_event = self._create_behavior_event(
                    user_id, session_id, event_data
                )

                # Добавление события в историю
                self._add_behavior_event(user_id, behavior_event)

                # Анализ поведения
                analysis = self._perform_behavior_analysis(
                    user_id, session_id, behavior_event
                )

                if analysis:
                    # Обновление метрик
                    self._update_behavior_metrics(analysis)

                    # Обновление статистики
                    analysis_time = time.time() - start_time
                    self.statistics["total_analyses_performed"] += 1
                    self.statistics["last_analysis"] = datetime.now()
                    self.statistics["average_analysis_time"] = (
                        (self.statistics["average_analysis_time"] *
                         (self.statistics["total_analyses_performed"] - 1) +
                         analysis_time) / self.statistics["total_analyses_performed"]
                    )

                return analysis

        except Exception as e:
            self.log_activity(f"Ошибка анализа поведения: {e}", "error")
            return None

    def get_user_behavior_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Получение профиля поведения пользователя"""
        try:
            with self.analysis_lock:
                if user_id in self.user_profiles:
                    return self.user_profiles[user_id].copy()

                # Создание профиля на основе истории
                profile = self._create_behavior_profile(user_id)
                if profile:
                    self.user_profiles[user_id] = profile
                    return profile.copy()

                return None

        except Exception as e:
            self.log_activity(f"Ошибка получения профиля поведения: {e}", "error")
            return None

    def get_behavior_patterns(self, user_id: Optional[str] = None) -> List[BehaviorPattern]:
        """Получение паттернов поведения"""
        try:
            with self.analysis_lock:
                if user_id:
                    return self.behavior_patterns.get(user_id, []).copy()

                all_patterns = []
                for patterns in self.behavior_patterns.values():
                    all_patterns.extend(patterns)
                return all_patterns

        except Exception as e:
            self.log_activity(f"Ошибка получения паттернов поведения: {e}", "error")
            return []

    def get_behavior_metrics(self) -> BehaviorMetrics:
        """Получение метрик анализа поведения"""
        try:
            with self.analysis_lock:
                return self.behavior_metrics
        except Exception as e:
            self.log_activity(f"Ошибка получения метрик поведения: {e}", "error")
            return BehaviorMetrics()

    def get_agent_status(self) -> Dict[str, Any]:
        """Получение статуса агента"""
        try:
            with self.analysis_lock:
                return {
                    "status": self.status.value,
                    "total_events": sum(len(events) for events in self.behavior_events.values()),
                    "total_patterns": sum(len(patterns) for patterns in self.behavior_patterns.values()),
                    "total_users": len(self.user_profiles),
                    "metrics": self.behavior_metrics.to_dict(),
                    "statistics": self.statistics,
                    "ai_enabled": self.ai_enabled,
                    "analysis_interval": self.analysis_interval
                }
        except Exception as e:
            self.log_activity(f"Ошибка получения статуса агента: {e}", "error")
            return {}

    def _initialize_ai_models(self):
        """Инициализация AI моделей"""
        try:
            # Симуляция инициализации AI моделей
            self.log_activity("AI модели анализа поведения инициализированы", "info")
        except Exception as e:
            self.log_activity(f"Ошибка инициализации AI моделей: {e}", "error")

    def _load_behavior_patterns(self):
        """Загрузка паттернов поведения"""
        try:
            # Создание тестовых паттернов
            test_patterns = [
                BehaviorPattern(
                    pattern_id="normal_navigation",
                    user_id="test_user",
                    pattern_type="navigation",
                    frequency=50,
                    confidence=0.9,
                    time_window=3600,
                    characteristics={"avg_session_duration": 1800, "pages_per_session": 15},
                    created_at=datetime.now() - timedelta(days=1),
                    last_seen=datetime.now()
                ),
                BehaviorPattern(
                    pattern_id="suspicious_activity",
                    user_id="test_user",
                    pattern_type="anomalous",
                    frequency=5,
                    confidence=0.7,
                    time_window=3600,
                    characteristics={"unusual_timing": True, "rapid_actions": True},
                    created_at=datetime.now() - timedelta(hours=2),
                    last_seen=datetime.now()
                )
            ]

            for pattern in test_patterns:
                if pattern.user_id not in self.behavior_patterns:
                    self.behavior_patterns[pattern.user_id] = []
                self.behavior_patterns[pattern.user_id].append(pattern)

            self.behavior_metrics.patterns_learned = len(test_patterns)
            self.log_activity(f"Загружено {len(test_patterns)} паттернов поведения", "info")
        except Exception as e:
            self.log_activity(f"Ошибка загрузки паттернов поведения: {e}", "error")

    def _start_background_tasks(self):
        """Запуск фоновых задач"""
        try:
            # Запуск задачи анализа поведения
            analysis_thread = threading.Thread(
                target=self._behavior_analysis_task,
                daemon=True
            )
            analysis_thread.start()

            # Запуск задачи обучения паттернов
            learning_thread = threading.Thread(
                target=self._pattern_learning_task,
                daemon=True
            )
            learning_thread.start()

            self.log_activity("Фоновые задачи запущены", "info")
        except Exception as e:
            self.log_activity(f"Ошибка запуска фоновых задач: {e}", "error")

    def _stop_background_tasks(self):
        """Остановка фоновых задач"""
        try:
            # Фоновые задачи остановятся автоматически при остановке агента
            self.log_activity("Фоновые задачи остановлены", "info")
        except Exception as e:
            self.log_activity(f"Ошибка остановки фоновых задач: {e}", "error")

    def _create_behavior_event(self, user_id: str, session_id: str,
                               event_data: Dict[str, Any]) -> BehaviorEvent:
        """Создание события поведения"""
        try:
            # Определение типа поведения
            behavior_type = self._classify_behavior_type(event_data)
            category = self._classify_behavior_category(event_data)

            # Расчет риска и уверенности
            risk_score = self._calculate_risk_score(event_data)
            confidence = self._calculate_confidence(event_data)

            event = BehaviorEvent(
                event_id=f"event-{int(time.time() * 1000)}-{random.randint(1000, 9999)}",
                user_id=user_id,
                session_id=session_id,
                behavior_type=behavior_type,
                category=category,
                timestamp=datetime.now(),
                data=event_data,
                risk_score=risk_score,
                confidence=confidence,
                metadata={"source": "behavioral_analysis_agent"}
            )

            return event

        except Exception as e:
            self.log_activity(f"Ошибка создания события поведения: {e}", "error")
            # Возвращаем базовое событие
            return BehaviorEvent(
                event_id=f"event-{int(time.time() * 1000)}",
                user_id=user_id,
                session_id=session_id,
                behavior_type=BehaviorType.UNKNOWN,
                category=BehaviorCategory.INTERACTION,
                timestamp=datetime.now(),
                data=event_data,
                risk_score=0.5,
                confidence=0.5
            )

    def _add_behavior_event(self, user_id: str, event: BehaviorEvent):
        """Добавление события поведения"""
        try:
            if user_id not in self.behavior_events:
                self.behavior_events[user_id] = []

            self.behavior_events[user_id].append(event)

            # Ограничиваем количество событий
            if len(self.behavior_events[user_id]) > self.max_events_per_session:
                self.behavior_events[user_id] = self.behavior_events[user_id][-self.max_events_per_session:]

            # Очищаем старые события
            cutoff_time = datetime.now() - timedelta(hours=self.behavior_retention_hours)
            self.behavior_events[user_id] = [
                e for e in self.behavior_events[user_id]
                if e.timestamp > cutoff_time
            ]

            self.behavior_metrics.total_events_analyzed += 1
            self.statistics["total_events_processed"] += 1

        except Exception as e:
            self.log_activity(f"Ошибка добавления события поведения: {e}", "error")

    def _perform_behavior_analysis(self, user_id: str, session_id: str,
                                   event: BehaviorEvent) -> Optional[BehaviorAnalysis]:
        """Выполнение анализа поведения"""
        try:
            # Получение истории поведения пользователя
            user_events = self.behavior_events.get(user_id, [])
            recent_events = [e for e in user_events if e.timestamp > datetime.now() - timedelta(hours=1)]

            # Анализ аномалий
            anomalies = self._detect_anomalies(user_id, event, recent_events)

            # Идентификация паттернов
            patterns = self._identify_patterns(user_id, event, recent_events)

            # Расчет общего риска
            overall_risk, risk_score = self._calculate_overall_risk(event, anomalies, patterns)

            # Генерация рекомендаций
            recommendations = self._generate_recommendations(overall_risk, anomalies, patterns)

            # Создание анализа
            analysis = BehaviorAnalysis(
                analysis_id=f"analysis-{int(time.time() * 1000)}",
                user_id=user_id,
                session_id=session_id,
                timestamp=datetime.now(),
                overall_risk=overall_risk,
                risk_score=risk_score,
                confidence=event.confidence,
                anomalies_detected=anomalies,
                patterns_identified=patterns,
                recommendations=recommendations,
                behavioral_events=[event],
                analysis_metadata={
                    "events_analyzed": len(recent_events),
                    "analysis_duration": 0.1,
                    "ai_models_used": list(self.ml_models.keys())
                }
            )

            return analysis

        except Exception as e:
            self.log_activity(f"Ошибка выполнения анализа поведения: {e}", "error")
            return None

    def _classify_behavior_type(self, event_data: Dict[str, Any]) -> BehaviorType:
        """Классификация типа поведения"""
        try:
            # Простая эвристическая классификация
            action = event_data.get("action", "").lower()

            if "login" in action or "logout" in action:
                return BehaviorType.NORMAL
            elif "download" in action or "upload" in action:
                return BehaviorType.SUSPICIOUS
            elif "admin" in action or "root" in action:
                return BehaviorType.MALICIOUS
            elif "rapid" in action or "burst" in action:
                return BehaviorType.ANOMALOUS
            else:
                return BehaviorType.NORMAL

        except Exception as e:
            self.log_activity(f"Ошибка классификации типа поведения: {e}", "error")
            return BehaviorType.UNKNOWN

    def _classify_behavior_category(self, event_data: Dict[str, Any]) -> BehaviorCategory:
        """Классификация категории поведения"""
        try:
            action = event_data.get("action", "").lower()

            if "navigate" in action or "page" in action:
                return BehaviorCategory.NAVIGATION
            elif "click" in action or "interact" in action:
                return BehaviorCategory.INTERACTION
            elif "message" in action or "chat" in action:
                return BehaviorCategory.COMMUNICATION
            elif "access" in action or "read" in action:
                return BehaviorCategory.DATA_ACCESS
            elif "system" in action or "config" in action:
                return BehaviorCategory.SYSTEM_USAGE
            else:
                return BehaviorCategory.SECURITY_ACTIONS

        except Exception as e:
            self.log_activity(f"Ошибка классификации категории поведения: {e}", "error")
            return BehaviorCategory.INTERACTION

    def _calculate_risk_score(self, event_data: Dict[str, Any]) -> float:
        """Расчет оценки риска"""
        try:
            base_risk = 0.1

            # Факторы риска
            if event_data.get("suspicious", False):
                base_risk += 0.3
            if event_data.get("admin_access", False):
                base_risk += 0.4
            if event_data.get("unusual_timing", False):
                base_risk += 0.2
            if event_data.get("rapid_actions", False):
                base_risk += 0.3

            return min(base_risk, 1.0)

        except Exception as e:
            self.log_activity(f"Ошибка расчета оценки риска: {e}", "error")
            return 0.5

    def _calculate_confidence(self, event_data: Dict[str, Any]) -> float:
        """Расчет уверенности в анализе"""
        try:
            # Базовая уверенность
            confidence = 0.7

            # Увеличиваем уверенность при наличии четких индикаторов
            if event_data.get("clear_indicators", False):
                confidence += 0.2
            if event_data.get("multiple_signals", False):
                confidence += 0.1

            return min(confidence, 1.0)

        except Exception as e:
            self.log_activity(f"Ошибка расчета уверенности: {e}", "error")
            return 0.5

    def _detect_anomalies(self, user_id: str, event: BehaviorEvent,
                          recent_events: List[BehaviorEvent]) -> List[str]:
        """Обнаружение аномалий"""
        try:
            anomalies = []

            # Проверка на необычное время активности
            if event.timestamp.hour < 6 or event.timestamp.hour > 23:
                anomalies.append("unusual_timing")

            # Проверка на частые действия
            if len(recent_events) > 50:
                anomalies.append("high_frequency")

            # Проверка на подозрительные действия
            if event.behavior_type == BehaviorType.SUSPICIOUS:
                anomalies.append("suspicious_behavior")

            # Проверка на злонамеренные действия
            if event.behavior_type == BehaviorType.MALICIOUS:
                anomalies.append("malicious_behavior")

            return anomalies

        except Exception as e:
            self.log_activity(f"Ошибка обнаружения аномалий: {e}", "error")
            return []

    def _identify_patterns(self, user_id: str, event: BehaviorEvent,
                           recent_events: List[BehaviorEvent]) -> List[str]:
        """Идентификация паттернов"""
        try:
            patterns = []

            # Анализ частоты действий
            if len(recent_events) > 20:
                patterns.append("frequent_user")

            # Анализ типов действий
            categories = [e.category for e in recent_events]
            if len(set(categories)) == 1:
                patterns.append("single_category_user")

            # Анализ времени активности
            hours = [e.timestamp.hour for e in recent_events]
            if len(set(hours)) < 3:
                patterns.append("consistent_timing")

            return patterns

        except Exception as e:
            self.log_activity(f"Ошибка идентификации паттернов: {e}", "error")
            return []

    def _calculate_overall_risk(self, event: BehaviorEvent, anomalies: List[str],
                                patterns: List[str]) -> Tuple[RiskLevel, float]:
        """Расчет общего риска"""
        try:
            risk_score = event.risk_score

            # Увеличиваем риск при наличии аномалий
            risk_score += len(anomalies) * 0.1

            # Увеличиваем риск при подозрительных паттернах
            if "suspicious_behavior" in anomalies:
                risk_score += 0.3
            if "malicious_behavior" in anomalies:
                risk_score += 0.5

            # Определяем уровень риска
            if risk_score >= 0.8:
                risk_level = RiskLevel.CRITICAL
            elif risk_score >= 0.6:
                risk_level = RiskLevel.HIGH
            elif risk_score >= 0.4:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW

            return risk_level, min(risk_score, 1.0)

        except Exception as e:
            self.log_activity(f"Ошибка расчета общего риска: {e}", "error")
            return RiskLevel.MEDIUM, 0.5

    def _generate_recommendations(self, risk_level: RiskLevel, anomalies: List[str],
                                  patterns: List[str]) -> List[str]:
        """Генерация рекомендаций"""
        try:
            recommendations = []

            if risk_level == RiskLevel.CRITICAL:
                recommendations.append("Немедленно заблокировать пользователя")
                recommendations.append("Уведомить администратора безопасности")
            elif risk_level == RiskLevel.HIGH:
                recommendations.append("Усилить мониторинг пользователя")
                recommendations.append("Проверить активность пользователя")
            elif risk_level == RiskLevel.MEDIUM:
                recommendations.append("Продолжить наблюдение")
                recommendations.append("Собрать дополнительную информацию")
            else:
                recommendations.append("Нормальное поведение")
                recommendations.append("Продолжить стандартный мониторинг")

            return recommendations

        except Exception as e:
            self.log_activity(f"Ошибка генерации рекомендаций: {e}", "error")
            return ["Ошибка анализа - требуется ручная проверка"]

    def _create_behavior_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Создание профиля поведения пользователя"""
        try:
            user_events = self.behavior_events.get(user_id, [])
            if not user_events:
                return None

            # Анализ паттернов пользователя
            categories = [e.category.value for e in user_events]
            types = [e.behavior_type.value for e in user_events]

            profile = {
                "user_id": user_id,
                "total_events": len(user_events),
                "most_common_category": max(set(categories), key=categories.count) if categories else "unknown",
                "most_common_type": max(set(types), key=types.count) if types else "unknown",
                "average_risk_score": statistics.mean([e.risk_score for e in user_events]),
                "created_at": datetime.now().isoformat(),
                "last_activity": max([e.timestamp for e in user_events]).isoformat() if user_events else None
            }

            return profile

        except Exception as e:
            self.log_activity(f"Ошибка создания профиля поведения: {e}", "error")
            return None

    def _update_behavior_metrics(self, analysis: BehaviorAnalysis):
        """Обновление метрик поведения"""
        try:
            self.behavior_metrics.total_events_analyzed += 1
            self.behavior_metrics.last_analysis = datetime.now()

            if analysis.overall_risk == RiskLevel.CRITICAL:
                self.behavior_metrics.malicious_behaviors += 1
            elif analysis.overall_risk == RiskLevel.HIGH:
                self.behavior_metrics.suspicious_behaviors += 1

            if analysis.anomalies_detected:
                self.behavior_metrics.anomalies_detected += len(analysis.anomalies_detected)

        except Exception as e:
            self.log_activity(f"Ошибка обновления метрик поведения: {e}", "error")

    def _behavior_analysis_task(self):
        """Задача анализа поведения"""
        try:
            while self.status == ComponentStatus.RUNNING:
                time.sleep(self.analysis_interval)

                # Анализ накопленных событий
                self._analyze_accumulated_events()

        except Exception as e:
            self.log_activity(f"Ошибка задачи анализа поведения: {e}", "error")

    def _pattern_learning_task(self):
        """Задача обучения паттернов"""
        try:
            while self.status == ComponentStatus.RUNNING:
                time.sleep(self.pattern_learning_window)

                # Обучение новых паттернов
                self._learn_new_patterns()

        except Exception as e:
            self.log_activity(f"Ошибка задачи обучения паттернов: {e}", "error")

    def _analyze_accumulated_events(self):
        """Анализ накопленных событий"""
        try:
            # Симуляция анализа накопленных событий
            for user_id, events in self.behavior_events.items():
                if len(events) > 10:  # Анализируем только при достаточном количестве событий
                    # Здесь можно добавить более сложный анализ
                    pass

        except Exception as e:
            self.log_activity(f"Ошибка анализа накопленных событий: {e}", "error")

    def _learn_new_patterns(self):
        """Обучение новых паттернов"""
        try:
            # Симуляция обучения новых паттернов
            for user_id, events in self.behavior_events.items():
                if len(events) > 20:
                    # Анализируем паттерны пользователя
                    patterns = self._identify_user_patterns(user_id, events)
                    if patterns:
                        if user_id not in self.behavior_patterns:
                            self.behavior_patterns[user_id] = []
                        self.behavior_patterns[user_id].extend(patterns)

        except Exception as e:
            self.log_activity(f"Ошибка обучения новых паттернов: {e}", "error")

    def _identify_user_patterns(self, user_id: str, events: List[BehaviorEvent]) -> List[BehaviorPattern]:
        """Идентификация паттернов пользователя"""
        try:
            patterns = []

            # Простой анализ паттернов
            if len(events) > 10:
                pattern = BehaviorPattern(
                    pattern_id=f"pattern-{user_id}-{int(time.time())}",
                    user_id=user_id,
                    pattern_type="user_behavior",
                    frequency=len(events),
                    confidence=0.8,
                    time_window=3600,
                    characteristics={"event_count": len(events)},
                    created_at=datetime.now(),
                    last_seen=datetime.now()
                )
                patterns.append(pattern)

            return patterns

        except Exception as e:
            self.log_activity(f"Ошибка идентификации паттернов пользователя: {e}", "error")
            return []

    def _save_behavior_state(self):
        """Сохранение состояния анализа поведения"""
        try:
            import os
            os.makedirs("/tmp/aladdin_behavior", exist_ok=True)

            data_to_save = {
                "patterns": {k: [p.to_dict() for p in v] for k, v in self.behavior_patterns.items()},
                "profiles": self.user_profiles,
                "metrics": self.behavior_metrics.to_dict(),
                "statistics": self.statistics,
                "saved_at": datetime.now().isoformat()
            }

            with open("/tmp/aladdin_behavior/last_state.json", 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)

            self.log_activity("Состояние анализа поведения сохранено", "info")
        except Exception as e:
            self.log_activity(f"Ошибка сохранения состояния анализа поведения: {e}", "error")
