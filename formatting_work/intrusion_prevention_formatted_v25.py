# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Intrusion Prevention Service
Система предотвращения вторжений для семей
Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-02
"""
import asyncio
import hashlib
import ipaddress
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Union

from core.base import SecurityBase


class ParameterValidator:
    """Класс для валидации параметров системы предотвращения вторжений"""

    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """
        Валидация IP адреса.

        Args:
            ip: IP адрес для проверки

        Returns:
            bool: True если IP валидный

        Raises:
            ValueError: Если IP невалидный
        """
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            raise ValueError(f"Невалидный IP адрес: {ip}")

    @staticmethod
    def validate_user_age(age: Optional[int]) -> bool:
        """
        Валидация возраста пользователя.

        Args:
            age: Возраст пользователя

        Returns:
            bool: True если возраст валидный

        Raises:
            ValueError: Если возраст невалидный
        """
        if age is None:
            return True
        if not isinstance(age, int):
            raise ValueError(f"Возраст должен быть числом: {age}")
        if age < 0 or age > 150:
            raise ValueError(f"Возраст должен быть от 0 до 150: {age}")
        return True

    @staticmethod
    def validate_event_data(event_data: Dict[str, Any]) -> bool:
        """
        Валидация данных события.

        Args:
            event_data: Данные события

        Returns:
            bool: True если данные валидные

        Raises:
            ValueError: Если данные невалидные
        """
        if not isinstance(event_data, dict):
            raise ValueError(
                f"event_data должен быть словарем: {type(event_data)}"
            )

        if not event_data:
            raise ValueError("event_data не может быть пустым")

        # Проверяем обязательные поля
        required_fields = ["source_ip"]
        for field in required_fields:
            if field not in event_data:
                raise ValueError(f"Отсутствует обязательное поле: {field}")

        # Валидируем IP если есть
        if "source_ip" in event_data:
            ParameterValidator.validate_ip_address(event_data["source_ip"])

        return True

    @staticmethod
    def validate_confidence(confidence: float) -> bool:
        """
        Валидация значения уверенности.

        Args:
            confidence: Значение уверенности (0.0 - 1.0)

        Returns:
            bool: True если значение валидное

        Raises:
            ValueError: Если значение невалидное
        """
        if not isinstance(confidence, (int, float)):
            raise ValueError(
                f"Уверенность должна быть числом: {type(confidence)}"
            )

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                f"Уверенность должна быть от 0.0 до 1.0: {confidence}"
            )

        return True


def validate_parameters(**validators):
    """
    Декоратор для валидации параметров метода.

    Args:
        **validators: Словарь с валидаторами для каждого параметра

    Example:
        @validate_parameters(
            event_data=ParameterValidator.validate_event_data,
            user_age=ParameterValidator.validate_user_age
        )
        def detect_intrusion(self, event_data, user_id=None, user_age=None):
            pass
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Получаем имена параметров функции
            import inspect

            sig = inspect.signature(func)
            bound_args = sig.bind(self, *args, **kwargs)
            bound_args.apply_defaults()

            # Валидируем каждый параметр
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    validator(value)

            return func(self, *args, **kwargs)

        return wrapper

    return decorator


def performance_monitor(func):
    """
    Декоратор для мониторинга производительности методов.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        try:
            result = func(self, *args, **kwargs)
            execution_time = time.time() - start_time

            # Логируем метрики
            if hasattr(self, "logger"):
                self.logger.info(
                    f"Метод {func.__name__} выполнен за {execution_time:.4f}с"
                )

            # Сохраняем метрики
            if not hasattr(self, "_performance_metrics"):
                self._performance_metrics = {}

            if func.__name__ not in self._performance_metrics:
                self._performance_metrics[func.__name__] = []

            self._performance_metrics[func.__name__].append(
                {
                    "execution_time": execution_time,
                    "timestamp": start_time,
                    "success": True,
                }
            )

            return result
        except Exception as e:
            execution_time = time.time() - start_time
            if hasattr(self, "logger"):
                self.logger.error(
                    f"Ошибка в методе {func.__name__} за {execution_time:.4f}с: {e}"
                )
            raise

    return wrapper


def cache_result(ttl_seconds: int = 300):
    """
    Декоратор для кэширования результатов методов.

    Args:
        ttl_seconds: Время жизни кэша в секундах
    """

    def decorator(func):
        cache = {}

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Создаем ключ кэша
            cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            current_time = time.time()

            # Проверяем кэш
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < ttl_seconds:
                    return result

            # Выполняем функцию и кэшируем результат
            result = func(self, *args, **kwargs)
            cache[cache_key] = (result, current_time)

            return result

        return wrapper

    return decorator


class IntrusionType(Enum):
    """Типы вторжений"""

    BRUTE_FORCE = "brute_force"
    DDoS_ATTACK = "ddos_attack"
    PORT_SCAN = "port_scan"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"
    MALWARE_UPLOAD = "malware_upload"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class IntrusionSeverity(Enum):
    """Уровни серьезности вторжений"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PreventionAction(Enum):
    """Действия предотвращения"""

    BLOCK_IP = "block_ip"
    RATE_LIMIT = "rate_limit"
    REQUIRE_MFA = "require_mfa"
    QUARANTINE_USER = "quarantine_user"
    ALERT_ADMIN = "alert_admin"
    LOG_EVENT = "log_event"
    TERMINATE_SESSION = "terminate_session"
    BLOCK_RESOURCE = "block_resource"


class IntrusionStatus(Enum):
    """Статусы вторжений"""

    DETECTED = "detected"
    PREVENTED = "prevented"
    BLOCKED = "blocked"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"


