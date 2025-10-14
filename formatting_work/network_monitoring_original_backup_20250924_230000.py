# -*- coding: utf-8 -*-
"""
ALADDIN Security System - NetworkMonitoring
Мониторинг сети - КРИТИЧНО

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-12
"""

import time
import datetime
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque

# Путь к файлу конфигурации мониторинга
NETWORK_MONITORING_CONFIG = "data/network/monitoring_config.json"

class NetworkStatus(Enum):
    """Статус сети"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    DOWN = "down"

class AlertLevel(Enum):
    """Уровень предупреждения"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class NetworkMetric:
    """
    Представляет метрику сети.
    """
    metric_name: str
    value: float
    unit: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    device_id: Optional[str] = None
    interface: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp,
            "device_id": self.device_id,
            "interface": self.interface
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkMetric':
        return cls(
            metric_name=data["metric_name"],
            value=data["value"],
            unit=data["unit"],
            timestamp=data.get("timestamp", datetime.datetime.now().isoformat()),
            device_id=data.get("device_id"),
            interface=data.get("interface")
        )

@dataclass
class NetworkAlert:
    """
    Представляет предупреждение сети.
    """
    alert_id: str
    alert_type: str
    level: AlertLevel
    message: str
    device_id: Optional[str] = None
    interface: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "level": self.level.value,
            "message": self.message,
            "device_id": self.device_id,
            "interface": self.interface,
            "timestamp": self.timestamp,
            "resolved": self.resolved
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkAlert':
        return cls(
            alert_id=data["alert_id"],
            alert_type=data["alert_type"],
            level=AlertLevel(data["level"]),
            message=data["message"],
            device_id=data.get("device_id"),
            interface=data.get("interface"),
            timestamp=data.get("timestamp", datetime.datetime.now().isoformat()),
            resolved=data.get("resolved", False)
        )

@dataclass
class NetworkDevice:
    """
    Представляет сетевое устройство.
    """
    device_id: str
    name: str
    ip_address: str
    device_type: str  # router, switch, firewall, etc.
    status: NetworkStatus = NetworkStatus.HEALTHY
    last_seen: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    interfaces: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "ip_address": self.ip_address,
            "device_type": self.device_type,
            "status": self.status.value,
            "last_seen": self.last_seen,
            "interfaces": self.interfaces
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkDevice':
        return cls(
            device_id=data["device_id"],
            name=data["name"],
            ip_address=data["ip_address"],
            device_type=data["device_type"],
            status=NetworkStatus(data.get("status", "healthy")),
            last_seen=data.get("last_seen", datetime.datetime.now().isoformat()),
            interfaces=data.get("interfaces", [])
        )

