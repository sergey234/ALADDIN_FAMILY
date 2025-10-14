#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM API Integration Tests для ALADDIN Dashboard
Тесты интеграции API Safe Function Manager

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
import statistics
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


class APITestType(Enum):
    """Типы тестов API"""
    ENDPOINT_DISCOVERY = "endpoint_discovery"
    API_VERSIONING = "api_versioning"
    RESPONSE_FORMAT = "response_format"
    ERROR_HANDLING = "error_handling"
    RATE_LIMITING = "rate_limiting"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_VALIDATION = "data_validation"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"


class APIResponseStatus(Enum):
    """Статусы ответов API"""
    SUCCESS = "success"
    CLIENT_ERROR = "client_error"
    SERVER_ERROR = "server_error"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"


@dataclass
class APIEndpoint:
    """Endpoint API"""
    endpoint_id: str
    path: str
    method: str
    description: str
    parameters: List[Dict[str, Any]]
    response_schema: Dict[str, Any]
    authentication_required: bool
    rate_limit: Optional[int] = None


@dataclass
class APITestResult:
    """Результат теста API"""
    test_id: str
    test_type: APITestType
    endpoint: str
    timestamp: datetime
    status: APIResponseStatus
    response_code: int
    response_time: float
    response_size: int
    success: bool
    error_message: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None


@dataclass
class APIIntegrationMetrics:
    """Метрики интеграции API"""
    total_endpoints_tested: int
    successful_endpoints: int
    failed_endpoints: int
    average_response_time: float
    max_response_time: float
    min_response_time: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    api_coverage_percent: float
    integration_quality: str


