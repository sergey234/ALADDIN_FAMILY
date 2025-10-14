# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Compliance Manager Module
Модуль управления соответствием требованиям для системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-01
"""

import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from core.base import ComponentStatus, SecurityBase, SecurityLevel


class ComplianceStandard(Enum):
    """Стандарты соответствия"""

    GDPR = "gdpr"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    SOX = "sox"
    HIPAA = "hipaa"
    FZ152 = "fz152"  # 152-ФЗ
    FZ149 = "fz149"  # 149-ФЗ
    FZ187 = "fz187"  # 187-ФЗ


class ComplianceStatus(Enum):
    """Статусы соответствия"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"
    UNDER_REVIEW = "under_review"


class ComplianceRequirement:
    """Класс для представления требования соответствия"""

    def __init__(
        self,
        requirement_id: str,
        title: str,
        description: str,
        standard: ComplianceStandard,
        category: str,
        priority: SecurityLevel,
    ):
        """
        Инициализация требования соответствия.

        Args:
            requirement_id: Уникальный идентификатор требования
            title: Название требования
            description: Описание требования
            standard: Стандарт соответствия (GDPR, ISO27001, FZ152)
            category: Категория требования
            priority: Приоритет требования (SecurityLevel)
        """
        # Валидация параметров
        if not requirement_id or not isinstance(requirement_id, str):
            raise ValueError("requirement_id должен быть непустой строкой")
        if not title or not isinstance(title, str):
            raise ValueError("title должен быть непустой строкой")
        if not description or not isinstance(description, str):
            raise ValueError("description должен быть непустой строкой")
        if not isinstance(standard, ComplianceStandard):
            raise ValueError(
                "standard должен быть экземпляром ComplianceStandard"
            )
        if not category or not isinstance(category, str):
            raise ValueError("category должен быть непустой строкой")
        if not isinstance(priority, SecurityLevel):
            raise ValueError("priority должен быть экземпляром SecurityLevel")
        self.requirement_id = requirement_id
        self.title = title
        self.description = description
        self.standard = standard
        self.category = category
        self.priority = priority
        self.status = ComplianceStatus.UNDER_REVIEW
        self.created_at = datetime.now()
        self.last_assessment = None
        self.next_assessment = None
        self.assessment_frequency = 30  # дни
        self.controls = []
        self.evidence = []
        self.risks = []
        self.remediation_plan = ""

    def update_status(
        self,
        new_status: ComplianceStatus,
        assessment_date: Optional[datetime] = None,
    ):
        """Обновление статуса соответствия"""
        self.status = new_status
        self.last_assessment = assessment_date or datetime.now()
        self.next_assessment = self.last_assessment + timedelta(
            days=self.assessment_frequency
        )

    def add_control(
        self,
        control_id: str,
        control_name: str,
        control_type: str,
        description: str,
    ):
        """Добавление контрольной меры"""
        control = {
            "control_id": control_id,
            "control_name": control_name,
            "control_type": control_type,
            "description": description,
            "implemented": False,
            "implementation_date": None,
            "effectiveness": 0.0,
        }
        self.controls.append(control)

    def add_evidence(
        self, evidence_type: str, description: str, data: Optional[Any] = None
    ):
        """Добавление доказательства соответствия"""
        evidence = {
            "type": evidence_type,
            "description": description,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(days=365)).isoformat(),
        }
        self.evidence.append(evidence)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "requirement_id": self.requirement_id,
            "title": self.title,
            "description": self.description,
            "standard": self.standard.value,
            "category": self.category,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_assessment": (
                self.last_assessment.isoformat()
                if self.last_assessment
                else None
            ),
            "next_assessment": (
                self.next_assessment.isoformat()
                if self.next_assessment
                else None
            ),
            "assessment_frequency": self.assessment_frequency,
            "controls": self.controls,
            "evidence": self.evidence,
            "risks": self.risks,
            "remediation_plan": self.remediation_plan,
        }

    def __str__(self) -> str:
        """Строковое представление требования"""
        return (
            f"ComplianceRequirement(id={self.requirement_id}, "
            f"title={self.title}, status={self.status.value})"
        )

    def __repr__(self) -> str:
        """Представление для отладки"""
        return (
            f"ComplianceRequirement(requirement_id='{self.requirement_id}', "
            f"title='{self.title}', standard={self.standard}, "
            f"status={self.status})"
        )

    def __eq__(self, other) -> bool:
        """Сравнение требований по ID"""
        if not isinstance(other, ComplianceRequirement):
            return False
        return self.requirement_id == other.requirement_id

    def __hash__(self) -> int:
        """Хеш требования по ID"""
        return hash(self.requirement_id)

    def __len__(self) -> int:
        """Количество элементов в требовании"""
        return len(self.controls) + len(self.evidence) + len(self.risks)


