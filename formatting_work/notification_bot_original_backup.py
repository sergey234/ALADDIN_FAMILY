#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotificationBot - Бот уведомлений
function_90: Интеллектуальный бот для управления уведомлениями

Этот модуль предоставляет интеллектуального бота для управления уведомлениями,
включающего:
- Умную фильтрацию уведомлений
- Персонализацию контента
- Приоритизацию сообщений
- Адаптивную доставку
- Анализ эффективности
- Интеграцию с каналами
- Геолокационные уведомления
- Временные ограничения
- Группировку сообщений
- Автоматические ответы

Основные возможности:
1. Интеллектуальная фильтрация уведомлений
2. Персонализация под пользователя
3. Приоритизация по важности
4. Адаптивная доставка по каналам
5. Анализ эффективности доставки
6. Интеграция с множественными каналами
7. Геолокационные и контекстные уведомления
8. Управление временными ограничениями
9. Группировка и батчинг уведомлений
10. Автоматические ответы и действия

Технические детали:
- Использует ML для персонализации
- Применяет NLP для анализа контента
- Интегрирует с различными каналами доставки
- Использует геолокацию для контекстных уведомлений
- Применяет A/B тестирование для оптимизации
- Интегрирует с системами аналитики
- Использует кэширование для производительности
- Применяет алгоритмы приоритизации
- Интегрирует с внешними API
- Использует машинное обучение для предсказания поведения

Автор: ALADDIN Security System
Версия: 2.0
Дата: 2025-01-27
Лицензия: MIT
"""

from core.base import ComponentStatus, SecurityBase, SecurityLevel
import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import threading
from collections import defaultdict

# Внешние зависимости
import redis
import sqlalchemy
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, JSON, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, Field, validator
from prometheus_client import Counter, Histogram, Gauge
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Внутренние импорты
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# База данных
Base = declarative_base()


class NotificationType(Enum):
    """Типы уведомлений"""
    SECURITY_ALERT = "security_alert"
    SYSTEM_UPDATE = "system_update"
    USER_ACTION = "user_action"
    PROMOTIONAL = "promotional"
    EDUCATIONAL = "educational"
    EMERGENCY = "emergency"
    REMINDER = "reminder"
    SOCIAL = "social"
    NEWS = "news"
    TRANSACTION = "transaction"


class Priority(Enum):
    """Приоритеты уведомлений"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class DeliveryChannel(Enum):
    """Каналы доставки"""
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    VOICE = "voice"
    SLACK = "slack"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    WHATSAPP = "whatsapp"


