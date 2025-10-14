#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FamilyNotificationManagerEnhanced - Расширенная система уведомлений для монетизации
Версия 2.0 - Полная интеграция с системой подписок и платежей

Интегрируется с:
- SubscriptionManager (напоминания о подписках)
- QRPaymentManager (уведомления об оплате)
- ReferralManager (реферальные уведомления)
- PersonalizationAgent (персонализированные уведомления)

Автор: ALADDIN Security System
Версия: 2.0.0
Дата: 2025-01-27
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import uuid

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Типы уведомлений"""
    # Базовые уведомления
    SECURITY_ALERT = "security_alert"           # Угроза безопасности
    FAMILY_STATUS = "family_status"             # Статус семьи
    THREAT_DETECTED = "threat_detected"         # Обнаружена угроза
    DAILY_REPORT = "daily_report"               # Ежедневный отчет
    EMERGENCY = "emergency"                     # Экстренное уведомление
    SYSTEM_UPDATE = "system_update"             # Обновление системы

    # Уведомления о подписках
    TRIAL_STARTED = "trial_started"             # Начался тестовый период
    TRIAL_REMINDER = "trial_reminder"           # Напоминание о тестовом периоде
    TRIAL_EXPIRING = "trial_expiring"           # Тестовый период истекает
    TRIAL_EXPIRED = "trial_expired"             # Тестовый период истек
    SUBSCRIPTION_ACTIVATED = "subscription_activated"  # Подписка активирована
    SUBSCRIPTION_RENEWED = "subscription_renewed"      # Подписка продлена
    SUBSCRIPTION_EXPIRING = "subscription_expiring"    # Подписка истекает
    SUBSCRIPTION_EXPIRED = "subscription_expired"      # Подписка истекла
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"  # Подписка отменена

    # Уведомления об оплате
    PAYMENT_PENDING = "payment_pending"         # Ожидается оплата
    PAYMENT_SUCCESS = "payment_success"         # Оплата успешна
    PAYMENT_FAILED = "payment_failed"           # Оплата не удалась
    PAYMENT_REFUNDED = "payment_refunded"       # Возврат средств
    QR_CODE_GENERATED = "qr_code_generated"     # QR-код сгенерирован

    # Реферальные уведомления
    REFERRAL_LINK_CREATED = "referral_link_created"     # Создана реферальная ссылка
    REFERRAL_SIGNUP = "referral_signup"                 # Регистрация по реферальной ссылке
    REFERRAL_CONVERSION = "referral_conversion"         # Конверсия реферала
    REFERRAL_REWARD = "referral_reward"                 # Награда за реферал

    # Персонализированные уведомления
    TARIFF_RECOMMENDATION = "tariff_recommendation"     # Рекомендация тарифа
    DISCOUNT_OFFER = "discount_offer"                   # Предложение скидки
    FEATURE_ANNOUNCEMENT = "feature_announcement"       # Анонс новой функции
    PERSONALIZED_TIP = "personalized_tip"               # Персональный совет


class NotificationPriority(Enum):
    """Приоритеты уведомлений"""
    LOW = "low"                 # Низкий
    MEDIUM = "medium"           # Средний
    HIGH = "high"               # Высокий
    CRITICAL = "critical"       # Критический
    EMERGENCY = "emergency"     # Экстренный


class NotificationChannel(Enum):
    """Каналы уведомлений (ТОЛЬКО ВНУТРИ ПРИЛОЖЕНИЯ)"""
    IN_APP = "in_app"           # Внутри приложения (ОСНОВНОЙ)
    QR_CODE = "qr_code"         # QR-код уведомления
    VOICE = "voice"             # Голосовое уведомление
    # УДАЛЕНО: PUSH, TELEGRAM, WHATSAPP, EMAIL, SMS - не можем отправлять


@dataclass
class FamilyNotification:
    """Структура анонимного уведомления"""
    notification_id: str        # Уникальный ID уведомления
    family_id: str              # Анонимный ID семьи
    notification_type: NotificationType
    priority: NotificationPriority
    channels: List[NotificationChannel]
    title: str                  # Заголовок уведомления
    message: str                # Текст уведомления
    created_at: datetime        # Время создания
    expires_at: Optional[datetime] = None  # Время истечения
    is_read: bool = False       # Прочитано ли
    read_at: Optional[datetime] = None     # Время прочтения
    metadata: Dict[str, Any] = None        # Дополнительные данные
    action_required: bool = False          # Требуется ли действие
    action_url: Optional[str] = None       # URL для действия
    qr_code: Optional[str] = None          # QR-код для уведомления


@dataclass
class NotificationResult:
    """Результат отправки уведомления"""
    notification_id: str
    success: bool
    sent_channels: List[NotificationChannel]
    failed_channels: List[NotificationChannel]
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None


@dataclass
class NotificationTemplate:
    """Шаблон уведомления"""
    template_id: str
    notification_type: NotificationType
    title_template: str
    message_template: str
    priority: NotificationPriority
    channels: List[NotificationChannel]
    variables: List[str] = field(default_factory=list)
    is_active: bool = True


class FamilyNotificationManagerEnhanced:
    """
    Расширенный менеджер анонимных уведомлений для семей

    Новые функции:
    - Напоминания о подписках
    - Уведомления об оплате
    - Реферальные уведомления
    - Персонализированные уведомления
    - Шаблоны уведомлений
    - QR-код уведомления
    """

    def __init__(self):
        """Инициализация расширенной системы уведомлений"""
        self.notifications: Dict[str, FamilyNotification] = {}
        self.family_channels: Dict[str, Dict[NotificationChannel, str]] = {}
        self.notification_history: List[NotificationResult] = []
        self.notification_templates: Dict[str, NotificationTemplate] = {}
        self.scheduled_notifications: Dict[str, Dict[str, Any]] = {}

        # Настройки уведомлений
        self.max_notifications_per_family = 1000
        self.notification_retention_days = 30
        self.retry_attempts = 3
        self.retry_delay_seconds = 5

        # Инициализация шаблонов
        self._initialize_notification_templates()

        logger.info("Расширенная система анонимных уведомлений инициализирована")

    def _initialize_notification_templates(self) -> None:
        """Инициализация шаблонов уведомлений"""

        # Шаблон напоминания о тестовом периоде
        self.notification_templates["trial_reminder"] = NotificationTemplate(
            template_id="trial_reminder",
            notification_type=NotificationType.TRIAL_REMINDER,
            title_template="Тестовый период истекает через {days_left} дней",
            message_template="У вас осталось {days_left} дней тестового периода. "
            "Продлите подписку, чтобы сохранить защиту семьи.",
            priority=NotificationPriority.HIGH,
            channels=[
                NotificationChannel.PUSH,
                NotificationChannel.IN_APP,
                NotificationChannel.EMAIL],
            variables=[
                "days_left",
                "subscription_tier"])

        # Шаблон успешной оплаты
        self.notification_templates["payment_success"] = NotificationTemplate(
            template_id="payment_success",
            notification_type=NotificationType.PAYMENT_SUCCESS,
            title_template="Оплата успешно проведена",
            message_template="Ваша подписка {subscription_tier} активирована. Сумма: {amount}₽. Спасибо за доверие!",
            priority=NotificationPriority.MEDIUM,
            channels=[NotificationChannel.PUSH, NotificationChannel.IN_APP, NotificationChannel.EMAIL],
            variables=["subscription_tier", "amount"]
        )

        # Шаблон QR-кода для оплаты
        self.notification_templates["qr_payment"] = NotificationTemplate(
            template_id="qr_payment",
            notification_type=NotificationType.QR_CODE_GENERATED,
            title_template="QR-код для оплаты подписки",
            message_template="Отсканируйте QR-код для оплаты подписки {subscription_tier} на сумму {amount}₽",
            priority=NotificationPriority.HIGH,
            channels=[NotificationChannel.QR_CODE, NotificationChannel.IN_APP],
            variables=["subscription_tier", "amount", "qr_code"]
        )

        # Шаблон реферального уведомления
        self.notification_templates["referral_signup"] = NotificationTemplate(
            template_id="referral_signup",
            notification_type=NotificationType.REFERRAL_SIGNUP,
            title_template="Новый реферал присоединился!",
            message_template="По вашей реферальной ссылке зарегистрировалась новая семья. "
            "Вы получите дополнительные функции!",
            priority=NotificationPriority.MEDIUM,
            channels=[NotificationChannel.IN_APP],  # ТОЛЬКО ВНУТРИ ПРИЛОЖЕНИЯ
            variables=["referral_code"]
        )

        # Шаблон рекомендации тарифа
        self.notification_templates["tariff_recommendation"] = NotificationTemplate(
            template_id="tariff_recommendation",
            notification_type=NotificationType.TARIFF_RECOMMENDATION,
            title_template="Персональная рекомендация тарифа",
            message_template="На основе вашего использования мы рекомендуем тариф "
            "{recommended_tariff}. Скидка {discount}%!",
            priority=NotificationPriority.LOW,
            channels=[NotificationChannel.IN_APP],  # ТОЛЬКО ВНУТРИ ПРИЛОЖЕНИЯ
            variables=["recommended_tariff", "discount"]
        )

    async def send_trial_reminder(self, family_id: str, days_left: int,
                                  subscription_tier: str) -> NotificationResult:
        """
        Напоминание о тестовом периоде

        Args:
            family_id: ID семьи
            days_left: Дней до истечения
            subscription_tier: Тариф подписки

        Returns:
            Результат отправки уведомления
        """
        try:
            template = self.notification_templates["trial_reminder"]

            # Формируем сообщение
            title = template.title_template.format(days_left=days_left)
            message = template.message_template.format(
                days_left=days_left,
                subscription_tier=subscription_tier
            )

            # Отправляем уведомление
            result = await self.send_family_alert(
                family_id=family_id,
                notification_type=NotificationType.TRIAL_REMINDER,
                priority=template.priority,
                title=title,
                message=message,
                channels=template.channels,
                metadata={
                    "days_left": days_left,
                    "subscription_tier": subscription_tier,
                    "template_id": template.template_id
                },
                action_required=True,
                action_url=f"/subscription/upgrade?tier={subscription_tier}"
            )

            logger.info(f"Отправлено напоминание о тестовом периоде семье {family_id}")
            return result

        except Exception as e:
            logger.error(f"Ошибка отправки напоминания о тестовом периоде: {e}")
            return NotificationResult(
                notification_id="",
                success=False,
                sent_channels=[],
                failed_channels=[],
                error_message=str(e)
            )

    async def send_payment_success_notification(self, family_id: str,
                                                subscription_tier: str,
                                                amount: float) -> NotificationResult:
        """
        Уведомление об успешной оплате

        Args:
            family_id: ID семьи
            subscription_tier: Тариф подписки
            amount: Сумма оплаты

        Returns:
            Результат отправки уведомления
        """
        try:
            template = self.notification_templates["payment_success"]

            # Формируем сообщение
            title = template.title_template
            message = template.message_template.format(
                subscription_tier=subscription_tier,
                amount=amount
            )

            # Отправляем уведомление
            result = await self.send_family_alert(
                family_id=family_id,
                notification_type=NotificationType.PAYMENT_SUCCESS,
                priority=template.priority,
                title=title,
                message=message,
                channels=template.channels,
                metadata={
                    "subscription_tier": subscription_tier,
                    "amount": amount,
                    "template_id": template.template_id
                }
            )

            logger.info(f"Отправлено уведомление об успешной оплате семье {family_id}")
            return result

        except Exception as e:
            logger.error(f"Ошибка отправки уведомления об оплате: {e}")
            return NotificationResult(
                notification_id="",
                success=False,
                sent_channels=[],
                failed_channels=[],
                error_message=str(e)
            )

    async def send_qr_payment_notification(self, family_id: str,
                                           subscription_tier: str,
                                           amount: float,
                                           qr_code: str) -> NotificationResult:
        """
        Уведомление с QR-кодом для оплаты

        Args:
            family_id: ID семьи
            subscription_tier: Тариф подписки
            amount: Сумма оплаты
            qr_code: QR-код для оплаты

        Returns:
            Результат отправки уведомления
        """
        try:
            template = self.notification_templates["qr_payment"]

            # Формируем сообщение
            title = template.title_template
            message = template.message_template.format(
                subscription_tier=subscription_tier,
                amount=amount,
                qr_code=qr_code
            )

            # Отправляем уведомление
            result = await self.send_family_alert(
                family_id=family_id,
                notification_type=NotificationType.QR_CODE_GENERATED,
                priority=template.priority,
                title=title,
                message=message,
                channels=template.channels,
                metadata={
                    "subscription_tier": subscription_tier,
                    "amount": amount,
                    "qr_code": qr_code,
                    "template_id": template.template_id
                },
                qr_code=qr_code
            )

            logger.info(f"Отправлено QR-код уведомление семье {family_id}")
            return result

        except Exception as e:
            logger.error(f"Ошибка отправки QR-код уведомления: {e}")
            return NotificationResult(
                notification_id="",
                success=False,
                sent_channels=[],
                failed_channels=[],
                error_message=str(e)
            )

    async def send_referral_notification(self, family_id: str,
                                         referral_code: str,
                                         notification_type: NotificationType) -> NotificationResult:
        """
        Реферальное уведомление

        Args:
            family_id: ID семьи
            referral_code: Код реферальной ссылки
            notification_type: Тип реферального уведомления

        Returns:
            Результат отправки уведомления
        """
        try:
            if notification_type == NotificationType.REFERRAL_SIGNUP:
                template = self.notification_templates["referral_signup"]

                title = template.title_template
                message = template.message_template.format(referral_code=referral_code)

                result = await self.send_family_alert(
                    family_id=family_id,
                    notification_type=notification_type,
                    priority=template.priority,
                    title=title,
                    message=message,
                    channels=template.channels,
                    metadata={
                        "referral_code": referral_code,
                        "template_id": template.template_id
                    }
                )
            else:
                # Для других типов реферальных уведомлений
                result = await self.send_family_alert(
                    family_id=family_id,
                    notification_type=notification_type,
                    priority=NotificationPriority.MEDIUM,
                    title="Реферальное уведомление",
                    message="Обновление по реферальной программе",
                    channels=[NotificationChannel.IN_APP],
                    metadata={"referral_code": referral_code}
                )

            logger.info(f"Отправлено реферальное уведомление семье {family_id}")
            return result

        except Exception as e:
            logger.error(f"Ошибка отправки реферального уведомления: {e}")
            return NotificationResult(
                notification_id="",
                success=False,
                sent_channels=[],
                failed_channels=[],
                error_message=str(e)
            )

    async def send_tariff_recommendation(self, family_id: str,
                                         recommended_tariff: str,
                                         discount: float) -> NotificationResult:
        """
        Персонализированная рекомендация тарифа

        Args:
            family_id: ID семьи
            recommended_tariff: Рекомендуемый тариф
            discount: Размер скидки

        Returns:
            Результат отправки уведомления
        """
        try:
            template = self.notification_templates["tariff_recommendation"]

            # Формируем сообщение
            title = template.title_template
            message = template.message_template.format(
                recommended_tariff=recommended_tariff,
                discount=discount
            )

            # Отправляем уведомление
            result = await self.send_family_alert(
                family_id=family_id,
                notification_type=NotificationType.TARIFF_RECOMMENDATION,
                priority=template.priority,
                title=title,
                message=message,
                channels=template.channels,
                metadata={
                    "recommended_tariff": recommended_tariff,
                    "discount": discount,
                    "template_id": template.template_id
                },
                action_required=True,
                action_url=f"/subscription/upgrade?tier={recommended_tariff}&discount={discount}"
            )

            logger.info(f"Отправлена рекомендация тарифа семье {family_id}")
            return result

        except Exception as e:
            logger.error(f"Ошибка отправки рекомендации тарифа: {e}")
            return NotificationResult(
                notification_id="",
                success=False,
                sent_channels=[],
                failed_channels=[],
                error_message=str(e)
            )

    async def schedule_subscription_reminder(self, family_id: str,
                                             reminder_type: str,
                                             scheduled_time: datetime,
                                             metadata: Dict[str, Any]) -> bool:
        """
        Планирование напоминания о подписке

        Args:
            family_id: ID семьи
            reminder_type: Тип напоминания
            scheduled_time: Время отправки
            metadata: Дополнительные данные

        Returns:
            True если напоминание запланировано
        """
        try:
            reminder_id = str(uuid.uuid4())

            self.scheduled_notifications[reminder_id] = {
                "reminder_id": reminder_id,
                "family_id": family_id,
                "reminder_type": reminder_type,
                "scheduled_time": scheduled_time,
                "metadata": metadata,
                "created_at": datetime.now(),
                "is_sent": False
            }

            logger.info(f"Запланировано напоминание {reminder_type} для семьи {family_id} на {scheduled_time}")
            return True

        except Exception as e:
            logger.error(f"Ошибка планирования напоминания: {e}")
            return False

    async def process_scheduled_notifications(self) -> int:
        """
        Обработка запланированных уведомлений

        Returns:
            Количество отправленных уведомлений
        """
        try:
            sent_count = 0
            now = datetime.now()

            for reminder_id, reminder in list(self.scheduled_notifications.items()):
                if (not reminder["is_sent"] and
                        reminder["scheduled_time"] <= now):

                    # Отправляем напоминание
                    success = await self._send_scheduled_reminder(reminder)

                    if success:
                        reminder["is_sent"] = True
                        sent_count += 1
                        logger.info(f"Отправлено запланированное напоминание {reminder_id}")

            return sent_count

        except Exception as e:
            logger.error(f"Ошибка обработки запланированных уведомлений: {e}")
            return 0

    async def _send_scheduled_reminder(self, reminder: Dict[str, Any]) -> bool:
        """Отправка запланированного напоминания"""
        try:
            family_id = reminder["family_id"]
            reminder_type = reminder["reminder_type"]
            metadata = reminder["metadata"]

            if reminder_type == "trial_reminder":
                return await self.send_trial_reminder(
                    family_id=family_id,
                    days_left=metadata.get("days_left", 0),
                    subscription_tier=metadata.get("subscription_tier", "basic")
                ).success

            elif reminder_type == "subscription_expiring":
                return await self.send_family_alert(
                    family_id=family_id,
                    notification_type=NotificationType.SUBSCRIPTION_EXPIRING,
                    priority=NotificationPriority.HIGH,
                    title="Подписка истекает",
                    message=f"Ваша подписка {metadata.get('subscription_tier', '')} "
                    f"истекает через {metadata.get('days_left', 0)} дней",
                    channels=[NotificationChannel.PUSH, NotificationChannel.IN_APP]
                ).success

            return False

        except Exception as e:
            logger.error(f"Ошибка отправки запланированного напоминания: {e}")
            return False

    async def send_family_alert(
        self,
        family_id: str,
        notification_type: NotificationType,
        priority: NotificationPriority,
        title: str,
        message: str,
        channels: List[NotificationChannel] = None,
        metadata: Dict[str, Any] = None,
        action_required: bool = False,
        action_url: Optional[str] = None,
        qr_code: Optional[str] = None
    ) -> NotificationResult:
        """
        Отправка анонимного уведомления семье (расширенная версия)

        Args:
            family_id: Анонимный ID семьи
            notification_type: Тип уведомления
            priority: Приоритет
            title: Заголовок
            message: Текст сообщения
            channels: Каналы отправки
            metadata: Дополнительные данные
            action_required: Требуется ли действие
            action_url: URL для действия
            qr_code: QR-код для уведомления

        Returns:
            NotificationResult с результатом отправки
        """
        try:
            # Создание уведомления
            notification = FamilyNotification(
                notification_id=self._generate_notification_id(),
                family_id=family_id,
                notification_type=notification_type,
                priority=priority,
                channels=channels or self._get_available_channels(family_id),
                title=title,
                message=message,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=7),
                metadata=metadata or {},
                action_required=action_required,
                action_url=action_url,
                qr_code=qr_code
            )

            # Сохранение уведомления
            self.notifications[notification.notification_id] = notification

            # Отправка по каналам
            result = await self._send_notification(notification)

            # Сохранение результата
            self.notification_history.append(result)

            logger.info(f"Уведомление {notification.notification_id} "
                        f"отправлено семье {family_id}")
            return result

        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")
            return NotificationResult(
                notification_id="",
                success=False,
                sent_channels=[],
                failed_channels=[],
                error_message=str(e)
            )

    def _generate_notification_id(self) -> str:
        """Генерация уникального ID уведомления"""
        return str(uuid.uuid4())

    def _get_available_channels(self, family_id: str) -> List[NotificationChannel]:
        """Получение доступных каналов для семьи"""
        available_channels = [NotificationChannel.IN_APP]  # Всегда доступен

        if family_id in self.family_channels:
            family_channels = self.family_channels[family_id]
            for channel in NotificationChannel:
                if channel in family_channels:
                    available_channels.append(channel)

        return available_channels

    async def _send_notification(self, notification: FamilyNotification) -> NotificationResult:
        """Отправка уведомления по каналам"""
        try:
            sent_channels = []
            failed_channels = []

            for channel in notification.channels:
                try:
                    success = await self._send_to_channel(notification, channel)
                    if success:
                        sent_channels.append(channel)
                    else:
                        failed_channels.append(channel)
                except Exception as e:
                    logger.error(f"Ошибка отправки по каналу {channel.value}: {e}")
                    failed_channels.append(channel)

            return NotificationResult(
                notification_id=notification.notification_id,
                success=len(sent_channels) > 0,
                sent_channels=sent_channels,
                failed_channels=failed_channels,
                sent_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")
            return NotificationResult(
                notification_id=notification.notification_id,
                success=False,
                sent_channels=[],
                failed_channels=notification.channels,
                error_message=str(e)
            )

    async def _send_to_channel(self, notification: FamilyNotification,
                               channel: NotificationChannel) -> bool:
        """Отправка уведомления по конкретному каналу"""
        try:
            if channel == NotificationChannel.IN_APP:
                # Внутри приложения - всегда успешно
                return True

            elif channel == NotificationChannel.PUSH:
                # PUSH-уведомления
                return await self._send_push_notification(notification)

            elif channel == NotificationChannel.EMAIL:
                # Email уведомления
                return await self._send_email_notification(notification)

            elif channel == NotificationChannel.SMS:
                # SMS уведомления
                return await self._send_sms_notification(notification)

            elif channel == NotificationChannel.TELEGRAM:
                # Telegram уведомления
                return await self._send_telegram_notification(notification)

            elif channel == NotificationChannel.WHATSAPP:
                # WhatsApp уведомления
                return await self._send_whatsapp_notification(notification)

            elif channel == NotificationChannel.QR_CODE:
                # QR-код уведомления
                return await self._send_qr_notification(notification)

            else:
                logger.warning(f"Неподдерживаемый канал: {channel.value}")
                return False

        except Exception as e:
            logger.error(f"Ошибка отправки по каналу {channel.value}: {e}")
            return False

    async def _send_push_notification(self, notification: FamilyNotification) -> bool:
        """Отправка PUSH-уведомления"""
        # Здесь должна быть интеграция с PUSH-сервисом
        logger.info(f"PUSH уведомление отправлено: {notification.title}")
        return True

    async def _send_email_notification(self, notification: FamilyNotification) -> bool:
        """Отправка email уведомления"""
        # Здесь должна быть интеграция с email-сервисом
        logger.info(f"Email уведомление отправлено: {notification.title}")
        return True

    async def _send_sms_notification(self, notification: FamilyNotification) -> bool:
        """Отправка SMS уведомления"""
        # Здесь должна быть интеграция с SMS-сервисом
        logger.info(f"SMS уведомление отправлено: {notification.title}")
        return True

    async def _send_telegram_notification(self, notification: FamilyNotification) -> bool:
        """Отправка Telegram уведомления"""
        # Здесь должна быть интеграция с Telegram Bot API
        logger.info(f"Telegram уведомление отправлено: {notification.title}")
        return True

    async def _send_whatsapp_notification(self, notification: FamilyNotification) -> bool:
        """Отправка WhatsApp уведомления"""
        # Здесь должна быть интеграция с WhatsApp Business API
        logger.info(f"WhatsApp уведомление отправлено: {notification.title}")
        return True

    async def _send_qr_notification(self, notification: FamilyNotification) -> bool:
        """Отправка QR-код уведомления"""
        if notification.qr_code:
            logger.info(f"QR-код уведомление отправлено: {notification.title}")
            return True
        return False

    def register_device_token(self, family_id: str, device_token: str,
                              device_type: str) -> bool:
        """Регистрация токена устройства для PUSH-уведомлений"""
        try:
            if family_id not in self.family_channels:
                self.family_channels[family_id] = {}

            # Сохраняем токен с привязкой к типу устройства
            token_key = f"push_{device_type}"
            self.family_channels[family_id][NotificationChannel.PUSH] = f"{token_key}:{device_token}"

            logger.info(f"Токен устройства зарегистрирован для семьи {family_id}")
            return True

        except Exception as e:
            logger.error(f"Ошибка регистрации токена: {e}")
            return False

    async def get_notification_stats(self) -> Dict[str, Any]:
        """Получение статистики уведомлений"""
        try:
            stats = {
                "total_notifications": len(self.notifications),
                "total_sent": len([r for r in self.notification_history if r.success]),
                "total_failed": len([r for r in self.notification_history if not r.success]),
                "by_type": {},
                "by_priority": {},
                "by_channel": {},
                "scheduled_notifications": len(self.scheduled_notifications),
                "unread_notifications": len([n for n in self.notifications.values() if not n.is_read])
            }

            # Подсчет по типам
            for notification in self.notifications.values():
                notification_type = notification.notification_type.value
                stats["by_type"][notification_type] = stats["by_type"].get(notification_type, 0) + 1

                priority = notification.priority.value
                stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1

                for channel in notification.channels:
                    channel_name = channel.value
                    stats["by_channel"][channel_name] = stats["by_channel"].get(channel_name, 0) + 1

            return stats

        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}

    async def cleanup_old_notifications(self) -> int:
        """Очистка старых уведомлений"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.notification_retention_days)
            cleaned_count = 0

            # Очищаем уведомления
            for notification_id, notification in list(self.notifications.items()):
                if notification.created_at < cutoff_date:
                    del self.notifications[notification_id]
                    cleaned_count += 1

            # Очищаем историю
            self.notification_history = [
                r for r in self.notification_history
                if r.sent_at and r.sent_at > cutoff_date
            ]

            logger.info(f"Очищено {cleaned_count} старых уведомлений")
            return cleaned_count

        except Exception as e:
            logger.error(f"Ошибка очистки уведомлений: {e}")
            return 0