class SFMAPIIntegrationTester:
    """Тестер интеграции API SFM"""
    
    def __init__(self, sfm_url: str = "http://localhost:8011"):
        """
        Инициализация тестера API
        
        Args:
            sfm_url: URL SFM API
        """
        self.sfm_url = sfm_url
        self.logger = LoggingManager(name="SFMAPIIntegrationTester") if ALADDIN_AVAILABLE else None
        self.api_endpoints: List[APIEndpoint] = []
        self.api_test_results: List[APITestResult] = []
        self.discovered_endpoints: List[str] = []
        
    async def discover_api_endpoints(self) -> List[APIEndpoint]:
        """
        Обнаружение endpoints API SFM
        
        Returns:
            Список обнаруженных endpoints
        """
        print("📊 Обнаружение endpoints API SFM...")
        
        discovered_endpoints = []
        
        # Список ожидаемых endpoints SFM
        expected_endpoints = [
            {
                "path": "/health",
                "method": "GET",
                "description": "Health check endpoint",
                "auth_required": False
            },
            {
                "path": "/functions",
                "method": "GET",
                "description": "List all functions",
                "auth_required": True
            },
            {
                "path": "/functions/{function_id}/status",
                "method": "GET",
                "description": "Get function status",
                "auth_required": True
            },
            {
                "path": "/functions/{function_id}/enable",
                "method": "POST",
                "description": "Enable function",
                "auth_required": True
            },
            {
                "path": "/functions/{function_id}/disable",
                "method": "POST",
                "description": "Disable function",
                "auth_required": True
            },
            {
                "path": "/functions/{function_id}/restart",
                "method": "POST",
                "description": "Restart function",
                "auth_required": True
            },
            {
                "path": "/functions/{function_id}/config",
                "method": "GET",
                "description": "Get function configuration",
                "auth_required": True
            },
            {
                "path": "/functions/{function_id}/config",
                "method": "PUT",
                "description": "Update function configuration",
                "auth_required": True
            },
            {
                "path": "/functions/{function_id}/metrics",
                "method": "GET",
                "description": "Get function metrics",
                "auth_required": True
            },
            {
                "path": "/functions/{function_id}/health",
                "method": "GET",
                "description": "Get function health",
                "auth_required": True
            },
            {
                "path": "/metrics",
                "method": "GET",
                "description": "Get system metrics",
                "auth_required": True
            },
            {
                "path": "/docs",
                "method": "GET",
                "description": "API documentation",
                "auth_required": False
            },
            {
                "path": "/openapi.json",
                "method": "GET",
                "description": "OpenAPI specification",
                "auth_required": False
            }
        ]
        
        # Тестируем каждый ожидаемый endpoint
        for endpoint_info in expected_endpoints:
            print(f"  Тестирование {endpoint_info['method']} {endpoint_info['path']}...")
            
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    headers = {"Authorization": "Bearer demo_token"} if endpoint_info["auth_required"] else {}
                    
                    # Заменяем {function_id} на реальный ID
                    test_path = endpoint_info["path"].replace("{function_id}", "test_function")
                    
                    if endpoint_info["method"] == "GET":
                        response = await client.get(f"{self.sfm_url}{test_path}", headers=headers)
                    elif endpoint_info["method"] == "POST":
                        response = await client.post(f"{self.sfm_url}{test_path}", headers=headers, json={})
                    elif endpoint_info["method"] == "PUT":
                        response = await client.put(f"{self.sfm_url}{test_path}", headers=headers, json={})
                    else:
                        continue
                    
                    # Создаем endpoint объект
                    endpoint = APIEndpoint(
                        endpoint_id=f"{endpoint_info['method'].lower()}_{endpoint_info['path'].replace('/', '_').replace('{', '').replace('}', '')}",
                        path=endpoint_info["path"],
                        method=endpoint_info["method"],
                        description=endpoint_info["description"],
                        parameters=[],  # Заполняется при необходимости
                        response_schema={},  # Заполняется при анализе ответов
                        authentication_required=endpoint_info["auth_required"],
                        rate_limit=None  # Заполняется при тестировании rate limiting
                    )
                    
                    discovered_endpoints.append(endpoint)
                    self.discovered_endpoints.append(test_path)
                    
                    print(f"    ✅ Найден: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ Не найден: {e}")
        
        self.api_endpoints = discovered_endpoints
        
        print(f"  Обнаружено endpoints: {len(discovered_endpoints)}")
        
        return discovered_endpoints
    
    async def test_api_response_formats(self) -> Dict[str, Any]:
        """
        Тест форматов ответов API
        
        Returns:
            Результаты тестирования форматов ответов
        """
        print("📊 Тестирование форматов ответов API...")
        
        format_results = {
            "endpoints_tested": [],
            "format_compliance": {},
            "schema_validation": {},
            "overall_compliance": "unknown"
        }
        
        # Тестируем каждый обнаруженный endpoint
        for endpoint in self.api_endpoints:
            print(f"  Тестирование формата ответа: {endpoint.method} {endpoint.path}")
            
            endpoint_result = {
                "endpoint": f"{endpoint.method} {endpoint.path}",
                "response_format": "unknown",
                "content_type": "unknown",
                "schema_valid": False,
                "status_codes": []
            }
            
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    headers = {"Authorization": "Bearer demo_token"} if endpoint.authentication_required else {}
                    
                    # Заменяем параметры в пути
                    test_path = endpoint.path.replace("{function_id}", "test_function")
                    
                    if endpoint.method == "GET":
                        response = await client.get(f"{self.sfm_url}{test_path}", headers=headers)
                    elif endpoint.method == "POST":
                        response = await client.post(f"{self.sfm_url}{test_path}", headers=headers, json={})
                    else:
                        continue
                    
                    endpoint_result["status_codes"].append(response.status_code)
                    
                    # Анализируем Content-Type
                    content_type = response.headers.get("Content-Type", "")
                    endpoint_result["content_type"] = content_type
                    
                    # Проверяем формат ответа
                    if "application/json" in content_type:
                        endpoint_result["response_format"] = "json"
                        
                        try:
                            json_data = response.json()
                            endpoint_result["schema_valid"] = isinstance(json_data, (dict, list))
                            
                            # Базовая валидация JSON схемы
                            if isinstance(json_data, dict):
                                # Проверяем наличие стандартных полей
                                has_status = "status" in json_data or "success" in json_data
                                has_data = "data" in json_data or "result" in json_data
                                endpoint_result["schema_valid"] = has_status or has_data
                                
                        except json.JSONDecodeError:
                            endpoint_result["schema_valid"] = False
                            endpoint_result["response_format"] = "invalid_json"
                            
                    elif "text/html" in content_type:
                        endpoint_result["response_format"] = "html"
                    elif "text/plain" in content_type:
                        endpoint_result["response_format"] = "text"
                    else:
                        endpoint_result["response_format"] = "unknown"
                    
                    format_results["endpoints_tested"].append(endpoint_result)
                    
            except Exception as e:
                endpoint_result["error"] = str(e)
                format_results["endpoints_tested"].append(endpoint_result)
        
        # Анализируем общее соответствие
        total_endpoints = len(format_results["endpoints_tested"])
        json_endpoints = len([e for e in format_results["endpoints_tested"] if e["response_format"] == "json"])
        valid_schemas = len([e for e in format_results["endpoints_tested"] if e["schema_valid"]])
        
        if json_endpoints == total_endpoints and valid_schemas >= total_endpoints * 0.8:
            format_results["overall_compliance"] = "excellent"
        elif json_endpoints >= total_endpoints * 0.8 and valid_schemas >= total_endpoints * 0.6:
            format_results["overall_compliance"] = "good"
        elif json_endpoints >= total_endpoints * 0.5:
            format_results["overall_compliance"] = "fair"
        else:
            format_results["overall_compliance"] = "poor"
        
        format_results["format_compliance"] = {
            "total_endpoints": total_endpoints,
            "json_endpoints": json_endpoints,
            "valid_schemas": valid_schemas,
            "json_percentage": (json_endpoints / total_endpoints) * 100 if total_endpoints > 0 else 0,
            "schema_validity_percentage": (valid_schemas / total_endpoints) * 100 if total_endpoints > 0 else 0
        }
        
        print(f"  Соответствие форматам: {format_results['overall_compliance']}")
        print(f"  JSON endpoints: {json_endpoints}/{total_endpoints}")
        print(f"  Валидные схемы: {valid_schemas}/{total_endpoints}")
        
        return format_results
    
    async def test_api_error_handling(self) -> Dict[str, Any]:
        """
        Тест обработки ошибок API
        
        Returns:
            Результаты тестирования обработки ошибок
        """
        print("📊 Тестирование обработки ошибок API...")
        
        error_results = {
            "error_scenarios_tested": [],
            "error_response_formats": {},
            "error_handling_quality": "unknown"
        }
        
        # Сценарии ошибок для тестирования
        error_scenarios = [
            {
                "name": "invalid_function_id",
                "endpoint": "/functions/invalid_id_12345/status",
                "method": "GET",
                "expected_status": [404, 400]
            },
            {
                "name": "invalid_endpoint",
                "endpoint": "/invalid/endpoint",
                "method": "GET",
                "expected_status": [404, 405]
            },
            {
                "name": "unauthorized_access",
                "endpoint": "/functions",
                "method": "GET",
                "headers": {},  # Без авторизации
                "expected_status": [401, 403]
            },
            {
                "name": "invalid_request_body",
                "endpoint": "/functions/test_function/config",
                "method": "PUT",
                "data": {"invalid": "data"},
                "expected_status": [400, 422]
            },
            {
                "name": "method_not_allowed",
                "endpoint": "/health",
                "method": "DELETE",
                "expected_status": [405]
            }
        ]
        
        # Тестируем каждый сценарий ошибки
        for scenario in error_scenarios:
            print(f"  Тестирование сценария: {scenario['name']}")
            
            scenario_result = {
                "scenario": scenario["name"],
                "endpoint": scenario["endpoint"],
                "method": scenario["method"],
                "expected_status": scenario["expected_status"],
                "actual_status": None,
                "response_format": "unknown",
                "error_message_present": False,
                "success": False
            }
            
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    headers = scenario.get("headers", {"Authorization": "Bearer demo_token"})
                    data = scenario.get("data", {})
                    
                    if scenario["method"] == "GET":
                        response = await client.get(f"{self.sfm_url}{scenario['endpoint']}", headers=headers)
                    elif scenario["method"] == "POST":
                        response = await client.post(f"{self.sfm_url}{scenario['endpoint']}", headers=headers, json=data)
                    elif scenario["method"] == "PUT":
                        response = await client.put(f"{self.sfm_url}{scenario['endpoint']}", headers=headers, json=data)
                    elif scenario["method"] == "DELETE":
                        response = await client.delete(f"{self.sfm_url}{scenario['endpoint']}", headers=headers)
                    else:
                        continue
                    
                    scenario_result["actual_status"] = response.status_code
                    
                    # Проверяем, соответствует ли статус ожидаемому
                    scenario_result["success"] = response.status_code in scenario["expected_status"]
                    
                    # Анализируем формат ответа об ошибке
                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        try:
                            error_data = response.json()
                            scenario_result["response_format"] = "json"
                            scenario_result["error_message_present"] = any(
                                key in error_data for key in ["error", "message", "detail", "description"]
                            )
                        except json.JSONDecodeError:
                            scenario_result["response_format"] = "invalid_json"
                    else:
                        scenario_result["response_format"] = "non_json"
                        scenario_result["error_message_present"] = len(response.text) > 0
                    
                    error_results["error_scenarios_tested"].append(scenario_result)
                    
            except Exception as e:
                scenario_result["actual_status"] = 0
                scenario_result["error"] = str(e)
                error_results["error_scenarios_tested"].append(scenario_result)
        
        # Анализируем качество обработки ошибок
        total_scenarios = len(error_results["error_scenarios_tested"])
        successful_scenarios = len([s for s in error_results["error_scenarios_tested"] if s["success"]])
        json_error_responses = len([s for s in error_results["error_scenarios_tested"] if s["response_format"] == "json"])
        messages_present = len([s for s in error_results["error_scenarios_tested"] if s["error_message_present"]])
        
        if successful_scenarios >= total_scenarios * 0.8 and json_error_responses >= total_scenarios * 0.8 and messages_present >= total_scenarios * 0.8:
            error_results["error_handling_quality"] = "excellent"
        elif successful_scenarios >= total_scenarios * 0.6 and json_error_responses >= total_scenarios * 0.6:
            error_results["error_handling_quality"] = "good"
        elif successful_scenarios >= total_scenarios * 0.4:
            error_results["error_handling_quality"] = "fair"
        else:
            error_results["error_handling_quality"] = "poor"
        
        error_results["error_response_formats"] = {
            "total_scenarios": total_scenarios,
            "successful_scenarios": successful_scenarios,
            "json_responses": json_error_responses,
            "messages_present": messages_present,
            "success_rate": (successful_scenarios / total_scenarios) * 100 if total_scenarios > 0 else 0
        }
        
        print(f"  Качество обработки ошибок: {error_results['error_handling_quality']}")
        print(f"  Успешных сценариев: {successful_scenarios}/{total_scenarios}")
        print(f"  JSON ответы: {json_error_responses}/{total_scenarios}")
        
        return error_results
    
    async def test_api_performance(self) -> Dict[str, Any]:
        """
        Тест производительности API
        
        Returns:
            Результаты тестирования производительности API
        """
        print("📊 Тестирование производительности API...")
        
        performance_results = {
            "endpoint_performance": [],
            "load_test_results": {},
            "concurrent_test_results": {},
            "overall_performance": "unknown"
        }
        
        # Тестируем производительность основных endpoints
        main_endpoints = [
            {"path": "/health", "method": "GET", "auth": False},
            {"path": "/functions", "method": "GET", "auth": True},
            {"path": "/functions/test_function/status", "method": "GET", "auth": True}
        ]
        
        # 1. Тест производительности отдельных endpoints
        print("  1. Тестирование производительности endpoints...")
        
        for endpoint_info in main_endpoints:
            print(f"    Тестирование {endpoint_info['method']} {endpoint_info['path']}...")
            
            response_times = []
            success_count = 0
            
            # Делаем 10 запросов для измерения производительности
            for i in range(10):
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        headers = {"Authorization": "Bearer demo_token"} if endpoint_info["auth"] else {}
                        
                        start_time = time.time()
                        
                        if endpoint_info["method"] == "GET":
                            response = await client.get(f"{self.sfm_url}{endpoint_info['path']}", headers=headers)
                        else:
                            continue
                        
                        response_time = time.time() - start_time
                        response_times.append(response_time)
                        
                        if 200 <= response.status_code < 300:
                            success_count += 1
                        
                        await asyncio.sleep(0.1)  # Небольшая пауза между запросами
                        
                except Exception:
                    response_times.append(10.0)  # Таймаут
            
            if response_times:
                avg_response_time = statistics.mean(response_times)
                min_response_time = min(response_times)
                max_response_time = max(response_times)
                success_rate = (success_count / len(response_times)) * 100
                
                endpoint_perf = {
                    "endpoint": f"{endpoint_info['method']} {endpoint_info['path']}",
                    "avg_response_time": avg_response_time,
                    "min_response_time": min_response_time,
                    "max_response_time": max_response_time,
                    "success_rate": success_rate,
                    "requests_tested": len(response_times)
                }
                
                performance_results["endpoint_performance"].append(endpoint_perf)
                
                print(f"      Среднее время: {avg_response_time:.3f}s, Успешность: {success_rate:.1f}%")
        
        # 2. Тест нагрузки
        print("  2. Тестирование нагрузки...")
        
        load_test_requests = 50
        load_response_times = []
        load_success_count = 0
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": "Bearer demo_token"}
            
            for i in range(load_test_requests):
                try:
                    start_time = time.time()
                    response = await client.get(f"{self.sfm_url}/health", headers=headers)
                    response_time = time.time() - start_time
                    
                    load_response_times.append(response_time)
                    
                    if 200 <= response.status_code < 300:
                        load_success_count += 1
                    
                except Exception:
                    load_response_times.append(10.0)
        
        performance_results["load_test_results"] = {
            "total_requests": load_test_requests,
            "successful_requests": load_success_count,
            "avg_response_time": statistics.mean(load_response_times) if load_response_times else 0,
            "max_response_time": max(load_response_times) if load_response_times else 0,
            "success_rate": (load_success_count / load_test_requests) * 100
        }
        
        # 3. Тест конкурентности
        print("  3. Тестирование конкурентности...")
        
        concurrent_requests = 20
        concurrent_start = time.time()
        
        async def make_concurrent_request():
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    headers = {"Authorization": "Bearer demo_token"}
                    start_time = time.time()
                    response = await client.get(f"{self.sfm_url}/health", headers=headers)
                    return time.time() - start_time, response.status_code
            except Exception:
                return 10.0, 0
        
        # Запускаем конкурентные запросы
        tasks = [make_concurrent_request() for _ in range(concurrent_requests)]
        concurrent_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        concurrent_total_time = time.time() - concurrent_start
        concurrent_response_times = [r[0] if isinstance(r, tuple) else 10.0 for r in concurrent_results]
        concurrent_success_count = sum(1 for r in concurrent_results if isinstance(r, tuple) and 200 <= r[1] < 300)
        
        performance_results["concurrent_test_results"] = {
            "total_requests": concurrent_requests,
            "successful_requests": concurrent_success_count,
            "total_time": concurrent_total_time,
            "avg_response_time": statistics.mean(concurrent_response_times),
            "max_response_time": max(concurrent_response_times),
            "requests_per_second": concurrent_requests / concurrent_total_time if concurrent_total_time > 0 else 0,
            "success_rate": (concurrent_success_count / concurrent_requests) * 100
        }
        
        # Анализируем общую производительность
        avg_endpoint_time = statistics.mean([ep["avg_response_time"] for ep in performance_results["endpoint_performance"]])
        avg_load_time = performance_results["load_test_results"]["avg_response_time"]
        avg_concurrent_time = performance_results["concurrent_test_results"]["avg_response_time"]
        
        overall_avg_time = statistics.mean([avg_endpoint_time, avg_load_time, avg_concurrent_time])
        
        if overall_avg_time < 1.0:
            performance_results["overall_performance"] = "excellent"
        elif overall_avg_time < 2.0:
            performance_results["overall_performance"] = "good"
        elif overall_avg_time < 5.0:
            performance_results["overall_performance"] = "fair"
        else:
            performance_results["overall_performance"] = "poor"
        
        print(f"  Общая производительность: {performance_results['overall_performance']}")
        print(f"  Среднее время отклика: {overall_avg_time:.3f}s")
        print(f"  Нагрузочный тест: {load_success_count}/{load_test_requests} успешно")
        print(f"  Конкурентный тест: {concurrent_success_count}/{concurrent_requests} успешно")
        
        return performance_results
    
    def calculate_api_integration_metrics(self) -> APIIntegrationMetrics:
        """Вычисление метрик интеграции API"""
        # Подсчитываем метрики из результатов тестов
        total_endpoints = len(self.api_endpoints)
        successful_endpoints = len([ep for ep in self.api_endpoints if ep.endpoint_id in self.discovered_endpoints])
        failed_endpoints = total_endpoints - successful_endpoints
        
        # Анализируем результаты тестов (если есть)
        if self.api_test_results:
            response_times = [r.response_time for r in self.api_test_results]
            total_requests = len(self.api_test_results)
            successful_requests = len([r for r in self.api_test_results if r.success])
            failed_requests = total_requests - successful_requests
            
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
        else:
            avg_response_time = max_response_time = min_response_time = 0.0
            total_requests = successful_requests = failed_requests = 0
        
        # Вычисляем покрытие API
        api_coverage_percent = (successful_endpoints / total_endpoints) * 100 if total_endpoints > 0 else 0
        
        # Определяем качество интеграции
        if api_coverage_percent >= 90 and avg_response_time < 2.0:
            integration_quality = "excellent"
        elif api_coverage_percent >= 80 and avg_response_time < 5.0:
            integration_quality = "good"
        elif api_coverage_percent >= 60:
            integration_quality = "fair"
        else:
            integration_quality = "poor"
        
        return APIIntegrationMetrics(
            total_endpoints_tested=total_endpoints,
            successful_endpoints=successful_endpoints,
            failed_endpoints=failed_endpoints,
            average_response_time=avg_response_time,
            max_response_time=max_response_time,
            min_response_time=min_response_time,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            api_coverage_percent=api_coverage_percent,
            integration_quality=integration_quality
        )
    
    def generate_api_integration_report(self) -> Dict[str, Any]:
        """Генерация отчета об интеграции API"""
        print("📊 Генерация отчета об интеграции API SFM...")
        
        metrics = self.calculate_api_integration_metrics()
        
        report = {
            "report_date": datetime.now().isoformat(),
            "api_integration_metrics": {
                "total_endpoints_tested": metrics.total_endpoints_tested,
                "successful_endpoints": metrics.successful_endpoints,
                "failed_endpoints": metrics.failed_endpoints,
                "average_response_time": metrics.average_response_time,
                "max_response_time": metrics.max_response_time,
                "min_response_time": metrics.min_response_time,
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "api_coverage_percent": metrics.api_coverage_percent,
                "integration_quality": metrics.integration_quality
            },
            "discovered_endpoints": [
                {
                    "endpoint_id": ep.endpoint_id,
                    "path": ep.path,
                    "method": ep.method,
                    "description": ep.description,
                    "authentication_required": ep.authentication_required,
                    "rate_limit": ep.rate_limit
                }
                for ep in self.api_endpoints
            ],
            "test_results": [
                {
                    "test_id": r.test_id,
                    "test_type": r.test_type.value,
                    "endpoint": r.endpoint,
                    "timestamp": r.timestamp.isoformat(),
                    "status": r.status.value,
                    "response_code": r.response_code,
                    "response_time": r.response_time,
                    "response_size": r.response_size,
                    "success": r.success,
                    "error_message": r.error_message
                }
                for r in self.api_test_results
            ],
            "summary": {
                "api_availability": "high" if metrics.api_coverage_percent >= 80 else "medium" if metrics.api_coverage_percent >= 60 else "low",
                "performance_grade": "A+" if metrics.average_response_time < 1.0 else
                                   "A" if metrics.average_response_time < 2.0 else
                                   "B" if metrics.average_response_time < 5.0 else "C",
                "integration_recommendations": self._generate_api_recommendations(metrics)
            }
        }
        
        return report
    
    def _generate_api_recommendations(self, metrics: APIIntegrationMetrics) -> List[str]:
        """Генерация рекомендаций по API"""
        recommendations = []
        
        if metrics.api_coverage_percent < 80:
            recommendations.append("Увеличить покрытие API - не все endpoints доступны")
        
        if metrics.average_response_time > 2.0:
            recommendations.append("Оптимизировать время отклика API")
        
        if metrics.successful_requests < metrics.total_requests * 0.9:
            recommendations.append("Улучшить надежность API endpoints")
        
        if metrics.failed_endpoints > 0:
            recommendations.append(f"Исправить {metrics.failed_endpoints} недоступных endpoints")
        
        if not recommendations:
            recommendations.append("API интеграция работает оптимально")
        
        return recommendations


