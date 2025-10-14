#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ архитектуры ALADDIN_NEW - проверка размещения функций
"""

import os
import sys
from datetime import datetime

def analyze_architecture():
    """Анализ архитектуры системы"""
    print("🏗️ АНАЛИЗ АРХИТЕКТУРЫ ALADDIN_NEW")
    print("=" * 80)
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Определяем ожидаемое размещение функций по архитектуре
    expected_placement = {
        # Core функции (должны быть в core/)
        "core_base": "core/base.py",
        "service_base": "core/service_base.py", 
        "database": "core/database.py",
        "configuration": "core/configuration.py",
        "logging_module": "core/logging_module.py",
        
        # Security базовые (должны быть в security/)
        "security_base": "security/security_core.py",
        "authentication": "security/authentication.py",
        
        # Family функции (должны быть в security/family/)
        "family_profile_manager": "security/family/family_profile_manager.py",
        "child_protection": "security/family/child_protection.py",
        "elderly_protection": "security/family/elderly_protection.py",
        
        # Preliminary функции (должны быть в security/preliminary/)
        "function_22": "security/preliminary/policy_engine.py",
        "function_23": "security/preliminary/risk_assessment.py",
        "function_24": "security/preliminary/behavioral_analysis.py",
        "function_25": "security/preliminary/mfa_service.py",
        "function_26": "security/preliminary/zero_trust_service.py",
        "function_27": "security/preliminary/trust_scoring.py",
        "function_28": "security/preliminary/context_aware_access.py",
        
        # Reactive функции (должны быть в security/reactive/)
        "function_34": "security/reactive/recovery_service.py",
        "function_36": "security/reactive/threat_intelligence.py",
        "function_37": "security/reactive/forensics_service.py",
        
        # Microservices функции (должны быть в security/microservices/)
        "function_38": "security/microservices/redis_cache_manager.py",
        "function_41": "security/microservices/service_mesh_manager.py",
        "function_42": "security/scaling/auto_scaling_engine.py",
        "function_81": "security/microservices/api_gateway.py",
        "function_82": "security/microservices/load_balancer.py",
        "function_83": "security/microservices/rate_limiter.py",
        "function_84": "security/microservices/circuit_breaker.py",
        "function_85": "security/microservices/user_interface_manager.py",
        
        # Privacy функции (должны быть в security/privacy/)
        "function_45": "security/ai_agents/data_protection_agent.py",
        "function_47": "security/privacy/universal_privacy_manager.py",
        
        # Family compliance (должны быть в security/compliance/)
        "function_46": "security/compliance/russian_child_protection_manager.py",
        "function_152_fz_compliance": "security/compliance/russian_data_protection_manager.py",
        
        # AI функции (должны быть в security/ai_agents/)
        "function_48": "security/ai_agents/anti_fraud_master_ai.py",
        "function_76": "security/managers/monitor_manager.py",
        "function_77": "security/managers/alert_manager.py",
        "function_78": "security/ai_agents/report_manager.py",
        "function_79": "security/managers/analytics_manager.py",
        "function_80": "security/managers/dashboard_manager.py",
        
        # CI/CD функции (должны быть в security/ci_cd/)
        "function_49": "security/ci_cd/ci_pipeline_manager.py",
        
        # Mobile функции (должны быть в security/mobile/)
        "function_56": "security/ai_agents/mobile_security_agent.py",
        
        # Bot функции (должны быть в security/bots/)
        "function_86": "security/bots/mobile_navigation_bot.py",
        "function_87": "security/bots/gaming_security_bot.py",
        "function_88": "security/bots/emergency_response_bot.py",
        "function_89": "security/bots/parental_control_bot.py",
        "function_90": "security/bots/notification_bot.py",
        "function_91": "security/bots/whatsapp_security_bot.py",
        "function_92": "security/bots/telegram_security_bot.py",
        "function_93": "security/bots/instagram_security_bot.py",
        "function_94": "security/bots/max_messenger_security_bot.py",
        "function_95": "security/bots/analytics_bot.py",
        "function_96": "security/bots/website_navigation_bot.py",
        "function_97": "security/bots/browser_security_bot.py",
        "function_98": "security/bots/cloud_storage_security_bot.py",
        "function_99": "security/bots/network_security_bot.py",
        "function_100": "security/bots/device_security_bot.py",
        
        # API функции (должны быть в security/)
        "russian_yandex_maps": "security/russian_api_manager.py",
        "russian_glonass": "security/russian_api_manager.py",
        "russian_free_glonass": "security/russian_api_manager.py",
        "russian_altox_server": "security/russian_api_manager.py",
        "russian_api_manager": "security/russian_api_manager.py",
        "external_api_manager": "security/external_api_manager.py",
        "advanced_alerting_system": "security/advanced_alerting_system.py",
        "trust_scoring": "security/preliminary/trust_scoring.py",
        "context_aware_access": "security/preliminary/context_aware_access.py"
    }
    
    # Проверяем размещение функций
    base_path = "/Users/sergejhlystov/ALADDIN_NEW"
    correct_placement = 0
    incorrect_placement = 0
    missing_files = 0
    
    print("🔍 ПРОВЕРКА РАЗМЕЩЕНИЯ ФУНКЦИЙ:")
    print("-" * 80)
    
    for function_id, expected_path in expected_placement.items():
        full_path = os.path.join(base_path, expected_path)
        if os.path.exists(full_path):
            print(f"✅ {function_id:25} | {expected_path}")
            correct_placement += 1
        else:
            print(f"❌ {function_id:25} | {expected_path} - ФАЙЛ НЕ НАЙДЕН")
            missing_files += 1
    
    print()
    print("📊 СТАТИСТИКА РАЗМЕЩЕНИЯ:")
    print(f"   ✅ Правильно размещены: {correct_placement}")
    print(f"   ❌ Неправильно размещены: {incorrect_placement}")
    print(f"   🔍 Файлы не найдены: {missing_files}")
    print(f"   📈 Процент правильности: {(correct_placement/(correct_placement+missing_files)*100):.1f}%")
    
    print()
    print("🏗️ АРХИТЕКТУРНАЯ СТРУКТУРА:")
    print("-" * 80)
    
    # Анализируем структуру каталогов
    directories = {
        "core/": "Базовые компоненты системы",
        "security/": "Основная система безопасности",
        "security/family/": "Семейная безопасность",
        "security/preliminary/": "Предварительные функции безопасности",
        "security/reactive/": "Реактивные функции безопасности",
        "security/microservices/": "Микросервисы",
        "security/scaling/": "Масштабирование",
        "security/ai_agents/": "AI агенты",
        "security/bots/": "Боты безопасности",
        "security/privacy/": "Приватность и защита данных",
        "security/compliance/": "Соответствие требованиям",
        "security/ci_cd/": "CI/CD пайплайны",
        "security/orchestration/": "Оркестрация",
        "security/mobile/": "Мобильная безопасность"
    }
    
    for dir_path, description in directories.items():
        full_dir_path = os.path.join(base_path, dir_path)
        if os.path.exists(full_dir_path):
            file_count = len([f for f in os.listdir(full_dir_path) if f.endswith('.py')])
            print(f"✅ {dir_path:25} | {description:40} | Файлов: {file_count:2d}")
        else:
            print(f"❌ {dir_path:25} | {description:40} | КАТАЛОГ НЕ НАЙДЕН")
    
    print()
    print("🎯 РЕКОМЕНДАЦИИ ПО АРХИТЕКТУРЕ:")
    print("-" * 80)
    
    if missing_files > 0:
        print("⚠️  Обнаружены проблемы с размещением функций:")
        print("   1. Некоторые файлы не найдены в ожидаемых местах")
        print("   2. Возможно, функции перемещены или переименованы")
        print("   3. Рекомендуется проверить актуальные пути к файлам")
    else:
        print("✅ Все функции размещены правильно согласно архитектуре!")
    
    print()
    print("📋 ПРИНЦИПЫ АРХИТЕКТУРЫ ALADDIN_NEW:")
    print("   1. Модульность - каждый компонент в своем каталоге")
    print("   2. Разделение ответственности - четкое разделение функций")
    print("   3. Масштабируемость - поддержка горизонтального масштабирования")
    print("   4. Безопасность - многоуровневая защита")
    print("   5. Семейная ориентация - специальные функции для семей")
    print("   6. Российская специфика - соответствие 152-ФЗ и ГЛОНАСС")
    
    print()
    print("=" * 80)
    print("✅ АНАЛИЗ АРХИТЕКТУРЫ ЗАВЕРШЕН!")
    print("=" * 80)

if __name__ == "__main__":
    analyze_architecture()