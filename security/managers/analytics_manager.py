#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnalyticsManager - Расширенный менеджер аналитики системы безопасности
Глубокая аналитика поведения пользователей и трендов безопасности

Этот модуль предоставляет комплексную систему аналитики для AI системы безопасности,
включающую глубокий анализ поведения, предсказательное моделирование и статистический анализ.

Автор: ALADDIN Security System
Версия: 3.0
Дата: 2025-01-06
Лицензия: MIT
"""

import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsType(Enum):
    """Типы аналитики"""

    BEHAVIORAL = "behavioral"
    THREAT = "threat"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    PREDICTIVE = "predictive"
    ANOMALY = "anomaly"
    TREND = "trend"
    CORRELATION = "correlation"


class DataSource(Enum):
    """Источники данных"""

    SECURITY_EVENTS = "security_events"
    USER_ACTIVITY = "user_activity"
    SYSTEM_LOGS = "system_logs"
    NETWORK_TRAFFIC = "network_traffic"
    THREAT_INTELLIGENCE = "threat_intelligence"
    COMPLIANCE_DATA = "compliance_data"


class AnalysisStatus(Enum):
    """Статусы анализа"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AnalyticsConfig:
    """Конфигурация аналитики"""

    analysis_type: AnalyticsType
    data_source: DataSource
    time_window: int = 3600  # секунды
    sample_size: int = 10000
    confidence_threshold: float = 0.95
    anomaly_threshold: float = 0.1
    enable_ml: bool = True
    enable_clustering: bool = True
    enable_prediction: bool = True


@dataclass
class AnalyticsResult:
    """Результат аналитики"""

    analysis_id: str
    analysis_type: AnalyticsType
    status: AnalysisStatus
    start_time: datetime
    end_time: Optional[datetime]
    data_points: int
    insights: List[str]
    recommendations: List[str]
    confidence_score: float
    anomaly_score: float
    metadata: Dict[str, Any]


class DataProcessor(ABC):
    """Абстрактный класс для обработки данных"""

    @abstractmethod
    async def process(self, data: List[Dict[str, Any]]) -> np.ndarray:
        """Обработка данных"""
        pass


class MLModel(ABC):
    """Абстрактный класс для ML моделей"""

    @abstractmethod
    async def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Обучение модели"""
        pass

    @abstractmethod
    async def predict(self, X: np.ndarray) -> np.ndarray:
        """Предсказание"""
        pass


class BehavioralAnalyzer(DataProcessor):
    """Анализатор поведения пользователей"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.encoder = LabelEncoder()

    async def process(self, data: List[Dict[str, Any]]) -> np.ndarray:
        """Обработка данных поведения"""
        try:
            # Извлекаем признаки поведения
            features = []
            for record in data:
                feature_vector = [
                    record.get("session_duration", 0),
                    record.get("page_views", 0),
                    record.get("click_rate", 0.0),
                    record.get("time_on_site", 0),
                    record.get("bounce_rate", 0.0),
                    record.get("conversion_rate", 0.0),
                ]
                features.append(feature_vector)

            return np.array(features)

        except Exception as e:
            logger.error(f"Ошибка обработки данных поведения: {e}")
            return np.array([])


class ThreatAnalyzer(DataProcessor):
    """Анализатор угроз"""

    def __init__(self):
        self.scaler = StandardScaler()

    async def process(self, data: List[Dict[str, Any]]) -> np.ndarray:
        """Обработка данных угроз"""
        try:
            # Извлекаем признаки угроз
            features = []
            for record in data:
                feature_vector = [
                    record.get("severity_score", 0),
                    record.get("threat_level", 0),
                    record.get("attack_type", 0),
                    record.get("source_ip_risk", 0.0),
                    record.get("target_risk", 0.0),
                    record.get("time_risk", 0.0),
                ]
                features.append(feature_vector)

            return np.array(features)

        except Exception as e:
            logger.error(f"Ошибка обработки данных угроз: {e}")
            return np.array([])


class AnomalyDetector(MLModel):
    """Детектор аномалий"""

    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)

    async def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Обучение модели детекции аномалий"""
        try:
            self.model.fit(X)
            logger.info("Модель детекции аномалий обучена")
        except Exception as e:
            logger.error(f"Ошибка обучения модели аномалий: {e}")

    async def predict(self, X: np.ndarray) -> np.ndarray:
        """Предсказание аномалий"""
        try:
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"Ошибка предсказания аномалий: {e}")
            return np.array([])


class ClusteringModel(MLModel):
    """Модель кластеризации"""

    def __init__(self, n_clusters: int = 5):
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
        self.scaler = StandardScaler()

    async def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Обучение модели кластеризации"""
        try:
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled)
            logger.info("Модель кластеризации обучена")
        except Exception as e:
            logger.error(f"Ошибка обучения модели кластеризации: {e}")

    async def predict(self, X: np.ndarray) -> np.ndarray:
        """Предсказание кластеров"""
        try:
            X_scaled = self.scaler.transform(X)
            return self.model.predict(X_scaled)
        except Exception as e:
            logger.error(f"Ошибка предсказания кластеров: {e}")
            return np.array([])


