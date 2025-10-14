#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой скрипт для отображения всех функций в SafeFunctionManager
Без сложной инициализации
"""

import sys
import os
from datetime import datetime

# Добавляем путь к модулям
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

def show_functions_from_code():
    """Показать функции, найденные в коде"""
    print("🔍 ФУНКЦИИ В SAFEFUNCTIONMANAGER (из анализа кода)")
    print("=" * 60)
    
    # Базовые функции из SafeFunctionManager
    basic_functions = [
        {
            "function_id": "core_base",
            "name": "CoreBase", 
            "description": "Базовая архитектура системы",
            "function_type": "core",
            "security_level": "high",
            "is_critical": True,
            "status": "enabled"
        },
        {
            "function_id": "service_base",
            "name": "ServiceBase",
            "description": "Базовый сервис", 
            "function_type": "core",
            "security_level": "high",
            "is_critical": True,
            "status": "enabled"
        },
        {
            "function_id": "security_base",
            "name": "SecurityBase",
            "description": "Базовая безопасность",
            "function_type": "security", 
            "security_level": "high",
            "is_critical": True,
            "status": "enabled"
        },
        {
            "function_id": "database",
            "name": "Database",
            "description": "Модуль базы данных",
            "function_type": "core",
            "security_level": "high", 
            "is_critical": True,
            "status": "enabled"
        },
        {
            "function_id": "configuration",
            "name": "Configuration",
            "description": "Управление конфигурацией",
            "function_type": "core",
            "security_level": "medium",
            "is_critical": False,
            "status": "enabled"
        },
        {
            "function_id": "logging_module",
            "name": "LoggingModule", 
            "description": "Система логирования",
            "function_type": "core",
            "security_level": "medium",
            "is_critical": False,
            "status": "enabled"
        },
        {
            "function_id": "authentication",
            "name": "Authentication",
            "description": "Аутентификация",
            "function_type": "security",
            "security_level": "high",
            "is_critical": True,
            "status": "enabled"
        }
    ]
    
    # Функции из скриптов интеграции
    integrated_functions = [
        {
            "function_id": "russian_yandex_maps",
            "name": "Russian Yandex Maps",
            "description": "Интеграция с Яндекс.Картами",
            "function_type": "api",
            "security_level": "medium",
            "is_critical": False,
            "status": "sleeping"
        },
        {
            "function_id": "russian_glonass", 
            "name": "Russian GLONASS",
            "description": "Интеграция с ГЛОНАСС",
            "function_type": "api",
            "security_level": "high",
            "is_critical": False,
            "status": "sleeping"
        },
        {
            "function_id": "russian_free_glonass",
            "name": "Russian Free GLONASS",
            "description": "Бесплатная интеграция с ГЛОНАСС",
            "function_type": "api", 
            "security_level": "medium",
            "is_critical": False,
            "status": "sleeping"
        },
        {
            "function_id": "russian_altox_server",
            "name": "Russian Altox Server",
            "description": "Сервер Altox для России",
            "function_type": "api",
            "security_level": "medium",
            "is_critical": False,
            "status": "sleeping"
        },
        {
            "function_id": "family_profile_manager",
            "name": "Family Profile Manager",
            "description": "Управление профилями семьи",
            "function_type": "family",
            "security_level": "high",
            "is_critical": True,
            "status": "enabled"
        },
        {
            "function_id": "child_protection",
            "name": "Child Protection",
            "description": "Защита детей",
            "function_type": "family",
            "security_level": "high",
            "is_critical": True,
            "status": "enabled"
        },
        {
            "function_id": "elderly_protection",
            "name": "Elderly Protection", 
            "description": "Защита пожилых",
            "function_type": "family",
            "security_level": "high",
            "is_critical": True,
            "status": "enabled"
        },
        {
            "function_id": "trust_scoring",
            "name": "Trust Scoring",
            "description": "Система оценки доверия",
            "function_type": "security",
            "security_level": "high",
            "is_critical": False,
            "status": "sleeping"
        },
        {
            "function_id": "context_aware_access",
            "name": "Context Aware Access",
            "description": "Контекстно-зависимый доступ",
            "function_type": "security",
            "security_level": "high",
            "is_critical": False,
            "status": "sleeping"
        },
        {
            "function_id": "advanced_alerting_system",
            "name": "Advanced Alerting System",
            "description": "Продвинутая система оповещений",
            "function_type": "monitoring",
            "security_level": "medium",
            "is_critical": False,
            "status": "sleeping"
        },
        {
            "function_id": "notification_bot",
            "name": "Notification Bot",
            "description": "Бот уведомлений",
            "function_type": "bot",
            "security_level": "medium",
            "is_critical": False,
            "status": "sleeping"
        },
        {
            "function_id": "emergency_response_interface",
            "name": "Emergency Response Interface",
            "description": "Интерфейс экстренного реагирования",
            "function_type": "emergency",
            "security_level": "high",
            "is_critical": True,
            "status": "sleeping"
        },
        {
            "function_id": "family_communication_hub",
            "name": "Family Communication Hub",
            "description": "Центр семейной коммуникации",
            "function_type": "family",
            "security_level": "medium",
            "is_critical": False,
            "status": "sleeping"
        },
        {
            "function_id": "russian_api_manager",
            "name": "Russian API Manager",
            "description": "Менеджер российских API",
            "function_type": "api",
            "security_level": "medium",
            "is_critical": False,
            "status": "sleeping"
        },
        {
            "function_id": "external_api_manager",
            "name": "External API Manager",
            "description": "Менеджер внешних API",
            "function_type": "api",
            "security_level": "medium",
            "is_critical": False,
            "status": "sleeping"
        }
    ]
    
    all_functions = basic_functions + integrated_functions
    
    # Группируем по статусу
    enabled_functions = [f for f in all_functions if f['status'] == 'enabled']
    sleeping_functions = [f for f in all_functions if f['status'] == 'sleeping']
    disabled_functions = [f for f in all_functions if f['status'] == 'disabled']
    
    # Общая статистика
    print(f"📊 ОБЩАЯ СТАТИСТИКА:")
    print(f"   Всего функций: {len(all_functions)}")
    print(f"   ✅ Активных: {len(enabled_functions)}")
    print(f"   😴 Спящих: {len(sleeping_functions)}")
    print(f"   ❌ Отключенных: {len(disabled_functions)}")
    print()
    
    # Активные функции
    print("✅ АКТИВНЫЕ ФУНКЦИИ:")
    print("-" * 40)
    for func in enabled_functions:
        critical = "🔴 КРИТИЧЕСКАЯ" if func.get('is_critical', False) else "🟢 Обычная"
        security_level = func.get('security_level', 'unknown')
        func_type = func.get('function_type', 'unknown')
        print(f"   • {func.get('name', 'Unknown')} ({func.get('function_id', 'unknown')})")
        print(f"     {critical} | Безопасность: {security_level} | Тип: {func_type}")
        print(f"     Описание: {func.get('description', 'Нет описания')}")
        print()
    
    # Спящие функции
    print("😴 СПЯЩИЕ ФУНКЦИИ:")
    print("-" * 40)
    for func in sleeping_functions:
        critical = "🔴 КРИТИЧЕСКАЯ" if func.get('is_critical', False) else "🟢 Обычная"
        security_level = func.get('security_level', 'unknown')
        func_type = func.get('function_type', 'unknown')
        print(f"   • {func.get('name', 'Unknown')} ({func.get('function_id', 'unknown')})")
        print(f"     {critical} | Безопасность: {security_level} | Тип: {func_type}")
        print(f"     Описание: {func.get('description', 'Нет описания')}")
        print()
    
    # Статистика по типам
    print("📈 СТАТИСТИКА ПО ТИПАМ ФУНКЦИЙ:")
    print("-" * 40)
    function_types = {}
    for func in all_functions:
        func_type = func.get('function_type', 'unknown')
        if func_type not in function_types:
            function_types[func_type] = {'total': 0, 'enabled': 0, 'sleeping': 0, 'disabled': 0}
        
        function_types[func_type]['total'] += 1
        status = func.get('status', 'unknown')
        if status in function_types[func_type]:
            function_types[func_type][status] += 1
    
    for func_type, stats in function_types.items():
        print(f"   📦 {func_type.upper()}:")
        print(f"      Всего: {stats['total']} | Активных: {stats['enabled']} | Спящих: {stats['sleeping']} | Отключенных: {stats['disabled']}")
        print()
    
    # Статистика по уровням безопасности
    print("🛡️  СТАТИСТИКА ПО УРОВНЯМ БЕЗОПАСНОСТИ:")
    print("-" * 40)
    security_levels = {}
    for func in all_functions:
        level = func.get('security_level', 'unknown')
        if level not in security_levels:
            security_levels[level] = {'total': 0, 'enabled': 0, 'sleeping': 0, 'disabled': 0}
        
        security_levels[level]['total'] += 1
        status = func.get('status', 'unknown')
        if status in security_levels[level]:
            security_levels[level][status] += 1
    
    for level, stats in security_levels.items():
        level_name = {
            'high': '🔴 ВЫСОКИЙ',
            'medium': '🟡 СРЕДНИЙ', 
            'low': '🟢 НИЗКИЙ'
        }.get(level, f'❓ {level.upper()}')
        
        print(f"   {level_name}:")
        print(f"      Всего: {stats['total']} | Активных: {stats['enabled']} | Спящих: {stats['sleeping']} | Отключенных: {stats['disabled']}")
        print()
    
    print("✅ Анализ завершен успешно!")

if __name__ == "__main__":
    show_functions_from_code()