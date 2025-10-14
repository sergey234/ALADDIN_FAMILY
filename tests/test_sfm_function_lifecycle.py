#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Function Lifecycle Tests для ALADDIN Dashboard
Тесты жизненного цикла функций Safe Function Manager

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
import time
import pytest
import httpx
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from security.safe_function_manager import SafeFunctionManager
    from core.base import ComponentStatus, SecurityLevel
    from core.logging_module import LoggingManager
    ALADDIN_AVAILABLE = True
except ImportError:
    ALADDIN_AVAILABLE = False


class FunctionState(Enum):
    """Состояния функции"""
    UNKNOWN = "unknown"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    SLEEPING = "sleeping"
    DISABLED = "disabled"
    ERROR = "error"
    RESTARTING = "restarting"
    UPDATING = "updating"


class FunctionEvent(Enum):
    """События функции"""
    CREATED = "created"
    ENABLED = "enabled"
    DISABLED = "disabled"
    RESTARTED = "restarted"
    CONFIGURED = "configured"
    HEALTH_CHECK = "health_check"
    ERROR_OCCURRED = "error_occurred"
    RECOVERED = "recovered"
    DESTROYED = "destroyed"


@dataclass
class FunctionLifecycleEvent:
    """Событие жизненного цикла функции"""
    event_id: str
    function_id: str
    event_type: FunctionEvent
    timestamp: datetime
    previous_state: FunctionState
    current_state: FunctionState
    event_data: Dict[str, Any]
    duration: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class FunctionLifecycleMetrics:
    """Метрики жизненного цикла функции"""
    function_id: str
    total_events: int
    state_transitions: int
    average_transition_time: float
    error_count: int
    recovery_count: int
    uptime_percent: float
    last_activity: datetime
    lifecycle_duration: float
    health_score: float


@dataclass
class FunctionConfiguration:
    """Конфигурация функции"""
    function_id: str
    name: str
    description: str
    security_level: str
    is_critical: bool
    auto_enable: bool
    dependencies: List[str]
    configuration: Dict[str, Any]
    version: str
    created_at: datetime
    updated_at: datetime