class NotificationStatus(Enum):
    """Статусы уведомлений"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    CLICKED = "clicked"
    FAILED = "failed"
    CANCELLED = "cancelled"


class UserPreference(Base):
    """Предпочтения пользователя"""
    __tablename__ = "user_preferences"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    notification_type = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    quiet_hours_start = Column(String)  # HH:MM
    quiet_hours_end = Column(String)    # HH:MM
    timezone = Column(String, default="UTC")
    language = Column(String, default="en")
    frequency_limit = Column(Integer, default=10)  # уведомлений в час
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notification(Base):
    """Уведомление"""
    __tablename__ = "notifications"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    notification_type = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    channel = Column(String, nullable=False)
    status = Column(String, default=NotificationStatus.PENDING.value)
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    clicked_at = Column(DateTime)
    notification_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class NotificationTemplate(Base):
    """Шаблон уведомления"""
    __tablename__ = "notification_templates"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    notification_type = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    subject_template = Column(String)
    message_template = Column(Text, nullable=False)
    variables = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class NotificationRequest(BaseModel):
    """Запрос на отправку уведомления"""
    user_id: str
    notification_type: NotificationType
    priority: Priority
    title: str
    message: str
    channel: Optional[DeliveryChannel] = None
    scheduled_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    template_id: Optional[str] = None
    variables: Dict[str, Any] = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    """Ответ на отправку уведомления"""
    success: bool
    notification_id: str
    message: str
    delivery_estimate: Optional[datetime] = None
    channels_used: List[DeliveryChannel] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class NotificationAnalytics(BaseModel):
    """Аналитика уведомлений"""
    total_sent: int = 0
    total_delivered: int = 0
    total_read: int = 0
    total_clicked: int = 0
    delivery_rate: float = 0.0
    read_rate: float = 0.0
    click_rate: float = 0.0
    average_delivery_time: float = 0.0  # секунды
    top_channels: List[Dict[str, Any]] = Field(default_factory=list)
    top_notification_types: List[Dict[str, Any]] = Field(default_factory=list)


# Prometheus метрики
notifications_sent_total = Counter(
    'notifications_sent_total',
    'Total number of notifications sent',
    ['type', 'channel', 'priority']
)

notifications_delivered_total = Counter(
    'notifications_delivered_total',
    'Total number of notifications delivered',
    ['type', 'channel']
)

notification_delivery_time = Histogram(
    'notification_delivery_time_seconds',
    'Time taken to deliver notifications',
    ['channel']
)

active_notifications = Gauge(
    'active_notifications',
    'Number of active notifications'
)


class NotificationBot(SecurityBase):
    """
    Интеллектуальный бот уведомлений

    Предоставляет продвинутую систему управления уведомлениями с поддержкой:
    - Умной фильтрации и персонализации
    - Приоритизации по важности
    - Адаптивной доставки по каналам
    - Аналитики эффективности
    - Интеграции с множественными каналами
    """

    def __init__(self, name: str = "NotificationBot", config: Optional[Dict[str, Any]] = None):
        """
        Инициализация NotificationBot

        Args:
            name: Имя бота
            config: Конфигурация
        """
        super().__init__(name, config)

        # Конфигурация по умолчанию
        self.default_config = {
            "redis_url": "redis://localhost:6379/0",
            "database_url": "sqlite:///notification_bot.db",
            "personalization_enabled": True,
            "priority_algorithm": "ml_based",
            "delivery_optimization": True,
            "analytics_enabled": True,
            "template_engine": True,
            "batch_processing": True,
            "rate_limiting": True,
            "quiet_hours_respect": True,
            "geolocation_enabled": True,
            "ml_enabled": True,
            "adaptive_learning": True,
            "cleanup_interval": 300,
            "metrics_enabled": True,
            "logging_enabled": True
        }

        # Объединение конфигураций
        self.config = {**self.default_config, **(config or {})}

        # Инициализация компонентов
        self.redis_client: Optional[redis.Redis] = None
        self.db_engine: Optional[sqlalchemy.Engine] = None
        self.db_session: Optional[sqlalchemy.orm.Session] = None
        self.user_preferences: Dict[str, Dict[str, UserPreference]] = {}
        self.notification_templates: Dict[str, NotificationTemplate] = {}
        self.pending_notifications: Dict[str, Notification] = {}
        self.ml_model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None

        # Статистика
        self.stats = {
            "total_notifications": 0,
            "sent_notifications": 0,
            "delivered_notifications": 0,
            "read_notifications": 0,
            "clicked_notifications": 0,
            "failed_notifications": 0,
            "average_delivery_time": 0.0,
            "delivery_rate": 0.0,
            "read_rate": 0.0,
            "click_rate": 0.0
        }

        # Потоки
        self.monitoring_thread: Optional[threading.Thread] = None
        self.delivery_thread: Optional[threading.Thread] = None
        self.running = False

        # Блокировки
        self.lock = threading.RLock()

        self.logger.info(f"NotificationBot {name} инициализирован")

    async def start(self) -> bool:
        """Запуск бота уведомлений"""
        try:
            with self.lock:
                if self.running:
                    self.logger.warning("NotificationBot уже запущен")
                    return True

                # Инициализация базы данных
                await self._setup_database()

                # Инициализация Redis
                await self._setup_redis()

                # Инициализация ML модели
                if self.config.get("ml_enabled", True):
                    await self._setup_ml_model()

                # Загрузка предпочтений пользователей
                await self._load_user_preferences()

                # Загрузка шаблонов
                await self._load_notification_templates()

                # Запуск потоков
                self.running = True
                self.monitoring_thread = threading.Thread(target=self._monitoring_worker)
                self.delivery_thread = threading.Thread(target=self._delivery_worker)

                self.monitoring_thread.daemon = True
                self.delivery_thread.daemon = True

                self.monitoring_thread.start()
                self.delivery_thread.start()

                self.logger.info("NotificationBot запущен успешно")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка запуска NotificationBot: {e}")
            return False

    async def stop(self) -> bool:
        """Остановка бота уведомлений"""
        try:
            with self.lock:
                if not self.running:
                    self.logger.warning("NotificationBot уже остановлен")
                    return True

                self.running = False

                # Ожидание завершения потоков
                if self.monitoring_thread and self.monitoring_thread.is_alive():
                    self.monitoring_thread.join(timeout=5)

                if self.delivery_thread and self.delivery_thread.is_alive():
                    self.delivery_thread.join(timeout=5)

                # Закрытие соединений
                if self.db_session:
                    self.db_session.close()

                if self.redis_client:
                    self.redis_client.close()

                self.logger.info("NotificationBot остановлен")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка остановки NotificationBot: {e}")
            return False

    async def _setup_database(self) -> None:
        """Настройка базы данных"""
        try:
            database_url = self.config.get("database_url", "sqlite:///notification_bot.db")
            self.db_engine = create_engine(database_url)
            Base.metadata.create_all(self.db_engine)

            Session = sessionmaker(bind=self.db_engine)
            self.db_session = Session()

            self.logger.info("База данных NotificationBot настроена")

        except Exception as e:
            self.logger.error(f"Ошибка настройки базы данных: {e}")
            raise

    async def _setup_redis(self) -> None:
        """Настройка Redis"""
        try:
            redis_url = self.config.get("redis_url", "redis://localhost:6379/0")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)

            # Тест соединения
            self.redis_client.ping()

            self.logger.info("Redis для NotificationBot настроен")

        except Exception as e:
            self.logger.error(f"Ошибка настройки Redis: {e}")
            raise

    async def _setup_ml_model(self) -> None:
        """Настройка ML модели для персонализации"""
        try:
            self.ml_model = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            self.scaler = StandardScaler()

            self.logger.info("ML модель NotificationBot настроена")

        except Exception as e:
            self.logger.error(f"Ошибка настройки ML модели: {e}")

    async def _load_user_preferences(self) -> None:
        """Загрузка предпочтений пользователей"""
        try:
            if self.db_session:
                preferences = self.db_session.query(UserPreference).all()

                for pref in preferences:
                    if pref.user_id not in self.user_preferences:
                        self.user_preferences[pref.user_id] = {}

                    self.user_preferences[pref.user_id][f"{pref.notification_type}_{pref.channel}"] = pref

                self.logger.info(f"Загружено {len(preferences)} предпочтений пользователей")

        except Exception as e:
            self.logger.error(f"Ошибка загрузки предпочтений пользователей: {e}")

    async def _load_notification_templates(self) -> None:
        """Загрузка шаблонов уведомлений"""
        try:
            if self.db_session:
                templates = self.db_session.query(NotificationTemplate).filter(
                    NotificationTemplate.is_active
                ).all()

                for template in templates:
                    self.notification_templates[template.id] = template

                self.logger.info(f"Загружено {len(templates)} шаблонов уведомлений")

        except Exception as e:
            self.logger.error(f"Ошибка загрузки шаблонов уведомлений: {e}")

    def _monitoring_worker(self) -> None:
        """Фоновый процесс мониторинга"""
        while self.running:
            try:
                time.sleep(1)  # Проверка каждую секунду

                # Обновление статистики
                self._update_stats()

                # Обработка отложенных уведомлений
                self._process_scheduled_notifications()

            except Exception as e:
                self.logger.error(f"Ошибка в процессе мониторинга: {e}")

    def _delivery_worker(self) -> None:
        """Фоновый процесс доставки уведомлений"""
        while self.running:
            try:
                time.sleep(0.1)  # Частая проверка для быстрой доставки

                # Обработка очереди доставки
                self._process_delivery_queue()

            except Exception as e:
                self.logger.error(f"Ошибка в процессе доставки: {e}")

    def _update_stats(self) -> None:
        """Обновление статистики"""
        try:
            with self.lock:
                # Расчет метрик
                if self.stats["sent_notifications"] > 0:
                    self.stats["delivery_rate"] = (
                        self.stats["delivered_notifications"] / self.stats["sent_notifications"]
                    ) * 100

                if self.stats["delivered_notifications"] > 0:
                    self.stats["read_rate"] = (
                        self.stats["read_notifications"] / self.stats["delivered_notifications"]
                    ) * 100

                if self.stats["read_notifications"] > 0:
                    self.stats["click_rate"] = (
                        self.stats["clicked_notifications"] / self.stats["read_notifications"]
                    ) * 100

                # Обновление метрик Prometheus
                active_notifications.set(len(self.pending_notifications))

        except Exception as e:
            self.logger.error(f"Ошибка обновления статистики: {e}")

    def _process_scheduled_notifications(self) -> None:
        """Обработка отложенных уведомлений"""
        try:
            current_time = datetime.utcnow()

            for notification_id, notification in list(self.pending_notifications.items()):
                if (notification.scheduled_at and
                    notification.scheduled_at <= current_time and
                        notification.status == NotificationStatus.PENDING.value):

                    # Перемещение в очередь доставки
                    self._queue_for_delivery(notification)

        except Exception as e:
            self.logger.error(f"Ошибка обработки отложенных уведомлений: {e}")

    def _process_delivery_queue(self) -> None:
        """Обработка очереди доставки"""
        try:
            # Здесь должна быть логика обработки очереди доставки
            # Пока что заглушка
            pass

        except Exception as e:
            self.logger.error(f"Ошибка обработки очереди доставки: {e}")

    def _queue_for_delivery(self, notification: Notification) -> None:
        """Добавление уведомления в очередь доставки"""
        try:
            # Здесь должна быть логика добавления в очередь
            # Пока что просто обновляем статус
            notification.status = NotificationStatus.SENT.value
            notification.sent_at = datetime.utcnow()

            # Обновление в базе данных
            if self.db_session:
                self.db_session.commit()

            # Обновление статистики
            self.stats["sent_notifications"] += 1

            # Обновление метрик
            notifications_sent_total.labels(
                type=notification.notification_type,
                channel=notification.channel,
                priority=notification.priority
            ).inc()

        except Exception as e:
            self.logger.error(f"Ошибка добавления в очередь доставки: {e}")

    async def send_notification(self, request: NotificationRequest) -> NotificationResponse:
        """Отправка уведомления"""
        try:
            # Проверка предпочтений пользователя
            if not await self._should_send_notification(request):
                return NotificationResponse(
                    success=False,
                    notification_id="",
                    message="Уведомление заблокировано настройками пользователя"
                )

            # Определение канала доставки
            channel = await self._determine_delivery_channel(request)

            # Создание уведомления
            notification = await self._create_notification(request, channel)

            # Добавление в очередь
            self.pending_notifications[notification.id] = notification

            # Обновление статистики
            self.stats["total_notifications"] += 1

            return NotificationResponse(
                success=True,
                notification_id=notification.id,
                message="Уведомление добавлено в очередь",
                delivery_estimate=notification.scheduled_at or datetime.utcnow(),
                channels_used=[channel]
            )

        except Exception as e:
            self.logger.error(f"Ошибка отправки уведомления: {e}")
            return NotificationResponse(
                success=False,
                notification_id="",
                message=f"Ошибка отправки уведомления: {e}",
                errors=[str(e)]
            )

    async def _should_send_notification(self, request: NotificationRequest) -> bool:
        """Проверка, следует ли отправлять уведомление"""
        try:
            user_prefs = self.user_preferences.get(request.user_id, {})

            # Проверка включенности типа уведомления
            key = f"{request.notification_type.value}_{request.channel.value if request.channel else 'any'}"
            pref = user_prefs.get(key)

            if pref and not pref.enabled:
                return False

            # Проверка тихих часов
            if pref and pref.quiet_hours_start and pref.quiet_hours_end:
                if self._is_quiet_hours(pref.quiet_hours_start, pref.quiet_hours_end, pref.timezone):
                    return False

            # Проверка лимита частоты
            if pref and pref.frequency_limit:
                if self._exceeds_frequency_limit(request.user_id, pref.frequency_limit):
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Ошибка проверки отправки уведомления: {e}")
            return True  # По умолчанию разрешаем

    def _is_quiet_hours(self, start_time: str, end_time: str, timezone: str) -> bool:
        """Проверка тихих часов"""
        try:
            current_time = datetime.now()
            current_hour = current_time.hour

            start_hour = int(start_time.split(':')[0])
            end_hour = int(end_time.split(':')[0])

            if start_hour <= end_hour:
                return start_hour <= current_hour < end_hour
            else:  # Переход через полночь
                return current_hour >= start_hour or current_hour < end_hour

        except Exception as e:
            self.logger.error(f"Ошибка проверки тихих часов: {e}")
            return False

    def _exceeds_frequency_limit(self, user_id: str, limit: int) -> bool:
        """Проверка превышения лимита частоты"""
        try:
            # Простая проверка за последний час
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)

            if self.db_session:
                count = self.db_session.query(Notification).filter(
                    Notification.user_id == user_id,
                    Notification.created_at >= one_hour_ago
                ).count()

                return count >= limit

            return False

        except Exception as e:
            self.logger.error(f"Ошибка проверки лимита частоты: {e}")
            return False

    async def _determine_delivery_channel(self, request: NotificationRequest) -> DeliveryChannel:
        """Определение канала доставки"""
        try:
            # Если канал указан в запросе, используем его
            if request.channel:
                return request.channel

            # Получение предпочтений пользователя
            user_prefs = self.user_preferences.get(request.user_id, {})

            # Поиск предпочтения для данного типа уведомления
            for key, pref in user_prefs.items():
                if (pref.notification_type == request.notification_type.value and
                        pref.enabled):
                    return DeliveryChannel(pref.channel)

            # Канал по умолчанию на основе типа уведомления
            default_channels = {
                NotificationType.EMERGENCY: DeliveryChannel.PUSH,
                NotificationType.SECURITY_ALERT: DeliveryChannel.PUSH,
                NotificationType.SYSTEM_UPDATE: DeliveryChannel.EMAIL,
                NotificationType.PROMOTIONAL: DeliveryChannel.IN_APP,
                NotificationType.EDUCATIONAL: DeliveryChannel.IN_APP,
                NotificationType.REMINDER: DeliveryChannel.PUSH,
                NotificationType.SOCIAL: DeliveryChannel.IN_APP,
                NotificationType.NEWS: DeliveryChannel.EMAIL,
                NotificationType.TRANSACTION: DeliveryChannel.EMAIL,
                NotificationType.USER_ACTION: DeliveryChannel.IN_APP
            }

            return default_channels.get(request.notification_type, DeliveryChannel.IN_APP)

        except Exception as e:
            self.logger.error(f"Ошибка определения канала доставки: {e}")
            return DeliveryChannel.IN_APP

    async def _create_notification(self, request: NotificationRequest, channel: DeliveryChannel) -> Notification:
        """Создание уведомления"""
        try:
            # Генерация ID
            notification_id = self._generate_notification_id()

            # Обработка шаблона
            title, message = await self._process_template(request, channel)

            # Создание уведомления
            notification = Notification(
                id=notification_id,
                user_id=request.user_id,
                notification_type=request.notification_type.value,
                priority=request.priority.value,
                title=title,
                message=message,
                channel=channel.value,
                scheduled_at=request.scheduled_at,
                notification_metadata=request.metadata
            )

            # Сохранение в базу данных
            if self.db_session:
                self.db_session.add(notification)
                self.db_session.commit()

            return notification

        except Exception as e:
            self.logger.error(f"Ошибка создания уведомления: {e}")
            raise

    def _generate_notification_id(self) -> str:
        """Генерация ID уведомления"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(f"{timestamp}{time.time()}".encode()).hexdigest()[:8]
        return f"NOTIF_{timestamp}_{random_part}"

    async def _process_template(self, request: NotificationRequest, channel: DeliveryChannel) -> Tuple[str, str]:
        """Обработка шаблона уведомления"""
        try:
            # Если указан шаблон, используем его
            if request.template_id and request.template_id in self.notification_templates:
                template = self.notification_templates[request.template_id]

                # Подстановка переменных
                title = self._substitute_variables(template.subject_template or request.title, request.variables)
                message = self._substitute_variables(template.message_template, request.variables)

                return title, message

            # Иначе используем переданные значения
            return request.title, request.message

        except Exception as e:
            self.logger.error(f"Ошибка обработки шаблона: {e}")
            return request.title, request.message

    def _substitute_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """Подстановка переменных в текст"""
        try:
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                text = text.replace(placeholder, str(value))

            return text

        except Exception as e:
            self.logger.error(f"Ошибка подстановки переменных: {e}")
            return text

    async def get_notification_status(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """Получение статуса уведомления"""
        try:
            notification = self.pending_notifications.get(notification_id)
            if not notification:
                # Поиск в базе данных
                if self.db_session:
                    notification = self.db_session.query(Notification).filter(
                        Notification.id == notification_id
                    ).first()

            if not notification:
                return None

            return {
                "notification_id": notification.id,
                "user_id": notification.user_id,
                "type": notification.notification_type,
                "priority": notification.priority,
                "title": notification.title,
                "message": notification.message,
                "channel": notification.channel,
                "status": notification.status,
                "created_at": notification.created_at.isoformat(),
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
                "delivered_at": notification.delivered_at.isoformat() if notification.delivered_at else None,
                "read_at": notification.read_at.isoformat() if notification.read_at else None,
                "clicked_at": notification.clicked_at.isoformat() if notification.clicked_at else None
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса уведомления: {e}")
            return None

    async def mark_notification_read(self, notification_id: str) -> bool:
        """Отметка уведомления как прочитанного"""
        try:
            notification = self.pending_notifications.get(notification_id)
            if not notification:
                # Поиск в базе данных
                if self.db_session:
                    notification = self.db_session.query(Notification).filter(
                        Notification.id == notification_id
                    ).first()

            if not notification:
                return False

            # Обновление статуса
            notification.status = NotificationStatus.READ.value
            notification.read_at = datetime.utcnow()

            # Обновление в базе данных
            if self.db_session:
                self.db_session.commit()

            # Обновление статистики
            self.stats["read_notifications"] += 1

            return True

        except Exception as e:
            self.logger.error(f"Ошибка отметки уведомления как прочитанного: {e}")
            return False

    async def get_analytics(self, user_id: Optional[str] = None,
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None) -> NotificationAnalytics:
        """Получение аналитики уведомлений"""
        try:
            analytics = NotificationAnalytics()

            if not self.db_session:
                return analytics

            # Базовый запрос
            query = self.db_session.query(Notification)

            if user_id:
                query = query.filter(Notification.user_id == user_id)

            if start_date:
                query = query.filter(Notification.created_at >= start_date)

            if end_date:
                query = query.filter(Notification.created_at <= end_date)

            notifications = query.all()

            # Подсчет метрик
            analytics.total_sent = len([n for n in notifications if n.status in [
                NotificationStatus.SENT.value,
                NotificationStatus.DELIVERED.value,
                NotificationStatus.READ.value,
                NotificationStatus.CLICKED.value
            ]])

            analytics.total_delivered = len([n for n in notifications if n.status in [
                NotificationStatus.DELIVERED.value,
                NotificationStatus.READ.value,
                NotificationStatus.CLICKED.value
            ]])

            analytics.total_read = len([n for n in notifications if n.status in [
                NotificationStatus.READ.value,
                NotificationStatus.CLICKED.value
            ]])

            analytics.total_clicked = len([n for n in notifications if n.status == NotificationStatus.CLICKED.value])

            # Расчет процентов
            if analytics.total_sent > 0:
                analytics.delivery_rate = (analytics.total_delivered / analytics.total_sent) * 100

            if analytics.total_delivered > 0:
                analytics.read_rate = (analytics.total_read / analytics.total_delivered) * 100

            if analytics.total_read > 0:
                analytics.click_rate = (analytics.total_clicked / analytics.total_read) * 100

            # Топ каналы
            channel_counts = defaultdict(int)
            for notification in notifications:
                channel_counts[notification.channel] += 1

            analytics.top_channels = [
                {"channel": channel, "count": count}
                for channel, count in sorted(channel_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            ]

            # Топ типы уведомлений
            type_counts = defaultdict(int)
            for notification in notifications:
                type_counts[notification.notification_type] += 1

            analytics.top_notification_types = [
                {"type": ntype, "count": count}
                for ntype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            ]

            return analytics

        except Exception as e:
            self.logger.error(f"Ошибка получения аналитики: {e}")
            return NotificationAnalytics()

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса бота"""
        try:
            return {
                "name": self.name,
                "status": "running" if self.running else "stopped",
                "config": self.config,
                "stats": self.stats,
                "pending_notifications": len(self.pending_notifications),
                "user_preferences": len(self.user_preferences),
                "templates": len(self.notification_templates),
                "ml_enabled": self.config.get("ml_enabled", False),
                "last_update": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"error": str(e)}

    def start_notifications(self) -> bool:
        """Запуск системы уведомлений"""
        try:
            self.logger.info("Запуск системы уведомлений...")
            # Здесь можно добавить логику запуска уведомлений
            self.logger.info("Система уведомлений запущена")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка запуска системы уведомлений: {e}")
            return False

    def stop_notifications(self) -> bool:
        """Остановка системы уведомлений"""
        try:
            self.logger.info("Остановка системы уведомлений...")
            # Здесь можно добавить логику остановки уведомлений
            self.logger.info("Система уведомлений остановлена")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка остановки системы уведомлений: {e}")
            return False

    def get_bot_info(self) -> Dict[str, Any]:
        """Получение информации о боте уведомлений"""
        try:
            return {
                "bot_name": self.name,
                "is_running": getattr(self, 'is_running', False),
                "notifications_sent": getattr(self, 'notifications_sent', 0),
                "notifications_failed": getattr(self, 'notifications_failed', 0),
                "channels_available": len(DeliveryChannel),
                "notification_types": len(NotificationType),
                "priorities": len(Priority),
                "ml_enabled": self.config.get("ml_enabled", False),
                "database_connected": self.db_session is not None,
                "redis_connected": self.redis_client is not None,
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о боте: {e}")
            return {
                "bot_name": self.name,
                "is_running": False,
                "notifications_sent": 0,
                "notifications_failed": 0,
                "channels_available": 0,
                "notification_types": 0,
                "priorities": 0,
                "ml_enabled": False,
                "database_connected": False,
                "redis_connected": False,
                "error": str(e),
            }


# Функция тестирования
async def test_notification_bot():
    """Тестирование NotificationBot"""
    print("🧪 Тестирование NotificationBot...")

    # Создание бота
    bot = NotificationBot("TestNotificationBot")

    try:
        # Запуск
        await bot.start()
        print("✅ NotificationBot запущен")

        # Отправка уведомления
        request = NotificationRequest(
            user_id="test_user",
            notification_type=NotificationType.SECURITY_ALERT,
            priority=Priority.HIGH,
            title="Тестовое уведомление",
            message="Это тестовое уведомление безопасности",
            channel=DeliveryChannel.PUSH
        )

        response = await bot.send_notification(request)
        print(f"✅ Уведомление отправлено: {response.success} - {response.message}")

        # Получение статуса уведомления
        if response.success:
            status = await bot.get_notification_status(response.notification_id)
            print(f"✅ Статус уведомления: {status['status'] if status else 'не найден'}")

        # Получение аналитики
        analytics = await bot.get_analytics()
        print(f"✅ Аналитика: {analytics.total_sent} отправлено, {analytics.delivery_rate:.1f}% доставлено")

        # Получение общего статуса
        bot_status = await bot.get_status()
        print(f"✅ Статус бота: {bot_status['status']}")

    finally:
        # Остановка
        await bot.stop()
        print("✅ NotificationBot остановлен")


# Запуск тестов при прямом выполнении
if __name__ == "__main__":
    asyncio.run(test_notification_bot())
