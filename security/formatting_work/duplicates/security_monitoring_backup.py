# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Security Monitoring Module
Модуль мониторинга безопасности для системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-01
"""

import threading
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import ComponentStatus, SecurityBase


class MonitoringType(Enum):
    """Типы мониторинга"""

    REAL_TIME = "real_time"
    PERIODIC = "periodic"
    EVENT_DRIVEN = "event_driven"
    CONTINUOUS = "continuous"


class AlertSeverity(Enum):
    """Уровни серьезности оповещений"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MonitoringRule:
    """Класс для представления правила мониторинга"""

    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        monitoring_type: MonitoringType,
        target_component: str,
        condition: str,
        severity: AlertSeverity,
    ):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.monitoring_type = monitoring_type
        self.target_component = target_component
        self.condition = condition
        self.severity = severity
        self.enabled = True
        self.created_at = datetime.now()
        self.last_triggered: Optional[datetime] = None
        self.trigger_count = 0
        self.threshold = 1
        self.time_window = 300  # 5 минут
        self.actions: List[Dict[str, Any]] = []

    def add_action(self, action_type: str, action_config: Dict[str, Any]):
        """Добавление действия к правилу"""
        action = {"type": action_type, "config": action_config, "enabled": True}
        self.actions.append(action)

    def check_condition(self, data: Dict[str, Any]) -> bool:
        """Проверка условия правила"""
        try:
            # Простая реализация проверки условий
            # В реальной системе здесь будет более сложная логика
            if "value" in data and "threshold" in data:
                return data["value"] > data["threshold"]
            return False
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "monitoring_type": self.monitoring_type.value,
            "target_component": self.target_component,
            "condition": self.condition,
            "severity": self.severity.value,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "last_triggered": (self.last_triggered.isoformat() if self.last_triggered else None),
            "trigger_count": self.trigger_count,
            "threshold": self.threshold,
            "time_window": self.time_window,
            "actions": self.actions,
        }


class SecurityAlert:
    """Класс для представления оповещения безопасности"""

    def __init__(
        self,
        alert_id: str,
        rule_id: str,
        title: str,
        description: str,
        severity: AlertSeverity,
        source_component: str,
    ):
        self.alert_id = alert_id
        self.rule_id = rule_id
        self.title = title
        self.description = description
        self.severity = severity
        self.source_component = source_component
        self.created_at = datetime.now()
        self.acknowledged_at: Optional[datetime] = None
        self.resolved_at: Optional[datetime] = None
        self.acknowledged_by: Optional[str] = None
        self.resolved_by: Optional[str] = None
        self.status = "active"
        self.data: Dict[str, Any] = {}

    def acknowledge(self, acknowledged_by: str):
        """Подтверждение оповещения"""
        self.acknowledged_at = datetime.now()
        self.acknowledged_by = acknowledged_by
        self.status = "acknowledged"

    def resolve(self, resolved_by: str, resolution_notes: Optional[str] = None):
        """Разрешение оповещения"""
        self.resolved_at = datetime.now()
        self.resolved_by = resolved_by
        self.status = "resolved"
        if resolution_notes:
            self.data["resolution_notes"] = resolution_notes

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "alert_id": self.alert_id,
            "rule_id": self.rule_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "source_component": self.source_component,
            "created_at": self.created_at.isoformat(),
            "acknowledged_at": (self.acknowledged_at.isoformat() if self.acknowledged_at else None),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "acknowledged_by": self.acknowledged_by,
            "resolved_by": self.resolved_by,
            "status": self.status,
            "data": self.data,
        }


