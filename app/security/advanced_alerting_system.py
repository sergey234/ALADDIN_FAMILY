#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расширенная система алертов ALADDIN
Продвинутые уведомления о безопасности

Автор: ALADDIN Security Team
Версия: 2.0
Дата: 2025-09-08
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import requests
import uuid
# Импорт модулей ALADDIN
try:
    from security.core.security_base import ComponentStatus, SecurityLevel
    from security.core.security_base import SecurityBase
except ImportError as e:
    print(f"Предупреждение: Не удалось импортировать модули ALADDIN: {e}")
    ComponentStatus = None
    SecurityLevel = None
    SecurityBase = object


class AlertType(Enum):
    """Типы алертов"""

    SECURITY_THREAT = "security_threat"
    PERFORMANCE_ISSUE = "performance_issue"
    SYSTEM_ERROR = "system_error"
    COMPLIANCE_VIOLATION = "compliance_violation"
    USER_ACTIVITY = "user_activity"
    MAINTENANCE = "maintenance"
    BACKUP = "backup"
    INTEGRATION = "integration"


class AlertSeverity(Enum):
    """Уровни критичности алертов"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Каналы уведомлений"""

    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"
    LOG = "log"


@dataclass
class AlertRule:
    """Правило для генерации алертов"""

    name: str
    description: str
    alert_type: AlertType
    severity: AlertSeverity
    condition: str  # Python expression
    channels: List[AlertChannel]
    cooldown: int = 300  # секунды
    enabled: bool = True


