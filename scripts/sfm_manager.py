#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Manager - Главный скрипт управления SFM системой
"""

import json
import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

class SFMManager:
    """Главный менеджер SFM системы"""
    
    def __init__(self):
        self.scripts_dir = "scripts"
        self.registry_path = "data/sfm/function_registry.json"
        self.available_commands = {
            'stats': 'Показать статистику SFM',
            'validate': 'Валидация структуры SFM',
            'fix': 'Исправление проблем SFM',
            'add': 'Добавление новой функции',
            'backup': 'Создание резервной копии',
            'restore': 'Восстановление из резервной копии',
            'list': 'Список всех функций',
            'search': 'Поиск функций',
            'status': 'Общий статус системы'
        }
    
    def run_script(self, script_name, args=None):
        """Запуск скрипта"""
        script_path = os.path.join(self.scripts_dir, script_name)
        
        if not os.path.exists(script_path):
            print(f"❌ Скрипт не найден: {script_path}")
            return False
        
        try:
            cmd = [sys.executable, script_path]
            if args:
                cmd.extend(args)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(result.stdout)
                return True
            else:
                print(f"❌ Ошибка выполнения скрипта: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Ошибка запуска скрипта: {e}")
            return False
    
    def show_stats(self):
        """Показать статистику SFM"""
        print("📊 СТАТИСТИКА SFM")
        print("=" * 50)
        
        # Запуск универсального анализатора
        if os.path.exists(os.path.join(self.scripts_dir, "sfm_stats_universal.py")):
            self.run_script("sfm_stats_universal.py")
        else:
            # Fallback на быструю статистику
            self.run_script("sfm_quick_stats.py")
    
    def validate_structure(self):
        """Валидация структуры SFM"""
        print("🔍 ВАЛИДАЦИЯ СТРУКТУРЫ SFM")
        print("=" * 50)
        
        self.run_script("sfm_structure_validator.py")
    
    def fix_issues(self):
        """Исправление проблем SFM"""
        print("🔧 ИСПРАВЛЕНИЕ ПРОБЛЕМ SFM")
        print("=" * 50)
        
        self.run_script("sfm_fix_and_validate.py")
    
    def add_function(self, args):
        """Добавление новой функции"""
        print("➕ ДОБАВЛЕНИЕ НОВОЙ ФУНКЦИИ")
        print("=" * 50)
        
        if os.path.exists(os.path.join(self.scripts_dir, "sfm_add_function.py")):
            self.run_script("sfm_add_function.py", args)
        else:
            print("❌ Скрипт добавления функций не найден")
    
    def create_backup(self):
        """Создание резервной копии"""
        print("💾 СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ")
        print("=" * 50)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"data/sfm/function_registry_backup_manual_{timestamp}.json"
        
        try:
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            with open(self.registry_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            print(f"✅ Резервная копия создана: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Ошибка создания резервной копии: {e}")
            return None
    
    def restore_backup(self, backup_path):
        """Восстановление из резервной копии"""
        print("🔄 ВОССТАНОВЛЕНИЕ ИЗ РЕЗЕРВНОЙ КОПИИ")
        print("=" * 50)
        
        if not os.path.exists(backup_path):
            print(f"❌ Резервная копия не найдена: {backup_path}")
            return False
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as src:
                with open(self.registry_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            print(f"✅ Восстановлено из: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Ошибка восстановления: {e}")
            return False
    
    def list_functions(self):
        """Список всех функций"""
        print("📋 СПИСОК ВСЕХ ФУНКЦИЙ")
        print("=" * 50)
        
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            functions = registry.get('functions', {})
            
            if not functions:
                print("❌ Функции не найдены")
                return
            
            print(f"Всего функций: {len(functions)}")
            print()
            
            for func_id, func_data in functions.items():
                if isinstance(func_data, dict):
                    name = func_data.get('name', 'Unknown')
                    func_type = func_data.get('function_type', 'unknown')
                    status = func_data.get('status', 'unknown')
                    is_critical = func_data.get('is_critical', False)
                    
                    critical_mark = "🔴" if is_critical else "⚪"
                    status_icon = "🟢" if status == "active" else "🟡" if status == "sleeping" else "🔴"
                    
                    print(f"{critical_mark} {status_icon} {func_id}")
                    print(f"    Name: {name}")
                    print(f"    Type: {func_type}")
                    print(f"    Status: {status}")
                    print()
        except Exception as e:
            print(f"❌ Ошибка загрузки реестра: {e}")
    
    def search_functions(self, query):
        """Поиск функций"""
        print(f"🔍 ПОИСК ФУНКЦИЙ: {query}")
        print("=" * 50)
        
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            functions = registry.get('functions', {})
            found_functions = []
            
            query_lower = query.lower()
            
            for func_id, func_data in functions.items():
                if isinstance(func_data, dict):
                    # Поиск по ID
                    if query_lower in func_id.lower():
                        found_functions.append((func_id, func_data))
                        continue
                    
                    # Поиск по имени
                    name = func_data.get('name', '')
                    if query_lower in name.lower():
                        found_functions.append((func_id, func_data))
                        continue
                    
                    # Поиск по описанию
                    description = func_data.get('description', '')
                    if query_lower in description.lower():
                        found_functions.append((func_id, func_data))
                        continue
            
            if found_functions:
                print(f"Найдено функций: {len(found_functions)}")
                print()
                
                for func_id, func_data in found_functions:
                    name = func_data.get('name', 'Unknown')
                    func_type = func_data.get('function_type', 'unknown')
                    status = func_data.get('status', 'unknown')
                    is_critical = func_data.get('is_critical', False)
                    
                    critical_mark = "🔴" if is_critical else "⚪"
                    status_icon = "🟢" if status == "active" else "🟡" if status == "sleeping" else "🔴"
                    
                    print(f"{critical_mark} {status_icon} {func_id}")
                    print(f"    Name: {name}")
                    print(f"    Type: {func_type}")
                    print(f"    Status: {status}")
                    print()
            else:
                print("❌ Функции не найдены")
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
    
    def show_status(self):
        """Общий статус системы"""
        print("📊 ОБЩИЙ СТАТУС СИСТЕМЫ SFM")
        print("=" * 50)
        
        # Проверка реестра
        if os.path.exists(self.registry_path):
            print("✅ SFM реестр найден")
        else:
            print("❌ SFM реестр не найден")
            return
        
        # Проверка скриптов
        print("\n🔍 Проверка скриптов:")
        scripts = [
            "sfm_quick_stats.py",
            "sfm_analyzer.py",
            "sfm_structure_validator.py",
            "sfm_add_function.py",
            "sfm_fix_and_validate.py",
            "sfm_stats_universal.py"
        ]
        
        for script in scripts:
            script_path = os.path.join(self.scripts_dir, script)
            if os.path.exists(script_path):
                print(f"  ✅ {script}")
            else:
                print(f"  ❌ {script}")
        
        # Запуск валидации
        print("\n🔍 Валидация структуры:")
        self.validate_structure()
        
        # Показать статистику
        print("\n📊 Статистика:")
        self.show_stats()
    
    def show_help(self):
        """Показать справку"""
        print("🚀 SFM MANAGER - Управление SFM системой")
        print("=" * 50)
        print()
        print("Доступные команды:")
        for cmd, desc in self.available_commands.items():
            print(f"  {cmd:<12} - {desc}")
        print()
        print("Примеры использования:")
        print("  python3 scripts/sfm_manager.py stats")
        print("  python3 scripts/sfm_manager.py validate")
        print("  python3 scripts/sfm_manager.py fix")
        print("  python3 scripts/sfm_manager.py add --interactive")
        print("  python3 scripts/sfm_manager.py list")
        print("  python3 scripts/sfm_manager.py search 'ai_agent'")
        print("  python3 scripts/sfm_manager.py status")

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description='SFM Manager - Управление SFM системой')
    parser.add_argument('command', nargs='?', help='Команда для выполнения')
    parser.add_argument('args', nargs='*', help='Аргументы команды')
    
    args = parser.parse_args()
    
    manager = SFMManager()
    
    if not args.command:
        manager.show_help()
        return
    
    command = args.command.lower()
    
    if command == 'stats':
        manager.show_stats()
    elif command == 'validate':
        manager.validate_structure()
    elif command == 'fix':
        manager.fix_issues()
    elif command == 'add':
        manager.add_function(args.args)
    elif command == 'backup':
        manager.create_backup()
    elif command == 'restore':
        if args.args:
            manager.restore_backup(args.args[0])
        else:
            print("❌ Укажите путь к резервной копии")
    elif command == 'list':
        manager.list_functions()
    elif command == 'search':
        if args.args:
            manager.search_functions(' '.join(args.args))
        else:
            print("❌ Укажите поисковый запрос")
    elif command == 'status':
        manager.show_status()
    elif command == 'help':
        manager.show_help()
    else:
        print(f"❌ Неизвестная команда: {command}")
        manager.show_help()

if __name__ == "__main__":
    main()