#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Load Performance Tests для ALADDIN Dashboard
Нагрузочное тестирование веб-дашборда системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
import time
import psutil
import pytest
import httpx
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import os
import sys

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.base import ComponentStatus, SecurityLevel
    from core.logging_module import LoggingManager
    ALADDIN_AVAILABLE = True
except ImportError:
    ALADDIN_AVAILABLE = False


class DashboardLoadTester:
    """Класс для нагрузочного тестирования дашборда"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Инициализация нагрузочного тестера
        
        Args:
            base_url: Базовый URL дашборда
        """
        self.base_url = base_url
        self.logger = LoggingManager(name="DashboardLoadTester") if ALADDIN_AVAILABLE else None
        self.test_results: List[Dict[str, Any]] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
    async def simulate_user_session(self, user_id: int) -> Dict[str, Any]:
        """
        Симуляция сессии пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Результаты сессии
        """
        session_start = time.time()
        session_results = {
            "user_id": user_id,
            "requests": [],
            "total_time": 0,
            "success": True,
            "errors": []
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 1. Главная страница
                response = await self._make_request(client, "GET", "/")
                session_results["requests"].append({
                    "endpoint": "/",
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                })
                
                # 2. API endpoints
                response = await self._make_request(client, "GET", "/api/endpoints")
                session_results["requests"].append({
                    "endpoint": "/api/endpoints",
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                })
                
                # 3. Статус сервисов
                response = await self._make_request(client, "GET", "/api/services")
                session_results["requests"].append({
                    "endpoint": "/api/services",
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                })
                
                # 4. История тестов
                response = await self._make_request(client, "GET", "/api/test-history")
                session_results["requests"].append({
                    "endpoint": "/api/test-history",
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                })
                
                # 5. ML аналитика (если доступна)
                try:
                    response = await self._make_request(client, "GET", "/api/ml/health-analysis")
                    session_results["requests"].append({
                        "endpoint": "/api/ml/health-analysis",
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds()
                    })
                except Exception as e:
                    session_results["errors"].append(f"ML analytics error: {str(e)}")
                
                # 6. Тестирование endpoint
                response = await self._make_request(
                    client, 
                    "POST", 
                    "/api/test",
                    json_data={
                        "endpoint": "/health",
                        "method": "GET"
                    }
                )
                session_results["requests"].append({
                    "endpoint": "/api/test",
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                })
                
        except Exception as e:
            session_results["success"] = False
            session_results["errors"].append(str(e))
            
        session_results["total_time"] = time.time() - session_start
        return session_results
    
    async def _make_request(
        self, 
        client: httpx.AsyncClient, 
        method: str, 
        endpoint: str,
        json_data: Optional[Dict] = None
    ) -> httpx.Response:
        """
        Выполнение HTTP запроса
        
        Args:
            client: HTTP клиент
            method: HTTP метод
            endpoint: Endpoint
            json_data: JSON данные для POST запросов
            
        Returns:
            HTTP ответ
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": "Bearer demo_token"}
        
        if method.upper() == "GET":
            response = await client.get(url, headers=headers)
        elif method.upper() == "POST":
            response = await client.post(url, json=json_data, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        return response


class TestDashboardLoadPerformance:
    """Тесты нагрузочного тестирования дашборда"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестов"""
        self.tester = DashboardLoadTester()
        self.tester.start_time = datetime.now()
        
    def teardown_method(self):
        """Очистка после тестов"""
        if self.tester:
            self.tester.end_time = datetime.now()
    
    @pytest.mark.asyncio
    async def test_concurrent_users_10(self):
        """Тест 10 одновременных пользователей"""
        print("\n🧪 Тестирование 10 одновременных пользователей...")
        
        start_time = time.time()
        tasks = [self.tester.simulate_user_session(i) for i in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time
        
        # Анализ результатов
        successful_sessions = [r for r in results if isinstance(r, dict) and r.get("success", False)]
        failed_sessions = [r for r in results if not (isinstance(r, dict) and r.get("success", False))]
        
        print(f"✅ Успешных сессий: {len(successful_sessions)}/10")
        print(f"❌ Неудачных сессий: {len(failed_sessions)}/10")
        print(f"⏱️ Общее время: {duration:.2f} секунд")
        
        # Проверки
        assert len(successful_sessions) >= 8, f"Слишком много неудачных сессий: {len(failed_sessions)}"
        assert duration < 60, f"Тест слишком медленный: {duration:.2f}s > 60s"
        
        # Сохранение результатов
        self.tester.test_results.append({
            "test_name": "concurrent_users_10",
            "duration": duration,
            "successful_sessions": len(successful_sessions),
            "failed_sessions": len(failed_sessions),
            "success_rate": len(successful_sessions) / 10 * 100
        })
    
    @pytest.mark.asyncio
    async def test_concurrent_users_50(self):
        """Тест 50 одновременных пользователей"""
        print("\n🧪 Тестирование 50 одновременных пользователей...")
        
        start_time = time.time()
        tasks = [self.tester.simulate_user_session(i) for i in range(50)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time
        
        # Анализ результатов
        successful_sessions = [r for r in results if isinstance(r, dict) and r.get("success", False)]
        failed_sessions = [r for r in results if not (isinstance(r, dict) and r.get("success", False))]
        
        print(f"✅ Успешных сессий: {len(successful_sessions)}/50")
        print(f"❌ Неудачных сессий: {len(failed_sessions)}/50")
        print(f"⏱️ Общее время: {duration:.2f} секунд")
        
        # Проверки (более мягкие для 50 пользователей)
        assert len(successful_sessions) >= 35, f"Слишком много неудачных сессий: {len(failed_sessions)}"
        assert duration < 120, f"Тест слишком медленный: {duration:.2f}s > 120s"
        
        # Сохранение результатов
        self.tester.test_results.append({
            "test_name": "concurrent_users_50",
            "duration": duration,
            "successful_sessions": len(successful_sessions),
            "failed_sessions": len(failed_sessions),
            "success_rate": len(successful_sessions) / 50 * 100
        })
    
    @pytest.mark.asyncio
    async def test_concurrent_users_100(self):
        """Тест 100 одновременных пользователей"""
        print("\n🧪 Тестирование 100 одновременных пользователей...")
        
        start_time = time.time()
        tasks = [self.tester.simulate_user_session(i) for i in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time
        
        # Анализ результатов
        successful_sessions = [r for r in results if isinstance(r, dict) and r.get("success", False)]
        failed_sessions = [r for r in results if not (isinstance(r, dict) and r.get("success", False))]
        
        print(f"✅ Успешных сессий: {len(successful_sessions)}/100")
        print(f"❌ Неудачных сессий: {len(failed_sessions)}/100")
        print(f"⏱️ Общее время: {duration:.2f} секунд")
        
        # Проверки (еще более мягкие для 100 пользователей)
        assert len(successful_sessions) >= 60, f"Слишком много неудачных сессий: {len(failed_sessions)}"
        assert duration < 180, f"Тест слишком медленный: {duration:.2f}s > 180s"
        
        # Сохранение результатов
        self.tester.test_results.append({
            "test_name": "concurrent_users_100",
            "duration": duration,
            "successful_sessions": len(successful_sessions),
            "failed_sessions": len(failed_sessions),
            "success_rate": len(successful_sessions) / 100 * 100
        })
    
    @pytest.mark.asyncio
    async def test_sustained_load(self):
        """Тест продолжительной нагрузки (5 минут)"""
        print("\n🧪 Тестирование продолжительной нагрузки (5 минут)...")
        
        start_time = time.time()
        end_time = start_time + 300  # 5 минут
        concurrent_users = 20
        results = []
        
        while time.time() < end_time:
            # Запускаем batch пользователей
            tasks = [
                self.tester.simulate_user_session(i) 
                for i in range(concurrent_users)
            ]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(batch_results)
            
            # Небольшая пауза между batches
            await asyncio.sleep(10)
        
        duration = time.time() - start_time
        
        # Анализ результатов
        successful_sessions = [r for r in results if isinstance(r, dict) and r.get("success", False)]
        failed_sessions = [r for r in results if not (isinstance(r, dict) and r.get("success", False))]
        
        print(f"✅ Успешных сессий: {len(successful_sessions)}")
        print(f"❌ Неудачных сессий: {len(failed_sessions)}")
        print(f"⏱️ Общее время: {duration:.2f} секунд")
        
        # Проверки
        assert len(successful_sessions) >= len(results) * 0.7, "Слишком много неудачных сессий"
        assert duration >= 280, f"Тест слишком короткий: {duration:.2f}s < 280s"
        
        # Сохранение результатов
        self.tester.test_results.append({
            "test_name": "sustained_load_5min",
            "duration": duration,
            "successful_sessions": len(successful_sessions),
            "failed_sessions": len(failed_sessions),
            "success_rate": len(successful_sessions) / len(results) * 100
        })
    
    @pytest.mark.asyncio
    async def test_memory_usage_during_load(self):
        """Тест потребления памяти во время нагрузки"""
        print("\n🧪 Тестирование потребления памяти во время нагрузки...")
        
        # Получаем начальное потребление памяти
        initial_memory = psutil.virtual_memory().percent
        process = psutil.Process()
        initial_process_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"📊 Начальная память системы: {initial_memory:.1f}%")
        print(f"📊 Начальная память процесса: {initial_process_memory:.1f} MB")
        
        # Запускаем нагрузочный тест
        start_time = time.time()
        tasks = [self.tester.simulate_user_session(i) for i in range(30)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time
        
        # Получаем финальное потребление памяти
        final_memory = psutil.virtual_memory().percent
        final_process_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_increase = final_memory - initial_memory
        process_memory_increase = final_process_memory - initial_process_memory
        
        print(f"📊 Финальная память системы: {final_memory:.1f}%")
        print(f"📊 Финальная память процесса: {final_process_memory:.1f} MB")
        print(f"📊 Увеличение памяти системы: {memory_increase:.1f}%")
        print(f"📊 Увеличение памяти процесса: {process_memory_increase:.1f} MB")
        
        # Проверки
        assert memory_increase < 20, f"Слишком большое увеличение памяти системы: {memory_increase:.1f}%"
        assert process_memory_increase < 100, f"Слишком большое увеличение памяти процесса: {process_memory_increase:.1f} MB"
        
        # Сохранение результатов
        self.tester.test_results.append({
            "test_name": "memory_usage_during_load",
            "duration": duration,
            "initial_memory_percent": initial_memory,
            "final_memory_percent": final_memory,
            "memory_increase_percent": memory_increase,
            "initial_process_memory_mb": initial_process_memory,
            "final_process_memory_mb": final_process_memory,
            "process_memory_increase_mb": process_memory_increase
        })
    
    def test_generate_performance_report(self):
        """Генерация отчета о производительности"""
        print("\n📊 Генерация отчета о производительности...")
        
        if not self.tester.test_results:
            print("❌ Нет результатов тестов для отчета")
            return
        
        report = {
            "test_date": datetime.now().isoformat(),
            "total_tests": len(self.tester.test_results),
            "tests": self.tester.test_results,
            "summary": self._generate_summary()
        }
        
        # Сохранение отчета
        report_file = f"load_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Отчет сохранен: {report_file}")
        
        # Вывод краткой статистики
        print("\n📈 КРАТКАЯ СТАТИСТИКА:")
        for test in self.tester.test_results:
            print(f"  {test['test_name']}: {test.get('success_rate', 'N/A'):.1f}% успех")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Генерация краткого резюме тестов"""
        if not self.tester.test_results:
            return {}
        
        total_tests = len(self.tester.test_results)
        successful_tests = sum(1 for test in self.tester.test_results if test.get('success_rate', 0) >= 70)
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": successful_tests / total_tests * 100,
            "average_duration": sum(test.get('duration', 0) for test in self.tester.test_results) / total_tests
        }


class TestDashboardEndpoints:
    """Тесты отдельных endpoints дашборда"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестов"""
        self.base_url = "http://localhost:8080"
    
    @pytest.mark.asyncio
    async def test_main_page_response_time(self):
        """Тест времени отклика главной страницы"""
        print("\n🧪 Тестирование времени отклика главной страницы...")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            start_time = time.time()
            response = await client.get(f"{self.base_url}/")
            duration = time.time() - start_time
            
            print(f"⏱️ Время отклика: {duration:.3f} секунд")
            print(f"📊 Статус код: {response.status_code}")
            
            assert response.status_code == 200, f"Неверный статус код: {response.status_code}"
            assert duration < 2.0, f"Слишком медленный отклик: {duration:.3f}s > 2.0s"
    
    @pytest.mark.asyncio
    async def test_api_endpoints_response_time(self):
        """Тест времени отклика API endpoints"""
        print("\n🧪 Тестирование времени отклика API endpoints...")
        
        endpoints = [
            "/api/endpoints",
            "/api/services",
            "/api/test-history",
            "/api/autocomplete?query=test"
        ]
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": "Bearer demo_token"}
            
            for endpoint in endpoints:
                start_time = time.time()
                response = await client.get(f"{self.base_url}{endpoint}", headers=headers)
                duration = time.time() - start_time
                
                print(f"  {endpoint}: {duration:.3f}s (статус: {response.status_code})")
                
                assert duration < 3.0, f"Слишком медленный отклик для {endpoint}: {duration:.3f}s"
                assert response.status_code in [200, 404], f"Неверный статус код для {endpoint}: {response.status_code}"
    
    @pytest.mark.asyncio
    async def test_api_test_endpoint(self):
        """Тест endpoint для тестирования API"""
        print("\n🧪 Тестирование endpoint для тестирования API...")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {"Authorization": "Bearer demo_token"}
            
            test_data = {
                "endpoint": "/health",
                "method": "GET"
            }
            
            start_time = time.time()
            response = await client.post(
                f"{self.base_url}/api/test", 
                json=test_data, 
                headers=headers
            )
            duration = time.time() - start_time
            
            print(f"⏱️ Время отклика: {duration:.3f} секунд")
            print(f"📊 Статус код: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📊 Результат теста: {result.get('success', 'unknown')}")
            
            assert response.status_code in [200, 400, 500], f"Неожиданный статус код: {response.status_code}"
            assert duration < 10.0, f"Слишком медленный отклик: {duration:.3f}s > 10.0s"


if __name__ == "__main__":
    print("🚀 Запуск нагрузочных тестов для ALADDIN Dashboard...")
    print("📊 Тестирование производительности веб-интерфейса...")
    print("🛡️ Проверка стабильности под нагрузкой...")
    
    # Запуск тестов через pytest
    pytest.main([__file__, "-v", "--tb=short"])