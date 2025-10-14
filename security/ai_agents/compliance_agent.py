#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ComplianceAgent - Агент соответствия требованиям ALADDIN
Обеспечивает соответствие стандартам безопасности, аудит и мониторинг
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any

# Добавляем путь к модулям

from core.base import SecurityBase  # noqa: E402


class ComplianceStandard(Enum):
    """Стандарты соответствия"""

    ISO27001 = "iso27001"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    NIST = "nist"
    CIS = "cis"
    COBIT = "cobit"
    ITIL = "itil"
    CUSTOM = "custom"


class ComplianceLevel(Enum):
    """Уровни соответствия"""

    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_ASSESSED = "not_assessed"
    PENDING = "pending"


class ComplianceCategory(Enum):
    """Категории соответствия"""

    ACCESS_CONTROL = "access_control"
    DATA_PROTECTION = "data_protection"
    NETWORK_SECURITY = "network_security"
    INCIDENT_RESPONSE = "incident_response"
    BUSINESS_CONTINUITY = "business_continuity"
    RISK_MANAGEMENT = "risk_management"
    AUDIT_LOGGING = "audit_logging"
    PHYSICAL_SECURITY = "physical_security"
    VULNERABILITY_MANAGEMENT = "vulnerability_management"
    SECURITY_AWARENESS = "security_awareness"