@dataclass
class Alert:
    """Алерт"""

    id: str
    rule_name: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime
    metadata: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class AdvancedAlertingSystem(SecurityBase):
    """Расширенная система алертов"""

    def __init__(self):
        super().__init__("AdvancedAlertingSystem")
        self.status = ComponentStatus.RUNNING if ComponentStatus else "RUNNING"
        self.security_level = SecurityLevel.HIGH if SecurityLevel else "HIGH"

        # Конфигурация
        self.config = {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_email": "aladdin@security.local",
            },
            "webhook": {
                "url": "http://localhost:5000/api/alerts/webhook",
                "timeout": 10,
            },
            "sms": {
                "api_url": "https://api.sms.ru/sms/send",
                "api_id": "",
                "timeout": 10,
            },
        }

        # Правила алертов
        self.alert_rules = self._initialize_alert_rules()

        # История алертов
        self.alert_history: List[Alert] = []

        # Активные алерты
        self.active_alerts: Dict[str, Alert] = {}

        # Последние срабатывания правил
        self.last_triggered: Dict[str, datetime] = {}

        # Логгер
        self.logger = logging.getLogger(__name__)

        print("✅ AdvancedAlertingSystem инициализирован")

    def _initialize_alert_rules(self) -> List[AlertRule]:
        """Инициализация правил алертов"""
        rules = [
            # Критические угрозы безопасности
            AlertRule(
                name="critical_security_threat",
                description="Критическая угроза безопасности",
                alert_type=AlertType.SECURITY_THREAT,
                severity=AlertSeverity.CRITICAL,
                condition="metadata.get('threat_level') == 'critical'",
                channels=[
                    AlertChannel.EMAIL,
                    AlertChannel.SMS,
                    AlertChannel.WEBHOOK,
                    AlertChannel.DASHBOARD,
                ],
                cooldown=60,
            ),
            # Высокая загрузка CPU
            AlertRule(
                name="high_cpu_usage",
                description="Высокая загрузка процессора",
                alert_type=AlertType.PERFORMANCE_ISSUE,
                severity=AlertSeverity.HIGH,
                condition="metadata.get('cpu_usage', 0) > 90",
                channels=[AlertChannel.EMAIL, AlertChannel.DASHBOARD],
                cooldown=300,
            ),
            # Недостаток памяти
            AlertRule(
                name="low_memory",
                description="Недостаток оперативной памяти",
                alert_type=AlertType.PERFORMANCE_ISSUE,
                severity=AlertSeverity.MEDIUM,
                condition="metadata.get('memory_usage', 0) > 85",
                channels=[AlertChannel.EMAIL, AlertChannel.DASHBOARD],
                cooldown=600,
            ),
            # Ошибки системы
            AlertRule(
                name="system_errors",
                description="Критические ошибки системы",
                alert_type=AlertType.SYSTEM_ERROR,
                severity=AlertSeverity.HIGH,
                condition="metadata.get('error_count', 0) > 10",
                channels=[
                    AlertChannel.EMAIL,
                    AlertChannel.WEBHOOK,
                    AlertChannel.DASHBOARD,
                ],
                cooldown=180,
            ),
            # Нарушения соответствия
            AlertRule(
                name="compliance_violation",
                description="Нарушение требований соответствия",
                alert_type=AlertType.COMPLIANCE_VIOLATION,
                severity=AlertSeverity.HIGH,
                condition="metadata.get('compliance_score', 100) < 80",
                channels=[AlertChannel.EMAIL, AlertChannel.DASHBOARD],
                cooldown=900,
            ),
            # Подозрительная активность пользователей
            AlertRule(
                name="suspicious_user_activity",
                description="Подозрительная активность пользователей",
                alert_type=AlertType.USER_ACTIVITY,
                severity=AlertSeverity.MEDIUM,
                condition="metadata.get('suspicious_activity', False)",
                channels=[AlertChannel.EMAIL, AlertChannel.DASHBOARD],
                cooldown=600,
            ),
            # Проблемы с резервным копированием
            AlertRule(
                name="backup_failure",
                description="Ошибка резервного копирования",
                alert_type=AlertType.BACKUP,
                severity=AlertSeverity.HIGH,
                condition="metadata.get('backup_status') == 'failed'",
                channels=[AlertChannel.EMAIL, AlertChannel.DASHBOARD],
                cooldown=1800,
            ),
            # Проблемы с интеграциями
            AlertRule(
                name="integration_failure",
                description="Ошибка интеграции с внешними сервисами",
                alert_type=AlertType.INTEGRATION,
                severity=AlertSeverity.MEDIUM,
                condition="metadata.get('integration_status') == 'failed'",
                channels=[AlertChannel.EMAIL, AlertChannel.DASHBOARD],
                cooldown=1200,
            ),
        ]

        return rules

    def check_alerts(self, data: Dict[str, Any]) -> List[Alert]:
        """Проверка данных на соответствие правилам алертов"""
        triggered_alerts = []

        for rule in self.alert_rules:
            if not rule.enabled:
                continue

            # Проверка cooldown
            if rule.name in self.last_triggered:
                time_since_last = (
                    datetime.now() - self.last_triggered[rule.name]
                ).total_seconds()
                if time_since_last < rule.cooldown:
                    continue

            # Проверка условия
            try:
                if eval(
                    rule.condition, {"metadata": data, "datetime": datetime}
                ):
                    alert = self._create_alert(rule, data)
                    triggered_alerts.append(alert)
                    self.last_triggered[rule.name] = datetime.now()
            except Exception as e:
                self.logger.error(
                    f"Ошибка при проверке правила {rule.name}: {e}"
                )

        return triggered_alerts

    def _create_alert(self, rule: AlertRule, data: Dict[str, Any]) -> Alert:
        """Создание алерта"""
        alert_id = f"{rule.name}_{int(time.time())}"

        alert = Alert(
            id=alert_id,
            rule_name=rule.name,
            alert_type=rule.alert_type,
            severity=rule.severity,
            title=f"🚨 {rule.description}",
            message=self._generate_alert_message(rule, data),
            timestamp=datetime.now(),
            metadata=data,
        )

        # Добавляем в историю
        self.alert_history.append(alert)
        self.active_alerts[alert_id] = alert

        # Отправляем уведомления
        self._send_notifications(alert, rule.channels)

        return alert

    def _generate_alert_message(
        self, rule: AlertRule, data: Dict[str, Any]
    ) -> str:
        """Генерация сообщения алерта"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = f"""
🚨 АЛЕРТ БЕЗОПАСНОСТИ ALADDIN
═══════════════════════════════════════

📋 Описание: {rule.description}
🔴 Критичность: {rule.severity.value.upper()}
📅 Время: {timestamp}
🏷️ Тип: {rule.alert_type.value}

📊 Данные:
{json.dumps(data, indent=2, ensure_ascii=False)}

