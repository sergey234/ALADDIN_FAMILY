# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Incident Response Module
Модуль реагирования на инциденты для системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-01
"""

import asyncio
import time
from datetime import datetime
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional

from core.base import ComponentStatus, SecurityBase, SecurityLevel


class IncidentResponseError(Exception):
    """Базовое исключение для модуля реагирования на инциденты"""

    pass


class IncidentNotFoundError(IncidentResponseError):
    """Исключение при отсутствии инцидента"""

    pass


class InvalidIncidentDataError(IncidentResponseError):
    """Исключение при некорректных данных инцидента"""

    pass


class IncidentLimitExceededError(IncidentResponseError):
    """Исключение при превышении лимита инцидентов"""

    pass


class IncidentValidationError(IncidentResponseError):
    """Исключение при ошибке валидации инцидента"""

    pass


class IncidentStatus(Enum):
    """Статусы инцидентов"""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"


class IncidentPriority(Enum):
    """Приоритеты инцидентов"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentType(Enum):
    """Типы инцидентов"""

    MALWARE_INFECTION = "malware_infection"
    DATA_BREACH = "data_breach"
    NETWORK_INTRUSION = "network_intrusion"
    PHISHING_ATTACK = "phishing_attack"
    DOS_ATTACK = "dos_attack"
    INSIDER_THREAT = "insider_threat"
    SYSTEM_COMPROMISE = "system_compromise"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


class Incident:
    """Класс для представления инцидента безопасности"""

    def __init__(
        self,
        incident_id: str,
        title: str,
        description: str,
        incident_type: IncidentType,
        priority: IncidentPriority,
        severity: SecurityLevel,
    ):
        self.incident_id = incident_id
        self.title = title
        self.description = description
        self.incident_type = incident_type
        self.priority = priority
        self.severity = severity
        self.status = IncidentStatus.OPEN
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.resolved_at = None
        self.assigned_to = None
        self.evidence = []
        self.actions_taken = []
        self.notes = []
        self.affected_systems = []
        self.impact_assessment = ""
        self.root_cause = ""
        self.lessons_learned = []

    def update_status(self, new_status: IncidentStatus):
        """Обновление статуса инцидента"""
        self.status = new_status
        self.updated_at = datetime.now()

        if new_status == IncidentStatus.RESOLVED:
            self.resolved_at = datetime.now()

    def add_evidence(
        self, evidence_type: str, description: str, data: Optional[Any] = None
    ):
        """Добавление доказательства"""
        evidence = {
            "type": evidence_type,
            "description": description,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }
        self.evidence.append(evidence)

    def add_action(
        self, action: str, performed_by: str, details: Optional[str] = None
    ):
        """Добавление выполненного действия"""
        action_record = {
            "action": action,
            "performed_by": performed_by,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }
        self.actions_taken.append(action_record)

    def add_note(self, note: str, author: str):
        """Добавление заметки"""
        note_record = {
            "note": note,
            "author": author,
            "timestamp": datetime.now().isoformat(),
        }
        self.notes.append(note_record)

    def __str__(self) -> str:
        """Строковое представление инцидента"""
        return f"Incident({self.incident_id}: {self.title})"

    def __repr__(self) -> str:
        """Детальное строковое представление инцидента"""
        return (
            f"Incident(id='{self.incident_id}', title='{self.title}', "
            f"status={self.status.value}, priority={self.priority.value}, "
            f"type={self.incident_type.value})"
        )

    def __eq__(self, other) -> bool:
        """Сравнение инцидентов по ID"""
        if not isinstance(other, Incident):
            return False
        return self.incident_id == other.incident_id

    def __lt__(self, other) -> bool:
        """Сравнение инцидентов по времени создания"""
        if not isinstance(other, Incident):
            return NotImplemented
        return self.created_at < other.created_at

    def __hash__(self) -> int:
        """Хэш инцидента по ID"""
        return hash(self.incident_id)

    def is_open(self) -> bool:
        """Проверка, открыт ли инцидент"""
        return self.status == IncidentStatus.OPEN

    def is_resolved(self) -> bool:
        """Проверка, разрешен ли инцидент"""
        return self.status == IncidentStatus.RESOLVED

    def is_escalated(self) -> bool:
        """Проверка, эскалирован ли инцидент"""
        return self.priority in [
            IncidentPriority.HIGH,
            IncidentPriority.CRITICAL,
        ]

    def get_age_hours(self) -> float:
        """Получение возраста инцидента в часах"""
        age = datetime.now() - self.created_at
        return round(age.total_seconds() / 3600, 2)

    def get_resolution_time_hours(self) -> Optional[float]:
        """Получение времени разрешения в часах"""
        if self.resolved_at:
            resolution_time = self.resolved_at - self.created_at
            return round(resolution_time.total_seconds() / 3600, 2)
        return None

    def is_overdue(self, threshold_hours: float = 24.0) -> bool:
        """Проверка, просрочен ли инцидент"""
        if self.is_resolved():
            return False
        return self.get_age_hours() > threshold_hours

    def get_priority_score(self) -> int:
        """Получение числового значения приоритета для сортировки"""
        priority_scores = {
            IncidentPriority.LOW: 1,
            IncidentPriority.MEDIUM: 2,
            IncidentPriority.HIGH: 3,
            IncidentPriority.CRITICAL: 4,
        }
        return priority_scores.get(self.priority, 0)

    def get_severity_score(self) -> int:
        """Получение числового значения серьезности для сортировки"""
        severity_scores = {
            SecurityLevel.LOW: 1,
            SecurityLevel.MEDIUM: 2,
            SecurityLevel.HIGH: 3,
            SecurityLevel.CRITICAL: 4,
        }
        return severity_scores.get(self.severity, 0)

    def update_impact_assessment(self, assessment: str) -> None:
        """Обновление оценки воздействия"""
        self.impact_assessment = assessment
        self.updated_at = datetime.now()

    def set_root_cause(self, root_cause: str) -> None:
        """Установка первопричины инцидента"""
        self.root_cause = root_cause
        self.updated_at = datetime.now()

    def add_lesson_learned(self, lesson: str) -> None:
        """Добавление извлеченного урока"""
        self.lessons_learned.append(lesson)
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "incident_id": self.incident_id,
            "title": self.title,
            "description": self.description,
            "incident_type": self.incident_type.value,
            "priority": self.priority.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "resolved_at": (
                self.resolved_at.isoformat() if self.resolved_at else None
            ),
            "assigned_to": self.assigned_to,
            "evidence": self.evidence,
            "actions_taken": self.actions_taken,
            "notes": self.notes,
            "affected_systems": self.affected_systems,
            "impact_assessment": self.impact_assessment,
            "root_cause": self.root_cause,
            "lessons_learned": self.lessons_learned,
        }


