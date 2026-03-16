#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки соответствия endpoints документации
Сравнивает реализованные endpoints с документацией
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Set

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

class Colors:
    """Цвета для вывода в консоль"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(message: str):
    """Вывести успешное сообщение"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str):
    """Вывести сообщение об ошибке"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message: str):
    """Вывести предупреждение"""
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.RESET}")

def print_info(message: str):
    """Вывести информационное сообщение"""
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.RESET}")

def extract_endpoints_from_router(file_path: Path) -> List[Dict]:
    """Извлечь endpoints из роутера"""
    endpoints = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Ищем префикс роутера
        prefix_match = re.search(r'router\s*=\s*APIRouter\(prefix=["\']([^"\']+)["\']', content)
        prefix = prefix_match.group(1) if prefix_match else ""
        
        # Ищем все декораторы @router.get, @router.post и т.д.
        pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            method = match.group(1).upper()
            path = match.group(2)
            full_path = prefix + path
            
            endpoints.append({
                "method": method,
                "path": path,
                "full_path": full_path,
                "file": str(file_path)
            })
    
    except Exception as e:
        print_error(f"Ошибка чтения файла {file_path}: {e}")
    
    return endpoints

def get_expected_endpoints() -> Dict[str, List[str]]:
    """Получить ожидаемые endpoints из документации"""
    # Ожидаемые endpoints для компонентов защиты
    return {
        "dark_web": [
            "GET /api/reports/dark-web/stats",
            "GET /api/reports/dark-web/leaks",
            "GET /api/reports/dark-web/scans",
            "POST /api/reports/dark-web/resolve",
            "POST /api/reports/dark-web/scan/start",
            "POST /api/reports/dark-web/scan/secure",
            "POST /api/reports/dark-web/scan/fast",
            "GET /api/reports/dark-web/health",
        ],
        "identity_theft": [
            "GET /api/reports/identity-theft/stats",
            "GET /api/reports/identity-theft/attempts",
            "POST /api/reports/identity-theft/allow",
            "POST /api/reports/identity-theft/block",
            "POST /api/reports/identity-theft/whitelist",
            "GET /api/reports/identity-theft/health",
        ],
        "location_bubble": [
            "GET /api/reports/privacy/location/stats",
            "GET /api/reports/privacy/location/requests",
            "POST /api/reports/privacy/location/allow",
            "POST /api/reports/privacy/location/block",
            "POST /api/reports/privacy/location/update-accuracy",
            "GET /api/reports/privacy/location/health",
        ],
        "data_cleanup": [
            "GET /api/reports/privacy/cleanup/stats",
            "GET /api/reports/privacy/cleanup/records",
            "POST /api/reports/privacy/cleanup/start",
            "GET /api/reports/privacy/cleanup/health",
        ],
        "anti_tracker": [
            "GET /api/reports/privacy/tracker/stats",
            "GET /api/reports/privacy/tracker/top",
            "POST /api/reports/privacy/tracker/whitelist",
            "GET /api/reports/privacy/tracker/health",
        ],
        "ai_categories": [
            "GET /api/reports/ai-categories/stats",
            "GET /api/reports/ai-categories/reports",
            "POST /api/reports/ai-categories/allow",
            "POST /api/reports/ai-categories/block",
            "GET /api/reports/ai-categories/health",
        ],
    }

def verify_endpoints():
    """Проверить соответствие endpoints документации"""
    print("=" * 60)
    print("ПРОВЕРКА СООТВЕТСТВИЯ ENDPOINTS ДОКУМЕНТАЦИИ")
    print("=" * 60)
    print()
    
    # Путь к роутерам (от корня проекта)
    # Определяем корень проекта относительно текущего файла
    # __file__ = app/database/migrations/verify_endpoints.py
    # Нужно подняться на 4 уровня вверх: migrations -> database -> app -> корень
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent
    routers_dir = project_root / "app" / "security" / "api" / "routers"
    
    # Если не найдено, пробуем найти корень проекта по наличию app/security
    if not routers_dir.exists():
        # Ищем корень проекта, поднимаясь вверх
        check_path = current_file.parent
        for _ in range(10):  # Максимум 10 уровней вверх
            potential_routers = check_path / "app" / "security" / "api" / "routers"
            if potential_routers.exists():
                routers_dir = potential_routers
                break
            check_path = check_path.parent
            if check_path == check_path.parent:  # Достигли корня файловой системы
                break
    
    # Файлы роутеров для проверки
    router_files = {
        "dark_web": routers_dir / "dark_web_monitoring_router.py",
        "identity_theft": routers_dir / "identity_theft_protection_router.py",
        "location_bubble": routers_dir / "location_bubble_router.py",
        "data_cleanup": routers_dir / "data_cleanup_router.py",
        "anti_tracker": routers_dir / "anti_tracker_router.py",
        "ai_categories": routers_dir / "ai_categories_router.py",
    }
    
    # Получаем ожидаемые endpoints
    expected = get_expected_endpoints()
    
    # Извлекаем реализованные endpoints
    implemented = {}
    for component, file_path in router_files.items():
        if file_path.exists():
            implemented[component] = extract_endpoints_from_router(file_path)
        else:
            print_error(f"Файл не найден: {file_path}")
            implemented[component] = []
    
    # Проверяем соответствие
    all_match = True
    
    for component, expected_endpoints in expected.items():
        print(f"\n{'=' * 60}")
        print(f"📋 Компонент: {component.upper().replace('_', ' ')}")
        print("=" * 60)
        
        # Преобразуем ожидаемые endpoints в формат для сравнения
        expected_set = set()
        for ep in expected_endpoints:
            parts = ep.split(" ", 1)
            if len(parts) == 2:
                method, path = parts
                expected_set.add((method, path))
        
        # Преобразуем реализованные endpoints
        implemented_set = set()
        for ep in implemented.get(component, []):
            implemented_set.add((ep["method"], ep["full_path"]))
        
        # Проверяем соответствие
        missing = expected_set - implemented_set
        extra = implemented_set - expected_set
        
        if not missing and not extra:
            print_success(f"Все endpoints соответствуют документации ({len(expected_set)} endpoints)")
        else:
            all_match = False
            
            if missing:
                print_error(f"Отсутствующие endpoints ({len(missing)}):")
                for method, path in sorted(missing):
                    print_error(f"  {method} {path}")
            
            if extra:
                print_warning(f"Дополнительные endpoints ({len(extra)}):")
                for method, path in sorted(extra):
                    print_warning(f"  {method} {path}")
        
        # Выводим список всех реализованных endpoints
        print_info(f"Реализовано endpoints: {len(implemented_set)}")
        for method, path in sorted(implemented_set):
            print(f"  ✅ {method} {path}")
    
    return all_match

def main():
    """Главная функция"""
    try:
        all_match = verify_endpoints()
        
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ")
        print("=" * 60)
        
        if all_match:
            print_success("✅ Все endpoints соответствуют документации!")
            return 0
        else:
            print_warning("⚠️ Обнаружены расхождения с документацией")
            return 1
            
    except Exception as e:
        print_error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
