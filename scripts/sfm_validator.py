#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM REGISTRY VALIDATOR
Валидатор реестра SFM с детальным анализом

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class SFMValidator:
    def __init__(self, project_root="/Users/sergejhlystov/ALADDIN_NEW"):
        self.project_root = Path(project_root)
        self.sfm_dir = self.project_root / "data" / "sfm"
        self.registry_file = self.sfm_dir / "function_registry.json"
        
        # Обязательные поля для функций
        self.required_fields = [
            'function_id', 'name', 'function_type', 'status'
        ]
        
        # Рекомендуемые поля
        self.recommended_fields = [
            'description', 'security_level', 'created_at', 'version',
            'file_path', 'quality_score', 'dependencies'
        ]

    def validate_json_structure(self, data: Dict) -> List[str]:
        """Валидация структуры JSON"""
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Корневой элемент должен быть объектом")
            return errors
        
        if "functions" not in data:
            errors.append("Отсутствует ключ 'functions'")
            return errors
        
        if not isinstance(data["functions"], dict):
            errors.append("Поле 'functions' должно быть объектом")
            return errors
        
        return errors

    def validate_function(self, func_id: str, func_data: Dict) -> Dict[str, Any]:
        """Валидация отдельной функции"""
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "missing_required": [],
            "missing_recommended": []
        }
        
        # Проверка обязательных полей
        for field in self.required_fields:
            if field not in func_data:
                validation["missing_required"].append(field)
                validation["errors"].append(f"Отсутствует обязательное поле: {field}")
                validation["is_valid"] = False
        
        # Проверка рекомендуемых полей
        for field in self.recommended_fields:
            if field not in func_data:
                validation["missing_recommended"].append(field)
                validation["warnings"].append(f"Отсутствует рекомендуемое поле: {field}")
        
        # Проверка типов данных
        if 'status' in func_data:
            valid_statuses = ['active', 'sleeping', 'disabled', 'enabled']
            if func_data['status'] not in valid_statuses:
                validation["warnings"].append(f"Неизвестный статус: {func_data['status']}")
        
        if 'security_level' in func_data:
            valid_levels = ['low', 'medium', 'high', 'critical']
            if func_data['security_level'] not in valid_levels:
                validation["warnings"].append(f"Неизвестный уровень безопасности: {func_data['security_level']}")
        
        # Проверка file_path
        if 'file_path' in func_data and func_data['file_path']:
            file_path = Path(func_data['file_path'])
            if not file_path.exists():
                validation["warnings"].append(f"Файл не найден: {func_data['file_path']}")
        
        return validation

    def analyze_categories(self, functions: Dict) -> Dict[str, int]:
        """Анализ категорий функций"""
        categories = {}
        for func_data in functions.values():
            if isinstance(func_data, dict) and 'function_type' in func_data:
                category = func_data['function_type'].upper()
                categories[category] = categories.get(category, 0) + 1
        return categories

    def analyze_statuses(self, functions: Dict) -> Dict[str, int]:
        """Анализ статусов функций"""
        statuses = {}
        for func_data in functions.values():
            if isinstance(func_data, dict) and 'status' in func_data:
                status = func_data['status']
                statuses[status] = statuses.get(status, 0) + 1
        return statuses

    def check_duplicates(self, functions: Dict) -> List[str]:
        """Проверка дубликатов"""
        duplicates = []
        seen_ids = set()
        
        for func_id, func_data in functions.items():
            if func_id in seen_ids:
                duplicates.append(f"Дублированный ID: {func_id}")
            seen_ids.add(func_id)
            
            # Проверка дубликатов по имени
            if isinstance(func_data, dict) and 'name' in func_data:
                name = func_data['name']
                name_count = sum(1 for f in functions.values() 
                               if isinstance(f, dict) and f.get('name') == name)
                if name_count > 1:
                    duplicates.append(f"Дублированное имя: {name}")
        
        return duplicates

    def validate_registry(self) -> Dict[str, Any]:
        """Полная валидация реестра"""
        result = {
            "is_valid": False,
            "total_functions": 0,
            "valid_functions": 0,
            "invalid_functions": 0,
            "categories": {},
            "statuses": {},
            "errors": [],
            "warnings": [],
            "duplicates": [],
            "file_info": {},
            "function_validations": {}
        }
        
        try:
            # Информация о файле
            if self.registry_file.exists():
                stat = self.registry_file.stat()
                result["file_info"] = {
                    "size_bytes": stat.st_size,
                    "size_kb": stat.st_size / 1024,
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "exists": True
                }
            else:
                result["errors"].append("Файл реестра не найден")
                result["file_info"]["exists"] = False
                return result
            
            # Загрузка JSON
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Валидация структуры
            structure_errors = self.validate_json_structure(data)
            result["errors"].extend(structure_errors)
            
            if structure_errors:
                return result
            
            functions = data["functions"]
            result["total_functions"] = len(functions)
            result["is_valid"] = True
            
            # Валидация каждой функции
            for func_id, func_data in functions.items():
                func_validation = self.validate_function(func_id, func_data)
                result["function_validations"][func_id] = func_validation
                
                if func_validation["is_valid"]:
                    result["valid_functions"] += 1
                else:
                    result["invalid_functions"] += 1
                
                result["errors"].extend(func_validation["errors"])
                result["warnings"].extend(func_validation["warnings"])
            
            # Анализ категорий и статусов
            result["categories"] = self.analyze_categories(functions)
            result["statuses"] = self.analyze_statuses(functions)
            
            # Проверка дубликатов
            result["duplicates"] = self.check_duplicates(functions)
            
        except json.JSONDecodeError as e:
            result["errors"].append(f"Ошибка парсинга JSON: {str(e)}")
        except Exception as e:
            result["errors"].append(f"Ошибка валидации: {str(e)}")
        
        return result

    def generate_report(self) -> None:
        """Генерация отчета валидации"""
        print("🔍 ВАЛИДАЦИЯ SFM РЕЕСТРА")
        print("=" * 50)
        
        validation = self.validate_registry()
        
        # Общая информация
        print(f"📁 Файл: {self.registry_file}")
        print(f"📊 Размер: {validation['file_info'].get('size_kb', 0):.1f} KB")
        print(f"🕒 Изменен: {validation['file_info'].get('last_modified', 'N/A')}")
        print(f"✅ Существует: {'Да' if validation['file_info'].get('exists', False) else 'Нет'}")
        
        # Статистика функций
        print(f"\n📊 СТАТИСТИКА ФУНКЦИЙ:")
        print(f"  • Всего функций: {validation['total_functions']}")
        print(f"  • Валидных: {validation['valid_functions']}")
        print(f"  • Невалидных: {validation['invalid_functions']}")
        print(f"  • Процент валидности: {(validation['valid_functions'] / validation['total_functions'] * 100):.1f}%" if validation['total_functions'] > 0 else "  • Процент валидности: 0%")
        
        # Статусы функций
        if validation['statuses']:
            print(f"\n🔄 СТАТУСЫ ФУНКЦИЙ:")
            for status, count in sorted(validation['statuses'].items()):
                print(f"  • {status:<12} : {count:>3} функций")
        
        # Категории функций
        if validation['categories']:
            print(f"\n📂 КАТЕГОРИИ ФУНКЦИЙ:")
            sorted_categories = sorted(validation['categories'].items(), key=lambda x: x[1], reverse=True)
            for category, count in sorted_categories[:15]:  # Топ 15
                print(f"  • {category:<25} : {count:>3} функций")
        
        # Ошибки
        if validation['errors']:
            print(f"\n❌ ОШИБКИ ({len(validation['errors'])}):")
            for error in validation['errors'][:10]:  # Первые 10 ошибок
                print(f"  • {error}")
            if len(validation['errors']) > 10:
                print(f"  ... и еще {len(validation['errors']) - 10} ошибок")
        
        # Предупреждения
        if validation['warnings']:
            print(f"\n⚠️  ПРЕДУПРЕЖДЕНИЯ ({len(validation['warnings'])}):")
            for warning in validation['warnings'][:10]:  # Первые 10 предупреждений
                print(f"  • {warning}")
            if len(validation['warnings']) > 10:
                print(f"  ... и еще {len(validation['warnings']) - 10} предупреждений")
        
        # Дубликаты
        if validation['duplicates']:
            print(f"\n🔄 ДУБЛИКАТЫ ({len(validation['duplicates'])}):")
            for duplicate in validation['duplicates']:
                print(f"  • {duplicate}")
        
        # Итоговая оценка
        print(f"\n🎯 ИТОГОВАЯ ОЦЕНКА:")
        if validation['is_valid'] and validation['invalid_functions'] == 0:
            print(f"  ✅ РЕЕСТР ВАЛИДЕН И КОРРЕКТЕН")
        elif validation['is_valid']:
            print(f"  ⚠️  РЕЕСТР ВАЛИДЕН, НО ЕСТЬ ПРОБЛЕМЫ")
        else:
            print(f"  ❌ РЕЕСТР НЕВАЛИДЕН - ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ")
        
        print("=" * 50)

def main():
    """Главная функция"""
    validator = SFMValidator()
    validator.generate_report()

if __name__ == "__main__":
    main()