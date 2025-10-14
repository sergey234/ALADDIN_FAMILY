#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Security Audit - Комплексный аудит безопасности системы ALADDIN
Проверка всех 299 файлов на уязвимости, качество кода и безопасность

Функция: Comprehensive Security Audit
Приоритет: КРИТИЧЕСКИЙ
Версия: 1.0
Дата: 2025-09-07
"""

import os
import sys
import subprocess
import json
import re
import ast
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import shutil

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Уровни безопасности"""
    CRITICAL = "critical"    # Критический
    HIGH = "high"           # Высокий
    MEDIUM = "medium"       # Средний
    LOW = "low"             # Низкий
    INFO = "info"           # Информационный

class VulnerabilityType(Enum):
    """Типы уязвимостей"""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    PATH_TRAVERSAL = "path_traversal"
    CODE_INJECTION = "code_injection"
    HARDCODED_SECRETS = "hardcoded_secrets"
    WEAK_CRYPTO = "weak_crypto"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    MISSING_AUTHENTICATION = "missing_authentication"
    MISSING_AUTHORIZATION = "missing_authorization"
    INSECURE_REDIRECT = "insecure_redirect"
    INFORMATION_DISCLOSURE = "information_disclosure"
    WEAK_RANDOMNESS = "weak_randomness"
    TIMING_ATTACK = "timing_attack"
    BUFFER_OVERFLOW = "buffer_overflow"
    MEMORY_LEAK = "memory_leak"
    RACE_CONDITION = "race_condition"
    LOG_INJECTION = "log_injection"
    COMMAND_INJECTION = "command_injection"
    LDAP_INJECTION = "ldap_injection"
    XXE = "xxe"
    SSRF = "ssrf"
    BROKEN_ACCESS_CONTROL = "broken_access_control"
    SECURITY_MISCONFIGURATION = "security_misconfiguration"
    VULNERABLE_COMPONENTS = "vulnerable_components"
    INSUFFICIENT_LOGGING = "insufficient_logging"
    WEAK_PASSWORD_POLICY = "weak_password_policy"
    INSECURE_COMMUNICATION = "insecure_communication"
    IMPROPER_ERROR_HANDLING = "improper_error_handling"
    INSECURE_STORAGE = "insecure_storage"
    MISSING_ENCRYPTION = "missing_encryption"
    WEAK_SESSION_MANAGEMENT = "weak_session_management"
    INSECURE_DESIGN = "insecure_design"
    UNKNOWN = "unknown"

@dataclass
class SecurityIssue:
    """Проблема безопасности"""
    file_path: str
    line_number: int
    vulnerability_type: VulnerabilityType
    security_level: SecurityLevel
    description: str
    recommendation: str
    code_snippet: str = ""
    cwe_id: str = ""
    owasp_category: str = ""

@dataclass
class SecurityAuditResult:
    """Результат аудита безопасности"""
    total_files_scanned: int
    total_issues_found: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    info_issues: int
    issues_by_type: Dict[VulnerabilityType, int]
    issues_by_file: Dict[str, List[SecurityIssue]]
    security_score: float
    recommendations: List[str]
    scan_timestamp: datetime
    scan_duration: float

