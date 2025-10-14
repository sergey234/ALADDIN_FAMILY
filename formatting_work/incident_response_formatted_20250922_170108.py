# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Incident Response Module
Модуль реагирования на инциденты для системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-01
"""

import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import ComponentStatus, SecurityBase, SecurityLevel


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
        self.lessons_learned = ""

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

    def initialize(self) -> bool:
        """Инициализация менеджера реагирования на инциденты"""
        try:
            self.log_activity(
                f"Инициализация менеджера реагирования на инциденты {self.name}"
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
                f"Менеджер реагирования на инциденты {self.name} успешно инициализирован"
            )
            return True

        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка инициализации менеджера реагирования на инциденты {self.name}: {e}",
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
        Создание нового инцидента

        Args:
            title: Заголовок инцидента
            description: Описание инцидента
            incident_type: Тип инцидента
            priority: Приоритет инцидента
            severity: Серьезность инцидента
            affected_systems: Затронутые системы

        Returns:
            Optional[Incident]: Созданный инцидент
        """
        try:
            # Проверка лимита открытых инцидентов
            if self.open_incidents >= self.max_open_incidents:
                self.log_activity(
                    "Достигнут лимит открытых инцидентов", "warning"
                )
                return None

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
                    f"Инцидент {incident.incident_id} эскалирован к команде {incident.assigned_to}"
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
                    f"Автоматическое реагирование выполнено для инцидента {incident.incident_id}"
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
            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Менеджер реагирования на инциденты {self.name} успешно запущен"
            )
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка запуска менеджера реагирования на инциденты {self.name}: {e}",
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
                f"Менеджер реагирования на инциденты {self.name} успешно остановлен"
            )
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка остановки менеджера реагирования на инциденты {self.name}: {e}",
                "error",
            )
            return False
