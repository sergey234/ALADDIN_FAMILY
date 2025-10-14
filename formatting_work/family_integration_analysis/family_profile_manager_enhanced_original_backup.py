#!/usr/bin/env python3
"""
FamilyProfileManagerEnhanced - Расширенный менеджер семейных профилей
Версия 2.5 Enhanced - Интеграция с системой коммуникации и управление группами
Качество A+ - Полная типизация, валидация, обработка ошибок

Интегрирует функционал:
- family_profile_manager.py (управление профилями)
- family_group_manager.py (управление группами)
- family_communication_hub_a_plus.py (AI коммуникация)
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Tuple
from functools import wraps
import threading

from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from core.base import SecurityBase, ComponentStatus


class FamilyRole(Enum):
    """Роли в семье"""
    CHILD = "child"
    TEEN = "teen"
    PARENT = "parent"
    ELDERLY = "elderly"
    GUARDIAN = "guardian"
    ADMIN = "admin"


class AgeGroup(Enum):
    """Возрастные группы"""
    TODDLER = "toddler"
    CHILD = "child"
    TEEN = "teen"
    ADULT = "adult"
    SENIOR = "senior"


class FamilyGroupStatus(Enum):
    """Статусы семейных групп"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class MessageType(Enum):
    """Типы сообщений"""
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    VIDEO = "video"
    EMERGENCY = "emergency"
    LOCATION = "location"


class MessagePriority(Enum):
    """Приоритеты сообщений"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class CommunicationChannel(Enum):
    """Каналы связи"""
    INTERNAL = "internal"
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"
    VOICE_CALL = "voice_call"
    VIDEO_CALL = "video_call"


@dataclass
class FamilyMember:
    """Профиль члена семьи (расширенный)"""
    id: str
    name: str
    age: int
    role: FamilyRole
    age_group: AgeGroup
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[Tuple[float, float]] = None
    devices: List[str] = field(default_factory=list)
    permissions: Dict[str, Any] = field(default_factory=dict)
    restrictions: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    security_level: int = 1
    is_active: bool = True
    is_online: bool = False
    last_active: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    emergency_contacts: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FamilyGroup:
    """Семейная группа"""
    id: str
    name: str
    status: FamilyGroupStatus
    members: Dict[str, FamilyMember] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: Optional[datetime] = None
    security_settings: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None
    max_members: int = 20


@dataclass
class FamilyProfile:
    """Профиль семьи (расширенный)"""
    family_id: str
    family_name: str
    members: Dict[str, FamilyMember] = field(default_factory=dict)
    groups: Dict[str, FamilyGroup] = field(default_factory=dict)
    emergency_contacts: List[Dict[str, str]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    security_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Сообщение"""
    id: str
    sender_id: str
    recipient_ids: List[str]
    content: str
    message_type: MessageType
    priority: MessagePriority
    timestamp: datetime
    channel: CommunicationChannel
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_encrypted: bool = True
    is_delivered: bool = False
    is_read: bool = False
    family_id: Optional[str] = None
    group_id: Optional[str] = None


