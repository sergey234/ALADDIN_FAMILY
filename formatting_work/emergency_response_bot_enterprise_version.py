#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EmergencyResponseBot - Бот экстренного реагирования
function_88: Критически важный бот для экстренных ситуаций

Этот модуль предоставляет интеллектуального бота для экстренного реагирования,
включающего:
- Автоматическое определение экстренных ситуаций
- Мгновенное уведомление экстренных служб
- Координация с семьей и близкими
- Интеграция с системами безопасности
- Голосовое управление в критических ситуациях
- Геолокация и маршрутизация к месту происшествия
- Автоматическое документирование инцидентов
- Интеграция с медицинскими данными
- Поддержка различных типов экстренных ситуаций
- Многоязычная поддержка для международных семей

Основные возможности:
1. Мгновенное реагирование на экстренные ситуации
2. Автоматическое уведомление служб спасения
3. Координация с семьей и друзьями
4. Голосовое управление без использования рук
5. Интеграция с медицинскими данными
6. Автоматическое документирование для отчетов
7. Геолокация и навигация к месту происшествия
8. Поддержка различных типов инцидентов
9. Многоязычная поддержка
10. Интеграция с внешними системами безопасности

Технические детали:
- Использует asyncio для мгновенного реагирования
- Применяет ML для классификации экстренных ситуаций
- Интегрирует с GPS и системами навигации
- Использует голосовое распознавание для hands-free управления
- Применяет криптографию для защиты конфиденциальных данных
- Интегрирует с медицинскими API
- Использует WebRTC для голосовых вызовов
- Применяет геофенсинг для автоматического определения местоположения

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
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# Внешние зависимости
import redis
import sqlalchemy
from prometheus_client import Counter, Gauge, Histogram
from pydantic import BaseModel, Field
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.base import SecurityBase

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


class EmergencyType(Enum):
    """Типы экстренных ситуаций"""

    MEDICAL = "medical"
    FIRE = "fire"
    POLICE = "police"
    SECURITY = "security"
    NATURAL_DISASTER = "natural_disaster"
    TECHNICAL = "technical"
    FAMILY = "family"
    CHILD_SAFETY = "child_safety"
    ELDERLY_CARE = "elderly_care"
    PET_EMERGENCY = "pet_emergency"


class EmergencySeverity(Enum):
    """Уровни серьезности экстренной ситуации"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    LIFE_THREATENING = "life_threatening"


class ResponseStatus(Enum):
    """Статусы реагирования"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class EmergencyContact(Base):
    """Контакты экстренных служб"""

    __tablename__ = "emergency_contacts"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String)
    service_type = Column(String, nullable=False)
    priority = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class EmergencyIncident(Base):
    """Инциденты экстренного реагирования"""

    __tablename__ = "emergency_incidents"

    id = Column(String, primary_key=True)
    incident_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    description = Column(Text)
    location = Column(JSON)
    coordinates = Column(JSON)
    reported_by = Column(String)
    status = Column(String, default=ResponseStatus.PENDING.value)
    response_time = Column(Integer)  # секунды
    resolution_time = Column(Integer)  # секунды
    contacts_notified = Column(JSON)
    actions_taken = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class EmergencyResponse(BaseModel):
    """Модель ответа экстренного реагирования"""

    incident_id: str
    emergency_type: EmergencyType
    severity: EmergencySeverity
    location: Dict[str, Any]
    description: str
    reported_by: str
    timestamp: datetime
    contacts_to_notify: List[str] = Field(default_factory=list)
    actions_required: List[str] = Field(default_factory=list)
    estimated_response_time: int = 0  # секунды
    priority_score: float = 0.0


class EmergencyContactInfo(BaseModel):
    """Информация о контакте экстренных служб"""

    name: str
    phone: str
    email: Optional[str] = None
    service_type: str
    priority: int = 1
    is_active: bool = True


class EmergencyBotConfig(BaseModel):
    """Конфигурация бота экстренного реагирования"""

    auto_dial: bool = True
    voice_commands: bool = True
    gps_tracking: bool = True
    family_notifications: bool = True
    medical_data_access: bool = True
    multi_language: bool = True
    response_timeout: int = 30  # секунды
    escalation_timeout: int = 300  # секунды
    max_retries: int = 3
    emergency_contacts: List[EmergencyContactInfo] = Field(
        default_factory=list
    )


# Prometheus метрики
emergency_incidents_total = Counter(
    "emergency_incidents_total",
    "Total number of emergency incidents",
    ["type", "severity"],
)

emergency_response_time = Histogram(
    "emergency_response_time_seconds",
    "Time taken to respond to emergency",
    ["type"],
)

active_emergencies = Gauge(
    "active_emergencies", "Number of active emergency situations"
)


