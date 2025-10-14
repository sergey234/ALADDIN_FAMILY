#!/usr/bin/env python3
"""
ALADDIN Security System - Secrets Monitoring
Интеграция SecretsManager с системой мониторинга

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-26
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.security_base import ComponentStatus, SecurityBase
from security.secrets_api import get_secrets_api
from security.secrets_manager import get_secrets_manager


class SecretsMonitoring(SecurityBase):
    """Мониторинг системы секретов"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Инициализация мониторинга"""
        super().__init__("SecretsMonitoring")
        self.config = config or {}
        self.secrets_api = get_secrets_api()
        self.secrets_manager = get_secrets_manager()

        # Настройки мониторинга
        self.monitoring_interval = self.config.get(
            "monitoring_interval", 300
        )  # 5 минут
        self.alert_thresholds = self.config.get(
            "alert_thresholds",
            {
                "expired_secrets": 5,
                "error_rate": 0.1,  # 10%
                "access_frequency": 1000,  # в час
                "rotation_frequency": 10,  # в день
            },
        )

        # Метрики
        self.metrics_history = []
        self.alerts = []
        self.last_check = None

        # Интеграции
        self.integrations = {
            "dashboard": self.config.get("dashboard_integration", True),
            "alerts": self.config.get("alerts_integration", True),
            "logging": self.config.get("logging_integration", True),
        }

        self.log_activity("SecretsMonitoring инициализирован")

    def initialize(self) -> bool:
        """Инициализация мониторинга"""
        try:
            self.log_activity("Инициализация мониторинга секретов...")

            # Проверка доступности API
            if not self.secrets_api or not self.secrets_manager:
                self.log_activity(
                    "SecretsAPI или SecretsManager недоступны", "error"
                )
                return False

            # Инициализация интеграций
            self._initialize_integrations()

            # Первоначальная проверка
            self._perform_health_check()

            self.status = ComponentStatus.RUNNING
            self.log_activity("Мониторинг секретов инициализирован успешно")
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации мониторинга: {e}", "error"
            )
            self.status = ComponentStatus.ERROR
            return False

    def _initialize_integrations(self) -> None:
        """Инициализация интеграций с системой мониторинга"""
        try:
            # Интеграция с дашбордом
            if self.integrations["dashboard"]:
                self._setup_dashboard_integration()

            # Интеграция с системой алертов
            if self.integrations["alerts"]:
                self._setup_alerts_integration()

            # Интеграция с логированием
            if self.integrations["logging"]:
                self._setup_logging_integration()

            self.log_activity("Интеграции мониторинга настроены")

        except Exception as e:
            self.log_activity(f"Ошибка инициализации интеграций: {e}", "error")

    def _setup_dashboard_integration(self) -> None:
        """Настройка интеграции с дашбордом"""
        try:
            # Создание метрик для дашборда
            dashboard_metrics = {
                "secrets_count": 0,
                "active_secrets": 0,
                "expired_secrets": 0,
                "error_rate": 0.0,
                "access_count": 0,
                "rotation_count": 0,
                "external_providers_status": {},
                "last_updated": datetime.now().isoformat(),
            }

            # Сохранение метрик
            self._save_dashboard_metrics(dashboard_metrics)

        except Exception as e:
            self.log_activity(f"Ошибка настройки дашборда: {e}", "error")

    def _setup_alerts_integration(self) -> None:
        """Настройка интеграции с системой алертов"""
        try:
            # Создание правил алертов
            alert_rules = [
                {
                    "name": "expired_secrets_alert",
                    "condition": "expired_secrets > threshold",
                    "threshold": self.alert_thresholds["expired_secrets"],
                    "severity": "warning",
                    "message": "Обнаружены истекшие секреты",
                },
                {
                    "name": "high_error_rate_alert",
                    "condition": "error_rate > threshold",
                    "threshold": self.alert_thresholds["error_rate"],
                    "severity": "critical",
                    "message": "Высокий уровень ошибок в системе секретов",
                },
                {
                    "name": "external_provider_down_alert",
                    "condition": "external_provider_status == False",
                    "severity": "warning",
                    "message": "Внешний провайдер секретов недоступен",
                },
            ]

            # Сохранение правил
            self._save_alert_rules(alert_rules)

        except Exception as e:
            self.log_activity(f"Ошибка настройки алертов: {e}", "error")

    def _setup_logging_integration(self) -> None:
        """Настройка интеграции с логированием"""
        try:
            # Настройка структурированного логирования
            logging_config = {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "level": "INFO",
                "handlers": ["file", "console"],
                "file_path": "logs/secrets_monitoring.log",
            }

            # Сохранение конфигурации
            self._save_logging_config(logging_config)

        except Exception as e:
            self.log_activity(f"Ошибка настройки логирования: {e}", "error")

    def _perform_health_check(self) -> Dict[str, Any]:
        """Выполнение проверки здоровья системы"""
        try:
            # Получение статуса здоровья
            health_status = self.secrets_api.get_health_status()

            if not health_status.get("success"):
                self.log_activity("Ошибка получения статуса здоровья", "error")
                return {
                    "status": "error",
                    "message": "Не удалось получить статус",
                }

            health_data = health_status["health"]

            # Анализ статуса
            overall_status = "healthy"
            issues = []

            if health_data["api_status"] != "running":
                overall_status = "unhealthy"
                issues.append("API не работает")

            if health_data["manager_status"] != "healthy":
                overall_status = "degraded"
                issues.append("Менеджер секретов нездоров")

            if not health_data["storage_writable"]:
                overall_status = "unhealthy"
                issues.append("Хранилище недоступно для записи")

            # Проверка внешних провайдеров
            external_issues = []
            for provider, status in health_data["external_providers"].items():
                if not status:
                    external_issues.append(f"Провайдер {provider} недоступен")

            if external_issues:
                if overall_status == "healthy":
                    overall_status = "degraded"
                issues.extend(external_issues)

            # Создание отчета
            health_report = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": overall_status,
                "api_status": health_data["api_status"],
                "manager_status": health_data["manager_status"],
                "secrets_count": health_data["secrets_count"],
                "external_providers": health_data["external_providers"],
                "storage_writable": health_data["storage_writable"],
                "rotation_active": health_data["rotation_active"],
                "issues": issues,
            }

            # Сохранение отчета
            self._save_health_report(health_report)

            # Проверка алертов
            self._check_alerts(health_report)

            return health_report

        except Exception as e:
            self.log_activity(f"Ошибка проверки здоровья: {e}", "error")
            return {"status": "error", "message": str(e)}

    def _check_alerts(self, health_report: Dict[str, Any]) -> None:
        """Проверка условий для алертов"""
        try:
            # Получение статистики
            stats = self.secrets_api.get_statistics()
            if not stats.get("success"):
                return

            statistics = stats["statistics"]

            # Проверка истекших секретов
            expired_count = statistics.get("expired_secrets", 0)
            if expired_count > self.alert_thresholds["expired_secrets"]:
                self._create_alert(
                    "expired_secrets_alert",
                    "warning",
                    f"Обнаружено {expired_count} истекших секретов",
                    {"expired_count": expired_count},
                )

            # Проверка уровня ошибок
            error_count = statistics.get("manager_metrics", {}).get(
                "error_count", 0
            )
            access_count = statistics.get("total_access_count", 1)
            error_rate = error_count / access_count if access_count > 0 else 0

            if error_rate > self.alert_thresholds["error_rate"]:
                self._create_alert(
                    "high_error_rate_alert",
                    "critical",
                    f"Высокий уровень ошибок: {error_rate:.2%}",
                    {"error_rate": error_rate, "error_count": error_count},
                )

            # Проверка внешних провайдеров
            for provider, status in health_report[
                "external_providers"
            ].items():
                if not status:
                    self._create_alert(
                        "external_provider_down_alert",
                        "warning",
                        f"Внешний провайдер {provider} недоступен",
                        {"provider": provider, "status": status},
                    )

        except Exception as e:
            self.log_activity(f"Ошибка проверки алертов: {e}", "error")

    def _create_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        data: Dict[str, Any],
    ) -> None:
        """Создание алерта"""
        try:
            alert = {
                "id": f"{alert_type}_{int(time.time())}",
                "type": alert_type,
                "severity": severity,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "data": data,
                "acknowledged": False,
                "resolved": False,
            }

            # Добавление алерта
            self.alerts.append(alert)

            # Логирование алерта
            self.log_activity(
                f"АЛЕРТ [{severity.upper()}]: {message}", "warning"
            )

            # Отправка в систему алертов
            self._send_alert(alert)

            # Сохранение алерта
            self._save_alert(alert)

        except Exception as e:
            self.log_activity(f"Ошибка создания алерта: {e}", "error")

    def _send_alert(self, alert: Dict[str, Any]) -> None:
        """Отправка алерта в систему мониторинга"""
        try:
            # Интеграция с внешней системой алертов
            if self.integrations["alerts"]:
                # Здесь может быть интеграция с Prometheus, Grafana, PagerDuty и т.д.
                self._send_to_external_alerting_system(alert)

        except Exception as e:
            self.log_activity(f"Ошибка отправки алерта: {e}", "error")

    def _send_to_external_alerting_system(self, alert: Dict[str, Any]) -> None:
        """Отправка алерта во внешнюю систему"""
        try:
            # Пример интеграции с внешней системой
            # alert_data = {
            #     "source": "aladdin_secrets",
            #     "alert_id": alert["id"],
            #     "severity": alert["severity"],
            #     "message": alert["message"],
            #     "timestamp": alert["timestamp"],
            #     "metadata": alert["data"],
            # }

            # Здесь может быть HTTP запрос к внешней системе
            # requests.post("https://alerts.example.com/api/alerts", json=alert_data)

            self.log_activity(
                f"Алерт отправлен во внешнюю систему: {alert['id']}"
            )

        except Exception as e:
            self.log_activity(
                f"Ошибка отправки во внешнюю систему: {e}", "error"
            )

    def collect_metrics(self) -> Dict[str, Any]:
        """Сбор метрик системы секретов"""
        try:
            # Получение статистики
            stats = self.secrets_api.get_statistics()
            if not stats.get("success"):
                return {}

            statistics = stats["statistics"]

            # Получение статуса здоровья
            health = self.secrets_api.get_health_status()
            health_data = (
                health.get("health", {}) if health.get("success") else {}
            )

            # Сбор метрик
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "secrets": {
                    "total": statistics.get("total_secrets", 0),
                    "active": statistics.get("status_distribution", {}).get(
                        "active", 0
                    ),
                    "expired": statistics.get("expired_secrets", 0),
                    "by_type": statistics.get("type_distribution", {}),
                },
                "performance": {
                    "access_count": statistics.get("total_access_count", 0),
                    "rotation_count": statistics.get(
                        "manager_metrics", {}
                    ).get("rotation_count", 0),
                    "error_count": statistics.get("manager_metrics", {}).get(
                        "error_count", 0
                    ),
                    "error_rate": 0.0,
                },
                "system": {
                    "api_status": health_data.get("api_status", "unknown"),
                    "manager_status": health_data.get(
                        "manager_status", "unknown"
                    ),
                    "storage_writable": health_data.get(
                        "storage_writable", False
                    ),
                    "rotation_active": health_data.get(
                        "rotation_active", False
                    ),
                },
                "external_providers": health_data.get(
                    "external_providers", {}
                ),
                "alerts": {
                    "total": len(self.alerts),
                    "unacknowledged": len(
                        [a for a in self.alerts if not a["acknowledged"]]
                    ),
                    "critical": len(
                        [a for a in self.alerts if a["severity"] == "critical"]
                    ),
                },
            }

            # Расчет уровня ошибок
            if metrics["performance"]["access_count"] > 0:
                metrics["performance"]["error_rate"] = (
                    metrics["performance"]["error_count"]
                    / metrics["performance"]["access_count"]
                )

            # Сохранение метрик
            self.metrics_history.append(metrics)

            # Ограничение истории метрик
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]

            # Обновление дашборда
            if self.integrations["dashboard"]:
                self._update_dashboard_metrics(metrics)

            return metrics

        except Exception as e:
            self.log_activity(f"Ошибка сбора метрик: {e}", "error")
            return {}

    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Получение истории метрик за указанный период"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)

            filtered_metrics = []
            for metrics in self.metrics_history:
                metrics_time = datetime.fromisoformat(metrics["timestamp"])
                if metrics_time >= cutoff_time:
                    filtered_metrics.append(metrics)

            return filtered_metrics

        except Exception as e:
            self.log_activity(f"Ошибка получения истории метрик: {e}", "error")
            return []

    def get_alerts(
        self,
        severity: Optional[str] = None,
        acknowledged: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Получение списка алертов с фильтрацией"""
        try:
            filtered_alerts = self.alerts.copy()

            if severity:
                filtered_alerts = [
                    a for a in filtered_alerts if a["severity"] == severity
                ]

            if acknowledged is not None:
                filtered_alerts = [
                    a
                    for a in filtered_alerts
                    if a["acknowledged"] == acknowledged
                ]

            # Сортировка по времени (новые первыми)
            filtered_alerts.sort(key=lambda x: x["timestamp"], reverse=True)

            return filtered_alerts

        except Exception as e:
            self.log_activity(f"Ошибка получения алертов: {e}", "error")
            return []

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Подтверждение алерта"""
        try:
            for alert in self.alerts:
                if alert["id"] == alert_id:
                    alert["acknowledged"] = True
                    alert["acknowledged_at"] = datetime.now().isoformat()

                    self.log_activity(f"Алерт подтвержден: {alert_id}")
                    self._save_alert(alert)
                    return True

            return False

        except Exception as e:
            self.log_activity(f"Ошибка подтверждения алерта: {e}", "error")
            return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Разрешение алерта"""
        try:
            for alert in self.alerts:
                if alert["id"] == alert_id:
                    alert["resolved"] = True
                    alert["resolved_at"] = datetime.now().isoformat()

                    self.log_activity(f"Алерт разрешен: {alert_id}")
                    self._save_alert(alert)
                    return True

            return False

        except Exception as e:
            self.log_activity(f"Ошибка разрешения алерта: {e}", "error")
            return False

    def _save_dashboard_metrics(self, metrics: Dict[str, Any]) -> None:
        """Сохранение метрик для дашборда"""
        try:
            metrics_file = Path("data/secrets_dashboard_metrics.json")
            metrics_file.parent.mkdir(parents=True, exist_ok=True)

            with open(metrics_file, "w", encoding="utf-8") as f:
                json.dump(metrics, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.log_activity(
                f"Ошибка сохранения метрик дашборда: {e}", "error"
            )

    def _update_dashboard_metrics(self, metrics: Dict[str, Any]) -> None:
        """Обновление метрик дашборда"""
        try:
            dashboard_metrics = {
                "secrets_count": metrics["secrets"]["total"],
                "active_secrets": metrics["secrets"]["active"],
                "expired_secrets": metrics["secrets"]["expired"],
                "error_rate": metrics["performance"]["error_rate"],
                "access_count": metrics["performance"]["access_count"],
                "rotation_count": metrics["performance"]["rotation_count"],
                "external_providers_status": metrics["external_providers"],
                "last_updated": metrics["timestamp"],
            }

            self._save_dashboard_metrics(dashboard_metrics)

        except Exception as e:
            self.log_activity(
                f"Ошибка обновления метрик дашборда: {e}", "error"
            )

    def _save_alert_rules(self, rules: List[Dict[str, Any]]) -> None:
        """Сохранение правил алертов"""
        try:
            rules_file = Path("data/secrets_alert_rules.json")
            rules_file.parent.mkdir(parents=True, exist_ok=True)

            with open(rules_file, "w", encoding="utf-8") as f:
                json.dump(rules, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.log_activity(
                f"Ошибка сохранения правил алертов: {e}", "error"
            )

    def _save_logging_config(self, config: Dict[str, Any]) -> None:
        """Сохранение конфигурации логирования"""
        try:
            config_file = Path("data/secrets_logging_config.json")
            config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.log_activity(
                f"Ошибка сохранения конфигурации логирования: {e}", "error"
            )

    def _save_health_report(self, report: Dict[str, Any]) -> None:
        """Сохранение отчета о здоровье"""
        try:
            report_file = Path("data/secrets_health_report.json")
            report_file.parent.mkdir(parents=True, exist_ok=True)

            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.log_activity(
                f"Ошибка сохранения отчета о здоровье: {e}", "error"
            )

    def _save_alert(self, alert: Dict[str, Any]) -> None:
        """Сохранение алерта"""
        try:
            alerts_file = Path("data/secrets_alerts.json")
            alerts_file.parent.mkdir(parents=True, exist_ok=True)

            # Загрузка существующих алертов
            existing_alerts = []
            if alerts_file.exists():
                with open(alerts_file, "r", encoding="utf-8") as f:
                    existing_alerts = json.load(f)

            # Добавление нового алерта
            existing_alerts.append(alert)

            # Сохранение
            with open(alerts_file, "w", encoding="utf-8") as f:
                json.dump(existing_alerts, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.log_activity(f"Ошибка сохранения алерта: {e}", "error")

    def start_monitoring(self) -> bool:
        """Запуск мониторинга"""
        try:
            self.log_activity("Запуск мониторинга секретов...")

            # Первоначальный сбор метрик
            self.collect_metrics()

            # Запуск периодического мониторинга
            self._start_periodic_monitoring()

            self.log_activity("Мониторинг секретов запущен")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка запуска мониторинга: {e}", "error")
            return False

    def _start_periodic_monitoring(self) -> None:
        """Запуск периодического мониторинга"""
        try:
            import threading

            def monitoring_worker():
                while self.status == ComponentStatus.RUNNING:
                    try:
                        # Сбор метрик
                        self.collect_metrics()

                        # Проверка здоровья
                        self._perform_health_check()

                        # Ожидание следующего цикла
                        time.sleep(self.monitoring_interval)

                    except Exception as e:
                        self.log_activity(
                            f"Ошибка в цикле мониторинга: {e}", "error"
                        )
                        time.sleep(60)  # Пауза при ошибке

            # Запуск в отдельном потоке
            monitoring_thread = threading.Thread(
                target=monitoring_worker, daemon=True
            )
            monitoring_thread.start()

        except Exception as e:
            self.log_activity(
                f"Ошибка запуска периодического мониторинга: {e}", "error"
            )

    def stop(self) -> bool:
        """Остановка мониторинга"""
        try:
            self.log_activity("Остановка мониторинга секретов...")

            self.status = ComponentStatus.STOPPED

            # Финальный сбор метрик
            self.collect_metrics()

            self.log_activity("Мониторинг секретов остановлен")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка остановки мониторинга: {e}", "error")
            return False

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Получение статуса мониторинга"""
        try:
            return {
                "status": self.status.value,
                "monitoring_interval": self.monitoring_interval,
                "last_check": self.last_check,
                "metrics_count": len(self.metrics_history),
                "alerts_count": len(self.alerts),
                "integrations": self.integrations,
                "alert_thresholds": self.alert_thresholds,
            }

        except Exception as e:
            self.log_activity(
                f"Ошибка получения статуса мониторинга: {e}", "error"
            )
            return {"status": "error", "message": str(e)}


# Глобальный экземпляр мониторинга
_secrets_monitoring_instance = None


def get_secrets_monitoring() -> SecretsMonitoring:
    """Получение глобального экземпляра мониторинга секретов"""
    global _secrets_monitoring_instance
    if _secrets_monitoring_instance is None:
        _secrets_monitoring_instance = SecretsMonitoring()
        _secrets_monitoring_instance.initialize()
    return _secrets_monitoring_instance


def initialize_secrets_monitoring(
    config: Optional[Dict[str, Any]] = None
) -> SecretsMonitoring:
    """Инициализация глобального мониторинга секретов"""
    global _secrets_monitoring_instance
    _secrets_monitoring_instance = SecretsMonitoring(config)
    _secrets_monitoring_instance.initialize()
    return _secrets_monitoring_instance


if __name__ == "__main__":
    # Пример использования мониторинга
    config = {
        "monitoring_interval": 60,  # 1 минута
        "alert_thresholds": {
            "expired_secrets": 3,
            "error_rate": 0.05,  # 5%
            "access_frequency": 500,
            "rotation_frequency": 5,
        },
        "dashboard_integration": True,
        "alerts_integration": True,
        "logging_integration": True,
    }

    # Инициализация мониторинга
    monitoring = initialize_secrets_monitoring(config)

    # Запуск мониторинга
    monitoring.start_monitoring()

    # Сбор метрик
    metrics = monitoring.collect_metrics()
    print(f"Метрики: {metrics}")

    # Получение алертов
    alerts = monitoring.get_alerts()
    print(f"Алерты: {alerts}")

    # Статус мониторинга
    status = monitoring.get_monitoring_status()
    print(f"Статус: {status}")

    # Остановка мониторинга
    monitoring.stop()
