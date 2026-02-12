#!/usr/bin/env python3
"""
Улучшенный скрипт автоматического тестирования всех endpoint'ов ALADDIN API
С детальным анализом всех статусов, производительности, безопасности и валидации

⚠️ ВАЖНО: МЫ НЕ СОБИРАЕМ ПЕРСОНАЛЬНЫЕ ДАННЫЕ!
- Используем только анонимные данные: family_id, recovery_code
- НЕ используем email, password, телефон
"""

import requests
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import re

# Конфигурация
BASE_URL = "http://149.154.65.180:8002"
TIMEOUT = 10  # секунд
MAX_RETRIES = 3
PERFORMANCE_THRESHOLD_MS = 2000  # Порог производительности (2 секунды)
SECURITY_CHECK_ENABLED = True
VALIDATION_CHECK_ENABLED = True

# Цвета для вывода
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'

class EnhancedEndpointTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.family_id: Optional[str] = None
        self.recovery_code: Optional[str] = None
        self.results: List[Dict] = []
        self.detailed_analysis: Dict = {
            'status_401': [],  # Endpoint'ы с 401 - требуют авторизацию
            'status_422': [],  # Endpoint'ы с 422 - ошибка валидации
            'status_404': [],  # Endpoint'ы с 404 - не найдены
            'status_500': [],  # Endpoint'ы с 500 - ошибка сервера
            'performance_issues': [],  # Медленные endpoint'ы
            'security_issues': [],  # Проблемы безопасности
            'validation_issues': []  # Проблемы валидации
        }
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'requires_auth': 0,
            'public': 0,
            'status_200': 0,
            'status_201': 0,
            'status_204': 0,
            'status_401': 0,
            'status_403': 0,
            'status_404': 0,
            'status_422': 0,
            'status_500': 0,
            'status_other': 0,
            'performance_ok': 0,
            'performance_slow': 0,
            'security_ok': 0,
            'security_issues_count': 0,
            'validation_ok': 0,
            'validation_issues_count': 0
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
                return False
            
            family_data = response.json()
            self.family_id = family_data.get("family_id")
            self.recovery_code = self.family_id
            
            self.log(f"✅ Семья создана: {self.family_id}", Colors.GREEN)
            
            # ШАГ 2: Получить токен
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
                return False
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
            
            self.log(f"✅ Токен получен", Colors.GREEN)
            return True
            
        except Exception as e:
            self.log(f"❌ Ошибка: {e}", Colors.RED)
            return False
    
    def requires_auth(self, endpoint_spec: Dict) -> bool:
        """Проверить, требует ли endpoint авторизацию"""
        if 'security' in endpoint_spec:
            return True
        if 'parameters' in endpoint_spec:
            for param in endpoint_spec['parameters']:
                if param.get('name') == 'Authorization' or 'bearer' in param.get('name', '').lower():
                    return True
        return False
    
    def check_security(self, method: str, path: str, response: requests.Response, endpoint_spec: Dict) -> Dict:
        """Проверка безопасности endpoint'а"""
        security_issues = []
        security_score = 100
        
        # Проверка 1: HTTPS (если доступен)
        if not self.base_url.startswith('https'):
            security_issues.append("Используется HTTP вместо HTTPS")
            security_score -= 10
        
        # Проверка 2: Защита от CSRF
        csrf_headers = ['X-CSRF-Token', 'X-Requested-With']
        has_csrf = any(header in response.headers for header in csrf_headers)
        if not has_csrf and method.upper() in ['POST', 'PUT', 'DELETE']:
            security_issues.append("Нет защиты от CSRF")
            security_score -= 5
        
        # Проверка 3: Защита от XSS
        xss_headers = ['X-Content-Type-Options', 'X-Frame-Options', 'X-XSS-Protection']
        has_xss = any(header in response.headers for header in xss_headers)
        if not has_xss:
            security_issues.append("Нет защиты от XSS")
            security_score -= 5
        
        # Проверка 4: Rate Limiting
        rate_limit_headers = ['X-RateLimit-Limit', 'X-RateLimit-Remaining', 'Retry-After']
        has_rate_limit = any(header in response.headers for header in rate_limit_headers)
        if not has_rate_limit:
            security_issues.append("Нет Rate Limiting заголовков")
            security_score -= 5
        
        # Проверка 5: Информация в ошибках
        if response.status_code >= 400:
            error_body = response.text.lower()
            sensitive_info = ['password', 'token', 'secret', 'key', 'database']
            if any(info in error_body for info in sensitive_info):
                security_issues.append("Возможна утечка чувствительной информации в ошибках")
                security_score -= 20
        
        return {
            'score': max(0, security_score),
            'issues': security_issues,
            'has_csrf': has_csrf,
            'has_xss': has_xss,
            'has_rate_limit': has_rate_limit
        }
    
    def check_validation(self, method: str, path: str, response: requests.Response, test_data: Dict) -> Dict:
        """Проверка валидации данных"""
        validation_issues = []
        validation_score = 100
        
        if response.status_code == 422:
            # Анализ ошибок валидации
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    if isinstance(error_data['detail'], list):
                        validation_issues.append(f"Ошибки валидации: {len(error_data['detail'])} полей")
                        # Анализ типов ошибок
                        error_types = defaultdict(int)
                        for error in error_data['detail']:
                            if 'type' in error:
                                error_types[error['type']] += 1
                        validation_issues.append(f"Типы ошибок: {dict(error_types)}")
                    else:
                        validation_issues.append(f"Ошибка валидации: {error_data['detail']}")
            except:
                validation_issues.append("Не удалось разобрать ошибку валидации")
        
        # Проверка: endpoint должен валидировать входные данные
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            if response.status_code not in [200, 201, 204, 422]:
                # Если не 422 и не успех, возможно проблема с валидацией
                if response.status_code == 400:
                    validation_issues.append("Возвращает 400 вместо 422 для ошибок валидации")
                    validation_score -= 10
        
        return {
            'score': max(0, validation_score),
            'issues': validation_issues,
            'has_validation': response.status_code == 422
        }
    
    def generate_test_data(self, method: str, path: str, endpoint_spec: Dict) -> Optional[Dict]:
        """Генерировать тестовые данные для запроса"""
        if method.upper() not in ['POST', 'PUT', 'PATCH']:
            return None
        
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
        
        test_data = {}
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        for field, field_spec in properties.items():
            # ⚠️ ВАЖНО: НЕ используем персональные данные!
            if any(sensitive in field.lower() for sensitive in ['email', 'password', 'phone', 'ssn', 'credit']):
                continue
            
            field_type = field_spec.get('type', 'string')
            default = field_spec.get('default')
            
            if default is not None:
                test_data[field] = default
            elif field_type == 'string':
                if 'id' in field.lower():
                    test_data[field] = f"TEST_{field.upper()}_123"
                elif 'code' in field.lower():
                    test_data[field] = "TEST_CODE"
                elif field in required:
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
    
    def analyze_status_code(self, status_code: int, method: str, path: str, requires_auth: bool, 
                           has_token: bool, response: requests.Response) -> Dict:
        """Детальный анализ HTTP статус кода"""
        analysis = {
            'status_code': status_code,
            'is_success': False,
            'is_expected': False,
            'reason': '',
            'action_needed': '',
            'category': 'unknown'
        }
        
        # Успешные статусы
        if status_code in [200, 201, 204]:
            analysis['is_success'] = True
            analysis['is_expected'] = True
            analysis['category'] = 'success'
            if status_code == 200:
                analysis['reason'] = 'OK - запрос успешно выполнен'
            elif status_code == 201:
                analysis['reason'] = 'Created - ресурс успешно создан'
            elif status_code == 204:
                analysis['reason'] = 'No Content - успешно, но без содержимого'
        
        # 401 Unauthorized
        elif status_code == 401:
            analysis['category'] = 'authentication'
            if requires_auth and not has_token:
                analysis['is_expected'] = True
                analysis['reason'] = 'Ожидаемо - endpoint требует авторизацию, токен не предоставлен'
                analysis['action_needed'] = 'Добавить токен авторизации'
            elif requires_auth and has_token:
                analysis['is_expected'] = False
                analysis['reason'] = 'Проблема - endpoint требует авторизацию, но токен недействителен'
                analysis['action_needed'] = 'Проверить валидность токена или обновить его'
            else:
                analysis['is_expected'] = False
                analysis['reason'] = 'Неожиданно - endpoint не должен требовать авторизацию'
                analysis['action_needed'] = 'Проверить конфигурацию endpoint\'а'
        
        # 403 Forbidden
        elif status_code == 403:
            analysis['category'] = 'authorization'
            analysis['is_expected'] = False
            analysis['reason'] = 'Forbidden - недостаточно прав доступа'
            analysis['action_needed'] = 'Проверить права доступа пользователя'
        
        # 404 Not Found
        elif status_code == 404:
            analysis['category'] = 'not_found'
            analysis['is_expected'] = False
            analysis['reason'] = 'Not Found - endpoint не найден'
            analysis['action_needed'] = 'Проверить правильность пути или подключение роутера'
        
        # 422 Unprocessable Entity
        elif status_code == 422:
            analysis['category'] = 'validation'
            analysis['is_expected'] = True  # Ожидаемо для тестовых данных
            analysis['reason'] = 'Validation Error - ошибка валидации входных данных'
            analysis['action_needed'] = 'Проверить формат и обязательные поля запроса'
            # Детальный анализ ошибок валидации
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    if isinstance(error_data['detail'], list):
                        analysis['validation_errors'] = error_data['detail']
                    else:
                        analysis['validation_message'] = str(error_data['detail'])
            except:
                pass
        
        # 500+ Server Error
        elif status_code >= 500:
            analysis['category'] = 'server_error'
            analysis['is_expected'] = False
            analysis['reason'] = f'Server Error - ошибка на сервере ({status_code})'
            analysis['action_needed'] = 'Проверить логи сервера и исправить ошибку'
        
        # Другие статусы
        else:
            analysis['category'] = 'other'
            analysis['reason'] = f'Неожиданный статус код: {status_code}'
            analysis['action_needed'] = 'Проверить документацию API'
        
        return analysis
    
    def test_endpoint(self, method: str, path: str, endpoint_spec: Dict) -> Dict:
        """Тестировать один endpoint с детальным анализом"""
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
            'response_preview': None,
            'status_analysis': {},
            'security_check': {},
            'validation_check': {},
            'performance_check': {}
        }
        
        # Пропускаем только системные endpoint'ы (точное совпадение)
        skip_paths = ['/docs', '/openapi.json', '/redoc', '/']
        if path in skip_paths or path == '/':
            result['status'] = 'skipped'
            result['error'] = 'System endpoint'
            self.stats['skipped'] += 1
            return result
        
        try:
            # Подготовка запроса
            headers = {}
            has_token = False
            if requires_auth and self.access_token:
                headers['Authorization'] = f"Bearer {self.access_token}"
                has_token = True
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
            
            # Детальный анализ статус кода
            result['status_analysis'] = self.analyze_status_code(
                response.status_code, method, path, requires_auth, has_token, response
            )
            
            # Проверка производительности
            if response_time > PERFORMANCE_THRESHOLD_MS:
                result['performance_check'] = {
                    'is_slow': True,
                    'threshold_ms': PERFORMANCE_THRESHOLD_MS,
                    'actual_ms': result['response_time_ms'],
                    'issue': f'Медленный ответ: {result["response_time_ms"]}ms > {PERFORMANCE_THRESHOLD_MS}ms'
                }
                self.detailed_analysis['performance_issues'].append({
                    'method': method,
                    'path': path,
                    'response_time_ms': result['response_time_ms']
                })
                self.stats['performance_slow'] += 1
            else:
                result['performance_check'] = {'is_slow': False}
                self.stats['performance_ok'] += 1
            
            # Проверка безопасности
            if SECURITY_CHECK_ENABLED:
                result['security_check'] = self.check_security(method, path, response, endpoint_spec)
                if result['security_check']['issues']:
                    self.detailed_analysis['security_issues'].append({
                        'method': method,
                        'path': path,
                        'issues': result['security_check']['issues'],
                        'score': result['security_check']['score']
                    })
                    self.stats['security_issues_count'] += 1
                else:
                    self.stats['security_ok'] += 1
            
            # Проверка валидации
            if VALIDATION_CHECK_ENABLED:
                result['validation_check'] = self.check_validation(method, path, response, test_data)
                if result['validation_check']['issues']:
                    self.detailed_analysis['validation_issues'].append({
                        'method': method,
                        'path': path,
                        'issues': result['validation_check']['issues']
                    })
                    self.stats['validation_issues_count'] += 1
                else:
                    self.stats['validation_ok'] += 1
            
            # Определение статуса
            if response.status_code in [200, 201, 204]:
                result['status'] = 'success'
                self.stats['success'] += 1
                if response.status_code == 200:
                    self.stats['status_200'] += 1
                elif response.status_code == 201:
                    self.stats['status_201'] += 1
                elif response.status_code == 204:
                    self.stats['status_204'] += 1
            elif response.status_code == 401:
                result['status'] = 'unauthorized'
                self.stats['status_401'] += 1
                self.detailed_analysis['status_401'].append({
                    'method': method,
                    'path': path,
                    'requires_auth': requires_auth,
                    'has_token': has_token,
                    'analysis': result['status_analysis']
                })
                if result['status_analysis']['is_expected']:
                    self.stats['success'] += 1  # Ожидаемо
                else:
                    self.stats['failed'] += 1
            elif response.status_code == 403:
                result['status'] = 'forbidden'
                self.stats['status_403'] += 1
                self.stats['failed'] += 1
            elif response.status_code == 404:
                result['status'] = 'not_found'
                self.stats['status_404'] += 1
                self.stats['failed'] += 1
                self.detailed_analysis['status_404'].append({
                    'method': method,
                    'path': path,
                    'analysis': result['status_analysis']
                })
            elif response.status_code == 422:
                result['status'] = 'validation_error'
                self.stats['status_422'] += 1
                self.detailed_analysis['status_422'].append({
                    'method': method,
                    'path': path,
                    'test_data': test_data,
                    'validation_check': result['validation_check'],
                    'analysis': result['status_analysis']
                })
                self.stats['success'] += 1  # Ожидаемо для тестовых данных
            elif response.status_code >= 500:
                result['status'] = 'server_error'
                self.stats['status_500'] += 1
                self.stats['failed'] += 1
                self.detailed_analysis['status_500'].append({
                    'method': method,
                    'path': path,
                    'analysis': result['status_analysis']
                })
            else:
                result['status'] = 'unknown'
                self.stats['status_other'] += 1
                self.stats['failed'] += 1
            
            # Сохраняем превью ответа
            try:
                result['response_preview'] = response.text[:500]
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
        self.log("   (проверка производительности, безопасности и валидации включена)", Colors.CYAN)
        
        endpoint_count = 0
        for path, methods in paths.items():
            for method, endpoint_spec in methods.items():
                endpoint_count += 1
                self.log(f"[{endpoint_count}/{self.stats['total']}] {method.upper()} {path}", Colors.BLUE)
                
                result = self.test_endpoint(method, path, endpoint_spec)
                self.results.append(result)
                
                # Вывод результата с деталями
                status_emoji = {
                    'success': '✅',
                    'unauthorized': '⚠️',
                    'validation_error': '⚠️',
                    'not_found': '❌',
                    'server_error': '❌',
                    'error': '❌',
                    'skipped': '⏭️'
                }.get(result['status'], '❓')
                
                status_color = {
                    'success': Colors.GREEN,
                    'unauthorized': Colors.YELLOW,
                    'validation_error': Colors.YELLOW,
                    'not_found': Colors.RED,
                    'server_error': Colors.RED,
                    'error': Colors.RED,
                    'skipped': Colors.CYAN
                }.get(result['status'], Colors.END)
                
                msg = f"  {status_emoji} {result['http_code']} ({result['response_time_ms']}ms)"
                if result.get('performance_check', {}).get('is_slow'):
                    msg += f" {Colors.YELLOW}🐌 МЕДЛЕННО{Colors.END}"
                if result.get('security_check', {}).get('issues'):
                    msg += f" {Colors.RED}🔒 БЕЗОПАСНОСТЬ{Colors.END}"
                
                self.log(msg, status_color)
                
                # Детальная информация для проблемных endpoint'ов
                if result['status'] in ['not_found', 'server_error']:
                    self.log(f"     Причина: {result.get('status_analysis', {}).get('reason', 'Unknown')}", Colors.YELLOW)
                
                time.sleep(0.1)  # Задержка, чтобы не перегружать сервер
        
        return True
    
    def generate_detailed_report(self) -> Tuple[str, str]:
        """Создать детальный отчет о тестировании"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"endpoints_test_report_{timestamp}.json"
        markdown_file = f"endpoints_test_report_{timestamp}.md"
        
        # JSON отчет
        report_data = {
            'test_date': datetime.now().isoformat(),
            'base_url': self.base_url,
            'family_id': self.family_id,
            'stats': self.stats,
            'detailed_analysis': self.detailed_analysis,
            'results': self.results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # Markdown отчет
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(f"# 📊 ДЕТАЛЬНЫЙ ОТЧЕТ О ТЕСТИРОВАНИИ ENDPOINT'ОВ\n\n")
            f.write(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Base URL:** {self.base_url}\n")
            f.write(f"**Family ID:** {self.family_id}\n\n")
            
            # Статистика
            f.write(f"## 📈 СТАТИСТИКА\n\n")
            f.write(f"- **Всего endpoint'ов:** {self.stats['total']}\n")
            f.write(f"- **✅ Успешно:** {self.stats['success']}\n")
            f.write(f"- **❌ Ошибки:** {self.stats['failed']}\n")
            f.write(f"- **⏭️ Пропущено:** {self.stats['skipped']}\n")
            f.write(f"- **🔐 Требуют авторизацию:** {self.stats['requires_auth']}\n")
            f.write(f"- **🌐 Публичные:** {self.stats['public']}\n\n")
            
            success_rate = (self.stats['success'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
            f.write(f"**Процент успеха:** {success_rate:.1f}%\n\n")
            
            # Детальная статистика по статусам
            f.write(f"### 📊 Статусы HTTP:\n\n")
            f.write(f"- **200 OK:** {self.stats['status_200']}\n")
            f.write(f"- **201 Created:** {self.stats['status_201']}\n")
            f.write(f"- **204 No Content:** {self.stats['status_204']}\n")
            f.write(f"- **401 Unauthorized:** {self.stats['status_401']}\n")
            f.write(f"- **403 Forbidden:** {self.stats.get('status_403', 0)}\n")
            f.write(f"- **404 Not Found:** {self.stats['status_404']}\n")
            f.write(f"- **422 Validation Error:** {self.stats['status_422']}\n")
            f.write(f"- **500+ Server Error:** {self.stats['status_500']}\n\n")
            
            # Производительность
            f.write(f"### ⚡ Производительность:\n\n")
            f.write(f"- **✅ Быстрые (< {PERFORMANCE_THRESHOLD_MS}ms):** {self.stats['performance_ok']}\n")
            f.write(f"- **🐌 Медленные (> {PERFORMANCE_THRESHOLD_MS}ms):** {self.stats['performance_slow']}\n\n")
            
            # Безопасность
            f.write(f"### 🔒 Безопасность:\n\n")
            f.write(f"- **✅ Без проблем:** {self.stats['security_ok']}\n")
            f.write(f"- **⚠️ Проблемы:** {self.stats['security_issues_count']}\n\n")
            
            # Валидация
            f.write(f"### ✅ Валидация:\n\n")
            f.write(f"- **✅ Без проблем:** {self.stats['validation_ok']}\n")
            f.write(f"- **⚠️ Проблемы:** {self.stats['validation_issues_count']}\n\n")
            
            # Детальный анализ 401
            if self.detailed_analysis['status_401']:
                f.write(f"## 🔐 ДЕТАЛЬНЫЙ АНАЛИЗ 401 (UNAUTHORIZED)\n\n")
                f.write(f"**Всего:** {len(self.detailed_analysis['status_401'])}\n\n")
                f.write(f"| Метод | Путь | Требует авторизацию | Есть токен | Причина | Действие |\n")
                f.write(f"|-------|------|---------------------|------------|---------|----------|\n")
                for item in self.detailed_analysis['status_401']:
                    analysis = item.get('analysis', {})
                    f.write(f"| {item['method']} | `{item['path']}` | {'✅' if item['requires_auth'] else '❌'} | "
                           f"{'✅' if item['has_token'] else '❌'} | {analysis.get('reason', '')[:50]} | "
                           f"{analysis.get('action_needed', '')[:50]} |\n")
                f.write(f"\n")
            
            # Детальный анализ 422
            if self.detailed_analysis['status_422']:
                f.write(f"## ✅ ДЕТАЛЬНЫЙ АНАЛИЗ 422 (VALIDATION ERROR)\n\n")
                f.write(f"**Всего:** {len(self.detailed_analysis['status_422'])}\n\n")
                f.write(f"| Метод | Путь | Проблемы валидации |\n")
                f.write(f"|-------|------|-------------------|\n")
                for item in self.detailed_analysis['status_422']:
                    issues = item.get('validation_check', {}).get('issues', [])
                    issues_str = '; '.join(issues[:2]) if issues else 'Ожидаемо для тестовых данных'
                    f.write(f"| {item['method']} | `{item['path']}` | {issues_str[:100]} |\n")
                f.write(f"\n")
            
            # Детальный анализ 404
            if self.detailed_analysis['status_404']:
                f.write(f"## ❌ ДЕТАЛЬНЫЙ АНАЛИЗ 404 (NOT FOUND)\n\n")
                f.write(f"**Всего:** {len(self.detailed_analysis['status_404'])}\n\n")
                f.write(f"| Метод | Путь | Причина | Действие |\n")
                f.write(f"|-------|------|---------|----------|\n")
                for item in self.detailed_analysis['status_404']:
                    analysis = item.get('analysis', {})
                    f.write(f"| {item['method']} | `{item['path']}` | {analysis.get('reason', '')[:50]} | "
                           f"{analysis.get('action_needed', '')[:50]} |\n")
                f.write(f"\n")
            
            # Проблемы производительности
            if self.detailed_analysis['performance_issues']:
                f.write(f"## 🐌 ПРОБЛЕМЫ ПРОИЗВОДИТЕЛЬНОСТИ\n\n")
                f.write(f"**Всего:** {len(self.detailed_analysis['performance_issues'])}\n\n")
                f.write(f"| Метод | Путь | Время ответа (мс) |\n")
                f.write(f"|-------|------|-------------------|\n")
                for item in sorted(self.detailed_analysis['performance_issues'], 
                                 key=lambda x: x['response_time_ms'], reverse=True)[:20]:
                    f.write(f"| {item['method']} | `{item['path']}` | {item['response_time_ms']} |\n")
                f.write(f"\n")
            
            # Проблемы безопасности
            if self.detailed_analysis['security_issues']:
                f.write(f"## 🔒 ПРОБЛЕМЫ БЕЗОПАСНОСТИ\n\n")
                f.write(f"**Всего:** {len(self.detailed_analysis['security_issues'])}\n\n")
                f.write(f"| Метод | Путь | Проблемы | Оценка |\n")
                f.write(f"|-------|------|----------|--------|\n")
                for item in self.detailed_analysis['security_issues']:
                    issues_str = '; '.join(item['issues'][:2])
                    f.write(f"| {item['method']} | `{item['path']}` | {issues_str[:80]} | {item['score']}/100 |\n")
                f.write(f"\n")
            
            # Все результаты
            f.write(f"## 📋 ВСЕ РЕЗУЛЬТАТЫ\n\n")
            f.write(f"| Метод | Путь | Статус | HTTP | Время (мс) | Производительность | Безопасность | Валидация |\n")
            f.write(f"|-------|------|--------|------|------------|-------------------|--------------|-----------|\n")
            
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
                
                perf = '✅' if not result.get('performance_check', {}).get('is_slow') else '🐌'
                security = f"{result.get('security_check', {}).get('score', 'N/A')}/100"
                validation = '✅' if not result.get('validation_check', {}).get('issues') else '⚠️'
                
                f.write(f"| {result['method']} | `{result['path']}` | {status_emoji} {result['status']} | "
                       f"{result['http_code'] or 'N/A'} | {result['response_time_ms'] or 'N/A'} | "
                       f"{perf} | {security} | {validation} |\n")
        
        self.log(f"✅ Отчеты сохранены:", Colors.GREEN)
        self.log(f"   - JSON: {report_file}", Colors.GREEN)
        self.log(f"   - Markdown: {markdown_file}", Colors.GREEN)
        
        return report_file, markdown_file

def main():
    """Главная функция"""
    print("=" * 80)
    print("🚀 УЛУЧШЕННОЕ АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ ВСЕХ ENDPOINT'ОВ ALADDIN API")
    print("=" * 80)
    print()
    print("⚠️ ВАЖНО: МЫ НЕ СОБИРАЕМ ПЕРСОНАЛЬНЫЕ ДАННЫЕ!")
    print("   - Используем только анонимные данные: family_id, recovery_code")
    print("   - НЕ используем email, password, телефон")
    print()
    print("📊 ПРОВЕРКИ:")
    print("   ✅ Производительность (порог: 2000ms)")
    print("   ✅ Безопасность (CSRF, XSS, Rate Limiting)")
    print("   ✅ Валидация данных")
    print("   ✅ Детальный анализ всех статус кодов")
    print()
    
    tester = EnhancedEndpointTester(BASE_URL)
    
    if tester.test_all_endpoints():
        tester.generate_detailed_report()
        
        print()
        print("=" * 80)
        print("📊 ИТОГОВАЯ СТАТИСТИКА")
        print("=" * 80)
        print(f"Всего endpoint'ов: {tester.stats['total']}")
        print(f"✅ Успешно: {tester.stats['success']}")
        print(f"❌ Ошибки: {tester.stats['failed']}")
        print(f"⏭️ Пропущено: {tester.stats['skipped']}")
        print()
        print("📊 ПО СТАТУСАМ:")
        print(f"  200 OK: {tester.stats['status_200']}")
        print(f"  201 Created: {tester.stats['status_201']}")
        print(f"  401 Unauthorized: {tester.stats['status_401']}")
        print(f"  404 Not Found: {tester.stats['status_404']}")
        print(f"  422 Validation Error: {tester.stats['status_422']}")
        print(f"  500+ Server Error: {tester.stats['status_500']}")
        print()
        print("⚡ ПРОИЗВОДИТЕЛЬНОСТЬ:")
        print(f"  ✅ Быстрые: {tester.stats['performance_ok']}")
        print(f"  🐌 Медленные: {tester.stats['performance_slow']}")
        print()
        print("🔒 БЕЗОПАСНОСТЬ:")
        print(f"  ✅ Без проблем: {tester.stats['security_ok']}")
        print(f"  ⚠️ Проблемы: {tester.stats['security_issues_count']}")
        print()
        print("✅ ВАЛИДАЦИЯ:")
        print(f"  ✅ Без проблем: {tester.stats['validation_ok']}")
        print(f"  ⚠️ Проблемы: {tester.stats['validation_issues_count']}")
        print()
        print("📋 ДЕТАЛЬНЫЙ АНАЛИЗ:")
        print(f"  401 (Unauthorized): {len(tester.detailed_analysis['status_401'])} endpoint'ов")
        print(f"  422 (Validation Error): {len(tester.detailed_analysis['status_422'])} endpoint'ов")
        print(f"  404 (Not Found): {len(tester.detailed_analysis['status_404'])} endpoint'ов")
        print(f"  500+ (Server Error): {len(tester.detailed_analysis['status_500'])} endpoint'ов")
        print("=" * 80)
    else:
        print("❌ Ошибка при тестировании")

if __name__ == '__main__':
    main()
