#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MonitorManager - Менеджер мониторинга системы безопасности
Централизованный мониторинг всех компонентов системы

Этот модуль предоставляет комплексную систему мониторинга для AI системы безопасности,
включающую реальное время мониторинга всех компонентов системы,
автоматическое обнаружение аномалий с использованием машинного обучения
и генерацию метрик производительности и статистики.

Автор: ALADDIN Security System
Версия: 3.0
Дата: 2025-01-06
Лицензия: MIT
"""

import asyncio
import logging
import queue
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import psutil
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitorStatus(Enum):
    """Статусы мониторинга"""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    """Уровни серьезности алертов"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MetricData:
    """Структура данных метрики"""

    name: str
    value: float
    timestamp: datetime
    unit: str = "count"
    tags: Dict[str, str] = field(default_factory=dict)
    status: MonitorStatus = MonitorStatus.UNKNOWN


@dataclass
class AlertRule:
    """Правило генерации алертов"""

    name: str
    metric_name: str
    threshold: float
    operator: str  # '>', '<', '>=', '<=', '==', '!='
    severity: AlertSeverity = AlertSeverity.MEDIUM
    enabled: bool = True
    cooldown: int = 300  # секунды


@dataclass
class Alert:
    """Структура алерта"""

    id: str
    rule_name: str
    metric_name: str
    value: float
    threshold: float
    severity: AlertSeverity
    timestamp: datetime
    message: str
    resolved: bool = False


@dataclass
class MonitorConfig:
    """Конфигурация мониторинга"""

    collection_interval: int = 30  # секунды
    retention_days: int = 30
    anomaly_detection_enabled: bool = True
    alerting_enabled: bool = True
    max_metrics_per_second: int = 1000
    cpu_threshold: float = 80.0
    memory_threshold: float = 85.0
    disk_threshold: float = 90.0


class MetricCollector(ABC):
    """Абстрактный класс для сбора метрик"""

    @abstractmethod
    async def collect(self) -> List[MetricData]:
        """Сбор метрик"""
        pass


