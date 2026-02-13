#!/usr/bin/env python3
"""
Скрипт для анализа всех роутеров и проверки их подключения в main.py
"""
import re
import os
from pathlib import Path
from collections import defaultdict

def find_all_router_files(base_path):
    """Найти все файлы роутеров"""
    router_files = []
    for root, dirs, files in os.walk(base_path):
        # Пропускаем venv и другие служебные директории
        if 'venv' in root or '__pycache__' in root or '.git' in root:
            continue
        
        for file in files:
            if file.endswith('_router.py') or file.endswith('router.py'):
                full_path = os.path.join(root, file)
                router_files.append(full_path)
    
    return sorted(router_files)

def extract_router_name(file_path):
    """Извлечь имя роутера из пути файла"""
    filename = os.path.basename(file_path)
    # Убираем расширение
    name = filename.replace('.py', '')
    return name

def analyze_main_py(main_py_path):
    """Проанализировать main.py и найти все подключенные роутеры"""
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Найти все include_router
    include_pattern = r'app\.include_router\(([^,)]+)'
    includes = re.findall(include_pattern, content)
    
    # Найти все импорты роутеров
    import_pattern = r'from\s+([^\s]+)\s+import\s+router\s+as\s+(\w+)'
    imports = re.findall(import_pattern, content)
    
    # Найти security_routers словарь
    security_routers_pattern = r"security_routers\['([^']+)'\]\s*=\s*(\w+)"
    security_routers = re.findall(security_routers_pattern, content)
    
    # Найти все переменные с router в названии
    router_vars_pattern = r'(\w+router\w*)\s*='
    router_vars = re.findall(router_vars_pattern, content, re.IGNORECASE)
    
    return {
        'includes': includes,
        'imports': imports,
        'security_routers': security_routers,
        'router_vars': router_vars
    }

def main():
    base_path = '/opt/aladdin-backend'
    main_py_path = os.path.join(base_path, 'main.py')
    
    print("=" * 80)
    print("АНАЛИЗ РОУТЕРОВ В ALADDIN BACKEND")
    print("=" * 80)
    print()
    
    # 1. Найти все router файлы
    print("1. ПОИСК ВСЕХ ROUTER ФАЙЛОВ")
    print("-" * 80)
    router_files = find_all_router_files(base_path)
    print(f"Найдено router файлов: {len(router_files)}")
    print()
    
    router_info = {}
    for router_file in router_files:
        rel_path = os.path.relpath(router_file, base_path)
        name = extract_router_name(router_file)
        router_info[name] = {
            'file': rel_path,
            'full_path': router_file
        }
        print(f"  ✅ {name:40} -> {rel_path}")
    
    print()
    
    # 2. Анализ main.py
    print("2. АНАЛИЗ ПОДКЛЮЧЕНИЙ В main.py")
    print("-" * 80)
    analysis = analyze_main_py(main_py_path)
    
    print(f"Найдено app.include_router(): {len(analysis['includes'])}")
    print(f"Найдено импортов router: {len(analysis['imports'])}")
    print(f"Найдено security_routers: {len(analysis['security_routers'])}")
    print()
    
    # 3. Проверка подключения каждого роутера
    print("3. СТАТУС ПОДКЛЮЧЕНИЯ РОУТЕРОВ")
    print("-" * 80)
    
    connected = []
    not_connected = []
    duplicates = defaultdict(list)
    
    for name, info in router_info.items():
        file_content = ''
        try:
            with open(info['full_path'], 'r', encoding='utf-8') as f:
                file_content = f.read()
        except:
            pass
        
        # Проверить, есть ли router в файле
        has_router = 'router = APIRouter' in file_content or 'router = Router' in file_content
        
        # Проверить подключение в main.py
        is_connected = False
        connection_method = None
        
        # Проверка через include_router
        for include in analysis['includes']:
            if name.replace('_router', '') in include.lower() or include.lower() in name.lower():
                is_connected = True
                connection_method = f"include_router({include})"
                duplicates[name].append(include)
                break
        
        # Проверка через security_routers
        for sec_name, sec_var in analysis['security_routers']:
            if name.replace('_router', '') in sec_name.lower() or sec_name.lower() in name.replace('_router', ''):
                is_connected = True
                connection_method = f"security_routers['{sec_name}']"
                break
        
        # Проверка через прямые импорты
        for imp_path, imp_var in analysis['imports']:
            if name.replace('_router', '') in imp_path.lower() or name.replace('_router', '') in imp_var.lower():
                is_connected = True
                connection_method = f"import {imp_var} from {imp_path}"
                break
        
        if is_connected:
            connected.append((name, connection_method))
        else:
            not_connected.append(name)
    
    print(f"✅ Подключено: {len(connected)}")
    for name, method in connected:
        print(f"  ✅ {name:40} -> {method}")
    
    print()
    print(f"❌ НЕ подключено: {len(not_connected)}")
    for name in not_connected:
        print(f"  ❌ {name:40}")
    
    print()
    
    # 4. Поиск дубликатов
    print("4. ПОИСК ДУБЛИКАТОВ")
    print("-" * 80)
    duplicate_found = False
    for name, includes in duplicates.items():
        if len(includes) > 1:
            duplicate_found = True
            print(f"  ⚠️ {name}: подключен {len(includes)} раз")
            for inc in includes:
                print(f"      - {inc}")
    
    if not duplicate_found:
        print("  ✅ Дубликатов не найдено")
    
    print()
    
    # 5. Итоговая статистика
    print("5. ИТОГОВАЯ СТАТИСТИКА")
    print("-" * 80)
    print(f"Всего router файлов: {len(router_files)}")
    print(f"Подключено: {len(connected)}")
    print(f"НЕ подключено: {len(not_connected)}")
    print(f"Дубликатов: {sum(1 for v in duplicates.values() if len(v) > 1)}")
    print()
    
    # 6. Рекомендации
    print("6. РЕКОМЕНДАЦИИ")
    print("-" * 80)
    if not_connected:
        print("⚠️ Нужно подключить следующие роутеры:")
        for name in not_connected:
            print(f"  - {name}")
    else:
        print("✅ Все роутеры подключены!")
    
    if duplicate_found:
        print()
        print("⚠️ Найдены дубликаты подключений. Нужно удалить лишние.")
    
    print()
    print("=" * 80)

if __name__ == '__main__':
    main()
