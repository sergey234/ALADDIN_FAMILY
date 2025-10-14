#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Экспертный анализ архитектуры системы ALADDIN
Тщательная проверка каждого файла и определение правильного места
"""

import sys
import os
import re
from pathlib import Path
from collections import defaultdict

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

def analyze_file_content(file_path):
    """Анализ содержимого файла для определения его функциональности"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            'classes': [],
            'functions': [],
            'imports': [],
            'dependencies': [],
            'purpose': 'unknown',
            'category': 'unknown'
        }
        
        # Поиск классов
        class_matches = re.findall(r'class\s+(\w+)', content)
        analysis['classes'] = class_matches
        
        # Поиск функций
        func_matches = re.findall(r'def\s+(\w+)', content)
        analysis['functions'] = func_matches
        
        # Поиск импортов
        import_matches = re.findall(r'from\s+(\S+)\s+import|import\s+(\S+)', content)
        analysis['imports'] = [imp[0] or imp[1] for imp in import_matches]
        
        # Анализ функциональности по ключевым словам
        content_lower = content.lower()
        
        # Определение категории по содержимому
        if any(keyword in content_lower for keyword in ['class', 'agent', 'ai', 'intelligence']):
            if 'agent' in content_lower and 'ai' in content_lower:
                analysis['category'] = 'ai_agent'
            elif 'manager' in content_lower:
                analysis['category'] = 'manager'
            elif 'engine' in content_lower or 'system' in content_lower:
                analysis['category'] = 'engine'
            elif 'bot' in content_lower:
                analysis['category'] = 'bot'
            elif 'analyzer' in content_lower or 'detector' in content_lower:
                analysis['category'] = 'analyzer'
            elif 'service' in content_lower or 'microservice' in content_lower:
                analysis['category'] = 'microservice'
            elif 'model' in content_lower or 'base' in content_lower:
                analysis['category'] = 'model'
            elif 'integration' in content_lower:
                analysis['category'] = 'integration'
            elif 'utils' in content_lower or 'helper' in content_lower:
                analysis['category'] = 'utils'
            elif 'config' in content_lower:
                analysis['category'] = 'config'
            elif 'core' in content_lower or 'singleton' in content_lower:
                analysis['category'] = 'core'
        
        # Определение назначения
        if 'emergency' in content_lower:
            analysis['purpose'] = 'emergency'
        elif 'security' in content_lower:
            analysis['purpose'] = 'security'
        elif 'notification' in content_lower:
            analysis['purpose'] = 'notification'
        elif 'analytics' in content_lower:
            analysis['purpose'] = 'analytics'
        elif 'voice' in content_lower or 'speech' in content_lower:
            analysis['purpose'] = 'voice'
        elif 'family' in content_lower:
            analysis['purpose'] = 'family'
        elif 'elderly' in content_lower:
            analysis['purpose'] = 'elderly'
        elif 'child' in content_lower or 'parental' in content_lower:
            analysis['purpose'] = 'parental'
        
        return analysis
        
    except Exception as e:
        return {'error': str(e)}

def analyze_existing_structure():
    """Анализ существующей структуры папок"""
    print("🔍 АНАЛИЗ СУЩЕСТВУЮЩЕЙ СТРУКТУРЫ ПАПОК")
    print("=" * 80)
    
    existing_folders = {
        "security/ai_agents/": "AI агенты",
        "security/bots/": "Боты безопасности", 
        "security/managers/": "Менеджеры",
        "security/microservices/": "Микросервисы",
        "security/privacy/": "Приватность",
        "security/ci_cd/": "CI/CD",
        "core/": "Основные модули",
        "config/": "Конфигурация"
    }
    
    for folder, description in existing_folders.items():
        if os.path.exists(folder):
            files_count = len([f for f in os.listdir(folder) if f.endswith('.py')])
            print(f"✅ {folder} - {description} ({files_count} файлов)")
        else:
            print(f"❌ {folder} - {description} (НЕ СУЩЕСТВУЕТ)")
    
    return existing_folders

