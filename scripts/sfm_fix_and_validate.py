#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Fix and Validate - Валидация и автоматическое исправление SFM реестра
"""

import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path

class SFMFixAndValidate:
    """Валидация и исправление SFM реестра"""
    
    def __init__(self):
        self.registry_path = "data/sfm/function_registry.json"
        self.registry_data = None
        self.backup_path = None
        self.errors = []
        self.fixes_applied = []
    
    def create_backup(self):
        """Создание резервной копии"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_path = f"data/sfm/function_registry_backup_fix_{timestamp}.json"
        
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
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка JSON: {e}")
            print(f"Строка: {e.lineno if hasattr(e, 'lineno') else 'неизвестно'}")
            return False
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
    
    def validate_structure(self):
        """Валидация структуры реестра"""
        print("🔍 ВАЛИДАЦИЯ СТРУКТУРЫ SFM РЕЕСТРА")
        print("=" * 50)
        
        if not self.registry_data:
            self.errors.append("Реестр не загружен")
            return False
        
        # Проверка основных блоков
        required_blocks = ['functions', 'statistics']
        for block in required_blocks:
            if block not in self.registry_data:
                self.errors.append(f"Отсутствует блок: {block}")
        
        # Проверка блока functions
        functions = self.registry_data.get('functions', {})
        if not isinstance(functions, dict):
            self.errors.append("Блок functions должен быть объектом")
            return False
        
        print(f"✅ Блок functions найден: {len(functions)} функций")
        
        # Проверка каждой функции
        invalid_functions = []
        for func_id, func_data in functions.items():
            if not isinstance(func_data, dict):
                invalid_functions.append(f"{func_id}: не является объектом")
                continue
            
            # Проверка обязательных полей
            required_fields = ['function_id', 'name', 'function_type', 'status']
            for field in required_fields:
                if field not in func_data:
                    invalid_functions.append(f"{func_id}: отсутствует поле {field}")
            
            # Проверка function_id
            if 'function_id' in func_data and func_data['function_id'] != func_id:
                invalid_functions.append(f"{func_id}: function_id не совпадает с ключом")
        
        if invalid_functions:
            self.errors.extend(invalid_functions)
            print(f"❌ Найдено {len(invalid_functions)} невалидных функций")
            for error in invalid_functions:
                print(f"  - {error}")
        else:
            print("✅ Все функции имеют правильную структуру")
        
        return len(invalid_functions) == 0
    
    def fix_structure_issues(self):
        """Исправление проблем структуры"""
        print("\n🔧 ИСПРАВЛЕНИЕ ПРОБЛЕМ СТРУКТУРЫ")
        print("=" * 50)
        
        if not self.registry_data:
            return False
        
        functions = self.registry_data.get('functions', {})
        fixes_applied = 0
        
        for func_id, func_data in functions.items():
            if not isinstance(func_data, dict):
                continue
            
            # Исправление отсутствующего function_id
            if 'function_id' not in func_data:
                func_data['function_id'] = func_id
                self.fixes_applied.append(f"{func_id}: добавлен function_id")
                fixes_applied += 1
            
            # Исправление несовпадающего function_id
            elif func_data.get('function_id') != func_id:
                func_data['function_id'] = func_id
                self.fixes_applied.append(f"{func_id}: исправлен function_id")
                fixes_applied += 1
            
            # Добавление отсутствующих обязательных полей
            if 'name' not in func_data:
                func_data['name'] = func_id.replace('_', ' ').title()
                self.fixes_applied.append(f"{func_id}: добавлено поле name")
                fixes_applied += 1
            
            if 'function_type' not in func_data:
                func_data['function_type'] = 'unknown'
                self.fixes_applied.append(f"{func_id}: добавлено поле function_type")
                fixes_applied += 1
            
            if 'status' not in func_data:
                func_data['status'] = 'sleeping'
                self.fixes_applied.append(f"{func_id}: добавлено поле status")
                fixes_applied += 1
            
            # Добавление стандартных полей
            if 'created_at' not in func_data:
                func_data['created_at'] = datetime.now().isoformat()
                self.fixes_applied.append(f"{func_id}: добавлено поле created_at")
                fixes_applied += 1
            
            if 'is_critical' not in func_data:
                func_data['is_critical'] = False
                self.fixes_applied.append(f"{func_id}: добавлено поле is_critical")
                fixes_applied += 1
            
            if 'auto_enable' not in func_data:
                func_data['auto_enable'] = False
                self.fixes_applied.append(f"{func_id}: добавлено поле auto_enable")
                fixes_applied += 1
        
        if fixes_applied > 0:
            print(f"✅ Применено {fixes_applied} исправлений")
            for fix in self.fixes_applied:
                print(f"  - {fix}")
        else:
            print("✅ Исправления не требуются")
        
        return True
    
    def update_statistics(self):
        """Обновление статистики"""
        print("\n📊 ОБНОВЛЕНИЕ СТАТИСТИКИ")
        print("=" * 50)
        
        if not self.registry_data:
            return False
        
        functions = self.registry_data.get('functions', {})
        
        stats = {
            'total_functions': len(functions),
            'active_functions': sum(1 for f in functions.values() if isinstance(f, dict) and f.get('status') == 'active'),
            'sleeping_functions': sum(1 for f in functions.values() if isinstance(f, dict) and f.get('status') == 'sleeping'),
            'critical_functions': sum(1 for f in functions.values() if isinstance(f, dict) and f.get('is_critical', False)),
            'auto_enable_functions': sum(1 for f in functions.values() if isinstance(f, dict) and f.get('auto_enable', False))
        }
        
        self.registry_data['statistics'] = stats
        self.registry_data['last_updated'] = datetime.now().isoformat()
        
        print(f"✅ Статистика обновлена:")
        print(f"  - Всего функций: {stats['total_functions']}")
        print(f"  - Активные: {stats['active_functions']}")
        print(f"  - Спящие: {stats['sleeping_functions']}")
        print(f"  - Критические: {stats['critical_functions']}")
        print(f"  - Автовключение: {stats['auto_enable_functions']}")
        
        return True
    
    def validate_json_syntax(self):
        """Валидация JSON синтаксиса"""
        print("\n🔍 ВАЛИДАЦИЯ JSON СИНТАКСИСА")
        print("=" * 50)
        
        try:
            # Попытка сериализации и десериализации
            json_str = json.dumps(self.registry_data, indent=2, ensure_ascii=False)
            parsed_data = json.loads(json_str)
            
            print("✅ JSON синтаксис корректен")
            return True
        except Exception as e:
            print(f"❌ Ошибка JSON синтаксиса: {e}")
            return False
    
    def generate_report(self):
        """Генерация отчета"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"data/sfm/fix_validate_report_{timestamp}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'registry_path': self.registry_path,
            'backup_path': self.backup_path,
            'errors_found': self.errors,
            'fixes_applied': self.fixes_applied,
            'final_stats': self.registry_data.get('statistics', {}) if self.registry_data else {}
        }
        
        try:
            os.makedirs(os.path.dirname(report_file), exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Отчет сохранен: {report_file}")
        except Exception as e:
            print(f"❌ Ошибка сохранения отчета: {e}")

def main():
    """Главная функция"""
    print("🚀 SFM FIX AND VALIDATE")
    print("=" * 50)
    
    fixer = SFMFixAndValidate()
    
    # Создание резервной копии
    if not fixer.create_backup():
        sys.exit(1)
    
    # Загрузка реестра
    if not fixer.load_registry():
        print("❌ Не удалось загрузить реестр")
        sys.exit(1)
    
    # Валидация структуры
    structure_valid = fixer.validate_structure()
    
    # Исправление проблем
    if not structure_valid:
        fixer.fix_structure_issues()
    
    # Обновление статистики
    fixer.update_statistics()
    
    # Валидация JSON синтаксиса
    json_valid = fixer.validate_json_syntax()
    
    # Сохранение реестра
    if fixer.save_registry():
        print("\n✅ Реестр успешно сохранен")
    else:
        print("\n❌ Ошибка сохранения реестра")
        sys.exit(1)
    
    # Генерация отчета
    fixer.generate_report()
    
    if structure_valid and json_valid:
        print("\n🎉 Валидация и исправление завершены успешно!")
    else:
        print("\n⚠️  Валидация завершена с предупреждениями")

if __name__ == "__main__":
    main()