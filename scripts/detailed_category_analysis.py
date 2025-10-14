#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Детальный анализ системы ALADDIN по категориям
Полное разделение компонентов по их реальному типу
"""

import sys
import os
import json
from pathlib import Path
from collections import defaultdict

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

def analyze_ai_agents_detailed():
    """Детальный анализ AI Agents с разделением по типам"""
    print("🤖 ДЕТАЛЬНЫЙ АНАЛИЗ AI AGENTS:")
    print("=" * 60)
    
    ai_agents_path = "security/ai_agents/"
    
    if not os.path.exists(ai_agents_path):
        print("❌ Папка AI Agents не найдена!")
        return
    
    # Категории компонентов
    categories = {
        "🤖 НАСТОЯЩИЕ AI АГЕНТЫ": ["agent"],
        "⚙️ МЕНЕДЖЕРЫ": ["manager"],
        "🔧 ДВИЖКИ И СИСТЕМЫ": ["engine", "system", "hub", "interface"],
        "🤖 БОТЫ": ["bot"],
        "🔍 АНАЛИЗАТОРЫ И ДЕТЕКТОРЫ": ["analyzer", "detector", "protector", "validator"],
        "📊 ДОПОЛНИТЕЛЬНЫЕ": ["extra", "main", "utils", "backup", "__init__"]
    }
    
    files_by_category = defaultdict(list)
    total_files = 0
    
    # Сканируем все файлы
    for file in os.listdir(ai_agents_path):
        if file.endswith('.py'):
            total_files += 1
            file_lower = file.lower()
            
            # Определяем категорию
            categorized = False
            for category, keywords in categories.items():
                for keyword in keywords:
                    if keyword in file_lower:
                        files_by_category[category].append(file)
                        categorized = True
                        break
                if categorized:
                    break
            
            # Если не определили категорию
            if not categorized:
                files_by_category["❓ НЕОПРЕДЕЛЕННЫЕ"].append(file)
    
    # Выводим результаты
    for category, files in files_by_category.items():
        if files:
            print(f"\n{category} ({len(files)} файлов):")
            print("-" * 40)
            for file in sorted(files):
                print(f"  • {file}")
    
    print(f"\n📊 ИТОГО ФАЙЛОВ: {total_files}")
    
    return files_by_category, total_files

def analyze_security_bots_detailed():
    """Детальный анализ Security Bots"""
    print("\n🤖 ДЕТАЛЬНЫЙ АНАЛИЗ SECURITY BOTS:")
    print("=" * 60)
    
    bots_path = "security/bots/"
    
    if not os.path.exists(bots_path):
        print("❌ Папка Security Bots не найдена!")
        return
    
    categories = {
        "🤖 ОСНОВНЫЕ БОТЫ": ["bot"],
        "🔧 ДВИЖКИ И СИСТЕМЫ": ["engine", "system"],
        "⚙️ МЕНЕДЖЕРЫ": ["manager"],
        "🔍 АНАЛИЗАТОРЫ": ["analyzer", "detector"],
        "📊 ДОПОЛНИТЕЛЬНЫЕ": ["extra", "main", "utils", "backup", "__init__"]
    }
    
    files_by_category = defaultdict(list)
    total_files = 0
    
    for file in os.listdir(bots_path):
        if file.endswith('.py'):
            total_files += 1
            file_lower = file.lower()
            
            categorized = False
            for category, keywords in categories.items():
                for keyword in keywords:
                    if keyword in file_lower:
                        files_by_category[category].append(file)
                        categorized = True
                        break
                if categorized:
                    break
            
            if not categorized:
                files_by_category["❓ НЕОПРЕДЕЛЕННЫЕ"].append(file)
    
    for category, files in files_by_category.items():
        if files:
            print(f"\n{category} ({len(files)} файлов):")
            print("-" * 40)
            for file in sorted(files):
                print(f"  • {file}")
    
    print(f"\n📊 ИТОГО ФАЙЛОВ: {total_files}")
    
    return files_by_category, total_files

def analyze_managers_detailed():
    """Детальный анализ Managers"""
    print("\n⚙️ ДЕТАЛЬНЫЙ АНАЛИЗ MANAGERS:")
    print("=" * 60)
    
    managers_path = "security/managers/"
    
    if not os.path.exists(managers_path):
        print("❌ Папка Managers не найдена!")
        return
    
    categories = {
        "⚙️ ОСНОВНЫЕ МЕНЕДЖЕРЫ": ["manager"],
        "🔧 ДВИЖКИ И СИСТЕМЫ": ["engine", "system"],
        "🤖 БОТЫ": ["bot"],
        "🔍 АНАЛИЗАТОРЫ": ["analyzer", "detector"],
        "📊 ДОПОЛНИТЕЛЬНЫЕ": ["extra", "main", "utils", "backup", "__init__"]
    }
    
    files_by_category = defaultdict(list)
    total_files = 0
    
    for file in os.listdir(managers_path):
        if file.endswith('.py'):
            total_files += 1
            file_lower = file.lower()
            
            categorized = False
            for category, keywords in categories.items():
                for keyword in keywords:
                    if keyword in file_lower:
                        files_by_category[category].append(file)
                        categorized = True
                        break
                if categorized:
                    break
            
            if not categorized:
                files_by_category["❓ НЕОПРЕДЕЛЕННЫЕ"].append(file)
    
    for category, files in files_by_category.items():
        if files:
            print(f"\n{category} ({len(files)} файлов):")
            print("-" * 40)
            for file in sorted(files):
                print(f"  • {file}")
    
    print(f"\n📊 ИТОГО ФАЙЛОВ: {total_files}")
    
    return files_by_category, total_files

def analyze_microservices_detailed():
    """Детальный анализ Microservices"""
    print("\n🔧 ДЕТАЛЬНЫЙ АНАЛИЗ MICROSERVICES:")
    print("=" * 60)
    
    microservices_path = "security/microservices/"
    
    if not os.path.exists(microservices_path):
        print("❌ Папка Microservices не найдена!")
        return
    
    categories = {
        "🔧 ОСНОВНЫЕ МИКРОСЕРВИСЫ": ["service", "microservice"],
        "⚙️ МЕНЕДЖЕРЫ": ["manager"],
        "🔍 АНАЛИЗАТОРЫ": ["analyzer", "detector"],
        "📊 ДОПОЛНИТЕЛЬНЫЕ": ["extra", "main", "utils", "backup", "__init__"]
    }
    
    files_by_category = defaultdict(list)
    total_files = 0
    
    for file in os.listdir(microservices_path):
        if file.endswith('.py'):
            total_files += 1
            file_lower = file.lower()
            
            categorized = False
            for category, keywords in categories.items():
                for keyword in keywords:
                    if keyword in file_lower:
                        files_by_category[category].append(file)
                        categorized = True
                        break
                if categorized:
                    break
            
            if not categorized:
                files_by_category["❓ НЕОПРЕДЕЛЕННЫЕ"].append(file)
    
    for category, files in files_by_category.items():
        if files:
            print(f"\n{category} ({len(files)} файлов):")
            print("-" * 40)
            for file in sorted(files):
                print(f"  • {file}")
    
    print(f"\n📊 ИТОГО ФАЙЛОВ: {total_files}")
    
    return files_by_category, total_files

def analyze_all_categories_detailed():
    """Детальный анализ всех категорий"""
    print("🚀 ДЕТАЛЬНЫЙ АНАЛИЗ ВСЕХ КАТЕГОРИЙ ALADDIN")
    print("=" * 80)
    
    # Анализируем каждую категорию
    ai_agents_data = analyze_ai_agents_detailed()
    bots_data = analyze_security_bots_detailed()
    managers_data = analyze_managers_detailed()
    microservices_data = analyze_microservices_detailed()
    
    # Итоговая статистика
    print("\n🎯 ИТОГОВАЯ СТАТИСТИКА ПО КАТЕГОРИЯМ:")
    print("=" * 60)
    
    total_files = 0
    if ai_agents_data:
        total_files += ai_agents_data[1]
        print(f"🤖 AI Agents: {ai_agents_data[1]} файлов")
    if bots_data:
        total_files += bots_data[1]
        print(f"🤖 Security Bots: {bots_data[1]} файлов")
    if managers_data:
        total_files += managers_data[1]
        print(f"⚙️ Managers: {managers_data[1]} файлов")
    if microservices_data:
        total_files += microservices_data[1]
        print(f"🔧 Microservices: {microservices_data[1]} файлов")
    
    print(f"\n📊 ВСЕГО ФАЙЛОВ: {total_files}")

def main():
    """Основная функция"""
    if len(sys.argv) > 1:
        category = sys.argv[1].lower()
        
        if category == "ai_agents" or category == "agents":
            analyze_ai_agents_detailed()
        elif category == "bots":
            analyze_security_bots_detailed()
        elif category == "managers":
            analyze_managers_detailed()
        elif category == "microservices":
            analyze_microservices_detailed()
        else:
            print("❌ Неизвестная категория! Используйте: ai_agents, bots, managers, microservices")
    else:
        analyze_all_categories_detailed()

if __name__ == "__main__":
    main()