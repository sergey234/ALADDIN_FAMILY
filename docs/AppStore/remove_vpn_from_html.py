#!/usr/bin/env python3
# Скрипт для удаления всех упоминаний VPN из privacy.html и terms.html

import re
import sys
from datetime import datetime

def remove_vpn_from_file(file_path):
    """Удаляет все упоминания VPN из HTML файла"""
    
    # Читаем файл
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Удаляем строку "Где используем: VPN подключение..."
    content = re.sub(
        r'<p><strong>Где используем:</strong>\s*VPN подключение[^<]*</p>',
        '',
        content,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    # 2. Удаляем "Zero-logs VPN"
    content = re.sub(
        r'<li>.*?Zero-logs\s+VPN.*?</li>',
        '',
        content,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    # 3. Удаляем "Энергосбережение VPN"
    content = re.sub(
        r'<li>.*?Энергосбережение\s+VPN.*?</li>',
        '',
        content,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    # 4. Удаляем весь раздел "6. VPN и безопасность" в terms.html
    # Находим начало раздела (комментарий или заголовок)
    content = re.sub(
        r'<!--\s*6\.\s*VPN\s+и\s+безопасность\s*-->.*?<h2>6\.\s*VPN\s+и\s+безопасность</h2>.*?</section>',
        '',
        content,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    # 5. Заменяем "Включает: VPN, антивирус..." на "Включает: антивирус..."
    content = re.sub(
        r'<li>Включает:\s*VPN,\s*',
        '<li>Включает: ',
        content,
        flags=re.IGNORECASE
    )
    
    # 6. Удаляем отдельные упоминания "VPN" в тексте (но не в тегах)
    # Более аккуратно - только в тексте параграфов
    content = re.sub(
        r'(<p[^>]*>.*?)\bVPN\b([^<]*</p>)',
        r'\1\2',
        content,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    # 7. Удаляем упоминания VPN в списках
    content = re.sub(
        r'<li>.*?\bVPN\b.*?</li>',
        '',
        content,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    # 8. Очищаем множественные пустые строки
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    
    # Сохраняем только если были изменения
    if content != original_content:
        # Создаем резервную копию
        backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"✅ Backup created: {backup_path}")
        
        # Сохраняем измененный файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ VPN removed from: {file_path}")
        return True
    else:
        print(f"⚠️ No VPN found in: {file_path}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 remove_vpn_from_html.py <file1> [file2] ...")
        sys.exit(1)
    
    for file_path in sys.argv[1:]:
        try:
            remove_vpn_from_file(file_path)
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
