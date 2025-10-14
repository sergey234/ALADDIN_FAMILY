#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ функций и угроз системы ALADDIN Family Security System
"""

import re
import os

def analyze_functions_and_threats():
    """Анализирует количество функций и угроз в системе"""
    
    # Читаем документацию
    with open('/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_FAMILY_SECURITY_SYSTEM_COMPLETE_DOCUMENTATION.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем все основные функции
    functions_pattern = r'- \*\*Основные функции:\*\*\s*\n((?:  - .+\n?)*)'
    functions_matches = re.findall(functions_pattern, content, re.MULTILINE)
    
    all_functions = []
    all_threats = []
    
    print("=== АНАЛИЗ ФУНКЦИЙ И УГРОЗ СИСТЕМЫ ALADDIN ===\n")
    
    # Обрабатываем каждый модуль
    module_pattern = r'\*\*([^*]+\.py)\*\*.*?\*\*Основные функции:\*\*\s*\n((?:  - .+\n?)*)\*\*Защищает от:\*\* ((?:[^-]|-[^-])*)'
    module_matches = re.findall(module_pattern, content, re.DOTALL)
    
    total_functions = 0
    total_threats = 0
    modules_count = 0
    
    print("📋 МОДУЛИ И ИХ ФУНКЦИИ:")
    print("=" * 50)
    
    for module_name, functions_text, threats_text in module_matches:
        modules_count += 1
        
        # Извлекаем функции
        functions = re.findall(r'  - ([^-\n]+)', functions_text)
        functions = [f.strip() for f in functions if f.strip()]
        
        # Извлекаем угрозы
        threats = re.findall(r'[^,]+', threats_text)
        threats = [t.strip() for t in threats if t.strip() and t.strip() != '**Интеграция:**']
        
        total_functions += len(functions)
        total_threats += len(threats)
        
        print(f"\n🔧 {module_name}")
        print(f"   Функций: {len(functions)}")
        print(f"   Угроз: {len(threats)}")
        
        # Добавляем в общие списки
        all_functions.extend(functions)
        all_threats.extend(threats)
    
    # Ищем дополнительные функции в интегрированных модулях
    integrated_pattern = r'\*\*ИНТЕГРИРОВАННЫЕ ФУНКЦИИ:\*\*\s*\n((?:    - .+\n?)*)'
    integrated_matches = re.findall(integrated_pattern, content, re.MULTILINE)
    
    integrated_functions = 0
    for match in integrated_matches:
        functions = re.findall(r'    - ([^-\n]+)', match)
        integrated_functions += len(functions)
        all_functions.extend([f.strip() for f in functions if f.strip()])
    
    # Ищем функции AURA
    aura_pattern = r'\*\*([^*]+)\*\*\s*\n- \*\*Файл:\*\* ([^*]+)\n- \*\*Функция:\*\* ([^*]+)\n- \*\*Что делает:\*\* ([^*]+)\n- \*\*Защищает от:\*\* ([^*]+)'
    aura_matches = re.findall(aura_pattern, content, re.MULTILINE)
    
    aura_functions = 0
    for aura_name, file_name, function_name, description, threats in aura_matches:
        aura_functions += 1
        all_functions.append(f"{function_name} - {description}")
        # Разбираем угрозы
        threat_list = re.findall(r'[^,]+', threats)
        all_threats.extend([t.strip() for t in threat_list if t.strip()])
    
    # Ищем геймификацию
    gamification_functions = [
        "5 игровых уровней",
        "5 типов достижений", 
        "Система очков",
        "Награды и персонажи",
        "Обучающие игры",
        "Семейные квесты"
    ]
    
    all_functions.extend(gamification_functions)
    
    print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 50)
    print(f"🔧 Модулей: {modules_count}")
    print(f"⚙️ Основных функций: {total_functions}")
    print(f"🔗 Интегрированных функций: {integrated_functions}")
    print(f"🌟 AURA функций: {aura_functions}")
    print(f"🎮 Геймификация функций: {len(gamification_functions)}")
    print(f"📈 ВСЕГО ФУНКЦИЙ: {len(all_functions)}")
    print(f"🛡️ ВСЕГО УГРОЗ: {len(set(all_threats))}")
    
    # Анализируем типы угроз
    print(f"\n🛡️ АНАЛИЗ ТИПОВ УГРОЗ:")
    print("=" * 50)
    
    threat_categories = {
        'Киберугрозы': ['вирусы', 'трояны', 'ransomware', 'шпионское', 'ботнеты', 'ddos', 'фишинг', 'вредоносное'],
        'Мошенничество': ['мошенничество', 'фишинг', 'социальная инженерия', 'поддельные', 'аферы'],
        'Детские угрозы': ['неподходящий контент', 'кибербуллинг', 'опасные знакомства', 'игровая зависимость'],
        'Утечки данных': ['кража паролей', 'утечки', 'компрометация', 'приватность', 'слежка'],
        'Подделки': ['deepfake', 'спуфинг', 'поддельные', 'фейковые'],
        'Семейные угрозы': ['семейные конфликты', 'изоляция', 'эмоциональные проблемы']
    }
    
    for category, keywords in threat_categories.items():
        count = 0
        for threat in set(all_threats):
            if any(keyword.lower() in threat.lower() for keyword in keywords):
                count += 1
        print(f"   {category}: {count} типов")
    
    # Проверяем соответствие с мобильным приложением
    print(f"\n📱 СООТВЕТСТВИЕ С МОБИЛЬНЫМ ПРИЛОЖЕНИЕМ:")
    print("=" * 50)
    
    mobile_file = '/Users/sergejhlystov/ALADDIN_NEW/MOBILE_APP_INFO_SECTIONS.md'
    if os.path.exists(mobile_file):
        with open(mobile_file, 'r', encoding='utf-8') as f:
            mobile_content = f.read()
        
        # Ищем упоминания о количестве функций и угроз
        functions_mentions = re.findall(r'(\d+)\+?\s*функци', mobile_content, re.IGNORECASE)
        threats_mentions = re.findall(r'(\d+)\+?\s*типов?\s*угроз', mobile_content, re.IGNORECASE)
        
        print(f"   Упоминания функций в мобильном приложении: {functions_mentions}")
        print(f"   Упоминания угроз в мобильном приложении: {threats_mentions}")
    
    return len(all_functions), len(set(all_threats))

if __name__ == "__main__":
    functions_count, threats_count = analyze_functions_and_threats()
    print(f"\n🎯 РЕЗУЛЬТАТ: {functions_count} функций защищают от {threats_count} типов угроз")
