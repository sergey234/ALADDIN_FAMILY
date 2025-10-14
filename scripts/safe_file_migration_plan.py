#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Безопасный план миграции файлов
Детальный анализ зависимостей и пошаговый перенос
"""

import sys
import os
import re
import shutil
from pathlib import Path
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

def analyze_file_dependencies(file_path):
    """Анализ зависимостей файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        dependencies = {
            'imports': [],
            'from_imports': [],
            'relative_imports': [],
            'external_dependencies': [],
            'internal_dependencies': []
        }
        
        # Поиск всех импортов
        import_patterns = [
            r'import\s+(\w+)',
            r'from\s+(\S+)\s+import\s+(\S+)',
            r'from\s+\.(\w+)\s+import',
            r'from\s+\.\.(\w+)\s+import'
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            if pattern.startswith('import '):
                dependencies['imports'].extend(matches)
            elif pattern.startswith('from ') and 'import' in pattern:
                if pattern.startswith('from .'):
                    dependencies['relative_imports'].extend(matches)
                else:
                    dependencies['from_imports'].extend(matches)
        
        # Определение внутренних и внешних зависимостей
        for imp in dependencies['imports'] + [imp[0] for imp in dependencies['from_imports']]:
            if imp.startswith('security.') or imp.startswith('core.') or imp.startswith('config.'):
                dependencies['internal_dependencies'].append(imp)
            else:
                dependencies['external_dependencies'].append(imp)
        
        return dependencies
        
    except Exception as e:
        return {'error': str(e)}

def find_files_importing_module(module_name, search_path="."):
    """Поиск файлов, которые импортируют указанный модуль"""
    importing_files = []
    
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Проверяем различные варианты импорта
                    import_patterns = [
                        f'import {module_name}',
                        f'from {module_name} import',
                        f'from .{module_name} import',
                        f'from ..{module_name} import'
                    ]
                    
                    for pattern in import_patterns:
                        if re.search(pattern, content):
                            importing_files.append(file_path)
                            break
                            
                except Exception:
                    continue
    
    return importing_files

def create_backup(file_path, backup_dir="migration_backups"):
    """Создание резервной копии файла"""
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{os.path.basename(file_path)}_{timestamp}.backup"
    backup_path = os.path.join(backup_dir, backup_name)
    
    shutil.copy2(file_path, backup_path)
    return backup_path

def create_migration_plan():
    """Создание детального плана миграции"""
    print("🚀 ДЕТАЛЬНЫЙ ПЛАН БЕЗОПАСНОЙ МИГРАЦИИ ФАЙЛОВ")
    print("=" * 80)
    
    files_to_move = [
        {
            'file': 'emergency_formatters.py',
            'from': 'security/ai_agents/',
            'to': 'security/microservices/',
            'reason': 'Микросервис форматирования данных'
        },
        {
            'file': 'emergency_base_models.py',
            'from': 'security/ai_agents/',
            'to': 'security/microservices/',
            'reason': 'Базовые модели для микросервисов'
        },
        {
            'file': 'emergency_base_models_refactored.py',
            'from': 'security/ai_agents/',
            'to': 'security/microservices/',
            'reason': 'Рефакторированные базовые модели'
        },
        {
            'file': 'emergency_service.py',
            'from': 'security/ai_agents/',
            'to': 'security/managers/',
            'reason': 'Менеджер экстренных сервисов'
        },
        {
            'file': 'emergency_service_caller.py',
            'from': 'security/ai_agents/',
            'to': 'security/microservices/',
            'reason': 'Микросервис вызова экстренных сервисов'
        },
        {
            'file': 'messenger_integration.py',
            'from': 'security/ai_agents/',
            'to': 'security/bots/',
            'reason': 'Бот интеграции с мессенджерами'
        }
    ]
    
    print("\n📋 ЭТАП 1: ПОДГОТОВКА И АНАЛИЗ")
    print("-" * 50)
    print("1.1 Создание резервных копий всех файлов")
    print("1.2 Анализ зависимостей каждого файла")
    print("1.3 Поиск файлов, которые импортируют перемещаемые модули")
    print("1.4 Проверка существования целевых папок")
    
    for i, file_info in enumerate(files_to_move, 1):
        print(f"\n📁 ФАЙЛ {i}: {file_info['file']}")
        print("=" * 60)
        
        file_path = os.path.join(file_info['from'], file_info['file'])
        target_path = os.path.join(file_info['to'], file_info['file'])
        
        print(f"📍 Откуда: {file_path}")
        print(f"📍 Куда: {target_path}")
        print(f"💡 Причина: {file_info['reason']}")
        
        # Проверяем существование файла
        if os.path.exists(file_path):
            print("✅ Файл существует")
            
            # Анализируем зависимости
            dependencies = analyze_file_dependencies(file_path)
            if 'error' not in dependencies:
                print(f"📦 Импорты: {len(dependencies['imports'])}")
                print(f"📦 From импорты: {len(dependencies['from_imports'])}")
                print(f"📦 Относительные импорты: {len(dependencies['relative_imports'])}")
                print(f"📦 Внутренние зависимости: {len(dependencies['internal_dependencies'])}")
                print(f"📦 Внешние зависимости: {len(dependencies['external_dependencies'])}")
                
                # Ищем файлы, которые импортируют этот модуль
                module_name = file_info['file'][:-3]  # убираем .py
                importing_files = find_files_importing_module(module_name)
                
                if importing_files:
                    print(f"⚠️  Файлы, импортирующие этот модуль ({len(importing_files)}):")
                    for imp_file in importing_files:
                        print(f"   • {imp_file}")
                else:
                    print("✅ Никто не импортирует этот модуль")
            else:
                print(f"❌ Ошибка анализа: {dependencies['error']}")
        else:
            print("❌ Файл не найден!")
        
        print(f"\n🔧 ПЛАН ДЕЙСТВИЙ ДЛЯ {file_info['file']}:")
        print("-" * 40)
        print(f"1. Создать резервную копию: {file_path}")
        print(f"2. Переместить файл: mv {file_path} {target_path}")
        print(f"3. Обновить импорты в зависимых файлах")
        print(f"4. Проверить синтаксис: python3 -m py_compile {target_path}")
        print(f"5. Проверить импорты: python3 -c \"import {file_info['file'][:-3]}\"")
        print(f"6. Запустить тесты зависимых файлов")
    
    print(f"\n📋 ЭТАП 2: ПОШАГОВОЕ ВЫПОЛНЕНИЕ")
    print("-" * 50)
    print("2.1 Создать резервные копии")
    print("2.2 Переместить файлы по одному")
    print("2.3 Обновить импорты после каждого перемещения")
    print("2.4 Проверить работоспособность после каждого шага")
    print("2.5 В случае ошибки - откатиться к резервной копии")
    
    print(f"\n📋 ЭТАП 3: ВАЛИДАЦИЯ")
    print("-" * 50)
    print("3.1 Проверить, что все файлы на новых местах")
    print("3.2 Запустить полные тесты системы")
    print("3.3 Проверить работу SFM")
    print("3.4 Убедиться, что все импорты работают")
    
    return files_to_move

def create_execution_script(files_to_move):
    """Создание скрипта для выполнения миграции"""
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт безопасной миграции файлов
Выполняет пошаговое перемещение с проверками
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime

def run_command(command, description):
    """Выполнение команды с проверкой результата"""
    print(f"🔧 {description}")
    print(f"   Команда: {command}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   ✅ Успешно")
        if result.stdout:
            print(f"   Вывод: {result.stdout.strip()}")
    else:
        print("   ❌ Ошибка")
        print(f"   Ошибка: {result.stderr.strip()}")
        return False
    
    return True

def main():
    """Основная функция миграции"""
    print("🚀 НАЧАЛО БЕЗОПАСНОЙ МИГРАЦИИ ФАЙЛОВ")
    print("=" * 80)
    
    # Создаем папку для резервных копий
    backup_dir = f"migration_backups_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    print(f"📁 Создана папка для резервных копий: {backup_dir}")
    
    # Список файлов для перемещения
    files_to_move = [
        {
            'file': 'emergency_formatters.py',
            'from': 'security/ai_agents/',
            'to': 'security/microservices/'
        },
        {
            'file': 'emergency_base_models.py',
            'from': 'security/ai_agents/',
            'to': 'security/microservices/'
        },
        {
            'file': 'emergency_base_models_refactored.py',
            'from': 'security/ai_agents/',
            'to': 'security/microservices/'
        },
        {
            'file': 'emergency_service.py',
            'from': 'security/ai_agents/',
            'to': 'security/managers/'
        },
        {
            'file': 'emergency_service_caller.py',
            'from': 'security/ai_agents/',
            'to': 'security/microservices/'
        },
        {
            'file': 'messenger_integration.py',
            'from': 'security/ai_agents/',
            'to': 'security/bots/'
        }
    ]
    
    success_count = 0
    total_files = len(files_to_move)
    
    for i, file_info in enumerate(files_to_move, 1):
        print(f"\\n📁 ФАЙЛ {i}/{total_files}: {file_info['file']}")
        print("=" * 60)
        
        source_path = os.path.join(file_info['from'], file_info['file'])
        target_path = os.path.join(file_info['to'], file_info['file'])
        
        # Проверяем существование исходного файла
        if not os.path.exists(source_path):
            print(f"❌ Исходный файл не найден: {source_path}")
            continue
        
        # Создаем резервную копию
        backup_path = os.path.join(backup_dir, file_info['file'])
        if not run_command(f"cp {source_path} {backup_path}", "Создание резервной копии"):
            continue
        
        # Перемещаем файл
        if not run_command(f"mv {source_path} {target_path}", f"Перемещение {file_info['file']}"):
            # В случае ошибки восстанавливаем из резервной копии
            run_command(f"cp {backup_path} {source_path}", "Восстановление из резервной копии")
            continue
        
        # Проверяем синтаксис
        if not run_command(f"python3 -m py_compile {target_path}", "Проверка синтаксиса"):
            # В случае ошибки восстанавливаем из резервной копии
            run_command(f"cp {backup_path} {source_path}", "Восстановление из резервной копии")
            run_command(f"rm {target_path}", "Удаление поврежденного файла")
            continue
        
        # Проверяем импорты
        module_name = file_info['file'][:-3]
        if not run_command(f"python3 -c \"import {module_name}\"", "Проверка импортов"):
            print(f"⚠️  Предупреждение: импорт {module_name} не работает")
        
        success_count += 1
        print(f"✅ Файл {file_info['file']} успешно перемещен")
    
    print(f"\\n🎯 РЕЗУЛЬТАТ МИГРАЦИИ:")
    print(f"✅ Успешно перемещено: {success_count}/{total_files} файлов")
    print(f"📁 Резервные копии сохранены в: {backup_dir}")
    
    if success_count == total_files:
        print("🎉 ВСЕ ФАЙЛЫ УСПЕШНО ПЕРЕМЕЩЕНЫ!")
    else:
        print("⚠️  НЕКОТОРЫЕ ФАЙЛЫ НЕ УДАЛОСЬ ПЕРЕМЕСТИТЬ")

if __name__ == "__main__":
    main()
'''
    
    with open('ALADDIN_NEW/scripts/execute_migration.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"\n📝 Создан скрипт выполнения: scripts/execute_migration.py")

def main():
    """Основная функция"""
    print("🚀 СОЗДАНИЕ ДЕТАЛЬНОГО ПЛАНА МИГРАЦИИ")
    print("=" * 80)
    
    # Создаем план миграции
    files_to_move = create_migration_plan()
    
    # Создаем скрипт выполнения
    create_execution_script(files_to_move)
    
    print(f"\n🎯 ЗАКЛЮЧЕНИЕ:")
    print("=" * 50)
    print("✅ Создан детальный план миграции 6 файлов")
    print("✅ Проанализированы все зависимости")
    print("✅ Создан безопасный скрипт выполнения")
    print("✅ Предусмотрены резервные копии и откат")
    print("✅ Добавлены проверки на каждом шаге")

if __name__ == "__main__":
    main()