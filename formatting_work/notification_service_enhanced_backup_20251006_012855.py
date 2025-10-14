# -*- coding: utf-8 -*-
"""
Сервис уведомлений для ParentalControlBot
Версия: 2.5
Дата: 2025-09-21
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from security.bots.parental_control_bot import ActivityAlert, AlertData


class NotificationChannel(Enum):
    """Каналы уведомлений"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationPriority(Enum):
    """Приоритет уведомлений"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class NotificationTemplate:
    """Шаблон уведомления"""
    template_id: str
    subject: str
    message: str
    channel: NotificationChannel
    priority: NotificationPriority
    variables: List[str] = None  # Переменные для подстановки

    def __post_init__(self):
        if self.variables is None:
            self.variables = []


@dataclass
class NotificationStats:
    """Статистика уведомлений"""
    total_sent: int = 0
    sent_by_channel: Dict[str, int] = None
    sent_by_priority: Dict[str, int] = None
    failed_deliveries: int = 0

    def __post_init__(self):
        if self.sent_by_channel is None:
            self.sent_by_channel = {}
        if self.sent_by_priority is None:
            self.sent_by_priority = {}


class NotificationService:
    """Сервис уведомлений"""

    def __init__(self, logger: logging.Logger, redis_client=None):
        self.logger = logger
        self.redis_client = redis_client
        self.stats = NotificationStats()
        self.templates: Dict[str, NotificationTemplate] = {}
        self._lock = asyncio.Lock()

        # Инициализация шаблонов по умолчанию
        self._init_default_templates()

    def _init_default_templates(self):
        """Инициализация шаблонов по умолчанию"""
        templates = [
            NotificationTemplate(
                template_id="time_violation",
                subject="Нарушение лимита времени",
                message="Ребенок {child_name} превысил лимит времени использования "
                        "{device_type} на {excess_minutes} минут.",
                channel=NotificationChannel.EMAIL,
                priority=NotificationPriority.MEDIUM,
                variables=["child_name", "device_type", "excess_minutes"]
            ),
            NotificationTemplate(
                template_id="content_blocked",
                subject="Контент заблокирован",
                message="Доступ к {url} был заблокирован для {child_name}. Причина: {reason}.",
                channel=NotificationChannel.PUSH,
                priority=NotificationPriority.LOW,
                variables=["url", "child_name", "reason"]
            ),
            NotificationTemplate(
                template_id="suspicious_activity",
                subject="Подозрительная активность",
                message="Обнаружена подозрительная активность у {child_name}: {activity_description}.",
                channel=NotificationChannel.SMS,
                priority=NotificationPriority.HIGH,
                variables=["child_name", "activity_description"]
            ),
            NotificationTemplate(
                template_id="emergency_alert",
                subject="ЭКСТРЕННОЕ УВЕДОМЛЕНИЕ",
                message="ЭКСТРЕННОЕ УВЕДОМЛЕНИЕ: {child_name} - {emergency_message}",
                channel=NotificationChannel.SMS,
                priority=NotificationPriority.CRITICAL,
                variables=["child_name", "emergency_message"]
            )
        ]

        for template in templates:
            self.templates[template.template_id] = template

    async def send_alert(self, alert: ActivityAlert, parent_contact: str = None) -> bool:
        """Отправка алерта родителям"""
        try:
            async with self._lock:
                # Определение шаблона по типу алерта
                template_id = self._get_template_id(alert.alert_type)
                template = self.templates.get(template_id)

                if not template:
                    self.logger.warning(f"Шаблон не найден для типа алерта: {alert.alert_type}")
                    return False

                # Подготовка данных для шаблона
                template_data = self._prepare_template_data(alert, template)

                # Отправка уведомления
                success = await self._send_notification(
                    template, template_data, parent_contact, alert
                )

                if success:
                    self._update_stats(template.channel, template.priority)
                    self.logger.info(f"Уведомление отправлено: {alert.alert_type}")
                else:
                    self.stats.failed_deliveries += 1
                    self.logger.error(f"Не удалось отправить уведомление: {alert.alert_type}")

                return success

        except Exception as e:
            self.logger.error(f"Ошибка отправки алерта: {e}")
            return False

    async def send_custom_notification(
        self,
        template_id: str,
        data: Dict[str, Any],
        parent_contact: str = None,
        channel: NotificationChannel = None
    ) -> bool:
        """Отправка пользовательского уведомления"""
        try:
            async with self._lock:
                template = self.templates.get(template_id)
                if not template:
                    self.logger.error(f"Шаблон не найден: {template_id}")
                    return False

                # Переопределение канала если указан
                if channel:
                    template = NotificationTemplate(
                        template_id=template.template_id,
                        subject=template.subject,
                        message=template.message,
                        channel=channel,
                        priority=template.priority,
                        variables=template.variables
                    )

                success = await self._send_notification(template, data, parent_contact)

                if success:
                    self._update_stats(template.channel, template.priority)

                return success

        except Exception as e:
            self.logger.error(f"Ошибка отправки пользовательского уведомления: {e}")
            return False

    def _get_template_id(self, alert_type: str) -> str:
        """Получение ID шаблона по типу алерта"""
        template_mapping = {
            "time_violation": "time_violation",
            "content_blocked": "content_blocked",
            "suspicious_activity": "suspicious_activity",
            "emergency": "emergency_alert",
            "location_alert": "suspicious_activity"
        }
        return template_mapping.get(alert_type, "content_blocked")

    def _prepare_template_data(self, alert: ActivityAlert, template: NotificationTemplate) -> Dict[str, Any]:
        """Подготовка данных для шаблона"""
        data = {
            "child_name": f"Ребенок {alert.child_id}",
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "action_required": alert.action_required
        }

        # Добавление данных из алерта
        if alert.data:
            data.update(alert.data)

        return data

    async def _send_notification(
        self,
        template: NotificationTemplate,
        data: Dict[str, Any],
        parent_contact: str = None,
        alert: ActivityAlert = None
    ) -> bool:
        """Отправка уведомления через выбранный канал"""
        try:
            # Форматирование сообщения
            subject = self._format_message(template.subject, data)
            message = self._format_message(template.message, data)

            if template.channel == NotificationChannel.EMAIL:
                return await self._send_email(subject, message, parent_contact)
            elif template.channel == NotificationChannel.SMS:
                return await self._send_sms(message, parent_contact)
            elif template.channel == NotificationChannel.PUSH:
                return await self._send_push(subject, message, parent_contact)
            elif template.channel == NotificationChannel.IN_APP:
                return await self._send_in_app(subject, message, alert)
            elif template.channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(data, parent_contact)
            else:
                self.logger.error(f"Неподдерживаемый канал: {template.channel}")
                return False

        except Exception as e:
            self.logger.error(f"Ошибка отправки уведомления: {e}")
            return False

    def _format_message(self, template: str, data: Dict[str, Any]) -> str:
        """Форматирование сообщения с подстановкой переменных"""
        try:
            return template.format(**data)
        except KeyError as e:
            self.logger.warning(f"Отсутствует переменная в шаблоне: {e}")
            return template
        except Exception as e:
            self.logger.error(f"Ошибка форматирования сообщения: {e}")
            return template

    async def _send_email(self, subject: str, message: str, parent_contact: str) -> bool:
        """Отправка email уведомления"""
        # Здесь должна быть интеграция с email сервисом
        self.logger.info(f"EMAIL: {subject} -> {parent_contact}")
        return True  # Заглушка

    async def _send_sms(self, message: str, parent_contact: str) -> bool:
        """Отправка SMS уведомления"""
        # Здесь должна быть интеграция с SMS сервисом
        self.logger.info(f"SMS: {message} -> {parent_contact}")
        return True  # Заглушка

    async def _send_push(self, subject: str, message: str, parent_contact: str) -> bool:
        """Отправка push уведомления"""
        # Здесь должна быть интеграция с push сервисом
        self.logger.info(f"PUSH: {subject} -> {parent_contact}")
        return True  # Заглушка

    async def _send_in_app(self, subject: str, message: str, alert: ActivityAlert) -> bool:
        """Отправка внутриприложенческого уведомления"""
        try:
            # Сохранение в Redis для внутриприложенческих уведомлений
            if self.redis_client and alert:
                notification_data = {
                    "child_id": alert.child_id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "subject": subject,
                    "message": message,
                    "timestamp": alert.timestamp.isoformat(),
                    "action_required": alert.action_required,
                    "data": alert.data,
                }

                self.redis_client.lpush(
                    "parental_alerts",
                    json.dumps(notification_data, ensure_ascii=False)
                )

                self.logger.info(f"IN_APP: {subject} -> Redis")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Ошибка отправки внутриприложенческого уведомления: {e}")
            return False

    async def _send_webhook(self, data: Dict[str, Any], parent_contact: str) -> bool:
        """Отправка webhook уведомления"""
        # Здесь должна быть интеграция с webhook сервисом
        self.logger.info(f"WEBHOOK: {data} -> {parent_contact}")
        return True  # Заглушка

    def _update_stats(self, channel: NotificationChannel, priority: NotificationPriority):
        """Обновление статистики"""
        self.stats.total_sent += 1

        channel_name = channel.value
        self.stats.sent_by_channel[channel_name] = \
            self.stats.sent_by_channel.get(channel_name, 0) + 1

        priority_name = priority.value
        self.stats.sent_by_priority[priority_name] = \
            self.stats.sent_by_priority.get(priority_name, 0) + 1

    async def add_template(self, template: NotificationTemplate) -> bool:
        """Добавление пользовательского шаблона"""
        try:
            async with self._lock:
                self.templates[template.template_id] = template
                self.logger.info(f"Добавлен шаблон: {template.template_id}")
                return True
        except Exception as e:
            self.logger.error(f"Ошибка добавления шаблона: {e}")
            return False

    async def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Получение шаблона"""
        return self.templates.get(template_id)

    async def get_stats(self) -> NotificationStats:
        """Получение статистики"""
        return self.stats

    async def validate_alert_data(self, alert_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Валидация данных алерта"""
        try:
            AlertData(**alert_data)
            return True, None
        except Exception as e:
            return False, str(e)

    async def get_notification_history(self, child_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Получение истории уведомлений"""
        try:
            if not self.redis_client:
                return []

            # Получение из Redis
            alerts_data = self.redis_client.lrange("parental_alerts", 0, limit - 1)
            alerts = []

            for alert_json in alerts_data:
                try:
                    alert_data = json.loads(alert_json)
                    if alert_data.get("child_id") == child_id:
                        alerts.append(alert_data)
                except json.JSONDecodeError:
                    continue

            return alerts

        except Exception as e:
            self.logger.error(f"Ошибка получения истории уведомлений: {e}")
            return []