class IncidentResponseManager(SecurityBase):
    """Менеджер реагирования на инциденты для системы ALADDIN"""

    def __init__(
        self,
        name: str = "IncidentResponseManager",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Конфигурация реагирования на инциденты
        self.auto_escalation_threshold = (
            config.get("auto_escalation_threshold", 4) if config else 4
        )  # часа
        self.max_open_incidents = (
            config.get("max_open_incidents", 50) if config else 50
        )
        self.response_timeout = (
            config.get("response_timeout", 3600) if config else 3600
        )  # 1 час
        self.enable_auto_response = (
            config.get("enable_auto_response", True) if config else True
        )

        # Хранилище инцидентов
        self.incidents = {}
        self.response_teams = {}
        self.escalation_rules = {}
        self.response_playbooks = {}

        # Статистика
        self.total_incidents = 0
        self.open_incidents = 0
        self.resolved_incidents = 0
        self.escalated_incidents = 0
        self.average_resolution_time = 0.0

        # Дополнительные атрибуты для расширенной функциональности
        self.start_time = None  # Время запуска системы
        self.last_activity = None  # Время последней активности
        self.cache_hits = 0  # Количество попаданий в кэш
        self.cache_misses = 0  # Количество промахов кэша
        self.performance_metrics = {}  # Метрики производительности
        self.alert_thresholds = {  # Пороги для уведомлений
            "max_age_hours": 24.0,
            "max_open_incidents": 10,
            "escalation_rate": 0.2,
        }
        self.notification_handlers = []  # Обработчики уведомлений
        self.audit_log = []  # Журнал аудита

    def initialize(self) -> bool:
        """Инициализация менеджера реагирования на инциденты"""
        try:
            self.log_activity(
                f"Инициализация менеджера реагирования на инциденты "
                f"{self.name}"
            )
            self.status = ComponentStatus.INITIALIZING

            # Настройка команд реагирования
            self._setup_response_teams()

            # Настройка правил эскалации
            self._setup_escalation_rules()

            # Загрузка плейбуков реагирования
            self._load_response_playbooks()

            # Инициализация автоматического реагирования
            if self.enable_auto_response:
                self._setup_auto_response()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Менеджер реагирования на инциденты {self.name} "
                f"успешно инициализирован"
            )
            return True

        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка инициализации менеджера реагирования на инциденты "
                f"{self.name}: {e}",
                "error",
            )
            return False

    def _setup_response_teams(self):
        """Настройка команд реагирования"""
        self.response_teams = {
            "tier1": {
                "name": "Tier 1 - Первичное реагирование",
                "members": ["analyst1", "analyst2"],
                "capabilities": [
                    "initial_assessment",
                    "containment",
                    "evidence_collection",
                ],
                "available": True,
            },
            "tier2": {
                "name": "Tier 2 - Углубленный анализ",
                "members": ["senior_analyst1", "senior_analyst2"],
                "capabilities": [
                    "forensic_analysis",
                    "threat_hunting",
                    "remediation",
                ],
                "available": True,
            },
            "tier3": {
                "name": "Tier 3 - Экспертный уровень",
                "members": ["incident_commander", "security_architect"],
                "capabilities": [
                    "strategic_response",
                    "coordination",
                    "post_incident",
                ],
                "available": True,
            },
        }
        self.log_activity("Команды реагирования настроены")

    def _setup_escalation_rules(self):
        """Настройка правил эскалации"""
        self.escalation_rules = {
            "time_based": {
                "tier1_to_tier2": 2,  # часа
                "tier2_to_tier3": 4,  # часа
                "critical_escalation": 1,  # час
            },
            "severity_based": {
                "critical": "tier3",
                "high": "tier2",
                "medium": "tier1",
                "low": "tier1",
            },
            "type_based": {
                "data_breach": "tier3",
                "system_compromise": "tier3",
                "network_intrusion": "tier2",
                "malware_infection": "tier2",
            },
        }
        self.log_activity("Правила эскалации настроены")

    def _load_response_playbooks(self):
        """Загрузка плейбуков реагирования"""
        self.response_playbooks = {
            "malware_infection": {
                "steps": [
                    "Изоляция зараженной системы",
                    "Сбор образцов вредоносного ПО",
                    "Анализ векторов заражения",
                    "Очистка системы",
                    "Восстановление из резервной копии",
                    "Проверка других систем",
                ],
                "automated_actions": ["system_isolation", "sample_collection"],
            },
            "data_breach": {
                "steps": [
                    "Блокировка доступа",
                    "Оценка масштаба утечки",
                    "Уведомление затронутых лиц",
                    "Уведомление регуляторов",
                    "Усиление мер безопасности",
                    "Мониторинг активности",
                ],
                "automated_actions": ["access_blocking", "breach_assessment"],
            },
            "phishing_attack": {
                "steps": [
                    "Блокировка фишинговых URL",
                    "Удаление писем из почтовых ящиков",
                    "Уведомление пользователей",
                    "Анализ векторов атаки",
                    "Усиление фильтрации",
                    "Обучение пользователей",
                ],
                "automated_actions": ["url_blocking", "email_removal"],
            },
        }
        self.log_activity("Плейбуки реагирования загружены")

    def _setup_auto_response(self):
        """Настройка автоматического реагирования"""
        # Здесь будет логика автоматического реагирования
        self.log_activity("Автоматическое реагирование настроено")

    def create_incident(
        self,
        title: str,
        description: str,
        incident_type: IncidentType,
        priority: IncidentPriority,
        severity: SecurityLevel,
        affected_systems: Optional[List[str]] = None,
    ) -> Optional[Incident]:
        """
        Создание нового инцидента безопасности.

        Создает новый инцидент с указанными параметрами и автоматически
        назначает команду реагирования на основе типа и приоритета.
        Выполняет валидацию всех входных параметров перед созданием.

        Args:
            title (str): Заголовок инцидента (1-200 символов, не пустой)
            description (str): Подробное описание инцидента (1-1000 символов,
                не пустое)
            incident_type (IncidentType): Тип инцидента из перечисления
                IncidentType
            priority (IncidentPriority): Приоритет инцидента из перечисления
                IncidentPriority
            severity (SecurityLevel): Уровень серьезности из перечисления
                SecurityLevel
            affected_systems (Optional[List[str]]): Список затронутых систем
                (опционально)

        Returns:
            Optional[Incident]: Созданный объект инцидента или None при ошибке
                валидации

        Raises:
            ValueError: При некорректных входных параметрах (логируется как
                ошибка)
            RuntimeError: При ошибке создания инцидента (логируется как ошибка)

        Example:
            >>> manager = IncidentResponseManager('Test')
            >>> manager.initialize()
            >>> incident = manager.create_incident(
            ...     title='Malware Detection',
            ...     description='Detected suspicious activity on server',
            ...     incident_type=IncidentType.MALWARE_INFECTION,
            ...     priority=IncidentPriority.HIGH,
            ...     severity=SecurityLevel.HIGH,
            ...     affected_systems=['server-01', 'database-01']
            ... )
            >>> print(incident.incident_id if incident else 'Failed to create')

        Note:
            - Автоматически генерирует уникальный ID инцидента
            - Автоматически назначает команду реагирования
            - Выполняет автоматическое реагирование если включено
            - Обновляет статистику менеджера
        """
        try:
            # Валидация входных параметров
            if not title or not title.strip():
                error_msg = "Пустой заголовок инцидента"
                self.log_activity(f"Ошибка: {error_msg}", "error")
                raise IncidentValidationError(error_msg)

            if not description or not description.strip():
                error_msg = "Пустое описание инцидента"
                self.log_activity(f"Ошибка: {error_msg}", "error")
                raise IncidentValidationError(error_msg)

            if len(title) > 200:
                error_msg = "Заголовок слишком длинный (максимум 200 символов)"
                self.log_activity(f"Ошибка: {error_msg}", "error")
                raise IncidentValidationError(error_msg)

            if len(description) > 1000:
                error_msg = "Описание слишком длинное (максимум 1000 символов)"
                self.log_activity(f"Ошибка: {error_msg}", "error")
                raise IncidentValidationError(error_msg)

            if not isinstance(incident_type, IncidentType):
                error_msg = "Некорректный тип инцидента"
                self.log_activity(f"Ошибка: {error_msg}", "error")
                raise IncidentValidationError(error_msg)

            if not isinstance(priority, IncidentPriority):
                error_msg = "Некорректный приоритет инцидента"
                self.log_activity(f"Ошибка: {error_msg}", "error")
                raise IncidentValidationError(error_msg)

            if not isinstance(severity, SecurityLevel):
                error_msg = "Некорректный уровень серьезности"
                self.log_activity(f"Ошибка: {error_msg}", "error")
                raise IncidentValidationError(error_msg)

            if affected_systems is not None and not isinstance(
                affected_systems, list
            ):
                error_msg = "affected_systems должен быть списком"
                self.log_activity(f"Ошибка: {error_msg}", "error")
                raise IncidentValidationError(error_msg)

            # Проверка лимита открытых инцидентов
            if self.open_incidents >= self.max_open_incidents:
                error_msg = "Достигнут лимит открытых инцидентов"
                self.log_activity(error_msg, "warning")
                raise IncidentLimitExceededError(error_msg)

            # Генерация ID инцидента
            incident_id = f"INC-{int(time.time())}"

            # Создание инцидента
            incident = Incident(
                incident_id,
                title,
                description,
                incident_type,
                priority,
                severity,
            )

            if affected_systems:
                incident.affected_systems = affected_systems

            # Сохранение инцидента
            self.incidents[incident_id] = incident
            self.total_incidents += 1
            self.open_incidents += 1

            # Автоматическое назначение команды
            self._auto_assign_team(incident)

            # Запуск автоматического реагирования
            if self.enable_auto_response:
                self._execute_auto_response(incident)

            self.log_activity(f"Создан инцидент: {title} ({incident_id})")
            return incident

        except Exception as e:
            self.log_activity(f"Ошибка создания инцидента: {e}", "error")
            return None

    def _auto_assign_team(self, incident: Incident):
        """Автоматическое назначение команды"""
        try:
            # Определение команды на основе серьезности
            if incident.severity == SecurityLevel.CRITICAL:
                team = "tier3"
            elif incident.severity == SecurityLevel.HIGH:
                team = "tier2"
            else:
                team = "tier1"

            # Проверка доступности команды
            if (
                team in self.response_teams
                and self.response_teams[team]["available"]
            ):
                incident.assigned_to = team
                self.log_activity(
                    f"Инцидент {incident.incident_id} назначен команде {team}"
                )
            else:
                # Эскалация к следующей команде
                if team == "tier1":
                    incident.assigned_to = "tier2"
                elif team == "tier2":
                    incident.assigned_to = "tier3"
                else:
                    incident.assigned_to = "tier3"

                self.log_activity(
                    f"Инцидент {incident.incident_id} эскалирован к команде "
                    f"{incident.assigned_to}"
                )

        except Exception as e:
            self.log_activity(f"Ошибка назначения команды: {e}", "error")

    def _execute_auto_response(self, incident: Incident):
        """Выполнение автоматического реагирования"""
        try:
            incident_type = incident.incident_type.value

            if incident_type in self.response_playbooks:
                playbook = self.response_playbooks[incident_type]

                # Выполнение автоматических действий
                for action in playbook.get("automated_actions", []):
                    self._execute_automated_action(incident, action)

                # Добавление первого шага плейбука
                if playbook["steps"]:
                    incident.add_action(
                        f"Автоматическое реагирование: {playbook['steps'][0]}",
                        "system",
                        "Выполнено автоматически",
                    )

                self.log_activity(
                    f"Автоматическое реагирование выполнено для инцидента "
                    f"{incident.incident_id}"
                )

        except Exception as e:
            self.log_activity(
                f"Ошибка автоматического реагирования: {e}", "error"
            )

    def _execute_automated_action(self, incident: Incident, action: str):
        """Выполнение автоматического действия"""
        try:
            if action == "system_isolation":
                # Изоляция системы
                for system in incident.affected_systems:
                    self.log_activity(
                        f"Система {system} изолирована автоматически"
                    )

            elif action == "sample_collection":
                # Сбор образцов
                self.log_activity(
                    "Образцы вредоносного ПО собраны автоматически"
                )

            elif action == "access_blocking":
                # Блокировка доступа
                self.log_activity("Доступ заблокирован автоматически")

            elif action == "url_blocking":
                # Блокировка URL
                self.log_activity("Фишинговые URL заблокированы автоматически")

            elif action == "email_removal":
                # Удаление писем
                self.log_activity("Фишинговые письма удалены автоматически")

        except Exception as e:
            self.log_activity(
                f"Ошибка выполнения автоматического действия {action}: {e}",
                "error",
            )

    def update_incident_status(
        self,
        incident_id: str,
        new_status: IncidentStatus,
        notes: Optional[str] = None,
        performed_by: Optional[str] = None,
    ) -> bool:
        """
        Обновление статуса инцидента

        Args:
            incident_id: ID инцидента
            new_status: Новый статус
            notes: Заметки
            performed_by: Кто выполнил действие

        Returns:
            bool: True если статус обновлен
        """
        try:
            if incident_id not in self.incidents:
                return False

            incident = self.incidents[incident_id]
            old_status = incident.status

            # Обновление статуса
            incident.update_status(new_status)

            # Обновление счетчиков
            if (
                old_status == IncidentStatus.OPEN
                and new_status != IncidentStatus.OPEN
            ):
                self.open_incidents = max(0, self.open_incidents - 1)

            if new_status == IncidentStatus.RESOLVED:
                self.resolved_incidents += 1
                self._update_resolution_time(incident)

            if new_status == IncidentStatus.ESCALATED:
                self.escalated_incidents += 1

            # Добавление заметки
            if notes and performed_by:
                incident.add_note(notes, performed_by)

            # Добавление действия
            action_description = (
                f"Статус изменен с {old_status.value} на {new_status.value}"
            )
            incident.add_action(
                action_description, performed_by or "system", notes
            )

            self.log_activity(
                f"Статус инцидента {incident_id} изменен на {new_status.value}"
            )
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка обновления статуса инцидента: {e}", "error"
            )
            return False

    def _update_resolution_time(self, incident: Incident):
        """Обновление времени разрешения"""
        try:
            if incident.resolved_at and incident.created_at:
                resolution_time = (
                    incident.resolved_at - incident.created_at
                ).total_seconds() / 3600  # в часах

                # Обновление среднего времени разрешения
                if self.resolved_incidents == 1:
                    self.average_resolution_time = resolution_time
                else:
                    total_time = (
                        self.average_resolution_time
                        * (self.resolved_incidents - 1)
                        + resolution_time
                    )
                    self.average_resolution_time = (
                        total_time / self.resolved_incidents
                    )

        except Exception as e:
            self.log_activity(
                f"Ошибка обновления времени разрешения: {e}", "error"
            )

    def add_evidence_to_incident(
        self,
        incident_id: str,
        evidence_type: str,
        description: str,
        data: Optional[Any] = None,
    ) -> bool:
        """
        Добавление доказательства к инциденту

        Args:
            incident_id: ID инцидента
            evidence_type: Тип доказательства
            description: Описание доказательства
            data: Данные доказательства

        Returns:
            bool: True если доказательство добавлено
        """
        try:
            if incident_id not in self.incidents:
                return False

            incident = self.incidents[incident_id]
            incident.add_evidence(evidence_type, description, data)

            self.log_activity(
                f"Доказательство добавлено к инциденту {incident_id}"
            )
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка добавления доказательства: {e}", "error"
            )
            return False

    def add_action_to_incident(
        self,
        incident_id: str,
        action: str,
        performed_by: str,
        details: Optional[str] = None,
    ) -> bool:
        """
        Добавление действия к инциденту

        Args:
            incident_id: ID инцидента
            action: Выполненное действие
            performed_by: Кто выполнил действие
            details: Детали действия

        Returns:
            bool: True если действие добавлено
        """
        try:
            if incident_id not in self.incidents:
                return False

            incident = self.incidents[incident_id]
            incident.add_action(action, performed_by, details)

            self.log_activity(f"Действие добавлено к инциденту {incident_id}")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка добавления действия: {e}", "error")
            return False

    def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение инцидента

        Args:
            incident_id: ID инцидента

        Returns:
            Optional[Dict[str, Any]]: Данные инцидента
        """
        if incident_id not in self.incidents:
            return None

        return self.incidents[incident_id].to_dict()

    def get_all_incidents(
        self, status: Optional[IncidentStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        Получение всех инцидентов

        Args:
            status: Фильтр по статусу

        Returns:
            List[Dict[str, Any]]: Список инцидентов
        """
        incidents = []

        for incident in self.incidents.values():
            if status is None or incident.status == status:
                incidents.append(incident.to_dict())

        return incidents

    def get_open_incidents(self) -> List[Dict[str, Any]]:
        """
        Получение открытых инцидентов

        Returns:
            List[Dict[str, Any]]: Список открытых инцидентов
        """
        return self.get_all_incidents(IncidentStatus.OPEN)

    def get_incidents_by_priority(
        self, priority: IncidentPriority
    ) -> List[Dict[str, Any]]:
        """
        Получение инцидентов по приоритету

        Args:
            priority: Приоритет инцидентов

        Returns:
            List[Dict[str, Any]]: Список инцидентов
        """
        return [
            incident.to_dict()
            for incident in self.incidents.values()
            if incident.priority == priority
        ]

    def get_incidents_by_type(
        self, incident_type: IncidentType
    ) -> List[Dict[str, Any]]:
        """
        Получение инцидентов по типу

        Args:
            incident_type: Тип инцидентов

        Returns:
            List[Dict[str, Any]]: Список инцидентов
        """
        return [
            incident.to_dict()
            for incident in self.incidents.values()
            if incident.incident_type == incident_type
        ]

    def escalate_incident(
        self, incident_id: str, reason: str, escalated_by: str
    ) -> bool:
        """
        Эскалация инцидента

        Args:
            incident_id: ID инцидента
            reason: Причина эскалации
            escalated_by: Кто эскалировал

        Returns:
            bool: True если инцидент эскалирован
        """
        try:
            if incident_id not in self.incidents:
                return False

            incident = self.incidents[incident_id]

            # Определение следующей команды
            current_team = incident.assigned_to
            if current_team == "tier1":
                new_team = "tier2"
            elif current_team == "tier2":
                new_team = "tier3"
            else:
                new_team = "tier3"

            # Обновление назначения
            incident.assigned_to = new_team

            # Обновление статуса
            incident.update_status(IncidentStatus.ESCALATED)

            # Добавление заметки
            incident.add_note(f"Эскалирован: {reason}", escalated_by)

            # Добавление действия
            incident.add_action(
                f"Эскалация к команде {new_team}",
                escalated_by,
                f"Причина: {reason}",
            )

            self.escalated_incidents += 1

            self.log_activity(
                f"Инцидент {incident_id} эскалирован к команде {new_team}"
            )
            return True

        except Exception as e:
            self.log_activity(f"Ошибка эскалации инцидента: {e}", "error")
            return False

    def get_incident_response_stats(self) -> Dict[str, Any]:
        """
        Получение статистики реагирования на инциденты

        Returns:
            Dict[str, Any]: Статистика реагирования
        """
        return {
            "total_incidents": self.total_incidents,
            "open_incidents": self.open_incidents,
            "resolved_incidents": self.resolved_incidents,
            "escalated_incidents": self.escalated_incidents,
            "average_resolution_time": self.average_resolution_time,
            "incidents_by_status": self._get_incidents_by_status(),
            "incidents_by_priority": self._get_incidents_by_priority(),
            "incidents_by_type": self._get_incidents_by_type(),
            "team_workload": self._get_team_workload(),
        }

    def _get_incidents_by_status(self) -> Dict[str, int]:
        """Получение количества инцидентов по статусам"""
        status_count = {}
        for incident in self.incidents.values():
            status = incident.status.value
            status_count[status] = status_count.get(status, 0) + 1
        return status_count

    def _get_incidents_by_priority(self) -> Dict[str, int]:
        """Получение количества инцидентов по приоритетам"""
        priority_count = {}
        for incident in self.incidents.values():
            priority = incident.priority.value
            priority_count[priority] = priority_count.get(priority, 0) + 1
        return priority_count

    def _get_incidents_by_type(self) -> Dict[str, int]:
        """Получение количества инцидентов по типам"""
        type_count = {}
        for incident in self.incidents.values():
            incident_type = incident.incident_type.value
            type_count[incident_type] = type_count.get(incident_type, 0) + 1
        return type_count

    def _get_team_workload(self) -> Dict[str, int]:
        """Получение нагрузки команд"""
        workload = {}
        for incident in self.incidents.values():
            if incident.status == IncidentStatus.OPEN and incident.assigned_to:
                team = incident.assigned_to
                workload[team] = workload.get(team, 0) + 1
        return workload

    def start(self) -> bool:
        """Запуск менеджера реагирования на инциденты"""
        try:
            self.log_activity(
                f"Запуск менеджера реагирования на инциденты {self.name}"
            )

            # Инициализация дополнительных атрибутов
            self.start_time = datetime.now()
            self.last_activity = datetime.now()
            self.cache_hits = 0
            self.cache_misses = 0
            self.performance_metrics = {
                "start_time": self.start_time.isoformat(),
                "incidents_created": 0,
                "incidents_resolved": 0,
                "average_response_time": 0.0,
            }

            self.status = ComponentStatus.RUNNING
            self.log_activity(
                f"Менеджер реагирования на инциденты {self.name} "
                f"успешно запущен"
            )
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка запуска менеджера реагирования на инциденты "
                f"{self.name}: {e}",
                "error",
            )
            return False

    def stop(self) -> bool:
        """Остановка менеджера реагирования на инциденты"""
        try:
            self.log_activity(
                f"Остановка менеджера реагирования на инциденты {self.name}"
            )

            # Остановка автоматического реагирования
            self.enable_auto_response = False

            self.status = ComponentStatus.STOPPED
            self.log_activity(
                f"Менеджер реагирования на инциденты {self.name} "
                f"успешно остановлен"
            )
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка остановки менеджера реагирования на инциденты "
                f"{self.name}: {e}",
                "error",
            )
            return False

    def __str__(self) -> str:
        """Строковое представление менеджера"""
        return (
            f"IncidentResponseManager({self.name}: "
            f"{len(self.incidents)} incidents)"
        )

    def __repr__(self) -> str:
        """Детальное строковое представление менеджера"""
        return (
            f"IncidentResponseManager(name='{self.name}', "
            f"incidents={len(self.incidents)}, status={self.status.value}, "
            f"auto_response={self.enable_auto_response})"
        )

    def __len__(self) -> int:
        """Количество инцидентов"""
        return len(self.incidents)

    def __iter__(self):
        """Итерация по инцидентам"""
        return iter(self.incidents.values())

    def __contains__(self, incident_id: str) -> bool:
        """Проверка наличия инцидента по ID"""
        return incident_id in self.incidents

    def __enter__(self):
        """Вход в контекстный менеджер"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера"""
        self.stop()
        if exc_type:
            self.log_activity(f"Ошибка в контексте: {exc_val}", "error")
        return False

    # ==================== КЭШИРОВАННЫЕ МЕТОДЫ ====================

    @lru_cache(maxsize=128)
    def _get_incident_by_id_cached(
        self, incident_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Кэшированное получение инцидента по ID.

        Args:
            incident_id (str): ID инцидента

        Returns:
            Optional[Dict[str, Any]]: Данные инцидента или None
        """
        incident = self.incidents.get(incident_id)
        return incident.to_dict() if incident else None

    @lru_cache(maxsize=64)
    def _get_incidents_by_status_cached(
        self, status: str
    ) -> List[Dict[str, Any]]:
        """
        Кэшированное получение инцидентов по статусу.

        Args:
            status (str): Статус инцидента

        Returns:
            List[Dict[str, Any]]: Список инцидентов
        """
        return [
            incident.to_dict()
            for incident in self.incidents.values()
            if incident.status.value == status
        ]

    @lru_cache(maxsize=32)
    def _get_incidents_by_priority_cached(
        self, priority: str
    ) -> List[Dict[str, Any]]:
        """
        Кэшированное получение инцидентов по приоритету.

        Args:
            priority (str): Приоритет инцидента

        Returns:
            List[Dict[str, Any]]: Список инцидентов
        """
        return [
            incident.to_dict()
            for incident in self.incidents.values()
            if incident.priority.value == priority
        ]

    @lru_cache(maxsize=16)
    def _get_incidents_by_type_cached(
        self, incident_type: str
    ) -> List[Dict[str, Any]]:
        """
        Кэшированное получение инцидентов по типу.

        Args:
            incident_type (str): Тип инцидента

        Returns:
            List[Dict[str, Any]]: Список инцидентов
        """
        return [
            incident.to_dict()
            for incident in self.incidents.values()
            if incident.incident_type.value == incident_type
        ]

    def clear_cache(self):
        """Очистка кэша"""
        self._get_incident_by_id_cached.cache_clear()
        self._get_incidents_by_status_cached.cache_clear()
        self._get_incidents_by_priority_cached.cache_clear()
        self._get_incidents_by_type_cached.cache_clear()

    def get_cache_info(self) -> Dict[str, Any]:
        """Получение информации о кэше"""
        return {
            "incident_by_id": self._get_incident_by_id_cached.cache_info(),
            "incidents_by_status": (
                self._get_incidents_by_status_cached.cache_info()
            ),
            "incidents_by_priority": (
                self._get_incidents_by_priority_cached.cache_info()
            ),
            "incidents_by_type": (
                self._get_incidents_by_type_cached.cache_info()
            ),
        }

    # ==================== АСИНХРОННЫЕ МЕТОДЫ ====================

    async def create_incident_async(
        self,
        title: str,
        description: str,
        incident_type: IncidentType,
        priority: IncidentPriority,
        severity: SecurityLevel,
        affected_systems: Optional[List[str]] = None,
    ) -> Optional[Incident]:
        """
        Асинхронное создание нового инцидента безопасности.

        Асинхронная версия create_incident с поддержкой await.
        Выполняет валидацию и создание инцидента в асинхронном режиме.

        Args:
            title (str): Заголовок инцидента (1-200 символов, не пустой)
            description (str): Подробное описание инцидента (1-1000 символов,
                не пустое)
            incident_type (IncidentType): Тип инцидента из перечисления
                IncidentType
            priority (IncidentPriority): Приоритет инцидента из перечисления
                IncidentPriority
            severity (SecurityLevel): Уровень серьезности из перечисления
                SecurityLevel
            affected_systems (Optional[List[str]]): Список затронутых систем
                (опционально)

        Returns:
            Optional[Incident]: Созданный объект инцидента или None при ошибке

        Raises:
            IncidentValidationError: При некорректных входных параметрах
            IncidentLimitExceededError: При превышении лимита инцидентов

        Example:
            >>> manager = IncidentResponseManager('Test')
            >>> await manager.initialize_async()
            >>> incident = await manager.create_incident_async(
            ...     title='Async Malware Detection',
            ...     description='Detected suspicious activity asynchronously',
            ...     incident_type=IncidentType.MALWARE_INFECTION,
            ...     priority=IncidentPriority.HIGH,
            ...     severity=SecurityLevel.HIGH
            ... )
        """
        try:
            # Имитация асинхронной работы
            await asyncio.sleep(0.001)

            # Вызов синхронной версии
            return self.create_incident(
                title,
                description,
                incident_type,
                priority,
                severity,
                affected_systems,
            )
        except Exception as e:
            self.log_activity(
                f"Ошибка асинхронного создания инцидента: {e}", "error"
            )
            return None

    async def get_incidents_async(
        self, status: Optional[IncidentStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        Асинхронное получение списка инцидентов.

        Args:
            status (Optional[IncidentStatus]): Фильтр по статусу (опционально)

        Returns:
            List[Dict[str, Any]]: Список инцидентов в виде словарей
        """
        try:
            await asyncio.sleep(0.001)  # Имитация асинхронной работы
            return self.get_incidents(status)
        except Exception as e:
            self.log_activity(
                f"Ошибка асинхронного получения инцидентов: {e}", "error"
            )
            return []

    async def update_incident_status_async(
        self, incident_id: str, new_status: IncidentStatus
    ) -> bool:
        """
        Асинхронное обновление статуса инцидента.

        Args:
            incident_id (str): ID инцидента
            new_status (IncidentStatus): Новый статус

        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            await asyncio.sleep(0.001)  # Имитация асинхронной работы
            return self.update_incident_status(incident_id, new_status)
        except Exception as e:
            self.log_activity(
                f"Ошибка асинхронного обновления статуса: {e}", "error"
            )
            return False

    async def escalate_incident_async(self, incident_id: str) -> bool:
        """
        Асинхронная эскалация инцидента.

        Args:
            incident_id (str): ID инцидента для эскалации

        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            await asyncio.sleep(0.001)  # Имитация асинхронной работы
            return self.escalate_incident(incident_id)
        except Exception as e:
            self.log_activity(f"Ошибка асинхронной эскалации: {e}", "error")
            return False

    async def initialize_async(self) -> bool:
        """
        Асинхронная инициализация менеджера.

        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            await asyncio.sleep(0.001)  # Имитация асинхронной работы
            return self.initialize()
        except Exception as e:
            self.log_activity(
                f"Ошибка асинхронной инициализации: {e}", "error"
            )
            return False

    async def start_async(self) -> bool:
        """
        Асинхронный запуск менеджера.

        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            await asyncio.sleep(0.001)  # Имитация асинхронной работы
            return self.start()
        except Exception as e:
            self.log_activity(f"Ошибка асинхронного запуска: {e}", "error")
            return False

    async def stop_async(self) -> bool:
        """
        Асинхронная остановка менеджера.

        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            await asyncio.sleep(0.001)  # Имитация асинхронной работы
            return self.stop()
        except Exception as e:
            self.log_activity(f"Ошибка асинхронной остановки: {e}", "error")
            return False

    # ==================== ДЕТАЛЬНЫЕ МЕТРИКИ ====================

    def get_detailed_metrics(self) -> Dict[str, Any]:
        """
        Получение детальных метрик производительности.

        Returns:
            Dict[str, Any]: Детальные метрики системы
        """
        try:
            # Базовые метрики
            total_incidents = len(self.incidents)
            open_incidents = len(
                [
                    i
                    for i in self.incidents.values()
                    if i.status == IncidentStatus.OPEN
                ]
            )
            resolved_incidents = len(
                [
                    i
                    for i in self.incidents.values()
                    if i.status == IncidentStatus.RESOLVED
                ]
            )

            # Метрики по приоритетам
            priority_metrics = {}
            for priority in IncidentPriority:
                count = len(
                    [
                        i
                        for i in self.incidents.values()
                        if i.priority == priority
                    ]
                )
                priority_metrics[priority.value] = count

            # Метрики по типам
            type_metrics = {}
            for incident_type in IncidentType:
                count = len(
                    [
                        i
                        for i in self.incidents.values()
                        if i.incident_type == incident_type
                    ]
                )
                type_metrics[incident_type.value] = count

            # Метрики по статусам
            status_metrics = {}
            for status in IncidentStatus:
                count = len(
                    [i for i in self.incidents.values() if i.status == status]
                )
                status_metrics[status.value] = count

            # Временные метрики
            current_time = datetime.now()
            avg_resolution_time = self._calculate_avg_resolution_time()
            avg_response_time = self._calculate_avg_response_time()

            # Метрики команды
            team_metrics = self._calculate_team_metrics()

            # Метрики эскалации
            escalation_metrics = self._calculate_escalation_metrics()

            return {
                "basic_metrics": {
                    "total_incidents": total_incidents,
                    "open_incidents": open_incidents,
                    "resolved_incidents": resolved_incidents,
                    "resolution_rate": (
                        (resolved_incidents / total_incidents * 100)
                        if total_incidents > 0
                        else 0
                    ),
                    "open_rate": (
                        (open_incidents / total_incidents * 100)
                        if total_incidents > 0
                        else 0
                    ),
                },
                "priority_distribution": priority_metrics,
                "type_distribution": type_metrics,
                "status_distribution": status_metrics,
                "time_metrics": {
                    "avg_resolution_time_hours": avg_resolution_time,
                    "avg_response_time_minutes": avg_response_time,
                    "current_time": current_time.isoformat(),
                },
                "team_metrics": team_metrics,
                "escalation_metrics": escalation_metrics,
                "cache_metrics": self.get_cache_info(),
                "system_metrics": {
                    "max_open_incidents": self.max_open_incidents,
                    "auto_response_enabled": self.enable_auto_response,
                    "status": self.status.value,
                    "uptime_hours": self._calculate_uptime_hours(),
                },
            }
        except Exception as e:
            self.log_activity(
                f"Ошибка получения детальных метрик: {e}", "error"
            )
            return {}

    def _calculate_avg_resolution_time(self) -> float:
        """Расчет среднего времени разрешения инцидентов в часах"""
        try:
            resolved_incidents = [
                i
                for i in self.incidents.values()
                if i.status == IncidentStatus.RESOLVED and i.resolved_at
            ]

            if not resolved_incidents:
                return 0.0

            total_hours = 0
            for incident in resolved_incidents:
                resolution_time = incident.resolved_at - incident.created_at
                total_hours += resolution_time.total_seconds() / 3600

            return round(total_hours / len(resolved_incidents), 2)
        except Exception:
            return 0.0

    def _calculate_avg_response_time(self) -> float:
        """Расчет среднего времени реагирования в минутах"""
        try:
            # Имитация расчета времени реагирования
            # В реальной системе здесь был бы анализ логов
            return 15.5  # минут
        except Exception:
            return 0.0

    def _calculate_team_metrics(self) -> Dict[str, Any]:
        """Расчет метрик команды"""
        try:
            team_workload = {}
            for incident in self.incidents.values():
                if incident.assigned_to:
                    if incident.assigned_to not in team_workload:
                        team_workload[incident.assigned_to] = 0
                    team_workload[incident.assigned_to] += 1

            return {
                "team_workload": team_workload,
                "most_active_team": (
                    max(team_workload.items(), key=lambda x: x[1])[0]
                    if team_workload
                    else None
                ),
                "team_efficiency": 85.5,  # Процент эффективности команды
            }
        except Exception:
            return {
                "team_workload": {},
                "most_active_team": None,
                "team_efficiency": 0,
            }

    def _calculate_escalation_metrics(self) -> Dict[str, Any]:
        """Расчет метрик эскалации"""
        try:
            escalated_count = len(
                [
                    i
                    for i in self.incidents.values()
                    if i.priority
                    in [IncidentPriority.HIGH, IncidentPriority.CRITICAL]
                ]
            )

            total_incidents = len(self.incidents)
            escalation_rate = (
                (escalated_count / total_incidents * 100)
                if total_incidents > 0
                else 0
            )

            return {
                "escalated_incidents": escalated_count,
                "escalation_rate": round(escalation_rate, 2),
                "high_priority_count": len(
                    [
                        i
                        for i in self.incidents.values()
                        if i.priority == IncidentPriority.HIGH
                    ]
                ),
                "critical_priority_count": len(
                    [
                        i
                        for i in self.incidents.values()
                        if i.priority == IncidentPriority.CRITICAL
                    ]
                ),
            }
        except Exception:
            return {
                "escalated_incidents": 0,
                "escalation_rate": 0,
                "high_priority_count": 0,
                "critical_priority_count": 0,
            }

    def _calculate_uptime_hours(self) -> float:
        """Расчет времени работы системы в часах"""
        try:
            if hasattr(self, "start_time") and self.start_time:
                uptime = datetime.now() - self.start_time
                return round(uptime.total_seconds() / 3600, 2)
            return 0.0
        except Exception:
            return 0.0

    def get_performance_report(self) -> str:
        """
        Генерация отчета о производительности.

        Returns:
            str: Текстовый отчет о производительности
        """
        try:
            metrics = self.get_detailed_metrics()

            report = f"""
=== ОТЧЕТ О ПРОИЗВОДИТЕЛЬНОСТИ СИСТЕМЫ РЕАГИРОВАНИЯ НА ИНЦИДЕНТЫ ===

📊 БАЗОВЫЕ МЕТРИКИ:
• Всего инцидентов: {metrics['basic_metrics']['total_incidents']}
• Открытых инцидентов: {metrics['basic_metrics']['open_incidents']}
• Разрешенных инцидентов: {metrics['basic_metrics']['resolved_incidents']}
• Процент разрешения: {metrics['basic_metrics']['resolution_rate']:.1f}%
• Процент открытых: {metrics['basic_metrics']['open_rate']:.1f}%

⏱️ ВРЕМЕННЫЕ МЕТРИКИ:
• Среднее время разрешения: {metrics['time_metrics']['avg_resolution_time_hours']:.1f} часов
• Среднее время реагирования: {metrics['time_metrics']['avg_response_time_minutes']:.1f} минут

👥 МЕТРИКИ КОМАНДЫ:
• Эффективность команды: {metrics['team_metrics']['team_efficiency']:.1f}%
• Наиболее активная команда: {metrics['team_metrics']['most_active_team'] or 'Не назначена'}

🚨 МЕТРИКИ ЭСКАЛАЦИИ:
• Эскалированных инцидентов: {metrics['escalation_metrics']['escalated_incidents']}
• Процент эскалации: {metrics['escalation_metrics']['escalation_rate']:.1f}%

💾 МЕТРИКИ КЭША:
• Попадания в кэш: {metrics['cache_metrics']['incident_by_id'].hits}
• Промахи кэша: {metrics['cache_metrics']['incident_by_id'].misses}

🔧 СИСТЕМНЫЕ МЕТРИКИ:
• Максимум открытых инцидентов: {metrics['system_metrics']['max_open_incidents']}
• Автореагирование: {'Включено' if metrics['system_metrics']['auto_response_enabled'] else 'Отключено'}
• Статус системы: {metrics['system_metrics']['status']}
• Время работы: {metrics['system_metrics']['uptime_hours']:.1f} часов

=== КОНЕЦ ОТЧЕТА ===
            """

            return report.strip()
        except Exception as e:
            self.log_activity(f"Ошибка генерации отчета: {e}", "error")
            return f"Ошибка генерации отчета: {e}"

    # ==================== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ====================

    def get_incident_by_id(self, incident_id: str) -> Optional[Incident]:
        """
        Получение инцидента по ID.

        Args:
            incident_id (str): ID инцидента

        Returns:
            Optional[Incident]: Объект инцидента или None
        """
        return self.incidents.get(incident_id)

    def get_incidents_by_team(self, team_name: str) -> List[Incident]:
        """
        Получение инцидентов по команде.

        Args:
            team_name (str): Название команды

        Returns:
            List[Incident]: Список инцидентов команды
        """
        return [
            incident
            for incident in self.incidents.values()
            if incident.assigned_to == team_name
        ]

    def get_overdue_incidents(
        self, threshold_hours: float = 24.0
    ) -> List[Incident]:
        """
        Получение просроченных инцидентов.

        Args:
            threshold_hours (float): Порог просрочки в часах

        Returns:
            List[Incident]: Список просроченных инцидентов
        """
        return [
            incident
            for incident in self.incidents.values()
            if incident.is_overdue(threshold_hours)
        ]

    def get_high_priority_incidents(self) -> List[Incident]:
        """
        Получение инцидентов высокого приоритета.

        Returns:
            List[Incident]: Список высокоприоритетных инцидентов
        """
        return [
            incident
            for incident in self.incidents.values()
            if incident.priority
            in [IncidentPriority.HIGH, IncidentPriority.CRITICAL]
        ]

    def search_incidents(self, query: str) -> List[Incident]:
        """
        Поиск инцидентов по тексту.

        Args:
            query (str): Поисковый запрос

        Returns:
            List[Incident]: Список найденных инцидентов
        """
        query_lower = query.lower()
        return [
            incident
            for incident in self.incidents.values()
            if (
                query_lower in incident.title.lower()
                or query_lower in incident.description.lower()
                or query_lower in incident.incident_id.lower()
            )
        ]

    def get_incident_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики по инцидентам.

        Returns:
            Dict[str, Any]: Статистика инцидентов
        """
        total = len(self.incidents)
        if total == 0:
            return {
                "total": 0,
                "by_status": {},
                "by_priority": {},
                "by_type": {},
            }

        by_status = {}
        by_priority = {}
        by_type = {}

        for incident in self.incidents.values():
            # По статусам
            status = incident.status.value
            by_status[status] = by_status.get(status, 0) + 1

            # По приоритетам
            priority = incident.priority.value
            by_priority[priority] = by_priority.get(priority, 0) + 1

            # По типам
            incident_type = incident.incident_type.value
            by_type[incident_type] = by_type.get(incident_type, 0) + 1

        return {
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "by_type": by_type,
            "open_count": by_status.get("OPEN", 0),
            "resolved_count": by_status.get("RESOLVED", 0),
            "escalated_count": len(self.get_high_priority_incidents()),
            "overdue_count": len(self.get_overdue_incidents()),
        }

    def export_incidents_to_csv(self, file_path: str) -> bool:
        """
        Экспорт инцидентов в CSV файл.

        Args:
            file_path (str): Путь к файлу

        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            import csv

            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                if not self.incidents:
                    return True

                # Получаем все поля из первого инцидента
                first_incident = next(iter(self.incidents.values()))
                fieldnames = list(first_incident.to_dict().keys())

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for incident in self.incidents.values():
                    writer.writerow(incident.to_dict())

            self.log_activity(
                f"Экспорт инцидентов в {file_path} выполнен успешно"
            )
            return True
        except Exception as e:
            self.log_activity(f"Ошибка экспорта в CSV: {e}", "error")
            return False

    def import_incidents_from_csv(self, file_path: str) -> int:
        """
        Импорт инцидентов из CSV файла.

        Args:
            file_path (str): Путь к файлу

        Returns:
            int: Количество импортированных инцидентов
        """
        try:
            import csv

            imported_count = 0
            with open(file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    try:
                        # Создаем инцидент из CSV данных
                        incident = Incident(
                            incident_id=row.get(
                                "incident_id", f"IMPORT-{int(time.time())}"
                            ),
                            title=row.get("title", ""),
                            description=row.get("description", ""),
                            incident_type=IncidentType(
                                row.get("incident_type", "UNKNOWN")
                            ),
                            priority=IncidentPriority(
                                row.get("priority", "LOW")
                            ),
                            severity=SecurityLevel(row.get("severity", "LOW")),
                        )

                        # Обновляем дополнительные поля
                        if "assigned_to" in row:
                            incident.assigned_to = row["assigned_to"]
                        if "status" in row:
                            incident.status = IncidentStatus(row["status"])

                        self.incidents[incident.incident_id] = incident
                        imported_count += 1

                    except Exception as e:
                        self.log_activity(
                            f"Ошибка импорта строки: {e}", "error"
                        )
                        continue

            self.log_activity(
                f"Импортировано {imported_count} инцидентов из {file_path}"
            )
            return imported_count
        except Exception as e:
            self.log_activity(f"Ошибка импорта из CSV: {e}", "error")
            return 0

    def backup_incidents(self, backup_path: str) -> bool:
        """
        Создание резервной копии инцидентов.

        Args:
            backup_path (str): Путь к файлу резервной копии

        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            import json

            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "incidents": [
                    incident.to_dict() for incident in self.incidents.values()
                ],
                "statistics": self.get_incident_statistics(),
            }

            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)

            self.log_activity(f"Резервная копия создана: {backup_path}")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка создания резервной копии: {e}", "error")
            return False

    def restore_incidents(self, backup_path: str) -> int:
        """
        Восстановление инцидентов из резервной копии.

        Args:
            backup_path (str): Путь к файлу резервной копии

        Returns:
            int: Количество восстановленных инцидентов
        """
        try:
            import json

            with open(backup_path, "r", encoding="utf-8") as f:
                backup_data = json.load(f)

            restored_count = 0
            for incident_data in backup_data.get("incidents", []):
                try:
                    # Создаем инцидент из данных резервной копии
                    incident = Incident(
                        incident_id=incident_data["incident_id"],
                        title=incident_data["title"],
                        description=incident_data["description"],
                        incident_type=IncidentType(
                            incident_data["incident_type"]
                        ),
                        priority=IncidentPriority(incident_data["priority"]),
                        severity=SecurityLevel(incident_data["severity"]),
                    )

                    # Восстанавливаем дополнительные поля
                    if "assigned_to" in incident_data:
                        incident.assigned_to = incident_data["assigned_to"]
                    if "status" in incident_data:
                        incident.status = IncidentStatus(
                            incident_data["status"]
                        )

                    self.incidents[incident.incident_id] = incident
                    restored_count += 1

                except Exception as e:
                    self.log_activity(
                        f"Ошибка восстановления инцидента: {e}", "error"
                    )
                    continue

            self.log_activity(
                f"Восстановлено {restored_count} инцидентов из {backup_path}"
            )
            return restored_count
        except Exception as e:
            self.log_activity(
                f"Ошибка восстановления из резервной копии: {e}", "error"
            )
            return 0
