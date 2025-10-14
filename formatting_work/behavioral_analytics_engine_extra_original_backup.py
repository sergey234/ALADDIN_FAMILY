#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Behavioral Analytics Engine Extra - Дополнительные функции движка поведенческой аналитики
"""

import numpy as np
import logging
import time
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class QualityMetrics:
    """Метрики качества"""
    unit_tests: bool = True
    integration_tests: bool = True
    quality_tests: bool = True
    error_tests: bool = True

class BehavioralAnalyticsEngineExtra:
    """Дополнительные функции движка поведенческой аналитики"""
    
    def __init__(self):
        self.logger = logging.getLogger("ALADDIN.BehavioralAnalyticsEngineExtra")
        self.quality_metrics = QualityMetrics()
        self.performance_data = {}
        self.error_patterns = {}
        self.stats = {
            "data_validations": 0,
            "quality_checks": 0,
            "performance_analyses": 0,
            "error_detections": 0
        }
        self._init_quality_standards()
    
    def _init_quality_standards(self) -> None:
        """Инициализация стандартов качества"""
        try:
            self.quality_standards = {
                "data_completeness": 0.95,  # 95% полноты данных
                "data_accuracy": 0.98,      # 98% точности данных
                "response_time": 0.5,       # 500ms максимальное время отклика
                "error_rate": 0.01,         # 1% максимальная частота ошибок
                "availability": 0.999       # 99.9% доступность
            }
            self.logger.info("Стандарты качества инициализированы")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации стандартов качества: {e}")
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Получение метрик качества"""
        try:
            self.stats["quality_checks"] += 1
            
            metrics = {
                "unit_tests": self.quality_metrics.unit_tests,
                "integration_tests": self.quality_metrics.integration_tests,
                "quality_tests": self.quality_metrics.quality_tests,
                "error_tests": self.quality_metrics.error_tests,
                "standards": self.quality_standards,
                "performance": self._get_performance_metrics(),
                "timestamp": datetime.now().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Ошибка получения метрик качества: {e}")
            return {}
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Получение метрик производительности"""
        try:
            return {
                "data_validations": self.stats["data_validations"],
                "quality_checks": self.stats["quality_checks"],
                "performance_analyses": self.stats["performance_analyses"],
                "error_detections": self.stats["error_detections"],
                "avg_response_time": self._calculate_avg_response_time(),
                "error_rate": self._calculate_error_rate()
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения метрик производительности: {e}")
            return {}
    
    def _calculate_avg_response_time(self) -> float:
        """Расчет среднего времени отклика"""
        try:
            if not self.performance_data:
                return 0.0
            
            response_times = [
                data.get("response_time", 0) 
                for data in self.performance_data.values()
            ]
            
            return sum(response_times) / len(response_times) if response_times else 0.0
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета среднего времени отклика: {e}")
            return 0.0
    
    def _calculate_error_rate(self) -> float:
        """Расчет частоты ошибок"""
        try:
            if not self.performance_data:
                return 0.0
            
            total_operations = len(self.performance_data)
            error_operations = sum(
                1 for data in self.performance_data.values()
                if data.get("has_error", False)
            )
            
            return error_operations / total_operations if total_operations > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета частоты ошибок: {e}")
            return 0.0
    
    def validate_behavior_data(self, data: Dict[str, Any]) -> bool:
        """Валидация данных поведения"""
        try:
            self.stats["data_validations"] += 1
            
            # Проверка обязательных полей
            required_fields = ["user_id", "action", "timestamp", "context"]
            for field in required_fields:
                if field not in data:
                    self.logger.warning(f"Отсутствует обязательное поле: {field}")
                    return False
            
            # Проверка типов данных
            if not isinstance(data["user_id"], str):
                self.logger.warning("user_id должен быть строкой")
                return False
            
            if not isinstance(data["action"], str):
                self.logger.warning("action должен быть строкой")
                return False
            
            if not isinstance(data["timestamp"], (str, datetime)):
                self.logger.warning("timestamp должен быть строкой или datetime")
                return False
            
            # Проверка контекста
            context = data.get("context", {})
            if not isinstance(context, dict):
                self.logger.warning("context должен быть словарем")
                return False
            
            # Дополнительные проверки качества
            if self._check_data_quality(data):
                self.logger.info(f"Данные поведения для пользователя {data['user_id']} прошли валидацию")
                return True
            else:
                self.logger.warning(f"Данные поведения для пользователя {data['user_id']} не прошли проверку качества")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка валидации данных поведения: {e}")
            return False
    
    def _check_data_quality(self, data: Dict[str, Any]) -> bool:
        """Проверка качества данных"""
        try:
            # Проверка полноты данных
            completeness_score = self._calculate_completeness(data)
            if completeness_score < self.quality_standards["data_completeness"]:
                self.logger.warning(f"Низкая полнота данных: {completeness_score:.2f}")
                return False
            
            # Проверка точности данных
            accuracy_score = self._calculate_accuracy(data)
            if accuracy_score < self.quality_standards["data_accuracy"]:
                self.logger.warning(f"Низкая точность данных: {accuracy_score:.2f}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки качества данных: {e}")
            return False
    
    def _calculate_completeness(self, data: Dict[str, Any]) -> float:
        """Расчет полноты данных"""
        try:
            total_fields = len(data)
            non_empty_fields = sum(1 for value in data.values() if value is not None and value != "")
            return non_empty_fields / total_fields if total_fields > 0 else 0.0
        except Exception as e:
            self.logger.error(f"Ошибка расчета полноты данных: {e}")
            return 0.0
    
    def _calculate_accuracy(self, data: Dict[str, Any]) -> float:
        """Расчет точности данных"""
        try:
            # Простая проверка точности на основе валидности значений
            accuracy_score = 1.0
            
            # Проверка user_id
            if not data.get("user_id") or len(data["user_id"]) < 3:
                accuracy_score -= 0.2
            
            # Проверка action
            if not data.get("action") or len(data["action"]) < 2:
                accuracy_score -= 0.2
            
            # Проверка timestamp
            try:
                if isinstance(data.get("timestamp"), str):
                    datetime.fromisoformat(data["timestamp"])
                elif isinstance(data.get("timestamp"), datetime):
                    pass
                else:
                    accuracy_score -= 0.3
            except:
                accuracy_score -= 0.3
            
            return max(0.0, accuracy_score)
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета точности данных: {e}")
            return 0.0
    
    def analyze_performance(self, operation_id: str, start_time: float, end_time: float, 
                          success: bool, error_message: str = None) -> None:
        """Анализ производительности операции"""
        try:
            self.stats["performance_analyses"] += 1
            
            response_time = end_time - start_time
            
            self.performance_data[operation_id] = {
                "start_time": start_time,
                "end_time": end_time,
                "response_time": response_time,
                "success": success,
                "has_error": not success,
                "error_message": error_message,
                "timestamp": datetime.now().isoformat()
            }
            
            # Проверка на превышение стандартов
            if response_time > self.quality_standards["response_time"]:
                self.logger.warning(f"Операция {operation_id} превысила время отклика: {response_time:.3f}s")
            
            if not success:
                self.stats["error_detections"] += 1
                self._record_error_pattern(operation_id, error_message)
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа производительности: {e}")
    
    def _record_error_pattern(self, operation_id: str, error_message: str) -> None:
        """Запись паттерна ошибки"""
        try:
            if error_message:
                error_type = self._classify_error(error_message)
                if error_type not in self.error_patterns:
                    self.error_patterns[error_type] = {
                        "count": 0,
                        "operations": [],
                        "first_seen": datetime.now().isoformat()
                    }
                
                self.error_patterns[error_type]["count"] += 1
                self.error_patterns[error_type]["operations"].append(operation_id)
                
        except Exception as e:
            self.logger.error(f"Ошибка записи паттерна ошибки: {e}")
    
    def _classify_error(self, error_message: str) -> str:
        """Классификация ошибки"""
        try:
            error_lower = error_message.lower()
            
            if "timeout" in error_lower:
                return "timeout"
            elif "connection" in error_lower:
                return "connection"
            elif "permission" in error_lower or "access" in error_lower:
                return "permission"
            elif "validation" in error_lower:
                return "validation"
            elif "memory" in error_lower:
                return "memory"
            else:
                return "unknown"
                
        except Exception as e:
            self.logger.error(f"Ошибка классификации ошибки: {e}")
            return "unknown"
    
    def get_error_analysis(self) -> Dict[str, Any]:
        """Получение анализа ошибок"""
        try:
            return {
                "error_patterns": self.error_patterns,
                "total_errors": sum(pattern["count"] for pattern in self.error_patterns.values()),
                "most_common_error": max(
                    self.error_patterns.items(), 
                    key=lambda x: x[1]["count"]
                )[0] if self.error_patterns else None,
                "error_rate": self._calculate_error_rate()
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения анализа ошибок: {e}")
            return {}
    
    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса движка"""
        try:
            return {
                "data_validations": self.stats["data_validations"],
                "quality_checks": self.stats["quality_checks"],
                "performance_analyses": self.stats["performance_analyses"],
                "error_detections": self.stats["error_detections"],
                "quality_standards": self.quality_standards,
                "error_patterns_count": len(self.error_patterns),
                "status": "active"
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}
    
    def cleanup(self) -> None:
        """Очистка ресурсов"""
        try:
            self.performance_data.clear()
            self.error_patterns.clear()
            self.stats = {
                "data_validations": 0,
                "quality_checks": 0,
                "performance_analyses": 0,
                "error_detections": 0
            }
        except Exception as e:
            self.logger.error(f"Ошибка очистки: {e}")

# Глобальный экземпляр
behavioral_analytics_engine_extra = BehavioralAnalyticsEngineExtra()