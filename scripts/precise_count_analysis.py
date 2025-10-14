#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Точный подсчет всех функций и классов для интеграции в SFM

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-11
"""

import os
import ast
import sys
from pathlib import Path

def count_classes_and_functions_in_file(file_path):
    """Подсчет классов и функций в одном файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        classes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        
        return classes, functions
    except Exception as e:
        print(f"❌ Ошибка при анализе {file_path}: {e}")
        return [], []

def analyze_all_components():
    """Анализ всех компонентов системы"""
    
    # Уже интегрированные в SFM
    already_integrated = {
        'core_base': 'CoreBase',
        'service_base': 'ServiceBase', 
        'security_base': 'SecurityBase',
        'database': 'Database',
        'configuration': 'Configuration',
        'logging_module': 'LoggingModule',
        'authentication': 'Authentication',
        'mobile_security_agent': 'Mobile Security Agent',
        'test_function': 'Test Function',
        'test_auto_save': 'Test Auto Save'
    }
    
    print("🔍 ТОЧНЫЙ ПОДСЧЕТ ВСЕХ КОМПОНЕНТОВ ДЛЯ ИНТЕГРАЦИИ В SFM")
    print("="*80)
    
    # Директории для анализа
    directories = {
        'CORE': '/Users/sergejhlystov/ALADDIN_NEW/core',
        'SECURITY': '/Users/sergejhlystov/ALADDIN_NEW/security',
        'AI_AGENTS': '/Users/sergejhlystov/ALADDIN_NEW/ai_agents',
        'BOTS': '/Users/sergejhlystov/ALADDIN_NEW/bots',
        'MICROSERVICES': '/Users/sergejhlystov/ALADDIN_NEW/microservices',
        'FAMILY': '/Users/sergejhlystov/ALADDIN_NEW/family',
        'COMPLIANCE': '/Users/sergejhlystov/ALADDIN_NEW/compliance',
        'PRIVACY': '/Users/sergejhlystov/ALADDIN_NEW/privacy',
        'REACTIVE': '/Users/sergejhlystov/ALADDIN_NEW/reactive',
        'ACTIVE': '/Users/sergejhlystov/ALADDIN_NEW/active',
        'PRELIMINARY': '/Users/sergejhlystov/ALADDIN_NEW/preliminary',
        'ORCHESTRATION': '/Users/sergejhlystov/ALADDIN_NEW/orchestration',
        'SCALING': '/Users/sergejhlystov/ALADDIN_NEW/scaling'
    }
    
    total_classes = 0
    total_functions = 0
    total_files = 0
    all_components = {}
    
    for dir_name, dir_path in directories.items():
        if not os.path.exists(dir_path):
            print(f"⚠️ Директория {dir_name} не найдена: {dir_path}")
            continue
            
        print(f"\n📁 АНАЛИЗ ДИРЕКТОРИИ: {dir_name}")
        print("-" * 50)
        
        dir_classes = 0
        dir_functions = 0
        dir_files = 0
        components = {}
        
        for file_path in Path(dir_path).rglob('*.py'):
            if file_path.name.startswith('__'):
                continue
                
            classes, functions = count_classes_and_functions_in_file(file_path)
            
            if classes or functions:
                relative_path = str(file_path.relative_to(Path(dir_path)))
                components[relative_path] = {
                    'classes': len(classes),
                    'functions': len(functions),
                    'class_names': classes,
                    'function_names': functions
                }
                
                dir_classes += len(classes)
                dir_functions += len(functions)
                dir_files += 1
                
                print(f"  📄 {relative_path}: {len(classes)} классов, {len(functions)} функций")
        
        all_components[dir_name] = {
            'classes': dir_classes,
            'functions': dir_functions,
            'files': dir_files,
            'components': components
        }
        
        total_classes += dir_classes
        total_functions += dir_functions
        total_files += dir_files
        
        print(f"  📊 ИТОГО {dir_name}: {dir_classes} классов, {dir_functions} функций, {dir_files} файлов")
    
    # Подсчет функций (не классов!) для интеграции
    print(f"\n🎯 АНАЛИЗ ФУНКЦИЙ ДЛЯ ИНТЕГРАЦИИ:")
    print("="*80)
    
    # Функции из вашего списка
    security_functions = [
        'register_function', 'enable_function', 'disable_function', 'get_function_status', 'execute_function',
        '_save_functions', '_load_saved_functions', 'authenticate_user', 'verify_credentials', 'generate_token',
        'validate_token', 'logout_user', 'initialize_security', 'check_permissions', 'validate_access',
        'log_security_event', 'analyze_threats', 'update_threat_database', 'get_threat_level', 'classify_threat',
        'handle_incident', 'escalate_incident', 'resolve_incident', 'generate_incident_report', 'start_monitoring',
        'stop_monitoring', 'get_security_metrics', 'alert_on_threat', 'grant_access', 'revoke_access',
        'check_access_level', 'update_permissions', 'create_policy', 'update_policy', 'enforce_policy',
        'validate_policy', 'analyze_security_data', 'generate_security_report', 'identify_patterns',
        'predict_threats', 'perform_audit', 'generate_audit_report', 'check_compliance', 'recommend_improvements'
    ]
    
    ai_agent_functions = [
        'perform_full_scan', 'analyze_app_permissions', 'check_device_security', 'detect_malicious_apps',
        'generate_security_report', 'scan_for_threats', 'analyze_network_traffic', 'detect_anomalies',
        'classify_threats', 'analyze_user_behavior', 'detect_suspicious_activity', 'create_behavior_profile',
        'update_behavior_model', 'validate_password_strength', 'detect_weak_passwords', 'suggest_password_improvements',
        'check_password_reuse', 'detect_fraud_patterns', 'analyze_transaction_risk', 'block_suspicious_activity',
        'generate_fraud_report', 'analyze_voice_patterns', 'detect_voice_spoofing', 'verify_speaker_identity',
        'extract_voice_features', 'detect_deepfake_content', 'analyze_media_authenticity', 'verify_content_integrity',
        'block_fake_content'
    ]
    
    bot_functions = [
        'handle_emergency', 'send_emergency_alert', 'coordinate_response', 'update_emergency_status',
        'monitor_child_activity', 'block_inappropriate_content', 'set_time_limits', 'generate_activity_report',
        'send_notification', 'schedule_notification', 'manage_notification_preferences', 'track_notification_delivery'
    ]
    
    microservice_functions = [
        'route_request', 'authenticate_request', 'rate_limit_request', 'log_request', 'distribute_load',
        'health_check', 'failover_service', 'monitor_performance'
    ]
    
    all_functions = security_functions + ai_agent_functions + bot_functions + microservice_functions
    
    print(f"📊 ФУНКЦИИ ДЛЯ ИНТЕГРАЦИИ ПО КАТЕГОРИЯМ:")
    print(f"  🔐 Security функции: {len(security_functions)}")
    print(f"  🤖 AI Agent функции: {len(ai_agent_functions)}")
    print(f"  🤖 Bot функции: {len(bot_functions)}")
    print(f"  ⚙️ Microservice функции: {len(microservice_functions)}")
    print(f"  📊 ВСЕГО ФУНКЦИЙ: {len(all_functions)}")
    
    # Итоговая статистика
    print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print("="*80)
    print(f"✅ УЖЕ ИНТЕГРИРОВАНО В SFM:")
    print(f"  🏗️ Классов: {len(already_integrated)}")
    print(f"  ⚙️ Функций: 0 (только классы)")
    
    print(f"\n📋 ДЛЯ ИНТЕГРАЦИИ В SFM:")
    print(f"  🏗️ Всего классов: {total_classes}")
    print(f"  ⚙️ Всего функций: {len(all_functions)}")
    print(f"  📁 Всего файлов: {total_files}")
    
    print(f"\n🎯 ПРИОРИТЕТЫ ИНТЕГРАЦИИ:")
    print("-" * 50)
    
    # Первый приоритет - критические
    critical_classes = 0
    critical_functions = len(security_functions) + len(ai_agent_functions[:10])  # Топ-10 AI функций
    
    for dir_name in ['CORE', 'SECURITY']:
        if dir_name in all_components:
            critical_classes += all_components[dir_name]['classes']
    
    print(f"🔴 ПЕРВЫЙ ПРИОРИТЕТ (критические):")
    print(f"  🏗️ Классов: {critical_classes}")
    print(f"  ⚙️ Функций: {critical_functions}")
    
    # Второй приоритет - высокие
    high_classes = 0
    high_functions = len(ai_agent_functions[10:]) + len(bot_functions) + len(microservice_functions)
    
    for dir_name in ['AI_AGENTS', 'BOTS', 'MICROSERVICES']:
        if dir_name in all_components:
            high_classes += all_components[dir_name]['classes']
    
    print(f"🟡 ВТОРОЙ ПРИОРИТЕТ (высокие):")
    print(f"  🏗️ Классов: {high_classes}")
    print(f"  ⚙️ Функций: {high_functions}")
    
    # Третий приоритет - средние
    medium_classes = 0
    medium_functions = 0
    
    for dir_name in ['FAMILY', 'COMPLIANCE', 'PRIVACY']:
        if dir_name in all_components:
            medium_classes += all_components[dir_name]['classes']
    
    print(f"🟠 ТРЕТИЙ ПРИОРИТЕТ (средние):")
    print(f"  🏗️ Классов: {medium_classes}")
    print(f"  ⚙️ Функций: {medium_functions}")
    
    # Четвертый приоритет - дополнительные
    additional_classes = 0
    additional_functions = 0
    
    for dir_name in ['REACTIVE', 'ACTIVE', 'PRELIMINARY', 'ORCHESTRATION', 'SCALING']:
        if dir_name in all_components:
            additional_classes += all_components[dir_name]['classes']
    
    print(f"🔵 ЧЕТВЕРТЫЙ ПРИОРИТЕТ (дополнительные):")
    print(f"  🏗️ Классов: {additional_classes}")
    print(f"  ⚙️ Функций: {additional_functions}")
    
    print(f"\n✅ ФИНАЛЬНЫЙ ИТОГ:")
    print("="*80)
    print(f"🏗️ ВСЕГО КЛАССОВ ДЛЯ ИНТЕГРАЦИИ: {total_classes}")
    print(f"⚙️ ВСЕГО ФУНКЦИЙ ДЛЯ ИНТЕГРАЦИИ: {len(all_functions)}")
    print(f"📁 ВСЕГО ФАЙЛОВ ДЛЯ ИНТЕГРАЦИИ: {total_files}")
    print(f"✅ УЖЕ ИНТЕГРИРОВАНО: {len(already_integrated)} классов")
    print(f"📊 ПРОЦЕНТ ГОТОВНОСТИ: {len(already_integrated)/(len(already_integrated)+total_classes)*100:.1f}%")
    
    return {
        'total_classes': total_classes,
        'total_functions': len(all_functions),
        'total_files': total_files,
        'already_integrated': len(already_integrated),
        'components': all_components
    }

def main():
    """Главная функция"""
    analyze_all_components()

if __name__ == "__main__":
    main()