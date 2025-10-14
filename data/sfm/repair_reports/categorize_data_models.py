#!/usr/bin/env python3
"""
Скрипт для категоризации UNKNOWN функций, которые являются моделями данных
Определяет типы на основе контекста использования
"""

import json
import os
import re
from datetime import datetime
from collections import Counter

def categorize_data_model(func_id, func_name, description):
    """Категоризирует модель данных на основе ID, имени и описания."""
    
    # Паттерны для определения типов моделей
    patterns = {
        'security_model': [
            r'security_', r'user.*session', r'rate.*limit', r'health.*check',
            r'load.*balancing', r'access.*control', r'authentication', r'authorization',
            r'device.*fingerprint', r'network.*monitoring', r'performance.*metrics',
            r'threat.*detection', r'intrusion.*attempt', r'circuit.*breaker',
            r'recovery.*plan', r'security.*alert', r'family.*contact', r'audit.*finding'
        ],
        'bot_model': [
            r'bot_', r'activity.*alert', r'user.*preference', r'message.*analysis',
            r'notification.*', r'telegram.*', r'whatsapp.*', r'instagram.*',
            r'parental.*control', r'emergency.*response', r'content.*analysis',
            r'child.*profile', r'emergency.*contact'
        ],
        'ai_agent_model': [
            r'ai_agent_', r'data.*protection.*result', r'behavior.*pattern',
            r'incident.*', r'threat.*intelligence', r'password.*metrics',
            r'emergency.*response.*system', r'network.*threat', r'compliance.*metrics',
            r'deepfake.*analysis', r'financial.*protection.*hub', r'performance.*metric',
            r'antifraud.*master', r'behaviormetrics', r'optimization.*recommendation',
            r'behaviorevent', r'mobile.*threat', r'incident.*response.*metrics',
            r'voice.*analysis.*engine', r'threat.*intelligence.*metrics',
            r'mobile.*device', r'behavior.*analysis', r'network.*analysis',
            r'threat.*indicator', r'emergency.*alert', r'password.*policy',
            r'financial.*risk.*assessment', r'voice.*analysis.*result'
        ],
        'monitoring_model': [
            r'performance.*metrics', r'optimization.*metrics', r'detection.*metrics',
            r'scaling.*metrics', r'orchestration.*metrics', r'cache.*metrics',
            r'network.*metric', r'load.*balancing.*metrics', r'circuit.*breaker.*event',
            r'interface.*event.*record', r'alert.*level', r'load.*balancing.*request',
            r'api.*log', r'intrusion.*attempt', r'circuit.*breaker.*record',
            r'access.*request', r'attack.*type', r'interface.*config',
            r'voice.*interface', r'fixed.*window', r'least.*connections.*algorithm',
            r'mobile.*app', r'circuit.*breakerevent', r'device.*status',
            r'instagram.*comment', r'instagram.*user', r'compliance.*requirement',
            r'malware.*protection', r'time.*based.*strategy', r'network.*monitoring',
            r'ratelimit.*request', r'device.*fingerprint', r'authentication.*interface',
            r'network.*packet', r'telegram.*message', r'incident.*response.*metrics',
            r'circuit.*breaker.*request', r'intrusion.*prevention', r'optimization.*result',
            r'performance.*optimizer', r'threat.*level', r'threat.*intelligence.*metrics',
            r'forensics.*report', r'sliding.*window', r'load.*balancing.*session',
            r'threat.*report', r'error.*rate.*based.*strategy', r'evidence',
            r'round.*robin.*algorithm', r'mobile.*device', r'emergency.*incident',
            r'anomaly.*detector', r'node.*info', r'behavior.*analysis',
            r'content.*filter', r'telegram.*user', r'network.*analysis',
            r'threat.*indicator', r'api.*route', r'auto.*save', r'control.*rule',
            r'emergency.*response', r'circuit.*breaker.*config', r'emergency.*contact.*info',
            r'interface.*record', r'emergency.*alert', r'child.*protection',
            r'policy.*rule', r'cache.*metrics', r'child.*profile', r'ratelimiter',
            r'password.*policy', r'web.*interface', r'financial.*risk.*assessment',
            r'api.*key', r'elderly.*protection', r'interface.*response',
            r'network.*flow', r'api.*response', r'emergency.*contact', r'threat.*type',
            r'voice.*analysis.*result', r'whatsapp.*message', r'child.*activity.*summary'
        ],
        'utility_model': [
            r'test_', r'color.*scheme', r'optimization.*metrics', r'cache.*entry',
            r'api.*interface', r'token.*bucket', r'scam.*pattern', r'count.*based.*strategy',
            r'pbkdf2.*hmac', r'circuit.*breaker.*response', r'network.*alert',
            r'metric.*data', r'network.*device', r'health.*check.*interface',
            r'parental.*controls', r'device.*type', r'notification.*',
            r'access.*control', r'scaling.*decision', r'scaling.*rule',
            r'metrics.*collector.*interface', r'threat.*status', r'interface.*request',
            r'api.*gateway', r'load.*balancing.*algorithm.*interface', r'action.*type',
            r'user', r'behaviormetrics', r'optimization.*recommendation',
            r'telegram.*security.*config', r'behaviorevent', r'interface.*event.*record',
            r'cluster.*analyzer', r'alert.*level', r'load.*balancing.*request',
            r'mobile.*threat', r'api.*log', r'notification.*response',
            r'intrusion.*attempt', r'circuit.*breaker.*record', r'recovery.*plan',
            r'access.*request', r'attack.*type', r'interface.*config',
            r'network.*metric', r'voice.*interface', r'fixed.*window',
            r'least.*connections.*algorithm', r'circuit.*breaker', r'mobile.*app',
            r'load.*balancing.*metrics', r'circuit.*breakerevent', r'test.*function',
            r'device.*status', r'instagram.*comment', r'instagram.*user',
            r'compliance.*requirement', r'malware.*protection', r'scaling.*metrics',
            r'orchestration.*metrics', r'time.*based.*strategy', r'detection.*metrics',
            r'network.*monitoring', r'ratelimit.*request', r'device.*fingerprint',
            r'authentication.*interface', r'network.*packet', r'telegram.*message',
            r'incident.*response.*metrics', r'circuit.*breaker.*request',
            r'intrusion.*prevention', r'optimization.*result', r'performance.*optimizer',
            r'threat.*level', r'threat.*intelligence.*metrics', r'forensics.*report',
            r'sliding.*window', r'load.*balancing.*session', r'threat.*report',
            r'error.*rate.*based.*strategy', r'evidence', r'round.*robin.*algorithm',
            r'mobile.*device', r'emergency.*incident', r'anomaly.*detector',
            r'node.*info', r'behavior.*analysis', r'content.*filter',
            r'telegram.*user', r'network.*analysis', r'threat.*indicator',
            r'api.*route', r'auto.*save', r'control.*rule', r'emergency.*response',
            r'circuit.*breaker.*config', r'emergency.*contact.*info',
            r'interface.*record', r'emergency.*alert', r'child.*protection',
            r'policy.*rule', r'cache.*metrics', r'child.*profile', r'ratelimiter',
            r'password.*policy', r'web.*interface', r'financial.*risk.*assessment',
            r'api.*key', r'elderly.*protection', r'interface.*response',
            r'network.*flow', r'api.*response', r'emergency.*contact', r'threat.*type',
            r'voice.*analysis.*result', r'whatsapp.*message', r'child.*activity.*summary'
        ]
    }
    
    # Анализируем ID, имя и описание
    text_to_analyze = f"{func_id} {func_name} {description}".lower()
    
    # Подсчитываем совпадения для каждого типа
    type_scores = {}
    for func_type, pattern_list in patterns.items():
        score = 0
        for pattern in pattern_list:
            matches = len(re.findall(pattern, text_to_analyze))
            score += matches
        type_scores[func_type] = score
    
    # Возвращаем тип с наибольшим количеством совпадений
    if type_scores:
        best_type = max(type_scores, key=type_scores.get)
        if type_scores[best_type] > 0:
            return best_type
    
    return "data_model"  # По умолчанию для моделей данных

