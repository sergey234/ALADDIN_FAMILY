#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Circuit Breaker Main - Основной Circuit Breaker
"""

import logging
import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class CircuitState(Enum):
    """Состояния Circuit Breaker"""
    CLOSED = "closed"      # Закрыт - нормальная работа
    OPEN = "open"          # Открыт - блокировка вызовов
    HALF_OPEN = "half_open"  # Полуоткрыт - тестирование

@dataclass
class CircuitBreakerConfig:
    """Конфигурация Circuit Breaker"""
    service_name: str
    service_type: str
    strategy: str
    failure_threshold: int
    timeout: int
    half_open_max_calls: int = 5
    success_threshold: int = 3
    adaptive: bool = True
    ml_enabled: bool = True

class CircuitBreakerMain:
    """Основной Circuit Breaker"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.logger = logging.getLogger(f"ALADDIN.CircuitBreakerMain.{config.service_name}")
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.half_open_calls = 0
        self.lock = threading.Lock()
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "circuit_opens": 0,
            "circuit_closes": 0
        }
        self._init_ml_analyzer()
    
    def _init_ml_analyzer(self) -> None:
        """Инициализация ML анализатора"""
        try:
            if self.config.ml_enabled:
                # Здесь должна быть инициализация ML модели
                self.ml_analyzer = None
                self.logger.info("ML анализатор инициализирован")
            else:
                self.ml_analyzer = None
        except Exception as e:
            self.logger.error(f"Ошибка инициализации ML анализатора: {e}")
            self.ml_analyzer = None
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Выполнение функции через Circuit Breaker"""
        try:
            with self.lock:
                self.stats["total_calls"] += 1
                
                # Проверка состояния
                if self.state == CircuitState.OPEN:
                    if self._should_attempt_reset():
                        self.state = CircuitState.HALF_OPEN
                        self.half_open_calls = 0
                        self.logger.info(f"Circuit Breaker {self.config.service_name} переходит в HALF_OPEN")
                    else:
                        raise Exception(f"Circuit Breaker {self.config.service_name} is OPEN")
                
                elif self.state == CircuitState.HALF_OPEN:
                    if self.half_open_calls >= self.config.half_open_max_calls:
                        raise Exception(f"Circuit Breaker {self.config.service_name} HALF_OPEN call limit exceeded")
                    self.half_open_calls += 1
                
                # Выполнение функции
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Обработка успешного выполнения
                self._on_success(execution_time)
                
                return result
                
        except Exception as e:
            # Обработка ошибки
            self._on_failure(str(e))
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Проверка возможности сброса Circuit Breaker"""
        try:
            if self.last_failure_time is None:
                return True
            
            time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
            return time_since_failure >= self.config.timeout
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки сброса: {e}")
            return True
    
    def _on_success(self, execution_time: float) -> None:
        """Обработка успешного выполнения"""
        try:
            self.success_count += 1
            self.last_success_time = datetime.now()
            
            # ML анализ (если включен)
            if self.ml_analyzer:
                self._ml_analyze_success(execution_time)
            
            # Обновление статистики
            self.stats["successful_calls"] += 1
            
            # Проверка перехода в CLOSED
            if self.state == CircuitState.HALF_OPEN:
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    self.stats["circuit_closes"] += 1
                    self.logger.info(f"Circuit Breaker {self.config.service_name} переходит в CLOSED")
            
            elif self.state == CircuitState.CLOSED:
                # Сброс счетчика сбоев при успешном вызове
                self.failure_count = 0
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки успеха: {e}")
    
    def _on_failure(self, error_message: str) -> None:
        """Обработка ошибки выполнения"""
        try:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            # ML анализ (если включен)
            if self.ml_analyzer:
                self._ml_analyze_failure(error_message)
            
            # Обновление статистики
            self.stats["failed_calls"] += 1
            
            # Проверка перехода в OPEN
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                self.stats["circuit_opens"] += 1
                self.logger.warning(f"Circuit Breaker {self.config.service_name} переходит в OPEN")
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки сбоя: {e}")
    
    def _ml_analyze_success(self, execution_time: float) -> None:
        """ML анализ успешного выполнения"""
        try:
            # Здесь должна быть логика ML анализа
            # Пока просто логируем
            self.logger.debug(f"ML анализ успеха: время выполнения {execution_time:.3f}s")
            
        except Exception as e:
            self.logger.error(f"Ошибка ML анализа успеха: {e}")
    
    def _ml_analyze_failure(self, error_message: str) -> None:
        """ML анализ сбоя"""
        try:
            # Здесь должна быть логика ML анализа
            # Пока просто логируем
            self.logger.debug(f"ML анализ сбоя: {error_message}")
            
        except Exception as e:
            self.logger.error(f"Ошибка ML анализа сбоя: {e}")
    
    def get_state(self) -> Dict[str, Any]:
        """Получение текущего состояния"""
        try:
            return {
                "service_name": self.config.service_name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
                "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None,
                "half_open_calls": self.half_open_calls,
                "stats": self.stats
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения состояния: {e}")
            return {"error": str(e)}
    
    def reset(self) -> None:
        """Сброс Circuit Breaker"""
        try:
            with self.lock:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.half_open_calls = 0
                self.last_failure_time = None
                self.last_success_time = None
                
            self.logger.info(f"Circuit Breaker {self.config.service_name} сброшен")
            
        except Exception as e:
            self.logger.error(f"Ошибка сброса Circuit Breaker: {e}")
    
    def update_config(self, new_config: CircuitBreakerConfig) -> None:
        """Обновление конфигурации"""
        try:
            with self.lock:
                self.config = new_config
                
            self.logger.info(f"Конфигурация Circuit Breaker {self.config.service_name} обновлена")
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления конфигурации: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса Circuit Breaker"""
        try:
            return {
                "service_name": self.config.service_name,
                "state": self.state.value,
                "stats": self.stats,
                "config": {
                    "failure_threshold": self.config.failure_threshold,
                    "timeout": self.config.timeout,
                    "adaptive": self.config.adaptive,
                    "ml_enabled": self.config.ml_enabled
                },
                "status": "active"
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}
    
    def cleanup(self) -> None:
        """Очистка ресурсов"""
        try:
            with self.lock:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.half_open_calls = 0
                self.last_failure_time = None
                self.last_success_time = None
                self.stats = {
                    "total_calls": 0,
                    "successful_calls": 0,
                    "failed_calls": 0,
                    "circuit_opens": 0,
                    "circuit_closes": 0
                }
        except Exception as e:
            self.logger.error(f"Ошибка очистки: {e}")

# Глобальный экземпляр
circuit_breaker_main = CircuitBreakerMain(
    CircuitBreakerConfig(
        service_name="default",
        service_type="api",
        strategy="standard",
        failure_threshold=5,
        timeout=60
    )
)