#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM File Validator - Валидатор существования файлов в SFM реестре
Проверяет, что все зарегистрированные файлы действительно существуют
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple

def validate_file_existence():
    """Валидация существования файлов"""
    try:
        print("🔍 ВАЛИДАЦИЯ СУЩЕСТВОВАНИЯ ФАЙЛОВ В SFM РЕЕСТРЕ")
        print("=" * 60)
        
        # Загружаем файл
        with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        functions = registry.get('functions', {})
        
        # Статистика
        total_functions = len(functions)
        existing_files = 0
        missing_files = 0
        missing_functions = []
        
        print(f"📊 Всего функций в реестре: {total_functions}")
        print()
        
        # Проверяем каждую функцию
        for func_id, func_data in functions.items():
            if isinstance(func_data, dict):
                file_path = func_data.get('file_path', '')
                
                if file_path:
                    # Проверяем существование файла
                    full_path = os.path.join('/Users/sergejhlystov/ALADDIN_NEW', file_path)
                    
                    if os.path.exists(full_path):
                        existing_files += 1
                        status = "✅"
                    else:
                        missing_files += 1
                        status = "❌"
                        missing_functions.append({
                            'function_id': func_id,
                            'file_path': file_path,
                            'name': func_data.get('name', 'неизвестно'),
                            'status': func_data.get('status', 'неизвестно')
                        })
                        print(f"{status} {func_id}: {file_path}")
                else:
                    missing_files += 1
                    missing_functions.append({
                        'function_id': func_id,
                        'file_path': 'НЕ УКАЗАН',
                        'name': func_data.get('name', 'неизвестно'),
                        'status': func_data.get('status', 'неизвестно')
                    })
                    print(f"❌ {func_id}: ПУТЬ К ФАЙЛУ НЕ УКАЗАН")
        
        print()
        print("📊 СТАТИСТИКА:")
        print(f"✅ Существующие файлы: {existing_files}")
        print(f"❌ Отсутствующие файлы: {missing_files}")
        print(f"📈 Процент валидности: {(existing_files/total_functions)*100:.1f}%")
        
        # Генерируем отчет
        report = generate_file_validation_report(existing_files, missing_files, missing_functions)
        
        return missing_files == 0, report
        
    except Exception as e:
        print(f"❌ Ошибка валидации: {e}")
        return False, None

def generate_file_validation_report(existing_files: int, missing_files: int, missing_functions: List[Dict]) -> Dict:
    """Генерация отчета о валидации файлов"""
    try:
        report = {
            "timestamp": datetime.now().isoformat(),
            "validation_type": "file_existence",
            "total_functions": existing_files + missing_files,
            "existing_files": existing_files,
            "missing_files": missing_files,
            "validity_percentage": (existing_files / (existing_files + missing_files)) * 100,
            "missing_functions": missing_functions,
            "recommendations": []
        }
        
        # Рекомендации
        if missing_files > 0:
            report["recommendations"].append("Удалить функции с несуществующими файлами")
            report["recommendations"].append("Проверить правильность путей к файлам")
            report["recommendations"].append("Обновить регистрацию функций")
        
        if missing_files == 0:
            report["recommendations"].append("Все файлы существуют - SFM реестр валиден")
        
        # Сохраним отчет
        report_file = f"data/sfm/file_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Отчет о валидации файлов сохранен: {report_file}")
        return report
        
    except Exception as e:
        print(f"❌ Ошибка генерации отчета: {e}")
        return None

def fix_missing_functions():
    """Исправление функций с несуществующими файлами"""
    try:
        print("\n🔧 ИСПРАВЛЕНИЕ ФУНКЦИЙ С НЕСУЩЕСТВУЮЩИМИ ФАЙЛАМИ")
        print("=" * 60)
        
        # Загружаем файл
        with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        functions = registry.get('functions', {})
        
        # Находим функции с несуществующими файлами
        functions_to_remove = []
        
        for func_id, func_data in functions.items():
            if isinstance(func_data, dict):
                file_path = func_data.get('file_path', '')
                
                if file_path:
                    full_path = os.path.join('/Users/sergejhlystov/ALADDIN_NEW', file_path)
                    
                    if not os.path.exists(full_path):
                        functions_to_remove.append(func_id)
                        print(f"❌ Функция для удаления: {func_id} -> {file_path}")
        
        if functions_to_remove:
            print(f"\n📊 Найдено {len(functions_to_remove)} функций для удаления")
            
            # Создаем резервную копию
            backup_file = f"data/sfm/function_registry_backup_before_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            print(f"✅ Резервная копия создана: {backup_file}")
            
            # Удаляем функции
            for func_id in functions_to_remove:
                del functions[func_id]
                print(f"🗑️ Удалена функция: {func_id}")
            
            # Сохраняем исправленный реестр
            with open('data/sfm/function_registry.json', 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Реестр очищен от {len(functions_to_remove)} несуществующих функций")
            print(f"✅ Осталось функций: {len(functions)}")
            
            return True
        else:
            print("✅ Несуществующих функций не найдено")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка исправления: {e}")
        return False

def suggest_alternatives():
    """Предложение альтернатив для несуществующих файлов"""
    try:
        print("\n🔍 ПОИСК АЛЬТЕРНАТИВ ДЛЯ НЕСУЩЕСТВУЮЩИХ ФАЙЛОВ")
        print("=" * 60)
        
        # Загружаем файл
        with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        functions = registry.get('functions', {})
        
        # Специальные случаи
        special_cases = {
            'security_authenticationinterface': {
                'suggested_path': 'security/microservices/api_gateway.py',
                'suggested_class': 'AuthenticationInterface',
                'reason': 'Класс находится внутри api_gateway.py как абстрактный интерфейс',
                'action': 'Исправить путь или удалить как отдельную функцию'
            }
        }
        
        for func_id, func_data in functions.items():
            if isinstance(func_data, dict):
                file_path = func_data.get('file_path', '')
                
                if file_path and func_id in special_cases:
                    case = special_cases[func_id]
                    print(f"\n🎯 Функция: {func_id}")
                    print(f"   Текущий путь: {file_path}")
                    print(f"   Предлагаемый путь: {case['suggested_path']}")
                    print(f"   Класс: {case['suggested_class']}")
                    print(f"   Причина: {case['reason']}")
                    print(f"   Действие: {case['action']}")
                    
                    # Проверяем, существует ли предлагаемый файл
                    suggested_full_path = os.path.join('/Users/sergejhlystov/ALADDIN_NEW', case['suggested_path'])
                    if os.path.exists(suggested_full_path):
                        print(f"   ✅ Предлагаемый файл существует")
                    else:
                        print(f"   ❌ Предлагаемый файл не существует")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка поиска альтернатив: {e}")
        return False

if __name__ == "__main__":
    # Валидация существования файлов
    is_valid, report = validate_file_existence()
    
    if not is_valid:
        print("\n❌ НАЙДЕНЫ НЕСУЩЕСТВУЮЩИЕ ФАЙЛЫ!")
        
        # Предлагаем альтернативы
        suggest_alternatives()
        
        # Предлагаем исправление
        print("\n🔧 Хотите исправить автоматически? (y/n)")
        # В реальном использовании здесь был бы input()
        print("💡 Для автоматического исправления запустите:")
        print("   python3 scripts/sfm_file_validator.py --fix")
    else:
        print("\n🎉 ВСЕ ФАЙЛЫ СУЩЕСТВУЮТ!")
        print("✅ SFM реестр полностью валиден")