class ComprehensiveSecurityAudit:
    """Комплексный аудит безопасности системы ALADDIN"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.issues: List[SecurityIssue] = []
        self.scan_patterns = self._initialize_scan_patterns()
        self.dangerous_functions = self._initialize_dangerous_functions()
        self.hardcoded_secrets_patterns = self._initialize_secrets_patterns()
        
    def _initialize_scan_patterns(self) -> Dict[VulnerabilityType, List[str]]:
        """Инициализация паттернов для сканирования"""
        return {
            VulnerabilityType.SQL_INJECTION: [
                r"execute\s*\(\s*['\"].*%.*['\"]",
                r"cursor\.execute\s*\(\s*['\"].*%.*['\"]",
                r"query\s*=\s*['\"].*%.*['\"]",
                r"SELECT.*%.*FROM",
                r"INSERT.*%.*INTO",
                r"UPDATE.*%.*SET",
                r"DELETE.*%.*FROM"
            ],
            VulnerabilityType.XSS: [
                r"render_template_string\s*\(",
                r"Markup\s*\(",
                r"safe\s*\(",
                r"autoescape\s*=\s*False",
                r"{{.*\|.*safe.*}}",
                r"innerHTML\s*=",
                r"document\.write\s*\("
            ],
            VulnerabilityType.CSRF: [
                r"@csrf\.exempt",
                r"csrf_exempt",
                r"@app\.before_request",
                r"@csrf\.ignore"
            ],
            VulnerabilityType.PATH_TRAVERSAL: [
                r"open\s*\(\s*['\"].*\.\./.*['\"]",
                r"file\s*=\s*['\"].*\.\./.*['\"]",
                r"path\s*=\s*['\"].*\.\./.*['\"]",
                r"os\.path\.join\s*\(\s*.*\.\./.*\)",
                r"os\.chdir\s*\(\s*.*\.\./.*\)"
            ],
            VulnerabilityType.CODE_INJECTION: [
                r"eval\s*\(",
                r"exec\s*\(",
                r"compile\s*\(",
                r"__import__\s*\(",
                r"getattr\s*\(\s*.*,\s*['\"].*['\"]\s*\)",
                r"setattr\s*\(\s*.*,\s*['\"].*['\"]\s*\)",
                r"globals\s*\(\s*\)",
                r"locals\s*\(\s*\)"
            ],
            VulnerabilityType.HARDCODED_SECRETS: [
                r"password\s*=\s*['\"][^'\"]{3,}['\"]",
                r"secret\s*=\s*['\"][^'\"]{3,}['\"]",
                r"key\s*=\s*['\"][^'\"]{3,}['\"]",
                r"token\s*=\s*['\"][^'\"]{3,}['\"]",
                r"api_key\s*=\s*['\"][^'\"]{3,}['\"]",
                r"private_key\s*=\s*['\"][^'\"]{3,}['\"]"
            ],
            VulnerabilityType.WEAK_CRYPTO: [
                r"md5\s*\(",
                r"sha1\s*\(",
                r"DES\s*\(",
                r"RC4\s*\(",
                r"random\.random\s*\(",
                r"random\.randint\s*\(",
                r"hashlib\.md5\s*\(",
                r"hashlib\.sha1\s*\("
            ],
            VulnerabilityType.INSECURE_DESERIALIZATION: [
                r"pickle\.loads\s*\(",
                r"pickle\.load\s*\(",
                r"marshal\.loads\s*\(",
                r"marshal\.load\s*\(",
                r"yaml\.load\s*\(",
                r"json\.loads\s*\(\s*.*unsafe\s*=\s*True"
            ],
            VulnerabilityType.MISSING_AUTHENTICATION: [
                r"@app\.route\s*\(\s*['\"][^'\"]*['\"]\s*\)",
                r"def\s+\w+\s*\(\s*\):",
                r"class\s+\w+.*:",
                r"if\s+not\s+authenticated:"
            ],
            VulnerabilityType.INSECURE_REDIRECT: [
                r"redirect\s*\(\s*request\.args\s*\[",
                r"redirect\s*\(\s*request\.form\s*\[",
                r"redirect\s*\(\s*request\.values\s*\[",
                r"return\s+redirect\s*\(\s*.*request\."
            ],
            VulnerabilityType.INFORMATION_DISCLOSURE: [
                r"print\s*\(\s*.*password.*\)",
                r"print\s*\(\s*.*secret.*\)",
                r"print\s*\(\s*.*key.*\)",
                r"print\s*\(\s*.*token.*\)",
                r"logger\.debug\s*\(\s*.*password.*\)",
                r"logger\.info\s*\(\s*.*secret.*\)"
            ],
            VulnerabilityType.WEAK_RANDOMNESS: [
                r"random\.random\s*\(",
                r"random\.randint\s*\(",
                r"random\.choice\s*\(",
                r"random\.sample\s*\(",
                r"random\.shuffle\s*\("
            ],
            VulnerabilityType.COMMAND_INJECTION: [
                r"os\.system\s*\(",
                r"subprocess\.call\s*\(",
                r"subprocess\.run\s*\(",
                r"subprocess\.Popen\s*\(",
                r"os\.popen\s*\(",
                r"commands\.getoutput\s*\("
            ],
            VulnerabilityType.LOG_INJECTION: [
                r"logger\.\w+\s*\(\s*.*%.*\)",
                r"logging\.\w+\s*\(\s*.*%.*\)",
                r"print\s*\(\s*.*%.*\)"
            ],
            VulnerabilityType.INSECURE_COMMUNICATION: [
                r"http://",
                r"ftp://",
                r"telnet://",
                r"verify\s*=\s*False",
                r"ssl_verify\s*=\s*False",
                r"check_hostname\s*=\s*False"
            ],
            VulnerabilityType.INSECURE_STORAGE: [
                r"password.*=.*['\"][^'\"]*['\"]",
                r"secret.*=.*['\"][^'\"]*['\"]",
                r"key.*=.*['\"][^'\"]*['\"]",
                r"token.*=.*['\"][^'\"]*['\"]"
            ],
            VulnerabilityType.MISSING_ENCRYPTION: [
                r"open\s*\(\s*['\"][^'\"]*\.txt['\"]",
                r"open\s*\(\s*['\"][^'\"]*\.csv['\"]",
                r"open\s*\(\s*['\"][^'\"]*\.json['\"]",
                r"with\s+open\s*\(\s*['\"][^'\"]*\.txt['\"]"
            ]
        }
    
    def _initialize_dangerous_functions(self) -> List[str]:
        """Инициализация опасных функций"""
        return [
            "eval", "exec", "compile", "__import__", "getattr", "setattr",
            "globals", "locals", "vars", "dir", "hasattr", "delattr",
            "os.system", "os.popen", "subprocess.call", "subprocess.run",
            "subprocess.Popen", "commands.getoutput", "pickle.loads",
            "pickle.load", "marshal.loads", "marshal.load", "yaml.load"
        ]
    
    def _initialize_secrets_patterns(self) -> List[str]:
        """Инициализация паттернов для поиска секретов"""
        return [
            r"password\s*=\s*['\"][^'\"]{3,}['\"]",
            r"secret\s*=\s*['\"][^'\"]{3,}['\"]",
            r"key\s*=\s*['\"][^'\"]{3,}['\"]",
            r"token\s*=\s*['\"][^'\"]{3,}['\"]",
            r"api_key\s*=\s*['\"][^'\"]{3,}['\"]",
            r"private_key\s*=\s*['\"][^'\"]{3,}['\"]",
            r"access_token\s*=\s*['\"][^'\"]{3,}['\"]",
            r"refresh_token\s*=\s*['\"][^'\"]{3,}['\"]"
        ]
    
    def scan_file(self, file_path: str) -> List[SecurityIssue]:
        """Сканирование файла на уязвимости"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Проверка на различные типы уязвимостей
            for vuln_type, patterns in self.scan_patterns.items():
                for pattern in patterns:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            issue = SecurityIssue(
                                file_path=file_path,
                                line_number=line_num,
                                vulnerability_type=vuln_type,
                                security_level=self._get_security_level(vuln_type),
                                description=self._get_description(vuln_type),
                                recommendation=self._get_recommendation(vuln_type),
                                code_snippet=line.strip(),
                                cwe_id=self._get_cwe_id(vuln_type),
                                owasp_category=self._get_owasp_category(vuln_type)
                            )
                            issues.append(issue)
            
            # Проверка на опасные функции
            for line_num, line in enumerate(lines, 1):
                for func in self.dangerous_functions:
                    if func in line and not line.strip().startswith('#'):
                        issue = SecurityIssue(
                            file_path=file_path,
                            line_number=line_num,
                            vulnerability_type=VulnerabilityType.CODE_INJECTION,
                            security_level=SecurityLevel.HIGH,
                            description=f"Использование опасной функции: {func}",
                            recommendation=f"Замените {func} на безопасную альтернативу",
                            code_snippet=line.strip(),
                            cwe_id="CWE-94",
                            owasp_category="A03:2021 – Injection"
                        )
                        issues.append(issue)
            
            # Проверка на хардкод секретов
            for line_num, line in enumerate(lines, 1):
                for pattern in self.hardcoded_secrets_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issue = SecurityIssue(
                            file_path=file_path,
                            line_number=line_num,
                            vulnerability_type=VulnerabilityType.HARDCODED_SECRETS,
                            security_level=SecurityLevel.CRITICAL,
                            description="Обнаружен хардкод секрета в коде",
                            recommendation="Используйте переменные окружения или безопасное хранилище секретов",
                            code_snippet=line.strip(),
                            cwe_id="CWE-798",
                            owasp_category="A07:2021 – Identification and Authentication Failures"
                        )
                        issues.append(issue)
            
        except Exception as e:
            logger.error(f"Ошибка сканирования файла {file_path}: {e}")
        
        return issues
    
    def _get_security_level(self, vuln_type: VulnerabilityType) -> SecurityLevel:
        """Получение уровня безопасности для типа уязвимости"""
        critical_types = {
            VulnerabilityType.HARDCODED_SECRETS,
            VulnerabilityType.CODE_INJECTION,
            VulnerabilityType.SQL_INJECTION,
            VulnerabilityType.COMMAND_INJECTION
        }
        
        high_types = {
            VulnerabilityType.XSS,
            VulnerabilityType.PATH_TRAVERSAL,
            VulnerabilityType.INSECURE_DESERIALIZATION,
            VulnerabilityType.MISSING_AUTHENTICATION,
            VulnerabilityType.INSECURE_REDIRECT,
            VulnerabilityType.WEAK_CRYPTO
        }
        
        medium_types = {
            VulnerabilityType.CSRF,
            VulnerabilityType.INFORMATION_DISCLOSURE,
            VulnerabilityType.WEAK_RANDOMNESS,
            VulnerabilityType.INSECURE_COMMUNICATION,
            VulnerabilityType.INSECURE_STORAGE,
            VulnerabilityType.MISSING_ENCRYPTION
        }
        
        if vuln_type in critical_types:
            return SecurityLevel.CRITICAL
        elif vuln_type in high_types:
            return SecurityLevel.HIGH
        elif vuln_type in medium_types:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW
    
    def _get_description(self, vuln_type: VulnerabilityType) -> str:
        """Получение описания уязвимости"""
        descriptions = {
            VulnerabilityType.SQL_INJECTION: "Возможна SQL инъекция",
            VulnerabilityType.XSS: "Возможна XSS атака",
            VulnerabilityType.CSRF: "Отсутствует защита от CSRF",
            VulnerabilityType.PATH_TRAVERSAL: "Возможен path traversal",
            VulnerabilityType.CODE_INJECTION: "Возможна инъекция кода",
            VulnerabilityType.HARDCODED_SECRETS: "Хардкод секретов в коде",
            VulnerabilityType.WEAK_CRYPTO: "Слабое шифрование",
            VulnerabilityType.INSECURE_DESERIALIZATION: "Небезопасная десериализация",
            VulnerabilityType.MISSING_AUTHENTICATION: "Отсутствует аутентификация",
            VulnerabilityType.MISSING_AUTHORIZATION: "Отсутствует авторизация",
            VulnerabilityType.INSECURE_REDIRECT: "Небезопасное перенаправление",
            VulnerabilityType.INFORMATION_DISCLOSURE: "Утечка информации",
            VulnerabilityType.WEAK_RANDOMNESS: "Слабая генерация случайных чисел",
            VulnerabilityType.TIMING_ATTACK: "Уязвимость к timing атакам",
            VulnerabilityType.BUFFER_OVERFLOW: "Возможен buffer overflow",
            VulnerabilityType.MEMORY_LEAK: "Возможна утечка памяти",
            VulnerabilityType.RACE_CONDITION: "Race condition",
            VulnerabilityType.LOG_INJECTION: "Возможна инъекция в логи",
            VulnerabilityType.COMMAND_INJECTION: "Возможна инъекция команд",
            VulnerabilityType.LDAP_INJECTION: "Возможна LDAP инъекция",
            VulnerabilityType.XXE: "XXE уязвимость",
            VulnerabilityType.SSRF: "SSRF уязвимость",
            VulnerabilityType.BROKEN_ACCESS_CONTROL: "Нарушен контроль доступа",
            VulnerabilityType.SECURITY_MISCONFIGURATION: "Неправильная конфигурация безопасности",
            VulnerabilityType.VULNERABLE_COMPONENTS: "Уязвимые компоненты",
            VulnerabilityType.INSUFFICIENT_LOGGING: "Недостаточное логирование",
            VulnerabilityType.WEAK_PASSWORD_POLICY: "Слабая политика паролей",
            VulnerabilityType.INSECURE_COMMUNICATION: "Небезопасная коммуникация",
            VulnerabilityType.IMPROPER_ERROR_HANDLING: "Неправильная обработка ошибок",
            VulnerabilityType.INSECURE_STORAGE: "Небезопасное хранение",
            VulnerabilityType.MISSING_ENCRYPTION: "Отсутствует шифрование",
            VulnerabilityType.WEAK_SESSION_MANAGEMENT: "Слабое управление сессиями",
            VulnerabilityType.INSECURE_DESIGN: "Небезопасный дизайн",
            VulnerabilityType.UNKNOWN: "Неизвестная уязвимость"
        }
        return descriptions.get(vuln_type, "Неизвестная уязвимость")
    
    def _get_recommendation(self, vuln_type: VulnerabilityType) -> str:
        """Получение рекомендации по исправлению"""
        recommendations = {
            VulnerabilityType.SQL_INJECTION: "Используйте параметризованные запросы",
            VulnerabilityType.XSS: "Экранируйте пользовательский ввод",
            VulnerabilityType.CSRF: "Добавьте CSRF токены",
            VulnerabilityType.PATH_TRAVERSAL: "Валидируйте пути к файлам",
            VulnerabilityType.CODE_INJECTION: "Избегайте динамического выполнения кода",
            VulnerabilityType.HARDCODED_SECRETS: "Используйте переменные окружения",
            VulnerabilityType.WEAK_CRYPTO: "Используйте сильные алгоритмы шифрования",
            VulnerabilityType.INSECURE_DESERIALIZATION: "Избегайте десериализации недоверенных данных",
            VulnerabilityType.MISSING_AUTHENTICATION: "Добавьте аутентификацию",
            VulnerabilityType.MISSING_AUTHORIZATION: "Добавьте авторизацию",
            VulnerabilityType.INSECURE_REDIRECT: "Валидируйте URL перенаправления",
            VulnerabilityType.INFORMATION_DISCLOSURE: "Не логируйте чувствительные данные",
            VulnerabilityType.WEAK_RANDOMNESS: "Используйте криптографически стойкие генераторы",
            VulnerabilityType.TIMING_ATTACK: "Используйте константное время для сравнений",
            VulnerabilityType.BUFFER_OVERFLOW: "Проверяйте границы буферов",
            VulnerabilityType.MEMORY_LEAK: "Освобождайте память после использования",
            VulnerabilityType.RACE_CONDITION: "Используйте блокировки для критических секций",
            VulnerabilityType.LOG_INJECTION: "Экранируйте данные перед логированием",
            VulnerabilityType.COMMAND_INJECTION: "Валидируйте и экранируйте команды",
            VulnerabilityType.LDAP_INJECTION: "Используйте параметризованные LDAP запросы",
            VulnerabilityType.XXE: "Отключите обработку внешних сущностей",
            VulnerabilityType.SSRF: "Валидируйте URL запросов",
            VulnerabilityType.BROKEN_ACCESS_CONTROL: "Реализуйте правильный контроль доступа",
            VulnerabilityType.SECURITY_MISCONFIGURATION: "Исправьте конфигурацию безопасности",
            VulnerabilityType.VULNERABLE_COMPONENTS: "Обновите уязвимые компоненты",
            VulnerabilityType.INSUFFICIENT_LOGGING: "Добавьте детальное логирование",
            VulnerabilityType.WEAK_PASSWORD_POLICY: "Усильте политику паролей",
            VulnerabilityType.INSECURE_COMMUNICATION: "Используйте HTTPS/TLS",
            VulnerabilityType.IMPROPER_ERROR_HANDLING: "Улучшите обработку ошибок",
            VulnerabilityType.INSECURE_STORAGE: "Шифруйте чувствительные данные",
            VulnerabilityType.MISSING_ENCRYPTION: "Добавьте шифрование данных",
            VulnerabilityType.WEAK_SESSION_MANAGEMENT: "Улучшите управление сессиями",
            VulnerabilityType.INSECURE_DESIGN: "Пересмотрите архитектуру безопасности",
            VulnerabilityType.UNKNOWN: "Проверьте код на безопасность"
        }
        return recommendations.get(vuln_type, "Проверьте код на безопасность")
    
    def _get_cwe_id(self, vuln_type: VulnerabilityType) -> str:
        """Получение CWE ID для уязвимости"""
        cwe_mapping = {
            VulnerabilityType.SQL_INJECTION: "CWE-89",
            VulnerabilityType.XSS: "CWE-79",
            VulnerabilityType.CSRF: "CWE-352",
            VulnerabilityType.PATH_TRAVERSAL: "CWE-22",
            VulnerabilityType.CODE_INJECTION: "CWE-94",
            VulnerabilityType.HARDCODED_SECRETS: "CWE-798",
            VulnerabilityType.WEAK_CRYPTO: "CWE-327",
            VulnerabilityType.INSECURE_DESERIALIZATION: "CWE-502",
            VulnerabilityType.MISSING_AUTHENTICATION: "CWE-306",
            VulnerabilityType.MISSING_AUTHORIZATION: "CWE-862",
            VulnerabilityType.INSECURE_REDIRECT: "CWE-601",
            VulnerabilityType.INFORMATION_DISCLOSURE: "CWE-200",
            VulnerabilityType.WEAK_RANDOMNESS: "CWE-330",
            VulnerabilityType.TIMING_ATTACK: "CWE-208",
            VulnerabilityType.BUFFER_OVERFLOW: "CWE-120",
            VulnerabilityType.MEMORY_LEAK: "CWE-401",
            VulnerabilityType.RACE_CONDITION: "CWE-362",
            VulnerabilityType.LOG_INJECTION: "CWE-117",
            VulnerabilityType.COMMAND_INJECTION: "CWE-78",
            VulnerabilityType.LDAP_INJECTION: "CWE-90",
            VulnerabilityType.XXE: "CWE-611",
            VulnerabilityType.SSRF: "CWE-918",
            VulnerabilityType.BROKEN_ACCESS_CONTROL: "CWE-284",
            VulnerabilityType.SECURITY_MISCONFIGURATION: "CWE-16",
            VulnerabilityType.VULNERABLE_COMPONENTS: "CWE-1104",
            VulnerabilityType.INSUFFICIENT_LOGGING: "CWE-778",
            VulnerabilityType.WEAK_PASSWORD_POLICY: "CWE-521",
            VulnerabilityType.INSECURE_COMMUNICATION: "CWE-319",
            VulnerabilityType.IMPROPER_ERROR_HANDLING: "CWE-755",
            VulnerabilityType.INSECURE_STORAGE: "CWE-922",
            VulnerabilityType.MISSING_ENCRYPTION: "CWE-311",
            VulnerabilityType.WEAK_SESSION_MANAGEMENT: "CWE-613",
            VulnerabilityType.INSECURE_DESIGN: "CWE-1021",
            VulnerabilityType.UNKNOWN: "CWE-000"
        }
        return cwe_mapping.get(vuln_type, "CWE-000")
    
    def _get_owasp_category(self, vuln_type: VulnerabilityType) -> str:
        """Получение OWASP категории для уязвимости"""
        owasp_mapping = {
            VulnerabilityType.SQL_INJECTION: "A03:2021 – Injection",
            VulnerabilityType.XSS: "A03:2021 – Injection",
            VulnerabilityType.CSRF: "A01:2021 – Broken Access Control",
            VulnerabilityType.PATH_TRAVERSAL: "A01:2021 – Broken Access Control",
            VulnerabilityType.CODE_INJECTION: "A03:2021 – Injection",
            VulnerabilityType.HARDCODED_SECRETS: "A07:2021 – Identification and Authentication Failures",
            VulnerabilityType.WEAK_CRYPTO: "A02:2021 – Cryptographic Failures",
            VulnerabilityType.INSECURE_DESERIALIZATION: "A08:2021 – Software and Data Integrity Failures",
            VulnerabilityType.MISSING_AUTHENTICATION: "A07:2021 – Identification and Authentication Failures",
            VulnerabilityType.MISSING_AUTHORIZATION: "A01:2021 – Broken Access Control",
            VulnerabilityType.INSECURE_REDIRECT: "A01:2021 – Broken Access Control",
            VulnerabilityType.INFORMATION_DISCLOSURE: "A09:2021 – Security Logging and Monitoring Failures",
            VulnerabilityType.WEAK_RANDOMNESS: "A02:2021 – Cryptographic Failures",
            VulnerabilityType.TIMING_ATTACK: "A02:2021 – Cryptographic Failures",
            VulnerabilityType.BUFFER_OVERFLOW: "A06:2021 – Vulnerable and Outdated Components",
            VulnerabilityType.MEMORY_LEAK: "A06:2021 – Vulnerable and Outdated Components",
            VulnerabilityType.RACE_CONDITION: "A04:2021 – Insecure Design",
            VulnerabilityType.LOG_INJECTION: "A09:2021 – Security Logging and Monitoring Failures",
            VulnerabilityType.COMMAND_INJECTION: "A03:2021 – Injection",
            VulnerabilityType.LDAP_INJECTION: "A03:2021 – Injection",
            VulnerabilityType.XXE: "A05:2021 – Security Misconfiguration",
            VulnerabilityType.SSRF: "A10:2021 – Server-Side Request Forgery",
            VulnerabilityType.BROKEN_ACCESS_CONTROL: "A01:2021 – Broken Access Control",
            VulnerabilityType.SECURITY_MISCONFIGURATION: "A05:2021 – Security Misconfiguration",
            VulnerabilityType.VULNERABLE_COMPONENTS: "A06:2021 – Vulnerable and Outdated Components",
            VulnerabilityType.INSUFFICIENT_LOGGING: "A09:2021 – Security Logging and Monitoring Failures",
            VulnerabilityType.WEAK_PASSWORD_POLICY: "A07:2021 – Identification and Authentication Failures",
            VulnerabilityType.INSECURE_COMMUNICATION: "A02:2021 – Cryptographic Failures",
            VulnerabilityType.IMPROPER_ERROR_HANDLING: "A04:2021 – Insecure Design",
            VulnerabilityType.INSECURE_STORAGE: "A02:2021 – Cryptographic Failures",
            VulnerabilityType.MISSING_ENCRYPTION: "A02:2021 – Cryptographic Failures",
            VulnerabilityType.WEAK_SESSION_MANAGEMENT: "A07:2021 – Identification and Authentication Failures",
            VulnerabilityType.INSECURE_DESIGN: "A04:2021 – Insecure Design",
            VulnerabilityType.UNKNOWN: "A04:2021 – Insecure Design"
        }
        return owasp_mapping.get(vuln_type, "A04:2021 – Insecure Design")
    
    def scan_directory(self, directory: str) -> List[SecurityIssue]:
        """Сканирование директории на уязвимости"""
        all_issues = []
        
        for root, dirs, files in os.walk(directory):
            # Пропускаем служебные директории
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.html', '.css', '.json', '.yaml', '.yml', '.xml', '.sql')):
                    file_path = os.path.join(root, file)
                    issues = self.scan_file(file_path)
                    all_issues.extend(issues)
        
        return all_issues
    
    def run_comprehensive_audit(self) -> SecurityAuditResult:
        """Запуск комплексного аудита безопасности"""
        start_time = datetime.now()
        
        print("🔍 ЗАПУСК КОМПЛЕКСНОГО АУДИТА БЕЗОПАСНОСТИ ALADDIN")
        print("=" * 60)
        
        # Сканирование всех файлов
        print("📁 Сканирование файлов...")
        all_issues = self.scan_directory(self.project_root)
        
        # Подсчет статистики
        total_files = self._count_files()
        total_issues = len(all_issues)
        
        critical_issues = len([i for i in all_issues if i.security_level == SecurityLevel.CRITICAL])
        high_issues = len([i for i in all_issues if i.security_level == SecurityLevel.HIGH])
        medium_issues = len([i for i in all_issues if i.security_level == SecurityLevel.MEDIUM])
        low_issues = len([i for i in all_issues if i.security_level == SecurityLevel.LOW])
        info_issues = len([i for i in all_issues if i.security_level == SecurityLevel.INFO])
        
        # Группировка по типам
        issues_by_type = {}
        for issue in all_issues:
            vuln_type = issue.vulnerability_type
            issues_by_type[vuln_type] = issues_by_type.get(vuln_type, 0) + 1
        
        # Группировка по файлам
        issues_by_file = {}
        for issue in all_issues:
            file_path = issue.file_path
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)
        
        # Расчет оценки безопасности
        security_score = self._calculate_security_score(total_issues, critical_issues, high_issues, medium_issues, low_issues)
        
        # Генерация рекомендаций
        recommendations = self._generate_recommendations(all_issues)
        
        end_time = datetime.now()
        scan_duration = (end_time - start_time).total_seconds()
        
        result = SecurityAuditResult(
            total_files_scanned=total_files,
            total_issues_found=total_issues,
            critical_issues=critical_issues,
            high_issues=high_issues,
            medium_issues=medium_issues,
            low_issues=low_issues,
            info_issues=info_issues,
            issues_by_type=issues_by_type,
            issues_by_file=issues_by_file,
            security_score=security_score,
            recommendations=recommendations,
            scan_timestamp=start_time,
            scan_duration=scan_duration
        )
        
        return result
    
    def _count_files(self) -> int:
        """Подсчет количества файлов для сканирования"""
        count = 0
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
            for file in files:
                if file.endswith(('.py', '.js', '.html', '.css', '.json', '.yaml', '.yml', '.xml', '.sql')):
                    count += 1
        return count
    
    def _calculate_security_score(self, total_issues: int, critical: int, high: int, medium: int, low: int) -> float:
        """Расчет оценки безопасности (0-100)"""
        if total_issues == 0:
            return 100.0
        
        # Веса для разных уровней
        critical_weight = 10.0
        high_weight = 5.0
        medium_weight = 2.0
        low_weight = 1.0
        
        # Расчет штрафа
        penalty = (critical * critical_weight + 
                  high * high_weight + 
                  medium * medium_weight + 
                  low * low_weight)
        
        # Максимальный штраф
        max_penalty = 100.0
        
        # Расчет оценки
        score = max(0.0, 100.0 - (penalty / max_penalty * 100.0))
        
        return round(score, 2)
    
    def _generate_recommendations(self, issues: List[SecurityIssue]) -> List[str]:
        """Генерация рекомендаций по улучшению безопасности"""
        recommendations = []
        
        # Анализ критических проблем
        critical_issues = [i for i in issues if i.security_level == SecurityLevel.CRITICAL]
        if critical_issues:
            recommendations.append("🚨 КРИТИЧНО: Исправьте все критические уязвимости немедленно")
        
        # Анализ по типам уязвимостей
        vuln_counts = {}
        for issue in issues:
            vuln_type = issue.vulnerability_type
            vuln_counts[vuln_type] = vuln_counts.get(vuln_type, 0) + 1
        
        # Рекомендации по наиболее частым уязвимостям
        sorted_vulns = sorted(vuln_counts.items(), key=lambda x: x[1], reverse=True)
        
        for vuln_type, count in sorted_vulns[:5]:
            if count > 0:
                recommendations.append(f"🔧 {vuln_type.value}: {count} случаев - {self._get_recommendation(vuln_type)}")
        
        # Общие рекомендации
        recommendations.extend([
            "📚 Проведите обучение команды по безопасности",
            "🔍 Регулярно проводите аудит безопасности",
            "🛡️ Внедрите автоматизированное тестирование безопасности",
            "📊 Настройте мониторинг безопасности в реальном времени",
            "🔄 Обновляйте зависимости и компоненты",
            "📝 Ведите журнал изменений безопасности",
            "🎯 Создайте план реагирования на инциденты"
        ])
        
        return recommendations
    
    def generate_report(self, result: SecurityAuditResult) -> str:
        """Генерация отчета по аудиту безопасности"""
        report = []
        
        report.append("🔍 ОТЧЕТ ПО АУДИТУ БЕЗОПАСНОСТИ СИСТЕМЫ ALADDIN")
        report.append("=" * 60)
        report.append(f"Время сканирования: {result.scan_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Длительность сканирования: {result.scan_duration:.2f} секунд")
        report.append(f"Файлов просканировано: {result.total_files_scanned}")
        report.append("")
        
        # Общая статистика
        report.append("📊 ОБЩАЯ СТАТИСТИКА:")
        report.append(f"Всего проблем найдено: {result.total_issues_found}")
        report.append(f"Критических: {result.critical_issues}")
        report.append(f"Высокого уровня: {result.high_issues}")
        report.append(f"Среднего уровня: {result.medium_issues}")
        report.append(f"Низкого уровня: {result.low_issues}")
        report.append(f"Информационных: {result.info_issues}")
        report.append("")
        
        # Оценка безопасности
        report.append("�� ОЦЕНКА БЕЗОПАСНОСТИ:")
        score_color = "🟢" if result.security_score >= 80 else "🟡" if result.security_score >= 60 else "🔴"
        report.append(f"{score_color} Общая оценка: {result.security_score}/100")
        
        if result.security_score >= 90:
            report.append("✅ Отличный уровень безопасности!")
        elif result.security_score >= 80:
            report.append("✅ Хороший уровень безопасности")
        elif result.security_score >= 60:
            report.append("⚠️ Удовлетворительный уровень безопасности")
        else:
            report.append("❌ Низкий уровень безопасности - требуется срочное исправление!")
        report.append("")
        
        # Топ уязвимостей
        if result.issues_by_type:
            report.append("🔍 ТОП-5 УЯЗВИМОСТЕЙ:")
            sorted_types = sorted(result.issues_by_type.items(), key=lambda x: x[1], reverse=True)
            for i, (vuln_type, count) in enumerate(sorted_types[:5], 1):
                report.append(f"{i}. {vuln_type.value}: {count} случаев")
            report.append("")
        
        # Топ файлов с проблемами
        if result.issues_by_file:
            report.append("📁 ТОП-10 ФАЙЛОВ С ПРОБЛЕМАМИ:")
            sorted_files = sorted(result.issues_by_file.items(), key=lambda x: len(x[1]), reverse=True)
            for i, (file_path, issues) in enumerate(sorted_files[:10], 1):
                report.append(f"{i}. {file_path}: {len(issues)} проблем")
            report.append("")
        
        # Рекомендации
        report.append("💡 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:")
        for i, rec in enumerate(result.recommendations, 1):
            report.append(f"{i}. {rec}")
        report.append("")
        
        # Детали по критическим проблемам
        critical_issues = [i for i in result.issues_by_file.values() for i in i if i.security_level == SecurityLevel.CRITICAL]
        if critical_issues:
            report.append("🚨 КРИТИЧЕСКИЕ ПРОБЛЕМЫ:")
            for issue in critical_issues[:10]:  # Показываем только первые 10
                report.append(f"• {issue.file_path}:{issue.line_number} - {issue.description}")
                report.append(f"  Рекомендация: {issue.recommendation}")
                report.append(f"  Код: {issue.code_snippet}")
                report.append("")
        
        return "\n".join(report)

# Тестирование
if __name__ == "__main__":
    print("🔍 ЗАПУСК КОМПЛЕКСНОГО АУДИТА БЕЗОПАСНОСТИ")
    print("=" * 60)
    
    # Создание аудитора
    auditor = ComprehensiveSecurityAudit(".")
    
    # Запуск аудита
    result = auditor.run_comprehensive_audit()
    
    # Генерация отчета
    report = auditor.generate_report(result)
    
    # Вывод отчета
    print(report)
    
    # Сохранение отчета
    with open("security_audit_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("📄 Отчет сохранен в файл: security_audit_report.txt")
    print("🎉 АУДИТ БЕЗОПАСНОСТИ ЗАВЕРШЕН!")
