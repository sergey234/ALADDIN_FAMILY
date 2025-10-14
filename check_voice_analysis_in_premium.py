#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка наличия модуля АНАЛИЗ ГОЛОСА в Premium тарифе
"""

import re

def check_voice_analysis_in_premium():
    """Проверяет наличие модуля АНАЛИЗ ГОЛОСА в Premium тарифе"""
    
    with open('/Users/sergejhlystov/ALADDIN_NEW/MOBILE_APP_INFO_SECTIONS.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== ПРОВЕРКА МОДУЛЯ АНАЛИЗ ГОЛОСА В PREMIUM ===\n")
    
    # Ищем раздел Premium
    premium_pattern = r'### ⭐ PREMIUM - 900₽/месяц.*?(?=### |$)'
    premium_match = re.search(premium_pattern, content, re.DOTALL)
    
    if premium_match:
        premium_content = premium_match.group()
        print("✅ РАЗДЕЛ PREMIUM НАЙДЕН")
        
        # Ищем модуль АНАЛИЗ ГОЛОСА в Premium
        voice_analysis_pattern = r'22\. \*\*АНАЛИЗ ГОЛОСА\*\*'
        voice_analysis_match = re.search(voice_analysis_pattern, premium_content)
        
        if voice_analysis_match:
            print("✅ МОДУЛЬ АНАЛИЗ ГОЛОСА НАЙДЕН В PREMIUM")
            
            # Ищем описание модуля в Premium
            description_pattern = r'22\. \*\*АНАЛИЗ ГОЛОСА\*\*\n((?:[^#\n]*\n)*?)(?=\n\d+\.|\n\*\*🎯 Защищает от:)'
            description_match = re.search(description_pattern, premium_content)
            
            if description_match:
                print("📋 ОПИСАНИЕ В PREMIUM:")
                print(description_match.group(1).strip())
            
            return True
        else:
            print("❌ МОДУЛЬ АНАЛИЗ ГОЛОСА НЕ НАЙДЕН В PREMIUM")
            return False
    else:
        print("❌ РАЗДЕЛ PREMIUM НЕ НАЙДЕН")
        return False

if __name__ == "__main__":
    found = check_voice_analysis_in_premium()
    if found:
        print("\n🎯 РЕЗУЛЬТАТ: Модуль АНАЛИЗ ГОЛОСА присутствует в Premium тарифе")
    else:
        print("\n🎯 РЕЗУЛЬТАТ: Модуль АНАЛИЗ ГОЛОСА отсутствует в Premium тарифе")
