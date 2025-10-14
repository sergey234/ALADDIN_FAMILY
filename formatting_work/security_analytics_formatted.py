# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Security Analytics Module
Модуль аналитики безопасности для системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-01
"""

import math
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import ComponentStatus, SecurityBase


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

    def update_value(
        self, new_value: float, timestamp: Optional[datetime] = None
    ):
        """Обновление значения метрики"""
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
                    f"Превышен максимальный порог: {self.value} > {threshold_value}"
                )
            elif threshold_type == "min" and self.value < threshold_value:
                alerts.append(
                    f"Ниже минимального порога: {self.value} < {threshold_value}"
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
                f"Менеджер аналитики безопасности {self.name} успешно инициализирован"
            )
            return True

        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка инициализации менеджера аналитики безопасности {self.name}: {e}",
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

            self.log_activity(f"Добавлена метрика безопасности: {metric.name}")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка добавления метрики: {e}", "error")
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

        except Exception as e:
            self.log_activity(f"Ошибка обновления метрики: {e}", "error")
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
                    "Провести дополнительный анализ безопасности"
                )

            self.analyses_conducted += 1
            self.log_activity(
                f"Анализ угроз завершен: уровень {analysis_result['threat_level']}"
            )

            return analysis_result

        except Exception as e:
            self.log_activity(f"Ошибка анализа угроз: {e}", "error")
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
                f"Оценка рисков завершена: общий риск {risk_assessment['overall_risk_score']:.2f}"
            )

            return risk_assessment

        except Exception as e:
            self.log_activity(f"Ошибка оценки рисков: {e}", "error")
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
                f"Анализ производительности завершен: здоровье {performance_analysis['system_health']}"
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
                            "expected_range": f"{mean_value - 2*std_dev:.2f} - {mean_value + 2*std_dev:.2f}",
                            "z_score": z_score,
                            "timestamp": datetime.now().isoformat(),
                            "severity": "high" if z_score > 3.0 else "medium",
                        }
                        anomalies.append(anomaly)

            self.anomalies_detected += len(anomalies)

            if anomalies:
                self.log_activity(f"Обнаружено {len(anomalies)} аномалий")

            return anomalies

        except Exception as e:
            self.log_activity(f"Ошибка обнаружения аномалий: {e}", "error")
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
                            "description": f"{metric.name} показывает {trend} на {abs(change_percent):.1f}%",
                            "timestamp": datetime.now().isoformat(),
                            "category": metric.tags.get("category", "general"),
                        }
                        insights.append(insight)

            self.insights_generated += len(insights)

            if insights:
                self.log_activity(f"Сгенерировано {len(insights)} инсайтов")

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
            self.log_activity(f"Ошибка получения данных панели: {e}", "error")
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
            self.log_activity(f"Ошибка получения трендов: {e}", "error")
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
                f"Менеджер аналитики безопасности {self.name} успешно запущен"
            )
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка запуска менеджера аналитики безопасности {self.name}: {e}",
                "error",
            )
            return False

    def stop(self) -> bool:
        """Остановка менеджера аналитики безопасности"""
        try:
            self.log_activity(
                f"Остановка менеджера аналитики безопасности {self.name}"
            )

            # Остановка аналитики в реальном времени
            self.enable_real_time = False

            self.status = ComponentStatus.STOPPED
            self.log_activity(
                f"Менеджер аналитики безопасности {self.name} успешно остановлен"
            )
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка остановки менеджера аналитики безопасности {self.name}: {e}",
                "error",
            )
            return False
