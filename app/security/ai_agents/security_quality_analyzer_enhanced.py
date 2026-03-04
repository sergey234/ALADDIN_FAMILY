#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЦЕЛЕВАЯ СИСТЕМА КАЧЕСТВА ДЛЯ СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN
Проверяет ТОЛЬКО компоненты системы безопасности:
- Менеджеры (8 классов)
- Агенты (8 классов)
- Боты (8 классов)
- SFM (Safe Function Manager)
- Архитектура безопасности
- Конфигурация безопасности
"""

import ast
import subprocess
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple
import concurrent.futures
import time

# --- КОНФИГУРАЦИЯ ДЛЯ СИСТЕМЫ БЕЗОПАСНОСТИ ---
MAX_LINE_LENGTH = 79
FLAKE8_SAFE_CODES = ["E501", "E302", "E305", "W292", "W293", "W291", "E128", "E129"]

# Ключевые слова безопасности для системы ALADDIN
SECURITY_KEYWORDS = [
    "encrypt",
    "decrypt",
    "auth",
    "authenticate",
    "authorize",
    "permission",
    "security",
    "hash",
    "ssl",
    "tls",
    "cipher",
    "key",
    "token",
    "session",
    "firewall",
    "intrusion",
    "threat",
    "vulnerability",
    "malware",
    "virus",
    "circuit_breaker",
    "monitoring",
    "alert",
    "incident",
    "response",
    "compliance",
    "audit",
    "log",
    "trace",
    "forensic",
    "analysis",
]

# Классы системы безопасности для проверки
SECURITY_CLASSES = [
    "SafeFunctionManager",
    "AnalyticsManager",
    "DashboardManager",
    "MonitorManager",
    "ReportManager",
    "APIGateway",
    "LoadBalancer",
    "UniversalPrivacyManager",
    "BehavioralAnalysisAgent",
    "ThreatDetectionAgent",
    "PasswordSecurityAgent",
    "IncidentResponseAgent",
    "ThreatIntelligenceAgent",
    "NetworkSecurityAgent",
    "DataProtectionAgent",
    "ComplianceAgent",
    "MobileNavigationBot",
    "GamingSecurityBot",
    "EmergencyResponseBot",
    "ParentalControlBot",
    "NotificationBot",
    "WhatsAppSecurityBot",
    "TelegramSecurityBot",
    "InstagramSecurityBot",
    "CircuitBreakerMain",
]

# Функции SFM для проверки
SFM_FUNCTIONS = [
    "register_function",
    "unregister_function",
    "enable_function",
    "disable_function",
    "get_function_status",
    "execute_function",
    "validate_function",
    "backup_function",
    "restore_function",
    "monitor_function",
    "analyze_function",
    "optimize_function",
]

# --- Вспомогательные функции ---


def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Выполняет команду в терминале и возвращает код выхода, stdout, stderr."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def is_security_file(file_path: str) -> bool:
    """Проверяет, является ли файл компонентом системы безопасности."""
    # Исключаем бэкапы и скрипты
    if any(exclude in file_path.lower() for exclude in ["backup", "script", "test", "temp", "old"]):
        return False

    # Проверяем, что файл в директории системы безопасности
    security_dirs = ["security/", "ai_agents/", "bots/", "managers/", "agents/"]
    if not any(security_dir in file_path for security_dir in security_dirs):
        return False

    return True


def classify_flake8_error(error_code: str) -> Dict[str, str]:
    """Классифицирует ошибку flake8 по уровню безопасности и серьезности."""
    if error_code in FLAKE8_SAFE_CODES:
        severity = "low" if error_code.startswith("W") else "medium"
        return {"security_level": "safe", "severity": severity, "category": "formatting", "auto_fixable": True}
    elif error_code.startswith("F"):  # F401, F821 etc.
        return {"security_level": "manual", "severity": "high", "category": "fatal", "auto_fixable": False}
    else:
        return {"security_level": "manual", "severity": "medium", "category": "error", "auto_fixable": False}


def get_flake8_suggestion(error: Dict[str, Any]) -> str:
    """Возвращает предложение по исправлению для ошибки flake8."""
    code = error["code"]
    message = error["message"]
    line = error["line"]

    if code == "E501":
        return f"Строка {line} слишком длинная. Разбейте на несколько строк используя \\ или скобки"
    elif code == "E302":
        return f"Строка {line}: Ожидается 2 пустые строки перед определением"
    elif code == "E305":
        return f"Строка {line}: Ожидается 2 пустые строки после определения"
    elif code == "W292":
        return "Файл не заканчивается переводом строки. Добавьте \\n в конец файла"
    elif code == "W293":
        return f"Строка {line} содержит пробелы в конце. Удалите их"
    elif code == "W291":
        return f"Строка {line} содержит пробелы в конце. Удалите их"
    elif code.startswith("F4"):  # F401
        return f"Строка {line}: Импорт не используется. Удалите или используйте"
    elif code.startswith("F8"):  # F821
        return f"Строка {line}: Неопределенное имя. Проверьте объявление или импорт"
    elif code.startswith("E1"):  # E128, E129
        return f"Строка {line}: Проблема с отступами. Проверьте PEP8"
    else:
        return f"Строка {line}: {message}"


# --- Функции анализа для системы безопасности ---


def analyze_syntax(file_path: str) -> Dict[str, Any]:
    """Анализ синтаксиса."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        ast.parse(source)
        return {"status": "success", "message": "Синтаксис корректен"}
    except SyntaxError as e:
        return {
            "status": "error",
            "message": f"Ошибка синтаксиса: {e}",
            "security_level": "critical",
            "severity": "high",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Неизвестная ошибка синтаксиса: {e}",
            "security_level": "critical",
            "severity": "high",
        }


