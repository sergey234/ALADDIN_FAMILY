#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Add Function - Автоматическое добавление функций в SFM реестр
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

class SFMFunctionAdder:
    """Автоматическое добавление функций в SFM реестр"""
    
    def __init__(self):
        self.registry_path = "data/sfm/function_registry.json"
        self.registry_data = None
        self.backup_path = None
    
    def create_backup(self):
        """Создание резервной копии"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_path = f"data/sfm/function_registry_backup_add_{timestamp}.json"
        
        try:
            os.makedirs(os.path.dirname(self.backup_path), exist_ok=True)
            with open(self.registry_path, 'r', encoding='utf-8') as src:
                with open(self.backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            print(f"✅ Резервная копия создана: {self.backup_path}")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания резервной копии: {e}")
            return False
    
    def load_registry(self):
        """Загрузка SFM реестра"""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                self.registry_data = json.load(f)
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки реестра: {e}")
            return False
    
    def save_registry(self):
        """Сохранение SFM реестра"""
        try:
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(self.registry_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения реестра: {e}")
            return False
    
    def validate_function_data(self, func_data):
        """Валидация данных функции"""
        required_fields = ['function_id', 'name', 'function_type', 'status']
        
        for field in required_fields:
            if field not in func_data:
                print(f"❌ Отсутствует обязательное поле: {field}")
                return False
        
        # Проверка типов
        if not isinstance(func_data['function_id'], str):
            print("❌ function_id должен быть строкой")
            return False
        
        if not isinstance(func_data['name'], str):
            print("❌ name должен быть строкой")
            return False
        
        if func_data['function_type'] not in ['ai_agent', 'security', 'bot', 'manager', 'monitoring', 'service']:
            print(f"❌ Неизвестный тип функции: {func_data['function_type']}")
            return False
        
        if func_data['status'] not in ['active', 'sleeping', 'disabled']:
            print(f"❌ Неизвестный статус: {func_data['status']}")
            return False
        
        return True
    
    def add_function(self, func_data):
        """Добавление функции в реестр"""
        if not self.validate_function_data(func_data):
            return False
        
        func_id = func_data['function_id']
        
        # Проверка на дубликат
        if func_id in self.registry_data.get('functions', {}):
            print(f"⚠️  Функция {func_id} уже существует. Перезаписать? (y/N): ", end='')
            response = input().strip().lower()
            if response != 'y':
                print("❌ Добавление отменено")
                return False
        
        # Добавление функции
        if 'functions' not in self.registry_data:
            self.registry_data['functions'] = {}
        
        # Добавление стандартных полей
        default_fields = {
            'created_at': datetime.now().isoformat(),
            'is_critical': func_data.get('is_critical', False),
            'auto_enable': func_data.get('auto_enable', False),
            'quality_grade': func_data.get('quality_grade', 'A'),
            'test_coverage': func_data.get('test_coverage', '0%'),
            'execution_count': 0,
            'success_count': 0,
            'error_count': 0
        }
        
        # Объединение данных
        final_func_data = {**default_fields, **func_data}
        
        self.registry_data['functions'][func_id] = final_func_data
        
        # Обновление статистики
        self.update_statistics()
        
        print(f"✅ Функция {func_id} успешно добавлена")
        return True
    
    def update_statistics(self):
        """Обновление статистики в реестре"""
        functions = self.registry_data.get('functions', {})
        
        stats = {
            'total_functions': len(functions),
            'active_functions': sum(1 for f in functions.values() if f.get('status') == 'active'),
            'sleeping_functions': sum(1 for f in functions.values() if f.get('status') == 'sleeping'),
            'critical_functions': sum(1 for f in functions.values() if f.get('is_critical', False)),
            'auto_enable_functions': sum(1 for f in functions.values() if f.get('auto_enable', False))
        }
        
        self.registry_data['statistics'] = stats
        self.registry_data['last_updated'] = datetime.now().isoformat()
    
    def add_function_from_file(self, file_path):
        """Добавление функции из файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                func_data = json.load(f)
            
            if isinstance(func_data, list):
                # Если файл содержит массив функций
                for func in func_data:
                    if not self.add_function(func):
                        return False
            else:
                # Если файл содержит одну функцию
                if not self.add_function(func_data):
                    return False
            
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки файла: {e}")
            return False
    
    def add_function_interactive(self):
        """Интерактивное добавление функции"""
        print("🔧 ИНТЕРАКТИВНОЕ ДОБАВЛЕНИЕ ФУНКЦИИ")
        print("=" * 50)
        
        func_data = {}
        
        # Обязательные поля
        func_data['function_id'] = input("Function ID: ").strip()
        func_data['name'] = input("Name: ").strip()
        func_data['description'] = input("Description: ").strip()
        
        print("\nТип функции:")
        print("1. ai_agent")
        print("2. security")
        print("3. bot")
        print("4. manager")
        print("5. monitoring")
        print("6. service")
        
        type_choice = input("Выберите тип (1-6): ").strip()
        type_map = {
            '1': 'ai_agent',
            '2': 'security',
            '3': 'bot',
            '4': 'manager',
            '5': 'monitoring',
            '6': 'service'
        }
        func_data['function_type'] = type_map.get(type_choice, 'ai_agent')
        
        print("\nСтатус:")
        print("1. active")
        print("2. sleeping")
        print("3. disabled")
        
        status_choice = input("Выберите статус (1-3): ").strip()
        status_map = {
            '1': 'active',
            '2': 'sleeping',
            '3': 'disabled'
        }
        func_data['status'] = status_map.get(status_choice, 'active')
        
        # Дополнительные поля
        func_data['file_path'] = input("File path (optional): ").strip() or None
        func_data['class_name'] = input("Class name (optional): ").strip() or None
        
        is_critical = input("Критическая функция? (y/N): ").strip().lower() == 'y'
        func_data['is_critical'] = is_critical
        
        auto_enable = input("Автовключение? (y/N): ").strip().lower() == 'y'
        func_data['auto_enable'] = auto_enable
        
        return self.add_function(func_data)

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description='Добавление функций в SFM реестр')
    parser.add_argument('-f', '--file', help='Файл с данными функции (JSON)')
    parser.add_argument('-i', '--interactive', action='store_true', help='Интерактивное добавление')
    parser.add_argument('--function-id', help='ID функции')
    parser.add_argument('--name', help='Имя функции')
    parser.add_argument('--description', help='Описание функции')
    parser.add_argument('--type', choices=['ai_agent', 'security', 'bot', 'manager', 'monitoring', 'service'], help='Тип функции')
    parser.add_argument('--status', choices=['active', 'sleeping', 'disabled'], help='Статус функции')
    parser.add_argument('--critical', action='store_true', help='Критическая функция')
    parser.add_argument('--auto-enable', action='store_true', help='Автовключение')
    
    args = parser.parse_args()
    
    adder = SFMFunctionAdder()
    
    # Создание резервной копии
    if not adder.create_backup():
        sys.exit(1)
    
    # Загрузка реестра
    if not adder.load_registry():
        sys.exit(1)
    
    success = False
    
    if args.file:
        # Добавление из файла
        success = adder.add_function_from_file(args.file)
    elif args.interactive:
        # Интерактивное добавление
        success = adder.add_function_interactive()
    elif args.function_id and args.name and args.type and args.status:
        # Добавление через аргументы командной строки
        func_data = {
            'function_id': args.function_id,
            'name': args.name,
            'description': args.description or '',
            'function_type': args.type,
            'status': args.status,
            'is_critical': args.critical,
            'auto_enable': args.auto_enable
        }
        success = adder.add_function(func_data)
    else:
        print("❌ Недостаточно аргументов. Используйте --help для справки")
        sys.exit(1)
    
    if success:
        # Сохранение реестра
        if adder.save_registry():
            print("✅ Функция успешно добавлена в SFM реестр")
        else:
            print("❌ Ошибка сохранения реестра")
            sys.exit(1)
    else:
        print("❌ Ошибка добавления функции")
        sys.exit(1)

if __name__ == "__main__":
    main()