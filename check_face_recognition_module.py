#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка наличия модуля РАСПОЗНАВАНИЕ ЛИЦ в защите
"""

import re

def check_face_recognition_module():
    """Проверяет наличие модуля РАСПОЗНАВАНИЕ ЛИЦ в защите"""
    
    with open('/Users/sergejhlystov/ALADDIN_NEW/MOBILE_APP_INFO_SECTIONS.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== ПРОВЕРКА МОДУЛЯ РАСПОЗНАВАНИЕ ЛИЦ ===\n")
    
    # Ищем модуль РАСПОЗНАВАНИЕ ЛИЦ
    face_recognition_pattern = r'### [^#\n]*24\. РАСПОЗНАВАНИЕ ЛИЦ[^#\n]*'
    face_recognition_match = re.search(face_recognition_pattern, content)
    
    if face_recognition_match:
        print("✅ МОДУЛЬ НАЙДЕН:")
        print(face_recognition_match.group())
        
        # Ищем описание модуля
        description_pattern = r'### [^#\n]*24\. РАСПОЗНАВАНИЕ ЛИЦ[^#\n]*\n\n\*\*Что это такое\?\*\*\n([^#\n]+)\n\n\*\*Что делает система:\*\*\n((?:[^#\n]*\n)*?)\*\*От чего защищает:\*\*\n((?:[^#\n]*\n)*?)(?=---|\n###)'
        description_match = re.search(description_pattern, content, re.DOTALL)
        
        if description_match:
            print("\n📋 ОПИСАНИЕ МОДУЛЯ:")
            print(f"Что это такое: {description_match.group(1).strip()}")
            print(f"Что делает система: {description_match.group(2).strip()}")
            print(f"От чего защищает: {description_match.group(3).strip()}")
        
        return True
    else:
        print("❌ МОДУЛЬ НЕ НАЙДЕН")
        return False

if __name__ == "__main__":
    found = check_face_recognition_module()
    if found:
        print("\n🎯 РЕЗУЛЬТАТ: Модуль РАСПОЗНАВАНИЕ ЛИЦ присутствует в системе защиты")
    else:
        print("\n🎯 РЕЗУЛЬТАТ: Модуль РАСПОЗНАВАНИЕ ЛИЦ отсутствует в системе защиты")
