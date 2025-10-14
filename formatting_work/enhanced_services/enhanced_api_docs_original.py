#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Interactive API Docs для ALADDIN Security System
Реальная интеграция с системой безопасности

Автор: ALADDIN Security Team
Версия: 2.0
Дата: 2025-01-06
"""

import hashlib
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import psutil
import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Импорты для интеграции с ALADDIN
try:
    from security.safe_function_manager import SafeFunctionManager

    ALADDIN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ALADDIN modules not available: {e}")
    ALADDIN_AVAILABLE = False

# Импорт ML аналитики
try:
    from advanced_ml_analytics import advanced_analytics

    ML_ANALYTICS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ML Analytics not available: {e}")
    ML_ANALYTICS_AVAILABLE = False

# Создание FastAPI приложения
app = FastAPI(
    title="🛡️ ALADDIN Enhanced API Docs",
    description="Интерактивная документация API системы безопасности ALADDIN",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Security
security = HTTPBearer()


# Модели данных
class APIEndpoint(BaseModel):
    """Модель API endpoint"""

    method: str
    path: str
    description: str
    parameters: List[Dict[str, Any]]
    responses: List[Dict[str, Any]]
    security_level: str
    rate_limit: Optional[int] = None
    service: str
    service_status: str = "active"


class ServiceStatus(BaseModel):
    """Модель статуса сервиса"""

    name: str
    status: str
    port: int
    uptime: float
    cpu_usage: float
    memory_usage: float
    last_check: datetime


class TestResult(BaseModel):
    """Модель результата теста API"""

    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime


class APIDocsManager:
    """Менеджер для работы с API документацией"""

    def __init__(self):
        self.endpoints: List[APIEndpoint] = []
        self.services: Dict[str, ServiceStatus] = {}
        self.test_history: List[TestResult] = []
        self.db_path = "api_docs.db"
        self.cache: Dict[str, Any] = {}
        self.cache_ttl: Dict[str, datetime] = {}
        self.ml_predictor = None
        self.init_database()

        # Инициализируем ML предсказатель если доступен
        if ML_ANALYTICS_AVAILABLE:
            self.ml_predictor = advanced_analytics.ml_predictor

    def init_database(self):
        """Инициализация базы данных для хранения истории тестов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS test_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                response_time REAL NOT NULL,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                timestamp DATETIME NOT NULL
            )
        """
        )

        conn.commit()
        conn.close()

    def _get_cache_key(self, key: str) -> str:
        """Генерация ключа кэша"""
        return hashlib.md5(key.encode()).hexdigest()

    def _is_cache_valid(self, key: str, ttl_seconds: int = 300) -> bool:
        """Проверка валидности кэша"""
        if key not in self.cache_ttl:
            return False
        return (
            datetime.now() - self.cache_ttl[key]
        ).total_seconds() < ttl_seconds

    def _get_cached(self, key: str, ttl_seconds: int = 300) -> Optional[Any]:
        """Получение данных из кэша"""
        cache_key = self._get_cache_key(key)
        if cache_key in self.cache and self._is_cache_valid(
            cache_key, ttl_seconds
        ):
            return self.cache[cache_key]
        return None

    def _set_cache(self, key: str, value: Any, ttl_seconds: int = 300):
        """Сохранение данных в кэш"""
        cache_key = self._get_cache_key(key)
        self.cache[cache_key] = value
        self.cache_ttl[cache_key] = datetime.now()

    def _clear_cache(self):
        """Очистка кэша"""
        self.cache.clear()
        self.cache_ttl.clear()

    async def scan_aladdin_endpoints(self) -> List[APIEndpoint]:
        """Сканирование реальных API endpoints из ALADDIN"""
        # Проверяем кэш
        cached_endpoints = self._get_cached(
            "endpoints", ttl_seconds=600
        )  # 10 минут
        if cached_endpoints:
            return cached_endpoints

        endpoints = []

        if not ALADDIN_AVAILABLE:
            endpoints = self.get_mock_endpoints()
            self._set_cache("endpoints", endpoints)
            return endpoints

        try:
            # Сканируем microservices
            microservices_dir = Path("security/microservices")
            if microservices_dir.exists():
                for py_file in microservices_dir.glob("*.py"):
                    if py_file.name.startswith("__"):
                        continue

                    endpoints.extend(await self._scan_file_endpoints(py_file))

            # Добавляем endpoints из SafeFunctionManager
            if hasattr(SafeFunctionManager, "__init__"):
                sfm_endpoints = await self._get_sfm_endpoints()
                endpoints.extend(sfm_endpoints)

        except Exception as e:
            print(f"Error scanning ALADDIN endpoints: {e}")
            endpoints = self.get_mock_endpoints()

        self.endpoints = endpoints
        self._set_cache("endpoints", endpoints)
        return endpoints

    async def _scan_file_endpoints(self, file_path: Path) -> List[APIEndpoint]:
        """Сканирование endpoints в конкретном файле"""
        endpoints = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Поиск FastAPI декораторов
            import re

            patterns = [
                r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
                r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)'
                r'["\'].*?response_model=(\w+)',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    method = match[0].upper()
                    path = match[1]

                    # Определяем сервис по имени файла
                    service = file_path.stem.replace("_", " ").title()

                    endpoint = APIEndpoint(
                        method=method,
                        path=path,
                        description=f"Endpoint from {service}",
                        parameters=[],
                        responses=[{"status": 200, "description": "Success"}],
                        security_level="medium",
                        service=service,
                        status="active",
                    )
                    endpoints.append(endpoint)

        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")

        return endpoints

    async def _get_sfm_endpoints(self) -> List[APIEndpoint]:
        """Получение endpoints из SafeFunctionManager"""
        endpoints = []

        sfm_endpoints = [
            ("GET", "/sfm/status", "Get SFM status"),
            ("GET", "/sfm/functions", "List all functions"),
            ("POST", "/sfm/function/{function_id}/enable", "Enable function"),
            (
                "POST",
                "/sfm/function/{function_id}/disable",
                "Disable function",
            ),
            (
                "GET",
                "/sfm/function/{function_id}/status",
                "Get function status",
            ),
            ("POST", "/sfm/function/{function_id}/test", "Test function"),
        ]

        for method, path, description in sfm_endpoints:
            endpoint = APIEndpoint(
                method=method,
                path=path,
                description=description,
                parameters=[],
                responses=[{"status": 200, "description": "Success"}],
                security_level="high",
                service="SafeFunctionManager",
                status="active",
            )
            endpoints.append(endpoint)

        return endpoints

    def get_mock_endpoints(self) -> List[APIEndpoint]:
        """Получение mock endpoints для демонстрации"""
        return [
            APIEndpoint(
                method="GET",
                path="/health",
                description="Health check endpoint",
                parameters=[],
                responses=[{"status": 200, "description": "OK"}],
                security_level="low",
                service="API Gateway",
                status="active",
            ),
            APIEndpoint(
                method="GET",
                path="/metrics",
                description="Prometheus metrics",
                parameters=[],
                responses=[{"status": 200, "description": "Metrics data"}],
                security_level="medium",
                service="API Gateway",
                status="active",
            ),
            APIEndpoint(
                method="POST",
                path="/sfm/function/{function_id}/enable",
                description="Enable security function",
                parameters=[
                    {"name": "function_id", "type": "string", "required": True}
                ],
                responses=[{"status": 200, "description": "Function enabled"}],
                security_level="high",
                service="SafeFunctionManager",
                status="active",
            ),
        ]

    async def monitor_services(self) -> Dict[str, ServiceStatus]:
        """Мониторинг статуса сервисов ALADDIN"""
        # Проверяем кэш (короткий TTL для real-time данных)
        cached_services = self._get_cached(
            "services", ttl_seconds=30
        )  # 30 секунд
        if cached_services:
            return cached_services

        services = {}

        # Порты ALADDIN системы
        aladdin_ports = {
            "API Gateway": 8006,
            "Load Balancer": 8007,
            "Rate Limiter": 8008,
            "Circuit Breaker": 8009,
            "User Interface Manager": 8010,
            "SafeFunctionManager": 8011,
            "Service Mesh": 8012,
        }

        for service_name, port in aladdin_ports.items():
            try:
                # Проверяем, слушает ли порт
                is_listening = self._check_port_status(port)

                # Получаем информацию о процессе
                process_info = self._get_process_info(port)

                service_status = ServiceStatus(
                    name=service_name,
                    status="running" if is_listening else "stopped",
                    port=port,
                    uptime=process_info.get("uptime", 0),
                    cpu_usage=process_info.get("cpu_percent", 0),
                    memory_usage=process_info.get("memory_percent", 0),
                    last_check=datetime.now(),
                )

                services[service_name] = service_status

            except Exception as e:
                print(f"Error monitoring service {service_name}: {e}")
                services[service_name] = ServiceStatus(
                    name=service_name,
                    status="error",
                    port=port,
                    uptime=0,
                    cpu_usage=0,
                    memory_usage=0,
                    last_check=datetime.now(),
                )

        self.services = services
        self._set_cache("services", services)
        return services

    def _check_port_status(self, port: int) -> bool:
        """Проверка статуса порта"""
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _get_process_info(self, port: int) -> Dict[str, float]:
        """Получение информации о процессе по порту"""
        try:
            for proc in psutil.process_iter(
                ["pid", "name", "create_time", "cpu_percent", "memory_percent"]
            ):
                try:
                    connections = proc.connections()
                    for conn in connections:
                        if conn.laddr.port == port:
                            uptime = time.time() - proc.info["create_time"]
                            return {
                                "uptime": uptime,
                                "cpu_percent": proc.info["cpu_percent"],
                                "memory_percent": proc.info["memory_percent"],
                            }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"Error getting process info for port {port}: {e}")

        return {"uptime": 0, "cpu_percent": 0, "memory_percent": 0}

    async def test_endpoint(
        self, endpoint: str, method: str, data: Optional[Dict] = None
    ) -> TestResult:
        """Тестирование API endpoint"""
        start_time = time.time()

        try:
            async with httpx.AsyncClient() as client:
                # Определяем URL
                if endpoint.startswith("/sfm/"):
                    url = f"http://localhost:8011{endpoint}"
                elif endpoint.startswith("/api/"):
                    url = f"http://localhost:8006{endpoint}"
                else:
                    url = f"http://localhost:8006{endpoint}"

                # Выполняем запрос
                if method.upper() == "GET":
                    response = await client.get(url)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data)
                elif method.upper() == "PUT":
                    response = await client.put(url, json=data)
                elif method.upper() == "DELETE":
                    response = await client.delete(url)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                response_time = time.time() - start_time

                test_result = TestResult(
                    endpoint=endpoint,
                    method=method,
                    status_code=response.status_code,
                    response_time=response_time,
                    success=200 <= response.status_code < 300,
                    timestamp=datetime.now(),
                )

                # Сохраняем в базу данных
                self._save_test_result(test_result)
                self.test_history.append(test_result)

                return test_result

        except Exception as e:
            response_time = time.time() - start_time
            test_result = TestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e),
                timestamp=datetime.now(),
            )

            self._save_test_result(test_result)
            self.test_history.append(test_result)

            return test_result

    async def test_endpoint_advanced(
        self,
        endpoint: str,
        method: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> TestResult:
        """Расширенное тестирование API endpoint с кастомными заголовками"""
        start_time = time.time()

        try:
            async with httpx.AsyncClient() as client:
                # Определяем URL
                if endpoint.startswith("/sfm/"):
                    url = f"http://localhost:8011{endpoint}"
                elif endpoint.startswith("/api/"):
                    url = f"http://localhost:8006{endpoint}"
                else:
                    url = f"http://localhost:8006{endpoint}"

                # Подготавливаем заголовки
                request_headers = {"Content-Type": "application/json"}
                if headers:
                    request_headers.update(headers)

                # Выполняем запрос
                if method.upper() == "GET":
                    response = await client.get(url, headers=request_headers)
                elif method.upper() == "POST":
                    response = await client.post(
                        url, json=data, headers=request_headers
                    )
                elif method.upper() == "PUT":
                    response = await client.put(
                        url, json=data, headers=request_headers
                    )
                elif method.upper() == "DELETE":
                    response = await client.delete(
                        url, headers=request_headers
                    )
                else:
                    raise ValueError(f"Unsupported method: {method}")

                response_time = time.time() - start_time

                test_result = TestResult(
                    endpoint=endpoint,
                    method=method,
                    status_code=response.status_code,
                    response_time=response_time,
                    success=200 <= response.status_code < 300,
                    timestamp=datetime.now(),
                )

                # Сохраняем в базу данных
                self._save_test_result(test_result)
                self.test_history.append(test_result)

                return test_result

        except Exception as e:
            response_time = time.time() - start_time
            test_result = TestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e),
                timestamp=datetime.now(),
            )

            self._save_test_result(test_result)
            self.test_history.append(test_result)

            return test_result

    def _save_test_result(self, result: TestResult):
        """Сохранение результата теста в базу данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO test_history
                (endpoint, method, status_code, response_time, success,
                 error_message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    result.endpoint,
                    result.method,
                    result.status_code,
                    result.response_time,
                    result.success,
                    result.error_message,
                    result.timestamp,
                ),
            )

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving test result: {e}")


