#!/usr/bin/env python3
"""
ПОСЛЕДОВАТЕЛЬНОЕ ТЕСТИРОВАНИЕ ВСЕХ 183 ЭНДПОИНТОВ
По 1 эндпоинту за раз с перезапуском сервера для каждого теста
Решение проблемы event loop конфликта
"""

import subprocess
import time
import requests
import json
from datetime import datetime
import signal
import os

class SequentialEndpointTester:
    def __init__(self):
        self.base_url = "http://localhost:8002"
        self.server_process = None
        self.results = []
        self.current_test = 0
        self.total_tests = 183

        # Все 183 эндпоинта для тестирования
        self.all_endpoints = self._get_all_endpoints()

    def _get_all_endpoints(self):
        """Получить все 183 эндпоинта из файла"""
        endpoints = []

        # Читаем файл и извлекаем все декораторы
        with open('api_gateway_complete.py', 'r') as f:
            lines = f.readlines()

        current_method = None
        current_path = None

        for line in lines:
            line = line.strip()

            if line.startswith('@app.'):
                import re

                if 'get(' in line:
                    current_method = 'GET'
                    match = re.search(r'@app\.get\((.*?)\)', line)
                    if match:
                        path_str = match.group(1).strip()
                        current_path = path_str.strip('"\'')  # Remove quotes

                elif 'post(' in line:
                    current_method = 'POST'
                    match = re.search(r'@app\.post\((.*?)\)', line)
                    if match:
                        path_str = match.group(1).strip()
                        current_path = path_str.strip('"\'')  # Remove quotes

                elif 'put(' in line:
                    current_method = 'PUT'
                    match = re.search(r'@app\.put\((.*?)\)', line)
                    if match:
                        path_str = match.group(1).strip()
                        current_path = path_str.strip('"\'')  # Remove quotes

                elif 'delete(' in line:
                    current_method = 'DELETE'
                    match = re.search(r'@app\.delete\((.*?)\)', line)
                    if match:
                        path_str = match.group(1).strip()
                        current_path = path_str.strip('"\'')  # Remove quotes

            elif current_method and current_path and (line.startswith('def ') or line.startswith('async def ')):
                # Извлекаем имя функции
                func_name = line.split('def ')[1].split('(')[0].strip()

                endpoints.append({
                    'method': current_method,
                    'path': current_path,
                    'function': func_name,
                    'test_name': f"{current_method} {current_path}",
                    'expected_status': 200
                })

                current_method = None
                current_path = None

        return endpoints

    def start_server(self):
        """Запуск сервера"""
        print(f"🚀 Запуск сервера для теста #{self.current_test + 1}...")

        # Убиваем возможные предыдущие процессы
        subprocess.run(['pkill', '-f', 'uvicorn'], capture_output=True, timeout=5)

        # Запускаем сервер
        self.server_process = subprocess.Popen([
            'python3', '-m', 'uvicorn',
            'api_gateway_complete:app',
            '--host', '0.0.0.0',
            '--port', '8002',
            '--reload'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Ждем запуска
        time.sleep(3)

        # Проверяем, что сервер запустился
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Сервер вернул статус {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка подключения к серверу: {e}")
            return False

    def stop_server(self):
        """Остановка сервера"""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                print("✅ Сервер остановлен")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                print("⚠️ Сервер принудительно остановлен")

    def test_single_endpoint(self, endpoint):
        """Тестирование одного эндпоинта"""
        method = endpoint['method']
        path = endpoint['path']
        test_name = endpoint['test_name']
        expected_status = endpoint['expected_status']

        url = f"{self.base_url}{path}"

        print(f"🧪 ТЕСТ #{self.current_test + 1}/{self.total_tests}: {test_name}")

        try:
            start_time = time.time()

            # Подготавливаем запрос
            test_data = self.get_test_data(path)

            if method == 'GET':
                response = requests.get(url, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=test_data, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=test_data, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=15)

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
                'test_number': self.current_test + 1,
                'test_name': test_name,
                'method': method,
                'path': path,
                'status': status,
                'http_status': response.status_code,
                'expected_status': expected_status,
                'response_time': response_time,
                'sfm_integration': sfm_integration,
                'response_data': response_data,
                'error': None if success else f'Expected {expected_status}, got {response.status_code}',
                'timestamp': datetime.now().isoformat()
            }

            # Вывод результата
            status_icon = "✅" if success else "❌"
            sfm_icon = "🔐" if sfm_integration else "⚠️"
            time_icon = "⚡" if response_time < 200 else "🐌"

            print(f"   {status_icon} {sfm_icon} {time_icon} {response_time}ms (статус: {response.status_code})")

            return result

        except requests.exceptions.RequestException as e:
            response_time = int((time.time() - start_time) * 1000)
            result = {
                'test_number': self.current_test + 1,
                'test_name': test_name,
                'method': method,
                'path': path,
                'status': 'ERROR',
                'http_status': None,
                'expected_status': expected_status,
                'response_time': response_time,
                'sfm_integration': False,
                'response_data': None,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"   ❌ Сетевая ошибка: {str(e)}")
            return result

    def get_test_data(self, path):
        """Тестовые данные для эндпоинта"""
        test_data = {}

        # Authentication
        if '/auth/register' in path:
            test_data = {"username": "test_user", "email": "test@example.com", "password": "test123", "device_info": {"platform": "ios"}}
        elif '/auth/login' in path:
            test_data = {"username": "test_user", "password": "test123"}
        elif '/auth/refresh' in path:
            test_data = {"refresh_token": "test_token"}

        # Subscription
        elif '/subscription/upgrade' in path:
            test_data = {"new_plan": "premium"}
        elif '/subscription/cancel' in path:
            test_data = {"reason": "test"}

        # Components
        elif '/components/enable/' in path or '/components/disable/' in path:
            test_data = {"reason": "test"}
        elif '/components/restart/' in path:
            test_data = {"reason": "test"}
        elif '/components/backup/' in path:
            test_data = {"backup_type": "full"}
        elif '/components/restore/' in path:
            test_data = {"backup_id": "test"}
        elif '/components/config/' in path:
            test_data = {"max_connections": 100}

        # Notifications
        elif '/notifications/mark_read/' in path:
            test_data = {"notification_ids": ["123"]}
        elif '/notifications/delete/' in path:
            test_data = {"notification_ids": ["123"]}
        elif '/notifications/bulk_mark_read' in path:
            test_data = {"notification_ids": ["1", "2", "3"]}
        elif '/notifications/test' in path:
            test_data = {"message": "test"}
        elif '/notifications/settings' in path:
            test_data = {"enabled": True, "email_notifications": True}

        # Parental Control
        elif '/parental/restrict/' in path:
            test_data = {"restriction_type": "website_block", "target": "social", "duration": 3600}
        elif '/parental/alert' in path:
            test_data = {"message": "test alert"}

        # Identity Protection
        elif '/identity/allow' in path:
            test_data = {"identity_type": "email", "identity_value": "test@example.com"}
        elif '/identity/block' in path:
            test_data = {"identity_type": "ip", "identity_value": "192.168.1.1"}
        elif '/identity/whitelist' in path:
            test_data = {"identity_type": "domain", "identity_value": "trusted.com"}
        elif '/identity/theft/report/' in path:
            test_data = {"report_type": "theft", "description": "test", "evidence": ["test.jpg"]}

        # Dark Web Monitoring
        elif '/darkweb/scan_start' in path:
            test_data = {"scan_type": "full", "target": "test@example.com"}
        elif '/darkweb/resolve' in path:
            test_data = {"leak_id": "12345", "action": "remove"}

        # Location Tracking
        elif '/location/allow' in path:
            test_data = {"app_id": "maps", "reason": "navigation"}
        elif '/location/block' in path:
            test_data = {"app_id": "spy", "reason": "privacy"}
        elif '/location/accuracy' in path:
            test_data = {"accuracy_level": "high", "update_interval": 30}

        # Data Cleanup
        elif '/data/cleanup/start' in path:
            test_data = {"cleanup_type": "full", "target": "history"}

        # Anti-Tracker
        elif '/antitracker/scan' in path:
            test_data = {"scan_type": "quick", "target": "example.com"}
        elif '/antitracker/whitelist' in path:
            test_data = {"tracker_domain": "cdn.example.com", "reason": "trusted"}

        # Roadside Assistance
        elif '/roadside/emergency' in path:
            test_data = {
                "emergency_type": "tow",
                "location": {"lat": 55.7558, "lon": 37.6176},
                "description": "Broken down",
                "priority": "high"
            }
        elif '/roadside/settings' in path:
            test_data = {"emergency_enabled": True, "auto_call": True}

        # Analytics
        elif '/analytics/export' in path:
            test_data = {"format": "json", "period": "month"}
        elif '/analytics/settings' in path:
            test_data = {"enabled": True, "retention_days": 90}

        # AI Categories
        elif '/ai/categories/allow' in path:
            test_data = {"category_name": "safe", "reason": "trusted"}
        elif '/ai/categories/block' in path:
            test_data = {"category_name": "malicious", "reason": "danger"}

        # System Management
        elif '/system/maintenance' in path:
            test_data = {"maintenance_type": "cleanup", "schedule": "weekly"}
        elif '/system/backup' in path:
            test_data = {"backup_type": "full", "include_logs": True}

        return test_data

    def run_sequential_testing(self):
        """Запуск последовательного тестирования всех 183 эндпоинтов"""

        print("=" * 80)
        print("🚀 ПОСЛЕДОВАТЕЛЬНОЕ ТЕСТИРОВАНИЕ ВСЕХ 183 ЭНДПОИНТОВ")
        print("=" * 80)
        print(f"Всего эндпоинтов для тестирования: {len(self.all_endpoints)}")
        print("Каждый тест запускается в чистой среде (перезапуск сервера)")
        print()

        successful_tests = 0
        total_response_time = 0
        sfm_integrated_count = 0

        try:
            for i, endpoint in enumerate(self.all_endpoints):
                self.current_test = i

                # Запускаем сервер для этого теста
                if not self.start_server():
                    print(f"❌ Не удалось запустить сервер для теста #{i+1}")
                    continue

                # Тестируем эндпоинт
                result = self.test_single_endpoint(endpoint)
                self.results.append(result)

                if result['status'] == 'SUCCESS':
                    successful_tests += 1
                if result['sfm_integration']:
                    sfm_integrated_count += 1

                total_response_time += result['response_time']

                # Останавливаем сервер
                self.stop_server()

                # Небольшая пауза между тестами
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n⚠️ Тестирование прервано пользователем")
        finally:
            self.stop_server()

        # Итоговый отчет
        self.generate_final_report(successful_tests, total_response_time, sfm_integrated_count)

    def generate_final_report(self, successful_tests, total_response_time, sfm_integrated_count):
        """Генерация итогового отчета"""

        total_tests = len(self.results)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        avg_response_time = total_response_time / total_tests if total_tests > 0 else 0

        print("\n" + "=" * 80)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ПОСЛЕДОВАТЕЛЬНОГО ТЕСТИРОВАНИЯ")
        print("=" * 80)

        print(f"✅ Успешных тестов: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"⚡ Среднее время ответа: {avg_response_time:.1f}ms")
        print(f"🔐 SFM интеграция: {sfm_integrated_count}/{total_tests}")
        print(f"🚀 Быстрые ответы (<200ms): {sum(1 for r in self.results if r['response_time'] < 200)}/{total_tests}")

        # Детальный анализ ошибок
        errors = [r for r in self.results if r['status'] != 'SUCCESS']
        if errors:
            print(f"\n❌ Детали ошибок ({len(errors)}):")
            for error in errors[:10]:  # Показываем первые 10 ошибок
                print(f"   • Тест #{error['test_number']}: {error['test_name']} - {error['error']}")
            if len(errors) > 10:
                print(f"   ... и еще {len(errors) - 10} ошибок")

        # Сохранение результатов
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"sequential_183_endpoints_test_results_{timestamp}.json"

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'sfm_integrated': sfm_integrated_count,
                'fast_responses': sum(1 for r in self.results if r['response_time'] < 200),
                'errors_count': len(errors),
                'results': self.results
            }, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Подробные результаты сохранены в: {results_file}")

        # Рекомендации
        print("\n🎯 РЕКОМЕНДАЦИИ:")
        if success_rate >= 95:
            print("✅ СИСТЕМА ГОТОВА К ПРОДАКШЕНУ!")
            print("   • Высокая надежность и производительность")
            print("   • Хорошая SFM интеграция")
        elif success_rate >= 80:
            print("⚠️ СИСТЕМА ТРЕБУЕТ ДОРАБОТКИ")
            print("   • Проверьте проблемные эндпоинты")
            print("   • Улучшите SFM интеграцию")
        else:
            print("❌ СИСТЕМА НУЖДАЕТСЯ В СЕРЬЕЗНОЙ ДОРАБОТКЕ")
            print("   • Большое количество ошибок")
            print("   • Проверьте базовую функциональность")

        return success_rate >= 95

def main():
    print("🔍 НАЧИНАЕМ ПОСЛЕДОВАТЕЛЬНОЕ ТЕСТИРОВАНИЕ ВСЕХ 183 ЭНДПОИНТОВ")
    print("Каждый эндпоинт тестируется в отдельной сессии сервера")
    print("Это займет время, но даст максимально точные результаты")
    print()

    tester = SequentialEndpointTester()

    # Проверяем наличие файла
    if not os.path.exists('api_gateway_complete.py'):
        print("❌ Файл api_gateway_complete.py не найден!")
        return False

    # Запускаем тестирование
    success = tester.run_sequential_testing()

    if success:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! ГОТОВ К ПРОДАКШЕНУ!")
        return True
    else:
        print("\n⚠️ ТРЕБУЕТСЯ ДОРАБОТКА ПЕРЕД ПРОДАКШЕНОМ!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)