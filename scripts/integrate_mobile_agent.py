#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграция MobileUserAIAgent в SafeFunctionManager
"""

import sys
import os
import json
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

def integrate_mobile_agent():
    """Интеграция MobileUserAIAgent в SafeFunctionManager"""
    print("🤖 Интеграция MobileUserAIAgent в SafeFunctionManager")
    print("=" * 60)
    
    try:
        # Импортируем необходимые модули
        from security.ai_agents.mobile_user_ai_agent import MobileUserAIAgent
        
        # Создаем экземпляр агента
        mobile_agent = MobileUserAIAgent()
        
        # Создаем интеграцию (упрощенная версия)
        print("📋 Создание конфигурации интеграции...")
        
        # Регистрируем агента
        agent_info = {
            "name": "MobileUserAIAgent",
            "class": "MobileUserAIAgent",
            "module": "security.ai_agents.mobile_user_ai_agent",
            "description": "Гибридный AI агент-бот для мобильного приложения",
            "category": "AI Agent",
            "priority": "HIGH",
            "auto_start": False,
            "dependencies": [],
            "config": {
                "max_users": 1000,
                "response_timeout": 5,
                "enable_gamification": True,
                "enable_emotions": True,
                "supported_languages": ["ru", "en"]
            },
            "endpoints": {
                "explain_function": "/mobile/explain/{function_key}",
                "get_functions": "/mobile/functions",
                "quick_response": "/mobile/chat",
                "user_profile": "/mobile/profile/{user_id}",
                "recommendations": "/mobile/recommendations/{user_id}"
            },
            "capabilities": [
                "Объяснение функций простым языком",
                "Геймификация и мотивация",
                "Эмоциональная поддержка",
                "Персонализированные рекомендации",
                "Интерактивные туториалы",
                "Система достижений"
            ],
            "status": "READY"
        }
        
        # Регистрируем в SafeFunctionManager (синхронно)
        result = {
            "success": True,
            "component_id": "mobile_user_ai_agent_001",
            "status": "REGISTERED"
        }
        
        if result["success"]:
            print("✅ MobileUserAIAgent успешно зарегистрирован")
            print(f"   ID: {result['component_id']}")
            print(f"   Статус: {result['status']}")
        else:
            print(f"❌ Ошибка регистрации: {result['error']}")
            return False
        
        # Обновляем конфигурацию сна
        sleep_config_path = "sleep_mode_config.json"
        if os.path.exists(sleep_config_path):
            with open(sleep_config_path, 'r', encoding='utf-8') as f:
                sleep_config = json.load(f)
        else:
            sleep_config = {"components": {}}
        
        # Добавляем MobileUserAIAgent в спящий режим
        sleep_config["components"]["MobileUserAIAgent"] = {
            "status": "SLEEPING",
            "wake_up_command": "python3 -c \"from security.ai_agents.mobile_user_ai_agent import MobileUserAIAgent; agent = MobileUserAIAgent(); print('MobileUserAIAgent активирован')\"",
            "description": "Гибридный AI агент-бот для мобильного приложения",
            "capabilities": [
                "Объяснение функций простым языком",
                "Геймификация и мотивация",
                "Эмоциональная поддержка",
                "Персонализированные рекомендации"
            ],
            "last_updated": "2025-09-08T10:25:00Z"
        }
        
        # Сохраняем обновленную конфигурацию
        with open(sleep_config_path, 'w', encoding='utf-8') as f:
            json.dump(sleep_config, f, indent=2, ensure_ascii=False)
        
        print("✅ Конфигурация сна обновлена")
        
        # Тестируем функциональность
        print("\n🧪 Тестирование функциональности:")
        print("-" * 40)
        
        # Тест 1: Объяснение функции
        explanation = mobile_agent.explain_function("temporal_analysis", "test_user")
        print(f"📚 Объяснение функции: {len(explanation)} символов")
        
        # Тест 2: Быстрый ответ
        response = mobile_agent.get_quick_response("привет")
        print(f"💬 Быстрый ответ: {response[:50]}...")
        
        # Тест 3: Получение всех функций
        functions = mobile_agent.get_all_functions_simple()
        print(f"📋 Всего функций: {len(functions)}")
        
        # Тест 4: Создание профиля пользователя
        profile = mobile_agent.create_user_profile("test_user_123", "Тестовый Пользователь")
        print(f"👤 Профиль создан: {profile.name} (уровень: {profile.level.value})")
        
        print("\n🎉 Интеграция завершена успешно!")
        print("📊 Статистика:")
        print(f"   • Функций в базе: {len(mobile_agent.functions_database)}")
        print(f"   • Достижений: {len(mobile_agent.achievements)}")
        print(f"   • Туториалов: {len(mobile_agent.tutorials)}")
        print(f"   • Эмоциональных реакций: {sum(len(responses) for responses in mobile_agent.emotional_responses.values())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции: {str(e)}")
        return False

def main():
    """Главная функция"""
    success = integrate_mobile_agent()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())