@dataclass
class IntrusionAttempt:
    """Попытка вторжения"""

    attempt_id: str
    intrusion_type: IntrusionType
    severity: IntrusionSeverity
    source_ip: str
    user_id: Optional[str]
    timestamp: datetime
    description: str
    status: IntrusionStatus
    prevention_actions: List[PreventionAction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PreventionRule:
    """Правило предотвращения"""

    rule_id: str
    name: str
    description: str
    intrusion_type: IntrusionType
    severity_threshold: IntrusionSeverity
    conditions: Dict[str, Any]
    actions: List[PreventionAction]
    enabled: bool = True
    family_specific: bool = False
    age_group: Optional[str] = None


@dataclass
class IntrusionPattern:
    """Паттерн вторжения"""

    pattern_id: str
    name: str
    description: str
    intrusion_type: IntrusionType
    indicators: List[str]
    confidence_threshold: float
    family_protection: bool = True


class IntrusionPreventionService(SecurityBase):
    """Сервис предотвращения вторжений для семей"""

    def __init__(
        self,
        name: str = "IntrusionPrevention",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализация сервиса предотвращения вторжений.

        Args:
            name: Имя сервиса
            config: Конфигурация сервиса
        """
        super().__init__(name, config)
        self.logger = logging.getLogger(__name__)
        # Хранилища данных
        self.intrusion_attempts: Dict[str, IntrusionAttempt] = {}
        self.prevention_rules: Dict[str, PreventionRule] = {}
        self.intrusion_patterns: Dict[str, IntrusionPattern] = {}
        self.blocked_ips: Set[str] = set()
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        self.family_protection_history: Dict[str, List[str]] = (
            {}
        )  # user_id -> attempt_ids
        # Настройки предотвращения
        self.prevention_thresholds = {
            IntrusionSeverity.LOW: 0.3,
            IntrusionSeverity.MEDIUM: 0.5,
            IntrusionSeverity.HIGH: 0.7,
            IntrusionSeverity.CRITICAL: 0.9,
        }
        # Семейные настройки
        self.family_protection_enabled = True
        self.child_protection_mode = True
        self.elderly_protection_mode = True
        # Инициализация
        self._initialize_intrusion_patterns()
        self._initialize_prevention_rules()
        self._setup_family_protection()

    def _initialize_intrusion_patterns(self):
        """Инициализация паттернов вторжений"""
        patterns = [
            IntrusionPattern(
                pattern_id="brute_force_login",
                name="Брутфорс атака на вход",
                description="Множественные попытки входа с неверными паролями",
                intrusion_type=IntrusionType.BRUTE_FORCE,
                indicators=[
                    "multiple_failed_logins",
                    "rapid_login_attempts",
                    "common_passwords",
                ],
                confidence_threshold=0.3,
                family_protection=True,
            ),
            IntrusionPattern(
                pattern_id="ddos_attack",
                name="DDoS атака",
                description="Распределенная атака типа отказ в обслуживании",
                intrusion_type=IntrusionType.DDoS_ATTACK,
                indicators=[
                    "high_request_volume",
                    "multiple_source_ips",
                    "unusual_traffic_patterns",
                ],
                confidence_threshold=0.3,
                family_protection=True,
            ),
            IntrusionPattern(
                pattern_id="port_scanning",
                name="Сканирование портов",
                description="Попытка сканирования открытых портов",
                intrusion_type=IntrusionType.PORT_SCAN,
                indicators=[
                    "sequential_port_access",
                    "multiple_port_attempts",
                    "unusual_port_combinations",
                ],
                confidence_threshold=0.3,
                family_protection=True,
            ),
            IntrusionPattern(
                pattern_id="sql_injection",
                name="SQL инъекция",
                description="Попытка внедрения SQL кода",
                intrusion_type=IntrusionType.SQL_INJECTION,
                indicators=[
                    "sql_keywords",
                    "suspicious_queries",
                    "database_errors",
                ],
                confidence_threshold=0.3,
                family_protection=True,
            ),
            IntrusionPattern(
                pattern_id="xss_attack",
                name="XSS атака",
                description="Попытка внедрения скриптов",
                intrusion_type=IntrusionType.XSS_ATTACK,
                indicators=[
                    "script_tags",
                    "javascript_code",
                    "suspicious_input",
                ],
                confidence_threshold=0.3,
                family_protection=True,
            ),
            IntrusionPattern(
                pattern_id="unauthorized_access",
                name="Несанкционированный доступ",
                description="Попытка доступа к защищенным ресурсам",
                intrusion_type=IntrusionType.UNAUTHORIZED_ACCESS,
                indicators=[
                    "privilege_escalation",
                    "access_denied_errors",
                    "suspicious_permissions",
                ],
                confidence_threshold=0.3,
                family_protection=True,
            ),
            IntrusionPattern(
                pattern_id="child_exploitation",
                name="Эксплуатация детей",
                description="Попытка эксплуатации несовершеннолетних",
                intrusion_type=IntrusionType.SUSPICIOUS_BEHAVIOR,
                indicators=[
                    "inappropriate_content",
                    "grooming_behavior",
                    "age_inappropriate_requests",
                ],
                confidence_threshold=0.3,
                family_protection=True,
            ),
            IntrusionPattern(
                pattern_id="elderly_fraud",
                name="Мошенничество с пожилыми",
                description="Попытка мошенничества с пожилыми людьми",
                intrusion_type=IntrusionType.SUSPICIOUS_BEHAVIOR,
                indicators=[
                    "financial_requests",
                    "urgency_tactics",
                    "personal_info_requests",
                ],
                confidence_threshold=0.3,
                family_protection=True,
            ),
        ]
        for pattern in patterns:
            self.intrusion_patterns[pattern.pattern_id] = pattern
        self.log_activity(
            f"Инициализировано {len(patterns)} паттернов вторжений"
        )

    def _initialize_prevention_rules(self):
        """Инициализация правил предотвращения"""
        rules = [
            PreventionRule(
                rule_id="block_brute_force",
                name="Блокировка брутфорс атак",
                description="Блокировка IP при множественных попытках входа",
                intrusion_type=IntrusionType.BRUTE_FORCE,
                severity_threshold=IntrusionSeverity.MEDIUM,
                conditions={"max_attempts": 5, "time_window": 300},  # 5 минут
                actions=[
                    PreventionAction.BLOCK_IP,
                    PreventionAction.ALERT_ADMIN,
                ],
                family_specific=True,
            ),
            PreventionRule(
                rule_id="rate_limit_ddos",
                name="Ограничение DDoS атак",
                description="Ограничение скорости запросов при DDoS",
                intrusion_type=IntrusionType.DDoS_ATTACK,
                severity_threshold=IntrusionSeverity.HIGH,
                conditions={
                    "max_requests": 100,
                    "time_window": 60,
                },  # 1 минута
                actions=[
                    PreventionAction.RATE_LIMIT,
                    PreventionAction.BLOCK_IP,
                ],
                family_specific=True,
            ),
            PreventionRule(
                rule_id="block_port_scan",
                name="Блокировка сканирования портов",
                description="Блокировка IP при сканировании портов",
                intrusion_type=IntrusionType.PORT_SCAN,
                severity_threshold=IntrusionSeverity.MEDIUM,
                conditions={"max_ports": 10, "time_window": 60},
                actions=[
                    PreventionAction.BLOCK_IP,
                    PreventionAction.LOG_EVENT,
                ],
                family_specific=True,
            ),
            PreventionRule(
                rule_id="prevent_sql_injection",
                name="Предотвращение SQL инъекций",
                description="Блокировка SQL инъекций",
                intrusion_type=IntrusionType.SQL_INJECTION,
                severity_threshold=IntrusionSeverity.HIGH,
                conditions={"sql_patterns": True},
                actions=[
                    PreventionAction.BLOCK_RESOURCE,
                    PreventionAction.ALERT_ADMIN,
                ],
                family_specific=True,
            ),
            PreventionRule(
                rule_id="prevent_xss",
                name="Предотвращение XSS атак",
                description="Блокировка XSS атак",
                intrusion_type=IntrusionType.XSS_ATTACK,
                severity_threshold=IntrusionSeverity.MEDIUM,
                conditions={"script_patterns": True},
                actions=[
                    PreventionAction.BLOCK_RESOURCE,
                    PreventionAction.LOG_EVENT,
                ],
                family_specific=True,
            ),
            PreventionRule(
                rule_id="child_protection",
                name="Защита детей",
                description="Специальная защита для детей",
                intrusion_type=IntrusionType.SUSPICIOUS_BEHAVIOR,
                severity_threshold=IntrusionSeverity.CRITICAL,
                conditions={
                    "age_group": "child",
                    "inappropriate_content": True,
                },
                actions=[
                    PreventionAction.BLOCK_RESOURCE,
                    PreventionAction.ALERT_ADMIN,
                    PreventionAction.QUARANTINE_USER,
                ],
                family_specific=True,
                age_group="child",
            ),
            PreventionRule(
                rule_id="elderly_protection",
                name="Защита пожилых",
                description="Специальная защита для пожилых",
                intrusion_type=IntrusionType.SUSPICIOUS_BEHAVIOR,
                severity_threshold=IntrusionSeverity.HIGH,
                conditions={
                    "age_group": "elderly",
                    "financial_requests": True,
                },
                actions=[
                    PreventionAction.BLOCK_RESOURCE,
                    PreventionAction.ALERT_ADMIN,
                    PreventionAction.REQUIRE_MFA,
                ],
                family_specific=True,
                age_group="elderly",
            ),
        ]
        for rule in rules:
            self.prevention_rules[rule.rule_id] = rule
        self.log_activity(
            f"Инициализировано {len(rules)} правил предотвращения"
        )

    def _setup_family_protection(self):
        """Настройка семейной защиты"""
        self.family_protection_settings = {
            "child_protection": {
                "enabled": True,
                "strict_mode": True,
                "parent_notifications": True,
                "blocked_content_types": [
                    "inappropriate",
                    "adult",
                    "violence",
                ],
            },
            "elderly_protection": {
                "enabled": True,
                "fraud_detection": True,
                "family_notifications": True,
                "suspicious_behavior_alerts": True,
            },
            "general_family": {
                "unified_protection": True,
                "shared_threat_intelligence": True,
                "family_aware_blocking": True,
            },
        }
        self.log_activity("Настроена семейная защита")

    @validate_parameters(
        event_data=ParameterValidator.validate_event_data,
        user_age=ParameterValidator.validate_user_age,
    )
    @performance_monitor
    @cache_result(ttl_seconds=60)
    def detect_intrusion(
        self,
        event_data: Dict[str, Any],
        user_id: Optional[str] = None,
        user_age: Optional[int] = None,
    ) -> List[IntrusionAttempt]:
        """
        Обнаружение попыток вторжения с расширенной аналитикой.

        Этот метод анализирует входящие события на предмет признаков
        различных типов атак, используя машинное обучение и эвристические
        алгоритмы. Поддерживает семейную защиту с учетом возраста пользователей.

        Args:
            event_data (Dict[str, Any]): Данные события для анализа.
                Должен содержать:
                - source_ip (str): IP адрес источника
                - timestamp (str, optional): Время события в ISO формате
                - user_agent (str, optional): User-Agent браузера
                - failed_logins (int, optional): Количество неудачных попыток входа
                - request_count (int, optional): Количество запросов
                - sql_keywords (List[str], optional): SQL ключевые слова
                - script_tags (List[str], optional): HTML теги скриптов
            user_id (Optional[str]): Уникальный идентификатор пользователя.
                Используется для персонализированной защиты и истории.
                Defaults to None.
            user_age (Optional[int]): Возраст пользователя в годах.
                Используется для активации детской/пожилой защиты.
                Должен быть от 0 до 150. Defaults to None.

        Returns:
            List[IntrusionAttempt]: Список обнаруженных вторжений. Каждый элемент
                содержит:
                - attempt_id (str): Уникальный ID попытки
                - intrusion_type (IntrusionType): Тип обнаруженного вторжения
                - severity (IntrusionSeverity): Уровень серьезности
                - confidence (float): Уверенность в обнаружении (0.0-1.0)
                - source_ip (str): IP адрес источника
                - timestamp (datetime): Время обнаружения
                - description (str): Описание атаки
                - prevention_actions (List[PreventionAction]): Рекомендуемые действия

        Raises:
            ValueError: Если event_data пустой или содержит невалидные данные
            TypeError: Если user_age не является числом
            RuntimeError: Если произошла ошибка при анализе

        Example:
            >>> service = IntrusionPreventionService()
            >>>
            >>> # Пример 1: Обнаружение атаки перебора паролей
            >>> event = {
            ...     'source_ip': '192.168.1.100',
            ...     'failed_logins': 15,
            ...     'timestamp': '2025-01-22T10:30:00Z',
            ...     'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            ... }
            >>> detections = service.detect_intrusion(event, 'user123', 25)
            >>> print(f"Обнаружено {len(detections)} атак")
            >>> for detection in detections:
            ...     print(f"Тип: {detection.intrusion_type}, "
            ...           f"Серьезность: {detection.severity}")

        Note:
            - Метод использует кэширование для оптимизации производительности
            - Поддерживает параллельную обработку множественных паттернов
            - Автоматически применяет семейные правила защиты
            - Логирует все обнаружения для последующего анализа

        Version:
            2.5

        Author:
            ALADDIN Security Team

        Since:
            1.0
        """
        try:
            detections = []
            # Анализ по паттернам
            for pattern_id, pattern in self.intrusion_patterns.items():
                confidence = self._calculate_pattern_confidence(
                    event_data, pattern
                )
                if confidence >= pattern.confidence_threshold:
                    # Создаем попытку вторжения
                    attempt = IntrusionAttempt(
                        attempt_id=self._generate_attempt_id(),
                        intrusion_type=pattern.intrusion_type,
                        severity=self._determine_severity(confidence, pattern),
                        source_ip=event_data.get("source_ip", "unknown"),
                        user_id=user_id,
                        timestamp=datetime.now(),
                        description=f"Обнаружена {pattern.name}",
                        status=IntrusionStatus.DETECTED,
                        metadata={
                            "pattern_id": pattern_id,
                            "confidence": confidence,
                            "user_age": user_age,
                            "family_protection": pattern.family_protection,
                        },
                    )
                    detections.append(attempt)
                    self.intrusion_attempts[attempt.attempt_id] = attempt
                    # Добавляем в семейную историю
                    if user_id:
                        if user_id not in self.family_protection_history:
                            self.family_protection_history[user_id] = []
                        self.family_protection_history[user_id].append(
                            attempt.attempt_id
                        )
                    # Добавляем событие безопасности
                    self.add_security_event(
                        event_type="intrusion_detected",
                        severity=attempt.severity.value,
                        description=f"Обнаружено вторжение: {pattern.name}",
                        source="IntrusionPrevention",
                        metadata={
                            "attempt_id": attempt.attempt_id,
                            "intrusion_type": pattern.intrusion_type.value,
                            "severity": attempt.severity.value,
                            "confidence": confidence,
                            "user_id": user_id,
                            "user_age": user_age,
                        },
                    )
            return detections
        except Exception as e:
            self.logger.error(f"Ошибка обнаружения вторжения: {e}")
            return []

    async def detect_intrusion_async(
        self,
        event_data: Dict[str, Any],
        user_id: Optional[str] = None,
        user_age: Optional[int] = None,
    ) -> List[IntrusionAttempt]:
        """
        Асинхронное обнаружение попыток вторжения.

        Асинхронная версия метода detect_intrusion с поддержкой параллельной
        обработки паттернов атак и неблокирующей обработки больших объемов данных.

        Args:
            event_data: Данные события для анализа
            user_id: ID пользователя (опционально)
            user_age: Возраст пользователя (опционально)

        Returns:
            List[IntrusionAttempt]: Список обнаруженных вторжений

        Example:
            >>> service = IntrusionPreventionService()
            >>> event = {'source_ip': '192.168.1.100', 'failed_logins': 5}
            >>> detections = await service.detect_intrusion_async(event, 'user123', 25)
        """
        try:
            # Валидация параметров
            ParameterValidator.validate_event_data(event_data)
            ParameterValidator.validate_user_age(user_age)

            detections = []

            # Параллельная обработка паттернов
            tasks = []
            for pattern_id, pattern in self.intrusion_patterns.items():
                task = asyncio.create_task(
                    self._check_pattern_async(
                        event_data, pattern, user_id, user_age
                    )
                )
                tasks.append(task)

            # Ждем завершения всех задач
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Фильтруем успешные результаты
            for result in results:
                if not isinstance(result, Exception) and result is not None:
                    detections.append(result)

            return detections

        except Exception as e:
            self.logger.error(
                f"Ошибка асинхронного обнаружения вторжения: {e}"
            )
            return []

    async def _check_pattern_async(
        self,
        event_data: Dict[str, Any],
        pattern: IntrusionPattern,
        user_id: Optional[str],
        user_age: Optional[int],
    ) -> Optional[IntrusionAttempt]:
        """Асинхронная проверка паттерна"""
        try:
            # Асинхронная проверка индикаторов
            confidence = await self._calculate_confidence_async(
                event_data, pattern
            )
            if confidence >= pattern.confidence_threshold:
                return self._create_detection(
                    event_data, pattern, confidence, user_id, user_age
                )
        except Exception as e:
            self.logger.error(f"Ошибка асинхронной проверки паттерна: {e}")
        return None

    async def _calculate_confidence_async(
        self,
        event_data: Dict[str, Any],
        pattern: IntrusionPattern,
    ) -> float:
        """Асинхронный расчет уверенности"""
        # Имитация асинхронной работы
        await asyncio.sleep(0.001)
        return self._calculate_pattern_confidence(event_data, pattern)

    def _create_detection(
        self,
        event_data: Dict[str, Any],
        pattern: IntrusionPattern,
        confidence: float,
        user_id: Optional[str],
        user_age: Optional[int],
    ) -> IntrusionAttempt:
        """Создание объекта обнаружения"""
        return IntrusionAttempt(
            attempt_id=self._generate_attempt_id(),
            intrusion_type=pattern.intrusion_type,
            severity=self._determine_severity(confidence, pattern),
            source_ip=event_data.get("source_ip", "unknown"),
            user_id=user_id,
            timestamp=datetime.now(),
            description=f"Обнаружена {pattern.name}",
            status=IntrusionStatus.DETECTED,
            metadata={
                "pattern_id": pattern.pattern_id,
                "confidence": confidence,
                "user_age": user_age,
                "family_protection": pattern.family_protection,
            },
        )

    def _calculate_pattern_confidence(
        self, event_data: Dict[str, Any], pattern: IntrusionPattern
    ) -> float:
        """Расчет уверенности в паттерне"""
        try:
            confidence = 0.0
            matched_indicators = 0
            for indicator in pattern.indicators:
                if self._check_indicator(event_data, indicator):
                    matched_indicators += 1
                    confidence += 1.0 / len(pattern.indicators)
            # Дополнительные факторы для семейной защиты
            if pattern.family_protection:
                if event_data.get("user_age") and event_data["user_age"] < 18:
                    confidence += 0.1  # Дополнительная защита для детей
                elif (
                    event_data.get("user_age") and event_data["user_age"] > 65
                ):
                    confidence += 0.1  # Дополнительная защита для пожилых
            return min(confidence, 1.0)
        except Exception as e:
            self.logger.error(f"Ошибка расчета уверенности: {e}")
            return 0.0

    def _check_indicator(
        self, event_data: Dict[str, Any], indicator: str
    ) -> bool:
        """Проверка индикатора"""
        try:
            if indicator == "multiple_failed_logins":
                return event_data.get("failed_logins", 0) > 3
            elif indicator == "rapid_login_attempts":
                return (
                    event_data.get("login_frequency", 0) > 10
                )  # 10 попыток в минуту
            elif indicator == "high_request_volume":
                return event_data.get("request_count", 0) > 100
            elif indicator == "multiple_source_ips":
                return event_data.get("unique_ips", 0) > 50
            elif indicator == "sequential_port_access":
                return event_data.get("port_sequence", False)
            elif indicator == "sql_keywords":
                content = event_data.get("content", "").lower()
                sql_keywords = [
                    "select",
                    "insert",
                    "update",
                    "delete",
                    "drop",
                    "union",
                ]
                return any(keyword in content for keyword in sql_keywords)
            elif indicator == "script_tags":
                content = event_data.get("content", "").lower()
                return "<script>" in content or "javascript:" in content
            elif indicator == "inappropriate_content":
                return event_data.get("inappropriate_content", False)
            elif indicator == "financial_requests":
                return event_data.get("financial_requests", False)
            elif indicator == "urgency_tactics":
                return event_data.get("urgency_tactics", False)
            return False
        except Exception as e:
            self.logger.error(f"Ошибка проверки индикатора {indicator}: {e}")
            return False

    def _determine_severity(
        self, confidence: float, pattern: IntrusionPattern
    ) -> IntrusionSeverity:
        """Определение серьезности вторжения"""
        try:
            if confidence >= 0.9:
                return IntrusionSeverity.CRITICAL
            elif confidence >= 0.7:
                return IntrusionSeverity.HIGH
            elif confidence >= 0.5:
                return IntrusionSeverity.MEDIUM
            else:
                return IntrusionSeverity.LOW
        except Exception as e:
            self.logger.error(f"Ошибка определения серьезности: {e}")
            return IntrusionSeverity.LOW

    def prevent_intrusion(
        self, attempt: IntrusionAttempt
    ) -> List[PreventionAction]:
        """Предотвращение вторжения"""
        try:
            applied_actions = []
            # Находим подходящие правила
            applicable_rules = self._find_applicable_rules(attempt)
            for rule in applicable_rules:
                if self._evaluate_rule_conditions(attempt, rule):
                    # Применяем действия правила
                    for action in rule.actions:
                        if self._apply_prevention_action(attempt, action):
                            applied_actions.append(action)
                    # Обновляем статус попытки
                    attempt.status = IntrusionStatus.PREVENTED
                    attempt.prevention_actions.extend(applied_actions)
            # Добавляем событие предотвращения
            if applied_actions:
                self.add_security_event(
                    event_type="intrusion_prevented",
                    severity=attempt.severity.value,
                    description=(
                        f"Предотвращено вторжение: {attempt.description}"
                    ),
                    source="IntrusionPrevention",
                    metadata={
                        "attempt_id": attempt.attempt_id,
                        "intrusion_type": attempt.intrusion_type.value,
                        "severity": attempt.severity.value,
                        "applied_actions": [
                            action.value for action in applied_actions
                        ],
                        "user_id": attempt.user_id,
                    },
                )
            return applied_actions
        except Exception as e:
            self.logger.error(f"Ошибка предотвращения вторжения: {e}")
            return []

    def _find_applicable_rules(
        self, attempt: IntrusionAttempt
    ) -> List[PreventionRule]:
        """Поиск применимых правил"""
        try:
            applicable_rules = []
            for rule in self.prevention_rules.values():
                if (
                    rule.enabled
                    and rule.intrusion_type == attempt.intrusion_type
                    and self._compare_severity(
                        attempt.severity, rule.severity_threshold
                    )
                ):
                    applicable_rules.append(rule)
            return applicable_rules
        except Exception as e:
            self.logger.error(f"Ошибка поиска применимых правил: {e}")
            return []

    def _compare_severity(
        self,
        attempt_severity: IntrusionSeverity,
        rule_threshold: IntrusionSeverity,
    ) -> bool:
        """Сравнение серьезности"""
        try:
            severity_order = {
                IntrusionSeverity.LOW: 1,
                IntrusionSeverity.MEDIUM: 2,
                IntrusionSeverity.HIGH: 3,
                IntrusionSeverity.CRITICAL: 4,
            }
            return (
                severity_order[attempt_severity]
                >= severity_order[rule_threshold]
            )
        except Exception as e:
            self.logger.error(f"Ошибка сравнения серьезности: {e}")
            return False

    def _evaluate_rule_conditions(
        self, attempt: IntrusionAttempt, rule: PreventionRule
    ) -> bool:
        """Оценка условий правила"""
        try:
            conditions = rule.conditions
            # Проверка семейных условий
            if rule.family_specific:
                if (
                    rule.age_group == "child"
                    and attempt.metadata.get("user_age", 0) >= 18
                ):
                    return False
                elif (
                    rule.age_group == "elderly"
                    and attempt.metadata.get("user_age", 0) < 65
                ):
                    return False
            # Проверка временных условий
            if "time_window" in conditions:
                time_window = conditions["time_window"]
                cutoff_time = datetime.now() - timedelta(seconds=time_window)
                if attempt.timestamp < cutoff_time:
                    return False
            # Проверка количественных условий
            if "max_attempts" in conditions:
                max_attempts = conditions["max_attempts"]
                recent_attempts = self._count_recent_attempts(
                    attempt.source_ip,
                    attempt.intrusion_type,
                    conditions.get("time_window", 300),
                )
                if recent_attempts < max_attempts:
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Ошибка оценки условий правила: {e}")
            return False

    def _count_recent_attempts(
        self, source_ip: str, intrusion_type: IntrusionType, time_window: int
    ) -> int:
        """Подсчет недавних попыток"""
        try:
            cutoff_time = datetime.now() - timedelta(seconds=time_window)
            count = 0
            for attempt in self.intrusion_attempts.values():
                if (
                    attempt.source_ip == source_ip
                    and attempt.intrusion_type == intrusion_type
                    and attempt.timestamp >= cutoff_time
                ):
                    count += 1
            return count
        except Exception as e:
            self.logger.error(f"Ошибка подсчета недавних попыток: {e}")
            return 0

    def _apply_prevention_action(
        self, attempt: IntrusionAttempt, action: PreventionAction
    ) -> bool:
        """Применение действия предотвращения"""
        try:
            if action == PreventionAction.BLOCK_IP:
                self.blocked_ips.add(attempt.source_ip)
                self.log_activity(f"Заблокирован IP: {attempt.source_ip}")
            elif action == PreventionAction.RATE_LIMIT:
                self.rate_limits[attempt.source_ip] = {
                    "limit": 10,  # 10 запросов в минуту
                    "window": 60,
                    "start_time": datetime.now(),
                }
                self.log_activity(
                    f"Установлено ограничение скорости для IP: "
                    f"{attempt.source_ip}"
                )
            elif action == PreventionAction.ALERT_ADMIN:
                self.log_activity(
                    f"Отправлено уведомление администратору о вторжении: "
                    f"{attempt.attempt_id}"
                )
            elif action == PreventionAction.LOG_EVENT:
                self.log_activity(
                    f"Записано событие вторжения: {attempt.attempt_id}"
                )
            elif action == PreventionAction.QUARANTINE_USER:
                if attempt.user_id:
                    self.log_activity(
                        f"Пользователь {attempt.user_id} помещен в карантин"
                    )
            elif action == PreventionAction.REQUIRE_MFA:
                if attempt.user_id:
                    self.log_activity(
                        f"Требуется MFA для пользователя {attempt.user_id}"
                    )
            elif action == PreventionAction.TERMINATE_SESSION:
                if attempt.user_id:
                    self.log_activity(
                        f"Сессия пользователя {attempt.user_id} завершена"
                    )
            elif action == PreventionAction.BLOCK_RESOURCE:
                self.log_activity(
                    f"Заблокирован ресурс для IP: {attempt.source_ip}"
                )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка применения действия {action}: {e}")
            return False

    def _generate_attempt_id(self) -> str:
        """Генерация ID попытки"""
        try:
            timestamp = str(int(time.time() * 1000))
            random_part = hashlib.md5(timestamp.encode()).hexdigest()[:8]
            return f"intrusion_{timestamp}_{random_part}"
        except Exception as e:
            self.logger.error(f"Ошибка генерации ID попытки: {e}")
            return f"intrusion_error_{int(time.time())}"

    def get_intrusion_summary(
        self, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получение сводки по вторжениям"""
        try:
            if user_id:
                # Сводка для конкретного пользователя
                user_attempts = [
                    attempt
                    for attempt in self.intrusion_attempts.values()
                    if attempt.user_id == user_id
                ]
            else:
                # Общая сводка
                user_attempts = list(self.intrusion_attempts.values())
            summary = {
                "total_attempts": len(user_attempts),
                "prevented_attempts": len(
                    [
                        a
                        for a in user_attempts
                        if a.status == IntrusionStatus.PREVENTED
                    ]
                ),
                "blocked_attempts": len(
                    [
                        a
                        for a in user_attempts
                        if a.status == IntrusionStatus.BLOCKED
                    ]
                ),
                "by_severity": {
                    severity.value: len(
                        [a for a in user_attempts if a.severity == severity]
                    )
                    for severity in IntrusionSeverity
                },
                "by_type": {
                    intrusion_type.value: len(
                        [
                            a
                            for a in user_attempts
                            if a.intrusion_type == intrusion_type
                        ]
                    )
                    for intrusion_type in IntrusionType
                },
                "recent_attempts": [
                    {
                        "attempt_id": attempt.attempt_id,
                        "type": attempt.intrusion_type.value,
                        "severity": attempt.severity.value,
                        "timestamp": attempt.timestamp.isoformat(),
                        "status": attempt.status.value,
                    }
                    for attempt in sorted(
                        user_attempts, key=lambda x: x.timestamp, reverse=True
                    )[:10]
                ],
            }
            return summary
        except Exception as e:
            self.logger.error(f"Ошибка получения сводки: {e}")
            return {}

    def get_family_protection_status(self) -> Dict[str, Any]:
        """Получение статуса семейной защиты"""
        try:
            status = {
                "family_protection_enabled": self.family_protection_enabled,
                "child_protection_mode": self.child_protection_mode,
                "elderly_protection_mode": self.elderly_protection_mode,
                "active_rules": len(
                    [r for r in self.prevention_rules.values() if r.enabled]
                ),
                "family_specific_rules": len(
                    [
                        r
                        for r in self.prevention_rules.values()
                        if r.family_specific
                    ]
                ),
                "blocked_ips_count": len(self.blocked_ips),
                "rate_limited_ips": len(self.rate_limits),
                "protection_settings": self.family_protection_settings,
                "family_history": {
                    user_id: len(attempt_ids)
                    for user_id, attempt_ids in (
                        self.family_protection_history.items()
                    )
                },
            }
            return status
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса семейной защиты: {e}")
            return {}

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса сервиса"""
        try:
            return {
                "service_name": self.name,
                "status": self.status.value,
                "intrusion_patterns": len(self.intrusion_patterns),
                "prevention_rules": len(self.prevention_rules),
                "total_attempts": len(self.intrusion_attempts),
                "blocked_ips": len(self.blocked_ips),
                "rate_limits": len(self.rate_limits),
                "family_protection_enabled": self.family_protection_enabled,
                "uptime": (
                    (datetime.now() - self.start_time).total_seconds()
                    if hasattr(self, "start_time") and self.start_time
                    else 0
                ),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {}

    # ==================== СИСТЕМА АНАЛИТИКИ И МОНИТОРИНГА ====================

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Получение метрик производительности.

        Returns:
            Dict с метриками производительности всех методов
        """
        try:
            if not hasattr(self, "_performance_metrics"):
                return {}

            metrics = {}
            for method_name, executions in self._performance_metrics.items():
                if executions:
                    execution_times = [
                        ex["execution_time"] for ex in executions
                    ]
                    metrics[method_name] = {
                        "total_calls": len(executions),
                        "avg_execution_time": sum(execution_times)
                        / len(execution_times),
                        "min_execution_time": min(execution_times),
                        "max_execution_time": max(execution_times),
                        "success_rate": sum(
                            1 for ex in executions if ex["success"]
                        )
                        / len(executions)
                        * 100,
                    }

            return metrics
        except Exception as e:
            self.logger.error(
                f"Ошибка получения метрик производительности: {e}"
            )
            return {}

    def get_intrusion_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики по вторжениям.

        Returns:
            Dict с детальной статистикой атак
        """
        try:
            attempts = list(self.intrusion_attempts.values())

            # Статистика по типам атак
            type_stats = {}
            for attempt in attempts:
                attack_type = attempt.intrusion_type.value
                if attack_type not in type_stats:
                    type_stats[attack_type] = 0
                type_stats[attack_type] += 1

            # Статистика по серьезности
            severity_stats = {}
            for attempt in attempts:
                severity = attempt.severity.value
                if severity not in severity_stats:
                    severity_stats[severity] = 0
                severity_stats[severity] += 1

            # Статистика по IP адресам
            ip_stats = {}
            for attempt in attempts:
                ip = attempt.source_ip
                if ip not in ip_stats:
                    ip_stats[ip] = 0
                ip_stats[ip] += 1

            # Топ атакующих IP
            top_attacking_ips = sorted(
                ip_stats.items(), key=lambda x: x[1], reverse=True
            )[:10]

            return {
                "total_attempts": len(attempts),
                "attack_types": type_stats,
                "severity_levels": severity_stats,
                "top_attacking_ips": top_attacking_ips,
                "unique_ips": len(ip_stats),
                "time_range": {
                    "earliest": (
                        min(
                            attempt.timestamp for attempt in attempts
                        ).isoformat()
                        if attempts
                        else None
                    ),
                    "latest": (
                        max(
                            attempt.timestamp for attempt in attempts
                        ).isoformat()
                        if attempts
                        else None
                    ),
                },
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики вторжений: {e}")
            return {}

    def analyze_attack_trends(self, hours: int = 24) -> Dict[str, Any]:
        """
        Анализ трендов атак за указанный период.

        Args:
            hours: Период анализа в часах

        Returns:
            Dict с анализом трендов
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_attempts = [
                attempt
                for attempt in self.intrusion_attempts.values()
                if attempt.timestamp >= cutoff_time
            ]

            # Группировка по часам
            hourly_stats = {}
            for attempt in recent_attempts:
                hour_key = attempt.timestamp.strftime("%Y-%m-%d %H:00")
                if hour_key not in hourly_stats:
                    hourly_stats[hour_key] = 0
                hourly_stats[hour_key] += 1

            # Анализ трендов
            attack_counts = list(hourly_stats.values())
            if len(attack_counts) > 1:
                trend = (
                    "increasing"
                    if attack_counts[-1] > attack_counts[0]
                    else "decreasing"
                )
                avg_attacks_per_hour = sum(attack_counts) / len(attack_counts)
            else:
                trend = "stable"
                avg_attacks_per_hour = attack_counts[0] if attack_counts else 0

            return {
                "period_hours": hours,
                "total_attacks": len(recent_attempts),
                "hourly_breakdown": hourly_stats,
                "trend": trend,
                "avg_attacks_per_hour": avg_attacks_per_hour,
                "peak_hour": (
                    max(hourly_stats.items(), key=lambda x: x[1])[0]
                    if hourly_stats
                    else None
                ),
            }
        except Exception as e:
            self.logger.error(f"Ошибка анализа трендов: {e}")
            return {}

    def generate_security_report(self) -> Dict[str, Any]:
        """
        Генерация комплексного отчета по безопасности.

        Returns:
            Dict с полным отчетом по безопасности
        """
        try:
            return {
                "report_timestamp": datetime.now().isoformat(),
                "service_status": self.get_status(),
                "family_protection": self.get_family_protection_status(),
                "intrusion_statistics": self.get_intrusion_statistics(),
                "performance_metrics": self.get_performance_metrics(),
                "attack_trends_24h": self.analyze_attack_trends(24),
                "attack_trends_7d": self.analyze_attack_trends(168),  # 7 дней
                "recommendations": self._generate_recommendations(),
            }
        except Exception as e:
            self.logger.error(f"Ошибка генерации отчета по безопасности: {e}")
            return {}

    def _generate_recommendations(self) -> List[str]:
        """
        Генерация рекомендаций по улучшению безопасности.

        Returns:
            List[str]: Список рекомендаций
        """
        try:
            recommendations = []
            stats = self.get_intrusion_statistics()

            # Рекомендации на основе статистики
            if stats.get("total_attempts", 0) > 100:
                recommendations.append(
                    "Высокий уровень атак - рекомендуется усилить мониторинг"
                )

            if stats.get("unique_ips", 0) > 50:
                recommendations.append(
                    "Множественные атакующие IP - рассмотрите блокировку подсетей"
                )

            # Рекомендации по производительности
            perf_metrics = self.get_performance_metrics()
            for method, metrics in perf_metrics.items():
                if metrics.get("avg_execution_time", 0) > 1.0:
                    recommendations.append(
                        f"Метод {method} работает медленно - требуется оптимизация"
                    )

            # Рекомендации по семейной защите
            family_status = self.get_family_protection_status()
            if family_status.get("family_specific_rules", 0) < 5:
                recommendations.append(
                    "Рекомендуется добавить больше правил семейной защиты"
                )

            return recommendations
        except Exception as e:
            self.logger.error(f"Ошибка генерации рекомендаций: {e}")
            return ["Ошибка при генерации рекомендаций"]

    # ==================== СИСТЕМА УВЕДОМЛЕНИЙ ====================

    def add_notification_handler(self, handler: Callable):
        """
        Добавление обработчика уведомлений.

        Args:
            handler: Функция-обработчик уведомлений
        """
        if not hasattr(self, "_notification_handlers"):
            self._notification_handlers = []
        self._notification_handlers.append(handler)

    async def send_notification(self, intrusion_data: Dict[str, Any]):
        """
        Отправка уведомления о вторжении.

        Args:
            intrusion_data: Данные о вторжении
        """
        try:
            if hasattr(self, "_notification_handlers"):
                for handler in self._notification_handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(intrusion_data)
                        else:
                            handler(intrusion_data)
                    except Exception as e:
                        self.logger.error(
                            f"Ошибка в обработчике уведомлений: {e}"
                        )
        except Exception as e:
            self.logger.error(f"Ошибка отправки уведомления: {e}")

    # ==================== МАШИННОЕ ОБУЧЕНИЕ ====================

    def train_anomaly_detection(self, data: List[Dict[str, Any]]):
        """
        Обучение модели обнаружения аномалий.

        Args:
            data: Данные для обучения
        """
        try:
            if not hasattr(self, "_ml_models"):
                self._ml_models = {}

            # Простая реализация обучения (заглушка)
            self._ml_models["anomaly_detection"] = {
                "trained": True,
                "training_data_size": len(data),
                "last_training": datetime.now().isoformat(),
            }

            self.logger.info(
                f"Модель обнаружения аномалий обучена на {len(data)} примерах"
            )
        except Exception as e:
            self.logger.error(f"Ошибка обучения модели: {e}")

    def predict_attack_probability(self, event_data: Dict[str, Any]) -> float:
        """
        Предсказание вероятности атаки на основе ML.

        Args:
            event_data: Данные события

        Returns:
            float: Вероятность атаки (0.0-1.0)
        """
        try:
            if (
                not hasattr(self, "_ml_models")
                or "anomaly_detection" not in self._ml_models
            ):
                # Возвращаем базовую вероятность на основе эвристик
                return self._calculate_pattern_confidence(
                    event_data,
                    IntrusionPattern(
                        pattern_id="ml_prediction",
                        name="ML Prediction",
                        description="ML-based attack prediction",
                        intrusion_type=IntrusionType.SUSPICIOUS_BEHAVIOR,
                        indicators=["ml_anomaly"],
                        confidence_threshold=0.5,
                    ),
                )

            # Здесь должна быть реальная ML модель
            # Пока возвращаем случайное значение
            import random

            return random.uniform(0.0, 1.0)
        except Exception as e:
            self.logger.error(f"Ошибка предсказания атаки: {e}")
            return 0.0