def analyze_imports(file_path: str) -> Dict[str, Any]:
    """Анализ импортов."""
    file_dir = os.path.dirname(os.path.abspath(file_path))
    module_name = os.path.basename(file_path).replace(".py", "")
    original_sys_path = list(sys.path)
    if file_dir not in sys.path:
        sys.path.insert(0, file_dir)
    try:
        __import__(module_name)
        return {"status": "success", "message": "Импорты корректны"}
    except ImportError as e:
        return {"status": "error", "message": f"Ошибка импорта: {e}", "security_level": "critical", "severity": "high"}
    except Exception as e:
        return {
            "status": "error",
            "message": f"Неизвестная ошибка импорта: {e}",
            "security_level": "critical",
            "severity": "high",
        }
    finally:
        sys.path = original_sys_path


def analyze_flake8(file_path: str) -> Dict[str, Any]:
    """Анализ flake8."""
    _, stdout, _ = run_command(["flake8", file_path])
    errors = []
    for line in stdout.splitlines():
        parts = line.split(":", 3)
        if len(parts) == 4:
            error_code = parts[3].strip().split(" ")[0]
            classification = classify_flake8_error(error_code)
            errors.append(
                {
                    "line": int(parts[1]),
                    "col": int(parts[2]),
                    "code": error_code,
                    "message": parts[3].strip(),
                    **classification,
                }
            )
    return {
        "status": "success" if not errors else "warning",
        "errors": errors,
        "message": f"Найдено {len(errors)} ошибок flake8",
    }


def analyze_security_keywords(file_path: str) -> Dict[str, Any]:
    """Поиск ключевых слов безопасности."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    found_keywords = []
    for keyword in SECURITY_KEYWORDS:
        if keyword in content:
            found_keywords.append(keyword)
    return {
        "status": "success" if found_keywords else "info",
        "found_keywords": found_keywords,
        "message": f"Найдено {len(found_keywords)} ключевых слов безопасности",
    }


def analyze_security_classes(file_path: str) -> Dict[str, Any]:
    """Проверка наличия классов системы безопасности."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    found_classes = []
    for class_name in SECURITY_CLASSES:
        if f"class {class_name}" in content:
            found_classes.append(class_name)
    return {
        "status": "success" if found_classes else "warning",
        "found_classes": found_classes,
        "message": f"Найдено {len(found_classes)} классов системы безопасности",
    }


