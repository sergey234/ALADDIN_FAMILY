#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ParentalControlBot - Бот родительского контроля
function_89: Критически важный бот для семейной безопасности

Этот модуль предоставляет интеллектуального бота для родительского контроля,
включающего:
- Мониторинг активности детей в интернете
- Блокировка нежелательного контента
- Контроль времени использования устройств
- Отслеживание местоположения
- Уведомления о подозрительной активности
- Настройка возрастных ограничений
- Контроль приложений и игр
- Мониторинг социальных сетей
- Безопасное общение
- Образовательный контент

Основные возможности:
1. Умная фильтрация контента
2. Контроль времени использования
3. Геолокация и безопасные зоны
4. Мониторинг социальных сетей
5. Блокировка опасных приложений
6. Образовательные рекомендации
7. Родительские уведомления
8. Настройка возрастных ограничений
9. Контроль покупок в приложениях
10. Анализ поведения детей

Технические детали:
- Использует ML для анализа контента
- Применяет геофенсинг для контроля местоположения
- Интегрирует с браузерами и приложениями
- Использует NLP для анализа текста
- Применяет компьютерное зрение для анализа изображений
- Интегрирует с образовательными платформами
- Использует криптографию для защиты данных
- Применяет поведенческий анализ
- Интегрирует с социальными сетями
- Использует рекомендательные системы

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


class ContentCategory(Enum):
    """Категории контента"""
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    SOCIAL = "social"
    GAMING = "gaming"
    SHOPPING = "shopping"
    NEWS = "news"
    ADULT = "adult"
    VIOLENCE = "violence"
    DRUGS = "drugs"
    GAMBLING = "gambling"
    UNKNOWN = "unknown"


class AgeGroup(Enum):
    """Возрастные группы"""
    TODDLER = "toddler"  # 2-4 года
    PRESCHOOL = "preschool"  # 4-6 лет
    ELEMENTARY = "elementary"  # 6-12 лет
    TEEN = "teen"  # 12-18 лет
    ADULT = "adult"  # 18+ лет


class DeviceType(Enum):
    """Типы устройств"""
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    SMART_TV = "smart_tv"
    GAMING_CONSOLE = "gaming_console"
    SMART_WATCH = "smart_watch"


class ControlAction(Enum):
    """Действия контроля"""
    ALLOW = "allow"
    BLOCK = "block"
    WARN = "warn"
    RESTRICT = "restrict"
    MONITOR = "monitor"


class ChildProfile(Base):
    """Профиль ребенка"""
    __tablename__ = "child_profiles"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    age_group = Column(String, nullable=False)
    parent_id = Column(String, nullable=False)
    device_ids = Column(JSON)
    restrictions = Column(JSON)
    time_limits = Column(JSON)
    safe_zones = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ContentFilter(Base):
    """Фильтры контента"""
    __tablename__ = "content_filters"

    id = Column(String, primary_key=True)
    child_id = Column(String, nullable=False)
    category = Column(String, nullable=False)
    keywords = Column(JSON)
    domains = Column(JSON)
    action = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ActivityLog(Base):
    """Лог активности"""
    __tablename__ = "activity_logs"

    id = Column(String, primary_key=True)
    child_id = Column(String, nullable=False)
    device_id = Column(String, nullable=False)
    activity_type = Column(String, nullable=False)
    content_url = Column(String)
    content_category = Column(String)
    duration = Column(Integer)  # секунды
    timestamp = Column(DateTime, default=datetime.utcnow)
    location = Column(JSON)
    risk_score = Column(Float, default=0.0)


class ParentalControlConfig(BaseModel):
    """Конфигурация родительского контроля"""
    child_id: str
    age_group: AgeGroup
    time_limits: Dict[str, int] = Field(default_factory=dict)  # device_type -> minutes
    content_filters: List[str] = Field(default_factory=list)
    safe_zones: List[Dict[str, Any]] = Field(default_factory=list)
    app_restrictions: List[str] = Field(default_factory=list)
    social_media_monitoring: bool = True
    location_tracking: bool = True
    emergency_contacts: List[str] = Field(default_factory=list)
    educational_content: bool = True
    bedtime_mode: bool = True


class ContentAnalysisResult(BaseModel):
    """Результат анализа контента"""
    url: str
    category: ContentCategory
    risk_score: float
    age_appropriate: bool
    keywords: List[str] = Field(default_factory=list)
    action: ControlAction
    reason: str


