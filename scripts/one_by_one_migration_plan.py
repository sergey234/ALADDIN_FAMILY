#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПЛАН ПОШАГОВОЙ МИГРАЦИИ - СТРОГО ПО 1 ФАЙЛУ ЗА РАЗ
С полной проверкой каждого шага
"""

import sys
import os
import re
import shutil
from pathlib import Path
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

def analyze_single_file(file_path):
    """Анализ одного файла перед перемещением"""
    print(f"🔍 АНАЛИЗ ФАЙЛА: {os.path.basename(file_path)}")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print("❌ Файл не найден!")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Анализ содержимого
        classes = re.findall(r'class\s+(\w+)', content)
        functions = re.findall(r'def\s+(\w+)', content)
        imports = re.findall(r'import\s+(\w+)|from\s+(\S+)\s+import', content)
        
        print(f"📊 Статистика файла:")
        print(f"   • Классы: {len(classes)} - {classes}")
        print(f"   • Функции: {len(functions)}")
        print(f"   • Импорты: {len(imports)}")
        
        # Поиск файлов, которые импортируют этот модуль
        module_name = os.path.basename(file_path)[:-3]  # убираем .py
        importing_files = find_files_importing_module(module_name)
        
        if importing_files:
            print(f"⚠️  Файлы, импортирующие этот модуль ({len(importing_files)}):")
            for imp_file in importing_files:
                print(f"   • {imp_file}")
        else:
            print("✅ Никто не импортирует этот модуль")
        
        return {
            'classes': classes,
            'functions': functions,
            'imports': imports,
            'importing_files': importing_files,
            'content': content
        }
        
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        return None

def find_files_importing_module(module_name, search_path="."):
    """Поиск файлов, которые импортируют указанный модуль"""
    importing_files = []
    
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if file.endswith('.py') and file != f"{module_name}.py":
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Проверяем различные варианты импорта
                    import_patterns = [
                        f'import {module_name}',
                        f'from {module_name} import',
                        f'from .{module_name} import',
                        f'from ..{module_name} import',
                        f'from security.ai_agents.{module_name} import',
                        f'from security.microservices.{module_name} import',
                        f'from security.managers.{module_name} import',
                        f'from security.bots.{module_name} import'
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
    print(f"💾 Создана резервная копия: {backup_path}")
    return backup_path

def update_imports_in_file(file_path, old_module_path, new_module_path):
    """Обновление импортов в файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Заменяем импорты
        replacements = [
            (f'from {old_module_path} import', f'from {new_module_path} import'),
            (f'import {old_module_path}', f'import {new_module_path}'),
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Обновлены импорты в {file_path}")
            return True
        else:
            print(f"ℹ️  Импорты в {file_path} не требуют обновления")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка обновления импортов в {file_path}: {e}")
        return False

def execute_single_file_migration(file_info, step_number):
    """Выполнение миграции одного файла"""
    print(f"\n🚀 ШАГ {step_number}: МИГРАЦИЯ {file_info['file']}")
    print("=" * 80)
    
    source_path = os.path.join(file_info['from'], file_info['file'])
    target_path = os.path.join(file_info['to'], file_info['file'])
    
    print(f"📍 Откуда: {source_path}")
    print(f"📍 Куда: {target_path}")
    print(f"💡 Причина: {file_info['reason']}")
    
    # ШАГ 1: Анализ файла
    print(f"\n📋 ШАГ 1: АНАЛИЗ ФАЙЛА")
    print("-" * 40)
    analysis = analyze_single_file(source_path)
    if not analysis:
        return False
    
    # ШАГ 2: Создание резервной копии
    print(f"\n📋 ШАГ 2: СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ")
    print("-" * 40)
    backup_path = create_backup(source_path)
    
    # ШАГ 3: Проверка целевой папки
    print(f"\n📋 ШАГ 3: ПРОВЕРКА ЦЕЛЕВОЙ ПАПКИ")
    print("-" * 40)
    target_dir = os.path.dirname(target_path)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"✅ Создана папка: {target_dir}")
    else:
        print(f"✅ Папка существует: {target_dir}")
    
    # ШАГ 4: Перемещение файла
    print(f"\n📋 ШАГ 4: ПЕРЕМЕЩЕНИЕ ФАЙЛА")
    print("-" * 40)
    try:
        shutil.move(source_path, target_path)
        print(f"✅ Файл перемещен: {source_path} → {target_path}")
    except Exception as e:
        print(f"❌ Ошибка перемещения: {e}")
        # Восстанавливаем из резервной копии
        shutil.copy2(backup_path, source_path)
        print(f"🔄 Восстановлен из резервной копии")
        return False
    
    # ШАГ 5: Проверка синтаксиса
    print(f"\n📋 ШАГ 5: ПРОВЕРКА СИНТАКСИСА")
    print("-" * 40)
    import subprocess
    result = subprocess.run(f"python3 -m py_compile {target_path}", 
                          shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Синтаксис корректен")
    else:
        print(f"❌ Ошибка синтаксиса: {result.stderr}")
        # Восстанавливаем из резервной копии
        shutil.copy2(backup_path, source_path)
        os.remove(target_path)
        print(f"🔄 Восстановлен из резервной копии")
        return False
    
    # ШАГ 6: Обновление импортов в зависимых файлах
    print(f"\n📋 ШАГ 6: ОБНОВЛЕНИЕ ИМПОРТОВ")
    print("-" * 40)
    if analysis['importing_files']:
        module_name = file_info['file'][:-3]
        old_module_path = f"security.ai_agents.{module_name}"
        new_module_path = f"{file_info['to'].replace('/', '.')}.{module_name}"
        
        for imp_file in analysis['importing_files']:
            update_imports_in_file(imp_file, old_module_path, new_module_path)
    else:
        print("ℹ️  Нет файлов, которые импортируют этот модуль")
    
    # ШАГ 7: Финальная проверка
    print(f"\n📋 ШАГ 7: ФИНАЛЬНАЯ ПРОВЕРКА")
    print("-" * 40)
    
    # Проверяем, что файл на новом месте
    if os.path.exists(target_path):
        print("✅ Файл находится в целевой папке")
    else:
        print("❌ Файл не найден в целевой папке")
        return False
    
    # Проверяем, что файл не остался в исходной папке
    if not os.path.exists(source_path):
        print("✅ Файл удален из исходной папки")
    else:
        print("⚠️  Файл остался в исходной папке")
    
    print(f"\n🎉 ФАЙЛ {file_info['file']} УСПЕШНО ПЕРЕМЕЩЕН!")
    print(f"💾 Резервная копия: {backup_path}")
    
    return True

def create_migration_plan():
    """Создание плана миграции"""
    print("🚀 ПЛАН ПОШАГОВОЙ МИГРАЦИИ - СТРОГО ПО 1 ФАЙЛУ ЗА РАЗ")
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
    
    print(f"\n📋 ОБЩИЙ ПЛАН МИГРАЦИИ")
    print("-" * 50)
    print(f"Всего файлов для перемещения: {len(files_to_move)}")
    print(f"Стратегия: СТРОГО ПО 1 ФАЙЛУ ЗА РАЗ")
    print(f"Проверка: ПОЛНАЯ НА КАЖДОМ ШАГЕ")
    print(f"Безопасность: РЕЗЕРВНЫЕ КОПИИ + ОТКАТ")
    
    print(f"\n📋 ПОСЛЕДОВАТЕЛЬНОСТЬ ПЕРЕМЕЩЕНИЯ:")
    print("-" * 50)
    for i, file_info in enumerate(files_to_move, 1):
        print(f"{i}. {file_info['file']}")
        print(f"   {file_info['from']} → {file_info['to']}")
        print(f"   Причина: {file_info['reason']}")
        print()
    
    return files_to_move

def execute_migration_interactive():
    """Интерактивное выполнение миграции"""
    files_to_move = create_migration_plan()
    
    print(f"\n🚀 НАЧАЛО ИНТЕРАКТИВНОЙ МИГРАЦИИ")
    print("=" * 80)
    print("⚠️  ВНИМАНИЕ: Миграция будет выполняться строго по 1 файлу за раз!")
    print("⚠️  После каждого файла будет пауза для проверки!")
    print("⚠️  В случае ошибки - автоматический откат!")
    
    input("\nНажмите Enter для начала миграции...")
    
    success_count = 0
    total_files = len(files_to_move)
    
    for i, file_info in enumerate(files_to_move, 1):
        print(f"\n{'='*80}")
        print(f"ШАГ {i}/{total_files}: {file_info['file']}")
        print(f"{'='*80}")
        
        success = execute_single_file_migration(file_info, i)
        
        if success:
            success_count += 1
            print(f"\n✅ ШАГ {i} ЗАВЕРШЕН УСПЕШНО!")
        else:
            print(f"\n❌ ШАГ {i} ЗАВЕРШЕН С ОШИБКОЙ!")
            print("🔄 Выполнен откат к предыдущему состоянию")
        
        if i < total_files:
            input(f"\nНажмите Enter для перехода к следующему файлу...")
    
    print(f"\n🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print("=" * 50)
    print(f"✅ Успешно перемещено: {success_count}/{total_files} файлов")
    
    if success_count == total_files:
        print("🎉 ВСЕ ФАЙЛЫ УСПЕШНО ПЕРЕМЕЩЕНЫ!")
        print("✅ Архитектура системы исправлена!")
    else:
        print("⚠️  НЕКОТОРЫЕ ФАЙЛЫ НЕ УДАЛОСЬ ПЕРЕМЕСТИТЬ")
        print("📁 Проверьте резервные копии в папке migration_backups/")

def main():
    """Основная функция"""
    print("🚀 ПЛАН ПОШАГОВОЙ МИГРАЦИИ ФАЙЛОВ")
    print("=" * 80)
    
    # Создаем план
    files_to_move = create_migration_plan()
    
    # Предлагаем варианты выполнения
    print(f"\n📋 ВАРИАНТЫ ВЫПОЛНЕНИЯ:")
    print("-" * 50)
    print("1. Показать только план (без выполнения)")
    print("2. Выполнить интерактивную миграцию")
    print("3. Создать скрипт для автоматического выполнения")
    
    choice = input("\nВыберите вариант (1-3): ").strip()
    
    if choice == "1":
        print("\n✅ План создан. Готов к выполнению!")
    elif choice == "2":
        execute_migration_interactive()
    elif choice == "3":
        create_automation_script(files_to_move)
    else:
        print("❌ Неверный выбор!")

def create_automation_script(files_to_move):
    """Создание скрипта автоматического выполнения"""
    script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматический скрипт миграции файлов
Выполняет перемещение строго по 1 файлу за раз
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime

def execute_single_file_migration(file_info, step_number):
    """Выполнение миграции одного файла"""
    print(f"\\n🚀 ШАГ {{step_number}}: МИГРАЦИЯ {{file_info['file']}}")
    print("=" * 80)
    
    source_path = os.path.join(file_info['from'], file_info['file'])
    target_path = os.path.join(file_info['to'], file_info['file'])
    
    # Создаем резервную копию
    backup_dir = f"migration_backups_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}"
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, file_info['file'])
    shutil.copy2(source_path, backup_path)
    
    try:
        # Перемещаем файл
        shutil.move(source_path, target_path)
        print(f"✅ Файл перемещен: {{source_path}} → {{target_path}}")
        
        # Проверяем синтаксис
        result = subprocess.run(f"python3 -m py_compile {{target_path}}", 
                              shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Синтаксис корректен")
            return True
        else:
            print(f"❌ Ошибка синтаксиса: {{result.stderr}}")
            # Откатываемся
            shutil.copy2(backup_path, source_path)
            os.remove(target_path)
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {{e}}")
        # Откатываемся
        shutil.copy2(backup_path, source_path)
        return False

def main():
    files_to_move = {files_to_move}
    
    print("🚀 АВТОМАТИЧЕСКАЯ МИГРАЦИЯ ФАЙЛОВ")
    print("=" * 80)
    
    success_count = 0
    for i, file_info in enumerate(files_to_move, 1):
        if execute_single_file_migration(file_info, i):
            success_count += 1
    
    print(f"\\n🎯 РЕЗУЛЬТАТ: {{success_count}}/{{len(files_to_move)}} файлов перемещено")

if __name__ == "__main__":
    main()
'''
    
    with open('ALADDIN_NEW/scripts/auto_migration.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ Создан скрипт автоматического выполнения: scripts/auto_migration.py")

if __name__ == "__main__":
    main()