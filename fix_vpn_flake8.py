#!/usr/bin/env python3
"""
Скрипт для автоматического исправления ошибок Flake8 в VPN модулях
"""

import re
from pathlib import Path

def fix_flake8_errors(file_path):
    """Исправление ошибок Flake8 в файле"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Удаляем trailing whitespace (W291)
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]
    content = '\n'.join(lines)
    
    # 2. Удаляем пробелы в пустых строках (W293)
    content = re.sub(r'\n\s+\n', '\n\n', content)
    
    # 3. Исправляем неиспользуемые импорты (F401)
    # vpn_manager.py
    if 'vpn_manager.py' in str(file_path):
        content = content.replace('import time\n', '')
        content = content.replace('from typing import Dict, List, Optional, Any, Union', 
                                'from typing import Dict, Optional, Any')
    
    # vpn_monitoring.py
    if 'vpn_monitoring.py' in str(file_path):
        content = content.replace('import socket\n', '')
    
    # vpn_integration.py
    if 'vpn_integration.py' in str(file_path):
        content = content.replace('import time\n', '')
        content = content.replace('from datetime import datetime, timedelta',
                                'from datetime import datetime')
        content = content.replace('from typing import Dict, List, Optional, Any, Union, Callable',
                                'from typing import Dict, List, Optional, Any, Callable')
        content = content.replace('import base64\n', '')
        content = content.replace('from urllib.parse import urlencode, urlparse\n', '')
    
    # vpn_analytics.py
    if 'vpn_analytics.py' in str(file_path):
        content = content.replace('import csv\n', '')
    
    # 4. Исправляем E261 (at least two spaces before inline comment)
    content = re.sub(r' #', '  #', content)
    
    # Сохраняем только если были изменения
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Главная функция"""
    vpn_files = [
        'security/vpn/vpn_manager.py',
        'security/vpn/vpn_monitoring.py',
        'security/vpn/vpn_analytics.py',
        'security/vpn/vpn_integration.py'
    ]
    
    fixed_count = 0
    for file_path in vpn_files:
        if fix_flake8_errors(file_path):
            print(f"✅ Исправлен: {file_path}")
            fixed_count += 1
        else:
            print(f"⏭️  Без изменений: {file_path}")
    
    print(f"\n📊 Итого исправлено файлов: {fixed_count}/{len(vpn_files)}")

if __name__ == "__main__":
    main()
