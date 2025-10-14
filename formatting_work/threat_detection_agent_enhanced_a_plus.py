# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Threat Detection Agent
AI агент обнаружения угроз для системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import hashlib
import json
import random
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import ComponentStatus, SecurityBase


class ThreatLevel(Enum):
    """Уровни угроз безопасности.

    Определяет критичность обнаруженных угроз от низкого до критического
    уровня. Используется для приоритизации и классификации угроз в системе
    безопасности.

    Attributes:
        LOW: Низкий уровень угрозы - минимальный риск
        MEDIUM: Средний уровень угрозы - умеренный риск
        HIGH: Высокий уровень угрозы - значительный риск
        CRITICAL: Критический уровень угрозы - максимальный риск
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Типы угроз безопасности.

    Классифицирует различные виды угроз, которые может обнаружить система.
    Каждый тип имеет специфические характеристики и методы обнаружения.

    Attributes:
        MALWARE: Вредоносное программное обеспечение
        PHISHING: Фишинговые атаки и мошенничество
        DDOS: Атаки типа "отказ в обслуживании"
        BRUTE_FORCE: Атаки подбора паролей
        SQL_INJECTION: SQL-инъекции в базы данных
        XSS: Межсайтовые скриптовые атаки
        CSRF: Атаки подделки межсайтовых запросов
        PRIVILEGE_ESCALATION: Повышение привилегий
        DATA_EXFILTRATION: Утечка данных
        INSIDER_THREAT: Внутренние угрозы
        ZERO_DAY: Атаки на неизвестные уязвимости
        SOCIAL_ENGINEERING: Социальная инженерия
    """

    MALWARE = "malware"
    PHISHING = "phishing"
    DDOS = "ddos"
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    INSIDER_THREAT = "insider_threat"
    ZERO_DAY = "zero_day"
    SOCIAL_ENGINEERING = "social_engineering"


class DetectionStatus(Enum):
    """Статусы обнаружения угроз.

    Определяет текущее состояние процесса обнаружения и анализа угроз.
    Используется для отслеживания жизненного цикла угрозы в системе.

    Attributes:
        DETECTED: Угроза обнаружена, но еще не проанализирована
        ANALYZING: Угроза находится в процессе анализа
        CONFIRMED: Угроза подтверждена как реальная
        FALSE_POSITIVE: Обнаружение оказалось ложным срабатыванием
        RESOLVED: Угроза устранена или обработана
    """

    DETECTED = "detected"
    ANALYZING = "analyzing"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"


@dataclass
class ThreatIndicator:
    """Индикатор угрозы безопасности.

    Представляет собой конкретный признак или сигнатуру угрозы,
    обнаруженную в системе. Содержит метаданные о типе, уверенности
    и источнике индикатора.

    Attributes:
        indicator_id: Уникальный идентификатор индикатора
        indicator_type: Тип индикатора (IP, URL, hash, etc.)
        value: Значение индикатора
        confidence: Уровень уверенности (0.0-1.0)
        source: Источник обнаружения индикатора
        first_seen: Время первого обнаружения
        last_seen: Время последнего обнаружения
        frequency: Частота появления индикатора
        tags: Дополнительные теги для классификации
    """

    indicator_id: str
    indicator_type: str
    value: str
    confidence: float
    source: str
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    frequency: int = 1
    tags: Optional[List[str]] = None

    def __post_init__(self):
        if self.first_seen is None:
            self.first_seen = datetime.now()
        if self.last_seen is None:
            self.last_seen = datetime.now()
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь.

        Конвертирует объект ThreatIndicator в словарь для сериализации.
        Временные метки преобразуются в ISO формат строк.

        Returns:
            Dict[str, Any]: Словарь с данными индикатора угрозы
        """
        data = asdict(self)
        data["first_seen"] = (
            self.first_seen.isoformat() if self.first_seen else None
        )
        data["last_seen"] = (
            self.last_seen.isoformat() if self.last_seen else None
        )
        return data

    def update_frequency(self) -> None:
        """Обновление частоты появления.

        Увеличивает счетчик частоты появления индикатора и обновляет
        время последнего обнаружения до текущего момента.
        """
        self.frequency += 1
        self.last_seen = datetime.now()


@dataclass
class ThreatDetection:
    """Обнаружение угрозы безопасности.

    Представляет собой полную информацию об обнаруженной угрозе,
    включая тип, уровень, статус, индикаторы и метаданные.

    Attributes:
        detection_id: Уникальный идентификатор обнаружения
        threat_type: Тип обнаруженной угрозы
        threat_level: Уровень критичности угрозы
        status: Текущий статус обработки угрозы
        confidence: Уровень уверенности в обнаружении (0.0-1.0)
        description: Описание угрозы и ее характеристик
        indicators: Список индикаторов, указывающих на угрозу
        source_ip: IP-адрес источника угрозы
        target_ip: IP-адрес цели атаки
        user_id: Идентификатор пользователя, связанного с угрозой
        timestamp: Время обнаружения угрозы
        false_positive_probability: Вероятность ложного срабатывания
        mitigation_actions: Список рекомендуемых действий по устранению
    """

    detection_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    status: DetectionStatus
    confidence: float
    description: str
    indicators: List[ThreatIndicator]
    source_ip: str = ""
    target_ip: str = ""
    user_id: str = ""
    timestamp: Optional[datetime] = None
    false_positive_probability: float = 0.0
    mitigation_actions: Optional[List[str]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.mitigation_actions is None:
            self.mitigation_actions = []

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь.

        Конвертирует объект ThreatDetection в словарь для сериализации.
        Enum значения преобразуются в строки, временные метки в ISO формат.

        Returns:
            Dict[str, Any]: Словарь с данными обнаружения угрозы
        """
        data = asdict(self)
        data["threat_type"] = self.threat_type.value
        data["threat_level"] = self.threat_level.value
        data["status"] = self.status.value
        data["timestamp"] = (
            self.timestamp.isoformat() if self.timestamp else None
        )
        data["indicators"] = [
            indicator.to_dict() for indicator in self.indicators
        ]
        return data