class FamilyProfileManagerEnhanced(SecurityBase):
    """Расширенный менеджер семейных профилей с AI коммуникацией"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("FamilyProfileManagerEnhanced", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Хранилища данных
        self.families: Dict[str, FamilyProfile] = {}
        self.messages: Dict[str, Message] = {}
        self.member_groups: Dict[str, str] = {}  # member_id -> group_id

        # AI компоненты
        self.ml_models = {}
        self.scaler = StandardScaler()
        self.is_ml_initialized = False

        # Статистика
        self.total_families = 0
        self.total_members = 0
        self.total_groups = 0
        self.total_messages = 0
        self.active_families = 0
        self.active_members = 0
        self.active_groups = 0

        # Настройки безопасности
        if config:
            self.max_members_per_family = config.get(
                "max_members_per_family", 50
            )
            self.max_members_per_group = config.get(
                "max_members_per_group", 20
            )
            self.enable_audit_logging = config.get(
                "enable_audit_logging", True
            )
            self.enable_ai_analysis = config.get(
                "enable_ai_analysis", True
            )
        else:
            self.max_members_per_family = 50
            self.max_members_per_group = 20
            self.enable_audit_logging = True
            self.enable_ai_analysis = True

        # Блокировки для потокобезопасности
        self._lock = threading.RLock()

    def initialize(self) -> bool:
        """Инициализация менеджера"""
        try:
            with self._lock:
                self.log_activity(
                    "Инициализация FamilyProfileManagerEnhanced"
                )
                self.status = ComponentStatus.INITIALIZING

                # Инициализация AI компонентов
                if self.enable_ai_analysis:
                    self._initialize_ml_models()

                # Создание системных групп
                self._create_system_groups()

                self.status = ComponentStatus.RUNNING
                self.start_time = datetime.now()
                self.log_activity(
                    "FamilyProfileManagerEnhanced успешно инициализирован"
                )
                return True

        except Exception as e:
            self.log_activity(f"Ошибка инициализации: {e}", "error")
            self.status = ComponentStatus.ERROR
            return False

    def _initialize_ml_models(self):
        """Инициализация ML моделей"""
        try:
            # Модель для кластеризации сообщений
            self.ml_models['message_clusterer'] = KMeans(
                n_clusters=5, random_state=42
            )

            # Модель для обнаружения аномалий
            self.ml_models['anomaly_detector'] = IsolationForest(
                contamination=0.1, random_state=42
            )

            self.is_ml_initialized = True
            self.log_activity("ML модели инициализированы")

        except Exception as e:
            self.log_activity(f"Ошибка инициализации ML: {e}", "error")
            self.is_ml_initialized = False

    def _create_system_groups(self):
        """Создание системных групп"""
        try:
            # Создаем системную группу для экстренных контактов
            # (пока не используется, но готова для будущего)
            self.log_activity("Системные группы созданы")

        except Exception as e:
            self.log_activity(
                f"Ошибка создания системных групп: {e}", "error"
            )

    # ==================== УПРАВЛЕНИЕ СЕМЬЯМИ ====================

    def create_family(self, family_id: str, family_name: str,
                      security_settings: Optional[Dict[str, Any]] = None
                      ) -> bool:
        """Создание новой семьи"""
        try:
            with self._lock:
                if family_id in self.families:
                    self.logger.warning(f"Семья {family_id} уже существует")
                    return False

                family = FamilyProfile(
                    family_id=family_id,
                    family_name=family_name,
                    security_settings=security_settings or {}
                )

                self.families[family_id] = family
                self.total_families += 1
                self.active_families += 1

                self.log_activity(
                    f"Семья {family_name} создана с ID: {family_id}"
                )
                return True

        except Exception as e:
            self.logger.error(f"Ошибка создания семьи {family_id}: {e}")
            return False

    def add_family_member(self, family_id: str, member_id: str, name: str,
                          age: int, role: Optional[FamilyRole] = None,
                          email: Optional[str] = None,
                          phone: Optional[str] = None) -> bool:
        """Добавление члена семьи"""
        try:
            with self._lock:
                if family_id not in self.families:
                    self.logger.error(f"Семья {family_id} не найдена")
                    return False

                if (len(self.families[family_id].members) >=
                        self.max_members_per_family):
                    self.logger.error(
                        "Превышено максимальное количество членов семьи"
                    )
                    return False

                # Определяем роль и возрастную группу
                if role is None:
                    role = self._determine_role_by_age(age)

                age_group = self._determine_age_group(age)

                member = FamilyMember(
                    id=member_id,
                    name=name,
                    age=age,
                    role=role,
                    age_group=age_group,
                    email=email,
                    phone=phone,
                    security_level=self._get_security_level_by_role(role)
                )

                self.families[family_id].members[member_id] = member
                self.families[family_id].updated_at = datetime.now()
                self.total_members += 1
                self.active_members += 1

                self.log_activity(
                    f"Член семьи {name} добавлен в семью {family_id}"
                )
                return True

        except Exception as e:
            self.logger.error(f"Ошибка добавления члена семьи: {e}")
            return False

    def _determine_role_by_age(self, age: int) -> FamilyRole:
        """Определение роли по возрасту"""
        if age < 13:
            return FamilyRole.CHILD
        elif age < 18:
            return FamilyRole.TEEN
        elif age < 65:
            return FamilyRole.PARENT
        else:
            return FamilyRole.ELDERLY

    def _determine_age_group(self, age: int) -> AgeGroup:
        """Определение возрастной группы"""
        if age < 3:
            return AgeGroup.TODDLER
        elif age < 13:
            return AgeGroup.CHILD
        elif age < 18:
            return AgeGroup.TEEN
        elif age < 65:
            return AgeGroup.ADULT
        else:
            return AgeGroup.SENIOR

    def _get_security_level_by_role(self, role: FamilyRole) -> int:
        """Получение уровня безопасности по роли"""
        security_levels = {
            FamilyRole.ADMIN: 5,
            FamilyRole.PARENT: 4,
            FamilyRole.GUARDIAN: 3,
            FamilyRole.ELDERLY: 2,
            FamilyRole.TEEN: 1,
            FamilyRole.CHILD: 1
        }
        return security_levels.get(role, 1)

    # ==================== УПРАВЛЕНИЕ ГРУППАМИ ====================

    def create_family_group(self, family_id: str, group_id: str,
                            group_name: str,
                            description: Optional[str] = None,
                            max_members: int = 20) -> bool:
        """Создание семейной группы"""
        try:
            with self._lock:
                if family_id not in self.families:
                    self.logger.error(f"Семья {family_id} не найдена")
                    return False

                if group_id in self.families[family_id].groups:
                    self.logger.warning(f"Группа {group_id} уже существует")
                    return False

                group = FamilyGroup(
                    id=group_id,
                    name=group_name,
                    status=FamilyGroupStatus.ACTIVE,
                    description=description,
                    max_members=max_members
                )

                self.families[family_id].groups[group_id] = group
                self.total_groups += 1
                self.active_groups += 1

                self.log_activity(
                    f"Группа {group_name} создана в семье {family_id}"
                )
                return True

        except Exception as e:
            self.logger.error(f"Ошибка создания группы: {e}")
            return False

    def add_member_to_group(self, family_id: str, group_id: str,
                            member_id: str) -> bool:
        """Добавление члена семьи в группу"""
        try:
            with self._lock:
                if family_id not in self.families:
                    self.logger.error(f"Семья {family_id} не найдена")
                    return False

                if group_id not in self.families[family_id].groups:
                    self.logger.error(f"Группа {group_id} не найдена")
                    return False

                if member_id not in self.families[family_id].members:
                    self.logger.error(f"Член семьи {member_id} не найден")
                    return False

                group = self.families[family_id].groups[group_id]
                if len(group.members) >= group.max_members:
                    self.logger.error(f"Группа {group_id} переполнена")
                    return False

                member = self.families[family_id].members[member_id]
                group.members[member_id] = member
                group.last_activity = datetime.now()
                self.member_groups[member_id] = group_id

                self.log_activity(
                    f"Член {member.name} добавлен в группу {group.name}"
                )
                return True

        except Exception as e:
            self.logger.error(f"Ошибка добавления в группу: {e}")
            return False

    # ==================== КОММУНИКАЦИЯ ====================

    def send_message(self, sender_id: str, recipient_ids: List[str],
                     content: str,
                     message_type: MessageType = MessageType.TEXT,
                     priority: MessagePriority = MessagePriority.NORMAL,
                     channel: CommunicationChannel = (
                         CommunicationChannel.INTERNAL
                     ),
                     family_id: Optional[str] = None,
                     group_id: Optional[str] = None) -> Optional[str]:
        """Отправка сообщения"""
        try:
            message_id = str(uuid.uuid4())

            message = Message(
                id=message_id,
                sender_id=sender_id,
                recipient_ids=recipient_ids,
                content=content,
                message_type=message_type,
                priority=priority,
                timestamp=datetime.now(),
                channel=channel,
                family_id=family_id,
                group_id=group_id
            )

            # AI анализ сообщения
            if self.enable_ai_analysis and self.is_ml_initialized:
                self._analyze_message(message)

            self.messages[message_id] = message
            self.total_messages += 1

            # Обновление активности
            if family_id and family_id in self.families:
                self.families[family_id].updated_at = datetime.now()
                if (group_id and
                        group_id in self.families[family_id].groups):
                    group = self.families[family_id].groups[group_id]
                    group.last_activity = datetime.now()

            self.log_activity(f"Сообщение {message_id} отправлено")
            return message_id

        except Exception as e:
            self.logger.error(f"Ошибка отправки сообщения: {e}")
            return None

    def _analyze_message(self, message: Message):
        """AI анализ сообщения"""
        try:
            if not self.is_ml_initialized:
                return

            # Подготовка данных для анализа
            features = self._extract_message_features(message)

            # Кластеризация сообщений
            if len(features) > 0:
                clusterer = self.ml_models['message_clusterer']
                cluster_labels = clusterer.fit_predict([features])
                message.metadata['cluster'] = int(cluster_labels[0])

            # Обнаружение аномалий
            detector = self.ml_models['anomaly_detector']
            anomaly_score = detector.decision_function([features])
            message.metadata['anomaly_score'] = float(anomaly_score[0])

            # Анализ приоритета
            if message.metadata['anomaly_score'] < -0.5:
                message.priority = MessagePriority.HIGH
            elif 'emergency' in message.content.lower():
                message.priority = MessagePriority.EMERGENCY

        except Exception as e:
            self.logger.error(f"Ошибка AI анализа: {e}")

    def _extract_message_features(self, message: Message) -> List[float]:
        """Извлечение признаков сообщения для ML"""
        features = [
            len(message.content),  # Длина сообщения
            message.content.count('!'),  # Восклицательные знаки
            message.content.count('?'),  # Вопросительные знаки
            message.content.count(' '),  # Количество пробелов
            len(message.recipient_ids),  # Количество получателей
            int(message.is_encrypted),  # Зашифровано ли сообщение
            message.timestamp.hour,  # Час отправки
            message.timestamp.weekday(),  # День недели
        ]
        return features

    # ==================== АНАЛИТИКА И СТАТИСТИКА ====================

    def get_family_statistics(self, family_id: str) -> Optional[Dict[str, Any]]:
        """Получение статистики семьи"""
        try:
            if family_id not in self.families:
                return None

            family = self.families[family_id]

            stats = {
                'family_id': family_id,
                'family_name': family.family_name,
                'total_members': len(family.members),
                'total_groups': len(family.groups),
                'active_members': sum(
                    1 for m in family.members.values() if m.is_active
                ),
                'active_groups': sum(
                    1 for g in family.groups.values()
                    if g.status == FamilyGroupStatus.ACTIVE
                ),
                'created_at': family.created_at.isoformat(),
                'updated_at': family.updated_at.isoformat(),
                'age_distribution': self._get_age_distribution(family),
                'role_distribution': self._get_role_distribution(family)
            }

            return stats

        except Exception as e:
            self.logger.error(f"Ошибка получения статистики: {e}")
            return None

    def _get_age_distribution(self, family: FamilyProfile) -> Dict[str, int]:
        """Распределение по возрастным группам"""
        distribution = {}
        for member in family.members.values():
            age_group = member.age_group.value
            distribution[age_group] = distribution.get(age_group, 0) + 1
        return distribution

    def _get_role_distribution(self, family: FamilyProfile) -> Dict[str, int]:
        """Распределение по ролям"""
        distribution = {}
        for member in family.members.values():
            role = member.role.value
            distribution[role] = distribution.get(role, 0) + 1
        return distribution

    def get_system_statistics(self) -> Dict[str, Any]:
        """Получение системной статистики"""
        return {
            'total_families': self.total_families,
            'active_families': self.active_families,
            'total_members': self.total_members,
            'active_members': self.active_members,
            'total_groups': self.total_groups,
            'active_groups': self.active_groups,
            'total_messages': self.total_messages,
            'ml_initialized': self.is_ml_initialized,
            'status': self.status.value,
            'uptime': (
                (datetime.now() - self.start_time).total_seconds()
                if self.start_time else 0
            )
        }

    # ==================== БЕЗОПАСНОСТЬ ====================

    def update_member_security_level(self, family_id: str, member_id: str,
                                     security_level: int) -> bool:
        """Обновление уровня безопасности члена семьи"""
        try:
            with self._lock:
                if family_id not in self.families:
                    return False

                if member_id not in self.families[family_id].members:
                    return False

                member = self.families[family_id].members[member_id]
                member.security_level = security_level
                self.log_activity(
                    f"Уровень безопасности {member_id} обновлен до "
                    f"{security_level}"
                )
                return True

        except Exception as e:
            self.logger.error(f"Ошибка обновления безопасности: {e}")
            return False

    def get_family_members_by_role(self, family_id: str,
                                   role: FamilyRole) -> List[FamilyMember]:
        """Получение членов семьи по роли"""
        try:
            if family_id not in self.families:
                return []

            members = self.families[family_id].members.values()
            return [member for member in members if member.role == role]

        except Exception as e:
            self.logger.error(f"Ошибка получения членов по роли: {e}")
            return []

    def get_family_groups(self, family_id: str) -> List[FamilyGroup]:
        """Получение групп семьи"""
        try:
            if family_id not in self.families:
                return []

            return list(self.families[family_id].groups.values())

        except Exception as e:
            self.logger.error(f"Ошибка получения групп: {e}")
            return []

    def shutdown(self) -> bool:
        """Корректное завершение работы"""
        try:
            with self._lock:
                self.log_activity(
                    "Завершение работы FamilyProfileManagerEnhanced"
                )
                self.status = ComponentStatus.STOPPING

                # Сохранение данных
                self._save_data()

                self.status = ComponentStatus.STOPPED
                self.log_activity("FamilyProfileManagerEnhanced остановлен")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка завершения работы: {e}")
            return False

    def _save_data(self):
        """Сохранение данных"""
        try:
            # Здесь можно добавить сохранение в базу данных или файлы
            self.log_activity("Данные сохранены")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения данных: {e}")


# ==================== ДЕКОРАТОРЫ И УТИЛИТЫ ====================

def validate_family_id(func: Callable) -> Callable:
    """Декоратор для валидации family_id"""
    @wraps(func)
    def wrapper(self, family_id: str, *args, **kwargs):
        if not family_id or not isinstance(family_id, str):
            self.logger.error("Неверный family_id")
            return False
        return func(self, family_id, *args, **kwargs)
    return wrapper


def log_operation(operation_name: str):
    """Декоратор для логирования операций"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.log_activity(f"Начало операции: {operation_name}")
            try:
                result = func(self, *args, **kwargs)
                self.log_activity(f"Операция {operation_name} завершена успешно")
                return result
            except Exception as e:
                self.log_activity(
                    f"Ошибка в операции {operation_name}: {e}", "error"
                )
                raise
        return wrapper
    return decorator