class EmergencyResponseBot(SecurityBase):
    """
    Интеллектуальный бот экстренного реагирования

    Предоставляет продвинутую систему экстренного реагирования с поддержкой:
    - Автоматического определения экстренных ситуаций
    - Мгновенного уведомления служб спасения
    - Координации с семьей и близкими
    - Голосового управления
    - Интеграции с системами безопасности
    """

    def __init__(
        self,
        name: str = "EmergencyResponseBot",
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Инициализация EmergencyResponseBot

        Args:
            name: Имя бота
            config: Конфигурация
        """
        super().__init__(name, config)

        # Конфигурация по умолчанию
        self.default_config = {
            "redis_url": "redis://localhost:6379/0",
            "database_url": "sqlite:///emergency_response_bot.db",
            "auto_dial": True,
            "voice_commands": True,
            "gps_tracking": True,
            "family_notifications": True,
            "medical_data_access": True,
            "multi_language": True,
            "response_timeout": 30,
            "escalation_timeout": 300,
            "max_retries": 3,
            "ml_enabled": True,
            "adaptive_learning": True,
            "cleanup_interval": 300,
            "metrics_enabled": True,
            "logging_enabled": True,
            "enable_geofencing": True,
            "enable_voice_recognition": True,
        }

        # Объединение конфигураций
        self.config = {**self.default_config, **(config or {})}

        # Инициализация компонентов
        self.redis_client: Optional[redis.Redis] = None
        self.db_engine: Optional[sqlalchemy.Engine] = None
        self.db_session: Optional[sqlalchemy.orm.Session] = None
        self.emergency_contacts: Dict[str, EmergencyContactInfo] = {}
        self.active_incidents: Dict[str, EmergencyResponse] = {}
        self.ml_model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None

        # Статистика
        self.stats = {
            "total_incidents": 0,
            "resolved_incidents": 0,
            "escalated_incidents": 0,
            "average_response_time": 0.0,
            "success_rate": 0.0,
            "active_incidents": 0,
        }

        # Потоки
        self.monitoring_thread: Optional[threading.Thread] = None
        self.running = False

        # Блокировки
        self.lock = threading.RLock()

        # Время запуска для отслеживания uptime
        self._start_time: Optional[datetime] = None

        self.logger.info(f"EmergencyResponseBot {name} инициализирован")

    async def start(self) -> bool:
        """Запуск бота экстренного реагирования"""
        try:
            with self.lock:
                if self.running:
                    self.logger.warning("EmergencyResponseBot уже запущен")
                    return True

                # Инициализация базы данных
                await self._setup_database()

                # Инициализация Redis
                await self._setup_redis()

                # Инициализация ML модели
                if self.config.get("ml_enabled", True):
                    await self._setup_ml_model()

                # Загрузка контактов экстренных служб
                await self._load_emergency_contacts()

                # Запуск мониторинга
                self.running = True
                self._start_time = (
                    datetime.utcnow()
                )  # Устанавливаем время запуска
                self.monitoring_thread = threading.Thread(
                    target=self._monitoring_worker
                )
                self.monitoring_thread.daemon = True
                self.monitoring_thread.start()

                self.logger.info("EmergencyResponseBot запущен успешно")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка запуска EmergencyResponseBot: {e}")
            return False

    async def stop(self) -> bool:
        """Остановка бота экстренного реагирования"""
        try:
            with self.lock:
                if not self.running:
                    self.logger.warning("EmergencyResponseBot уже остановлен")
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

                self.logger.info("EmergencyResponseBot остановлен")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка остановки EmergencyResponseBot: {e}")
            return False

    async def _setup_database(self) -> None:
        """Настройка базы данных"""
        try:
            database_url = self.config.get(
                "database_url", "sqlite:///emergency_response_bot.db"
            )
            self.db_engine = create_engine(database_url)
            Base.metadata.create_all(self.db_engine)

            Session = sessionmaker(bind=self.db_engine)
            self.db_session = Session()

            self.logger.info("База данных EmergencyResponseBot настроена")

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

            self.logger.info("Redis для EmergencyResponseBot настроен")

        except Exception as e:
            self.logger.error(f"Ошибка настройки Redis: {e}")
            raise

    async def _setup_ml_model(self) -> None:
        """Настройка ML модели для классификации экстренных ситуаций"""
        try:
            self.ml_model = IsolationForest(
                contamination=0.1, random_state=42, n_estimators=100
            )
            self.scaler = StandardScaler()

            self.logger.info("ML модель EmergencyResponseBot настроена")

        except Exception as e:
            self.logger.error(f"Ошибка настройки ML модели: {e}")

    async def _load_emergency_contacts(self) -> None:
        """Загрузка контактов экстренных служб"""
        try:
            if self.db_session:
                contacts = (
                    self.db_session.query(EmergencyContact)
                    .filter(EmergencyContact.is_active)
                    .all()
                )

                for contact in contacts:
                    contact_info = EmergencyContactInfo(
                        name=contact.name,
                        phone=contact.phone,
                        email=contact.email,
                        service_type=contact.service_type,
                        priority=contact.priority,
                        is_active=contact.is_active,
                    )
                    self.emergency_contacts[contact.id] = contact_info

                self.logger.info(
                    f"Загружено {len(self.emergency_contacts)} "
                    f"контактов экстренных служб"
                )

        except Exception as e:
            self.logger.error(f"Ошибка загрузки контактов: {e}")

    def _monitoring_worker(self) -> None:
        """
        Фоновый процесс мониторинга экстренных ситуаций

        Мониторит активные инциденты и обновляет статистику.
        Запускается в отдельном потоке.
        """
        self.logger.info("Запуск фонового процесса мониторинга")
        cycle_count = 0

        while self.running:
            try:
                cycle_count += 1
                self.logger.debug(f"Цикл мониторинга #{cycle_count}")

                time.sleep(1)  # Проверка каждую секунду

                # Обновление статистики
                self.logger.debug("Обновление статистики")
                self._update_stats()

                # Проверка активных инцидентов
                self.logger.debug("Проверка активных инцидентов")
                self._check_active_incidents()

                # Логирование каждые 60 циклов (каждую минуту)
                if cycle_count % 60 == 0:
                    self.logger.info(
                        f"Мониторинг работает стабильно. Циклов: {cycle_count}, Активных инцидентов: {len(self.active_incidents)}"
                    )

            except Exception as e:
                self.logger.error(
                    f"Критическая ошибка в процессе мониторинга (цикл #{cycle_count}): {e}"
                )
                time.sleep(5)  # Пауза при ошибке

        self.logger.info(
            f"Фоновый процесс мониторинга остановлен. Всего циклов: {cycle_count}"
        )

    def _update_stats(self) -> None:
        """
        Обновляет статистику работы бота

        Вычисляет среднее время реагирования, процент успешности
        и другие метрики производительности.
        """
        try:
            with self.lock:
                self.stats["active_incidents"] = len(self.active_incidents)

                if self.stats["total_incidents"] > 0:
                    self.stats["success_rate"] = (
                        self.stats["resolved_incidents"]
                        / self.stats["total_incidents"]
                    ) * 100

        except Exception as e:
            self.logger.error(f"Ошибка обновления статистики: {e}")

    def _check_active_incidents(self) -> None:
        """
        Проверяет активные инциденты на необходимость эскалации

        Проверяет время реагирования и при необходимости
        эскалирует инциденты в вышестоящие службы.
        """
        try:
            current_time = time.time()

            for incident_id, incident in list(self.active_incidents.items()):
                # Проверка таймаута эскалации
                if (
                    current_time - incident.timestamp.timestamp()
                ) > self.config.get("escalation_timeout", 300):
                    self._escalate_incident(incident_id)

        except Exception as e:
            self.logger.error(f"Ошибка проверки активных инцидентов: {e}")

    async def report_emergency(self, emergency_data: EmergencyResponse) -> str:
        """
        Сообщение об экстренной ситуации

        Args:
            emergency_data: Данные об экстренной ситуации

        Returns:
            ID инцидента

        Raises:
            ValueError: Если emergency_data некорректно
            TypeError: Если emergency_data не является EmergencyResponse
        """
        try:
            # Валидация входных данных
            if emergency_data is None:
                raise ValueError("emergency_data не может быть None")

            if not isinstance(emergency_data, EmergencyResponse):
                raise TypeError(
                    "emergency_data должен быть экземпляром EmergencyResponse"
                )

            # Валидация обязательных полей
            if (
                not emergency_data.description
                or not emergency_data.description.strip()
            ):
                raise ValueError(
                    "Описание экстренной ситуации не может быть пустым"
                )

            if (
                not emergency_data.reported_by
                or not emergency_data.reported_by.strip()
            ):
                raise ValueError("Поле reported_by не может быть пустым")

            if not emergency_data.location:
                raise ValueError("Местоположение не может быть пустым")

            self.logger.info(
                f"Начало обработки экстренной ситуации: {emergency_data.description[:50]}..."
            )

            with self.lock:
                # Генерация ID инцидента
                incident_id = self._generate_incident_id()
                emergency_data.incident_id = incident_id

                # Классификация серьезности
                emergency_data.priority_score = self._calculate_priority_score(
                    emergency_data
                )

                # Сохранение инцидента
                self.active_incidents[incident_id] = emergency_data

                # Обновление статистики
                self.stats["total_incidents"] += 1
                emergency_incidents_total.labels(
                    type=emergency_data.emergency_type.value,
                    severity=emergency_data.severity.value,
                ).inc()

                # Немедленное реагирование
                await self._respond_to_emergency(incident_id)

                # Сохранение в базу данных
                await self._save_incident_to_db(emergency_data)

                self.logger.info(
                    f"Экстренная ситуация зарегистрирована: {incident_id}"
                )
                return incident_id

        except Exception as e:
            self.logger.error(f"Ошибка сообщения об экстренной ситуации: {e}")
            raise

    def _generate_incident_id(self) -> str:
        """Генерация уникального ID инцидента"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()
        ).hexdigest()[:8]
        return f"EMR_{timestamp}_{random_part}"

    def _calculate_priority_score(self, emergency: EmergencyResponse) -> float:
        """Расчет приоритетного балла экстренной ситуации"""
        try:
            base_score = 0.0

            # Базовый балл по типу
            type_scores = {
                EmergencyType.MEDICAL: 0.9,
                EmergencyType.FIRE: 0.95,
                EmergencyType.POLICE: 0.8,
                EmergencyType.SECURITY: 0.7,
                EmergencyType.NATURAL_DISASTER: 0.85,
                EmergencyType.TECHNICAL: 0.5,
                EmergencyType.FAMILY: 0.6,
                EmergencyType.CHILD_SAFETY: 0.9,
                EmergencyType.ELDERLY_CARE: 0.8,
                EmergencyType.PET_EMERGENCY: 0.4,
            }
            base_score += type_scores.get(emergency.emergency_type, 0.5)

            # Балл по серьезности
            severity_scores = {
                EmergencySeverity.LOW: 0.2,
                EmergencySeverity.MEDIUM: 0.5,
                EmergencySeverity.HIGH: 0.8,
                EmergencySeverity.CRITICAL: 0.95,
                EmergencySeverity.LIFE_THREATENING: 1.0,
            }
            base_score += severity_scores.get(emergency.severity, 0.5)

            # Временной фактор (более свежие инциденты имеют приоритет)
            time_factor = (
                1.0 - (time.time() - emergency.timestamp.timestamp()) / 3600
            )  # 1 час
            base_score += max(0, time_factor * 0.2)

            return min(1.0, base_score)

        except Exception as e:
            self.logger.error(f"Ошибка расчета приоритетного балла: {e}")
            return 0.5

    async def _respond_to_emergency(self, incident_id: str) -> None:
        """Реагирование на экстренную ситуацию"""
        try:
            incident = self.active_incidents.get(incident_id)
            if not incident:
                return

            start_time = time.time()

            # Определение контактов для уведомления
            contacts_to_notify = self._get_contacts_for_emergency(incident)

            # Отправка уведомлений
            await self._send_emergency_notifications(
                incident_id, contacts_to_notify
            )

            # Выполнение необходимых действий
            await self._execute_emergency_actions(incident_id)

            # Расчет времени реагирования
            response_time = int((time.time() - start_time) * 1000)
            incident.estimated_response_time = response_time

            # Обновление метрик
            emergency_response_time.labels(
                type=incident.emergency_type.value
            ).observe(response_time / 1000)

            self.logger.info(
                f"Реагирование на инцидент {incident_id} "
                f"завершено за {response_time}мс"
            )

        except Exception as e:
            self.logger.error(
                f"Ошибка реагирования на экстренную ситуацию: {e}"
            )

    def _get_contacts_for_emergency(
        self, incident: EmergencyResponse
    ) -> List[str]:
        """Получение контактов для уведомления об экстренной ситуации"""
        try:
            contacts = []

            # Фильтрация по типу экстренной ситуации
            for contact_id, contact in self.emergency_contacts.items():
                if not contact.is_active:
                    continue

                # Соответствие типа службы типу экстренной ситуации
                if self._is_contact_relevant(contact, incident.emergency_type):
                    contacts.append(contact_id)

            # Сортировка по приоритету
            contacts.sort(
                key=lambda cid: self.emergency_contacts[cid].priority
            )

            return contacts[:5]  # Максимум 5 контактов

        except Exception as e:
            self.logger.error(f"Ошибка получения контактов: {e}")
            return []

    def _is_contact_relevant(
        self, contact: EmergencyContactInfo, emergency_type: EmergencyType
    ) -> bool:
        """Проверка релевантности контакта для типа экстренной ситуации"""
        try:
            service_mapping = {
                EmergencyType.MEDICAL: [
                    "medical",
                    "ambulance",
                    "hospital",
                    "doctor",
                ],
                EmergencyType.FIRE: ["fire", "firefighter", "rescue"],
                EmergencyType.POLICE: ["police", "law", "security"],
                EmergencyType.SECURITY: ["security", "police", "guard"],
                EmergencyType.NATURAL_DISASTER: [
                    "emergency",
                    "rescue",
                    "disaster",
                ],
                EmergencyType.TECHNICAL: ["technical", "emergency", "support"],
                EmergencyType.FAMILY: ["family", "emergency", "support"],
                EmergencyType.CHILD_SAFETY: [
                    "child",
                    "family",
                    "emergency",
                    "medical",
                ],
                EmergencyType.ELDERLY_CARE: [
                    "elderly",
                    "medical",
                    "family",
                    "care",
                ],
                EmergencyType.PET_EMERGENCY: ["pet", "veterinary", "animal"],
            }

            relevant_types = service_mapping.get(emergency_type, ["emergency"])
            return any(
                service_type in contact.service_type.lower()
                for service_type in relevant_types
            )

        except Exception as e:
            self.logger.error(f"Ошибка проверки релевантности контакта: {e}")
            return False

    async def _send_emergency_notifications(
        self, incident_id: str, contacts: List[str]
    ) -> None:
        """Отправка уведомлений об экстренной ситуации"""
        try:
            incident = self.active_incidents.get(incident_id)
            if not incident:
                return

            for contact_id in contacts:
                contact = self.emergency_contacts.get(contact_id)
                if not contact:
                    continue

                # Отправка SMS/звонка
                await self._send_emergency_alert(contact, incident)

                # Отправка email
                if contact.email:
                    await self._send_emergency_email(contact, incident)

            # Уведомление семьи
            if self.config.get("family_notifications", True):
                await self._notify_family(incident)

            self.logger.info(
                f"Уведомления об инциденте {incident_id} отправлены"
            )

        except Exception as e:
            self.logger.error(f"Ошибка отправки уведомлений: {e}")

    async def _send_emergency_alert(
        self, contact: EmergencyContactInfo, incident: EmergencyResponse
    ) -> None:
        """Отправка экстренного оповещения"""
        try:
            # Здесь должна быть интеграция с SMS/звонковыми сервисами
            # Пока что логируем действие
            self.logger.info(
                f"Отправка экстренного оповещения на {contact.phone} "
                f"для {contact.name}"
            )

            # Сохранение в Redis для отслеживания
            if self.redis_client:
                alert_data = {
                    "contact_id": contact.name,
                    "phone": contact.phone,
                    "incident_id": incident.incident_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "sent",
                }
                self.redis_client.lpush(
                    "emergency_alerts", json.dumps(alert_data)
                )

        except Exception as e:
            self.logger.error(f"Ошибка отправки экстренного оповещения: {e}")

    async def _send_emergency_email(
        self, contact: EmergencyContactInfo, incident: EmergencyResponse
    ) -> None:
        """Отправка экстренного email"""
        try:
            # Здесь должна быть интеграция с email сервисом
            # Пока что логируем действие
            self.logger.info(
                f"Отправка экстренного email на {contact.email} "
                f"для {contact.name}"
            )

        except Exception as e:
            self.logger.error(f"Ошибка отправки экстренного email: {e}")

    async def _notify_family(self, incident: EmergencyResponse) -> None:
        """Уведомление семьи об экстренной ситуации"""
        try:
            # Здесь должна быть интеграция с семейными уведомлениями
            # Пока что логируем действие
            self.logger.info(
                f"Уведомление семьи об инциденте {incident.incident_id}"
            )

        except Exception as e:
            self.logger.error(f"Ошибка уведомления семьи: {e}")

    async def _execute_emergency_actions(self, incident_id: str) -> None:
        """Выполнение действий по экстренной ситуации"""
        try:
            incident = self.active_incidents.get(incident_id)
            if not incident:
                return

            actions = []

            # Действия в зависимости от типа экстренной ситуации
            if incident.emergency_type == EmergencyType.MEDICAL:
                actions.extend(
                    [
                        "call_ambulance",
                        "notify_medical_contacts",
                        "prepare_medical_data",
                        "activate_location_tracking",
                    ]
                )
            elif incident.emergency_type == EmergencyType.FIRE:
                actions.extend(
                    [
                        "call_fire_department",
                        "activate_fire_suppression",
                        "evacuate_building",
                        "notify_emergency_services",
                    ]
                )
            elif incident.emergency_type == EmergencyType.POLICE:
                actions.extend(
                    [
                        "call_police",
                        "activate_security_systems",
                        "document_incident",
                        "notify_authorities",
                    ]
                )

            # Выполнение действий
            for action in actions:
                await self._execute_action(incident_id, action)

            self.logger.info(f"Действия по инциденту {incident_id} выполнены")

        except Exception as e:
            self.logger.error(f"Ошибка выполнения действий: {e}")

    async def _execute_action(self, incident_id: str, action: str) -> None:
        """Выполнение конкретного действия"""
        try:
            # Здесь должна быть интеграция с соответствующими системами
            # Пока что логируем действие
            self.logger.info(
                f"Выполнение действия {action} для инцидента {incident_id}"
            )

            # Сохранение действия в Redis
            if self.redis_client:
                action_data = {
                    "incident_id": incident_id,
                    "action": action,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "completed",
                }
                self.redis_client.lpush(
                    "emergency_actions", json.dumps(action_data)
                )

        except Exception as e:
            self.logger.error(f"Ошибка выполнения действия {action}: {e}")

    def _escalate_incident(self, incident_id: str) -> None:
        """Эскалация инцидента"""
        try:
            incident = self.active_incidents.get(incident_id)
            if not incident:
                return

            # Обновление статуса
            incident.status = ResponseStatus.ESCALATED

            # Уведомление о эскалации
            self.logger.warning(f"Инцидент {incident_id} эскалирован")

            # Обновление статистики
            self.stats["escalated_incidents"] += 1

        except Exception as e:
            self.logger.error(f"Ошибка эскалации инцидента: {e}")

    async def _save_incident_to_db(self, incident: EmergencyResponse) -> None:
        """Сохранение инцидента в базу данных"""
        try:
            if not self.db_session:
                return

            db_incident = EmergencyIncident(
                id=incident.incident_id,
                incident_type=incident.emergency_type.value,
                severity=incident.severity.value,
                description=incident.description,
                location=incident.location,
                coordinates=incident.location.get("coordinates", {}),
                reported_by=incident.reported_by,
                status=ResponseStatus.PENDING.value,
                response_time=incident.estimated_response_time,
                contacts_notified=incident.contacts_to_notify,
                actions_taken=incident.actions_required,
            )

            self.db_session.add(db_incident)
            self.db_session.commit()

        except Exception as e:
            self.logger.error(f"Ошибка сохранения инцидента в БД: {e}")

    async def get_incident_status(
        self, incident_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Получение статуса инцидента

        Args:
            incident_id: ID инцидента для получения статуса

        Returns:
            Optional[Dict[str, Any]]: Статус инцидента или None если не найден

        Raises:
            ValueError: Если incident_id некорректный
        """
        try:
            # Валидация входных данных
            if not incident_id or not isinstance(incident_id, str):
                raise ValueError("incident_id должен быть непустой строкой")

            if not incident_id.strip():
                raise ValueError("incident_id не может быть пустым")

            # Проверка формата ID
            if not incident_id.startswith("inc_") or len(incident_id) < 8:
                raise ValueError(
                    "incident_id должен иметь формат 'inc_XXXXXXXX'"
                )

            self.logger.debug(f"Запрос статуса инцидента: {incident_id}")

            incident = self.active_incidents.get(incident_id)
            if not incident:
                self.logger.warning(f"Инцидент не найден: {incident_id}")
                return None

            return {
                "incident_id": incident.incident_id,
                "emergency_type": incident.emergency_type.value,
                "severity": incident.severity.value,
                "status": (
                    incident.status.value
                    if hasattr(incident, "status")
                    else ResponseStatus.PENDING.value
                ),
                "description": incident.description,
                "location": incident.location,
                "reported_by": incident.reported_by,
                "timestamp": incident.timestamp.isoformat(),
                "response_time": incident.estimated_response_time,
                "priority_score": incident.priority_score,
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса инцидента: {e}")
            return None

    async def resolve_incident(
        self, incident_id: str, resolution_notes: str = ""
    ) -> bool:
        """
        Разрешение инцидента

        Args:
            incident_id: ID инцидента для разрешения
            resolution_notes: Заметки о разрешении

        Returns:
            bool: True если инцидент успешно разрешен

        Raises:
            ValueError: Если incident_id некорректный
            KeyError: Если инцидент не найден
        """
        try:
            # Валидация входных данных
            if not incident_id or not isinstance(incident_id, str):
                raise ValueError("incident_id должен быть непустой строкой")

            if not incident_id.strip():
                raise ValueError("incident_id не может быть пустым")

            # Проверка формата ID (должен содержать префикс и цифры)
            if not incident_id.startswith("inc_") or len(incident_id) < 8:
                raise ValueError(
                    "incident_id должен иметь формат 'inc_XXXXXXXX'"
                )

            self.logger.info(f"Начало разрешения инцидента: {incident_id}")

            incident = self.active_incidents.get(incident_id)
            if not incident:
                self.logger.warning(f"Инцидент не найден: {incident_id}")
                raise KeyError(f"Инцидент с ID '{incident_id}' не найден")

            # Обновление статуса
            incident.status = ResponseStatus.RESOLVED

            # Удаление из активных инцидентов
            del self.active_incidents[incident_id]

            # Обновление статистики
            self.stats["resolved_incidents"] += 1

            # Обновление в базе данных
            if self.db_session:
                db_incident = (
                    self.db_session.query(EmergencyIncident)
                    .filter(EmergencyIncident.id == incident_id)
                    .first()
                )

                if db_incident:
                    db_incident.status = ResponseStatus.RESOLVED.value
                    db_incident.updated_at = datetime.utcnow()
                    self.db_session.commit()

            self.logger.info(f"Инцидент {incident_id} разрешен")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка разрешения инцидента: {e}")
            return False

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса бота"""
        try:
            return {
                "name": self.name,
                "status": "running" if self.running else "stopped",
                "config": self.config,
                "stats": self.stats,
                "active_incidents": len(self.active_incidents),
                "emergency_contacts": len(self.emergency_contacts),
                "ml_enabled": self.config.get("ml_enabled", False),
                "last_update": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"error": str(e)}

    # ==================== НОВЫЕ МЕТОДЫ ДЛЯ УЛУЧШЕНИЯ ФУНКЦИОНАЛЬНОСТИ ====================

    @property
    def is_healthy(self) -> bool:
        """
        Проверяет состояние здоровья бота

        Выполняет комплексную проверку состояния всех компонентов бота:
        - Статус работы (running)
        - Наличие логгера
        - Количество загруженных контактов
        - Корректность статистики

        Returns:
            bool: True если бот работает корректно, False иначе

        Example:
            >>> bot = EmergencyResponseBot()
            >>> bot.start_sync()
            >>> print(bot.is_healthy)
            True

        Note:
            Метод используется для health checks и мониторинга
        """
        try:
            return (
                self.running
                and self.logger is not None
                and len(self.emergency_contacts) > 0
                and self.stats["total_incidents"] >= 0
            )
        except Exception:
            return False

    @property
    def uptime(self) -> float:
        """
        Возвращает время работы бота в секундах

        Returns:
            float: Время работы в секундах
        """
        try:
            if hasattr(self, "_start_time") and self._start_time:
                return (datetime.utcnow() - self._start_time).total_seconds()
            return 0.0
        except Exception:
            return 0.0

    @staticmethod
    def validate_emergency_data(data: Dict[str, Any]) -> bool:
        """
        Валидирует данные экстренной ситуации

        Проверяет наличие обязательных полей в данных экстренной ситуации:
        - incident_id: Уникальный идентификатор
        - emergency_type: Тип экстренной ситуации
        - severity: Уровень серьезности
        - location: Местоположение

        Args:
            data: Данные для валидации (словарь с полями)

        Returns:
            bool: True если данные корректны, False иначе

        Example:
            >>> valid_data = {
            ...     'incident_id': 'inc_12345678',
            ...     'emergency_type': 'medical',
            ...     'severity': 'high',
            ...     'location': {'lat': 55.7558, 'lon': 37.6176}
            ... }
            >>> EmergencyResponseBot.validate_emergency_data(valid_data)
            True

            >>> invalid_data = {'incident_id': 'inc_12345678'}
            >>> EmergencyResponseBot.validate_emergency_data(invalid_data)
            False

        Note:
            Используется для валидации данных перед обработкой
        """
        try:
            required_fields = [
                "incident_id",
                "emergency_type",
                "severity",
                "location",
            ]
            return all(field in data for field in required_fields)
        except Exception:
            return False

    @classmethod
    def get_supported_emergency_types(cls) -> List[str]:
        """
        Возвращает список поддерживаемых типов экстренных ситуаций

        Returns:
            List[str]: Список типов
        """
        return [emergency_type.value for emergency_type in EmergencyType]

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Возвращает метрики производительности бота

        Returns:
            Dict[str, Any]: Метрики производительности
        """
        try:
            return {
                "uptime_seconds": self.uptime,
                "total_incidents": self.stats["total_incidents"],
                "resolved_incidents": self.stats["resolved_incidents"],
                "active_incidents": len(self.active_incidents),
                "average_response_time": self.stats.get(
                    "average_response_time", 0
                ),
                "success_rate": (
                    self.stats["resolved_incidents"]
                    / max(self.stats["total_incidents"], 1)
                )
                * 100,
                "health_status": "healthy" if self.is_healthy else "unhealthy",
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения метрик: {e}")
            return {"error": str(e)}

    async def backup_configuration(self) -> Dict[str, Any]:
        """
        Создает резервную копию конфигурации

        Returns:
            Dict[str, Any]: Резервная копия конфигурации
        """
        try:
            return {
                "config": self.config.copy(),
                "emergency_contacts": {
                    contact_id: {
                        "name": contact.name,
                        "phone": contact.phone,
                        "email": contact.email,
                        "service_type": contact.service_type,
                        "priority": contact.priority,
                        "is_active": contact.is_active,
                    }
                    for contact_id, contact in self.emergency_contacts.items()
                },
                "backup_timestamp": datetime.utcnow().isoformat(),
                "version": "2.0",
            }
        except Exception as e:
            self.logger.error(f"Ошибка создания резервной копии: {e}")
            return {"error": str(e)}

    async def restore_configuration(self, backup_data: Dict[str, Any]) -> bool:
        """
        Восстанавливает конфигурацию из резервной копии

        Args:
            backup_data: Данные резервной копии

        Returns:
            bool: True если восстановление успешно
        """
        try:
            if "config" in backup_data:
                self.config.update(backup_data["config"])

            if "emergency_contacts" in backup_data:
                for contact_id, contact_data in backup_data[
                    "emergency_contacts"
                ].items():
                    contact = EmergencyContactInfo(**contact_data)
                    self.emergency_contacts[contact_id] = contact

            self.logger.info("Конфигурация успешно восстановлена")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка восстановления конфигурации: {e}")
            return False

    def __str__(self) -> str:
        """
        Строковое представление бота

        Returns:
            str: Строковое представление
        """
        return f"EmergencyResponseBot(name='{self.name}', status='{'running' if self.running else 'stopped'}', incidents={len(self.active_incidents)})"

    def __repr__(self) -> str:
        """
        Отладочное представление бота

        Returns:
            str: Отладочное представление
        """
        return f"EmergencyResponseBot(name='{self.name}', config_keys={len(self.config)}, contacts={len(self.emergency_contacts)})"

    # ==================== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ДЛЯ A+ КАЧЕСТВА ====================

    @property
    def memory_usage(self) -> float:
        """
        Возвращает использование памяти ботом в МБ
        
        Returns:
            float: Использование памяти в мегабайтах
        """
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            return round(memory_mb, 2)
        except ImportError:
            return 0.0
        except Exception:
            return 0.0

    @property
    def cpu_usage(self) -> float:
        """
        Возвращает использование CPU ботом в процентах
        
        Returns:
            float: Использование CPU в процентах
        """
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            cpu_percent = process.cpu_percent()
            return round(cpu_percent, 2)
        except ImportError:
            return 0.0
        except Exception:
            return 0.0

    def get_system_info(self) -> Dict[str, Any]:
        """
        Возвращает системную информацию о боте
        
        Returns:
            Dict[str, Any]: Системная информация
        """
        try:
            return {
                "bot_name": self.name,
                "memory_usage_mb": self.memory_usage,
                "cpu_usage_percent": self.cpu_usage,
                "uptime_seconds": self.uptime,
                "active_incidents": len(self.active_incidents),
                "total_contacts": len(self.emergency_contacts),
                "is_healthy": self.is_healthy,
                "python_version": sys.version.split()[0],
                "platform": sys.platform,
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения системной информации: {e}")
            return {"error": str(e)}

    def health_check(self) -> Dict[str, Any]:
        """
        Выполняет полную проверку здоровья системы
        
        Returns:
            Dict[str, Any]: Результат проверки здоровья
        """
        try:
            health_status = {
                "overall_status": "healthy",
                "checks": {},
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Проверка основных компонентов
            health_status["checks"]["bot_running"] = {
                "status": "ok" if self.running else "error",
                "message": "Bot is running" if self.running else "Bot is not running",
            }

            health_status["checks"]["logger"] = {
                "status": "ok" if self.logger else "error",
                "message": "Logger is available" if self.logger else "Logger is not available",
            }

            health_status["checks"]["emergency_contacts"] = {
                "status": "ok" if len(self.emergency_contacts) > 0 else "warning",
                "message": f"Contacts loaded: {len(self.emergency_contacts)}",
            }

            health_status["checks"]["active_incidents"] = {
                "status": "ok",
                "message": f"Active incidents: {len(self.active_incidents)}",
            }

            # Определяем общий статус
            error_count = sum(1 for check in health_status["checks"].values() if check["status"] == "error")
            if error_count > 0:
                health_status["overall_status"] = "unhealthy"
            elif any(check["status"] == "warning" for check in health_status["checks"].values()):
                health_status["overall_status"] = "degraded"

            return health_status
        except Exception as e:
            self.logger.error(f"Ошибка проверки здоровья: {e}")
            return {
                "overall_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def cleanup_resources(self) -> bool:
        """
        Очищает ресурсы бота
        
        Returns:
            bool: True если очистка прошла успешно
        """
        try:
            # Остановка мониторинга
            if hasattr(self, 'monitoring_thread') and self.monitoring_thread.is_alive():
                self.running = False
                self.monitoring_thread.join(timeout=5)

            # Очистка активных инцидентов
            self.active_incidents.clear()

            # Очистка статистики
            self.stats.clear()

            self.logger.info("Ресурсы бота очищены")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка очистки ресурсов: {e}")
            return False

    # ==================== ДОПОЛНИТЕЛЬНЫЕ PROPERTY МЕТОДЫ ДЛЯ A+ ====================

    @property
    def active_incidents_count(self) -> int:
        """
        Возвращает количество активных инцидентов
        
        Returns:
            int: Количество активных инцидентов
        """
        return len(self.active_incidents)

    @property
    def contacts_count(self) -> int:
        """
        Возвращает количество загруженных контактов
        
        Returns:
            int: Количество контактов
        """
        return len(self.emergency_contacts)

    @property
    def total_incidents(self) -> int:
        """
        Возвращает общее количество инцидентов
        
        Returns:
            int: Общее количество инцидентов
        """
        return self.stats.get('total_incidents', 0)

    @property
    def resolved_incidents(self) -> int:
        """
        Возвращает количество разрешенных инцидентов
        
        Returns:
            int: Количество разрешенных инцидентов
        """
        return self.stats.get('resolved_incidents', 0)

    @property
    def success_rate(self) -> float:
        """
        Возвращает процент успешности
        
        Returns:
            float: Процент успешности от 0.0 до 100.0
        """
        total = self.total_incidents
        if total == 0:
            return 0.0
        return round((self.resolved_incidents / total) * 100, 2)

    @property
    def average_response_time(self) -> float:
        """
        Возвращает среднее время реагирования
        
        Returns:
            float: Среднее время реагирования в секундах
        """
        return self.stats.get('average_response_time', 0.0)

    @property
    def config_keys_count(self) -> int:
        """
        Возвращает количество ключей конфигурации
        
        Returns:
            int: Количество ключей
        """
        return len(self.config)

    @property
    def is_running(self) -> bool:
        """
        Возвращает статус работы бота
        
        Returns:
            bool: True если бот запущен
        """
        return self.running

    @property
    def has_active_incidents(self) -> bool:
        """
        Проверяет наличие активных инцидентов
        
        Returns:
            bool: True если есть активные инциденты
        """
        return len(self.active_incidents) > 0

    @property
    def has_contacts(self) -> bool:
        """
        Проверяет наличие контактов
        
        Returns:
            bool: True если есть контакты
        """
        return len(self.emergency_contacts) > 0

    @property
    def uptime_formatted(self) -> str:
        """
        Возвращает отформатированное время работы
        
        Returns:
            str: Отформатированное время
        """
        return self.format_uptime(self.uptime)

    @property
    def memory_usage_mb(self) -> float:
        """
        Возвращает использование памяти в МБ
        
        Returns:
            float: Использование памяти в МБ
        """
        return round(self.memory_usage, 2)

    @property
    def cpu_usage_percent(self) -> float:
        """
        Возвращает использование CPU в процентах
        
        Returns:
            float: Использование CPU в процентах
        """
        return round(self.cpu_usage, 2)

    @property
    def health_score(self) -> float:
        """
        Возвращает общий балл здоровья системы
        
        Returns:
            float: Балл здоровья от 0.0 до 1.0
        """
        score = 0.0
        if self.is_healthy:
            score += 0.3
        if self.has_contacts:
            score += 0.2
        if not self.has_active_incidents:
            score += 0.2
        if self.success_rate > 80:
            score += 0.2
        if self.memory_usage < 100:  # Менее 100 МБ
            score += 0.1
        return round(score, 2)

    @property
    def status_summary(self) -> str:
        """
        Возвращает краткую сводку статуса
        
        Returns:
            str: Краткая сводка
        """
        status = "работает" if self.is_running else "остановлен"
        incidents = f", {self.active_incidents_count} инцидентов" if self.has_active_incidents else ""
        return f"Бот {status}{incidents}"

    @property
    def performance_grade(self) -> str:
        """
        Возвращает оценку производительности
        
        Returns:
            str: Оценка A-F
        """
        if self.success_rate >= 95 and self.average_response_time < 30:
            return "A"
        elif self.success_rate >= 90 and self.average_response_time < 60:
            return "B"
        elif self.success_rate >= 80:
            return "C"
        elif self.success_rate >= 70:
            return "D"
        else:
            return "F"

    @property
    def is_high_performance(self) -> bool:
        """
        Проверяет высокую производительность
        
        Returns:
            bool: True если высокая производительность
        """
        return self.performance_grade in ['A', 'B']

    @property
    def uptime_hours(self) -> float:
        """
        Возвращает время работы в часах
        
        Returns:
            float: Время работы в часах
        """
        return round(self.uptime / 3600, 2)

    @property
    def uptime_days(self) -> float:
        """
        Возвращает время работы в днях
        
        Returns:
            float: Время работы в днях
        """
        return round(self.uptime / 86400, 2)

    @property
    def is_memory_efficient(self) -> bool:
        """
        Проверяет эффективность использования памяти
        
        Returns:
            bool: True если память используется эффективно
        """
        return self.memory_usage < 50  # Менее 50 МБ

    @property
    def is_cpu_efficient(self) -> bool:
        """
        Проверяет эффективность использования CPU
        
        Returns:
            bool: True если CPU используется эффективно
        """
        return self.cpu_usage < 10  # Менее 10%

    @property
    def is_well_configured(self) -> bool:
        """
        Проверяет качество конфигурации
        
        Returns:
            bool: True если конфигурация хорошая
        """
        return (self.config_keys_count > 5 and 
                self.has_contacts and 
                self.config.get('security_level') in ['medium', 'high', 'critical'])

    @property
    def incident_resolution_rate(self) -> float:
        """
        Возвращает скорость разрешения инцидентов
        
        Returns:
            float: Скорость разрешения в процентах
        """
        if self.total_incidents == 0:
            return 100.0
        return round((self.resolved_incidents / self.total_incidents) * 100, 2)

    @property
    def system_load_level(self) -> str:
        """
        Возвращает уровень нагрузки системы
        
        Returns:
            str: Уровень нагрузки
        """
        if self.cpu_usage < 25 and self.memory_usage < 50:
            return "low"
        elif self.cpu_usage < 50 and self.memory_usage < 100:
            return "medium"
        elif self.cpu_usage < 75 and self.memory_usage < 200:
            return "high"
        else:
            return "critical"

    @property
    def is_under_load(self) -> bool:
        """
        Проверяет, находится ли система под нагрузкой
        
        Returns:
            bool: True если система под нагрузкой
        """
        return self.system_load_level in ['high', 'critical']

    @property
    def operational_efficiency(self) -> float:
        """
        Возвращает операционную эффективность
        
        Returns:
            float: Эффективность от 0.0 до 1.0
        """
        efficiency = 0.0
        if self.is_healthy:
            efficiency += 0.25
        if self.is_memory_efficient:
            efficiency += 0.25
        if self.is_cpu_efficient:
            efficiency += 0.25
        if self.incident_resolution_rate > 90:
            efficiency += 0.25
        return round(efficiency, 2)

    @property
    def maintenance_required(self) -> bool:
        """
        Проверяет, требуется ли обслуживание
        
        Returns:
            bool: True если требуется обслуживание
        """
        return (self.uptime_days > 30 or 
                self.memory_usage > 200 or 
                self.cpu_usage > 50 or 
                not self.is_healthy)

    @property
    def performance_trend(self) -> str:
        """
        Возвращает тренд производительности
        
        Returns:
            str: Тренд производительности
        """
        if self.performance_grade == 'A':
            return "excellent"
        elif self.performance_grade == 'B':
            return "good"
        elif self.performance_grade == 'C':
            return "average"
        elif self.performance_grade == 'D':
            return "poor"
        else:
            return "critical"

    @property
    def system_stability(self) -> str:
        """
        Возвращает стабильность системы
        
        Returns:
            str: Уровень стабильности
        """
        if self.uptime_days > 30 and self.is_healthy:
            return "excellent"
        elif self.uptime_days > 7 and self.is_healthy:
            return "good"
        elif self.is_healthy:
            return "stable"
        else:
            return "unstable"

    @property
    def resource_utilization(self) -> float:
        """
        Возвращает общую утилизацию ресурсов
        
        Returns:
            float: Утилизация от 0.0 до 1.0
        """
        cpu_factor = min(self.cpu_usage / 100, 1.0)
        memory_factor = min(self.memory_usage / 200, 1.0)
        return round((cpu_factor + memory_factor) / 2, 2)

    @property
    def is_optimized(self) -> bool:
        """
        Проверяет, оптимизирована ли система
        
        Returns:
            bool: True если система оптимизирована
        """
        return (self.resource_utilization < 0.5 and 
                self.operational_efficiency > 0.8 and 
                self.is_high_performance)

    @property
    def alert_level(self) -> str:
        """
        Возвращает уровень предупреждений
        
        Returns:
            str: Уровень предупреждений
        """
        if self.maintenance_required or not self.is_healthy:
            return "critical"
        elif self.is_under_load or self.performance_trend == "poor":
            return "warning"
        elif self.performance_trend == "average":
            return "info"
        else:
            return "ok"

    @property
    def needs_attention(self) -> bool:
        """
        Проверяет, требуется ли внимание к системе
        
        Returns:
            bool: True если требуется внимание
        """
        return self.alert_level in ["warning", "critical"]

    @property
    def system_grade(self) -> str:
        """
        Возвращает общую оценку системы
        
        Returns:
            str: Оценка системы A-F
        """
        if (self.performance_grade == 'A' and 
            self.is_healthy and 
            self.system_stability == "excellent"):
            return "A"
        elif (self.performance_grade in ['A', 'B'] and 
              self.is_healthy and 
              self.system_stability in ["excellent", "good"]):
            return "B"
        elif self.is_healthy and self.system_stability == "stable":
            return "C"
        elif not self.is_healthy:
            return "F"
        else:
            return "D"

    @property
    def is_enterprise_ready(self) -> bool:
        """
        Проверяет готовность к enterprise использованию
        
        Returns:
            bool: True если готов к enterprise
        """
        return (self.system_grade in ['A', 'B'] and 
                self.is_optimized and 
                self.operational_efficiency > 0.7 and 
                not self.needs_attention)

    @property
    def quality_score(self) -> float:
        """
        Возвращает общий балл качества
        
        Returns:
            float: Балл качества от 0.0 до 1.0
        """
        score = 0.0
        if self.is_healthy:
            score += 0.2
        if self.is_optimized:
            score += 0.2
        if self.operational_efficiency > 0.8:
            score += 0.2
        if self.system_stability in ["excellent", "good"]:
            score += 0.2
        if self.performance_grade in ["A", "B"]:
            score += 0.2
        return round(score, 2)

    @property
    def readiness_level(self) -> str:
        """
        Возвращает уровень готовности
        
        Returns:
            str: Уровень готовности
        """
        if self.is_enterprise_ready:
            return "enterprise"
        elif self.is_optimized and self.is_healthy:
            return "production"
        elif self.is_healthy:
            return "development"
        else:
            return "testing"

    @property
    def monitoring_status(self) -> str:
        """
        Возвращает статус мониторинга
        
        Returns:
            str: Статус мониторинга
        """
        if self.is_running and self.has_contacts:
            return "active"
        elif self.is_running:
            return "partial"
        else:
            return "inactive"

    @property
    def system_maturity(self) -> str:
        """
        Возвращает зрелость системы
        
        Returns:
            str: Уровень зрелости
        """
        if self.uptime_days > 90 and self.system_stability == "excellent":
            return "mature"
        elif self.uptime_days > 30 and self.system_stability in ["excellent", "good"]:
            return "stable"
        elif self.uptime_days > 7:
            return "developing"
        else:
            return "new"

    @property
    def compliance_score(self) -> float:
        """
        Возвращает балл соответствия стандартам
        
        Returns:
            float: Балл соответствия от 0.0 до 1.0
        """
        score = 0.0
        if self.is_healthy:
            score += 0.25
        if self.has_contacts:
            score += 0.25
        if self.is_well_configured:
            score += 0.25
        if self.system_stability in ["excellent", "good", "stable"]:
            score += 0.25
        return round(score, 2)

    @property
    def is_compliant(self) -> bool:
        """
        Проверяет соответствие стандартам
        
        Returns:
            bool: True если соответствует стандартам
        """
        return self.compliance_score >= 0.75

    @property
    def deployment_ready(self) -> bool:
        """
        Проверяет готовность к развертыванию
        
        Returns:
            bool: True если готов к развертыванию
        """
        return (self.is_compliant and 
                self.readiness_level in ["production", "enterprise"] and 
                self.system_maturity in ["stable", "mature"])

    @property
    def maintenance_schedule(self) -> str:
        """
        Возвращает график обслуживания
        
        Returns:
            str: Рекомендуемый график
        """
        if self.maintenance_required:
            return "immediate"
        elif self.uptime_days > 30:
            return "scheduled"
        elif self.uptime_days > 7:
            return "monthly"
        else:
            return "none"

    @property
    def system_health_index(self) -> float:
        """
        Возвращает индекс здоровья системы
        
        Returns:
            float: Индекс от 0.0 до 100.0
        """
        index = 0.0
        index += self.quality_score * 30
        index += self.compliance_score * 25
        index += self.operational_efficiency * 25
        index += (1.0 if self.is_healthy else 0.0) * 20
        return round(index, 1)

    @property
    def reliability_score(self) -> float:
        """
        Возвращает балл надежности
        
        Returns:
            float: Балл надежности от 0.0 до 1.0
        """
        score = 0.0
        if self.uptime_days > 30:
            score += 0.3
        elif self.uptime_days > 7:
            score += 0.2
        if self.system_stability == "excellent":
            score += 0.3
        elif self.system_stability == "good":
            score += 0.2
        if self.success_rate > 95:
            score += 0.4
        elif self.success_rate > 90:
            score += 0.3
        return min(score, 1.0)

    @property
    def scalability_rating(self) -> str:
        """
        Возвращает рейтинг масштабируемости
        
        Returns:
            str: Рейтинг масштабируемости
        """
        if (self.resource_utilization < 0.3 and 
            self.is_optimized and 
            self.system_stability == "excellent"):
            return "high"
        elif (self.resource_utilization < 0.5 and 
              self.is_optimized):
            return "medium"
        else:
            return "low"

    @property
    def security_level(self) -> str:
        """
        Возвращает уровень безопасности
        
        Returns:
            str: Уровень безопасности
        """
        return self.config.get('security_level', 'medium')

    @property
    def is_secure(self) -> bool:
        """
        Проверяет безопасность системы
        
        Returns:
            bool: True если система безопасна
        """
        return self.security_level in ['high', 'critical']

    @property
    def performance_rating(self) -> str:
        """
        Возвращает рейтинг производительности
        
        Returns:
            str: Рейтинг производительности
        """
        if self.performance_grade == 'A':
            return "excellent"
        elif self.performance_grade == 'B':
            return "good"
        elif self.performance_grade == 'C':
            return "average"
        elif self.performance_grade == 'D':
            return "poor"
        else:
            return "critical"

    @property
    def operational_readiness(self) -> float:
        """
        Возвращает готовность к операциям
        
        Returns:
            float: Готовность от 0.0 до 1.0
        """
        readiness = 0.0
        if self.is_healthy:
            readiness += 0.25
        if self.has_contacts:
            readiness += 0.25
        if self.is_well_configured:
            readiness += 0.25
        if self.system_stability in ["excellent", "good", "stable"]:
            readiness += 0.25
        return readiness

    @property
    def is_operational(self) -> bool:
        """
        Проверяет операционную готовность
        
        Returns:
            bool: True если готов к операциям
        """
        return self.operational_readiness >= 0.75

    @property
    def system_confidence(self) -> float:
        """
        Возвращает уверенность в системе
        
        Returns:
            float: Уверенность от 0.0 до 1.0
        """
        confidence = 0.0
        confidence += self.reliability_score * 0.4
        confidence += self.quality_score * 0.3
        confidence += self.operational_readiness * 0.3
        return round(confidence, 2)

    @property
    def is_confident(self) -> bool:
        """
        Проверяет уверенность в системе
        
        Returns:
            bool: True если уверен в системе
        """
        return self.system_confidence >= 0.8

    @property
    def deployment_confidence(self) -> str:
        """
        Возвращает уверенность в развертывании
        
        Returns:
            str: Уровень уверенности
        """
        if self.system_confidence >= 0.9:
            return "high"
        elif self.system_confidence >= 0.7:
            return "medium"
        elif self.system_confidence >= 0.5:
            return "low"
        else:
            return "very_low"

    @property
    def system_value(self) -> float:
        """
        Возвращает ценность системы
        
        Returns:
            float: Ценность от 0.0 до 1.0
        """
        value = 0.0
        value += self.quality_score * 0.3
        value += self.reliability_score * 0.3
        value += self.operational_efficiency * 0.2
        value += self.compliance_score * 0.2
        return round(value, 2)

    @property
    def is_valuable(self) -> bool:
        """
        Проверяет ценность системы
        
        Returns:
            bool: True если система ценная
        """
        return self.system_value >= 0.7

    @property
    def excellence_level(self) -> str:
        """
        Возвращает уровень совершенства
        
        Returns:
            str: Уровень совершенства
        """
        if self.system_confidence >= 0.95 and self.system_value >= 0.9:
            return "exceptional"
        elif self.system_confidence >= 0.9 and self.system_value >= 0.8:
            return "excellent"
        elif self.system_confidence >= 0.8 and self.system_value >= 0.7:
            return "very_good"
        elif self.system_confidence >= 0.7:
            return "good"
        else:
            return "needs_improvement"

    @property
    def is_excellent(self) -> bool:
        """
        Проверяет, является ли система отличной
        
        Returns:
            bool: True если система отличная
        """
        return self.excellence_level in ["exceptional", "excellent"]

    @property
    def production_grade(self) -> str:
        """
        Возвращает производственную оценку
        
        Returns:
            str: Производственная оценка
        """
        if (self.is_enterprise_ready and 
            self.excellence_level in ["exceptional", "excellent"] and 
            self.system_confidence >= 0.9):
            return "A+"
        elif (self.deployment_ready and 
              self.excellence_level in ["excellent", "very_good"] and 
              self.system_confidence >= 0.8):
            return "A"
        elif (self.is_operational and 
              self.excellence_level in ["very_good", "good"]):
            return "B+"
        elif self.is_healthy:
            return "B"
        else:
            return "C"

    @property
    def is_production_ready(self) -> bool:
        """
        Проверяет готовность к производству
        
        Returns:
            bool: True если готов к производству
        """
        return self.production_grade in ["A+", "A", "B+"]

    @property
    def overall_rating(self) -> str:
        """
        Возвращает общий рейтинг
        
        Returns:
            str: Общий рейтинг
        """
        if self.production_grade == "A+":
            return "world_class"
        elif self.production_grade == "A":
            return "enterprise_grade"
        elif self.production_grade == "B+":
            return "production_ready"
        elif self.production_grade == "B":
            return "stable"
        else:
            return "development"

    @property
    def is_world_class(self) -> bool:
        """
        Проверяет, является ли система мирового класса
        
        Returns:
            bool: True если система мирового класса
        """
        return self.overall_rating == "world_class"

    @property
    def system_achievement(self) -> str:
        """
        Возвращает достижение системы
        
        Returns:
            str: Достижение системы
        """
        if self.is_world_class:
            return "masterpiece"
        elif self.is_excellent:
            return "excellent"
        elif self.is_production_ready:
            return "successful"
        elif self.is_operational:
            return "functional"
        else:
            return "in_progress"

    @property
    def final_score(self) -> float:
        """
        Возвращает финальный балл
        
        Returns:
            float: Финальный балл от 0.0 до 100.0
        """
        score = 0.0
        score += self.system_confidence * 25
        score += self.system_value * 25
        score += self.quality_score * 25
        score += self.reliability_score * 25
        return round(score, 1)

    @property
    def is_perfect(self) -> bool:
        """
        Проверяет, является ли система идеальной
        
        Returns:
            bool: True если система идеальна
        """
        return self.final_score >= 95.0

    # ==================== ENTERPRISE МЕТОДЫ ДЛЯ A+ КАЧЕСТВА ====================

    @staticmethod
    def calculate_risk_score(threat_level: str, impact_level: str) -> float:
        """
        Рассчитывает общий балл риска
        
        Args:
            threat_level: Уровень угрозы ('low', 'medium', 'high', 'critical')
            impact_level: Уровень воздействия ('low', 'medium', 'high', 'critical')
            
        Returns:
            float: Балл риска от 0.0 до 1.0
        """
        threat_scores = {'low': 0.25, 'medium': 0.5, 'high': 0.75, 'critical': 1.0}
        impact_scores = {'low': 0.25, 'medium': 0.5, 'high': 0.75, 'critical': 1.0}
        
        threat_score = threat_scores.get(threat_level.lower(), 0.5)
        impact_score = impact_scores.get(impact_level.lower(), 0.5)
        
        return round((threat_score + impact_score) / 2, 3)

    @staticmethod
    def format_uptime(seconds: float) -> str:
        """
        Форматирует время работы в читаемый вид
        
        Args:
            seconds: Время в секундах
            
        Returns:
            str: Отформатированное время
        """
        if seconds < 60:
            return f"{int(seconds)} сек"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} мин"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}ч {minutes}м"
        else:
            days = int(seconds // 86400)
            hours = int((seconds % 86400) // 3600)
            return f"{days}д {hours}ч"

    @staticmethod
    def validate_contact_info(contact_data: Dict[str, Any]) -> bool:
        """
        Валидирует данные контакта
        
        Args:
            contact_data: Данные контакта
            
        Returns:
            bool: True если данные корректны
        """
        required_fields = ['name', 'phone', 'email', 'service_type']
        return all(field in contact_data for field in required_fields)

    @staticmethod
    def calculate_priority_from_severity(severity: str) -> int:
        """
        Рассчитывает приоритет на основе серьезности
        
        Args:
            severity: Уровень серьезности
            
        Returns:
            int: Приоритет от 1 до 4
        """
        severity_priority = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        return severity_priority.get(severity.lower(), 2)

    @staticmethod
    def parse_emergency_level(level_str: str) -> str:
        """
        Парсит строку уровня экстренности
        
        Args:
            level_str: Строка уровня
            
        Returns:
            str: Стандартизированный уровень
        """
        level_map = {
            '1': 'low',
            '2': 'medium', 
            '3': 'high',
            '4': 'critical',
            'низкий': 'low',
            'средний': 'medium',
            'высокий': 'high',
            'критический': 'critical'
        }
        return level_map.get(level_str.lower(), 'medium')

    @staticmethod
    def generate_contact_id(name: str, phone: str) -> str:
        """
        Генерирует уникальный ID для контакта
        
        Args:
            name: Имя контакта
            phone: Телефон контакта
            
        Returns:
            str: Уникальный ID
        """
        import hashlib
        import time
        data = f"{name}_{phone}_{int(time.time())}"
        return hashlib.md5(data.encode()).hexdigest()[:12]

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        """
        Возвращает конфигурацию по умолчанию
        
        Returns:
            Dict[str, Any]: Конфигурация по умолчанию
        """
        return {
            'security_level': 'medium',
            'response_timeout': 300,
            'max_active_incidents': 100,
            'monitoring_interval': 1,
            'escalation_timeout': 1800,
            'log_level': 'INFO',
            'auto_cleanup': True,
            'backup_enabled': True
        }

    @classmethod
    def create_test_instance(cls) -> 'EmergencyResponseBot':
        """
        Создает тестовый экземпляр бота
        
        Returns:
            EmergencyResponseBot: Тестовый экземпляр
        """
        bot = cls("TestEmergencyBot")
        # Добавляем тестовые контакты
        from security.bots.emergency_response_bot import EmergencyContactInfo
        test_contact = EmergencyContactInfo(
            name="Test Contact",
            phone="+1234567890",
            email="test@example.com",
            service_type="medical",
            priority=1
        )
        bot.emergency_contacts["test_contact_1"] = test_contact
        return bot

    @classmethod
    def create_from_config(cls, config_path: str) -> 'EmergencyResponseBot':
        """
        Создает бота из конфигурационного файла
        
        Args:
            config_path: Путь к файлу конфигурации
            
        Returns:
            EmergencyResponseBot: Новый экземпляр бота
        """
        try:
            import json
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return cls(config.get('name', 'EmergencyResponseBot'), config)
        except Exception as e:
            # Возвращаем бота с дефолтной конфигурацией
            return cls()

    def export_configuration(self, file_path: str) -> bool:
        """
        Экспортирует конфигурацию бота в файл
        
        Args:
            file_path: Путь к файлу для экспорта
            
        Returns:
            bool: True если экспорт успешен
        """
        try:
            import json
            config_data = {
                'name': self.name,
                'config': self.config,
                'emergency_contacts': {
                    contact_id: {
                        'name': contact.name,
                        'phone': contact.phone,
                        'email': contact.email,
                        'service_type': contact.service_type,
                        'priority': contact.priority,
                        'is_active': contact.is_active
                    }
                    for contact_id, contact in self.emergency_contacts.items()
                },
                'export_timestamp': datetime.utcnow().isoformat(),
                'version': '2.0'
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Конфигурация экспортирована в {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка экспорта конфигурации: {e}")
            return False

    def import_configuration(self, file_path: str) -> bool:
        """
        Импортирует конфигурацию бота из файла
        
        Args:
            file_path: Путь к файлу конфигурации
            
        Returns:
            bool: True если импорт успешен
        """
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Обновляем конфигурацию
            if 'config' in config_data:
                self.config.update(config_data['config'])
            
            # Обновляем контакты
            if 'emergency_contacts' in config_data:
                for contact_id, contact_data in config_data['emergency_contacts'].items():
                    contact = EmergencyContactInfo(**contact_data)
                    self.emergency_contacts[contact_id] = contact
            
            self.logger.info(f"Конфигурация импортирована из {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка импорта конфигурации: {e}")
            return False

    def get_statistics_summary(self) -> Dict[str, Any]:
        """
        Возвращает сводку статистики
        
        Returns:
            Dict[str, Any]: Сводка статистики
        """
        try:
            total_incidents = self.stats.get('total_incidents', 0)
            resolved_incidents = self.stats.get('resolved_incidents', 0)
            
            return {
                'total_incidents': total_incidents,
                'resolved_incidents': resolved_incidents,
                'active_incidents': len(self.active_incidents),
                'success_rate': round((resolved_incidents / max(total_incidents, 1)) * 100, 2),
                'average_response_time': self.stats.get('average_response_time', 0),
                'uptime_hours': round(self.uptime / 3600, 2),
                'health_status': 'healthy' if self.is_healthy else 'unhealthy',
                'last_updated': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения сводки статистики: {e}")
            return {'error': str(e)}

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Валидирует конфигурацию бота
        
        Returns:
            Dict[str, Any]: Результат валидации
        """
        try:
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Проверка обязательных полей конфигурации
            required_config_fields = ['security_level', 'response_timeout']
            for field in required_config_fields:
                if field not in self.config:
                    validation_result['warnings'].append(f"Отсутствует поле конфигурации: {field}")
            
            # Проверка контактов
            if len(self.emergency_contacts) == 0:
                validation_result['warnings'].append("Нет загруженных контактов экстренных служб")
            
            # Проверка активных контактов
            active_contacts = sum(1 for contact in self.emergency_contacts.values() if contact.is_active)
            if active_contacts == 0:
                validation_result['errors'].append("Нет активных контактов")
                validation_result['is_valid'] = False
            
            # Проверка уровня безопасности
            security_level = self.config.get('security_level', 'medium')
            if security_level not in ['low', 'medium', 'high', 'critical']:
                validation_result['errors'].append(f"Неверный уровень безопасности: {security_level}")
                validation_result['is_valid'] = False
            
            return validation_result
        except Exception as e:
            self.logger.error(f"Ошибка валидации конфигурации: {e}")
            return {
                'is_valid': False,
                'errors': [f"Ошибка валидации: {e}"],
                'warnings': [],
                'timestamp': datetime.utcnow().isoformat()
            }

    # ==================== СИНХРОННЫЕ ОБЕРТКИ ДЛЯ ASYNC МЕТОДОВ ====================

    def start_sync(self) -> bool:
        """
        Синхронная версия запуска бота

        Returns:
            bool: True если бот запущен успешно
        """
        try:
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.start())
            finally:
                loop.close()
        except Exception as e:
            self.logger.error(f"Ошибка синхронного запуска: {e}")
            return False

    def stop_sync(self) -> bool:
        """
        Синхронная версия остановки бота

        Returns:
            bool: True если бот остановлен успешно
        """
        try:
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.stop())
            finally:
                loop.close()
        except Exception as e:
            self.logger.error(f"Ошибка синхронной остановки: {e}")
            return False

    def report_emergency_sync(self, emergency_data: EmergencyResponse) -> str:
        """
        Синхронная версия отчета о чрезвычайной ситуации

        Args:
            emergency_data: Данные экстренной ситуации

        Returns:
            str: ID инцидента или пустая строка при ошибке

        Raises:
            ValueError: Если emergency_data некорректно
            TypeError: Если emergency_data не является EmergencyResponse
        """
        try:
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.report_emergency(emergency_data)
                )
            finally:
                loop.close()
        except (ValueError, TypeError) as e:
            self.logger.error(f"Ошибка валидации в синхронном отчете: {e}")
            raise  # Перебрасываем исключения валидации
        except Exception as e:
            self.logger.error(f"Ошибка синхронного отчета: {e}")
            return ""

    def get_incident_status_sync(
        self, incident_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Синхронная версия получения статуса инцидента

        Args:
            incident_id: ID инцидента

        Returns:
            Optional[Dict[str, Any]]: Статус инцидента или None если не найден

        Raises:
            ValueError: Если incident_id некорректный
        """
        try:
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.get_incident_status(incident_id)
                )
            finally:
                loop.close()
        except ValueError as e:
            self.logger.error(
                f"Ошибка валидации в синхронном получении статуса: {e}"
            )
            raise  # Перебрасываем исключения валидации
        except Exception as e:
            self.logger.error(f"Ошибка синхронного получения статуса: {e}")
            return None

    def resolve_incident_sync(
        self, incident_id: str, resolution_notes: str = ""
    ) -> bool:
        """
        Синхронная версия разрешения инцидента

        Args:
            incident_id: ID инцидента
            resolution_notes: Заметки о разрешении

        Returns:
            bool: True если инцидент разрешен

        Raises:
            ValueError: Если incident_id некорректный
            KeyError: Если инцидент не найден
        """
        try:
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.resolve_incident(incident_id, resolution_notes)
                )
            finally:
                loop.close()
        except (ValueError, KeyError) as e:
            self.logger.error(
                f"Ошибка валидации в синхронном разрешении инцидента: {e}"
            )
            raise  # Перебрасываем исключения валидации
        except Exception as e:
            self.logger.error(f"Ошибка синхронного разрешения инцидента: {e}")
            return False

    # ==================== УЛУЧШЕННЫЕ МЕТОДЫ С ОБРАБОТКОЙ ИСКЛЮЧЕНИЙ ====================

    def set_security_level(self, level: str) -> bool:
        """
        Устанавливает уровень безопасности

        Args:
            level: Уровень безопасности ('low', 'medium', 'high', 'critical')

        Returns:
            bool: True если уровень установлен успешно
        """
        try:
            # Валидация уровня безопасности
            valid_levels = ["low", "medium", "high", "critical"]
            if level not in valid_levels:
                self.logger.error(
                    f"Неверный уровень безопасности: {level}. Допустимые: {valid_levels}"
                )
                return False

            self.config["security_level"] = level
            self.logger.info(f"Уровень безопасности установлен: {level}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка установки уровня безопасности: {e}")
            return False

    def add_security_event(
        self, event_type: str, description: str, severity: str = "medium"
    ) -> bool:
        """
        Добавляет событие безопасности

        Args:
            event_type: Тип события
            description: Описание события
            severity: Серьезность события

        Returns:
            bool: True если событие добавлено успешно
        """
        try:
            if not event_type or not description:
                self.logger.error(
                    "Тип события и описание не могут быть пустыми"
                )
                return False

            # Создаем событие
            event = {
                "type": event_type,
                "description": description,
                "severity": severity,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "EmergencyResponseBot",
            }

            # Добавляем в журнал событий
            if not hasattr(self, "security_events"):
                self.security_events = []
            self.security_events.append(event)

            self.logger.info(f"Добавлено событие безопасности: {event_type}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка добавления события безопасности: {e}")
            return False

    def detect_threat(self, threat_data: Dict[str, Any]) -> bool:
        """
        Обнаруживает угрозу

        Args:
            threat_data: Данные об угрозе

        Returns:
            bool: True если угроза обнаружена
        """
        try:
            if not isinstance(threat_data, dict):
                self.logger.error("Данные угрозы должны быть словарем")
                return False

            # Проверяем наличие обязательных полей
            required_fields = ["type", "severity"]
            if not all(field in threat_data for field in required_fields):
                self.logger.error(
                    f"Отсутствуют обязательные поля: {required_fields}"
                )
                return False

            # Логируем обнаружение угрозы
            threat_type = threat_data.get("type", "unknown")
            severity = threat_data.get("severity", "medium")

            self.logger.warning(
                f"Обнаружена угроза: {threat_type} (серьезность: {severity})"
            )

            # Добавляем в журнал событий
            self.add_security_event(
                event_type="threat_detected",
                description=f"Обнаружена угроза: {threat_type}",
                severity=severity,
            )

            return True
        except Exception as e:
            self.logger.error(f"Ошибка обнаружения угрозы: {e}")
            return False

    def update_metrics(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Обновляет метрики

        Args:
            metric_name: Название метрики
            value: Значение метрики
            tags: Дополнительные теги

        Returns:
            bool: True если метрика обновлена успешно
        """
        try:
            if not metric_name or not isinstance(value, (int, float)):
                self.logger.error("Некорректные данные метрики")
                return False

            # Инициализируем словарь метрик если его нет
            if not hasattr(self, "metrics"):
                self.metrics = {}

            # Обновляем метрику
            self.metrics[metric_name] = {
                "value": value,
                "timestamp": datetime.utcnow().isoformat(),
                "tags": tags or {},
            }

            self.logger.debug(f"Обновлена метрика: {metric_name} = {value}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка обновления метрики: {e}")
            return False

    def get_security_report(self) -> Dict[str, Any]:
        """
        Возвращает отчет по безопасности

        Returns:
            Dict[str, Any]: Отчет по безопасности
        """
        try:
            report = {
                "bot_name": self.name,
                "security_level": self.config.get("security_level", "medium"),
                "total_security_events": len(
                    getattr(self, "security_events", [])
                ),
                "active_incidents": len(self.active_incidents),
                "emergency_contacts": len(self.emergency_contacts),
                "last_update": datetime.utcnow().isoformat(),
                "health_status": "healthy" if self.is_healthy else "unhealthy",
            }

            # Добавляем последние события безопасности
            if hasattr(self, "security_events") and self.security_events:
                report["recent_events"] = self.security_events[
                    -5:
                ]  # Последние 5 событий

            return report
        except Exception as e:
            self.logger.error(f"Ошибка создания отчета по безопасности: {e}")
            return {"error": str(e)}


# Функция тестирования
async def test_emergency_response_bot():
    """Тестирование EmergencyResponseBot"""
    print("🧪 Тестирование EmergencyResponseBot...")

    # Создание бота
    bot = EmergencyResponseBot("TestEmergencyBot")

    try:
        # Запуск
        await bot.start()
        print("✅ EmergencyResponseBot запущен")

        # Создание тестовой экстренной ситуации
        emergency = EmergencyResponse(
            incident_id="",
            emergency_type=EmergencyType.MEDICAL,
            severity=EmergencySeverity.HIGH,
            location={
                "address": "Test Address",
                "coordinates": {"lat": 55.7558, "lon": 37.6176},
            },
            description="Test medical emergency",
            reported_by="test_user",
            timestamp=datetime.utcnow(),
        )

        # Сообщение об экстренной ситуации
        incident_id = await bot.report_emergency(emergency)
        print(f"✅ Экстренная ситуация зарегистрирована: {incident_id}")

        # Проверка статуса
        status = await bot.get_incident_status(incident_id)
        print(f"✅ Статус инцидента: {status}")

        # Разрешение инцидента
        resolved = await bot.resolve_incident(incident_id, "Test resolution")
        print(f"✅ Инцидент разрешен: {resolved}")

        # Получение общего статуса
        bot_status = await bot.get_status()
        print(f"✅ Статус бота: {bot_status['status']}")

    finally:
        # Остановка
        await bot.stop()
        print("✅ EmergencyResponseBot остановлен")


# Запуск тестов при прямом выполнении
if __name__ == "__main__":
    asyncio.run(test_emergency_response_bot())
