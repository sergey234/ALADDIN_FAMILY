#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка распределения модулей по тарифам
"""

import re

def check_modules_distribution():
    """Проверяет распределение модулей по тарифам"""
    
    with open('/Users/sergejhlystov/ALADDIN_NEW/MOBILE_APP_INFO_SECTIONS.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== ПРОВЕРКА РАСПРЕДЕЛЕНИЯ МОДУЛЕЙ ПО ТАРИФАМ ===\n")
    
    # Ищем все модули в основном разделе
    main_modules_pattern = r'### [^#\n]+\d+\. [^#\n]+'
    main_modules = re.findall(main_modules_pattern, content)
    
    print(f"📋 ОСНОВНЫЕ МОДУЛИ: {len(main_modules)}")
    for i, module in enumerate(main_modules, 1):
        print(f"   {i}. {module}")
    
    # Ищем модули в Premium разделе
    premium_pattern = r'\d+\. \*\*[^*]+\*\*'
    premium_modules = re.findall(premium_pattern, content)
    
    print(f"\n⭐ МОДУЛИ В PREMIUM: {len(premium_modules)}")
    
    # Фильтруем только основные модули (не функции)
    premium_main_modules = []
    for module in premium_modules:
        if not any(word in module.lower() for word in ['контроль', 'фильтрация', 'управление', 'отслеживание', 'мониторинг', 'анализ', 'защита', 'блокировка', 'создание', 'настройка', 'проверка', 'шифрование', 'анонимная', 'семейная', 'голоса', 'лиц', 'вирусы', 'трояны', 'ransomware', 'шпионское', 'ботнеты', 'ddos', 'фишинговые', 'поддельные', 'вредоносные', 'криптовалютные', 'руткиты', 'небезопасные', 'dns', 'man-in-the-middle', 'sms', 'кража', 'геолокационные', 'bluetooth', 'взлом', 'компрометация', 'сетевые', 'телефонное', 'финансовое', 'медицинские', 'социальная', 'инвестиционные', 'лотерейные', 'романтические', 'техническое', 'образовательное', 'недвижимое', 'игровое', 'благотворительное', 'государственное', 'неподходящий', 'кибербуллинг', 'опасные', 'игровая', 'зависимость', 'чрезмерное', 'случайные', 'взрослые', 'насилие', 'наркотики', 'алкоголь', 'азартные', 'сексуальные', 'психологическое', 'эмоциональные', 'изоляция', 'персональных', 'компрометация', 'нарушение', 'слежка', 'темной', 'метаданных', 'финансовых', 'медицинских', 'образовательных', 'биометрических', 'геолокационных', 'поведенческих', 'социальных', 'профессиональных', 'deepfake', 'поддельные', 'спуфинг', 'фейковые', 'документы', 'профили', 'уведомления', 'приложения', 'сертификаты', 'домашнее', 'семейные', 'конфликты', 'поколенческие', 'цифровое', 'военное', 'государственного', 'анонимность', 'vpn', 'критической']):
            premium_main_modules.append(module)
    
    print(f"\n🔍 ОСНОВНЫЕ МОДУЛИ В PREMIUM: {len(premium_main_modules)}")
    for i, module in enumerate(premium_main_modules, 1):
        print(f"   {i}. {module}")
    
    # Проверяем соответствие
    print(f"\n📊 СРАВНЕНИЕ:")
    print(f"   Основные модули: {len(main_modules)}")
    print(f"   Модули в Premium: {len(premium_main_modules)}")
    
    if len(main_modules) == len(premium_main_modules):
        print("   ✅ КОЛИЧЕСТВО СОВПАДАЕТ")
    else:
        print("   ❌ КОЛИЧЕСТВО НЕ СОВПАДАЕТ")
    
    return len(main_modules), len(premium_main_modules)

if __name__ == "__main__":
    main_count, premium_count = check_modules_distribution()
    print(f"\n🎯 ИТОГ: {main_count} основных модулей, {premium_count} в Premium")
