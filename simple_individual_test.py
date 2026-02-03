#!/usr/bin/env python3
"""
ПРОСТОЕ ИНДИВИДУАЛЬНОЕ ТЕСТИРОВАНИЕ API ЭНДПОИНТОВ
Тестирование без запуска сервера - предполагается, что сервер уже работает
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple

class SimpleAPITester:
    def __init__(self, base_url: str = "http://localhost:8003"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results = []

    def test_single_endpoint(self, method: str, path: str, test_name: str, expected_status: int = 200) -> Dict:
        """Тестирование одного эндпоинта"""
        url = f"{self.base_url}{path}"
        start_time = time.time()

        print(f"🧪 {test_name}")
        print(f"   {method} {url}")

        try:
            # Подготавливаем запрос
            test_data = self.get_test_data(path)

            if method.upper() == 'GET':
                response = self.session.get(url, timeout=15)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=test_data, timeout=15)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=test_data, timeout=15)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=15)

            response_time = int((time.time() - start_time) * 1000)

            # Проверяем статус
            success = response.status_code == expected_status
            status = 'SUCCESS' if success else 'FAILED'

            # Проверяем SFM интеграцию
            sfm_integration = False
            response_data = None
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    response_data = response.json()
                    if isinstance(response_data, dict) and 'source' in response_data:
                        sfm_integration = response_data['source'] == 'real_sfm'
            except:
                pass

            result = {
                'test_name': test_name,
                'method': method,
                'path': path,
                'status': status,
                'http_status': response.status_code,
                'expected_status': expected_status,
                'response_time': response_time,
                'sfm_integration': sfm_integration,
                'response_data': response_data,
                'error': None if success else f'Expected {expected_status}, got {response.status_code}'
            }

            # Вывод результата
            status_icon = "✅" if success else "❌"
            sfm_icon = "🔐" if sfm_integration else "⚠️"
            time_icon = "⚡" if response_time < 200 else "🐌"

            print(f"   {status_icon} {sfm_icon} {time_icon} {response_time}ms")
            if not success:
                print(f"      Ожидали: {expected_status}, Получили: {response.status_code}")

            return result

        except requests.exceptions.RequestException as e:
            response_time = int((time.time() - start_time) * 1000)
            result = {
                'test_name': test_name,
                'method': method,
                'path': path,
                'status': 'ERROR',
                'http_status': None,
                'expected_status': expected_status,
                'response_time': response_time,
                'sfm_integration': False,
                'response_data': None,
                'error': str(e)
            }
            print(f"   ❌ Сетевая ошибка: {str(e)}")
            return result

    def get_test_data(self, path: str) -> Dict:
        """Тестовые данные для эндпоинта"""
        # Используем тот же словарь, что и в основном скрипте
        test_data = {}

        if '/auth/register' in path:
            test_data = {"username": "test_user", "email": "test@example.com", "password": "test123"}
        elif '/auth/login' in path:
            test_data = {"username": "test_user", "password": "test123"}
        elif '/subscription/upgrade' in path:
            test_data = {"new_plan": "premium"}
        elif '/components/enable/' in path or '/components/disable/' in path:
            test_data = {"reason": "test"}
        elif '/components/config/' in path:
            test_data = {"max_connections": 100}
        elif '/notifications/mark_read/' in path:
            test_data = {"notification_ids": ["123"]}
        # Добавьте другие тестовые данные по необходимости

        return test_data

    def run_all_tests(self) -> bool:
        """Запуск тестирования всех основных эндпоинтов"""

        # Список основных эндпоинтов для тестирования (представительная выборка)
        test_endpoints = [
            # Health checks
            ("GET", "/", "Root endpoint"),
            ("GET", "/api/health", "API Health check"),

            # Authentication
            ("POST", "/api/auth/register", "User registration"),
            ("POST", "/api/auth/login", "User login"),
            ("GET", "/api/auth/profile", "Get user profile"),
            ("POST", "/api/auth/refresh", "Refresh token"),

            # Components
            ("GET", "/api/components/health", "Components health"),
            ("GET", "/api/components/status/sfm_core", "Component status"),
            ("POST", "/api/components/enable/sfm_core", "Enable component"),
            ("PUT", "/api/components/config/sfm_core", "Update component config"),

            # Security features
            ("GET", "/api/phishing/sensitivity", "Anti-phishing sensitivity"),
            ("GET", "/api/malware/scan_scheduled", "Antivirus schedule"),
            ("GET", "/api/mobile/app_lock", "Mobile security status"),

            # Analytics
            ("GET", "/api/analytics/overview", "Analytics overview"),
            ("GET", "/api/analytics/performance", "Performance metrics"),

            # System
            ("GET", "/api/system/info", "System information"),
            ("GET", "/api/system/health", "System health"),
        ]

        print("=" * 70)
        print("🧪 ИНДИВИДУАЛЬНОЕ ТЕСТИРОВАНИЕ API ЭНДПОИНТОВ")
        print("=" * 70)
        print(f"Всего эндпоинтов для тестирования: {len(test_endpoints)}")
        print()

        successful_tests = 0
        total_response_time = 0

        for i, (method, path, test_name) in enumerate(test_endpoints, 1):
            print(f"\n[{i:2d}/{len(test_endpoints)}] ", end="")
            result = self.test_single_endpoint(method, path, test_name)
            self.results.append(result)

            if result['status'] == 'SUCCESS':
                successful_tests += 1
            total_response_time += result['response_time']

            # Небольшая пауза между тестами
            time.sleep(0.1)

        # Итоговый отчет
        print("\n" + "=" * 70)
        print("📊 РЕЗУЛЬТАТЫ ИНДИВИДУАЛЬНОГО ТЕСТИРОВАНИЯ")
        print("=" * 70)

        total_tests = len(test_endpoints)
        success_rate = (successful_tests / total_tests) * 100
        avg_response_time = total_response_time / total_tests

        print(f"✅ Успешных тестов: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"⚡ Среднее время ответа: {avg_response_time:.1f}ms")

        # Детальный анализ
        sfm_integrated = sum(1 for r in self.results if r.get('sfm_integration', False))
        fast_responses = sum(1 for r in self.results if r['response_time'] < 200)
        errors = [r for r in self.results if r['status'] != 'SUCCESS']

        print(f"🔐 SFM интеграция: {sfm_integrated}/{total_tests}")
        print(f"🚀 Быстрые ответы (<200ms): {fast_responses}/{total_tests}")
        print(f"❌ Ошибок: {len(errors)}")

        if errors:
            print("\n❌ Детали ошибок:")
            for error in errors:
                print(f"   • {error['test_name']}: {error['error']}")

        # Сохранение результатов
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"simple_individual_test_results_{timestamp}.json"

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'sfm_integrated': sfm_integrated,
                'fast_responses': fast_responses,
                'errors': len(errors),
                'results': self.results
            }, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Результаты сохранены в: {results_file}")

        # Критерии успешности
        success_criteria = (
            success_rate >= 95 and  # 95% успешность
            avg_response_time < 200 and  # Среднее время < 200ms
            sfm_integrated >= total_tests * 0.8  # 80% SFM интеграция
        )

        if success_criteria:
            print("\n🎉 ВСЕ КРИТЕРИИ ВЫПОЛНЕНЫ!")
            print("✅ API готов к продакшену")
            return True
        else:
            print("\n⚠️ НЕКОТОРЫЕ КРИТЕРИИ НЕ ВЫПОЛНЕНЫ")
            print("Проверьте настройки сервера")
            return False

def main():
    print("🔍 Проверка доступности сервера...")

    tester = SimpleAPITester()

    # Проверяем доступность сервера
    try:
        response = requests.get("http://localhost:8003/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Сервер недоступен или возвращает ошибку")
            return False
    except:
        print("❌ Сервер не запущен. Запустите тестовый сервер командой:")
        print("   python3 api_gateway_sync_test.py")
        return False

    print("✅ Сервер доступен, начинаем тестирование...")

    return tester.run_all_tests()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)