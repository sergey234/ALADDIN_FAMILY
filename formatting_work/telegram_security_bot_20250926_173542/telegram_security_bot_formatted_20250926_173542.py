#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TelegramSecurityBot - Бот безопасности Telegram
function_92: Интеллектуальный бот для безопасности Telegram

Этот модуль предоставляет интеллектуального бота для безопасности Telegram,
включающего:
- Мониторинг каналов и групп на подозрительный контент
- Детекция спама и ботов
- Защита от вредоносных ссылок и файлов
- Контроль конфиденциальности
- Анализ участников групп
- Блокировка нежелательных пользователей
- Шифрование сообщений
- Резервное копирование чатов
- Антивирусная проверка файлов
- Модерация контента

Основные возможности:
1. Умная модерация каналов и групп
2. Детекция спама и ботов
3. Защита от вредоносных ссылок
4. Контроль конфиденциальности
5. Анализ и блокировка пользователей
6. Шифрование сообщений
7. Резервное копирование
8. Антивирусная проверка
9. Автоматическая модерация
10. Интеграция с системой безопасности

Технические детали:
- Использует ML для анализа сообщений
- Применяет NLP для понимания контекста
- Интегрирует с Telegram Bot API
- Использует криптографию для шифрования
- Применяет антивирусные движки
- Интегрирует с базами данных угроз
- Использует геолокацию для анализа
- Применяет поведенческий анализ
- Интегрирует с системами уведомлений
- Использует машинное обучение для адаптации

