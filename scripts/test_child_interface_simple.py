#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Упрощенный тест ChildInterfaceManager
"""

import os
import sys
import time
import json
from datetime import datetime

def test_child_interface_simple():
    """Упрощенный тест ChildInterfaceManager"""
    print("🧪 УПРОЩЕННЫЙ ТЕСТ CHILDINTERFACEMANAGER")
    print("=" * 50)
    
    try:
        # Проверка импорта
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'security', 'ai_agents'))
        
        from child_interface_manager import (
            ChildInterfaceManager, 
            ChildAgeCategory, 
            GameLevel, 
            AchievementType,
            ChildInterfaceMetrics
        )
        
        print("✅ Импорт модулей успешен")
        
        # Создание экземпляра
        manager = ChildInterfaceManager()
        print("✅ Создание ChildInterfaceManager успешно")
        
        # Тест определения возрастной категории
        user_data_toddler = {
            "interaction_pattern": {"touch_heavy": True, "voice_commands": True},
            "preferences": {"simple_games": True},
            "behavior": {"help_seeking": True}
        }
        
        age_category = manager.detect_age_category(user_data_toddler)
        print("✅ Определение возрастной категории: {}".format(age_category.value))
        
        # Тест получения интерфейса
        interface = manager.get_interface_for_age(age_category)
        if interface and "design" in interface:
            print("✅ Получение интерфейса: {}".format(interface["design"]["theme"]))
        else:
            print("❌ Ошибка получения интерфейса")
            return False
        
        # Тест запуска обучающего модуля
        module = manager.start_learning_module(age_category, "interactive")
        if module and "module" in module:
            print("✅ Запуск обучающего модуля: {}".format(module["module"]))
        else:
            print("❌ Ошибка запуска модуля")
            return False
        
        # Тест завершения квеста
        quest_result = manager.complete_quest("test_user", "daily", 100)
        if quest_result and "progress" in quest_result:
            print("✅ Завершение квеста: балл {}".format(quest_result["progress"]["score"]))
        else:
            print("❌ Ошибка завершения квеста")
            return False
        
        # Тест семейной панели
        family_data = manager.get_family_dashboard_data("test_family")
        if family_data and "family_id" in family_data:
            print("✅ Получение семейных данных: {}".format(family_data["family_id"]))
        else:
            print("❌ Ошибка получения семейных данных")
            return False
        
        # Тест уведомлений
        notification = manager.send_parent_notification("test_parent", "Тест", "normal")
        if notification and "parent_id" in notification:
            print("✅ Отправка уведомления: {}".format(notification["parent_id"]))
        else:
            print("❌ Ошибка отправки уведомления")
            return False
        
        # Тест защиты приватности
        test_data = {"personal_info": "test", "device_id": "12345"}
        protected = manager.protect_privacy_data(test_data)
        if "***MASKED***" in str(protected):
            print("✅ Защита приватности работает")
        else:
            print("❌ Ошибка защиты приватности")
            return False
        
        # Тест шифрования
        encrypted = manager.encrypt_sensitive_data("test_password")
        if len(encrypted) == 64:  # SHA256 hash length
            print("✅ Шифрование работает")
        else:
            print("❌ Ошибка шифрования")
            return False
        
        # Тест валидации приватности
        privacy_settings = {
            "data_collection": True,
            "data_sharing": False,
            "data_retention": 30,
            "parental_consent": True,
            "child_protection": True
        }
        if manager.validate_privacy_settings(privacy_settings):
            print("✅ Валидация приватности работает")
        else:
            print("❌ Ошибка валидации приватности")
            return False
        
        # Тест метрик
        metrics = ChildInterfaceMetrics()
        metrics.update_metrics(
            {"age_category": "7-9"},
            {"module_completed": 1},
            {"quest_completed": 1},
            {"family_quest": 1}
        )
        if metrics.total_users == 1:
            print("✅ Метрики работают")
        else:
            print("❌ Ошибка метрик")
            return False
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ ChildInterfaceManager работает корректно")
        
        return True
        
    except Exception as e:
        print("❌ ОШИБКА ТЕСТИРОВАНИЯ: {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_child_interface_simple()
    if success:
        print("\n🏆 КАЧЕСТВО: A+ (ОТЛИЧНО)")
        print("✅ Все функции работают корректно")
    else:
        print("\n⚠️ КАЧЕСТВО: ТРЕБУЕТ УЛУЧШЕНИЯ")
    exit(0 if success else 1)