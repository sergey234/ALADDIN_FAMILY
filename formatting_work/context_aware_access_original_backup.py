# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Context Aware Access
Контекстно-зависимый доступ для семей
Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-02
"""
import logging
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field

from core.base import SecurityBase
from core.security_base import SecurityEvent, IncidentSeverity, ThreatType


class AccessContext(Enum):
    """Контексты доступа"""
    HOME = "home"  # Домашняя сеть
    WORK = "work"  # Рабочая сеть
    PUBLIC = "public"  # Публичная сеть
    MOBILE = "mobile"  # Мобильная сеть
    UNKNOWN = "unknown"  # Неизвестная сеть


class AccessLevel(Enum):
    """Уровни доступа"""
    DENIED = "denied"  # Доступ запрещен
    RESTRICTED = "restricted"  # Ограниченный доступ
    LIMITED = "limited"  # Ограниченный доступ
    STANDARD = "standard"  # Стандартный доступ
    FULL = "full"  # Полный доступ


class ContextFactor(Enum):
    """Факторы контекста"""
    LOCATION = "location"  # Местоположение
    TIME = "time"  # Время
    DEVICE = "device"  # Устройство
    NETWORK = "network"  # Сеть
    USER_BEHAVIOR = "user_behavior"  # Поведение пользователя
    RISK_LEVEL = "risk_level"  # Уровень риска
    TRUST_SCORE = "trust_score"  # Балл доверия
    AUTHENTICATION = "authentication"  # Аутентификация
    ENVIRONMENT = "environment"  # Окружение
    ACTIVITY = "activity"  # Активность


class AccessDecisionType(Enum):
    """Решения по доступу"""
    ALLOW = "allow"  # Разрешить
    DENY = "deny"  # Запретить
    CHALLENGE = "challenge"  # Запросить дополнительную аутентификацию
    MONITOR = "monitor"  # Мониторить
    ESCALATE = "escalate"  # Эскалировать


@dataclass
class ContextData:
    """Данные контекста"""
    user_id: str
    device_id: str
    location: Optional[str] = None
    network_type: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    risk_score: float = 0.0
    trust_score: float = 0.0
    authentication_level: int = 0
    activity_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessRule:
    """Правило доступа"""
    rule_id: str
    name: str
    description: str
    context_conditions: Dict[ContextFactor, Any] = field(default_factory=dict)
    access_level: AccessLevel = AccessLevel.STANDARD
    priority: int = 100
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class AccessDecision:
    """Решение по доступу"""
    decision_id: str
    user_id: str
    resource: str
    decision: AccessDecisionType
    access_level: AccessLevel
    context_data: ContextData
    applied_rules: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


class ContextAwareAccess(SecurityBase):
    """
    Контекстно-зависимый доступ для семей
    Система принятия решений о доступе на основе контекста
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("ContextAwareAccess", config)
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
        # Данные системы
        self.access_rules: Dict[str, AccessRule] = {}
        self.access_decisions: List[AccessDecision] = []
        self.context_cache: Dict[str, ContextData] = {}
        self.activity_log: List[SecurityEvent] = []
        
        # Настройки системы
        self.default_access_level = AccessLevel.STANDARD
        self.max_cache_age = timedelta(hours=1)
        self.decision_confidence_threshold = 0.7
        
        # Веса факторов контекста
        self.context_weights = {
            ContextFactor.LOCATION: 0.20,
            ContextFactor.TIME: 0.15,
            ContextFactor.DEVICE: 0.18,
            ContextFactor.NETWORK: 0.15,
            ContextFactor.USER_BEHAVIOR: 0.12,
            ContextFactor.RISK_LEVEL: 0.10,
            ContextFactor.TRUST_SCORE: 0.05,
            ContextFactor.AUTHENTICATION: 0.03,
            ContextFactor.ENVIRONMENT: 0.01,
            ContextFactor.ACTIVITY: 0.01
        }
        
        # Настройки доступа по контексту
        self.context_access_levels = {
            AccessContext.HOME: AccessLevel.FULL,
            AccessContext.WORK: AccessLevel.STANDARD,
            AccessContext.PUBLIC: AccessLevel.RESTRICTED,
            AccessContext.MOBILE: AccessLevel.LIMITED,
            AccessContext.UNKNOWN: AccessLevel.DENIED
        }
        
        # Временные ограничения
        self.time_restrictions = {
            "night_hours": (22, 6),  # Ночные часы (22:00 - 06:00)
            "school_hours": (8, 15),  # Школьные часы (08:00 - 15:00)
            "work_hours": (9, 17)  # Рабочие часы (09:00 - 17:00)
        }
        
        self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        """Инициализация правил доступа по умолчанию"""
        try:
            # Правило для домашней сети
            home_rule = AccessRule(
                rule_id="home_network_full_access",
                name="Полный доступ в домашней сети",
                description="Разрешить полный доступ для доверенных устройств в домашней сети",
                context_conditions={
                    ContextFactor.NETWORK: "home",
                    ContextFactor.TRUST_SCORE: 0.7
                },
                access_level=AccessLevel.FULL,
                priority=100
            )
            self.access_rules[home_rule.rule_id] = home_rule
            
            # Правило для публичной сети
            public_rule = AccessRule(
                rule_id="public_network_restricted",
                name="Ограниченный доступ в публичной сети",
                description="Ограничить доступ в публичных сетях",
                context_conditions={
                    ContextFactor.NETWORK: "public"
                },
                access_level=AccessLevel.RESTRICTED,
                priority=90
            )
            self.access_rules[public_rule.rule_id] = public_rule
            
            # Правило для ночных часов
            night_rule = AccessRule(
                rule_id="night_hours_restricted",
                name="Ограничения в ночные часы",
                description="Ограничить доступ в ночные часы для детей",
                context_conditions={
                    ContextFactor.TIME: "night_hours",
                    ContextFactor.ACTIVITY: "child"
                },
                access_level=AccessLevel.RESTRICTED,
                priority=80
            )
            self.access_rules[night_rule.rule_id] = night_rule
            
            # Правило для школьных часов
            school_rule = AccessRule(
                rule_id="school_hours_blocked",
                name="Блокировка в школьные часы",
                description="Заблокировать развлекательный контент в школьные часы",
                context_conditions={
                    ContextFactor.TIME: "school_hours",
                    ContextFactor.ACTIVITY: "entertainment"
                },
                access_level=AccessLevel.DENIED,
                priority=85
            )
            self.access_rules[school_rule.rule_id] = school_rule
            
            # Правило для высокого риска
            high_risk_rule = AccessRule(
                rule_id="high_risk_denied",
                name="Запрет при высоком риске",
                description="Запретить доступ при высоком уровне риска",
                context_conditions={
                    ContextFactor.RISK_LEVEL: 0.8
                },
                access_level=AccessLevel.DENIED,
                priority=95
            )
            self.access_rules[high_risk_rule.rule_id] = high_risk_rule
            
            # Правило для низкого доверия
            low_trust_rule = AccessRule(
                rule_id="low_trust_challenge",
                name="Дополнительная аутентификация при низком доверии",
                description="Запросить дополнительную аутентификацию при низком доверии",
                context_conditions={
                    ContextFactor.TRUST_SCORE: 0.3
                },
                access_level=AccessLevel.RESTRICTED,
                priority=75
            )
            self.access_rules[low_trust_rule.rule_id] = low_trust_rule
            
            self.logger.info(f"Инициализировано {len(self.access_rules)} правил доступа")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации правил доступа: {e}")
    
    def evaluate_access_request(self, user_id: str, resource: str, 
                              context_data: ContextData) -> AccessDecision:
        """
        Оценка запроса на доступ
        Args:
            user_id: ID пользователя
            resource: Ресурс для доступа
            context_data: Данные контекста
        Returns:
            AccessDecision: Решение по доступу
        """
        try:
            decision_id = f"access_decision_{user_id}_{int(time.time())}"
            
            # Анализируем контекст
            context_score = self._analyze_context(context_data)
            
            # Применяем правила доступа
            applicable_rules = self._find_applicable_rules(context_data)
            
            # Принимаем решение
            decision, access_level, confidence = self._make_access_decision(
                context_data, applicable_rules, context_score
            )
            
            # Создаем решение
            access_decision = AccessDecision(
                decision_id=decision_id,
                user_id=user_id,
                resource=resource,
                decision=decision,
                access_level=access_level,
                context_data=context_data,
                applied_rules=[rule.rule_id for rule in applicable_rules],
                confidence_score=confidence,
                reasoning=self._generate_reasoning(applicable_rules, context_score),
                expires_at=datetime.now() + timedelta(hours=1)
            )
            
            # Сохраняем решение
            self.access_decisions.append(access_decision)
            
            # Кэшируем контекст
            self.context_cache[f"{user_id}_{resource}"] = context_data
            
            # Создаем событие безопасности
            security_event = SecurityEvent(
                event_type="access_decision",
                severity=IncidentSeverity.LOW if decision == AccessDecisionType.ALLOW else IncidentSeverity.MEDIUM,
                description=f"Принято решение о доступе: {decision.value} для {user_id}",
                source="ContextAwareAccess"
            )
            self.activity_log.append(security_event)
            
            self.logger.info(f"Принято решение о доступе: {decision.value} для {user_id} (уверенность: {confidence:.2f})")
            return access_decision
            
        except Exception as e:
            self.logger.error(f"Ошибка оценки запроса на доступ: {e}")
            # Возвращаем безопасное решение по умолчанию
            return AccessDecision(
                decision_id=f"error_decision_{int(time.time())}",
                user_id=user_id,
                resource=resource,
                decision=AccessDecisionType.DENY,
                access_level=AccessLevel.DENIED,
                context_data=context_data,
                confidence_score=0.0,
                reasoning="Ошибка при принятии решения"
            )
    
    def _analyze_context(self, context_data: ContextData) -> float:
        """Анализ контекста и расчет балла"""
        try:
            context_score = 0.0
            total_weight = 0.0
            
            # Анализируем местоположение
            if context_data.location:
                location_score = self._evaluate_location(context_data.location)
                context_score += location_score * self.context_weights[ContextFactor.LOCATION]
                total_weight += self.context_weights[ContextFactor.LOCATION]
            
            # Анализируем время
            time_score = self._evaluate_time(context_data.timestamp)
            context_score += time_score * self.context_weights[ContextFactor.TIME]
            total_weight += self.context_weights[ContextFactor.TIME]
            
            # Анализируем устройство
            device_score = self._evaluate_device(context_data.device_id)
            context_score += device_score * self.context_weights[ContextFactor.DEVICE]
            total_weight += self.context_weights[ContextFactor.DEVICE]
            
            # Анализируем сеть
            if context_data.network_type:
                network_score = self._evaluate_network(context_data.network_type)
                context_score += network_score * self.context_weights[ContextFactor.NETWORK]
                total_weight += self.context_weights[ContextFactor.NETWORK]
            
            # Анализируем поведение пользователя
            behavior_score = self._evaluate_user_behavior(context_data.user_id)
            context_score += behavior_score * self.context_weights[ContextFactor.USER_BEHAVIOR]
            total_weight += self.context_weights[ContextFactor.USER_BEHAVIOR]
            
            # Анализируем уровень риска
            risk_score = 1.0 - context_data.risk_score  # Инвертируем риск
            context_score += risk_score * self.context_weights[ContextFactor.RISK_LEVEL]
            total_weight += self.context_weights[ContextFactor.RISK_LEVEL]
            
            # Анализируем балл доверия
            trust_score = context_data.trust_score
            context_score += trust_score * self.context_weights[ContextFactor.TRUST_SCORE]
            total_weight += self.context_weights[ContextFactor.TRUST_SCORE]
            
            # Анализируем аутентификацию
            auth_score = min(1.0, context_data.authentication_level / 3.0)
            context_score += auth_score * self.context_weights[ContextFactor.AUTHENTICATION]
            total_weight += self.context_weights[ContextFactor.AUTHENTICATION]
            
            # Нормализуем балл
            if total_weight > 0:
                context_score = context_score / total_weight
            
            return max(0.0, min(1.0, context_score))
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа контекста: {e}")
            return 0.5  # Средний балл по умолчанию
    
    def _evaluate_location(self, location: str) -> float:
        """Оценка местоположения"""
        try:
            # Простая логика оценки местоположения
            if "home" in location.lower():
                return 1.0
            elif "work" in location.lower():
                return 0.8
            elif "public" in location.lower():
                return 0.3
            else:
                return 0.5
                
        except Exception as e:
            self.logger.error(f"Ошибка оценки местоположения: {e}")
            return 0.5
    
    def _evaluate_time(self, timestamp: datetime) -> float:
        """Оценка времени"""
        try:
            hour = timestamp.hour
            
            # Ночные часы (22:00 - 06:00)
            if 22 <= hour or hour <= 6:
                return 0.3
            
            # Рабочие часы (09:00 - 17:00)
            elif 9 <= hour <= 17:
                return 0.7
            
            # Вечерние часы (18:00 - 21:00)
            elif 18 <= hour <= 21:
                return 0.9
            
            # Утренние часы (07:00 - 08:00)
            else:
                return 0.6
                
        except Exception as e:
            self.logger.error(f"Ошибка оценки времени: {e}")
            return 0.5
    
    def _evaluate_device(self, device_id: str) -> float:
        """Оценка устройства"""
        try:
            # Простая логика оценки устройства
            if "trusted" in device_id.lower():
                return 1.0
            elif "mobile" in device_id.lower():
                return 0.7
            elif "unknown" in device_id.lower():
                return 0.2
            else:
                return 0.5
                
        except Exception as e:
            self.logger.error(f"Ошибка оценки устройства: {e}")
            return 0.5
    
    def _evaluate_network(self, network_type: str) -> float:
        """Оценка сети"""
        try:
            # Простая логика оценки сети
            if network_type == "home":
                return 1.0
            elif network_type == "work":
                return 0.8
            elif network_type == "mobile":
                return 0.6
            elif network_type == "public":
                return 0.2
            else:
                return 0.3
                
        except Exception as e:
            self.logger.error(f"Ошибка оценки сети: {e}")
            return 0.5
    
    def _evaluate_user_behavior(self, user_id: str) -> float:
        """Оценка поведения пользователя"""
        try:
            # Простая логика оценки поведения
            # В реальной системе здесь был бы анализ истории поведения
            if "admin" in user_id.lower():
                return 1.0
            elif "parent" in user_id.lower():
                return 0.9
            elif "child" in user_id.lower():
                return 0.6
            elif "elderly" in user_id.lower():
                return 0.7
            else:
                return 0.5
                
        except Exception as e:
            self.logger.error(f"Ошибка оценки поведения пользователя: {e}")
            return 0.5
    
    def _find_applicable_rules(self, context_data: ContextData) -> List[AccessRule]:
        """Поиск применимых правил"""
        try:
            applicable_rules = []
            
            for rule in self.access_rules.values():
                if not rule.enabled:
                    continue
                
                if self._rule_matches_context(rule, context_data):
                    applicable_rules.append(rule)
            
            # Сортируем по приоритету (высокий приоритет = низкий номер)
            applicable_rules.sort(key=lambda r: r.priority)
            
            return applicable_rules
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска применимых правил: {e}")
            return []
    
    def _rule_matches_context(self, rule: AccessRule, context_data: ContextData) -> bool:
        """Проверка соответствия правила контексту"""
        try:
            for factor, condition in rule.context_conditions.items():
                if factor == ContextFactor.NETWORK:
                    if context_data.network_type != condition:
                        return False
                
                elif factor == ContextFactor.TIME:
                    if not self._check_time_condition(condition, context_data.timestamp):
                        return False
                
                elif factor == ContextFactor.TRUST_SCORE:
                    if context_data.trust_score < condition:
                        return False
                
                elif factor == ContextFactor.RISK_LEVEL:
                    if context_data.risk_score < condition:
                        return False
                
                elif factor == ContextFactor.ACTIVITY:
                    if context_data.activity_type != condition:
                        return False
                
                # Добавить другие факторы по необходимости
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки соответствия правила: {e}")
            return False
    
    def _check_time_condition(self, condition: str, timestamp: datetime) -> bool:
        """Проверка временного условия"""
        try:
            if condition == "night_hours":
                hour = timestamp.hour
                return 22 <= hour or hour <= 6
            
            elif condition == "school_hours":
                hour = timestamp.hour
                return 8 <= hour <= 15
            
            elif condition == "work_hours":
                hour = timestamp.hour
                return 9 <= hour <= 17
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки временного условия: {e}")
            return False
    
    def _make_access_decision(self, context_data: ContextData, 
                            applicable_rules: List[AccessRule], 
                            context_score: float) -> Tuple[AccessDecisionType, AccessLevel, float]:
        """Принятие решения о доступе"""
        try:
            if not applicable_rules:
                # Нет применимых правил - используем контекстный балл
                if context_score >= 0.7:
                    return AccessDecisionType.ALLOW, AccessLevel.STANDARD, context_score
                elif context_score >= 0.4:
                    return AccessDecisionType.CHALLENGE, AccessLevel.RESTRICTED, context_score
                else:
                    return AccessDecisionType.DENY, AccessLevel.DENIED, context_score
            
            # Применяем правила в порядке приоритета
            for rule in applicable_rules:
                if rule.access_level == AccessLevel.DENIED:
                    return AccessDecisionType.DENY, AccessLevel.DENIED, 0.9
                elif rule.access_level == AccessLevel.RESTRICTED:
                    return AccessDecisionType.CHALLENGE, AccessLevel.RESTRICTED, 0.8
                elif rule.access_level == AccessLevel.LIMITED:
                    return AccessDecisionType.MONITOR, AccessLevel.LIMITED, 0.7
                elif rule.access_level == AccessLevel.STANDARD:
                    return AccessDecisionType.ALLOW, AccessLevel.STANDARD, 0.8
                elif rule.access_level == AccessLevel.FULL:
                    return AccessDecisionType.ALLOW, AccessLevel.FULL, 0.9
            
            # Если дошли до сюда, используем контекстный балл
            if context_score >= 0.7:
                return AccessDecisionType.ALLOW, AccessLevel.STANDARD, context_score
            else:
                return AccessDecisionType.CHALLENGE, AccessLevel.RESTRICTED, context_score
                
        except Exception as e:
            self.logger.error(f"Ошибка принятия решения о доступе: {e}")
            return AccessDecisionType.DENY, AccessLevel.DENIED, 0.0
    
    def _generate_reasoning(self, applicable_rules: List[AccessRule], 
                          context_score: float) -> str:
        """Генерация обоснования решения"""
        try:
            if not applicable_rules:
                return f"Решение на основе контекстного балла: {context_score:.2f}"
            
            rule_names = [rule.name for rule in applicable_rules]
            return f"Применены правила: {', '.join(rule_names)}. Контекстный балл: {context_score:.2f}"
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации обоснования: {e}")
            return "Ошибка при генерации обоснования"
    
    def create_access_rule(self, rule_id: str, name: str, description: str,
                          context_conditions: Dict[ContextFactor, Any],
                          access_level: AccessLevel, priority: int = 100) -> bool:
        """
        Создание правила доступа
        Args:
            rule_id: ID правила
            name: Название правила
            description: Описание правила
            context_conditions: Условия контекста
            access_level: Уровень доступа
            priority: Приоритет правила
        Returns:
            bool: Успешность создания
        """
        try:
            if rule_id in self.access_rules:
                self.logger.warning(f"Правило {rule_id} уже существует")
                return False
            
            rule = AccessRule(
                rule_id=rule_id,
                name=name,
                description=description,
                context_conditions=context_conditions,
                access_level=access_level,
                priority=priority
            )
            
            self.access_rules[rule_id] = rule
            
            # Создаем событие безопасности
            security_event = SecurityEvent(
                event_type="access_rule_created",
                severity=IncidentSeverity.LOW,
                description=f"Создано правило доступа: {name}",
                source="ContextAwareAccess"
            )
            self.activity_log.append(security_event)
            
            self.logger.info(f"Создано правило доступа: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка создания правила доступа: {e}")
            return False
    
    def update_access_rule(self, rule_id: str, **kwargs) -> bool:
        """
        Обновление правила доступа
        Args:
            rule_id: ID правила
            **kwargs: Поля для обновления
        Returns:
            bool: Успешность обновления
        """
        try:
            if rule_id not in self.access_rules:
                self.logger.warning(f"Правило {rule_id} не найдено")
                return False
            
            rule = self.access_rules[rule_id]
            
            # Обновляем поля
            for key, value in kwargs.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            rule.updated_at = datetime.now()
            
            self.logger.info(f"Обновлено правило доступа: {rule_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления правила доступа: {e}")
            return False
    
    def delete_access_rule(self, rule_id: str) -> bool:
        """
        Удаление правила доступа
        Args:
            rule_id: ID правила
        Returns:
            bool: Успешность удаления
        """
        try:
            if rule_id not in self.access_rules:
                self.logger.warning(f"Правило {rule_id} не найдено")
                return False
            
            rule_name = self.access_rules[rule_id].name
            del self.access_rules[rule_id]
            
            # Создаем событие безопасности
            security_event = SecurityEvent(
                event_type="access_rule_deleted",
                severity=IncidentSeverity.LOW,
                description=f"Удалено правило доступа: {rule_name}",
                source="ContextAwareAccess"
            )
            self.activity_log.append(security_event)
            
            self.logger.info(f"Удалено правило доступа: {rule_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка удаления правила доступа: {e}")
            return False
    
    def get_access_summary(self, user_id: str, hours: int = 24) -> Dict[str, Any]:
        """
        Получение сводки доступа пользователя
        Args:
            user_id: ID пользователя
            hours: Количество часов для анализа
        Returns:
            Dict[str, Any]: Сводка доступа
        """
        try:
            start_time = datetime.now() - timedelta(hours=hours)
            
            # Получаем решения за период
            user_decisions = [
                d for d in self.access_decisions 
                if d.user_id == user_id and d.timestamp >= start_time
            ]
            
            if not user_decisions:
                return {
                    "user_id": user_id,
                    "period_hours": hours,
                    "total_requests": 0,
                    "message": "Нет данных за указанный период"
                }
            
            # Анализируем решения
            decision_counts: Dict[str, int] = {}
            access_level_counts: Dict[str, int] = {}
            confidence_scores = []
            
            for decision in user_decisions:
                # Подсчитываем решения
                decision_type = decision.decision.value
                decision_counts[decision_type] = decision_counts.get(decision_type, 0) + 1
                
                # Подсчитываем уровни доступа
                access_level = decision.access_level.value
                access_level_counts[access_level] = access_level_counts.get(access_level, 0) + 1
                
                # Собираем баллы уверенности
                confidence_scores.append(decision.confidence_score)
            
            # Рассчитываем статистику
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            return {
                "user_id": user_id,
                "period_hours": hours,
                "total_requests": len(user_decisions),
                "decision_counts": decision_counts,
                "access_level_counts": access_level_counts,
                "average_confidence": avg_confidence,
                "recent_decisions": [
                    {
                        "resource": d.resource,
                        "decision": d.decision.value,
                        "access_level": d.access_level.value,
                        "confidence": d.confidence_score,
                        "timestamp": d.timestamp.isoformat()
                    }
                    for d in user_decisions[-5:]  # Последние 5 решений
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения сводки доступа: {e}")
            return {"user_id": user_id, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Получение статуса Context Aware Access
        Returns:
            Dict[str, Any]: Статус сервиса
        """
        try:
            # Получаем базовый статус
            base_status = super().get_status()
            
            # Добавляем специфичную информацию
            status = {
                **base_status,
                "total_rules": len(self.access_rules),
                "total_decisions": len(self.access_decisions),
                "cache_size": len(self.context_cache),
                "rules_by_priority": {
                    str(rule.priority): len([r for r in self.access_rules.values() if r.priority == rule.priority])
                    for rule in self.access_rules.values()
                },
                "decisions_by_type": {
                    decision.value: len([d for d in self.access_decisions if d.decision == decision])
                    for decision in AccessDecisionType
                },
                "context_weights": {k.value: v for k, v in self.context_weights.items()},
                "context_access_levels": {k.value: v.value for k, v in self.context_access_levels.items()},
                "time_restrictions": self.time_restrictions
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}