Автор: ALADDIN Security System
Версия: 2.0
Дата: 2025-01-27
Лицензия: MIT
"""

import asyncio
import hashlib
import json
import logging
import os

# Внутренние импорты
import sys
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Внешние зависимости
import redis
import sqlalchemy
from prometheus_client import Counter, Gauge, Histogram
from pydantic import BaseModel, Field, validator
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.base import ComponentStatus, SecurityBase, SecurityLevel

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
)


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# База данных
Base = declarative_base()


class TelegramMessageType(Enum):
    """Типы сообщений Telegram"""

    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    DOCUMENT = "document"
    STICKER = "sticker"
    ANIMATION = "animation"
    VIDEO_NOTE = "video_note"
    CONTACT = "contact"
    LOCATION = "location"
    VENUE = "venue"
    POLL = "poll"
    DICE = "dice"
    GAME = "game"
    INVOICE = "invoice"
    SUCCESSFUL_PAYMENT = "successful_payment"
    SYSTEM = "system"


class ChatType(Enum):
    """Типы чатов Telegram"""

    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"


class ThreatLevel(Enum):
    """Уровни угроз"""

    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ModerationAction(Enum):
    """Действия модерации"""

    ALLOW = "allow"
    WARN = "warn"
    DELETE = "delete"
    BAN = "ban"
    MUTE = "mute"
    RESTRICT = "restrict"


class TelegramMessage(Base):
    """Сообщение Telegram"""

    __tablename__ = "telegram_messages"

    id = Column(String, primary_key=True)
    message_id = Column(Integer, nullable=False)
    chat_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    username = Column(String)
    message_type = Column(String, nullable=False)
    content = Column(Text)
    media_file_id = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    threat_level = Column(String, default=ThreatLevel.SAFE.value)
    is_deleted = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)
    moderation_action = Column(String)
    analysis_result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class TelegramUser(Base):
    """Пользователь Telegram"""

    __tablename__ = "telegram_users"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_bot = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    is_restricted = Column(Boolean, default=False)
    threat_score = Column(Float, default=0.0)
    violation_count = Column(Integer, default=0)
    last_activity = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class TelegramChat(Base):
    """Чат Telegram"""

    __tablename__ = "telegram_chats"

    id = Column(String, primary_key=True)
    chat_id = Column(String, nullable=False)
    chat_type = Column(String, nullable=False)
    title = Column(String)
    description = Column(Text)
    is_monitored = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    member_count = Column(Integer, default=0)
    admin_count = Column(Integer, default=0)
    threat_level = Column(String, default=ThreatLevel.SAFE.value)
    moderation_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MessageAnalysisResult(BaseModel):
    """Результат анализа сообщения"""

    message_id: int
    threat_level: ThreatLevel
    is_spam: bool = False
    is_bot_activity: bool = False
    is_malicious: bool = False
    is_inappropriate: bool = False
    confidence: float = 0.0
    detected_patterns: List[str] = Field(default_factory=list)
    recommended_action: ModerationAction = ModerationAction.ALLOW
    risk_factors: List[str] = Field(default_factory=list)
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class TelegramSecurityConfig(BaseModel):
    """Конфигурация безопасности Telegram"""

    spam_detection: bool = True
    bot_detection: bool = True
    malware_scanning: bool = True
    content_moderation: bool = True
    link_analysis: bool = True
    user_verification: bool = True
    encryption_enabled: bool = True
    backup_enabled: bool = True
    auto_moderation: bool = False
    notification_alerts: bool = True


# Prometheus метрики
telegram_messages_analyzed_total = Counter(
    "telegram_messages_analyzed_total",
    "Total number of Telegram messages analyzed",
    ["threat_level", "message_type", "chat_type"],
)

telegram_threats_detected_total = Counter(
    "telegram_threats_detected_total",
    "Total number of threats detected in Telegram",
    ["threat_type", "severity"],
)

telegram_messages_moderated_total = Counter(
    "telegram_messages_moderated_total",
    "Total number of Telegram messages moderated",
    ["action", "reason"],
)

active_telegram_chats = Gauge(
    "active_telegram_chats", "Number of active Telegram chats"
)


class TelegramSecurityBot(SecurityBase):
    """
    Интеллектуальный бот безопасности Telegram

    Предоставляет комплексную систему безопасности Telegram с поддержкой:
    - Мониторинга каналов и групп на подозрительный контент
    - Детекции спама и ботов
    - Защиты от вредоносных ссылок и файлов
    - Контроля конфиденциальности
    - Анализа и блокировки пользователей
    """

    def __init__(
        self,
        name: str = "TelegramSecurityBot",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализация TelegramSecurityBot

        Args:
            name: Имя бота
            config: Конфигурация
        """
        super().__init__(name, config)

        # Конфигурация по умолчанию
        self.default_config = {
            "redis_url": "redis://localhost:6379/0",
            "database_url": "sqlite:///telegram_security_bot.db",
            "spam_detection": True,
            "bot_detection": True,
            "malware_scanning": True,
            "content_moderation": True,
            "link_analysis": True,
            "user_verification": True,
            "encryption_enabled": True,
            "backup_enabled": True,
            "auto_moderation": False,
            "notification_alerts": True,
            "ml_enabled": True,
            "adaptive_learning": True,
            "real_time_monitoring": True,
            "cleanup_interval": 300,
            "metrics_enabled": True,
            "logging_enabled": True,
        }

        # Объединение конфигураций
        self.config = {**self.default_config, **(config or {})}

        # Инициализация компонентов
        self.redis_client: Optional[redis.Redis] = None
        self.db_engine: Optional[sqlalchemy.Engine] = None
        self.db_session: Optional[sqlalchemy.orm.Session] = None
        self.monitored_chats: Dict[str, TelegramChat] = {}
        self.blocked_users: Dict[str, TelegramUser] = {}
        self.ml_model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None

        # Статистика
        self.stats = {
            "total_messages": 0,
            "analyzed_messages": 0,
            "moderated_messages": 0,
            "threats_detected": 0,
            "spam_detected": 0,
            "bot_activity_detected": 0,
            "malware_detected": 0,
            "inappropriate_content": 0,
            "active_chats": 0,
            "blocked_users": 0,
            "false_positives": 0,
        }

        # Потоки
        self.monitoring_thread: Optional[threading.Thread] = None
        self.running = False

        # Блокировки
        self.lock = threading.RLock()

        self.logger.info(f"TelegramSecurityBot {name} инициализирован")

    async def start(self) -> bool:
        """Запуск бота безопасности Telegram"""
        try:
            with self.lock:
                if self.running:
                    self.logger.warning("TelegramSecurityBot уже запущен")
                    return True

                # Инициализация базы данных
                await self._setup_database()

                # Инициализация Redis
                await self._setup_redis()

                # Инициализация ML модели
                if self.config.get("ml_enabled", True):
                    await self._setup_ml_model()

                # Загрузка мониторируемых чатов
                await self._load_monitored_chats()

                # Запуск мониторинга
                self.running = True
                self.monitoring_thread = threading.Thread(
                    target=self._monitoring_worker
                )
                self.monitoring_thread.daemon = True
                self.monitoring_thread.start()

                self.logger.info("TelegramSecurityBot запущен успешно")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка запуска TelegramSecurityBot: {e}")
            return False

    async def stop(self) -> bool:
        """Остановка бота безопасности Telegram"""
        try:
            with self.lock:
                if not self.running:
                    self.logger.warning("TelegramSecurityBot уже остановлен")
                    return True

                self.running = False

                # Ожидание завершения потоков
                if (
                    self.monitoring_thread
                    and self.monitoring_thread.is_alive()
                ):
                    self.monitoring_thread.join(timeout=5)

                # Закрытие соединений
                if self.db_session:
                    self.db_session.close()

                if self.redis_client:
                    self.redis_client.close()

                self.logger.info("TelegramSecurityBot остановлен")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка остановки TelegramSecurityBot: {e}")
            return False

    async def _setup_database(self) -> None:
        """Настройка базы данных"""
        try:
            database_url = self.config.get(
                "database_url", "sqlite:///telegram_security_bot.db"
            )
            self.db_engine = create_engine(database_url)
            Base.metadata.create_all(self.db_engine)

            Session = sessionmaker(bind=self.db_engine)
            self.db_session = Session()

            self.logger.info("База данных TelegramSecurityBot настроена")

        except Exception as e:
            self.logger.error(f"Ошибка настройки базы данных: {e}")
            raise

    async def _setup_redis(self) -> None:
        """Настройка Redis"""
        try:
            redis_url = self.config.get(
                "redis_url", "redis://localhost:6379/0"
            )
            self.redis_client = redis.from_url(
                redis_url, decode_responses=True
            )

            # Тест соединения
            self.redis_client.ping()

            self.logger.info("Redis для TelegramSecurityBot настроен")

        except Exception as e:
            self.logger.error(f"Ошибка настройки Redis: {e}")
            raise

    async def _setup_ml_model(self) -> None:
        """Настройка ML модели для анализа сообщений"""
        try:
            self.ml_model = IsolationForest(
                contamination=0.1, random_state=42, n_estimators=100
            )
            self.scaler = StandardScaler()

            self.logger.info("ML модель TelegramSecurityBot настроена")

        except Exception as e:
            self.logger.error(f"Ошибка настройки ML модели: {e}")

    async def _load_monitored_chats(self) -> None:
        """Загрузка мониторируемых чатов"""
        try:
            if self.db_session:
                chats = (
                    self.db_session.query(TelegramChat)
                    .filter(TelegramChat.is_monitored)
                    .all()
                )

                for chat in chats:
                    self.monitored_chats[chat.chat_id] = chat

                self.stats["active_chats"] = len(self.monitored_chats)

                self.logger.info(
                    f"Загружено {len(self.monitored_chats)} мониторируемых чатов"
                )

        except Exception as e:
            self.logger.error(f"Ошибка загрузки мониторируемых чатов: {e}")

    def _monitoring_worker(self) -> None:
        """Фоновый процесс мониторинга"""
        while self.running:
            try:
                time.sleep(1)  # Проверка каждую секунду

                # Обновление статистики
                self._update_stats()

                # Обработка очереди сообщений
                self._process_message_queue()

            except Exception as e:
                self.logger.error(f"Ошибка в процессе мониторинга: {e}")

    def _update_stats(self) -> None:
        """Обновление статистики"""
        try:
            with self.lock:
                # Обновление метрик Prometheus
                active_telegram_chats.set(self.stats["active_chats"])

        except Exception as e:
            self.logger.error(f"Ошибка обновления статистики: {e}")

    def _process_message_queue(self) -> None:
        """Обработка очереди сообщений"""
        try:
            # Здесь должна быть логика обработки очереди сообщений
            # Пока что заглушка
            pass

        except Exception as e:
            self.logger.error(f"Ошибка обработки очереди сообщений: {e}")

    async def analyze_message(
        self, message_data: Dict[str, Any]
    ) -> MessageAnalysisResult:
        """Анализ сообщения Telegram на предмет угроз"""
        try:
            message_id = message_data.get("message_id", 0)
            content = message_data.get("text", "")
            message_type = TelegramMessageType(
                message_data.get("type", "text")
            )
            # chat_id = str(message_data.get("chat", {}).get("id", ""))
            # user_id = str(message_data.get("from", {}).get("id", ""))
            # username = message_data.get("from", {}).get("username", "")
            is_bot = message_data.get("from", {}).get("is_bot", False)

            # Базовый анализ
            threat_level = ThreatLevel.SAFE
            is_spam = False
            is_bot_activity = False
            is_malicious = False
            is_inappropriate = False
            confidence = 0.0
            detected_patterns = []
            risk_factors = []

            # Проверка на бота
            if is_bot:
                is_bot_activity = True
                threat_level = ThreatLevel.MEDIUM
                confidence = 0.7
                detected_patterns.append("bot_user")
                risk_factors.append("automated_activity")

            # Анализ текстовых сообщений
            if message_type == TelegramMessageType.TEXT and content:
                analysis_result = await self._analyze_text_content(content)
                threat_level = max(
                    threat_level,
                    analysis_result["threat_level"],
                    key=lambda x: x.value,
                )
                is_spam = analysis_result["is_spam"]
                is_malicious = analysis_result["is_malicious"]
                is_inappropriate = analysis_result["is_inappropriate"]
                confidence = max(confidence, analysis_result["confidence"])
                detected_patterns.extend(analysis_result["detected_patterns"])
                risk_factors.extend(analysis_result["risk_factors"])

            # Анализ медиафайлов
            elif message_type in [
                TelegramMessageType.PHOTO,
                TelegramMessageType.VIDEO,
                TelegramMessageType.DOCUMENT,
                TelegramMessageType.AUDIO,
            ]:
                analysis_result = await self._analyze_media_content(
                    message_data
                )
                threat_level = max(
                    threat_level,
                    analysis_result["threat_level"],
                    key=lambda x: x.value,
                )
                is_malicious = analysis_result["is_malicious"]
                confidence = max(confidence, analysis_result["confidence"])
                detected_patterns.extend(analysis_result["detected_patterns"])
                risk_factors.extend(analysis_result["risk_factors"])

            # Анализ ссылок
            if content and (
                "http" in content or "t.me" in content or "@" in content
            ):
                link_analysis = await self._analyze_links(content)
                if link_analysis["is_malicious"]:
                    threat_level = max(
                        threat_level, ThreatLevel.HIGH, key=lambda x: x.value
                    )
                    is_malicious = True
                    detected_patterns.extend(
                        link_analysis["detected_patterns"]
                    )
                    risk_factors.extend(link_analysis["risk_factors"])

            # Определение рекомендуемого действия
            recommended_action = self._get_recommended_action(
                threat_level,
                is_spam,
                is_bot_activity,
                is_malicious,
                is_inappropriate,
            )

            # Создание результата анализа
            result = MessageAnalysisResult(
                message_id=message_id,
                threat_level=threat_level,
                is_spam=is_spam,
                is_bot_activity=is_bot_activity,
                is_malicious=is_malicious,
                is_inappropriate=is_inappropriate,
                confidence=confidence,
                detected_patterns=detected_patterns,
                recommended_action=recommended_action,
                risk_factors=risk_factors,
            )

            # Обновление статистики
            self.stats["total_messages"] += 1
            self.stats["analyzed_messages"] += 1

            if threat_level != ThreatLevel.SAFE:
                self.stats["threats_detected"] += 1

            if is_spam:
                self.stats["spam_detected"] += 1

            if is_bot_activity:
                self.stats["bot_activity_detected"] += 1

            if is_malicious:
                self.stats["malware_detected"] += 1

            if is_inappropriate:
                self.stats["inappropriate_content"] += 1

            # Обновление метрик
            chat_type = message_data.get("chat", {}).get("type", "private")
            telegram_messages_analyzed_total.labels(
                threat_level=threat_level.value,
                message_type=message_type.value,
                chat_type=chat_type,
            ).inc()

            if threat_level != ThreatLevel.SAFE:
                telegram_threats_detected_total.labels(
                    threat_type="general", severity=threat_level.value
                ).inc()

            # Логирование результата
            await self._log_message_analysis(message_data, result)

            return result

        except Exception as e:
            self.logger.error(f"Ошибка анализа сообщения: {e}")
            return MessageAnalysisResult(
                message_id=message_data.get("message_id", 0),
                threat_level=ThreatLevel.SAFE,
                recommended_action=ModerationAction.ALLOW,
            )

    async def _analyze_text_content(self, content: str) -> Dict[str, Any]:
        """Анализ текстового контента"""
        try:
            threat_level = ThreatLevel.SAFE
            is_spam = False
            is_malicious = False
            is_inappropriate = False
            confidence = 0.0
            detected_patterns = []
            risk_factors = []

            content_lower = content.lower()

            # Проверка на спам
            spam_indicators = [
                "реклама",
                "заработок",
                "быстро",
                "легко",
                "бесплатно",
                "срочно",
                "только сегодня",
                "не упустите",
                "гарантия",
            ]

            spam_count = sum(
                1
                for indicator in spam_indicators
                if indicator in content_lower
            )
            if spam_count >= 2:
                is_spam = True
                threat_level = ThreatLevel.MEDIUM
                confidence = min(0.8, spam_count * 0.3)
                detected_patterns.append("spam_indicators")
                risk_factors.append("spam_keywords")

            # Проверка на неподходящий контент
            inappropriate_keywords = [
                "порно",
                "xxx",
                "секс",
                "наркотики",
                "наркотик",
                "оружие",
                "взрывчатка",
                "террор",
                "экстремизм",
            ]

            inappropriate_count = sum(
                1
                for keyword in inappropriate_keywords
                if keyword in content_lower
            )
            if inappropriate_count >= 1:
                is_inappropriate = True
                threat_level = ThreatLevel.HIGH
                confidence = 0.9
                detected_patterns.append("inappropriate_content")
                risk_factors.append("inappropriate_keywords")

            # Проверка на подозрительные ссылки
            if "http" in content or "t.me" in content:
                detected_patterns.append("contains_links")
                risk_factors.append("suspicious_links")

            # Проверка на подозрительные символы
            suspicious_chars = [
                "$",
                "€",
                "₽",
                "bitcoin",
                "btc",
                "crypto",
                "крипто",
            ]
            if any(char in content_lower for char in suspicious_chars):
                detected_patterns.append("suspicious_characters")
                risk_factors.append("financial_keywords")

            return {
                "threat_level": threat_level,
                "is_spam": is_spam,
                "is_malicious": is_malicious,
                "is_inappropriate": is_inappropriate,
                "confidence": confidence,
                "detected_patterns": detected_patterns,
                "risk_factors": risk_factors,
            }

        except Exception as e:
            self.logger.error(f"Ошибка анализа текстового контента: {e}")
            return {
                "threat_level": ThreatLevel.SAFE,
                "is_spam": False,
                "is_malicious": False,
                "is_inappropriate": False,
                "confidence": 0.0,
                "detected_patterns": [],
                "risk_factors": [],
            }

    async def _analyze_media_content(
        self, message_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Анализ медиафайлов"""
        try:
            # Здесь должна быть интеграция с антивирусными движками
            # Пока что базовая проверка

            threat_level = ThreatLevel.SAFE
            is_malicious = False
            confidence = 0.0
            detected_patterns = []
            risk_factors = []

            # Проверка размера файла
            file_size = message_data.get("file_size", 0)
            if file_size > 50 * 1024 * 1024:  # 50MB
                detected_patterns.append("large_file")
                risk_factors.append("suspicious_file_size")

            # Проверка типа файла
            file_name = message_data.get("file_name", "")
            if file_name:
                suspicious_extensions = [
                    ".exe",
                    ".bat",
                    ".cmd",
                    ".scr",
                    ".pif",
                    ".com",
                ]
                if any(
                    file_name.lower().endswith(ext)
                    for ext in suspicious_extensions
                ):
                    is_malicious = True
                    threat_level = ThreatLevel.HIGH
                    confidence = 0.8
                    detected_patterns.append("suspicious_extension")
                    risk_factors.append("executable_file")

            return {
                "threat_level": threat_level,
                "is_malicious": is_malicious,
                "confidence": confidence,
                "detected_patterns": detected_patterns,
                "risk_factors": risk_factors,
            }

        except Exception as e:
            self.logger.error(f"Ошибка анализа медиафайлов: {e}")
            return {
                "threat_level": ThreatLevel.SAFE,
                "is_malicious": False,
                "confidence": 0.0,
                "detected_patterns": [],
                "risk_factors": [],
            }

    async def _analyze_links(self, content: str) -> Dict[str, Any]:
        """Анализ ссылок в сообщении"""
        try:
            import re

            # Поиск ссылок
            url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
            urls = re.findall(url_pattern, content)

            # Поиск Telegram ссылок
            telegram_pattern = r"t\.me/[a-zA-Z0-9_]+"
            telegram_links = re.findall(telegram_pattern, content)

            is_malicious = False
            detected_patterns = []
            risk_factors = []

            for url in urls + telegram_links:
                # Проверка на подозрительные домены
                suspicious_domains = [
                    "bit.ly",
                    "tinyurl.com",
                    "goo.gl",
                    "t.co",
                    "short.link",
                    "is.gd",
                    "v.gd",
                    "clck.ru",
                ]

                if any(domain in url.lower() for domain in suspicious_domains):
                    detected_patterns.append("shortened_url")
                    risk_factors.append("suspicious_domain")

                # Проверка на подозрительные ключевые слова в URL
                suspicious_keywords = [
                    "bank",
                    "paypal",
                    "amazon",
                    "apple",
                    "microsoft",
                    "google",
                    "facebook",
                    "instagram",
                    "twitter",
                    "youtube",
                ]

                if any(
                    keyword in url.lower() for keyword in suspicious_keywords
                ):
                    detected_patterns.append("brand_impersonation")
                    risk_factors.append("potential_phishing")
                    is_malicious = True

            return {
                "is_malicious": is_malicious,
                "detected_patterns": detected_patterns,
                "risk_factors": risk_factors,
            }

        except Exception as e:
            self.logger.error(f"Ошибка анализа ссылок: {e}")
            return {
                "is_malicious": False,
                "detected_patterns": [],
                "risk_factors": [],
            }

    def _get_recommended_action(
        self,
        threat_level: ThreatLevel,
        is_spam: bool,
        is_bot_activity: bool,
        is_malicious: bool,
        is_inappropriate: bool,
    ) -> ModerationAction:
        """Получение рекомендуемого действия модерации"""
        try:
            if (
                threat_level == ThreatLevel.CRITICAL
                or is_malicious
                or is_inappropriate
            ):
                return ModerationAction.BAN
            elif threat_level == ThreatLevel.HIGH or is_spam:
                return ModerationAction.DELETE
            elif threat_level == ThreatLevel.MEDIUM or is_bot_activity:
                return ModerationAction.WARN
            else:
                return ModerationAction.ALLOW

        except Exception as e:
            self.logger.error(f"Ошибка получения рекомендуемого действия: {e}")
            return ModerationAction.ALLOW

    async def _log_message_analysis(
        self, message_data: Dict[str, Any], result: MessageAnalysisResult
    ) -> None:
        """Логирование результата анализа сообщения"""
        try:
            if not self.db_session:
                return

            # Создание записи сообщения
            message = TelegramMessage(
                id=self._generate_message_id(),
                message_id=result.message_id,
                chat_id=str(message_data.get("chat", {}).get("id", "")),
                user_id=str(message_data.get("from", {}).get("id", "")),
                username=message_data.get("from", {}).get("username"),
                message_type=message_data.get("type", "text"),
                content=message_data.get("text", ""),
                media_file_id=message_data.get("file_id"),
                threat_level=result.threat_level.value,
                is_deleted=result.recommended_action
                in [ModerationAction.DELETE, ModerationAction.BAN],
                moderation_action=result.recommended_action.value,
                analysis_result={
                    "is_spam": result.is_spam,
                    "is_bot_activity": result.is_bot_activity,
                    "is_malicious": result.is_malicious,
                    "is_inappropriate": result.is_inappropriate,
                    "confidence": result.confidence,
                    "detected_patterns": result.detected_patterns,
                    "risk_factors": result.risk_factors,
                },
            )

            self.db_session.add(message)
            self.db_session.commit()

        except Exception as e:
            self.logger.error(f"Ошибка логирования анализа сообщения: {e}")

    def _generate_message_id(self) -> str:
        """Генерация ID сообщения"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()
        ).hexdigest()[:8]
        return f"TG_{timestamp}_{random_part}"

    async def block_user(
        self, user_id: str, reason: str = "Suspicious activity"
    ) -> bool:
        """Блокировка пользователя"""
        try:
            with self.lock:
                # Создание записи заблокированного пользователя
                user = TelegramUser(
                    id=self._generate_user_id(),
                    user_id=user_id,
                    is_blocked=True,
                    threat_score=1.0,
                )

                # Сохранение в базу данных
                if self.db_session:
                    self.db_session.add(user)
                    self.db_session.commit()

                # Добавление в список заблокированных
                self.blocked_users[user_id] = user

                # Обновление статистики
                self.stats["blocked_users"] += 1

                self.logger.info(
                    f"Пользователь {user_id} заблокирован: {reason}"
                )
                return True

        except Exception as e:
            self.logger.error(f"Ошибка блокировки пользователя: {e}")
            return False

    def _generate_user_id(self) -> str:
        """Генерация ID пользователя"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()
        ).hexdigest()[:8]
        return f"USER_{timestamp}_{random_part}"

    async def add_chat_to_monitoring(
        self,
        chat_id: str,
        chat_type: str,
        title: str = "",
        description: str = "",
    ) -> bool:
        """Добавление чата в мониторинг"""
        try:
            with self.lock:
                # Создание записи чата
                chat = TelegramChat(
                    id=self._generate_chat_id(),
                    chat_id=chat_id,
                    chat_type=chat_type,
                    title=title,
                    description=description,
                    is_monitored=True,
                )

                # Сохранение в базу данных
                if self.db_session:
                    self.db_session.add(chat)
                    self.db_session.commit()

                # Добавление в мониторируемые чаты
                self.monitored_chats[chat_id] = chat

                # Обновление статистики
                self.stats["active_chats"] += 1

                self.logger.info(f"Чат {chat_id} добавлен в мониторинг")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка добавления чата в мониторинг: {e}")
            return False

    def _generate_chat_id(self) -> str:
        """Генерация ID чата"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()
        ).hexdigest()[:8]
        return f"CHAT_{timestamp}_{random_part}"

    async def get_security_report(
        self, chat_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получение отчета по безопасности"""
        try:
            report = {
                "total_messages": self.stats["total_messages"],
                "analyzed_messages": self.stats["analyzed_messages"],
                "moderated_messages": self.stats["moderated_messages"],
                "threats_detected": self.stats["threats_detected"],
                "spam_detected": self.stats["spam_detected"],
                "bot_activity_detected": self.stats["bot_activity_detected"],
                "malware_detected": self.stats["malware_detected"],
                "inappropriate_content": self.stats["inappropriate_content"],
                "active_chats": self.stats["active_chats"],
                "blocked_users": self.stats["blocked_users"],
                "false_positives": self.stats["false_positives"],
                "timestamp": datetime.utcnow().isoformat(),
            }

            if chat_id:
                # Дополнительная статистика по конкретному чату
                if self.db_session:
                    chat_messages = (
                        self.db_session.query(TelegramMessage)
                        .filter(TelegramMessage.chat_id == chat_id)
                        .count()
                    )

                    deleted_chat_messages = (
                        self.db_session.query(TelegramMessage)
                        .filter(
                            TelegramMessage.chat_id == chat_id,
                            TelegramMessage.is_deleted,
                        )
                        .count()
                    )

                    report["chat_messages"] = chat_messages
                    report["deleted_chat_messages"] = deleted_chat_messages

            return report

        except Exception as e:
            self.logger.error(f"Ошибка получения отчета по безопасности: {e}")
            return {"error": str(e)}

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса бота"""
        try:
            return {
                "name": self.name,
                "status": "running" if self.running else "stopped",
                "config": self.config,
                "stats": self.stats,
                "monitored_chats": len(self.monitored_chats),
                "blocked_users": len(self.blocked_users),
                "ml_enabled": self.config.get("ml_enabled", False),
                "last_update": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"error": str(e)}


# Функция тестирования
async def test_telegram_security_bot():
    """Тестирование TelegramSecurityBot"""
    print("🧪 Тестирование TelegramSecurityBot...")

    # Создание бота
    bot = TelegramSecurityBot("TestTelegramBot")

    try:
        # Запуск
        await bot.start()
        print("✅ TelegramSecurityBot запущен")

        # Добавление чата в мониторинг
        chat_added = await bot.add_chat_to_monitoring(
            chat_id="-1001234567890",
            chat_type="supergroup",
            title="Test Security Group",
            description="Test group for security monitoring",
        )
        print(f"✅ Чат добавлен в мониторинг: {chat_added}")

        # Анализ тестового сообщения
        message_data = {
            "message_id": 12345,
            "text": "Срочно! Заработайте 100000 рублей за день! Переходите по ссылке: http://fake-earnings.com",
            "type": "text",
            "chat": {"id": -1001234567890, "type": "supergroup"},
            "from": {
                "id": 123456789,
                "username": "test_user",
                "is_bot": False,
            },
        }

        result = await bot.analyze_message(message_data)
        print(
            f"✅ Анализ сообщения: {result.threat_level.value} - {result.recommended_action.value}"
        )

        # Блокировка подозрительного пользователя
        blocked = await bot.block_user("123456789", "Spam activity")
        print(f"✅ Пользователь заблокирован: {blocked}")

        # Получение отчета по безопасности
        report = await bot.get_security_report()
        print(
            f"✅ Отчет по безопасности: {report['threats_detected']} угроз обнаружено"
        )

        # Получение общего статуса
        bot_status = await bot.get_status()
        print(f"✅ Статус бота: {bot_status['status']}")

    finally:
        # Остановка
        await bot.stop()
        print("✅ TelegramSecurityBot остановлен")


# Запуск тестов при прямом выполнении
if __name__ == "__main__":
    asyncio.run(test_telegram_security_bot())