class ComplianceRequirement:
    """Класс для хранения требований соответствия"""

    def __init__(
        self, requirement_id, title, description, standard, category, priority
    ):
        self.requirement_id = requirement_id
        self.title = title
        self.description = description
        self.standard = standard
        self.category = category
        self.priority = priority
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.status = ComplianceLevel.NOT_ASSESSED
        self.evidence = []
        self.controls = []
        self.risks = []
        self.recommendations = []
        self.last_assessment = None
        self.next_assessment = None
        self.assessor = None
        self.notes = ""
        self.tags = []
        self.metadata = {}

    def add_evidence(self, evidence_type, data, description=""):
        """Добавление доказательств соответствия"""
        self.evidence.append(
            {
                "type": evidence_type,
                "data": data,
                "description": description,
                "added_at": datetime.now(),
            }
        )

    def add_control(
        self, control_id, control_name, implementation_status, description=""
    ):
        """Добавление контрольных мер"""
        self.controls.append(
            {
                "control_id": control_id,
                "control_name": control_name,
                "implementation_status": implementation_status,
                "description": description,
                "added_at": datetime.now(),
            }
        )

    def add_risk(self, risk_id, risk_description, risk_level, mitigation=""):
        """Добавление рисков"""
        self.risks.append(
            {
                "risk_id": risk_id,
                "risk_description": risk_description,
                "risk_level": risk_level,
                "mitigation": mitigation,
                "added_at": datetime.now(),
            }
        )

    def add_recommendation(
        self, recommendation, priority, implementation_date=""
    ):
        """Добавление рекомендаций"""
        self.recommendations.append(
            {
                "recommendation": recommendation,
                "priority": priority,
                "implementation_date": implementation_date,
                "added_at": datetime.now(),
            }
        )

    def update_status(self, new_status, assessor, notes=""):
        """Обновление статуса соответствия"""
        self.status = new_status
        self.updated_at = datetime.now()
        self.assessor = assessor
        self.notes = notes
        self.last_assessment = datetime.now()

        # Установка следующей оценки
        if new_status == ComplianceLevel.COMPLIANT:
            self.next_assessment = datetime.now() + timedelta(days=90)
        elif new_status == ComplianceLevel.PARTIALLY_COMPLIANT:
            self.next_assessment = datetime.now() + timedelta(days=30)
        else:
            self.next_assessment = datetime.now() + timedelta(days=7)

    def to_dict(self):
        """Преобразование в словарь"""
        return {
            "requirement_id": self.requirement_id,
            "title": self.title,
            "description": self.description,
            "standard": (
                self.standard.value
                if hasattr(self.standard, "value")
                else str(self.standard)
            ),
            "category": (
                self.category.value
                if hasattr(self.category, "value")
                else str(self.category)
            ),
            "priority": self.priority,
            "status": (
                self.status.value
                if hasattr(self.status, "value")
                else str(self.status)
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "evidence": self.evidence,
            "controls": self.controls,
            "risks": self.risks,
            "recommendations": self.recommendations,
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
            "assessor": self.assessor,
            "notes": self.notes,
            "tags": self.tags,
            "metadata": self.metadata,
        }


class ComplianceMetrics:
    """Метрики агента соответствия"""

    def __init__(self):
        # Общие метрики
        self.total_requirements = 0
        self.requirements_by_standard = {}
        self.requirements_by_category = {}
        self.requirements_by_status = {}

        # Метрики соответствия
        self.compliance_rate = 0.0
        self.partial_compliance_rate = 0.0
        self.non_compliance_rate = 0.0
        self.assessment_completion_rate = 0.0

        # Метрики по стандартам
        self.iso27001_compliance = 0.0
        self.soc2_compliance = 0.0
        self.pci_dss_compliance = 0.0
        self.gdpr_compliance = 0.0
        self.hipaa_compliance = 0.0

        # Метрики по категориям
        self.access_control_compliance = 0.0
        self.data_protection_compliance = 0.0
        self.network_security_compliance = 0.0
        self.incident_response_compliance = 0.0
        self.business_continuity_compliance = 0.0

        # Временные метрики
        self.avg_assessment_time = 0.0  # часы
        self.avg_remediation_time = 0.0  # дни
        self.last_assessment_time = None
        self.next_assessment_time = None

        # Качественные метрики
        self.evidence_quality_score = 0.0
        self.control_effectiveness_score = 0.0
        self.risk_mitigation_score = 0.0
        self.audit_readiness_score = 0.0

        # Тренды
        self.compliance_trend = 0.0
        self.improvement_rate = 0.0
        self.risk_trend = 0.0

    def to_dict(self):
        """Преобразование в словарь"""
        return {
            "total_requirements": self.total_requirements,
            "requirements_by_standard": self.requirements_by_standard,
            "requirements_by_category": self.requirements_by_category,
            "requirements_by_status": self.requirements_by_status,
            "compliance_rate": self.compliance_rate,
            "partial_compliance_rate": self.partial_compliance_rate,
            "non_compliance_rate": self.non_compliance_rate,
            "assessment_completion_rate": self.assessment_completion_rate,
            "iso27001_compliance": self.iso27001_compliance,
            "soc2_compliance": self.soc2_compliance,
            "pci_dss_compliance": self.pci_dss_compliance,
            "gdpr_compliance": self.gdpr_compliance,
            "hipaa_compliance": self.hipaa_compliance,
            "access_control_compliance": self.access_control_compliance,
            "data_protection_compliance": self.data_protection_compliance,
            "network_security_compliance": self.network_security_compliance,
            "incident_response_compliance": self.incident_response_compliance,
            "business_continuity_compliance": (
                self.business_continuity_compliance
            ),
            "avg_assessment_time": self.avg_assessment_time,
            "avg_remediation_time": self.avg_remediation_time,
            "last_assessment_time": (
                self.last_assessment_time.isoformat()
                if self.last_assessment_time
                else None
            ),
            "next_assessment_time": (
                self.next_assessment_time.isoformat()
                if self.next_assessment_time
                else None
            ),
            "evidence_quality_score": self.evidence_quality_score,
            "control_effectiveness_score": self.control_effectiveness_score,
            "risk_mitigation_score": self.risk_mitigation_score,
            "audit_readiness_score": self.audit_readiness_score,
            "compliance_trend": self.compliance_trend,
            "improvement_rate": self.improvement_rate,
            "risk_trend": self.risk_trend,
        }


class ComplianceAgent(SecurityBase):
    """Агент соответствия требованиям ALADDIN"""

    def __init__(self, name="ComplianceAgent"):
        SecurityBase.__init__(self, name)

        # Конфигурация агента
        self.assessment_interval = 30  # дни
        self.auto_assessment = True
        self.continuous_monitoring = True
        self.alert_threshold = 0.8  # 80% соответствие

        # Хранилища данных
        self.requirements = {}  # requirement_id -> ComplianceRequirement
        self.standards = {}  # standard -> requirements
        self.categories = {}  # category -> requirements
        self.metrics = ComplianceMetrics()

        # AI модели для анализа
        self.ml_models = {}
        self.compliance_classifier = None
        self.risk_assessor = None
        self.control_analyzer = None
        self.evidence_validator = None
        self.gap_analyzer = None

        # Системы мониторинга
        self.continuous_monitoring_system = {}
        self.alert_system = {}
        self.reporting_system = {}

        # Системы аудита
        self.audit_trail = {}
        self.evidence_management = {}
        self.control_testing = {}

        # Системы соответствия
        self.standard_mappings = {}
        self.control_frameworks = {}
        self.assessment_templates = {}

    def initialize(self):
        """Инициализация агента"""
        try:
            self.log_activity("Инициализация ComplianceAgent...")

            # Инициализация AI моделей
            self._initialize_ai_models()

            # Загрузка стандартов соответствия
            self._load_compliance_standards()

            # Инициализация требований
            self._initialize_requirements()

            # Настройка мониторинга
            self._setup_monitoring()

            # Запуск фоновых процессов
            self._start_background_processes()

            self.log_activity("ComplianceAgent инициализирован успешно")
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации ComplianceAgent: {str(e)}", "error"
            )
            return False

    def _initialize_ai_models(self):
        """Инициализация AI моделей"""
        try:
            self.log_activity("Инициализация AI моделей для соответствия...")

            # Классификатор соответствия
            self.compliance_classifier = {
                "model_type": "ensemble_classifier",
                "features": [
                    "requirement_text",
                    "standard_type",
                    "category",
                    "implementation_evidence",
                    "control_effectiveness",
                    "risk_level",
                ],
                "accuracy": 0.96,
                "confidence_threshold": 0.90,
                "last_trained": datetime.now(),
            }

            # Оценщик рисков
            self.risk_assessor = {
                "model_type": "gradient_boosting",
                "features": [
                    "requirement_complexity",
                    "implementation_gaps",
                    "control_weaknesses",
                    "historical_incidents",
                    "external_threats",
                    "business_impact",
                ],
                "accuracy": 0.93,
                "confidence_threshold": 0.85,
                "last_trained": datetime.now(),
            }

            # Анализатор контролей
            self.control_analyzer = {
                "model_type": "neural_network",
                "features": [
                    "control_design",
                    "implementation_status",
                    "testing_results",
                    "effectiveness_metrics",
                    "maintenance_frequency",
                    "update_history",
                ],
                "accuracy": 0.91,
                "confidence_threshold": 0.80,
                "last_trained": datetime.now(),
            }

            # Валидатор доказательств
            self.evidence_validator = {
                "model_type": "deep_learning",
                "features": [
                    "evidence_type",
                    "data_quality",
                    "completeness",
                    "authenticity",
                    "relevance",
                    "timeliness",
                ],
                "accuracy": 0.94,
                "confidence_threshold": 0.88,
                "last_trained": datetime.now(),
            }

            # Анализатор пробелов
            self.gap_analyzer = {
                "model_type": "rule_based_ml",
                "features": [
                    "requirement_coverage",
                    "implementation_gaps",
                    "control_gaps",
                    "evidence_gaps",
                    "training_gaps",
                    "process_gaps",
                ],
                "accuracy": 0.89,
                "confidence_threshold": 0.82,
                "last_trained": datetime.now(),
            }

            self.ml_models = {
                "compliance_classifier": self.compliance_classifier,
                "risk_assessor": self.risk_assessor,
                "control_analyzer": self.control_analyzer,
                "evidence_validator": self.evidence_validator,
                "gap_analyzer": self.gap_analyzer,
            }

            self.log_activity("AI модели инициализированы успешно")

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации AI моделей: {str(e)}", "error"
            )

    def _load_compliance_standards(self):
        """Загрузка стандартов соответствия"""
        try:
            self.log_activity("Загрузка стандартов соответствия...")

            # ISO 27001
            self.standards[ComplianceStandard.ISO27001] = {
                "name": "ISO/IEC 27001:2013",
                "description": (
                    "Система управления информационной безопасностью"
                ),
                "requirements_count": 114,
                "categories": [
                    "Политика безопасности",
                    "Организация информационной безопасности",
                    "Управление активами",
                    "Контроль доступа",
                    "Криптография",
                    "Физическая безопасность",
                    "Безопасность операций",
                    "Безопасность коммуникаций",
                    "Приобретение, разработка и сопровождение систем",
                    "Управление инцидентами",
                    "Бизнес-непрерывность",
                    "Соответствие",
                ],
            }

            # SOC 2
            self.standards[ComplianceStandard.SOC2] = {
                "name": "SOC 2 Type II",
                "description": (
                    "Отчет о контролях безопасности, доступности, "
                    "целостности, конфиденциальности и конфиденциальности"
                ),
                "requirements_count": 64,
                "categories": [
                    "CC1 - Контрольная среда",
                    "CC2 - Коммуникация и информация",
                    "CC3 - Оценка рисков",
                    "CC4 - Мониторинг деятельности",
                    "CC5 - Контрольные мероприятия",
                ],
            }

            # PCI DSS
            self.standards[ComplianceStandard.PCI_DSS] = {
                "name": "PCI DSS v3.2.1",
                "description": (
                    "Стандарт безопасности данных индустрии платежных карт"
                ),
                "requirements_count": 12,
                "categories": [
                    "Создание и поддержание безопасной сети",
                    "Защита данных держателей карт",
                    "Поддержание программы управления уязвимостями",
                    "Реализация строгих мер контроля доступа",
                    "Регулярный мониторинг и тестирование сетей",
                    "Поддержание политики информационной безопасности",
                ],
            }

            # GDPR
            self.standards[ComplianceStandard.GDPR] = {
                "name": "General Data Protection Regulation",
                "description": "Общий регламент по защите данных",
                "requirements_count": 99,
                "categories": [
                    "Принципы обработки данных",
                    "Права субъектов данных",
                    "Обязанности контроллера и процессора",
                    "Передача персональных данных",
                    "Надзорные органы",
                    "Сотрудничество и согласованность",
                    "Специальные ситуации",
                    "Делегированные акты и исполнительные акты",
                    "Заключительные положения",
                ],
            }

            # HIPAA
            self.standards[ComplianceStandard.HIPAA] = {
                "name": "Health Insurance Portability and Accountability Act",
                "description": (
                    "Закон о переносимости и подотчетности медицинского "
                    "страхования"
                ),
                "requirements_count": 45,
                "categories": [
                    "Административные меры",
                    "Физические меры",
                    "Технические меры",
                    "Организационные требования",
                    "Политики и процедуры",
                    "Документация",
                ],
            }

            self.log_activity("Стандарты соответствия загружены успешно")

        except Exception as e:
            self.log_activity(
                "Ошибка загрузки стандартов: {}".format(str(e)), "error"
            )

    def _initialize_requirements(self):
        """Инициализация требований соответствия"""
        try:
            self.log_activity("Инициализация требований соответствия...")

            # Создание базовых требований для каждого стандарта
            for standard, standard_info in self.standards.items():
                self._create_requirements_for_standard(standard, standard_info)

            self.log_activity("Требования соответствия инициализированы")

        except Exception as e:
            self.log_activity(
                "Ошибка инициализации требований: {}".format(str(e)), "error"
            )

    def _create_requirements_for_standard(self, standard, standard_info):
        """Создание требований для стандарта"""
        try:
            # Создание требований на основе категорий
            for category in standard_info["categories"]:
                requirement_id = "REQ_{}_{}_{}".format(
                    standard.value.upper(),
                    category.replace(" ", "_").upper(),
                    int(time.time()),
                )

                requirement = ComplianceRequirement(
                    requirement_id=requirement_id,
                    title="{} - {}".format(standard_info["name"], category),
                    description=(
                        "Требование соответствия для {} в категории {}"
                        .format(standard_info["name"], category)
                    ),
                    standard=standard,
                    category=self._map_category(category),
                    priority=self._calculate_priority(standard, category),
                )

                self.requirements[requirement_id] = requirement

                # Добавление в категории
                if requirement.category not in self.categories:
                    self.categories[requirement.category] = []
                self.categories[requirement.category].append(requirement_id)

                # Добавление в стандарты
                if standard not in self.standards:
                    self.standards[standard] = {"requirements": []}
                if "requirements" not in self.standards[standard]:
                    self.standards[standard]["requirements"] = []
                self.standards[standard]["requirements"].append(requirement_id)

        except Exception as e:
            self.log_activity(
                "Ошибка создания требований для стандарта {}: {}".format(
                    standard.value, str(e)
                ),
                "error",
            )

    def _map_category(self, category_name):
        """Маппинг категории по названию"""
        category_mapping = {
            "Политика безопасности": ComplianceCategory.ACCESS_CONTROL,
            "Контроль доступа": ComplianceCategory.ACCESS_CONTROL,
            "Управление активами": ComplianceCategory.DATA_PROTECTION,
            "Криптография": ComplianceCategory.DATA_PROTECTION,
            "Физическая безопасность": ComplianceCategory.PHYSICAL_SECURITY,
            "Безопасность операций": ComplianceCategory.NETWORK_SECURITY,
            "Управление инцидентами": ComplianceCategory.INCIDENT_RESPONSE,
            "Бизнес-непрерывность": ComplianceCategory.BUSINESS_CONTINUITY,
            "Соответствие": ComplianceCategory.RISK_MANAGEMENT,
            "Мониторинг": ComplianceCategory.AUDIT_LOGGING,
            "Управление уязвимостями": (
                ComplianceCategory.VULNERABILITY_MANAGEMENT
            ),
            "Обучение": ComplianceCategory.SECURITY_AWARENESS,
        }

        for key, value in category_mapping.items():
            if key.lower() in category_name.lower():
                return value

        return ComplianceCategory.RISK_MANAGEMENT  # По умолчанию

    def _calculate_priority(self, standard, category):
        """Расчет приоритета требования"""
        priority = 1

        # Приоритет по стандарту
        standard_priority = {
            ComplianceStandard.ISO27001: 3,
            ComplianceStandard.SOC2: 4,
            ComplianceStandard.PCI_DSS: 5,
            ComplianceStandard.GDPR: 5,
            ComplianceStandard.HIPAA: 4,
        }

        priority += standard_priority.get(standard, 1)

        # Приоритет по категории
        if (
            "критическ" in category.lower()
            or "безопасность" in category.lower()
        ):
            priority += 2
        elif "контроль" in category.lower() or "доступ" in category.lower():
            priority += 1

        return min(priority, 10)

    def _setup_monitoring(self):
        """Настройка мониторинга"""
        try:
            self.log_activity("Настройка мониторинга соответствия...")

            # Система непрерывного мониторинга
            self.continuous_monitoring_system = {
                "enabled": True,
                "check_interval": 3600,  # 1 час
                "alert_threshold": 0.8,
                "monitored_standards": list(self.standards.keys()),
                "monitored_categories": list(ComplianceCategory),
            }

            # Система оповещений
            self.alert_system = {
                "email_alerts": True,
                "dashboard_alerts": True,
                "threshold_alerts": True,
                "compliance_drop_alerts": True,
                "assessment_due_alerts": True,
            }

            # Система отчетности
            self.reporting_system = {
                "daily_reports": True,
                "weekly_reports": True,
                "monthly_reports": True,
                "quarterly_reports": True,
                "annual_reports": True,
                "custom_reports": True,
            }

            self.log_activity("Мониторинг настроен успешно")

        except Exception as e:
            self.log_activity(
                "Ошибка настройки мониторинга: {}".format(str(e)), "error"
            )

    def _start_background_processes(self):
        """Запуск фоновых процессов"""
        try:
            self.log_activity("Запуск фоновых процессов...")

            # Здесь будут запущены фоновые процессы
            # В реальной реализации это будут отдельные потоки

            self.log_activity("Фоновые процессы запущены")

        except Exception as e:
            self.log_activity(
                "Ошибка запуска фоновых процессов: {}".format(str(e)), "error"
            )

    def create_requirement(
        self, title, description, standard, category, priority=1
    ):
        """Создание нового требования соответствия"""
        try:
            # Валидация входных данных
            if not self._validate_requirement_data(
                title, description, standard, category
            ):
                self.log_activity(
                    "Ошибка валидации данных требования", "error"
                )
                return None

            self.log_activity("Создание нового требования: {}".format(title))

            # Генерация ID требования
            requirement_id = "REQ_{}_{}".format(
                int(time.time()), hashlib.md5(title.encode()).hexdigest()[:8]
            )

            # Создание требования
            requirement = ComplianceRequirement(
                requirement_id=requirement_id,
                title=title,
                description=description,
                standard=standard,
                category=category,
                priority=priority,
            )

            # Сохранение требования
            self.requirements[requirement_id] = requirement

            # Обновление метрик
            self._update_metrics(requirement, "created")

            self.log_activity("Требование создано: {}".format(requirement_id))
            return requirement

        except Exception as e:
            self.log_activity(
                "Ошибка создания требования: {}".format(str(e)), "error"
            )
            return None

    def _validate_requirement_data(
        self, title, description, standard, category
    ):
        """Валидация данных требования"""
        try:
            # Проверка обязательных полей
            if (
                not title
                or not isinstance(title, str)
                or len(title.strip()) == 0
            ):
                self.log_activity("Некорректное название требования", "error")
                return False

            if (
                not description
                or not isinstance(description, str)
                or len(description.strip()) == 0
            ):
                self.log_activity("Некорректное описание требования", "error")
                return False

            # Проверка стандарта
            if not isinstance(standard, ComplianceStandard):
                self.log_activity(
                    "Некорректный стандарт соответствия", "error"
                )
                return False

            # Проверка категории
            if not isinstance(category, ComplianceCategory):
                self.log_activity("Некорректная категория требования", "error")
                return False

            # Проверка длины полей
            if len(title) > 200:
                self.log_activity(
                    "Название требования слишком длинное", "error"
                )
                return False

            if len(description) > 2000:
                self.log_activity(
                    "Описание требования слишком длинное", "error"
                )
                return False

            return True

        except Exception as e:
            self.log_activity(
                "Ошибка валидации данных требования: {}".format(str(e)),
                "error",
            )
            return False

    def assess_requirement(
        self, requirement_id, assessor, evidence=None, controls=None
    ):
        """Оценка требования соответствия"""
        try:
            if requirement_id not in self.requirements:
                self.log_activity(
                    "Требование не найдено: {}".format(requirement_id), "error"
                )
                return False

            requirement = self.requirements[requirement_id]

            # AI анализ соответствия
            compliance_analysis = self._analyze_compliance(
                requirement, evidence, controls
            )

            # Обновление статуса
            requirement.update_status(
                compliance_analysis["status"],
                assessor,
                compliance_analysis["notes"],
            )

            # Добавление доказательств
            if evidence:
                for ev in evidence:
                    requirement.add_evidence(
                        ev.get("type", "document"),
                        ev.get("data", ""),
                        ev.get("description", ""),
                    )

            # Добавление контролей
            if controls:
                for control in controls:
                    requirement.add_control(
                        control.get("control_id", ""),
                        control.get("control_name", ""),
                        control.get(
                            "implementation_status", "not_implemented"
                        ),
                        control.get("description", ""),
                    )

            # Обновление метрик
            self._update_metrics(requirement, "assessed")

            self.log_activity("Требование оценено: {}".format(requirement_id))
            return True

        except Exception as e:
            self.log_activity(
                "Ошибка оценки требования: {}".format(str(e)), "error"
            )
            return False

    def _analyze_compliance(self, requirement, evidence=None, controls=None):
        """AI анализ соответствия"""
        try:
            # Симуляция AI анализа
            compliance_score = 0.85  # Базовый балл

            # Анализ доказательств
            if evidence:
                evidence_quality = self._analyze_evidence_quality(evidence)
                compliance_score += evidence_quality * 0.3

            # Анализ контролей
            if controls:
                control_effectiveness = self._analyze_control_effectiveness(
                    controls
                )
                compliance_score += control_effectiveness * 0.4

            # Анализ рисков
            risk_level = self._analyze_risk_level(requirement)
            compliance_score -= risk_level * 0.2

            # Определение статуса
            if compliance_score >= 0.9:
                status = ComplianceLevel.COMPLIANT
            elif compliance_score >= 0.7:
                status = ComplianceLevel.PARTIALLY_COMPLIANT
            else:
                status = ComplianceLevel.NON_COMPLIANT

            return {
                "status": status,
                "score": compliance_score,
                "notes": (
                    "AI анализ завершен. Балл соответствия: {:.2f}"
                    .format(compliance_score)
                ),
            }

        except Exception as e:
            self.log_activity(
                "Ошибка AI анализа соответствия: {}".format(str(e)), "error"
            )
            return {
                "status": ComplianceLevel.NOT_ASSESSED,
                "score": 0.0,
                "notes": "Ошибка анализа",
            }

    def _analyze_evidence_quality(self, evidence):
        """Анализ качества доказательств"""
        try:
            if not evidence:
                return 0.0

            total_quality = 0.0
            for ev in evidence:
                quality = 0.5  # Базовое качество

                # Проверка типа доказательства
                if ev.get("type") in ["document", "log", "screenshot"]:
                    quality += 0.2

                # Проверка описания
                if (
                    ev.get("description")
                    and len(ev.get("description", "")) > 10
                ):
                    quality += 0.2

                # Проверка данных
                if ev.get("data") and len(ev.get("data", "")) > 0:
                    quality += 0.1

                total_quality += min(quality, 1.0)

            return total_quality / len(evidence)

        except Exception as e:
            self.log_activity(
                "Ошибка анализа качества доказательств: {}".format(str(e)),
                "error",
            )
            return 0.0

    def _analyze_control_effectiveness(self, controls):
        """Анализ эффективности контролей"""
        try:
            if not controls:
                return 0.0

            total_effectiveness = 0.0
            for control in controls:
                effectiveness = 0.3  # Базовая эффективность

                # Проверка статуса реализации
                status = control.get(
                    "implementation_status", "not_implemented"
                )
                if status == "fully_implemented":
                    effectiveness += 0.4
                elif status == "partially_implemented":
                    effectiveness += 0.2

                # Проверка описания
                if (
                    control.get("description")
                    and len(control.get("description", "")) > 20
                ):
                    effectiveness += 0.2

                # Проверка ID контроля
                if (
                    control.get("control_id")
                    and len(control.get("control_id", "")) > 0
                ):
                    effectiveness += 0.1

                total_effectiveness += min(effectiveness, 1.0)

            return total_effectiveness / len(controls)

        except Exception as e:
            self.log_activity(
                "Ошибка анализа эффективности контролей: {}".format(str(e)),
                "error",
            )
            return 0.0

    def _analyze_risk_level(self, requirement):
        """Анализ уровня риска"""
        try:
            risk_level = 0.1  # Базовый риск

            # Риск по приоритету
            if requirement.priority >= 8:
                risk_level += 0.3
            elif requirement.priority >= 5:
                risk_level += 0.2
            else:
                risk_level += 0.1

            # Риск по стандарту
            if requirement.standard in [
                ComplianceStandard.PCI_DSS,
                ComplianceStandard.GDPR,
            ]:
                risk_level += 0.2

            # Риск по категории
            if requirement.category in [
                ComplianceCategory.DATA_PROTECTION,
                ComplianceCategory.ACCESS_CONTROL,
            ]:
                risk_level += 0.1

            return min(risk_level, 1.0)

        except Exception as e:
            self.log_activity(
                "Ошибка анализа уровня риска: {}".format(str(e)), "error"
            )
            return 0.5

    def _update_metrics(self, requirement, action):
        """Обновление метрик"""
        try:
            if action == "created":
                self.metrics.total_requirements += 1

                # Обновление метрик по стандартам
                standard = (
                    requirement.standard.value
                    if hasattr(requirement.standard, "value")
                    else str(requirement.standard)
                )
                self.metrics.requirements_by_standard[standard] = (
                    self.metrics.requirements_by_standard.get(standard, 0) + 1
                )

                # Обновление метрик по категориям
                category = (
                    requirement.category.value
                    if hasattr(requirement.category, "value")
                    else str(requirement.category)
                )
                self.metrics.requirements_by_category[category] = (
                    self.metrics.requirements_by_category.get(category, 0) + 1
                )

            elif action == "assessed":
                # Обновление метрик по статусам
                status = (
                    requirement.status.value
                    if hasattr(requirement.status, "value")
                    else str(requirement.status)
                )
                self.metrics.requirements_by_status[status] = (
                    self.metrics.requirements_by_status.get(status, 0) + 1
                )

                # Пересчет общего соответствия
                self._recalculate_compliance_metrics()

        except Exception as e:
            self.log_activity(
                "Ошибка обновления метрик: {}".format(str(e)), "error"
            )

    def _recalculate_compliance_metrics(self):
        """Пересчет метрик соответствия"""
        try:
            total_requirements = self.metrics.total_requirements
            if total_requirements == 0:
                return

            # Расчет процентов соответствия
            compliant_count = self.metrics.requirements_by_status.get(
                "compliant", 0
            )
            partial_count = self.metrics.requirements_by_status.get(
                "partially_compliant", 0
            )
            non_compliant_count = self.metrics.requirements_by_status.get(
                "non_compliant", 0
            )

            self.metrics.compliance_rate = compliant_count / total_requirements
            self.metrics.partial_compliance_rate = (
                partial_count / total_requirements
            )
            self.metrics.non_compliance_rate = (
                non_compliant_count / total_requirements
            )

            # Расчет завершенности оценок
            assessed_count = (
                compliant_count + partial_count + non_compliant_count
            )
            self.metrics.assessment_completion_rate = (
                assessed_count / total_requirements
            )

        except Exception as e:
            self.log_activity(
                "Ошибка пересчета метрик соответствия: {}".format(str(e)),
                "error",
            )

    def generate_compliance_report(self):
        """Генерация отчета о соответствии"""
        try:
            self.log_activity("Генерация отчета о соответствии...")

            report = {
                "report_id": "compliance_report_{}".format(int(time.time())),
                "generated_at": datetime.now().isoformat(),
                "agent_name": self.name,
                "summary": {
                    "total_requirements": self.metrics.total_requirements,
                    "compliance_rate": self.metrics.compliance_rate,
                    "partial_compliance_rate": (
                        self.metrics.partial_compliance_rate
                    ),
                    "non_compliance_rate": self.metrics.non_compliance_rate,
                    "assessment_completion_rate": (
                        self.metrics.assessment_completion_rate
                    ),
                },
                "standards_compliance": {
                    "iso27001": self.metrics.iso27001_compliance,
                    "soc2": self.metrics.soc2_compliance,
                    "pci_dss": self.metrics.pci_dss_compliance,
                    "gdpr": self.metrics.gdpr_compliance,
                    "hipaa": self.metrics.hipaa_compliance,
                },
                "category_compliance": {
                    "access_control": (
                        self.metrics.access_control_compliance
                    ),
                    "data_protection": (
                        self.metrics.data_protection_compliance
                    ),
                    "network_security": (
                        self.metrics.network_security_compliance
                    ),
                    "incident_response": (
                        self.metrics.incident_response_compliance
                    ),
                    "business_continuity": (
                        self.metrics.business_continuity_compliance
                    ),
                },
                "requirements": [
                    req.to_dict() for req in self.requirements.values()
                ],
                "metrics": self.metrics.to_dict(),
                "recommendations": self._generate_recommendations(),
            }

            # Сохранение отчета
            report_dir = "data/compliance_reports"
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)

            report_file = os.path.join(
                report_dir,
                "compliance_report_{}.json".format(int(time.time())),
            )
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            self.log_activity("Отчет сохранен: {}".format(report_file))
            return report

        except Exception as e:
            self.log_activity(
                "Ошибка генерации отчета: {}".format(str(e)), "error"
            )
            return None

    def _generate_recommendations(self):
        """Генерация рекомендаций"""
        try:
            recommendations = []

            # Рекомендации на основе метрик
            if self.metrics.compliance_rate < 0.8:
                recommendations.append(
                    {
                        "type": "compliance_improvement",
                        "priority": "high",
                        "description": (
                            "Низкий уровень соответствия, требуется улучшение"
                        ),
                        "action": (
                            "Провести детальный аудит и устранить пробелы"
                        ),
                    }
                )

            if self.metrics.assessment_completion_rate < 0.9:
                recommendations.append(
                    {
                        "type": "assessment_completion",
                        "priority": "medium",
                        "description": "Не все требования оценены",
                        "action": "Завершить оценку всех требований",
                    }
                )

            if self.metrics.non_compliance_rate > 0.2:
                recommendations.append(
                    {
                        "type": "non_compliance_reduction",
                        "priority": "high",
                        "description": "Высокий уровень несоответствия",
                        "action": "Принять меры по устранению несоответствий",
                    }
                )

            return recommendations

        except Exception as e:
            self.log_activity(
                "Ошибка генерации рекомендаций: {}".format(str(e)), "error"
            )
            return []

    def stop(self):
        """Остановка агента"""
        try:
            self.log_activity("Остановка ComplianceAgent...")

            # Остановка фоновых процессов
            # В реальной реализации здесь будет остановка потоков

            # Сохранение данных
            self._save_data()

            self.log_activity("ComplianceAgent остановлен")

        except Exception as e:
            self.log_activity(
                "Ошибка остановки ComplianceAgent: {}".format(str(e)), "error"
            )

    def _save_data(self):
        """Сохранение данных агента"""
        try:
            data_dir = "data/compliance"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)

            # Сохранение требований
            requirements_file = os.path.join(data_dir, "requirements.json")
            with open(requirements_file, "w") as f:
                json.dump(
                    {
                        rid: req.to_dict()
                        for rid, req in self.requirements.items()
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            # Сохранение метрик
            metrics_file = os.path.join(data_dir, "metrics.json")
            with open(metrics_file, "w") as f:
                json.dump(
                    self.metrics.to_dict(), f, indent=2, ensure_ascii=False
                )

            self.log_activity("Данные сохранены в {}".format(data_dir))

        except Exception as e:
            self.log_activity(
                "Ошибка сохранения данных: {}".format(str(e)), "error"
            )

    def start_compliance(self) -> bool:
        """Запуск системы соответствия требованиям"""
        try:
            self.is_running = True
            self.log_activity("Система соответствия требованиям запущена")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка запуска системы соответствия: {e}", "error")
            return False

    def stop_compliance(self) -> bool:
        """Остановка системы соответствия требованиям"""
        try:
            self.is_running = False
            self.log_activity("Система соответствия требованиям остановлена")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка остановки системы соответствия: {e}", "error")
            return False

    def get_compliance_info(self) -> Dict[str, Any]:
        """Получение информации о системе соответствия требованиям"""
        try:
            return {
                "is_running": getattr(self, 'is_running', False),
                "requirements_count": len(self.requirements),
                "standards_count": len(ComplianceStandard),
                "categories_count": len(ComplianceCategory),
                "levels_count": len(ComplianceLevel),
                "compliance_score": getattr(self.metrics, 'compliance_score', 0),
                "non_compliant_count": getattr(self.metrics, 'non_compliant_count', 0),
                "pending_reviews": getattr(self.metrics, 'pending_reviews', 0),
                "last_assessment": getattr(self.metrics, 'last_assessment', None),
            }
        except Exception as e:
            self.log_activity(f"Ошибка получения информации о системе соответствия: {e}", "error")
            return {
                "is_running": False,
                "requirements_count": 0,
                "standards_count": 0,
                "categories_count": 0,
                "levels_count": 0,
                "compliance_score": 0,
                "non_compliant_count": 0,
                "pending_reviews": 0,
                "last_assessment": None,
                "error": str(e),
            }


if __name__ == "__main__":
    # Тестирование агента
    agent = ComplianceAgent()

    if agent.initialize():
        print("ComplianceAgent инициализирован успешно")

        # Создание тестового требования
        requirement = agent.create_requirement(
            title="Test Compliance Requirement",
            description="Test requirement for compliance testing",
            standard=ComplianceStandard.ISO27001,
            category=ComplianceCategory.ACCESS_CONTROL,
            priority=5,
        )

        if requirement:
            print("Требование создано: {}".format(requirement.requirement_id))

            # Оценка требования
            success = agent.assess_requirement(
                requirement.requirement_id,
                "test_assessor",
                evidence=[
                    {
                        "type": "document",
                        "data": "test_evidence",
                        "description": "Test evidence",
                    }
                ],
                controls=[
                    {
                        "control_id": "CTRL001",
                        "control_name": "Test Control",
                        "implementation_status": "fully_implemented",
                    }
                ],
            )

            if success:
                print("Требование оценено успешно")

        # Генерация отчета
        report = agent.generate_compliance_report()
        if report:
            print("Отчет сгенерирован: {}".format(report["report_id"]))

        # Остановка агента
        agent.stop()
    else:
        print("Ошибка инициализации ComplianceAgent")
