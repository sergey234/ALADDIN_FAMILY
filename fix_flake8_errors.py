#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления ошибок flake8
"""

import os
import re

def fix_file(filepath):
    """Исправление ошибок flake8 в файле"""
    print(f"Исправление файла: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Исправления
    fixes = [
        # Удаление неиспользуемых импортов
        (r'from datetime import datetime, timedelta\n', 'from datetime import datetime\n'),
        (r'from typing import Dict, List, Any, Optional\n', 'from typing import Dict, List, Any\n'),
        (r'from typing import Dict, List, Any, Tuple\n', 'from typing import Dict, List, Any\n'),
        
        # Исправление f-strings без placeholder
        (r'f"Исправление файла: \{filepath\}"', '"Исправление файла: {}"'.format(filepath)),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    # Удаление пробелов в конце строк
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]
    content = '\n'.join(lines)
    
    # Добавление новой строки в конец
    if not content.endswith('\n'):
        content += '\n'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Файл исправлен: {filepath}")

def main():
    """Основная функция"""
    files_to_fix = [
        'security/ai_agents/auto_learning_system.py',
        'security/ai_agents/enhanced_data_collector.py',
        'security/ai_agents/fraud_detection_api.py',
        'security/ai_agents/improved_ml_models.py'
    ]
    
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            fix_file(filepath)
        else:
            print(f"❌ Файл не найден: {filepath}")
    
    print("🎉 Все файлы исправлены!")

if __name__ == "__main__":
    main()