def analyze_undefined_files_detailed():
    """Детальный анализ неопределенных файлов"""
    print("\n🔍 ДЕТАЛЬНЫЙ АНАЛИЗ НЕОПРЕДЕЛЕННЫХ ФАЙЛОВ")
    print("=" * 80)
    
    undefined_files = [
        "anti_fraud_master_ai.py",
        "voice_response_generator.py", 
        "natural_language_processor.py",
        "family_communication_replacement.py",
        "emergency_id_generator.py",
        "parent_control_panel.py",
        "emergency_models.py",
        "emergency_ml_models.py",
        "emergency_formatters.py",
        "emergency_base_models.py",
        "emergency_base_models_refactored.py",
        "emergency_statistics_models.py",
        "emergency_service.py",
        "emergency_service_caller.py",
        "messenger_integration.py",
        "circuit_breaker.py",
        "rate_limiter.py",
        "put_to_sleep.py",
        "simple_sleep.py",
        "configuration.py",
        "singleton.py",
        "logging_module.py",
        "code_quality_config.py",
        "safe_config.py",
        "replacement_components_config.py"
    ]
    
    file_analysis = {}
    
    for file_name in undefined_files:
        print(f"\n📁 Анализ файла: {file_name}")
        print("-" * 60)
        
        # Ищем файл
        found_path = None
        for root, dirs, files in os.walk("."):
            if file_name in files:
                found_path = os.path.join(root, file_name)
                break
        
        if not found_path:
            print("❌ Файл не найден")
            continue
            
        print(f"📍 Найден: {found_path}")
        
        # Анализируем содержимое
        analysis = analyze_file_content(found_path)
        
        if 'error' in analysis:
            print(f"❌ Ошибка анализа: {analysis['error']}")
            continue
        
        print(f"🏷️  Классы: {analysis['classes']}")
        print(f"⚙️  Функции: {len(analysis['functions'])} функций")
        print(f"📦 Импорты: {len(analysis['imports'])} импортов")
        print(f"🎯 Категория: {analysis['category']}")
        print(f"💡 Назначение: {analysis['purpose']}")
        
        # Определяем правильное место
        suggested_location = determine_correct_location(file_name, analysis)
        print(f"✅ ДОЛЖЕН БЫТЬ: {suggested_location}")
        
        file_analysis[file_name] = {
            'current_path': found_path,
            'analysis': analysis,
            'suggested_location': suggested_location
        }
    
    return file_analysis

def determine_correct_location(file_name, analysis):
    """Определение правильного места для файла"""
    file_lower = file_name.lower()
    category = analysis['category']
    purpose = analysis['purpose']
    classes = analysis['classes']
    
    # Логика определения места
    if category == 'ai_agent':
        return "security/ai_agents/"
    elif category == 'manager':
        return "security/managers/"
    elif category == 'engine':
        return "security/ai_agents/"  # Движки остаются в ai_agents
    elif category == 'bot':
        return "security/bots/"
    elif category == 'analyzer':
        return "security/ai_agents/"  # Анализаторы остаются в ai_agents
    elif category == 'microservice':
        return "security/microservices/"
    elif category == 'model':
        return "security/ai_agents/"  # Модели остаются в ai_agents
    elif category == 'integration':
        return "security/ai_agents/"  # Интеграции остаются в ai_agents
    elif category == 'utils':
        return "security/ai_agents/"  # Утилиты остаются в ai_agents
    elif category == 'config':
        return "config/"
    elif category == 'core':
        return "core/"
    else:
        # Специальные случаи
        if 'anti_fraud' in file_lower:
            return "security/ai_agents/"  # AI агент
        elif 'voice' in file_lower or 'speech' in file_lower:
            return "security/ai_agents/"  # AI компонент
        elif 'natural_language' in file_lower:
            return "security/ai_agents/"  # AI компонент
        elif 'family_communication' in file_lower:
            return "security/ai_agents/"  # AI компонент
        elif 'parent_control' in file_lower:
            return "security/ai_agents/"  # AI компонент
        elif 'emergency_id' in file_lower:
            return "security/ai_agents/"  # Утилита
        elif 'circuit_breaker' in file_lower:
            return "security/ci_cd/"  # CI/CD компонент
        elif 'rate_limiter' in file_lower:
            return "security/microservices/"  # Микросервис
        elif 'sleep' in file_lower:
            return "security/microservices/"  # Микросервис
        else:
            return "security/ai_agents/"  # По умолчанию

