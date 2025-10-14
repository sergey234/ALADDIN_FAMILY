# -*- coding: utf-8 -*-
"""
Интеграционные тесты производительности для Service Mesh Manager

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import pytest
import time
import threading
import asyncio
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import json
import os

from security.microservices.service_mesh_manager import (
    ServiceMeshManager,
    ServiceInfo,
    ServiceType,
    ServiceEndpoint,
    ServiceRequest,
    ServiceResponse,
    ServiceStatus,
    LoadBalancingStrategy,
    # Исключения
    ServiceMeshError,
    ServiceNotFoundError,
    ServiceAlreadyRegisteredError,
    CircuitBreakerOpenError,
    ServiceUnavailableError,
    InvalidServiceConfigurationError,
    LoadBalancingError,
    HealthCheckError,
    MetricsCollectionError
)


class TestPerformanceIntegration:
    """Интеграционные тесты производительности"""
    
    @pytest.fixture
    def manager(self):
        """Фикстура для создания экземпляра ServiceMeshManager"""
        return ServiceMeshManager()
    
    @pytest.fixture
    def performance_service(self):
        """Фикстура для сервиса производительности"""
        endpoint = ServiceEndpoint(
            service_id="performance_service",
            host="localhost",
            port=8080,
            protocol="http",
            path="/performance"
        )
        return ServiceInfo(
            service_id="performance_service",
            name="Performance Service",
            description="Service for performance testing",
            service_type=ServiceType.API,
            version="1.0.0",
            endpoints=[endpoint],
            dependencies=[]
        )
    
    @pytest.mark.performance
    def test_throughput_performance(self, manager, performance_service):
        """Тест пропускной способности"""
        manager.initialize()
        assert manager.register_service(performance_service) is True
        
        # Тест пропускной способности
        num_requests = 1000
        start_time = time.time()
        
        responses = []
        for i in range(num_requests):
            response = manager.send_request("performance_service", "GET", f"/throughput_{i}")
            responses.append(response)
        
        end_time = time.time()
        total_time = end_time - start_time
        throughput = num_requests / total_time
        
        # Проверяем результаты
        assert len(responses) == num_requests
        successful_responses = [r for r in responses if isinstance(r, ServiceResponse) and r.status_code in [200, 201, 202]]
        success_rate = len(successful_responses) / num_requests
        
        # Требования к производительности
        assert throughput > 10  # Минимум 10 запросов в секунду
        assert success_rate > 0.9  # Минимум 90% успешных запросов
        assert total_time < 100  # Максимум 100 секунд
        
        print(f"Throughput: {throughput:.2f} requests/second")
        print(f"Success rate: {success_rate:.2%}")
        print(f"Total time: {total_time:.2f} seconds")
        
        manager.stop()
    
    @pytest.mark.performance
    def test_latency_performance(self, manager, performance_service):
        """Тест задержки"""
        manager.initialize()
        assert manager.register_service(performance_service) is True
        
        # Тест задержки
        num_requests = 100
        latencies = []
        
        for i in range(num_requests):
            start_time = time.time()
            response = manager.send_request("performance_service", "GET", f"/latency_{i}")
            end_time = time.time()
            
            if isinstance(response, ServiceResponse):
                latency = end_time - start_time
                latencies.append(latency)
        
        # Анализ задержек
        if latencies:
            avg_latency = statistics.mean(latencies)
            p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95-й перцентиль
            p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99-й перцентиль
            max_latency = max(latencies)
            
            # Требования к задержке
            assert avg_latency < 1.0  # Средняя задержка менее 1 секунды
            assert p95_latency < 2.0  # 95% запросов менее 2 секунд
            assert p99_latency < 5.0  # 99% запросов менее 5 секунд
            
            print(f"Average latency: {avg_latency:.3f} seconds")
            print(f"P95 latency: {p95_latency:.3f} seconds")
            print(f"P99 latency: {p99_latency:.3f} seconds")
            print(f"Max latency: {max_latency:.3f} seconds")
        
        manager.stop()
    
    @pytest.mark.performance
    def test_concurrent_performance(self, manager, performance_service):
        """Тест производительности при конкурентных запросах"""
        manager.initialize()
        assert manager.register_service(performance_service) is True
        
        # Параметры теста
        num_threads = 10
        requests_per_thread = 50
        total_requests = num_threads * requests_per_thread
        
        def send_requests(thread_id):
            """Функция для отправки запросов в отдельном потоке"""
            responses = []
            for i in range(requests_per_thread):
                try:
                    response = manager.send_request("performance_service", "GET", f"/concurrent_{thread_id}_{i}")
                    responses.append(response)
                except Exception as e:
                    responses.append(e)
            return responses
        
        # Запуск конкурентных запросов
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(send_requests, i) for i in range(num_threads)]
            all_responses = []
            
            for future in as_completed(futures):
                responses = future.result()
                all_responses.extend(responses)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Анализ результатов
        assert len(all_responses) == total_requests
        
        successful_responses = [r for r in all_responses if isinstance(r, ServiceResponse) and r.status_code in [200, 201, 202]]
        success_rate = len(successful_responses) / total_requests
        throughput = total_requests / total_time
        
        # Требования к производительности
        assert success_rate > 0.8  # Минимум 80% успешных запросов
        assert throughput > 5  # Минимум 5 запросов в секунду
        assert total_time < 200  # Максимум 200 секунд
        
        print(f"Concurrent throughput: {throughput:.2f} requests/second")
        print(f"Success rate: {success_rate:.2%}")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Threads: {num_threads}, Requests per thread: {requests_per_thread}")
        
        manager.stop()
    
    @pytest.mark.performance
    def test_memory_performance(self, manager, performance_service):
        """Тест производительности памяти"""
        manager.initialize()
        assert manager.register_service(performance_service) is True
        
        # Тест использования памяти
        initial_memory = self._get_memory_usage()
        
        # Отправляем много запросов
        num_requests = 500
        responses = []
        
        for i in range(num_requests):
            response = manager.send_request("performance_service", "GET", f"/memory_{i}")
            responses.append(response)
            
            # Проверяем память каждые 100 запросов
            if i % 100 == 0:
                current_memory = self._get_memory_usage()
                memory_increase = current_memory - initial_memory
                assert memory_increase < 100 * 1024 * 1024  # Максимум 100MB увеличения
        
        final_memory = self._get_memory_usage()
        total_memory_increase = final_memory - initial_memory
        
        # Требования к памяти
        assert total_memory_increase < 50 * 1024 * 1024  # Максимум 50MB увеличения
        
        print(f"Initial memory: {initial_memory / 1024 / 1024:.2f} MB")
        print(f"Final memory: {final_memory / 1024 / 1024:.2f} MB")
        print(f"Memory increase: {total_memory_increase / 1024 / 1024:.2f} MB")
        
        manager.stop()
    
    def _get_memory_usage(self):
        """Получение использования памяти"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            # Если psutil недоступен, возвращаем 0
            return 0
    
    @pytest.mark.performance
    def test_cpu_performance(self, manager, performance_service):
        """Тест производительности CPU"""
        manager.initialize()
        assert manager.register_service(performance_service) is True
        
        # Тест использования CPU
        initial_cpu = self._get_cpu_usage()
        
        # Отправляем много запросов
        num_requests = 200
        responses = []
        
        for i in range(num_requests):
            response = manager.send_request("performance_service", "GET", f"/cpu_{i}")
            responses.append(response)
        
        final_cpu = self._get_cpu_usage()
        
        # Проверяем, что CPU не перегружен
        assert final_cpu < 80  # Максимум 80% CPU
        
        print(f"Initial CPU: {initial_cpu:.2f}%")
        print(f"Final CPU: {final_cpu:.2f}%")
        
        manager.stop()
    
    def _get_cpu_usage(self):
        """Получение использования CPU"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            # Если psutil недоступен, возвращаем 0
            return 0
    
    @pytest.mark.performance
    def test_scalability_performance(self, manager):
        """Тест масштабируемости"""
        manager.initialize()
        
        # Создаем несколько сервисов для тестирования масштабируемости
        services = []
        for i in range(10):
            service = ServiceInfo(
                service_id=f"scalability_service_{i}",
                name=f"Scalability Service {i}",
                description=f"Service {i} for scalability testing",
                service_type=ServiceType.API,
                version="1.0.0",
                endpoints=[ServiceEndpoint(f"scalability_service_{i}", "localhost", 8080 + i, "http", f"/service_{i}")],
                dependencies=[]
            )
            services.append(service)
            assert manager.register_service(service) is True
        
        # Отправляем запросы ко всем сервисам
        num_requests_per_service = 20
        total_requests = len(services) * num_requests_per_service
        
        start_time = time.time()
        responses = []
        
        for service in services:
            for i in range(num_requests_per_service):
                response = manager.send_request(service.service_id, "GET", f"/scalability_{i}")
                responses.append(response)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Анализ результатов
        assert len(responses) == total_requests
        
        successful_responses = [r for r in responses if isinstance(r, ServiceResponse) and r.status_code in [200, 201, 202]]
        success_rate = len(successful_responses) / total_requests
        throughput = total_requests / total_time
        
        # Требования к масштабируемости
        assert success_rate > 0.8  # Минимум 80% успешных запросов
        assert throughput > 2  # Минимум 2 запроса в секунду
        assert total_time < 300  # Максимум 300 секунд
        
        print(f"Services: {len(services)}")
        print(f"Total requests: {total_requests}")
        print(f"Scalability throughput: {throughput:.2f} requests/second")
        print(f"Success rate: {success_rate:.2%}")
        print(f"Total time: {total_time:.2f} seconds")
        
        manager.stop()
    
    @pytest.mark.performance
    def test_stress_performance(self, manager, performance_service):
        """Тест стресс-тестирования"""
        manager.initialize()
        assert manager.register_service(performance_service) is True
        
        # Стресс-тест с большим количеством запросов
        num_requests = 2000
        start_time = time.time()
        
        responses = []
        errors = 0
        
        for i in range(num_requests):
            try:
                response = manager.send_request("performance_service", "GET", f"/stress_{i}")
                responses.append(response)
            except Exception as e:
                errors += 1
                responses.append(e)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Анализ результатов стресс-теста
        successful_responses = [r for r in responses if isinstance(r, ServiceResponse) and r.status_code in [200, 201, 202]]
        success_rate = len(successful_responses) / num_requests
        error_rate = errors / num_requests
        throughput = num_requests / total_time
        
        # Требования к стресс-тесту
        assert success_rate > 0.7  # Минимум 70% успешных запросов
        assert error_rate < 0.3  # Максимум 30% ошибок
        assert throughput > 1  # Минимум 1 запрос в секунду
        assert total_time < 600  # Максимум 600 секунд
        
        print(f"Stress test results:")
        print(f"Total requests: {num_requests}")
        print(f"Successful: {len(successful_responses)}")
        print(f"Errors: {errors}")
        print(f"Success rate: {success_rate:.2%}")
        print(f"Error rate: {error_rate:.2%}")
        print(f"Throughput: {throughput:.2f} requests/second")
        print(f"Total time: {total_time:.2f} seconds")
        
        manager.stop()
    
    @pytest.mark.performance
    def test_endurance_performance(self, manager, performance_service):
        """Тест выносливости (длительная работа)"""
        manager.initialize()
        assert manager.register_service(performance_service) is True
        
        # Тест выносливости - длительная работа
        test_duration = 30  # 30 секунд
        start_time = time.time()
        request_count = 0
        responses = []
        
        while time.time() - start_time < test_duration:
            response = manager.send_request("performance_service", "GET", f"/endurance_{request_count}")
            responses.append(response)
            request_count += 1
            
            # Небольшая пауза между запросами
            time.sleep(0.1)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        # Анализ результатов выносливости
        successful_responses = [r for r in responses if isinstance(r, ServiceResponse) and r.status_code in [200, 201, 202]]
        success_rate = len(successful_responses) / len(responses) if responses else 0
        throughput = len(responses) / actual_duration
        
        # Требования к выносливости
        assert success_rate > 0.8  # Минимум 80% успешных запросов
        assert throughput > 0.5  # Минимум 0.5 запросов в секунду
        assert actual_duration >= test_duration * 0.9  # Минимум 90% от запланированного времени
        
        print(f"Endurance test results:")
        print(f"Test duration: {test_duration} seconds")
        print(f"Actual duration: {actual_duration:.2f} seconds")
        print(f"Total requests: {len(responses)}")
        print(f"Success rate: {success_rate:.2%}")
        print(f"Throughput: {throughput:.2f} requests/second")
        
        manager.stop()


if __name__ == "__main__":
    pytest.main([__file__])