class NetworkMonitoring:
    """
    Модуль для мониторинга сети.
    """
    def __init__(self, config_path: str = NETWORK_MONITORING_CONFIG):
        self.config_path = config_path
        self.devices: Dict[str, NetworkDevice] = {}
        self.metrics: List[NetworkMetric] = []
        self.alerts: List[NetworkAlert] = []
        self.monitoring_rules: List[Dict[str, Any]] = []
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))  # Храним последние 1000 метрик для каждого типа
        self._load_config()

    def _load_config(self):
        """Загружает конфигурацию мониторинга."""
        if not os.path.exists(self.config_path):
            self._create_default_config()
            return
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.monitoring_rules = config.get('rules', [])
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Ошибка загрузки конфигурации мониторинга: {e}")
            self._create_default_config()

    def _create_default_config(self):
        """Создает конфигурацию по умолчанию."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        default_config = {
            "rules": [
                {
                    "name": "High CPU Usage",
                    "metric": "cpu_usage",
                    "threshold": 80.0,
                    "level": "warning"
                },
                {
                    "name": "High Memory Usage",
                    "metric": "memory_usage",
                    "threshold": 85.0,
                    "level": "warning"
                },
                {
                    "name": "Network Latency",
                    "metric": "latency",
                    "threshold": 100.0,
                    "level": "error"
                }
            ]
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)

    def register_device(self, device: NetworkDevice):
        """Регистрирует новое сетевое устройство."""
        self.devices[device.device_id] = device
        print(f"Устройство {device.name} ({device.device_id}) зарегистрировано для мониторинга.")

    def add_metric(self, metric: NetworkMetric):
        """Добавляет новую метрику сети."""
        self.metrics.append(metric)
        self.metrics_history[metric.metric_name].append(metric)
        self._check_alerts(metric)
        print(f"Метрика {metric.metric_name}: {metric.value} {metric.unit}")

    def _check_alerts(self, metric: NetworkMetric):
        """Проверяет метрики на соответствие правилам предупреждений."""
        for rule in self.monitoring_rules:
            if rule.get("metric") == metric.metric_name and metric.value > rule.get("threshold", 0):
                alert = NetworkAlert(
                    alert_id=f"alert-{int(time.time())}-{metric.metric_name}",
                    alert_type=rule["name"],
                    level=AlertLevel(rule.get("level", "warning")),
                    message=f"{rule['name']}: {metric.value} {metric.unit} превышает порог {rule['threshold']}",
                    device_id=metric.device_id,
                    interface=metric.interface
                )
                self.alerts.append(alert)
                print(f"🚨 ПРЕДУПРЕЖДЕНИЕ: {alert.message}")

    def get_device_status(self, device_id: str) -> Optional[NetworkStatus]:
        """Возвращает статус устройства."""
        device = self.devices.get(device_id)
        return device.status if device else None

    def update_device_status(self, device_id: str, status: NetworkStatus):
        """Обновляет статус устройства."""
        if device_id in self.devices:
            self.devices[device_id].status = status
            self.devices[device_id].last_seen = datetime.datetime.now().isoformat()
            print(f"Статус устройства {device_id} обновлен на {status.value}")

    def get_active_alerts(self) -> List[NetworkAlert]:
        """Возвращает список активных предупреждений."""
        return [alert for alert in self.alerts if not alert.resolved]

    def resolve_alert(self, alert_id: str) -> bool:
        """Разрешает предупреждение."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                print(f"Предупреждение {alert_id} разрешено.")
                return True
        return False

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Возвращает сводку метрик."""
        if not self.metrics:
            return {"message": "Нет данных метрик"}
        
        summary = {}
        for metric_name in set(m.value for m in self.metrics):
            metric_values = [m.value for m in self.metrics if m.metric_name == metric_name]
            if metric_values:
                summary[metric_name] = {
                    "count": len(metric_values),
                    "min": min(metric_values),
                    "max": max(metric_values),
                    "avg": sum(metric_values) / len(metric_values),
                    "latest": metric_values[-1]
                }
        return summary

    def get_network_health_score(self) -> float:
        """Вычисляет общий показатель здоровья сети (0-100)."""
        if not self.devices:
            return 0.0
        
        healthy_devices = len([d for d in self.devices.values() if d.status == NetworkStatus.HEALTHY])
        total_devices = len(self.devices)
        
        # Учитываем активные предупреждения
        active_alerts = len(self.get_active_alerts())
        alert_penalty = min(active_alerts * 5, 50)  # Максимальный штраф 50%
        
        base_score = (healthy_devices / total_devices) * 100
        final_score = max(base_score - alert_penalty, 0)
        
        return round(final_score, 2)

    def add_monitoring_rule(self, rule_name: str, metric: str, threshold: float, level: str):
        """Добавляет новое правило мониторинга."""
        new_rule = {
            "name": rule_name,
            "metric": metric,
            "threshold": threshold,
            "level": level
        }
        self.monitoring_rules.append(new_rule)
        self._save_config()
        print(f"Добавлено правило мониторинга: {rule_name}")

    def _save_config(self):
        """Сохраняет конфигурацию."""
        config = {"rules": self.monitoring_rules}
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def get_device_metrics(self, device_id: str, metric_name: Optional[str] = None) -> List[NetworkMetric]:
        """Возвращает метрики для конкретного устройства."""
        device_metrics = [m for m in self.metrics if m.device_id == device_id]
        if metric_name:
            device_metrics = [m for m in device_metrics if m.metric_name == metric_name]
        return device_metrics

    def cleanup_old_metrics(self, hours: int = 24):
        """Очищает старые метрики (старше указанного количества часов)."""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
        cutoff_timestamp = cutoff_time.isoformat()
        
        initial_count = len(self.metrics)
        self.metrics = [m for m in self.metrics if m.timestamp > cutoff_timestamp]
        removed_count = initial_count - len(self.metrics)
        
        if removed_count > 0:
            print(f"Удалено {removed_count} старых метрик (старше {hours} часов)")

    def export_metrics(self, file_path: str):
        """Экспортирует метрики в файл."""
        metrics_data = [m.to_dict() for m in self.metrics]
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(metrics_data, f, indent=4, ensure_ascii=False)
        print(f"Метрики экспортированы в {file_path}")

    def get_network_topology(self) -> Dict[str, Any]:
        """Возвращает топологию сети."""
        topology = {
            "devices": [device.to_dict() for device in self.devices.values()],
            "total_devices": len(self.devices),
            "healthy_devices": len([d for d in self.devices.values() if d.status == NetworkStatus.HEALTHY]),
            "degraded_devices": len([d for d in self.devices.values() if d.status == NetworkStatus.DEGRADED]),
            "critical_devices": len([d for d in self.devices.values() if d.status == NetworkStatus.CRITICAL]),
            "down_devices": len([d for d in self.devices.values() if d.status == NetworkStatus.DOWN])
        }
        return topology