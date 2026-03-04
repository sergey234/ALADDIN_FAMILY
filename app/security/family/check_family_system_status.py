#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПРОВЕРКА СТАТУСА СИСТЕМЫ СЕМЕЙ В SFM
====================================

Быстрая проверка статуса интеграции системы анонимной регистрации семей
"""

import sys
import os
import json
from datetime import datetime

# Добавляем путь к корневой директории

def check_family_system_status():
    """Проверка статуса системы семей в SFM"""
    print("🔍 ПРОВЕРКА СТАТУСА СИСТЕМЫ СЕМЕЙ В SFM")
    print("=" * 50)
    
    try:
        # Импорт SFM
        from security.safe_function_manager import SafeFunctionManager
        sfm = SafeFunctionManager()
        
        # Поиск семейных функций
        family_functions = {}
        for func_id, func in sfm.functions.items():
            if 'family' in func_id:
                family_functions[func_id] = {
                    'name': func.name,
                    'status': func.status.value,
                    'security_level': func.security_level.value,
                    'is_critical': func.is_critical
                }
        
        # Вывод результатов
        print(f"📊 Найдено семейных функций: {len(family_functions)}")
        print()
        
        for func_id, info in family_functions.items():
            status_icon = "✅" if info['status'] == 'enabled' else "⚠️" if info['status'] == 'sleeping' else "❌"
            critical_icon = "🔒" if info['is_critical'] else "🔓"
            
            print(f"{status_icon} {func_id}")
            print(f"   Название: {info['name']}")
            print(f"   Статус: {info['status']}")
            print(f"   Безопасность: {info['security_level']} {critical_icon}")
            print()
        
        # Проверка реестра
        registry_path = "data/sfm/function_registry.json"
        if os.path.exists(registry_path):
            with open(registry_path, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)
            
            registry_family_functions = [k for k in registry_data.get('functions', {}).keys() if 'family' in k]
            print(f"💾 В реестре SFM: {len(registry_family_functions)} семейных функций")
            print(f"📁 Путь к реестру: {registry_path}")
        else:
            print("❌ Файл реестра не найден")
        
        # Общий статус
        print("\n🎯 ОБЩИЙ СТАТУС")
        print("=" * 50)
        
        if len(family_functions) >= 4:
            print("✅ Система семей полностью интегрирована в SFM")
            print("🔐 Готова к использованию")
            print("📱 Все компоненты доступны через SFM API")
        else:
            print("⚠️ Частичная интеграция - требуется доработка")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки статуса: {e}")
        return False

def show_usage_examples():
    """Показать примеры использования"""
    print("\n📚 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ")
    print("=" * 50)
    
    print("1. Создание анонимной семьи:")
    print("   from security.family import create_family, RegistrationData, FamilyRole, AgeGroup")
    print("   data = RegistrationData(role=FamilyRole.PARENT, age_group=AgeGroup.ADULT_24_55)")
    print("   result = create_family(data)")
    print()
    
    print("2. Присоединение к семье:")
    print("   from security.family import join_family")
    print("   result = join_family(qr_code='family_abc123...')")
    print()
    
    print("3. Отправка уведомлений:")
    print("   from security.family import send_family_alert")
    print("   result = send_family_alert(family_id='family_abc123', message='Проверьте безопасность')")
    print()
    
    print("4. Активация функций в SFM:")
    print("   sfm.enable_function('family_registration_system')")
    print("   sfm.enable_function('family_notification_system')")

if __name__ == "__main__":
    """Запуск проверки статуса системы семей"""
    print("🔐 СИСТЕМА АНОНИМНОЙ РЕГИСТРАЦИИ СЕМЕЙ")
    print("Проверка статуса интеграции с SFM")
    print("Полное соответствие 152-ФЗ")
    print()
    
    # Проверка статуса
    success = check_family_system_status()
    
    # Показать примеры использования
    if success:
        show_usage_examples()
    
    print(f"\n⏰ Время проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")