class SystemMetricCollector(MetricCollector):
    """Сборщик системных метрик"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def collect(self) -> List[MetricData]:
        """Сбор системных метрик"""
        try:
            metrics = []

            # CPU метрики
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(
                MetricData(
                    name="cpu_usage",
                    value=cpu_percent,
                    timestamp=datetime.now(),
                    unit="percent",
                    tags={"type": "system"},
                    status=self._get_status(cpu_percent, 80.0),
                )
            )

            # Memory метрики
            memory = psutil.virtual_memory()
            metrics.append(
                MetricData(
                    name="memory_usage",
                    value=memory.percent,
                    timestamp=datetime.now(),
                    unit="percent",
                    tags={"type": "system"},
                    status=self._get_status(memory.percent, 85.0),
                )
            )

            # Disk метрики
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            metrics.append(
                MetricData(
                    name="disk_usage",
                    value=disk_percent,
                    timestamp=datetime.now(),
                    unit="percent",
                    tags={"type": "system"},
                    status=self._get_status(disk_percent, 90.0),
                )
            )

            # Network метрики
            network = psutil.net_io_counters()
            metrics.append(
                MetricData(
                    name="network_bytes_sent",
                    value=network.bytes_sent,
                    timestamp=datetime.now(),
                    unit="bytes",
                    tags={"type": "network", "direction": "sent"},
                )
            )

            metrics.append(
                MetricData(
                    name="network_bytes_recv",
                    value=network.bytes_recv,
                    timestamp=datetime.now(),
                    unit="bytes",
                    tags={"type": "network", "direction": "received"},
                )
            )

            return metrics

        except Exception as e:
            self.logger.error(f"Ошибка сбора системных метрик: {e}")
            return []

    def _get_status(self, value: float, threshold: float) -> MonitorStatus:
        """Определение статуса на основе порогового значения"""
        if value >= threshold:
            return MonitorStatus.CRITICAL
        elif value >= threshold * 0.8:
            return MonitorStatus.WARNING
        else:
            return MonitorStatus.HEALTHY


class AnomalyDetector:
    """Детектор аномалий на основе машинного обучения"""

    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.logger = logging.getLogger(__name__)

    async def train(self, historical_data: List[List[float]]) -> bool:
        """Обучение модели детекции аномалий"""
        try:
            if len(historical_data) < 10:
                self.logger.warning("Недостаточно данных для обучения")
                return False

            # Подготовка данных
            data_array = np.array(historical_data)
            scaled_data = self.scaler.fit_transform(data_array)

            # Обучение модели
            self.isolation_forest.fit(scaled_data)
            self.is_trained = True

            self.logger.info("Модель детекции аномалий обучена")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка обучения модели: {e}")
            return False

    async def detect_anomalies(
        self, current_data: List[float]
    ) -> Tuple[bool, float]:
        """Детекция аномалий в текущих данных"""
        try:
            if not self.is_trained:
                return False, 0.0

            # Подготовка данных
            data_array = np.array([current_data])
            scaled_data = self.scaler.transform(data_array)

            # Предсказание
            anomaly_score = self.isolation_forest.decision_function(
                scaled_data
            )[0]
            is_anomaly = self.isolation_forest.predict(scaled_data)[0] == -1

            return bool(is_anomaly), float(anomaly_score)

        except Exception as e:
            self.logger.error(f"Ошибка детекции аномалий: {e}")
            return False, 0.0


class AlertManager:
    """Менеджер алертов"""

    def __init__(self):
        self.rules: List[AlertRule] = []
        self.alerts: List[Alert] = []
        self.last_alert_time: Dict[str, datetime] = {}
        self.logger = logging.getLogger(__name__)

    def add_rule(self, rule: AlertRule) -> None:
        """Добавление правила алерта"""
        self.rules.append(rule)
        self.logger.info(f"Правило алерта добавлено: {rule.name}")

    def check_alerts(self, metrics: List[MetricData]) -> List[Alert]:
        """Проверка метрик на соответствие правилам алертов"""
        new_alerts = []

        for metric in metrics:
            for rule in self.rules:
                if not rule.enabled or rule.metric_name != metric.name:
                    continue

                # Проверка cooldown
                rule_key = f"{rule.name}_{metric.name}"
                if rule_key in self.last_alert_time:
                    time_since_last = (
                        datetime.now() - self.last_alert_time[rule_key]
                    ).total_seconds()
                    if time_since_last < rule.cooldown:
                        continue

                # Проверка условия
                if self._evaluate_condition(
                    metric.value, rule.threshold, rule.operator
                ):
                    alert = Alert(
                        id=f"{rule.name}_{int(time.time())}",
                        rule_name=rule.name,
                        metric_name=metric.name,
                        value=metric.value,
                        threshold=rule.threshold,
                        severity=rule.severity,
                        timestamp=datetime.now(),
                        message=f"Метрика {metric.name} = {metric.value} {rule.operator} {rule.threshold}",
                    )

                    new_alerts.append(alert)
                    self.alerts.append(alert)
                    self.last_alert_time[rule_key] = datetime.now()

                    self.logger.warning(f"Алерт сгенерирован: {alert.message}")

        return new_alerts

    def _evaluate_condition(
        self, value: float, threshold: float, operator: str
    ) -> bool:
        """Оценка условия алерта"""
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return abs(value - threshold) < 0.001
        elif operator == "!=":
            return abs(value - threshold) >= 0.001
        else:
            return False

    def get_active_alerts(self) -> List[Alert]:
        """Получение активных алертов"""
        return [alert for alert in self.alerts if not alert.resolved]

    def resolve_alert(self, alert_id: str) -> bool:
        """Разрешение алерта"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                self.logger.info(f"Алерт разрешен: {alert_id}")
                return True
        return False


