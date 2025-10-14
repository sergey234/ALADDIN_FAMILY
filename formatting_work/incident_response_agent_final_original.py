#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IncidentResponseAgent - Агент реагирования на инциденты ALADDIN
Обеспечивает автоматическое реагирование, координацию и восстановление
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime
from enum import Enum

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from core.base import SecurityBase
except ImportError:
    # Fallback для тестирования
    class SecurityBase:
        def __init__(self, name):
            self.name = name
            self.logs = []

        def log_activity(self, message, level="info"):
            self.logs.append("{}: {}".format(level.upper(), message))
            print("{}: {}".format(level.upper(), message))


class IncidentSeverity(Enum):
    """Уровни серьезности инцидентов"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class IncidentStatus(Enum):
    """Статусы инцидентов"""

    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class IncidentType(Enum):
    """Типы инцидентов"""

    MALWARE = "malware"
    PHISHING = "phishing"
    DDOS = "ddos"
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SYSTEM_COMPROMISE = "system_compromise"
    INSIDER_THREAT = "insider_threat"
    VULNERABILITY_EXPLOIT = "vulnerability_exploit"
    SOCIAL_ENGINEERING = "social_engineering"
    RANSOMWARE = "ransomware"


class ResponseAction(Enum):
    """Действия реагирования"""

    ISOLATE = "isolate"
    QUARANTINE = "quarantine"
    BLOCK = "block"
    MONITOR = "monitor"
    INVESTIGATE = "investigate"
    ESCALATE = "escalate"
    NOTIFY = "notify"
    PATCH = "patch"
    RESTORE = "restore"
    TERMINATE = "terminate"


class Incident:
    """Класс для хранения данных об инциденте"""

    def __init__(
        self, incident_id, title, description, incident_type, severity
    ):
        self.incident_id = incident_id
        self.title = title
        self.description = description
        self.incident_type = incident_type
        self.severity = severity
        self.status = IncidentStatus.NEW
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.assigned_to = None
        self.priority = 0
        self.affected_systems = []
        self.indicators = []
        self.actions_taken = []
        self.evidence = []
        self.timeline = []
        self.resolution = None
        self.lessons_learned = []
        self.tags = []
        self.raw_data = {}

    def __str__(self):
        """Строковое представление инцидента"""
        return (
            f"Incident({self.incident_id}: {self.title} - "
            f"{self.severity.value})"
        )

    def __repr__(self):
        """Представление инцидента для отладки"""
        return (
            f"Incident(id='{self.incident_id}', title='{self.title}', "
            f"type='{self.incident_type.value}', "
            f"severity='{self.severity.value}', status='{self.status.value}')"
        )

    def add_affected_system(self, system_id, system_type, description=""):
        """Добавление затронутой системы"""
        self.affected_systems.append(
            {
                "system_id": system_id,
                "system_type": system_type,
                "description": description,
                "added_at": datetime.now(),
            }
        )

    def add_indicator(self, indicator_type, value, description=""):
        """Добавление индикатора"""
        self.indicators.append(
            {
                "type": indicator_type,
                "value": value,
                "description": description,
                "added_at": datetime.now(),
            }
        )

    def add_action(self, action, description, result=""):
        """Добавление выполненного действия"""
        self.actions_taken.append(
            {
                "action": action,
                "description": description,
                "result": result,
                "timestamp": datetime.now(),
            }
        )

    def add_evidence(self, evidence_type, data, description=""):
        """Добавление доказательств"""
        self.evidence.append(
            {
                "type": evidence_type,
                "data": data,
                "description": description,
                "collected_at": datetime.now(),
            }
        )

    def add_timeline_event(self, event, description=""):
        """Добавление события в временную линию"""
        self.timeline.append(
            {
                "event": event,
                "description": description,
                "timestamp": datetime.now(),
            }
        )

    def update_status(self, new_status, reason=""):
        """Обновление статуса инцидента"""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now()

        # Добавление в временную линию
        self.add_timeline_event(
            "status_change",
            "Статус изменен с {} на {}. Причина: {}".format(
                old_status.value, new_status.value, reason
            ),
        )

    def to_dict(self):
        """Преобразование в словарь"""
        return {
            "incident_id": self.incident_id,
            "title": self.title,
            "description": self.description,
            "incident_type": (
                self.incident_type.value
                if hasattr(self.incident_type, "value")
                else str(self.incident_type)
            ),
            "severity": (
                self.severity.value
                if hasattr(self.severity, "value")
                else str(self.severity)
            ),
            "status": (
                self.status.value
                if hasattr(self.status, "value")
                else str(self.status)
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "assigned_to": self.assigned_to,
            "priority": self.priority,
            "affected_systems": self.affected_systems,
            "indicators": self.indicators,
            "actions_taken": self.actions_taken,
            "evidence": self.evidence,
            "timeline": self.timeline,
            "resolution": self.resolution,
            "lessons_learned": self.lessons_learned,
            "tags": self.tags,
            "raw_data": self.raw_data,
        }


class IncidentResponseMetrics:
    """Метрики агента реагирования на инциденты"""

    def __init__(self):
        # Общие метрики
        self.total_incidents = 0
        self.incidents_by_type = {}
        self.incidents_by_severity = {}
        self.incidents_by_status = {}

        # Метрики времени реагирования
        self.avg_response_time = 0.0  # минуты
        self.avg_resolution_time = 0.0  # часы
        self.avg_escalation_time = 0.0  # минуты
        self.sla_compliance = 0.0  # процент

        # Метрики эффективности
        self.auto_resolved_incidents = 0
        self.manually_resolved_incidents = 0
        self.escalated_incidents = 0
        self.false_positives = 0

        # Метрики действий
        self.total_actions_taken = 0
        self.successful_actions = 0
        self.failed_actions = 0
        self.actions_by_type = {}

        # Метрики качества
        self.incident_accuracy = 0.0
        self.response_effectiveness = 0.0
        self.customer_satisfaction = 0.0
        self.team_performance = 0.0

        # Временные метрики
        self.last_incident_time = None
        self.last_response_time = None
        self.peak_incident_hour = None
        self.incident_trend = 0.0

    def __str__(self):
        """Строковое представление метрик"""
        return (
            f"IncidentResponseMetrics(total_incidents={self.total_incidents}, "
            f"avg_response_time={self.avg_response_time:.1f}min, "
            f"sla_compliance={self.sla_compliance:.1%})"
        )

    def __repr__(self):
        """Представление метрик для отладки"""
        return (
            f"IncidentResponseMetrics(total_incidents={self.total_incidents}, "
            f"auto_resolved={self.auto_resolved_incidents}, "
            f"escalated={self.escalated_incidents})"
        )

    def to_dict(self):
        """Преобразование в словарь"""
        return {
            "total_incidents": self.total_incidents,
            "incidents_by_type": self.incidents_by_type,
            "incidents_by_severity": self.incidents_by_severity,
            "incidents_by_status": self.incidents_by_status,
            "avg_response_time": self.avg_response_time,
            "avg_resolution_time": self.avg_resolution_time,
            "avg_escalation_time": self.avg_escalation_time,
            "sla_compliance": self.sla_compliance,
            "auto_resolved_incidents": self.auto_resolved_incidents,
            "manually_resolved_incidents": self.manually_resolved_incidents,
            "escalated_incidents": self.escalated_incidents,
            "false_positives": self.false_positives,
            "total_actions_taken": self.total_actions_taken,
            "successful_actions": self.successful_actions,
            "failed_actions": self.failed_actions,
            "actions_by_type": self.actions_by_type,
            "incident_accuracy": self.incident_accuracy,
            "response_effectiveness": self.response_effectiveness,
            "customer_satisfaction": self.customer_satisfaction,
            "team_performance": self.team_performance,
            "last_incident_time": (
                self.last_incident_time.isoformat()
                if self.last_incident_time
                else None
            ),
            "last_response_time": (
                self.last_response_time.isoformat()
                if self.last_response_time
                else None
            ),
            "peak_incident_hour": self.peak_incident_hour,
            "incident_trend": self.incident_trend,
        }


class IncidentResponseAgent(SecurityBase):
    """Агент реагирования на инциденты ALADDIN"""

    def __init__(self, name="IncidentResponseAgent"):
        SecurityBase.__init__(self, name)

        # Конфигурация агента
        self.response_timeout = 300  # 5 минут
        self.escalation_timeout = 1800  # 30 минут
        self.auto_resolution_threshold = 0.8
        self.sla_targets = {
            "critical": 15,  # 15 минут
            "high": 60,  # 1 час
            "medium": 240,  # 4 часа
            "low": 1440,  # 24 часа
        }

        # Хранилища данных
        self.incidents = {}  # incident_id -> Incident
        self.response_plans = {}  # incident_type -> response_plan
        self.escalation_rules = {}  # severity -> escalation_rules
        self.metrics = IncidentResponseMetrics()

        # AI модели для анализа
        self.ml_models = {}
        self.incident_classifier = None
        self.severity_predictor = None
        self.response_recommender = None
        self.escalation_predictor = None
        self.impact_analyzer = None

        # Системы уведомлений
        self.notification_channels = {}
        self.escalation_contacts = {}
        self.alert_rules = {}

        # Системы автоматизации
        self.auto_response_rules = {}
        self.workflow_engine = {}
        self.integration_apis = {}

        # Системы мониторинга
        self.incident_monitoring = {}
        self.performance_tracking = {}
        self.quality_metrics = {}

    def __str__(self):
        """Строковое представление агента"""
        return (
            f"IncidentResponseAgent(name='{self.name}', "
            f"incidents={len(self.incidents)}, "
            f"status='initialized')"
        )

    def __repr__(self):
        """Представление агента для отладки"""
        return (
            f"IncidentResponseAgent(name='{self.name}', "
            f"incidents={len(self.incidents)}, "
            f"metrics={self.metrics})"
        )

    def initialize(self):
        """Инициализация агента"""
        try:
            self.log_activity("Инициализация IncidentResponseAgent...")

            # Инициализация AI моделей
            self._initialize_ai_models()

            # Загрузка планов реагирования
            self._load_response_plans()

            # Инициализация правил эскалации
            self._initialize_escalation_rules()

            # Настройка уведомлений
            self._setup_notifications()

            # Запуск фоновых процессов
            self._start_background_processes()

            self.log_activity("IncidentResponseAgent инициализирован успешно")
            return True

        except Exception as e:
            self.log_activity(
                "Ошибка инициализации IncidentResponseAgent: {}".format(
                    str(e)
                ),
                "error",
            )
            return False

    def _initialize_ai_models(self):
        """Инициализация AI моделей"""
        try:
            self.log_activity(
                "Инициализация AI моделей для реагирования на инциденты..."
            )

            # Классификатор инцидентов
            self.incident_classifier = {
                "model_type": "deep_learning_ensemble",
                "features": [
                    "incident_description",
                    "indicators",
                    "affected_systems",
                    "temporal_features",
                    "severity_indicators",
                    "attack_patterns",
                ],
                "accuracy": 0.94,
                "confidence_threshold": 0.85,
                "last_trained": datetime.now(),
            }

            # Предиктор серьезности
            self.severity_predictor = {
                "model_type": "gradient_boosting",
                "features": [
                    "incident_type",
                    "affected_systems_count",
                    "indicators_count",
                    "attack_complexity",
                    "impact_potential",
                    "temporal_factors",
                ],
                "accuracy": 0.91,
                "confidence_threshold": 0.80,
                "last_trained": datetime.now(),
            }

            # Рекомендатель действий
            self.response_recommender = {
                "model_type": "reinforcement_learning",
                "features": [
                    "incident_type",
                    "severity",
                    "affected_systems",
                    "available_resources",
                    "historical_success",
                    "time_constraints",
                ],
                "accuracy": 0.89,
                "confidence_threshold": 0.75,
                "last_trained": datetime.now(),
            }

            # Предиктор эскалации
            self.escalation_predictor = {
                "model_type": "time_series_analysis",
                "features": [
                    "incident_age",
                    "severity",
                    "resolution_progress",
                    "resource_availability",
                    "escalation_history",
                    "sla_status",
                ],
                "accuracy": 0.87,
                "confidence_threshold": 0.70,
                "last_trained": datetime.now(),
            }

            # Анализатор воздействия
            self.impact_analyzer = {
                "model_type": "neural_network",
                "features": [
                    "affected_systems",
                    "data_exposure",
                    "business_impact",
                    "recovery_time",
                    "financial_impact",
                    "reputation_risk",
                ],
                "accuracy": 0.92,
                "confidence_threshold": 0.80,
                "last_trained": datetime.now(),
            }

            self.ml_models = {
                "incident_classifier": self.incident_classifier,
                "severity_predictor": self.severity_predictor,
                "response_recommender": self.response_recommender,
                "escalation_predictor": self.escalation_predictor,
                "impact_analyzer": self.impact_analyzer,
            }

            self.log_activity("AI модели инициализированы успешно")

        except Exception as e:
            self.log_activity(
                "Ошибка инициализации AI моделей: {}".format(str(e)), "error"
            )

    def _load_response_plans(self):
        """Загрузка планов реагирования"""
        try:
            self.log_activity("Загрузка планов реагирования...")

            # План реагирования на вредоносное ПО
            self.response_plans["malware"] = {
                "name": "Malware Response Plan",
                "steps": [
                    {
                        "action": "ISOLATE",
                        "description": "Изолировать зараженные системы",
                    },
                    {
                        "action": "QUARANTINE",
                        "description": (
                            "Поместить в карантин подозрительные файлы"
                        ),
                    },
                    {
                        "action": "INVESTIGATE",
                        "description": "Провести расследование инцидента",
                    },
                    {
                        "action": "PATCH",
                        "description": "Установить исправления безопасности",
                    },
                    {
                        "action": "RESTORE",
                        "description": (
                            "Восстановить системы из резервных копий"
                        ),
                    },
                ],
                "priority": 1,
                "estimated_time": 240,  # 4 часа
            }

            # План реагирования на фишинг
            self.response_plans["phishing"] = {
                "name": "Phishing Response Plan",
                "steps": [
                    {
                        "action": "BLOCK",
                        "description": (
                            "Заблокировать подозрительные URL и email"
                        ),
                    },
                    {
                        "action": "NOTIFY",
                        "description": (
                            "Уведомить пользователей о фишинговой атаке"
                        ),
                    },
                    {
                        "action": "INVESTIGATE",
                        "description": "Провести расследование источника",
                    },
                    {
                        "action": "PATCH",
                        "description": "Обновить системы защиты от фишинга",
                    },
                ],
                "priority": 2,
                "estimated_time": 120,  # 2 часа
            }

            # План реагирования на DDoS
            self.response_plans["ddos"] = {
                "name": "DDoS Response Plan",
                "steps": [
                    {
                        "action": "BLOCK",
                        "description": (
                            "Заблокировать атакующий трафик"
                        ),
                    },
                    {
                        "action": "ESCALATE",
                        "description": (
                            "Эскалировать в команду сетевой безопасности"
                        ),
                    },
                    {
                        "action": "MONITOR",
                        "description": "Мониторить состояние системы",
                    },
                    {
                        "action": "RESTORE",
                        "description": "Восстановить нормальную работу",
                    },
                ],
                "priority": 1,
                "estimated_time": 60,  # 1 час
            }

            # План реагирования на утечку данных
            self.response_plans["data_breach"] = {
                "name": "Data Breach Response Plan",
                "steps": [
                    {
                        "action": "ISOLATE",
                        "description": (
                            "Изолировать затронутые системы"
                        ),
                    },
                    {
                        "action": "INVESTIGATE",
                        "description": (
                            "Провести расследование масштаба утечки"
                        ),
                    },
                    {
                        "action": "NOTIFY",
                        "description": "Уведомить затронутых пользователей",
                    },
                    {
                        "action": "ESCALATE",
                        "description": (
                            "Эскалировать в руководство и регуляторы"
                        ),
                    },
                    {"action": "PATCH", "description": "Устранить уязвимости"},
                ],
                "priority": 1,
                "estimated_time": 480,  # 8 часов
            }

            self.log_activity("Планы реагирования загружены успешно")

        except Exception as e:
            self.log_activity(
                "Ошибка загрузки планов реагирования: {}".format(str(e)),
                "error",
            )

    def _initialize_escalation_rules(self):
        """Инициализация правил эскалации"""
        try:
            self.log_activity("Инициализация правил эскалации...")

            # Правила эскалации по серьезности
            self.escalation_rules["critical"] = {
                "immediate_escalation": True,
                "escalation_time": 15,  # 15 минут
                "escalation_contacts": [
                    "security_team",
                    "management",
                    "legal",
                ],
                "notification_channels": ["email", "sms", "phone"],
            }

            self.escalation_rules["high"] = {
                "immediate_escalation": False,
                "escalation_time": 60,  # 1 час
                "escalation_contacts": ["security_team", "management"],
                "notification_channels": ["email", "sms"],
            }

            self.escalation_rules["medium"] = {
                "immediate_escalation": False,
                "escalation_time": 240,  # 4 часа
                "escalation_contacts": ["security_team"],
                "notification_channels": ["email"],
            }

            self.escalation_rules["low"] = {
                "immediate_escalation": False,
                "escalation_time": 1440,  # 24 часа
                "escalation_contacts": ["security_team"],
                "notification_channels": ["email"],
            }

            self.log_activity("Правила эскалации инициализированы успешно")

        except Exception as e:
            self.log_activity(
                "Ошибка инициализации правил эскалации: {}".format(str(e)),
                "error",
            )

    def _setup_notifications(self):
        """Настройка системы уведомлений"""
        try:
            self.log_activity("Настройка системы уведомлений...")

            # Каналы уведомлений
            self.notification_channels = {
                "email": {
                    "enabled": True,
                    "template": "incident_notification.html",
                    "recipients": ["security@company.com"],
                },
                "sms": {
                    "enabled": True,
                    "template": "incident_sms.txt",
                    "recipients": ["+1234567890"],
                },
                "slack": {
                    "enabled": True,
                    "channel": "#security-incidents",
                    "webhook": "https://hooks.slack.com/services/...",
                },
            }

            # Контакты для эскалации
            self.escalation_contacts = {
                "security_team": {
                    "email": "security@company.com",
                    "phone": "+1234567890",
                    "slack": "@security-team",
                },
                "management": {
                    "email": "management@company.com",
                    "phone": "+1234567891",
                    "slack": "@management",
                },
                "legal": {
                    "email": "legal@company.com",
                    "phone": "+1234567892",
                    "slack": "@legal",
                },
            }

            self.log_activity("Система уведомлений настроена успешно")

        except Exception as e:
            self.log_activity(
                "Ошибка настройки уведомлений: {}".format(str(e)), "error"
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

    def _validate_incident_data(
        self, title, description, incident_type, severity
    ):
        """Валидация данных инцидента"""
        try:
            # Проверка обязательных полей
            if (
                not title
                or not isinstance(title, str)
                or len(title.strip()) == 0
            ):
                self.log_activity("Некорректное название инцидента", "error")
                return False

            if (
                not description
                or not isinstance(description, str)
                or len(description.strip()) == 0
            ):
                self.log_activity("Некорректное описание инцидента", "error")
                return False

            # Проверка типа инцидента
            if not isinstance(incident_type, IncidentType):
                self.log_activity("Некорректный тип инцидента", "error")
                return False

            # Проверка серьезности
            if not isinstance(severity, IncidentSeverity):
                self.log_activity(
                    "Некорректная серьезность инцидента", "error"
                )
                return False

            # Проверка длины полей
            if len(title) > 200:
                self.log_activity(
                    "Название инцидента слишком длинное", "error"
                )
                return False

            if len(description) > 2000:
                self.log_activity(
                    "Описание инцидента слишком длинное", "error"
                )
                return False

            return True

        except Exception as e:
            self.log_activity(
                "Ошибка валидации данных инцидента: {}".format(str(e)), "error"
            )
            return False

    def create_incident(
        self,
        title,
        description,
        incident_type,
        severity,
        affected_systems=None,
    ):
        """Создание нового инцидента"""
        try:
            # Валидация входных данных
            if not self._validate_incident_data(
                title, description, incident_type, severity
            ):
                self.log_activity("Ошибка валидации данных инцидента", "error")
                return None

            self.log_activity("Создание нового инцидента: {}".format(title))

            # Генерация ID инцидента
            incident_id = "INC_{}_{}".format(
                int(time.time()), hashlib.md5(title.encode()).hexdigest()[:8]
            )

            # Создание инцидента
            incident = Incident(
                incident_id, title, description, incident_type, severity
            )

            # Добавление затронутых систем
            if affected_systems:
                for system in affected_systems:
                    incident.add_affected_system(
                        system.get("id", ""),
                        system.get("type", ""),
                        system.get("description", ""),
                    )

            # Классификация инцидента
            classification = self._classify_incident(incident)
            incident.incident_type = classification.get("type", incident_type)

            # Предсказание серьезности
            severity_prediction = self._predict_severity(incident)
            incident.severity = severity_prediction.get("severity", severity)

            # Установка приоритета
            incident.priority = self._calculate_priority(incident)

            # Сохранение инцидента
            self.incidents[incident_id] = incident

            # Обновление метрик
            self._update_metrics(incident, "created")

            # Автоматическое реагирование
            self._auto_respond(incident)

            self.log_activity("Инцидент создан: {}".format(incident_id))
            return incident

        except Exception as e:
            self.log_activity(
                "Ошибка создания инцидента: {}".format(str(e)), "error"
            )
            return None

    def _classify_incident(self, incident):
        """Классификация инцидента"""
        try:
            # Симуляция классификации инцидента
            classification_score = 0.92

            return {
                "type": incident.incident_type,
                "confidence": classification_score,
                "model_used": "incident_classifier",
            }

        except Exception as e:
            self.log_activity(
                "Ошибка классификации инцидента: {}".format(str(e)), "error"
            )
            return {"type": incident.incident_type, "confidence": 0.5}

    def _predict_severity(self, incident):
        """Предсказание серьезности инцидента"""
        try:
            # Симуляция предсказания серьезности
            severity_score = 0.88

            return {
                "severity": incident.severity,
                "confidence": severity_score,
                "model_used": "severity_predictor",
            }

        except Exception as e:
            self.log_activity(
                "Ошибка предсказания серьезности: {}".format(str(e)), "error"
            )
            return {"severity": incident.severity, "confidence": 0.5}

    def _calculate_priority(self, incident):
        """Расчет приоритета инцидента"""
        try:
            priority = 0

            # Базовый приоритет по серьезности
            severity_priority = {
                IncidentSeverity.EMERGENCY: 5,
                IncidentSeverity.CRITICAL: 4,
                IncidentSeverity.HIGH: 3,
                IncidentSeverity.MEDIUM: 2,
                IncidentSeverity.LOW: 1,
            }

            priority += severity_priority.get(incident.severity, 1)

            # Бонус за количество затронутых систем
            priority += min(len(incident.affected_systems), 3)

            # Бонус за количество индикаторов
            priority += min(len(incident.indicators), 2)

            return min(priority, 10)  # Максимум 10

        except Exception as e:
            self.log_activity(
                "Ошибка расчета приоритета: {}".format(str(e)), "error"
            )
            return 1

    def _update_metrics(self, incident, action):
        """Обновление метрик"""
        try:
            if action == "created":
                self.metrics.total_incidents += 1
                self.metrics.last_incident_time = datetime.now()

                # Обновление метрик по типам
                incident_type = (
                    incident.incident_type.value
                    if hasattr(incident.incident_type, "value")
                    else str(incident.incident_type)
                )
                self.metrics.incidents_by_type[incident_type] = (
                    self.metrics.incidents_by_type.get(incident_type, 0) + 1
                )

                # Обновление метрик по серьезности
                severity = (
                    incident.severity.value
                    if hasattr(incident.severity, "value")
                    else str(incident.severity)
                )
                self.metrics.incidents_by_severity[severity] = (
                    self.metrics.incidents_by_severity.get(severity, 0) + 1
                )

                # Обновление метрик по статусу
                status = (
                    incident.status.value
                    if hasattr(incident.status, "value")
                    else str(incident.status)
                )
                self.metrics.incidents_by_status[status] = (
                    self.metrics.incidents_by_status.get(status, 0) + 1
                )

        except Exception as e:
            self.log_activity(
                "Ошибка обновления метрик: {}".format(str(e)), "error"
            )

    def _auto_respond(self, incident):
        """Автоматическое реагирование на инцидент"""
        try:
            self.log_activity(
                "Автоматическое реагирование на инцидент: {}".format(
                    incident.incident_id
                )
            )

            # Получение плана реагирования
            response_plan = self._get_response_plan(incident.incident_type)

            if response_plan:
                # Выполнение автоматических действий
                for step in response_plan["steps"]:
                    if self._can_auto_execute(step["action"]):
                        self._execute_action(
                            incident, step["action"], step["description"]
                        )

            # Проверка необходимости эскалации
            if self._should_escalate(incident):
                self._escalate_incident(incident)

        except Exception as e:
            self.log_activity(
                "Ошибка автоматического реагирования: {}".format(str(e)),
                "error",
            )

    def _get_response_plan(self, incident_type):
        """Получение плана реагирования для типа инцидента"""
        try:
            incident_type_str = (
                incident_type.value
                if hasattr(incident_type, "value")
                else str(incident_type)
            )
            return self.response_plans.get(incident_type_str)
        except Exception as e:
            self.log_activity(
                "Ошибка получения плана реагирования: {}".format(str(e)),
                "error",
            )
            return None

    def _can_auto_execute(self, action):
        """Проверка возможности автоматического выполнения действия"""
        auto_actions = ["BLOCK", "QUARANTINE", "MONITOR", "NOTIFY"]
        return action in auto_actions

    def _execute_action(self, incident, action, description):
        """Выполнение действия"""
        try:
            self.log_activity(
                "Выполнение действия {} для инцидента {}: {}".format(
                    action, incident.incident_id, description
                )
            )

            # Добавление действия в инцидент
            incident.add_action(action, description, "Выполнено автоматически")

            # Обновление метрик
            self.metrics.total_actions_taken += 1
            self.metrics.successful_actions += 1

            # Обновление метрик по типам действий
            self.metrics.actions_by_type[action] = (
                self.metrics.actions_by_type.get(action, 0) + 1
            )

        except Exception as e:
            self.log_activity(
                "Ошибка выполнения действия: {}".format(str(e)), "error"
            )
            self.metrics.failed_actions += 1

    def _should_escalate(self, incident):
        """Проверка необходимости эскалации"""
        try:
            severity = (
                incident.severity.value
                if hasattr(incident.severity, "value")
                else str(incident.severity)
            )
            escalation_rules = self.escalation_rules.get(severity)

            if escalation_rules and escalation_rules.get(
                "immediate_escalation", False
            ):
                return True

            # Проверка времени с момента создания
            time_since_creation = datetime.now() - incident.created_at
            escalation_time = (
                escalation_rules.get("escalation_time", 1440)
                if escalation_rules
                else 1440
            )

            return time_since_creation.total_seconds() / 60 >= escalation_time

        except Exception as e:
            self.log_activity(
                "Ошибка проверки эскалации: {}".format(str(e)), "error"
            )
            return False

    def _escalate_incident(self, incident):
        """Эскалация инцидента"""
        try:
            self.log_activity(
                "Эскалация инцидента: {}".format(incident.incident_id)
            )

            # Обновление статуса
            incident.update_status(
                IncidentStatus.ESCALATED, "Автоматическая эскалация"
            )

            # Отправка уведомлений
            self._send_escalation_notifications(incident)

            # Обновление метрик
            self.metrics.escalated_incidents += 1

        except Exception as e:
            self.log_activity(
                "Ошибка эскалации инцидента: {}".format(str(e)), "error"
            )

    def _send_escalation_notifications(self, incident):
        """Отправка уведомлений об эскалации"""
        try:
            severity = (
                incident.severity.value
                if hasattr(incident.severity, "value")
                else str(incident.severity)
            )
            escalation_rules = self.escalation_rules.get(severity, {})

            # Получение контактов для эскалации
            contacts = escalation_rules.get("escalation_contacts", [])
            channels = escalation_rules.get("notification_channels", ["email"])

            # Отправка уведомлений
            for contact in contacts:
                contact_info = self.escalation_contacts.get(contact, {})
                for channel in channels:
                    if channel in contact_info:
                        self._send_notification(
                            incident, contact_info[channel], channel
                        )

        except Exception as e:
            self.log_activity(
                "Ошибка отправки уведомлений: {}".format(str(e)), "error"
            )

    def _send_notification(self, incident, recipient, channel):
        """Отправка уведомления"""
        try:
            self.log_activity(
                "Отправка уведомления {} на {}: {}".format(
                    channel, recipient, incident.incident_id
                )
            )

            # Симуляция отправки уведомления
            # В реальной реализации здесь будет отправка через
            # соответствующий канал

        except Exception as e:
            self.log_activity(
                "Ошибка отправки уведомления: {}".format(str(e)), "error"
            )

    def resolve_incident(self, incident_id, resolution, lessons_learned=None):
        """Разрешение инцидента"""
        try:
            if incident_id not in self.incidents:
                self.log_activity(
                    "Инцидент не найден: {}".format(incident_id), "error"
                )
                return False

            incident = self.incidents[incident_id]

            # Установка разрешения
            incident.resolution = resolution
            incident.lessons_learned = lessons_learned or []

            # Обновление статуса
            incident.update_status(
                IncidentStatus.RESOLVED, "Инцидент разрешен"
            )

            # Обновление метрик
            self._update_resolution_metrics(incident)

            self.log_activity("Инцидент разрешен: {}".format(incident_id))
            return True

        except Exception as e:
            self.log_activity(
                "Ошибка разрешения инцидента: {}".format(str(e)), "error"
            )
            return False

    def _update_resolution_metrics(self, incident):
        """Обновление метрик разрешения"""
        try:
            # Расчет времени разрешения
            resolution_time = incident.updated_at - incident.created_at
            resolution_hours = resolution_time.total_seconds() / 3600

            # Обновление среднего времени разрешения
            if self.metrics.manually_resolved_incidents > 0:
                total_time = (
                    self.metrics.avg_resolution_time
                    * self.metrics.manually_resolved_incidents
                )
                self.metrics.avg_resolution_time = (
                    total_time + resolution_hours
                ) / (self.metrics.manually_resolved_incidents + 1)
            else:
                self.metrics.avg_resolution_time = resolution_hours

            self.metrics.manually_resolved_incidents += 1

        except Exception as e:
            self.log_activity(
                "Ошибка обновления метрик разрешения: {}".format(str(e)),
                "error",
            )

    def generate_report(self):
        """Генерация отчета о реагировании на инциденты"""
        try:
            self.log_activity(
                "Генерация отчета о реагировании на инциденты..."
            )

            report = {
                "report_id": "incident_response_{}".format(int(time.time())),
                "generated_at": datetime.now().isoformat(),
                "agent_name": self.name,
                "summary": {
                    "total_incidents": len(self.incidents),
                    "incidents_by_type": self.metrics.incidents_by_type,
                    "incidents_by_severity": (
                        self.metrics.incidents_by_severity
                    ),
                    "incidents_by_status": self.metrics.incidents_by_status,
                    "avg_response_time": self.metrics.avg_response_time,
                    "avg_resolution_time": self.metrics.avg_resolution_time,
                    "sla_compliance": self.metrics.sla_compliance,
                },
                "incidents": [
                    incident.to_dict() for incident in self.incidents.values()
                ],
                "metrics": self.metrics.to_dict(),
                "recommendations": self._generate_recommendations(),
            }

            # Сохранение отчета
            report_dir = "data/incident_response_reports"
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)

            report_file = os.path.join(
                report_dir,
                "incident_response_report_{}.json".format(int(time.time())),
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
            if self.metrics.avg_response_time > 60:
                recommendations.append(
                    {
                        "type": "response_time",
                        "priority": "high",
                        "description": (
                            "Высокое время реагирования, рекомендуется "
                            "оптимизировать процессы"
                        ),
                        "action": (
                            "Автоматизировать больше действий и "
                            "улучшить мониторинг"
                        ),
                    }
                )

            if self.metrics.sla_compliance < 0.9:
                recommendations.append(
                    {
                        "type": "sla_compliance",
                        "priority": "high",
                        "description": (
                            "Низкое соблюдение SLA, требуется "
                            "улучшение процессов"
                        ),
                        "action": (
                            "Пересмотреть SLA и улучшить автоматизацию"
                        ),
                    }
                )

            if (
                self.metrics.false_positives
                > self.metrics.total_incidents * 0.1
            ):
                recommendations.append(
                    {
                        "type": "false_positives",
                        "priority": "medium",
                        "description": "Высокий уровень ложных срабатываний",
                        "action": (
                            "Улучшить алгоритмы классификации инцидентов"
                        ),
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
            self.log_activity("Остановка IncidentResponseAgent...")

            # Остановка фоновых процессов
            # В реальной реализации здесь будет остановка потоков

            # Сохранение данных
            self._save_data()

            self.log_activity("IncidentResponseAgent остановлен")

        except Exception as e:
            self.log_activity(
                "Ошибка остановки IncidentResponseAgent: {}".format(str(e)),
                "error",
            )

    def _save_data(self):
        """Сохранение данных агента"""
        try:
            data_dir = "data/incident_response"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)

            # Сохранение инцидентов
            incidents_file = os.path.join(data_dir, "incidents.json")
            with open(incidents_file, "w") as f:
                json.dump(
                    {
                        iid: incident.to_dict()
                        for iid, incident in self.incidents.items()
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


if __name__ == "__main__":
    # Тестирование агента
    agent = IncidentResponseAgent()

    if agent.initialize():
        print("IncidentResponseAgent инициализирован успешно")

        # Создание тестового инцидента
        incident = agent.create_incident(
            title="Test Malware Incident",
            description="Test malware incident for testing",
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.HIGH,
            affected_systems=[
                {
                    "id": "server1",
                    "type": "web_server",
                    "description": "Web server",
                }
            ],
        )

        if incident:
            print("Инцидент создан: {}".format(incident.incident_id))

            # Разрешение инцидента
            success = agent.resolve_incident(
                incident.incident_id,
                "Malware removed, systems patched",
                ["Improve endpoint protection", "Update security policies"],
            )

            if success:
                print("Инцидент разрешен успешно")

        # Генерация отчета
        report = agent.generate_report()
        if report:
            print("Отчет сгенерирован: {}".format(report["report_id"]))

        # Остановка агента
        agent.stop()
    else:
        print("Ошибка инициализации IncidentResponseAgent")

    def create_incident(
        self, title, description, incident_type, severity,
        affected_systems=None
    ):
        """Создание нового инцидента"""
        try:
            # Валидация данных
            if not self._validate_incident_data(
                title, description, incident_type, severity
            ):
                return None

            # Генерация ID инцидента
            incident_id = self._generate_incident_id()

            # Создание объекта инцидента
            incident = Incident(
                incident_id, title, description, incident_type, severity
            )

            # Добавление затронутых систем
            if affected_systems:
                for system in affected_systems:
                    incident.add_affected_system(
                        system.get("system_id", ""),
                        system.get("system_type", ""),
                        system.get("description", "")
                    )

            # Сохранение инцидента
            self.incidents[incident_id] = incident

            # Обновление метрик
            self._update_metrics(incident, "created")

            # Автоматическое реагирование
            self._auto_respond(incident)

            self.log_activity(
                "Создан инцидент: {} - {}".format(incident_id, title), "info"
            )

            return incident

        except Exception as e:
            self.log_activity(
                "Ошибка создания инцидента: {}".format(str(e)), "error"
            )
            return None

    def resolve_incident(self, incident_id, resolution, lessons_learned=None):
        """Разрешение инцидента"""
        try:
            # Поиск инцидента
            if incident_id not in self.incidents:
                self.log_activity(
                    "Инцидент не найден: {}".format(incident_id), "error"
                )
                return False

            incident = self.incidents[incident_id]

            # Обновление статуса
            incident.update_status(IncidentStatus.RESOLVED, resolution)

            # Добавление урока
            if lessons_learned:
                incident.lessons_learned.append({
                    "lesson": lessons_learned,
                    "added_at": datetime.now()
                })

            # Обновление метрик
            self._update_resolution_metrics(incident)

            # Уведомления
            self._send_resolution_notifications(incident)

            self.log_activity(
                "Инцидент разрешен: {} - {}".format(incident_id, resolution),
                "info"
            )

            return True

        except Exception as e:
            self.log_activity(
                "Ошибка разрешения инцидента: {}".format(str(e)), "error"
            )
            return False

    def _generate_incident_id(self):
        """Генерация уникального ID инцидента"""
        timestamp = int(time.time())
        random_part = hashlib.md5(str(timestamp).encode()).hexdigest()[:8]
        return "INC-{}-{}".format(timestamp, random_part)

    def _send_resolution_notifications(self, incident):
        """Отправка уведомлений о разрешении"""
        try:
            # В реальной реализации здесь будет отправка уведомлений
            self.log_activity(
                "Отправлено уведомление о разрешении: {}".format(
                    incident.incident_id
                ),
                "info"
            )
        except Exception as e:
            self.log_activity(
                "Ошибка отправки уведомления: {}".format(str(e)), "error"
            )
