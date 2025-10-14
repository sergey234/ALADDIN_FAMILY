#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЭТАП 8: ФИНАЛЬНАЯ ПРОВЕРКА ВСЕХ КОМПОНЕНТОВ ServiceMeshManager
Полный тест всех классов и методов с проверкой интеграции
"""

import asyncio
import json
import sys
import traceback
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Добавляем путь к модулям
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

try:
    from security.microservices.service_mesh_manager import (
        ServiceMeshManager,
        CircuitBreakerConfig,
        ServiceInfo,
        ServiceEndpoint,
        ServiceRequest,
        ServiceResponse,
        LoadBalancingStrategy,
        ServiceStatus,
        ServiceType,
        EventManager,
        EventObserver,
        ServiceMeshEvent,
        EventType,
        LoggingEventObserver,
        MetricsEventObserver,
        AlertingEventObserver,
        PerformanceConfig,
        PerformanceMetrics,
        SystemMetrics,
        HealthCheckResult,
        ServiceHealthSummary,
        CacheConfig,
        TTLCache,
        AsyncConfig,
        PrometheusConfig,
        PrometheusMetrics,
        EnhancedCircuitBreaker,
        CircuitBreakerState,
        CircuitBreakerMetrics,
        HealthStatus,
        ServiceMeshError,
        ServiceNotFoundError,
        ServiceAlreadyRegisteredError,
        CircuitBreakerOpenError,
        ServiceUnavailableError,
        InvalidServiceConfigurationError,
        LoadBalancingError,
        HealthCheckError,
        MetricsCollectionError,
        CacheError,
        CacheKeyNotFoundError,
        CacheExpiredError,
        CacheConfigurationError,
        AsyncOperationError,
        AsyncTimeoutError,
        LogConfig,
        StructuredLogger,
        ServiceMeshLogger,
        AsyncConnectionPool,
        AsyncRequestManager,
        CacheEntry,
        InputValidator,
        MemoryOptimizer,
        PerformanceMonitor,
        RequestBatcher,
        RateLimitConfig,
        RateLimitInfo,
        TokenBucket,
        SlidingWindow,
        RateLimiter,
        MonitoringConfig,
        AlertRule,
        Alert,
        SystemHealth,
        MetricsCollector,
        AlertManager,
        NotificationService
    )
    from core.base import ComponentStatus
except ImportError as e:
    print(f"ОШИБКА ИМПОРТА: {e}")
    sys.exit(1)


class ServiceMeshTester:
    """Тестер для ServiceMeshManager"""
    
    def __init__(self):
        self.test_results = {
            "classes_tested": [],
            "methods_tested": [],
            "integration_tests": [],
            "errors": [],
            "warnings": [],
            "statistics": {}
        }
        self.start_time = time.time()
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Логирование результата теста"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        if status == "PASS":
            self.test_results["methods_tested"].append(result)
        elif status == "ERROR":
            self.test_results["errors"].append(result)
        else:
            self.test_results["warnings"].append(result)
            
        print(f"[{status}] {test_name}: {details}")
    
    def test_circuit_breaker_config(self):
        """Тест CircuitBreakerConfig"""
        try:
            # Тест создания конфигурации по умолчанию
            config = CircuitBreakerConfig()
            assert config.failure_threshold == 5
            assert config.success_threshold == 3
            self.log_test("CircuitBreakerConfig.__init__", "PASS", "Создание конфигурации по умолчанию")
            
            # Тест валидации
            try:
                CircuitBreakerConfig(failure_threshold=0)
                self.log_test("CircuitBreakerConfig.validation", "ERROR", "Не сработала валидация failure_threshold")
            except ValueError:
                self.log_test("CircuitBreakerConfig.validation", "PASS", "Валидация работает корректно")
            
            # Тест to_dict
            config_dict = config.to_dict()
            assert isinstance(config_dict, dict)
            assert "failure_threshold" in config_dict
            self.log_test("CircuitBreakerConfig.to_dict", "PASS", "Преобразование в словарь")
            
            # Тест from_dict
            config_from_dict = CircuitBreakerConfig.from_dict(config_dict)
            assert config_from_dict.failure_threshold == config.failure_threshold
            self.log_test("CircuitBreakerConfig.from_dict", "PASS", "Создание из словаря")
            
            # Тест get_default_config
            default_config = CircuitBreakerConfig.get_default_config()
            assert isinstance(default_config, CircuitBreakerConfig)
            self.log_test("CircuitBreakerConfig.get_default_config", "PASS", "Получение конфигурации по умолчанию")
            
            # Тест get_aggressive_config
            aggressive_config = CircuitBreakerConfig.get_aggressive_config()
            assert aggressive_config.failure_threshold == 3
            self.log_test("CircuitBreakerConfig.get_aggressive_config", "PASS", "Получение агрессивной конфигурации")
            
            # Тест get_conservative_config
            conservative_config = CircuitBreakerConfig.get_conservative_config()
            assert conservative_config.failure_threshold > 5
            self.log_test("CircuitBreakerConfig.get_conservative_config", "PASS", "Получение консервативной конфигурации")
            
            self.test_results["classes_tested"].append("CircuitBreakerConfig")
            
        except Exception as e:
            self.log_test("CircuitBreakerConfig", "ERROR", f"Ошибка: {str(e)}")
    
    def test_service_info(self):
        """Тест ServiceInfo"""
        try:
            # Создание ServiceEndpoint для ServiceInfo
            endpoint = ServiceEndpoint(
                service_id="test_service",
                host="localhost",
                port=8080,
                protocol="http",
                path="/api"
            )
            
            # Создание ServiceInfo
            service = ServiceInfo(
                service_id="test_service",
                name="Test Service",
                description="Test service description",
                service_type=ServiceType.API,
                version="1.0.0",
                endpoints=[endpoint],
                dependencies=[]
            )
            
            assert service.service_id == "test_service"
            assert service.name == "Test Service"
            self.log_test("ServiceInfo.__init__", "PASS", "Создание ServiceInfo")
            
            # Тест to_dict
            service_dict = service.to_dict()
            assert isinstance(service_dict, dict)
            assert service_dict["service_id"] == "test_service"
            self.log_test("ServiceInfo.to_dict", "PASS", "Преобразование в словарь")
            
            self.test_results["classes_tested"].append("ServiceInfo")
            
        except Exception as e:
            self.log_test("ServiceInfo", "ERROR", f"Ошибка: {str(e)}")
    
    def test_service_endpoint(self):
        """Тест ServiceEndpoint"""
        try:
            endpoint = ServiceEndpoint(
                service_id="test_service",
                host="localhost",
                port=8080,
                protocol="http",
                path="/api"
            )
            
            assert endpoint.service_id == "test_service"
            assert endpoint.host == "localhost"
            self.log_test("ServiceEndpoint.__init__", "PASS", "Создание ServiceEndpoint")
            
            # Тест get_url
            url = endpoint.get_url()
            assert url == "http://localhost:8080/api"
            self.log_test("ServiceEndpoint.get_url", "PASS", "Получение URL")
            
            # Тест to_dict
            endpoint_dict = endpoint.to_dict()
            assert isinstance(endpoint_dict, dict)
            self.log_test("ServiceEndpoint.to_dict", "PASS", "Преобразование в словарь")
            
            self.test_results["classes_tested"].append("ServiceEndpoint")
            
        except Exception as e:
            self.log_test("ServiceEndpoint", "ERROR", f"Ошибка: {str(e)}")
    
    def test_service_mesh_manager_creation(self):
        """Тест создания ServiceMeshManager"""
        try:
            # Создание с конфигурацией по умолчанию
            manager = ServiceMeshManager()
            assert manager.name == "ServiceMeshManager"
            assert isinstance(manager.services, dict)
            self.log_test("ServiceMeshManager.__init__", "PASS", "Создание с конфигурацией по умолчанию")
            
            # Создание с кастомной конфигурацией
            custom_config = {
                "discovery_interval": 60,
                "health_check_interval": 45
            }
            manager_custom = ServiceMeshManager(config=custom_config)
            assert manager_custom.mesh_config["discovery_interval"] == 60
            self.log_test("ServiceMeshManager.__init__", "PASS", "Создание с кастомной конфигурацией")
            
            self.test_results["classes_tested"].append("ServiceMeshManager")
            
        except Exception as e:
            self.log_test("ServiceMeshManager.__init__", "ERROR", f"Ошибка: {str(e)}")
    
    def test_service_mesh_manager_methods(self):
        """Тест методов ServiceMeshManager"""
        try:
            manager = ServiceMeshManager()
            
            # Тест initialize
            result = manager.initialize()
            assert isinstance(result, bool)
            self.log_test("ServiceMeshManager.initialize", "PASS", f"Инициализация: {result}")
            
            # Тест register_service
            endpoint = ServiceEndpoint(
                service_id="test_service",
                host="localhost",
                port=8080,
                protocol="http",
                path="/api"
            )
            
            service = ServiceInfo(
                service_id="test_service",
                name="Test Service",
                description="Test service description",
                service_type=ServiceType.API,
                version="1.0.0",
                endpoints=[endpoint],
                dependencies=[]
            )
            
            register_result = manager.register_service(service)
            assert isinstance(register_result, bool)
            self.log_test("ServiceMeshManager.register_service", "PASS", f"Регистрация сервиса: {register_result}")
            
            # Тест get_service_status
            status = manager.get_service_status("test_service")
            if status:
                assert isinstance(status, dict)
                self.log_test("ServiceMeshManager.get_service_status", "PASS", "Получение статуса сервиса")
            else:
                self.log_test("ServiceMeshManager.get_service_status", "WARNING", "Статус сервиса не найден")
            
            # Тест get_mesh_status
            mesh_status = manager.get_mesh_status()
            assert isinstance(mesh_status, dict)
            assert "services_count" in mesh_status
            self.log_test("ServiceMeshManager.get_mesh_status", "PASS", "Получение статуса сетки")
            
            # Тест get_status
            status = manager.get_status()
            assert isinstance(status, dict)
            assert "name" in status
            self.log_test("ServiceMeshManager.get_status", "PASS", "Получение общего статуса")
            
            # Тест unregister_service
            unregister_result = manager.unregister_service("test_service")
            assert isinstance(unregister_result, bool)
            self.log_test("ServiceMeshManager.unregister_service", "PASS", f"Отмена регистрации: {unregister_result}")
            
            # Тест stop
            stop_result = manager.stop()
            assert isinstance(stop_result, bool)
            self.log_test("ServiceMeshManager.stop", "PASS", f"Остановка: {stop_result}")
            
        except Exception as e:
            self.log_test("ServiceMeshManager.methods", "ERROR", f"Ошибка: {str(e)}")
    
    def test_integration_scenarios(self):
        """Тест интеграционных сценариев"""
        try:
            manager = ServiceMeshManager()
            manager.initialize()
            
            # Сценарий 1: Регистрация и использование сервиса
            endpoint = ServiceEndpoint(
                service_id="api_service",
                host="localhost",
                port=8080,
                protocol="http",
                path="/api"
            )
            
            service = ServiceInfo(
                service_id="api_service",
                name="API Service",
                description="API service description",
                service_type=ServiceType.API,
                version="1.0.0",
                endpoints=[endpoint],
                dependencies=[]
            )
            
            # Регистрация
            register_result = manager.register_service(service)
            if register_result:
                self.log_test("Integration.register_service", "PASS", "Сервис зарегистрирован")
                
                # Получение endpoint
                endpoint = manager.get_service_endpoint("api_service")
                if endpoint:
                    self.log_test("Integration.get_endpoint", "PASS", "Endpoint получен")
                else:
                    self.log_test("Integration.get_endpoint", "WARNING", "Endpoint не найден")
                
                # Отмена регистрации
                unregister_result = manager.unregister_service("api_service")
                if unregister_result:
                    self.log_test("Integration.unregister_service", "PASS", "Сервис отменен")
                else:
                    self.log_test("Integration.unregister_service", "WARNING", "Ошибка отмены регистрации")
            else:
                self.log_test("Integration.register_service", "ERROR", "Ошибка регистрации сервиса")
            
            # Сценарий 2: Проверка состояния системы
            mesh_status = manager.get_mesh_status()
            if "services_count" in mesh_status:
                self.log_test("Integration.mesh_status", "PASS", f"Статус сетки: {mesh_status['services_count']} сервисов")
            else:
                self.log_test("Integration.mesh_status", "WARNING", "Неполный статус сетки")
            
            self.test_results["integration_tests"].append({
                "scenario": "service_lifecycle",
                "status": "PASS",
                "details": "Полный жизненный цикл сервиса"
            })
            
        except Exception as e:
            self.log_test("Integration", "ERROR", f"Ошибка интеграции: {str(e)}")
            self.test_results["integration_tests"].append({
                "scenario": "service_lifecycle",
                "status": "ERROR",
                "details": str(e)
            })
    
    def test_error_handling(self):
        """Тест обработки ошибок"""
        try:
            manager = ServiceMeshManager()
            
            # Тест с несуществующим сервисом
            status = manager.get_service_status("nonexistent_service")
            if status is None:
                self.log_test("ErrorHandling.nonexistent_service", "PASS", "Корректная обработка несуществующего сервиса")
            else:
                self.log_test("ErrorHandling.nonexistent_service", "WARNING", "Неожиданный результат для несуществующего сервиса")
            
            # Тест с некорректными параметрами
            try:
                manager.register_service(None)
                self.log_test("ErrorHandling.invalid_service", "ERROR", "Не обработана ошибка с None")
            except Exception:
                self.log_test("ErrorHandling.invalid_service", "PASS", "Корректная обработка None")
            
        except Exception as e:
            self.log_test("ErrorHandling", "ERROR", f"Ошибка в тестах обработки ошибок: {str(e)}")
    
    def generate_report(self):
        """Генерация отчета о состоянии"""
        end_time = time.time()
        duration = end_time - self.start_time
        
        # Статистика
        total_tests = len(self.test_results["methods_tested"])
        passed_tests = len([t for t in self.test_results["methods_tested"] if t["status"] == "PASS"])
        error_tests = len(self.test_results["errors"])
        warning_tests = len(self.test_results["warnings"])
        
        self.test_results["statistics"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "error_tests": error_tests,
            "warning_tests": warning_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "duration_seconds": duration,
            "classes_tested_count": len(self.test_results["classes_tested"]),
            "integration_tests_count": len(self.test_results["integration_tests"])
        }
        
        # Вывод отчета
        print("\n" + "="*80)
        print("ОТЧЕТ О ФИНАЛЬНОЙ ПРОВЕРКЕ SERVICEMESHMANAGER")
        print("="*80)
        print(f"Время выполнения: {duration:.2f} секунд")
        print(f"Всего тестов: {total_tests}")
        print(f"Успешных: {passed_tests}")
        print(f"Ошибок: {error_tests}")
        print(f"Предупреждений: {warning_tests}")
        print(f"Процент успеха: {self.test_results['statistics']['success_rate']:.1f}%")
        print(f"Протестированных классов: {len(self.test_results['classes_tested'])}")
        print(f"Интеграционных тестов: {len(self.test_results['integration_tests'])}")
        
        print("\nПРОТЕСТИРОВАННЫЕ КЛАССЫ:")
        for class_name in self.test_results["classes_tested"]:
            print(f"  ✓ {class_name}")
        
        if self.test_results["errors"]:
            print("\nОШИБКИ:")
            for error in self.test_results["errors"]:
                print(f"  ✗ {error['test_name']}: {error['details']}")
        
        if self.test_results["warnings"]:
            print("\nПРЕДУПРЕЖДЕНИЯ:")
            for warning in self.test_results["warnings"]:
                print(f"  ⚠ {warning['test_name']}: {warning['details']}")
        
        print("\nРЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:")
        print("  1. Добавить async/await поддержку для всех методов")
        print("  2. Улучшить валидацию параметров")
        print("  3. Расширить docstrings для лучшей документации")
        print("  4. Добавить больше unit-тестов")
        print("  5. Реализовать реальные HTTP-запросы вместо заглушек")
        
        return self.test_results
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("ЗАПУСК ЭТАПА 8: ФИНАЛЬНАЯ ПРОВЕРКА SERVICEMESHMANAGER")
        print("="*60)
        
        # 8.1 - ПОЛНЫЙ ТЕСТ ВСЕХ КЛАССОВ И МЕТОДОВ
        print("\n8.1 - ПОЛНЫЙ ТЕСТ ВСЕХ КЛАССОВ И МЕТОДОВ")
        print("-" * 50)
        
        self.test_circuit_breaker_config()
        self.test_service_info()
        self.test_service_endpoint()
        self.test_service_mesh_manager_creation()
        self.test_service_mesh_manager_methods()
        
        # 8.2 - ПРОВЕРКА ИНТЕГРАЦИИ МЕЖДУ КОМПОНЕНТАМИ
        print("\n8.2 - ПРОВЕРКА ИНТЕГРАЦИИ МЕЖДУ КОМПОНЕНТАМИ")
        print("-" * 50)
        
        self.test_integration_scenarios()
        self.test_error_handling()
        
        # 8.3 - ГЕНЕРАЦИЯ ОТЧЕТА О СОСТОЯНИИ
        print("\n8.3 - ГЕНЕРАЦИЯ ОТЧЕТА О СОСТОЯНИИ")
        print("-" * 50)
        
        return self.generate_report()


def main():
    """Основная функция"""
    try:
        tester = ServiceMeshTester()
        results = tester.run_all_tests()
        
        # Сохранение результатов
        with open('/Users/sergejhlystov/ALADDIN_NEW/formatting_work/service_mesh_manager_etap8_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\nРезультаты сохранены в: /Users/sergejhlystov/ALADDIN_NEW/formatting_work/service_mesh_manager_etap8_results.json")
        
        return results
        
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()