def analyze_sfm_functions(file_path: str) -> Dict[str, Any]:
    """Проверка SFM реестра и количества зарегистрированных функций."""
    # Получаем имя файла без расширения
    file_name = os.path.basename(file_path).replace(".py", "")

    # Загружаем SFM реестр
    sfm_registry_path = "data/sfm/function_registry.json"
    if os.path.exists(sfm_registry_path):
        try:
            with open(sfm_registry_path, "r", encoding="utf-8") as f:
                sfm_data = json.load(f)

            # Получаем общую статистику SFM
            functions = sfm_data.get("functions", {})
            total_functions = len(functions)

            # Проверяем, зарегистрирована ли текущая функция
            is_registered = file_name in functions
            function_data = functions.get(file_name, {}) if is_registered else {}

            # Статистика по статусам
            active_functions = len([f for f in functions.values() if f.get("status") == "active"])
            critical_functions = len([f for f in functions.values() if f.get("is_critical", False)])

            return {
                "status": "success",
                "total_sfm_functions": total_functions,
                "active_functions": active_functions,
                "critical_functions": critical_functions,
                "is_current_registered": is_registered,
                "current_function_data": function_data,
                "message": (
                    f"SFM реестр: {total_functions} функций, "
                    f"{active_functions} активных, {critical_functions} критических"
                ),
            }
        except Exception as e:
            return {"status": "error", "total_sfm_functions": 0, "message": f"Ошибка чтения SFM реестра: {e}"}
    else:
        return {"status": "error", "total_sfm_functions": 0, "message": "SFM реестр не найден"}


def analyze_docstrings(file_path: str) -> Dict[str, Any]:
    """Проверка наличия docstrings."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    missing_docstrings = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            if not (ast.get_docstring(node)):
                missing_docstrings.append(f"Отсутствует docstring для {node.name} (строка {node.lineno})")
    return {
        "status": "success" if not missing_docstrings else "warning",
        "missing_docstrings": missing_docstrings,
        "message": f"Найдено {len(missing_docstrings)} отсутствующих docstring",
    }


def analyze_type_hints(file_path: str) -> Dict[str, Any]:
    """Проверка наличия type hints (базовая)."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    missing_type_hints = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.returns:
                missing_type_hints.append(
                    f"Отсутствует тип возвращаемого значения для функции {node.name} (строка {node.lineno})"
                )
            for arg in node.args.args:
                if arg.arg != "self" and not arg.annotation:
                    missing_type_hints.append(
                        f"Отсутствует тип для аргумента '{arg.arg}' в функции {node.name} (строка {node.lineno})"
                    )
    return {
        "status": "success" if not missing_type_hints else "warning",
        "missing_type_hints": missing_type_hints,
        "message": f"Найдено {len(missing_type_hints)} отсутствующих type hints",
    }


def analyze_complexity(file_path: str) -> Dict[str, Any]:
    """Базовый анализ сложности (количество функций/классов)."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    num_functions = 0
    num_classes = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            num_functions += 1
        elif isinstance(node, ast.ClassDef):
            num_classes += 1
    return {
        "status": "info",
        "num_functions": num_functions,
        "num_classes": num_classes,
        "message": f"Функций: {num_functions}, Классов: {num_classes}",
    }


def analyze_file_size(file_path: str) -> Dict[str, Any]:
    """Анализ размера файла и количества строк."""
    size_bytes = os.path.getsize(file_path)
    lines = sum(1 for line in open(file_path, "r", encoding="utf-8"))
    return {
        "status": "info",
        "size_bytes": size_bytes,
        "lines": lines,
        "message": f"Размер: {size_bytes} байт, Строк: {lines}",
    }


def analyze_dependencies(file_path: str) -> Dict[str, Any]:
    """Базовый анализ зависимостей (импортированные модули)."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    dependencies = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                dependencies.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            dependencies.add(node.module.split(".")[0])
    return {"status": "info", "dependencies": list(dependencies), "message": f"Зависимости: {len(dependencies)}"}


