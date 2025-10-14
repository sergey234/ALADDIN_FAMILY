#!/usr/bin/env python3
"""
Создание улучшенной версии security_monitoring.py с исправлением всех Flake8 ошибок
"""

import re
from datetime import datetime

def create_enhanced_security_monitoring():
    """Создает улучшенную версию security_monitoring.py"""
    
    # Читаем продвинутую версию
    with open('security/security_monitoring_ultimate_a_plus.py.backup_20250927_031440', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 СОЗДАНИЕ УЛУЧШЕННОЙ ВЕРСИИ SECURITY_MONITORING")
    print("=" * 60)
    
    # Исправляем Flake8 ошибки
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines, 1):
        # W293: blank line contains whitespace
        if line.strip() == '' and line != '':
            fixed_lines.append('')
            print(f"   Строка {i}: Исправлены пробелы в пустой строке")
        # W291: trailing whitespace
        elif line.rstrip() != line:
            fixed_lines.append(line.rstrip())
            print(f"   Строка {i}: Удалены trailing пробелы")
        # E128: continuation line under-indented for visual indent
        elif 'def _create_event(self, event_id: str, level: MonitoringLevel,' in line:
            fixed_lines.append('    def _create_event(self, event_id: str, level: MonitoringLevel,')
        elif 'alert_type: AlertType, description: str,' in line:
            fixed_lines.append('                         alert_type: AlertType, description: str,')
        elif 'source: str) -> SecurityEvent:' in line:
            fixed_lines.append('                         source: str) -> SecurityEvent:')
        else:
            fixed_lines.append(line)
    
    # Создаем улучшенную версию
    enhanced_content = '\n'.join(fixed_lines)
    
    # Создаем резервную копию текущего файла
    backup_name = f"security/security_monitoring_backup_before_enhancement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    with open(backup_name, 'w', encoding='utf-8') as f:
        with open('security/security_monitoring.py', 'r', encoding='utf-8') as orig:
            f.write(orig.read())
    
    print(f"   📁 Создана резервная копия: {backup_name}")
    
    # Записываем улучшенную версию
    with open('security/security_monitoring.py', 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print(f"   ✅ Создана улучшенная версия: security/security_monitoring.py")
    
    return True

if __name__ == "__main__":
    success = create_enhanced_security_monitoring()
    exit(0 if success else 1)