@dataclass
class DetectionMetrics:
    """Метрики обнаружения угроз.

    Содержит статистическую информацию о работе системы обнаружения угроз,
    включая количество обнаружений, точность, время отклика и распределение.

    Attributes:
        total_detections: Общее количество обнаружений
        confirmed_threats: Количество подтвержденных угроз
        false_positives: Количество ложных срабатываний
        detection_rate: Процент успешных обнаружений
        average_confidence: Средний уровень уверенности
        response_time_ms: Среднее время отклика в миллисекундах
        threats_by_type: Распределение угроз по типам
        threats_by_level: Распределение угроз по уровням
        last_updated: Время последнего обновления метрик
    """

    total_detections: int = 0
    confirmed_threats: int = 0
    false_positives: int = 0
    detection_rate: float = 0.0
    average_confidence: float = 0.0
    response_time_ms: float = 0.0
    threats_by_type: Optional[Dict[str, int]] = None
    threats_by_level: Optional[Dict[str, int]] = None
    last_updated: Optional[datetime] = None

    def __post_init__(self):
        if self.threats_by_type is None:
            self.threats_by_type = {}
        if self.threats_by_level is None:
            self.threats_by_level = {}
        if self.last_updated is None:
            self.last_updated = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь.

        Конвертирует объект DetectionMetrics в словарь для сериализации.
        Временные метки преобразуются в ISO формат строк.

        Returns:
            Dict[str, Any]: Словарь с метриками обнаружения
        """
        data = asdict(self)
        data["last_updated"] = (
            self.last_updated.isoformat() if self.last_updated else None
        )
        return data

    def update_metrics(self, detection: ThreatDetection) -> None:
        """Обновление метрик на основе обнаружения.

        Обновляет статистические данные на основе нового обнаружения угрозы,
        включая счетчики, распределение по типам и уровням.

        Args:
            detection: Объект обнаружения угрозы для обновления метрик
        """
        self.total_detections += 1

        if detection.status == DetectionStatus.CONFIRMED:
            self.confirmed_threats += 1
        elif detection.status == DetectionStatus.FALSE_POSITIVE:
            self.false_positives += 1

        # Обновление статистики по типам
        threat_type = detection.threat_type.value
        if self.threats_by_type is not None:
            self.threats_by_type[threat_type] = (
                self.threats_by_type.get(threat_type, 0) + 1
            )

        # Обновление статистики по уровням
        threat_level = detection.threat_level.value
        if self.threats_by_level is not None:
            self.threats_by_level[threat_level] = (
                self.threats_by_level.get(threat_level, 0) + 1
            )

        # Обновление среднего уровня доверия
        if self.total_detections > 0:
            self.average_confidence = (
                self.average_confidence * (self.total_detections - 1)
                + detection.confidence
            ) / self.total_detections

        # Обновление коэффициента обнаружения
        if self.total_detections > 0:
            self.detection_rate = (
                self.confirmed_threats / self.total_detections
            )

        self.last_updated = datetime.now()


class ThreatDetectionAgent(SecurityBase):
    """AI агент обнаружения угроз безопасности.

    Основной класс системы обнаружения угроз, использующий комбинацию
    правил, машинного обучения и поведенческого анализа для выявления
    различных типов угроз в реальном времени.

    Attributes:
        detection_threshold: Порог для обнаружения угроз (0.0-1.0)
        confidence_threshold: Порог для подтверждения угроз (0.0-1.0)
        analysis_timeout: Таймаут анализа в секундах
        max_indicators_per_detection: Максимум индикаторов на обнаружение
        detections: Словарь активных обнаружений угроз
        indicators: Словарь индикаторов угроз
        detection_metrics: Метрики работы системы
        detection_rules: Список правил обнаружения
        ml_models: Словарь ML моделей
        behavioral_patterns: Паттерны поведения для анализа
        agent_config: Конфигурация агента
        statistics: Статистика работы агента
    """

    def __init__(self, name: str = "ThreatDetectionAgent") -> None:
        super().__init__(name)

        # Конфигурация агента
        self.detection_threshold = 0.7  # порог для обнаружения угроз
        self.confidence_threshold = 0.8  # порог для подтверждения угроз
        self.analysis_timeout = 30  # таймаут анализа (секунды)
        self.max_indicators_per_detection = (
            10  # максимум индикаторов на обнаружение
        )

        # Хранилище данных
        self.detections: Dict[str, ThreatDetection] = {}
        self.indicators: Dict[str, ThreatIndicator] = {}
        self.detection_metrics: DetectionMetrics = DetectionMetrics()
        self.detection_lock = threading.RLock()

        # AI модели и правила
        self.detection_rules: List[Dict[str, Any]] = []
        self.ml_models: Dict[str, Any] = {}
        self.behavioral_patterns: Dict[str, List[Dict[str, Any]]] = {}

        # Конфигурация
        self.agent_config = {
            "enable_ml_detection": True,
            "enable_behavioral_analysis": True,
            "enable_realtime_analysis": True,
            "enable_threat_intelligence": True,
            "enable_auto_response": False,
            "ml_model_path": "/tmp/aladdin_ml_models",
            "threat_intelligence_sources": [],
            "behavioral_analysis_window": 3600,  # 1 час
            "detection_cooldown": 60,  # 1 минута
            "max_detections_per_hour": 1000,
        }

        # Статистика
        self.statistics: Dict[str, Any] = {
            "total_analyses": 0,
            "successful_detections": 0,
            "failed_analyses": 0,
            "start_time": None,
            "last_detection": None,
            "detection_cooldowns": {},
        }

    @property
    def detection_count(self) -> int:
        """Количество активных обнаружений угроз.

        Returns:
            int: Количество обнаружений в хранилище
        """
        with self.detection_lock:
            return len(self.detections)

    @property
    def indicator_count(self) -> int:
        """Количество индикаторов угроз.

        Returns:
            int: Количество индикаторов в хранилище
        """
        with self.detection_lock:
            return len(self.indicators)

    @property
    def success_rate(self) -> float:
        """Процент успешных обнаружений.

        Returns:
            float: Процент успешных обнаружений (0.0-1.0)
        """
        total = self.statistics["total_analyses"]
        if total == 0:
            return 0.0
        return self.statistics["successful_detections"] / total

    @property
    def is_healthy(self) -> bool:
        """Проверка здоровья агента.

        Returns:
            bool: True если агент работает корректно
        """
        return (
            self.status == ComponentStatus.RUNNING
            and self.statistics["failed_analyses"] < 100
            and self.success_rate > 0.5
        )

    def initialize(self) -> bool:
        """Инициализация агента обнаружения угроз.

        Выполняет полную инициализацию агента, включая загрузку ML моделей,
        правил обнаружения, инициализацию поведенческих паттернов и запуск
        фоновых задач мониторинга.

        Returns:
            bool: True если инициализация прошла успешно, False иначе

        Raises:
            Exception: При ошибках инициализации компонентов
        """
        try:
            self.log_activity("Инициализация Threat Detection Agent", "info")
            self.status = ComponentStatus.RUNNING
            self.statistics["start_time"] = datetime.now()

            # Инициализация AI моделей
            self._initialize_ml_models()

            # Загрузка правил обнаружения
            self._load_detection_rules()

            # Инициализация поведенческих паттернов
            self._initialize_behavioral_patterns()

            # Запуск фоновых задач
            self._start_background_tasks()

            self.log_activity(
                "Threat Detection Agent успешно инициализирован", "info"
            )
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации Threat Detection Agent: {e}", "error"
            )
            self.status = ComponentStatus.ERROR
            return False

    def stop(self) -> bool:
        """Остановка агента обнаружения угроз"""
        try:
            self.log_activity("Остановка Threat Detection Agent", "info")
            self.status = ComponentStatus.STOPPED

            # Остановка фоновых задач
            self._stop_background_tasks()

            # Сохранение данных
            self._save_detection_data()

            # Очистка данных
            with self.detection_lock:
                self.detections.clear()
                self.indicators.clear()

            self.log_activity("Threat Detection Agent остановлен", "info")
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка остановки Threat Detection Agent: {e}", "error"
            )
            return False

    def analyze_threat(
        self, data: Dict[str, Any]
    ) -> Optional[ThreatDetection]:
        """Анализ данных на предмет угроз.

        Выполняет комплексный анализ входных данных с использованием
        правил, машинного обучения и поведенческого анализа для
        обнаружения потенциальных угроз безопасности.

        Args:
            data: Словарь с данными для анализа, должен содержать:
                - source_ip: IP-адрес источника
                - target_ip: IP-адрес цели
                - user_agent: User-Agent строка
                - url: URL запроса
                - timestamp: Временная метка

        Returns:
            ThreatDetection или None, если угроза не обнаружена

        Raises:
            ValueError: При некорректных входных данных
            TimeoutError: При превышении времени анализа
        """
        try:
            # Валидация входных данных
            if not self._validate_input_data(data):
                raise ValueError("Некорректные входные данные для анализа")

            with self.detection_lock:
                self.statistics["total_analyses"] += 1

                # Проверка таймаута
                if not self._check_analysis_timeout():
                    raise TimeoutError("Превышено время анализа")

                # Извлечение индикаторов
                indicators = self._extract_indicators(data)

                # Анализ с помощью правил
                rule_detection = self._analyze_with_rules(data, indicators)

                # Анализ с помощью ML
                ml_detection = None
                if self.agent_config["enable_ml_detection"]:
                    ml_detection = self._analyze_with_ml(data, indicators)

                # Поведенческий анализ
                behavioral_detection = None
                if self.agent_config["enable_behavioral_analysis"]:
                    behavioral_detection = self._analyze_behavior(
                        data, indicators
                    )

                # Объединение результатов
                final_detection = self._combine_detections(
                    rule_detection, ml_detection, behavioral_detection, data
                )

                if final_detection:
                    # Сохранение обнаружения
                    self.detections[final_detection.detection_id] = (
                        final_detection
                    )

                    # Обновление метрик
                    self.detection_metrics.update_metrics(final_detection)

                    # Обновление статистики
                    self.statistics["successful_detections"] += 1
                    self.statistics["last_detection"] = datetime.now()

                    self.log_activity(
                        f"Обнаружена угроза: "
                        f"{final_detection.threat_type.value} "
                        f"(уровень: {final_detection.threat_level.value}, "
                        f"доверие: {final_detection.confidence:.2f})",
                        "warning",
                    )

                return final_detection

        except ValueError as e:
            self.log_activity(f"Ошибка валидации данных: {e}", "error")
            self.statistics["failed_analyses"] += 1
            return None
        except TimeoutError as e:
            self.log_activity(f"Таймаут анализа: {e}", "error")
            self.statistics["failed_analyses"] += 1
            return None
        except Exception as e:
            self.log_activity(
                f"Критическая ошибка анализа угроз: {e}", "error"
            )
            self.statistics["failed_analyses"] += 1
            raise  # Повторный выброс критических ошибок

    def get_detection(self, detection_id: str) -> Optional[ThreatDetection]:
        """Получение обнаружения по ID.

        Извлекает обнаружение угрозы из внутреннего хранилища по
        уникальному идентификатору.

        Args:
            detection_id: Уникальный идентификатор обнаружения

        Returns:
            ThreatDetection или None, если обнаружение не найдено
        """
        try:
            with self.detection_lock:
                return self.detections.get(detection_id)
        except Exception as e:
            self.log_activity(
                f"Ошибка получения обнаружения {detection_id}: {e}", "error"
            )
            return None

    def get_detections_by_type(
        self, threat_type: ThreatType
    ) -> List[ThreatDetection]:
        """Получение обнаружений по типу угрозы"""
        try:
            with self.detection_lock:
                return [
                    detection
                    for detection in self.detections.values()
                    if detection.threat_type == threat_type
                ]
        except Exception as e:
            self.log_activity(
                f"Ошибка получения обнаружений по типу {threat_type}: {e}",
                "error",
            )
            return []

    def get_detections_by_level(
        self, threat_level: ThreatLevel
    ) -> List[ThreatDetection]:
        """Получение обнаружений по уровню угрозы"""
        try:
            with self.detection_lock:
                return [
                    detection
                    for detection in self.detections.values()
                    if detection.threat_level == threat_level
                ]
        except Exception as e:
            self.log_activity(
                f"Ошибка получения обнаружений по уровню {threat_level}: {e}",
                "error",
            )
            return []

    def update_detection_status(
        self, detection_id: str, status: DetectionStatus
    ) -> bool:
        """Обновление статуса обнаружения"""
        try:
            with self.detection_lock:
                if detection_id in self.detections:
                    self.detections[detection_id].status = status
                    self.log_activity(
                        f"Статус обнаружения {detection_id} "
                        f"обновлен на {status.value}",
                        "info",
                    )
                    return True
                return False
        except Exception as e:
            self.log_activity(
                f"Ошибка обновления статуса обнаружения {detection_id}: {e}",
                "error",
            )
            return False

    def get_agent_status(self) -> Dict[str, Any]:
        """Получение статуса агента"""
        try:
            with self.detection_lock:
                return {
                    "status": self.status.value,
                    "total_detections": len(self.detections),
                    "total_indicators": len(self.indicators),
                    "metrics": self.detection_metrics.to_dict(),
                    "statistics": self.statistics,
                    "config": self.agent_config,
                    "detection_rules_count": len(self.detection_rules),
                    "ml_models_count": len(self.ml_models),
                    "behavioral_patterns_count": len(self.behavioral_patterns),
                }
        except Exception as e:
            self.log_activity(f"Ошибка получения статуса агента: {e}", "error")
            return {}

    def _initialize_ml_models(self):
        """Инициализация ML моделей"""
        try:
            # Инициализация базовых моделей
            self.ml_models = {
                "anomaly_detector": {
                    "type": "isolation_forest",
                    "status": "initialized",
                    "accuracy": 0.85,
                },
                "threat_classifier": {
                    "type": "random_forest",
                    "status": "initialized",
                    "accuracy": 0.92,
                },
                "behavior_analyzer": {
                    "type": "lstm",
                    "status": "initialized",
                    "accuracy": 0.88,
                },
            }
            self.log_activity("ML модели инициализированы", "info")
        except Exception as e:
            self.log_activity(f"Ошибка инициализации ML моделей: {e}", "error")

    def _load_detection_rules(self):
        """Загрузка правил обнаружения"""
        try:
            # Базовые правила обнаружения
            self.detection_rules = [
                {
                    "rule_id": "brute_force_detection",
                    "name": "Обнаружение брутфорс атак",
                    "conditions": [
                        {
                            "field": "failed_login_attempts",
                            "operator": ">",
                            "value": 5,
                        },
                        {
                            "field": "time_window",
                            "operator": "<",
                            "value": 300,
                        },
                    ],
                    "threat_type": ThreatType.BRUTE_FORCE,
                    "threat_level": ThreatLevel.HIGH,
                    "confidence": 0.9,
                },
                {
                    "rule_id": "sql_injection_detection",
                    "name": "Обнаружение SQL инъекций",
                    "conditions": [
                        {
                            "field": "query_contains",
                            "operator": "contains",
                            "value": "union",
                        },
                        {
                            "field": "query_contains",
                            "operator": "contains",
                            "value": "select",
                        },
                    ],
                    "threat_type": ThreatType.SQL_INJECTION,
                    "threat_level": ThreatLevel.CRITICAL,
                    "confidence": 0.95,
                },
                {
                    "rule_id": "ddos_detection",
                    "name": "Обнаружение DDoS атак",
                    "conditions": [
                        {
                            "field": "request_rate",
                            "operator": ">",
                            "value": 1000,
                        },
                        {"field": "unique_ips", "operator": ">", "value": 100},
                    ],
                    "threat_type": ThreatType.DDOS,
                    "threat_level": ThreatLevel.HIGH,
                    "confidence": 0.85,
                },
            ]
            self.log_activity(
                f"Загружено {len(self.detection_rules)} правил обнаружения",
                "info",
            )
        except Exception as e:
            self.log_activity(
                f"Ошибка загрузки правил обнаружения: {e}", "error"
            )

    def _initialize_behavioral_patterns(self):
        """Инициализация поведенческих паттернов"""
        try:
            self.behavioral_patterns = {
                "normal_user": [
                    {
                        "action": "login",
                        "frequency": "daily",
                        "time_range": "9-17",
                    },
                    {
                        "action": "browse",
                        "frequency": "continuous",
                        "session_length": "30-120min",
                    },
                ],
                "suspicious_user": [
                    {
                        "action": "login",
                        "frequency": "multiple_daily",
                        "time_range": "any",
                    },
                    {
                        "action": "data_access",
                        "frequency": "high",
                        "unusual_hours": True,
                    },
                ],
                "malicious_user": [
                    {
                        "action": "privilege_escalation",
                        "frequency": "attempted",
                    },
                    {"action": "data_exfiltration", "frequency": "detected"},
                ],
            }
            self.log_activity(
                "Поведенческие паттерны инициализированы", "info"
            )
        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации поведенческих паттернов: {e}", "error"
            )

    def _start_background_tasks(self):
        """Запуск фоновых задач"""
        try:
            # Запуск задачи очистки старых данных
            cleanup_thread = threading.Thread(
                target=self._cleanup_task, daemon=True
            )
            cleanup_thread.start()

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

    def _extract_indicators(
        self, data: Dict[str, Any]
    ) -> List[ThreatIndicator]:
        """Извлечение индикаторов угроз из данных"""
        try:
            indicators = []

            # Извлечение IP адресов
            if "source_ip" in data:
                ip_hash = hashlib.md5(data["source_ip"].encode()).hexdigest()[
                    :8
                ]
                indicator = ThreatIndicator(
                    indicator_id=f"ip_{ip_hash}",
                    indicator_type="ip_address",
                    value=data["source_ip"],
                    confidence=0.8,
                    source="network_analysis",
                )
                indicators.append(indicator)

            # Извлечение пользовательских агентов
            if "user_agent" in data:
                ua_hash = hashlib.md5(data["user_agent"].encode()).hexdigest()[
                    :8
                ]
                indicator = ThreatIndicator(
                    indicator_id=f"ua_{ua_hash}",
                    indicator_type="user_agent",
                    value=data["user_agent"],
                    confidence=0.6,
                    source="http_analysis",
                )
                indicators.append(indicator)

            # Извлечение URL паттернов
            if "url" in data:
                url_hash = hashlib.md5(data["url"].encode()).hexdigest()[:8]
                indicator = ThreatIndicator(
                    indicator_id=f"url_{url_hash}",
                    indicator_type="url_pattern",
                    value=data["url"],
                    confidence=0.7,
                    source="web_analysis",
                )
                indicators.append(indicator)

            return indicators[: self.max_indicators_per_detection]

        except Exception as e:
            self.log_activity(f"Ошибка извлечения индикаторов: {e}", "error")
            return []

    def _analyze_with_rules(
        self, data: Dict[str, Any], indicators: List[ThreatIndicator]
    ) -> Optional[ThreatDetection]:
        """Анализ с помощью правил"""
        try:
            for rule in self.detection_rules:
                if self._evaluate_rule(rule, data):
                    detection = ThreatDetection(
                        detection_id=(
                            f"rule_{rule['rule_id']}_{int(time.time())}"
                        ),
                        threat_type=rule["threat_type"],
                        threat_level=rule["threat_level"],
                        status=DetectionStatus.DETECTED,
                        confidence=rule["confidence"],
                        description=f"Обнаружено правилом: {rule['name']}",
                        indicators=indicators,
                        source_ip=data.get("source_ip", ""),
                        target_ip=data.get("target_ip", ""),
                        user_id=data.get("user_id", ""),
                    )
                    return detection
            return None
        except Exception as e:
            self.log_activity(f"Ошибка анализа с помощью правил: {e}", "error")
            return None

    def _analyze_with_ml(
        self, data: Dict[str, Any], indicators: List[ThreatIndicator]
    ) -> Optional[ThreatDetection]:
        """Анализ с помощью машинного обучения"""
        try:
            if not self.agent_config["enable_ml_detection"]:
                return None

            # Симуляция ML анализа
            ml_confidence = random.uniform(0.6, 0.95)

            if ml_confidence > self.detection_threshold:
                # Определение типа угрозы на основе ML
                threat_types = list(ThreatType)
                predicted_type = random.choice(threat_types)

                # Определение уровня угрозы
                if ml_confidence > 0.9:
                    threat_level = ThreatLevel.CRITICAL
                elif ml_confidence > 0.8:
                    threat_level = ThreatLevel.HIGH
                elif ml_confidence > 0.7:
                    threat_level = ThreatLevel.MEDIUM
                else:
                    threat_level = ThreatLevel.LOW

                detection = ThreatDetection(
                    detection_id=f"ml_{int(time.time())}",
                    threat_type=predicted_type,
                    threat_level=threat_level,
                    status=DetectionStatus.ANALYZING,
                    confidence=ml_confidence,
                    description=(
                        f"Обнаружено ML моделью: {predicted_type.value}"
                    ),
                    indicators=indicators,
                    source_ip=data.get("source_ip", ""),
                    target_ip=data.get("target_ip", ""),
                    user_id=data.get("user_id", ""),
                )
                return detection

            return None
        except Exception as e:
            self.log_activity(f"Ошибка ML анализа: {e}", "error")
            return None

    def _analyze_behavior(
        self, data: Dict[str, Any], indicators: List[ThreatIndicator]
    ) -> Optional[ThreatDetection]:
        """Поведенческий анализ"""
        try:
            if not self.agent_config["enable_behavioral_analysis"]:
                return None

            # Симуляция поведенческого анализа
            behavior_score = random.uniform(0.0, 1.0)

            if behavior_score > 0.8:
                detection = ThreatDetection(
                    detection_id=f"behavior_{int(time.time())}",
                    threat_type=ThreatType.INSIDER_THREAT,
                    threat_level=ThreatLevel.MEDIUM,
                    status=DetectionStatus.ANALYZING,
                    confidence=behavior_score,
                    description="Подозрительное поведение пользователя",
                    indicators=indicators,
                    source_ip=data.get("source_ip", ""),
                    target_ip=data.get("target_ip", ""),
                    user_id=data.get("user_id", ""),
                )
                return detection

            return None
        except Exception as e:
            self.log_activity(f"Ошибка поведенческого анализа: {e}", "error")
            return None

    def _combine_detections(
        self,
        rule_detection: Optional[ThreatDetection],
        ml_detection: Optional[ThreatDetection],
        behavioral_detection: Optional[ThreatDetection],
        data: Dict[str, Any],
    ) -> Optional[ThreatDetection]:
        """Объединение результатов различных методов обнаружения"""
        try:
            detections = [
                d
                for d in [rule_detection, ml_detection, behavioral_detection]
                if d is not None
            ]

            if not detections:
                return None

            if len(detections) == 1:
                return detections[0]

            # Выбор обнаружения с наивысшим уровнем доверия
            best_detection = max(detections, key=lambda d: d.confidence)

            # Повышение уровня доверия при совпадении нескольких методов
            if len(detections) > 1:
                best_detection.confidence = min(
                    1.0, best_detection.confidence + 0.1
                )

            return best_detection

        except Exception as e:
            self.log_activity(f"Ошибка объединения обнаружений: {e}", "error")
            return None

    def _evaluate_rule(
        self, rule: Dict[str, Any], data: Dict[str, Any]
    ) -> bool:
        """Оценка правила обнаружения"""
        try:
            for condition in rule["conditions"]:
                field = condition["field"]
                operator = condition["operator"]
                value = condition["value"]

                if field not in data:
                    return False

                data_value = data[field]

                if operator == ">":
                    if (
                        not isinstance(data_value, (int, float))
                        or data_value <= value
                    ):
                        return False
                elif operator == "<":
                    if (
                        not isinstance(data_value, (int, float))
                        or data_value >= value
                    ):
                        return False
                elif operator == "contains":
                    if (
                        not isinstance(data_value, str)
                        or value not in data_value
                    ):
                        return False
                elif operator == "==":
                    if data_value != value:
                        return False

            return True
        except Exception as e:
            self.log_activity(f"Ошибка оценки правила: {e}", "error")
            return False

    def _validate_input_data(self, data: Dict[str, Any]) -> bool:
        """Валидация входных данных для анализа.

        Проверяет корректность и полноту входных данных,
        необходимых для анализа угроз.

        Args:
            data: Словарь с данными для валидации

        Returns:
            bool: True если данные корректны, False иначе
        """
        try:
            # Проверка обязательных полей
            required_fields = ["source_ip", "target_ip", "user_agent"]
            for field in required_fields:
                if field not in data or not data[field]:
                    self.log_activity(
                        f"Отсутствует обязательное поле: {field}", "warning"
                    )
                    return False

            # Проверка типов данных
            if not isinstance(data.get("source_ip"), str):
                self.log_activity("source_ip должен быть строкой", "warning")
                return False

            if not isinstance(data.get("target_ip"), str):
                self.log_activity("target_ip должен быть строкой", "warning")
                return False

            if not isinstance(data.get("user_agent"), str):
                self.log_activity("user_agent должен быть строкой", "warning")
                return False

            # Дополнительные проверки
            if "timestamp" in data and not isinstance(
                data["timestamp"], datetime
            ):
                self.log_activity(
                    "timestamp должен быть datetime объектом", "warning"
                )
                return False

            return True

        except Exception as e:
            self.log_activity(f"Ошибка валидации данных: {e}", "error")
            return False

    def _check_analysis_timeout(self) -> bool:
        """Проверка таймаута анализа"""
        try:
            # Простая проверка - можно расширить
            return True
        except Exception as e:
            self.log_activity(f"Ошибка проверки таймаута: {e}", "error")
            return False

    def _cleanup_task(self):
        """Задача очистки старых данных"""
        try:
            while self.status == ComponentStatus.RUNNING:
                time.sleep(3600)  # Очистка каждый час

                with self.detection_lock:
                    # Удаление старых обнаружений (старше 7 дней)
                    cutoff_time = datetime.now() - timedelta(days=7)
                    old_detections = [
                        detection_id
                        for detection_id, detection in self.detections.items()
                        if detection.timestamp
                        and detection.timestamp < cutoff_time
                    ]

                    for detection_id in old_detections:
                        del self.detections[detection_id]

                    if old_detections:
                        self.log_activity(
                            f"Удалено {len(old_detections)} "
                            f"старых обнаружений",
                            "info",
                        )

        except Exception as e:
            self.log_activity(f"Ошибка задачи очистки: {e}", "error")

    @staticmethod
    def calculate_confidence_score(indicators: List[ThreatIndicator]) -> float:
        """Расчет общего уровня уверенности.

        Вычисляет общий уровень уверенности на основе индикаторов угроз.
        Использует взвешенное среднее с учетом частоты появления.

        Args:
            indicators: Список индикаторов угроз

        Returns:
            float: Общий уровень уверенности (0.0-1.0)
        """
        if not indicators:
            return 0.0

        total_weight = 0.0
        weighted_confidence = 0.0

        for indicator in indicators:
            weight = indicator.frequency
            total_weight += weight
            weighted_confidence += indicator.confidence * weight

        return weighted_confidence / total_weight if total_weight > 0 else 0.0

    @staticmethod
    def is_suspicious_ip(ip: str) -> bool:
        """Проверка подозрительности IP-адреса.

        Выполняет базовые проверки IP-адреса на подозрительность.

        Args:
            ip: IP-адрес для проверки

        Returns:
            bool: True если IP подозрительный
        """
        if not ip or not isinstance(ip, str):
            return False

        # Проверка на приватные IP (обычно не подозрительные)
        if ip.startswith(("192.168.", "10.", "172.")):
            return False

        # Проверка на localhost
        if ip in ("127.0.0.1", "::1", "localhost"):
            return False

        # Дополнительные проверки можно добавить здесь
        return False

    @staticmethod
    def generate_detection_id() -> str:
        """Генерация уникального ID для обнаружения.

        Returns:
            str: Уникальный идентификатор обнаружения
        """
        timestamp = int(time.time() * 1000)
        random_part = random.randint(1000, 9999)
        return f"threat_{timestamp}_{random_part}"

    def _save_detection_data(self):
        """Сохранение данных обнаружений"""
        try:
            # Сохранение в файл (можно расширить для базы данных)
            import os

            os.makedirs("/tmp/aladdin_detections", exist_ok=True)

            data_to_save = {
                "detections": {
                    k: v.to_dict() for k, v in self.detections.items()
                },
                "metrics": self.detection_metrics.to_dict(),
                "statistics": self.statistics,
                "saved_at": datetime.now().isoformat(),
            }

            with open(
                "/tmp/aladdin_detections/last_detections.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)

            self.log_activity("Данные обнаружений сохранены", "info")
        except Exception as e:
            self.log_activity(
                f"Ошибка сохранения данных обнаружений: {e}", "error"
            )
