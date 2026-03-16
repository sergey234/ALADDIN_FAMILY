#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Проверка регистрации всех 42 компонентов в function_registry.json
"""

import json
import sys
from pathlib import Path

# Список всех 42 компонентов
ALL_42_COMPONENTS = [
    # NetworkProtectionScreen (10)
    "crash_detection_agent",
    "roadside_assistance_agent",
    "emergency_response_bot",
    "emergency_event_manager",
    "phishing_protection_agent",
    "malware_detection_agent",
    "mobile_security_agent",
    "network_security_agent",
    "incident_response_agent",
    "password_security_agent",
    
    # ParentalControlScreen (5)
    "self_harm_detection_agent",
    "grooming_detection_agent",
    "online_predators_agent",
    "psychological_support_agent",
    "parental_control_bot",
    
    # AdvancedProtectionSettingsScreen (13)
    "telegram_security_bot",
    "whatsapp_security_bot",
    "instagram_security_bot",
    "max_messenger_security_bot",
    "gaming_security_bot",
    "browser_security_bot",
    "location_bubble_agent",
    "personal_data_cleanup_agent",
    "anti_tracker_agent",
    "dark_web_monitoring_agent",
    "russian_identity_theft_protection_agent",
    "ai_categories_agent",
    "driving_reports_agent",
    
    # SettingsScreen (5)
    "emergency_contacts_manager",
    "emergency_notifications_manager",
    "voice_control_manager",
    "russian_child_protection_compliance_manager",
    "russian_data_protection_compliance_manager",
    
    # Улучшение существующих (9)
    "family_notification_manager",
    "smart_notification_manager",
    "child_interface_manager",
    "elderly_interface_manager",
    "subscription_manager",
    "referral_manager",
    "qr_payment_manager",
    "analytics_manager",
    "report_manager",
]


def check_component_registry(registry_path: str):
    """
    Проверить регистрацию всех 42 компонентов в function_registry.json
    """
    print("=" * 80)
    print("ПРОВЕРКА РЕГИСТРАЦИИ 42 КОМПОНЕНТОВ В SFM REGISTRY")
    print("=" * 80)
    print()
    
    # Загрузить registry
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    except FileNotFoundError:
        print(f"❌ ОШИБКА: Файл не найден: {registry_path}")
        print("   Убедитесь, что файл существует на сервере.")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ ОШИБКА: Не удалось распарсить JSON: {e}")
        return False
    
    # Получить словарь функций
    functions = registry.get('functions', {})
    if not functions:
        print("❌ ОШИБКА: В registry нет ключа 'functions'")
        return False
    
    print(f"📊 Всего функций в registry: {len(functions)}")
    print()
    
    # Проверить каждый компонент
    registered = []
    missing = []
    partial_matches = []
    
    for component_id in ALL_42_COMPONENTS:
        # Прямое совпадение
        if component_id in functions:
            func_data = functions[component_id]
            status = func_data.get('status', 'unknown')
            func_type = func_data.get('function_type', 'unknown')
            registered.append({
                'id': component_id,
                'status': status,
                'type': func_type,
                'name': func_data.get('name', 'N/A')
            })
        else:
            # Поиск частичных совпадений (например, "CrashDetectionAgent" вместо "crash_detection_agent")
            found = False
            component_words = component_id.lower().replace('_', ' ').split()
            
            for func_id, func_data in functions.items():
                # Проверка различных вариантов имен
                name = func_data.get('name', '').lower()
                func_id_lower = func_id.lower()
                component_lower = component_id.lower()
                
                # Расширенные варианты совпадений
                matches = False
                
                # 1. Точное совпадение (без учета регистра)
                if component_lower == func_id_lower or component_lower == name:
                    matches = True
                
                # 2. Частичное совпадение ID
                elif (component_lower in func_id_lower or 
                      func_id_lower in component_lower):
                    matches = True
                
                # 3. Совпадение без подчеркиваний
                elif (component_lower.replace('_', '') in func_id_lower.replace('_', '') or
                      func_id_lower.replace('_', '') in component_lower.replace('_', '')):
                    matches = True
                
                # 4. Совпадение ключевых слов (для многословных названий)
                elif len(component_words) > 1:
                    # Проверяем, что хотя бы 2 ключевых слова совпадают
                    matching_words = sum(1 for word in component_words 
                                       if len(word) > 3 and (word in func_id_lower or word in name))
                    if matching_words >= 2:
                        matches = True
                
                # 5. Совпадение по отдельным словам (для длинных названий)
                elif any(len(word) > 4 and (word in func_id_lower or word in name) 
                        for word in component_words):
                    matches = True
                
                if matches:
                    partial_matches.append({
                        'component_id': component_id,
                        'found_as': func_id,
                        'name': func_data.get('name', 'N/A'),
                        'status': func_data.get('status', 'unknown'),
                        'type': func_data.get('function_type', 'unknown')
                    })
                    found = True
                    # Не break - собираем все совпадения для анализа
            
            if not found:
                missing.append(component_id)
    
    # Вывести результаты
    print("=" * 80)
    print("РЕЗУЛЬТАТЫ ПРОВЕРКИ")
    print("=" * 80)
    print()
    
    print(f"✅ ЗАРЕГИСТРИРОВАНО (прямое совпадение): {len(registered)}/{len(ALL_42_COMPONENTS)}")
    print(f"⚠️  ЧАСТИЧНЫЕ СОВПАДЕНИЯ: {len(partial_matches)}")
    print(f"❌ НЕ НАЙДЕНО: {len(missing)}/{len(ALL_42_COMPONENTS)}")
    print()
    
    # Детальный список зарегистрированных
    if registered:
        print("=" * 80)
        print("✅ ЗАРЕГИСТРИРОВАННЫЕ КОМПОНЕНТЫ:")
        print("=" * 80)
        for i, comp in enumerate(registered, 1):
            print(f"{i:2d}. {comp['id']:50s} | Статус: {comp['status']:10s} | Тип: {comp['type']}")
        print()
    
    # Частичные совпадения
    if partial_matches:
        print("=" * 80)
        print("⚠️  ЧАСТИЧНЫЕ СОВПАДЕНИЯ (требуют проверки):")
        print("=" * 80)
        for i, match in enumerate(partial_matches, 1):
            print(f"{i:2d}. Искали: {match['component_id']:50s}")
            print(f"    Найдено: {match['found_as']:50s} | {match['name']}")
            print(f"    Статус: {match['status']:10s} | Тип: {match['type']}")
            print()
    
    # Не найденные компоненты
    if missing:
        print("=" * 80)
        print("❌ НЕ НАЙДЕННЫЕ КОМПОНЕНТЫ:")
        print("=" * 80)
        for i, comp_id in enumerate(missing, 1):
            print(f"{i:2d}. {comp_id}")
        print()
    
    # Статистика по статусам
    if registered:
        status_counts = {}
        type_counts = {}
        for comp in registered:
            status = comp['status']
            func_type = comp['type']
            status_counts[status] = status_counts.get(status, 0) + 1
            type_counts[func_type] = type_counts.get(func_type, 0) + 1
        
        print("=" * 80)
        print("СТАТИСТИКА ПО СТАТУСАМ:")
        print("=" * 80)
        for status, count in sorted(status_counts.items()):
            print(f"  {status:20s}: {count}")
        print()
        
        print("=" * 80)
        print("СТАТИСТИКА ПО ТИПАМ:")
        print("=" * 80)
        for func_type, count in sorted(type_counts.items()):
            print(f"  {func_type:20s}: {count}")
        print()
    
    # Итоговый результат
    print("=" * 80)
    if len(registered) == len(ALL_42_COMPONENTS):
        print("✅ ВСЕ 42 КОМПОНЕНТА ЗАРЕГИСТРИРОВАНЫ!")
        return True
    elif len(registered) + len(partial_matches) == len(ALL_42_COMPONENTS):
        print("⚠️  ВСЕ КОМПОНЕНТЫ НАЙДЕНЫ (часть через частичные совпадения)")
        print("   Рекомендуется проверить частичные совпадения вручную")
        return True
    else:
        print(f"❌ НЕ ВСЕ КОМПОНЕНТЫ ЗАРЕГИСТРИРОВАНЫ")
        print(f"   Зарегистрировано: {len(registered)}/{len(ALL_42_COMPONENTS)}")
        print(f"   Частичные совпадения: {len(partial_matches)}")
        print(f"   Не найдено: {len(missing)}")
        return False
    print("=" * 80)


def main():
    # Путь к registry на сервере
    registry_path = '/opt/aladdin-backend/data/sfm/function_registry.json'
    
    # Если файл не найден, попробовать локальный путь (для тестирования)
    if not Path(registry_path).exists():
        print(f"⚠️  Файл не найден по пути: {registry_path}")
        print("   Это нормально, если скрипт запускается локально.")
        print("   Скрипт должен быть выполнен на сервере.")
        print()
        print("   Для выполнения на сервере:")
        print(f"   ssh root@149.154.65.180")
        print(f"   cd /opt/aladdin-backend")
        print(f"   python3 docs/server/check_42_components_registry.py")
        return
    
    success = check_component_registry(registry_path)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
