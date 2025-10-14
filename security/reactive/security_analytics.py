"""
SecurityAnalytics - Анализ эффективности защиты системы
Уровень 3: Реактивная защита
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Union

from core.base import SecurityBase


class AnalyticsType(Enum):
    """Типы аналитики"""

    PERFORMANCE = "performance"
    SECURITY = "security"
    FAMILY = "family"
    THREAT = "threat"
    COMPLIANCE = "compliance"


class MetricType(Enum):
    """Типы метрик"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertLevel(Enum):
    """Уровни оповещений"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"
    ERROR = "error"


@dataclass
class SecurityMetric:
    """Метрика безопасности"""

    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    description: str = ""


@dataclass
class AnalyticsReport:
    """Отчет аналитики"""

    report_id: str
    report_type: AnalyticsType
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    metrics: List[SecurityMetric] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    alerts: List[Dict[str, Any]] = field(default_factory=list)
    family_impact: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Метрики производительности"""

    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_latency: float
    response_time: float
    throughput: float
    error_rate: float
    availability: float


@dataclass
class SecurityMetrics:
    """Метрики безопасности"""

    threats_detected: int
    threats_blocked: int
    false_positives: int
    false_negatives: int
    security_score: float
    compliance_score: float
    risk_level: str
    protection_coverage: float


@dataclass
class FamilyMetrics:
    """Семейные метрики"""

    total_family_members: int
    active_users: int
    parental_controls_active: int
    child_activities_monitored: int
    elderly_protection_active: int
    family_security_score: float
    age_appropriate_protection: Dict[str, float]


