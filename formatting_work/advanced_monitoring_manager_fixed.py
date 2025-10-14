#!/usr/bin/env python3
"""
ALADDIN Security System - Advanced Monitoring Manager
Расширенный мониторинг системы с метриками, алертами и дашбордом
"""

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import psutil

from core.base import ComponentStatus, SecurityLevel
from core.logging_module import LoggingManager
from core.security_base import SecurityBase


class MetricType(Enum):
    """Типы метрик"""

    SYSTEM = "system"
    SECURITY = "security"
    PERFORMANCE = "performance"
    NETWORK = "network"
    API = "api"
    DATABASE = "database"
    CUSTOM = "custom"


class AlertSeverity(Enum):
    """Уровни серьезности алертов"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Метрика системы"""

    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""


@dataclass
class Alert:
    """Алерт системы"""

    alert_id: str
    title: str
    message: str
    severity: AlertSeverity
    metric_name: str
    threshold_value: float
    current_value: float
    timestamp: datetime
    resolved: bool = False
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class MonitoringRule:
    """Правило мониторинга"""

    rule_id: str
    name: str
    metric_name: str
    condition: str  # ">", "<", ">=", "<=", "==", "!="
    threshold: float
    severity: AlertSeverity
    enabled: bool = True
    cooldown: int = 300  # секунды
    last_triggered: Optional[datetime] = None