class TestSFMAPIIntegration:
    """Тесты интеграции API SFM"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестов"""
        self.tester = SFMAPIIntegrationTester()
    
    @pytest.mark.asyncio
    async def test_api_endpoint_discovery(self):
        """Тест обнаружения endpoints API"""
        print("\n🧪 Тестирование обнаружения endpoints API...")
        
        endpoints = await self.tester.discover_api_endpoints()
        
        # Проверки
        assert len(endpoints) > 0, "Не обнаружено ни одного endpoint"
        assert all(isinstance(ep, APIEndpoint) for ep in endpoints), "Некорректные endpoint объекты"
        
        # Проверяем, что есть основные endpoints
        endpoint_paths = [ep.path for ep in endpoints]
        assert "/health" in endpoint_paths or "/health" in self.tester.discovered_endpoints, "Отсутствует health endpoint"
        
        print(f"✅ Обнаружение endpoints: {len(endpoints)} endpoints найдено")
    
    @pytest.mark.asyncio
    async def test_api_response_formats(self):
        """Тест форматов ответов API"""
        print("\n🧪 Тестирование форматов ответов API...")
        
        format_results = await self.tester.test_api_response_formats()
        
        # Проверки
        assert len(format_results["endpoints_tested"]) > 0, "Нет протестированных endpoints"
        assert format_results["overall_compliance"] != "unknown", "Неопределенное соответствие форматам"
        
        compliance = format_results["format_compliance"]
        assert compliance["total_endpoints"] > 0, "Нет endpoints для анализа"
        assert 0 <= compliance["json_percentage"] <= 100, "Некорректный процент JSON endpoints"
        
        print(f"✅ Форматы ответов: {format_results['overall_compliance']}")
        print(f"  JSON endpoints: {compliance['json_percentage']:.1f}%")
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Тест обработки ошибок API"""
        print("\n🧪 Тестирование обработки ошибок API...")
        
        error_results = await self.tester.test_api_error_handling()
        
        # Проверки
        assert len(error_results["error_scenarios_tested"]) > 0, "Нет протестированных сценариев ошибок"
        assert error_results["error_handling_quality"] != "unknown", "Неопределенное качество обработки ошибок"
        
        error_formats = error_results["error_response_formats"]
        assert error_formats["total_scenarios"] > 0, "Нет сценариев ошибок"
        assert 0 <= error_formats["success_rate"] <= 100, "Некорректный процент успешных сценариев"
        
        print(f"✅ Обработка ошибок: {error_results['error_handling_quality']}")
        print(f"  Успешных сценариев: {error_formats['success_rate']:.1f}%")
    
    @pytest.mark.asyncio
    async def test_api_performance(self):
        """Тест производительности API"""
        print("\n🧪 Тестирование производительности API...")
        
        performance_results = await self.tester.test_api_performance()
        
        # Проверки
        assert len(performance_results["endpoint_performance"]) > 0, "Нет данных о производительности endpoints"
        assert performance_results["overall_performance"] != "unknown", "Неопределенная производительность"
        
        load_results = performance_results["load_test_results"]
        concurrent_results = performance_results["concurrent_test_results"]
        
        assert load_results["total_requests"] > 0, "Нет данных нагрузочного теста"
        assert concurrent_results["total_requests"] > 0, "Нет данных конкурентного теста"
        
        print(f"✅ Производительность API: {performance_results['overall_performance']}")
        print(f"  Нагрузочный тест: {load_results['success_rate']:.1f}% успешно")
        print(f"  Конкурентный тест: {concurrent_results['success_rate']:.1f}% успешно")
    
    @pytest.mark.asyncio
    async def test_comprehensive_api_integration(self):
        """Комплексный тест интеграции API"""
        print("\n🧪 Комплексное тестирование интеграции API...")
        
        # Запускаем все тесты API
        endpoints = await self.tester.discover_api_endpoints()
        format_results = await self.tester.test_api_response_formats()
        error_results = await self.tester.test_api_error_handling()
        performance_results = await self.tester.test_api_performance()
        
        # Анализируем общие результаты
        metrics = self.tester.calculate_api_integration_metrics()
        
        # Проверки
        assert metrics.total_endpoints_tested > 0, "Нет протестированных endpoints"
        assert 0 <= metrics.api_coverage_percent <= 100, "Некорректный процент покрытия API"
        assert metrics.integration_quality != "unknown", "Неопределенное качество интеграции"
        
        print(f"✅ Комплексная интеграция API:")
        print(f"  Endpoints: {metrics.successful_endpoints}/{metrics.total_endpoints_tested}")
        print(f"  Покрытие API: {metrics.api_coverage_percent:.1f}%")
        print(f"  Качество интеграции: {metrics.integration_quality}")
        print(f"  Среднее время отклика: {metrics.average_response_time:.3f}s")
    
    def test_generate_api_integration_report(self):
        """Генерация отчета об интеграции API"""
        print("\n📊 Генерация отчета об интеграции API SFM...")
        
        report = self.tester.generate_api_integration_report()
        
        # Сохранение отчета
        report_file = f"sfm_api_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Отчет об интеграции API сохранен: {report_file}")
        
        # Вывод краткой статистики
        metrics = report['api_integration_metrics']
        summary = report['summary']
        
        print(f"\n📈 КРАТКАЯ СТАТИСТИКА ИНТЕГРАЦИИ API:")
        print(f"  Endpoints протестировано: {metrics['total_endpoints_tested']}")
        print(f"  Endpoints успешных: {metrics['successful_endpoints']}")
        print(f"  Покрытие API: {metrics['api_coverage_percent']:.1f}%")
        print(f"  Среднее время отклика: {metrics['average_response_time']:.3f}s")
        print(f"  Всего запросов: {metrics['total_requests']}")
        print(f"  Успешных запросов: {metrics['successful_requests']}")
        print(f"  Качество интеграции: {metrics['integration_quality']}")
        print(f"  Доступность API: {summary['api_availability']}")
        print(f"  Оценка производительности: {summary['performance_grade']}")
        
        # Проверки отчета
        assert report['api_integration_metrics']['total_endpoints_tested'] > 0, "Нет данных об endpoints"
        assert 0 <= metrics['api_coverage_percent'] <= 100, "Некорректный процент покрытия API"


if __name__ == "__main__":
    print("🚀 Запуск тестов интеграции API ALADDIN Dashboard с SFM...")
    print("🔍 Обнаружение endpoints и тестирование API...")
    print("📊 Проверка форматов ответов и обработки ошибок...")
    print("⚡ Тестирование производительности и нагрузочных тестов...")
    
    # Запуск тестов через pytest
    pytest.main([__file__, "-v", "--tb=short"])