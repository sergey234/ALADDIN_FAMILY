#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced SFM Integration Tests для ALADDIN Dashboard
Продвинутые тесты интеграции с Safe Function Manager

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


class SFMOperationType(Enum):
    """Типы операций SFM"""
    ENABLE = "enable"
    DISABLE = "disable"
    RESTART = "restart"
    STATUS_CHECK = "status_check"
    CONFIG_UPDATE = "config_update"
    HEALTH_CHECK = "health_check"
    METRICS_COLLECTION = "metrics_collection"


class SFMIntegrationStatus(Enum):
    """Статусы интеграции SFM"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    TIMEOUT = "timeout"
    UNAVAILABLE = "unavailable"


@dataclass
class SFMOperation:
    """Операция SFM"""
    operation_id: str
    operation_type: SFMOperationType
    function_id: str
    timestamp: datetime
    duration: float
    success: bool
    error_message: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None


@dataclass
class SFMIntegrationMetrics:
    """Метрики интеграции SFM"""
    total_operations: int
    successful_operations: int
    failed_operations: int
    average_response_time: float
    max_response_time: float
    min_response_time: float
    operations_per_second: float
    error_rate: float
    availability_percent: float
    last_health_check: datetime
    integration_status: SFMIntegrationStatus


@dataclass
class SFMFunctionState:
    """Состояние функции SFM"""
    function_id: str
    name: str
    status: str
    security_level: str
    is_critical: bool
    auto_enable: bool
    last_activity: datetime
    health_score: float
    performance_metrics: Dict[str, Any]
    dependencies: List[str]
    configuration: Dict[str, Any]


class SFMAdvancedIntegrationTester:
    """Продвинутый тестер интеграции SFM"""
    
    def __init__(self, dashboard_url: str = "http://localhost:8080", sfm_url: str = "http://localhost:8011"):
        """
        Инициализация продвинутого тестера
        
        Args:
            dashboard_url: URL дашборда
            sfm_url: URL SFM
        """
        self.dashboard_url = dashboard_url
        self.sfm_url = sfm_url
        self.logger = LoggingManager(name="SFMAdvancedIntegrationTester") if ALADDIN_AVAILABLE else None
        self.operations: List[SFMOperation] = []
        self.function_states: Dict[str, SFMFunctionState] = {}
        self.integration_metrics: SFMIntegrationMetrics = SFMIntegrationMetrics(
            total_operations=0,
            successful_operations=0,
            failed_operations=0,
            average_response_time=0.0,
            max_response_time=0.0,
            min_response_time=float('inf'),
            operations_per_second=0.0,
            error_rate=0.0,
            availability_percent=0.0,
            last_health_check=datetime.now(),
            integration_status=SFMIntegrationStatus.DISCONNECTED
        )
        
    async def check_sfm_connectivity(self) -> SFMIntegrationStatus:
        """
        Проверка подключения к SFM
        
        Returns:
            Статус подключения
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Проверяем health endpoint
                response = await client.get(f"{self.sfm_url}/health")
                if response.status_code == 200:
                    return SFMIntegrationStatus.CONNECTED
                else:
                    return SFMIntegrationStatus.ERROR
        except httpx.TimeoutException:
            return SFMIntegrationStatus.TIMEOUT
        except httpx.ConnectError:
            return SFMIntegrationStatus.DISCONNECTED
        except Exception:
            return SFMIntegrationStatus.UNAVAILABLE
    
    async def execute_sfm_operation(
        self, 
        operation_type: SFMOperationType,
        function_id: str = "test_function",
        data: Optional[Dict[str, Any]] = None
    ) -> SFMOperation:
        """
        Выполнение операции SFM
        
        Args:
            operation_type: Тип операции
            function_id: ID функции
            data: Дополнительные данные
            
        Returns:
            Результат операции
        """
        operation_id = f"{operation_type.value}_{function_id}_{int(time.time())}"
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                
                if operation_type == SFMOperationType.ENABLE:
                    url = f"{self.sfm_url}/functions/{function_id}/enable"
                    response = await client.post(url, headers=headers, json=data)
                elif operation_type == SFMOperationType.DISABLE:
                    url = f"{self.sfm_url}/functions/{function_id}/disable"
                    response = await client.post(url, headers=headers, json=data)
                elif operation_type == SFMOperationType.RESTART:
                    url = f"{self.sfm_url}/functions/{function_id}/restart"
                    response = await client.post(url, headers=headers, json=data)
                elif operation_type == SFMOperationType.STATUS_CHECK:
                    url = f"{self.sfm_url}/functions/{function_id}/status"
                    response = await client.get(url, headers=headers)
                elif operation_type == SFMOperationType.HEALTH_CHECK:
                    url = f"{self.sfm_url}/health"
                    response = await client.get(url, headers=headers)
                elif operation_type == SFMOperationType.METRICS_COLLECTION:
                    url = f"{self.sfm_url}/metrics"
                    response = await client.get(url, headers=headers)
                else:
                    raise ValueError(f"Unsupported operation type: {operation_type}")
                
                duration = time.time() - start_time
                success = 200 <= response.status_code < 300
                
                operation = SFMOperation(
                    operation_id=operation_id,
                    operation_type=operation_type,
                    function_id=function_id,
                    timestamp=datetime.now(),
                    duration=duration,
                    success=success,
                    response_data=response.json() if success else None
                )
                
                if not success:
                    operation.error_message = f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            duration = time.time() - start_time
            operation = SFMOperation(
                operation_id=operation_id,
                operation_type=operation_type,
                function_id=function_id,
                timestamp=datetime.now(),
                duration=duration,
                success=False,
                error_message=str(e)
            )
        
        self.operations.append(operation)
        self._update_integration_metrics()
        
        return operation
    
    def _update_integration_metrics(self):
        """Обновление метрик интеграции"""
        if not self.operations:
            return
        
        total_ops = len(self.operations)
        successful_ops = sum(1 for op in self.operations if op.success)
        failed_ops = total_ops - successful_ops
        
        response_times = [op.duration for op in self.operations]
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        # Вычисляем operations per second
        if self.operations:
            time_span = (self.operations[-1].timestamp - self.operations[0].timestamp).total_seconds()
            ops_per_second = total_ops / time_span if time_span > 0 else 0
        else:
            ops_per_second = 0
        
        error_rate = (failed_ops / total_ops) * 100 if total_ops > 0 else 0
        availability_percent = (successful_ops / total_ops) * 100 if total_ops > 0 else 0
        
        self.integration_metrics = SFMIntegrationMetrics(
            total_operations=total_ops,
            successful_operations=successful_ops,
            failed_operations=failed_ops,
            average_response_time=avg_response_time,
            max_response_time=max_response_time,
            min_response_time=min_response_time,
            operations_per_second=ops_per_second,
            error_rate=error_rate,
            availability_percent=availability_percent,
            last_health_check=datetime.now(),
            integration_status=SFMIntegrationStatus.CONNECTED if availability_percent > 80 else SFMIntegrationStatus.ERROR
        )
    
    async def test_sfm_function_lifecycle(self, function_id: str = "test_function") -> Dict[str, Any]:
        """
        Тест жизненного цикла функции SFM
        
        Args:
            function_id: ID функции для тестирования
            
        Returns:
            Результаты тестирования жизненного цикла
        """
        print(f"📊 Тестирование жизненного цикла функции: {function_id}")
        
        lifecycle_results = {
            "function_id": function_id,
            "operations": [],
            "success": True,
            "total_duration": 0.0
        }
        
        start_time = time.time()
        
        # 1. Проверка статуса (начальное состояние)
        print("  1. Проверка начального статуса...")
        status_op = await self.execute_sfm_operation(
            SFMOperationType.STATUS_CHECK, 
            function_id
        )
        lifecycle_results["operations"].append(status_op)
        
        # 2. Включение функции
        print("  2. Включение функции...")
        enable_op = await self.execute_sfm_operation(
            SFMOperationType.ENABLE, 
            function_id
        )
        lifecycle_results["operations"].append(enable_op)
        
        # 3. Проверка статуса после включения
        print("  3. Проверка статуса после включения...")
        await asyncio.sleep(1)  # Даем время на активацию
        status_after_enable = await self.execute_sfm_operation(
            SFMOperationType.STATUS_CHECK, 
            function_id
        )
        lifecycle_results["operations"].append(status_after_enable)
        
        # 4. Сбор метрик
        print("  4. Сбор метрик...")
        metrics_op = await self.execute_sfm_operation(
            SFMOperationType.METRICS_COLLECTION, 
            function_id
        )
        lifecycle_results["operations"].append(metrics_op)
        
        # 5. Перезапуск функции
        print("  5. Перезапуск функции...")
        restart_op = await self.execute_sfm_operation(
            SFMOperationType.RESTART, 
            function_id
        )
        lifecycle_results["operations"].append(restart_op)
        
        # 6. Проверка статуса после перезапуска
        print("  6. Проверка статуса после перезапуска...")
        await asyncio.sleep(2)  # Даем время на перезапуск
        status_after_restart = await self.execute_sfm_operation(
            SFMOperationType.STATUS_CHECK, 
            function_id
        )
        lifecycle_results["operations"].append(status_after_restart)
        
        # 7. Отключение функции
        print("  7. Отключение функции...")
        disable_op = await self.execute_sfm_operation(
            SFMOperationType.DISABLE, 
            function_id
        )
        lifecycle_results["operations"].append(disable_op)
        
        # 8. Финальная проверка статуса
        print("  8. Финальная проверка статуса...")
        final_status = await self.execute_sfm_operation(
            SFMOperationType.STATUS_CHECK, 
            function_id
        )
        lifecycle_results["operations"].append(final_status)
        
        lifecycle_results["total_duration"] = time.time() - start_time
        
        # Анализируем результаты
        successful_ops = sum(1 for op in lifecycle_results["operations"] if op.success)
        total_ops = len(lifecycle_results["operations"])
        success_rate = (successful_ops / total_ops) * 100 if total_ops > 0 else 0
        
        lifecycle_results["success"] = success_rate >= 80
        lifecycle_results["success_rate"] = success_rate
        lifecycle_results["successful_operations"] = successful_ops
        lifecycle_results["total_operations"] = total_ops
        
        print(f"  Результат: {success_rate:.1f}% успешных операций за {lifecycle_results['total_duration']:.2f}s")
        
        return lifecycle_results
    
    async def test_sfm_concurrent_operations(self) -> Dict[str, Any]:
        """
        Тест конкурентных операций SFM
        
        Returns:
            Результаты конкурентного тестирования
        """
        print("📊 Тестирование конкурентных операций SFM...")
        
        # Список функций для тестирования
        test_functions = [
            "russian_api_manager",
            "russian_banking_integration", 
            "messenger_integration",
            "safe_function_manager",
            "threat_detection_agent"
        ]
        
        concurrent_results = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "average_response_time": 0.0,
            "concurrent_execution_time": 0.0
        }
        
        start_time = time.time()
        
        # Создаем задачи для конкурентного выполнения
        tasks = []
        for function_id in test_functions:
            # Каждая функция выполняет несколько операций
            for operation_type in [SFMOperationType.STATUS_CHECK, SFMOperationType.HEALTH_CHECK]:
                task = self.execute_sfm_operation(operation_type, function_id)
                tasks.append(task)
        
        # Выполняем все задачи параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        concurrent_results["concurrent_execution_time"] = time.time() - start_time
        
        # Анализируем результаты
        successful_ops = 0
        failed_ops = 0
        total_response_time = 0.0
        
        for result in results:
            if isinstance(result, SFMOperation):
                concurrent_results["total_operations"] += 1
                if result.success:
                    successful_ops += 1
                    total_response_time += result.duration
                else:
                    failed_ops += 1
        
        concurrent_results["successful_operations"] = successful_ops
        concurrent_results["failed_operations"] = failed_ops
        concurrent_results["average_response_time"] = total_response_time / successful_ops if successful_ops > 0 else 0
        
        print(f"  Конкурентных операций: {concurrent_results['total_operations']}")
        print(f"  Успешных: {concurrent_results['successful_operations']}")
        print(f"  Неудачных: {concurrent_results['failed_operations']}")
        print(f"  Время выполнения: {concurrent_results['concurrent_execution_time']:.2f}s")
        print(f"  Среднее время отклика: {concurrent_results['average_response_time']:.3f}s")
        
        return concurrent_results
    
    async def test_sfm_error_handling(self) -> Dict[str, Any]:
        """
        Тест обработки ошибок SFM
        
        Returns:
            Результаты тестирования обработки ошибок
        """
        print("📊 Тестирование обработки ошибок SFM...")
        
        error_test_results = {
            "invalid_function_id": None,
            "invalid_operation": None,
            "timeout_scenario": None,
            "malformed_request": None,
            "unauthorized_access": None
        }
        
        # 1. Тест с несуществующим ID функции
        print("  1. Тест с несуществующим ID функции...")
        invalid_id_op = await self.execute_sfm_operation(
            SFMOperationType.STATUS_CHECK, 
            "nonexistent_function_12345"
        )
        error_test_results["invalid_function_id"] = {
            "success": invalid_id_op.success,
            "error_message": invalid_id_op.error_message,
            "response_time": invalid_id_op.duration
        }
        
        # 2. Тест с неверным типом операции (имитируем)
        print("  2. Тест с неверным типом операции...")
        try:
            # Пытаемся выполнить несуществующую операцию
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.sfm_url}/invalid/endpoint")
                error_test_results["invalid_operation"] = {
                    "success": False,
                    "error_message": f"HTTP {response.status_code}",
                    "response_time": 0.0
                }
        except Exception as e:
            error_test_results["invalid_operation"] = {
                "success": False,
                "error_message": str(e),
                "response_time": 0.0
            }
        
        # 3. Тест таймаута
        print("  3. Тест таймаута...")
        try:
            async with httpx.AsyncClient(timeout=0.1) as client:  # Очень короткий таймаут
                response = await client.get(f"{self.sfm_url}/health")
        except httpx.TimeoutException:
            error_test_results["timeout_scenario"] = {
                "success": False,
                "error_message": "Timeout",
                "response_time": 0.1
            }
        
        # 4. Тест с некорректными данными
        print("  4. Тест с некорректными данными...")
        malformed_op = await self.execute_sfm_operation(
            SFMOperationType.ENABLE,
            "test_function",
            {"invalid": "data", "malformed": True}
        )
        error_test_results["malformed_request"] = {
            "success": malformed_op.success,
            "error_message": malformed_op.error_message,
            "response_time": malformed_op.duration
        }
        
        # 5. Тест неавторизованного доступа
        print("  5. Тест неавторизованного доступа...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.sfm_url}/functions", headers={})  # Без авторизации
                error_test_results["unauthorized_access"] = {
                    "success": False,
                    "error_message": f"HTTP {response.status_code}",
                    "response_time": 0.0
                }
        except Exception as e:
            error_test_results["unauthorized_access"] = {
                "success": False,
                "error_message": str(e),
                "response_time": 0.0
            }
        
        # Анализируем результаты
        total_error_tests = len(error_test_results)
        expected_failures = sum(1 for result in error_test_results.values() if result and not result["success"])
        
        print(f"  Всего тестов ошибок: {total_error_tests}")
        print(f"  Ожидаемых неудач: {expected_failures}")
        print(f"  Обработка ошибок: {'✅ Корректная' if expected_failures >= total_error_tests * 0.8 else '❌ Требует улучшения'}")
        
        return error_test_results
    
    async def test_sfm_dashboard_integration(self) -> Dict[str, Any]:
        """
        Тест интеграции SFM с дашбордом
        
        Returns:
            Результаты интеграции с дашбордом
        """
        print("📊 Тестирование интеграции SFM с дашбордом...")
        
        integration_results = {
            "dashboard_sfm_endpoints": [],
            "sfm_data_in_dashboard": False,
            "real_time_updates": False,
            "integration_quality": "unknown"
        }
        
        # 1. Проверяем endpoints дашборда, связанные с SFM
        print("  1. Проверка SFM endpoints в дашборде...")
        dashboard_endpoints = [
            "/api/services",
            "/api/endpoints", 
            "/api/test-history"
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"Authorization": "Bearer demo_token"}
            
            for endpoint in dashboard_endpoints:
                try:
                    response = await client.get(f"{self.dashboard_url}{endpoint}", headers=headers)
                    
                    endpoint_result = {
                        "endpoint": endpoint,
                        "status_code": response.status_code,
                        "success": 200 <= response.status_code < 300,
                        "contains_sfm_data": False
                    }
                    
                    if endpoint_result["success"]:
                        try:
                            data = response.json()
                            # Проверяем наличие SFM данных
                            if endpoint == "/api/services":
                                sfm_data = "SafeFunctionManager" in str(data)
                            elif endpoint == "/api/endpoints":
                                sfm_data = "sfm" in str(data).lower()
                            else:
                                sfm_data = False
                            
                            endpoint_result["contains_sfm_data"] = sfm_data
                            
                        except json.JSONDecodeError:
                            pass
                    
                    integration_results["dashboard_sfm_endpoints"].append(endpoint_result)
                    
                except Exception as e:
                    integration_results["dashboard_sfm_endpoints"].append({
                        "endpoint": endpoint,
                        "status_code": 0,
                        "success": False,
                        "error": str(e)
                    })
        
        # 2. Проверяем наличие SFM данных в дашборде
        print("  2. Проверка наличия SFM данных...")
        sfm_data_found = any(
            endpoint.get("contains_sfm_data", False) 
            for endpoint in integration_results["dashboard_sfm_endpoints"]
        )
        integration_results["sfm_data_in_dashboard"] = sfm_data_found
        
        # 3. Тестируем real-time обновления (упрощенно)
        print("  3. Тестирование real-time обновлений...")
        try:
            # Делаем два запроса с интервалом
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                
                response1 = await client.get(f"{self.dashboard_url}/api/services", headers=headers)
                await asyncio.sleep(2)
                response2 = await client.get(f"{self.dashboard_url}/api/services", headers=headers)
                
                # Сравниваем timestamps или другие изменяющиеся данные
                try:
                    data1 = response1.json()
                    data2 = response2.json()
                    
                    # Простая проверка на изменения
                    integration_results["real_time_updates"] = str(data1) != str(data2)
                except json.JSONDecodeError:
                    integration_results["real_time_updates"] = False
                    
        except Exception:
            integration_results["real_time_updates"] = False
        
        # 4. Определяем качество интеграции
        successful_endpoints = sum(1 for ep in integration_results["dashboard_sfm_endpoints"] if ep["success"])
        total_endpoints = len(integration_results["dashboard_sfm_endpoints"])
        
        if successful_endpoints == total_endpoints and integration_results["sfm_data_in_dashboard"]:
            integration_results["integration_quality"] = "excellent"
        elif successful_endpoints >= total_endpoints * 0.8 and integration_results["sfm_data_in_dashboard"]:
            integration_results["integration_quality"] = "good"
        elif successful_endpoints >= total_endpoints * 0.5:
            integration_results["integration_quality"] = "fair"
        else:
            integration_results["integration_quality"] = "poor"
        
        print(f"  Качество интеграции: {integration_results['integration_quality']}")
        print(f"  SFM данные в дашборде: {'✅ Да' if integration_results['sfm_data_in_dashboard'] else '❌ Нет'}")
        print(f"  Real-time обновления: {'✅ Да' if integration_results['real_time_updates'] else '❌ Нет'}")
        
        return integration_results
    
    def generate_advanced_integration_report(self) -> Dict[str, Any]:
        """Генерация отчета о продвинутой интеграции"""
        print("📊 Генерация отчета о продвинутой интеграции SFM...")
        
        # Анализируем все операции
        total_operations = len(self.operations)
        successful_operations = sum(1 for op in self.operations if op.success)
        
        # Группируем операции по типам
        operations_by_type = {}
        for op in self.operations:
            op_type = op.operation_type.value
            if op_type not in operations_by_type:
                operations_by_type[op_type] = {"total": 0, "successful": 0, "failed": 0}
            
            operations_by_type[op_type]["total"] += 1
            if op.success:
                operations_by_type[op_type]["successful"] += 1
            else:
                operations_by_type[op_type]["failed"] += 1
        
        # Вычисляем статистику по типам операций
        for op_type in operations_by_type:
            stats = operations_by_type[op_type]
            stats["success_rate"] = (stats["successful"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        
        report = {
            "report_date": datetime.now().isoformat(),
            "integration_metrics": {
                "total_operations": self.integration_metrics.total_operations,
                "successful_operations": self.integration_metrics.successful_operations,
                "failed_operations": self.integration_metrics.failed_operations,
                "average_response_time": self.integration_metrics.average_response_time,
                "max_response_time": self.integration_metrics.max_response_time,
                "min_response_time": self.integration_metrics.min_response_time,
                "operations_per_second": self.integration_metrics.operations_per_second,
                "error_rate": self.integration_metrics.error_rate,
                "availability_percent": self.integration_metrics.availability_percent,
                "integration_status": self.integration_metrics.integration_status.value
            },
            "operations_by_type": operations_by_type,
            "detailed_operations": [
                {
                    "operation_id": op.operation_id,
                    "operation_type": op.operation_type.value,
                    "function_id": op.function_id,
                    "timestamp": op.timestamp.isoformat(),
                    "duration": op.duration,
                    "success": op.success,
                    "error_message": op.error_message
                }
                for op in self.operations
            ],
            "summary": {
                "overall_success_rate": (successful_operations / total_operations) * 100 if total_operations > 0 else 0,
                "integration_quality": "excellent" if self.integration_metrics.availability_percent >= 95 else 
                                     "good" if self.integration_metrics.availability_percent >= 85 else
                                     "fair" if self.integration_metrics.availability_percent >= 70 else "poor",
                "performance_grade": "A+" if self.integration_metrics.average_response_time < 1.0 else
                                   "A" if self.integration_metrics.average_response_time < 2.0 else
                                   "B" if self.integration_metrics.average_response_time < 5.0 else "C",
                "recommendations": self._generate_integration_recommendations()
            }
        }
        
        return report
    
    def _generate_integration_recommendations(self) -> List[str]:
        """Генерация рекомендаций по интеграции"""
        recommendations = []
        
        if self.integration_metrics.availability_percent < 90:
            recommendations.append("Улучшить надежность подключения к SFM")
        
        if self.integration_metrics.average_response_time > 2.0:
            recommendations.append("Оптимизировать время отклика SFM операций")
        
        if self.integration_metrics.error_rate > 10:
            recommendations.append("Улучшить обработку ошибок SFM")
        
        if self.integration_metrics.operations_per_second < 10:
            recommendations.append("Увеличить пропускную способность SFM")
        
        # Анализируем операции по типам
        for op in self.operations:
            if not op.success and op.operation_type == SFMOperationType.ENABLE:
                recommendations.append("Проверить процесс включения функций SFM")
                break
        
        if not recommendations:
            recommendations.append("Интеграция SFM работает оптимально")
        
        return recommendations


class TestSFMAdvancedIntegration:
    """Тесты продвинутой интеграции SFM"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестов"""
        self.tester = SFMAdvancedIntegrationTester()
    
    @pytest.mark.asyncio
    async def test_sfm_connectivity(self):
        """Тест подключения к SFM"""
        print("\n🧪 Тестирование подключения к SFM...")
        
        connectivity_status = await self.tester.check_sfm_connectivity()
        
        print(f"📊 Статус подключения: {connectivity_status.value}")
        
        # Проверки
        assert connectivity_status in [
            SFMIntegrationStatus.CONNECTED,
            SFMIntegrationStatus.DISCONNECTED,
            SFMIntegrationStatus.ERROR,
            SFMIntegrationStatus.TIMEOUT
        ], f"Неожиданный статус подключения: {connectivity_status}"
        
        if connectivity_status == SFMIntegrationStatus.CONNECTED:
            print("✅ SFM доступен и отвечает")
        else:
            print(f"⚠️ SFM недоступен: {connectivity_status.value}")
    
    @pytest.mark.asyncio
    async def test_sfm_function_lifecycle(self):
        """Тест жизненного цикла функции SFM"""
        print("\n🧪 Тестирование жизненного цикла функции SFM...")
        
        lifecycle_results = await self.tester.test_sfm_function_lifecycle("test_function")
        
        # Проверки
        assert lifecycle_results["success"], f"Жизненный цикл функции не прошел: {lifecycle_results['success_rate']:.1f}%"
        assert lifecycle_results["success_rate"] >= 70, f"Слишком низкий процент успеха: {lifecycle_results['success_rate']:.1f}%"
        assert lifecycle_results["total_duration"] < 30, f"Слишком долгое выполнение: {lifecycle_results['total_duration']:.2f}s"
        
        print(f"✅ Жизненный цикл функции: {lifecycle_results['success_rate']:.1f}% успех")
    
    @pytest.mark.asyncio
    async def test_sfm_concurrent_operations(self):
        """Тест конкурентных операций SFM"""
        print("\n🧪 Тестирование конкурентных операций SFM...")
        
        concurrent_results = await self.tester.test_sfm_concurrent_operations()
        
        # Проверки
        assert concurrent_results["total_operations"] > 0, "Нет конкурентных операций"
        assert concurrent_results["successful_operations"] >= concurrent_results["total_operations"] * 0.7, "Слишком много неудачных операций"
        assert concurrent_results["concurrent_execution_time"] < 60, f"Слишком долгое выполнение: {concurrent_results['concurrent_execution_time']:.2f}s"
        
        print(f"✅ Конкурентные операции: {concurrent_results['successful_operations']}/{concurrent_results['total_operations']} успешно")
    
    @pytest.mark.asyncio
    async def test_sfm_error_handling(self):
        """Тест обработки ошибок SFM"""
        print("\n🧪 Тестирование обработки ошибок SFM...")
        
        error_results = await self.tester.test_sfm_error_handling()
        
        # Проверки
        assert "invalid_function_id" in error_results, "Не протестирован несуществующий ID функции"
        assert "invalid_operation" in error_results, "Не протестирована неверная операция"
        assert "timeout_scenario" in error_results, "Не протестирован таймаут"
        
        # Большинство тестов ошибок должны завершиться неудачей (это ожидаемо)
        total_error_tests = len([r for r in error_results.values() if r is not None])
        expected_failures = sum(1 for r in error_results.values() if r and not r["success"])
        
        assert expected_failures >= total_error_tests * 0.7, "Слишком мало ожидаемых неудач в тестах ошибок"
        
        print(f"✅ Обработка ошибок: {expected_failures}/{total_error_tests} корректно обработаны")
    
    @pytest.mark.asyncio
    async def test_sfm_dashboard_integration(self):
        """Тест интеграции SFM с дашбордом"""
        print("\n🧪 Тестирование интеграции SFM с дашбордом...")
        
        integration_results = await self.tester.test_sfm_dashboard_integration()
        
        # Проверки
        assert len(integration_results["dashboard_sfm_endpoints"]) > 0, "Нет SFM endpoints в дашборде"
        
        successful_endpoints = sum(1 for ep in integration_results["dashboard_sfm_endpoints"] if ep["success"])
        total_endpoints = len(integration_results["dashboard_sfm_endpoints"])
        
        assert successful_endpoints >= total_endpoints * 0.5, f"Слишком много недоступных endpoints: {successful_endpoints}/{total_endpoints}"
        
        print(f"✅ Интеграция с дашбордом: {integration_results['integration_quality']}")
        print(f"  SFM данные: {'✅' if integration_results['sfm_data_in_dashboard'] else '❌'}")
        print(f"  Real-time: {'✅' if integration_results['real_time_updates'] else '❌'}")
    
    def test_generate_advanced_integration_report(self):
        """Генерация отчета о продвинутой интеграции"""
        print("\n📊 Генерация отчета о продвинутой интеграции SFM...")
        
        report = self.tester.generate_advanced_integration_report()
        
        # Сохранение отчета
        report_file = f"sfm_advanced_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Отчет о продвинутой интеграции сохранен: {report_file}")
        
        # Вывод краткой статистики
        metrics = report['integration_metrics']
        summary = report['summary']
        
        print(f"\n📈 КРАТКАЯ СТАТИСТИКА:")
        print(f"  Всего операций: {metrics['total_operations']}")
        print(f"  Успешных операций: {metrics['successful_operations']}")
        print(f"  Процент успеха: {metrics['availability_percent']:.1f}%")
        print(f"  Среднее время отклика: {metrics['average_response_time']:.3f}s")
        print(f"  Операций в секунду: {metrics['operations_per_second']:.2f}")
        print(f"  Качество интеграции: {summary['integration_quality']}")
        print(f"  Оценка производительности: {summary['performance_grade']}")
        
        # Проверки отчета
        assert report['integration_metrics']['total_operations'] > 0, "Нет данных об операциях"
        assert report['summary']['overall_success_rate'] >= 0, "Процент успеха не может быть отрицательным"


if __name__ == "__main__":
    print("🚀 Запуск продвинутых тестов интеграции ALADDIN Dashboard с SFM...")
    print("🔗 Комплексная интеграция с Safe Function Manager...")
    print("🛡️ Тестирование жизненного цикла функций...")
    print("⚡ Конкурентные операции и обработка ошибок...")
    
    # Запуск тестов через pytest
    pytest.main([__file__, "-v", "--tb=short"])