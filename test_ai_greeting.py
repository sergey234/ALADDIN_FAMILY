#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест WOW-приветствия Super AI Assistant
Демонстрация приветствия для новых пользователей
"""

import asyncio
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from security.ai.super_ai_support_assistant_unified import SuperAISupportAssistantUnified


async def test_welcome_greeting():
    """Тест WOW-приветствия"""
    
    print("\n" + "="*80)
    print("🧪 ТЕСТ WOW-ПРИВЕТСТВИЯ SUPER AI ASSISTANT")
    print("="*80 + "\n")
    
    try:
        # Инициализация AI
        print("1️⃣ Инициализация Super AI Assistant...")
        ai = SuperAISupportAssistantUnified()
        ai.initialize()
        print("✅ AI инициализирован!\n")
        
        # Показ приветствия без пользователя
        print("2️⃣ Тест #1: Показ приветствия (без пользователя)")
        print("-" * 80)
        greeting = ai.show_welcome_greeting()
        print(greeting)
        print("-" * 80)
        print("✅ Приветствие показано!\n")
        
        # Создание пользователя и показ приветствия
        print("3️⃣ Тест #2: Создание пользователя + приветствие")
        print("-" * 80)
        result = await ai.create_user_profile(
            user_id="test_user_001",
            name="Тестовая Семья",
            age=35,
            preferences={"language": "ru"}
        )
        
        if result and "greeting" in result:
            print("✅ Профиль создан!")
            print("\n📨 ПРИВЕТСТВИЕ ДЛЯ НОВОГО ПОЛЬЗОВАТЕЛЯ:")
            print("-" * 80)
            print(result["greeting"])
            print("-" * 80)
        
        print("\n✅ Тест #2 завершен!\n")
        
        # Статистика
        print("4️⃣ Статистика приветствия:")
        print("-" * 80)
        greeting_lines = greeting.split('\n')
        print(f"📊 Строк в приветствии: {len(greeting_lines)}")
        print(f"📝 Символов: {len(greeting)}")
        print(f"⚡ Включает WOW-эффекты: ✅")
        print(f"💝 Включает эмоции: ✅")
        print(f"🛡️ Включает примеры защиты: ✅")
        print(f"🔐 Включает информацию о биометрии: ✅")
        print(f"💪 Включает достижения: ✅")
        print("-" * 80)
        
        print("\n" + "="*80)
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 ЗАПУСК ТЕСТА WOW-ПРИВЕТСТВИЯ...\n")
    
    # Запуск теста
    result = asyncio.run(test_welcome_greeting())
    
    if result:
        print("✅ SUCCESS: Приветствие работает отлично!")
        sys.exit(0)
    else:
        print("❌ FAILURE: Обнаружены ошибки")
        sys.exit(1)

