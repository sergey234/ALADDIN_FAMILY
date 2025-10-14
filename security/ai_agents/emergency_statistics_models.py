#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модели статистики для системы экстренного реагирования
Применение Single Responsibility принципа
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class EmergencyStatistics:
    """Статистика экстренных ситуаций"""
    total_events: int = 0
    resolved_events: int = 0
    pending_events: int = 0
    cancelled_events: int = 0
    resolution_rate: float = 0.0
    average_response_time: float = 0.0
    type_statistics: Dict[str, int] = field(default_factory=dict)
    severity_statistics: Dict[str, int] = field(default_factory=dict)
    time_period_statistics: Dict[str, int] = field(default_factory=dict)
    location_statistics: Dict[str, int] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EmergencyTrends:
    """Тренды экстренных ситуаций"""
    period_days: int = 7
    events_per_day: Dict[str, int] = field(default_factory=dict)
    resolution_trend: str = "stable"  # increasing, decreasing, stable
    response_time_trend: str = "stable"
    severity_trend: str = "stable"
    type_trend: str = "stable"
    peak_hours: List[int] = field(default_factory=list)
    peak_days: List[str] = field(default_factory=list)
    risk_level_trend: str = "stable"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EmergencyPerformanceMetrics:
    """Метрики производительности системы"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    success_rate: float = 0.0
    average_response_time: float = 0.0
    max_response_time: float = 0.0
    min_response_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    active_connections: int = 0
    error_rate: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EmergencyRiskMetrics:
    """Метрики рисков экстренных ситуаций"""
    total_risk_score: float = 0.0
    average_risk_score: float = 0.0
    high_risk_events: int = 0
    critical_risk_events: int = 0
    risk_distribution: Dict[str, int] = field(default_factory=dict)
    risk_trend: str = "stable"
    most_risky_types: List[str] = field(default_factory=list)
    most_risky_locations: List[str] = field(default_factory=list)
    risk_recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EmergencyNotificationMetrics:
    """Метрики уведомлений"""
    total_notifications: int = 0
    successful_notifications: int = 0
    failed_notifications: int = 0
    success_rate: float = 0.0
    channel_statistics: Dict[str, Dict[str, int]] = field(default_factory=dict)
    average_delivery_time: float = 0.0
    retry_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EmergencyServiceMetrics:
    """Метрики служб экстренного реагирования"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    success_rate: float = 0.0
    average_response_time: float = 0.0
    service_statistics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    most_called_service: Optional[str] = None
    least_called_service: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EmergencySystemHealth:
    """Состояние здоровья системы"""
    overall_health: str = "good"  # excellent, good, fair, poor, critical
    component_health: Dict[str, str] = field(default_factory=dict)
    performance_health: str = "good"
    security_health: str = "good"
    reliability_health: str = "good"
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    uptime_percentage: float = 100.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EmergencyReport:
    """Отчет по экстренным ситуациям"""
    report_id: str
    period_start: datetime
    period_end: datetime
    statistics: EmergencyStatistics
    trends: EmergencyTrends
    performance: EmergencyPerformanceMetrics
    risks: EmergencyRiskMetrics
    notifications: EmergencyNotificationMetrics
    services: EmergencyServiceMetrics
    system_health: EmergencySystemHealth
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)


class EmergencyMetricsCalculator:
    """Калькулятор метрик экстренных ситуаций"""

    @staticmethod
    def calculate_resolution_rate(resolved: int, total: int) -> float:
        """Рассчитать процент разрешения"""
        if total == 0:
            return 0.0
        return (resolved / total) * 100

    @staticmethod
    def calculate_success_rate(successful: int, total: int) -> float:
        """Рассчитать процент успешности"""
        if total == 0:
            return 0.0
        return (successful / total) * 100

    @staticmethod
    def calculate_average_time(times: List[float]) -> float:
        """Рассчитать среднее время"""
        if not times:
            return 0.0
        return sum(times) / len(times)

    @staticmethod
    def calculate_trend(current_values: List[float], previous_values: List[float]) -> str:
        """Рассчитать тренд"""
        if not current_values or not previous_values:
            return "stable"

        current_avg = sum(current_values) / len(current_values)
        previous_avg = sum(previous_values) / len(previous_values)

        change_percent = ((current_avg - previous_avg) / previous_avg) * 100

        if change_percent > 5:
            return "increasing"
        elif change_percent < -5:
            return "decreasing"
        else:
            return "stable"

    @staticmethod
    def calculate_health_score(metrics: EmergencyPerformanceMetrics) -> str:
        """Рассчитать оценку здоровья системы"""
        if metrics.success_rate >= 99 and metrics.average_response_time <= 1.0:
            return "excellent"
        elif metrics.success_rate >= 95 and metrics.average_response_time <= 2.0:
            return "good"
        elif metrics.success_rate >= 90 and metrics.average_response_time <= 5.0:
            return "fair"
        elif metrics.success_rate >= 80 and metrics.average_response_time <= 10.0:
            return "poor"
        else:
            return "critical"
