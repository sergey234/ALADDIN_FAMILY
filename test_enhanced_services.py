#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для Enhanced Services
Проверка функциональности API Docs и Architecture Visualizer

Автор: ALADDIN Security Team
Версия: 2.0
Дата: 2025-01-06
"""

import asyncio
import httpx
import json
import time
from datetime import datetime

class EnhancedServicesTester:
    """Тестер для Enhanced Services"""
    
    def __init__(self):
        self.api_docs_url = "http://localhost:8080"
        self.arch_viz_url = "http://localhost:8081"
        self.test_results = []
    
    async def test_api_docs(self):
        """Тестирование Enhanced API Docs"""
        print("🧪 Тестирование Enhanced API Docs...")
        
        async with httpx.AsyncClient() as client:
            try:
                # Тест 1: Главная страница
                print("  📄 Тест главной страницы...")
                response = await client.get(f"{self.api_docs_url}/")
                if response.status_code == 200:
                    print("    ✅ Главная страница загружена")
                    self.test_results.append({"test": "API Docs Homepage", "status": "PASS"})
                else:
                    print(f"    ❌ Ошибка загрузки главной страницы: {response.status_code}")
                    self.test_results.append({"test": "API Docs Homepage", "status": "FAIL"})
                
                # Тест 2: Получение endpoints
                print("  📡 Тест получения endpoints...")
                response = await client.get(f"{self.api_docs_url}/api/endpoints")
                if response.status_code == 200:
                    data = response.json()
                    endpoints_count = len(data.get("endpoints", []))
                    print(f"    ✅ Получено {endpoints_count} endpoints")
                    self.test_results.append({"test": "Get Endpoints", "status": "PASS", "count": endpoints_count})
                else:
                    print(f"    ❌ Ошибка получения endpoints: {response.status_code}")
                    self.test_results.append({"test": "Get Endpoints", "status": "FAIL"})
                
                # Тест 3: Получение сервисов
                print("  🔧 Тест получения сервисов...")
                response = await client.get(f"{self.api_docs_url}/api/services")
                if response.status_code == 200:
                    data = response.json()
                    services_count = len(data.get("services", {}))
                    print(f"    ✅ Получено {services_count} сервисов")
                    self.test_results.append({"test": "Get Services", "status": "PASS", "count": services_count})
                else:
                    print(f"    ❌ Ошибка получения сервисов: {response.status_code}")
                    self.test_results.append({"test": "Get Services", "status": "FAIL"})
                
                # Тест 4: Тестирование API endpoint
                print("  🧪 Тест тестирования API endpoint...")
                test_data = {
                    "endpoint": "/health",
                    "method": "GET"
                }
                response = await client.post(
                    f"{self.api_docs_url}/api/test",
                    json=test_data,
                    headers={"Authorization": "Bearer demo_token"}
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"    ✅ Тест endpoint выполнен: {data.get('status_code', 'N/A')}")
                    self.test_results.append({"test": "Test Endpoint", "status": "PASS"})
                else:
                    print(f"    ❌ Ошибка тестирования endpoint: {response.status_code}")
                    self.test_results.append({"test": "Test Endpoint", "status": "FAIL"})
                
                # Тест 5: История тестов
                print("  📊 Тест истории тестов...")
                response = await client.get(f"{self.api_docs_url}/api/test-history")
                if response.status_code == 200:
                    data = response.json()
                    history_count = len(data.get("history", []))
                    print(f"    ✅ Получено {history_count} записей истории")
                    self.test_results.append({"test": "Get Test History", "status": "PASS", "count": history_count})
                else:
                    print(f"    ❌ Ошибка получения истории: {response.status_code}")
                    self.test_results.append({"test": "Get Test History", "status": "FAIL"})
                
                # Тест 6: Экспорт JSON
                print("  📤 Тест экспорта JSON...")
                response = await client.get(f"{self.api_docs_url}/api/export/json")
                if response.status_code == 200:
                    data = response.json()
                    print(f"    ✅ JSON экспорт выполнен")
                    self.test_results.append({"test": "JSON Export", "status": "PASS"})
                else:
                    print(f"    ❌ Ошибка JSON экспорта: {response.status_code}")
                    self.test_results.append({"test": "JSON Export", "status": "FAIL"})
                
            except Exception as e:
                print(f"    ❌ Ошибка подключения к API Docs: {e}")
                self.test_results.append({"test": "API Docs Connection", "status": "FAIL", "error": str(e)})
    
    async def test_architecture_visualizer(self):
        """Тестирование Enhanced Architecture Visualizer"""
        print("\n🏗️ Тестирование Enhanced Architecture Visualizer...")
        
        async with httpx.AsyncClient() as client:
            try:
                # Тест 1: Главная страница
                print("  📄 Тест главной страницы...")
                response = await client.get(f"{self.arch_viz_url}/")
                if response.status_code == 200:
                    print("    ✅ Главная страница загружена")
                    self.test_results.append({"test": "Arch Viz Homepage", "status": "PASS"})
                else:
                    print(f"    ❌ Ошибка загрузки главной страницы: {response.status_code}")
                    self.test_results.append({"test": "Arch Viz Homepage", "status": "FAIL"})
                
                # Тест 2: Получение архитектуры
                print("  🏗️ Тест получения архитектуры...")
                response = await client.get(f"{self.arch_viz_url}/api/architecture")
                if response.status_code == 200:
                    data = response.json()
                    services_count = len(data.get("services", {}))
                    connections_count = len(data.get("connections", []))
                    print(f"    ✅ Получена архитектура: {services_count} сервисов, {connections_count} соединений")
                    self.test_results.append({"test": "Get Architecture", "status": "PASS", "services": services_count, "connections": connections_count})
                else:
                    print(f"    ❌ Ошибка получения архитектуры: {response.status_code}")
                    self.test_results.append({"test": "Get Architecture", "status": "FAIL"})
                
                # Тест 3: Получение сервисов
                print("  🔧 Тест получения сервисов...")
                response = await client.get(f"{self.arch_viz_url}/api/services")
                if response.status_code == 200:
                    data = response.json()
                    services_count = len(data.get("services", {}))
                    print(f"    ✅ Получено {services_count} сервисов")
                    self.test_results.append({"test": "Get Services", "status": "PASS", "count": services_count})
                else:
                    print(f"    ❌ Ошибка получения сервисов: {response.status_code}")
                    self.test_results.append({"test": "Get Services", "status": "FAIL"})
                
                # Тест 4: Получение метрик
                print("  📊 Тест получения метрик...")
                response = await client.get(f"{self.arch_viz_url}/api/metrics")
                if response.status_code == 200:
                    data = response.json()
                    metrics = data.get("metrics", {})
                    print(f"    ✅ Получены метрики: CPU {metrics.get('cpu', {}).get('percent', 0):.1f}%, RAM {metrics.get('memory', {}).get('percent', 0):.1f}%")
                    self.test_results.append({"test": "Get Metrics", "status": "PASS"})
                else:
                    print(f"    ❌ Ошибка получения метрик: {response.status_code}")
                    self.test_results.append({"test": "Get Metrics", "status": "FAIL"})
                
                # Тест 5: Получение алертов
                print("  🚨 Тест получения алертов...")
                response = await client.get(f"{self.arch_viz_url}/api/alerts")
                if response.status_code == 200:
                    data = response.json()
                    alerts_count = len(data.get("alerts", []))
                    print(f"    ✅ Получено {alerts_count} алертов")
                    self.test_results.append({"test": "Get Alerts", "status": "PASS", "count": alerts_count})
                else:
                    print(f"    ❌ Ошибка получения алертов: {response.status_code}")
                    self.test_results.append({"test": "Get Alerts", "status": "FAIL"})
                
            except Exception as e:
                print(f"    ❌ Ошибка подключения к Architecture Visualizer: {e}")
                self.test_results.append({"test": "Arch Viz Connection", "status": "FAIL", "error": str(e)})
    
    async def test_websocket_connection(self):
        """Тестирование WebSocket соединения"""
        print("\n🔌 Тестирование WebSocket соединения...")
        
        try:
            import websockets
            
            async with websockets.connect(f"ws://localhost:8081/ws") as websocket:
                print("  ✅ WebSocket соединение установлено")
                
                # Ждем сообщение
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(message)
                
                if "services" in data and "timestamp" in data:
                    print("  ✅ Получено WebSocket сообщение с архитектурой")
                    self.test_results.append({"test": "WebSocket Connection", "status": "PASS"})
                else:
                    print("  ❌ Неверный формат WebSocket сообщения")
                    self.test_results.append({"test": "WebSocket Connection", "status": "FAIL"})
                
        except ImportError:
            print("  ⚠️  websockets не установлен, пропускаем WebSocket тест")
            self.test_results.append({"test": "WebSocket Connection", "status": "SKIP", "reason": "websockets not installed"})
        except Exception as e:
            print(f"  ❌ Ошибка WebSocket соединения: {e}")
            self.test_results.append({"test": "WebSocket Connection", "status": "FAIL", "error": str(e)})
    
    def print_summary(self):
        """Вывод сводки тестов"""
        print("\n" + "="*60)
        print("📊 СВОДКА ТЕСТОВ")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIP"])
        
        print(f"Всего тестов: {total_tests}")
        print(f"✅ Пройдено: {passed_tests}")
        print(f"❌ Провалено: {failed_tests}")
        print(f"⏭️  Пропущено: {skipped_tests}")
        print(f"📈 Успешность: {(passed_tests/total_tests*100):.1f}%")
        
        print("\n📋 Детали тестов:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⏭️"
            print(f"  {status_icon} {result['test']}: {result['status']}")
            if "error" in result:
                print(f"      Ошибка: {result['error']}")
            if "count" in result:
                print(f"      Количество: {result['count']}")
        
        # Сохранение результатов
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "skipped": skipped_tests,
                    "success_rate": passed_tests/total_tests*100
                },
                "results": self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Результаты сохранены в {filename}")
        
        if failed_tests > 0:
            print("\n⚠️  Некоторые тесты провалились. Проверьте:")
            print("   • Запущены ли Enhanced Services")
            print("   • Доступны ли порты 8080 и 8081")
            print("   • Установлены ли все зависимости")
            return False
        else:
            print("\n🎉 Все тесты пройдены успешно!")
            return True

async def main():
    """Главная функция тестирования"""
    print("🛡️ ALADDIN Enhanced Services Tester")
    print("="*50)
    print(f"⏰ Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tester = EnhancedServicesTester()
    
    # Запуск тестов
    await tester.test_api_docs()
    await tester.test_architecture_visualizer()
    await tester.test_websocket_connection()
    
    # Вывод результатов
    success = tester.print_summary()
    
    if success:
        print("\n🚀 Enhanced Services работают корректно!")
        print("🌐 Доступные сервисы:")
        print("   📡 Enhanced API Docs: http://localhost:8080")
        print("   🏗️ Enhanced Architecture Visualizer: http://localhost:8081")
    else:
        print("\n❌ Обнаружены проблемы. Проверьте логи выше.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)