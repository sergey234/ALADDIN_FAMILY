#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Глубокий анализ всех компонентов системы

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-11
"""

import os
import ast
import sys
from pathlib import Path
import re

def find_component_in_system(component_name, search_paths):
    """Поиск компонента в системе"""
    found_files = []
    
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
            
        for file_path in Path(search_path).rglob('*.py'):
            if file_path.name.startswith('__'):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Поиск по имени класса
                if component_name.lower() in content.lower():
                    # Проверяем, что это действительно определение класса
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            if component_name.lower() in node.name.lower():
                                found_files.append({
                                    'file': str(file_path),
                                    'class': node.name,
                                    'line': node.lineno
                                })
            except Exception as e:
                continue
    
    return found_files

def analyze_recommended_components():
    """Анализ рекомендованных компонентов"""
    
    print("🔍 ГЛУБОКИЙ АНАЛИЗ ВСЕХ КОМПОНЕНТОВ СИСТЕМЫ")
    print("="*80)
    
    # Рекомендованные компоненты для поиска
    recommended_components = [
        "AntiFraudMasterAI",
        "VoiceAnalysisEngine", 
        "DeepfakeProtectionSystem",
        "FinancialProtectionHub",
        "EmergencyResponseSystem",
        "ElderlyProtectionInterface",
        "MobileUserAIAgent",
        "VPNSecuritySystem",
        "AntivirusSecuritySystem",
        "ZeroTrustManager",
        "RansomwareProtection",
        "SecureConfigManager"
    ]
    
    # Пути для поиска
    search_paths = [
        '/Users/sergejhlystov/ALADDIN_NEW/security',
        '/Users/sergejhlystov/ALADDIN_NEW/core',
        '/Users/sergejhlystov/ALADDIN_NEW/ai_agents',
        '/Users/sergejhlystov/ALADDIN_NEW/bots',
        '/Users/sergejhlystov/ALADDIN_NEW/microservices',
        '/Users/sergejhlystov/ALADDIN_NEW/family',
        '/Users/sergejhlystov/ALADDIN_NEW/compliance',
        '/Users/sergejhlystov/ALADDIN_NEW/privacy',
        '/Users/sergejhlystov/ALADDIN_NEW/reactive',
        '/Users/sergejhlystov/ALADDIN_NEW/active',
        '/Users/sergejhlystov/ALADDIN_NEW/preliminary',
        '/Users/sergejhlystov/ALADDIN_NEW/orchestration',
        '/Users/sergejhlystov/ALADDIN_NEW/scaling'
    ]
    
    found_components = {}
    missing_components = []
    
    print("🔍 ПОИСК РЕКОМЕНДОВАННЫХ КОМПОНЕНТОВ:")
    print("-" * 50)
    
    for component in recommended_components:
        print(f"\n🔍 Поиск: {component}")
        found_files = find_component_in_system(component, search_paths)
        
        if found_files:
            found_components[component] = found_files
            print(f"  ✅ НАЙДЕН в {len(found_files)} файлах:")
            for file_info in found_files:
                print(f"    📄 {file_info['file']}")
                print(f"    🏗️ Класс: {file_info['class']} (строка {file_info['line']})")
        else:
            missing_components.append(component)
            print(f"  ❌ НЕ НАЙДЕН")
    
    # Анализ найденных компонентов
    print(f"\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
    print("="*80)
    print(f"✅ НАЙДЕНО КОМПОНЕНТОВ: {len(found_components)}")
    print(f"❌ ОТСУТСТВУЕТ КОМПОНЕНТОВ: {len(missing_components)}")
    
    if found_components:
        print(f"\n✅ НАЙДЕННЫЕ КОМПОНЕНТЫ:")
        for component, files in found_components.items():
            print(f"  🔹 {component}: {len(files)} файлов")
    
    if missing_components:
        print(f"\n❌ ОТСУТСТВУЮЩИЕ КОМПОНЕНТЫ:")
        for i, component in enumerate(missing_components, 1):
            print(f"  {i:2d}. {component}")
    
    # Дополнительный поиск по ключевым словам
    print(f"\n🔍 ДОПОЛНИТЕЛЬНЫЙ ПОИСК ПО КЛЮЧЕВЫМ СЛОВАМ:")
    print("-" * 50)
    
    keyword_search = {
        "AntiFraud": ["anti_fraud", "antifraud", "fraud"],
        "VoiceAnalysis": ["voice_analysis", "voiceanalysis", "voice"],
        "Deepfake": ["deepfake", "deep_fake", "fake"],
        "Financial": ["financial", "finance", "banking"],
        "Emergency": ["emergency", "emergency_response", "crisis"],
        "Elderly": ["elderly", "elder", "senior"],
        "Mobile": ["mobile", "mobile_user", "mobile_ai"],
        "VPN": ["vpn", "virtual_private", "tunnel"],
        "Antivirus": ["antivirus", "antimalware", "malware"],
        "ZeroTrust": ["zero_trust", "zerotrust", "zero-trust"],
        "Ransomware": ["ransomware", "ransom", "crypto"],
        "SecureConfig": ["secure_config", "config_manager", "configuration"]
    }
    
    keyword_found = {}
    
    for category, keywords in keyword_search.items():
        found_files = []
        for search_path in search_paths:
            if not os.path.exists(search_path):
                continue
                
            for file_path in Path(search_path).rglob('*.py'):
                if file_path.name.startswith('__'):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                    
                    for keyword in keywords:
                        if keyword.lower() in content:
                            found_files.append(str(file_path))
                            break
                except Exception:
                    continue
        
        if found_files:
            keyword_found[category] = list(set(found_files))
            print(f"  🔍 {category}: {len(keyword_found[category])} файлов")
    
    # Анализ структуры системы
    print(f"\n📁 АНАЛИЗ СТРУКТУРЫ СИСТЕМЫ:")
    print("-" * 50)
    
    total_files = 0
    total_classes = 0
    total_functions = 0
    total_lines = 0
    
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
            
        dir_files = 0
        dir_classes = 0
        dir_functions = 0
        dir_lines = 0
        
        for file_path in Path(search_path).rglob('*.py'):
            if file_path.name.startswith('__'):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                dir_lines += len(lines)
                
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        dir_classes += 1
                    elif isinstance(node, ast.FunctionDef):
                        dir_functions += 1
                
                dir_files += 1
            except Exception:
                continue
        
        if dir_files > 0:
            relative_path = os.path.relpath(search_path, '/Users/sergejhlystov/ALADDIN_NEW')
            print(f"  📁 {relative_path}: {dir_files} файлов, {dir_classes} классов, {dir_functions} функций, {dir_lines} строк")
            
            total_files += dir_files
            total_classes += dir_classes
            total_functions += dir_functions
            total_lines += dir_lines
    
    print(f"\n📊 ОБЩАЯ СТАТИСТИКА СИСТЕМЫ:")
    print("="*80)
    print(f"📁 Всего файлов: {total_files}")
    print(f"🏗️ Всего классов: {total_classes}")
    print(f"⚙️ Всего функций: {total_functions}")
    print(f"📄 Всего строк: {total_lines}")
    
    # Финальный отчет
    print(f"\n🎯 ФИНАЛЬНЫЙ ОТЧЕТ:")
    print("="*80)
    
    print(f"✅ КОМПОНЕНТЫ НАЙДЕНЫ:")
    for component, files in found_components.items():
        print(f"  {component}: {len(files)} файлов")
    
    print(f"\n❌ КОМПОНЕНТЫ ОТСУТСТВУЮТ:")
    for i, component in enumerate(missing_components, 1):
        print(f"  {i:2d}. {component}")
    
    print(f"\n🔍 ДОПОЛНИТЕЛЬНЫЕ НАХОДКИ:")
    for category, files in keyword_found.items():
        print(f"  {category}: {len(files)} файлов")
    
    return {
        'found_components': found_components,
        'missing_components': missing_components,
        'keyword_found': keyword_found,
        'total_stats': {
            'files': total_files,
            'classes': total_classes,
            'functions': total_functions,
            'lines': total_lines
        }
    }

def main():
    """Главная функция"""
    analyze_recommended_components()

if __name__ == "__main__":
    main()