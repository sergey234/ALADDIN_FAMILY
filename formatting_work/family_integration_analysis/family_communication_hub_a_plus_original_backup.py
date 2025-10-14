#!/usr/bin/env python3
"""
FamilyCommunicationHubAPlus - AI коммуникационный хаб для семей
ОЧИЩЕННАЯ ВЕРСИЯ - Интеграция с FamilyProfileManagerEnhanced

Этот файл теперь является специализированным AI компонентом
для коммуникации, интегрированным с FamilyProfileManagerEnhanced
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

from core.base import SecurityBase, ComponentStatus

# Импорт из enhanced версии
from ..family.family_profile_manager_enhanced import (
    FamilyProfileManagerEnhanced,
    MessageType,
    MessagePriority,
    CommunicationChannel,
    Message
)


class SentimentType(Enum):
    """Типы тональности сообщений"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    URGENT = "urgent"
    EMERGENCY = "emergency"


@dataclass
class CommunicationAnalysis:
    """Результат анализа коммуникации"""
    message_id: str
    sentiment: SentimentType
    urgency_score: float
    anomaly_score: float
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class FamilyCommunicationHubAPlus(SecurityBase):
    """AI коммуникационный хаб для семей (очищенная версия)"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("FamilyCommunicationHubAPlus", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )
        
        # Ссылка на enhanced менеджер
        self.profile_manager: Optional[FamilyProfileManagerEnhanced] = None
        
        # AI компоненты
        self.ml_models = {}
        self.is_ml_initialized = False
        
        # Анализ коммуникации
        self.communication_analyses: Dict[str, CommunicationAnalysis] = {}

    def initialize(self) -> bool:
        """Инициализация AI хаба"""
        try:
            self.log_activity("Инициализация FamilyCommunicationHubAPlus")
            self.status = ComponentStatus.INITIALIZING
            
            # Инициализация AI компонентов
            self._initialize_ml_models()
            
            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity("FamilyCommunicationHubAPlus успешно инициализирован")
            return True
            
        except Exception as e:
            self.log_activity(f"Ошибка инициализации: {e}", "error")
            self.status = ComponentStatus.ERROR
            return False

    def set_profile_manager(self, profile_manager: FamilyProfileManagerEnhanced):
        """Установка ссылки на профильный менеджер"""
        self.profile_manager = profile_manager
        self.log_activity("Профильный менеджер установлен")

    def _initialize_ml_models(self):
        """Инициализация ML моделей"""
        try:
            # Модель для кластеризации сообщений (упрощенная)
            self.ml_models['message_clusterer'] = KMeans(
                n_clusters=3, random_state=42  # Уменьшили количество кластеров
            )
            
            # Модель для обнаружения аномалий (упрощенная)
            self.ml_models['anomaly_detector'] = IsolationForest(
                contamination=0.1, random_state=42
            )
            
            # Предварительное обучение на тестовых данных
            import numpy as np
            test_features = np.random.rand(10, 13)  # 10 образцов, 13 признаков
            self.ml_models['message_clusterer'].fit(test_features)
            self.ml_models['anomaly_detector'].fit(test_features)
            
            self.is_ml_initialized = True
            self.log_activity("ML модели инициализированы и обучены")
            
        except Exception as e:
            self.log_activity(f"Ошибка инициализации ML: {e}", "error")
            self.is_ml_initialized = False

    def analyze_message(self, message: Message) -> Optional[CommunicationAnalysis]:
        """AI анализ сообщения"""
        try:
            if not self.is_ml_initialized:
                return None
            
            # Извлечение признаков
            features = self._extract_communication_features(message)
            
            # Анализ тональности
            sentiment = self._analyze_sentiment(message, features)
            
            # Оценка срочности
            urgency_score = self._calculate_urgency_score(message, features)
            
            # Обнаружение аномалий
            anomaly_score = 0.0
            if 'anomaly_detector' in self.ml_models:
                detector = self.ml_models['anomaly_detector']
                anomaly_score = float(detector.decision_function([features])[0])
            
            # Генерация рекомендаций
            recommendations = self._generate_recommendations(
                message, sentiment, urgency_score, anomaly_score
            )
            
            # Создание анализа
            analysis = CommunicationAnalysis(
                message_id=message.id,
                sentiment=sentiment,
                urgency_score=urgency_score,
                anomaly_score=anomaly_score,
                recommendations=recommendations
            )
            
            # Сохранение анализа
            self.communication_analyses[message.id] = analysis
            
            self.log_activity(f"Анализ сообщения {message.id} завершен")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа сообщения: {e}")
            return None

    def _extract_communication_features(self, message: Message) -> List[float]:
        """Извлечение признаков для анализа коммуникации"""
        features = [
            len(message.content),  # Длина сообщения
            message.content.count('!'),  # Восклицательные знаки
            message.content.count('?'),  # Вопросительные знаки
            message.content.count(' '),  # Пробелы
            len(message.recipient_ids),  # Количество получателей
            int(message.is_encrypted),  # Зашифровано
            message.timestamp.hour,  # Час
            message.timestamp.weekday(),  # День недели
            len(message.content.split()),  # Количество слов
            message.content.count('urgent'),  # Ключевые слова
            message.content.count('emergency'),
            message.content.count('help'),
            message.content.count('danger'),
        ]
        return features

    def _analyze_sentiment(self, message: Message, features: List[float]) -> SentimentType:
        """Анализ тональности сообщения"""
        try:
            content = message.content.lower()
            
            # Простой анализ тональности на основе ключевых слов
            positive_words = ['good', 'great', 'excellent', 'happy', 'love', 'thanks']
            negative_words = ['bad', 'terrible', 'awful', 'hate', 'angry', 'sad']
            urgent_words = ['urgent', 'emergency', 'help', 'danger', 'asap']
            
            positive_count = sum(1 for word in positive_words if word in content)
            negative_count = sum(1 for word in negative_words if word in content)
            urgent_count = sum(1 for word in urgent_words if word in content)
            
            if urgent_count > 0:
                return SentimentType.EMERGENCY
            elif urgent_count > 2 or 'emergency' in content:
                return SentimentType.URGENT
            elif positive_count > negative_count:
                return SentimentType.POSITIVE
            elif negative_count > positive_count:
                return SentimentType.NEGATIVE
            else:
                return SentimentType.NEUTRAL
                
        except Exception as e:
            self.logger.error(f"Ошибка анализа тональности: {e}")
            return SentimentType.NEUTRAL

    def _calculate_urgency_score(self, message: Message, features: List[float]) -> float:
        """Расчет оценки срочности сообщения"""
        try:
            score = 0.0
            
            # Базовые факторы
            if message.priority == MessagePriority.EMERGENCY:
                score += 0.8
            elif message.priority == MessagePriority.URGENT:
                score += 0.6
            elif message.priority == MessagePriority.HIGH:
                score += 0.4
            
            # Ключевые слова
            urgent_words = ['urgent', 'emergency', 'help', 'danger', 'asap']
            content_lower = message.content.lower()
            urgent_word_count = sum(1 for word in urgent_words if word in content_lower)
            score += min(urgent_word_count * 0.1, 0.3)
            
            # Восклицательные знаки
            exclamation_count = features[1]
            score += min(exclamation_count * 0.05, 0.2)
            
            return min(score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета срочности: {e}")
            return 0.0

    def _generate_recommendations(self, message: Message, sentiment: SentimentType,
                                 urgency_score: float, anomaly_score: float) -> List[str]:
        """Генерация рекомендаций по безопасности"""
        recommendations = []
        
        try:
            # Рекомендации по срочности
            if urgency_score > 0.7:
                recommendations.append("Сообщение требует немедленного внимания")
                recommendations.append("Рекомендуется уведомить родителей")
            
            # Рекомендации по аномалиям
            if anomaly_score < -0.5:
                recommendations.append("Обнаружена аномальная активность")
                recommendations.append("Рекомендуется дополнительная проверка")
            
            # Рекомендации по тональности
            if sentiment == SentimentType.NEGATIVE:
                recommendations.append("Отрицательная тональность - возможны проблемы")
            elif sentiment == SentimentType.EMERGENCY:
                recommendations.append("ЭКСТРЕННОЕ сообщение - немедленные действия")
            
            # Рекомендации по безопасности
            if not message.is_encrypted:
                recommendations.append("Сообщение не зашифровано")
            
            if len(message.recipient_ids) > 5:
                recommendations.append("Большое количество получателей")
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации рекомендаций: {e}")
        
        return recommendations

    def get_analysis_for_message(self, message_id: str) -> Optional[CommunicationAnalysis]:
        """Получение анализа для конкретного сообщения"""
        return self.communication_analyses.get(message_id)

    def shutdown(self) -> bool:
        """Корректное завершение работы"""
        try:
            self.log_activity("Завершение работы FamilyCommunicationHubAPlus")
            self.status = ComponentStatus.STOPPING
            
            # Очистка данных
            self.communication_analyses.clear()
            self.ml_models.clear()
            
            self.status = ComponentStatus.STOPPED
            self.log_activity("FamilyCommunicationHubAPlus остановлен")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка завершения работы: {e}")
            return False


def create_communication_hub(config: Optional[Dict[str, Any]] = None) -> FamilyCommunicationHubAPlus:
    """Фабрика для создания FamilyCommunicationHubAPlus"""
    hub = FamilyCommunicationHubAPlus(config)
    hub.initialize()
    return hub


if __name__ == "__main__":
    print("FamilyCommunicationHubAPlus успешно создан!")