class ComplianceManager(SecurityBase):
    """Менеджер соответствия требованиям для системы ALADDIN"""

    def __init__(
        self,
        name: str = "ComplianceManager",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализация менеджера соответствия требованиям.

        Args:
            name: Название менеджера
            config: Конфигурация менеджера (опционально)
        """
        # Валидация параметров
        if not name or not isinstance(name, str):
            raise ValueError("name должен быть непустой строкой")
        if config is not None and not isinstance(config, dict):
            raise ValueError("config должен быть словарем или None")
        super().__init__(name, config)

        # Конфигурация соответствия
        self.assessment_interval = (
            config.get("assessment_interval", 30) if config else 30
        )  # дни
        self.auto_assessment = (
            config.get("auto_assessment", True) if config else True
        )
        self.alert_threshold = (
            config.get("alert_threshold", 0.8) if config else 0.8
        )
        self.enable_reporting = (
            config.get("enable_reporting", True) if config else True
        )

        # Хранилище требований
        self.requirements = {}
        self.compliance_frameworks = {}
        self.assessment_history = {}
        self.remediation_tasks = {}

        # Статистика
        self.total_requirements = 0
        self.compliant_requirements = 0
        self.non_compliant_requirements = 0
        self.assessments_conducted = 0
        self.remediation_tasks_completed = 0

    def initialize(self) -> bool:
        """Инициализация менеджера соответствия требованиям"""
        try:
            self.log_activity(
                f"Инициализация менеджера соответствия требованиям {self.name}"
            )
            self.status = ComponentStatus.INITIALIZING

            # Загрузка стандартов соответствия
            self._load_compliance_frameworks()

            # Создание базовых требований
            self._create_basic_requirements()

            # Настройка автоматической оценки
            if self.auto_assessment:
                self._setup_auto_assessment()

            # Инициализация отчетности
            if self.enable_reporting:
                self._setup_reporting()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Менеджер соответствия требованиям {self.name} "
                f"успешно инициализирован"
            )
            return True

        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка инициализации менеджера соответствия требованиям "
                f"{self.name}: {e}",
                "error",
            )
            return False

    def _load_compliance_frameworks(self):
        """Загрузка стандартов соответствия"""
        try:
            self.compliance_frameworks = {
            ComplianceStandard.GDPR: {
                "name": "General Data Protection Regulation",
                "description": "Регламент по защите персональных данных ЕС",
                "categories": [
                    "data_protection",
                    "privacy",
                    "consent",
                    "breach_notification",
                ],
                "requirements_count": 99,
            },
            ComplianceStandard.ISO27001: {
                "name": "ISO/IEC 27001 Information Security Management",
                "description": (
                    "Стандарт управления информационной безопасностью"
                ),
                "categories": [
                    "information_security",
                    "risk_management",
                    "access_control",
                    "incident_management",
                ],
                "requirements_count": 114,
            },
            ComplianceStandard.PCI_DSS: {
                "name": "Payment Card Industry Data Security Standard",
                "description": (
                    "Стандарт безопасности данных индустрии платежных карт"
                ),
                "categories": [
                    "payment_security",
                    "card_data_protection",
                    "network_security",
                    "access_control",
                ],
                "requirements_count": 78,
            },
            ComplianceStandard.FZ152: {
                "name": "152-ФЗ О персональных данных",
                "description": (
                    "Федеральный закон о защите персональных данных"
                ),
                "categories": [
                    "personal_data_protection",
                    "consent_management",
                    "data_processing",
                    "breach_notification",
                ],
                "requirements_count": 45,
            },
        }
        
            self.log_activity("Стандарты соответствия загружены")
        except Exception as e:
            self.log_activity(f"Ошибка загрузки стандартов соответствия: {e}", "error")
            raise

    def _create_basic_requirements(self):
        """Создание базовых требований соответствия"""
        try:
            basic_requirements = [
                {
                    "requirement_id": "GDPR_001",
                    "title": "Правовая основа обработки данных",
                    "description": (
                        "Обеспечение правовой основы для обработки "
                        "персональных данных"
                    ),
                    "standard": ComplianceStandard.GDPR,
                    "category": "data_protection",
                    "priority": SecurityLevel.HIGH,
                },
                {
                    "requirement_id": "ISO27001_001",
                    "title": "Политика информационной безопасности",
                    "description": (
                        "Разработка и поддержание политики "
                        "информационной безопасности"
                    ),
                    "standard": ComplianceStandard.ISO27001,
                    "category": "information_security",
                    "priority": SecurityLevel.HIGH,
                },
                {
                    "requirement_id": "PCI_DSS_001",
                    "title": "Защита данных карт",
                    "description": (
                        "Защита данных платежных карт от "
                        "несанкционированного доступа"
                    ),
                    "standard": ComplianceStandard.PCI_DSS,
                    "category": "payment_security",
                    "priority": SecurityLevel.CRITICAL,
                },
                {
                    "requirement_id": "FZ152_001",
                    "title": "Согласие на обработку данных",
                    "description": (
                        "Получение согласия субъекта персональных данных "
                        "на обработку"
                    ),
                    "standard": ComplianceStandard.FZ152,
                    "category": "personal_data_protection",
                    "priority": SecurityLevel.HIGH,
                },
            ]

            for req_data in basic_requirements:
                requirement = ComplianceRequirement(
                    requirement_id=req_data["requirement_id"],
                    title=req_data["title"],
                    description=req_data["description"],
                    standard=req_data["standard"],
                    category=req_data["category"],
                    priority=req_data["priority"],
                )

                self.add_requirement(requirement)

            self.log_activity(
                f"Создано {len(basic_requirements)} базовых требований "
                f"соответствия"
            )
        except Exception as e:
            self.log_activity(f"Ошибка создания базовых требований: {e}", "error")
            raise

    def _setup_auto_assessment(self):
        """Настройка автоматической оценки"""
        try:
            # Здесь будет логика автоматической оценки
            self.log_activity("Автоматическая оценка соответствия настроена")
        except Exception as e:
            self.log_activity(f"Ошибка настройки автоматической оценки: {e}", "error")
            raise

    def _setup_reporting(self):
        """Настройка отчетности"""
        try:
            # Здесь будет логика отчетности
            self.log_activity("Система отчетности настроена")
        except Exception as e:
            self.log_activity(f"Ошибка настройки отчетности: {e}", "error")
            raise

    def add_requirement(self, requirement: ComplianceRequirement) -> bool:
        """
        Добавление требования соответствия

        Args:
            requirement: Требование соответствия

        Returns:
            bool: True если требование добавлено
        """
        try:
            if requirement.requirement_id in self.requirements:
                self.log_activity(
                    f"Требование {requirement.requirement_id} уже существует",
                    "warning",
                )
                return False

            self.requirements[requirement.requirement_id] = requirement
            self.total_requirements += 1

            self.log_activity(
                f"Добавлено требование соответствия: {requirement.title}"
            )
            return True

        except Exception as e:
            self.log_activity(f"Ошибка добавления требования: {e}", "error")
            return False

    def assess_requirement(
        self,
        requirement_id: str,
        assessment_data: Dict[str, Any],
        assessor: str = "system",
    ) -> Tuple[bool, ComplianceStatus, str]:
        """
        Оценка требования соответствия

        Args:
            requirement_id: ID требования
            assessment_data: Данные оценки
            assessor: Кто проводил оценку

        Returns:
            Tuple[bool, ComplianceStatus, str]: (успех, статус, сообщение)
        """
        try:
            if requirement_id not in self.requirements:
                return (
                    False,
                    ComplianceStatus.NOT_APPLICABLE,
                    "Требование не найдено",
                )

            requirement = self.requirements[requirement_id]

            # Анализ данных оценки
            compliance_score = self._calculate_compliance_score(
                requirement, assessment_data
            )

            # Определение статуса соответствия
            if compliance_score >= 0.9:
                status = ComplianceStatus.COMPLIANT
                message = "Полное соответствие"
            elif compliance_score >= 0.7:
                status = ComplianceStatus.PARTIALLY_COMPLIANT
                message = "Частичное соответствие"
            else:
                status = ComplianceStatus.NON_COMPLIANT
                message = "Несоответствие"

            # Обновление статуса
            requirement.update_status(status)

            # Обновление статистики
            self._update_compliance_statistics(requirement, status)

            # Сохранение истории оценки
            self._save_assessment_history(
                requirement_id, assessment_data, assessor, compliance_score
            )

            self.assessments_conducted += 1

            self.log_activity(
                f"Оценка требования {requirement_id}: {status.value} "
                f"({compliance_score:.2f})"
            )
            return True, status, message

        except Exception as e:
            self.log_activity(f"Ошибка оценки требования: {e}", "error")
            return False, ComplianceStatus.UNDER_REVIEW, f"Ошибка оценки: {e}"

    def _calculate_compliance_score(
        self,
        requirement: ComplianceRequirement,
        assessment_data: Dict[str, Any],
    ) -> float:
        """Расчет оценки соответствия"""
        try:
            score = 0.0
            total_weight = 0.0

            # Оценка контрольных мер
            for control in requirement.controls:
                control_id = control["control_id"]
                if control_id in assessment_data:
                    control_score = assessment_data[control_id].get(
                        "score", 0.0
                    )
                    control_weight = assessment_data[control_id].get(
                        "weight", 1.0
                    )

                    score += control_score * control_weight
                    total_weight += control_weight

            # Оценка доказательств
            evidence_score = 0.0
            if requirement.evidence:
                # Максимум 5 доказательств
                evidence_score = min(1.0, len(requirement.evidence) / 5.0)

            # Итоговая оценка
            if total_weight > 0:
                final_score = (score / total_weight * 0.8) + (
                    evidence_score * 0.2
                )
            else:
                final_score = evidence_score

            return min(1.0, max(0.0, final_score))

        except Exception as e:
            self.log_activity(
                f"Ошибка расчета оценки соответствия: {e}", "error"
            )
            return 0.0

    def _update_compliance_statistics(
        self, requirement: ComplianceRequirement, status: ComplianceStatus
    ):
        """Обновление статистики соответствия"""
        try:
            # Обновление счетчиков
            if status == ComplianceStatus.COMPLIANT:
                self.compliant_requirements += 1
            elif status == ComplianceStatus.NON_COMPLIANT:
                self.non_compliant_requirements += 1

            # Проверка порога оповещений
            compliance_rate = self.compliant_requirements / max(
                1, self.total_requirements
            )
            if compliance_rate < self.alert_threshold:
                self.log_activity(
                    f"Низкий уровень соответствия: {compliance_rate:.2f}",
                    "warning",
                )

        except Exception as e:
            self.log_activity(f"Ошибка обновления статистики: {e}", "error")

    def _save_assessment_history(
        self,
        requirement_id: str,
        assessment_data: Dict[str, Any],
        assessor: str,
        score: float,
    ):
        """Сохранение истории оценки"""
        try:
            if requirement_id not in self.assessment_history:
                self.assessment_history[requirement_id] = []

            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "assessor": assessor,
                "score": score,
                "data": assessment_data,
            }

            self.assessment_history[requirement_id].append(history_entry)

            # Ограничиваем размер истории
            if len(self.assessment_history[requirement_id]) > 10:
                self.assessment_history[requirement_id].pop(0)

        except Exception as e:
            self.log_activity(
                f"Ошибка сохранения истории оценки: {e}", "error"
            )

    def get_requirement(self, requirement_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение требования соответствия

        Args:
            requirement_id: ID требования

        Returns:
            Optional[Dict[str, Any]]: Данные требования
        """
        if requirement_id not in self.requirements:
            return None

        return self.requirements[requirement_id].to_dict()

    def get_requirements_by_standard(
        self, standard: ComplianceStandard
    ) -> List[Dict[str, Any]]:
        """
        Получение требований по стандарту

        Args:
            standard: Стандарт соответствия

        Returns:
            List[Dict[str, Any]]: Список требований
        """
        return [
            req.to_dict()
            for req in self.requirements.values()
            if req.standard == standard
        ]

    def get_requirements_by_status(
        self, status: ComplianceStatus
    ) -> List[Dict[str, Any]]:
        """
        Получение требований по статусу

        Args:
            status: Статус соответствия

        Returns:
            List[Dict[str, Any]]: Список требований
        """
        return [
            req.to_dict()
            for req in self.requirements.values()
            if req.status == status
        ]

    def get_requirements_by_category(
        self, category: str
    ) -> List[Dict[str, Any]]:
        """
        Получение требований по категории

        Args:
            category: Категория требований

        Returns:
            List[Dict[str, Any]]: Список требований
        """
        return [
            req.to_dict()
            for req in self.requirements.values()
            if req.category == category
        ]

    def add_control_to_requirement(
        self,
        requirement_id: str,
        control_id: str,
        control_name: str,
        control_type: str,
        description: str,
    ) -> bool:
        """
        Добавление контрольной меры к требованию

        Args:
            requirement_id: ID требования
            control_id: ID контрольной меры
            control_name: Название контрольной меры
            control_type: Тип контрольной меры
            description: Описание контрольной меры

        Returns:
            bool: True если контрольная мера добавлена
        """
        try:
            if requirement_id not in self.requirements:
                return False

            requirement = self.requirements[requirement_id]
            requirement.add_control(
                control_id, control_name, control_type, description
            )

            self.log_activity(
                f"Контрольная мера добавлена к требованию {requirement_id}"
            )
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка добавления контрольной меры: {e}", "error"
            )
            return False

    def add_evidence_to_requirement(
        self,
        requirement_id: str,
        evidence_type: str,
        description: str,
        data: Optional[Any] = None,
    ) -> bool:
        """
        Добавление доказательства к требованию

        Args:
            requirement_id: ID требования
            evidence_type: Тип доказательства
            description: Описание доказательства
            data: Данные доказательства

        Returns:
            bool: True если доказательство добавлено
        """
        try:
            if requirement_id not in self.requirements:
                return False

            requirement = self.requirements[requirement_id]
            requirement.add_evidence(evidence_type, description, data)

            self.log_activity(
                f"Доказательство добавлено к требованию {requirement_id}"
            )
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка добавления доказательства: {e}", "error"
            )
            return False

    def create_remediation_task(
        self,
        requirement_id: str,
        task_description: str,
        priority: SecurityLevel,
        due_date: Optional[datetime] = None,
    ) -> str:
        """
        Создание задачи по устранению несоответствия

        Args:
            requirement_id: ID требования
            task_description: Описание задачи
            priority: Приоритет задачи
            due_date: Срок выполнения

        Returns:
            str: ID созданной задачи
        """
        try:
            task_id = f"REMED-{int(time.time())}"

            task = {
                "task_id": task_id,
                "requirement_id": requirement_id,
                "description": task_description,
                "priority": priority.value,
                "status": "open",
                "created_at": datetime.now().isoformat(),
                "due_date": due_date.isoformat() if due_date else None,
                "assigned_to": None,
                "completed_at": None,
            }

            self.remediation_tasks[task_id] = task

            self.log_activity(f"Создана задача по устранению: {task_id}")
            return task_id

        except Exception as e:
            self.log_activity(
                f"Ошибка создания задачи по устранению: {e}", "error"
            )
            return ""

    def complete_remediation_task(
        self,
        task_id: str,
        completed_by: str,
        completion_notes: Optional[str] = None,
    ) -> bool:
        """
        Завершение задачи по устранению

        Args:
            task_id: ID задачи
            completed_by: Кто завершил задачу
            completion_notes: Заметки о завершении

        Returns:
            bool: True если задача завершена
        """
        try:
            if task_id not in self.remediation_tasks:
                return False

            task = self.remediation_tasks[task_id]
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()
            task["completed_by"] = completed_by
            task["completion_notes"] = completion_notes

            self.remediation_tasks_completed += 1

            self.log_activity(f"Задача по устранению завершена: {task_id}")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка завершения задачи: {e}", "error")
            return False

    def get_compliance_report(
        self, standard: Optional[ComplianceStandard] = None
    ) -> Dict[str, Any]:
        """
        Получение отчета о соответствии

        Args:
            standard: Стандарт соответствия (если None, возвращается "
            "общий отчет)

        Returns:
            Dict[str, Any]: Отчет о соответствии
        """
        try:
            if standard:
                requirements = self.get_requirements_by_standard(standard)
            else:
                requirements = [
                    req.to_dict() for req in self.requirements.values()
                ]

            # Расчет статистики
            total_reqs = len(requirements)
            compliant_reqs = len(
                [
                    req
                    for req in requirements
                    if req["status"] == ComplianceStatus.COMPLIANT.value
                ]
            )
            non_compliant_reqs = len(
                [
                    req
                    for req in requirements
                    if req["status"] == ComplianceStatus.NON_COMPLIANT.value
                ]
            )
            partially_compliant_reqs = len(
                [
                    req
                    for req in requirements
                    if req["status"]
                    == ComplianceStatus.PARTIALLY_COMPLIANT.value
                ]
            )

            compliance_rate = compliant_reqs / max(1, total_reqs)

            report = {
                "standard": standard.value if standard else "all",
                "total_requirements": total_reqs,
                "compliant_requirements": compliant_reqs,
                "non_compliant_requirements": non_compliant_reqs,
                "partially_compliant_requirements": partially_compliant_reqs,
                "compliance_rate": compliance_rate,
                "assessment_date": datetime.now().isoformat(),
                "requirements_by_category": self._get_requirements_by_category(
                    requirements
                ),
                "requirements_by_priority": self._get_requirements_by_priority(
                    requirements
                ),
                "open_remediation_tasks": len(
                    [
                        task
                        for task in self.remediation_tasks.values()
                        if task["status"] == "open"
                    ]
                ),
            }

            return report

        except Exception as e:
            self.log_activity(
                f"Ошибка создания отчета о соответствии: {e}", "error"
            )
            return {}

    def _get_requirements_by_category(
        self, requirements: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Получение количества требований по категориям"""
        category_count = {}
        for req in requirements:
            category = req["category"]
            category_count[category] = category_count.get(category, 0) + 1
        return category_count

    def _get_requirements_by_priority(
        self, requirements: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Получение количества требований по приоритетам"""
        priority_count = {}
        for req in requirements:
            priority = req["priority"]
            priority_count[priority] = priority_count.get(priority, 0) + 1
        return priority_count

    def get_compliance_stats(self) -> Dict[str, Any]:
        """
        Получение статистики соответствия

        Returns:
            Dict[str, Any]: Статистика соответствия
        """
        return {
            "total_requirements": self.total_requirements,
            "compliant_requirements": self.compliant_requirements,
            "non_compliant_requirements": self.non_compliant_requirements,
            "assessments_conducted": self.assessments_conducted,
            "remediation_tasks_completed": self.remediation_tasks_completed,
            "overall_compliance_rate": self.compliant_requirements
            / max(1, self.total_requirements),
            "requirements_by_standard": self._get_requirements_by_standard(),
            "requirements_by_status": self._get_requirements_by_status(),
            "open_remediation_tasks": len(
                [
                    task
                    for task in self.remediation_tasks.values()
                    if task["status"] == "open"
                ]
            ),
        }

    def _get_requirements_by_standard(self) -> Dict[str, int]:
        """Получение количества требований по стандартам"""
        standard_count = {}
        for req in self.requirements.values():
            standard = req.standard.value
            standard_count[standard] = standard_count.get(standard, 0) + 1
        return standard_count

    def _get_requirements_by_status(self) -> Dict[str, int]:
        """Получение количества требований по статусам"""
        status_count = {}
        for req in self.requirements.values():
            status = req.status.value
            status_count[status] = status_count.get(status, 0) + 1
        return status_count

    def start(self) -> bool:
        """Запуск менеджера соответствия требованиям"""
        try:
            self.log_activity(
                f"Запуск менеджера соответствия требованиям {self.name}"
            )
            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Менеджер соответствия требованиям {self.name} "
                f"успешно запущен"
            )
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка запуска менеджера соответствия требованиям "
                f"{self.name}: {e}",
                "error",
            )
            return False

    def stop(self) -> bool:
        """Остановка менеджера соответствия требованиям"""
        try:
            self.log_activity(
                f"Остановка менеджера соответствия требованиям "
                f"{self.name}"
            )

            # Остановка автоматической оценки
            self.auto_assessment = False

            self.status = ComponentStatus.STOPPED
            self.log_activity(
                f"Менеджер соответствия требованиям {self.name} "
                f"успешно остановлен"
            )
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка остановки менеджера соответствия требований "
                f"{self.name}: {e}",
                "error",
            )
            return False

    def __str__(self) -> str:
        """Строковое представление менеджера"""
        return (
            f"ComplianceManager(name={self.name}, "
            f"status={self.status.value}, "
            f"requirements={self.total_requirements})"
        )

    def __repr__(self) -> str:
        """Представление для отладки"""
        return (
            f"ComplianceManager(name='{self.name}', "
            f"status={self.status}, "
            f"total_requirements={self.total_requirements})"
        )

    def __eq__(self, other) -> bool:
        """Сравнение менеджеров по имени"""
        if not isinstance(other, ComplianceManager):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        """Хеш менеджера по имени"""
        return hash(self.name)

    def __len__(self) -> int:
        """Количество требований в менеджере"""
        return len(self.requirements)
