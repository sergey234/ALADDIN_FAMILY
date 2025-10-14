#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Подсчет модулей в системе ALADDIN - исправленная версия
"""

import re

def count_modules():
    """Подсчитывает количество модулей в мобильном приложении"""
    
    with open('/Users/sergejhlystov/ALADDIN_NEW/MOBILE_APP_INFO_SECTIONS.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем все заголовки модулей - более простой паттерн
    module_pattern = r'### [^#\n]+\d+\. [^#\n]+'
    
    modules = re.findall(module_pattern, content)
    
    print(f"Найдено модулей: {len(modules)}")
    print("\nСписок модулей:")
    for i, module in enumerate(modules, 1):
        print(f"{i}. {module}")
    
    # Также ищем модули в разделе Premium
    premium_pattern = r'\d+\. \*\*[^*]+\*\*'
    premium_modules = re.findall(premium_pattern, content)
    
    print(f"\nМодули в Premium разделе: {len(premium_modules)}")
    for i, module in enumerate(premium_modules, 1):
        print(f"{i}. {module}")
    
    return len(modules), len(premium_modules)

if __name__ == "__main__":
    main_count, premium_count = count_modules()
    print(f"\nИтого основных модулей: {main_count}")
    print(f"Итого модулей в Premium: {premium_count}")
