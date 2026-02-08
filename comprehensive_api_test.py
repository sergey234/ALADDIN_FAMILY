#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексное тестирование всех API эндпоинтов ALADDIN системы
На основе документации ALADDIN_COMPLETE_SYSTEM_ARCHITECTURE_AND_API_REFERENCE.md
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple
import statistics

class AladdinAPITester:
    def __init__(self, base_url: str = "http://149.154.65.180:8002"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
        self.results = {}

    def test_endpoint(self, method: str, endpoint: str, data: dict = None, expected_status: int = 200) -> Dict:
        """Тестирование одного эндпоинта"""
        url = f"{self.base_url}/{endpoint}"
        start_time = time.time()

        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers={'Content-Type': 'application/json'})
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers={'Content-Type': 'application/json'})
            elif method.upper() == "DELETE":
                response = self.session.delete(url, json=data, headers={'Content-Type': 'application/json'})
            else:
                return {"error": f"Unsupported method: {method}"}

            response_time = (time.time() - start_time) * 1000  # в миллисекундах

            result = {
                "method": method,
                "endpoint": endpoint,
                "http_status": response.status_code,
                "response_time_ms": round(response_time, 2),
                "expected_status": expected_status,
                "status_match": response.status_code == expected_status
            }

            # Анализ JSON ответа
            try:
                json_data = response.json()
                result["json_valid"] = True
                result["response_size_bytes"] = len(response.content)

                # Проверка SFM интеграции
                if "source" in json_data:
                    result["sfm_source"] = json_data["source"]
                    result["sfm_valid"] = json_data["source"] == "real_sfm"
                else:
                    result["sfm_source"] = None
                    result["sfm_valid"] = False

                if "function" in json_data:
                    result["sfm_function"] = json_data["function"]
                if "timestamp" in json_data:
                    result["has_timestamp"] = True
                else:
                    result["has_timestamp"] = False

            except json.JSONDecodeError:
                result["json_valid"] = False
                result["error"] = "Invalid JSON response"
                result["response_preview"] = response.text[:200] + "..." if len(response.text) > 200 else response.text

            return result

        except requests.RequestException as e:
            return {
                "method": method,
                "endpoint": endpoint,
                "error": str(e),
                "response_time_ms": (time.time() - start_time) * 1000
            }

    def run_full_test(self) -> Dict:
        """Запуск полного тестирования всех эндпоинтов"""

        # Эндпоинты из документации
        endpoints = [
            # Authentication (1-12)
            ("POST", "api/auth/register", {"username": "test", "email": "test@example.com", "password": "test123", "device_info": {"platform": "ios", "version": "15.0", "model": "iPhone14"}}),
            ("POST", "api/auth/login", {"username": "test", "password": "test123", "device_fingerprint": "test_device"}),
            ("POST", "api/auth/logout", {}),
            ("POST", "api/auth/refresh", {"refresh_token": "test_token"}),
            ("GET", "api/auth/profile", None),
            ("PUT", "api/auth/profile", {"email": "new@example.com"}),
            ("POST", "api/auth/verify_email", {}),
            ("POST", "api/auth/forgot_password", {}),
            ("POST", "api/auth/reset_password", {}),
            ("POST", "api/auth/change_password", {}),
            ("GET", "api/auth/sessions", None),
            ("DELETE", "api/auth/sessions/123", None),

            # Subscription (13-24)
            ("GET", "api/subscription/status", None),
            ("GET", "api/subscription/plans", None),
            ("GET", "api/subscription/billing_history", None),
            ("POST", "api/subscription/upgrade", {}),
            ("POST", "api/subscription/cancel", {}),
            ("PUT", "api/subscription/payment_method", {}),
            ("POST", "api/subscription/reactivate", {}),
            ("GET", "api/subscription/usage", None),
            ("GET", "api/subscription/limits", None),
            ("POST", "api/subscription/pause", {}),
            ("POST", "api/subscription/resume", {}),
            ("GET", "api/subscription/invoices/123", None),

            # Notifications (25-40)
            ("GET", "api/notifications/list", None),
            ("GET", "api/notifications/stats", None),
            ("GET", "api/notifications/unread_count", None),
            ("POST", "api/notifications/mark_read/123", {}),
            ("POST", "api/notifications/delete/123", {}),
            ("POST", "api/notifications/bulk_mark_read", {}),
            ("POST", "api/notifications/test", {}),
        ]

        # Добавляем оставшиеся категории...
        categories = [
            ("Parental Control", 13, ["GET", "POST"]),
            ("Identity Protection", 26, ["GET", "POST", "PUT"]),
            ("Dark Web", 7, ["GET", "POST"]),
            ("Location", 15, ["GET", "POST", "PUT"]),
            ("Data Cleanup", 9, ["GET", "POST"]),
            ("Anti-Tracker", 27, ["GET", "POST", "PUT"]),
            ("Roadside", 9, ["GET", "POST"]),
            ("System", 17, ["GET", "POST", "PUT"]),
            ("Analytics", 17, ["GET", "POST"]),
            ("AI", 12, ["GET", "POST"]),
            ("Components", 20, ["GET", "POST", "PUT"]),
            ("Anti-Phishing", 8, ["GET", "POST"]),
            ("Antivirus", 8, ["GET", "POST"]),
            ("Mobile Security", 5, ["GET", "POST"]),
            ("Health Checks", 2, ["GET"]),
            ("Settings", 6, ["PUT"]),
            ("Additional APIs", 2, ["POST"])
        ]

        print("🚀 НАЧИНАЮ КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ ALADDIN API")
        print("=" * 80)

        all_results = []
        start_total = time.time()

        # Тестируем основные эндпоинты
        for method, endpoint, data in endpoints:
            print(f"🧪 Тестирую {method} {endpoint}")
            result = self.test_endpoint(method, endpoint, data)
            all_results.append(result)

            status_icon = "✅" if result.get("status_match", False) else "❌"
            sfm_icon = "🔒" if result.get("sfm_valid", False) else "⚠️"
            time_str = f"{result.get('response_time_ms', 0):.1f}ms"
            print(f"   {status_icon} {sfm_icon} {time_str}")

        # Статистика
        total_time = time.time() - start_total
        successful_requests = [r for r in all_results if r.get("status_match", False)]
        sfm_valid_requests = [r for r in all_results if r.get("sfm_valid", False)]
        response_times = [r.get("response_time_ms", 0) for r in all_results if "response_time_ms" in r]

        print("\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("=" * 80)
        print(f"Всего эндпоинтов протестировано: {len(all_results)}")
        print(f"HTTP 200 успехов: {len(successful_requests)}/{len(all_results)} ({len(successful_requests)/len(all_results)*100:.1f}%)")
        print(f"SFM интеграция: {len(sfm_valid_requests)}/{len(all_results)} ({len(sfm_valid_requests)/len(all_results)*100:.1f}%)")

        if response_times:
            print(f"Среднее время ответа: {statistics.mean(response_times):.2f}ms")
            print(f"95-й перцентиль: {statistics.quantiles(response_times, n=20)[18]:.2f}ms")  # 95-й перцентиль
            print(f"Максимальное время: {max(response_times):.2f}ms")
            print(f"Минимальное время: {min(response_times):.2f}ms")

        print(f"Общее время тестирования: {total_time:.2f} сек")

        # Проверка на соответствие документации
        print("\n📋 СРАВНЕНИЕ С ДОКУМЕНТАЦИЕЙ")
        print("-" * 40)
        print(f"Документация: 187 эндпоинтов, 100% HTTP 200, <0.015 сек среднее")
        print(f"Реальность: {len(all_results)} эндпоинтов, {len(successful_requests)/len(all_results)*100:.1f}% HTTP 200")

        if response_times:
            avg_time_sec = statistics.mean(response_times) / 1000
            print(f"Среднее время (сек): {avg_time_sec:.4f}")
        return {
            "total_endpoints_tested": len(all_results),
            "successful_requests": len(successful_requests),
            "sfm_valid_requests": len(sfm_valid_requests),
            "average_response_time_ms": statistics.mean(response_times) if response_times else 0,
            "p95_response_time_ms": statistics.quantiles(response_times, n=20)[18] if response_times else 0,
            "total_test_time_sec": total_time,
            "all_results": all_results
        }

if __name__ == "__main__":
    tester = AladdinAPITester()
    results = tester.run_full_test()

    # Сохранение результатов
    with open("api_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Результаты сохранены в api_test_results.json")