class MonitorManager:
    """Основной класс менеджера мониторинга"""

    def __init__(self, config: MonitorConfig):
        """Инициализация менеджера мониторинга"""
        self.config = config
        self.collectors: List[MetricCollector] = []
        self.anomaly_detector = AnomalyDetector()
        self.alert_manager = AlertManager()
        self.metrics_history: List[MetricData] = []
        self.is_running = False
        self.logger = logging.getLogger(__name__)

        # Очередь для метрик
        self.metrics_queue = queue.Queue()

    async def initialize(self) -> bool:
        """Инициализация мониторинга"""
        try:
            self.logger.info("Инициализация MonitorManager")

            # Добавляем сборщик системных метрик
            system_collector = SystemMetricCollector()
            self.collectors.append(system_collector)

            # Настраиваем правила алертов
            self._setup_default_alert_rules()

            self.is_running = True

            # Запуск фонового сбора метрик
            asyncio.create_task(self._collect_metrics_loop())

            self.logger.info("MonitorManager инициализирован успешно")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка инициализации MonitorManager: {e}")
            return False

    def _setup_default_alert_rules(self) -> None:
        """Настройка правил алертов по умолчанию"""
        rules = [
            AlertRule(
                name="high_cpu_usage",
                metric_name="cpu_usage",
                threshold=self.config.cpu_threshold,
                operator=">",
                severity=AlertSeverity.HIGH,
            ),
            AlertRule(
                name="high_memory_usage",
                metric_name="memory_usage",
                threshold=self.config.memory_threshold,
                operator=">",
                severity=AlertSeverity.HIGH,
            ),
            AlertRule(
                name="high_disk_usage",
                metric_name="disk_usage",
                threshold=self.config.disk_threshold,
                operator=">",
                severity=AlertSeverity.CRITICAL,
            ),
        ]

        for rule in rules:
            self.alert_manager.add_rule(rule)

    async def _collect_metrics_loop(self) -> None:
        """Цикл сбора метрик"""
        while self.is_running:
            try:
                # Сбор метрик от всех сборщиков
                all_metrics = []
                for collector in self.collectors:
                    metrics = await collector.collect()
                    all_metrics.extend(metrics)

                # Добавление в историю
                self.metrics_history.extend(all_metrics)

                # Ограничение размера истории
                if len(self.metrics_history) > 10000:
                    self.metrics_history = self.metrics_history[-5000:]

                # Проверка алертов
                if self.config.alerting_enabled:
                    new_alerts = self.alert_manager.check_alerts(all_metrics)
                    if new_alerts:
                        self.logger.warning(
                            f"Сгенерировано {len(new_alerts)} новых алертов"
                        )

                # Детекция аномалий
                if (
                    self.config.anomaly_detection_enabled
                    and len(all_metrics) > 0
                ):
                    await self._check_anomalies(all_metrics)

                await asyncio.sleep(self.config.collection_interval)

            except Exception as e:
                self.logger.error(f"Ошибка в цикле сбора метрик: {e}")
                await asyncio.sleep(5)

    async def _check_anomalies(self, metrics: List[MetricData]) -> None:
        """Проверка аномалий в метриках"""
        try:
            # Подготовка данных для детекции аномалий
            target_metrics = ["cpu_usage", "memory_usage", "disk_usage"]
            metric_values = [
                m.value for m in metrics if m.name in target_metrics
            ]

            if len(metric_values) < 3:
                return

            # Обучение модели на исторических данных
            if (
                not self.anomaly_detector.is_trained
                and len(self.metrics_history) > 50
            ):
                historical_data = []
                for metric in self.metrics_history[-50:]:
                    if metric.name in target_metrics:
                        historical_data.append([metric.value])

                if len(historical_data) >= 10:
                    await self.anomaly_detector.train(historical_data)

            # Детекция аномалий
            if self.anomaly_detector.is_trained:
                is_anomaly, score = (
                    await self.anomaly_detector.detect_anomalies(metric_values)
                )
                if is_anomaly:
                    self.logger.warning(
                        f"Обнаружена аномалия! Score: {score:.3f}"
                    )

        except Exception as e:
            self.logger.error(f"Ошибка проверки аномалий: {e}")

    async def get_metrics(
        self, metric_name: Optional[str] = None, limit: int = 100
    ) -> List[MetricData]:
        """Получение метрик"""
        try:
            if metric_name:
                filtered_metrics = [
                    m for m in self.metrics_history if m.name == metric_name
                ]
            else:
                filtered_metrics = self.metrics_history

            if limit > 0:
                return filtered_metrics[-limit:]
            else:
                return filtered_metrics

        except Exception as e:
            self.logger.error(f"Ошибка получения метрик: {e}")
            return []

    async def get_alerts(
        self, severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """Получение алертов"""
        try:
            alerts = self.alert_manager.get_active_alerts()

            if severity:
                alerts = [
                    alert for alert in alerts if alert.severity == severity
                ]

            return alerts

        except Exception as e:
            self.logger.error(f"Ошибка получения алертов: {e}")
            return []

    async def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        try:
            # Получение последних метрик
            recent_metrics = await self.get_metrics(limit=10)

            # Анализ статуса
            status_counts = {}
            for metric in recent_metrics:
                status = metric.status.value
                status_counts[status] = status_counts.get(status, 0) + 1

            # Определение общего статуса
            if status_counts.get("critical", 0) > 0:
                overall_status = "critical"
            elif status_counts.get("warning", 0) > 0:
                overall_status = "warning"
            else:
                overall_status = "healthy"

            # Получение алертов
            active_alerts = await self.get_alerts()

            return {
                "overall_status": overall_status,
                "status_counts": status_counts,
                "active_alerts_count": len(active_alerts),
                "metrics_count": len(self.metrics_history),
                "last_update": datetime.now().isoformat(),
                "collectors_count": len(self.collectors),
                "anomaly_detection_enabled": (
                    self.config.anomaly_detection_enabled
                ),
                "alerting_enabled": self.config.alerting_enabled,
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса системы: {e}")
            return {"overall_status": "unknown", "error": str(e)}

    async def add_collector(self, collector: MetricCollector) -> None:
        """Добавление сборщика метрик"""
        self.collectors.append(collector)
        self.logger.info(
            f"Сборщик метрик добавлен: {type(collector).__name__}"
        )

    async def add_alert_rule(self, rule: AlertRule) -> None:
        """Добавление правила алерта"""
        self.alert_manager.add_rule(rule)
        self.logger.info(f"Правило алерта добавлено: {rule.name}")

    async def resolve_alert(self, alert_id: str) -> bool:
        """Разрешение алерта"""
        return self.alert_manager.resolve_alert(alert_id)

    async def shutdown(self) -> None:
        """Завершение работы мониторинга"""
        try:
            self.is_running = False
            self.logger.info("MonitorManager завершил работу")
        except Exception as e:
            self.logger.error(f"Ошибка завершения работы: {e}")


# Пример использования
async def main():
    """Пример использования MonitorManager"""
    # Создаем конфигурацию
    config = MonitorConfig(
        collection_interval=30,
        retention_days=30,
        anomaly_detection_enabled=True,
        alerting_enabled=True,
        cpu_threshold=80.0,
        memory_threshold=85.0,
        disk_threshold=90.0,
    )

    # Создаем менеджер мониторинга
    manager = MonitorManager(config)

    # Инициализация
    await manager.initialize()

    # Получение статуса системы
    status = await manager.get_system_status()
    print(f"Статус системы: {status['overall_status']}")
    print(f"Активных алертов: {status['active_alerts_count']}")

    # Получение метрик
    metrics = await manager.get_metrics(limit=5)
    print(f"Получено метрик: {len(metrics)}")

    # Получение алертов
    alerts = await manager.get_alerts()
    print(f"Активных алертов: {len(alerts)}")

    # Завершение работы
    await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
