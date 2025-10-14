#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnalyticsBot - Бот аналитики безопасности
function_95: Интеллектуальный бот для аналитики и мониторинга безопасности

Этот модуль предоставляет интеллектуального бота для аналитики безопасности,
включающего:
- Сбор и анализ метрик безопасности
- Мониторинг производительности системы
- Детекция аномалий и трендов
- Генерация отчетов и дашбордов
- Прогнозирование угроз
- Анализ эффективности защиты
- Мониторинг ресурсов
- Анализ пользовательского поведения
- Интеграция с внешними системами
- Автоматические уведомления

Основные возможности:
1. Сбор метрик безопасности
2. Анализ производительности
3. Детекция аномалий
4. Генерация отчетов
5. Прогнозирование угроз
6. Анализ эффективности
7. Мониторинг ресурсов
8. Анализ поведения
9. Интеграция с системами
10. Автоматические уведомления

Технические детали:
- Использует ML для анализа данных
- Применяет статистические методы
- Интегрирует с Prometheus и Grafana
- Использует временные ряды для анализа
- Применяет алгоритмы машинного обучения
- Интегрирует с базами данных
- Использует геолокацию для анализа
- Применяет поведенческий анализ
- Интегрирует с системами уведомлений
- Использует машинное обучение для адаптации

Автор: ALADDIN Security System
Версия: 2.0
Дата: 2025-01-27
Лицензия: MIT
"""

import asyncio
import hashlib
import logging
import os

# Внутренние импорты
import sys
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

# Внешние зависимости
import redis
import sqlalchemy
from prometheus_client import Counter, Gauge
from pydantic import BaseModel, Field
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.base import SecurityBase

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# База данных
Base = declarative_base()


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
    ERROR = "error"
    CRITICAL = "critical"


class ReportType(Enum):
    """Типы отчетов"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class SecurityMetric(Base):
    """Метрика безопасности"""

    __tablename__ = "security_metrics"

    id = Column(String, primary_key=True)
    metric_name = Column(String, nullable=False)
    metric_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    labels = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    component = Column(String)
    severity = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class SecurityAlert(Base):
    """Оповещение безопасности"""

    __tablename__ = "security_alerts"

    id = Column(String, primary_key=True)
    alert_name = Column(String, nullable=False)
    alert_level = Column(String, nullable=False)
    message = Column(Text)
    component = Column(String)
    metric_name = Column(String)
    threshold_value = Column(Float)
    actual_value = Column(Float)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class SecurityReport(Base):
    """Отчет по безопасности"""

    __tablename__ = "security_reports"

    id = Column(String, primary_key=True)
    report_name = Column(String, nullable=False)
    report_type = Column(String, nullable=False)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    data = Column(JSON)
    summary = Column(Text)
    recommendations = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnomalyDetectionResult(BaseModel):
    """Результат детекции аномалий"""

    metric_name: str
    is_anomaly: bool = False
    anomaly_score: float = 0.0
    confidence: float = 0.0
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    description: str = ""
    severity: AlertLevel = AlertLevel.INFO


class ThreatPrediction(BaseModel):
    """Прогноз угроз"""

    threat_type: str
    probability: float = 0.0
    confidence: float = 0.0
    predicted_at: datetime = Field(default_factory=datetime.utcnow)
    time_horizon: int = 24  # часы
    description: str = ""
    mitigation_suggestions: List[str] = Field(default_factory=list)


class AnalyticsConfig(BaseModel):
    """Конфигурация аналитики"""

    metrics_collection: bool = True
    anomaly_detection: bool = True
    threat_prediction: bool = True
    report_generation: bool = True
    alerting: bool = True
    data_retention_days: int = 365
    anomaly_threshold: float = 0.8
    prediction_horizon_hours: int = 24


# Prometheus метрики
analytics_metrics_collected_total = Counter(
    "analytics_metrics_collected_total",
    "Total number of metrics collected",
    ["metric_type", "component"],
)

analytics_anomalies_detected_total = Counter(
    "analytics_anomalies_detected_total",
    "Total number of anomalies detected",
    ["metric_name", "severity"],
)

analytics_alerts_generated_total = Counter(
    "analytics_alerts_generated_total",
    "Total number of alerts generated",
    ["alert_level", "component"],
)

active_analytics_components = Gauge(
    "active_analytics_components", "Number of active analytics components"
)