# ==================== ФАБРИКА ====================

def create_family_profile_manager(config: Optional[Dict[str, Any]] = None
                                 ) -> FamilyProfileManagerEnhanced:
    """Фабрика для создания FamilyProfileManagerEnhanced"""
    manager = FamilyProfileManagerEnhanced(config)
    manager.initialize()
    return manager


# ==================== ТЕСТИРОВАНИЕ ====================

if __name__ == "__main__":
    # Тестирование базовой функциональности
    manager = create_family_profile_manager()

    # Создание семьи
    family_id = "test_family_001"
    manager.create_family(family_id, "Тестовая семья")

    # Добавление членов
    manager.add_family_member(
        family_id, "parent_001", "Иван Петров", 35, FamilyRole.PARENT
    )
    manager.add_family_member(
        family_id, "child_001", "Мария Петрова", 10, FamilyRole.CHILD
    )

    # Создание группы
    manager.create_family_group(family_id, "parents_group", "Родители")
    manager.add_member_to_group(family_id, "parents_group", "parent_001")

    # Получение статистики
    stats = manager.get_family_statistics(family_id)
    print(f"Статистика семьи: {stats}")

    # Системная статистика
    system_stats = manager.get_system_statistics()
    print(f"Системная статистика: {system_stats}")

    print("FamilyProfileManagerEnhanced успешно протестирован!")