class AdvancedMonitoringManager(SecurityBase):
    """Расширенный менеджер мониторинга системы"""

    def __init__(self, name: str = "AdvancedMonitoringManager"):
        super().__init__(name)
        self.status = ComponentStatus.INITIALIZING
        self.security_level = SecurityLevel.HIGH
        self.logger = LoggingManager(name="AdvancedMonitoringManager")

        # Конфигурация
        self.monitoring_interval = 10  # секунды
        self.metrics_retention = 3600  # секунды (1 час)
        self.alerts_retention = 86400  # секунды (24 часа)

        # Хранилища данных
        self.metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self.alerts: List[Alert] = []
        self.monitoring_rules: Dict[str, MonitoringRule] = {}

        # Статистика
        self.stats = {
            "total_metrics": 0,
            "total_alerts": 0,
            "active_rules": 0,
            "system_uptime": time.time(),
            "last_update": None,
        }

        # Мониторинг компонентов
        self.monitored_components = {}
        self.monitoring_threads = {}
        self.stop_monitoring = False

        # Callbacks для алертов
        self.alert_callbacks: List[Callable] = []

        self._initialize_monitoring_rules()
        self._start_monitoring()

        self.status = ComponentStatus.RUNNING
        self.logger.log("INFO", "AdvancedMonitoringManager инициализирован")

    def _initialize_monitoring_rules(self):
        """Инициализация правил мониторинга"""
        rules = [
            # Системные метрики
            MonitoringRule(
                rule_id="cpu_high",
                name="Высокая загрузка CPU",
                metric_name="system.cpu_percent",
                condition=">",
                threshold=80.0,
                severity=AlertSeverity.WARNING,
            ),
            MonitoringRule(
                rule_id="memory_high",
                name="Высокое использование памяти",
                metric_name="system.memory_percent",
                condition=">",
                threshold=85.0,
                severity=AlertSeverity.WARNING,
            ),
            MonitoringRule(
                rule_id="disk_high",
                name="Мало места на диске",
                metric_name="system.disk_percent",
                condition=">",
                threshold=90.0,
                severity=AlertSeverity.ERROR,
            ),
            # Безопасность
            MonitoringRule(
                rule_id="failed_logins",
                name="Много неудачных входов",
                metric_name="security.failed_logins",
                condition=">",
                threshold=10.0,
                severity=AlertSeverity.WARNING,
            ),
            MonitoringRule(
                rule_id="suspicious_activity",
                name="Подозрительная активность",
                metric_name="security.suspicious_events",
                condition=">",
                threshold=5.0,
                severity=AlertSeverity.ERROR,
            ),
            # Производительность
            MonitoringRule(
                rule_id="response_time_high",
                name="Высокое время отклика",
                metric_name="performance.response_time",
                condition=">",
                threshold=5.0,
                severity=AlertSeverity.WARNING,
            ),
            MonitoringRule(
                rule_id="api_errors",
                name="Ошибки API",
                metric_name="api.error_rate",
                condition=">",
                threshold=5.0,
                severity=AlertSeverity.ERROR,
            ),
        ]

        for rule in rules:
            self.monitoring_rules[rule.rule_id] = rule

        self.stats["active_rules"] = len(self.monitoring_rules)
        self.logger.log(
            "INFO",
            f"Инициализировано {len(self.monitoring_rules)} "
            f"правил мониторинга",
        )

    def _start_monitoring(self):
        """Запуск мониторинга"""
        # Основной поток мониторинга
        main_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        main_thread.start()
        self.monitoring_threads["main"] = main_thread

        # Поток очистки старых данных
        cleanup_thread = threading.Thread(
            target=self._cleanup_loop, daemon=True
        )
        cleanup_thread.start()
        self.monitoring_threads["cleanup"] = cleanup_thread

        self.logger.log("INFO", "Мониторинг запущен")

    def _monitoring_loop(self):
        """Основной цикл мониторинга"""
        while not self.stop_monitoring:
            try:
                # Сбор системных метрик
                self._collect_system_metrics()

                # Сбор метрик безопасности
                self._collect_security_metrics()

                # Сбор метрик производительности
                self._collect_performance_metrics()

                # Сбор метрик API
                self._collect_api_metrics()

                # Проверка правил мониторинга
                self._check_monitoring_rules()

                self.stats["last_update"] = datetime.now()

            except Exception as e:
                self.logger.log("ERROR", f"Ошибка в цикле мониторинга: {e}")

            time.sleep(self.monitoring_interval)

    def _cleanup_loop(self):
        """Цикл очистки старых данных"""
        while not self.stop_monitoring:
            try:
                current_time = time.time()

                # Очистка старых метрик
                for metric_name, metric_deque in self.metrics.items():
                    while (
                        metric_deque
                        and (
                            current_time
                            - metric_deque[0].timestamp.timestamp()
                        )
                        > self.metrics_retention
                    ):
                        metric_deque.popleft()

                # Очистка старых алертов
                self.alerts = [
                    alert
                    for alert in self.alerts
                    if (current_time - alert.timestamp.timestamp())
                    <= self.alerts_retention
                ]

                time.sleep(300)  # Очистка каждые 5 минут

            except Exception as e:
                self.logger.log("ERROR", f"Ошибка в цикле очистки: {e}")

    def _collect_system_metrics(self):
        """Сбор системных метрик"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self._add_metric(
                "system.cpu_percent", cpu_percent, MetricType.SYSTEM, "percent"
            )

            # Память
            memory = psutil.virtual_memory()
            self._add_metric(
                "system.memory_percent",
                memory.percent,
                MetricType.SYSTEM,
                "percent",
            )
            self._add_metric(
                "system.memory_used", memory.used, MetricType.SYSTEM, "bytes"
            )
            self._add_metric(
                "system.memory_available",
                memory.available,
                MetricType.SYSTEM,
                "bytes",
            )

            # Диск
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            self._add_metric(
                "system.disk_percent",
                disk_percent,
                MetricType.SYSTEM,
                "percent",
            )
            self._add_metric(
                "system.disk_used", disk.used, MetricType.SYSTEM, "bytes"
            )
            self._add_metric(
                "system.disk_free", disk.free, MetricType.SYSTEM, "bytes"
            )

            # Сеть
            net_io = psutil.net_io_counters()
            self._add_metric(
                "system.network_bytes_sent",
                net_io.bytes_sent,
                MetricType.NETWORK,
                "bytes",
            )
            self._add_metric(
                "system.network_bytes_recv",
                net_io.bytes_recv,
                MetricType.NETWORK,
                "bytes",
            )

        except Exception as e:
            self.logger.log("ERROR", f"Ошибка сбора системных метрик: {e}")

    def _collect_security_metrics(self):
        """Сбор метрик безопасности"""
        try:
            # Мок-данные для демонстрации
            # В реальной системе здесь будут данные из логов безопасности
            failed_logins = 0  # Получать из логов
            suspicious_events = 0  # Получать из системы обнаружения угроз
            active_threats = 0  # Получать из threat intelligence

            self._add_metric(
                "security.failed_logins",
                failed_logins,
                MetricType.SECURITY,
                "count",
            )
            self._add_metric(
                "security.suspicious_events",
                suspicious_events,
                MetricType.SECURITY,
                "count",
            )
            self._add_metric(
                "security.active_threats",
                active_threats,
                MetricType.SECURITY,
                "count",
            )

        except Exception as e:
            self.logger.log("ERROR", f"Ошибка сбора метрик безопасности: {e}")

    def _collect_performance_metrics(self):
        """Сбор метрик производительности"""
        try:
            # Время отклика API (мок)
            response_time = 0.1  # Получать из реальных измерений
            self._add_metric(
                "performance.response_time",
                response_time,
                MetricType.PERFORMANCE,
                "seconds",
            )

            # Количество активных соединений
            connections = len(psutil.net_connections())
            self._add_metric(
                "performance.active_connections",
                connections,
                MetricType.PERFORMANCE,
                "count",
            )

            # Загрузка процессов
            process_count = len(psutil.pids())
            self._add_metric(
                "performance.process_count",
                process_count,
                MetricType.PERFORMANCE,
                "count",
            )

        except Exception as e:
            self.logger.log(
                "ERROR", f"Ошибка сбора метрик производительности: {e}"
            )

    def _collect_api_metrics(self):
        """Сбор метрик API"""
        try:
            # Мок-данные для демонстрации
            api_requests = 0  # Получать из логов API
            api_errors = 0  # Получать из логов ошибок
            api_response_time = 0.1  # Получать из измерений

            self._add_metric(
                "api.requests_per_second",
                api_requests,
                MetricType.API,
                "requests/sec",
            )
            self._add_metric(
                "api.error_rate", api_errors, MetricType.API, "errors/sec"
            )
            self._add_metric(
                "api.response_time",
                api_response_time,
                MetricType.API,
                "seconds",
            )

        except Exception as e:
            self.logger.log("ERROR", f"Ошибка сбора метрик API: {e}")

    def _add_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType,
        unit: str = "",
        tags: Dict[str, str] = None,
    ):
        """Добавление метрики"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.now(),
            unit=unit,
            tags=tags or {},
        )

        self.metrics[name].append(metric)
        self.stats["total_metrics"] += 1

    def _check_monitoring_rules(self):
        """Проверка правил мониторинга"""
        for rule in self.monitoring_rules.values():
            if not rule.enabled:
                continue

            # Проверяем cooldown
            if (
                rule.last_triggered
                and (datetime.now() - rule.last_triggered).seconds
                < rule.cooldown
            ):
                continue

            # Получаем последнее значение метрики
            if (
                rule.metric_name not in self.metrics
                or not self.metrics[rule.metric_name]
            ):
                continue

            latest_metric = self.metrics[rule.metric_name][-1]
            current_value = latest_metric.value

            # Проверяем условие
            if self._evaluate_condition(
                current_value, rule.condition, rule.threshold
            ):
                self._trigger_alert(rule, current_value)

    def _evaluate_condition(
        self, value: float, condition: str, threshold: float
    ) -> bool:
        """Оценка условия правила"""
        if condition == ">":
            return value > threshold
        elif condition == "<":
            return value < threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        elif condition == "!=":
            return value != threshold
        return False

    def _trigger_alert(self, rule: MonitoringRule, current_value: float):
        """Создание алерта"""
        alert = Alert(
            alert_id=f"{rule.rule_id}_{int(time.time())}",
            title=rule.name,
            message=(
                f"Метрика {rule.metric_name} = {current_value} "
                f"{rule.condition} {rule.threshold}"
            ),
            severity=rule.severity,
            metric_name=rule.metric_name,
            threshold_value=rule.threshold,
            current_value=current_value,
            timestamp=datetime.now(),
            tags={"rule_id": rule.rule_id},
        )

        self.alerts.append(alert)
        rule.last_triggered = datetime.now()
        self.stats["total_alerts"] += 1

        # Вызов callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.log("ERROR", f"Ошибка в callback алерта: {e}")

        self.logger.log("WARNING", f"Алерт: {alert.title} - {alert.message}")

    def add_monitoring_rule(self, rule: MonitoringRule) -> bool:
        """Добавление правила мониторинга"""
        try:
            self.monitoring_rules[rule.rule_id] = rule
            self.stats["active_rules"] = len(
                [r for r in self.monitoring_rules.values() if r.enabled]
            )
            self.logger.log(
                "INFO", f"Добавлено правило мониторинга: {rule.name}"
            )
            return True
        except Exception as e:
            self.logger.log("ERROR", f"Ошибка добавления правила: {e}")
            return False

    def remove_monitoring_rule(self, rule_id: str) -> bool:
        """Удаление правила мониторинга"""
        try:
            if rule_id in self.monitoring_rules:
                del self.monitoring_rules[rule_id]
                self.stats["active_rules"] = len(
                    [r for r in self.monitoring_rules.values() if r.enabled]
                )
                self.logger.log(
                    "INFO", f"Удалено правило мониторинга: {rule_id}"
                )
                return True
            return False
        except Exception as e:
            self.logger.log("ERROR", f"Ошибка удаления правила: {e}")
            return False

    def add_alert_callback(self, callback: Callable):
        """Добавление callback для алертов"""
        self.alert_callbacks.append(callback)
        self.logger.log("INFO", "Добавлен callback для алертов")

    def get_metrics(
        self, metric_name: Optional[str] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """Получение метрик"""
        if metric_name:
            if metric_name in self.metrics:
                metrics_list = list(self.metrics[metric_name])[-limit:]
                return {
                    "metric_name": metric_name,
                    "metrics": [
                        {
                            "value": m.value,
                            "timestamp": m.timestamp.isoformat(),
                            "unit": m.unit,
                            "tags": m.tags,
                        }
                        for m in metrics_list
                    ],
                }
            return {"error": "Метрика не найдена"}

        # Все метрики
        result = {}
        for name, metric_deque in self.metrics.items():
            metrics_list = list(metric_deque)[-limit:]
            result[name] = [
                {
                    "value": m.value,
                    "timestamp": m.timestamp.isoformat(),
                    "unit": m.unit,
                    "tags": m.tags,
                }
                for m in metrics_list
            ]

        return result

    def get_alerts(
        self, severity: Optional[AlertSeverity] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Получение алертов"""
        alerts = self.alerts

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        # Сортируем по времени (новые сначала)
        alerts.sort(key=lambda x: x.timestamp, reverse=True)

        return [
            {
                "alert_id": a.alert_id,
                "title": a.title,
                "message": a.message,
                "severity": a.severity.value,
                "metric_name": a.metric_name,
                "threshold_value": a.threshold_value,
                "current_value": a.current_value,
                "timestamp": a.timestamp.isoformat(),
                "resolved": a.resolved,
                "tags": a.tags,
            }
            for a in alerts[:limit]
        ]

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Получение данных для дашборда"""
        current_time = datetime.now()
        uptime = current_time.timestamp() - self.stats["system_uptime"]

        # Последние значения ключевых метрик
        latest_metrics = {}
        for name, metric_deque in self.metrics.items():
            if metric_deque:
                latest_metrics[name] = {
                    "value": metric_deque[-1].value,
                    "unit": metric_deque[-1].unit,
                    "timestamp": metric_deque[-1].timestamp.isoformat(),
                }

        # Статистика алертов по серьезности
        alert_stats = defaultdict(int)
        for alert in self.alerts:
            alert_stats[alert.severity.value] += 1

        return {
            "system_info": {
                "uptime_seconds": uptime,
                "uptime_formatted": str(timedelta(seconds=int(uptime))),
                "last_update": (
                    self.stats["last_update"].isoformat()
                    if self.stats["last_update"]
                    else None
                ),
            },
            "metrics": latest_metrics,
            "alerts": {
                "total": len(self.alerts),
                "by_severity": dict(alert_stats),
                "recent": self.get_alerts(limit=10),
            },
            "rules": {
                "total": len(self.monitoring_rules),
                "active": self.stats["active_rules"],
            },
            "stats": self.stats,
        }

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса менеджера"""
        return {
            "component_name": self.name,
            "status": self.status.name,
            "security_level": self.security_level.name,
            "monitoring_active": not self.stop_monitoring,
            "metrics_count": len(self.metrics),
            "alerts_count": len(self.alerts),
            "rules_count": len(self.monitoring_rules),
            "uptime": time.time() - self.stats["system_uptime"],
            "last_update": (
                self.stats["last_update"].isoformat()
                if self.stats["last_update"]
                else None
            ),
        }

    def stop(self):
        """Остановка мониторинга"""
        self.stop_monitoring = True
        self.status = ComponentStatus.STOPPED

        # Ожидание завершения потоков
        for thread in self.monitoring_threads.values():
            if thread.is_alive():
                thread.join(timeout=5)

        self.logger.log("INFO", "Мониторинг остановлен")


# Глобальный экземпляр
advanced_monitoring_manager = AdvancedMonitoringManager()
