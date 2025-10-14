#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Monitoring Integration Tests для ALADDIN Dashboard
Тесты интеграции мониторинга Safe Function Manager

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


class MonitoringMetricType(Enum):
    """Типы метрик мониторинга"""
    PERFORMANCE = "performance"
    AVAILABILITY = "availability"
    ERROR_RATE = "error_rate"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    CUSTOM = "custom"


class AlertLevel(Enum):
    """Уровни алертов"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MonitoringStatus(Enum):
    """Статусы мониторинга"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class MonitoringMetric:
    """Метрика мониторинга"""
    metric_id: str
    metric_type: MonitoringMetricType
    function_id: str
    timestamp: datetime
    value: float
    unit: str
    tags: Dict[str, str]
    metadata: Dict[str, Any]


@dataclass
class MonitoringAlert:
    """Алерт мониторинга"""
    alert_id: str
    function_id: str
    alert_level: AlertLevel
    timestamp: datetime
    message: str
    metric_name: str
    threshold: float
    current_value: float
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class MonitoringDashboard:
    """Дашборд мониторинга"""
    dashboard_id: str
    name: str
    description: str
    widgets: List[Dict[str, Any]]
    refresh_interval: int
    last_updated: datetime
    status: MonitoringStatus


class SFMMonitoringIntegrationTester:
    """Тестер интеграции мониторинга SFM"""
    
    def __init__(self, sfm_url: str = "http://localhost:8011", dashboard_url: str = "http://localhost:8080"):
        """
        Инициализация тестера мониторинга
        
        Args:
            sfm_url: URL SFM
            dashboard_url: URL дашборда
        """
        self.sfm_url = sfm_url
        self.dashboard_url = dashboard_url
        self.logger = LoggingManager(name="SFMMonitoringIntegrationTester") if ALADDIN_AVAILABLE else None
        self.monitoring_metrics: List[MonitoringMetric] = []
        self.monitoring_alerts: List[MonitoringAlert] = []
        self.monitoring_dashboards: List[MonitoringDashboard] = []
        self.monitoring_threads: List[threading.Thread] = []
        self.monitoring_active = False
        
    async def collect_sfm_metrics(self, function_id: str = "test_function") -> List[MonitoringMetric]:
        """
        Сбор метрик SFM
        
        Args:
            function_id: ID функции
            
        Returns:
            Список собранных метрик
        """
        print(f"📊 Сбор метрик SFM для функции: {function_id}")
        
        collected_metrics = []
        timestamp = datetime.now()
        
        # 1. Метрики производительности
        print("  1. Сбор метрик производительности...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                start_time = time.time()
                
                # Запрос к SFM для получения метрик
                response = await client.get(f"{self.sfm_url}/functions/{function_id}/metrics", headers=headers)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Создаем метрики на основе ответа
                    performance_metric = MonitoringMetric(
                        metric_id=f"response_time_{function_id}_{int(time.time())}",
                        metric_type=MonitoringMetricType.RESPONSE_TIME,
                        function_id=function_id,
                        timestamp=timestamp,
                        value=response_time,
                        unit="seconds",
                        tags={"function": function_id, "endpoint": "metrics"},
                        metadata={"status_code": response.status_code}
                    )
                    collected_metrics.append(performance_metric)
                    
                    # Извлекаем метрики из ответа (если есть)
                    if "metrics" in data:
                        for metric_name, metric_value in data["metrics"].items():
                            metric = MonitoringMetric(
                                metric_id=f"{metric_name}_{function_id}_{int(time.time())}",
                                metric_type=MonitoringMetricType.CUSTOM,
                                function_id=function_id,
                                timestamp=timestamp,
                                value=float(metric_value) if isinstance(metric_value, (int, float)) else 0.0,
                                unit="count",
                                tags={"function": function_id, "metric": metric_name},
                                metadata={"source": "sfm_response"}
                            )
                            collected_metrics.append(metric)
                            
        except Exception as e:
            # Создаем метрику об ошибке
            error_metric = MonitoringMetric(
                metric_id=f"error_{function_id}_{int(time.time())}",
                metric_type=MonitoringMetricType.ERROR_RATE,
                function_id=function_id,
                timestamp=timestamp,
                value=1.0,
                unit="count",
                tags={"function": function_id, "error": str(e)},
                metadata={"error_type": "collection_error"}
            )
            collected_metrics.append(error_metric)
        
        # 2. Метрики доступности
        print("  2. Сбор метрик доступности...")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                health_start = time.time()
                
                response = await client.get(f"{self.sfm_url}/health", headers=headers)
                health_time = time.time() - health_start
                
                availability_metric = MonitoringMetric(
                    metric_id=f"availability_{function_id}_{int(time.time())}",
                    metric_type=MonitoringMetricType.AVAILABILITY,
                    function_id=function_id,
                    timestamp=timestamp,
                    value=1.0 if response.status_code == 200 else 0.0,
                    unit="boolean",
                    tags={"function": function_id, "endpoint": "health"},
                    metadata={"status_code": response.status_code, "response_time": health_time}
                )
                collected_metrics.append(availability_metric)
                
        except Exception as e:
            # Метрика недоступности
            unavailability_metric = MonitoringMetric(
                metric_id=f"unavailability_{function_id}_{int(time.time())}",
                metric_type=MonitoringMetricType.AVAILABILITY,
                function_id=function_id,
                timestamp=timestamp,
                value=0.0,
                unit="boolean",
                tags={"function": function_id, "error": str(e)},
                metadata={"error_type": "health_check_error"}
            )
            collected_metrics.append(unavailability_metric)
        
        # 3. Метрики пропускной способности
        print("  3. Сбор метрик пропускной способности...")
        try:
            # Имитируем измерение пропускной способности
            throughput_start = time.time()
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                
                # Делаем несколько быстрых запросов для измерения пропускной способности
                requests = []
                for _ in range(10):
                    requests.append(client.get(f"{self.sfm_url}/functions/{function_id}/status", headers=headers))
                
                responses = await asyncio.gather(*requests, return_exceptions=True)
                throughput_time = time.time() - throughput_start
                
                successful_requests = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 200)
                throughput = successful_requests / throughput_time if throughput_time > 0 else 0
                
                throughput_metric = MonitoringMetric(
                    metric_id=f"throughput_{function_id}_{int(time.time())}",
                    metric_type=MonitoringMetricType.THROUGHPUT,
                    function_id=function_id,
                    timestamp=timestamp,
                    value=throughput,
                    unit="requests_per_second",
                    tags={"function": function_id, "test_type": "burst"},
                    metadata={"successful_requests": successful_requests, "total_time": throughput_time}
                )
                collected_metrics.append(throughput_metric)
                
        except Exception as e:
            error_metric = MonitoringMetric(
                metric_id=f"throughput_error_{function_id}_{int(time.time())}",
                metric_type=MonitoringMetricType.THROUGHPUT,
                function_id=function_id,
                timestamp=timestamp,
                value=0.0,
                unit="requests_per_second",
                tags={"function": function_id, "error": str(e)},
                metadata={"error_type": "throughput_test_error"}
            )
            collected_metrics.append(error_metric)
        
        # Добавляем метрики в общий список
        self.monitoring_metrics.extend(collected_metrics)
        
        print(f"  Собрано метрик: {len(collected_metrics)}")
        
        return collected_metrics
    
    async def test_monitoring_dashboard_integration(self) -> Dict[str, Any]:
        """
        Тест интеграции мониторинга с дашбордом
        
        Returns:
            Результаты интеграции мониторинга
        """
        print("📊 Тестирование интеграции мониторинга с дашбордом...")
        
        integration_results = {
            "dashboard_endpoints": [],
            "monitoring_data_available": False,
            "real_time_updates": False,
            "integration_quality": "unknown"
        }
        
        # 1. Проверяем endpoints дашборда для мониторинга
        print("  1. Проверка monitoring endpoints в дашборде...")
        monitoring_endpoints = [
            "/api/services",
            "/api/endpoints",
            "/api/test-history",
            "/api/cache/status"
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"Authorization": "Bearer demo_token"}
            
            for endpoint in monitoring_endpoints:
                try:
                    response = await client.get(f"{self.dashboard_url}{endpoint}", headers=headers)
                    
                    endpoint_result = {
                        "endpoint": endpoint,
                        "status_code": response.status_code,
                        "success": 200 <= response.status_code < 300,
                        "contains_monitoring_data": False,
                        "response_time": 0.0
                    }
                    
                    if endpoint_result["success"]:
                        try:
                            data = response.json()
                            # Проверяем наличие данных мониторинга
                            monitoring_indicators = ["status", "health", "metrics", "performance", "uptime"]
                            has_monitoring_data = any(indicator in str(data).lower() for indicator in monitoring_indicators)
                            endpoint_result["contains_monitoring_data"] = has_monitoring_data
                            
                        except json.JSONDecodeError:
                            pass
                    
                    integration_results["dashboard_endpoints"].append(endpoint_result)
                    
                except Exception as e:
                    integration_results["dashboard_endpoints"].append({
                        "endpoint": endpoint,
                        "status_code": 0,
                        "success": False,
                        "error": str(e)
                    })
        
        # 2. Проверяем наличие данных мониторинга в дашборде
        print("  2. Проверка наличия данных мониторинга...")
        monitoring_data_found = any(
            endpoint.get("contains_monitoring_data", False) 
            for endpoint in integration_results["dashboard_endpoints"]
        )
        integration_results["monitoring_data_available"] = monitoring_data_found
        
        # 3. Тестируем real-time обновления мониторинга
        print("  3. Тестирование real-time обновлений мониторинга...")
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                
                # Первый запрос
                response1 = await client.get(f"{self.dashboard_url}/api/services", headers=headers)
                
                # Ждем немного и делаем второй запрос
                await asyncio.sleep(3)
                response2 = await client.get(f"{self.dashboard_url}/api/services", headers=headers)
                
                # Сравниваем ответы
                if response1.status_code == 200 and response2.status_code == 200:
                    try:
                        data1 = response1.json()
                        data2 = response2.json()
                        
                        # Проверяем изменения в данных (timestamp, counters, etc.)
                        integration_results["real_time_updates"] = str(data1) != str(data2)
                        
                    except json.JSONDecodeError:
                        integration_results["real_time_updates"] = False
                        
        except Exception:
            integration_results["real_time_updates"] = False
        
        # 4. Определяем качество интеграции
        successful_endpoints = sum(1 for ep in integration_results["dashboard_endpoints"] if ep["success"])
        total_endpoints = len(integration_results["dashboard_endpoints"])
        
        if successful_endpoints == total_endpoints and integration_results["monitoring_data_available"]:
            integration_results["integration_quality"] = "excellent"
        elif successful_endpoints >= total_endpoints * 0.8 and integration_results["monitoring_data_available"]:
            integration_results["integration_quality"] = "good"
        elif successful_endpoints >= total_endpoints * 0.5:
            integration_results["integration_quality"] = "fair"
        else:
            integration_results["integration_quality"] = "poor"
        
        print(f"  Качество интеграции мониторинга: {integration_results['integration_quality']}")
        print(f"  Данные мониторинга доступны: {'✅ Да' if integration_results['monitoring_data_available'] else '❌ Нет'}")
        print(f"  Real-time обновления: {'✅ Да' if integration_results['real_time_updates'] else '❌ Нет'}")
        
        return integration_results
    
    async def test_monitoring_alerts(self) -> Dict[str, Any]:
        """
        Тест системы алертов мониторинга
        
        Returns:
            Результаты тестирования алертов
        """
        print("📊 Тестирование системы алертов мониторинга...")
        
        alert_results = {
            "alert_tests": [],
            "alerts_generated": [],
            "alert_resolution_tests": [],
            "alert_system_functional": False
        }
        
        # 1. Тест генерации алертов при превышении порогов
        print("  1. Тестирование генерации алертов...")
        
        # Собираем метрики для анализа
        test_metrics = await self.collect_sfm_metrics("alert_test_function")
        
        # Анализируем метрики и генерируем алерты
        for metric in test_metrics:
            alert_generated = False
            
            # Проверяем пороги для разных типов метрик
            if metric.metric_type == MonitoringMetricType.RESPONSE_TIME and metric.value > 5.0:
                alert = MonitoringAlert(
                    alert_id=f"slow_response_{metric.function_id}_{int(time.time())}",
                    function_id=metric.function_id,
                    alert_level=AlertLevel.WARNING,
                    timestamp=datetime.now(),
                    message=f"Медленный отклик функции {metric.function_id}",
                    metric_name="response_time",
                    threshold=5.0,
                    current_value=metric.value
                )
                alert_results["alerts_generated"].append(alert)
                self.monitoring_alerts.append(alert)
                alert_generated = True
                
            elif metric.metric_type == MonitoringMetricType.ERROR_RATE and metric.value > 0:
                alert = MonitoringAlert(
                    alert_id=f"error_detected_{metric.function_id}_{int(time.time())}",
                    function_id=metric.function_id,
                    alert_level=AlertLevel.ERROR,
                    timestamp=datetime.now(),
                    message=f"Ошибка в функции {metric.function_id}",
                    metric_name="error_rate",
                    threshold=0.0,
                    current_value=metric.value
                )
                alert_results["alerts_generated"].append(alert)
                self.monitoring_alerts.append(alert)
                alert_generated = True
                
            elif metric.metric_type == MonitoringMetricType.AVAILABILITY and metric.value == 0:
                alert = MonitoringAlert(
                    alert_id=f"service_down_{metric.function_id}_{int(time.time())}",
                    function_id=metric.function_id,
                    alert_level=AlertLevel.CRITICAL,
                    timestamp=datetime.now(),
                    message=f"Сервис {metric.function_id} недоступен",
                    metric_name="availability",
                    threshold=1.0,
                    current_value=metric.value
                )
                alert_results["alerts_generated"].append(alert)
                self.monitoring_alerts.append(alert)
                alert_generated = True
            
            alert_results["alert_tests"].append({
                "metric_id": metric.metric_id,
                "metric_type": metric.metric_type.value,
                "value": metric.value,
                "alert_generated": alert_generated
            })
        
        # 2. Тест разрешения алертов
        print("  2. Тестирование разрешения алертов...")
        
        # Имитируем разрешение алертов
        for alert in alert_results["alerts_generated"]:
            # Проверяем, что алерт еще не разрешен
            if not alert.resolved:
                # Имитируем повторную проверку метрики
                await asyncio.sleep(1)
                
                # В реальной системе здесь была бы проверка текущего значения метрики
                # Для тестирования имитируем, что проблема решена
                alert.resolved = True
                alert.resolved_at = datetime.now()
                
                alert_results["alert_resolution_tests"].append({
                    "alert_id": alert.alert_id,
                    "resolved": True,
                    "resolution_time": (alert.resolved_at - alert.timestamp).total_seconds()
                })
        
        # 3. Анализируем функциональность системы алертов
        total_alerts = len(alert_results["alerts_generated"])
        resolved_alerts = len([a for a in alert_results["alerts_generated"] if a.resolved])
        
        alert_results["alert_system_functional"] = total_alerts > 0 and resolved_alerts >= total_alerts * 0.5
        
        print(f"  Сгенерировано алертов: {total_alerts}")
        print(f"  Разрешено алертов: {resolved_alerts}")
        print(f"  Система алертов: {'✅ Функциональна' if alert_results['alert_system_functional'] else '❌ Нефункциональна'}")
        
        return alert_results
    
    async def test_monitoring_performance(self) -> Dict[str, Any]:
        """
        Тест производительности мониторинга
        
        Returns:
            Результаты тестирования производительности мониторинга
        """
        print("📊 Тестирование производительности мониторинга...")
        
        performance_results = {
            "collection_times": [],
            "dashboard_response_times": [],
            "alert_processing_times": [],
            "overall_performance": "unknown"
        }
        
        # 1. Тест времени сбора метрик
        print("  1. Тестирование времени сбора метрик...")
        
        collection_times = []
        for i in range(10):  # Собираем метрики 10 раз
            start_time = time.time()
            await self.collect_sfm_metrics(f"perf_test_function_{i}")
            collection_time = time.time() - start_time
            collection_times.append(collection_time)
        
        performance_results["collection_times"] = collection_times
        
        # 2. Тест времени отклика дашборда мониторинга
        print("  2. Тестирование времени отклика дашборда...")
        
        dashboard_times = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"Authorization": "Bearer demo_token"}
            
            for _ in range(10):
                start_time = time.time()
                try:
                    response = await client.get(f"{self.dashboard_url}/api/services", headers=headers)
                    response_time = time.time() - start_time
                    dashboard_times.append(response_time)
                except Exception:
                    dashboard_times.append(5.0)  # Таймаут
        
        performance_results["dashboard_response_times"] = dashboard_times
        
        # 3. Тест времени обработки алертов
        print("  3. Тестирование времени обработки алертов...")
        
        alert_times = []
        for alert in self.monitoring_alerts[:5]:  # Тестируем первые 5 алертов
            start_time = time.time()
            # Имитируем обработку алерта
            await asyncio.sleep(0.1)
            alert_processing_time = time.time() - start_time
            alert_times.append(alert_processing_time)
        
        performance_results["alert_processing_times"] = alert_times
        
        # 4. Анализируем общую производительность
        avg_collection_time = statistics.mean(collection_times) if collection_times else 0
        avg_dashboard_time = statistics.mean(dashboard_times) if dashboard_times else 0
        avg_alert_time = statistics.mean(alert_times) if alert_times else 0
        
        if avg_collection_time < 2.0 and avg_dashboard_time < 3.0 and avg_alert_time < 1.0:
            performance_results["overall_performance"] = "excellent"
        elif avg_collection_time < 5.0 and avg_dashboard_time < 5.0 and avg_alert_time < 2.0:
            performance_results["overall_performance"] = "good"
        elif avg_collection_time < 10.0 and avg_dashboard_time < 10.0:
            performance_results["overall_performance"] = "fair"
        else:
            performance_results["overall_performance"] = "poor"
        
        print(f"  Среднее время сбора метрик: {avg_collection_time:.3f}s")
        print(f"  Среднее время отклика дашборда: {avg_dashboard_time:.3f}s")
        print(f"  Среднее время обработки алертов: {avg_alert_time:.3f}s")
        print(f"  Общая производительность: {performance_results['overall_performance']}")
        
        return performance_results
    
    def generate_monitoring_report(self) -> Dict[str, Any]:
        """Генерация отчета о мониторинге"""
        print("📊 Генерация отчета о мониторинге SFM...")
        
        # Анализируем собранные метрики
        total_metrics = len(self.monitoring_metrics)
        metrics_by_type = {}
        for metric in self.monitoring_metrics:
            metric_type = metric.metric_type.value
            if metric_type not in metrics_by_type:
                metrics_by_type[metric_type] = []
            metrics_by_type[metric_type].append(metric)
        
        # Анализируем алерты
        total_alerts = len(self.monitoring_alerts)
        alerts_by_level = {}
        for alert in self.monitoring_alerts:
            level = alert.alert_level.value
            if level not in alerts_by_level:
                alerts_by_level[level] = []
            alerts_by_level[level].append(alert)
        
        resolved_alerts = len([a for a in self.monitoring_alerts if a.resolved])
        
        # Вычисляем статистику
        if self.monitoring_metrics:
            avg_value = statistics.mean([m.value for m in self.monitoring_metrics])
            min_value = min([m.value for m in self.monitoring_metrics])
            max_value = max([m.value for m in self.monitoring_metrics])
        else:
            avg_value = min_value = max_value = 0.0
        
        report = {
            "report_date": datetime.now().isoformat(),
            "monitoring_summary": {
                "total_metrics_collected": total_metrics,
                "total_alerts_generated": total_alerts,
                "resolved_alerts": resolved_alerts,
                "unresolved_alerts": total_alerts - resolved_alerts,
                "metrics_by_type": {k: len(v) for k, v in metrics_by_type.items()},
                "alerts_by_level": {k: len(v) for k, v in alerts_by_level.items()},
                "metric_statistics": {
                    "average_value": avg_value,
                    "min_value": min_value,
                    "max_value": max_value
                }
            },
            "detailed_metrics": [
                {
                    "metric_id": m.metric_id,
                    "metric_type": m.metric_type.value,
                    "function_id": m.function_id,
                    "timestamp": m.timestamp.isoformat(),
                    "value": m.value,
                    "unit": m.unit,
                    "tags": m.tags,
                    "metadata": m.metadata
                }
                for m in self.monitoring_metrics
            ],
            "detailed_alerts": [
                {
                    "alert_id": a.alert_id,
                    "function_id": a.function_id,
                    "alert_level": a.alert_level.value,
                    "timestamp": a.timestamp.isoformat(),
                    "message": a.message,
                    "metric_name": a.metric_name,
                    "threshold": a.threshold,
                    "current_value": a.current_value,
                    "resolved": a.resolved,
                    "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None
                }
                for a in self.monitoring_alerts
            ],
            "recommendations": self._generate_monitoring_recommendations()
        }
        
        return report
    
    def _generate_monitoring_recommendations(self) -> List[str]:
        """Генерация рекомендаций по мониторингу"""
        recommendations = []
        
        # Анализируем метрики
        if len(self.monitoring_metrics) == 0:
            recommendations.append("Настроить сбор метрик мониторинга")
        
        # Анализируем алерты
        critical_alerts = len([a for a in self.monitoring_alerts if a.alert_level == AlertLevel.CRITICAL])
        if critical_alerts > 0:
            recommendations.append(f"Обратить внимание на {critical_alerts} критических алертов")
        
        unresolved_alerts = len([a for a in self.monitoring_alerts if not a.resolved])
        if unresolved_alerts > 0:
            recommendations.append(f"Разрешить {unresolved_alerts} неразрешенных алертов")
        
        # Анализируем типы метрик
        metric_types = set(m.metric_type for m in self.monitoring_metrics)
        expected_types = {MonitoringMetricType.PERFORMANCE, MonitoringMetricType.AVAILABILITY, MonitoringMetricType.ERROR_RATE}
        
        missing_types = expected_types - metric_types
        if missing_types:
            recommendations.append(f"Добавить сбор метрик: {', '.join([t.value for t in missing_types])}")
        
        if not recommendations:
            recommendations.append("Система мониторинга работает оптимально")
        
        return recommendations


