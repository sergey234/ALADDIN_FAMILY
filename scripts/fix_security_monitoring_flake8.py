#!/usr/bin/env python3
"""
Скрипт для исправления Flake8 ошибок в security_monitoring.py
"""

import re

def fix_flake8_errors():
    """Исправляет Flake8 ошибки в файле"""
    
    file_path = "security/security_monitoring.py"
    
    try:
        # Читаем файл
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔧 ИСПРАВЛЕНИЕ FLAKE8 ОШИБОК")
        print("=" * 50)
        
        # Исправляем ошибки
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines, 1):
            # W293: blank line contains whitespace
            if line.strip() == '' and line != '':
                fixed_lines.append('')
                print(f"   Строка {i}: Удалены пробелы из пустой строки")
            # W291: trailing whitespace
            elif line.rstrip() != line:
                fixed_lines.append(line.rstrip())
                print(f"   Строка {i}: Удалены trailing пробелы")
            # E128: continuation line under-indented for visual indent
            elif i == 84 or i == 85:  # Специфичные строки с проблемами отступов
                if 'def _create_event(self, event_id: str, level: MonitoringLevel,' in line:
                    fixed_lines.append('    def _create_event(self, event_id: str, level: MonitoringLevel,')
                elif 'alert_type: AlertType, description: str,' in line:
                    fixed_lines.append('                         alert_type: AlertType, description: str,')
                elif 'source: str) -> SecurityEvent:' in line:
                    fixed_lines.append('                         source: str) -> SecurityEvent:')
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        # Записываем исправленный файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        
        print(f"\n✅ Файл исправлен: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = fix_flake8_errors()
    exit(0 if success else 1)
