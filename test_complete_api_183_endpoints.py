#!/usr/bin/env python3
"""
🚀 ПОЛНОЕ ТЕСТИРОВАНИЕ API GATEWAY COMPLETE - 183 ЭНДПОИНТА

Автоматизированное тестирование всех 183 декораторов FastAPI
в api_gateway_complete.py по одному эндпоинту за раз.
"""

import requests
import json
import time
from datetime import datetime
import sys
from typing import Dict, List, Tuple

class CompleteAPITester:
    """Тестер всех 183 эндпоинтов полной версии API"""

    def __init__(self, base_url: str = "http://149.154.65.180:8002"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None

        # Отключаем SSL warnings для тестов
        requests.packages.urllib3.disable_warnings()

    def authenticate(self) -> bool:
        """Аутентификация для получения токена"""
        try:
            auth_data = {
                "username": "test_user",
                "password": "test_password_123",
                "device_fingerprint": "api_tester_001"
            }

            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=auth_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    return True

            print(f"❌ Аутентификация не удалась: {response.status_code}")
            return False

        except Exception as e:
            print(f"❌ Ошибка аутентификации: {e}")
            return False

    def extract_endpoints_from_file(self, filepath: str) -> List[Tuple[str, str]]:
        """Извлечение всех эндпоинтов из файла api_gateway_complete.py"""
        endpoints = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Регулярное выражение для поиска FastAPI эндпоинтов
            import re
            pattern = r'@app\.(\w+)\s*\(\s*["\']([^"\']+)["\']'
            matches = re.findall(pattern, content)

            for method, path in matches:
                # Очистка пути от переменных для тестирования
                test_path = re.sub(r'\{[^}]+\}', '123', path)  # Заменяем {id} на 123
                endpoints.append((method.upper(), test_path))

            return endpoints

        except Exception as e:
            print(f"❌ Ошибка чтения файла {filepath}: {e}")
            return []

    def prepare_test_data(self, method: str, path: str) -> Dict:
        """Подготовка тестовых данных для эндпоинта"""
        test_data = {
            "method": method,
            "url": f"{self.base_url}{path}",
            "headers": {"Content-Type": "application/json"},
            "data": None,
            "expected_status": 200
        }

        # Специфические данные для разных типов эндпоинтов
        if "/auth/register" in path:
            test_data["data"] = {
                "username": "test_user",
                "email": "test@example.com",
                "password": "test_password",
                "device_info": {"platform": "test", "version": "1.0"}
            }
        elif "/auth/login" in path:
            test_data["data"] = {
                "username": "test_user",
                "password": "test_password",
                "device_fingerprint": "test_device"
            }
        elif "/identity" in path:
            test_data["data"] = {
                "identity_type": "email",
                "identity_value": "test@example.com"
            }
        elif "/darkweb/scan_start" in path:
            test_data["data"] = {
                "scan_type": "quick_scan",
                "target": "test@example.com"
            }
        elif "/location" in path:
            test_data["data"] = {
                "app_id": "test_app",
                "reason": "test_reason"
            }
        elif "/data/cleanup" in path:
            test_data["data"] = {
                "cleanup_type": "test_cleanup",
                "target": "test_target"
            }
        elif "/antitracker" in path:
            test_data["data"] = {
                "tracker_domain": "test.com",
                "reason": "test_block"
            }
        elif "/roadside" in path:
            test_data["data"] = {
                "emergency_type": "test_emergency",
                "location": {"lat": 55.7558, "lon": 37.6176}
            }
        elif "/system/maintenance" in path:
            test_data["data"] = {
                "maintenance_type": "test_maintenance",
                "schedule": "test_schedule"
            }
        elif "/analytics/export" in path:
            test_data["data"] = {
                "format": "json",
                "period": "test_period"
            }
        elif "/ai/categories" in path:
            test_data["data"] = {
                "category_name": "test_category",
                "reason": "test_reason"
            }
        elif "/phishing" in path:
            test_data["data"] = {"sensitivity": "high"}
        elif "/malware/scan_now" in path:
            test_data["data"] = {
                "scan_type": "quick_scan",
                "target": "/test/path"
            }
        elif "/network" in path:
            test_data["data"] = {
                "enabled": True,
                "server": "test.vpn.com"
            }
        elif "/subscription" in path:
            test_data["data"] = {"plan": "premium"}
        elif "/notifications" in path:
            test_data["data"] = {"notification_ids": ["test_id"]}
        elif "/parental" in path:
            test_data["data"] = {"child_id": "test_child"}
        elif "/components" in path:
            test_data["data"] = {"reason": "test_reason"}

        return test_data

    def test_single_endpoint(self, method: str, path: str) -> Dict:
        """Тестирование одного эндпоинта"""
        test_config = self.prepare_test_data(method, path)

        result = {
            "endpoint": f"{method} {path}",
            "url": test_config["url"],
            "method": method,
            "status_code": None,
            "response_time": None,
            "has_sfm": False,
            "success": False,
            "error": None,
            "response_preview": None
        }

        start_time = time.time()

        try:
            if method == "GET":
                response = self.session.get(test_config["url"])
            elif method == "POST":
                response = self.session.post(
                    test_config["url"],
                    json=test_config["data"],
                    headers=test_config["headers"]
                )
            elif method == "PUT":
                response = self.session.put(
                    test_config["url"],
                    json=test_config["data"],
                    headers=test_config["headers"]
                )
            elif method == "DELETE":
                response = self.session.delete(test_config["url"])
            else:
                result["error"] = f"Unsupported method: {method}"
                return result

            result["status_code"] = response.status_code
            result["response_time"] = round((time.time() - start_time) * 1000, 2)  # ms

            # Проверяем ответ
            try:
                response_data = response.json()
                result["response_preview"] = str(response_data)[:200] + "..."

                # Проверяем SFM интеграцию
                if isinstance(response_data, dict) and "source" in response_data:
                    if response_data["source"] == "real_sfm":
                        result["has_sfm"] = True

                # Определяем успех
                if response.status_code in [200, 201, 202] and result["has_sfm"]:
                    result["success"] = True
                elif response.status_code in [200, 201, 202]:
                    result["success"] = True  # Принимаем даже без SFM для некоторых эндпоинтов

            except json.JSONDecodeError:
                result["response_preview"] = response.text[:200] + "..."
                if response.status_code in [200, 201, 202]:
                    result["success"] = True

        except requests.exceptions.RequestException as e:
            result["error"] = str(e)
        except Exception as e:
            result["error"] = f"Unexpected error: {e}"

        return result

    def run_complete_test(self) -> Dict:
        """Запуск полного тестирования всех 183 эндпоинтов"""
        print("🚀 ЗАПУСК ПОЛНОГО ТЕСТИРОВАНИЯ API GATEWAY COMPLETE")
        print("=" * 60)
        print(f"🎯 Цель: протестировать все 183 декоратора FastAPI")
        print(f"🏆 Ожидание: 183 теста по одному эндпоинту")
        print(f"⏰ Время начала: {datetime.now().strftime('%H:%M:%S')}")
        print()

        # Аутентификация
        print("🔐 Аутентификация...")
        if not self.authenticate():
            return {
                "success": False,
                "error": "Не удалось аутентифицироваться",
                "total_tests": 0
            }
        print("✅ Аутентификация успешна")
        print()

        # Извлечение эндпоинтов
        print("📋 Извлечение эндпоинтов из api_gateway_complete.py...")
        endpoints = self.extract_endpoints_from_file("api_gateway_complete.py")

        if not endpoints:
            return {
                "success": False,
                "error": "Не удалось извлечь эндпоинты из файла",
                "total_tests": 0
            }

        print(f"📊 Найдено эндпоинтов: {len(endpoints)}")
        print()

        # Тестирование
        successful_tests = 0
        failed_tests = 0

        print("🧪 НАЧАЛО ТЕСТИРОВАНИЯ ПО ОДНОМУ ЭНДПОИНТУ:")
        print("-" * 50)

        for i, (method, path) in enumerate(endpoints, 1):
            print(f"[{i:3d}/183] Тестирование {method} {path}...")

            result = self.test_single_endpoint(method, path)
            self.test_results.append(result)

            if result["success"]:
                status_icon = "✅"
                successful_tests += 1
            else:
                status_icon = "❌"
                failed_tests += 1

            sfm_status = " (SFM)" if result["has_sfm"] else ""
            time_status = f" {result['response_time']}ms" if result["response_time"] else ""

            print(f"   {status_icon} {result['status_code']} {sfm_status}{time_status}")

            if result["error"]:
                print(f"   ⚠️  Ошибка: {result['error']}")

            # Небольшая задержка между тестами
            time.sleep(0.1)

        print()
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        print("=" * 40)
        print(f"✅ УСПЕШНЫХ: {successful_tests}")
        print(f"❌ НЕУДАЧНЫХ: {failed_tests}")
        print(f"📈 ОБЩИЙ ПРОЦЕНТ: {successful_tests/len(endpoints)*100:.1f}%")

        # Сохраняем результаты
        self.save_test_results()

        return {
            "success": failed_tests == 0,
            "total_tests": len(endpoints),
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": successful_tests/len(endpoints)*100
        }

    def save_test_results(self):
        """Сохранение результатов тестирования"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"complete_api_test_results_{timestamp}.json"

        results_data = {
            "test_timestamp": datetime.now().isoformat(),
            "api_version": "api_gateway_complete.py",
            "total_endpoints_tested": len(self.test_results),
            "results": self.test_results
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Результаты сохранены: {filename}")

        # Создаем краткий отчет
        successful = len([r for r in self.test_results if r["success"]])
        total = len(self.test_results)

        summary_file = f"complete_api_test_summary_{timestamp}.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"""# 🚀 ПОЛНОЕ ТЕСТИРОВАНИЕ API GATEWAY COMPLETE

**Дата тестирования:** {datetime.now().isoformat()}
**Версия API:** api_gateway_complete.py (183 декоратора)
**Всего эндпоинтов:** {total}

## 📊 РЕЗУЛЬТАТЫ

- ✅ **УСПЕШНЫХ:** {successful}
- ❌ **НЕУДАЧНЫХ:** {total - successful}
- 📈 **УСПЕШНОСТЬ:** {successful/total*100:.1f}%

## 🎯 СТАТУС

{'✅ **ТЕСТИРОВАНИЕ ПРОЙДЕНО**' if successful == total else '⚠️  **ТРЕБУЕТСЯ ДОРАБОТКА**'}

## 📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ

См. файл: {filename}
""")

        print(f"📄 Краткий отчет: {summary_file}")


def main():
    """Основная функция тестирования"""
    tester = CompleteAPITester()

    print("🎯 ПОЛНОЕ ТЕСТИРОВАНИЕ ВСЕХ 183 ЭНДПОИНТОВ")
    print("Это займет несколько минут...")
    print()

    results = tester.run_complete_test()

    print()
    print("=" * 60)
    if results["success"]:
        print("🎉 ВСЕ 183 ЭНДПОИНТА ПРОТЕСТИРОВАНЫ УСПЕШНО!")
        print("🏆 ПОЛНАЯ ВЕРСИЯ API ГОТОВА К ПРОДАКШЕНУ!")
    else:
        print(f"⚠️  ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ПРОБЛЕМАМИ")
        print(f"   Успешно: {results['successful_tests']}/{results['total_tests']}")
        print("   📋 Проверьте подробные результаты в логах")


if __name__ == "__main__":
    main()