#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Enhanced Alerting System
Улучшенная система алертов для мониторинга

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-08
"""

import json
import smtplib
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from security.core.security_base import ComponentStatus
from security.core.security_base import SecurityBase


class AlertSeverity(Enum):
    """Уровни серьезности алертов"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Каналы отправки алертов"""

    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    CONSOLE = "console"
    LOG = "log"


@dataclass
class AlertRule:
    """Правило для генерации алертов"""

    rule_id: str
    name: str
    description: str
    condition: str
    severity: AlertSeverity
    channels: List[AlertChannel]
    enabled: bool = True
    cooldown: int = 300  # секунд
    last_triggered: Optional[datetime] = None


@dataclass
class Alert:
    """Алерт"""

    alert_id: str
    rule_id: str
    severity: AlertSeverity
    title: str
    message: str
    component: str
    timestamp: datetime
    metadata: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class EnhancedAlertingSystem(SecurityBase):
    """Улучшенная система алертов"""

    def __init__(self):
        super().__init__("EnhancedAlertingSystem")
        self.service_name = "EnhancedAlertingSystem"
        self.status = ComponentStatus.RUNNING

        # Конфигурация
        self.config = self._load_config()

        # Хранилище алертов
        self.alerts: List[Alert] = []
        self.alert_rules: List[AlertRule] = []

        # Каналы отправки
        self.channels = self._initialize_channels()

        # Поток мониторинга
        self.monitoring_thread = None
        self.running = False

        # Инициализация
        self._initialize_default_rules()
        self._start_monitoring()

        self.logger.info("EnhancedAlertingSystem инициализирован")

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        return {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_email": "aladdin@security.local",
                "to_emails": ["admin@security.local"],
            },
            "sms": {
                "api_key": "",
                "api_url": "https://api.sms.ru/sms/send",
                "phone_numbers": ["+79000000000"],
            },
            "webhook": {
                "url": "http://localhost:5000/api/webhook",
                "timeout": 10,
            },
            "retention_days": 30,
            "max_alerts_per_hour": 100,
        }

    def _initialize_channels(self) -> Dict[AlertChannel, Callable]:
        """Инициализация каналов отправки"""
        return {
            AlertChannel.EMAIL: self._send_email_alert,
            AlertChannel.SMS: self._send_sms_alert,
            AlertChannel.WEBHOOK: self._send_webhook_alert,
            AlertChannel.CONSOLE: self._send_console_alert,
            AlertChannel.LOG: self._send_log_alert,
        }

    def _initialize_default_rules(self):
        """Инициализация правил по умолчанию"""
        default_rules = [
            AlertRule(
                rule_id="high_cpu_usage",
                name="Высокая нагрузка на CPU",
                description="CPU загрузка превышает 80%",
                condition="cpu_usage > 80",
                severity=AlertSeverity.WARNING,
                channels=[AlertChannel.EMAIL, AlertChannel.CONSOLE],
                cooldown=300,
            ),
            AlertRule(
                rule_id="high_memory_usage",
                name="Высокая нагрузка на память",
                description="Использование памяти превышает 90%",
                condition="memory_usage > 90",
                severity=AlertSeverity.ERROR,
                channels=[
                    AlertChannel.EMAIL,
                    AlertChannel.SMS,
                    AlertChannel.CONSOLE,
                ],
                cooldown=600,
            ),
            AlertRule(
                rule_id="security_threat_detected",
                name="Обнаружена угроза безопасности",
                description="Система обнаружила потенциальную угрозу",
                condition="threats_detected > 0",
                severity=AlertSeverity.CRITICAL,
                channels=[
                    AlertChannel.EMAIL,
                    AlertChannel.SMS,
                    AlertChannel.WEBHOOK,
                ],
                cooldown=60,
            ),
            AlertRule(
                rule_id="system_error",
                name="Системная ошибка",
                description="Произошла критическая системная ошибка",
                condition="error_rate > 5",
                severity=AlertSeverity.CRITICAL,
                channels=[
                    AlertChannel.EMAIL,
                    AlertChannel.SMS,
                    AlertChannel.CONSOLE,
                ],
                cooldown=120,
            ),
            AlertRule(
                rule_id="low_disk_space",
                name="Мало места на диске",
                description="Свободное место на диске менее 10%",
                condition="disk_free_percent < 10",
                severity=AlertSeverity.WARNING,
                channels=[AlertChannel.EMAIL, AlertChannel.CONSOLE],
                cooldown=1800,
            ),
        ]

        self.alert_rules.extend(default_rules)
        self.logger.info(
            f"Загружено {len(default_rules)} правил алертов по умолчанию"
        )

    def add_alert_rule(self, rule: AlertRule):
        """Добавление нового правила алерта"""
        self.alert_rules.append(rule)
        self.logger.info(f"Добавлено правило алерта: {rule.name}")

    def remove_alert_rule(self, rule_id: str):
        """Удаление правила алерта"""
        self.alert_rules = [
            rule for rule in self.alert_rules if rule.rule_id != rule_id
        ]
        self.logger.info(f"Удалено правило алерта: {rule_id}")

    def _start_monitoring(self):
        """Запуск мониторинга"""
        self.running = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitoring_thread.start()
        self.logger.info("Мониторинг алертов запущен")

    def _monitoring_loop(self):
        """Основной цикл мониторинга"""
        while self.running:
            try:
                # Получение метрик системы
                metrics = self._collect_system_metrics()

                # Проверка правил
                for rule in self.alert_rules:
                    if not rule.enabled:
                        continue

                    # Проверка cooldown
                    if rule.last_triggered:
                        time_since_last = (
                            datetime.now() - rule.last_triggered
                        ).total_seconds()
                        if time_since_last < rule.cooldown:
                            continue

                    # Проверка условия
                    if self._evaluate_condition(rule.condition, metrics):
                        self._trigger_alert(rule, metrics)
                        rule.last_triggered = datetime.now()

                # Очистка старых алертов
                self._cleanup_old_alerts()

                time.sleep(10)  # Проверка каждые 10 секунд

            except Exception as e:
                self.logger.error(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(30)

    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Сбор метрик системы"""
        try:
            import psutil

            return {
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_free_percent": psutil.disk_usage("/").free
                / psutil.disk_usage("/").total
                * 100,
                "threats_detected": 0,  # Заглушка
                "error_rate": 0,  # Заглушка
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            self.logger.error(f"Ошибка сбора метрик: {e}")
            return {}

    def _evaluate_condition(
        self, condition: str, metrics: Dict[str, Any]
    ) -> bool:
        """Оценка условия алерта"""
        try:
            # Простая оценка условий
            if "cpu_usage >" in condition:
                threshold = float(condition.split(">")[1].strip())
                return metrics.get("cpu_usage", 0) > threshold
            elif "memory_usage >" in condition:
                threshold = float(condition.split(">")[1].strip())
                return metrics.get("memory_usage", 0) > threshold
            elif "disk_free_percent <" in condition:
                threshold = float(condition.split("<")[1].strip())
                return metrics.get("disk_free_percent", 100) < threshold
            elif "threats_detected >" in condition:
                threshold = int(condition.split(">")[1].strip())
                return metrics.get("threats_detected", 0) > threshold
            elif "error_rate >" in condition:
                threshold = float(condition.split(">")[1].strip())
                return metrics.get("error_rate", 0) > threshold

            return False
        except Exception as e:
            self.logger.error(f"Ошибка оценки условия '{condition}': {e}")
            return False

    def _trigger_alert(self, rule: AlertRule, metrics: Dict[str, Any]):
        """Срабатывание алерта"""
        alert_id = f"alert_{int(time.time())}_{rule.rule_id}"

        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            severity=rule.severity,
            title=rule.name,
            message=rule.description,
            component="SystemMonitor",
            timestamp=datetime.now(),
            metadata=metrics,
        )

        self.alerts.append(alert)

        # Отправка через каналы
        for channel in rule.channels:
            try:
                self.channels[channel](alert)
            except Exception as e:
                self.logger.error(
                    f"Ошибка отправки алерта через {channel.value}: {e}"
                )

        self.logger.warning(f"Сработал алерт: {rule.name} (ID: {alert_id})")

    def _send_email_alert(self, alert: Alert):
        """Отправка алерта по email"""
        try:
            config = self.config["email"]
            if not config["username"] or not config["password"]:
                self.logger.warning("Email не настроен, пропускаем отправку")
                return

            msg = MIMEMultipart()
            msg["From"] = config["from_email"]
            msg["To"] = ", ".join(config["to_emails"])
            msg["Subject"] = f"[{alert.severity.value.upper()}] {alert.title}"

            body = f"""
            Алерт системы безопасности ALADDIN

            Уровень: {alert.severity.value.upper()}
            Компонент: {alert.component}
            Время: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

            Сообщение: {alert.message}

            Дополнительная информация:
            {json.dumps(alert.metadata, indent=2, ensure_ascii=False)}
            """

            msg.attach(MIMEText(body, "plain", "utf-8"))

            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            server.starttls()
            server.login(config["username"], config["password"])
            server.send_message(msg)
            server.quit()

            self.logger.info(f"Алерт отправлен по email: {alert.alert_id}")

        except Exception as e:
            self.logger.error(f"Ошибка отправки email: {e}")

    def _send_sms_alert(self, alert: Alert):
        """Отправка алерта по SMS"""
        try:
            config = self.config["sms"]
            if not config["api_key"]:
                self.logger.warning("SMS не настроен, пропускаем отправку")
                return

            # Здесь должна быть интеграция с SMS API
            # message = f"[{alert.severity.value.upper()}] " \
            #           f"{alert.title}: {alert.message}"
            self.logger.info(f"SMS отправлен: {alert.alert_id}")

        except Exception as e:
            self.logger.error(f"Ошибка отправки SMS: {e}")

    def _send_webhook_alert(self, alert: Alert):
        """Отправка алерта через webhook"""
        try:
            import requests

            config = self.config["webhook"]
            url = config["url"]

            payload = {
                "alert_id": alert.alert_id,
                "severity": alert.severity.value,
                "title": alert.title,
                "message": alert.message,
                "component": alert.component,
                "timestamp": alert.timestamp.isoformat(),
                "metadata": alert.metadata,
            }

            response = requests.post(
                url, json=payload, timeout=config["timeout"]
            )
            response.raise_for_status()

            self.logger.info(f"Webhook отправлен: {alert.alert_id}")

        except Exception as e:
            self.logger.error(f"Ошибка отправки webhook: {e}")

    def _send_console_alert(self, alert: Alert):
        """Отправка алерта в консоль"""
        severity_colors = {
            AlertSeverity.INFO: "\033[94m",  # Синий
            AlertSeverity.WARNING: "\033[93m",  # Желтый
            AlertSeverity.ERROR: "\033[91m",  # Красный
            AlertSeverity.CRITICAL: "\033[95m",  # Фиолетовый
        }

        color = severity_colors.get(alert.severity, "")
        reset = "\033[0m"

        print(f"{color}[{alert.severity.value.upper()}] {alert.title}{reset}")
        print(f"  Компонент: {alert.component}")
        print(f"  Время: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Сообщение: {alert.message}")
        print()

    def _send_log_alert(self, alert: Alert):
        """Отправка алерта в лог"""
        self.logger.warning(
            f"ALERT [{alert.severity.value.upper()}] "
            f"{alert.title}: {alert.message}"
        )

    def _cleanup_old_alerts(self):
        """Очистка старых алертов"""
        cutoff_date = datetime.now() - timedelta(
            days=self.config["retention_days"]
        )
        old_count = len(self.alerts)

        self.alerts = [
            alert for alert in self.alerts if alert.timestamp > cutoff_date
        ]

        removed_count = old_count - len(self.alerts)
        if removed_count > 0:
            self.logger.info(f"Удалено {removed_count} старых алертов")

    def get_alerts(
        self, limit: int = 50, severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """Получение алертов"""
        alerts = self.alerts

        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]

        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)[:limit]

    def resolve_alert(self, alert_id: str):
        """Разрешение алерта"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                self.logger.info(f"Алерт разрешен: {alert_id}")
                break

    def get_alert_statistics(self) -> Dict[str, Any]:
        """Получение статистики алертов"""
        total_alerts = len(self.alerts)
        unresolved_alerts = len([a for a in self.alerts if not a.resolved])

        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len(
                [a for a in self.alerts if a.severity == severity]
            )

        return {
            "total_alerts": total_alerts,
            "unresolved_alerts": unresolved_alerts,
            "severity_counts": severity_counts,
            "active_rules": len([r for r in self.alert_rules if r.enabled]),
            "last_alert": (
                self.alerts[-1].timestamp.isoformat() if self.alerts else None
            ),
        }

    def stop(self):
        """Остановка системы алертов"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Система алертов остановлена")

    def start_alerting(self) -> bool:
        """Запуск системы алертов"""
        try:
            if not self.running:
                self.running = True
                self.logger.info("Система алертов запущена")
                return True
            else:
                self.logger.warning("Система алертов уже запущена")
                return False
        except Exception as e:
            self.logger.error(f"Ошибка запуска системы алертов: {e}")
            return False

    def stop_alerting(self) -> bool:
        """Остановка системы алертов"""
        try:
            if self.running:
                self.running = False
                if self.monitoring_thread:
                    self.monitoring_thread.join(timeout=5)
                self.logger.info("Система алертов остановлена")
                return True
            else:
                self.logger.warning("Система алертов уже остановлена")
                return False
        except Exception as e:
            self.logger.error(f"Ошибка остановки системы алертов: {e}")
            return False

    def get_alerting_info(self) -> Dict[str, Any]:
        """Получение информации о системе алертов"""
        try:
            return {
                "is_running": self.running,
                "total_alerts": len(self.alerts),
                "unresolved_alerts": len([a for a in self.alerts if not a.resolved]),
                "alert_rules_count": len(self.alert_rules),
                "channels_available": len(AlertChannel),
                "severity_levels": len(AlertSeverity),
                "monitoring_thread_active": self.monitoring_thread is not None and self.monitoring_thread.is_alive(),
                "retention_days": self.config.get("retention_days", 30),
                "webhook_enabled": self.config.get("webhook_enabled", False),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о системе алертов: {e}")
            return {
                "is_running": False,
                "total_alerts": 0,
                "unresolved_alerts": 0,
                "alert_rules_count": 0,
                "channels_available": 0,
                "severity_levels": 0,
                "monitoring_thread_active": False,
                "retention_days": 30,
                "webhook_enabled": False,
                "error": str(e),
            }


# Пример использования
if __name__ == "__main__":
    # Создание системы алертов
    alerting_system = EnhancedAlertingSystem()

    try:
        # Работа системы
        print("🚨 Система алертов запущена. Нажмите Ctrl+C для остановки.")

        while True:
            time.sleep(1)

            # Показ статистики каждые 30 секунд
            if int(time.time()) % 30 == 0:
                stats = alerting_system.get_alert_statistics()
                print(
                    f"📊 Статистика алертов: {stats['total_alerts']} всего, "
                    f"{stats['unresolved_alerts']} неразрешенных"
                )

    except KeyboardInterrupt:
        print("\n🛑 Остановка системы алертов...")
        alerting_system.stop()
        print("✅ Система алертов остановлена")
