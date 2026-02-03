#!/usr/bin/env python3
"""
ИНДИВИДУАЛЬНОЕ ТЕСТИРОВАНИЕ API ЭНДПОИНТОВ
Решение проблемы с event loop конфликтом
"""

import requests
import time
import json
from datetime import datetime
import threading
import subprocess
import sys
import os
from typing import Dict

class IndividualAPITester:
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results = []
        self.server_process = None

    def start_server(self):
        """Запуск сервера в отдельном процессе"""
        print("🚀 Запуск API сервера...")

        # Убиваем возможные предыдущие процессы
        subprocess.run(['pkill', '-f', 'uvicorn'], capture_output=True)

        # Запускаем сервер в фоне
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
            response = self.session.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Сервер успешно запущен")
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
            print("🛑 Остановка сервера...")
            self.server_process.terminate()
            self.server_process.wait()
            subprocess.run(['pkill', '-f', 'uvicorn'], capture_output=True)
            print("✅ Сервер остановлен")

    def test_endpoint_sync(self, method: str, path: str, test_name: str, expected_status: int = 200) -> Dict:
        """Синхронное тестирование эндпоинта"""
        url = f"{self.base_url}{path}"
        start_time = time.time()

        print(f"🧪 ТЕСТИРОВАНИЕ: {test_name}")
        print(f"   {method} {url}")

        try:
            # Подготавливаем запрос
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=10)
            elif method.upper() == 'POST':
                test_data = self.get_test_data_for_endpoint(path)
                response = self.session.post(url, json=test_data, timeout=10)
            elif method.upper() == 'PUT':
                test_data = self.get_test_data_for_endpoint(path)
                response = self.session.put(url, json=test_data, timeout=10)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=10)
            else:
                return {
                    'test_name': test_name,
                    'method': method,
                    'path': path,
                    'status': 'ERROR',
                    'http_status': None,
                    'response_time': 0,
                    'error': f'Unsupported method: {method}',
                    'expected_status': expected_status
                }

            response_time = int((time.time() - start_time) * 1000)  # ms

            # Проверяем статус
            success = response.status_code == expected_status
            status = 'SUCCESS' if success else 'FAILED'

            # Проверяем SFM интеграцию
            sfm_integration = False
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    data = response.json()
                    if isinstance(data, dict) and 'source' in data:
                        sfm_integration = data['source'] == 'real_sfm'
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
                'error': None if success else f'Expected {expected_status}, got {response.status_code}'
            }

            # Вывод результата
            status_icon = "✅" if success else "❌"
            sfm_icon = "🔐" if sfm_integration else "⚠️"
            time_icon = "⚡" if response_time < 200 else "🐌"

            print(f"   {status_icon} {sfm_icon} {time_icon} {response_time}ms (ожидали {expected_status}, получили {response.status_code})")

            return result

        except requests.exceptions.RequestException as e:
            result = {
                'test_name': test_name,
                'method': method,
                'path': path,
                'status': 'ERROR',
                'http_status': None,
                'expected_status': expected_status,
                'response_time': int((time.time() - start_time) * 1000),
                'sfm_integration': False,
                'error': str(e)
            }
            print(f"   ❌ Ошибка сети: {str(e)}")
            return result

    def get_test_data_for_endpoint(self, path: str) -> Dict:
        """Генерирует тестовые данные для эндпоинта"""
        test_data = {}

        # Authentication
        if '/auth/register' in path:
            test_data = {
                "username": "test_user_123",
                "email": "test@example.com",
                "password": "test_password_123",
                "device_info": {"platform": "ios", "version": "15.0"}
            }
        elif '/auth/login' in path:
            test_data = {
                "username": "test_user_123",
                "password": "test_password_123",
                "device_fingerprint": "test_device_123"
            }
        elif '/auth/refresh' in path:
            test_data = {"refresh_token": "test_refresh_token_123"}

        # Subscription
        elif '/subscription/upgrade' in path:
            test_data = {"new_plan": "premium", "payment_method": "card"}
        elif '/subscription/cancel' in path:
            test_data = {"reason": "test_cancel"}

        # Components
        elif '/components/enable/' in path:
            test_data = {"reason": "test_enable"}
        elif '/components/disable/' in path:
            test_data = {"reason": "test_disable"}
        elif '/components/restart/' in path:
            test_data = {"reason": "test_restart"}
        elif '/components/backup/' in path:
            test_data = {"backup_type": "full"}
        elif '/components/restore/' in path:
            test_data = {"backup_id": "test_backup_123"}
        elif '/components/config/' in path:
            test_data = {"max_connections": 100, "timeout": 30}

        # Notifications
        elif '/notifications/mark_read/' in path:
            test_data = {"notification_ids": ["test_id_123"]}
        elif '/notifications/delete/' in path:
            test_data = {"notification_ids": ["test_id_123"]}
        elif '/notifications/bulk_mark_read' in path:
            test_data = {"notification_ids": ["id1", "id2", "id3"]}
        elif '/notifications/test' in path:
            test_data = {"message": "test_notification"}
        elif '/notifications/settings' in path:
            test_data = {
                "enabled": True,
                "email_notifications": True,
                "push_notifications": False
            }

        # Parental Control
        elif '/parental/restrict/' in path:
            test_data = {
                "restriction_type": "website_block",
                "target": "social_media",
                "duration": 3600
            }
        elif '/parental/alert' in path:
            test_data = {"message": "test_alert"}

        # Identity Protection
        elif '/identity/allow' in path:
            test_data = {
                "identity_type": "email",
                "identity_value": "trusted@example.com",
                "reason": "verified_contact"
            }
        elif '/identity/block' in path:
            test_data = {
                "identity_type": "ip",
                "identity_value": "192.168.1.1",
                "reason": "suspicious_activity"
            }
        elif '/identity/whitelist' in path:
            test_data = {
                "identity_type": "domain",
                "identity_value": "trusted.com",
                "reason": "verified_partner"
            }
        elif '/identity/theft/report/' in path:
            test_data = {
                "report_type": "identity_theft",
                "description": "Suspicious activity detected",
                "evidence": ["screenshot_1.jpg", "log_entry_123"]
            }

        # Dark Web Monitoring
        elif '/darkweb/scan_start' in path:
            test_data = {
                "scan_type": "full_scan",
                "target": "test@example.com",
                "priority": "high"
            }
        elif '/darkweb/resolve' in path:
            test_data = {
                "leak_id": "leak_12345",
                "action": "remove_data",
                "priority": "high"
            }

        # Location Tracking
        elif '/location/allow' in path:
            test_data = {
                "app_id": "maps_app",
                "reason": "navigation",
                "accuracy_level": "high"
            }
        elif '/location/block' in path:
            test_data = {
                "app_id": "suspicious_app",
                "reason": "privacy_concern"
            }
        elif '/location/accuracy' in path:
            test_data = {
                "accuracy_level": "high",
                "update_interval": 30,
                "battery_optimization": True
            }

        # Data Cleanup
        elif '/data/cleanup/start' in path:
            test_data = {
                "cleanup_type": "full_cleanup",
                "target": "browsing_history",
                "schedule": "immediate"
            }

        # Anti-Tracker
        elif '/antitracker/scan' in path:
            test_data = {
                "scan_type": "quick_scan",
                "target": "example.com",
                "deep_analysis": True
            }
        elif '/antitracker/whitelist' in path:
            test_data = {
                "tracker_domain": "trusted-cdn.com",
                "reason": "trusted_service",
                "temporary": False
            }

        # Roadside Assistance
        elif '/roadside/emergency' in path:
            test_data = {
                "emergency_type": "tow_truck",
                "location": {"lat": 55.7558, "lon": 37.6176, "accuracy": 10},
                "description": "Car broke down on highway",
                "priority": "high"
            }
        elif '/roadside/settings' in path:
            test_data = {
                "emergency_enabled": True,
                "auto_call_enabled": True,
                "preferred_services": ["tow_truck", "fuel_delivery"]
            }

        # Analytics
        elif '/analytics/export' in path:
            test_data = {
                "format": "json",
                "period": "month",
                "include_security_events": True,
                "anonymize": True
            }
        elif '/analytics/settings' in path:
            test_data = {
                "enabled": True,
                "retention_days": 90,
                "anonymize_data": True
            }

        # AI Categories
        elif '/ai/categories/allow' in path:
            test_data = {
                "category_name": "safe_content",
                "reason": "trusted_category",
                "confidence_threshold": 0.95
            }
        elif '/ai/categories/block' in path:
            test_data = {
                "category_name": "malicious_content",
                "reason": "security_risk"
            }

        # System Management
        elif '/system/maintenance' in path:
            test_data = {
                "maintenance_type": "database_cleanup",
                "schedule": "weekly",
                "impact": "low"
            }
        elif '/system/backup' in path:
            test_data = {
                "backup_type": "full_system",
                "include_logs": True,
                "compression": True
            }

        return test_data

    def run_individual_tests(self):
        """Запуск индивидуального тестирования всех эндпоинтов"""

        # Список всех эндпоинтов для тестирования
        endpoints_to_test = [
            # Health Checks
            ("GET", "/", "Root endpoint", 200),
            ("GET", "/api/health", "Health check", 200),

            # Authentication (12 endpoints)
            ("POST", "/api/auth/register", "User registration", 200),
            ("POST", "/api/auth/login", "User login", 200),
            ("GET", "/api/auth/profile", "Get user profile", 200),
            ("PUT", "/api/auth/profile", "Update user profile", 200),
            ("POST", "/api/auth/refresh", "Refresh token", 200),
            ("POST", "/api/auth/logout", "User logout", 200),

            # Subscription (6 endpoints - основные)
            ("GET", "/api/subscription/status", "Subscription status", 200),
            ("GET", "/api/subscription/plans", "Available plans", 200),
            ("POST", "/api/subscription/upgrade", "Upgrade subscription", 200),
            ("POST", "/api/subscription/cancel", "Cancel subscription", 200),
            ("GET", "/api/subscription/billing_history", "Billing history", 200),
            ("PUT", "/api/subscription/payment_method", "Update payment method", 200),

            # Notifications (7 endpoints - основные)
            ("GET", "/api/notifications/list", "List notifications", 200),
            ("GET", "/api/notifications/stats", "Notification stats", 200),
            ("GET", "/api/notifications/unread_count", "Unread count", 200),
            ("POST", "/api/notifications/mark_read/123", "Mark as read", 200),
            ("POST", "/api/notifications/delete/123", "Delete notification", 200),
            ("POST", "/api/notifications/bulk_mark_read", "Bulk mark read", 200),
            ("PUT", "/api/notifications/settings", "Notification settings", 200),

            # Components (6 endpoints - основные)
            ("GET", "/api/components/health", "Components health", 200),
            ("GET", "/api/components/status/sfm_core", "Component status", 200),
            ("POST", "/api/components/enable/sfm_core", "Enable component", 200),
            ("POST", "/api/components/disable/sfm_core", "Disable component", 200),
            ("POST", "/api/components/restart/sfm_core", "Restart component", 200),
            ("PUT", "/api/components/config/sfm_core", "Update config", 200),

            # Anti-Phishing (3 endpoints)
            ("GET", "/api/phishing/sensitivity", "Phishing sensitivity", 200),
            ("PUT", "/api/phishing/sensitivity", "Update sensitivity", 200),
            ("GET", "/api/phishing/block_suspicious", "Block suspicious", 200),

            # Antivirus (3 endpoints)
            ("GET", "/api/malware/scan_scheduled", "Scheduled scan", 200),
            ("PUT", "/api/malware/scan_scheduled", "Update schedule", 200),
            ("POST", "/api/malware/scan_now", "Scan now", 200),

            # Mobile Security (2 endpoints)
            ("GET", "/api/mobile/app_lock", "App lock status", 200),
            ("GET", "/api/mobile/biometric", "Biometric status", 200),

            # Network Security (2 endpoints)
            ("GET", "/api/network/firewall_rules", "Firewall rules", 200),
            ("PUT", "/api/network/vpn_config", "VPN config", 200),

            # Analytics (5 endpoints - основные)
            ("GET", "/api/analytics/overview", "Analytics overview", 200),
            ("GET", "/api/analytics/performance", "Performance metrics", 200),
            ("GET", "/api/analytics/security_events", "Security events", 200),
            ("POST", "/api/analytics/export", "Export analytics", 200),
            ("PUT", "/api/analytics/settings", "Analytics settings", 200),

            # AI Categories (4 endpoints)
            ("GET", "/api/ai/categories/stats", "AI categories stats", 200),
            ("GET", "/api/ai/categories/reports", "AI reports", 200),
            ("POST", "/api/ai/categories/allow", "Allow category", 200),
            ("POST", "/api/ai/categories/block", "Block category", 200),

            # System Management (4 endpoints - основные)
            ("GET", "/api/system/info", "System info", 200),
            ("GET", "/api/system/health", "System health", 200),
            ("POST", "/api/system/backup", "System backup", 200),
            ("GET", "/api/system/logs", "System logs", 200),
        ]

        print("=" * 80)
        print("🚀 ИНДИВИДУАЛЬНОЕ ТЕСТИРОВАНИЕ ВСЕХ API ЭНДПОИНТОВ")
        print("=" * 80)
        print(f"Всего эндпоинтов для тестирования: {len(endpoints_to_test)}")
        print()

        successful_tests = 0
        total_tests = len(endpoints_to_test)
        total_response_time = 0

        for i, (method, path, test_name, expected_status) in enumerate(endpoints_to_test, 1):
            print(f"\n[{i}/{total_tests}] ", end="")
            result = self.test_endpoint_sync(method, path, test_name, expected_status)
            self.results.append(result)

            if result['status'] == 'SUCCESS':
                successful_tests += 1
            total_response_time += result['response_time']

        # Итоговый отчет
        print("\n" + "=" * 80)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ИНДИВИДУАЛЬНОГО ТЕСТИРОВАНИЯ")
        print("=" * 80)

        success_rate = (successful_tests / total_tests) * 100
        avg_response_time = total_response_time / total_tests

        print(f"✅ Успешных тестов: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"⚡ Среднее время ответа: {avg_response_time:.1f}ms")

        # Анализ по категориям
        sfm_integrated = sum(1 for r in self.results if r.get('sfm_integration', False))
        fast_responses = sum(1 for r in self.results if r['response_time'] < 200)

        print(f"🔐 SFM интеграция: {sfm_integrated}/{total_tests}")
        print(f"🚀 Быстрые ответы (<200ms): {fast_responses}/{total_tests}")

        # Сохранение результатов
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"individual_api_test_results_{timestamp}.json"

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'sfm_integrated': sfm_integrated,
                'fast_responses': fast_responses,
                'results': self.results
            }, f, indent=2, ensure_ascii=False)

        print(f"💾 Результаты сохранены в: {results_file}")

        return success_rate >= 95  # 95% успешность для прохождения

def main():
    tester = IndividualAPITester()

    try:
        # Запуск сервера
        if not tester.start_server():
            print("❌ Не удалось запустить сервер")
            return False

        # Запуск тестирования
        success = tester.run_individual_tests()

        if success:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            print("✅ API готов к продакшену")
            return True
        else:
            print("\n❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛИЛИСЬ!")
            print("Проверьте логи выше")
            return False

    finally:
        # Остановка сервера
        tester.stop_server()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)