# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Policy Engine
Движок политик безопасности для семей
Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-02
"""
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import SecurityBase
from core.security_base import IncidentSeverity, SecurityEvent


class PolicyType(Enum):
    """Типы политик"""

    ACCESS_CONTROL = "access_control"  # Контроль доступа
    DATA_PROTECTION = "data_protection"  # Защита данных
    NETWORK_SECURITY = "network_security"  # Сетевая безопасность
    DEVICE_MANAGEMENT = "device_management"  # Управление устройствами
    USER_BEHAVIOR = "user_behavior"  # Поведение пользователей
    CONTENT_FILTERING = "content_filtering"  # Фильтрация контента
    TIME_RESTRICTIONS = "time_restrictions"  # Временные ограничения
    LOCATION_BASED = "location_based"  # На основе местоположения
    EMERGENCY = "emergency"  # Экстренные политики
    COMPLIANCE = "compliance"  # Соответствие требованиям


class PolicyStatus(Enum):
    """Статусы политик"""

    ACTIVE = "active"  # Активная
    INACTIVE = "inactive"  # Неактивная
    DRAFT = "draft"  # Черновик
    TESTING = "testing"  # Тестирование
    DEPRECATED = "deprecated"  # Устаревшая
    ERROR = "error"  # Ошибка


class PolicyPriority(Enum):
    """Приоритеты политик"""

    CRITICAL = "critical"  # Критический
    HIGH = "high"  # Высокий
    MEDIUM = "medium"  # Средний
    LOW = "low"  # Низкий
    INFO = "info"  # Информационный


class ActionType(Enum):
    """Типы действий"""

    ALLOW = "allow"  # Разрешить
    DENY = "deny"  # Запретить
    QUARANTINE = "quarantine"  # Карантин
    LOG = "log"  # Логировать
    NOTIFY = "notify"  # Уведомить
    ESCALATE = "escalate"  # Эскалировать
    BLOCK = "block"  # Заблокировать
    REDIRECT = "redirect"  # Перенаправить


class ConditionOperator(Enum):
    """Операторы условий"""

    EQUALS = "equals"  # Равно
    NOT_EQUALS = "not_equals"  # Не равно
    CONTAINS = "contains"  # Содержит
    NOT_CONTAINS = "not_contains"  # Не содержит
    GREATER_THAN = "greater_than"  # Больше
    LESS_THAN = "less_than"  # Меньше
    IN = "in"  # В списке
    NOT_IN = "not_in"  # Не в списке
    REGEX = "regex"  # Регулярное выражение
    TIME_RANGE = "time_range"  # Временной диапазон


@dataclass
class PolicyCondition:
    """Условие политики"""

    field: str  # Поле для проверки
    operator: ConditionOperator  # Оператор
    value: Any  # Значение для сравнения
    description: str = ""  # Описание условия


@dataclass
class PolicyAction:
    """Действие политики"""

    action_type: ActionType  # Тип действия
    parameters: Dict[str, Any] = field(
        default_factory=dict
    )  # Параметры действия
    description: str = ""  # Описание действия


@dataclass
class SecurityPolicy:
    """Политика безопасности"""

    policy_id: str
    name: str
    description: str
    policy_type: PolicyType
    status: PolicyStatus
    priority: PolicyPriority
    conditions: List[PolicyCondition] = field(default_factory=list)
    actions: List[PolicyAction] = field(default_factory=list)
    target_users: List[str] = field(
        default_factory=list
    )  # Целевые пользователи
    target_devices: List[str] = field(
        default_factory=list
    )  # Целевые устройства
    target_applications: List[str] = field(
        default_factory=list
    )  # Целевые приложения
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyEvaluation:
    """Результат оценки политики"""

    policy_id: str
    user_id: str
    request_context: Dict[str, Any]
    matched: bool
    matched_conditions: List[PolicyCondition] = field(default_factory=list)
    executed_actions: List[PolicyAction] = field(default_factory=list)
    evaluation_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None


class PolicyEngine(SecurityBase):
    """
    Движок политик безопасности для семей
    Централизованная система управления и применения политик
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("PolicyEngine", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Данные системы
        self.policies: Dict[str, SecurityPolicy] = {}
        self.policy_evaluations: List[PolicyEvaluation] = []
        self.policy_cache: Dict[str, List[SecurityPolicy]] = (
            {}
        )  # Кэш политик по типам
        self.activity_log: List[SecurityEvent] = []

        # Настройки движка
        self.evaluation_timeout = 5.0  # Таймаут оценки в секундах
        self.max_evaluations_per_request = 100  # Максимум оценок на запрос
        self.cache_ttl = 300  # TTL кэша в секундах
        self.enable_caching = True

        # Статистика
        self.evaluation_stats = {
            "total_evaluations": 0,
            "successful_evaluations": 0,
            "failed_evaluations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

        self._initialize_default_policies()

    def _initialize_default_policies(self) -> None:
        """Инициализация политик по умолчанию"""
        try:
            default_policies: List[Dict[str, Any]] = [
                {
                    "policy_id": "child_content_filter",
                    "name": "Фильтрация контента для детей",
                    "description": (
                        "Блокировка нежелательного контента для детей"
                    ),
                    "policy_type": PolicyType.CONTENT_FILTERING,
                    "priority": PolicyPriority.HIGH,
                    "conditions": [
                        PolicyCondition(
                            "user_age",
                            ConditionOperator.LESS_THAN,
                            18,
                            "Возраст пользователя",
                        ),
                        PolicyCondition(
                            "content_category",
                            ConditionOperator.IN,
                            ["adult", "violence", "gambling"],
                            "Категория контента",
                        ),
                    ],
                    "actions": [
                        PolicyAction(
                            ActionType.BLOCK,
                            {"reason": "Нежелательный контент для детей"},
                            "Блокировка доступа",
                        ),
                        PolicyAction(
                            ActionType.NOTIFY,
                            {"recipients": ["parents"]},
                            "Уведомление родителей",
                        ),
                    ],
                    "target_users": ["children"],
                },
                {
                    "policy_id": "elderly_scam_protection",
                    "name": "Защита пожилых от мошенничества",
                    "description": (
                        "Блокировка подозрительных сайтов и "
                        "уведомления о мошенничестве"
                    ),
                    "policy_type": PolicyType.USER_BEHAVIOR,
                    "priority": PolicyPriority.CRITICAL,
                    "conditions": [
                        PolicyCondition(
                            "user_age",
                            ConditionOperator.GREATER_THAN,
                            65,
                            "Возраст пользователя",
                        ),
                        PolicyCondition(
                            "website_category",
                            ConditionOperator.IN,
                            ["scam", "phishing", "suspicious"],
                            "Категория сайта",
                        ),
                    ],
                    "actions": [
                        PolicyAction(
                            ActionType.BLOCK,
                            {"reason": "Подозрительный сайт"},
                            "Блокировка сайта",
                        ),
                        PolicyAction(
                            ActionType.NOTIFY,
                            {"recipients": ["family"], "urgency": "high"},
                            "Срочное уведомление семьи",
                        ),
                    ],
                    "target_users": ["elderly"],
                },
                {
                    "policy_id": "time_restrictions",
                    "name": "Временные ограничения",
                    "description": (
                        "Ограничение времени использования устройств"
                    ),
                    "policy_type": PolicyType.TIME_RESTRICTIONS,
                    "priority": PolicyPriority.MEDIUM,
                    "conditions": [
                        PolicyCondition(
                            "current_time",
                            ConditionOperator.TIME_RANGE,
                            {"start": "22:00", "end": "07:00"},
                            "Ночное время",
                        ),
                        PolicyCondition(
                            "user_role",
                            ConditionOperator.IN,
                            ["child", "teenager"],
                            "Роль пользователя",
                        ),
                    ],
                    "actions": [
                        PolicyAction(
                            ActionType.BLOCK,
                            {"reason": "Время ограничено"},
                            "Блокировка в ночное время",
                        ),
                        PolicyAction(
                            ActionType.NOTIFY,
                            {"recipients": ["parents"]},
                            "Уведомление родителей",
                        ),
                    ],
                    "target_users": ["children", "teenagers"],
                },
                {
                    "policy_id": "device_security",
                    "name": "Безопасность устройств",
                    "description": (
                        "Проверка безопасности устройств при подключении"
                    ),
                    "policy_type": PolicyType.DEVICE_MANAGEMENT,
                    "priority": PolicyPriority.HIGH,
                    "conditions": [
                        PolicyCondition(
                            "device_trust_score",
                            ConditionOperator.LESS_THAN,
                            0.7,
                            "Уровень доверия устройства",
                        ),
                        PolicyCondition(
                            "device_encryption",
                            ConditionOperator.EQUALS,
                            False,
                            "Шифрование устройства",
                        ),
                    ],
                    "actions": [
                        PolicyAction(
                            ActionType.QUARANTINE,
                            {"reason": "Небезопасное устройство"},
                            "Карантин устройства",
                        ),
                        PolicyAction(
                            ActionType.NOTIFY,
                            {"recipients": ["admin"]},
                            "Уведомление администратора",
                        ),
                    ],
                    "target_devices": ["all"],
                },
                {
                    "policy_id": "data_protection",
                    "name": "Защита персональных данных",
                    "description": "Контроль доступа к персональным данным",
                    "policy_type": PolicyType.DATA_PROTECTION,
                    "priority": PolicyPriority.CRITICAL,
                    "conditions": [
                        PolicyCondition(
                            "data_type",
                            ConditionOperator.IN,
                            ["personal", "financial", "medical"],
                            "Тип данных",
                        ),
                        PolicyCondition(
                            "access_location",
                            ConditionOperator.NOT_IN,
                            ["home", "office"],
                            "Местоположение доступа",
                        ),
                    ],
                    "actions": [
                        PolicyAction(
                            ActionType.DENY,
                            {"reason": "Небезопасное местоположение"},
                            "Запрет доступа",
                        ),
                        PolicyAction(
                            ActionType.LOG,
                            {"level": "security"},
                            "Логирование попытки доступа",
                        ),
                        PolicyAction(
                            ActionType.ESCALATE,
                            {"level": "high"},
                            "Эскалация инцидента",
                        ),
                    ],
                    "target_applications": ["all"],
                },
            ]

            for policy_data in default_policies:
                policy = SecurityPolicy(
                    policy_id=str(policy_data["policy_id"]),
                    name=str(policy_data["name"]),
                    description=str(policy_data["description"]),
                    policy_type=PolicyType(policy_data["policy_type"]),
                    status=PolicyStatus.ACTIVE,
                    priority=PolicyPriority(policy_data["priority"]),
                    conditions=policy_data.get("conditions", []),
                    actions=policy_data.get("actions", []),
                    target_users=policy_data.get("target_users", []),
                    target_devices=policy_data.get("target_devices", []),
                    target_applications=policy_data.get(
                        "target_applications", []
                    ),
                )
                self.policies[policy.policy_id] = policy

            # Обновляем кэш
            self._update_policy_cache()

            self.logger.info(
                f"Инициализировано {len(self.policies)} политик по умолчанию"
            )

        except Exception as e:
            self.logger.error(
                f"Ошибка инициализации политик по умолчанию: {e}"
            )

    def create_policy(self, policy_data: Dict[str, Any]) -> bool:
        """
        Создание новой политики
        Args:
            policy_data: Данные политики
        Returns:
            bool: Успешность создания
        """
        try:
            policy_id = policy_data.get("policy_id")
            if not policy_id:
                policy_id = f"policy_{int(time.time())}"

            if policy_id in self.policies:
                self.logger.warning(f"Политика {policy_id} уже существует")
                return False

            # Создаем условия
            conditions = []
            for cond_data in policy_data.get("conditions", []):
                condition = PolicyCondition(
                    field=cond_data["field"],
                    operator=ConditionOperator(cond_data["operator"]),
                    value=cond_data["value"],
                    description=cond_data.get("description", ""),
                )
                conditions.append(condition)

            # Создаем действия
            actions = []
            for action_data in policy_data.get("actions", []):
                action = PolicyAction(
                    action_type=ActionType(action_data["action_type"]),
                    parameters=action_data.get("parameters", {}),
                    description=action_data.get("description", ""),
                )
                actions.append(action)

            # Создаем политику
            policy = SecurityPolicy(
                policy_id=policy_id,
                name=policy_data["name"],
                description=policy_data["description"],
                policy_type=PolicyType(policy_data["policy_type"]),
                status=PolicyStatus(policy_data.get("status", "active")),
                priority=PolicyPriority(policy_data.get("priority", "medium")),
                conditions=conditions,
                actions=actions,
                target_users=policy_data.get("target_users", []),
                target_devices=policy_data.get("target_devices", []),
                target_applications=policy_data.get("target_applications", []),
                created_by=policy_data.get("created_by", "system"),
                metadata=policy_data.get("metadata", {}),
            )

            self.policies[policy_id] = policy
            self._update_policy_cache()

            # Создаем событие безопасности
            security_event = SecurityEvent(
                event_type="policy_created",
                severity=IncidentSeverity.LOW,
                description=f"Создана политика: {policy.name}",
                source="PolicyEngine",
            )
            self.activity_log.append(security_event)

            self.logger.info(f"Создана политика {policy_id}: {policy.name}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка создания политики: {e}")
            return False

    def evaluate_policy(
        self, policy_id: str, user_id: str, request_context: Dict[str, Any]
    ) -> PolicyEvaluation:
        """
        Оценка политики для пользователя
        Args:
            policy_id: ID политики
            user_id: ID пользователя
            request_context: Контекст запроса
        Returns:
            PolicyEvaluation: Результат оценки
        """
        try:
            start_time = time.time()

            if policy_id not in self.policies:
                return PolicyEvaluation(
                    policy_id=policy_id,
                    user_id=user_id,
                    request_context=request_context,
                    matched=False,
                    error_message="Политика не найдена",
                )

            policy = self.policies[policy_id]

            # Проверяем статус политики
            if policy.status != PolicyStatus.ACTIVE:
                return PolicyEvaluation(
                    policy_id=policy_id,
                    user_id=user_id,
                    request_context=request_context,
                    matched=False,
                    error_message=f"Политика неактивна: {policy.status.value}",
                )

            # Проверяем целевых пользователей
            if policy.target_users and user_id not in policy.target_users:
                return PolicyEvaluation(
                    policy_id=policy_id,
                    user_id=user_id,
                    request_context=request_context,
                    matched=False,
                    error_message="Пользователь не входит в целевую группу",
                )

            # Оцениваем условия
            matched_conditions = []
            for condition in policy.conditions:
                if self._evaluate_condition(condition, request_context):
                    matched_conditions.append(condition)

            # Определяем, сработала ли политика
            matched = len(matched_conditions) == len(policy.conditions)

            # Выполняем действия, если политика сработала
            executed_actions = []
            if matched:
                for action in policy.actions:
                    if self._execute_action(action, user_id, request_context):
                        executed_actions.append(action)

            evaluation_time = time.time() - start_time

            evaluation = PolicyEvaluation(
                policy_id=policy_id,
                user_id=user_id,
                request_context=request_context,
                matched=matched,
                matched_conditions=matched_conditions,
                executed_actions=executed_actions,
                evaluation_time=evaluation_time,
            )

            self.policy_evaluations.append(evaluation)
            self.evaluation_stats["total_evaluations"] += 1

            if matched:
                self.evaluation_stats["successful_evaluations"] += 1
            else:
                self.evaluation_stats["failed_evaluations"] += 1

            return evaluation

        except Exception as e:
            self.logger.error(f"Ошибка оценки политики {policy_id}: {e}")
            return PolicyEvaluation(
                policy_id=policy_id,
                user_id=user_id,
                request_context=request_context,
                matched=False,
                error_message=str(e),
            )

    def evaluate_policies(
        self,
        user_id: str,
        request_context: Dict[str, Any],
        policy_types: Optional[List[PolicyType]] = None,
    ) -> List[PolicyEvaluation]:
        """
        Оценка всех подходящих политик
        Args:
            user_id: ID пользователя
            request_context: Контекст запроса
            policy_types: Типы политик для оценки (опционально)
        Returns:
            List[PolicyEvaluation]: Результаты оценок
        """
        try:
            evaluations = []

            # Получаем политики для оценки
            policies_to_evaluate = self._get_policies_for_evaluation(
                policy_types
            )

            # Ограничиваем количество оценок
            if len(policies_to_evaluate) > self.max_evaluations_per_request:
                policies_to_evaluate = policies_to_evaluate[
                    : self.max_evaluations_per_request
                ]
                self.logger.warning(
                    f"Ограничено количество политик для оценки: {self.max_evaluations_per_request}"
                )

            # Оцениваем каждую политику
            for policy in policies_to_evaluate:
                evaluation = self.evaluate_policy(
                    policy.policy_id, user_id, request_context
                )
                evaluations.append(evaluation)

                # Если политика сработала и имеет высокий приоритет, можем остановиться
                if evaluation.matched and policy.priority in [
                    PolicyPriority.CRITICAL,
                    PolicyPriority.HIGH,
                ]:
                    break

            return evaluations

        except Exception as e:
            self.logger.error(f"Ошибка оценки политик: {e}")
            return []

    def _evaluate_condition(
        self, condition: PolicyCondition, context: Dict[str, Any]
    ) -> bool:
        """Оценка условия политики"""
        try:
            field_value = context.get(condition.field)

            if field_value is None:
                return False

            if condition.operator == ConditionOperator.EQUALS:
                return field_value == condition.value
            elif condition.operator == ConditionOperator.NOT_EQUALS:
                return field_value != condition.value
            elif condition.operator == ConditionOperator.CONTAINS:
                return condition.value in str(field_value)
            elif condition.operator == ConditionOperator.NOT_CONTAINS:
                return condition.value not in str(field_value)
            elif condition.operator == ConditionOperator.GREATER_THAN:
                return float(field_value) > float(condition.value)
            elif condition.operator == ConditionOperator.LESS_THAN:
                return float(field_value) < float(condition.value)
            elif condition.operator == ConditionOperator.IN:
                return field_value in condition.value
            elif condition.operator == ConditionOperator.NOT_IN:
                return field_value not in condition.value
            elif condition.operator == ConditionOperator.TIME_RANGE:
                return self._evaluate_time_range(field_value, condition.value)
            else:
                return False

        except Exception as e:
            self.logger.error(f"Ошибка оценки условия: {e}")
            return False

    def _evaluate_time_range(
        self, current_time: Any, time_range: Dict[str, str]
    ) -> bool:
        """Оценка временного диапазона"""
        try:
            if isinstance(current_time, str):
                current_time = datetime.strptime(current_time, "%H:%M").time()
            elif isinstance(current_time, datetime):
                current_time = current_time.time()

            start_time = datetime.strptime(time_range["start"], "%H:%M").time()
            end_time = datetime.strptime(time_range["end"], "%H:%M").time()

            if start_time <= end_time:
                return start_time <= current_time <= end_time
            else:  # Переход через полночь
                return current_time >= start_time or current_time <= end_time

        except Exception as e:
            self.logger.error(f"Ошибка оценки временного диапазона: {e}")
            return False

    def _execute_action(
        self, action: PolicyAction, user_id: str, context: Dict[str, Any]
    ) -> bool:
        """Выполнение действия политики"""
        try:
            if action.action_type == ActionType.ALLOW:
                self.logger.info(f"Разрешен доступ для пользователя {user_id}")
                return True
            elif action.action_type == ActionType.DENY:
                self.logger.warning(
                    f"Запрещен доступ для пользователя {user_id}: {action.parameters.get('reason', '')}"
                )
                return True
            elif action.action_type == ActionType.BLOCK:
                self.logger.warning(
                    f"Заблокирован доступ для пользователя {user_id}: {action.parameters.get('reason', '')}"
                )
                return True
            elif action.action_type == ActionType.QUARANTINE:
                self.logger.warning(
                    f"Карантин для пользователя {user_id}: {action.parameters.get('reason', '')}"
                )
                return True
            elif action.action_type == ActionType.LOG:
                self.logger.info(
                    f"Логирование для пользователя {user_id}: {action.parameters.get('level', 'info')}"
                )
                return True
            elif action.action_type == ActionType.NOTIFY:
                recipients = action.parameters.get("recipients", [])
                self.logger.info(
                    f"Уведомление {recipients} о действии пользователя {user_id}"
                )
                return True
            elif action.action_type == ActionType.ESCALATE:
                level = action.parameters.get("level", "medium")
                self.logger.warning(
                    f"Эскалация инцидента уровня {level} для пользователя {user_id}"
                )
                return True
            elif action.action_type == ActionType.REDIRECT:
                target = action.parameters.get("target", "")
                self.logger.info(
                    f"Перенаправление пользователя {user_id} на {target}"
                )
                return True
            else:
                return False

        except Exception as e:
            self.logger.error(f"Ошибка выполнения действия: {e}")
            return False

    def _get_policies_for_evaluation(
        self, policy_types: Optional[List[PolicyType]] = None
    ) -> List[SecurityPolicy]:
        """Получение политик для оценки"""
        try:
            if policy_types is None:
                # Возвращаем все активные политики, отсортированные по приоритету
                active_policies = [
                    p
                    for p in self.policies.values()
                    if p.status == PolicyStatus.ACTIVE
                ]
                return sorted(
                    active_policies,
                    key=lambda x: self._get_priority_order(x.priority),
                )
            else:
                # Возвращаем политики указанных типов
                policies = []
                for policy_type in policy_types:
                    if policy_type.value in self.policy_cache:
                        policies.extend(self.policy_cache[policy_type.value])
                return sorted(
                    policies,
                    key=lambda x: self._get_priority_order(x.priority),
                )

        except Exception as e:
            self.logger.error(f"Ошибка получения политик для оценки: {e}")
            return []

    def _get_priority_order(self, priority: PolicyPriority) -> int:
        """Получение числового порядка приоритета"""
        priority_order = {
            PolicyPriority.CRITICAL: 0,
            PolicyPriority.HIGH: 1,
            PolicyPriority.MEDIUM: 2,
            PolicyPriority.LOW: 3,
            PolicyPriority.INFO: 4,
        }
        return priority_order.get(priority, 5)

    def _update_policy_cache(self) -> None:
        """Обновление кэша политик"""
        try:
            self.policy_cache.clear()

            for policy in self.policies.values():
                if policy.status == PolicyStatus.ACTIVE:
                    policy_type = policy.policy_type.value
                    if policy_type not in self.policy_cache:
                        self.policy_cache[policy_type] = []
                    self.policy_cache[policy_type].append(policy)

            self.logger.debug("Кэш политик обновлен")

        except Exception as e:
            self.logger.error(f"Ошибка обновления кэша политик: {e}")

    def get_policy_summary(self, policy_id: str) -> Dict[str, Any]:
        """
        Получение сводки по политике
        Args:
            policy_id: ID политики
        Returns:
            Dict[str, Any]: Сводка по политике
        """
        try:
            if policy_id not in self.policies:
                return {"error": "Политика не найдена"}

            policy = self.policies[policy_id]

            # Получаем статистику оценок
            policy_evaluations = [
                e for e in self.policy_evaluations if e.policy_id == policy_id
            ]
            total_evaluations = len(policy_evaluations)
            successful_evaluations = len(
                [e for e in policy_evaluations if e.matched]
            )

            return {
                "policy_id": policy_id,
                "name": policy.name,
                "description": policy.description,
                "type": policy.policy_type.value,
                "status": policy.status.value,
                "priority": policy.priority.value,
                "conditions_count": len(policy.conditions),
                "actions_count": len(policy.actions),
                "target_users": policy.target_users,
                "target_devices": policy.target_devices,
                "target_applications": policy.target_applications,
                "created_at": policy.created_at.isoformat(),
                "updated_at": policy.updated_at.isoformat(),
                "version": policy.version,
                "evaluation_stats": {
                    "total_evaluations": total_evaluations,
                    "successful_evaluations": successful_evaluations,
                    "success_rate": (
                        successful_evaluations / total_evaluations
                        if total_evaluations > 0
                        else 0.0
                    ),
                },
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения сводки по политике: {e}")
            return {"error": str(e)}

    def get_policies_by_type(
        self, policy_type: PolicyType
    ) -> List[Dict[str, Any]]:
        """
        Получение политик по типу
        Args:
            policy_type: Тип политики
        Returns:
            List[Dict[str, Any]]: Список политик
        """
        try:
            policies = []
            for policy in self.policies.values():
                if policy.policy_type == policy_type:
                    policies.append(
                        {
                            "policy_id": policy.policy_id,
                            "name": policy.name,
                            "status": policy.status.value,
                            "priority": policy.priority.value,
                            "conditions_count": len(policy.conditions),
                            "actions_count": len(policy.actions),
                        }
                    )

            return sorted(
                policies,
                key=lambda x: self._get_priority_order(
                    PolicyPriority(x["priority"])
                ),
            )

        except Exception as e:
            self.logger.error(f"Ошибка получения политик по типу: {e}")
            return []

    def get_status(self) -> Dict[str, Any]:
        """
        Получение статуса Policy Engine
        Returns:
            Dict[str, Any]: Статус сервиса
        """
        try:
            # Получаем базовый статус
            base_status = super().get_status()

            # Добавляем специфичную информацию
            status = {
                **base_status,
                "total_policies": len(self.policies),
                "active_policies": len(
                    [
                        p
                        for p in self.policies.values()
                        if p.status == PolicyStatus.ACTIVE
                    ]
                ),
                "policies_by_type": {
                    policy_type.value: len(
                        [
                            p
                            for p in self.policies.values()
                            if p.policy_type == policy_type
                        ]
                    )
                    for policy_type in PolicyType
                },
                "policies_by_priority": {
                    priority.value: len(
                        [
                            p
                            for p in self.policies.values()
                            if p.priority == priority
                        ]
                    )
                    for priority in PolicyPriority
                },
                "policies_by_status": {
                    status.value: len(
                        [
                            p
                            for p in self.policies.values()
                            if p.status == status
                        ]
                    )
                    for status in PolicyStatus
                },
                "evaluation_stats": self.evaluation_stats,
                "cache_stats": {
                    "cache_enabled": self.enable_caching,
                    "cache_ttl": self.cache_ttl,
                    "cached_types": len(self.policy_cache),
                },
                "engine_settings": {
                    "evaluation_timeout": self.evaluation_timeout,
                    "max_evaluations_per_request": self.max_evaluations_per_request,
                },
            }

            return status

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}

    def update_policy(self, policy_id: str, updates: Dict[str, Any]) -> bool:
        """
        Обновление существующей политики

        Args:
            policy_id: ID политики
            updates: Словарь с обновлениями

        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            if policy_id not in self.policies:
                self.logger.warning(f"Политика {policy_id} не найдена")
                return False

            policy = self.policies[policy_id]

            # Обновляем поля политики
            for key, value in updates.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)

            # Обновляем время изменения
            policy.updated_at = datetime.now()
            policy.version += 1

            # Обновляем кэш
            self._update_policy_cache()

            self.logger.info(f"Политика {policy_id} обновлена")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка обновления политики {policy_id}: {e}")
            return False

    def delete_policy(self, policy_id: str) -> bool:
        """
        Удаление политики

        Args:
            policy_id: ID политики

        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            if policy_id not in self.policies:
                self.logger.warning(f"Политика {policy_id} не найдена")
                return False

            # Удаляем политику
            del self.policies[policy_id]

            # Обновляем кэш
            self._update_policy_cache()

            self.logger.info(f"Политика {policy_id} удалена")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка удаления политики {policy_id}: {e}")
            return False

    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение конкретной политики

        Args:
            policy_id: ID политики

        Returns:
            Dict с данными политики или None если не найдена
        """
        try:
            if policy_id not in self.policies:
                return None

            policy = self.policies[policy_id]

            return {
                "policy_id": policy_id,
                "name": policy.name,
                "description": policy.description,
                "policy_type": policy.policy_type.value,
                "status": policy.status.value,
                "priority": policy.priority.value,
                "conditions": [
                    {
                        "field": c.field,
                        "operator": c.operator.value,
                        "value": c.value,
                    }
                    for c in policy.conditions
                ],
                "actions": [
                    {
                        "action_type": a.action_type.value,
                        "parameters": a.parameters,
                    }
                    for a in policy.actions
                ],
                "target_users": policy.target_users,
                "target_devices": policy.target_devices,
                "target_applications": policy.target_applications,
                "created_at": policy.created_at.isoformat(),
                "updated_at": policy.updated_at.isoformat(),
                "version": policy.version,
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения политики {policy_id}: {e}")
            return None

    def list_policies(self) -> List[Dict[str, Any]]:
        """
        Получение списка всех политик

        Returns:
            List[Dict]: Список всех политик
        """
        try:
            policies_list = []

            for policy_id, policy in self.policies.items():
                policies_list.append(
                    {
                        "policy_id": policy_id,
                        "name": policy.name,
                        "description": policy.description,
                        "policy_type": policy.policy_type.value,
                        "status": policy.status.value,
                        "priority": policy.priority.value,
                        "created_at": policy.created_at.isoformat(),
                        "updated_at": policy.updated_at.isoformat(),
                        "version": policy.version,
                    }
                )

            return policies_list

        except Exception as e:
            self.logger.error(f"Ошибка получения списка политик: {e}")
            return []

    def apply_policy(
        self, policy_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Применение политики к контексту

        Args:
            policy_id: ID политики
            context: Контекст для применения

        Returns:
            Dict с результатом применения
        """
        try:
            if policy_id not in self.policies:
                return {"error": "Политика не найдена"}

            policy = self.policies[policy_id]

            # Оцениваем политику
            evaluation_result = self.evaluate_policy(
                policy_id, context, context
            )

            if (
                hasattr(evaluation_result, "matched")
                and evaluation_result.matched
            ):
                # Выполняем действия
                actions_results = []
                for action in policy.actions:
                    action_result = self._execute_action(action, context)
                    actions_results.append(action_result)

                return {
                    "policy_id": policy_id,
                    "matched": True,
                    "actions_executed": actions_results,
                    "evaluation_time": getattr(
                        evaluation_result, "evaluation_time", 0
                    ),
                }
            else:
                return {
                    "policy_id": policy_id,
                    "matched": False,
                    "reason": getattr(
                        evaluation_result, "reason", "Условия не выполнены"
                    ),
                }

        except Exception as e:
            self.logger.error(f"Ошибка применения политики {policy_id}: {e}")
            return {"error": str(e)}

    def get_policy_status(self, policy_id: str) -> Dict[str, Any]:
        """
        Получение статуса конкретной политики

        Args:
            policy_id: ID политики

        Returns:
            Dict с статусом политики
        """
        try:
            if policy_id not in self.policies:
                return {"error": "Политика не найдена"}

            policy = self.policies[policy_id]

            # Получаем статистику оценок
            policy_evaluations = [
                e for e in self.policy_evaluations if e.policy_id == policy_id
            ]

            return {
                "policy_id": policy_id,
                "name": policy.name,
                "status": policy.status.value,
                "priority": policy.priority.value,
                "is_active": policy.status == PolicyStatus.ACTIVE,
                "total_evaluations": len(policy_evaluations),
                "successful_evaluations": len(
                    [e for e in policy_evaluations if e.matched]
                ),
                "last_evaluation": (
                    max(e.timestamp for e in policy_evaluations).isoformat()
                    if policy_evaluations
                    else None
                ),
                "created_at": policy.created_at.isoformat(),
                "updated_at": policy.updated_at.isoformat(),
                "version": policy.version,
            }

        except Exception as e:
            self.logger.error(
                f"Ошибка получения статуса политики {policy_id}: {e}"
            )
            return {"error": str(e)}

    def get_policy_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики по всем политикам

        Returns:
            Dict с общей статистикой
        """
        try:
            total_policies = len(self.policies)
            active_policies = len(
                [
                    p
                    for p in self.policies.values()
                    if p.status == PolicyStatus.ACTIVE
                ]
            )

            # Статистика по типам
            type_stats = {}
            for policy_type in PolicyType:
                type_stats[policy_type.value] = len(
                    [
                        p
                        for p in self.policies.values()
                        if p.policy_type == policy_type
                    ]
                )

            # Статистика по приоритетам
            priority_stats = {}
            for priority in PolicyPriority:
                priority_stats[priority.value] = len(
                    [
                        p
                        for p in self.policies.values()
                        if p.priority == priority
                    ]
                )

            # Статистика по статусам
            status_stats = {}
            for status in PolicyStatus:
                status_stats[status.value] = len(
                    [p for p in self.policies.values() if p.status == status]
                )

            return {
                "total_policies": total_policies,
                "active_policies": active_policies,
                "inactive_policies": total_policies - active_policies,
                "policies_by_type": type_stats,
                "policies_by_priority": priority_stats,
                "policies_by_status": status_stats,
                "evaluation_stats": self.evaluation_stats,
                "cache_stats": {
                    "cache_enabled": self.enable_caching,
                    "cache_ttl": self.cache_ttl,
                    "cached_types": len(self.policy_cache),
                },
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статистики политик: {e}")
            return {"error": str(e)}

    # ==================== PROPERTY МЕТОДЫ ====================

    @property
    def total_policies(self) -> int:
        """Общее количество политик"""
        return len(self.policies)

    @property
    def active_policies(self) -> int:
        """Количество активных политик"""
        return len(
            [
                p
                for p in self.policies.values()
                if p.status == PolicyStatus.ACTIVE
            ]
        )

    @property
    def is_initialized(self) -> bool:
        """Проверка инициализации движка"""
        return len(self.policies) > 0

    @property
    def cache_hit_rate(self) -> float:
        """Процент попаданий в кэш"""
        total = (
            self.evaluation_stats["cache_hits"]
            + self.evaluation_stats["cache_misses"]
        )
        return (
            (self.evaluation_stats["cache_hits"] / total) if total > 0 else 0.0
        )

    @property
    def evaluation_success_rate(self) -> float:
        """Процент успешных оценок"""
        total = self.evaluation_stats["total_evaluations"]
        return (
            (self.evaluation_stats["successful_evaluations"] / total)
            if total > 0
            else 0.0
        )

    # ==================== STATIC МЕТОДЫ ====================

    @staticmethod
    def validate_policy_id(policy_id: str) -> bool:
        """Валидация ID политики"""
        if not policy_id or not isinstance(policy_id, str):
            return False
        return (
            len(policy_id) >= 3
            and policy_id.replace("_", "").replace("-", "").isalnum()
        )

    @staticmethod
    def validate_priority(priority: PolicyPriority) -> bool:
        """Валидация приоритета политики"""
        return priority in PolicyPriority

    @staticmethod
    def calculate_risk_score(conditions: List[PolicyCondition]) -> float:
        """Расчет уровня риска на основе условий"""
        if not conditions:
            return 0.0

        risk_factors = {
            "user_age": 0.1,
            "device_trust_score": 0.3,
            "access_location": 0.2,
            "time_range": 0.1,
            "content_category": 0.3,
        }

        total_risk = 0.0
        for condition in conditions:
            risk_weight = risk_factors.get(condition.field, 0.1)
            total_risk += risk_weight

        return min(total_risk, 1.0)

    @staticmethod
    def format_policy_info(policy: SecurityPolicy) -> str:
        """Форматирование информации о политике"""
        return f"{policy.name} ({policy.policy_type.value}) - {policy.status.value}"

    # ==================== CLASS МЕТОДЫ ====================

    @classmethod
    def create_default_engine(cls) -> "PolicyEngine":
        """Создание движка с настройками по умолчанию"""
        return cls()

    @classmethod
    def create_high_security_engine(cls) -> "PolicyEngine":
        """Создание движка с высоким уровнем безопасности"""
        engine = cls()
        engine.evaluation_timeout = 2.0  # Более строгий таймаут
        engine.max_evaluations_per_request = 50  # Меньше оценок за раз
        return engine

    @classmethod
    def get_supported_policy_types(cls) -> List[str]:
        """Получение поддерживаемых типов политик"""
        return [policy_type.value for policy_type in PolicyType]

    @classmethod
    def get_supported_priorities(cls) -> List[str]:
        """Получение поддерживаемых приоритетов"""
        return [priority.value for priority in PolicyPriority]

    # ==================== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ====================

    def backup_policies(self, backup_path: str = None) -> Dict[str, Any]:
        """
        Создание резервной копии политик

        Args:
            backup_path: Путь для сохранения резервной копии

        Returns:
            Dict с результатом операции
        """
        try:
            if not backup_path:
                backup_path = f"policy_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "policies": {
                    pid: {
                        "policy_id": policy.policy_id,
                        "name": policy.name,
                        "description": policy.description,
                        "policy_type": policy.policy_type.value,
                        "status": policy.status.value,
                        "priority": policy.priority.value,
                        "conditions": [
                            {
                                "field": c.field,
                                "operator": c.operator.value,
                                "value": c.value,
                            }
                            for c in policy.conditions
                        ],
                        "actions": [
                            {
                                "action_type": a.action_type.value,
                                "parameters": a.parameters,
                            }
                            for a in policy.actions
                        ],
                        "target_users": policy.target_users,
                        "target_devices": policy.target_devices,
                        "target_applications": policy.target_applications,
                        "created_at": policy.created_at.isoformat(),
                        "updated_at": policy.updated_at.isoformat(),
                        "version": policy.version,
                    }
                    for pid, policy in self.policies.items()
                },
            }

            # В реальной реализации здесь было бы сохранение в файл
            # Используем backup_data для логирования
            self.logger.info(
                f"Резервная копия создана: {backup_path}, политик: {len(backup_data['policies'])}"
            )
            return {
                "success": True,
                "backup_path": backup_path,
                "policies_count": len(self.policies),
            }

        except Exception as e:
            self.logger.error(f"Ошибка создания резервной копии: {e}")
            return {"success": False, "error": str(e)}

    def restore_policies(self, backup_data: Dict[str, Any]) -> bool:
        """
        Восстановление политик из резервной копии

        Args:
            backup_data: Данные резервной копии

        Returns:
            bool: True если успешно
        """
        try:
            if "policies" not in backup_data:
                return False

            restored_count = 0
            for policy_id, policy_data in backup_data["policies"].items():
                # Восстанавливаем политику
                self.policies[policy_id] = SecurityPolicy(
                    policy_id=policy_data["policy_id"],
                    name=policy_data["name"],
                    description=policy_data["description"],
                    policy_type=PolicyType(policy_data["policy_type"]),
                    status=PolicyStatus(policy_data["status"]),
                    priority=PolicyPriority(policy_data["priority"]),
                    conditions=[],
                    actions=[],
                    target_users=policy_data.get("target_users", []),
                    target_devices=policy_data.get("target_devices", []),
                    target_applications=policy_data.get(
                        "target_applications", []
                    ),
                    created_at=datetime.fromisoformat(
                        policy_data["created_at"]
                    ),
                    updated_at=datetime.fromisoformat(
                        policy_data["updated_at"]
                    ),
                    version=policy_data["version"],
                )
                restored_count += 1

            self._update_policy_cache()
            self.logger.info(f"Восстановлено политик: {restored_count}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка восстановления политик: {e}")
            return False

    def export_policies(self, policy_ids: List[str] = None) -> Dict[str, Any]:
        """
        Экспорт политик

        Args:
            policy_ids: Список ID политик для экспорта (None = все)

        Returns:
            Dict с экспортированными данными
        """
        try:
            if policy_ids is None:
                policy_ids = list(self.policies.keys())

            exported_policies = {}
            for policy_id in policy_ids:
                if policy_id in self.policies:
                    policy = self.policies[policy_id]
                    exported_policies[policy_id] = {
                        "name": policy.name,
                        "description": policy.description,
                        "policy_type": policy.policy_type.value,
                        "priority": policy.priority.value,
                        "conditions": [
                            {
                                "field": c.field,
                                "operator": c.operator.value,
                                "value": c.value,
                            }
                            for c in policy.conditions
                        ],
                        "actions": [
                            {
                                "action_type": a.action_type.value,
                                "parameters": a.parameters,
                            }
                            for a in policy.actions
                        ],
                        "target_users": policy.target_users,
                        "target_devices": policy.target_devices,
                        "target_applications": policy.target_applications,
                    }

            return {
                "success": True,
                "policies": exported_policies,
                "count": len(exported_policies),
            }

        except Exception as e:
            self.logger.error(f"Ошибка экспорта политик: {e}")
            return {"success": False, "error": str(e)}

    def import_policies(self, policies_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Импорт политик

        Args:
            policies_data: Данные политик для импорта

        Returns:
            Dict с результатом импорта
        """
        try:
            imported_count = 0
            errors = []

            for policy_id, policy_data in policies_data.items():
                try:
                    # Создаем новую политику
                    new_policy = SecurityPolicy(
                        policy_id=policy_id,
                        name=policy_data["name"],
                        description=policy_data["description"],
                        policy_type=PolicyType(policy_data["policy_type"]),
                        status=PolicyStatus.ACTIVE,
                        priority=PolicyPriority(policy_data["priority"]),
                        conditions=[],
                        actions=[],
                        target_users=policy_data.get("target_users", []),
                        target_devices=policy_data.get("target_devices", []),
                        target_applications=policy_data.get(
                            "target_applications", []
                        ),
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        version=1,
                    )

                    self.policies[policy_id] = new_policy
                    imported_count += 1

                except Exception as e:
                    errors.append(f"Ошибка импорта {policy_id}: {e}")

            self._update_policy_cache()
            return {
                "success": True,
                "imported_count": imported_count,
                "errors": errors,
            }

        except Exception as e:
            self.logger.error(f"Ошибка импорта политик: {e}")
            return {"success": False, "error": str(e)}

    def validate_policy(self, policy_id: str) -> Dict[str, Any]:
        """
        Валидация политики

        Args:
            policy_id: ID политики для валидации

        Returns:
            Dict с результатами валидации
        """
        try:
            if policy_id not in self.policies:
                return {"valid": False, "errors": ["Политика не найдена"]}

            policy = self.policies[policy_id]
            errors = []
            warnings = []

            # Проверяем обязательные поля
            if not policy.name:
                errors.append("Название политики не может быть пустым")

            if not policy.description:
                warnings.append("Описание политики отсутствует")

            if not policy.conditions:
                warnings.append("Политика не имеет условий")

            if not policy.actions:
                warnings.append("Политика не имеет действий")

            # Проверяем условия
            for i, condition in enumerate(policy.conditions):
                if not condition.field:
                    errors.append(f"Условие {i+1}: поле не указано")
                if not condition.operator:
                    errors.append(f"Условие {i+1}: оператор не указан")

            # Проверяем действия
            for i, action in enumerate(policy.actions):
                if not action.action_type:
                    errors.append(f"Действие {i+1}: тип действия не указан")

            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "policy_id": policy_id,
            }

        except Exception as e:
            self.logger.error(f"Ошибка валидации политики {policy_id}: {e}")
            return {"valid": False, "errors": [str(e)]}

    def test_policy(
        self, policy_id: str, test_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Тестирование политики

        Args:
            policy_id: ID политики для тестирования
            test_context: Контекст для тестирования

        Returns:
            Dict с результатами тестирования
        """
        try:
            if policy_id not in self.policies:
                return {"success": False, "error": "Политика не найдена"}

            # Оцениваем политику
            evaluation_result = self.evaluate_policy(
                policy_id, "test_user", test_context
            )

            return {
                "success": True,
                "policy_id": policy_id,
                "matched": evaluation_result.matched,
                "evaluation_time": evaluation_result.evaluation_time,
                "reason": evaluation_result.reason,
                "test_context": test_context,
            }

        except Exception as e:
            self.logger.error(f"Ошибка тестирования политики {policy_id}: {e}")
            return {"success": False, "error": str(e)}

    def clone_policy(
        self, policy_id: str, new_policy_id: str, new_name: str = None
    ) -> bool:
        """
        Клонирование политики

        Args:
            policy_id: ID исходной политики
            new_policy_id: ID новой политики
            new_name: Новое название (опционально)

        Returns:
            bool: True если успешно
        """
        try:
            if policy_id not in self.policies:
                return False

            if new_policy_id in self.policies:
                return False  # Политика с таким ID уже существует

            original_policy = self.policies[policy_id]

            # Создаем копию политики
            cloned_policy = SecurityPolicy(
                policy_id=new_policy_id,
                name=new_name or f"{original_policy.name} (копия)",
                description=original_policy.description,
                policy_type=original_policy.policy_type,
                status=PolicyStatus.DRAFT,  # Копия создается как черновик
                priority=original_policy.priority,
                conditions=original_policy.conditions.copy(),
                actions=original_policy.actions.copy(),
                target_users=original_policy.target_users.copy(),
                target_devices=original_policy.target_devices.copy(),
                target_applications=original_policy.target_applications.copy(),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                version=1,
            )

            self.policies[new_policy_id] = cloned_policy
            self._update_policy_cache()

            self.logger.info(
                f"Политика {policy_id} клонирована как {new_policy_id}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка клонирования политики {policy_id}: {e}")
            return False

    def archive_policy(self, policy_id: str) -> bool:
        """
        Архивирование политики

        Args:
            policy_id: ID политики для архивирования

        Returns:
            bool: True если успешно
        """
        try:
            if policy_id not in self.policies:
                return False

            policy = self.policies[policy_id]
            policy.status = PolicyStatus.DEPRECATED
            policy.updated_at = datetime.now()

            self._update_policy_cache()
            self.logger.info(f"Политика {policy_id} заархивирована")
            return True

        except Exception as e:
            self.logger.error(
                f"Ошибка архивирования политики {policy_id}: {e}"
            )
            return False

    def get_policy_history(self, policy_id: str) -> List[Dict[str, Any]]:
        """
        Получение истории изменений политики

        Args:
            policy_id: ID политики

        Returns:
            List с историей изменений
        """
        try:
            if policy_id not in self.policies:
                return []

            # В реальной реализации здесь была бы база данных с историей
            # Пока возвращаем базовую информацию
            policy = self.policies[policy_id]
            history = [
                {
                    "timestamp": policy.created_at.isoformat(),
                    "action": "created",
                    "version": policy.version,
                    "description": "Политика создана",
                },
                {
                    "timestamp": policy.updated_at.isoformat(),
                    "action": "updated",
                    "version": policy.version,
                    "description": "Политика обновлена",
                },
            ]

            return history

        except Exception as e:
            self.logger.error(
                f"Ошибка получения истории политики {policy_id}: {e}"
            )
            return []

    def search_policies(
        self, query: str, search_fields: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Поиск политик

        Args:
            query: Поисковый запрос
            search_fields: Поля для поиска (None = все поля)

        Returns:
            List с найденными политиками
        """
        try:
            if search_fields is None:
                search_fields = ["name", "description", "policy_id"]

            results = []
            query_lower = query.lower()

            for policy_id, policy in self.policies.items():
                match_found = False

                for search_field in search_fields:
                    if (
                        search_field == "name"
                        and query_lower in policy.name.lower()
                    ):
                        match_found = True
                        break
                    elif (
                        search_field == "description"
                        and query_lower in policy.description.lower()
                    ):
                        match_found = True
                        break
                    elif (
                        search_field == "policy_id"
                        and query_lower in policy_id.lower()
                    ):
                        match_found = True
                        break

                if match_found:
                    results.append(
                        {
                            "policy_id": policy_id,
                            "name": policy.name,
                            "description": policy.description,
                            "policy_type": policy.policy_type.value,
                            "status": policy.status.value,
                            "priority": policy.priority.value,
                        }
                    )

            return results

        except Exception as e:
            self.logger.error(f"Ошибка поиска политик: {e}")
            return []

    def bulk_update_policies(
        self, updates: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Массовое обновление политик

        Args:
            updates: Словарь с обновлениями {policy_id: {field: value}}

        Returns:
            Dict с результатами обновления
        """
        try:
            updated_count = 0
            errors = []

            for policy_id, policy_updates in updates.items():
                try:
                    if policy_id in self.policies:
                        success = self.update_policy(policy_id, policy_updates)
                        if success:
                            updated_count += 1
                        else:
                            errors.append(f"Ошибка обновления {policy_id}")
                    else:
                        errors.append(f"Политика {policy_id} не найдена")
                except Exception as e:
                    errors.append(f"Ошибка обновления {policy_id}: {e}")

            return {
                "success": True,
                "updated_count": updated_count,
                "total_requests": len(updates),
                "errors": errors,
            }

        except Exception as e:
            self.logger.error(f"Ошибка массового обновления: {e}")
            return {"success": False, "error": str(e)}

    def get_policy_metrics(self, policy_id: str = None) -> Dict[str, Any]:
        """
        Получение метрик политики

        Args:
            policy_id: ID политики (None = общие метрики)

        Returns:
            Dict с метриками
        """
        try:
            if policy_id:
                # Метрики конкретной политики
                if policy_id not in self.policies:
                    return {"error": "Политика не найдена"}

                policy_evaluations = [
                    e
                    for e in self.policy_evaluations
                    if e.policy_id == policy_id
                ]

                return {
                    "policy_id": policy_id,
                    "total_evaluations": len(policy_evaluations),
                    "successful_evaluations": len(
                        [e for e in policy_evaluations if e.matched]
                    ),
                    "success_rate": (
                        len([e for e in policy_evaluations if e.matched])
                        / len(policy_evaluations)
                        if policy_evaluations
                        else 0
                    ),
                    "average_evaluation_time": (
                        sum(e.evaluation_time for e in policy_evaluations)
                        / len(policy_evaluations)
                        if policy_evaluations
                        else 0
                    ),
                    "last_evaluation": (
                        max(
                            e.timestamp for e in policy_evaluations
                        ).isoformat()
                        if policy_evaluations
                        else None
                    ),
                }
            else:
                # Общие метрики
                return {
                    "total_policies": len(self.policies),
                    "active_policies": len(
                        [
                            p
                            for p in self.policies.values()
                            if p.status == PolicyStatus.ACTIVE
                        ]
                    ),
                    "total_evaluations": self.evaluation_stats[
                        "total_evaluations"
                    ],
                    "successful_evaluations": self.evaluation_stats[
                        "successful_evaluations"
                    ],
                    "cache_hit_rate": self.cache_hit_rate,
                    "evaluation_success_rate": self.evaluation_success_rate,
                }

        except Exception as e:
            self.logger.error(f"Ошибка получения метрик: {e}")
            return {"error": str(e)}

    def optimize_policies(self) -> Dict[str, Any]:
        """
        Оптимизация политик

        Returns:
            Dict с результатами оптимизации
        """
        try:
            optimizations = []

            # Оптимизация кэша
            self._update_policy_cache()
            optimizations.append("Кэш политик обновлен")

            # Очистка старых оценок (оставляем только последние 1000)
            if len(self.policy_evaluations) > 1000:
                self.policy_evaluations = self.policy_evaluations[-1000:]
                optimizations.append("Старые оценки очищены")

            # Проверка неиспользуемых политик
            unused_policies = []
            for policy_id, policy in self.policies.items():
                policy_evaluations = [
                    e
                    for e in self.policy_evaluations
                    if e.policy_id == policy_id
                ]
                if (
                    not policy_evaluations
                    and policy.status == PolicyStatus.ACTIVE
                ):
                    unused_policies.append(policy_id)

            if unused_policies:
                optimizations.append(
                    f"Найдено {len(unused_policies)} неиспользуемых политик"
                )

            return {
                "success": True,
                "optimizations": optimizations,
                "policies_count": len(self.policies),
                "evaluations_count": len(self.policy_evaluations),
            }

        except Exception as e:
            self.logger.error(f"Ошибка оптимизации: {e}")
            return {"success": False, "error": str(e)}

    def cleanup_old_policies(self, days_old: int = 30) -> Dict[str, Any]:
        """
        Очистка старых политик

        Args:
            days_old: Возраст политик для удаления (в днях)

        Returns:
            Dict с результатами очистки
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            removed_count = 0

            policies_to_remove = []
            for policy_id, policy in self.policies.items():
                if (
                    policy.status == PolicyStatus.DEPRECATED
                    and policy.updated_at < cutoff_date
                ):
                    policies_to_remove.append(policy_id)

            for policy_id in policies_to_remove:
                del self.policies[policy_id]
                removed_count += 1

            self._update_policy_cache()

            return {
                "success": True,
                "removed_count": removed_count,
                "cutoff_date": cutoff_date.isoformat(),
                "remaining_policies": len(self.policies),
            }

        except Exception as e:
            self.logger.error(f"Ошибка очистки старых политик: {e}")
            return {"success": False, "error": str(e)}