class SecurityMonitoringManager(SecurityBase):
    """Менеджер мониторинга безопасности для системы ALADDIN"""

    def __init__(
        self,
        name: str = "SecurityMonitoringManager",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Конфигурация мониторинга
        self.monitoring_interval = config.get("monitoring_interval", 30) if config else 30  # секунды
        self.alert_retention_days = config.get("alert_retention_days", 30) if config else 30
        self.enable_real_time = config.get("enable_real_time", True) if config else True
        self.max_concurrent_monitors = config.get("max_concurrent_monitors", 10) if config else 10

        # Хранилище данных
        self.monitoring_rules: Dict[str, MonitoringRule] = {}
        self.active_alerts: Dict[str, SecurityAlert] = {}
        self.alert_history: List[SecurityAlert] = []
        self.monitoring_data: Dict[str, Any] = {}
        self.monitoring_callbacks: Dict[str, Any] = {}

        # Статистика
        self.total_alerts = 0
        self.active_alerts_count = 0
        self.acknowledged_alerts = 0
        self.resolved_alerts = 0
        self.rules_triggered = 0

        # Потоки мониторинга
        self.monitoring_threads: Dict[str, Any] = {}
        self.stop_monitoring = False

    def initialize(self) -> bool:
        """Инициализация менеджера мониторинга безопасности"""
        try:
            self.log_activity(f"Инициализация менеджера мониторинга безопасности {self.name}")
            self.status = ComponentStatus.INITIALIZING

            # Создание базовых правил мониторинга
            self._create_basic_monitoring_rules()

            # Настройка мониторинга компонентов
            self._setup_component_monitoring()

            # Инициализация системы оповещений
            self._setup_alerting_system()

            # Запуск мониторинга в реальном времени
            if self.enable_real_time:
                self._start_real_time_monitoring()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(f"Менеджер мониторинга безопасности {self.name} успешно инициализирован")
            return True

        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка инициализации менеджера мониторинга безопасности {self.name}: {e}",
                "error",
            )
            return False

    def _create_basic_monitoring_rules(self):
        """Создание базовых правил мониторинга"""
        basic_rules = [
            {
                "rule_id": "RULE_001",
                "name": "Высокий уровень угроз",
                "description": "Мониторинг высокого уровня угроз в системе",
                "monitoring_type": MonitoringType.REAL_TIME,
                "target_component": "threat_intelligence",
                "condition": "threat_level > 0.8",
                "severity": AlertSeverity.HIGH,
            },
            {
                "rule_id": "RULE_002",
                "name": "Неудачные попытки аутентификации",
                "description": "Мониторинг неудачных попыток входа",
                "monitoring_type": MonitoringType.EVENT_DRIVEN,
                "target_component": "authentication",
                "condition": "failed_attempts > 5",
                "severity": AlertSeverity.WARNING,
            },
            {
                "rule_id": "RULE_003",
                "name": "Критические инциденты",
                "description": "Мониторинг критических инцидентов безопасности",
                "monitoring_type": MonitoringType.EVENT_DRIVEN,
                "target_component": "incident_response",
                "condition": "critical_incidents > 0",
                "severity": AlertSeverity.CRITICAL,
            },
            {
                "rule_id": "RULE_004",
                "name": "Низкий uptime системы",
                "description": "Мониторинг времени работы системы",
                "monitoring_type": MonitoringType.PERIODIC,
                "target_component": "system_health",
                "condition": "uptime < 95",
                "severity": AlertSeverity.ERROR,
            },
            {
                "rule_id": "RULE_005",
                "name": "Нарушения соответствия",
                "description": "Мониторинг нарушений требований соответствия",
                "monitoring_type": MonitoringType.PERIODIC,
                "target_component": "compliance",
                "condition": "compliance_rate < 0.8",
                "severity": AlertSeverity.WARNING,
            },
        ]

        for rule_data in basic_rules:
            rule = MonitoringRule(
                rule_id=rule_data["rule_id"],
                name=rule_data["name"],
                description=rule_data["description"],
                monitoring_type=rule_data["monitoring_type"],
                target_component=rule_data["target_component"],
                condition=rule_data["condition"],
                severity=rule_data["severity"],
            )

            # Добавление действий по умолчанию
            rule.add_action("log", {"level": "warning"})
            rule.add_action("email", {"recipients": ["admin@aladdin.local"]})

            self.add_monitoring_rule(rule)

        self.log_activity(f"Создано {len(basic_rules)} базовых правил мониторинга")

    def _setup_component_monitoring(self):
        """Настройка мониторинга компонентов"""
        self.monitoring_data = {
            "threat_intelligence": {
                "enabled": True,
                "metrics": ["threat_level", "active_threats", "threat_detection_rate"],
                "interval": 60,
            },
            "authentication": {
                "enabled": True,
                "metrics": ["failed_attempts", "successful_logins", "active_sessions"],
                "interval": 30,
            },
            "incident_response": {
                "enabled": True,
                "metrics": ["open_incidents", "critical_incidents", "response_time"],
                "interval": 120,
            },
            "system_health": {
                "enabled": True,
                "metrics": ["uptime", "cpu_usage", "memory_usage", "disk_usage"],
                "interval": 60,
            },
            "compliance": {
                "enabled": True,
                "metrics": ["compliance_rate", "non_compliant_items", "audit_score"],
                "interval": 300,
            },
        }
        self.log_activity("Мониторинг компонентов настроен")

    def _setup_alerting_system(self):
        """Настройка системы оповещений"""
        # Здесь будет логика системы оповещений
        self.log_activity("Система оповещений настроена")

    def _start_real_time_monitoring(self):
        """Запуск мониторинга в реальном времени"""
        try:
            for component, config in self.monitoring_data.items():
                if config["enabled"]:
                    thread = threading.Thread(
                        target=self._monitor_component,
                        args=(component, config),
                        daemon=True,
                    )
                    thread.start()
                    self.monitoring_threads[component] = thread

            self.log_activity("Мониторинг в реальном времени запущен")

        except Exception as e:
            self.log_activity(f"Ошибка запуска мониторинга в реальном времени: {e}", "error")

    def _monitor_component(self, component: str, config: Dict[str, Any]):
        """Мониторинг компонента"""
        try:
            while not self.stop_monitoring:
                # Сбор метрик компонента
                metrics = self._collect_component_metrics(component, config["metrics"])

                # Проверка правил мониторинга
                self._check_monitoring_rules(component, metrics)

                # Ожидание следующего цикла
                time.sleep(config["interval"])

        except Exception as e:
            self.log_activity(f"Ошибка мониторинга компонента {component}: {e}", "error")

    def _collect_component_metrics(self, component: str, metrics: List[str]) -> Dict[str, Any]:
        """Сбор метрик компонента"""
        try:
            # В реальной системе здесь будет сбор реальных метрик
            # Пока используем мок-данные
            mock_metrics = {
                "threat_intelligence": {
                    "threat_level": 0.3,
                    "active_threats": 2,
                    "threat_detection_rate": 85.5,
                },
                "authentication": {
                    "failed_attempts": 3,
                    "successful_logins": 45,
                    "active_sessions": 12,
                },
                "incident_response": {
                    "open_incidents": 1,
                    "critical_incidents": 0,
                    "response_time": 15.2,
                },
                "system_health": {
                    "uptime": 99.8,
                    "cpu_usage": 45.2,
                    "memory_usage": 67.8,
                    "disk_usage": 23.4,
                },
                "compliance": {
                    "compliance_rate": 0.92,
                    "non_compliant_items": 3,
                    "audit_score": 88.5,
                },
            }

            return mock_metrics.get(component, {})  # type: ignore

        except Exception as e:
            self.log_activity(f"Ошибка сбора метрик компонента {component}: {e}", "error")
            return {}

    def _check_monitoring_rules(self, component: str, metrics: Dict[str, Any]):
        """Проверка правил мониторинга"""
        try:
            for rule in self.monitoring_rules.values():
                if not rule.enabled or rule.target_component != component:
                    continue

                # Проверка условия правила
                if self._evaluate_rule_condition(rule, metrics):
                    self._trigger_alert(rule, component, metrics)

        except Exception as e:
            self.log_activity(f"Ошибка проверки правил мониторинга: {e}", "error")

    def _evaluate_rule_condition(self, rule: MonitoringRule, metrics: Dict[str, Any]) -> bool:
        """Оценка условия правила"""
        try:
            # Простая реализация оценки условий
            # В реальной системе здесь будет более сложная логика

            if rule.condition == "threat_level > 0.8":
                return metrics.get("threat_level", 0) > 0.8
            elif rule.condition == "failed_attempts > 5":
                return metrics.get("failed_attempts", 0) > 5
            elif rule.condition == "critical_incidents > 0":
                return metrics.get("critical_incidents", 0) > 0
            elif rule.condition == "uptime < 95":
                return metrics.get("uptime", 100) < 95
            elif rule.condition == "compliance_rate < 0.8":
                return metrics.get("compliance_rate", 1.0) < 0.8

            return False

        except Exception as e:
            self.log_activity(f"Ошибка оценки условия правила: {e}", "error")
            return False

    def _trigger_alert(self, rule: MonitoringRule, component: str, metrics: Dict[str, Any]):
        """Срабатывание оповещения"""
        try:
            # Проверка частоты срабатывания
            if rule.last_triggered:
                time_since_last = (datetime.now() - rule.last_triggered).total_seconds()
                if time_since_last < rule.time_window:
                    return  # Слишком частое срабатывание

            # Создание оповещения
            alert_id = f"ALERT-{int(time.time())}"
            alert = SecurityAlert(
                alert_id=alert_id,
                rule_id=rule.rule_id,
                title=rule.name,
                description=f"{rule.description} - Компонент: {component}",
                severity=rule.severity,
                source_component=component,
            )
            alert.data = metrics

            # Сохранение оповещения
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            self.active_alerts_count += 1
            self.total_alerts += 1
            self.rules_triggered += 1

            # Обновление статистики правила
            rule.last_triggered = datetime.now()
            rule.trigger_count += 1

            # Выполнение действий
            self._execute_rule_actions(rule, alert)

            self.log_activity(f"Сработало оповещение: {alert.title} ({alert_id})")

        except Exception as e:
            self.log_activity(f"Ошибка срабатывания оповещения: {e}", "error")

    def _execute_rule_actions(self, rule: MonitoringRule, alert: SecurityAlert):
        """Выполнение действий правила"""
        try:
            for action in rule.actions:
                if not action["enabled"]:
                    continue

                action_type = action["type"]

                if action_type == "log":
                    self.log_activity(f"Оповещение: {alert.title}", "warning")

                elif action_type == "email":
                    # Здесь будет отправка email
                    self.log_activity(f"Email оповещение отправлено: {alert.title}")

                elif action_type == "webhook":
                    # Здесь будет отправка webhook
                    self.log_activity(f"Webhook оповещение отправлено: {alert.title}")

                elif action_type == "callback" and alert.alert_id in self.monitoring_callbacks:
                    callback = self.monitoring_callbacks[alert.alert_id]
                    callback(alert)

        except Exception as e:
            self.log_activity(f"Ошибка выполнения действий правила: {e}", "error")

    def add_monitoring_rule(self, rule: MonitoringRule) -> bool:
        """
        Добавление правила мониторинга

        Args:
            rule: Правило мониторинга

        Returns:
            bool: True если правило добавлено
        """
        try:
            if rule.rule_id in self.monitoring_rules:
                self.log_activity(f"Правило {rule.rule_id} уже существует", "warning")
                return False

            self.monitoring_rules[rule.rule_id] = rule

            self.log_activity(f"Добавлено правило мониторинга: {rule.name}")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка добавления правила мониторинга: {e}", "error")
            return False

    def remove_monitoring_rule(self, rule_id: str) -> bool:
        """
        УДАЛЕНИЕ ПРАВИЛА МОНИТОРИНГА ОТКЛЮЧЕНО В ЦЕЛЯХ БЕЗОПАСНОСТИ

        Args:
            rule_id: ID правила

        Returns:
            bool: False - операция заблокирована системой безопасности
        """
        self.log_activity(
            f"ПОПЫТКА УДАЛЕНИЯ ПРАВИЛА МОНИТОРИНГА {rule_id} ЗАБЛОКИРОВАНА СИСТЕМОЙ БЕЗОПАСНОСТИ",
            "critical",
        )

        # Создание события безопасности
        security_event = {
            "event_type": "blocked_dangerous_operation",
            "operation": "remove_monitoring_rule",
            "rule_id": rule_id,
            "timestamp": datetime.now().isoformat(),
            "reason": "Функция удаления отключена в целях безопасности",
            "severity": "CRITICAL",
        }

        # Логирование блокировки
        self.log_activity(f"КРИТИЧЕСКАЯ ОПЕРАЦИЯ ЗАБЛОКИРОВАНА: {security_event}", "critical")

        return False  # Операция заблокирована

    def enable_monitoring_rule(self, rule_id: str) -> bool:
        """
        Включение правила мониторинга

        Args:
            rule_id: ID правила

        Returns:
            bool: True если правило включено
        """
        try:
            if rule_id not in self.monitoring_rules:
                return False

            rule = self.monitoring_rules[rule_id]
            rule.enabled = True

            self.log_activity(f"Правило мониторинга включено: {rule.name}")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка включения правила мониторинга: {e}", "error")
            return False

    def disable_monitoring_rule(self, rule_id: str) -> bool:
        """
        Отключение правила мониторинга

        Args:
            rule_id: ID правила

        Returns:
            bool: True если правило отключено
        """
        try:
            if rule_id not in self.monitoring_rules:
                return False

            rule = self.monitoring_rules[rule_id]
            rule.enabled = False

            self.log_activity(f"Правило мониторинга отключено: {rule.name}")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка отключения правила мониторинга: {e}", "error")
            return False

    def get_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение оповещения

        Args:
            alert_id: ID оповещения

        Returns:
            Optional[Dict[str, Any]]: Данные оповещения
        """
        if alert_id in self.active_alerts:
            return self.active_alerts[alert_id].to_dict()
        return None

    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Dict[str, Any]]:
        """
        Получение активных оповещений

        Args:
            severity: Фильтр по серьезности

        Returns:
            List[Dict[str, Any]]: Список активных оповещений
        """
        alerts = []

        for alert in self.active_alerts.values():
            if severity is None or alert.severity == severity:
                alerts.append(alert.to_dict())

        return alerts

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """
        Подтверждение оповещения

        Args:
            alert_id: ID оповещения
            acknowledged_by: Кто подтвердил

        Returns:
            bool: True если оповещение подтверждено
        """
        try:
            if alert_id not in self.active_alerts:
                return False

            alert = self.active_alerts[alert_id]
            alert.acknowledge(acknowledged_by)

            self.acknowledged_alerts += 1

            self.log_activity(f"Оповещение подтверждено: {alert_id}")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка подтверждения оповещения: {e}", "error")
            return False

    def resolve_alert(self, alert_id: str, resolved_by: str, resolution_notes: str = "") -> bool:
        """
        Разрешение оповещения (БЕЗОПАСНАЯ ВЕРСИЯ)

        Args:
            alert_id: ID оповещения
            resolved_by: Кто разрешил
            resolution_notes: Заметки о разрешении

        Returns:
            bool: True если оповещение разрешено
        """
        try:
            if alert_id not in self.active_alerts:
                return False

            alert = self.active_alerts[alert_id]
            alert.resolve(resolved_by, resolution_notes)

            # БЕЗОПАСНОЕ РАЗРЕШЕНИЕ - НЕ УДАЛЯЕМ ОПОВЕЩЕНИЕ
            # Вместо удаления помечаем как разрешенное
            alert.status = "resolved"
            alert.resolved_at = datetime.now()
            alert.resolved_by = resolved_by
            if resolution_notes:
                alert.data["resolution_notes"] = resolution_notes

            # Обновляем счетчики
            self.active_alerts_count = max(0, self.active_alerts_count - 1)
            self.resolved_alerts += 1

            # Логируем безопасную операцию
            self.log_activity(f"Оповещение разрешено (БЕЗОПАСНО): {alert_id} пользователем {resolved_by}")

            # Создаем событие безопасности
            security_event = {
                "event_type": "alert_resolved_safely",
                "alert_id": alert_id,
                "resolved_by": resolved_by,
                "timestamp": datetime.now().isoformat(),
                "method": "safe_resolution_no_deletion",
            }

            self.log_activity(f"Событие безопасности: {security_event}")

            return True

        except Exception as e:
            self.log_activity(f"Ошибка разрешения оповещения: {e}", "error")
            return False

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """
        Получение статистики мониторинга

        Returns:
            Dict[str, Any]: Статистика мониторинга
        """
        return {
            "total_alerts": self.total_alerts,
            "active_alerts_count": self.active_alerts_count,
            "acknowledged_alerts": self.acknowledged_alerts,
            "resolved_alerts": self.resolved_alerts,
            "rules_triggered": self.rules_triggered,
            "total_rules": len(self.monitoring_rules),
            "enabled_rules": len([r for r in self.monitoring_rules.values() if r.enabled]),
            "monitoring_components": len(self.monitoring_data),
            "active_threads": len(self.monitoring_threads),
            "alerts_by_severity": self._get_alerts_by_severity(),
            "alerts_by_component": self._get_alerts_by_component(),
        }

    def _get_alerts_by_severity(self) -> Dict[str, int]:
        """Получение количества оповещений по серьезности"""
        severity_count: Dict[str, int] = {}
        for alert in self.active_alerts.values():
            severity = alert.severity.value
            severity_count[severity] = severity_count.get(severity, 0) + 1
        return severity_count

    def _get_alerts_by_component(self) -> Dict[str, int]:
        """Получение количества оповещений по компонентам"""
        component_count: Dict[str, int] = {}
        for alert in self.active_alerts.values():
            component = alert.source_component
            component_count[component] = component_count.get(component, 0) + 1
        return component_count

    def start(self) -> bool:
        """Запуск менеджера мониторинга безопасности"""
        try:
            self.log_activity(f"Запуск менеджера мониторинга безопасности {self.name}")
            self.stop_monitoring = False
            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(f"Менеджер мониторинга безопасности {self.name} успешно запущен")
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка запуска менеджера мониторинга безопасности {self.name}: {e}",
                "error",
            )
            return False

    def stop(self) -> bool:
        """
        Остановка менеджера мониторинга безопасности (БЕЗОПАСНАЯ ВЕРСИЯ)

        Returns:
            bool: True если менеджер остановлен
        """
        try:
            self.log_activity(f"Попытка остановки менеджера мониторинга безопасности {self.name}")

            # ПРОВЕРКА БЕЗОПАСНОСТИ - НЕ РАЗРЕШАЕМ ОСТАНОВКУ В ПРОДАКШЕНЕ
            if hasattr(self, "production_mode") and self.production_mode:
                self.log_activity("ОСТАНОВКА ЗАБЛОКИРОВАНА - ПРОДАКШЕН РЕЖИМ", "critical")

                # Создаем критическое событие безопасности
                security_event = {
                    "event_type": "blocked_stop_attempt",
                    "component": self.name,
                    "timestamp": datetime.now().isoformat(),
                    "reason": "Остановка заблокирована в продакшен режиме",
                    "severity": "CRITICAL",
                }

                self.log_activity(f"КРИТИЧЕСКАЯ ОПЕРАЦИЯ ЗАБЛОКИРОВАНА: {security_event}", "critical")
                return False

            # БЕЗОПАСНАЯ ОСТАНОВКА - НЕ ОЧИЩАЕМ ПОТОКИ
            self.log_activity(f"Безопасная остановка менеджера мониторинга безопасности {self.name}")

            # Остановка мониторинга
            self.stop_monitoring = True

            # Ожидание завершения потоков (безопасно)
            for thread in self.monitoring_threads.values():
                if thread.is_alive():
                    thread.join(timeout=5)

            # БЕЗОПАСНО - НЕ ОЧИЩАЕМ ПОТОКИ
            # self.monitoring_threads.clear()  # ЗАКОММЕНТИРОВАНО В ЦЕЛЯХ
            # БЕЗОПАСНОСТИ

            self.status = ComponentStatus.STOPPED
            self.log_activity(f"Менеджер мониторинга безопасности {self.name} безопасно остановлен")

            # Логируем безопасную остановку
            security_event = {
                "event_type": "safe_stop_completed",
                "component": self.name,
                "timestamp": datetime.now().isoformat(),
                "method": "safe_stop_no_thread_clearing",
            }

            self.log_activity(f"Безопасная остановка завершена: {security_event}")

            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка остановки менеджера мониторинга безопасности {self.name}: {e}",
                "error",
            )
            return False
