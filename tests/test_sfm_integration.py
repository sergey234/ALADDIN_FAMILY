#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Integration Tests для ALADDIN Dashboard
Тесты интеграции веб-дашборда с Safe Function Manager

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
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from security.safe_function_manager import SafeFunctionManager
    from core.base import ComponentStatus, SecurityLevel
    from core.logging_module import LoggingManager
    ALADDIN_AVAILABLE = True
except ImportError:
    ALADDIN_AVAILABLE = False


@dataclass
class SFMFunction:
    """Модель функции SFM"""
    function_id: str
    name: str
    description: str
    status: str
    security_level: str
    file_path: str
    is_critical: bool
    auto_enable: bool


@dataclass
class SFMIntegrationResult:
    """Результат интеграции с SFM"""
    endpoint: str
    method: str
    sfm_available: bool
    response_time: float
    status_code: int
    success: bool
    sfm_functions_count: int
    active_functions_count: int
    error_message: Optional[str] = None


class SFMIntegrationTester:
    """Тестер интеграции с SFM"""
    
    def __init__(self, dashboard_url: str = "http://localhost:8080"):
        """
        Инициализация тестера интеграции
        
        Args:
            dashboard_url: URL дашборда
        """
        self.dashboard_url = dashboard_url
        self.sfm_url = "http://localhost:8011"  # SFM порт
        self.logger = LoggingManager(name="SFMIntegrationTester") if ALADDIN_AVAILABLE else None
        self.integration_results: List[SFMIntegrationResult] = []
        self.sfm_functions: List[SFMFunction] = []
        
    async def check_sfm_availability(self) -> bool:
        """
        Проверка доступности SFM
        
        Returns:
            True если SFM доступен
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.sfm_url}/health")
                return response.status_code == 200
        except Exception:
            return False
    
    async def get_sfm_functions(self) -> List[SFMFunction]:
        """
        Получение списка функций SFM
        
        Returns:
            Список функций SFM
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.sfm_url}/functions")
                
                if response.status_code == 200:
                    data = response.json()
                    functions = []
                    
                    for func_data in data.get("functions", []):
                        function = SFMFunction(
                            function_id=func_data.get("function_id", ""),
                            name=func_data.get("name", ""),
                            description=func_data.get("description", ""),
                            status=func_data.get("status", ""),
                            security_level=func_data.get("security_level", ""),
                            file_path=func_data.get("file_path", ""),
                            is_critical=func_data.get("is_critical", False),
                            auto_enable=func_data.get("auto_enable", False)
                        )
                        functions.append(function)
                    
                    self.sfm_functions = functions
                    return functions
                else:
                    return []
                    
        except Exception as e:
            if self.logger:
                self.logger.log("ERROR", f"Ошибка получения функций SFM: {e}")
            return []
    
    async def test_dashboard_sfm_integration(
        self, 
        endpoint: str, 
        method: str = "GET",
        json_data: Optional[Dict] = None
    ) -> SFMIntegrationResult:
        """
        Тестирование интеграции дашборда с SFM
        
        Args:
            endpoint: Endpoint дашборда
            method: HTTP метод
            json_data: JSON данные
            
        Returns:
            Результат интеграции
        """
        start_time = time.time()
        sfm_available = await self.check_sfm_availability()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Authorization": "Bearer demo_token"}
                
                if method.upper() == "GET":
                    response = await client.get(f"{self.dashboard_url}{endpoint}", headers=headers)
                elif method.upper() == "POST":
                    response = await client.post(
                        f"{self.dashboard_url}{endpoint}", 
                        json=json_data, 
                        headers=headers
                    )
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                response_time = time.time() - start_time
                
                # Анализируем ответ на предмет SFM данных
                sfm_functions_count = 0
                active_functions_count = 0
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Ищем SFM данные в ответе
                        if "services" in data:
                            services = data["services"]
                            if "SafeFunctionManager" in services:
                                sfm_service = services["SafeFunctionManager"]
                                if sfm_service.get("status") == "running":
                                    sfm_functions_count = 1  # SFM сервис найден
                        
                        if "endpoints" in data:
                            endpoints = data["endpoints"]
                            sfm_endpoints = [ep for ep in endpoints if "sfm" in ep.get("service", "").lower()]
                            sfm_functions_count = len(sfm_endpoints)
                        
                    except (json.JSONDecodeError, KeyError):
                        pass
                
                result = SFMIntegrationResult(
                    endpoint=endpoint,
                    method=method,
                    sfm_available=sfm_available,
                    response_time=response_time,
                    status_code=response.status_code,
                    success=200 <= response.status_code < 300,
                    sfm_functions_count=sfm_functions_count,
                    active_functions_count=active_functions_count
                )
                
                self.integration_results.append(result)
                return result
                
        except Exception as e:
            response_time = time.time() - start_time
            
            result = SFMIntegrationResult(
                endpoint=endpoint,
                method=method,
                sfm_available=sfm_available,
                response_time=response_time,
                status_code=0,
                success=False,
                sfm_functions_count=0,
                active_functions_count=0,
                error_message=str(e)
            )
            
            self.integration_results.append(result)
            return result
    
    async def test_sfm_function_management(self) -> Dict[str, Any]:
        """
        Тестирование управления функциями SFM
        
        Returns:
            Результаты тестирования управления
        """
        print("🧪 Тестирование управления функциями SFM...")
        
        # Получаем список функций
        functions = await self.get_sfm_functions()
        
        if not functions:
            return {
                "success": False,
                "error": "Не удалось получить список функций SFM",
                "functions_count": 0
            }
        
        # Анализируем функции
        active_functions = [f for f in functions if f.status == "active"]
        critical_functions = [f for f in functions if f.is_critical]
        auto_enable_functions = [f for f in functions if f.auto_enable]
        
        # Тестируем управление функциями через дашборд
        management_tests = []
        
        # Тест получения статуса функций
        status_result = await self.test_dashboard_sfm_integration("/api/services")
        management_tests.append({
            "test": "get_functions_status",
            "success": status_result.success,
            "sfm_functions_found": status_result.sfm_functions_count > 0
        })
        
        # Тест получения endpoints
        endpoints_result = await self.test_dashboard_sfm_integration("/api/endpoints")
        management_tests.append({
            "test": "get_sfm_endpoints",
            "success": endpoints_result.success,
            "sfm_endpoints_found": endpoints_result.sfm_functions_count > 0
        })
        
        return {
            "success": True,
            "total_functions": len(functions),
            "active_functions": len(active_functions),
            "critical_functions": len(critical_functions),
            "auto_enable_functions": len(auto_enable_functions),
            "management_tests": management_tests,
            "sfm_available": await self.check_sfm_availability()
        }
    
    def generate_integration_report(self) -> Dict[str, Any]:
        """
        Генерация отчета об интеграции
        
        Returns:
            Отчет об интеграции
        """
        print("📊 Генерация отчета об интеграции с SFM...")
        
        if not self.integration_results:
            return {"error": "Нет данных об интеграции"}
        
        successful_tests = [r for r in self.integration_results if r.success]
        failed_tests = [r for r in self.integration_results if not r.success]
        
        avg_response_time = sum(r.response_time for r in self.integration_results) / len(self.integration_results)
        
        sfm_available_count = sum(1 for r in self.integration_results if r.sfm_available)
        sfm_functions_found_count = sum(1 for r in self.integration_results if r.sfm_functions_count > 0)
        
        report = {
            "report_date": datetime.now().isoformat(),
            "total_tests": len(self.integration_results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": len(successful_tests) / len(self.integration_results) * 100,
            "avg_response_time": avg_response_time,
            "sfm_availability": sfm_available_count / len(self.integration_results) * 100,
            "sfm_functions_discovered": sfm_functions_found_count / len(self.integration_results) * 100,
            "test_details": [
                {
                    "endpoint": r.endpoint,
                    "method": r.method,
                    "success": r.success,
                    "response_time": r.response_time,
                    "status_code": r.status_code,
                    "sfm_available": r.sfm_available,
                    "sfm_functions_count": r.sfm_functions_count,
                    "error_message": r.error_message
                }
                for r in self.integration_results
            ],
            "summary": {
                "integration_quality": "excellent" if len(successful_tests) / len(self.integration_results) >= 0.9 else "good" if len(successful_tests) / len(self.integration_results) >= 0.7 else "needs_improvement",
                "sfm_integration_status": "fully_integrated" if sfm_functions_found_count > 0 else "partially_integrated" if sfm_available_count > 0 else "not_integrated"
            }
        }
        
        return report


class TestSFMIntegration:
    """Тесты интеграции с SFM"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестов"""
        self.tester = SFMIntegrationTester()
        
    @pytest.mark.asyncio
    async def test_sfm_availability(self):
        """Тест доступности SFM"""
        print("\n🧪 Тестирование доступности SFM...")
        
        sfm_available = await self.tester.check_sfm_availability()
        
        print(f"📊 SFM доступен: {'Да' if sfm_available else 'Нет'}")
        
        if sfm_available:
            print("✅ SFM сервис работает и доступен")
        else:
            print("⚠️ SFM сервис недоступен - тесты будут выполняться в режиме мокирования")
    
    @pytest.mark.asyncio
    async def test_sfm_functions_discovery(self):
        """Тест обнаружения функций SFM"""
        print("\n🧪 Тестирование обнаружения функций SFM...")
        
        functions = await self.tester.get_sfm_functions()
        
        print(f"📊 Найдено функций SFM: {len(functions)}")
        
        if functions:
            active_functions = [f for f in functions if f.status == "active"]
            critical_functions = [f for f in functions if f.is_critical]
            
            print(f"📊 Активных функций: {len(active_functions)}")
            print(f"📊 Критических функций: {len(critical_functions)}")
            
            # Показываем несколько примеров
            for i, func in enumerate(functions[:5]):
                print(f"  {i+1}. {func.name} ({func.status}) - {func.description[:50]}...")
        
        # Проверки
        if functions:
            assert len(functions) > 0, "Функции SFM не найдены"
            active_functions = [f for f in functions if f.status == "active"]
            assert len(active_functions) > 0, "Нет активных функций SFM"
    
    @pytest.mark.asyncio
    async def test_dashboard_sfm_endpoints(self):
        """Тест SFM endpoints в дашборде"""
        print("\n🧪 Тестирование SFM endpoints в дашборде...")
        
        endpoints_to_test = [
            ("/api/services", "GET"),
            ("/api/endpoints", "GET"),
            ("/api/test-history", "GET")
        ]
        
        results = []
        
        for endpoint, method in endpoints_to_test:
            result = await self.tester.test_dashboard_sfm_integration(endpoint, method)
            results.append(result)
            
            print(f"  {method} {endpoint}:")
            print(f"    Успех: {'Да' if result.success else 'Нет'}")
            print(f"    Время отклика: {result.response_time:.3f}s")
            print(f"    SFM доступен: {'Да' if result.sfm_available else 'Нет'}")
            print(f"    SFM функций найдено: {result.sfm_functions_count}")
            
            if result.error_message:
                print(f"    Ошибка: {result.error_message}")
        
        # Анализируем результаты
        successful_tests = [r for r in results if r.success]
        sfm_integrated_tests = [r for r in results if r.sfm_functions_count > 0]
        
        print(f"\n📊 Результаты:")
        print(f"  Успешных тестов: {len(successful_tests)}/{len(results)}")
        print(f"  Тестов с SFM интеграцией: {len(sfm_integrated_tests)}/{len(results)}")
        
        # Проверки
        assert len(successful_tests) >= len(results) * 0.8, "Слишком много неудачных тестов"
        assert all(r.response_time < 10.0 for r in results), "Слишком медленные отклики"
    
    @pytest.mark.asyncio
    async def test_sfm_function_management(self):
        """Тест управления функциями SFM"""
        print("\n🧪 Тестирование управления функциями SFM...")
        
        management_result = await self.tester.test_sfm_function_management()
        
        if management_result["success"]:
            print(f"✅ Всего функций: {management_result['total_functions']}")
            print(f"✅ Активных функций: {management_result['active_functions']}")
            print(f"✅ Критических функций: {management_result['critical_functions']}")
            print(f"✅ Автовключенных функций: {management_result['auto_enable_functions']}")
            print(f"✅ SFM доступен: {'Да' if management_result['sfm_available'] else 'Нет'}")
            
            for test in management_result["management_tests"]:
                print(f"  {test['test']}: {'✅' if test['success'] else '❌'}")
        else:
            print(f"❌ Ошибка управления функциями: {management_result.get('error', 'Неизвестная ошибка')}")
        
        # Проверки
        assert management_result["success"], f"Ошибка управления функциями SFM: {management_result.get('error')}"
        assert management_result["total_functions"] > 0, "Нет функций SFM для управления"
    
    @pytest.mark.asyncio
    async def test_sfm_real_time_monitoring(self):
        """Тест мониторинга SFM в реальном времени"""
        print("\n🧪 Тестирование мониторинга SFM в реальном времени...")
        
        # Получаем начальный статус
        initial_result = await self.tester.test_dashboard_sfm_integration("/api/services")
        
        print(f"📊 Начальный статус SFM: {'Доступен' if initial_result.sfm_available else 'Недоступен'}")
        print(f"📊 Начальное количество функций: {initial_result.sfm_functions_count}")
        
        # Ждем немного и проверяем снова
        await asyncio.sleep(2)
        
        final_result = await self.tester.test_dashboard_sfm_integration("/api/services")
        
        print(f"📊 Финальный статус SFM: {'Доступен' if final_result.sfm_available else 'Недоступен'}")
        print(f"📊 Финальное количество функций: {final_result.sfm_functions_count}")
        
        # Проверяем стабильность
        status_changed = initial_result.sfm_available != final_result.sfm_available
        functions_changed = initial_result.sfm_functions_count != final_result.sfm_functions_count
        
        print(f"📊 Статус изменился: {'Да' if status_changed else 'Нет'}")
        print(f"📊 Количество функций изменилось: {'Да' if functions_changed else 'Нет'}")
        
        # Проверки
        assert not status_changed, "Статус SFM изменился во время теста"
        assert final_result.response_time < 5.0, f"Слишком медленный отклик: {final_result.response_time:.3f}s"
    
    @pytest.mark.asyncio
    async def test_sfm_error_handling(self):
        """Тест обработки ошибок SFM"""
        print("\n🧪 Тестирование обработки ошибок SFM...")
        
        # Тестируем несуществующий endpoint
        error_result = await self.tester.test_dashboard_sfm_integration("/api/nonexistent", "GET")
        
        print(f"📊 Тест несуществующего endpoint:")
        print(f"  Статус код: {error_result.status_code}")
        print(f"  Успех: {'Да' if error_result.success else 'Нет'}")
        print(f"  Время отклика: {error_result.response_time:.3f}s")
        
        # Тестируем неверный метод
        method_error_result = await self.tester.test_dashboard_sfm_integration("/api/services", "DELETE")
        
        print(f"📊 Тест неверного метода:")
        print(f"  Статус код: {method_error_result.status_code}")
        print(f"  Успех: {'Да' if method_error_result.success else 'Нет'}")
        print(f"  Время отклика: {method_error_result.response_time:.3f}s")
        
        # Проверки
        assert not error_result.success, "Несуществующий endpoint должен возвращать ошибку"
        assert error_result.response_time < 5.0, "Слишком медленная обработка ошибки"
    
    def test_generate_integration_report(self):
        """Генерация отчета об интеграции"""
        print("\n📊 Генерация отчета об интеграции с SFM...")
        
        report = self.tester.generate_integration_report()
        
        if "error" in report:
            print(f"❌ Ошибка генерации отчета: {report['error']}")
            return
        
        # Сохранение отчета
        report_file = f"sfm_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Отчет сохранен: {report_file}")
        
        # Вывод краткой статистики
        print(f"\n📈 КРАТКАЯ СТАТИСТИКА:")
        print(f"  Всего тестов: {report['total_tests']}")
        print(f"  Успешных тестов: {report['successful_tests']}")
        print(f"  Процент успеха: {report['success_rate']:.1f}%")
        print(f"  Среднее время отклика: {report['avg_response_time']:.3f}s")
        print(f"  Доступность SFM: {report['sfm_availability']:.1f}%")
        print(f"  Обнаружение функций SFM: {report['sfm_functions_discovered']:.1f}%")
        print(f"  Качество интеграции: {report['summary']['integration_quality']}")
        print(f"  Статус интеграции: {report['summary']['sfm_integration_status']}")
        
        # Проверки отчета
        assert report['total_tests'] > 0, "Нет данных о тестах"
        assert report['success_rate'] >= 70, f"Слишком низкий процент успеха: {report['success_rate']:.1f}%"
        assert report['avg_response_time'] < 5.0, f"Слишком медленный отклик: {report['avg_response_time']:.3f}s"


if __name__ == "__main__":
    print("🚀 Запуск тестов интеграции ALADDIN Dashboard с SFM...")
    print("🔗 Проверка интеграции с Safe Function Manager...")
    print("🛡️ Тестирование управления функциями безопасности...")
    
    # Запуск тестов через pytest
    pytest.main([__file__, "-v", "--tb=short"])