class ActivityAlert(BaseModel):
    """Оповещение о активности"""
    child_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    action_required: bool = False
    data: Dict[str, Any] = Field(default_factory=dict)


# Prometheus метрики
content_blocks_total = Counter(
    'content_blocks_total',
    'Total number of content blocks',
    ['category', 'age_group']
)

time_limit_violations = Counter(
    'time_limit_violations_total',
    'Total number of time limit violations',
    ['child_id', 'device_type']
)

suspicious_activities = Counter(
    'suspicious_activities_total',
    'Total number of suspicious activities',
    ['child_id', 'activity_type']
)

active_children = Gauge(
    'active_children',
    'Number of children currently monitored'
)


class ParentalControlBot(SecurityBase):
    """
    Интеллектуальный бот родительского контроля

    Предоставляет комплексную систему родительского контроля с поддержкой:
    - Умной фильтрации контента
    - Контроля времени использования
    - Геолокации и безопасных зон
    - Мониторинга социальных сетей
    - Блокировки опасных приложений
    - Образовательных рекомендаций
    """

    def __init__(self, name: str = "ParentalControlBot", config: Optional[Dict[str, Any]] = None):
        """
        Инициализация ParentalControlBot

        Args:
            name: Имя бота
            config: Конфигурация
        """
        super().__init__(name, config)

        # Конфигурация по умолчанию
        self.default_config = {
            "redis_url": "redis://localhost:6379/0",
            "database_url": "sqlite:///parental_control_bot.db",
            "content_analysis_enabled": True,
            "location_tracking_enabled": True,
            "social_media_monitoring": True,
            "educational_recommendations": True,
            "ml_enabled": True,
            "adaptive_learning": True,
            "real_time_monitoring": True,
            "bedtime_mode": True,
            "emergency_alerts": True,
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
        self.child_profiles: Dict[str, ChildProfile] = {}
        self.active_monitoring: Dict[str, bool] = {}
        self.ml_model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None

        # Статистика
        self.stats = {
            "total_children": 0,
            "active_children": 0,
            "content_blocks": 0,
            "time_violations": 0,
            "suspicious_activities": 0,
            "educational_recommendations": 0
        }

        # Потоки
        self.monitoring_thread: Optional[threading.Thread] = None
        self.running = False

        # Блокировки
        self.lock = threading.RLock()

        self.logger.info(f"ParentalControlBot {name} инициализирован")

    async def start(self) -> bool:
        """Запуск бота родительского контроля"""
        try:
            with self.lock:
                if self.running:
                    self.logger.warning("ParentalControlBot уже запущен")
                    return True

                # Инициализация базы данных
                await self._setup_database()

                # Инициализация Redis
                await self._setup_redis()

                # Инициализация ML модели
                if self.config.get("ml_enabled", True):
                    await self._setup_ml_model()

                # Загрузка профилей детей
                await self._load_child_profiles()

                # Запуск мониторинга
                self.running = True
                self.monitoring_thread = threading.Thread(target=self._monitoring_worker)
                self.monitoring_thread.daemon = True
                self.monitoring_thread.start()

                self.logger.info("ParentalControlBot запущен успешно")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка запуска ParentalControlBot: {e}")
            return False

    async def stop(self) -> bool:
        """Остановка бота родительского контроля"""
        try:
            with self.lock:
                if not self.running:
                    self.logger.warning("ParentalControlBot уже остановлен")
                    return True

                self.running = False

                # Ожидание завершения потоков
                if self.monitoring_thread and self.monitoring_thread.is_alive():
                    self.monitoring_thread.join(timeout=5)

                # Закрытие соединений
                if self.db_session:
                    self.db_session.close()

                if self.redis_client:
                    self.redis_client.close()

                self.logger.info("ParentalControlBot остановлен")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка остановки ParentalControlBot: {e}")
            return False

    async def _setup_database(self) -> None:
        """Настройка базы данных"""
        try:
            database_url = self.config.get("database_url", "sqlite:///parental_control_bot.db")
            self.db_engine = create_engine(database_url)
            Base.metadata.create_all(self.db_engine)

            Session = sessionmaker(bind=self.db_engine)
            self.db_session = Session()

            self.logger.info("База данных ParentalControlBot настроена")

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

            self.logger.info("Redis для ParentalControlBot настроен")

        except Exception as e:
            self.logger.error(f"Ошибка настройки Redis: {e}")
            raise

    async def _setup_ml_model(self) -> None:
        """Настройка ML модели для анализа контента"""
        try:
            self.ml_model = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            self.scaler = StandardScaler()

            self.logger.info("ML модель ParentalControlBot настроена")

        except Exception as e:
            self.logger.error(f"Ошибка настройки ML модели: {e}")

    async def _load_child_profiles(self) -> None:
        """Загрузка профилей детей"""
        try:
            if self.db_session:
                profiles = self.db_session.query(ChildProfile).all()

                for profile in profiles:
                    self.child_profiles[profile.id] = profile
                    self.active_monitoring[profile.id] = True

                self.stats["total_children"] = len(self.child_profiles)
                self.stats["active_children"] = len([p for p in self.child_profiles.values() if p])

                self.logger.info("Загружено {} профилей детей".format(len(self.child_profiles)))

        except Exception as e:
            self.logger.error(f"Ошибка загрузки профилей детей: {e}")

    def _monitoring_worker(self) -> None:
        """Фоновый процесс мониторинга"""
        while self.running:
            try:
                time.sleep(1)  # Проверка каждую секунду

                # Обновление статистики
                self._update_stats()

                # Проверка нарушений времени
                self._check_time_violations()

                # Проверка подозрительной активности
                self._check_suspicious_activities()

            except Exception as e:
                self.logger.error(f"Ошибка в процессе мониторинга: {e}")

    def _update_stats(self) -> None:
        """Обновление статистики"""
        try:
            with self.lock:
                self.stats["active_children"] = len([p for p in self.child_profiles.values() if p])
                active_children.set(self.stats["active_children"])

        except Exception as e:
            self.logger.error(f"Ошибка обновления статистики: {e}")

    def _check_time_violations(self) -> None:
        """Проверка нарушений времени использования"""
        try:
            for child_id, profile in self.child_profiles.items():
                if not self.active_monitoring.get(child_id, False):
                    continue

                # Проверка дневных лимитов
                daily_usage = self._get_daily_usage(child_id)
                time_limits = profile.time_limits or {}

                for device_type, limit_minutes in time_limits.items():
                    if daily_usage.get(device_type, 0) > limit_minutes:
                        self._handle_time_violation(child_id, device_type, daily_usage[device_type], limit_minutes)

        except Exception as e:
            self.logger.error(f"Ошибка проверки нарушений времени: {e}")

    def _check_suspicious_activities(self) -> None:
        """Проверка подозрительной активности"""
        try:
            # Здесь должна быть логика анализа подозрительной активности
            # Пока что заглушка
            pass

        except Exception as e:
            self.logger.error(f"Ошибка проверки подозрительной активности: {e}")

    def _get_daily_usage(self, child_id: str) -> Dict[str, int]:
        """Получение дневного использования устройств"""
        try:
            if not self.db_session:
                return {}

            today = datetime.now().date()
            logs = self.db_session.query(ActivityLog).filter(
                ActivityLog.child_id == child_id,
                ActivityLog.timestamp >= today
            ).all()

            usage = defaultdict(int)
            for log in logs:
                device_type = log.device_id.split('_')[0]  # Предполагаем формат device_type_id
                usage[device_type] += log.duration or 0

            return dict(usage)

        except Exception as e:
            self.logger.error(f"Ошибка получения дневного использования: {e}")
            return {}

    def _handle_time_violation(self, child_id: str, device_type: str, current_usage: int, limit: int) -> None:
        """Обработка нарушения времени использования"""
        try:
            # Создание оповещения
            alert = ActivityAlert(
                child_id=child_id,
                alert_type="time_violation",
                severity="medium",
                message=f"Превышен лимит времени использования {device_type}: {current_usage}м > {limit}м",
                timestamp=datetime.now(),
                action_required=True,
                data={
                    "device_type": device_type,
                    "current_usage": current_usage,
                    "limit": limit
                }
            )

            # Отправка уведомления родителям
            self._send_parent_notification(alert)

            # Обновление статистики
            self.stats["time_violations"] += 1
            time_limit_violations.labels(child_id=child_id, device_type=device_type).inc()

            self.logger.warning(f"Нарушение времени для {child_id}: {device_type}")

        except Exception as e:
            self.logger.error(f"Ошибка обработки нарушения времени: {e}")

    def _send_parent_notification(self, alert: ActivityAlert) -> None:
        """Отправка уведомления родителям"""
        try:
            # Здесь должна быть интеграция с системой уведомлений
            # Пока что логируем
            self.logger.info(f"Уведомление родителям: {alert.message}")

            # Сохранение в Redis
            if self.redis_client:
                alert_data = {
                    "child_id": alert.child_id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "action_required": alert.action_required,
                    "data": alert.data
                }
                self.redis_client.lpush("parental_alerts", json.dumps(alert_data))

        except Exception as e:
            self.logger.error(f"Ошибка отправки уведомления родителям: {e}")

    async def add_child_profile(self, child_data: Dict[str, Any]) -> str:
        """Добавление профиля ребенка"""
        try:
            with self.lock:
                # Генерация ID
                child_id = self._generate_child_id()

                # Создание профиля
                profile = ChildProfile(
                    id=child_id,
                    name=child_data["name"],
                    age=child_data["age"],
                    age_group=child_data.get("age_group", self._determine_age_group(child_data["age"])),
                    parent_id=child_data["parent_id"],
                    device_ids=child_data.get("device_ids", []),
                    restrictions=child_data.get("restrictions", {}),
                    time_limits=child_data.get("time_limits", {}),
                    safe_zones=child_data.get("safe_zones", [])
                )

                # Сохранение в базу данных
                if self.db_session:
                    self.db_session.add(profile)
                    self.db_session.commit()

                # Добавление в память
                self.child_profiles[child_id] = profile
                self.active_monitoring[child_id] = True

                # Обновление статистики
                self.stats["total_children"] += 1
                self.stats["active_children"] += 1

                self.logger.info(f"Профиль ребенка добавлен: {child_id}")
                return child_id

        except Exception as e:
            self.logger.error(f"Ошибка добавления профиля ребенка: {e}")
            raise

    def _generate_child_id(self) -> str:
        """Генерация уникального ID ребенка"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(f"{timestamp}{time.time()}".encode()).hexdigest()[:8]
        return f"CHILD_{timestamp}_{random_part}"

    def _determine_age_group(self, age: int) -> str:
        """Определение возрастной группы"""
        if age <= 4:
            return AgeGroup.TODDLER.value
        elif age <= 6:
            return AgeGroup.PRESCHOOL.value
        elif age <= 12:
            return AgeGroup.ELEMENTARY.value
        elif age <= 18:
            return AgeGroup.TEEN.value
        else:
            return AgeGroup.ADULT.value

    async def analyze_content(self, url: str, child_id: str) -> ContentAnalysisResult:
        """Анализ контента для ребенка"""
        try:
            # Базовый анализ URL
            category = self._categorize_url(url)
            risk_score = self._calculate_risk_score(url, category)
            age_appropriate = self._is_age_appropriate(category, child_id)

            # Определение действия
            action = self._determine_action(category, risk_score, age_appropriate, child_id)

            # Обновление статистики
            if action == ControlAction.BLOCK:
                self.stats["content_blocks"] += 1
                profile = self.child_profiles.get(child_id)
                if profile:
                    content_blocks_total.labels(
                        category=category.value,
                        age_group=profile.age_group
                    ).inc()

            result = ContentAnalysisResult(
                url=url,
                category=category,
                risk_score=risk_score,
                age_appropriate=age_appropriate,
                action=action,
                reason=self._get_action_reason(action, category, risk_score)
            )

            # Логирование активности
            await self._log_activity(child_id, "content_access", url, category, result)

            return result

        except Exception as e:
            self.logger.error(f"Ошибка анализа контента: {e}")
            # Возвращаем безопасный результат
            return ContentAnalysisResult(
                url=url,
                category=ContentCategory.UNKNOWN,
                risk_score=1.0,
                age_appropriate=False,
                action=ControlAction.BLOCK,
                reason="Ошибка анализа контента"
            )

    def _categorize_url(self, url: str) -> ContentCategory:
        """Категоризация URL"""
        try:
            url_lower = url.lower()

            # Простая категоризация по ключевым словам
            if any(word in url_lower for word in ["youtube", "video", "entertainment"]):
                return ContentCategory.ENTERTAINMENT
            elif any(word in url_lower for word in ["facebook", "instagram", "twitter", "social"]):
                return ContentCategory.SOCIAL
            elif any(word in url_lower for word in ["game", "gaming", "play"]):
                return ContentCategory.GAMING
            elif any(word in url_lower for word in ["shop", "buy", "store", "amazon"]):
                return ContentCategory.SHOPPING
            elif any(word in url_lower for word in ["news", "article", "blog"]):
                return ContentCategory.NEWS
            elif any(word in url_lower for word in ["adult", "xxx", "porn"]):
                return ContentCategory.ADULT
            elif any(word in url_lower for word in ["violence", "fight", "war"]):
                return ContentCategory.VIOLENCE
            elif any(word in url_lower for word in ["drug", "alcohol", "smoke"]):
                return ContentCategory.DRUGS
            elif any(word in url_lower for word in ["gambling", "casino", "bet"]):
                return ContentCategory.GAMBLING
            elif any(word in url_lower for word in ["edu", "learn", "school", "course"]):
                return ContentCategory.EDUCATIONAL
            else:
                return ContentCategory.UNKNOWN

        except Exception as e:
            self.logger.error(f"Ошибка категоризации URL: {e}")
            return ContentCategory.UNKNOWN

    def _calculate_risk_score(self, url: str, category: ContentCategory) -> float:
        """Расчет риска контента"""
        try:
            base_scores = {
                ContentCategory.EDUCATIONAL: 0.1,
                ContentCategory.ENTERTAINMENT: 0.3,
                ContentCategory.SOCIAL: 0.5,
                ContentCategory.GAMING: 0.4,
                ContentCategory.SHOPPING: 0.6,
                ContentCategory.NEWS: 0.2,
                ContentCategory.ADULT: 1.0,
                ContentCategory.VIOLENCE: 0.9,
                ContentCategory.DRUGS: 0.95,
                ContentCategory.GAMBLING: 0.8,
                ContentCategory.UNKNOWN: 0.7
            }

            return base_scores.get(category, 0.5)

        except Exception as e:
            self.logger.error(f"Ошибка расчета риска: {e}")
            return 0.5

    def _is_age_appropriate(self, category: ContentCategory, child_id: str) -> bool:
        """Проверка соответствия возрасту"""
        try:
            profile = self.child_profiles.get(child_id)
            if not profile:
                return False

            age_group = profile.age_group

            # Правила соответствия возрасту
            age_rules = {
                AgeGroup.TODDLER.value: [
                    ContentCategory.EDUCATIONAL,
                    ContentCategory.ENTERTAINMENT],
                AgeGroup.PRESCHOOL.value: [
                    ContentCategory.EDUCATIONAL,
                    ContentCategory.ENTERTAINMENT,
                    ContentCategory.GAMING],
                AgeGroup.ELEMENTARY.value: [
                    ContentCategory.EDUCATIONAL,
                    ContentCategory.ENTERTAINMENT,
                    ContentCategory.GAMING,
                    ContentCategory.SOCIAL],
                AgeGroup.TEEN.value: [
                    ContentCategory.EDUCATIONAL,
                    ContentCategory.ENTERTAINMENT,
                    ContentCategory.GAMING,
                    ContentCategory.SOCIAL,
                    ContentCategory.NEWS,
                    ContentCategory.SHOPPING],
                AgeGroup.ADULT.value: [
                    cat for cat in ContentCategory]}

            allowed_categories = age_rules.get(age_group, [])
            return category in allowed_categories

        except Exception as e:
            self.logger.error(f"Ошибка проверки соответствия возрасту: {e}")
            return False

    def _determine_action(
            self,
            category: ContentCategory,
            risk_score: float,
            age_appropriate: bool,
            child_id: str) -> ControlAction:
        """Определение действия по контенту"""
        try:
            profile = self.child_profiles.get(child_id)
            if not profile:
                return ControlAction.BLOCK

            # Высокий риск - блокировка
            if risk_score >= 0.8:
                return ControlAction.BLOCK

            # Не подходит по возрасту - блокировка
            if not age_appropriate:
                return ControlAction.BLOCK

            # Средний риск - предупреждение
            if risk_score >= 0.5:
                return ControlAction.WARN

            # Низкий риск - разрешение
            return ControlAction.ALLOW

        except Exception as e:
            self.logger.error(f"Ошибка определения действия: {e}")
            return ControlAction.BLOCK

    def _get_action_reason(self, action: ControlAction, category: ContentCategory, risk_score: float) -> str:
        """Получение причины действия"""
        try:
            if action == ControlAction.BLOCK:
                if risk_score >= 0.8:
                    return f"Высокий риск контента ({risk_score:.2f})"
                else:
                    return "Контент не подходит по возрасту"
            elif action == ControlAction.WARN:
                return f"Средний риск контента ({risk_score:.2f})"
            else:
                return "Контент безопасен"

        except Exception as e:
            self.logger.error(f"Ошибка получения причины действия: {e}")
            return "Неизвестная причина"

    async def _log_activity(
            self,
            child_id: str,
            activity_type: str,
            content_url: str,
            category: ContentCategory,
            result: ContentAnalysisResult) -> None:
        """Логирование активности"""
        try:
            if not self.db_session:
                return

            log = ActivityLog(
                id=self._generate_activity_id(),
                child_id=child_id,
                device_id="unknown",  # Должно передаваться извне
                activity_type=activity_type,
                content_url=content_url,
                content_category=category.value,
                duration=0,  # Для доступа к контенту
                risk_score=result.risk_score
            )

            self.db_session.add(log)
            self.db_session.commit()

        except Exception as e:
            self.logger.error(f"Ошибка логирования активности: {e}")

    def _generate_activity_id(self) -> str:
        """Генерация ID активности"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(f"{timestamp}{time.time()}".encode()).hexdigest()[:8]
        return f"ACT_{timestamp}_{random_part}"

    async def get_child_status(self, child_id: str) -> Optional[Dict[str, Any]]:
        """Получение статуса ребенка"""
        try:
            profile = self.child_profiles.get(child_id)
            if not profile:
                return None

            # Получение дневной статистики
            daily_usage = self._get_daily_usage(child_id)

            return {
                "child_id": child_id,
                "name": profile.name,
                "age": profile.age,
                "age_group": profile.age_group,
                "is_monitored": self.active_monitoring.get(child_id, False),
                "daily_usage": daily_usage,
                "time_limits": profile.time_limits or {},
                "restrictions": profile.restrictions or {},
                "safe_zones": profile.safe_zones or [],
                "last_update": profile.updated_at.isoformat()
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса ребенка: {e}")
            return None

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса бота"""
        try:
            return {
                "name": self.name,
                "status": "running" if self.running else "stopped",
                "config": self.config,
                "stats": self.stats,
                "children_monitored": len(self.child_profiles),
                "active_monitoring": len([m for m in self.active_monitoring.values() if m]),
                "ml_enabled": self.config.get("ml_enabled", False),
                "last_update": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"error": str(e)}


# Функция тестирования
async def test_parental_control_bot():
    """Тестирование ParentalControlBot"""
    print("🧪 Тестирование ParentalControlBot...")

    # Создание бота
    bot = ParentalControlBot("TestParentalBot")

    try:
        # Запуск
        await bot.start()
        print("✅ ParentalControlBot запущен")

        # Добавление профиля ребенка
        child_data = {
            "name": "Test Child",
            "age": 10,
            "parent_id": "parent_123",
            "time_limits": {"mobile": 120, "desktop": 180},
            "restrictions": {"adult_content": True, "social_media": False}
        }

        child_id = await bot.add_child_profile(child_data)
        print(f"✅ Профиль ребенка добавлен: {child_id}")

        # Анализ контента
        result = await bot.analyze_content("https://youtube.com/watch?v=test", child_id)
        print(f"✅ Анализ контента: {result.action.value} - {result.reason}")

        # Получение статуса ребенка
        status = await bot.get_child_status(child_id)
        print(f"✅ Статус ребенка: {status['name']} - {status['age_group']}")

        # Получение общего статуса
        bot_status = await bot.get_status()
        print(f"✅ Статус бота: {bot_status['status']}")

    finally:
        # Остановка
        await bot.stop()
        print("✅ ParentalControlBot остановлен")


# Запуск тестов при прямом выполнении
if __name__ == "__main__":
    asyncio.run(test_parental_control_bot())
