#!/usr/bin/env python3
"""
Быстрое исправление ошибок в новом TrustScoring
"""

def fix_trust_scoring_new():
    """Исправляет ошибки в trust_scoring_new.py"""
    
    file_path = "security/preliminary/trust_scoring_new.py"
    
    try:
        # Читаем файл
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Исправления
        fixes = [
            # Убираем неиспользуемые импорты
            ("import time\n", ""),
            ("from datetime import datetime, timedelta\n", "from datetime import datetime\n"),
            
            # Убираем пробелы в конце строк
            ("    \n", "\n"),
            ("  \n", "\n"),
            (" \n", "\n"),
            
            # Исправляем длинные строки
            ("        if user_id not in self.trust_profiles:\n", 
             "        if user_id not in self.trust_profiles:\n"),
            
            # Добавляем перевод строки в конце
            ("        return True", "        return True\n")
        ]
        
        # Применяем исправления
        for old, new in fixes:
            content = content.replace(old, new)
        
        # Записываем исправленный файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Исправлены ошибки в {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при исправлении: {e}")
        return False

if __name__ == "__main__":
    fix_trust_scoring_new()