# Глобальный экземпляр менеджера
docs_manager = APIDocsManager()


# JWT Authentication (упрощенная версия)
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Проверка JWT токена"""
    # В реальной системе здесь должна быть проверка JWT
    # Для демонстрации принимаем любой токен
    return {"user_id": "demo_user", "role": "developer"}


# API Routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница Enhanced API Docs"""
    return await get_enhanced_docs_page()


@app.get("/api/endpoints")
async def get_endpoints():
    """Получение списка всех API endpoints"""
    endpoints = await docs_manager.scan_aladdin_endpoints()
    return {"endpoints": [endpoint.dict() for endpoint in endpoints]}


@app.get("/api/services")
async def get_services():
    """Получение статуса всех сервисов"""
    services = await docs_manager.monitor_services()
    return {
        "services": {
            name: service.dict() for name, service in services.items()
        }
    }


@app.post("/api/test")
async def test_endpoint(
    endpoint: str,
    method: str,
    data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    user: dict = Depends(verify_token),
):
    """Тестирование API endpoint с расширенными параметрами"""
    result = await docs_manager.test_endpoint_advanced(
        endpoint, method, data, headers
    )
    return result.dict()


@app.get("/api/autocomplete")
async def get_autocomplete_suggestions(query: str):
    """Получение автодополнения для endpoints"""
    suggestions = []

    for endpoint in docs_manager.endpoints:
        if query.lower() in endpoint.path.lower():
            suggestions.append(
                {
                    "path": endpoint.path,
                    "method": endpoint.method,
                    "description": endpoint.description,
                    "service": endpoint.service,
                }
            )

    return {"suggestions": suggestions[:10]}  # Ограничиваем 10 результатами


