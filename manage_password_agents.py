#!/usr/bin/env python3
"""
Скрипт для управления версиями агентов безопасности паролей в SFM.

Позволяет:
- Просматривать все версии агентов
- Переключаться между версиями
- Удалять старые версии (с подтверждением)
- Сравнивать функциональность
"""

import json
import os
from datetime import datetime

def load_registry():
    """Загружает реестр SFM."""
    with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_registry(registry):
    """Сохраняет реестр SFM."""
    with open('data/sfm/function_registry.json', 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

def show_password_agents():
    """Показывает все агенты безопасности паролей."""
    registry = load_registry()
    
    print("🔐 АГЕНТЫ БЕЗОПАСНОСТИ ПАРОЛЕЙ В SFM")
    print("=" * 60)
    
    password_agents = {}
    for func_id, func_data in registry['functions'].items():
        if 'password' in func_id.lower() and 'security' in func_id.lower():
            password_agents[func_id] = func_data
    
    if not password_agents:
        print("❌ Агенты безопасности паролей не найдены в SFM")
        return
    
    for func_id, data in password_agents.items():
        status_emoji = "🟢" if data['status'] == 'active' else "🟡" if data['status'] == 'running' else "🔴"
        critical_emoji = "⚠️" if data.get('is_critical', False) else "✅"
        
        print(f"\n{status_emoji} {data['name']} ({func_id})")
        print(f"   📝 Описание: {data['description']}")
        print(f"   📊 Статус: {data['status']}")
        print(f"   🔢 Версия: {data.get('version', 'N/A')}")
        print(f"   ⭐ Качество: {data.get('quality_score', 'N/A')}")
        print(f"   🛡️ Критичность: {critical_emoji}")
        print(f"   📁 Файл: {data.get('file_path', 'N/A')}")
        print(f"   📏 Строк кода: {data.get('lines_of_code', 'N/A')}")
        
        if 'deprecation_note' in data:
            print(f"   ⚠️ Устарело: {data['deprecation_note']}")
        if 'replacement' in data:
            print(f"   🔄 Заменен на: {data['replacement']}")

def compare_agents():
    """Сравнивает функциональность агентов."""
    registry = load_registry()
    
    old_agent = registry['functions'].get('password_security_agent', {})
    new_agent = registry['functions'].get('password_security_agent_enhanced_v2', {})
    
    if not old_agent or not new_agent:
        print("❌ Не удалось найти агенты для сравнения")
        return
    
    print("\n🔄 СРАВНЕНИЕ АГЕНТОВ")
    print("=" * 60)
    
    print(f"\n📊 СТАРЫЙ АГЕНТ ({old_agent['name']}):")
    print(f"   🔢 Версия: {old_agent.get('version', 'N/A')}")
    print(f"   ⭐ Качество: {old_agent.get('quality_score', 'N/A')}")
    print(f"   📏 Строк кода: {old_agent.get('lines_of_code', 'N/A')}")
    print(f"   🛡️ Уровень безопасности: {old_agent.get('security_level', 'N/A')}")
    print(f"   📋 Функции: {len(old_agent.get('features', []))}")
    
    print(f"\n🚀 НОВЫЙ АГЕНТ ({new_agent['name']}):")
    print(f"   🔢 Версия: {new_agent.get('version', 'N/A')}")
    print(f"   ⭐ Качество: {new_agent.get('quality_score', 'N/A')}")
    print(f"   📏 Строк кода: {new_agent.get('lines_of_code', 'N/A')}")
    print(f"   🛡️ Уровень безопасности: {new_agent.get('security_level', 'N/A')}")
    print(f"   📋 Функции: {len(new_agent.get('features', []))}")
    
    print(f"\n📈 УЛУЧШЕНИЯ:")
    old_features = set(old_agent.get('features', []))
    new_features = set(new_agent.get('features', []))
    new_only = new_features - old_features
    
    if new_only:
        print("   ✨ Новые функции:")
        for feature in sorted(new_only):
            print(f"      • {feature}")
    else:
        print("   ℹ️ Новых функций не добавлено")

def remove_old_agent():
    """Удаляет старый агент из SFM (с подтверждением)."""
    registry = load_registry()
    
    if 'password_security_agent' not in registry['functions']:
        print("❌ Старый агент не найден в SFM")
        return
    
    old_agent = registry['functions']['password_security_agent']
    
    print(f"\n⚠️ ВНИМАНИЕ! Вы собираетесь удалить агент:")
    print(f"   📝 {old_agent['name']} ({old_agent['function_id']})")
    print(f"   🔢 Версия: {old_agent.get('version', 'N/A')}")
    print(f"   📊 Статус: {old_agent['status']}")
    
    print(f"\n🔄 Замена: {old_agent.get('replacement', 'Нет')}")
    
    confirm = input("\n❓ Вы уверены? Введите 'YES' для подтверждения: ")
    
    if confirm == 'YES':
        del registry['functions']['password_security_agent']
        save_registry(registry)
        print("✅ Старый агент удален из SFM")
        print("✅ Теперь в SFM только улучшенная версия")
    else:
        print("❌ Удаление отменено")

def show_sfm_stats():
    """Показывает общую статистику SFM."""
    registry = load_registry()
    
    total_functions = len(registry['functions'])
    active_functions = sum(1 for f in registry['functions'].values() if f['status'] == 'active')
    critical_functions = sum(1 for f in registry['functions'].values() if f.get('is_critical', False))
    
    print(f"\n📊 ОБЩАЯ СТАТИСТИКА SFM")
    print("=" * 40)
    print(f"🔢 Всего функций: {total_functions}")
    print(f"🟢 Активных: {active_functions}")
    print(f"⚠️ Критичных: {critical_functions}")
    print(f"📈 Процент активных: {(active_functions/total_functions)*100:.1f}%")

def main():
    """Главное меню."""
    while True:
        print(f"\n🔐 УПРАВЛЕНИЕ АГЕНТАМИ БЕЗОПАСНОСТИ ПАРОЛЕЙ")
        print("=" * 50)
        print("1. Показать все агенты паролей")
        print("2. Сравнить агенты")
        print("3. Удалить старый агент")
        print("4. Показать статистику SFM")
        print("5. Выход")
        
        choice = input("\n❓ Выберите действие (1-5): ")
        
        if choice == '1':
            show_password_agents()
        elif choice == '2':
            compare_agents()
        elif choice == '3':
            remove_old_agent()
        elif choice == '4':
            show_sfm_stats()
        elif choice == '5':
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор, попробуйте снова")

if __name__ == "__main__":
    main()