# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Security Analytics Module
Модуль аналитики безопасности для системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-01
"""

import asyncio
import functools
import json
import logging
import math
import time
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional

from core.base import ComponentStatus, SecurityBase


# ============================================================================
# ВАЛИДАЦИЯ ПАРАМЕТРОВ И УЛУЧШЕННАЯ ОБРАБОТКА ОШИБОК
# ============================================================================


class ValidationError(Exception):
    """Исключение для ошибок валидации"""

    pass


class SecurityAnalyticsError(Exception):
    """Базовое исключение для ошибок аналитики безопасности"""

    pass


class MetricNotFoundError(SecurityAnalyticsError):
    """Исключение когда метрика не найдена"""

    pass


class InvalidMetricValueError(SecurityAnalyticsError):
    """Исключение для недопустимых значений метрик"""

    pass


class ConfigurationError(SecurityAnalyticsError):
    """Исключение для ошибок конфигурации"""

    pass


def validate_metric_id(metric_id: str) -> None:
    """Валидация ID метрики"""
    if not isinstance(metric_id, str):
        raise ValidationError("metric_id должен быть строкой")
    if not metric_id.strip():
        raise ValidationError("metric_id не может быть пустым")
    if len(metric_id) > 100:
        raise ValidationError("metric_id не может быть длиннее 100 символов")
    if not metric_id.replace("_", "").replace("-", "").isalnum():
        raise ValidationError(
            "metric_id может содержать только буквы, цифры, _ и -"
        )


def validate_metric_value(value: Any, metric_type: "MetricType") -> None:
    """Валидация значения метрики"""
    if not isinstance(value, (int, float)):
        raise ValidationError("value должен быть числом")

    if not math.isfinite(value):
        raise ValidationError("value должен быть конечным числом")

    if metric_type in [MetricType.COUNTER, MetricType.GAUGE]:
        if value < 0:
            raise ValidationError(
                f"value не может быть отрицательным. "
                f"Некорректное значение для типа {metric_type.value}"
            )


def validate_threshold_value(value: float) -> None:
    """Валидация порогового значения"""
    if not isinstance(value, (int, float)):
        raise ValidationError("threshold value должен быть числом")
    if not math.isfinite(value):
        raise ValidationError("threshold value должен быть конечным числом")


def validate_config_dict(config: Any) -> None:
    """Валидация словаря конфигурации"""
    if not isinstance(config, dict):
        raise ValidationError("config должен быть словарем")

    allowed_keys = {
        "data_retention_days",
        "analysis_interval",
        "enable_real_time",
        "alert_threshold",
        "encryption_enabled",
        "max_metrics",
        "cleanup_interval",
        "performance_monitoring",
    }

    for key in config.keys():
        if key not in allowed_keys:
            raise ValidationError(f"Недопустимый ключ конфигурации: {key}")


def enhanced_error_handler(func):
    """Декоратор для улучшенной обработки ошибок"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            if hasattr(args[0], "log_activity"):
                args[0].log_activity(
                    f"Ошибка валидации в {func.__name__}: {e}", "error"
                )
            raise
        except SecurityAnalyticsError as e:
            if hasattr(args[0], "log_activity"):
                args[0].log_activity(
                    f"Ошибка валидации в {func.__name__}: {e}",
                    "error",
                )
            raise
        except Exception as e:
            if hasattr(args[0], "log_activity"):
                args[0].log_activity(
                    f"Ошибка в {func.__name__}: {type(e).__name__}: {e}",
                    "error",
                )
            raise SecurityAnalyticsError(
                f"Неожиданная ошибка в {func.__name__}: {e}"
            ) from e
    return wrapper


class AnalyticsType(Enum):
    """Типы аналитики"""

    THREAT_ANALYSIS = "threat_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    PERFORMANCE_METRICS = "performance_metrics"
    USER_BEHAVIOR = "user_behavior"
    SYSTEM_HEALTH = "system_health"
    COMPLIANCE_ANALYTICS = "compliance_analytics"


