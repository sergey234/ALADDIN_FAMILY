#!/usr/bin/env python3
"""
Комплексный интеграционный тест для Service Mesh Manager
Проверяет все новые функции: rate limiting, мониторинг, алертинг, производительность
"""

import sys
import os
import time
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.microservices.service_mesh_manager import (
    ServiceMeshManager,
    RateLimitConfig,
    MonitoringConfig,
    PerformanceConfig,
    AlertRule,
    ServiceInfo,
    ServiceType,
    ServiceStatus,
    LoadBalancingStrategy
)


class ComprehensiveServiceMeshTest:
    """Комплексный тест Service Mesh Manager"""
    
    def __init__(self):
        self.manager = None
        self.test_results = []
        self.errors = []
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Логирование результата теста"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}"
        if message:
            result += f" - {message}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now()
        })
        if not success:
            self.errors.append(f"{test_name}: {message}")
    
    def test_initialization(self) -> bool:
        """Тест инициализации"""
        try:
            self.manager = ServiceMeshManager(
                name="TestServiceMeshManager",
                config={
                    "discovery_interval": 10,
                    "health_check_interval": 15,
                    "enable_service_discovery": True,
                    "enable_health_checks": True,
                    "enable_load_balancing": True,
                    "enable_circuit_breaker": True,
                    "enable_metrics": True
                }
            )
            
            # Проверяем инициализацию
            assert self.manager is not None
            assert self.manager.name == "TestServiceMeshManager"
            assert hasattr(self.manager, 'rate_limiter')
            assert hasattr(self.manager, 'metrics_collector')
            assert hasattr(self.manager, 'alert_manager')
            assert hasattr(self.manager, 'notification_service')
            assert hasattr(self.manager, 'memory_optimizer')
            assert hasattr(self.manager, 'performance_monitor')
            assert hasattr(self.manager, 'request_batcher')
            
            self.log_test("Инициализация", True, "Все компоненты инициализированы")
            return True
            
        except Exception as e:
            self.log_test("Инициализация", False, str(e))
            return False
    
    def test_basic_functionality(self) -> bool:
        """Тест базовой функциональности"""
        try:
            # Инициализация
            success = self.manager.initialize()
            assert success, "Инициализация не удалась"
            
            # Регистрация тестового сервиса
            service_info = ServiceInfo(
                service_id="test_service",
                name="Test Service",
                description="Тестовый сервис",
                service_type=ServiceType.SECURITY,
                version="1.0.0",
                endpoints=[],
                dependencies=[]
            )
            
            self.manager.register_service(service_info)
            assert "test_service" in self.manager.services
            
            # Проверка статуса
            assert self.manager.status.value == "running"
            
            self.log_test("Базовая функциональность", True, "Сервис зарегистрирован")
            return True
            
        except Exception as e:
            self.log_test("Базовая функциональность", False, str(e))
            return False
    
    def test_rate_limiting(self) -> bool:
        """Тест rate limiting"""
        try:
            # Включаем rate limiting
            self.manager.enable_rate_limiting()
            assert self.manager.rate_limiting_enabled
            
            # Устанавливаем лимиты для тестового сервиса
            self.manager.set_service_rate_limit("test_service", {
                "per_minute": 5,
                "per_hour": 50,
                "per_day": 500
            })
            
            # Тестируем rate limiting
            allowed_requests = 0
            blocked_requests = 0
            
            for i in range(10):  # Пытаемся сделать 10 запросов
                if self.manager.check_rate_limit("service", "test_service"):
                    allowed_requests += 1
                else:
                    blocked_requests += 1
                time.sleep(0.1)  # Небольшая пауза
            
            # Должно быть разрешено 5 запросов, заблокировано 5
            assert allowed_requests <= 5, f"Слишком много разрешенных запросов: {allowed_requests}"
            assert blocked_requests >= 5, f"Слишком мало заблокированных запросов: {blocked_requests}"
            
            # Проверяем статистику
            stats = self.manager.get_rate_limit_stats("service", "test_service")
            assert "total_requests" in stats
            
            self.log_test("Rate Limiting", True, f"Разрешено: {allowed_requests}, Заблокировано: {blocked_requests}")
            return True
            
        except Exception as e:
            self.log_test("Rate Limiting", False, str(e))
            return False
    
    def test_monitoring_and_alerting(self) -> bool:
        """Тест мониторинга и алертинга"""
        try:
            # Включаем мониторинг
            self.manager.enable_monitoring()
            assert self.manager.monitoring_enabled
            
            # Добавляем тестовое правило алертинга
            test_rule = AlertRule(
                name="test_high_cpu",
                condition="cpu_usage > 0",  # Всегда срабатывает для теста
                severity="warning",
                message="Test CPU alert: {cpu_usage}%",
                cooldown=1  # Короткий cooldown для теста
            )
            self.manager.add_alert_rule(test_rule)
            
            # Получаем состояние системы
            system_health = self.manager.get_system_health()
            assert system_health is not None
            assert hasattr(system_health, 'cpu_usage')
            assert hasattr(system_health, 'memory_usage')
            
            # Ждем немного для срабатывания мониторинга
            time.sleep(2)
            
            # Проверяем алерты
            active_alerts = self.manager.get_active_alerts()
            # Может быть 0 или больше в зависимости от состояния системы
            
            # Отправляем тестовый алерт
            test_alert_sent = self.manager.send_test_alert("info", "Test alert message")
            assert test_alert_sent
            
            # Получаем сводку мониторинга
            monitoring_summary = self.manager.get_monitoring_summary()
            assert "enabled" in monitoring_summary
            assert "system_health" in monitoring_summary
            assert "alerts" in monitoring_summary
            
            self.log_test("Мониторинг и алертинг", True, f"Активных алертов: {len(active_alerts)}")
            return True
            
        except Exception as e:
            self.log_test("Мониторинг и алертинг", False, str(e))
            return False
    
    def test_performance_optimization(self) -> bool:
        """Тест оптимизации производительности"""
        try:
            # Включаем оптимизацию производительности
            self.manager.enable_performance_optimization()
            
            # Получаем статистику производительности
            perf_stats = self.manager.get_performance_stats()
            assert "memory_stats" in perf_stats
            assert "performance_stats" in perf_stats
            assert "config" in perf_stats
            
            # Получаем статистику памяти
            memory_stats = self.manager.get_memory_stats()
            assert "total_memory" in memory_stats
            assert "available_memory" in memory_stats
            
            # Тестируем оптимизацию памяти
            self.manager.memory_optimizer.optimize_memory()
            
            # Получаем статистику пула соединений
            pool_stats = self.manager.get_connection_pool_stats()
            assert "total_connections" in pool_stats
            assert "active_connections" in pool_stats
            
            self.log_test("Оптимизация производительности", True, "Все метрики получены")
            return True
            
        except Exception as e:
            self.log_test("Оптимизация производительности", False, str(e))
            return False
    
    def test_caching(self) -> bool:
        """Тест кэширования"""
        try:
            # Включаем кэширование
            self.manager.cache_enable()
            
            # Тестируем кэширование
            test_key = "test_cache_key"
            test_value = {"data": "test_value", "timestamp": datetime.now().isoformat()}
            
            # Устанавливаем значение в кэш
            self.manager.cache_set(test_key, test_value, ttl_seconds=60)
            
            # Получаем значение из кэша
            cached_value = self.manager.cache_get(test_key)
            assert cached_value is not None
            assert cached_value["data"] == test_value["data"]
            
            # Получаем статистику кэша
            cache_stats = self.manager.cache_get_statistics()
            assert "hits" in cache_stats
            assert "misses" in cache_stats
            assert "size" in cache_stats
            
            # Тестируем cache_get_or_set
            def expensive_operation():
                return {"computed": "value", "timestamp": datetime.now().isoformat()}
            
            result = self.manager.cache_get_or_set("computed_key", expensive_operation, ttl_seconds=30)
            assert result is not None
            assert "computed" in result
            
            self.log_test("Кэширование", True, f"Размер кэша: {cache_stats['size']}")
            return True
            
        except Exception as e:
            self.log_test("Кэширование", False, str(e))
            return False
    
    def test_async_functionality(self) -> bool:
        """Тест асинхронной функциональности"""
        try:
            # Включаем асинхронную поддержку
            self.manager.enable_async()
            
            # Запускаем асинхронный цикл
            self.manager.start_async_loop()
            
            # Ждем немного для инициализации
            time.sleep(1)
            
            # Получаем статистику асинхронных операций
            async_stats = self.manager.get_async_statistics()
            assert "enabled" in async_stats
            assert "loop_running" in async_stats
            
            # Останавливаем асинхронный цикл
            self.manager.stop_async_loop()
            
            self.log_test("Асинхронная функциональность", True, "Цикл запущен и остановлен")
            return True
            
        except Exception as e:
            self.log_test("Асинхронная функциональность", False, str(e))
            return False
    
    def test_logging_and_metrics(self) -> bool:
        """Тест логирования и метрик"""
        try:
            # Включаем логирование
            self.manager.enable_logging()
            
            # Получаем статистику логирования
            logging_stats = self.manager.get_logging_statistics()
            assert "enabled" in logging_stats
            assert "total_logs" in logging_stats
            
            # Включаем Prometheus метрики
            self.manager.enable_prometheus_metrics()
            
            # Получаем метрики Prometheus
            prometheus_text = self.manager.get_prometheus_metrics_text()
            assert isinstance(prometheus_text, str)
            assert len(prometheus_text) > 0
            
            # Получаем метрики в виде словаря
            prometheus_dict = self.manager.get_prometheus_metrics_dict()
            assert isinstance(prometheus_dict, dict)
            
            self.log_test("Логирование и метрики", True, f"Логов: {logging_stats['total_logs']}")
            return True
            
        except Exception as e:
            self.log_test("Логирование и метрики", False, str(e))
            return False
    
    def test_error_handling(self) -> bool:
        """Тест обработки ошибок"""
        try:
            # Тестируем обработку несуществующего сервиса
            endpoint = self.manager.get_service_endpoint("nonexistent_service")
            # Должно вернуть None для несуществующего сервиса
            if endpoint is not None:
                self.log_test("Обработка ошибок", False, "Не возвращен None для несуществующего сервиса")
                return False
            
            # Тестируем обработку неверных параметров
            try:
                self.manager.check_rate_limit("invalid_type", "test")
                # Должно работать без ошибок
            except Exception as e:
                self.log_test("Обработка ошибок", False, f"Ошибка при проверке rate limit: {e}")
                return False
            
            self.log_test("Обработка ошибок", True, "Ошибки обрабатываются корректно")
            return True
            
        except Exception as e:
            self.log_test("Обработка ошибок", False, str(e))
            return False
    
    def test_cleanup(self) -> bool:
        """Тест очистки ресурсов"""
        try:
            # Останавливаем все компоненты
            self.manager.disable_monitoring()
            self.manager.disable_rate_limiting()
            self.manager.disable_async()
            self.manager.disable_performance_optimization()
            
            # Очищаем ресурсы
            self.manager.cleanup_resources()
            
            # Останавливаем менеджер
            self.manager.stop()
            
            self.log_test("Очистка ресурсов", True, "Все ресурсы очищены")
            return True
            
        except Exception as e:
            self.log_test("Очистка ресурсов", False, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        print("🚀 Запуск комплексного тестирования Service Mesh Manager")
        print("=" * 60)
        
        start_time = time.time()
        
        # Список тестов
        tests = [
            ("Инициализация", self.test_initialization),
            ("Базовая функциональность", self.test_basic_functionality),
            ("Rate Limiting", self.test_rate_limiting),
            ("Мониторинг и алертинг", self.test_monitoring_and_alerting),
            ("Оптимизация производительности", self.test_performance_optimization),
            ("Кэширование", self.test_caching),
            ("Асинхронная функциональность", self.test_async_functionality),
            ("Логирование и метрики", self.test_logging_and_metrics),
            ("Обработка ошибок", self.test_error_handling),
            ("Очистка ресурсов", self.test_cleanup)
        ]
        
        # Запускаем тесты
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Неожиданная ошибка: {e}")
                failed += 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Результаты
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("=" * 60)
        print(f"✅ Пройдено: {passed}")
        print(f"❌ Провалено: {failed}")
        print(f"⏱️  Время выполнения: {duration:.2f} секунд")
        print(f"📈 Успешность: {(passed / (passed + failed)) * 100:.1f}%")
        
        if self.errors:
            print("\n❌ ОШИБКИ:")
            for error in self.errors:
                print(f"  - {error}")
        
        return {
            "total_tests": passed + failed,
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / (passed + failed)) * 100,
            "duration": duration,
            "errors": self.errors,
            "results": self.test_results
        }


def main():
    """Главная функция"""
    print("🔧 Комплексное тестирование Service Mesh Manager")
    print("Версия: 1.0.0")
    print("Дата:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Создаем и запускаем тесты
    tester = ComprehensiveServiceMeshTest()
    results = tester.run_all_tests()
    
    # Возвращаем код выхода
    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)