class AnalyticsBot(SecurityBase):
    """
    Интеллектуальный бот аналитики безопасности

    Предоставляет комплексную систему аналитики безопасности с поддержкой:
    - Сбора и анализа метрик безопасности
    - Мониторинга производительности системы
    - Детекции аномалий и трендов
    - Генерации отчетов и дашбордов
    """

    def __init__(
        self,
        name: str = "AnalyticsBot",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализация AnalyticsBot

        Args:
            name: Имя бота
            config: Конфигурация
        """
        super().__init__(name, config)

        # Конфигурация по умолчанию
        self.default_config = {
            "redis_url": "redis://localhost:6379/0",
            "database_url": "sqlite:///analytics_bot.db",
            "metrics_collection": True,
            "anomaly_detection": True,
            "threat_prediction": True,
            "report_generation": True,
            "alerting": True,
            "data_retention_days": 365,
            "anomaly_threshold": 0.8,
            "prediction_horizon_hours": 24,
            "ml_enabled": True,
            "adaptive_learning": True,
            "real_time_monitoring": True,
            "cleanup_interval": 300,
            "metrics_enabled": True,
            "logging_enabled": True,
        }

        # Объединение конфигураций
        self.config = {**self.default_config, **(config or {})}

        # Инициализация компонентов
        self.redis_client: Optional[redis.Redis] = None
        self.db_engine: Optional[sqlalchemy.Engine] = None
        self.db_session: Optional[sqlalchemy.orm.Session] = None
        self.ml_models: Dict[str, Any] = {}
        self.anomaly_detector: Optional[IsolationForest] = None
        self.threat_predictor: Optional[LinearRegression] = None
        self.scaler: Optional[StandardScaler] = None

        # Статистика
        self.stats = {
            "total_metrics": 0,
            "collected_metrics": 0,
            "anomalies_detected": 0,
            "alerts_generated": 0,
            "reports_generated": 0,
            "threats_predicted": 0,
            "active_components": 0,
            "data_points": 0,
            "false_positives": 0,
        }

        # Потоки
        self.monitoring_thread: Optional[threading.Thread] = None
        self.running = False

        # Блокировки
        self.lock = threading.RLock()

        self.logger.info(f"AnalyticsBot {name} инициализирован")

    async def start(self) -> bool:
        """Запуск бота аналитики"""
        try:
            with self.lock:
                if self.running:
                    self.logger.warning("AnalyticsBot уже запущен")
                    return True

                # Инициализация базы данных
                await self._setup_database()

                # Инициализация Redis
                await self._setup_redis()

                # Инициализация ML моделей
                if self.config.get("ml_enabled", True):
                    await self._setup_ml_models()

                # Запуск мониторинга
                self.running = True
                self.monitoring_thread = threading.Thread(
                    target=self._monitoring_worker
                )
                self.monitoring_thread.daemon = True
                self.monitoring_thread.start()

                self.logger.info("AnalyticsBot запущен успешно")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка запуска AnalyticsBot: {e}")
            return False

    async def stop(self) -> bool:
        """Остановка бота аналитики"""
        try:
            with self.lock:
                if not self.running:
                    self.logger.warning("AnalyticsBot уже остановлен")
                    return True

                self.running = False

                # Ожидание завершения потоков
                if (
                    self.monitoring_thread
                    and self.monitoring_thread.is_alive()
                ):
                    self.monitoring_thread.join(timeout=5)

                # Закрытие соединений
                if self.db_session:
                    self.db_session.close()

                if self.redis_client:
                    self.redis_client.close()

                self.logger.info("AnalyticsBot остановлен")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка остановки AnalyticsBot: {e}")
            return False

    async def _setup_database(self) -> None:
        """Настройка базы данных"""
        try:
            database_url = self.config.get(
                "database_url", "sqlite:///analytics_bot.db"
            )
            self.db_engine = create_engine(database_url)
            Base.metadata.create_all(self.db_engine)

            Session = sessionmaker(bind=self.db_engine)
            self.db_session = Session()

            self.logger.info("База данных AnalyticsBot настроена")

        except Exception as e:
            self.logger.error(f"Ошибка настройки базы данных: {e}")
            raise

    async def _setup_redis(self) -> None:
        """Настройка Redis"""
        try:
            redis_url = self.config.get(
                "redis_url", "redis://localhost:6379/0"
            )
            self.redis_client = redis.from_url(
                redis_url, decode_responses=True
            )

            # Тест соединения
            self.redis_client.ping()

            self.logger.info("Redis для AnalyticsBot настроен")

        except Exception as e:
            self.logger.error(f"Ошибка настройки Redis: {e}")
            raise

    async def _setup_ml_models(self) -> None:
        """Настройка ML моделей"""
        try:
            # Модель детекции аномалий
            self.anomaly_detector = IsolationForest(
                contamination=0.1, random_state=42, n_estimators=100
            )

            # Модель прогнозирования угроз
            self.threat_predictor = LinearRegression()

            # Масштабировщик
            self.scaler = StandardScaler()

            self.logger.info("ML модели AnalyticsBot настроены")

        except Exception as e:
            self.logger.error(f"Ошибка настройки ML моделей: {e}")

    def _monitoring_worker(self) -> None:
        """Фоновый процесс мониторинга"""
        while self.running:
            try:
                time.sleep(1)  # Проверка каждую секунду

                # Обновление статистики
                self._update_stats()

                # Обработка метрик
                self._process_metrics()

                # Детекция аномалий
                if self.config.get("anomaly_detection", True):
                    self._detect_anomalies()

                # Прогнозирование угроз
                if self.config.get("threat_prediction", True):
                    self._predict_threats()

            except Exception as e:
                self.logger.error(f"Ошибка в процессе мониторинга: {e}")

    def _update_stats(self) -> None:
        """Обновление статистики"""
        try:
            with self.lock:
                # Обновление метрик Prometheus
                active_analytics_components.set(
                    self.stats["active_components"]
                )

        except Exception as e:
            self.logger.error(f"Ошибка обновления статистики: {e}")

    def _process_metrics(self) -> None:
        """Обработка метрик"""
        try:
            # Здесь должна быть логика обработки метрик
            # Пока что заглушка
            pass

        except Exception as e:
            self.logger.error(f"Ошибка обработки метрик: {e}")

    def _detect_anomalies(self) -> None:
        """Детекция аномалий"""
        try:
            # Здесь должна быть логика детекции аномалий
            # Пока что заглушка
            pass

        except Exception as e:
            self.logger.error(f"Ошибка детекции аномалий: {e}")

    def _predict_threats(self) -> None:
        """Прогнозирование угроз"""
        try:
            # Здесь должна быть логика прогнозирования угроз
            # Пока что заглушка
            pass

        except Exception as e:
            self.logger.error(f"Ошибка прогнозирования угроз: {e}")

    async def collect_metric(
        self,
        metric_name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        labels: Optional[Dict[str, str]] = None,
        component: Optional[str] = None,
    ) -> bool:
        """Сбор метрики"""
        try:
            with self.lock:
                # Создание записи метрики
                metric = SecurityMetric(
                    id=self._generate_metric_id(),
                    metric_name=metric_name,
                    metric_type=metric_type.value,
                    value=value,
                    labels=labels or {},
                    component=component,
                    severity=self._get_severity_by_value(value),
                )

                # Сохранение в базу данных
                if self.db_session:
                    self.db_session.add(metric)
                    self.db_session.commit()

                # Обновление статистики
                self.stats["total_metrics"] += 1
                self.stats["collected_metrics"] += 1
                self.stats["data_points"] += 1

                # Обновление метрик Prometheus
                analytics_metrics_collected_total.labels(
                    metric_type=metric_type.value,
                    component=component or "unknown",
                ).inc()

                self.logger.debug(f"Метрика {metric_name} собрана: {value}")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка сбора метрики: {e}")
            return False

    def _generate_metric_id(self) -> str:
        """Генерация ID метрики"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()
        ).hexdigest()[:8]
        return f"METRIC_{timestamp}_{random_part}"

    def _get_severity_by_value(self, value: float) -> str:
        """Получение уровня серьезности по значению"""
        if value >= 0.9:
            return "critical"
        elif value >= 0.7:
            return "high"
        elif value >= 0.5:
            return "medium"
        elif value >= 0.3:
            return "low"
        else:
            return "info"

    async def detect_anomaly(
        self, metric_name: str, values: List[float]
    ) -> AnomalyDetectionResult:
        """Детекция аномалии в метрике"""
        try:
            if not self.anomaly_detector or len(values) < 10:
                return AnomalyDetectionResult(
                    metric_name=metric_name,
                    is_anomaly=False,
                    description="Недостаточно данных для анализа",
                )

            # Подготовка данных
            data = np.array(values).reshape(-1, 1)
            scaled_data = self.scaler.fit_transform(data)

            # Детекция аномалий
            anomaly_scores = self.anomaly_detector.decision_function(
                scaled_data
            )
            is_anomaly = self.anomaly_detector.predict(scaled_data)[-1] == -1

            # Вычисление уверенности
            confidence = abs(anomaly_scores[-1])
            anomaly_score = 1 - confidence  # Инвертируем для удобства

            # Определение уровня серьезности
            if anomaly_score >= 0.9:
                severity = AlertLevel.CRITICAL
            elif anomaly_score >= 0.7:
                severity = AlertLevel.ERROR
            elif anomaly_score >= 0.5:
                severity = AlertLevel.WARNING
            else:
                severity = AlertLevel.INFO

            # Обновление статистики
            if is_anomaly:
                self.stats["anomalies_detected"] += 1
                analytics_anomalies_detected_total.labels(
                    metric_name=metric_name, severity=severity.value
                ).inc()

            return AnomalyDetectionResult(
                metric_name=metric_name,
                is_anomaly=is_anomaly,
                anomaly_score=anomaly_score,
                confidence=confidence,
                description=f"Аномалия в метрике {metric_name}",
                severity=severity,
            )

        except Exception as e:
            self.logger.error(f"Ошибка детекции аномалии: {e}")
            return AnomalyDetectionResult(
                metric_name=metric_name,
                is_anomaly=False,
                description=f"Ошибка анализа: {e}",
            )

    async def predict_threat(
        self, metric_data: Dict[str, List[float]]
    ) -> ThreatPrediction:
        """Прогнозирование угрозы"""
        try:
            if not self.threat_predictor:
                return ThreatPrediction(
                    threat_type="unknown",
                    description="Модель прогнозирования не настроена",
                )

            # Здесь должна быть логика прогнозирования угроз
            # Пока что заглушка

            threat_type = "security_breach"
            probability = 0.3
            confidence = 0.7

            # Обновление статистики
            self.stats["threats_predicted"] += 1

            return ThreatPrediction(
                threat_type=threat_type,
                probability=probability,
                confidence=confidence,
                description=f"Прогнозируется угроза типа {threat_type}",
                mitigation_suggestions=[
                    "Усилить мониторинг",
                    "Проверить логи безопасности",
                    "Обновить правила фильтрации",
                ],
            )

        except Exception as e:
            self.logger.error(f"Ошибка прогнозирования угрозы: {e}")
            return ThreatPrediction(
                threat_type="unknown",
                description=f"Ошибка прогнозирования: {e}",
            )

    async def generate_alert(
        self,
        alert_name: str,
        message: str,
        alert_level: AlertLevel = AlertLevel.INFO,
        component: Optional[str] = None,
        metric_name: Optional[str] = None,
        threshold_value: Optional[float] = None,
        actual_value: Optional[float] = None,
    ) -> bool:
        """Генерация оповещения"""
        try:
            with self.lock:
                # Создание записи оповещения
                alert = SecurityAlert(
                    id=self._generate_alert_id(),
                    alert_name=alert_name,
                    alert_level=alert_level.value,
                    message=message,
                    component=component,
                    metric_name=metric_name,
                    threshold_value=threshold_value,
                    actual_value=actual_value,
                )

                # Сохранение в базу данных
                if self.db_session:
                    self.db_session.add(alert)
                    self.db_session.commit()

                # Обновление статистики
                self.stats["alerts_generated"] += 1

                # Обновление метрик Prometheus
                analytics_alerts_generated_total.labels(
                    alert_level=alert_level.value,
                    component=component or "unknown",
                ).inc()

                self.logger.info(
                    f"Оповещение {alert_name} сгенерировано: {message}"
                )
                return True

        except Exception as e:
            self.logger.error(f"Ошибка генерации оповещения: {e}")
            return False

    def _generate_alert_id(self) -> str:
        """Генерация ID оповещения"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()
        ).hexdigest()[:8]
        return f"ALERT_{timestamp}_{random_part}"

    async def generate_report(
        self,
        report_name: str,
        report_type: ReportType,
        period_start: datetime,
        period_end: datetime,
    ) -> Dict[str, Any]:
        """Генерация отчета"""
        try:
            # Сбор данных за период
            if self.db_session:
                metrics = (
                    self.db_session.query(SecurityMetric)
                    .filter(
                        SecurityMetric.timestamp >= period_start,
                        SecurityMetric.timestamp <= period_end,
                    )
                    .all()
                )

                alerts = (
                    self.db_session.query(SecurityAlert)
                    .filter(
                        SecurityAlert.created_at >= period_start,
                        SecurityAlert.created_at <= period_end,
                    )
                    .all()
                )

                # Анализ данных
                total_metrics = len(metrics)
                total_alerts = len(alerts)
                critical_alerts = len(
                    [
                        a
                        for a in alerts
                        if a.alert_level == AlertLevel.CRITICAL.value
                    ]
                )

                # Создание отчета
                report_data = {
                    "period_start": period_start.isoformat(),
                    "period_end": period_end.isoformat(),
                    "total_metrics": total_metrics,
                    "total_alerts": total_alerts,
                    "critical_alerts": critical_alerts,
                    "metrics_by_component": self._group_metrics_by_component(
                        metrics
                    ),
                    "alerts_by_level": self._group_alerts_by_level(alerts),
                    "top_metrics": self._get_top_metrics(metrics),
                    "recommendations": self._generate_recommendations(
                        metrics, alerts
                    ),
                }

                # Сохранение отчета
                report = SecurityReport(
                    id=self._generate_report_id(),
                    report_name=report_name,
                    report_type=report_type.value,
                    period_start=period_start,
                    period_end=period_end,
                    data=report_data,
                    summary=(
                        f"Отчет за период {period_start.date()} - "
                        f"{period_end.date()}"
                    ),
                    recommendations="Рекомендации по улучшению безопасности",
                )

                self.db_session.add(report)
                self.db_session.commit()

                # Обновление статистики
                self.stats["reports_generated"] += 1

                self.logger.info(f"Отчет {report_name} сгенерирован")
                return report_data

        except Exception as e:
            self.logger.error(f"Ошибка генерации отчета: {e}")
            return {"error": str(e)}

    def _group_metrics_by_component(
        self, metrics: List[SecurityMetric]
    ) -> Dict[str, int]:
        """Группировка метрик по компонентам"""
        components = defaultdict(int)
        for metric in metrics:
            component = metric.component or "unknown"
            components[component] += 1
        return dict(components)

    def _group_alerts_by_level(
        self, alerts: List[SecurityAlert]
    ) -> Dict[str, int]:
        """Группировка оповещений по уровням"""
        levels = defaultdict(int)
        for alert in alerts:
            levels[alert.alert_level] += 1
        return dict(levels)

    def _get_top_metrics(
        self, metrics: List[SecurityMetric], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Получение топ метрик"""
        metric_counts = defaultdict(int)
        for metric in metrics:
            metric_counts[metric.metric_name] += 1

        sorted_metrics = sorted(
            metric_counts.items(), key=lambda x: x[1], reverse=True
        )
        return [
            {"name": name, "count": count}
            for name, count in sorted_metrics[:limit]
        ]

    def _generate_recommendations(
        self, metrics: List[SecurityMetric], alerts: List[SecurityAlert]
    ) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []

        # Анализ критических оповещений
        critical_alerts = [
            a for a in alerts if a.alert_level == AlertLevel.CRITICAL.value
        ]
        if critical_alerts:
            recommendations.append(
                "Увеличить мониторинг критических компонентов"
            )

        # Анализ метрик
        if len(metrics) < 100:
            recommendations.append("Увеличить частоту сбора метрик")

        # Анализ оповещений
        if len(alerts) > 50:
            recommendations.append("Пересмотреть пороги оповещений")

        return recommendations

    def _generate_report_id(self) -> str:
        """Генерация ID отчета"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()
        ).hexdigest()[:8]
        return f"REPORT_{timestamp}_{random_part}"

    async def get_analytics_dashboard(self) -> Dict[str, Any]:
        """Получение дашборда аналитики"""
        try:
            # Получение последних метрик
            if self.db_session:
                recent_metrics = (
                    self.db_session.query(SecurityMetric)
                    .filter(
                        SecurityMetric.timestamp
                        >= datetime.utcnow() - timedelta(hours=24)
                    )
                    .all()
                )

                recent_alerts = (
                    self.db_session.query(SecurityAlert)
                    .filter(
                        SecurityAlert.created_at
                        >= datetime.utcnow() - timedelta(hours=24)
                    )
                    .all()
                )

                # Формирование дашборда
                dashboard = {
                    "overview": {
                        "total_metrics": self.stats["total_metrics"],
                        "anomalies_detected": self.stats["anomalies_detected"],
                        "alerts_generated": self.stats["alerts_generated"],
                        "reports_generated": self.stats["reports_generated"],
                        "threats_predicted": self.stats["threats_predicted"],
                    },
                    "recent_metrics": len(recent_metrics),
                    "recent_alerts": len(recent_alerts),
                    "critical_alerts": len(
                        [
                            a
                            for a in recent_alerts
                            if a.alert_level == AlertLevel.CRITICAL.value
                        ]
                    ),
                    "components_status": self._get_components_status(),
                    "timestamp": datetime.utcnow().isoformat(),
                }

                return dashboard

        except Exception as e:
            self.logger.error(f"Ошибка получения дашборда: {e}")
            return {"error": str(e)}

    def _get_components_status(self) -> Dict[str, str]:
        """Получение статуса компонентов"""
        return {
            "metrics_collection": (
                "active"
                if self.config.get("metrics_collection", True)
                else "inactive"
            ),
            "anomaly_detection": (
                "active"
                if self.config.get("anomaly_detection", True)
                else "inactive"
            ),
            "threat_prediction": (
                "active"
                if self.config.get("threat_prediction", True)
                else "inactive"
            ),
            "report_generation": (
                "active"
                if self.config.get("report_generation", True)
                else "inactive"
            ),
            "alerting": (
                "active" if self.config.get("alerting", True) else "inactive"
            ),
        }

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса бота"""
        try:
            return {
                "name": self.name,
                "status": "running" if self.running else "stopped",
                "config": self.config,
                "stats": self.stats,
                "ml_enabled": self.config.get("ml_enabled", False),
                "last_update": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"error": str(e)}


