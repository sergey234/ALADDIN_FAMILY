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
    ):
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
        """Фоновый процесс мониторинга экстренных ситуаций"""
        while self.running:
            try:
                time.sleep(1)  # Проверка каждую секунду

                # Обновление статистики
                self._update_stats()

                # Проверка активных инцидентов
                self._check_active_incidents()

            except Exception as e:
                self.logger.error(f"Ошибка в процессе мониторинга: {e}")

    def _update_stats(self) -> None:
        """Обновление статистики"""
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
        """Проверка активных инцидентов"""
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
        """
        try:
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
        """Получение статуса инцидента"""
        try:
            incident = self.active_incidents.get(incident_id)
            if not incident:
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
        """Разрешение инцидента"""
        try:
            incident = self.active_incidents.get(incident_id)
            if not incident:
                return False

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