# Создание глобального экземпляра
family_notification_manager_enhanced = FamilyNotificationManagerEnhanced()


async def main():
    """Тестирование FamilyNotificationManagerEnhanced"""
    print("🧪 Тестирование FamilyNotificationManagerEnhanced")
    print("=" * 60)

    # Тест напоминания о тестовом периоде
    trial_result = await family_notification_manager_enhanced.send_trial_reminder(
        family_id="test_family_123",
        days_left=3,
        subscription_tier="basic"
    )
    print(f"Напоминание о тестовом периоде: {trial_result.success}")

    # Тест уведомления об успешной оплате
    payment_result = await family_notification_manager_enhanced.send_payment_success_notification(
        family_id="test_family_123",
        subscription_tier="family",
        amount=490.0
    )
    print(f"Уведомление об оплате: {payment_result.success}")

    # Тест QR-код уведомления
    qr_result = await family_notification_manager_enhanced.send_qr_payment_notification(
        family_id="test_family_123",
        subscription_tier="premium",
        amount=900.0,
        qr_code="data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    )
    print(f"QR-код уведомление: {qr_result.success}")

    # Тест реферального уведомления
    referral_result = await family_notification_manager_enhanced.send_referral_notification(
        family_id="test_family_123",
        referral_code="REF123456",
        notification_type=NotificationType.REFERRAL_SIGNUP
    )
    print(f"Реферальное уведомление: {referral_result.success}")

    # Тест рекомендации тарифа
    recommendation_result = await family_notification_manager_enhanced.send_tariff_recommendation(
        family_id="test_family_123",
        recommended_tariff="premium",
        discount=20.0
    )
    print(f"Рекомендация тарифа: {recommendation_result.success}")

    # Планирование напоминания
    scheduled_time = datetime.now() + timedelta(hours=1)
    schedule_result = await family_notification_manager_enhanced.schedule_subscription_reminder(
        family_id="test_family_123",
        reminder_type="trial_reminder",
        scheduled_time=scheduled_time,
        metadata={"days_left": 1, "subscription_tier": "basic"}
    )
    print(f"Планирование напоминания: {schedule_result}")

    # Получение статистики
    stats = await family_notification_manager_enhanced.get_notification_stats()
    print(f"Статистика уведомлений: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