class MetricType(Enum):
    """Типы метрик"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"


class SecurityMetric:
    """Класс для представления метрики безопасности"""

    def __init__(
        self,
        metric_id: str,
        name: str,
        metric_type: MetricType,
        value: float = 0.0,
        unit: str = "",
        tags: Optional[Dict[str, str]] = None,
    ):
        # Валидация параметров
        validate_metric_id(metric_id)
        validate_metric_value(value, metric_type)

        if not isinstance(name, str) or not name.strip():
            raise ValidationError("name должен быть непустой строкой")
        if not isinstance(unit, str):
            raise ValidationError("unit должен быть строкой")
        if tags is not None and not isinstance(tags, dict):
            raise ValidationError("tags должен быть словарем")

        self.metric_id = metric_id
        self.name = name
        self.metric_type = metric_type
        self.value = value
        self.unit = unit
        self.tags = tags or {}
        self.timestamp = datetime.now()
        self.history = []
        self.thresholds = {}
        self.alert_enabled = False

    @enhanced_error_handler
    def update_value(
        self, new_value: float, timestamp: Optional[datetime] = None
    ):
        """Обновление значения метрики"""
        # Валидация нового значения
        validate_metric_value(new_value, self.metric_type)

        if timestamp is not None and not isinstance(timestamp, datetime):
            raise ValidationError("timestamp должен быть объектом datetime")

        self.value = new_value
        self.timestamp = timestamp or datetime.now()

        # Сохранение в историю
        history_entry = {
            "value": new_value,
            "timestamp": self.timestamp.isoformat(),
        }
        self.history.append(history_entry)

        # Ограничиваем размер истории
        if len(self.history) > 1000:
            self.history.pop(0)

    def set_threshold(self, threshold_type: str, value: float):
        """Установка порога для метрики"""
        self.thresholds[threshold_type] = value

    def check_thresholds(self) -> List[str]:
        """Проверка порогов метрики"""
        alerts = []

        for threshold_type, threshold_value in self.thresholds.items():
            if threshold_type == "max" and self.value > threshold_value:
                alerts.append(
                    f"Превышен максимальный порог: {self.value} > "
                    f"{threshold_value}"
                )
            elif threshold_type == "min" and self.value < threshold_value:
                alerts.append(
                    f"Ниже минимального порога: {self.value} < "
                    f"{threshold_value}"
                )

        return alerts

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "metric_type": self.metric_type.value,
            "value": self.value,
            "unit": self.unit,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat(),
            "thresholds": self.thresholds,
            "alert_enabled": self.alert_enabled,
        }

    def __str__(self) -> str:
        """Строковое представление метрики"""
        return (
            f"SecurityMetric(id='{self.metric_id}', name='{self.name}', "
            f"type={self.metric_type.value}, value={self.value}, "
            f"unit='{self.unit}')"
        )

    def __repr__(self) -> str:
        """Представление для отладки"""
        return (
            f"SecurityMetric(metric_id='{self.metric_id}', "
            f"name='{self.name}', metric_type={self.metric_type}, "
            f"value={self.value}, unit='{self.unit}', tags={self.tags})"
        )

    def __eq__(self, other) -> bool:
        """Сравнение метрик по ID"""
        if not isinstance(other, SecurityMetric):
            return False
        return self.metric_id == other.metric_id

    def __hash__(self) -> int:
        """Хеширование для использования в словарях"""
        return hash(self.metric_id)

    def __len__(self) -> int:
        """Количество записей в истории"""
        return len(self.history)

    def __contains__(self, item) -> bool:
        """Проверка наличия значения в истории"""
        if isinstance(item, (int, float)):
            return any(record["value"] == item for record in self.history)
        return False

    def validate(self) -> List[str]:
        """
        Валидация данных метрики

        Returns:
            List[str]: Список ошибок валидации
        """
        errors = []

        if not self.metric_id or not isinstance(self.metric_id, str):
            errors.append("metric_id должен быть непустой строкой")

        if not self.name or not isinstance(self.name, str):
            errors.append("name должен быть непустой строкой")

        if not isinstance(self.value, (int, float)):
            errors.append("value должен быть числом")

        if self.value < 0 and self.metric_type in [
            MetricType.COUNTER,
            MetricType.GAUGE,
        ]:
            errors.append(
                "value не может быть отрицательным для данного типа метрики"
            )

        if not isinstance(self.unit, str):
            errors.append("unit должен быть строкой")

        if not isinstance(self.tags, dict):
            errors.append("tags должен быть словарем")

        return errors

    def reset(self) -> None:
        """Сброс метрики к начальному состоянию"""
        self.value = 0.0
        self.history.clear()
        self.thresholds.clear()
        self.alert_enabled = True
        self.timestamp = datetime.now()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики метрики

        Returns:
            Dict[str, Any]: Статистика метрики
        """
        if not self.history:
            return {
                "count": 0,
                "min": self.value,
                "max": self.value,
                "avg": self.value,
                "sum": self.value,
            }

        values = [record["value"] for record in self.history]

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "sum": sum(values),
            "current": self.value,
            "last_updated": self.timestamp.isoformat(),
        }

    def export_data(self) -> Dict[str, Any]:
        """
        Экспорт данных метрики

        Returns:
            Dict[str, Any]: Экспортированные данные
        """
        return {
            "metric_info": self.to_dict(),
            "history": self.history,
            "statistics": self.get_statistics(),
        }

    def import_data(self, data: Dict[str, Any]) -> bool:
        """
        Импорт данных метрики

        Args:
            data: Данные для импорта

        Returns:
            bool: True если импорт успешен
        """
        try:
            if "metric_info" in data:
                metric_info = data["metric_info"]
                self.metric_id = metric_info.get("metric_id", self.metric_id)
                self.name = metric_info.get("name", self.name)
                self.value = metric_info.get("value", self.value)
                self.unit = metric_info.get("unit", self.unit)
                self.tags = metric_info.get("tags", self.tags)
                self.thresholds = metric_info.get(
                    "thresholds", self.thresholds
                )
                self.alert_enabled = metric_info.get(
                    "alert_enabled", self.alert_enabled
                )

            if "history" in data:
                self.history = data["history"]

            return True
        except Exception:
            return False

    @enhanced_error_handler
    def add_threshold(self, level: str, value: float) -> None:
        """
        Добавление порогового значения для метрики

        Args:
            level: Уровень порога (warning, critical, info)
            value: Значение порога
        """
        # Валидация параметров
        if not isinstance(level, str) or not level.strip():
            raise ValidationError("level должен быть непустой строкой")

        validate_threshold_value(value)

        # Проверка допустимых уровней
        allowed_levels = {"warning", "critical", "info", "error", "debug"}
        if level.lower() not in allowed_levels:
            raise ValidationError(
                f"level должен быть одним из: {', '.join(allowed_levels)}"
            )

        self.thresholds[level.lower()] = value
        # SecurityMetric не имеет log_activity, используем print для отладки

    def get_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Получение истории метрики с ограничением

        Args:
            limit: Максимальное количество записей (None = все)

        Returns:
            List[Dict[str, Any]]: История метрики
        """
        if limit is None:
            return self.history.copy()

        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit должен быть положительным целым числом")

        return (
            self.history[-limit:]
            if limit < len(self.history)
            else self.history.copy()
        )

    def clear_history(self) -> None:
        """Очистка истории метрики"""
        self.history.clear()
        # SecurityMetric не имеет log_activity, используем print для отладки


class SecurityAnalyticsManager(SecurityBase):
    """Менеджер аналитики безопасности для системы ALADDIN"""

    def __init__(
        self,
        name: str = "SecurityAnalyticsManager",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Конфигурация аналитики
        self.data_retention_days = (
            config.get("data_retention_days", 90) if config else 90
        )
        self.analysis_interval = (
            config.get("analysis_interval", 300) if config else 300
        )  # 5 минут
        self.enable_real_time = (
            config.get("enable_real_time", True) if config else True
        )
        self.alert_threshold = (
            config.get("alert_threshold", 0.8) if config else 0.8
        )

        # Хранилище данных
        self.metrics = {}
        self.analytics_data = {}
        self.insights = []
        self.anomalies = []
        self.trends = {}

        # Статистика
        self.total_metrics = 0
        self.active_metrics = 0
        self.analyses_conducted = 0
        self.insights_generated = 0
        self.anomalies_detected = 0
        self.threats_detected = 0
        self.incidents_handled = 0

        # Счетчики производительности
        self.execution_count = 0
        self.success_count = 0
        self.error_count = 0

        # Временные метки
        self.created_at = datetime.now()
        self.start_time = None
        self.last_activity = None

    def initialize(self) -> bool:
        """Инициализация менеджера аналитики безопасности"""
        try:
            self.log_activity(
                f"Инициализация менеджера аналитики безопасности {self.name}"
            )
            self.status = ComponentStatus.INITIALIZING

            # Создание базовых метрик
            self._create_basic_metrics()

            # Настройка аналитических процессов
            self._setup_analytics_processes()

            # Инициализация системы оповещений
            self._setup_alerting_system()

            # Запуск реального времени
            if self.enable_real_time:
                self._start_real_time_analytics()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Менеджер аналитики безопасности {self.name} "
                f"успешно инициализирован"
            )
            return True

        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка инициализации менеджера аналитики: {e}",
                "error",
            )
            return False

    def _create_basic_metrics(self):
        """Создание базовых метрик безопасности"""
        basic_metrics = [
            {
                "metric_id": "threat_detection_rate",
                "name": "Скорость обнаружения угроз",
                "metric_type": MetricType.RATE,
                "unit": "threats/hour",
                "tags": {"category": "threat_management"},
            },
            {
                "metric_id": "incident_response_time",
                "name": "Время реагирования на инциденты",
                "metric_type": MetricType.TIMER,
                "unit": "minutes",
                "tags": {"category": "incident_management"},
            },
            {
                "metric_id": "system_uptime",
                "name": "Время работы системы",
                "metric_type": MetricType.GAUGE,
                "unit": "percentage",
                "tags": {"category": "system_health"},
            },
            {
                "metric_id": "failed_login_attempts",
                "name": "Неудачные попытки входа",
                "metric_type": MetricType.COUNTER,
                "unit": "attempts",
                "tags": {"category": "authentication"},
            },
            {
                "metric_id": "data_breach_risk",
                "name": "Риск утечки данных",
                "metric_type": MetricType.GAUGE,
                "unit": "risk_score",
                "tags": {"category": "risk_assessment"},
            },
        ]

        for metric_data in basic_metrics:
            metric = SecurityMetric(
                metric_id=metric_data["metric_id"],
                name=metric_data["name"],
                metric_type=metric_data["metric_type"],
                unit=metric_data["unit"],
                tags=metric_data["tags"],
            )

            # Установка порогов для критических метрик
            if metric_data["metric_id"] == "system_uptime":
                metric.set_threshold("min", 95.0)  # Минимум 95% uptime
            elif metric_data["metric_id"] == "data_breach_risk":
                metric.set_threshold("max", 0.7)  # Максимальный риск 0.7

            self.add_metric(metric)

        self.log_activity(
            f"Создано {len(basic_metrics)} базовых метрик безопасности"
        )

    def _setup_analytics_processes(self):
        """Настройка аналитических процессов"""
        self.analytics_data = {
            "threat_analysis": {
                "enabled": True,
                "interval": 300,  # 5 минут
                "last_run": None,
            },
            "risk_assessment": {
                "enabled": True,
                "interval": 3600,  # 1 час
                "last_run": None,
            },
            "performance_metrics": {
                "enabled": True,
                "interval": 60,  # 1 минута
                "last_run": None,
            },
            "user_behavior": {
                "enabled": True,
                "interval": 1800,  # 30 минут
                "last_run": None,
            },
        }
        self.log_activity("Аналитические процессы настроены")

    def _setup_alerting_system(self):
        """Настройка системы оповещений"""
        # Здесь будет логика системы оповещений
        self.log_activity("Система оповещений настроена")

    def _start_real_time_analytics(self):
        """Запуск аналитики в реальном времени"""
        # Здесь будет логика аналитики в реальном времени
        self.log_activity("Аналитика в реальном времени запущена")

    def add_metric(self, metric: SecurityMetric) -> bool:
        """
        Добавление метрики безопасности

        Args:
            metric: Метрика безопасности

        Returns:
            bool: True если метрика добавлена
        """
        try:
            if metric.metric_id in self.metrics:
                self.log_activity(
                    f"Метрика {metric.metric_id} уже существует", "warning"
                )
                return False

            self.metrics[metric.metric_id] = metric
            self.total_metrics += 1
            self.active_metrics += 1

            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка добавления метрики {metric.metric_id}: {e}",
                "error",
            )
            return False

    def update_metric(
        self,
        metric_id: str,
        value: float,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """
        Обновление метрики

        Args:
            metric_id: ID метрики
            value: Новое значение
            timestamp: Временная метка

        Returns:
            bool: True если метрика обновлена
        """
        try:
            if metric_id not in self.metrics:
                return False

            metric = self.metrics[metric_id]
            metric.update_value(value, timestamp)

            # Проверка порогов
            if metric.alert_enabled:
                alerts = metric.check_thresholds()
                for alert in alerts:
                    self.log_activity(
                        f"Алерт метрики {metric_id}: {alert}", "warning"
                    )

            return True

        except Exception:
            return False

    def get_metric(self, metric_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение метрики

        Args:
            metric_id: ID метрики

        Returns:
            Optional[Dict[str, Any]]: Данные метрики
        """
        if metric_id not in self.metrics:
            return None

        return self.metrics[metric_id].to_dict()

    def get_metrics_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Получение метрик по категории

        Args:
            category: Категория метрик

        Returns:
            List[Dict[str, Any]]: Список метрик
        """
        return [
            metric.to_dict()
            for metric in self.metrics.values()
            if metric.tags.get("category") == category
        ]

    def get_metric_history(
        self, metric_id: str, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Получение истории метрики

        Args:
            metric_id: ID метрики
            hours: Количество часов истории

        Returns:
            List[Dict[str, Any]]: История метрики
        """
        try:
            if metric_id not in self.metrics:
                return []

            metric = self.metrics[metric_id]
            cutoff_time = datetime.now() - timedelta(hours=hours)

            history = [
                entry
                for entry in metric.history
                if datetime.fromisoformat(entry["timestamp"]) >= cutoff_time
            ]

            return history

        except Exception as e:
            self.log_activity(
                f"Ошибка получения истории метрики: {e}", "error"
            )
            return []

    def conduct_threat_analysis(self) -> Dict[str, Any]:
        """
        Проведение анализа угроз

        Returns:
            Dict[str, Any]: Результаты анализа угроз
        """
        try:
            analysis_result = {
                "timestamp": datetime.now().isoformat(),
                "threat_level": "medium",
                "active_threats": 0,
                "threat_trends": [],
                "recommendations": [],
            }

            # Анализ метрик угроз
            threat_metrics = self.get_metrics_by_category("threat_management")

            if threat_metrics:
                # Расчет общего уровня угроз
                threat_scores = []
                for metric in threat_metrics:
                    if metric["metric_id"] == "threat_detection_rate":
                        threat_scores.append(
                            min(1.0, metric["value"] / 100.0)
                        )  # Нормализация

                if threat_scores:
                    avg_threat_score = sum(threat_scores) / len(threat_scores)

                    if avg_threat_score > 0.8:
                        analysis_result["threat_level"] = "high"
                    elif avg_threat_score > 0.5:
                        analysis_result["threat_level"] = "medium"
                    else:
                        analysis_result["threat_level"] = "low"

            # Генерация рекомендаций
            if analysis_result["threat_level"] == "high":
                analysis_result["recommendations"].append(
                    "Усилить мониторинг угроз"
                )
                analysis_result["recommendations"].append(
                    "Провести дополнительный анализ " "безопасности"
                )

            self.analyses_conducted += 1
            self.log_activity(
                f"Анализ угроз завершен: уровень "
                f"{analysis_result['threat_level']}"
            )

            return analysis_result

        except Exception as e:
            self.log_activity(f"Ошибка получения метрик: {e}", "error")
            return {}

    def conduct_risk_assessment(self) -> Dict[str, Any]:
        """
        Проведение оценки рисков

        Returns:
            Dict[str, Any]: Результаты оценки рисков
        """
        try:
            risk_assessment = {
                "timestamp": datetime.now().isoformat(),
                "overall_risk_score": 0.0,
                "risk_categories": {},
                "high_risk_items": [],
                "mitigation_actions": [],
            }

            # Анализ метрик рисков
            risk_metrics = self.get_metrics_by_category("risk_assessment")

            risk_scores = []
            for metric in risk_metrics:
                if metric["metric_id"] == "data_breach_risk":
                    risk_score = metric["value"]
                    risk_scores.append(risk_score)

                    if risk_score > 0.7:
                        risk_assessment["high_risk_items"].append(
                            {
                                "metric": metric["name"],
                                "value": risk_score,
                                "description": "Высокий риск утечки данных",
                            }
                        )

            # Расчет общего риска
            if risk_scores:
                risk_assessment["overall_risk_score"] = sum(risk_scores) / len(
                    risk_scores
                )

            # Генерация действий по снижению рисков
            if risk_assessment["overall_risk_score"] > 0.6:
                risk_assessment["mitigation_actions"].append(
                    "Провести аудит безопасности"
                )
                risk_assessment["mitigation_actions"].append(
                    "Усилить меры защиты данных"
                )

            self.analyses_conducted += 1
            self.log_activity(
                f"Оценка рисков завершена: общий риск "
                f"{risk_assessment['overall_risk_score']:.2f}"
            )

            return risk_assessment

        except Exception as e:
            self.log_activity(f"Ошибка проведения оценки рисков: {e}", "error")
            return {}

    def analyze_performance_metrics(self) -> Dict[str, Any]:
        """
        Анализ метрик производительности

        Returns:
            Dict[str, Any]: Результаты анализа производительности
        """
        try:
            performance_analysis = {
                "timestamp": datetime.now().isoformat(),
                "system_health": "good",
                "performance_issues": [],
                "optimization_recommendations": [],
            }

            # Анализ метрик производительности
            health_metrics = self.get_metrics_by_category("system_health")

            for metric in health_metrics:
                if metric["metric_id"] == "system_uptime":
                    uptime = metric["value"]

                    if uptime < 95.0:
                        performance_analysis["system_health"] = "poor"
                        performance_analysis["performance_issues"].append(
                            {
                                "metric": metric["name"],
                                "value": uptime,
                                "issue": "Низкий uptime системы",
                            }
                        )
                    elif uptime < 99.0:
                        performance_analysis["system_health"] = "fair"
                        performance_analysis[
                            "optimization_recommendations"
                        ].append("Улучшить стабильность системы")

            self.analyses_conducted += 1
            self.log_activity(
                f"Анализ производительности завершен: "
                f"здоровье {performance_analysis['system_health']}"
            )

            return performance_analysis

        except Exception as e:
            self.log_activity(
                f"Ошибка анализа производительности: {e}", "error"
            )
            return {}

    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """
        Обнаружение аномалий

        Returns:
            List[Dict[str, Any]]: Список обнаруженных аномалий
        """
        try:
            anomalies = []

            for metric in self.metrics.values():
                if (
                    len(metric.history) < 10
                ):  # Нужно минимум 10 точек для анализа
                    continue

                # Простой алгоритм обнаружения аномалий (отклонение от
                # среднего)
                values = [
                    entry["value"] for entry in metric.history[-20:]
                ]  # Последние 20 значений

                if len(values) >= 5:
                    mean_value = sum(values) / len(values)
                    variance = sum(
                        (x - mean_value) ** 2 for x in values
                    ) / len(values)
                    std_dev = math.sqrt(variance)

                    current_value = metric.value
                    z_score = (
                        abs(current_value - mean_value) / std_dev
                        if std_dev > 0
                        else 0
                    )

                    # Аномалия если z-score > 2
                    if z_score > 2.0:
                        anomaly = {
                            "metric_id": metric.metric_id,
                            "metric_name": metric.name,
                            "current_value": current_value,
                            "expected_range": (
                                f"{mean_value - 2*std_dev:.2f} - "
                                f"{mean_value + 2*std_dev:.2f}"
                            ),
                            "z_score": z_score,
                            "timestamp": datetime.now().isoformat(),
                            "severity": (
                                "high" if z_score > 3.0 else "medium"
                            ),
                        }
                        anomalies.append(anomaly)

            self.anomalies_detected += len(anomalies)

            if anomalies:
                self.log_activity(
                    f"Обнаружено {len(anomalies)} аномалий",
                    "warning",
                )

            return anomalies

        except Exception as e:
            self.log_activity(
                f"Ошибка анализа метрик производительности: {e}", "error"
            )
            return []

    def generate_insights(self) -> List[Dict[str, Any]]:
        """
        Генерация аналитических инсайтов

        Returns:
            List[Dict[str, Any]]: Список инсайтов
        """
        try:
            insights = []

            # Анализ трендов
            for metric in self.metrics.values():
                if len(metric.history) < 20:
                    continue

                # Анализ тренда (последние 20 значений)
                recent_values = [
                    entry["value"] for entry in metric.history[-20:]
                ]

                if len(recent_values) >= 10:
                    # Простой анализ тренда
                    first_half = recent_values[:10]
                    second_half = recent_values[10:]

                    first_avg = sum(first_half) / len(first_half)
                    second_avg = sum(second_half) / len(second_half)

                    change_percent = (
                        ((second_avg - first_avg) / first_avg * 100)
                        if first_avg > 0
                        else 0
                    )

                    if abs(change_percent) > 10:  # Значительное изменение
                        trend = (
                            "увеличение" if change_percent > 0 else "снижение"
                        )

                        insight = {
                            "metric_id": metric.metric_id,
                            "metric_name": metric.name,
                            "trend": trend,
                            "change_percent": abs(change_percent),
                            "description": f"{metric.name} показывает {trend} "
                            f"изменение на {change_percent:.1f}%",
                            "timestamp": datetime.now().isoformat(),
                            "category": metric.tags.get("category", "general"),
                        }
                        insights.append(insight)

            self.insights_generated += len(insights)

            if insights:
                self.log_activity(
                    f"Сгенерировано {len(insights)} инсайтов",
                    "info",
                )

            return insights

        except Exception as e:
            self.log_activity(f"Ошибка генерации инсайтов: {e}", "error")
            return []

    def get_analytics_dashboard_data(self) -> Dict[str, Any]:
        """
        Получение данных для аналитической панели

        Returns:
            Dict[str, Any]: Данные для панели
        """
        try:
            dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "metrics_summary": {
                    "total_metrics": self.total_metrics,
                    "active_metrics": self.active_metrics,
                    "metrics_by_category": self._get_metrics_by_category(),
                },
                "recent_analyses": {
                    "threat_analysis": self.conduct_threat_analysis(),
                    "risk_assessment": self.conduct_risk_assessment(),
                    "performance_analysis": self.analyze_performance_metrics(),
                },
                "anomalies": self.detect_anomalies(),
                "insights": self.generate_insights(),
                "trends": self._get_system_trends(),
            }

            return dashboard_data

        except Exception as e:
            self.log_activity(
                f"Ошибка получения данных дашборда: {e}", "error"
            )
            return {}

    def _get_metrics_by_category(self) -> Dict[str, int]:
        """Получение количества метрик по категориям"""
        category_count = {}
        for metric in self.metrics.values():
            category = metric.tags.get("category", "general")
            category_count[category] = category_count.get(category, 0) + 1
        return category_count

    def _get_system_trends(self) -> Dict[str, Any]:
        """Получение системных трендов"""
        try:
            trends = {}

            for metric in self.metrics.values():
                if len(metric.history) >= 10:
                    recent_values = [
                        entry["value"] for entry in metric.history[-10:]
                    ]
                    trend_direction = "stable"

                    if len(recent_values) >= 5:
                        first_half = recent_values[:5]
                        second_half = recent_values[5:]

                        first_avg = sum(first_half) / len(first_half)
                        second_avg = sum(second_half) / len(second_half)

                        if second_avg > first_avg * 1.1:
                            trend_direction = "increasing"
                        elif second_avg < first_avg * 0.9:
                            trend_direction = "decreasing"

                    trends[metric.metric_id] = {
                        "direction": trend_direction,
                        "current_value": metric.value,
                        "category": metric.tags.get("category", "general"),
                    }

            return trends

        except Exception as e:
            self.log_activity(
                f"Ошибка получения метрик по категориям: {e}", "error"
            )
            return {}

    def get_analytics_stats(self) -> Dict[str, Any]:
        """
        Получение статистики аналитики

        Returns:
            Dict[str, Any]: Статистика аналитики
        """
        return {
            "total_metrics": self.total_metrics,
            "active_metrics": self.active_metrics,
            "analyses_conducted": self.analyses_conducted,
            "insights_generated": self.insights_generated,
            "anomalies_detected": self.anomalies_detected,
            "metrics_by_type": self._get_metrics_by_type(),
            "analytics_processes": len(self.analytics_data),
            "data_retention_days": self.data_retention_days,
        }

    def _get_metrics_by_type(self) -> Dict[str, int]:
        """Получение количества метрик по типам"""
        type_count = {}
        for metric in self.metrics.values():
            metric_type = metric.metric_type.value
            type_count[metric_type] = type_count.get(metric_type, 0) + 1
        return type_count

    def start(self) -> bool:
        """Запуск менеджера аналитики безопасности"""
        try:
            self.log_activity(
                f"Запуск менеджера аналитики безопасности {self.name}"
            )
            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Менеджер аналитики безопасности {self.name} "
                f"успешно запущен"
            )
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка запуска менеджера аналитики: {e}",
                "error",
            )
            return False

    def stop(self) -> bool:
        """Остановка менеджера аналитики безопасности"""
        try:
            self.log_activity(
                f"Остановка менеджера аналитики " f"безопасности {self.name}"
            )

            # Остановка аналитики в реальном времени
            self.enable_real_time = False

            self.status = ComponentStatus.STOPPED
            self.log_activity(
                f"Менеджер аналитики безопасности {self.name} "
                f"успешно остановлен"
            )
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка остановки менеджера аналитики: {e}",
                "error",
            )
            return False

    def __str__(self) -> str:
        """Строковое представление менеджера"""
        return (
            f"SecurityAnalyticsManager(name='{self.name}', "
            f"status={self.status.value}, metrics={len(self.metrics)})"
        )

    def __repr__(self) -> str:
        """Представление для отладки"""
        return (
            f"SecurityAnalyticsManager(name='{self.name}', "
            f"status={self.status}, metrics={len(self.metrics)}, "
            f"config={self.config})"
        )

    def __eq__(self, other) -> bool:
        """Сравнение менеджеров по имени"""
        if not isinstance(other, SecurityAnalyticsManager):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        """Хеширование для использования в словарях"""
        return hash(self.name)

    def __len__(self) -> int:
        """Количество метрик в менеджере"""
        return len(self.metrics)

    def __contains__(self, item) -> bool:
        """Проверка наличия метрики по ID"""
        if isinstance(item, str):
            return item in self.metrics
        return False

    def validate_config(self) -> List[str]:
        """
        Валидация конфигурации менеджера

        Returns:
            List[str]: Список ошибок валидации
        """
        errors = []

        if not isinstance(self.config, dict):
            errors.append("config должен быть словарем")

        if (
            not isinstance(self.analysis_interval, int)
            or self.analysis_interval <= 0
        ):
            errors.append(
                "analysis_interval должен быть положительным целым числом"
            )

        if (
            not isinstance(self.data_retention_days, int)
            or self.data_retention_days <= 0
        ):
            errors.append(
                "data_retention_days должен быть положительным целым числом"
            )

        if (
            not isinstance(self.alert_threshold, (int, float))
            or self.alert_threshold < 0
        ):
            errors.append("alert_threshold должен быть неотрицательным числом")

        if not isinstance(self.enable_real_time, bool):
            errors.append("enable_real_time должен быть булевым значением")

        if not isinstance(self.encryption_enabled, bool):
            errors.append("encryption_enabled должен быть булевым значением")

        return errors

    def get_health_status(self) -> Dict[str, Any]:
        """
        Получение статуса здоровья менеджера

        Returns:
            Dict[str, Any]: Статус здоровья
        """
        health_score = 100

        # Проверка статуса
        if self.status != ComponentStatus.RUNNING:
            health_score -= 30

        # Проверка метрик
        if len(self.metrics) == 0:
            health_score -= 20

        # Проверка ошибок
        if self.error_count > 0:
            health_score -= min(30, self.error_count * 5)

        # Проверка последней активности
        if self.last_activity:
            time_since_activity = (
                datetime.now() - self.last_activity
            ).total_seconds()
            if time_since_activity > 3600:  # 1 час
                health_score -= 20

        health_level = (
            "excellent"
            if health_score >= 90
            else (
                "good"
                if health_score >= 70
                else "fair" if health_score >= 50 else "poor"
            )
        )

        return {
            "health_score": health_score,
            "health_level": health_level,
            "status": self.status.value,
            "metrics_count": len(self.metrics),
            "error_count": self.error_count,
            "last_activity": (
                self.last_activity.isoformat() if self.last_activity else None
            ),
            "uptime": (
                (datetime.now() - self.start_time).total_seconds()
                if self.start_time
                else 0
            ),
        }

    def backup_data(self) -> Dict[str, Any]:
        """
        Резервное копирование данных менеджера

        Returns:
            Dict[str, Any]: Резервная копия данных
        """
        backup = {
            "manager_info": {
                "name": self.name,
                "config": self.config,
                "status": self.status.value,
                "created_at": (
                    self.created_at.isoformat()
                    if hasattr(self, "created_at")
                    else None
                ),
            },
            "metrics": {},
            "analytics_data": self.analytics_data,
            "trends": self.trends,
            "insights": self.insights,
            "anomalies": self.anomalies,
            "backup_timestamp": datetime.now().isoformat(),
        }

        # Экспорт всех метрик
        for metric_id, metric in self.metrics.items():
            backup["metrics"][metric_id] = metric.export_data()

        return backup

    def restore_data(self, backup_data: Dict[str, Any]) -> bool:
        """
        Восстановление данных из резервной копии

        Args:
            backup_data: Данные резервной копии

        Returns:
            bool: True если восстановление успешно
        """
        try:
            # Восстановление информации о менеджере
            if "manager_info" in backup_data:
                manager_info = backup_data["manager_info"]
                self.config = manager_info.get("config", self.config)

            # Восстановление метрик
            if "metrics" in backup_data:
                self.metrics.clear()
                for metric_id, metric_data in backup_data["metrics"].items():
                    metric = SecurityMetric("", "", MetricType.COUNTER, 0.0)
                    if metric.import_data(metric_data):
                        self.metrics[metric_id] = metric

            # Восстановление аналитических данных
            self.analytics_data = backup_data.get("analytics_data", {})
            self.trends = backup_data.get("trends", {})
            self.insights = backup_data.get("insights", [])
            self.anomalies = backup_data.get("anomalies", [])

            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка получения статистики аналитики: {e}", "error"
            )
            return False

    def cleanup_old_data(self, days: int = None) -> int:
        """
        Очистка старых данных

        Args:
            days: Количество дней для хранения (по умолчанию
                data_retention_days)

        Returns:
            int: Количество удаленных записей
        """
        if days is None:
            days = self.data_retention_days

        cutoff_date = datetime.now() - timedelta(days=days)
        removed_count = 0

        # Очистка истории метрик
        for metric in self.metrics.values():
            original_count = len(metric.history)
            metric.history = [
                record
                for record in metric.history
                if isinstance(record.get("timestamp"), datetime)
                and record["timestamp"] >= cutoff_date
            ]
            removed_count += original_count - len(metric.history)

        # Очистка аналитических данных
        if "threat_analysis" in self.analytics_data and isinstance(
            self.analytics_data["threat_analysis"], list
        ):
            original_count = len(self.analytics_data["threat_analysis"])
            self.analytics_data["threat_analysis"] = [
                analysis
                for analysis in self.analytics_data["threat_analysis"]
                if isinstance(analysis, dict)
                and analysis.get("timestamp", datetime.min) >= cutoff_date
            ]
            removed_count += original_count - len(
                self.analytics_data["threat_analysis"]
            )

        # Очистка инсайтов
        original_insights = len(self.insights)
        self.insights = [
            insight
            for insight in self.insights
            if isinstance(insight, dict)
            and insight.get("timestamp", datetime.min) >= cutoff_date
        ]
        removed_count += original_insights - len(self.insights)

        # Очистка аномалий
        original_anomalies = len(self.anomalies)
        self.anomalies = [
            anomaly
            for anomaly in self.anomalies
            if isinstance(anomaly, dict)
            and anomaly.get("timestamp", datetime.min) >= cutoff_date
        ]
        removed_count += original_anomalies - len(self.anomalies)

        self.log_activity(f"Очищено {removed_count} старых записей")
        return removed_count

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Получение метрик производительности менеджера

        Returns:
            Dict[str, Any]: Метрики производительности
        """
        return {
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": (self.success_count / max(1, self.execution_count))
            * 100,
            "metrics_processed": len(self.metrics),
            "analyses_conducted": self.analyses_conducted,
            "threats_detected": self.threats_detected,
            "anomalies_detected": self.anomalies_detected,
            "insights_generated": self.insights_generated,
            "incidents_handled": self.incidents_handled,
            "uptime_seconds": (
                (datetime.now() - self.start_time).total_seconds()
                if self.start_time
                else 0
            ),
            "memory_usage": len(str(self.metrics))
            + len(str(self.analytics_data)),
            "last_activity": (
                self.last_activity.isoformat() if self.last_activity else None
            ),
        }

    def validate_integrity(self) -> Dict[str, Any]:
        """
        Проверка целостности данных менеджера

        Returns:
            Dict[str, Any]: Результаты проверки целостности
        """
        integrity_issues = []

        # Проверка метрик
        for metric_id, metric in self.metrics.items():
            validation_errors = metric.validate()
            if validation_errors:
                integrity_issues.append(
                    {
                        "type": "metric_validation",
                        "metric_id": metric_id,
                        "errors": validation_errors,
                    }
                )

        # Проверка конфигурации
        config_errors = self.validate_config()
        if config_errors:
            integrity_issues.append(
                {"type": "config_validation", "errors": config_errors}
            )

        # Проверка статуса
        if self.status not in [
            ComponentStatus.INITIALIZING,
            ComponentStatus.RUNNING,
            ComponentStatus.STOPPED,
        ]:
            integrity_issues.append(
                {
                    "type": "status_validation",
                    "message": f"Проверка целостности: {self.status.value}",
                }
            )

        # Проверка счетчиков
        if (
            self.error_count < 0
            or self.success_count < 0
            or self.execution_count < 0
        ):
            integrity_issues.append(
                {
                    "type": "counter_validation",
                    "error": "Отрицательные значения счетчиков",
                }
            )

        return {
            "is_valid": len(integrity_issues) == 0,
            "issues_count": len(integrity_issues),
            "issues": integrity_issues,
            "checked_at": datetime.now().isoformat(),
        }

    def remove_metric(self, metric_id: str) -> bool:
        """
        Удаление метрики по ID

        Args:
            metric_id: ID метрики для удаления

        Returns:
            bool: True если метрика удалена успешно
        """
        if not isinstance(metric_id, str) or not metric_id.strip():
            raise ValueError("metric_id должен быть непустой строкой")

        if metric_id not in self.metrics:
            self.log_activity(f"Метрика {metric_id} не найдена", "warning")
            return False

        removed_metric = self.metrics.pop(metric_id)
        self.total_metrics = max(0, self.total_metrics - 1)
        self.log_activity(
            f"Удалена метрика {metric_id}: {removed_metric.name}"
        )
        return True

    def analyze_security_metrics(self) -> Dict[str, Any]:
        """
        Анализ метрик безопасности

        Returns:
            Dict[str, Any]: Результаты анализа
        """
        analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "total_metrics": len(self.metrics),
            "metrics_by_type": self._get_metrics_by_type(),
            "security_score": 0,
            "threats_detected": 0,
            "anomalies_found": 0,
            "recommendations": [],
        }

        # Анализ каждой метрики
        for metric_id, metric in self.metrics.items():
            # Проверка пороговых значений
            alerts = metric.check_thresholds()
            if alerts:
                analysis_results["threats_detected"] += len(alerts)

            # Анализ аномалий
            if len(metric.history) > 5:
                values = [record["value"] for record in metric.history[-10:]]
                avg_value = sum(values) / len(values)
                current_value = metric.value

                # Простая проверка на аномалии (отклонение > 50%)
                if abs(current_value - avg_value) / max(avg_value, 1) > 0.5:
                    analysis_results["anomalies_found"] += 1

        # Расчет общего балла безопасности
        if analysis_results["total_metrics"] > 0:
            threat_ratio = (
                analysis_results["threats_detected"]
                / analysis_results["total_metrics"]
            )
            anomaly_ratio = (
                analysis_results["anomalies_found"]
                / analysis_results["total_metrics"]
            )
            analysis_results["security_score"] = max(
                0, 100 - (threat_ratio + anomaly_ratio) * 100
            )

        # Генерация рекомендаций
        if analysis_results["threats_detected"] > 0:
            analysis_results["recommendations"].append(
                "Обнаружены угрозы - требуется немедленное внимание"
            )
        if analysis_results["anomalies_found"] > 0:
            analysis_results["recommendations"].append(
                "Обнаружены аномалии - рекомендуется дополнительный анализ"
            )
        if analysis_results["security_score"] < 70:
            analysis_results["recommendations"].append(
                "Низкий балл безопасности - требуется улучшение системы"
            )

        self.analyses_conducted += 1
        self.log_activity(
            "Проведен анализ безопасности"
        )

        return analysis_results

    def get_analytics_summary(self) -> Dict[str, Any]:
        """
        Получение сводки аналитики

        Returns:
            Dict[str, Any]: Сводка аналитики
        """
        summary = {
            "timestamp": datetime.now().isoformat(),
            "manager_status": self.status.value,
            "total_metrics": len(self.metrics),
            "metrics_by_type": self._get_metrics_by_type(),
            "performance": self.get_performance_metrics(),
            "health": self.get_health_status(),
            "recent_insights": self.insights[-5:] if self.insights else [],
            "recent_anomalies": self.anomalies[-5:] if self.anomalies else [],
            "trends": self.trends,
            "data_retention": {
                "days": self.data_retention_days,
                "cleanup_needed": len(self.insights) > 1000
                or len(self.anomalies) > 1000,
            },
        }

        return summary

    def export_analytics(self) -> Dict[str, Any]:
        """
        Экспорт аналитических данных

        Returns:
            Dict[str, Any]: Экспортированные данные
        """
        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "manager_name": self.name,
                "total_metrics": len(self.metrics),
            },
            "metrics": {},
            "analytics_data": self.analytics_data,
            "insights": self.insights,
            "anomalies": self.anomalies,
            "trends": self.trends,
            "performance": self.get_performance_metrics(),
            "health": self.get_health_status(),
        }

        # Экспорт всех метрик
        for metric_id, metric in self.metrics.items():
            export_data["metrics"][metric_id] = metric.export_data()

        self.log_activity("Экспортированы аналитические данные")
        return export_data

    def import_analytics(self, data: Dict[str, Any]) -> bool:
        """
        Импорт аналитических данных

        Args:
            data: Данные для импорта

        Returns:
            bool: True если импорт успешен
        """
        try:
            # Импорт метрик
            if "metrics" in data:
                for metric_id, metric_data in data["metrics"].items():
                    metric = SecurityMetric("", "", MetricType.COUNTER, 0.0)
                    if metric.import_data(metric_data):
                        self.metrics[metric_id] = metric

            # Импорт аналитических данных
            self.analytics_data = data.get("analytics_data", {})
            self.insights = data.get("insights", [])
            self.anomalies = data.get("anomalies", [])
            self.trends = data.get("trends", {})

            self.log_activity("Импортированы аналитические данные")
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка импорта аналитических данных: {e}", "error"
            )
            return False


# ============================================================================
# АСИНХРОННЫЕ ВЕРСИИ МЕТОДОВ ДЛЯ УЛУЧШЕННОЙ ПРОИЗВОДИТЕЛЬНОСТИ
# ============================================================================


def async_performance_monitor(func):
    """Декоратор для мониторинга производительности асинхронных методов"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            if hasattr(args[0], "log_activity"):
                args[0].log_activity(
                    f"Асинхронный метод {func.__name__} "
                    f"выполнен за {execution_time:.3f}с"
                )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            if hasattr(args[0], "log_activity"):
                args[0].log_activity(
                    f"Ошибка в асинхронном методе {func.__name__} "
                    f"за {execution_time:.3f}с: {e}",
                    "error",
                )
            raise

    return wrapper