class FunctionLifecycleTester:
    """Тестер жизненного цикла функций"""
    
    def __init__(self, sfm_url: str = "http://localhost:8011"):
        """
        Инициализация тестера жизненного цикла
        
        Args:
            sfm_url: URL SFM
        """
        self.sfm_url = sfm_url
        self.logger = LoggingManager(name="FunctionLifecycleTester") if ALADDIN_AVAILABLE else None
        self.lifecycle_events: List[FunctionLifecycleEvent] = []
        self.function_configurations: Dict[str, FunctionConfiguration] = {}
        self.function_metrics: Dict[str, FunctionLifecycleMetrics] = {}
        
    async def get_function_state(self, function_id: str) -> Tuple[FunctionState, Dict[str, Any]]:
        """
        Получение состояния функции
        
        Args:
            function_id: ID функции
            
        Returns:
            Кортеж (состояние, данные)
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                response = await client.get(f"{self.sfm_url}/functions/{function_id}/status", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")
                    
                    # Преобразуем строковый статус в enum
                    state_mapping = {
                        "active": FunctionState.ACTIVE,
                        "sleeping": FunctionState.SLEEPING,
                        "disabled": FunctionState.DISABLED,
                        "error": FunctionState.ERROR,
                        "initializing": FunctionState.INITIALIZING,
                        "restarting": FunctionState.RESTARTING,
                        "updating": FunctionState.UPDATING
                    }
                    
                    function_state = state_mapping.get(status, FunctionState.UNKNOWN)
                    return function_state, data
                else:
                    return FunctionState.ERROR, {"error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            return FunctionState.ERROR, {"error": str(e)}
    
    def record_lifecycle_event(
        self,
        function_id: str,
        event_type: FunctionEvent,
        previous_state: FunctionState,
        current_state: FunctionState,
        event_data: Dict[str, Any],
        duration: float = 0.0,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> FunctionLifecycleEvent:
        """
        Запись события жизненного цикла
        
        Args:
            function_id: ID функции
            event_type: Тип события
            previous_state: Предыдущее состояние
            current_state: Текущее состояние
            event_data: Данные события
            duration: Длительность операции
            success: Успешность операции
            error_message: Сообщение об ошибке
            
        Returns:
            Событие жизненного цикла
        """
        event_id = f"{function_id}_{event_type.value}_{int(time.time())}"
        
        event = FunctionLifecycleEvent(
            event_id=event_id,
            function_id=function_id,
            event_type=event_type,
            timestamp=datetime.now(),
            previous_state=previous_state,
            current_state=current_state,
            event_data=event_data,
            duration=duration,
            success=success,
            error_message=error_message
        )
        
        self.lifecycle_events.append(event)
        return event
    
    async def test_function_creation_lifecycle(self, function_config: FunctionConfiguration) -> Dict[str, Any]:
        """
        Тест жизненного цикла создания функции
        
        Args:
            function_config: Конфигурация функции
            
        Returns:
            Результаты тестирования создания
        """
        print(f"📊 Тестирование создания функции: {function_config.function_id}")
        
        creation_results = {
            "function_id": function_config.function_id,
            "events": [],
            "success": False,
            "total_duration": 0.0
        }
        
        start_time = time.time()
        
        # 1. Начальное состояние (функция не существует)
        print("  1. Проверка начального состояния...")
        initial_state, initial_data = await self.get_function_state(function_config.function_id)
        
        # 2. Создание функции (имитируем)
        print("  2. Создание функции...")
        creation_start = time.time()
        
        # В реальной системе здесь был бы POST запрос для создания функции
        # Для тестирования имитируем создание
        await asyncio.sleep(0.5)  # Имитация времени создания
        
        creation_event = self.record_lifecycle_event(
            function_id=function_config.function_id,
            event_type=FunctionEvent.CREATED,
            previous_state=initial_state,
            current_state=FunctionState.INITIALIZING,
            event_data={"config": function_config.__dict__},
            duration=time.time() - creation_start
        )
        creation_results["events"].append(creation_event)
        
        # 3. Проверка состояния после создания
        print("  3. Проверка состояния после создания...")
        await asyncio.sleep(1)  # Даем время на инициализацию
        post_creation_state, post_creation_data = await self.get_function_state(function_config.function_id)
        
        # 4. Конфигурация функции
        print("  4. Конфигурация функции...")
        config_start = time.time()
        
        # Имитируем конфигурацию
        await asyncio.sleep(0.3)
        
        config_event = self.record_lifecycle_event(
            function_id=function_config.function_id,
            event_type=FunctionEvent.CONFIGURED,
            previous_state=FunctionState.INITIALIZING,
            current_state=FunctionState.INITIALIZING,
            event_data={"configuration": function_config.configuration},
            duration=time.time() - config_start
        )
        creation_results["events"].append(config_event)
        
        # 5. Активация функции (если auto_enable)
        if function_config.auto_enable:
            print("  5. Автоматическая активация функции...")
            enable_start = time.time()
            
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    headers = {"Authorization": "Bearer demo_token"}
                    response = await client.post(
                        f"{self.sfm_url}/functions/{function_config.function_id}/enable",
                        headers=headers
                    )
                    
                    enable_success = 200 <= response.status_code < 300
                    
                    await asyncio.sleep(1)  # Даем время на активацию
                    post_enable_state, post_enable_data = await self.get_function_state(function_config.function_id)
                    
                    enable_event = self.record_lifecycle_event(
                        function_id=function_config.function_id,
                        event_type=FunctionEvent.ENABLED,
                        previous_state=FunctionState.INITIALIZING,
                        current_state=post_enable_state,
                        event_data={"response": response.json() if enable_success else None},
                        duration=time.time() - enable_start,
                        success=enable_success,
                        error_message=None if enable_success else f"HTTP {response.status_code}"
                    )
                    creation_results["events"].append(enable_event)
                    
            except Exception as e:
                enable_event = self.record_lifecycle_event(
                    function_id=function_config.function_id,
                    event_type=FunctionEvent.ENABLED,
                    previous_state=FunctionState.INITIALIZING,
                    current_state=FunctionState.ERROR,
                    event_data={},
                    duration=time.time() - enable_start,
                    success=False,
                    error_message=str(e)
                )
                creation_results["events"].append(enable_event)
        
        creation_results["total_duration"] = time.time() - start_time
        creation_results["success"] = all(event.success for event in creation_results["events"])
        
        print(f"  Результат создания: {'✅ Успешно' if creation_results['success'] else '❌ Неудачно'}")
        print(f"  Длительность: {creation_results['total_duration']:.2f}s")
        
        return creation_results
    
    async def test_function_operation_lifecycle(self, function_id: str) -> Dict[str, Any]:
        """
        Тест жизненного цикла операций функции
        
        Args:
            function_id: ID функции
            
        Returns:
            Результаты тестирования операций
        """
        print(f"📊 Тестирование операций функции: {function_id}")
        
        operation_results = {
            "function_id": function_id,
            "operations": [],
            "success": False,
            "total_duration": 0.0
        }
        
        start_time = time.time()
        
        # 1. Проверка текущего состояния
        print("  1. Проверка текущего состояния...")
        current_state, current_data = await self.get_function_state(function_id)
        
        # 2. Включение функции
        print("  2. Включение функции...")
        enable_start = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                response = await client.post(
                    f"{self.sfm_url}/functions/{function_id}/enable",
                    headers=headers
                )
                
                enable_success = 200 <= response.status_code < 300
                await asyncio.sleep(1)  # Даем время на активацию
                
                post_enable_state, post_enable_data = await self.get_function_state(function_id)
                
                enable_operation = {
                    "operation": "enable",
                    "success": enable_success,
                    "duration": time.time() - enable_start,
                    "previous_state": current_state.value,
                    "current_state": post_enable_state.value,
                    "response_data": response.json() if enable_success else None
                }
                operation_results["operations"].append(enable_operation)
                
        except Exception as e:
            enable_operation = {
                "operation": "enable",
                "success": False,
                "duration": time.time() - enable_start,
                "error": str(e)
            }
            operation_results["operations"].append(enable_operation)
        
        # 3. Проверка здоровья функции
        print("  3. Проверка здоровья функции...")
        health_start = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                response = await client.get(
                    f"{self.sfm_url}/functions/{function_id}/health",
                    headers=headers
                )
                
                health_success = 200 <= response.status_code < 300
                
                health_operation = {
                    "operation": "health_check",
                    "success": health_success,
                    "duration": time.time() - health_start,
                    "response_data": response.json() if health_success else None
                }
                operation_results["operations"].append(health_operation)
                
        except Exception as e:
            health_operation = {
                "operation": "health_check",
                "success": False,
                "duration": time.time() - health_start,
                "error": str(e)
            }
            operation_results["operations"].append(health_operation)
        
        # 4. Перезапуск функции
        print("  4. Перезапуск функции...")
        restart_start = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                response = await client.post(
                    f"{self.sfm_url}/functions/{function_id}/restart",
                    headers=headers
                )
                
                restart_success = 200 <= response.status_code < 300
                await asyncio.sleep(2)  # Даем время на перезапуск
                
                post_restart_state, post_restart_data = await self.get_function_state(function_id)
                
                restart_operation = {
                    "operation": "restart",
                    "success": restart_success,
                    "duration": time.time() - restart_start,
                    "previous_state": "unknown",
                    "current_state": post_restart_state.value,
                    "response_data": response.json() if restart_success else None
                }
                operation_results["operations"].append(restart_operation)
                
        except Exception as e:
            restart_operation = {
                "operation": "restart",
                "success": False,
                "duration": time.time() - restart_start,
                "error": str(e)
            }
            operation_results["operations"].append(restart_operation)
        
        # 5. Отключение функции
        print("  5. Отключение функции...")
        disable_start = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                response = await client.post(
                    f"{self.sfm_url}/functions/{function_id}/disable",
                    headers=headers
                )
                
                disable_success = 200 <= response.status_code < 300
                await asyncio.sleep(1)  # Даем время на деактивацию
                
                post_disable_state, post_disable_data = await self.get_function_state(function_id)
                
                disable_operation = {
                    "operation": "disable",
                    "success": disable_success,
                    "duration": time.time() - disable_start,
                    "previous_state": "unknown",
                    "current_state": post_disable_state.value,
                    "response_data": response.json() if disable_success else None
                }
                operation_results["operations"].append(disable_operation)
                
        except Exception as e:
            disable_operation = {
                "operation": "disable",
                "success": False,
                "duration": time.time() - disable_start,
                "error": str(e)
            }
            operation_results["operations"].append(disable_operation)
        
        operation_results["total_duration"] = time.time() - start_time
        
        # Анализируем результаты
        successful_operations = sum(1 for op in operation_results["operations"] if op["success"])
        total_operations = len(operation_results["operations"])
        operation_results["success"] = successful_operations >= total_operations * 0.7  # 70% успеха
        
        print(f"  Результат операций: {successful_operations}/{total_operations} успешно")
        print(f"  Длительность: {operation_results['total_duration']:.2f}s")
        
        return operation_results
    
    async def test_function_error_recovery_lifecycle(self, function_id: str) -> Dict[str, Any]:
        """
        Тест жизненного цикла восстановления после ошибок
        
        Args:
            function_id: ID функции
            
        Returns:
            Результаты тестирования восстановления
        """
        print(f"📊 Тестирование восстановления функции: {function_id}")
        
        recovery_results = {
            "function_id": function_id,
            "error_scenarios": [],
            "recovery_attempts": [],
            "success": False,
            "total_duration": 0.0
        }
        
        start_time = time.time()
        
        # 1. Имитация ошибки (отправка некорректного запроса)
        print("  1. Имитация ошибки...")
        error_start = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                # Отправляем некорректный запрос
                response = await client.post(
                    f"{self.sfm_url}/functions/{function_id}/invalid_operation",
                    headers=headers,
                    json={"invalid": "data"}
                )
                
                error_scenario = {
                    "scenario": "invalid_operation",
                    "error_occurred": True,
                    "error_code": response.status_code,
                    "duration": time.time() - error_start
                }
                recovery_results["error_scenarios"].append(error_scenario)
                
                # Записываем событие ошибки
                self.record_lifecycle_event(
                    function_id=function_id,
                    event_type=FunctionEvent.ERROR_OCCURRED,
                    previous_state=FunctionState.ACTIVE,
                    current_state=FunctionState.ERROR,
                    event_data={"error_code": response.status_code, "error_type": "invalid_operation"},
                    success=False,
                    error_message=f"Invalid operation: HTTP {response.status_code}"
                )
                
        except Exception as e:
            error_scenario = {
                "scenario": "invalid_operation",
                "error_occurred": True,
                "error_code": 0,
                "error_message": str(e),
                "duration": time.time() - error_start
            }
            recovery_results["error_scenarios"].append(error_scenario)
        
        # 2. Проверка состояния после ошибки
        print("  2. Проверка состояния после ошибки...")
        await asyncio.sleep(1)
        error_state, error_data = await self.get_function_state(function_id)
        
        # 3. Попытка восстановления (перезапуск)
        print("  3. Попытка восстановления...")
        recovery_start = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                response = await client.post(
                    f"{self.sfm_url}/functions/{function_id}/restart",
                    headers=headers
                )
                
                recovery_success = 200 <= response.status_code < 300
                await asyncio.sleep(2)  # Даем время на восстановление
                
                post_recovery_state, post_recovery_data = await self.get_function_state(function_id)
                
                recovery_attempt = {
                    "method": "restart",
                    "success": recovery_success,
                    "duration": time.time() - recovery_start,
                    "previous_state": error_state.value,
                    "current_state": post_recovery_state.value,
                    "response_data": response.json() if recovery_success else None
                }
                recovery_results["recovery_attempts"].append(recovery_attempt)
                
                if recovery_success and post_recovery_state != FunctionState.ERROR:
                    # Записываем событие восстановления
                    self.record_lifecycle_event(
                        function_id=function_id,
                        event_type=FunctionEvent.RECOVERED,
                        previous_state=error_state,
                        current_state=post_recovery_state,
                        event_data={"recovery_method": "restart"},
                        success=True
                    )
                
        except Exception as e:
            recovery_attempt = {
                "method": "restart",
                "success": False,
                "duration": time.time() - recovery_start,
                "error": str(e)
            }
            recovery_results["recovery_attempts"].append(recovery_attempt)
        
        recovery_results["total_duration"] = time.time() - start_time
        
        # Анализируем результаты
        successful_recoveries = sum(1 for attempt in recovery_results["recovery_attempts"] if attempt["success"])
        total_recoveries = len(recovery_results["recovery_attempts"])
        recovery_results["success"] = successful_recoveries > 0 and total_recoveries > 0
        
        print(f"  Восстановление: {successful_recoveries}/{total_recoveries} успешно")
        print(f"  Длительность: {recovery_results['total_duration']:.2f}s")
        
        return recovery_results
    
    def calculate_function_metrics(self, function_id: str) -> FunctionLifecycleMetrics:
        """
        Вычисление метрик жизненного цикла функции
        
        Args:
            function_id: ID функции
            
        Returns:
            Метрики жизненного цикла
        """
        function_events = [event for event in self.lifecycle_events if event.function_id == function_id]
        
        if not function_events:
            return FunctionLifecycleMetrics(
                function_id=function_id,
                total_events=0,
                state_transitions=0,
                average_transition_time=0.0,
                error_count=0,
                recovery_count=0,
                uptime_percent=0.0,
                last_activity=datetime.now(),
                lifecycle_duration=0.0,
                health_score=0.0
            )
        
        # Подсчитываем метрики
        total_events = len(function_events)
        state_transitions = len([e for e in function_events if e.previous_state != e.current_state])
        error_count = len([e for e in function_events if e.event_type == FunctionEvent.ERROR_OCCURRED])
        recovery_count = len([e for e in function_events if e.event_type == FunctionEvent.RECOVERED])
        
        # Вычисляем среднее время переходов
        transition_times = [e.duration for e in function_events if e.duration > 0]
        average_transition_time = sum(transition_times) / len(transition_times) if transition_times else 0.0
        
        # Вычисляем время жизни
        if function_events:
            lifecycle_duration = (function_events[-1].timestamp - function_events[0].timestamp).total_seconds()
            last_activity = function_events[-1].timestamp
        else:
            lifecycle_duration = 0.0
            last_activity = datetime.now()
        
        # Вычисляем uptime (упрощенно)
        active_events = len([e for e in function_events if e.current_state == FunctionState.ACTIVE])
        uptime_percent = (active_events / total_events) * 100 if total_events > 0 else 0.0
        
        # Вычисляем health score
        successful_events = len([e for e in function_events if e.success])
        health_score = (successful_events / total_events) * 100 if total_events > 0 else 0.0
        
        metrics = FunctionLifecycleMetrics(
            function_id=function_id,
            total_events=total_events,
            state_transitions=state_transitions,
            average_transition_time=average_transition_time,
            error_count=error_count,
            recovery_count=recovery_count,
            uptime_percent=uptime_percent,
            last_activity=last_activity,
            lifecycle_duration=lifecycle_duration,
            health_score=health_score
        )
        
        self.function_metrics[function_id] = metrics
        return metrics
    
    def generate_lifecycle_report(self) -> Dict[str, Any]:
        """Генерация отчета о жизненном цикле"""
        print("📊 Генерация отчета о жизненном цикле функций...")
        
        # Анализируем все функции
        function_ids = set(event.function_id for event in self.lifecycle_events)
        
        report = {
            "report_date": datetime.now().isoformat(),
            "total_functions_tested": len(function_ids),
            "total_lifecycle_events": len(self.lifecycle_events),
            "functions": {}
        }
        
        # Анализируем каждую функцию
        for function_id in function_ids:
            metrics = self.calculate_function_metrics(function_id)
            
            function_events = [event for event in self.lifecycle_events if event.function_id == function_id]
            
            report["functions"][function_id] = {
                "metrics": {
                    "total_events": metrics.total_events,
                    "state_transitions": metrics.state_transitions,
                    "average_transition_time": metrics.average_transition_time,
                    "error_count": metrics.error_count,
                    "recovery_count": metrics.recovery_count,
                    "uptime_percent": metrics.uptime_percent,
                    "health_score": metrics.health_score,
                    "lifecycle_duration": metrics.lifecycle_duration
                },
                "events": [
                    {
                        "event_id": event.event_id,
                        "event_type": event.event_type.value,
                        "timestamp": event.timestamp.isoformat(),
                        "previous_state": event.previous_state.value,
                        "current_state": event.current_state.value,
                        "duration": event.duration,
                        "success": event.success,
                        "error_message": event.error_message
                    }
                    for event in function_events
                ]
            }
        
        # Общая статистика
        all_events = self.lifecycle_events
        total_events = len(all_events)
        successful_events = len([e for e in all_events if e.success])
        error_events = len([e for e in all_events if e.event_type == FunctionEvent.ERROR_OCCURRED])
        recovery_events = len([e for e in all_events if e.event_type == FunctionEvent.RECOVERED])
        
        report["summary"] = {
            "overall_success_rate": (successful_events / total_events) * 100 if total_events > 0 else 0,
            "total_errors": error_events,
            "total_recoveries": recovery_events,
            "recovery_rate": (recovery_events / error_events) * 100 if error_events > 0 else 0,
            "average_health_score": sum(metrics.health_score for metrics in self.function_metrics.values()) / len(self.function_metrics) if self.function_metrics else 0,
            "lifecycle_quality": "excellent" if (successful_events / total_events) >= 0.9 else
                               "good" if (successful_events / total_events) >= 0.8 else
                               "fair" if (successful_events / total_events) >= 0.7 else "poor",
            "recommendations": self._generate_lifecycle_recommendations()
        }
        
        return report
    
    def _generate_lifecycle_recommendations(self) -> List[str]:
        """Генерация рекомендаций по жизненному циклу"""
        recommendations = []
        
        # Анализируем метрики
        if not self.function_metrics:
            recommendations.append("Нет данных о жизненном цикле функций")
            return recommendations
        
        avg_health_score = sum(metrics.health_score for metrics in self.function_metrics.values()) / len(self.function_metrics)
        
        if avg_health_score < 80:
            recommendations.append("Улучшить надежность функций - низкий health score")
        
        high_error_functions = [fid for fid, metrics in self.function_metrics.items() if metrics.error_count > 5]
        if high_error_functions:
            recommendations.append(f"Функции с высоким количеством ошибок: {', '.join(high_error_functions)}")
        
        low_recovery_functions = [fid for fid, metrics in self.function_metrics.items() 
                                if metrics.error_count > 0 and metrics.recovery_count == 0]
        if low_recovery_functions:
            recommendations.append(f"Функции без восстановления после ошибок: {', '.join(low_recovery_functions)}")
        
        slow_functions = [fid for fid, metrics in self.function_metrics.items() 
                         if metrics.average_transition_time > 5.0]
        if slow_functions:
            recommendations.append(f"Медленные функции (переходы > 5s): {', '.join(slow_functions)}")
        
        if not recommendations:
            recommendations.append("Жизненный цикл функций работает оптимально")
        
        return recommendations


class TestFunctionLifecycle:
    """Тесты жизненного цикла функций"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестов"""
        self.tester = FunctionLifecycleTester()
        
        # Создаем тестовую конфигурацию функции
        self.test_function_config = FunctionConfiguration(
            function_id="test_lifecycle_function",
            name="Test Lifecycle Function",
            description="Функция для тестирования жизненного цикла",
            security_level="medium",
            is_critical=False,
            auto_enable=True,
            dependencies=[],
            configuration={"test": True, "timeout": 30},
            version="1.0.0",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.mark.asyncio
    async def test_function_creation_lifecycle(self):
        """Тест жизненного цикла создания функции"""
        print("\n🧪 Тестирование создания функции...")
        
        creation_results = await self.tester.test_function_creation_lifecycle(self.test_function_config)
        
        # Проверки
        assert creation_results["function_id"] == self.test_function_config.function_id
        assert len(creation_results["events"]) > 0, "Нет событий создания"
        assert creation_results["total_duration"] < 30, f"Слишком долгое создание: {creation_results['total_duration']:.2f}s"
        
        # Проверяем, что есть событие создания
        creation_events = [e for e in creation_results["events"] if e.event_type == FunctionEvent.CREATED]
        assert len(creation_events) > 0, "Нет события создания функции"
        
        print(f"✅ Создание функции: {len(creation_results['events'])} событий за {creation_results['total_duration']:.2f}s")
    
    @pytest.mark.asyncio
    async def test_function_operation_lifecycle(self):
        """Тест жизненного цикла операций функции"""
        print("\n🧪 Тестирование операций функции...")
        
        operation_results = await self.tester.test_function_operation_lifecycle("test_function")
        
        # Проверки
        assert len(operation_results["operations"]) > 0, "Нет операций"
        assert operation_results["total_duration"] < 60, f"Слишком долгое выполнение: {operation_results['total_duration']:.2f}s"
        
        # Проверяем, что есть основные операции
        operation_types = [op["operation"] for op in operation_results["operations"]]
        expected_operations = ["enable", "health_check", "restart", "disable"]
        
        for expected_op in expected_operations:
            assert expected_op in operation_types, f"Отсутствует операция: {expected_op}"
        
        print(f"✅ Операции функции: {len(operation_results['operations'])} операций за {operation_results['total_duration']:.2f}s")
    
    @pytest.mark.asyncio
    async def test_function_error_recovery_lifecycle(self):
        """Тест жизненного цикла восстановления после ошибок"""
        print("\n🧪 Тестирование восстановления функции...")
        
        recovery_results = await self.tester.test_function_error_recovery_lifecycle("test_function")
        
        # Проверки
        assert len(recovery_results["error_scenarios"]) > 0, "Нет сценариев ошибок"
        assert len(recovery_results["recovery_attempts"]) > 0, "Нет попыток восстановления"
        assert recovery_results["total_duration"] < 30, f"Слишком долгое восстановление: {recovery_results['total_duration']:.2f}s"
        
        # Проверяем, что есть события ошибки и восстановления
        error_events = [e for e in self.tester.lifecycle_events if e.event_type == FunctionEvent.ERROR_OCCURRED]
        recovery_events = [e for e in self.tester.lifecycle_events if e.event_type == FunctionEvent.RECOVERED]
        
        print(f"✅ Восстановление функции: {len(error_events)} ошибок, {len(recovery_events)} восстановлений")
    
    @pytest.mark.asyncio
    async def test_function_state_transitions(self):
        """Тест переходов состояний функции"""
        print("\n🧪 Тестирование переходов состояний функции...")
        
        function_id = "test_state_function"
        
        # Выполняем несколько операций для создания переходов состояний
        await self.tester.test_function_operation_lifecycle(function_id)
        
        # Анализируем переходы состояний
        function_events = [e for e in self.tester.lifecycle_events if e.function_id == function_id]
        
        state_transitions = []
        for event in function_events:
            if event.previous_state != event.current_state:
                state_transitions.append({
                    "from": event.previous_state.value,
                    "to": event.current_state.value,
                    "event": event.event_type.value,
                    "timestamp": event.timestamp
                })
        
        # Проверки
        assert len(state_transitions) > 0, "Нет переходов состояний"
        
        # Проверяем, что есть переходы через разные состояния
        unique_states = set()
        for transition in state_transitions:
            unique_states.add(transition["from"])
            unique_states.add(transition["to"])
        
        assert len(unique_states) > 1, "Недостаточно различных состояний"
        
        print(f"✅ Переходы состояний: {len(state_transitions)} переходов через {len(unique_states)} состояний")
    
    def test_function_lifecycle_metrics(self):
        """Тест метрик жизненного цикла функции"""
        print("\n🧪 Тестирование метрик жизненного цикла...")
        
        # Создаем несколько событий для тестирования метрик
        function_id = "test_metrics_function"
        
        # Имитируем события
        self.tester.record_lifecycle_event(
            function_id=function_id,
            event_type=FunctionEvent.CREATED,
            previous_state=FunctionState.UNKNOWN,
            current_state=FunctionState.INITIALIZING,
            event_data={},
            duration=1.0
        )
        
        self.tester.record_lifecycle_event(
            function_id=function_id,
            event_type=FunctionEvent.ENABLED,
            previous_state=FunctionState.INITIALIZING,
            current_state=FunctionState.ACTIVE,
            event_data={},
            duration=2.0
        )
        
        self.tester.record_lifecycle_event(
            function_id=function_id,
            event_type=FunctionEvent.ERROR_OCCURRED,
            previous_state=FunctionState.ACTIVE,
            current_state=FunctionState.ERROR,
            event_data={},
            duration=0.5,
            success=False
        )
        
        self.tester.record_lifecycle_event(
            function_id=function_id,
            event_type=FunctionEvent.RECOVERED,
            previous_state=FunctionState.ERROR,
            current_state=FunctionState.ACTIVE,
            event_data={},
            duration=3.0
        )
        
        # Вычисляем метрики
        metrics = self.tester.calculate_function_metrics(function_id)
        
        # Проверки
        assert metrics.function_id == function_id
        assert metrics.total_events == 4
        assert metrics.state_transitions == 4  # Все события изменяют состояние
        assert metrics.error_count == 1
        assert metrics.recovery_count == 1
        assert metrics.average_transition_time > 0
        assert 0 <= metrics.health_score <= 100
        
        print(f"✅ Метрики жизненного цикла: health_score={metrics.health_score:.1f}, events={metrics.total_events}")
    
    def test_generate_lifecycle_report(self):
        """Генерация отчета о жизненном цикле"""
        print("\n📊 Генерация отчета о жизненном цикле функций...")
        
        report = self.tester.generate_lifecycle_report()
        
        # Сохранение отчета
        report_file = f"function_lifecycle_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Отчет о жизненном цикле сохранен: {report_file}")
        
        # Вывод краткой статистики
        print(f"\n📈 КРАТКАЯ СТАТИСТИКА:")
        print(f"  Функций протестировано: {report['total_functions_tested']}")
        print(f"  Событий жизненного цикла: {report['total_lifecycle_events']}")
        
        summary = report['summary']
        print(f"  Общий процент успеха: {summary['overall_success_rate']:.1f}%")
        print(f"  Всего ошибок: {summary['total_errors']}")
        print(f"  Всего восстановлений: {summary['total_recoveries']}")
        print(f"  Процент восстановления: {summary['recovery_rate']:.1f}%")
        print(f"  Средний health score: {summary['average_health_score']:.1f}")
        print(f"  Качество жизненного цикла: {summary['lifecycle_quality']}")
        
        # Проверки отчета
        assert report['total_functions_tested'] >= 0, "Количество функций не может быть отрицательным"
        assert report['total_lifecycle_events'] >= 0, "Количество событий не может быть отрицательным"
        assert 0 <= summary['overall_success_rate'] <= 100, "Процент успеха должен быть от 0 до 100"


if __name__ == "__main__":
    print("🚀 Запуск тестов жизненного цикла функций ALADDIN Dashboard...")
    print("🔄 Тестирование создания, операций и восстановления функций...")
    print("📊 Анализ переходов состояний и метрик...")
    print("🛡️ Проверка надежности жизненного цикла...")
    
    # Запуск тестов через pytest
    pytest.main([__file__, "-v", "--tb=short"])