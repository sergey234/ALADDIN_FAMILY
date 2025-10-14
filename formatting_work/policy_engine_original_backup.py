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
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field

from core.base import SecurityBase
from core.security_base import SecurityEvent, IncidentSeverity, ThreatType


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
    parameters: Dict[str, Any] = field(default_factory=dict)  # Параметры действия
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
    target_users: List[str] = field(default_factory=list)  # Целевые пользователи
    target_devices: List[str] = field(default_factory=list)  # Целевые устройства
    target_applications: List[str] = field(default_factory=list)  # Целевые приложения
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
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
        # Данные системы
        self.policies: Dict[str, SecurityPolicy] = {}
        self.policy_evaluations: List[PolicyEvaluation] = []
        self.policy_cache: Dict[str, List[SecurityPolicy]] = {}  # Кэш политик по типам
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
            "cache_misses": 0
        }
        
        self._initialize_default_policies()
    
    def _initialize_default_policies(self) -> None:
        """Инициализация политик по умолчанию"""
        try:
            default_policies: List[Dict[str, Any]] = [
                {
                    "policy_id": "child_content_filter",
                    "name": "Фильтрация контента для детей",
                    "description": "Блокировка нежелательного контента для детей",
                    "policy_type": PolicyType.CONTENT_FILTERING,
                    "priority": PolicyPriority.HIGH,
                    "conditions": [
                        PolicyCondition("user_age", ConditionOperator.LESS_THAN, 18, "Возраст пользователя"),
                        PolicyCondition("content_category", ConditionOperator.IN, ["adult", "violence", "gambling"], "Категория контента")
                    ],
                    "actions": [
                        PolicyAction(ActionType.BLOCK, {"reason": "Нежелательный контент для детей"}, "Блокировка доступа"),
                        PolicyAction(ActionType.NOTIFY, {"recipients": ["parents"]}, "Уведомление родителей")
                    ],
                    "target_users": ["children"]
                },
                {
                    "policy_id": "elderly_scam_protection",
                    "name": "Защита пожилых от мошенничества",
                    "description": "Блокировка подозрительных сайтов и уведомления о мошенничестве",
                    "policy_type": PolicyType.USER_BEHAVIOR,
                    "priority": PolicyPriority.CRITICAL,
                    "conditions": [
                        PolicyCondition("user_age", ConditionOperator.GREATER_THAN, 65, "Возраст пользователя"),
                        PolicyCondition("website_category", ConditionOperator.IN, ["scam", "phishing", "suspicious"], "Категория сайта")
                    ],
                    "actions": [
                        PolicyAction(ActionType.BLOCK, {"reason": "Подозрительный сайт"}, "Блокировка сайта"),
                        PolicyAction(ActionType.NOTIFY, {"recipients": ["family"], "urgency": "high"}, "Срочное уведомление семьи")
                    ],
                    "target_users": ["elderly"]
                },
                {
                    "policy_id": "time_restrictions",
                    "name": "Временные ограничения",
                    "description": "Ограничение времени использования устройств",
                    "policy_type": PolicyType.TIME_RESTRICTIONS,
                    "priority": PolicyPriority.MEDIUM,
                    "conditions": [
                        PolicyCondition("current_time", ConditionOperator.TIME_RANGE, {"start": "22:00", "end": "07:00"}, "Ночное время"),
                        PolicyCondition("user_role", ConditionOperator.IN, ["child", "teenager"], "Роль пользователя")
                    ],
                    "actions": [
                        PolicyAction(ActionType.BLOCK, {"reason": "Время ограничено"}, "Блокировка в ночное время"),
                        PolicyAction(ActionType.NOTIFY, {"recipients": ["parents"]}, "Уведомление родителей")
                    ],
                    "target_users": ["children", "teenagers"]
                },
                {
                    "policy_id": "device_security",
                    "name": "Безопасность устройств",
                    "description": "Проверка безопасности устройств при подключении",
                    "policy_type": PolicyType.DEVICE_MANAGEMENT,
                    "priority": PolicyPriority.HIGH,
                    "conditions": [
                        PolicyCondition("device_trust_score", ConditionOperator.LESS_THAN, 0.7, "Уровень доверия устройства"),
                        PolicyCondition("device_encryption", ConditionOperator.EQUALS, False, "Шифрование устройства")
                    ],
                    "actions": [
                        PolicyAction(ActionType.QUARANTINE, {"reason": "Небезопасное устройство"}, "Карантин устройства"),
                        PolicyAction(ActionType.NOTIFY, {"recipients": ["admin"]}, "Уведомление администратора")
                    ],
                    "target_devices": ["all"]
                },
                {
                    "policy_id": "data_protection",
                    "name": "Защита персональных данных",
                    "description": "Контроль доступа к персональным данным",
                    "policy_type": PolicyType.DATA_PROTECTION,
                    "priority": PolicyPriority.CRITICAL,
                    "conditions": [
                        PolicyCondition("data_type", ConditionOperator.IN, ["personal", "financial", "medical"], "Тип данных"),
                        PolicyCondition("access_location", ConditionOperator.NOT_IN, ["home", "office"], "Местоположение доступа")
                    ],
                    "actions": [
                        PolicyAction(ActionType.DENY, {"reason": "Небезопасное местоположение"}, "Запрет доступа"),
                        PolicyAction(ActionType.LOG, {"level": "security"}, "Логирование попытки доступа"),
                        PolicyAction(ActionType.ESCALATE, {"level": "high"}, "Эскалация инцидента")
                    ],
                    "target_applications": ["all"]
                }
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
                    target_applications=policy_data.get("target_applications", [])
                )
                self.policies[policy.policy_id] = policy
            
            # Обновляем кэш
            self._update_policy_cache()
            
            self.logger.info(f"Инициализировано {len(self.policies)} политик по умолчанию")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации политик по умолчанию: {e}")
    
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
                    description=cond_data.get("description", "")
                )
                conditions.append(condition)
            
            # Создаем действия
            actions = []
            for action_data in policy_data.get("actions", []):
                action = PolicyAction(
                    action_type=ActionType(action_data["action_type"]),
                    parameters=action_data.get("parameters", {}),
                    description=action_data.get("description", "")
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
                metadata=policy_data.get("metadata", {})
            )
            
            self.policies[policy_id] = policy
            self._update_policy_cache()
            
            # Создаем событие безопасности
            security_event = SecurityEvent(
                event_type="policy_created",
                severity=IncidentSeverity.LOW,
                description=f"Создана политика: {policy.name}",
                source="PolicyEngine"
            )
            self.activity_log.append(security_event)
            
            self.logger.info(f"Создана политика {policy_id}: {policy.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка создания политики: {e}")
            return False
    
    def evaluate_policy(self, policy_id: str, user_id: str, request_context: Dict[str, Any]) -> PolicyEvaluation:
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
                    error_message="Политика не найдена"
                )
            
            policy = self.policies[policy_id]
            
            # Проверяем статус политики
            if policy.status != PolicyStatus.ACTIVE:
                return PolicyEvaluation(
                    policy_id=policy_id,
                    user_id=user_id,
                    request_context=request_context,
                    matched=False,
                    error_message=f"Политика неактивна: {policy.status.value}"
                )
            
            # Проверяем целевых пользователей
            if policy.target_users and user_id not in policy.target_users:
                return PolicyEvaluation(
                    policy_id=policy_id,
                    user_id=user_id,
                    request_context=request_context,
                    matched=False,
                    error_message="Пользователь не входит в целевую группу"
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
                evaluation_time=evaluation_time
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
                error_message=str(e)
            )
    
    def evaluate_policies(self, user_id: str, request_context: Dict[str, Any], 
                         policy_types: Optional[List[PolicyType]] = None) -> List[PolicyEvaluation]:
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
            policies_to_evaluate = self._get_policies_for_evaluation(policy_types)
            
            # Ограничиваем количество оценок
            if len(policies_to_evaluate) > self.max_evaluations_per_request:
                policies_to_evaluate = policies_to_evaluate[:self.max_evaluations_per_request]
                self.logger.warning(f"Ограничено количество политик для оценки: {self.max_evaluations_per_request}")
            
            # Оцениваем каждую политику
            for policy in policies_to_evaluate:
                evaluation = self.evaluate_policy(policy.policy_id, user_id, request_context)
                evaluations.append(evaluation)
                
                # Если политика сработала и имеет высокий приоритет, можем остановиться
                if evaluation.matched and policy.priority in [PolicyPriority.CRITICAL, PolicyPriority.HIGH]:
                    break
            
            return evaluations
            
        except Exception as e:
            self.logger.error(f"Ошибка оценки политик: {e}")
            return []
    
    def _evaluate_condition(self, condition: PolicyCondition, context: Dict[str, Any]) -> bool:
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
    
    def _evaluate_time_range(self, current_time: Any, time_range: Dict[str, str]) -> bool:
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
    
    def _execute_action(self, action: PolicyAction, user_id: str, context: Dict[str, Any]) -> bool:
        """Выполнение действия политики"""
        try:
            if action.action_type == ActionType.ALLOW:
                self.logger.info(f"Разрешен доступ для пользователя {user_id}")
                return True
            elif action.action_type == ActionType.DENY:
                self.logger.warning(f"Запрещен доступ для пользователя {user_id}: {action.parameters.get('reason', '')}")
                return True
            elif action.action_type == ActionType.BLOCK:
                self.logger.warning(f"Заблокирован доступ для пользователя {user_id}: {action.parameters.get('reason', '')}")
                return True
            elif action.action_type == ActionType.QUARANTINE:
                self.logger.warning(f"Карантин для пользователя {user_id}: {action.parameters.get('reason', '')}")
                return True
            elif action.action_type == ActionType.LOG:
                self.logger.info(f"Логирование для пользователя {user_id}: {action.parameters.get('level', 'info')}")
                return True
            elif action.action_type == ActionType.NOTIFY:
                recipients = action.parameters.get("recipients", [])
                self.logger.info(f"Уведомление {recipients} о действии пользователя {user_id}")
                return True
            elif action.action_type == ActionType.ESCALATE:
                level = action.parameters.get("level", "medium")
                self.logger.warning(f"Эскалация инцидента уровня {level} для пользователя {user_id}")
                return True
            elif action.action_type == ActionType.REDIRECT:
                target = action.parameters.get("target", "")
                self.logger.info(f"Перенаправление пользователя {user_id} на {target}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка выполнения действия: {e}")
            return False
    
    def _get_policies_for_evaluation(self, policy_types: Optional[List[PolicyType]] = None) -> List[SecurityPolicy]:
        """Получение политик для оценки"""
        try:
            if policy_types is None:
                # Возвращаем все активные политики, отсортированные по приоритету
                active_policies = [p for p in self.policies.values() if p.status == PolicyStatus.ACTIVE]
                return sorted(active_policies, key=lambda x: self._get_priority_order(x.priority))
            else:
                # Возвращаем политики указанных типов
                policies = []
                for policy_type in policy_types:
                    if policy_type.value in self.policy_cache:
                        policies.extend(self.policy_cache[policy_type.value])
                return sorted(policies, key=lambda x: self._get_priority_order(x.priority))
                
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
            PolicyPriority.INFO: 4
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
            policy_evaluations = [e for e in self.policy_evaluations if e.policy_id == policy_id]
            total_evaluations = len(policy_evaluations)
            successful_evaluations = len([e for e in policy_evaluations if e.matched])
            
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
                    "success_rate": successful_evaluations / total_evaluations if total_evaluations > 0 else 0.0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения сводки по политике: {e}")
            return {"error": str(e)}
    
    def get_policies_by_type(self, policy_type: PolicyType) -> List[Dict[str, Any]]:
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
                    policies.append({
                        "policy_id": policy.policy_id,
                        "name": policy.name,
                        "status": policy.status.value,
                        "priority": policy.priority.value,
                        "conditions_count": len(policy.conditions),
                        "actions_count": len(policy.actions)
                    })
            
            return sorted(policies, key=lambda x: self._get_priority_order(PolicyPriority(x["priority"])))
            
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
                "active_policies": len([p for p in self.policies.values() if p.status == PolicyStatus.ACTIVE]),
                "policies_by_type": {
                    policy_type.value: len([p for p in self.policies.values() if p.policy_type == policy_type])
                    for policy_type in PolicyType
                },
                "policies_by_priority": {
                    priority.value: len([p for p in self.policies.values() if p.priority == priority])
                    for priority in PolicyPriority
                },
                "policies_by_status": {
                    status.value: len([p for p in self.policies.values() if p.status == status])
                    for status in PolicyStatus
                },
                "evaluation_stats": self.evaluation_stats,
                "cache_stats": {
                    "cache_enabled": self.enable_caching,
                    "cache_ttl": self.cache_ttl,
                    "cached_types": len(self.policy_cache)
                },
                "engine_settings": {
                    "evaluation_timeout": self.evaluation_timeout,
                    "max_evaluations_per_request": self.max_evaluations_per_request
                }
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}