class PredictiveModel(MLModel):
    """Предсказательная модель"""

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()

    async def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Обучение предсказательной модели"""
        try:
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            logger.info("Предсказательная модель обучена")
        except Exception as e:
            logger.error(f"Ошибка обучения предсказательной модели: {e}")

    async def predict(self, X: np.ndarray) -> np.ndarray:
        """Предсказание"""
        try:
            X_scaled = self.scaler.transform(X)
            return self.model.predict(X_scaled)
        except Exception as e:
            logger.error(f"Ошибка предсказания: {e}")
            return np.array([])


class AnalyticsManager:
    """Основной класс менеджера аналитики"""

    def __init__(self, config: AnalyticsConfig):
        """Инициализация менеджера аналитики"""
        self.config = config
        self.processors: Dict[AnalyticsType, DataProcessor] = {}
        self.models: Dict[str, MLModel] = {}
        self.results: Dict[str, AnalyticsResult] = {}
        self.is_running = False
        self.logger = logging.getLogger(__name__)

        # Инициализация процессоров
        self._initialize_processors()

        # Инициализация моделей
        self._initialize_models()

    def _initialize_processors(self) -> None:
        """Инициализация процессоров данных"""
        self.processors[AnalyticsType.BEHAVIORAL] = BehavioralAnalyzer()
        self.processors[AnalyticsType.THREAT] = ThreatAnalyzer()

    def _initialize_models(self) -> None:
        """Инициализация ML моделей"""
        self.models["anomaly_detector"] = AnomalyDetector()
        self.models["clustering"] = ClusteringModel()
        self.models["predictive"] = PredictiveModel()

    async def analyze(self, data: List[Dict[str, Any]]) -> AnalyticsResult:
        """Выполнение анализа данных"""
        analysis_id = hashlib.md5(
            f"{self.config.analysis_type.value}_{datetime.now()}".encode()
        ).hexdigest()[:8]

        result = AnalyticsResult(
            analysis_id=analysis_id,
            analysis_type=self.config.analysis_type,
            status=AnalysisStatus.RUNNING,
            start_time=datetime.now(),
            end_time=None,
            data_points=len(data),
            insights=[],
            recommendations=[],
            confidence_score=0.0,
            anomaly_score=0.0,
            metadata={},
        )

        try:
            # Обработка данных
            processor = self.processors.get(self.config.analysis_type)
            if not processor:
                raise ValueError(
                    f"Процессор для {self.config.analysis_type} не найден"
                )

            processed_data = await processor.process(data)
            if len(processed_data) == 0:
                raise ValueError("Нет данных для анализа")

            # Анализ аномалий
            if self.config.enable_ml:
                anomaly_model = self.models["anomaly_detector"]
                await anomaly_model.train(processed_data, np.array([]))
                anomaly_predictions = await anomaly_model.predict(
                    processed_data
                )
                result.anomaly_score = float(
                    np.mean(anomaly_predictions == -1)
                )

            # Кластеризация
            if self.config.enable_clustering:
                clustering_model = self.models["clustering"]
                await clustering_model.train(processed_data, np.array([]))
                clusters = await clustering_model.predict(processed_data)
                result.metadata["clusters"] = clusters.tolist()

            # Генерация инсайтов
            result.insights = await self._generate_insights(
                processed_data, result
            )
            result.recommendations = await self._generate_recommendations(
                result
            )

            # Расчет confidence score
            result.confidence_score = await self._calculate_confidence(result)

            result.status = AnalysisStatus.COMPLETED
            result.end_time = datetime.now()

        except Exception as e:
            self.logger.error(f"Ошибка анализа: {e}")
            result.status = AnalysisStatus.FAILED
            result.end_time = datetime.now()

        self.results[analysis_id] = result
        return result

    async def _generate_insights(
        self, data: np.ndarray, result: AnalyticsResult
    ) -> List[str]:
        """Генерация инсайтов"""
        insights = []

        try:
            # Базовые статистики
            mean_val = np.mean(data)
            std_val = np.std(data)
            min_val = np.min(data)
            max_val = np.max(data)

            insights.append(f"Среднее значение: {mean_val:.2f}")
            insights.append(f"Стандартное отклонение: {std_val:.2f}")
            insights.append(f"Диапазон: {min_val:.2f} - {max_val:.2f}")

            # Анализ аномалий
            if result.anomaly_score > 0.1:
                insights.append(
                    f"Обнаружено {result.anomaly_score:.1%} аномальных данных"
                )

            # Анализ кластеров
            if "clusters" in result.metadata:
                clusters = result.metadata["clusters"]
                unique_clusters = len(set(clusters))
                insights.append(f"Выявлено {unique_clusters} кластеров данных")

        except Exception as e:
            self.logger.error(f"Ошибка генерации инсайтов: {e}")

        return insights

    async def _generate_recommendations(
        self, result: AnalyticsResult
    ) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []

        try:
            # Рекомендации на основе аномалий
            if result.anomaly_score > 0.2:
                recommendations.append(
                    "Высокий уровень аномалий - требуется дополнительное расследование"
                )

            # Рекомендации на основе confidence score
            if result.confidence_score < 0.7:
                recommendations.append(
                    "Низкая уверенность в результатах - рекомендуется увеличить объем данных"
                )

            # Рекомендации на основе типа анализа
            if result.analysis_type == AnalyticsType.BEHAVIORAL:
                recommendations.append(
                    "Рекомендуется мониторинг поведения пользователей"
                )
            elif result.analysis_type == AnalyticsType.THREAT:
                recommendations.append(
                    "Рекомендуется усиление мер безопасности"
                )

        except Exception as e:
            self.logger.error(f"Ошибка генерации рекомендаций: {e}")

        return recommendations

    async def _calculate_confidence(self, result: AnalyticsResult) -> float:
        """Расчет confidence score"""
        try:
            confidence = 0.5  # Базовый уровень

            # Увеличиваем confidence на основе количества данных
            if result.data_points > 1000:
                confidence += 0.2
            elif result.data_points > 100:
                confidence += 0.1

            # Увеличиваем confidence на основе качества данных
            if result.anomaly_score < 0.1:
                confidence += 0.2
            elif result.anomaly_score < 0.2:
                confidence += 0.1

            return min(confidence, 1.0)

        except Exception as e:
            self.logger.error(f"Ошибка расчета confidence: {e}")
            return 0.5

    async def get_results(self, analysis_id: str) -> Optional[AnalyticsResult]:
        """Получение результата анализа"""
        return self.results.get(analysis_id)

    async def get_all_results(self) -> List[AnalyticsResult]:
        """Получение всех результатов"""
        return list(self.results.values())

    async def get_metrics(self) -> Dict[str, Any]:
        """Получение метрик"""
        try:
            total_analyses = len(self.results)
            completed_analyses = len(
                [
                    r
                    for r in self.results.values()
                    if r.status == AnalysisStatus.COMPLETED
                ]
            )
            failed_analyses = len(
                [
                    r
                    for r in self.results.values()
                    if r.status == AnalysisStatus.FAILED
                ]
            )

            return {
                "total_analyses": total_analyses,
                "completed_analyses": completed_analyses,
                "failed_analyses": failed_analyses,
                "success_rate": (
                    completed_analyses / total_analyses
                    if total_analyses > 0
                    else 0
                ),
                "average_confidence": (
                    np.mean(
                        [r.confidence_score for r in self.results.values()]
                    )
                    if self.results
                    else 0
                ),
                "average_anomaly_score": (
                    np.mean([r.anomaly_score for r in self.results.values()])
                    if self.results
                    else 0
                ),
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения метрик: {e}")
            return {}

    async def shutdown(self) -> None:
        """Завершение работы"""
        try:
            self.is_running = False
            self.logger.info("AnalyticsManager завершил работу")
        except Exception as e:
            self.logger.error(f"Ошибка завершения работы: {e}")


# Пример использования
async def main():
    """Пример использования AnalyticsManager"""
    config = AnalyticsConfig(
        analysis_type=AnalyticsType.BEHAVIORAL,
        data_source=DataSource.USER_ACTIVITY,
        time_window=3600,
        sample_size=1000,
        confidence_threshold=0.95,
        anomaly_threshold=0.1,
        enable_ml=True,
        enable_clustering=True,
        enable_prediction=True,
    )

    manager = AnalyticsManager(config)

    # Тестовые данные
    test_data = [
        {
            "session_duration": 1200,
            "page_views": 15,
            "click_rate": 0.3,
            "time_on_site": 800,
            "bounce_rate": 0.2,
            "conversion_rate": 0.05,
        }
        for _ in range(100)
    ]

    # Выполнение анализа
    result = await manager.analyze(test_data)
    print(f"Анализ завершен: {result.status}")
    print(f"Инсайты: {result.insights}")
    print(f"Рекомендации: {result.recommendations}")

    # Получение метрик
    metrics = await manager.get_metrics()
    print(f"Метрики: {metrics}")

    await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
