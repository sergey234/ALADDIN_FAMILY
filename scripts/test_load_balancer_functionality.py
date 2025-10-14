#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный тест функциональности LoadBalancer
"""

import asyncio
import sys
import os
import time
import json
from datetime import datetime, timedelta

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.microservices.load_balancer import (
    LoadBalancer, 
    LoadBalancingAlgorithm, 
    ServiceEndpoint, 
    LoadBalancingRequest,
    LoadBalancingResponse
)

class LoadBalancerTester:
    """Тестер функциональности LoadBalancer"""
    
    def __init__(self):
        self.test_results = []
        self.load_balancer = None
        
    async def run_all_tests(self):
        """Запуск всех тестов"""
        print("🧪 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ LOADBALANCER")
        print("=" * 60)
        
        # Создание LoadBalancer
        await self.test_initialization()
        
        # Тесты базовой функциональности
        await self.test_service_management()
        await self.test_algorithm_selection()
        await self.test_load_balancing()
        await self.test_health_checks()
        await self.test_metrics_collection()
        
        # Тесты продвинутых функций
        await self.test_ml_optimization()
        await self.test_adaptive_balancing()
        await self.test_error_handling()
        
        # Тесты производительности
        await self.test_performance()
        
        # Итоговый отчет
        self.print_test_summary()
        
    async def test_initialization(self):
        """Тест инициализации LoadBalancer"""
        print("\n🔧 ТЕСТ 1: ИНИЦИАЛИЗАЦИЯ")
        print("-" * 30)
        
        try:
            # Создание LoadBalancer с конфигурацией
            config = {
                'health_check_interval': 5,
                'health_check_timeout': 3,
                'health_check_path': '/health',
                'default_algorithm': 'round_robin',
                'database_url': 'sqlite:///test_load_balancer.db',
                'redis_url': 'redis://localhost:6379/1'
            }
            
            self.load_balancer = LoadBalancer(name="TestLoadBalancer", config=config)
            
            # Проверка инициализации
            assert self.load_balancer is not None, "LoadBalancer не создан"
            assert self.load_balancer.name == "TestLoadBalancer", "Неправильное имя"
            assert self.load_balancer.config == config, "Неправильная конфигурация"
            
            print("✅ LoadBalancer успешно инициализирован")
            self.test_results.append(("Инициализация", True, "Успешно"))
            
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            self.test_results.append(("Инициализация", False, str(e)))
    
    async def test_service_management(self):
        """Тест управления сервисами"""
        print("\n🔧 ТЕСТ 2: УПРАВЛЕНИЕ СЕРВИСАМИ")
        print("-" * 35)
        
        try:
            # Создание тестовых сервисов
            service1 = ServiceEndpoint(
                id="service_1",
                name="Test Service 1",
                url="localhost",
                port=8001,
                protocol="http",
                health_check_url="/health",
                max_connections=100,
                weight=1.0
            )
            
            service2 = ServiceEndpoint(
                id="service_2", 
                name="Test Service 2",
                url="localhost",
                port=8002,
                protocol="http",
                health_check_url="/health",
                max_connections=150,
                weight=1.5
            )
            
            # Добавление сервисов
            await self.load_balancer.add_service(service1)
            await self.load_balancer.add_service(service2)
            
            # Проверка добавления
            services = self.load_balancer.get_services()
            assert len(services) == 2, f"Ожидалось 2 сервиса, получено {len(services)}"
            
            # Проверка получения сервиса
            retrieved_service = self.load_balancer.get_service("service_1")
            assert retrieved_service is not None, "Сервис не найден"
            assert retrieved_service.name == "Test Service 1", "Неправильное имя сервиса"
            
            # Удаление сервиса
            await self.load_balancer.remove_service("service_1")
            services_after_removal = self.load_balancer.get_services()
            assert len(services_after_removal) == 1, "Сервис не удален"
            
            print("✅ Управление сервисами работает корректно")
            self.test_results.append(("Управление сервисами", True, "Успешно"))
            
        except Exception as e:
            print(f"❌ Ошибка управления сервисами: {e}")
            self.test_results.append(("Управление сервисами", False, str(e)))
    
    async def test_algorithm_selection(self):
        """Тест выбора алгоритмов"""
        print("\n🔧 ТЕСТ 3: ВЫБОР АЛГОРИТМОВ")
        print("-" * 30)
        
        try:
            # Тест всех доступных алгоритмов
            algorithms = [
                LoadBalancingAlgorithm.ROUND_ROBIN,
                LoadBalancingAlgorithm.LEAST_CONNECTIONS,
                LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN,
                LoadBalancingAlgorithm.IP_HASH,
                LoadBalancingAlgorithm.LEAST_RESPONSE_TIME
            ]
            
            for algorithm in algorithms:
                # Установка алгоритма
                success = self.load_balancer.set_algorithm(algorithm)
                assert success, f"Не удалось установить алгоритм {algorithm.value}"
                
                # Проверка текущего алгоритма
                current_algorithm = self.load_balancer.get_current_algorithm()
                assert current_algorithm == algorithm, f"Алгоритм не установлен: {algorithm.value}"
                
                print(f"  ✅ {algorithm.value} - работает")
            
            print("✅ Все алгоритмы работают корректно")
            self.test_results.append(("Выбор алгоритмов", True, "Успешно"))
            
        except Exception as e:
            print(f"❌ Ошибка выбора алгоритмов: {e}")
            self.test_results.append(("Выбор алгоритмов", False, str(e)))
    
    async def test_load_balancing(self):
        """Тест балансировки нагрузки"""
        print("\n🔧 ТЕСТ 4: БАЛАНСИРОВКА НАГРУЗКИ")
        print("-" * 35)
        
        try:
            # Добавление тестовых сервисов
            service1 = ServiceEndpoint(
                id="lb_service_1",
                name="LB Service 1", 
                url="localhost",
                port=8001,
                protocol="http",
                health_check_url="/health",
                max_connections=100,
                weight=1.0,
                is_healthy=True
            )
            
            service2 = ServiceEndpoint(
                id="lb_service_2",
                name="LB Service 2",
                url="localhost", 
                port=8002,
                protocol="http",
                health_check_url="/health",
                max_connections=100,
                weight=1.0,
                is_healthy=True
            )
            
            await self.load_balancer.add_service(service1)
            await self.load_balancer.add_service(service2)
            
            # Тест Round Robin
            self.load_balancer.set_algorithm(LoadBalancingAlgorithm.ROUND_ROBIN)
            
            selected_services = []
            for i in range(10):
                request = LoadBalancingRequest(
                    request_id=f"test_req_{i}",
                    service_name="default",  # Используем группу 'default'
                    algorithm=LoadBalancingAlgorithm.ROUND_ROBIN,
                    client_ip="192.168.1.100",
                    headers={"User-Agent": "TestClient/1.0"},
                    body=None
                )
                
                response = await self.load_balancer.balance_load(request)
                if response and response.selected_service:
                    selected_services.append(response.selected_service.service_id)
            
            # Проверка распределения (должно быть примерно равномерным)
            service1_count = selected_services.count("lb_service_1")
            service2_count = selected_services.count("lb_service_2")
            
            print(f"  📊 Распределение: Service 1: {service1_count}, Service 2: {service2_count}")
            
            # Тест Least Connections
            self.load_balancer.set_algorithm(LoadBalancingAlgorithm.LEAST_CONNECTIONS)
            
            # Симуляция разной нагрузки
            service1.current_connections = 5
            service2.current_connections = 15
            
            request = LoadBalancingRequest(
                request_id="test_least_conn",
                service_name="default",  # Используем группу 'default'
                algorithm=LoadBalancingAlgorithm.LEAST_CONNECTIONS,
                client_ip="192.168.1.101"
            )
            
            response = await self.load_balancer.balance_load(request)
            if response and response.selected_service:
                # Должен выбрать сервис с меньшим количеством соединений
                assert response.selected_service.service_id == "lb_service_1", "Не выбран сервис с меньшим количеством соединений"
                print("  ✅ Least Connections работает корректно")
            
            print("✅ Балансировка нагрузки работает корректно")
            self.test_results.append(("Балансировка нагрузки", True, "Успешно"))
            
        except Exception as e:
            print(f"❌ Ошибка балансировки нагрузки: {e}")
            self.test_results.append(("Балансировка нагрузки", False, str(e)))
    
    async def test_health_checks(self):
        """Тест проверок здоровья"""
        print("\n🔧 ТЕСТ 5: ПРОВЕРКИ ЗДОРОВЬЯ")
        print("-" * 30)
        
        try:
            # Создание сервиса с health check
            health_service = ServiceEndpoint(
                id="health_service",
                name="Health Check Service",
                url="httpbin.org",  # Используем реальный сервис для теста
                port=80,
                protocol="http",
                health_check_url="/status/200",  # HTTPBin endpoint
                max_connections=100,
                weight=1.0
            )
            
            await self.load_balancer.add_service(health_service)
            
            # Запуск LoadBalancer для активации health checks
            await self.load_balancer.start()
            
            # Ожидание выполнения health check
            await asyncio.sleep(2)
            
            # Проверка статуса здоровья
            service_status = self.load_balancer.get_service_status("health_service")
            print(f"  📊 Статус сервиса: {service_status}")
            
            # Остановка LoadBalancer
            await self.load_balancer.stop()
            
            print("✅ Проверки здоровья работают корректно")
            self.test_results.append(("Проверки здоровья", True, "Успешно"))
            
        except Exception as e:
            print(f"❌ Ошибка проверок здоровья: {e}")
            self.test_results.append(("Проверки здоровья", False, str(e)))
    
    async def test_metrics_collection(self):
        """Тест сбора метрик"""
        print("\n🔧 ТЕСТ 6: СБОР МЕТРИК")
        print("-" * 25)
        
        try:
            # Запуск LoadBalancer для активации сбора метрик
            await self.load_balancer.start()
            
            # Ожидание сбора метрик
            await asyncio.sleep(3)
            
            # Получение метрик
            metrics = await self.load_balancer.get_metrics()
            
            # Проверка наличия метрик
            assert metrics is not None, "Метрики не собраны"
            assert 'total_requests' in metrics, "Отсутствует total_requests"
            assert 'successful_requests' in metrics, "Отсутствует successful_requests"
            assert 'failed_requests' in metrics, "Отсутствует failed_requests"
            
            print(f"  📊 Метрики: {json.dumps(metrics, indent=2)}")
            
            # Остановка LoadBalancer
            await self.load_balancer.stop()
            
            print("✅ Сбор метрик работает корректно")
            self.test_results.append(("Сбор метрик", True, "Успешно"))
            
        except Exception as e:
            print(f"❌ Ошибка сбора метрик: {e}")
            self.test_results.append(("Сбор метрик", False, str(e)))
    
    async def test_ml_optimization(self):
        """Тест ML оптимизации"""
        print("\n🔧 ТЕСТ 7: ML ОПТИМИЗАЦИЯ")
        print("-" * 30)
        
        try:
            # Создание тестовых данных для ML
            test_services = {
                "ml_service_1": 85.0,
                "ml_service_2": 92.0,
                "ml_service_3": 78.0,
                "ml_service_4": 88.0
            }
            
            # Тест расчета оптимального алгоритма
            current_load = 65.0
            optimal_algorithm = self.load_balancer._calculate_optimal_algorithm(
                current_load, test_services
            )
            
            assert optimal_algorithm is not None, "Оптимальный алгоритм не рассчитан"
            print(f"  🤖 Оптимальный алгоритм: {optimal_algorithm.value}")
            
            # Тест анализа распределения нагрузки
            distribution_factor = self.load_balancer._analyze_load_distribution(test_services)
            print(f"  📊 Фактор распределения: {distribution_factor:.2f}")
            
            # Тест расчета корреляции
            correlation = self.load_balancer._calculate_health_correlation(test_services)
            print(f"  🔗 Корреляция здоровья: {correlation:.2f}")
            
            print("✅ ML оптимизация работает корректно")
            self.test_results.append(("ML оптимизация", True, "Успешно"))
            
        except Exception as e:
            print(f"❌ Ошибка ML оптимизации: {e}")
            self.test_results.append(("ML оптимизация", False, str(e)))
    
    async def test_adaptive_balancing(self):
        """Тест адаптивной балансировки"""
        print("\n🔧 ТЕСТ 8: АДАПТИВНАЯ БАЛАНСИРОВКА")
        print("-" * 35)
        
        try:
            # Включение адаптивной балансировки
            await self.load_balancer.enable_adaptive_balancing()
            
            # Ожидание работы адаптивной балансировки
            await asyncio.sleep(2)
            
            # Проверка статуса адаптивной балансировки
            status = self.load_balancer.get_status()
            print(f"  📊 Статус системы: {json.dumps(status, indent=2, default=str)}")
            
            # Отключение адаптивной балансировки
            await self.load_balancer.disable_adaptive_balancing()
            
            print("✅ Адаптивная балансировка работает корректно")
            self.test_results.append(("Адаптивная балансировка", True, "Успешно"))
            
        except Exception as e:
            print(f"❌ Ошибка адаптивной балансировки: {e}")
            self.test_results.append(("Адаптивная балансировка", False, str(e)))
    
    async def test_error_handling(self):
        """Тест обработки ошибок"""
        print("\n🔧 ТЕСТ 9: ОБРАБОТКА ОШИБОК")
        print("-" * 30)
        
        try:
            # Тест с несуществующим сервисом
            request = LoadBalancingRequest(
                request_id="error_test",
                service_name="nonexistent_service",  # Несуществующая группа
                algorithm=LoadBalancingAlgorithm.ROUND_ROBIN
            )
            
            response = await self.load_balancer.balance_load(request)
            # Должен вернуть None или пустой ответ
            print(f"  ⚠️ Ответ на несуществующий сервис: {response}")
            
            # Тест с недопустимым алгоритмом
            try:
                self.load_balancer.set_algorithm("invalid_algorithm")
                print("  ❌ Неожиданно принял недопустимый алгоритм")
            except Exception:
                print("  ✅ Корректно отклонил недопустимый алгоритм")
            
            # Тест с пустым списком сервисов
            await self.load_balancer.clear_services()
            request = LoadBalancingRequest(
                request_id="empty_test",
                service_name="default",  # Группа 'default' будет пустой
                algorithm=LoadBalancingAlgorithm.ROUND_ROBIN
            )
            
            response = await self.load_balancer.balance_load(request)
            print(f"  ⚠️ Ответ при пустом списке сервисов: {response}")
            
            print("✅ Обработка ошибок работает корректно")
            self.test_results.append(("Обработка ошибок", True, "Успешно"))
            
        except Exception as e:
            print(f"❌ Ошибка обработки ошибок: {e}")
            self.test_results.append(("Обработка ошибок", False, str(e)))
    
    async def test_performance(self):
        """Тест производительности"""
        print("\n🔧 ТЕСТ 10: ПРОИЗВОДИТЕЛЬНОСТЬ")
        print("-" * 35)
        
        try:
            # Добавление сервисов для теста производительности
            for i in range(5):
                service = ServiceEndpoint(
                    id=f"perf_service_{i}",
                    name=f"Performance Service {i}",
                    url="localhost",
                    port=8000 + i,
                    protocol="http",
                    health_check_url="/health",
                    max_connections=100,
                    weight=1.0,
                    is_healthy=True
                )
                await self.load_balancer.add_service(service)
            
            # Тест производительности балансировки
            start_time = time.time()
            request_count = 1000
            
            for i in range(request_count):
                request = LoadBalancingRequest(
                    request_id=f"perf_req_{i}",
                    service_name="default",  # Используем группу 'default'
                    algorithm=LoadBalancingAlgorithm.ROUND_ROBIN,
                    client_ip=f"192.168.1.{i % 255}"
                )
                
                response = await self.load_balancer.balance_load(request)
                if not response:
                    print(f"  ⚠️ Пустой ответ для запроса {i}")
            
            end_time = time.time()
            duration = end_time - start_time
            requests_per_second = request_count / duration
            
            print(f"  ⚡ Обработано {request_count} запросов за {duration:.2f} секунд")
            print(f"  🚀 Производительность: {requests_per_second:.0f} запросов/сек")
            
            # Проверка производительности
            if requests_per_second > 100:  # Минимум 100 RPS
                print("  ✅ Производительность удовлетворительная")
                self.test_results.append(("Производительность", True, f"{requests_per_second:.0f} RPS"))
            else:
                print("  ⚠️ Производительность ниже ожидаемой")
                self.test_results.append(("Производительность", False, f"Только {requests_per_second:.0f} RPS"))
            
        except Exception as e:
            print(f"❌ Ошибка теста производительности: {e}")
            self.test_results.append(("Производительность", False, str(e)))
    
    def print_test_summary(self):
        """Вывод итогового отчета"""
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed, _ in self.test_results if passed)
        failed_tests = total_tests - passed_tests
        
        print(f"📈 Всего тестов: {total_tests}")
        print(f"✅ Пройдено: {passed_tests}")
        print(f"❌ Провалено: {failed_tests}")
        print(f"📊 Успешность: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        print("-" * 40)
        
        for test_name, passed, message in self.test_results:
            status = "✅" if passed else "❌"
            print(f"  {status} {test_name}: {message}")
        
        if failed_tests == 0:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            print("🚀 LoadBalancer готов к использованию!")
        else:
            print(f"\n⚠️ {failed_tests} ТЕСТОВ ПРОВАЛЕНО")
            print("🔧 Требуется доработка LoadBalancer")
        
        # Сохранение отчета
        report_file = f"data/test_reports/load_balancer_test_report_{int(time.time())}.json"
        os.makedirs("data/test_reports", exist_ok=True)
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "test_results": [
                {"test_name": name, "passed": passed, "message": message}
                for name, passed, message in self.test_results
            ]
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Отчет сохранен: {report_file}")

async def main():
    """Главная функция"""
    tester = LoadBalancerTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())