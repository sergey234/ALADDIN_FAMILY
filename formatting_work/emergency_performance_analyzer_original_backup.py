#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализатор производительности для экстренных ситуаций
Применение Single Responsibility принципа
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .emergency_models import EmergencyEvent


@dataclass
class PerformanceMetrics:
    """Метрики производительности"""
    response_time: float
    processing_time: float
    memory_usage: float
    cpu_usage: float
    timestamp: datetime


class EmergencyPerformanceAnalyzer:
    """Анализатор производительности экстренного реагирования"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metrics_history: List[PerformanceMetrics] = []
        self.performance_thresholds = {
            'response_time': 5.0,  # секунды
            'processing_time': 2.0,  # секунды
            'memory_usage': 100.0,  # MB
            'cpu_usage': 80.0  # %
        }
    
    def measure_response_time(self, func, *args, **kwargs) -> tuple:
        """
        Измерить время отклика функции
        
        Args:
            func: Функция для измерения
            *args: Аргументы функции
            **kwargs: Именованные аргументы функции
            
        Returns:
            tuple: (результат функции, время выполнения)
        """
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            response_time = end_time - start_time
            self.logger.debug(f"Функция {func.__name__} выполнена за {response_time:.4f}с")
            
            return result, response_time
            
        except Exception as e:
            self.logger.error(f"Ошибка измерения времени отклика: {e}")
            return None, 0.0
    
    def measure_processing_time(self, events: List[EmergencyEvent]) -> float:
        """
        Измерить время обработки событий
        
        Args:
            events: Список событий для обработки
            
        Returns:
            float: Время обработки в секундах
        """
        try:
            start_time = time.time()
            
            # Симуляция обработки событий
            for event in events:
                self._process_event(event)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            self.logger.debug(f"Обработано {len(events)} событий за {processing_time:.4f}с")
            return processing_time
            
        except Exception as e:
            self.logger.error(f"Ошибка измерения времени обработки: {e}")
            return 0.0
    
    def _process_event(self, event: EmergencyEvent) -> None:
        """Обработать одно событие"""
        try:
            # Симуляция обработки
            time.sleep(0.001)  # 1мс на событие
        except Exception:
            pass
    
    def get_memory_usage(self) -> float:
        """
        Получить использование памяти
        
        Returns:
            float: Использование памяти в MB
        """
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024  # MB
        except ImportError:
            # Fallback если psutil недоступен
            return 0.0
        except Exception:
            return 0.0
    
    def get_cpu_usage(self) -> float:
        """
        Получить использование CPU
        
        Returns:
            float: Использование CPU в %
        """
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            # Fallback если psutil недоступен
            return 0.0
        except Exception:
            return 0.0
    
    def record_metrics(self, response_time: float, 
                      processing_time: float) -> None:
        """
        Записать метрики производительности
        
        Args:
            response_time: Время отклика
            processing_time: Время обработки
        """
        try:
            metrics = PerformanceMetrics(
                response_time=response_time,
                processing_time=processing_time,
                memory_usage=self.get_memory_usage(),
                cpu_usage=self.get_cpu_usage(),
                timestamp=datetime.now()
            )
            
            self.metrics_history.append(metrics)
            
            # Ограничиваем историю последними 1000 записями
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
        except Exception as e:
            self.logger.error(f"Ошибка записи метрик: {e}")
    
    def get_performance_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Получить статистику производительности
        
        Args:
            hours: Количество часов для анализа
            
        Returns:
            Dict[str, Any]: Статистика производительности
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [
                m for m in self.metrics_history 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {}
            
            # Рассчитываем статистики
            response_times = [m.response_time for m in recent_metrics]
            processing_times = [m.processing_time for m in recent_metrics]
            memory_usage = [m.memory_usage for m in recent_metrics]
            cpu_usage = [m.cpu_usage for m in recent_metrics]
            
            return {
                'total_measurements': len(recent_metrics),
                'response_time': {
                    'avg': sum(response_times) / len(response_times),
                    'min': min(response_times),
                    'max': max(response_times),
                    'threshold': self.performance_thresholds['response_time']
                },
                'processing_time': {
                    'avg': sum(processing_times) / len(processing_times),
                    'min': min(processing_times),
                    'max': max(processing_times),
                    'threshold': self.performance_thresholds['processing_time']
                },
                'memory_usage': {
                    'avg': sum(memory_usage) / len(memory_usage),
                    'min': min(memory_usage),
                    'max': max(memory_usage),
                    'threshold': self.performance_thresholds['memory_usage']
                },
                'cpu_usage': {
                    'avg': sum(cpu_usage) / len(cpu_usage),
                    'min': min(cpu_usage),
                    'max': max(cpu_usage),
                    'threshold': self.performance_thresholds['cpu_usage']
                }
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики производительности: {e}")
            return {}
    
    def check_performance_issues(self) -> List[str]:
        """
        Проверить проблемы производительности
        
        Returns:
            List[str]: Список проблем
        """
        try:
            issues = []
            stats = self.get_performance_statistics(1)  # Последний час
            
            if not stats:
                return issues
            
            # Проверяем время отклика
            if stats['response_time']['avg'] > self.performance_thresholds['response_time']:
                issues.append(f"Высокое время отклика: {stats['response_time']['avg']:.2f}с")
            
            # Проверяем время обработки
            if stats['processing_time']['avg'] > self.performance_thresholds['processing_time']:
                issues.append(f"Высокое время обработки: {stats['processing_time']['avg']:.2f}с")
            
            # Проверяем использование памяти
            if stats['memory_usage']['avg'] > self.performance_thresholds['memory_usage']:
                issues.append(f"Высокое использование памяти: {stats['memory_usage']['avg']:.2f}MB")
            
            # Проверяем использование CPU
            if stats['cpu_usage']['avg'] > self.performance_thresholds['cpu_usage']:
                issues.append(f"Высокое использование CPU: {stats['cpu_usage']['avg']:.2f}%")
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки проблем производительности: {e}")
            return []
    
    def get_performance_recommendations(self) -> List[str]:
        """
        Получить рекомендации по улучшению производительности
        
        Returns:
            List[str]: Список рекомендаций
        """
        try:
            recommendations = []
            issues = self.check_performance_issues()
            
            if not issues:
                recommendations.append("Производительность в норме")
                return recommendations
            
            # Рекомендации на основе проблем
            if any("время отклика" in issue for issue in issues):
                recommendations.extend([
                    "Оптимизировать алгоритмы обработки",
                    "Использовать кэширование",
                    "Рассмотреть асинхронную обработку"
                ])
            
            if any("время обработки" in issue for issue in issues):
                recommendations.extend([
                    "Разбить обработку на более мелкие задачи",
                    "Использовать параллельную обработку",
                    "Оптимизировать структуры данных"
                ])
            
            if any("память" in issue for issue in issues):
                recommendations.extend([
                    "Освобождать неиспользуемые ресурсы",
                    "Использовать генераторы вместо списков",
                    "Рассмотреть использование слабых ссылок"
                ])
            
            if any("CPU" in issue for issue in issues):
                recommendations.extend([
                    "Оптимизировать циклы и условия",
                    "Использовать более эффективные алгоритмы",
                    "Рассмотреть использование Cython или Numba"
                ])
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Ошибка получения рекомендаций: {e}")
            return ["Ошибка анализа производительности"]
    
    def cleanup_old_metrics(self, days: int = 7) -> int:
        """
        Очистить старые метрики
        
        Args:
            days: Количество дней для хранения
            
        Returns:
            int: Количество удаленных записей
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            old_count = len(self.metrics_history)
            
            self.metrics_history = [
                m for m in self.metrics_history 
                if m.timestamp >= cutoff_time
            ]
            
            removed_count = old_count - len(self.metrics_history)
            self.logger.info(f"Удалено {removed_count} старых метрик")
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки метрик: {e}")
            return 0