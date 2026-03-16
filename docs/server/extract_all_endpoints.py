#!/usr/bin/env python3
"""
ИЗВЛЕЧЕНИЕ ВСЕХ ENDPOINTS ИЗ РОУТЕРОВ
--------------------------------------
Извлекает все endpoints из всех роутеров для детального тестирования.

Дата: 2026-03-14
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Any

def extract_endpoints_from_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Извлекает endpoints из файла роутера
    
    Returns:
        Список словарей с информацией об endpoints
    """
    endpoints = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Паттерн для поиска декораторов роутера
        pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
        
        matches = re.finditer(pattern, content, re.IGNORECASE)
        
        for match in matches:
            method = match.group(1).upper()
            path = match.group(2)
            
            # Получаем имя функции после декоратора
            func_pattern = rf'{re.escape(match.group(0))}.*?def\s+(\w+)\('
            func_match = re.search(func_pattern, content, re.DOTALL)
            func_name = func_match.group(1) if func_match else "unknown"
            
            endpoints.append({
                "method": method,
                "path": path,
                "function": func_name,
                "file": os.path.basename(file_path)
            })
    
    except Exception as e:
        print(f"⚠️ Ошибка при чтении {file_path}: {e}")
    
    return endpoints

def find_all_routers(base_path: str) -> List[str]:
    """Находит все файлы роутеров"""
    router_files = []
    
    # Ищем в app/routers/
    app_routers_path = os.path.join(base_path, "app/routers")
    if os.path.exists(app_routers_path):
        for file in os.listdir(app_routers_path):
            if file.endswith(".py") and not file.startswith("__"):
                router_files.append(os.path.join(app_routers_path, file))
    
    # Ищем в security/api/routers/
    security_routers_path = os.path.join(base_path, "security/api/routers")
    if os.path.exists(security_routers_path):
        for file in os.listdir(security_routers_path):
            if file.endswith(".py") and not file.startswith("__"):
                router_files.append(os.path.join(security_routers_path, file))
    
    return router_files

def main():
    """Основная функция"""
    # Определяем базовый путь проекта
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(script_dir, "../..")
    
    print("🔍 Поиск всех роутеров...")
    router_files = find_all_routers(base_path)
    
    print(f"✅ Найдено роутеров: {len(router_files)}")
    print()
    
    all_endpoints = []
    
    for router_file in router_files:
        print(f"📄 Обработка: {os.path.basename(router_file)}")
        endpoints = extract_endpoints_from_file(router_file)
        all_endpoints.extend(endpoints)
        print(f"   Найдено endpoints: {len(endpoints)}")
    
    print()
    print(f"✅ Всего endpoints найдено: {len(all_endpoints)}")
    
    # Сохраняем в JSON
    output_file = os.path.join(script_dir, "all_endpoints.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_endpoints, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Сохранено в: {output_file}")
    
    # Группируем по методам
    by_method = {}
    for endpoint in all_endpoints:
        method = endpoint["method"]
        if method not in by_method:
            by_method[method] = []
        by_method[method].append(endpoint)
    
    print()
    print("📊 Статистика по методам:")
    for method, endpoints in sorted(by_method.items()):
        print(f"   {method}: {len(endpoints)} endpoints")
    
    return all_endpoints

if __name__ == "__main__":
    main()
