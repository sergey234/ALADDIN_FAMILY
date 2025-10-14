#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Объединенный анализ системы ALADDIN по категориям
Полная статистика с разбивкой по типам компонентов
"""

import sys
import os
import json
from pathlib import Path
from collections import defaultdict

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

def analyze_all_categories_unified():
    """Объединенный анализ всех категорий с полной статистикой"""
    print("🚀 ОБЪЕДИНЕННЫЙ АНАЛИЗ СИСТЕМЫ ALADDIN")
    print("=" * 80)
    
    # Определяем все папки для анализа
    categories = {
        "🤖 AI Agents": "security/ai_agents/",
        "🤖 Security Bots": "security/bots/",
        "⚙️ Managers": "security/managers/",
        "🔧 Microservices": "security/microservices/",
        "🔒 Privacy": "security/privacy/",
        "🔄 CI/CD": "security/ci_cd/",
        "🏗️ Core": "core/",
        "⚙️ Config": "config/"
    }
    
    # Общие категории компонентов
    component_types = {
        "🤖 AI АГЕНТЫ": ["agent"],
        "⚙️ МЕНЕДЖЕРЫ": ["manager"],
        "🔧 ДВИЖКИ И СИСТЕМЫ": ["engine", "system", "hub", "interface"],
        "🤖 БОТЫ": ["bot"],
        "🔍 АНАЛИЗАТОРЫ": ["analyzer", "detector", "protector", "validator"],
        "🔧 МИКРОСЕРВИСЫ": ["service", "microservice", "gateway", "balancer"],
        "📊 УТИЛИТЫ": ["utils", "helper", "tool"],
        "📋 МОДЕЛИ": ["model", "base", "formatter"],
        "🔧 ИНТЕГРАЦИИ": ["integration", "caller", "connector"],
        "📊 ДОПОЛНИТЕЛЬНЫЕ": ["extra", "main", "backup", "__init__", "test"]
    }
    
    # Общая статистика
    total_files = 0
    total_by_type = defaultdict(int)
    total_by_category = defaultdict(int)
    undefined_files = []
    
    print("\n📊 ДЕТАЛЬНАЯ СТАТИСТИКА ПО КАТЕГОРИЯМ:")
    print("=" * 80)
    
    for category_name, category_path in categories.items():
        if not os.path.exists(category_path):
            print(f"\n{category_name}: ❌ Папка не найдена")
            continue
            
        print(f"\n{category_name}:")
        print("-" * 50)
        
        files_by_type = defaultdict(list)
        category_files = 0
        
        # Сканируем файлы в категории
        for file in os.listdir(category_path):
            if file.endswith('.py'):
                category_files += 1
                total_files += 1
                file_lower = file.lower()
                
                # Определяем тип компонента
                categorized = False
                for type_name, keywords in component_types.items():
                    for keyword in keywords:
                        if keyword in file_lower:
                            files_by_type[type_name].append(file)
                            total_by_type[type_name] += 1
                            categorized = True
                            break
                    if categorized:
                        break
                
                # Если не определили тип
                if not categorized:
                    files_by_type["❓ НЕОПРЕДЕЛЕННЫЕ"].append(file)
                    total_by_type["❓ НЕОПРЕДЕЛЕННЫЕ"] += 1
                    undefined_files.append(f"{category_name}: {file}")
        
        total_by_category[category_name] = category_files
        
        # Выводим результаты для категории
        for type_name, files in files_by_type.items():
            if files:
                print(f"  {type_name}: {len(files)} файлов")
                for file in sorted(files)[:5]:  # Показываем первые 5 файлов
                    print(f"    • {file}")
                if len(files) > 5:
                    print(f"    ... и еще {len(files) - 5} файлов")
        
        print(f"  📊 ИТОГО: {category_files} файлов")
    
    # Итоговая статистика
    print("\n🎯 ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 80)
    
    print("\n📁 ПО КАТЕГОРИЯМ:")
    for category, count in total_by_category.items():
        print(f"  {category}: {count} файлов")
    
    print(f"\n📊 ВСЕГО ФАЙЛОВ: {total_files}")
    
    print("\n⚙️ ПО ТИПАМ КОМПОНЕНТОВ:")
    for type_name, count in total_by_type.items():
        percentage = (count / total_files * 100) if total_files > 0 else 0
        print(f"  {type_name}: {count} файлов ({percentage:.1f}%)")
    
    # Анализ неопределенных файлов
    print("\n❓ АНАЛИЗ НЕОПРЕДЕЛЕННЫХ ФАЙЛОВ:")
    print("=" * 80)
    print(f"Всего неопределенных файлов: {len(undefined_files)}")
    
    if undefined_files:
        print("\n📋 СПИСОК НЕОПРЕДЕЛЕННЫХ ФАЙЛОВ:")
        for file_info in undefined_files:
            print(f"  • {file_info}")
        
        print("\n🔍 АНАЛИЗ НЕОПРЕДЕЛЕННЫХ ФАЙЛОВ:")
        print("Эти файлы не попали ни в одну категорию потому что:")
        print("1. Имеют уникальные названия без стандартных суффиксов")
        print("2. Являются специализированными компонентами")
        print("3. Могут быть утилитами или вспомогательными модулями")
        print("4. Возможно, требуют ручной классификации")
    
    return total_files, total_by_type, total_by_category, undefined_files

def analyze_undefined_files_detailed():
    """Детальный анализ неопределенных файлов"""
    print("\n🔍 ДЕТАЛЬНЫЙ АНАЛИЗ НЕОПРЕДЕЛЕННЫХ ФАЙЛОВ:")
    print("=" * 80)
    
    undefined_analysis = {
        "🤖 AI-СИСТЕМЫ": [],
        "📋 МОДЕЛИ И ДАННЫЕ": [],
        "🔧 СЕРВИСЫ": [],
        "📊 УТИЛИТЫ": [],
        "🔗 ИНТЕГРАЦИИ": [],
        "❓ ДРУГИЕ": []
    }
    
    # Анализируем неопределенные файлы из AI Agents
    ai_agents_path = "security/ai_agents/"
    if os.path.exists(ai_agents_path):
        for file in os.listdir(ai_agents_path):
            if file.endswith('.py'):
                file_lower = file.lower()
                
                # Проверяем, является ли файл неопределенным
                is_undefined = True
                for keyword in ["agent", "manager", "engine", "system", "hub", "interface", "bot", "analyzer", "detector", "protector", "validator", "extra", "main", "utils", "backup", "__init__"]:
                    if keyword in file_lower:
                        is_undefined = False
                        break
                
                if is_undefined:
                    # Классифицируем по содержимому
                    if "ai" in file_lower or "master" in file_lower:
                        undefined_analysis["🤖 AI-СИСТЕМЫ"].append(file)
                    elif "model" in file_lower or "base" in file_lower or "formatter" in file_lower:
                        undefined_analysis["📋 МОДЕЛИ И ДАННЫЕ"].append(file)
                    elif "service" in file_lower or "caller" in file_lower:
                        undefined_analysis["🔧 СЕРВИСЫ"].append(file)
                    elif "utils" in file_lower or "helper" in file_lower:
                        undefined_analysis["📊 УТИЛИТЫ"].append(file)
                    elif "integration" in file_lower or "messenger" in file_lower:
                        undefined_analysis["🔗 ИНТЕГРАЦИИ"].append(file)
                    else:
                        undefined_analysis["❓ ДРУГИЕ"].append(file)
    
    # Выводим результаты
    for category, files in undefined_analysis.items():
        if files:
            print(f"\n{category} ({len(files)} файлов):")
            for file in files:
                print(f"  • {file}")
    
    return undefined_analysis

def main():
    """Основная функция"""
    print("🚀 ОБЪЕДИНЕННЫЙ АНАЛИЗ СИСТЕМЫ ALADDIN")
    print("=" * 80)
    
    # Объединенный анализ
    total_files, total_by_type, total_by_category, undefined_files = analyze_all_categories_unified()
    
    # Детальный анализ неопределенных файлов
    undefined_analysis = analyze_undefined_files_detailed()
    
    print("\n🎯 ЗАКЛЮЧЕНИЕ:")
    print("=" * 80)
    print("✅ Создана полная карта системы ALADDIN")
    print("✅ Определены все типы компонентов")
    print("✅ Выявлены неопределенные файлы")
    print("✅ Предложена классификация для неопределенных файлов")

if __name__ == "__main__":
    main()