class AsyncSecurityAnalyticsManager(SecurityAnalyticsManager):
    """Асинхронная версия менеджера аналитики безопасности"""

    def __init__(
        self,
        name: str = "AsyncSecurityAnalyticsManager",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)
        self.async_execution_count = 0
        self.async_success_count = 0
        self.async_error_count = 0

    @async_performance_monitor
    async def async_analyze_security_metrics(self) -> Dict[str, Any]:
        """
        Асинхронный анализ метрик безопасности

        Returns:
            Dict[str, Any]: Результаты анализа
        """
        self.async_execution_count += 1

        try:
            # Создаем задачи для параллельного анализа метрик
            tasks = []
            for metric_id, metric in self.metrics.items():
                task = asyncio.create_task(
                    self._async_analyze_single_metric(metric_id, metric)
                )
                tasks.append(task)

            # Ждем завершения всех задач
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Обрабатываем результаты
            analysis_results = {
                "timestamp": datetime.now().isoformat(),
                "total_metrics": len(self.metrics),
                "metrics_by_type": self._get_metrics_by_type(),
                "security_score": 0,
                "threats_detected": 0,
                "anomalies_found": 0,
                "recommendations": [],
                "async_analysis": True,
            }

            # Агрегируем результаты
            for result in results:
                if isinstance(result, dict):
                    analysis_results["threats_detected"] += result.get(
                        "threats", 0
                    )
                    analysis_results["anomalies_found"] += result.get(
                        "anomalies", 0
                    )

            # Расчет общего балла безопасности
            if analysis_results["total_metrics"] > 0:
                threat_ratio = (
                    analysis_results["threats_detected"]
                    / analysis_results["total_metrics"]
                )
                anomaly_ratio = (
                    analysis_results["anomalies_found"]
                    / analysis_results["total_metrics"]
                )
                analysis_results["security_score"] = max(
                    0, 100 - (threat_ratio + anomaly_ratio) * 100
                )

            # Генерация рекомендаций
            if analysis_results["threats_detected"] > 0:
                analysis_results["recommendations"].append(
                    "Обнаружены угрозы - требуется немедленное внимание"
                )
            if analysis_results["anomalies_found"] > 0:
                analysis_results["recommendations"].append(
                    "Обнаружены аномалии - рекомендуется дополнительный анализ"
                )
            if analysis_results["security_score"] < 70:
                analysis_results["recommendations"].append(
                    "Низкий балл безопасности - требуется улучшение системы"
                )

            self.analyses_conducted += 1
            self.async_success_count += 1
            self.log_activity(
                "Проведен асинхронный анализ безопасности"
            )

            return analysis_results

        except Exception as e:
            self.async_error_count += 1
            self.log_activity(f"Ошибка асинхронного анализа: {e}", "error")
            raise

    async def _async_analyze_single_metric(
        self, metric_id: str, metric: "SecurityMetric"
    ) -> Dict[str, Any]:
        """
        Асинхронный анализ одной метрики

        Args:
            metric_id: ID метрики
            metric: Объект метрики

        Returns:
            Dict[str, Any]: Результаты анализа метрики
        """
        # Имитируем асинхронную обработку
        await asyncio.sleep(0.001)  # Небольшая задержка для демонстрации

        result = {"metric_id": metric_id, "threats": 0, "anomalies": 0}

        # Проверка пороговых значений
        alerts = metric.check_thresholds()
        if alerts:
            result["threats"] = len(alerts)

        # Анализ аномалий
        if len(metric.history) > 5:
            values = [record["value"] for record in metric.history[-10:]]
            avg_value = sum(values) / len(values)
            current_value = metric.value

            # Простая проверка на аномалии (отклонение > 50%)
            if abs(current_value - avg_value) / max(avg_value, 1) > 0.5:
                result["anomalies"] = 1

        return result

    @async_performance_monitor
    async def async_detect_anomalies(self) -> List[Dict[str, Any]]:
        """
        Асинхронное обнаружение аномалий

        Returns:
            List[Dict[str, Any]]: Список обнаруженных аномалий
        """
        self.async_execution_count += 1

        try:
            anomalies = []

            # Создаем задачи для параллельного анализа метрик
            tasks = []
            for metric_id, metric in self.metrics.items():
                task = asyncio.create_task(
                    self._async_detect_metric_anomalies(metric_id, metric)
                )
                tasks.append(task)

            # Ждем завершения всех задач
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Собираем все аномалии
            for result in results:
                if isinstance(result, list):
                    anomalies.extend(result)

            self.anomalies.extend(anomalies)
            self.anomalies_detected += len(anomalies)
            self.async_success_count += 1

            self.log_activity(
                f"Асинхронно обнаружено {len(anomalies)} аномалий"
            )
            return anomalies

        except Exception as e:
            self.async_error_count += 1
            self.log_activity(
                f"Ошибка асинхронного обнаружения аномалий: {e}", "error"
            )
            raise

    async def _async_detect_metric_anomalies(
        self, metric_id: str, metric: "SecurityMetric"
    ) -> List[Dict[str, Any]]:
        """
        Асинхронное обнаружение аномалий в одной метрике

        Args:
            metric_id: ID метрики
            metric: Объект метрики

        Returns:
            List[Dict[str, Any]]: Список аномалий метрики
        """
        # Имитируем асинхронную обработку
        await asyncio.sleep(0.001)

        anomalies = []

        if len(metric.history) > 10:
            values = [record["value"] for record in metric.history[-20:]]
            avg_value = sum(values) / len(values)
            std_dev = (
                sum((x - avg_value) ** 2 for x in values) / len(values)
            ) ** 0.5

            current_value = metric.value

            # Проверка на аномалии (отклонение > 2 стандартных отклонений)
            if std_dev > 0 and abs(current_value - avg_value) > 2 * std_dev:
                anomaly = {
                    "metric_id": metric_id,
                    "metric_name": metric.name,
                    "value": current_value,
                    "expected_range": [
                        avg_value - 2 * std_dev,
                        avg_value + 2 * std_dev,
                    ],
                    "deviation": abs(current_value - avg_value) / std_dev,
                    "timestamp": datetime.now().isoformat(),
                    "severity": (
                        "high"
                        if abs(current_value - avg_value) > 3 * std_dev
                        else "medium"
                    ),
                }
                anomalies.append(anomaly)

        return anomalies

    @async_performance_monitor
    async def async_generate_insights(self) -> List[Dict[str, Any]]:
        """
        Асинхронная генерация инсайтов

        Returns:
            List[Dict[str, Any]]: Список сгенерированных инсайтов
        """
        self.async_execution_count += 1

        try:
            insights = []

            # Создаем задачи для параллельного анализа
            tasks = [
                asyncio.create_task(self._async_analyze_trends()),
                asyncio.create_task(self._async_analyze_correlations()),
                asyncio.create_task(self._async_analyze_performance()),
            ]

            # Ждем завершения всех задач
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Собираем все инсайты
            for result in results:
                if isinstance(result, list):
                    insights.extend(result)

            self.insights.extend(insights)
            self.insights_generated += len(insights)
            self.async_success_count += 1

            self.log_activity(
                f"Асинхронно сгенерировано {len(insights)} инсайтов"
            )
            return insights

        except Exception as e:
            self.async_error_count += 1
            self.log_activity(
                f"Ошибка асинхронной генерации инсайтов: {e}", "error"
            )
            raise

    async def _async_analyze_trends(self) -> List[Dict[str, Any]]:
        """Асинхронный анализ трендов"""
        await asyncio.sleep(0.002)

        insights = []
        for metric_id, metric in self.metrics.items():
            if len(metric.history) > 5:
                values = [record["value"] for record in metric.history[-10:]]
                trend = (
                    "increasing"
                    if values[-1] > values[0]
                    else "decreasing" if values[-1] < values[0] else "stable"
                )

                insight = {
                    "type": "trend_analysis",
                    "metric_id": metric_id,
                    "metric_name": metric.name,
                    "trend": trend,
                    "change_percent": (
                        ((values[-1] - values[0]) / values[0] * 100)
                        if values[0] != 0
                        else 0
                    ),
                    "timestamp": datetime.now().isoformat(),
                    "confidence": 0.8,
                }
                insights.append(insight)

        return insights

    async def _async_analyze_correlations(self) -> List[Dict[str, Any]]:
        """Асинхронный анализ корреляций между метриками"""
        await asyncio.sleep(0.003)

        insights = []
        metric_list = list(self.metrics.items())

        for i, (metric_id1, metric1) in enumerate(metric_list):
            for metric_id2, metric2 in metric_list[i + 1:]:
                if len(metric1.history) > 5 and len(metric2.history) > 5:
                    values1 = [
                        record["value"] for record in metric1.history[-10:]
                    ]
                    values2 = [
                        record["value"] for record in metric2.history[-10:]
                    ]

                    # Простой расчет корреляции
                    if len(values1) == len(values2):
                        correlation = self._calculate_correlation(
                            values1, values2
                        )
                        if abs(correlation) > 0.7:
                            insight = {
                                "type": "correlation_analysis",
                                "metric1_id": metric_id1,
                                "metric2_id": metric_id2,
                                "correlation": correlation,
                                "strength": (
                                    "strong"
                                    if abs(correlation) > 0.8
                                    else "moderate"
                                ),
                                "timestamp": datetime.now().isoformat(),
                                "confidence": abs(correlation),
                            }
                            insights.append(insight)

        return insights

    async def _async_analyze_performance(self) -> List[Dict[str, Any]]:
        """Асинхронный анализ производительности"""
        await asyncio.sleep(0.001)

        insights = []
        perf_metrics = self.get_performance_metrics()

        if perf_metrics["success_rate"] < 90:
            insight = {
                "type": "performance_analysis",
                "issue": "low_success_rate",
                "current_rate": perf_metrics["success_rate"],
                "recommendation": (
                    "Проверить логи ошибок и улучшить обработку исключений"
                ),
                "timestamp": datetime.now().isoformat(),
                "severity": "medium",
            }
            insights.append(insight)

        if perf_metrics["memory_usage"] > 1000000:  # 1MB
            insight = {
                "type": "performance_analysis",
                "issue": "high_memory_usage",
                "current_usage": perf_metrics["memory_usage"],
                "recommendation": "Рассмотреть очистку старых данных",
                "timestamp": datetime.now().isoformat(),
                "severity": "low",
            }
            insights.append(insight)

        return insights

    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Расчет корреляции Пирсона между двумя списками значений"""
        n = len(x)
        if n != len(y) or n < 2:
            return 0.0

        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        sum_y2 = sum(y[i] ** 2 for i in range(n))

        numerator = n * sum_xy - sum_x * sum_y
        denominator = (
            (n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2)
        ) ** 0.5

        return numerator / denominator if denominator != 0 else 0.0

    def get_async_performance_metrics(self) -> Dict[str, Any]:
        """
        Получение метрик производительности асинхронных операций

        Returns:
            Dict[str, Any]: Метрики производительности
        """
        return {
            "async_execution_count": self.async_execution_count,
            "async_success_count": self.async_success_count,
            "async_error_count": self.async_error_count,
            "async_success_rate": (
                self.async_success_count / max(1, self.async_execution_count)
            )
            * 100,
            "total_async_operations": self.async_execution_count,
            "async_error_rate": (
                self.async_error_count / max(1, self.async_execution_count)
            )
            * 100,
        }


# ============================================================================
# ДОПОЛНИТЕЛЬНЫЕ УЛУЧШЕНИЯ: ЛОГИРОВАНИЕ, КЭШИРОВАНИЕ, МОНИТОРИНГ
# ============================================================================


class EnhancedSecurityAnalyticsManager(SecurityAnalyticsManager):
    """Расширенная версия менеджера с дополнительными возможностями"""

    def __init__(
        self,
        name: str = "EnhancedSecurityAnalyticsManager",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Настройка логирования
        self.logger = self._setup_enhanced_logging()

        # Кэширование
        self._cache = {}
        self._cache_ttl = {}
        self._max_cache_size = (
            config.get("max_cache_size", 1000) if config else 1000
        )

        # Мониторинг производительности
        self._performance_metrics = {}
        self._method_call_counts = {}

        # Автоматическое масштабирование
        self._load_thresholds = {
            "memory": (
                config.get("memory_threshold", 1000000) if config else 1000000
            ),
            "metrics": (
                config.get("metrics_threshold", 1000) if config else 1000
            ),
            "errors": config.get("error_threshold", 10) if config else 10,
        }

    def _setup_enhanced_logging(self) -> logging.Logger:
        """Настройка расширенного логирования"""
        logger = logging.getLogger(f"security_analytics_{self.name}")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            # Создаем обработчик для файла
            file_handler = logging.FileHandler(
                f"logs/security_analytics_{self.name}.log"
            )
            file_handler.setLevel(logging.INFO)

            # Создаем форматтер
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - "
                "%(funcName)s:%(lineno)d - %(message)s"
            )
            file_handler.setFormatter(formatter)

            logger.addHandler(file_handler)

        return logger

    def _log_operation(
        self, operation: str, details: Dict[str, Any], level: str = "info"
    ) -> None:
        """Расширенное логирование операций"""
        log_data = {
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "manager_name": self.name,
            "details": details,
        }

        if level == "info":
            self.logger.info(f"Операция {operation}: {log_data}")
        elif level == "warning":
            self.logger.warning(f"Операция {operation}: {log_data}")
        elif level == "error":
            self.logger.error(f"Операция {operation}: {log_data}")
        elif level == "debug":
            self.logger.debug(f"Операция {operation}: {log_data}")

    def _measure_performance(self, method_name: str):
        """Декоратор для измерения производительности методов"""

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time

                    # Записываем метрики производительности
                    if method_name not in self._performance_metrics:
                        self._performance_metrics[method_name] = []

                    self._performance_metrics[method_name].append(
                        {
                            "execution_time": execution_time,
                            "timestamp": datetime.now(),
                            "success": True,
                        }
                    )

                    # Подсчитываем вызовы
                    self._method_call_counts[method_name] = (
                        self._method_call_counts.get(method_name, 0) + 1
                    )

                    # Логируем операцию
                    self._log_operation(
                        f"method_execution_{method_name}",
                        {
                            "execution_time": execution_time,
                            "success": True,
                            "args_count": len(args),
                            "kwargs_count": len(kwargs),
                        },
                    )

                    return result
                except Exception as e:
                    execution_time = time.time() - start_time

                    # Записываем ошибку
                    if method_name not in self._performance_metrics:
                        self._performance_metrics[method_name] = []

                    self._performance_metrics[method_name].append(
                        {
                            "execution_time": execution_time,
                            "timestamp": datetime.now(),
                            "success": False,
                            "error": str(e),
                        }
                    )

                    # Логируем ошибку
                    self._log_operation(
                        f"method_error_{method_name}",
                        {
                            "execution_time": execution_time,
                            "error": str(e),
                            "error_type": type(e).__name__,
                        },
                        "error",
                    )

                    raise

            return wrapper

        return decorator

    @functools.lru_cache(maxsize=128)
    def get_cached_statistics(self, metric_id: str) -> Dict[str, Any]:
        """Кэшированное получение статистики"""
        if metric_id not in self.metrics:
            self.log_activity(
                f"Метрика {metric_id} не найдена для кэширования",
                "warning",
            )
            return {}

        metric = self.metrics[metric_id]
        return metric.get_statistics()

    def _check_load_and_scale(self) -> None:
        """Проверка нагрузки и автоматическое масштабирование"""
        perf_metrics = self.get_performance_metrics()

        # Проверка использования памяти
        if perf_metrics["memory_usage"] > self._load_thresholds["memory"]:
            self._log_operation(
                "auto_scaling_memory_cleanup",
                {
                    "memory_usage": perf_metrics["memory_usage"],
                    "threshold": self._load_thresholds["memory"],
                },
                "warning",
            )
            self.cleanup_old_data()

        # Проверка количества метрик
        if len(self.metrics) > self._load_thresholds["metrics"]:
            self._log_operation(
                "auto_scaling_metrics_cleanup",
                {
                    "metrics_count": len(self.metrics),
                    "threshold": self._load_thresholds["metrics"],
                },
                "warning",
            )
            # Очищаем старые метрики
            self._cleanup_old_metrics()

        # Проверка количества ошибок
        if self.error_count > self._load_thresholds["errors"]:
            self._log_operation(
                "auto_scaling_error_reset",
                {
                    "error_count": self.error_count,
                    "threshold": self._load_thresholds["errors"],
                },
                "warning",
            )
            self._reset_error_counters()

    def _cleanup_old_metrics(self) -> None:
        """Очистка старых неактивных метрик"""
        current_time = datetime.now()
        metrics_to_remove = []

        for metric_id, metric in self.metrics.items():
            # Удаляем метрики, которые не обновлялись более 24 часов
            if (current_time - metric.timestamp).total_seconds() > 86400:
                metrics_to_remove.append(metric_id)

        for metric_id in metrics_to_remove:
            self.remove_metric(metric_id)
            self._log_operation(
                "auto_cleanup_old_metric", {"metric_id": metric_id}, "info"
            )

    def _reset_error_counters(self) -> None:
        """Сброс счетчиков ошибок"""
        self.error_count = 0
        self.async_error_count = 0
        self._log_operation("error_counters_reset", {}, "info")

    def load_config_from_file(self, config_path: str) -> None:
        """Загрузка конфигурации из файла"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                if config_path.endswith(".json"):
                    config = json.load(f)
                elif config_path.endswith(".yaml") or config_path.endswith(
                    ".yml"
                ):
                    import yaml

                    config = yaml.safe_load(f)
                else:
                    raise ValueError(
                        "Неподдерживаемый формат файла конфигурации"
                    )

            # Валидация конфигурации
            validate_config_dict(config)

            # Обновление конфигурации
            self.config.update(config)

            # Обновление параметров
            self.data_retention_days = config.get(
                "data_retention_days", self.data_retention_days
            )
            self.analysis_interval = config.get(
                "analysis_interval", self.analysis_interval
            )
            self.enable_real_time = config.get(
                "enable_real_time", self.enable_real_time
            )
            self.alert_threshold = config.get(
                "alert_threshold", self.alert_threshold
            )

            self._log_operation(
                "config_loaded_from_file",
                {
                    "config_path": config_path,
                    "config_keys": list(config.keys()),
                },
                "info",
            )

        except Exception as e:
            self._log_operation(
                "config_load_error",
                {"config_path": config_path, "error": str(e)},
                "error",
            )
            raise ConfigurationError(
                f"Ошибка загрузки конфигурации: {e}"
            ) from e

    def get_enhanced_performance_metrics(self) -> Dict[str, Any]:
        """Получение расширенных метрик производительности"""
        base_metrics = self.get_performance_metrics()

        # Метрики производительности методов
        method_metrics = {}
        for method_name, calls in self._method_call_counts.items():
            if method_name in self._performance_metrics:
                perf_data = self._performance_metrics[method_name]
                if perf_data:
                    avg_time = sum(
                        p["execution_time"] for p in perf_data
                    ) / len(perf_data)
                    success_rate = (
                        sum(1 for p in perf_data if p["success"])
                        / len(perf_data)
                        * 100
                    )

                    method_metrics[method_name] = {
                        "call_count": calls,
                        "avg_execution_time": avg_time,
                        "success_rate": success_rate,
                        "total_executions": len(perf_data),
                    }

        return {
            **base_metrics,
            "method_performance": method_metrics,
            "cache_size": len(self._cache),
            "max_cache_size": self._max_cache_size,
            "load_thresholds": self._load_thresholds,
        }

    def export_enhanced_analytics(self) -> Dict[str, Any]:
        """Экспорт расширенных аналитических данных"""
        base_export = self.export_analytics()

        enhanced_data = {
            **base_export,
            "enhanced_metrics": {
                "performance": self.get_enhanced_performance_metrics(),
                "method_analytics": self._performance_metrics,
                "cache_analytics": {
                    "cache_size": len(self._cache),
                    "cache_ttl_entries": len(self._cache_ttl),
                    "max_cache_size": self._max_cache_size,
                },
                "load_balancing": {
                    "current_load": self.get_performance_metrics()[
                        "memory_usage"
                    ],
                    "thresholds": self._load_thresholds,
                    "auto_scaling_enabled": True,
                },
            },
            "logging_info": {
                "log_level": self.logger.level,
                "handlers_count": len(self.logger.handlers),
            },
        }

        self._log_operation(
            "enhanced_analytics_exported",
            {"data_size": len(str(enhanced_data))},
            "info",
        )
        return enhanced_data