def categorize_unknown_data_models(registry_file, max_fixes=10):
    """Категоризирует UNKNOWN функции, которые являются моделями данных."""
    
    # Загружаем реестр
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry_data = json.load(f)
    
    functions = registry_data.get("functions", {})
    unknown_functions = []
    
    # Находим UNKNOWN функции без путей (модели данных)
    for func_id, func_data in functions.items():
        func_type = func_data.get('function_type', '')
        file_path = func_data.get('file_path', '')
        if func_type == 'unknown' and not file_path:
            unknown_functions.append((func_id, func_data))
    
    print(f"🔍 КАТЕГОРИЗАЦИЯ МОДЕЛЕЙ ДАННЫХ")
    print(f"================================================")
    print(f"Всего функций в реестре: {len(functions)}")
    print(f"UNKNOWN моделей данных: {len(unknown_functions)}")
    print(f"Максимум исправлений за раз: {max_fixes}")
    print("")
    
    fixed_count = 0
    type_changes = Counter()
    
    for func_id, func_data in unknown_functions:
        if fixed_count >= max_fixes:
            break
            
        func_name = func_data.get('name', '')
        description = func_data.get('description', '')
        
        print(f"🔍 Анализируем {func_id}...")
        print(f"   Name: {func_name}")
        print(f"   Description: {description[:60]}...")
        
        # Категоризируем модель данных
        new_type = categorize_data_model(func_id, func_name, description)
        
        if new_type != "unknown":
            old_type = func_data.get('function_type', 'unknown')
            func_data['function_type'] = new_type
            func_data['last_updated'] = datetime.now().isoformat()
            
            type_changes[new_type] += 1
            fixed_count += 1
            
            print(f"   ✅ Тип изменен: {old_type} → {new_type}")
        else:
            print(f"   ⚠️ Тип не определен: {new_type}")
        
        print()
    
    # Сохраняем изменения
    with open(registry_file, 'w', encoding='utf-8') as f:
        json.dump(registry_data, f, ensure_ascii=False, indent=4)
    
    print(f"💾 Изменения сохранены в {registry_file}")
    
    # Подсчитываем оставшиеся UNKNOWN
    remaining_unknown = 0
    for func_id, func_data in functions.items():
        if func_data.get('function_type', '') == 'unknown':
            remaining_unknown += 1
    
    print(f"\n🎯 РЕЗУЛЬТАТ:")
    print(f"   Моделей категоризировано: {fixed_count}")
    print(f"   Осталось UNKNOWN функций: {remaining_unknown}")
    
    if type_changes:
        print(f"\n📊 НОВЫЕ ТИПЫ:")
        for func_type, count in type_changes.most_common():
            print(f"   {func_type}: +{count}")

if __name__ == "__main__":
    # Указываем путь к файлу реестра
    registry_path = 'data/sfm/function_registry.json'

    # Запускаем категоризацию моделей данных (тестируем на 10)
    categorize_unknown_data_models(registry_path, max_fixes=10)
