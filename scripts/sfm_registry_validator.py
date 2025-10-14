#!/usr/bin/env python3
"""
Скрипт валидации SFM реестра
Проверяет целостность реестра и выявляет проблемы
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple

class SFMRegistryValidator:
    def __init__(self, registry_path: str):
        self.registry_path = registry_path
        self.registry = None
        self.errors = []
        self.warnings = []
        
    def load_registry(self) -> bool:
        """Загружает реестр из файла"""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                self.registry = json.load(f)
            return True
        except Exception as e:
            self.errors.append(f'Ошибка загрузки реестра: {e}')
            return False
    
    def validate_function(self, func_id: str, func_data: Dict) -> List[str]:
        """Валидирует одну функцию"""
        issues = []
        
        # Проверяем обязательные поля
        required_fields = ['function_id', 'name', 'class_name', 'file_path', 'status']
        for field in required_fields:
            if not func_data.get(field) or func_data.get(field) == 'unknown':
                issues.append(f'Отсутствует поле: {field}')
        
        # Проверяем файл
        file_path = func_data.get('file_path', '')
        if file_path and file_path != 'unknown':
            full_path = os.path.join(os.path.dirname(self.registry_path), '..', file_path)
            if not os.path.exists(full_path):
                issues.append(f'Файл не найден: {file_path}')
            else:
                # Проверяем, что файл не пустой
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content.strip()) == 0:
                            issues.append(f'Файл пустой: {file_path}')
                        elif 'class ' not in content:
                            issues.append(f'В файле нет классов: {file_path}')
                except Exception as e:
                    issues.append(f'Ошибка чтения файла {file_path}: {e}')
        else:
            issues.append('Нет пути к файлу')
        
        return issues
    
    def find_empty_functions(self) -> List[Tuple[str, Dict]]:
        """Находит пустые функции"""
        empty_functions = []
        
        for func_id, func_data in self.registry.get('functions', {}).items():
            issues = self.validate_function(func_id, func_data)
            if issues:
                empty_functions.append((func_id, func_data, issues))
        
        return empty_functions
    
    def find_duplicates(self) -> List[Tuple[str, List[str]]]:
        """Находит дубликаты по имени класса"""
        class_names = {}
        
        for func_id, func_data in self.registry.get('functions', {}).items():
            class_name = func_data.get('class_name', '')
            if class_name and class_name != 'unknown':
                if class_name not in class_names:
                    class_names[class_name] = []
                class_names[class_name].append(func_id)
        
        duplicates = []
        for class_name, func_ids in class_names.items():
            if len(func_ids) > 1:
                duplicates.append((class_name, func_ids))
        
        return duplicates
    
    def generate_report(self) -> str:
        """Генерирует отчет о валидации"""
        if not self.registry:
            return 'Ошибка: реестр не загружен'
        
        report = []
        report.append('=== ОТЧЕТ ВАЛИДАЦИИ SFM РЕЕСТРА ===')
        report.append(f'Дата: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        report.append(f'Всего функций: {len(self.registry.get("functions", {}))}')
        report.append('')
        
        # Проверяем пустые функции
        empty_functions = self.find_empty_functions()
        if empty_functions:
            report.append(f'❌ ПУСТЫЕ ФУНКЦИИ ({len(empty_functions)}):')
            for func_id, func_data, issues in empty_functions:
                report.append(f'  - {func_id}:')
                for issue in issues:
                    report.append(f'    • {issue}')
            report.append('')
        else:
            report.append('✅ Пустых функций не найдено')
            report.append('')
        
        # Проверяем дубликаты
        duplicates = self.find_duplicates()
        if duplicates:
            report.append(f'⚠️ ДУБЛИКАТЫ ({len(duplicates)}):')
            for class_name, func_ids in duplicates:
                report.append(f'  - {class_name}: {func_ids}')
            report.append('')
        else:
            report.append('✅ Дубликатов не найдено')
            report.append('')
        
        return '\n'.join(report)
    
    def fix_empty_functions(self, dry_run: bool = True) -> List[str]:
        """Исправляет пустые функции"""
        if not self.registry:
            return ['Ошибка: реестр не загружен']
        
        empty_functions = self.find_empty_functions()
        fixed_functions = []
        
        for func_id, func_data, issues in empty_functions:
            # Проверяем, есть ли реальная версия с ai_agent_ префиксом
            ai_agent_version = f'ai_agent_{func_id}'
            if ai_agent_version in self.registry.get('functions', {}):
                ai_agent_data = self.registry['functions'][ai_agent_version]
                
                if not dry_run:
                    # Удаляем пустую версию
                    del self.registry['functions'][func_id]
                    fixed_functions.append(f'Удалена пустая функция: {func_id}')
                else:
                    fixed_functions.append(f'Будет удалена пустая функция: {func_id}')
            else:
                fixed_functions.append(f'Не найдена замена для: {func_id}')
        
        return fixed_functions

def main():
    registry_path = 'data/sfm/function_registry.json'
    validator = SFMRegistryValidator(registry_path)
    
    if not validator.load_registry():
        print('Ошибка загрузки реестра')
        return
    
    # Генерируем отчет
    report = validator.generate_report()
    print(report)
    
    # Показываем, что можно исправить
    print('\n=== ПРЕДЛОЖЕНИЯ ПО ИСПРАВЛЕНИЮ ===')
    fixes = validator.fix_empty_functions(dry_run=True)
    for fix in fixes:
        print(f'  - {fix}')

if __name__ == '__main__':
    main()