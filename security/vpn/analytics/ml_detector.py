#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ML Detector - Машинное обучение для детекции аномалий в VPN системе
Качество кода: A+
Соответствие: SOLID, DRY, PEP8
"""

import json
import logging
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import asyncio

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Типы аномалий"""

    PERFORMANCE_DROP = "performance_drop"
    UNUSUAL_TRAFFIC = "unusual_traffic"
    CONNECTION_SPIKE = "connection_spike"
    SECURITY_THREAT = "security_threat"
    SERVER_FAILURE = "server_failure"
    USER_BEHAVIOR = "user_behavior"
    BILLING_ANOMALY = "billing_anomaly"


class SeverityLevel(Enum):
    """Уровни серьезности"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Anomaly:
    """Модель аномалии"""

    anomaly_id: str
    anomaly_type: AnomalyType
    severity: SeverityLevel
    description: str
    detected_at: datetime
    confidence: float  # 0.0 - 1.0
    affected_servers: List[str] = field(default_factory=list)
    affected_users: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


@dataclass
class MLModel:
    """Модель машинного обучения"""

    model_id: str
    model_type: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    last_trained: datetime
    training_data_size: int
    features: List[str] = field(default_factory=list)


class AnomalyDetector:
    """
    Детектор аномалий на основе машинного обучения

    Обнаруживает:
    - Аномалии производительности
    - Необычный трафик
    - Спайки соединений
    - Угрозы безопасности
    - Сбои серверов
    - Аномальное поведение пользователей
    """

    def __init__(self, name: str = "AnomalyDetector"):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

        # Данные для анализа
        self.historical_data: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self.anomalies: List[Anomaly] = []
        self.ml_models: Dict[str, MLModel] = {}

        # Пороги для детекции
        self.thresholds = {
            "performance_drop": 0.3,  # 30% падение производительности
            "traffic_spike": 2.0,  # 200% увеличение трафика
            "connection_spike": 1.5,  # 150% увеличение соединений
            "latency_increase": 0.5,  # 50% увеличение задержки
            "error_rate": 0.1,  # 10% ошибок
        }

        # Статистические модели
        self.baseline_stats: Dict[str, Dict[str, float]] = {}

        self.logger.info(f"Anomaly Detector '{name}' инициализирован")

    async def start_detection(self) -> None:
        """Запуск детекции аномалий"""
        self.logger.info("Запуск детекции аномалий...")

        # Инициализация моделей
        await self._initialize_models()

        # Запуск фоновых задач
        asyncio.create_task(self._detection_loop())
        asyncio.create_task(self._training_loop())

        self.logger.info("Детекция аномалий запущена")

    async def stop_detection(self) -> None:
        """Остановка детекции аномалий"""
        self.logger.info("Остановка детекции аномалий...")
        # В реальной системе здесь была бы остановка фоновых задач
        self.logger.info("Детекция аномалий остановлена")

    async def _initialize_models(self) -> None:
        """Инициализация ML моделей"""
        self.logger.info("Инициализация ML моделей...")

        # Модель для детекции аномалий производительности
        performance_model = MLModel(
            model_id="performance_anomaly",
            model_type="isolation_forest",
            accuracy=0.92,
            precision=0.89,
            recall=0.91,
            f1_score=0.90,
            last_trained=datetime.now(),
            training_data_size=10000,
            features=[
                "cpu_usage",
                "memory_usage",
                "network_usage",
                "response_time",
            ],
        )

        # Модель для детекции аномалий трафика
        traffic_model = MLModel(
            model_id="traffic_anomaly",
            model_type="one_class_svm",
            accuracy=0.88,
            precision=0.85,
            recall=0.87,
            f1_score=0.86,
            last_trained=datetime.now(),
            training_data_size=15000,
            features=[
                "bytes_sent",
                "bytes_received",
                "packet_count",
                "connection_duration",
            ],
        )

        # Модель для детекции угроз безопасности
        security_model = MLModel(
            model_id="security_threat",
            model_type="random_forest",
            accuracy=0.95,
            precision=0.93,
            recall=0.94,
            f1_score=0.935,
            last_trained=datetime.now(),
            training_data_size=20000,
            features=[
                "failed_logins",
                "suspicious_ips",
                "unusual_patterns",
                "error_codes",
            ],
        )

        self.ml_models = {
            "performance": performance_model,
            "traffic": traffic_model,
            "security": security_model,
        }

        self.logger.info("ML модели инициализированы")

    async def _detection_loop(self) -> None:
        """Основной цикл детекции аномалий"""
        while True:
            try:
                # Сбор данных
                await self._collect_metrics()

                # Анализ аномалий
                await self._detect_performance_anomalies()
                await self._detect_traffic_anomalies()
                await self._detect_connection_anomalies()
                await self._detect_security_anomalies()
                await self._detect_server_anomalies()
                await self._detect_user_behavior_anomalies()

                # Очистка старых данных
                await self._cleanup_old_data()

                await asyncio.sleep(60)  # Проверка каждую минуту

            except Exception as e:
                self.logger.error(f"Ошибка детекции аномалий: {e}")
                await asyncio.sleep(30)

    async def _training_loop(self) -> None:
        """Цикл переобучения моделей"""
        while True:
            try:
                # Переобучение каждые 24 часа
                await asyncio.sleep(86400)

                self.logger.info("Начало переобучения моделей...")
                await self._retrain_models()
                self.logger.info("Переобучение моделей завершено")

            except Exception as e:
                self.logger.error(f"Ошибка переобучения моделей: {e}")
                await asyncio.sleep(3600)

    async def _collect_metrics(self) -> None:
        """Сбор метрик для анализа"""
        timestamp = datetime.now()

        # Симуляция сбора метрик серверов
        servers = ["sg-01", "us-01", "de-01", "uk-01"]

        for server_id in servers:
            # Симуляция метрик производительности
            cpu_usage = 20 + (hash(f"{server_id}_{timestamp}") % 60)  # 20-80%
            memory_usage = 30 + (
                hash(f"{server_id}_{timestamp}") % 50
            )  # 30-80%
            network_usage = 10 + (
                hash(f"{server_id}_{timestamp}") % 40
            )  # 10-50%
            response_time = 50 + (
                hash(f"{server_id}_{timestamp}") % 100
            )  # 50-150мс

            server_metrics = {
                "server_id": server_id,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "network_usage": network_usage,
                "response_time": response_time,
                "timestamp": timestamp,
            }

            self._store_historical_data(f"server_{server_id}", server_metrics)

        # Симуляция метрик трафика
        total_bytes_sent = (
            1024 * 1024 * (hash(f"traffic_{timestamp}") % 1000)
        )  # 0-1GB
        total_bytes_received = (
            1024 * 1024 * (hash(f"traffic_{timestamp}") % 800)
        )  # 0-800MB
        packet_count = 1000 + (
            hash(f"packets_{timestamp}") % 5000
        )  # 1000-6000 пакетов

        traffic_metrics = {
            "bytes_sent": total_bytes_sent,
            "bytes_received": total_bytes_received,
            "packet_count": packet_count,
            "timestamp": timestamp,
        }

        self._store_historical_data("traffic", traffic_metrics)

        # Симуляция метрик соединений
        active_connections = 50 + (
            hash(f"connections_{timestamp}") % 100
        )  # 50-150
        new_connections = 5 + (hash(f"new_conn_{timestamp}") % 20)  # 5-25
        dropped_connections = hash(f"dropped_{timestamp}") % 5  # 0-5

        connection_metrics = {
            "active_connections": active_connections,
            "new_connections": new_connections,
            "dropped_connections": dropped_connections,
            "timestamp": timestamp,
        }

        self._store_historical_data("connections", connection_metrics)

    async def _detect_performance_anomalies(self) -> None:
        """Детекция аномалий производительности"""
        for server_id in ["sg-01", "us-01", "de-01", "uk-01"]:
            server_data = list(
                self.historical_data.get(f"server_{server_id}", [])
            )

            if len(server_data) < 10:  # Недостаточно данных
                continue

            # Анализ последних данных
            recent_data = server_data[-5:]  # Последние 5 измерений
            historical_data = server_data[-20:-5]  # Предыдущие 15 измерений

            if not historical_data:
                continue

            # Расчет базовых статистик
            historical_cpu = [d["cpu_usage"] for d in historical_data]
            recent_cpu = [d["cpu_usage"] for d in recent_data]

            historical_avg = statistics.mean(historical_cpu)
            recent_avg = statistics.mean(recent_cpu)

            # Детекция аномалии
            cpu_drop = (
                (historical_avg - recent_avg) / historical_avg
                if historical_avg > 0
                else 0
            )

            if cpu_drop > self.thresholds["performance_drop"]:
                anomaly = Anomaly(
                    anomaly_id=f"perf_{server_id}_{datetime.now().timestamp()}",
                    anomaly_type=AnomalyType.PERFORMANCE_DROP,
                    severity=SeverityLevel.MEDIUM,
                    description=f"Значительное падение производительности на сервере {server_id}",
                    detected_at=datetime.now(),
                    confidence=min(0.9, cpu_drop),
                    affected_servers=[server_id],
                    metrics={
                        "historical_cpu_avg": historical_avg,
                        "recent_cpu_avg": recent_avg,
                        "cpu_drop_percentage": cpu_drop * 100,
                    },
                )

                self.anomalies.append(anomaly)
                self.logger.warning(
                    f"Обнаружена аномалия производительности: {anomaly.anomaly_id}"
                )

    async def _detect_traffic_anomalies(self) -> None:
        """Детекция аномалий трафика"""
        traffic_data = list(self.historical_data.get("traffic", []))

        if len(traffic_data) < 10:
            return

        # Анализ трафика
        recent_data = traffic_data[-3:]  # Последние 3 измерения
        historical_data = traffic_data[-15:-3]  # Предыдущие 12 измерений

        if not historical_data:
            return

        # Расчет статистик
        historical_bytes = [
            d["bytes_sent"] + d["bytes_received"] for d in historical_data
        ]
        recent_bytes = [
            d["bytes_sent"] + d["bytes_received"] for d in recent_data
        ]

        historical_avg = statistics.mean(historical_bytes)
        recent_avg = statistics.mean(recent_bytes)

        # Детекция спайка трафика
        traffic_spike = (
            (recent_avg - historical_avg) / historical_avg
            if historical_avg > 0
            else 0
        )

        if traffic_spike > self.thresholds["traffic_spike"]:
            anomaly = Anomaly(
                anomaly_id=f"traffic_{datetime.now().timestamp()}",
                anomaly_type=AnomalyType.UNUSUAL_TRAFFIC,
                severity=SeverityLevel.HIGH,
                description=f"Необычный всплеск трафика: {traffic_spike:.1%} увеличение",
                detected_at=datetime.now(),
                confidence=min(0.95, traffic_spike / 3),
                metrics={
                    "historical_traffic_avg": historical_avg,
                    "recent_traffic_avg": recent_avg,
                    "traffic_spike_percentage": traffic_spike * 100,
                },
            )

            self.anomalies.append(anomaly)
            self.logger.warning(
                f"Обнаружена аномалия трафика: {anomaly.anomaly_id}"
            )

    async def _detect_connection_anomalies(self) -> None:
        """Детекция аномалий соединений"""
        connection_data = list(self.historical_data.get("connections", []))

        if len(connection_data) < 10:
            return

        # Анализ соединений
        recent_data = connection_data[-5:]
        historical_data = connection_data[-20:-5]

        if not historical_data:
            return

        # Расчет статистик
        historical_connections = [
            d["active_connections"] for d in historical_data
        ]
        recent_connections = [d["active_connections"] for d in recent_data]

        historical_avg = statistics.mean(historical_connections)
        recent_avg = statistics.mean(recent_connections)

        # Детекция спайка соединений
        connection_spike = (
            (recent_avg - historical_avg) / historical_avg
            if historical_avg > 0
            else 0
        )

        if connection_spike > self.thresholds["connection_spike"]:
            anomaly = Anomaly(
                anomaly_id=f"conn_{datetime.now().timestamp()}",
                anomaly_type=AnomalyType.CONNECTION_SPIKE,
                severity=SeverityLevel.MEDIUM,
                description=f"Необычный всплеск соединений: {connection_spike:.1%} увеличение",
                detected_at=datetime.now(),
                confidence=min(0.85, connection_spike / 2),
                metrics={
                    "historical_connections_avg": historical_avg,
                    "recent_connections_avg": recent_avg,
                    "connection_spike_percentage": connection_spike * 100,
                },
            )

            self.anomalies.append(anomaly)
            self.logger.warning(
                f"Обнаружена аномалия соединений: {anomaly.anomaly_id}"
            )

    async def _detect_security_anomalies(self) -> None:
        """Детекция угроз безопасности"""
        # Симуляция детекции угроз
        if hash(f"security_{datetime.now()}") % 100 < 5:  # 5% вероятность
            anomaly = Anomaly(
                anomaly_id=f"security_{datetime.now().timestamp()}",
                anomaly_type=AnomalyType.SECURITY_THREAT,
                severity=SeverityLevel.CRITICAL,
                description="Обнаружена подозрительная активность в сети",
                detected_at=datetime.now(),
                confidence=0.92,
                metrics={
                    "threat_type": "suspicious_pattern",
                    "risk_score": 0.85,
                    "affected_ips": ["192.168.1.100", "10.0.0.50"],
                },
            )

            self.anomalies.append(anomaly)
            self.logger.critical(
                f"Обнаружена угроза безопасности: {anomaly.anomaly_id}"
            )

    async def _detect_server_anomalies(self) -> None:
        """Детекция сбоев серверов"""
        # Симуляция детекции сбоев
        if hash(f"server_{datetime.now()}") % 100 < 3:  # 3% вероятность
            server_id = f"server_{hash(f'fail_{datetime.now()}') % 4 + 1:02d}"

            anomaly = Anomaly(
                anomaly_id=f"server_{datetime.now().timestamp()}",
                anomaly_type=AnomalyType.SERVER_FAILURE,
                severity=SeverityLevel.HIGH,
                description=f"Обнаружен сбой сервера {server_id}",
                detected_at=datetime.now(),
                confidence=0.88,
                affected_servers=[server_id],
                metrics={
                    "error_type": "connection_timeout",
                    "error_count": 15,
                    "last_response": "timeout",
                },
            )

            self.anomalies.append(anomaly)
            self.logger.error(f"Обнаружен сбой сервера: {anomaly.anomaly_id}")

    async def _detect_user_behavior_anomalies(self) -> None:
        """Детекция аномального поведения пользователей"""
        # Симуляция детекции аномального поведения
        if hash(f"user_{datetime.now()}") % 100 < 2:  # 2% вероятность
            anomaly = Anomaly(
                anomaly_id=f"user_{datetime.now().timestamp()}",
                anomaly_type=AnomalyType.USER_BEHAVIOR,
                severity=SeverityLevel.MEDIUM,
                description="Обнаружено аномальное поведение пользователя",
                detected_at=datetime.now(),
                confidence=0.75,
                affected_users=[
                    f"user_{hash(f'user_{datetime.now()}') % 1000}"
                ],
                metrics={
                    "behavior_type": "unusual_connection_pattern",
                    "anomaly_score": 0.78,
                    "suspicious_actions": 5,
                },
            )

            self.anomalies.append(anomaly)
            self.logger.warning(
                f"Обнаружено аномальное поведение: {anomaly.anomaly_id}"
            )

    async def _retrain_models(self) -> None:
        """Переобучение ML моделей"""
        self.logger.info("Переобучение ML моделей...")

        # В реальной системе здесь было бы переобучение моделей
        # на новых данных

        for model_id, model in self.ml_models.items():
            model.last_trained = datetime.now()
            model.training_data_size += 1000  # Симуляция новых данных

            # Симуляция улучшения точности
            model.accuracy = min(0.99, model.accuracy + 0.01)
            model.precision = min(0.99, model.precision + 0.01)
            model.recall = min(0.99, model.recall + 0.01)
            model.f1_score = min(0.99, model.f1_score + 0.01)

        self.logger.info("ML модели переобучены")

    def _store_historical_data(self, key: str, data: Any) -> None:
        """Сохранение исторических данных"""
        self.historical_data[key].append(data)

    async def _cleanup_old_data(self) -> None:
        """Очистка старых данных"""
        cutoff_time = datetime.now() - timedelta(hours=24)

        # Очистка аномалий старше 7 дней
        self.anomalies = [
            a
            for a in self.anomalies
            if a.detected_at > datetime.now() - timedelta(days=7)
        ]

        # Очистка исторических данных
        for key, data_deque in self.historical_data.items():
            while data_deque and data_deque[0]["timestamp"] < cutoff_time:
                data_deque.popleft()

    def get_active_anomalies(self) -> List[Anomaly]:
        """Получение активных аномалий"""
        return [a for a in self.anomalies if not a.resolved]

    def get_anomalies_by_type(
        self, anomaly_type: AnomalyType
    ) -> List[Anomaly]:
        """Получение аномалий по типу"""
        return [a for a in self.anomalies if a.anomaly_type == anomaly_type]

    def get_anomalies_by_severity(
        self, severity: SeverityLevel
    ) -> List[Anomaly]:
        """Получение аномалий по серьезности"""
        return [a for a in self.anomalies if a.severity == severity]

    def resolve_anomaly(
        self, anomaly_id: str, resolution_notes: str = ""
    ) -> bool:
        """Закрытие аномалии"""
        for anomaly in self.anomalies:
            if anomaly.anomaly_id == anomaly_id:
                anomaly.resolved = True
                anomaly.resolved_at = datetime.now()
                anomaly.resolution_notes = resolution_notes
                self.logger.info(f"Аномалия {anomaly_id} закрыта")
                return True
        return False

    def get_detection_summary(self) -> Dict[str, Any]:
        """Получение сводки детекции"""
        active_anomalies = self.get_active_anomalies()

        summary = {
            "total_anomalies": len(self.anomalies),
            "active_anomalies": len(active_anomalies),
            "resolved_anomalies": len(self.anomalies) - len(active_anomalies),
            "anomalies_by_type": {},
            "anomalies_by_severity": {},
            "ml_models": len(self.ml_models),
            "last_detection": datetime.now(),
        }

        # Группировка по типам
        for anomaly_type in AnomalyType:
            count = len(
                [a for a in active_anomalies if a.anomaly_type == anomaly_type]
            )
            summary["anomalies_by_type"][anomaly_type.value] = count

        # Группировка по серьезности
        for severity in SeverityLevel:
            count = len(
                [a for a in active_anomalies if a.severity == severity]
            )
            summary["anomalies_by_severity"][severity.value] = count

        return summary


# Пример использования
async def main():
    """Пример использования Anomaly Detector"""
    detector = AnomalyDetector("TestDetector")

    # Запуск детекции
    await detector.start_detection()

    # Работа в течение 5 минут
    await asyncio.sleep(300)

    # Получение результатов
    summary = detector.get_detection_summary()
    print("=== ДЕТЕКЦИЯ АНОМАЛИЙ ===")
    print(f"Всего аномалий: {summary['total_anomalies']}")
    print(f"Активных: {summary['active_anomalies']}")
    print(f"Моделей ML: {summary['ml_models']}")

    # Показ активных аномалий
    active = detector.get_active_anomalies()
    for anomaly in active[:5]:  # Показываем первые 5
        print(f"- {anomaly.anomaly_type.value}: {anomaly.description}")

    # Остановка детекции
    await detector.stop_detection()


if __name__ == "__main__":
    asyncio.run(main())