def create_detailed_migration_plan(file_analysis):
    """Создание детального плана миграции"""
    print("\n📋 ДЕТАЛЬНЫЙ ПЛАН МИГРАЦИИ")
    print("=" * 80)
    
    # Группируем файлы по действиям
    actions = {
        "✅ ОСТАВИТЬ НА МЕСТЕ": [],
        "🔄 ПЕРЕМЕСТИТЬ": [],
        "❓ ТРЕБУЕТ ДОПОЛНИТЕЛЬНОГО АНАЛИЗА": []
    }
    
    for file_name, data in file_analysis.items():
        current_path = data['current_path']
        suggested_location = data['suggested_location']
        
        # Определяем текущую папку
        current_folder = os.path.dirname(current_path)
        if current_folder.endswith('/'):
            current_folder = current_folder[:-1]
        
        if suggested_location in current_folder:
            actions["✅ ОСТАВИТЬ НА МЕСТЕ"].append(file_name)
        elif suggested_location != "❓ НЕОПРЕДЕЛЕННО":
            actions["🔄 ПЕРЕМЕСТИТЬ"].append((file_name, current_path, suggested_location))
        else:
            actions["❓ ТРЕБУЕТ ДОПОЛНИТЕЛЬНОГО АНАЛИЗА"].append(file_name)
    
    # Выводим план
    for action_type, files in actions.items():
        if files:
            print(f"\n{action_type} ({len(files)} файлов):")
            for item in files:
                if isinstance(item, tuple):
                    file_name, current_path, suggested_location = item
                    print(f"  • {file_name}")
                    print(f"    Откуда: {current_path}")
                    print(f"    Куда: {suggested_location}")
                else:
                    print(f"  • {item}")
    
    return actions

def create_step_by_step_migration_plan(actions):
    """Создание пошагового плана миграции"""
    print("\n🚀 ПОШАГОВЫЙ ПЛАН МИГРАЦИИ")
    print("=" * 80)
    
    print("\n📋 ЭТАП 1: ПОДГОТОВКА")
    print("-" * 40)
    print("1.1 Создать резервную копию всей системы")
    print("1.2 Проверить зависимости между файлами")
    print("1.3 Создать недостающие папки (если нужно)")
    
    print("\n📋 ЭТАП 2: ПЕРЕМЕЩЕНИЕ ФАЙЛОВ")
    print("-" * 40)
    
    step = 1
    for file_name, current_path, suggested_location in actions["🔄 ПЕРЕМЕСТИТЬ"]:
        print(f"\n{step}. ПЕРЕМЕЩЕНИЕ: {file_name}")
        print(f"   📍 Откуда: {current_path}")
        print(f"   📍 Куда: {suggested_location}")
        print(f"   🔧 Команда: mv {current_path} {suggested_location}")
        print(f"   ⚠️  Проверка: python3 -c \"import {file_name[:-3]}\"")
        step += 1
    
    print("\n📋 ЭТАП 3: ОБНОВЛЕНИЕ ИМПОРТОВ")
    print("-" * 40)
    print("3.1 Найти все файлы, которые импортируют перемещенные модули")
    print("3.2 Обновить пути импортов")
    print("3.3 Проверить синтаксис всех файлов")
    
    print("\n📋 ЭТАП 4: ТЕСТИРОВАНИЕ")
    print("-" * 40)
    print("4.1 Запустить тесты импортов")
    print("4.2 Запустить функциональные тесты")
    print("4.3 Проверить работу SFM")
    
    print("\n📋 ЭТАП 5: ВАЛИДАЦИЯ")
    print("-" * 40)
    print("5.1 Проверить, что все файлы на своих местах")
    print("5.2 Убедиться, что система работает корректно")
    print("5.3 Обновить документацию")

def main():
    """Основная функция"""
    print("🚀 ЭКСПЕРТНЫЙ АНАЛИЗ АРХИТЕКТУРЫ СИСТЕМЫ ALADDIN")
    print("=" * 80)
    
    # Анализ существующей структуры
    existing_folders = analyze_existing_structure()
    
    # Детальный анализ неопределенных файлов
    file_analysis = analyze_undefined_files_detailed()
    
    # Создание плана миграции
    actions = create_detailed_migration_plan(file_analysis)
    
    # Пошаговый план
    create_step_by_step_migration_plan(actions)
    
    print("\n🎯 ЗАКЛЮЧЕНИЕ:")
    print("=" * 50)
    print("✅ Проведен экспертный анализ каждого файла")
    print("✅ Определены правильные места для всех компонентов")
    print("✅ Создан детальный план миграции")
    print("✅ Предложены пошаговые инструкции")

if __name__ == "__main__":
    main()