🛡️ Система: ALADDIN Security Platform
🔧 Версия: 2.0
        """

        return message.strip()

    def _send_notifications(self, alert: Alert, channels: List[AlertChannel]):
        """Отправка уведомлений по каналам"""
        for channel in channels:
            try:
                if channel == AlertChannel.EMAIL:
                    self._send_email(alert)
                elif channel == AlertChannel.SMS:
                    self._send_sms(alert)
                elif channel == AlertChannel.WEBHOOK:
                    self._send_webhook(alert)
                elif channel == AlertChannel.DASHBOARD:
                    self._send_to_dashboard(alert)
                elif channel == AlertChannel.LOG:
                    self._log_alert(alert)
            except Exception as e:
                self.logger.error(
                    f"Ошибка отправки уведомления через {channel.value}: {e}"
                )

    def _send_email(self, alert: Alert):
        """Отправка email уведомления"""
        # Заглушка для email
        self.logger.info(f"📧 Email алерт отправлен: {alert.title}")

    def _send_sms(self, alert: Alert):
        """Отправка SMS уведомления"""
        # Заглушка для SMS
        self.logger.info(f"📱 SMS алерт отправлен: {alert.title}")

    def _send_webhook(self, alert: Alert):
        """Отправка webhook уведомления"""
        try:
            webhook_data = {
                "alert_id": alert.id,
                "title": alert.title,
                "message": alert.message,
                "severity": alert.severity.value,
                "timestamp": alert.timestamp.isoformat(),
                "metadata": alert.metadata,
            }

            response = requests.post(
                self.config["webhook"]["url"],
                json=webhook_data,
                timeout=self.config["webhook"]["timeout"],
            )

            if response.status_code == 200:
                self.logger.info(f"🔗 Webhook алерт отправлен: {alert.title}")
            else:
                self.logger.error(f"Ошибка webhook: {response.status_code}")

        except Exception as e:
            self.logger.error(f"Ошибка отправки webhook: {e}")

    def _send_to_dashboard(self, alert: Alert):
        """Отправка алерта в дашборд"""
        # Алерт уже в active_alerts, дашборд может его получить
        self.logger.info(f"📊 Алерт отправлен в дашборд: {alert.title}")

    def _log_alert(self, alert: Alert):
        """Логирование алерта"""
        self.logger.warning(f"🚨 АЛЕРТ: {alert.title} - {alert.message}")

    def resolve_alert(self, alert_id: str) -> bool:
        """Разрешение алерта"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            del self.active_alerts[alert_id]
            self.logger.info(f"✅ Алерт разрешен: {alert.title}")
            return True
        return False

    def get_active_alerts(self) -> List[Alert]:
        """Получение активных алертов"""
        return list(self.active_alerts.values())

    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Получение истории алертов"""
        return self.alert_history[-limit:]

    def get_alert_statistics(self) -> Dict[str, Any]:
        """Получение статистики алертов"""
        total_alerts = len(self.alert_history)
        active_alerts = len(self.active_alerts)
        resolved_alerts = total_alerts - active_alerts

        # Статистика по типам
        type_stats = {}
        for alert in self.alert_history:
            alert_type = alert.alert_type.value
            type_stats[alert_type] = type_stats.get(alert_type, 0) + 1

        # Статистика по критичности
        severity_stats = {}
        for alert in self.alert_history:
            severity = alert.severity.value
            severity_stats[severity] = severity_stats.get(severity, 0) + 1

        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "resolved_alerts": resolved_alerts,
            "type_statistics": type_stats,
            "severity_statistics": severity_stats,
            "last_alert": (
                self.alert_history[-1].timestamp.isoformat()
                if self.alert_history
                else None
            ),
        }

    def update_rule(self, rule_name: str, **kwargs) -> bool:
        """Обновление правила алерта"""
        for rule in self.alert_rules:
            if rule.name == rule_name:
                for key, value in kwargs.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                self.logger.info(f"✅ Правило обновлено: {rule_name}")
                return True
        return False

    def add_rule(self, rule: AlertRule) -> bool:
        """Добавление нового правила"""
        self.alert_rules.append(rule)
        self.logger.info(f"✅ Правило добавлено: {rule.name}")
        return True

    def remove_rule(self, rule_name: str) -> bool:
        """Удаление правила"""
        for i, rule in enumerate(self.alert_rules):
            if rule.name == rule_name:
                del self.alert_rules[i]
                self.logger.info(f"✅ Правило удалено: {rule_name}")
                return True
        return False

    def trigger_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        message: str,
        source: str = "system",
    ) -> bool:
        """Создание и отправка алерта"""
        try:
            alert = Alert(
                id=str(uuid.uuid4()),
                alert_type=alert_type,
                severity=severity,
                message=message,
                source=source,
                timestamp=datetime.datetime.now(),
                resolved=False,
            )

            self.active_alerts.append(alert)
            self.logger.info(
                f"🚨 Алерт создан: {alert_type.value} - {message}"
            )
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания алерта: {e}")
            return False

    def get_alerts(self, resolved: bool = None) -> List[Alert]:
        """Получение списка алертов"""
        try:
            if resolved is None:
                return self.active_alerts.copy()
            else:
                return [
                    alert
                    for alert in self.active_alerts
                    if alert.resolved == resolved
                ]
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения алертов: {e}")
            return []

    def send_notification(
        self, channel: AlertChannel, message: str, alert: Alert = None
    ) -> bool:
        """Отправка уведомления через указанный канал"""
        try:
            if channel == AlertChannel.LOG:
                self.logger.info(f"📝 Уведомление: {message}")
            elif channel == AlertChannel.EMAIL:
                # Заглушка для email уведомлений
                self.logger.info(f"📧 Email уведомление: {message}")
            elif channel == AlertChannel.DASHBOARD:
                # Заглушка для dashboard уведомлений
                self.logger.info(f"📊 Dashboard уведомление: {message}")

            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка отправки уведомления: {e}")
            return False

    def create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        message: str,
        source: str = "system",
    ) -> Alert:
        """Создание нового алерта"""
        try:
            alert = Alert(
                id=str(uuid.uuid4()),
                alert_type=alert_type,
                severity=severity,
                message=message,
                source=source,
                timestamp=datetime.datetime.now(),
                resolved=False,
            )
            return alert
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания алерта: {e}")
            return None

    def update_alert(self, alert_id: str, **kwargs) -> bool:
        """Обновление алерта"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                for key, value in kwargs.items():
                    if hasattr(alert, key):
                        setattr(alert, key, value)
                self.logger.info(f"✅ Алерт обновлен: {alert_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления алерта: {e}")
            return False

    def delete_alert(self, alert_id: str) -> bool:
        """Удаление алерта"""
        try:
            if alert_id in self.active_alerts:
                del self.active_alerts[alert_id]
                self.logger.info(f"✅ Алерт удален: {alert_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Ошибка удаления алерта: {e}")
            return False

    def get_alert_by_id(self, alert_id: str) -> Alert:
        """Получение алерта по ID"""
        try:
            return self.active_alerts.get(alert_id)
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения алерта: {e}")
            return None

    def clear_alerts(self) -> bool:
        """Очистка всех алертов"""
        try:
            self.active_alerts.clear()
            self.logger.info("✅ Все алерты очищены")
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка очистки алертов: {e}")
            return False


# Глобальный экземпляр системы алертов
alerting_system = AdvancedAlertingSystem()

if __name__ == "__main__":
    # Тестирование системы алертов
    print("🧪 Тестирование AdvancedAlertingSystem...")

    # Тестовые данные
    test_data = {
        "threat_level": "critical",
        "cpu_usage": 95,
        "memory_usage": 90,
        "error_count": 15,
        "compliance_score": 75,
        "suspicious_activity": True,
        "backup_status": "failed",
        "integration_status": "failed",
    }

    # Проверка алертов
    alerts = alerting_system.check_alerts(test_data)
    print(f"🚨 Сгенерировано алертов: {len(alerts)}")

    for alert in alerts:
        print(f"  - {alert.title} ({alert.severity.value})")

    # Статистика
    stats = alerting_system.get_alert_statistics()
    print(f"📊 Статистика: {stats}")

    print("✅ Тестирование завершено!")
