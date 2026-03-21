#!/usr/bin/env python3
"""
Поиск всех защищенных эндпоинтов с get_current_user
"""

import re
import os
from pathlib import Path

protected = []

# Ищем во всех роутерах
routers_dir = Path("app/routers")
for py_file in routers_dir.rglob("*.py"):
    try:
        content = py_file.read_text(encoding='utf-8')
        
        # Проверяем, есть ли get_current_user
        if 'get_current_user' in content or 'Depends(security)' in content:
            # Ищем все @router декораторы
            router_prefix = None
            # Ищем prefix роутера
            prefix_match = re.search(r'router\s*=\s*APIRouter\(prefix=["\']([^"\']+)["\']', content)
            if prefix_match:
                router_prefix = prefix_match.group(1)
            
            # Ищем все эндпоинты
            endpoint_pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
            for match in re.finditer(endpoint_pattern, content):
                method = match.group(1).upper()
                endpoint = match.group(2)
                
                # Проверяем, есть ли get_current_user в функции
                # Находим функцию после декоратора
                func_start = match.end()
                func_end = content.find('\n\n', func_start)
                if func_end == -1:
                    func_end = len(content)
                func_content = content[func_start:func_end]
                
                if 'get_current_user' in func_content or 'Depends(security)' in func_content:
                    full_path = endpoint
                    if router_prefix:
                        full_path = router_prefix + endpoint
                    protected.append((method, full_path, str(py_file)))
    except Exception as e:
        print(f"Ошибка в {py_file}: {e}")

# Выводим результаты
print(f"Найдено защищенных эндпоинтов: {len(protected)}\n")
for method, endpoint, file in sorted(set(protected)):
    print(f"{method:6} {endpoint:60} ({os.path.basename(file)})")