class SecurityAnalytics(SecurityBase):
    """Сервис аналитики безопасности"""

    def __init__(self) -> None:
        super().__init__("SecurityAnalytics")
        self.service_name = "SecurityAnalytics"
        self.analytics_type = AnalyticsType.SECURITY

        # Метрики
        self.performance_metrics = PerformanceMetrics(
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_usage=0.0,
            network_latency=0.0,
            response_time=0.0,
            throughput=0.0,
            error_rate=0.0,
            availability=100.0,
        )

        self.security_metrics = SecurityMetrics(
            threats_detected=0,
            threats_blocked=0,
            false_positives=0,
            false_negatives=0,
            security_score=0.0,
            compliance_score=0.0,
            risk_level="low",
            protection_coverage=0.0,
        )

        self.family_metrics = FamilyMetrics(
            total_family_members=0,
            active_users=0,
            parental_controls_active=0,
            child_activities_monitored=0,
            elderly_protection_active=0,
            family_security_score=0.0,
            age_appropriate_protection={},
        )

        # История аналитики
        self.analytics_history: List[AnalyticsReport] = []
        self.metrics_history: List[SecurityMetric] = []

        # Настройки
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "error_rate": 5.0,
            "security_score": 70.0,
            "family_security_score": 75.0,
        }

        self._initialize_analytics_rules()
        self._setup_family_analytics()

    def _initialize_analytics_rules(self) -> None:
        """Инициализация правил аналитики"""
        self.analytics_rules = {
            "performance_monitoring": {
                "enabled": True,
                "interval": 300,  # 5 минут
                "metrics": ["cpu", "memory", "disk", "network"],
            },
            "security_monitoring": {
                "enabled": True,
                "interval": 60,  # 1 минута
                "metrics": ["threats", "compliance", "risk"],
            },
            "family_monitoring": {
                "enabled": True,
                "interval": 600,  # 10 минут
                "metrics": ["users", "controls", "activities"],
            },
        }

    def _setup_family_analytics(self) -> None:
        """Настройка семейной аналитики"""
        self.family_analytics = {
            "age_groups": {
                "children": {"min_age": 0, "max_age": 17, "protection_level": "high"},
                "adults": {"min_age": 18, "max_age": 64, "protection_level": "medium"},
                "elderly": {"min_age": 65, "max_age": 100, "protection_level": "high"},
            },
            "protection_categories": {
                "content_filtering": "content",
                "time_limits": "time",
                "location_tracking": "location",
                "social_engineering": "social",
                "malware_protection": "malware",
            },
        }

    def collect_performance_metrics(self) -> PerformanceMetrics:
        """Сбор метрик производительности"""
        try:
            # Симуляция сбора метрик
            try:
                import psutil

                self.performance_metrics.cpu_usage = psutil.cpu_percent()
                self.performance_metrics.memory_usage = psutil.virtual_memory().percent
                self.performance_metrics.disk_usage = psutil.disk_usage("/").percent

                # Сетевые метрики
                net_io = psutil.net_io_counters()
                self.performance_metrics.throughput = net_io.bytes_sent + net_io.bytes_recv
            except ImportError:
                # Fallback если psutil не установлен
                self.performance_metrics.cpu_usage = 0.0
                self.performance_metrics.memory_usage = 0.0
                self.performance_metrics.disk_usage = 0.0
                self.performance_metrics.throughput = 0.0

            # Логирование
            self.add_security_event(
                event_type="performance_metrics_collected",
                description="Собраны метрики производительности",
                severity="info",
                source="SecurityAnalytics",
                metadata={
                    "cpu_usage": self.performance_metrics.cpu_usage,
                    "memory_usage": self.performance_metrics.memory_usage,
                    "disk_usage": self.performance_metrics.disk_usage,
                },
            )

            return self.performance_metrics

        except Exception as e:
            self.add_security_event(
                event_type="performance_metrics_error",
                description=f"Ошибка сбора метрик производительности: {str(e)}",
                severity="error",
                source="SecurityAnalytics",
            )
            return self.performance_metrics

    def collect_security_metrics(self) -> SecurityMetrics:
        """Сбор метрик безопасности"""
        try:
            # Анализ событий безопасности
            security_events = self.get_security_events()

            threats_detected = len([e for e in security_events if e.get("event_type") == "threat_detected"])
            threats_blocked = len([e for e in security_events if e.get("event_type") == "threat_blocked"])

            # Расчет показателей
            if threats_detected > 0:
                self.security_metrics.threats_detected = threats_detected
                self.security_metrics.threats_blocked = threats_blocked
                self.security_metrics.security_score = (threats_blocked / threats_detected) * 100
            else:
                self.security_metrics.security_score = 100.0

            # Определение уровня риска
            if self.security_metrics.security_score >= 90:
                self.security_metrics.risk_level = "low"
            elif self.security_metrics.security_score >= 70:
                self.security_metrics.risk_level = "medium"
            else:
                self.security_metrics.risk_level = "high"

            # Логирование
            self.add_security_event(
                event_type="security_metrics_collected",
                description="Собраны метрики безопасности",
                severity="info",
                source="SecurityAnalytics",
                metadata={
                    "threats_detected": threats_detected,
                    "threats_blocked": threats_blocked,
                    "security_score": self.security_metrics.security_score,
                    "risk_level": self.security_metrics.risk_level,
                },
            )

            return self.security_metrics

        except Exception as e:
            self.add_security_event(
                event_type="security_metrics_error",
                description=f"Ошибка сбора метрик безопасности: {str(e)}",
                severity="error",
                source="SecurityAnalytics",
            )
            return self.security_metrics

    def collect_family_metrics(self) -> FamilyMetrics:
        """Сбор семейных метрик"""
        try:
            # Анализ семейных событий
            family_events = [e for e in self.get_security_events() if "family" in e.get("event_type", "")]

            # Подсчет активных пользователей
            active_users = len(
                set(
                    [
                        e.get("metadata", {}).get("user_id", "")
                        for e in family_events
                        if e.get("metadata", {}).get("user_id")
                    ]
                )
            )

            # Подсчет активных родительских контролей
            parental_controls = len([e for e in family_events if "parental" in e.get("event_type", "")])

            # Подсчет мониторинга детской активности
            child_activities = len([e for e in family_events if "child" in e.get("event_type", "")])

            # Подсчет защиты пожилых
            elderly_protection = len([e for e in family_events if "elderly" in e.get("event_type", "")])

            # Расчет семейного показателя безопасности
            total_family_events = len(family_events)
            if total_family_events > 0:
                self.family_metrics.family_security_score = (
                    (parental_controls + child_activities + elderly_protection) / total_family_events * 100
                )
            else:
                self.family_metrics.family_security_score = 100.0

            # Обновление метрик
            self.family_metrics.active_users = active_users
            self.family_metrics.parental_controls_active = parental_controls
            self.family_metrics.child_activities_monitored = child_activities
            self.family_metrics.elderly_protection_active = elderly_protection

            # Логирование
            self.add_security_event(
                event_type="family_metrics_collected",
                description="Собраны семейные метрики",
                severity="info",
                source="SecurityAnalytics",
                metadata={
                    "active_users": active_users,
                    "parental_controls": parental_controls,
                    "child_activities": child_activities,
                    "elderly_protection": elderly_protection,
                    "family_security_score": self.family_metrics.family_security_score,
                },
            )

            return self.family_metrics

        except Exception as e:
            self.add_security_event(
                event_type="family_metrics_error",
                description=f"Ошибка сбора семейных метрик: {str(e)}",
                severity="error",
                source="SecurityAnalytics",
            )
            return self.family_metrics

    def generate_analytics_report(
        self, report_type: AnalyticsType, period_hours: int = 24
    ) -> Union[AnalyticsReport, None]:
        """Генерация отчета аналитики"""
        try:
            report_id = f"analytics_{report_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            period_end = datetime.now()
            period_start = period_end - timedelta(hours=period_hours)

            # Сбор метрик
            metrics: Any = None
            if report_type == AnalyticsType.PERFORMANCE:
                metrics = self.collect_performance_metrics()
            elif report_type == AnalyticsType.SECURITY:
                metrics = self.collect_security_metrics()
            elif report_type == AnalyticsType.FAMILY:
                metrics = self.collect_family_metrics()

            # Создание отчета
            report = AnalyticsReport(
                report_id=report_id,
                report_type=report_type,
                generated_at=datetime.now(),
                period_start=period_start,
                period_end=period_end,
                metrics=[],
                insights=[],
                recommendations=[],
                alerts=[],
                family_impact={},
            )

            # Генерация инсайтов
            insights = self._generate_insights(report_type, metrics)
            report.insights = insights

            # Генерация рекомендаций
            recommendations = self._generate_recommendations(report_type, metrics)
            report.recommendations = recommendations

            # Проверка на оповещения
            alerts = self._check_alerts(report_type, metrics)
            report.alerts = alerts

            # Анализ семейного воздействия
            family_impact = self._analyze_family_impact(report_type, metrics)
            report.family_impact = family_impact

            # Сохранение отчета
            self.analytics_history.append(report)

            # Логирование
            self.add_security_event(
                event_type="analytics_report_generated",
                description=f"Сгенерирован отчет аналитики {report_id}",
                severity="info",
                source="SecurityAnalytics",
                metadata={
                    "report_id": report_id,
                    "report_type": report_type.value,
                    "period_hours": period_hours,
                    "insights_count": len(insights),
                    "recommendations_count": len(recommendations),
                    "alerts_count": len(alerts),
                },
            )

            return report

        except Exception as e:
            self.add_security_event(
                event_type="analytics_report_error",
                description=f"Ошибка генерации отчета аналитики: {str(e)}",
                severity="error",
                source="SecurityAnalytics",
            )
            return None

    def _generate_insights(self, report_type: AnalyticsType, metrics: Any) -> List[str]:
        """Генерация инсайтов"""
        insights = []

        try:
            if report_type == AnalyticsType.PERFORMANCE:
                if hasattr(metrics, "cpu_usage") and metrics.cpu_usage > 80:
                    insights.append("Высокая загрузка CPU может влиять на производительность системы")
                if hasattr(metrics, "memory_usage") and metrics.memory_usage > 85:
                    insights.append("Высокое использование памяти может замедлять работу")
                if hasattr(metrics, "error_rate") and metrics.error_rate > 5:
                    insights.append("Повышенный уровень ошибок требует внимания")

            elif report_type == AnalyticsType.SECURITY:
                if hasattr(metrics, "security_score") and metrics.security_score < 70:
                    insights.append("Низкий показатель безопасности требует улучшения")
                if hasattr(metrics, "threats_detected") and metrics.threats_detected > 10:
                    insights.append("Обнаружено повышенное количество угроз")
                if hasattr(metrics, "risk_level") and metrics.risk_level == "high":
                    insights.append("Высокий уровень риска требует немедленных действий")

            elif report_type == AnalyticsType.FAMILY:
                if hasattr(metrics, "family_security_score") and metrics.family_security_score < 75:
                    insights.append("Семейная безопасность требует улучшения")
                if hasattr(metrics, "active_users") and metrics.active_users > 5:
                    insights.append("Высокая активность пользователей требует мониторинга")
                if hasattr(metrics, "parental_controls_active") and not metrics.parental_controls_active:
                    insights.append("Родительские контроли не активны")

            # Общие инсайты
            if not insights:
                insights.append("Система работает стабильно")

        except Exception as e:
            insights.append(f"Ошибка генерации инсайтов: {str(e)}")

        return insights

    def _generate_recommendations(self, report_type: AnalyticsType, metrics: Any) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []

        try:
            if report_type == AnalyticsType.PERFORMANCE:
                if hasattr(metrics, "cpu_usage") and metrics.cpu_usage > 80:
                    recommendations.append("Оптимизировать процессы для снижения загрузки CPU")
                if hasattr(metrics, "memory_usage") and metrics.memory_usage > 85:
                    recommendations.append("Увеличить объем памяти или оптимизировать использование")
                if hasattr(metrics, "error_rate") and metrics.error_rate > 5:
                    recommendations.append("Исследовать и исправить источники ошибок")

            elif report_type == AnalyticsType.SECURITY:
                if hasattr(metrics, "security_score") and metrics.security_score < 70:
                    recommendations.append("Усилить меры безопасности")
                if hasattr(metrics, "threats_detected") and metrics.threats_detected > 10:
                    recommendations.append("Обновить правила обнаружения угроз")
                if hasattr(metrics, "risk_level") and metrics.risk_level == "high":
                    recommendations.append("Немедленно принять меры по снижению рисков")

            elif report_type == AnalyticsType.FAMILY:
                if hasattr(metrics, "family_security_score") and metrics.family_security_score < 75:
                    recommendations.append("Улучшить семейные меры безопасности")
                if hasattr(metrics, "parental_controls_active") and not metrics.parental_controls_active:
                    recommendations.append("Активировать родительские контроли")
                if hasattr(metrics, "elderly_protection_active") and not metrics.elderly_protection_active:
                    recommendations.append("Активировать защиту пожилых")

            # Общие рекомендации
            if not recommendations:
                recommendations.append("Продолжать мониторинг системы")

        except Exception as e:
            recommendations.append(f"Ошибка генерации рекомендаций: {str(e)}")

        return recommendations

    def _check_alerts(self, report_type: AnalyticsType, metrics: Any) -> List[Dict[str, Any]]:
        """Проверка на оповещения"""
        alerts = []

        try:
            if report_type == AnalyticsType.PERFORMANCE:
                if hasattr(metrics, "cpu_usage") and metrics.cpu_usage > self.alert_thresholds["cpu_usage"]:
                    alerts.append(
                        {
                            "level": AlertLevel.WARNING.value,
                            "message": f"Высокая загрузка CPU: {metrics.cpu_usage}%",
                            "metric": "cpu_usage",
                            "value": metrics.cpu_usage,
                            "threshold": self.alert_thresholds["cpu_usage"],
                        }
                    )

            elif report_type == AnalyticsType.SECURITY:
                if (
                    hasattr(metrics, "security_score")
                    and metrics.security_score < self.alert_thresholds["security_score"]
                ):
                    alerts.append(
                        {
                            "level": AlertLevel.CRITICAL.value,
                            "message": f"Низкий показатель безопасности: {metrics.security_score}%",
                            "metric": "security_score",
                            "value": metrics.security_score,
                            "threshold": self.alert_thresholds["security_score"],
                        }
                    )

            elif report_type == AnalyticsType.FAMILY:
                if (
                    hasattr(metrics, "family_security_score")
                    and metrics.family_security_score < self.alert_thresholds["family_security_score"]
                ):
                    alerts.append(
                        {
                            "level": AlertLevel.WARNING.value,
                            "message": f"Низкий семейный показатель безопасности: {metrics.family_security_score}%",
                            "metric": "family_security_score",
                            "value": metrics.family_security_score,
                            "threshold": self.alert_thresholds["family_security_score"],
                        }
                    )

        except Exception as e:
            alerts.append(
                {
                    "level": AlertLevel.ERROR.value,
                    "message": f"Ошибка проверки оповещений: {str(e)}",
                    "metric": "error",
                    "value": 0,
                    "threshold": 0,
                }
            )

        return alerts

    def _analyze_family_impact(self, report_type: AnalyticsType, metrics: Any) -> Dict[str, Any]:
        """Анализ семейного воздействия"""
        family_impact = {}

        try:
            if report_type == AnalyticsType.FAMILY:
                family_impact = {
                    "total_family_members": getattr(metrics, "total_family_members", 0),
                    "active_users": getattr(metrics, "active_users", 0),
                    "security_score": getattr(metrics, "family_security_score", 0),
                    "protection_coverage": getattr(metrics, "age_appropriate_protection", {}),
                    "recommendations": self._generate_family_recommendations(metrics),
                }
            else:
                family_impact = {"impact_level": "low", "affected_members": 0, "recommendations": []}

        except Exception as e:
            family_impact = {"error": f"Ошибка анализа семейного воздействия: {str(e)}", "impact_level": "unknown"}

        return family_impact

    def _generate_family_recommendations(self, metrics: Any) -> List[str]:
        """Генерация семейных рекомендаций"""
        recommendations = []

        try:
            if hasattr(metrics, "family_security_score") and metrics.family_security_score < 75:
                recommendations.append("Улучшить семейные меры безопасности")
            if hasattr(metrics, "parental_controls_active") and not metrics.parental_controls_active:
                recommendations.append("Активировать родительские контроли")
            if hasattr(metrics, "elderly_protection_active") and not metrics.elderly_protection_active:
                recommendations.append("Активировать защиту пожилых")
            if hasattr(metrics, "child_activities_monitored") and not metrics.child_activities_monitored:
                recommendations.append("Начать мониторинг детской активности")

        except Exception as e:
            recommendations.append(f"Ошибка генерации семейных рекомендаций: {str(e)}")

        return recommendations

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Получение сводки аналитики"""
        try:
            summary = {
                "total_reports": len(self.analytics_history),
                "performance_metrics": {
                    "cpu_usage": self.performance_metrics.cpu_usage,
                    "memory_usage": self.performance_metrics.memory_usage,
                    "disk_usage": self.performance_metrics.disk_usage,
                    "availability": self.performance_metrics.availability,
                },
                "security_metrics": {
                    "threats_detected": self.security_metrics.threats_detected,
                    "threats_blocked": self.security_metrics.threats_blocked,
                    "security_score": self.security_metrics.security_score,
                    "risk_level": self.security_metrics.risk_level,
                },
                "family_metrics": {
                    "active_users": self.family_metrics.active_users,
                    "parental_controls_active": self.family_metrics.parental_controls_active,
                    "child_activities_monitored": self.family_metrics.child_activities_monitored,
                    "elderly_protection_active": self.family_metrics.elderly_protection_active,
                    "family_security_score": self.family_metrics.family_security_score,
                },
                "last_updated": datetime.now().isoformat(),
            }

            return summary

        except Exception as e:
            self.add_security_event(
                event_type="analytics_summary_error",
                description=f"Ошибка получения сводки аналитики: {str(e)}",
                severity="error",
                source="SecurityAnalytics",
            )
            return {}

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса сервиса"""
        try:
            status = {
                "service_name": self.service_name,
                "status": "active",
                "analytics_type": self.analytics_type.value,
                "total_reports": len(self.analytics_history),
                "performance_metrics": self.performance_metrics,
                "security_metrics": self.security_metrics,
                "family_metrics": self.family_metrics,
                "alert_thresholds": self.alert_thresholds,
                "last_updated": datetime.now().isoformat(),
            }

            return status

        except Exception as e:
            self.add_security_event(
                event_type="status_error",
                description=f"Ошибка получения статуса: {str(e)}",
                severity="error",
                source="SecurityAnalytics",
            )
            return {"error": str(e)}
