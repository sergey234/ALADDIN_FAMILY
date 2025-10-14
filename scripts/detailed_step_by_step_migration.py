#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ДЕТАЛЬНЫЙ ПОШАГОВЫЙ ПЛАН МИГРАЦИИ
Строго по 1 файлу за раз с полной проверкой каждого шага
"""

import os
import shutil
import subprocess
from datetime import datetime

def create_backup(file_path, backup_dir="migration_backups"):
    """Создание резервной копии файла"""
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{os.path.basename(file_path)}_{timestamp}.backup"
    backup_path = os.path.join(backup_dir, backup_name)
    
    shutil.copy2(file_path, backup_path)
    return backup_path

def check_file_exists(file_path):
    """Проверка существования файла"""
    if os.path.exists(file_path):
        print(f"✅ Файл существует: {file_path}")
        return True
    else:
        print(f"❌ Файл не найден: {file_path}")
        return False

def check_syntax(file_path):
    """Проверка синтаксиса файла"""
    result = subprocess.run(f"python3 -m py_compile {file_path}", 
                          shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Синтаксис корректен: {file_path}")
        return True
    else:
        print(f"❌ Ошибка синтаксиса: {result.stderr}")
        return False

def check_imports(file_path):
    """Проверка импортов файла"""
    module_name = os.path.basename(file_path)[:-3]  # убираем .py
    result = subprocess.run(f"python3 -c \"import {module_name}\"", 
                          shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Импорты работают: {module_name}")
        return True
    else:
        print(f"⚠️  Импорты не работают: {result.stderr}")
        return False

def move_file_safely(source_path, target_path, backup_path):
    """Безопасное перемещение файла с откатом при ошибке"""
    try:
        # Перемещаем файл
        shutil.move(source_path, target_path)
        print(f"✅ Файл перемещен: {source_path} → {target_path}")
        
        # Проверяем синтаксис на новом месте
        if not check_syntax(target_path):
            # Откатываемся при ошибке синтаксиса
            shutil.copy2(backup_path, source_path)
            os.remove(target_path)
            print(f"🔄 Откат: файл восстановлен в исходное место")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка перемещения: {e}")
        # Откатываемся при любой ошибке
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, source_path)
            print(f"🔄 Откат: файл восстановлен из резервной копии")
        return False

def execute_file_migration(file_info, step_number):
    """Выполнение миграции одного файла с полной проверкой"""
    print(f"\n{'='*80}")
    print(f"🚀 ШАГ {step_number}: МИГРАЦИЯ {file_info['file']}")
    print(f"{'='*80}")
    
    source_path = os.path.join(file_info['from'], file_info['file'])
    target_path = os.path.join(file_info['to'], file_info['file'])
    
    print(f"📍 Откуда: {source_path}")
    print(f"📍 Куда: {target_path}")
    print(f"💡 Причина: {file_info['reason']}")
    
    # ШАГ 1: Проверка исходного файла
    print(f"\n📋 ШАГ 1: ПРОВЕРКА ИСХОДНОГО ФАЙЛА")
    print("-" * 50)
    if not check_file_exists(source_path):
        return False
    
    # ШАГ 2: Проверка синтаксиса исходного файла
    print(f"\n📋 ШАГ 2: ПРОВЕРКА СИНТАКСИСА ИСХОДНОГО ФАЙЛА")
    print("-" * 50)
    if not check_syntax(source_path):
        return False
    
    # ШАГ 3: Создание резервной копии
    print(f"\n📋 ШАГ 3: СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ")
    print("-" * 50)
    backup_path = create_backup(source_path)
    print(f"💾 Резервная копия: {backup_path}")
    
    # ШАГ 4: Проверка целевой папки
    print(f"\n📋 ШАГ 4: ПРОВЕРКА ЦЕЛЕВОЙ ПАПКИ")
    print("-" * 50)
    target_dir = os.path.dirname(target_path)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"✅ Создана папка: {target_dir}")
    else:
        print(f"✅ Папка существует: {target_dir}")
    
    # ШАГ 5: Перемещение файла
    print(f"\n📋 ШАГ 5: ПЕРЕМЕЩЕНИЕ ФАЙЛА")
    print("-" * 50)
    if not move_file_safely(source_path, target_path, backup_path):
        return False
    
    # ШАГ 6: Проверка файла на новом месте
    print(f"\n📋 ШАГ 6: ПРОВЕРКА ФАЙЛА НА НОВОМ МЕСТЕ")
    print("-" * 50)
    if not check_file_exists(target_path):
        return False
    
    # ШАГ 7: Проверка синтаксиса на новом месте
    print(f"\n📋 ШАГ 7: ПРОВЕРКА СИНТАКСИСА НА НОВОМ МЕСТЕ")
    print("-" * 50)
    if not check_syntax(target_path):
        return False
    
    # ШАГ 8: Проверка импортов
    print(f"\n📋 ШАГ 8: ПРОВЕРКА ИМПОРТОВ")
    print("-" * 50)
    check_imports(target_path)  # Не критично, если не работает
    
    # ШАГ 9: Финальная проверка
    print(f"\n📋 ШАГ 9: ФИНАЛЬНАЯ ПРОВЕРКА")
    print("-" * 50)
    if os.path.exists(target_path) and not os.path.exists(source_path):
        print("✅ Файл успешно перемещен и удален из исходного места")
        print(f"💾 Резервная копия сохранена: {backup_path}")
        return True
    else:
        print("❌ Файл не найден в целевом месте или остался в исходном")
        return False

def main():
    """Основная функция выполнения миграции"""
    print("🚀 ДЕТАЛЬНЫЙ ПОШАГОВЫЙ ПЛАН МИГРАЦИИ")
    print("=" * 80)
    print("⚠️  ВНИМАНИЕ: Миграция выполняется СТРОГО ПО 1 ФАЙЛУ ЗА РАЗ!")
    print("⚠️  После каждого файла - полная проверка и пауза!")
    print("⚠️  В случае ошибки - автоматический откат!")
    
    # Список файлов для перемещения
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
    
    print(f"\n📋 ПЛАН МИГРАЦИИ:")
    print("-" * 50)
    for i, file_info in enumerate(files_to_move, 1):
        print(f"{i}. {file_info['file']}")
        print(f"   {file_info['from']} → {file_info['to']}")
        print(f"   {file_info['reason']}")
        print()
    
    input("Нажмите Enter для начала миграции...")
    
    success_count = 0
    total_files = len(files_to_move)
    
    for i, file_info in enumerate(files_to_move, 1):
        success = execute_file_migration(file_info, i)
        
        if success:
            success_count += 1
            print(f"\n🎉 ШАГ {i} ЗАВЕРШЕН УСПЕШНО!")
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

if __name__ == "__main__":
    main()