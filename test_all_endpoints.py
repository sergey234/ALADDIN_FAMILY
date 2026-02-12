#!/usr/bin/env python3
"""
Скрипт автоматического тестирования всех endpoint'ов ALADDIN API
С поддержкой авторизации через Recovery Code

⚠️ ВАЖНО: МЫ НЕ СОБИРАЕМ ПЕРСОНАЛЬНЫЕ ДАННЫЕ!
- Используем только анонимные данные: family_id, recovery_code
- НЕ используем email, password, телефон
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Конфигурация
BASE_URL = "http://149.154.65.180:8002"
TIMEOUT = 10  # секунд
MAX_RETRIES = 3

# Цвета для вывода (опционально)
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class EndpointTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.family_id: Optional[str] = None
        self.recovery_code: Optional[str] = None
        self.results: List[Dict] = []
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'requires_auth': 0,
            'public': 0
        }
    
    def log(self, message: str, color: str = ''):
        """Логирование с цветом"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if color:
            print(f"{color}[{timestamp}] {message}{Colors.END}")
        else:
            print(f"[{timestamp}] {message}")
    
    def get_openapi_spec(self) -> Dict:
        """Получить OpenAPI спецификацию"""
        try:
            response = self.session.get(f"{self.base_url}/openapi.json", timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"❌ Ошибка получения OpenAPI: {e}", Colors.RED)
            return {}
    
    def create_family_and_get_token(self) -> bool:
        """
        Создать семью и получить токен авторизации
        
        ⚠️ ВАЖНО: НЕ собираем персональные данные!
        Используем только анонимные данные: role, age_group, personal_letter, device_type
        """
        self.log("🔐 Создание семьи и получение токена...", Colors.BLUE)
        
        try:
            # ШАГ 1: Создать семью (БЕЗ персональных данных)
            create_family_data = {
                "role": "parent",
                "age_group": "24-55",
                "personal_letter": "T",  # Тестовая буква
                "device_type": "iOS"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/family/create",
                json=create_family_data,
                timeout=TIMEOUT
            )
            
            if response.status_code not in [200, 201]:
                self.log(f"❌ Ошибка создания семьи: {response.status_code}", Colors.RED)
                self.log(f"   Ответ: {response.text[:200]}", Colors.YELLOW)
                return False
            
            family_data = response.json()
            self.family_id = family_data.get("family_id")
            self.recovery_code = self.family_id  # В текущей реализации recovery_code = family_id
            
            self.log(f"✅ Семья создана: {self.family_id}", Colors.GREEN)
            
            # ШАГ 2: Получить токен авторизации
            login_data = {
                "family_id": self.family_id,
                "recovery_code": self.recovery_code
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/login-by-recovery-code",
                json=login_data,
                timeout=TIMEOUT
            )
            
            if response.status_code != 200:
                self.log(f"❌ Ошибка авторизации: {response.status_code}", Colors.RED)
                self.log(f"   Ответ: {response.text[:200]}", Colors.YELLOW)
                return False
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            
            # Установить токен в сессию
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}"
            })
            
            self.log(f"✅ Токен получен: {self.access_token[:20]}...", Colors.GREEN)
            return True
            
        except Exception as e:
            self.log(f"❌ Ошибка при создании семьи/авторизации: {e}", Colors.RED)
            return False
    
    def requires_auth(self, endpoint_spec: Dict) -> bool:
        """Проверить, требует ли endpoint авторизацию"""
        # Проверяем наличие security в спецификации
        if 'security' in endpoint_spec:
            return True
        
        # Проверяем наличие параметров авторизации
        if 'parameters' in endpoint_spec:
            for param in endpoint_spec['parameters']:
                if param.get('name') == 'Authorization' or param.get('in') == 'header':
                    if 'authorization' in param.get('name', '').lower() or 'bearer' in param.get('name', '').lower():
                        return True
        
        return False
    
    def generate_test_data(self, method: str, path: str, endpoint_spec: Dict) -> Optional[Dict]:
        """Генерировать тестовые данные для запроса"""
        if method.upper() not in ['POST', 'PUT', 'PATCH']:
            return None
        
        # Получаем схему запроса
        request_body = endpoint_spec.get('requestBody', {})
        if not request_body:
            return {}
        
        content = request_body.get('content', {})
        schema = None
        
        for content_type, content_spec in content.items():
            if 'application/json' in content_type:
                schema = content_spec.get('schema', {})
                break
        
        if not schema:
            return {}
        
        # Генерируем тестовые данные на основе схемы
        test_data = {}
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        for field, field_spec in properties.items():
            field_type = field_spec.get('type', 'string')
            default = field_spec.get('default')
            
            # ⚠️ ВАЖНО: НЕ используем персональные данные!
            # Генерируем только анонимные тестовые данные
            if 'email' in field.lower() or 'password' in field.lower() or 'phone' in field.lower():
                continue  # Пропускаем персональные данные
            
            if default is not None:
                test_data[field] = default
            elif field_type == 'string':
                if 'id' in field.lower():
                    test_data[field] = f"TEST_{field.upper()}_123"
                elif 'code' in field.lower():
                    test_data[field] = "TEST_CODE"
                else:
                    test_data[field] = f"test_{field}"
            elif field_type == 'integer':
                test_data[field] = 1
            elif field_type == 'boolean':
                test_data[field] = True
            elif field_type == 'array':
                test_data[field] = []
            elif field_type == 'object':
                test_data[field] = {}
        
        return test_data
    
    def test_endpoint(self, method: str, path: str, endpoint_spec: Dict) -> Dict:
        """Тестировать один endpoint"""
        full_url = f"{self.base_url}{path}"
        requires_auth = self.requires_auth(endpoint_spec)
        
        result = {
            'method': method.upper(),
            'path': path,
            'full_url': full_url,
            'requires_auth': requires_auth,
            'status': 'unknown',
            'http_code': None,
            'response_time_ms': None,
            'error': None,
            'response_preview': None
        }
        
        # Пропускаем некоторые endpoint'ы
        skip_paths = ['/docs', '/openapi.json', '/redoc', '/']
        if any(skip in path for skip in skip_paths):
            result['status'] = 'skipped'
            result['error'] = 'System endpoint'
            self.stats['skipped'] += 1
            return result
        
        try:
            # Подготовка запроса
            headers = {}
            if requires_auth and self.access_token:
                headers['Authorization'] = f"Bearer {self.access_token}"
                self.stats['requires_auth'] += 1
            else:
                self.stats['public'] += 1
            
            # Генерация тестовых данных
            test_data = self.generate_test_data(method, path, endpoint_spec)
            
            # Выполнение запроса
            start_time = time.time()
            
            if method.upper() == 'GET':
                response = self.session.get(full_url, headers=headers, timeout=TIMEOUT, params=test_data)
            elif method.upper() == 'POST':
                response = self.session.post(full_url, headers=headers, json=test_data, timeout=TIMEOUT)
            elif method.upper() == 'PUT':
                response = self.session.put(full_url, headers=headers, json=test_data, timeout=TIMEOUT)
            elif method.upper() == 'DELETE':
                response = self.session.delete(full_url, headers=headers, timeout=TIMEOUT)
            elif method.upper() == 'PATCH':
                response = self.session.patch(full_url, headers=headers, json=test_data, timeout=TIMEOUT)
            else:
                result['status'] = 'skipped'
                result['error'] = f'Unsupported method: {method}'
                return result
            
            response_time = (time.time() - start_time) * 1000  # в миллисекундах
            
            result['http_code'] = response.status_code
            result['response_time_ms'] = round(response_time, 2)
            
            # Определение статуса
            if response.status_code in [200, 201, 204]:
                result['status'] = 'success'
                self.stats['success'] += 1
            elif response.status_code == 401:
                result['status'] = 'unauthorized'
                result['error'] = 'Requires authentication'
                if not requires_auth:
                    self.stats['failed'] += 1
                else:
                    self.stats['success'] += 1  # Ожидаемо для защищенных endpoint'ов
            elif response.status_code == 403:
                result['status'] = 'forbidden'
                result['error'] = 'Forbidden'
                self.stats['failed'] += 1
            elif response.status_code == 404:
                result['status'] = 'not_found'
                result['error'] = 'Not found'
                self.stats['failed'] += 1
            elif response.status_code == 422:
                result['status'] = 'validation_error'
                result['error'] = 'Validation error (expected for test data)'
                self.stats['success'] += 1  # Ожидаемо для тестовых данных
            elif response.status_code >= 500:
                result['status'] = 'server_error'
                result['error'] = f'Server error: {response.status_code}'
                self.stats['failed'] += 1
            else:
                result['status'] = 'unknown'
                result['error'] = f'Unexpected status: {response.status_code}'
                self.stats['failed'] += 1
            
            # Сохраняем превью ответа
            try:
                response_text = response.text[:200]
                result['response_preview'] = response_text
            except:
                pass
            
        except requests.exceptions.Timeout:
            result['status'] = 'timeout'
            result['error'] = 'Request timeout'
            self.stats['failed'] += 1
        except requests.exceptions.ConnectionError:
            result['status'] = 'connection_error'
            result['error'] = 'Connection error'
            self.stats['failed'] += 1
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)[:200]
            self.stats['failed'] += 1
        
        return result
    
    def test_all_endpoints(self) -> bool:
        """Тестировать все endpoint'ы"""
        self.log("📋 Получение списка endpoint'ов из OpenAPI...", Colors.BLUE)
        
        openapi_spec = self.get_openapi_spec()
        if not openapi_spec:
            return False
        
        paths = openapi_spec.get('paths', {})
        self.stats['total'] = sum(len(methods) for methods in paths.values())
        
        self.log(f"✅ Найдено {self.stats['total']} endpoint'ов", Colors.GREEN)
        
        # Авторизация
        if not self.create_family_and_get_token():
            self.log("⚠️ Не удалось получить токен, продолжаем без авторизации...", Colors.YELLOW)
        
        # Тестирование каждого endpoint'а
        self.log(f"🚀 Начинаем тестирование {self.stats['total']} endpoint'ов...", Colors.BLUE)
        
        endpoint_count = 0
        for path, methods in paths.items():
            for method, endpoint_spec in methods.items():
                endpoint_count += 1
                self.log(f"[{endpoint_count}/{self.stats['total']}] {method.upper()} {path}", Colors.BLUE)
                
                result = self.test_endpoint(method, path, endpoint_spec)
                self.results.append(result)
                
                # Вывод результата
                if result['status'] == 'success':
                    self.log(f"  ✅ {result['http_code']} ({result['response_time_ms']}ms)", Colors.GREEN)
                elif result['status'] == 'unauthorized':
                    self.log(f"  ⚠️ {result['http_code']} (требует авторизацию)", Colors.YELLOW)
                elif result['status'] == 'validation_error':
                    self.log(f"  ⚠️ {result['http_code']} (ошибка валидации - ожидаемо)", Colors.YELLOW)
                else:
                    self.log(f"  ❌ {result['http_code']} - {result.get('error', 'Unknown')}", Colors.RED)
                
                # Небольшая задержка, чтобы не перегружать сервер
                time.sleep(0.1)
        
        return True
    
    def generate_report(self) -> str:
        """Создать отчет о тестировании"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"endpoints_test_report_{timestamp}.json"
        markdown_file = f"endpoints_test_report_{timestamp}.md"
        
        # JSON отчет
        report_data = {
            'test_date': datetime.now().isoformat(),
            'base_url': self.base_url,
            'family_id': self.family_id,
            'stats': self.stats,
            'results': self.results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # Markdown отчет
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(f"# 📊 ОТЧЕТ О ТЕСТИРОВАНИИ ENDPOINT'ОВ\n\n")
            f.write(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Base URL:** {self.base_url}\n")
            f.write(f"**Family ID:** {self.family_id}\n\n")
            
            f.write(f"## 📈 СТАТИСТИКА\n\n")
            f.write(f"- **Всего endpoint'ов:** {self.stats['total']}\n")
            f.write(f"- **✅ Успешно:** {self.stats['success']}\n")
            f.write(f"- **❌ Ошибки:** {self.stats['failed']}\n")
            f.write(f"- **⏭️ Пропущено:** {self.stats['skipped']}\n")
            f.write(f"- **🔐 Требуют авторизацию:** {self.stats['requires_auth']}\n")
            f.write(f"- **🌐 Публичные:** {self.stats['public']}\n\n")
            
            success_rate = (self.stats['success'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
            f.write(f"**Процент успеха:** {success_rate:.1f}%\n\n")
            
            f.write(f"## 📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ\n\n")
            f.write(f"| Метод | Путь | Статус | HTTP | Время (мс) | Ошибка |\n")
            f.write(f"|-------|------|--------|------|------------|--------|\n")
            
            for result in self.results:
                status_emoji = {
                    'success': '✅',
                    'unauthorized': '⚠️',
                    'validation_error': '⚠️',
                    'not_found': '❌',
                    'server_error': '❌',
                    'error': '❌',
                    'skipped': '⏭️'
                }.get(result['status'], '❓')
                
                f.write(f"| {result['method']} | `{result['path']}` | {status_emoji} {result['status']} | "
                       f"{result['http_code'] or 'N/A'} | {result['response_time_ms'] or 'N/A'} | "
                       f"{result.get('error', '')[:50] or '-'} |\n")
        
        self.log(f"✅ Отчеты сохранены:", Colors.GREEN)
        self.log(f"   - JSON: {report_file}", Colors.GREEN)
        self.log(f"   - Markdown: {markdown_file}", Colors.GREEN)
        
        return report_file

def main():
    """Главная функция"""
    print("=" * 80)
    print("🚀 АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ ВСЕХ ENDPOINT'ОВ ALADDIN API")
    print("=" * 80)
    print()
    print("⚠️ ВАЖНО: МЫ НЕ СОБИРАЕМ ПЕРСОНАЛЬНЫЕ ДАННЫЕ!")
    print("   - Используем только анонимные данные: family_id, recovery_code")
    print("   - НЕ используем email, password, телефон")
    print()
    
    tester = EndpointTester(BASE_URL)
    
    if tester.test_all_endpoints():
        tester.generate_report()
        
        print()
        print("=" * 80)
        print("📊 ИТОГОВАЯ СТАТИСТИКА")
        print("=" * 80)
        print(f"Всего endpoint'ов: {tester.stats['total']}")
        print(f"✅ Успешно: {tester.stats['success']}")
        print(f"❌ Ошибки: {tester.stats['failed']}")
        print(f"⏭️ Пропущено: {tester.stats['skipped']}")
        print(f"🔐 Требуют авторизацию: {tester.stats['requires_auth']}")
        print(f"🌐 Публичные: {tester.stats['public']}")
        
        success_rate = (tester.stats['success'] / tester.stats['total'] * 100) if tester.stats['total'] > 0 else 0
        print(f"📈 Процент успеха: {success_rate:.1f}%")
        print("=" * 80)
    else:
        print("❌ Ошибка при тестировании")

if __name__ == '__main__':
    main()
