#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый анализ системы ALADDIN
Получение точной статистики по всей системе
"""

import sys
import os
import json
from pathlib import Path
from collections import defaultdict

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

def analyze_file_structure():
    """Анализ структуры файлов по категориям"""
    print("📁 СТРУКТУРА ФАЙЛОВ ПО КАТЕГОРИЯМ:")
    print("=" * 50)
    
    categories = {
        "AI Agents": "security/ai_agents/",
        "Security Bots": "security/bots/", 
        "Managers": "security/managers/",
        "Microservices": "security/microservices/",
        "Privacy": "security/privacy/",
        "CI/CD": "security/ci_cd/",
        "Core": "core/",
        "Config": "config/"
    }
    
    total_files = 0
    file_stats = {}
    
    for category, path in categories.items():
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.endswith('.py')]
            file_count = len(files)
            file_stats[category] = file_count
            total_files += file_count
            print(f"* {category}: {file_count} файлов ✅")
        else:
            print(f"* {category}: 0 файлов ❌")
    
    print(f"* SFM файлы: 1 файл (основной)")
    print(f"* Всего файлов: {total_files + 1} файлов")
    
    return file_stats, total_files + 1

def analyze_functions():
    """Анализ функций по категориям"""
    print("\n⚙️ ФУНКЦИИ ПО КАТЕГОРИЯМ:")
    print("=" * 50)
    
    categories = {
        "AI Agents": "security/ai_agents/",
        "Security Bots": "security/bots/",
        "Managers": "security/managers/",
        "Microservices": "security/microservices/",
        "Privacy": "security/privacy/",
        "CI/CD": "security/ci_cd/",
        "Core": "core/",
        "Config": "config/"
    }
    
    total_functions = 0
    function_stats = {}
    
    for category, path in categories.items():
        if os.path.exists(path):
            function_count = 0
            for file in os.listdir(path):
                if file.endswith('.py'):
                    file_path = os.path.join(path, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Подсчет функций (def)
                            function_count += content.count('def ')
                    except:
                        pass
            function_stats[category] = function_count
            total_functions += function_count
            print(f"* {category}: {function_count} функций")
        else:
            print(f"* {category}: 0 функций ❌")
    
    print(f"* ВСЕГО ФУНКЦИЙ: {total_functions} функций")
    
    return function_stats, total_functions

def analyze_sfm_registry():
    """Анализ реестра SFM"""
    print("\n🎯 АНАЛИЗ SFM РЕЕСТРА:")
    print("=" * 50)
    
    registry_files = [
        "data/functions_registry.json",
        "data/sfm/function_registry.json"
    ]
    
    total_sfm_functions = 0
    
    for registry_file in registry_files:
        if os.path.exists(registry_file):
            try:
                with open(registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # Исправленная логика: считаем функции в data["functions"]
                        if 'functions' in data and isinstance(data['functions'], dict):
                            function_count = len(data['functions'])
                        else:
                            # Fallback для старого формата
                            function_count = len([k for k in data.keys() if not k.startswith('_')])
                        total_sfm_functions += function_count
                        print(f"* {registry_file}: {function_count} функций")
                    else:
                        print(f"* {registry_file}: 0 функций")
            except:
                print(f"* {registry_file}: Ошибка чтения ❌")
        else:
            print(f"* {registry_file}: Файл не найден ❌")
    
    print(f"* ВСЕГО В SFM: {total_sfm_functions} функций")
    
    return total_sfm_functions

def analyze_code_lines():
    """Анализ строк кода"""
    print("\n📊 СТРОКИ КОДА:")
    print("=" * 50)
    
    categories = {
        "Security модули": "security/",
        "Core модули": "core/",
        "Config модули": "config/"
    }
    
    total_lines = 0
    line_stats = {}
    
    for category, path in categories.items():
        if os.path.exists(path):
            line_count = 0
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = len(f.readlines())
                                line_count += lines
                        except:
                            pass
            line_stats[category] = line_count
            total_lines += line_count
            percentage = (line_count / total_lines * 100) if total_lines > 0 else 0
            print(f"* {category}: {line_count:,} строк ({percentage:.1f}%)")
        else:
            print(f"* {category}: 0 строк ❌")
    
    print(f"* ВСЕГО СТРОК: {total_lines:,} строк")
    
    return line_stats, total_lines

def find_function_in_sfm(function_name):
    """Поиск функции в SFM"""
    print(f"\n🔍 ПОИСК ФУНКЦИИ '{function_name}' В SFM:")
    print("=" * 50)
    
    registry_files = [
        "data/functions_registry.json",
        "data/sfm/function_registry.json"
    ]
    
    found = False
    
    for registry_file in registry_files:
        if os.path.exists(registry_file):
            try:
                with open(registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if function_name.lower() in key.lower() or (isinstance(value, dict) and function_name.lower() in str(value).lower()):
                                print(f"✅ НАЙДЕНО в {registry_file}:")
                                print(f"   Key: {key}")
                                if isinstance(value, dict):
                                    print(f"   Name: {value.get('name', 'N/A')}")
                                    print(f"   Description: {value.get('description', 'N/A')}")
                                    print(f"   Status: {value.get('status', 'N/A')}")
                                found = True
            except:
                pass
    
    if not found:
        print(f"❌ Функция '{function_name}' не найдена в SFM реестрах")
    
    return found

def main():
    """Основная функция"""
    print("🚀 БЫСТРЫЙ АНАЛИЗ СИСТЕМЫ ALADDIN")
    print("=" * 60)
    
    # Анализ структуры файлов
    file_stats, total_files = analyze_file_structure()
    
    # Анализ функций
    function_stats, total_functions = analyze_functions()
    
    # Анализ SFM реестра
    sfm_functions = analyze_sfm_registry()
    
    # Анализ строк кода
    line_stats, total_lines = analyze_code_lines()
    
    # Итоговая статистика
    print("\n🎯 ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 50)
    print(f"📁 Всего файлов: {total_files}")
    print(f"⚙️ Всего функций в коде: {total_functions}")
    print(f"🎯 Функций в SFM: {sfm_functions}")
    print(f"📊 Всего строк кода: {total_lines:,}")
    
    # Проверка аргументов командной строки
    if len(sys.argv) > 1:
        function_name = sys.argv[1]
        find_function_in_sfm(function_name)

if __name__ == "__main__":
    main()