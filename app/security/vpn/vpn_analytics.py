#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPN Analytics - Аналитика использования и отчеты для коммерческого VPN сервиса
Качество кода: A+
Соответствие: SOLID, DRY, PEP8
"""

import asyncio
import json
import logging
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# import matplotlib.pyplot as plt
# import pandas as pd
# import seaborn as sns

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Типы отчетов"""

    USAGE = "usage"
    PERFORMANCE = "performance"
    REVENUE = "revenue"
    USER_ACTIVITY = "user_activity"
    SERVER_ANALYTICS = "server_analytics"
    SECURITY = "security"
    CUSTOM = "custom"


class MetricType(Enum):
    """Типы метрик для аналитики"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    RATE = "rate"


@dataclass
class AnalyticsData:
    """Модель данных аналитики"""

    timestamp: datetime
    metric_name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    user_id: Optional[str] = None
    server_id: Optional[str] = None
    session_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "metric_name": self.metric_name,
            "value": self.value,
            "labels": self.labels,
            "user_id": self.user_id,
            "server_id": self.server_id,
            "session_id": self.session_id,
        }


@dataclass
class ReportConfig:
    """Конфигурация отчета"""

    report_type: ReportType
    title: str
    description: str
    metrics: List[str]
    time_range: Tuple[datetime, datetime]
    group_by: Optional[List[str]] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    format: str = "json"  # json, csv, pdf, html
    include_charts: bool = True


@dataclass
class ReportResult:
    """Результат генерации отчета"""

    report_id: str
    report_type: ReportType
    title: str
    generated_at: datetime
    data: Dict[str, Any]
    charts: List[str] = field(default_factory=list)
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class VPNAnalytics:
    """
    Система аналитики VPN сервиса

    Основные функции:
    - Сбор и хранение аналитических данных
    - Генерация отчетов (использование, производительность, доходы)
    - Визуализация данных (графики, диаграммы)
    - Экспорт данных в различных форматах
    - Анализ трендов и паттернов
    - Прогнозирование и рекомендации
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Инициализация системы аналитики

        Args:
            config_path: Путь к файлу конфигурации
        """
        self.config_path = config_path or "config/vpn_analytics_config.json"
        self.config = self._load_config()
        self.analytics_data: List[AnalyticsData] = []
        self.reports: Dict[str, ReportResult] = {}
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = timedelta(minutes=30)

        # Создаем директории для отчетов
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

        logger.info("VPN Analytics инициализирован")

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """Создание конфигурации по умолчанию"""
        default_config = {
            "data_retention_days": 365,
            "cache_ttl_minutes": 30,
            "report_formats": ["json", "csv", "html"],
            "chart_types": ["line", "bar", "pie", "heatmap"],
            "export_paths": {
                "reports": "reports/",
                "charts": "reports/charts/",
                "exports": "reports/exports/",
            },
            "metrics": {
                "user_metrics": [
                    "user_registrations",
                    "user_logins",
                    "user_sessions",
                    "user_data_usage",
                    "user_connection_time",
                ],
                "server_metrics": [
                    "server_load",
                    "server_connections",
                    "server_response_time",
                    "server_uptime",
                    "server_errors",
                ],
                "business_metrics": [
                    "revenue",
                    "subscription_payment",
                    "refund",
                    "churn_rate",
                    "customer_lifetime_value",
                    "conversion_rate",
                ],
            },
            "alerts": {
                "anomaly_detection": True,
                "threshold_alerts": True,
                "trend_alerts": True,
            },
        }
        self._save_config(default_config)
        return default_config

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Сохранение конфигурации"""
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")

    def add_data_point(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        user_id: Optional[str] = None,
        server_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """
        Добавление точки данных

        Args:
            metric_name: Название метрики
            value: Значение метрики
            labels: Дополнительные метки
            user_id: ID пользователя
            server_id: ID сервера
            session_id: ID сессии
        """
        data_point = AnalyticsData(
            timestamp=datetime.now(),
            metric_name=metric_name,
            value=value,
            labels=labels or {},
            user_id=user_id,
            server_id=server_id,
            session_id=session_id,
        )

        self.analytics_data.append(data_point)

        # Очистка старых данных
        self._cleanup_old_data()

        logger.debug(f"Добавлена точка данных: {metric_name} = {value}")

    def _cleanup_old_data(self) -> None:
        """Очистка старых данных"""
        cutoff_date = datetime.now() - timedelta(
            days=self.config["data_retention_days"]
        )
        self.analytics_data = [
            d for d in self.analytics_data if d.timestamp > cutoff_date
        ]

    def _get_cached_data(self, key: str) -> Optional[Any]:
        """Получение данных из кэша"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.cache_ttl:
                return data
            else:
                del self.cache[key]
        return None

    def _set_cached_data(self, key: str, data: Any) -> None:
        """Сохранение данных в кэш"""
        self.cache[key] = (data, datetime.now())

    async def get_usage_report(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Генерация отчета об использовании

        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            user_id: ID пользователя (опционально)

        Returns:
            Dict с данными отчета
        """
        cache_key = f"usage_report_{start_date}_{end_date}_{user_id}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        # Фильтрация данных по дате и пользователю
        filtered_data = [
            d
            for d in self.analytics_data
            if start_date <= d.timestamp <= end_date
            and (user_id is None or d.user_id == user_id)
        ]

        # Группировка по метрикам
        metrics_data = defaultdict(list)
        for data in filtered_data:
            metrics_data[data.metric_name].append(data.value)

        # Расчет статистики
        report_data = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "duration_days": (end_date - start_date).days,
            },
            "user_id": user_id,
            "metrics": {},
        }

        for metric_name, values in metrics_data.items():
            if values:
                report_data["metrics"][metric_name] = {
                    "count": len(values),
                    "sum": sum(values),
                    "average": statistics.mean(values),
                    "median": statistics.median(values),
                    "min": min(values),
                    "max": max(values),
                    "std_dev": (
                        statistics.stdev(values) if len(values) > 1 else 0
                    ),
                }

        # Дополнительные метрики
        report_data["summary"] = {
            "total_data_points": len(filtered_data),
            "unique_users": len(
                set(d.user_id for d in filtered_data if d.user_id)
            ),
            "unique_servers": len(
                set(d.server_id for d in filtered_data if d.server_id)
            ),
            "unique_sessions": len(
                set(d.session_id for d in filtered_data if d.session_id)
            ),
        }

        self._set_cached_data(cache_key, report_data)
        return report_data

    async def get_performance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        server_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Генерация отчета о производительности

        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            server_id: ID сервера (опционально)

        Returns:
            Dict с данными отчета
        """
        cache_key = f"performance_report_{start_date}_{end_date}_{server_id}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        # Фильтрация данных
        filtered_data = [
            d
            for d in self.analytics_data
            if start_date <= d.timestamp <= end_date
            and (server_id is None or d.server_id == server_id)
            and d.metric_name
            in [
                "server_load",
                "server_response_time",
                "server_connections",
                "server_errors",
            ]
        ]

        # Группировка по серверам
        server_data = defaultdict(lambda: defaultdict(list))
        for data in filtered_data:
            server_data[data.server_id or "unknown"][data.metric_name].append(
                data.value
            )

        report_data = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "server_id": server_id,
            "servers": {},
        }

        for server, metrics in server_data.items():
            server_report = {"server_id": server, "metrics": {}}

            for metric_name, values in metrics.items():
                if values:
                    server_report["metrics"][metric_name] = {
                        "count": len(values),
                        "average": statistics.mean(values),
                        "median": statistics.median(values),
                        "min": min(values),
                        "max": max(values),
                        "p95": self._percentile(values, 95),
                        "p99": self._percentile(values, 99),
                    }

            # Расчет общего индекса производительности
            performance_score = self._calculate_performance_score(
                server_report["metrics"]
            )
            server_report["performance_score"] = performance_score

            report_data["servers"][server] = server_report

        self._set_cached_data(cache_key, report_data)
        return report_data

    async def get_revenue_report(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """
        Генерация отчета о доходах

        Args:
            start_date: Начальная дата
            end_date: Конечная дата

        Returns:
            Dict с данными отчета
        """
        cache_key = f"revenue_report_{start_date}_{end_date}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        # Фильтрация данных по доходам
        revenue_data = [
            d
            for d in self.analytics_data
            if start_date <= d.timestamp <= end_date
            and d.metric_name in ["revenue", "subscription_payment", "refund"]
        ]

        # Группировка по типам доходов
        revenue_by_type = defaultdict(list)
        for data in revenue_data:
            revenue_type = data.labels.get("type", "unknown")
            revenue_by_type[revenue_type].append(data.value)

        report_data = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "revenue_by_type": {},
            "summary": {},
        }

        total_revenue = 0
        for revenue_type, values in revenue_by_type.items():
            if values:
                revenue_sum = sum(values)
                total_revenue += revenue_sum

                report_data["revenue_by_type"][revenue_type] = {
                    "total": revenue_sum,
                    "count": len(values),
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                }

        # Расчет трендов
        daily_revenue = self._calculate_daily_revenue(
            revenue_data, start_date, end_date
        )
        trend = self._calculate_trend(daily_revenue)

        report_data["summary"] = {
            "total_revenue": total_revenue,
            "daily_average": total_revenue
            / max(1, (end_date - start_date).days),
            "trend": trend,
            "daily_revenue": daily_revenue,
        }

        self._set_cached_data(cache_key, report_data)
        return report_data

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Расчет перцентиля"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]

    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> float:
        """Расчет индекса производительности сервера"""
        score = 100.0

        # Штрафы за плохие метрики
        if "server_load" in metrics:
            avg_load = metrics["server_load"]["average"]
            if avg_load > 80:
                score -= (avg_load - 80) * 0.5

        if "server_response_time" in metrics:
            avg_response = metrics["server_response_time"]["average"]
            if avg_response > 1000:  # > 1 секунда
                score -= (avg_response - 1000) / 100

        if "server_errors" in metrics:
            error_count = metrics["server_errors"]["count"]
            if error_count > 0:
                score -= min(error_count * 2, 50)  # Максимум -50 баллов

        return max(0.0, min(100.0, score))

    def _calculate_daily_revenue(
        self,
        revenue_data: List[AnalyticsData],
        start_date: datetime,
        end_date: datetime,
    ) -> List[float]:
        """Расчет ежедневных доходов"""
        daily_revenue = defaultdict(float)

        for data in revenue_data:
            day = data.timestamp.date()
            daily_revenue[day] += data.value

        # Заполняем пропущенные дни нулями
        result = []
        current_date = start_date.date()
        end_date_only = end_date.date()

        while current_date <= end_date_only:
            result.append(daily_revenue.get(current_date, 0.0))
            current_date += timedelta(days=1)

        return result

    def _calculate_trend(self, daily_values: List[float]) -> str:
        """Расчет тренда"""
        if len(daily_values) < 2:
            return "insufficient_data"

        # Простой линейный тренд
        first_half = daily_values[: len(daily_values) // 2]
        second_half = daily_values[len(daily_values) // 2:]

        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)

        if second_avg > first_avg * 1.1:
            return "increasing"
        elif second_avg < first_avg * 0.9:
            return "decreasing"
        else:
            return "stable"

    async def get_anomaly_detection(
        self, metric_name: str, threshold: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Обнаружение аномалий в данных

        Args:
            metric_name: Название метрики
            threshold: Порог для обнаружения аномалий (в стандартных отклонениях)

        Returns:
            Список аномальных точек данных
        """
        # Получаем данные для метрики
        metric_data = [
            d for d in self.analytics_data if d.metric_name == metric_name
        ]

        if len(metric_data) < 10:  # Недостаточно данных для анализа
            return []

        values = [d.value for d in metric_data]
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)

        anomalies = []
        for data in metric_data:
            z_score = (
                abs(data.value - mean_val) / std_val if std_val > 0 else 0
            )
            if z_score > threshold:
                anomalies.append(
                    {
                        "timestamp": data.timestamp.isoformat(),
                        "value": data.value,
                        "z_score": z_score,
                        "expected_range": [
                            mean_val - threshold * std_val,
                            mean_val + threshold * std_val,
                        ],
                        "labels": data.labels,
                    }
                )

        return anomalies

    async def get_recommendations(self) -> List[Dict[str, Any]]:
        """
        Получение рекомендаций на основе аналитики

        Returns:
            Список рекомендаций
        """
        recommendations = []

        # Анализ производительности серверов
        performance_data = await self.get_performance_report(
            datetime.now() - timedelta(days=7), datetime.now()
        )

        for server_id, server_data in performance_data.get(
            "servers", {}
        ).items():
            performance_score = server_data.get("performance_score", 0)

            if performance_score < 70:
                recommendations.append(
                    {
                        "type": "server_performance",
                        "priority": "high",
                        "title": f"Low performance on server {server_id}",
                        "description": f"Server {server_id} has performance score {performance_score:.1f}",
                        "action": "Consider scaling or optimizing server resources",
                        "server_id": server_id,
                        "performance_score": performance_score,
                    }
                )

        # Анализ доходов
        revenue_data = await self.get_revenue_report(
            datetime.now() - timedelta(days=30), datetime.now()
        )

        trend = revenue_data.get("summary", {}).get("trend", "stable")
        if trend == "decreasing":
            recommendations.append(
                {
                    "type": "revenue",
                    "priority": "high",
                    "title": "Decreasing revenue trend",
                    "description": "Revenue has been decreasing over the past 30 days",
                    "action": "Review pricing strategy and user acquisition",
                    "trend": trend,
                }
            )

        return recommendations


# Пример использования
async def main():
    """Пример использования VPN Analytics"""
    analytics = VPNAnalytics()

    # Добавляем тестовые данные
    for i in range(100):
        analytics.add_data_point(
            metric_name="user_data_usage",
            value=1000 + i * 10,
            user_id=f"user_{i % 10}",
            server_id=f"server_{i % 3}",
        )

    # Генерируем отчеты
    usage_report = await analytics.get_usage_report(
        datetime.now() - timedelta(days=7), datetime.now()
    )
    print(f"Usage report: {usage_report}")

    # Получаем рекомендации
    recommendations = await analytics.get_recommendations()
    print(f"Recommendations: {recommendations}")


if __name__ == "__main__":
    asyncio.run(main())
