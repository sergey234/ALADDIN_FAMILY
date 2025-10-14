#!/usr/bin/env python3
"""
Скрипт для типизации 907 функций по категориям и проверки на flake8 ошибки
"""

import json
import os
import subprocess
import sys
from typing import Dict, List, Tuple, Any

def load_json(filepath: str) -> Dict[str, Any]:
    """Загрузить JSON файл"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки {filepath}: {e}")
        return {}

def categorize_functions(functions: List[Dict]) -> Dict[str, List[Dict]]:
    """Категоризировать функции по типам"""
    
    categories = {
        'sleep_mode_management': [],
        'performance_optimization': [],
        'advanced_monitoring': [],
        'intrusion_prevention': [],
        'malware_protection': [],
        'vpn_configuration': [],
        'mobile_security': [],
        'compliance_management': [],
        'data_protection': [],
        'other': []
    }
    
    # Ключевые слова для категоризации
    keywords = {
        'sleep_mode_management': ['sleep', 'wake', 'disable', 'enable', 'sleep_mode', 'wake_up', 'priority_queue', 'wrappers', 'continuous_audit'],
        'performance_optimization': ['performance', 'optimization', 'optimizer', 'speed', 'efficiency', 'cpu_affinity', 'memory_compression', 'disk_compression', 'auto_optimization', 'async_optimization'],
        'advanced_monitoring': ['monitoring', 'monitor', 'alert', 'surveillance', 'security_monitoring', 'advanced_alerting', 'critical_security_threat', 'high_cpu_usage', 'low_memory', 'system_errors'],
        'intrusion_prevention': ['intrusion', 'prevention', 'detection', 'ddos', 'sql_injection', 'xss', 'path_traversal', 'command_injection', 'brute_force', 'port_scanning'],
        'malware_protection': ['malware', 'virus', 'antivirus', 'ransomware', 'trojan', 'spyware', 'wannacry', 'locky', 'cryptolocker', 'cerber', 'signature'],
        'vpn_configuration': ['vpn', 'tunnel', 'encryption', 'proxy', 'anonymity', 'privacy', 'server', 'singapore', 'russia', 'europe', 'amsterdam', 'london'],
        'mobile_security': ['mobile', 'device', 'app', 'ios', 'android', 'smartphone', 'whatsapp', 'messenger', 'smart_protection', 'fast', 'balanced'],
        'compliance_management': ['compliance', 'audit', 'regulation', 'policy', 'standard', 'certification', '152_fz', 'compliance_manager', 'compliance_agent'],
        'data_protection': ['data', 'privacy', 'gdpr', 'backup', 'recovery', 'database_password', 'lesson', 'rec_', 'политика_персональных_данных', 'secrets_manager']
    }
    
    for func in functions:
        name = func.get('name', '').lower()
        content = func.get('content', '').lower()
        file_path = func.get('file', '').lower()
        
        # Объединяем все текстовые поля для анализа
        full_text = f'{name} {content} {file_path}'
        
        categorized = False
        for category, category_keywords in keywords.items():
            if any(keyword in full_text for keyword in category_keywords):
                categories[category].append(func)
                categorized = True
                break
        
        if not categorized:
            categories['other'].append(func)
    
    return categories

def check_flake8_errors(file_path: str) -> Tuple[int, List[str]]:
    """Проверить файл на flake8 ошибки"""
    try:
        # Проверяем, существует ли файл
        if not os.path.exists(file_path):
            return 0, [f"Файл не найден: {file_path}"]
        
        # Запускаем flake8
        result = subprocess.run(
            ['flake8', file_path, '--max-line-length=120', '--ignore=E501,W503'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return 0, []
        else:
            errors = result.stderr.split('\n') if result.stderr else []
            return result.returncode, errors
            
    except subprocess.TimeoutExpired:
        return -1, ["Timeout при проверке flake8"]
    except Exception as e:
        return -1, [f"Ошибка flake8: {e}"]

def analyze_functions_by_category(categories: Dict[str, List[Dict]]) -> Dict[str, Dict]:
    """Анализировать функции по категориям"""
    
    analysis = {}
    
    for category, functions in categories.items():
        if not functions:
            continue
            
        print(f"\n🔍 АНАЛИЗ КАТЕГОРИИ: {category.upper()}")
        print(f"   Количество функций: {len(functions)}")
        
        # Анализируем файлы в категории
        file_analysis = {}
        flake8_errors = {}
        
        for func in functions:
            file_path = func.get('file', '')
            if file_path and file_path not in file_analysis:
                file_analysis[file_path] = 0
                # Проверяем flake8 ошибки
                error_code, errors = check_flake8_errors(file_path)
                if error_code != 0:
                    flake8_errors[file_path] = {
                        'error_code': error_code,
                        'errors': errors
                    }
            if file_path:
                file_analysis[file_path] += 1
        
        # Статистика по файлам
        print(f"   Уникальных файлов: {len(file_analysis)}")
        print(f"   Файлов с flake8 ошибками: {len(flake8_errors)}")
        
        # Показываем топ-5 файлов
        top_files = sorted(file_analysis.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"   Топ-5 файлов:")
        for file_name, count in top_files:
            file_short = file_name.split('/')[-1] if '/' in file_name else file_name
            print(f"     {file_short}: {count} функций")
        
        # Показываем flake8 ошибки
        if flake8_errors:
            print(f"   Flake8 ошибки:")
            for file_path, error_info in list(flake8_errors.items())[:3]:  # Показываем первые 3
                file_short = file_path.split('/')[-1] if '/' in file_path else file_name
                print(f"     {file_short}: {error_info['error_code']} ошибок")
                for error in error_info['errors'][:2]:  # Показываем первые 2 ошибки
                    if error.strip():
                        print(f"       - {error}")
        
        analysis[category] = {
            'function_count': len(functions),
            'file_count': len(file_analysis),
            'flake8_errors': len(flake8_errors),
            'top_files': top_files,
            'flake8_details': flake8_errors
        }
    
    return analysis

def create_typing_report(analysis: Dict[str, Dict]) -> str:
    """Создать отчет по типизации"""
    
    report = []
    report.append("# 🔍 ОТЧЕТ ПО ТИПИЗАЦИИ ФУНКЦИЙ")
    report.append("=" * 50)
    report.append("")
    
    total_functions = sum(cat['function_count'] for cat in analysis.values())
    total_files = sum(cat['file_count'] for cat in analysis.values())
    total_flake8_errors = sum(cat['flake8_errors'] for cat in analysis.values())
    
    report.append(f"📊 ОБЩАЯ СТАТИСТИКА:")
    report.append(f"   Всего функций: {total_functions}")
    report.append(f"   Всего файлов: {total_files}")
    report.append(f"   Файлов с flake8 ошибками: {total_flake8_errors}")
    report.append("")
    
    for category, data in analysis.items():
        report.append(f"## {category.upper().replace('_', ' ')}")
        report.append(f"   Функций: {data['function_count']}")
        report.append(f"   Файлов: {data['file_count']}")
        report.append(f"   Flake8 ошибок: {data['flake8_errors']}")
        report.append("")
        
        if data['top_files']:
            report.append("   Топ файлов:")
            for file_name, count in data['top_files']:
                file_short = file_name.split('/')[-1] if '/' in file_name else file_name
                report.append(f"     - {file_short}: {count} функций")
            report.append("")
        
        if data['flake8_details']:
            report.append("   Flake8 ошибки:")
            for file_path, error_info in data['flake8_details'].items():
                file_short = file_path.split('/')[-1] if '/' in file_path else file_path
                report.append(f"     - {file_short}: {error_info['error_code']} ошибок")
            report.append("")
    
    return "\n".join(report)

def main():
    """Основная функция"""
    print("🔍 ТИПИЗАЦИЯ ФУНКЦИЙ И ПРОВЕРКА НА ОШИБКИ")
    print("=" * 60)
    
    # Загружаем True SFM
    true_sfm = load_json('true_sfm_functions.json')
    if not true_sfm:
        print("❌ Не удалось загрузить true_sfm_functions.json")
        return
    
    # Получаем security функции
    functions = true_sfm.get('functions', [])
    security_functions = [func for func in functions if 'security/' in func.get('file', '')]
    
    print(f"📊 Загружено {len(security_functions)} security функций")
    
    # Категоризируем функции
    print("\n🔍 Категоризация функций...")
    categories = categorize_functions(security_functions)
    
    # Анализируем каждую категорию
    print("\n🔍 Анализ категорий...")
    analysis = analyze_functions_by_category(categories)
    
    # Создаем отчет
    print("\n📝 Создание отчета...")
    report = create_typing_report(analysis)
    
    # Сохраняем отчет
    with open('data/sfm/repair_reports/function_typing_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Отчет сохранен: data/sfm/repair_reports/function_typing_report.md")
    
    # Показываем краткую статистику
    print(f"\n📊 КРАТКАЯ СТАТИСТИКА:")
    for category, data in analysis.items():
        if data['function_count'] > 0:
            print(f"   {category}: {data['function_count']} функций, {data['file_count']} файлов, {data['flake8_errors']} ошибок")

if __name__ == "__main__":
    main()