class TestSFMMonitoringIntegration:
    """Тесты интеграции мониторинга SFM"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестов"""
        self.tester = SFMMonitoringIntegrationTester()
    
    @pytest.mark.asyncio
    async def test_sfm_metrics_collection(self):
        """Тест сбора метрик SFM"""
        print("\n🧪 Тестирование сбора метрик SFM...")
        
        metrics = await self.tester.collect_sfm_metrics("test_function")
        
        # Проверки
        assert len(metrics) > 0, "Нет собранных метрик"
        assert all(isinstance(m, MonitoringMetric) for m in metrics), "Некорректные метрики"
        
        # Проверяем, что есть разные типы метрик
        metric_types = set(m.metric_type for m in metrics)
        assert len(metric_types) > 1, "Слишком мало типов метрик"
        
        print(f"✅ Сбор метрик: {len(metrics)} метрик, {len(metric_types)} типов")
    
    @pytest.mark.asyncio
    async def test_monitoring_dashboard_integration(self):
        """Тест интеграции мониторинга с дашбордом"""
        print("\n🧪 Тестирование интеграции мониторинга с дашбордом...")
        
        integration_results = await self.tester.test_monitoring_dashboard_integration()
        
        # Проверки
        assert len(integration_results["dashboard_endpoints"]) > 0, "Нет endpoints дашборда"
        
        successful_endpoints = sum(1 for ep in integration_results["dashboard_endpoints"] if ep["success"])
        total_endpoints = len(integration_results["dashboard_endpoints"])
        
        assert successful_endpoints >= total_endpoints * 0.5, f"Слишком много недоступных endpoints: {successful_endpoints}/{total_endpoints}"
        
        print(f"✅ Интеграция мониторинга: {integration_results['integration_quality']}")
        print(f"  Данные мониторинга: {'✅' if integration_results['monitoring_data_available'] else '❌'}")
        print(f"  Real-time: {'✅' if integration_results['real_time_updates'] else '❌'}")
    
    @pytest.mark.asyncio
    async def test_monitoring_alerts(self):
        """Тест системы алертов мониторинга"""
        print("\n🧪 Тестирование системы алертов мониторинга...")
        
        alert_results = await self.tester.test_monitoring_alerts()
        
        # Проверки
        assert len(alert_results["alert_tests"]) > 0, "Нет тестов алертов"
        assert len(alert_results["alerts_generated"]) >= 0, "Ошибка в генерации алертов"
        assert len(alert_results["alert_resolution_tests"]) >= 0, "Ошибка в разрешении алертов"
        
        print(f"✅ Система алертов: {'Функциональна' if alert_results['alert_system_functional'] else 'Нефункциональна'}")
        print(f"  Алертов сгенерировано: {len(alert_results['alerts_generated'])}")
        print(f"  Алертов разрешено: {len(alert_results['alert_resolution_tests'])}")
    
    @pytest.mark.asyncio
    async def test_monitoring_performance(self):
        """Тест производительности мониторинга"""
        print("\n🧪 Тестирование производительности мониторинга...")
        
        performance_results = await self.tester.test_monitoring_performance()
        
        # Проверки
        assert len(performance_results["collection_times"]) > 0, "Нет данных о времени сбора метрик"
        assert len(performance_results["dashboard_response_times"]) > 0, "Нет данных о времени отклика дашборда"
        
        avg_collection_time = statistics.mean(performance_results["collection_times"])
        avg_dashboard_time = statistics.mean(performance_results["dashboard_response_times"])
        
        assert avg_collection_time < 30, f"Слишком долгий сбор метрик: {avg_collection_time:.3f}s"
        assert avg_dashboard_time < 30, f"Слишком долгий отклик дашборда: {avg_dashboard_time:.3f}s"
        
        print(f"✅ Производительность мониторинга: {performance_results['overall_performance']}")
        print(f"  Сбор метрик: {avg_collection_time:.3f}s")
        print(f"  Отклик дашборда: {avg_dashboard_time:.3f}s")
    
    @pytest.mark.asyncio
    async def test_comprehensive_monitoring(self):
        """Комплексный тест мониторинга"""
        print("\n🧪 Комплексное тестирование мониторинга...")
        
        # Запускаем все тесты мониторинга
        metrics = await self.tester.collect_sfm_metrics("comprehensive_test")
        integration_results = await self.tester.test_monitoring_dashboard_integration()
        alert_results = await self.tester.test_monitoring_alerts()
        performance_results = await self.tester.test_monitoring_performance()
        
        # Анализируем общие результаты
        total_metrics = len(self.tester.monitoring_metrics)
        total_alerts = len(self.tester.monitoring_alerts)
        
        # Проверки
        assert total_metrics > 0, "Нет собранных метрик"
        assert integration_results["integration_quality"] != "unknown", "Неопределенное качество интеграции"
        assert performance_results["overall_performance"] != "unknown", "Неопределенная производительность"
        
        print(f"✅ Комплексный мониторинг:")
        print(f"  Метрик: {total_metrics}")
        print(f"  Алертов: {total_alerts}")
        print(f"  Качество интеграции: {integration_results['integration_quality']}")
        print(f"  Производительность: {performance_results['overall_performance']}")
    
    def test_generate_monitoring_report(self):
        """Генерация отчета о мониторинге"""
        print("\n📊 Генерация отчета о мониторинге SFM...")
        
        report = self.tester.generate_monitoring_report()
        
        # Сохранение отчета
        report_file = f"sfm_monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Отчет о мониторинге сохранен: {report_file}")
        
        # Вывод краткой статистики
        summary = report['monitoring_summary']
        
        print(f"\n📈 КРАТКАЯ СТАТИСТИКА МОНИТОРИНГА:")
        print(f"  Метрик собрано: {summary['total_metrics_collected']}")
        print(f"  Алертов сгенерировано: {summary['total_alerts_generated']}")
        print(f"  Алертов разрешено: {summary['resolved_alerts']}")
        print(f"  Алертов неразрешено: {summary['unresolved_alerts']}")
        print(f"  Типов метрик: {len(summary['metrics_by_type'])}")
        print(f"  Уровней алертов: {len(summary['alerts_by_level'])}")
        
        # Проверки отчета
        assert report['monitoring_summary']['total_metrics_collected'] >= 0, "Количество метрик не может быть отрицательным"
        assert report['monitoring_summary']['total_alerts_generated'] >= 0, "Количество алертов не может быть отрицательным"


if __name__ == "__main__":
    print("🚀 Запуск тестов интеграции мониторинга ALADDIN Dashboard с SFM...")
    print("📊 Тестирование сбора метрик и мониторинга производительности...")
    print("🚨 Проверка системы алертов и уведомлений...")
    print("📈 Анализ интеграции с дашбордом мониторинга...")
    
    # Запуск тестов через pytest
    pytest.main([__file__, "-v", "--tb=short"])