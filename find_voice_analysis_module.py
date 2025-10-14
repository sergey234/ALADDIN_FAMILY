#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Поиск модуля АНАЛИЗ ГОЛОСА в системе
"""

import re

def find_voice_analysis_module():
    """Ищет модуль АНАЛИЗ ГОЛОСА в системе"""
    
    with open('/Users/sergejhlystov/ALADDIN_NEW/MOBILE_APP_INFO_SECTIONS.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== ПОИСК МОДУЛЯ АНАЛИЗ ГОЛОСА ===\n")
    
    # Ищем все упоминания "АНАЛИЗ ГОЛОСА"
    voice_analysis_pattern = r'АНАЛИЗ ГОЛОСА'
    voice_analysis_matches = re.findall(voice_analysis_pattern, content)
    
    print(f"📋 НАЙДЕНО УПОМИНАНИЙ: {len(voice_analysis_matches)}")
    
    # Ищем полное описание модуля
    module_pattern = r'### [^#\n]*22\. АНАЛИЗ ГОЛОСА[^#\n]*\n\n\*\*Что это такое\?\*\*\n([^#\n]+)\n\n\*\*Что делает система:\*\*\n((?:[^#\n]*\n)*?)\*\*От чего защищает:\*\*\n((?:[^#\n]*\n)*?)(?=---|\n###)'
    module_match = re.search(module_pattern, content, re.DOTALL)
    
    if module_match:
        print("✅ МОДУЛЬ НАЙДЕН:")
        print(f"Номер: 22")
        print(f"Название: АНАЛИЗ ГОЛОСА")
        print(f"Что это такое: {module_match.group(1).strip()}")
        print(f"Что делает система: {module_match.group(2).strip()}")
        print(f"От чего защищает: {module_match.group(3).strip()}")
        
        # Ищем конкретные функции
        functions_pattern = r'1\. \*\*🎤 Анализ голоса\*\* - ([^#\n]+)\n2\. \*\*🔍 Обнаружение подделок\*\* - ([^#\n]+)\n3\. \*\*🛡️ Защита от deepfake\*\* - ([^#\n]+)\n4\. \*\*⚠️ Предупреждения\*\* - ([^#\n]+)\n5\. \*\*📊 Анализ эмоций\*\* - ([^#\n]+)'
        functions_match = re.search(functions_pattern, content)
        
        if functions_match:
            print("\n🎯 НАЙДЕННЫЕ ФУНКЦИИ:")
            print(f"1. 🎤 Анализ голоса - {functions_match.group(1).strip()}")
            print(f"2. 🔍 Обнаружение подделок - {functions_match.group(2).strip()}")
            print(f"3. 🛡️ Защита от deepfake - {functions_match.group(3).strip()}")
            print(f"4. ⚠️ Предупреждения - {functions_match.group(4).strip()}")
            print(f"5. 📊 Анализ эмоций - {functions_match.group(5).strip()}")
        
        return True
    else:
        print("❌ МОДУЛЬ НЕ НАЙДЕН")
        return False

if __name__ == "__main__":
    found = find_voice_analysis_module()
    if found:
        print("\n🎯 РЕЗУЛЬТАТ: Модуль АНАЛИЗ ГОЛОСА присутствует в системе")
    else:
        print("\n🎯 РЕЗУЛЬТАТ: Модуль АНАЛИЗ ГОЛОСА отсутствует в системе")