@app.post("/api/batch-test")
async def batch_test_endpoints(
    tests: List[Dict[str, Any]], user: dict = Depends(verify_token)
):
    """Пакетное тестирование нескольких endpoints"""
    results = []

    for test in tests:
        result = await docs_manager.test_endpoint_advanced(
            test.get("endpoint", ""),
            test.get("method", "GET"),
            test.get("data"),
            test.get("headers"),
        )
        results.append(result.dict())

    return {"results": results, "total": len(results)}


@app.get("/api/test-history")
async def get_test_history(limit: int = 50):
    """Получение истории тестов"""
    return {
        "history": [
            result.dict() for result in docs_manager.test_history[-limit:]
        ]
    }


@app.get("/api/export/{format}")
async def export_data(format: str):
    """Экспорт данных в различных форматах"""
    if format == "json":
        return {
            "endpoints": [
                endpoint.dict() for endpoint in docs_manager.endpoints
            ],
            "services": {
                name: service.dict()
                for name, service in docs_manager.services.items()
            },
            "test_history": [
                result.dict() for result in docs_manager.test_history
            ],
        }
    elif format == "csv":
        # Простая CSV генерация
        csv_data = (
            "endpoint,method,status_code,response_time,success,timestamp\n"
        )
        for result in docs_manager.test_history:
            csv_data += (f"{result.endpoint},{result.method},"
                         f"{result.status_code},{result.response_time},"
                         f"{result.success},{result.timestamp}\n")
        return {"csv": csv_data}
    elif format == "html":
        # HTML отчет с графиками
        return await generate_html_report()
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")


