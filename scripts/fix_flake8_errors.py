#!/usr/bin/env python3
"""
Исправление ошибок flake8 в recovery_service.py
"""

import re
from pathlib import Path

def fix_flake8_errors():
    """Исправление ошибок flake8"""
    print("🔧 ИСПРАВЛЕНИЕ ОШИБОК FLAKE8")
    print("=" * 40)
    
    file_path = Path("security/reactive/recovery_service.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Исправляем ошибки
    fixed_lines = []
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # E301: expected 1 blank line, found 0
        if line_num in [1092, 1099, 1105, 1109, 1116, 1136, 1163]:
            if line.strip() and not line.startswith('    '):
                fixed_lines.append('')
            fixed_lines.append(line)
        
        # E501: line too long
        elif line_num in [1102, 1127, 1130, 1140, 1148, 1149, 1153, 1155, 1156, 1173, 1179]:
            if len(line) > 79:
                # Разбиваем длинные строки
                if 'return f"' in line:
                    # Для f-строк
                    parts = line.split('return f"')
                    if len(parts) == 2:
                        indent = len(line) - len(line.lstrip())
                        new_line = ' ' * indent + 'return f"' + parts[1]
                        if len(new_line) > 79:
                            # Разбиваем на несколько строк
                            fixed_lines.append(' ' * indent + 'return f"' + parts[1][:50] + '"')
                            fixed_lines.append(' ' * indent + '+ f"' + parts[1][50:] + '"')
                        else:
                            fixed_lines.append(new_line)
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        # W293: blank line contains whitespace
        elif line_num in [1121, 1125, 1129, 1146, 1150, 1155, 1157, 1159, 1168, 1171, 1178, 1181]:
            fixed_lines.append('')
        
        # W292: no newline at end of file
        elif line_num == len(lines) and line.strip():
            fixed_lines.append(line)
            fixed_lines.append('')
        
        else:
            fixed_lines.append(line)
    
    # Записываем исправленный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("   ✅ Ошибки flake8 исправлены")
    
    # Проверяем результат
    import subprocess
    result = subprocess.run(['python3', '-m', 'flake8', str(file_path)], 
                          capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print("   ✅ Flake8: 0 ошибок")
    else:
        error_count = len(result.stdout.split('\n')) - 1
        print(f"   ⚠️ Flake8: {error_count} ошибок осталось")
        print("   Первые 5 ошибок:")
        for error in result.stdout.split('\n')[:5]:
            if error.strip():
                print(f"      {error}")

if __name__ == "__main__":
    fix_flake8_errors()