# --- Основная система качества для системы безопасности ---


def security_quality_analyzer(file_path: str) -> Dict[str, Any]:
    """
    ЦЕЛЕВАЯ СИСТЕМА КАЧЕСТВА ДЛЯ СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN.
    Проверяет ТОЛЬКО компоненты системы безопасности.
    """
    print("🛡️ ЦЕЛЕВАЯ СИСТЕМА КАЧЕСТВА ДЛЯ СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN")
    print("=" * 80)
    print(f"Анализируем файл: {file_path}\n")

    # Проверяем, что файл относится к системе безопасности
    if not is_security_file(file_path):
        print("❌ ОШИБКА: Файл не является компонентом системы безопасности!")
        print("❌ Исключены: бэкапы, скрипты, тесты, временные файлы")
        print("✅ Разрешены: security/, ai_agents/, bots/, managers/, agents/")
        return {"error": "Файл не является компонентом системы безопасности"}

    start_time = time.time()

    analysis_tasks = {
        "syntax": analyze_syntax,
        "imports": analyze_imports,
        "flake8": analyze_flake8,
        "security_keywords": analyze_security_keywords,
        "security_classes": analyze_security_classes,
        "sfm_functions": analyze_sfm_functions,
        "docstrings": analyze_docstrings,
        "type_hints": analyze_type_hints,
        "complexity": analyze_complexity,
        "file_info": analyze_file_size,
        "dependencies": analyze_dependencies,
    }

    results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_analysis = {executor.submit(task_func, file_path): name for name, task_func in analysis_tasks.items()}
        for future in concurrent.futures.as_completed(future_to_analysis):
            name = future_to_analysis[future]
            try:
                results[name] = future.result()
            except Exception as exc:
                results[name] = {"status": "error", "message": f"Ошибка при выполнении {name}: {exc}"}

    end_time = time.time()
    total_time = end_time - start_time

    # Агрегация результатов
    flake8_errors = results.get("flake8", {}).get("errors", [])
    total_errors = len(flake8_errors)
    safe_errors = [e for e in flake8_errors if e.get("security_level") == "safe"]
    safe_to_fix_errors = len(safe_errors)
    manual_review_errors = total_errors - safe_to_fix_errors

    security_keywords = results.get("security_keywords", {}).get("found_keywords", [])
    security_keywords_found = len(security_keywords)

    security_classes = results.get("security_classes", {}).get("found_classes", [])
    security_classes_found = len(security_classes)

    sfm_functions = results.get("sfm_functions", {})
    sfm_total_functions = sfm_functions.get("total_sfm_functions", 0)
    sfm_active_functions = sfm_functions.get("active_functions", 0)
    sfm_critical_functions = sfm_functions.get("critical_functions", 0)
    is_sfm_registered = sfm_functions.get("is_current_registered", False)

    # Расчет общего балла качества для системы безопасности
    quality_score = 100.0

    syntax_status = results.get("syntax", {}).get("status")
    if syntax_status == "error":
        quality_score -= 30

    imports_status = results.get("imports", {}).get("status")
    if imports_status == "error":
        quality_score -= 20

    # Каждая ошибка flake8 снижает балл
    quality_score -= total_errors * 1.5

    missing_docstrings = results.get("docstrings", {}).get("missing_docstrings")
    if missing_docstrings:
        quality_score -= len(missing_docstrings) * 0.5

    missing_type_hints = results.get("type_hints", {}).get("missing_type_hints")
    if missing_type_hints:
        quality_score -= len(missing_type_hints) * 0.3

    # Бонусы за компоненты системы безопасности
    if security_classes_found > 0:
        quality_score += 5
    if is_sfm_registered:
        quality_score += 5
    if security_keywords_found > 5:
        quality_score += 5

    quality_score = max(0, min(100, quality_score))  # Ограничиваем 0-100

    report = {
        "file": file_path,
        "timestamp": datetime.now().isoformat(),
        "total_analysis_time_seconds": total_time,
        "overall_quality_score": round(quality_score, 1),
        "analysis_details": results,
        "summary": {
            "total_flake8_errors": total_errors,
            "safe_to_fix_errors": safe_to_fix_errors,
            "manual_review_errors": manual_review_errors,
            "security_keywords_found": security_keywords_found,
            "security_classes_found": security_classes_found,
            "sfm_total_functions": sfm_total_functions,
            "sfm_active_functions": sfm_active_functions,
            "sfm_critical_functions": sfm_critical_functions,
            "is_sfm_registered": is_sfm_registered,
            "syntax_ok": results.get("syntax", {}).get("status") == "success",
            "imports_ok": results.get("imports", {}).get("status") == "success",
            "docstrings_ok": results.get("docstrings", {}).get("status") == "success",
            "type_hints_ok": results.get("type_hints", {}).get("status") == "success",
        },
        "recommendations": [],
        "fix_plan": {"safe_auto_fixes": [], "manual_fixes_required": []},
    }

    if not report["summary"]["syntax_ok"]:
        report["recommendations"].append("Исправьте критические синтаксические ошибки.")
    if not report["summary"]["imports_ok"]:
        report["recommendations"].append("Исправьте критические ошибки импорта.")
    if total_errors > 0:
        report["recommendations"].append(f"Исправьте {total_errors} ошибок flake8.")
    if security_classes_found == 0:
        report["recommendations"].append("Добавьте классы системы безопасности.")
    if not is_sfm_registered:
        report["recommendations"].append("Зарегистрируйте функцию в SFM реестре.")
    if not report["summary"]["docstrings_ok"]:
        report["recommendations"].append("Добавьте отсутствующие docstrings для улучшения документации.")
    if not report["summary"]["type_hints_ok"]:
        report["recommendations"].append("Добавьте отсутствующие type hints для улучшения читаемости и надежности.")

    if not report["recommendations"]:
        report["recommendations"].append("Компонент системы безопасности в отличном состоянии!")

    # Формирование плана исправлений
    for error in results.get("flake8", {}).get("errors", []):
        if error.get("auto_fixable"):
            report["fix_plan"]["safe_auto_fixes"].append(
                {
                    "line": error["line"],
                    "code": error["code"],
                    "message": error["message"],
                    "suggestion": get_flake8_suggestion(error),
                }
            )
        else:
            report["fix_plan"]["manual_fixes_required"].append(
                {
                    "line": error["line"],
                    "code": error["code"],
                    "message": error["message"],
                    "suggestion": get_flake8_suggestion(error),
                    "security_level": error["security_level"],
                }
            )

    print("\n✅ Анализ системы безопасности завершен успешно!")
    print(f"📊 Общий балл: {report['overall_quality_score']}")
    print(f"📁 Файл: {report['file']}")
    print(f"📏 Строк: {report['analysis_details']['file_info']['lines']}")
    print(f"📊 Размер: {report['analysis_details']['file_info']['size_bytes']} байт")
    print(f"🛡️ Классов безопасности: {security_classes_found}")
    print(f"🔧 Всего SFM функций: {sfm_total_functions}")
    print(f"🔧 Активных SFM функций: {sfm_active_functions}")
    print(f"🔧 Критических SFM функций: {sfm_critical_functions}")
    print(f"🔧 Текущая функция в SFM: {'✅ Да' if is_sfm_registered else '❌ Нет'}")
    print(f"🔑 Ключевых слов безопасности: {security_keywords_found}")

    # Сохранение детального отчета
    report_filename = f"security_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path = os.path.join("formatting_work", report_filename)
    os.makedirs("formatting_work", exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"📄 Детальный отчет сохранен: {report_path}")

    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 security_quality_analyzer.py <file_path>")
        print("Проверяет ТОЛЬКО компоненты системы безопасности!")
        sys.exit(1)

    file_to_analyze = sys.argv[1]
    if not os.path.exists(file_to_analyze):
        print(f"Ошибка: Файл не найден по пути: {file_to_analyze}")
        sys.exit(1)

    security_quality_analyzer(file_to_analyze)