@app.get("/api/search")
async def search_endpoints(query: str, category: Optional[str] = None):
    """Поиск по API endpoints с фильтрацией"""
    results = []

    for endpoint in docs_manager.endpoints:
        if (
            query.lower() in endpoint.path.lower()
            or query.lower() in endpoint.description.lower()
        ):
            if not category or endpoint.service.lower() == category.lower():
                results.append(endpoint.dict())

    return {"results": results, "query": query, "category": category}


@app.get("/api/analytics")
async def get_analytics():
    """Получение аналитики по тестам и производительности"""
    if not docs_manager.test_history:
        return {"message": "No test data available"}

    # Статистика по тестам
    total_tests = len(docs_manager.test_history)
    successful_tests = len([t for t in docs_manager.test_history if t.success])
    success_rate = (
        (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    )

    # Статистика по времени отклика
    response_times = [
        t.response_time for t in docs_manager.test_history if t.success
    ]
    avg_response_time = (
        sum(response_times) / len(response_times) if response_times else 0
    )

    # Статистика по методам
    method_stats = {}
    for test in docs_manager.test_history:
        method = test.method
        if method not in method_stats:
            method_stats[method] = {"total": 0, "success": 0}
        method_stats[method]["total"] += 1
        if test.success:
            method_stats[method]["success"] += 1

    return {
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "success_rate": round(success_rate, 2),
        "average_response_time": round(avg_response_time, 3),
        "method_statistics": method_stats,
        "recent_tests": [t.dict() for t in docs_manager.test_history[-10:]],
    }


@app.post("/api/cache/clear")
async def clear_cache(user: dict = Depends(verify_token)):
    """Очистка кэша системы"""
    docs_manager._clear_cache()
    return {"message": "Cache cleared successfully"}


@app.get("/api/cache/status")
async def get_cache_status():
    """Получение статуса кэша"""
    cache_size = len(docs_manager.cache)
    cache_keys = list(docs_manager.cache.keys())

    return {
        "cache_size": cache_size,
        "cache_keys": cache_keys,
        "memory_usage": f"{cache_size * 0.001:.2f} KB",  # Примерная оценка
    }


# ML Analytics Endpoints
@app.get("/api/ml/health-analysis")
async def get_health_analysis():
    """Получение анализа здоровья системы с ML"""
    if not ML_ANALYTICS_AVAILABLE:
        return {"error": "ML Analytics not available"}

    services = await docs_manager.monitor_services()
    analysis = await advanced_analytics.analyze_system_health(services)
    return analysis


@app.post("/api/ml/train-models")
async def train_ml_models(user: dict = Depends(verify_token)):
    """Обучение ML моделей на исторических данных"""
    if not ML_ANALYTICS_AVAILABLE:
        return {"error": "ML Analytics not available"}

    # Получаем исторические данные
    historical_data = docs_manager.ml_predictor.get_ml_history(168)  # 7 дней

    if len(historical_data) < 50:
        return {"error": "Not enough historical data for training"}

    # Обучаем модели
    anomaly_result = docs_manager.ml_predictor.train_anomaly_detection(
        historical_data
    )
    status_result = docs_manager.ml_predictor.train_status_prediction(
        historical_data
    )

    return {
        "anomaly_detection": anomaly_result,
        "status_prediction": status_result,
        "training_data_points": len(historical_data),
    }


@app.get("/api/ml/predictions")
async def get_ml_predictions():
    """Получение ML предсказаний для текущих сервисов"""
    if not ML_ANALYTICS_AVAILABLE:
        return {"error": "ML Analytics not available"}

    services = await docs_manager.monitor_services()
    predictions = {}

    for service_name, service_data in services.items():
        anomaly_pred = docs_manager.ml_predictor.predict_anomalies(
            service_data
        )
        status_pred = docs_manager.ml_predictor.predict_status(service_data)

        predictions[service_name] = {
            "anomaly_prediction": anomaly_pred,
            "status_prediction": status_pred,
        }

    return {"predictions": predictions}


@app.get("/api/ml/trends")
async def get_trend_analysis(hours: int = 24):
    """Получение анализа трендов"""
    if not ML_ANALYTICS_AVAILABLE:
        return {"error": "ML Analytics not available"}

    historical_data = docs_manager.ml_predictor.get_ml_history(hours)
    trends = await advanced_analytics.generate_trend_analysis(historical_data)

    return trends


@app.get("/api/ml/insights")
async def get_ml_insights():
    """Получение ML инсайтов и рекомендаций"""
    if not ML_ANALYTICS_AVAILABLE:
        return {"error": "ML Analytics not available"}

    historical_data = docs_manager.ml_predictor.get_ml_history(24)
    insights = docs_manager.ml_predictor.generate_insights(historical_data)

    return insights


async def generate_html_report():
    """Генерация HTML отчета с графиками"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ALADDIN API Docs Report</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .chart-container {{ width: 400px; height: 300px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>🛡️ ALADDIN API Docs Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <div class="chart-container">
            <canvas id="successChart"></canvas>
        </div>
        
        <script>
            const ctx = document.getElementById('successChart')
                .getContext('2d');
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Success', 'Failed'],
                    datasets: [{{
                        data: [{len([t for t in docs_manager.test_history
                                   if t.success])},
                               {len([t for t in docs_manager.test_history
                                   if not t.success])}],
                        backgroundColor: ['#4CAF50', '#F44336']
                    }}]
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


async def get_enhanced_docs_page():
    """Генерация HTML страницы с улучшенным UI"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🛡️ ALADDIN Enhanced API Docs</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                min-height: 100vh;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
                padding: 30px 0;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            
            .header h1 {
                font-size: 3em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .header p {
                font-size: 1.2em;
                opacity: 0.9;
            }
            
            .dashboard {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin-bottom: 40px;
            }
            
            .card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 25px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .card h2 {
                margin-bottom: 20px;
                color: #4CAF50;
                font-size: 1.5em;
            }
            
            .endpoint-list {
                max-height: 400px;
                overflow-y: auto;
            }
            
            .endpoint-item {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                border-left: 4px solid #4CAF50;
            }
            
            .endpoint-method {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.8em;
                font-weight: bold;
                margin-right: 10px;
            }
            
            .method-get { background: #4CAF50; }
            .method-post { background: #2196F3; }
            .method-put { background: #FF9800; }
            .method-delete { background: #F44336; }
            
            .endpoint-path {
                font-family: 'Courier New', monospace;
                font-size: 1.1em;
            }
            
            .endpoint-description {
                margin-top: 5px;
                opacity: 0.8;
                font-size: 0.9em;
            }
            
            .service-status {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px;
                margin-bottom: 10px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
            }
            
            .status-indicator {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 10px;
            }
            
            .status-running { background: #4CAF50; }
            .status-stopped { background: #F44336; }
            .status-error { background: #FF9800; }
            
            .test-section {
                margin-top: 30px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 25px;
                backdrop-filter: blur(10px);
            }
            
            .test-form {
                display: grid;
                grid-template-columns: 1fr 1fr auto;
                gap: 15px;
                margin-bottom: 20px;
            }
            
            .test-form input, .test-form select {
                padding: 10px;
                border: none;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                font-size: 1em;
            }
            
            .test-form input::placeholder {
                color: rgba(255, 255, 255, 0.6);
            }
            
            .test-form button {
                padding: 10px 20px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1em;
                font-weight: bold;
            }
            
            .test-form button:hover {
                background: #45a049;
            }
            
            .test-results {
                max-height: 300px;
                overflow-y: auto;
            }
            
            .test-result {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                border-left: 4px solid #4CAF50;
            }
            
            .test-result.error {
                border-left-color: #F44336;
            }
            
            .loading {
                text-align: center;
                padding: 20px;
                font-size: 1.2em;
            }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 20px;
                text-align: center;
            }
            
            .stat-number {
                font-size: 2em;
                font-weight: bold;
                color: #4CAF50;
            }
            
            .stat-label {
                margin-top: 5px;
                opacity: 0.8;
            }
            
            @media (max-width: 768px) {
                .dashboard {
                    grid-template-columns: 1fr;
                }
                
                .test-form {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ ALADDIN Enhanced API Docs</h1>
                <p>Интерактивная документация и тестирование API системы безопасности</p>
            </div>
            
            <div class="stats" id="stats">
                <div class="stat-card">
                    <div class="stat-number" id="total-endpoints">-</div>
                    <div class="stat-label">API Endpoints</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="active-services">-</div>
                    <div class="stat-label">Активные сервисы</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="total-tests">-</div>
                    <div class="stat-label">Тестов выполнено</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="success-rate">-</div>
                    <div class="stat-label">Успешность %</div>
                </div>
            </div>
            
            <div class="dashboard">
                <div class="card">
                    <h2>📡 API Endpoints</h2>
                    <div class="endpoint-list" id="endpoints">
                        <div class="loading">Загрузка endpoints...</div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>🔧 Статус сервисов</h2>
                    <div id="services">
                        <div class="loading">Загрузка статуса сервисов...</div>
                    </div>
                </div>
            </div>
            
            <div class="test-section">
                <h2>🧪 Интерактивное тестирование</h2>
                <div class="test-form">
                    <input type="text" id="endpoint-input" placeholder="Введите endpoint (например: /health)" value="/health">
                    <select id="method-select">
                        <option value="GET">GET</option>
                        <option value="POST">POST</option>
                        <option value="PUT">PUT</option>
                        <option value="DELETE">DELETE</option>
                    </select>
                    <button onclick="testEndpoint()">Тестировать</button>
                </div>
                
                <div class="test-results" id="test-results">
                    <p>Результаты тестов появятся здесь...</p>
                </div>
            </div>
        </div>
        
        <script>
            let endpoints = [];
            let services = {};
            let testHistory = [];
            
            // Загрузка данных при загрузке страницы
            async function loadData() {
                try {
                    // Загрузка endpoints
                    const endpointsResponse = await fetch('/api/endpoints');
                    const endpointsData = await endpointsResponse.json();
                    endpoints = endpointsData.endpoints;
                    displayEndpoints();
                    
                    // Загрузка сервисов
                    const servicesResponse = await fetch('/api/services');
                    const servicesData = await servicesResponse.json();
                    services = servicesData.services;
                    displayServices();
                    
                    // Загрузка истории тестов
                    const historyResponse = await fetch('/api/test-history');
                    const historyData = await historyResponse.json();
                    testHistory = historyData.history;
                    displayStats();
                    
                } catch (error) {
                    console.error('Error loading data:', error);
                }
            }
            
            function displayEndpoints() {
                const container = document.getElementById('endpoints');
                if (endpoints.length === 0) {
                    container.innerHTML = '<p>Endpoints не найдены</p>';
                    return;
                }
                
                container.innerHTML = endpoints.map(endpoint => `
                    <div class="endpoint-item">
                        <span class="endpoint-method method-${endpoint.method.toLowerCase()}">${endpoint.method}</span>
                        <span class="endpoint-path">${endpoint.path}</span>
                        <div class="endpoint-description">${endpoint.description}</div>
                        <div style="margin-top: 5px; font-size: 0.8em; opacity: 0.7;">
                            Сервис: ${endpoint.service} | Безопасность: ${endpoint.security_level}
                        </div>
                    </div>
                `).join('');
            }
            
            function displayServices() {
                const container = document.getElementById('services');
                const serviceEntries = Object.entries(services);
                
                if (serviceEntries.length === 0) {
                    container.innerHTML = '<p>Сервисы не найдены</p>';
                    return;
                }
                
                container.innerHTML = serviceEntries.map(([name, service]) => `
                    <div class="service-status">
                        <div style="display: flex; align-items: center;">
                            <div class="status-indicator status-${service.status}"></div>
                            <div>
                                <div style="font-weight: bold;">${name}</div>
                                <div style="font-size: 0.8em; opacity: 0.7;">Порт: ${service.port}</div>
                            </div>
                        </div>
                        <div style="text-align: right; font-size: 0.8em;">
                            <div>CPU: ${service.cpu_usage.toFixed(1)}%</div>
                            <div>RAM: ${service.memory_usage.toFixed(1)}%</div>
                        </div>
                    </div>
                `).join('');
            }
            
            function displayStats() {
                document.getElementById('total-endpoints').textContent = endpoints.length;
                
                const activeServices = Object.values(services).filter(s => s.status === 'running').length;
                document.getElementById('active-services').textContent = activeServices;
                
                document.getElementById('total-tests').textContent = testHistory.length;
                
                if (testHistory.length > 0) {
                    const successCount = testHistory.filter(t => t.success).length;
                    const successRate = ((successCount / testHistory.length) * 100).toFixed(1);
                    document.getElementById('success-rate').textContent = successRate + '%';
                } else {
                    document.getElementById('success-rate').textContent = '0%';
                }
            }
            
            async function testEndpoint() {
                const endpoint = document.getElementById('endpoint-input').value;
                const method = document.getElementById('method-select').value;
                
                if (!endpoint) {
                    alert('Введите endpoint');
                    return;
                }
                
                const resultsContainer = document.getElementById('test-results');
                resultsContainer.innerHTML = '<div class="loading">Выполнение теста...</div>';
                
                try {
                    const response = await fetch('/api/test', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer demo_token'
                        },
                        body: JSON.stringify({
                            endpoint: endpoint,
                            method: method
                        })
                    });
                    
                    const result = await response.json();
                    
                    // Добавляем результат в историю
                    testHistory.unshift(result);
                    displayTestResults();
                    displayStats();
                    
                } catch (error) {
                    console.error('Test error:', error);
                    resultsContainer.innerHTML = '<div class="test-result error">Ошибка выполнения теста: ' + error.message + '</div>';
                }
            }
            
            function displayTestResults() {
                const container = document.getElementById('test-results');
                
                if (testHistory.length === 0) {
                    container.innerHTML = '<p>Результаты тестов появятся здесь...</p>';
                    return;
                }
                
                container.innerHTML = testHistory.slice(0, 10).map(result => `
                    <div class="test-result ${result.success ? '' : 'error'}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>${result.method} ${result.endpoint}</strong>
                                <span style="margin-left: 10px; padding: 2px 6px; background: ${result.success ? '#4CAF50' : '#F44336'}; border-radius: 4px; font-size: 0.8em;">
                                    ${result.status_code}
                                </span>
                            </div>
                            <div style="font-size: 0.8em; opacity: 0.7;">
                                ${result.response_time.toFixed(3)}s
                            </div>
                        </div>
                        ${result.error_message ? '<div style="margin-top: 5px; color: #F44336; font-size: 0.9em;">' + result.error_message + '</div>' : ''}
                        <div style="margin-top: 5px; font-size: 0.8em; opacity: 0.7;">
                            ${new Date(result.timestamp).toLocaleString()}
                        </div>
                    </div>
                `).join('');
            }
            
            // Автообновление каждые 30 секунд
            setInterval(loadData, 30000);
            
            // Загрузка данных при загрузке страницы
            loadData();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    print("🚀 Запуск ALADDIN Enhanced API Docs...")
    print("📡 Сканирование реальных API endpoints...")
    print("🔧 Мониторинг сервисов ALADDIN...")
    print("🛡️ Интеграция с системой безопасности...")

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
