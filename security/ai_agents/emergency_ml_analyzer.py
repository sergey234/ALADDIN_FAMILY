#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EmergencyMLAnalyzer - Координатор ML анализа экстренных ситуаций
Применение SOLID принципов и DRY
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.base import SecurityBase

from .emergency_ml_models import (
    EmergencyAnomalyDetector,
    EmergencyClusterAnalyzer,
    EmergencyPatternRecognizer,
)
from .emergency_models import EmergencyEvent, EmergencySeverity, EmergencyType
from .emergency_performance_analyzer import EmergencyPerformanceAnalyzer
from .emergency_risk_analyzer import EmergencyRiskAnalyzer
from .emergency_security_utils import EmergencySecurityUtils


class EmergencyMLAnalyzer(SecurityBase):
    """
    Координатор ML анализа экстренных ситуаций

    Применяет принципы SOLID:
    - Single Responsibility: координация ML анализа
    - Open/Closed: открыт для расширения через специализированные анализаторы
    - Liskov Substitution: использует абстракции
    - Interface Segregation: разделенные интерфейсы
    - Dependency Inversion: зависит от абстракций
    """

    def __init__(self, name: str = "EmergencyMLAnalyzer"):
        """
        Инициализация ML анализатора

        Args:
            name: Имя анализатора
        """
        super().__init__(name)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Инициализируем специализированные анализаторы
        self.anomaly_detector = EmergencyAnomalyDetector()
        self.cluster_analyzer = EmergencyClusterAnalyzer()
        self.pattern_recognizer = EmergencyPatternRecognizer()
        self.risk_analyzer = EmergencyRiskAnalyzer()
        self.performance_analyzer = EmergencyPerformanceAnalyzer()

        self.is_trained = False
        self.training_data = []

        self.logger.info("EmergencyMLAnalyzer инициализирован")

    def train_models(self, training_data: List[Dict[str, Any]]) -> bool:
        """
        Обучить все ML модели

        Args:
            training_data: Данные для обучения

        Returns:
            bool: True если обучение успешно
        """
        try:
            if not training_data:
                self.logger.warning("Нет данных для обучения")
                return False

            # Валидируем данные
            validated_data = self._validate_training_data(training_data)
            if not validated_data:
                return False

            # Обучаем модели
            anomaly_success = self.anomaly_detector.train(validated_data)
            cluster_success = self.cluster_analyzer.train(validated_data)
            pattern_success = self.pattern_recognizer.train(validated_data)

            # Проверяем успешность обучения
            if anomaly_success and cluster_success and pattern_success:
                self.is_trained = True
                self.training_data = validated_data
                self.logger.info("Все ML модели успешно обучены")
                return True
            else:
                self.logger.error("Ошибка обучения некоторых моделей")
                return False

        except Exception as e:
            self.logger.error(f"Ошибка обучения моделей: {e}")
            return False

    def _validate_training_data(
        self, data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Валидировать данные обучения

        Args:
            data: Исходные данные

        Returns:
            List[Dict[str, Any]]: Валидированные данные
        """
        try:
            validated_data = []

            for item in data:
                # Проверяем обязательные поля
                if not all(
                    key in item
                    for key in [
                        "severity_score",
                        "time_score",
                        "location_score",
                        "type_score",
                    ]
                ):
                    continue

                # Валидируем значения
                if not all(
                    isinstance(item[key], (int, float))
                    for key in [
                        "severity_score",
                        "time_score",
                        "location_score",
                        "type_score",
                    ]
                ):
                    continue

                validated_data.append(item)

            self.logger.info(
                f"Валидировано {len(validated_data)} из {len(data)} записей"
            )
            return validated_data

        except Exception as e:
            self.logger.error(f"Ошибка валидации данных: {e}")
            return []

    def analyze_event(self, event: EmergencyEvent) -> Dict[str, Any]:
        """
        Проанализировать экстренное событие

        Args:
            event: Событие для анализа

        Returns:
            Dict[str, Any]: Результаты анализа
        """
        try:
            if not self.is_trained:
                self.logger.warning("Модели не обучены")
                return {"error": "Модели не обучены"}

            # Подготавливаем данные для анализа
            event_data = self._prepare_event_data(event)

            # Анализируем аномалии
            anomalies = self.anomaly_detector.detect_anomalies([event_data])

            # Анализируем кластеры
            clusters = self.cluster_analyzer.analyze_clusters([event_data])

            # Распознаем паттерны
            patterns = self.pattern_recognizer.recognize_patterns([event_data])

            # Анализируем риски
            risk_score = self.risk_analyzer.calculate_risk_score(event)
            risk_level = self.risk_analyzer.get_risk_level(risk_score)

            # Формируем результат
            analysis_result = {
                "event_id": event.event_id,
                "is_anomaly": anomalies[0] if anomalies else False,
                "cluster_id": clusters[0] if clusters else -1,
                "patterns": patterns,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_recommendations": (
                    self.risk_analyzer.get_risk_recommendations(risk_score)
                ),
                "timestamp": datetime.now().isoformat(),
            }

            self.logger.info(f"Событие {event.event_id} проанализировано")
            return analysis_result

        except Exception as e:
            self.logger.error(f"Ошибка анализа события: {e}")
            return {"error": str(e)}

    def _prepare_event_data(self, event: EmergencyEvent) -> Dict[str, Any]:
        """
        Подготовить данные события для анализа

        Args:
            event: Событие для подготовки

        Returns:
            Dict[str, Any]: Подготовленные данные
        """
        try:
            # Извлекаем координаты
            coordinates = event.location.get("coordinates", (0, 0))
            latitude = (
                coordinates[0]
                if isinstance(coordinates, (list, tuple))
                and len(coordinates) >= 2
                else 0
            )
            longitude = (
                coordinates[1]
                if isinstance(coordinates, (list, tuple))
                and len(coordinates) >= 2
                else 0
            )

            # Преобразуем время в числовой формат
            timestamp = event.timestamp.timestamp() if event.timestamp else 0

            # Преобразуем тип и серьезность в числовые значения
            type_scores = {
                EmergencyType.MEDICAL: 1.0,
                EmergencyType.FIRE: 0.9,
                EmergencyType.POLICE: 0.8,
                EmergencyType.SECURITY: 0.7,
                EmergencyType.ACCIDENT: 0.9,
                EmergencyType.NATURAL_DISASTER: 1.0,
                EmergencyType.TECHNICAL: 0.5,
                EmergencyType.PERSONAL: 0.3,
            }

            severity_scores = {
                EmergencySeverity.LOW: 0.2,
                EmergencySeverity.MEDIUM: 0.5,
                EmergencySeverity.HIGH: 0.8,
                EmergencySeverity.CRITICAL: 0.95,
                EmergencySeverity.LIFE_THREATENING: 1.0,
            }

            return {
                "severity_score": severity_scores.get(event.severity, 0.5),
                "time_score": timestamp,
                "location_score": (latitude + longitude)
                / 2,  # Простая нормализация
                "type_score": type_scores.get(event.emergency_type, 0.5),
                "latitude": latitude,
                "longitude": longitude,
                "timestamp": timestamp,
                "type": event.emergency_type.value,
                "severity": event.severity.value,
            }

        except Exception as e:
            self.logger.error(f"Ошибка подготовки данных события: {e}")
            return {}

    def analyze_events_batch(
        self, events: List[EmergencyEvent]
    ) -> List[Dict[str, Any]]:
        """
        Проанализировать пакет событий

        Args:
            events: Список событий для анализа

        Returns:
            List[Dict[str, Any]]: Результаты анализа
        """
        try:
            if not events:
                return []

            # Измеряем производительность
            result, processing_time = (
                self.performance_analyzer.measure_response_time(
                    self._analyze_events_batch_internal, events
                )
            )

            # Записываем метрики
            self.performance_analyzer.record_metrics(
                processing_time, processing_time
            )

            return result

        except Exception as e:
            self.logger.error(f"Ошибка анализа пакета событий: {e}")
            return []

    def _analyze_events_batch_internal(
        self, events: List[EmergencyEvent]
    ) -> List[Dict[str, Any]]:
        """Внутренний метод анализа пакета событий"""
        try:
            results = []

            for event in events:
                analysis = self.analyze_event(event)
                results.append(analysis)

            return results

        except Exception as e:
            self.logger.error(f"Ошибка внутреннего анализа пакета: {e}")
            return []

    def get_analysis_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику анализа

        Returns:
            Dict[str, Any]: Статистика анализа
        """
        try:
            performance_stats = (
                self.performance_analyzer.get_performance_statistics()
            )

            return {
                "is_trained": self.is_trained,
                "training_data_size": len(self.training_data),
                "performance": performance_stats,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статистики анализа: {e}")
            return {}

    def get_performance_issues(self) -> List[str]:
        """
        Получить проблемы производительности

        Returns:
            List[str]: Список проблем
        """
        return self.performance_analyzer.check_performance_issues()

    def get_performance_recommendations(self) -> List[str]:
        """
        Получить рекомендации по производительности

        Returns:
            List[str]: Список рекомендаций
        """
        return self.performance_analyzer.get_performance_recommendations()

    def cleanup_old_data(self, days: int = 30) -> int:
        """
        Очистить старые данные

        Args:
            days: Количество дней для хранения

        Returns:
            int: Количество удаленных записей
        """
        try:
            # Очищаем метрики производительности
            cleaned_metrics = self.performance_analyzer.cleanup_old_metrics(
                days
            )

            # Очищаем данные обучения (если нужно)
            if days < 7:  # Если храним меньше недели
                old_count = len(self.training_data)
                self.training_data = []
                cleaned_training = old_count
            else:
                cleaned_training = 0

            total_cleaned = cleaned_metrics + cleaned_training
            self.logger.info(f"Очищено {total_cleaned} записей")
            return total_cleaned

        except Exception as e:
            self.logger.error(f"Ошибка очистки данных: {e}")
            return 0

    def start_analysis(self) -> bool:
        """Запуск анализа экстренных ситуаций"""
        try:
            self.is_running = True
            self.log_activity("Анализ экстренных ситуаций запущен")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка запуска анализа: {e}", "error")
            return False

    def stop_analysis(self) -> bool:
        """Остановка анализа экстренных ситуаций"""
        try:
            self.is_running = False
            self.log_activity("Анализ экстренных ситуаций остановлен")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка остановки анализа: {e}", "error")
            return False

    def get_analysis_info(self) -> Dict[str, Any]:
        """Получение информации об анализе экстренных ситуаций"""
        try:
            return {
                "is_running": getattr(self, 'is_running', False),
                "emergency_types": len(EmergencyType),
                "severity_levels": len(EmergencySeverity),
                "analyzed_events": len(getattr(self, 'analyzed_events', [])),
                "training_data_count": len(getattr(self, 'training_data', [])),
                "anomaly_detector_active": getattr(self, 'anomaly_detector', None) is not None,
                "pattern_recognizer_active": getattr(self, 'pattern_recognizer', None) is not None,
                "risk_analyzer_active": getattr(self, 'risk_analyzer', None) is not None,
                "performance_analyzer_active": getattr(self, 'performance_analyzer', None) is not None,
                "cluster_analyzer_active": getattr(self, 'cluster_analyzer', None) is not None,
            }
        except Exception as e:
            self.log_activity(f"Ошибка получения информации об анализе: {e}", "error")
            return {
                "is_running": False,
                "emergency_types": 0,
                "severity_levels": 0,
                "analyzed_events": 0,
                "training_data_count": 0,
                "anomaly_detector_active": False,
                "pattern_recognizer_active": False,
                "risk_analyzer_active": False,
                "performance_analyzer_active": False,
                "cluster_analyzer_active": False,
                "error": str(e),
            }