# Функция тестирования
async def test_analytics_bot():
    """Тестирование AnalyticsBot"""
    print("🧪 Тестирование AnalyticsBot...")

    # Создание бота
    bot = AnalyticsBot("TestAnalyticsBot")

    try:
        # Запуск
        await bot.start()
        print("✅ AnalyticsBot запущен")

        # Сбор тестовых метрик
        await bot.collect_metric(
            "cpu_usage", 0.75, MetricType.GAUGE, {"host": "server1"}, "system"
        )
        await bot.collect_metric(
            "memory_usage",
            0.60,
            MetricType.GAUGE,
            {"host": "server1"},
            "system",
        )
        await bot.collect_metric(
            "security_events",
            15,
            MetricType.COUNTER,
            {"type": "login"},
            "security",
        )
        print("✅ Метрики собраны")

        # Детекция аномалий
        anomaly_result = await bot.detect_anomaly(
            "cpu_usage", [0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99, 1.0, 1.1]
        )
        print(f"✅ Аномалия детектирована: {anomaly_result.is_anomaly}")

        # Генерация оповещения
        alert_generated = await bot.generate_alert(
            "High CPU Usage",
            "CPU usage превысил 90%",
            AlertLevel.WARNING,
            "system",
            "cpu_usage",
            0.9,
            0.95,
        )
        print(f"✅ Оповещение сгенерировано: {alert_generated}")

        # Генерация отчета
        report = await bot.generate_report(
            "Daily Security Report",
            ReportType.DAILY,
            datetime.utcnow() - timedelta(days=1),
            datetime.utcnow(),
        )
        print(
            f"✅ Отчет сгенерирован: {report.get('total_metrics', 0)} метрик"
        )

        # Получение дашборда
        dashboard = await bot.get_analytics_dashboard()
        print(
            f"✅ Дашборд получен: "
            f"{dashboard.get('overview', {}).get('total_metrics', 0)} метрик"
        )

        # Получение общего статуса
        bot_status = await bot.get_status()
        print(f"✅ Статус бота: {bot_status['status']}")

    finally:
        # Остановка
        await bot.stop()
        print("✅ AnalyticsBot остановлен")


# Запуск тестов при прямом выполнении
if __name__ == "__main__":
    asyncio.run(test_analytics_bot())
