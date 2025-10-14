#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер уведомлений экстренного реагирования
Применение Single Responsibility принципа
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from security.microservices.emergency_formatters import EmergencyMessageFormatter
from security.ai_agents.emergency_models import (
    EmergencyContact,
    EmergencyEvent,
    EmergencyResponse,
)
from security.ai_agents.emergency_time_utils import EmergencyTimeUtils


class EmergencyNotificationManager:
    """Менеджер уведомлений экстренного реагирования"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.notification_history: List[Dict[str, Any]] = []
        self.notification_channels = {
            "sms": self._send_sms_notification,
            "email": self._send_email_notification,
            "push": self._send_push_notification,
            "call": self._send_call_notification,
        }

    def send_emergency_notification(
        self,
        event: EmergencyEvent,
        contacts: List[EmergencyContact],
        channels: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Отправить уведомление об экстренной ситуации

        Args:
            event: Экстренное событие
            contacts: Список контактов для уведомления
            channels: Каналы уведомления

        Returns:
            Dict[str, Any]: Результат отправки уведомлений
        """
        try:
            if not channels:
                channels = ["sms", "push"]  # Каналы по умолчанию

            results = {
                "event_id": event.event_id,
                "total_contacts": len(contacts),
                "channels_used": channels,
                "successful_notifications": 0,
                "failed_notifications": 0,
                "notification_details": [],
            }

            # Формируем сообщение
            message = EmergencyMessageFormatter.format_emergency_message(event)

            for contact in contacts:
                for channel in channels:
                    try:
                        # Отправляем уведомление
                        success = self._send_notification_to_contact(
                            contact, message, channel, event
                        )

                        if success:
                            results["successful_notifications"] += 1
                        else:
                            results["failed_notifications"] += 1

                        # Записываем детали
                        results["notification_details"].append(
                            {
                                "contact_id": contact.contact_id,
                                "contact_name": contact.name,
                                "channel": channel,
                                "success": success,
                                "timestamp": datetime.now().isoformat(),
                            }
                        )

                    except Exception as e:
                        self.logger.error(f"Ошибка отправки уведомления: {e}")
                        results["failed_notifications"] += 1

            # Сохраняем в историю
            self.notification_history.append(results)

            self.logger.info(
                f"Отправлено уведомлений: "
                f"{results['successful_notifications']}"
            )
            return results

        except Exception as e:
            self.logger.error(f"Ошибка отправки уведомлений: {e}")
            return {"error": str(e)}

    def _send_notification_to_contact(
        self,
        contact: EmergencyContact,
        message: str,
        channel: str,
        event: EmergencyEvent,
    ) -> bool:
        """
        Отправить уведомление конкретному контакту

        Args:
            contact: Контакт
            message: Сообщение
            channel: Канал уведомления
            event: Событие

        Returns:
            bool: True если отправлено успешно
        """
        try:
            if channel not in self.notification_channels:
                self.logger.warning(
                    f"Неизвестный канал уведомления: {channel}"
                )
                return False

            # Проверяем доступность контакта для канала
            if not self._is_contact_available_for_channel(contact, channel):
                self.logger.warning(
                    f"Контакт {contact.name} недоступен для канала {channel}"
                )
                return False

            # Отправляем уведомление
            return self.notification_channels[channel](contact, message, event)

        except Exception as e:
            self.logger.error(f"Ошибка отправки уведомления контакту: {e}")
            return False

    def _is_contact_available_for_channel(
        self, contact: EmergencyContact, channel: str
    ) -> bool:
        """
        Проверить доступность контакта для канала

        Args:
            contact: Контакт
            channel: Канал уведомления

        Returns:
            bool: True если контакт доступен
        """
        if not contact.is_available:
            return False

        if channel == "email" and not contact.email:
            return False

        if channel == "sms" and not contact.phone:
            return False

        return True

    def _send_sms_notification(
        self, contact: EmergencyContact, message: str, event: EmergencyEvent
    ) -> bool:
        """
        Отправить SMS уведомление

        Args:
            contact: Контакт
            message: Сообщение
            event: Событие

        Returns:
            bool: True если отправлено успешно
        """
        try:
            # В реальной системе здесь интеграция с SMS провайдером
            self.logger.info(
                f"SMS отправлено {contact.name} ({contact.phone}): "
                f"{message[:50]}..."
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка отправки SMS: {e}")
            return False

    def _send_email_notification(
        self, contact: EmergencyContact, message: str, event: EmergencyEvent
    ) -> bool:
        """
        Отправить email уведомление

        Args:
            contact: Контакт
            message: Сообщение
            event: Событие

        Returns:
            bool: True если отправлено успешно
        """
        try:
            # В реальной системе здесь интеграция с email провайдером
            self.logger.info(
                f"Email отправлен {contact.name} ({contact.email}): "
                f"{message[:50]}..."
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка отправки email: {e}")
            return False

    def _send_push_notification(
        self, contact: EmergencyContact, message: str, event: EmergencyEvent
    ) -> bool:
        """
        Отправить push уведомление

        Args:
            contact: Контакт
            message: Сообщение
            event: Событие

        Returns:
            bool: True если отправлено успешно
        """
        try:
            # В реальной системе здесь интеграция с push сервисом
            self.logger.info(
                f"Push уведомление отправлено {contact.name}: "
                f"{message[:50]}..."
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка отправки push уведомления: {e}")
            return False

    def _send_call_notification(
        self, contact: EmergencyContact, message: str, event: EmergencyEvent
    ) -> bool:
        """
        Отправить голосовое уведомление

        Args:
            contact: Контакт
            message: Сообщение
            event: Событие

        Returns:
            bool: True если отправлено успешно
        """
        try:
            # В реальной системе здесь интеграция с голосовым сервисом
            self.logger.info(
                f"Голосовое уведомление отправлено {contact.name} "
                f"({contact.phone})"
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка отправки голосового уведомления: {e}")
            return False

    def get_notification_history(
        self, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Получить историю уведомлений

        Args:
            hours: Количество часов назад

        Returns:
            List[Dict[str, Any]]: История уведомлений
        """
        try:
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            return [
                notif
                for notif in self.notification_history
                if datetime.fromisoformat(
                    notif["notification_details"][0]["timestamp"]
                ).timestamp()
                >= cutoff_time
            ]
        except Exception as e:
            self.logger.error(f"Ошибка получения истории уведомлений: {e}")
            return []

    def get_notification_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику уведомлений

        Returns:
            Dict[str, Any]: Статистика уведомлений
        """
        try:
            total_notifications = sum(
                len(notif["notification_details"])
                for notif in self.notification_history
            )
            successful_notifications = sum(
                notif["successful_notifications"]
                for notif in self.notification_history
            )
            failed_notifications = sum(
                notif["failed_notifications"]
                for notif in self.notification_history
            )

            # Статистика по каналам
            channel_stats = {}
            for notif in self.notification_history:
                for detail in notif["notification_details"]:
                    channel = detail["channel"]
                    if channel not in channel_stats:
                        channel_stats[channel] = {"success": 0, "failed": 0}

                    if detail["success"]:
                        channel_stats[channel]["success"] += 1
                    else:
                        channel_stats[channel]["failed"] += 1

            return {
                "total_notifications": total_notifications,
                "successful_notifications": successful_notifications,
                "failed_notifications": failed_notifications,
                "success_rate": (
                    successful_notifications / max(total_notifications, 1)
                )
                * 100,
                "channel_statistics": channel_stats,
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики уведомлений: {e}")
            return {}

    def get_status(self) -> str:
        """Получение статуса менеджера уведомлений"""
        try:
            if hasattr(self, 'is_running') and self.is_running:
                return "running"
            else:
                return "stopped"
        except Exception:
            return "unknown"

    def start_notifications(self) -> bool:
        """Запуск системы уведомлений"""
        try:
            self.is_running = True
            self.logger.info("Система экстренных уведомлений запущена")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка запуска системы уведомлений: {e}")
            return False

    def stop_notifications(self) -> bool:
        """Остановка системы уведомлений"""
        try:
            self.is_running = False
            self.logger.info("Система экстренных уведомлений остановлена")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка остановки системы уведомлений: {e}")
            return False

    def get_manager_info(self) -> Dict[str, Any]:
        """Получение информации о менеджере уведомлений"""
        try:
            return {
                "is_running": getattr(self, 'is_running', False),
                "contacts_count": len(getattr(self, 'contacts', [])),
                "notification_history_count": len(getattr(self, 'notification_history', [])),
                "channels_available": len(getattr(self, 'channels', [])),
                "formatter_available": hasattr(self, 'formatter'),
                "time_utils_available": hasattr(self, 'time_utils'),
                "logger_configured": hasattr(self, 'logger'),
                "max_retries": getattr(self, 'max_retries', 3),
                "retry_delay": getattr(self, 'retry_delay', 1.0),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о менеджере: {e}")
            return {
                "is_running": False,
                "contacts_count": 0,
                "notification_history_count": 0,
                "channels_available": 0,
                "formatter_available": False,
                "time_utils_available": False,
                "logger_configured": False,
                "max_retries": 3,
                "retry_delay": 1.0,
                "error": str(e),
            }
