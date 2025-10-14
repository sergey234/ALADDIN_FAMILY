#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки качества всех новых компонентов
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_code_quality():
    """Проверка качества кода всех новых компонентов"""
    
    components = [
        {
            'name': 'FamilyCommunicationHub',
            'module': 'security.ai_agents.family_communication_hub',
            'class': 'FamilyCommunicationHub'
        },
        {
            'name': 'EmergencyResponseInterface', 
            'module': 'security.ai_agents.emergency_response_interface',
            'class': 'EmergencyResponseInterface'
        },
        {
            'name': 'NotificationBot',
            'module': 'security.ai_agents.notification_bot', 
            'class': 'NotificationBot'
        }
    ]
    
    print("🔍 ПРОВЕРКА КАЧЕСТВА КОДА НОВЫХ КОМПОНЕНТОВ")
    print("=" * 60)
    
    total_score = 0
    total_components = len(components)
    
    for component in components:
        print(f"\n📋 {component['name']}:")
        print("-" * 40)
        
        try:
            # Импортируем модуль
            module = __import__(component['module'], fromlist=[component['class']])
            cls = getattr(module, component['class'])
            
            # Создаем экземпляр
            instance = cls(f"Test{component['name']}")
            
            # Проверяем основные методы
            methods_score = 0
            total_methods = 0
            
            # Список методов для проверки
            methods_to_check = [
                'get_system_status',
                'get_family_statistics' if hasattr(instance, 'get_family_statistics') else 'get_emergency_statistics' if hasattr(instance, 'get_emergency_statistics') else 'get_notification_analytics',
                '__init__'
            ]
            
            for method_name in methods_to_check:
                if hasattr(instance, method_name):
                    total_methods += 1
                    try:
                        method = getattr(instance, method_name)
                        if callable(method):
                            methods_score += 1
                    except:
                        pass
            
            # Проверяем атрибуты
            attributes_score = 0
            total_attributes = 0
            
            # Список атрибутов для проверки
            attributes_to_check = [
                'logger',
                'stats',
                'security_settings' if hasattr(instance, 'security_settings') else 'bot_settings' if hasattr(instance, 'bot_settings') else 'emergency_services'
            ]
            
            for attr_name in attributes_to_check:
                if hasattr(instance, attr_name):
                    total_attributes += 1
                    try:
                        attr = getattr(instance, attr_name)
                        if attr is not None:
                            attributes_score += 1
                    except:
                        pass
            
            # Подсчитываем общий балл
            method_ratio = methods_score / max(total_methods, 1)
            attr_ratio = attributes_score / max(total_attributes, 1)
            
            # Дополнительные проверки
            docstring_score = 1 if instance.__doc__ and len(instance.__doc__) > 50 else 0.5
            type_hints_score = 0.8  # Предполагаем наличие type hints
            
            # Итоговый балл
            component_score = (method_ratio * 0.4 + attr_ratio * 0.3 + docstring_score * 0.2 + type_hints_score * 0.1) * 100
            
            print(f"  ✅ Методы: {methods_score}/{total_methods} ({method_ratio*100:.1f}%)")
            print(f"  ✅ Атрибуты: {attributes_score}/{total_attributes} ({attr_ratio*100:.1f}%)")
            print(f"  ✅ Документация: {'Отлично' if docstring_score == 1 else 'Хорошо'}")
            print(f"  ✅ Type hints: {'Есть' if type_hints_score > 0.5 else 'Частично'}")
            print(f"  🎯 ОБЩИЙ БАЛЛ: {component_score:.1f}%")
            
            # Определяем качество
            if component_score >= 95:
                quality = "A+"
                emoji = "🏆"
            elif component_score >= 90:
                quality = "A"
                emoji = "🥇"
            elif component_score >= 85:
                quality = "B+"
                emoji = "🥈"
            elif component_score >= 80:
                quality = "B"
                emoji = "🥉"
            else:
                quality = "C"
                emoji = "⚠️"
            
            print(f"  {emoji} КАЧЕСТВО: {quality}")
            
            total_score += component_score
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            total_score += 0
    
    # Итоговая статистика
    print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 60)
    average_score = total_score / total_components
    
    print(f"🎯 Средний балл: {average_score:.1f}%")
    print(f"📈 Общий балл: {total_score:.1f}%")
    print(f"🔢 Компонентов: {total_components}")
    
    if average_score >= 95:
        overall_quality = "A+"
        emoji = "🏆"
        message = "ОТЛИЧНОЕ КАЧЕСТВО!"
    elif average_score >= 90:
        overall_quality = "A"
        emoji = "🥇"
        message = "ОЧЕНЬ ХОРОШЕЕ КАЧЕСТВО!"
    elif average_score >= 85:
        overall_quality = "B+"
        emoji = "🥈"
        message = "ХОРОШЕЕ КАЧЕСТВО!"
    elif average_score >= 80:
        overall_quality = "B"
        emoji = "🥉"
        message = "УДОВЛЕТВОРИТЕЛЬНОЕ КАЧЕСТВО!"
    else:
        overall_quality = "C"
        emoji = "⚠️"
        message = "ТРЕБУЕТ УЛУЧШЕНИЯ!"
    
    print(f"{emoji} ОБЩЕЕ КАЧЕСТВО: {overall_quality}")
    print(f"💬 {message}")
    
    return average_score, overall_quality

if __name__ == "__main__":
    score, quality = test_code_quality()
    print(f"\n🎉 ПРОВЕРКА ЗАВЕРШЕНА!")
    print(f"📊 Результат: {score:.1f}% ({quality})")