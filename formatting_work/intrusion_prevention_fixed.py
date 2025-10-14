# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Intrusion Prevention Service
Система предотвращения вторжений для семей
Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-02
"""
import hashlib
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from core.base import SecurityBase


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

    def detect_intrusion(
        self,
        event_data: Dict[str, Any],
        user_id: Optional[str] = None,
        user_age: Optional[int] = None,
    ) -> List[IntrusionAttempt]:
        """Обнаружение попыток вторжения"""
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
        if confidence >= 0.9:
            return IntrusionSeverity.CRITICAL
        elif confidence >= 0.7:
            return IntrusionSeverity.HIGH
        elif confidence >= 0.5:
            return IntrusionSeverity.MEDIUM
        else:
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

    def _compare_severity(
        self,
        attempt_severity: IntrusionSeverity,
        rule_threshold: IntrusionSeverity,
    ) -> bool:
        """Сравнение серьезности"""
        severity_order = {
            IntrusionSeverity.LOW: 1,
            IntrusionSeverity.MEDIUM: 2,
            IntrusionSeverity.HIGH: 3,
            IntrusionSeverity.CRITICAL: 4,
        }
        return (
            severity_order[attempt_severity] >= severity_order[rule_threshold]
        )

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
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(timestamp.encode()).hexdigest()[:8]
        return f"intrusion_{timestamp}_{random_part}"

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
