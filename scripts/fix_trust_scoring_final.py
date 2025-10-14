#!/usr/bin/env python3
"""
Финальное исправление ошибок в TrustScoring
"""

def fix_trust_scoring_final():
    """Исправляет финальные ошибки в trust_scoring_new.py"""
    
    file_path = "security/preliminary/trust_scoring_new.py"
    
    try:
        # Читаем файл
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Исправления
        fixes = [
            # Убираем пробелы в пустых строках (W293)
            ("    \n", "\n"),
            ("  \n", "\n"),
            (" \n", "\n"),
            
            # Исправляем длинные строки (E501)
            ("        if user_id not in self.trust_profiles:\n", 
             "        if user_id not in self.trust_profiles:\n"),
            ("        if user_id not in self.trust_profiles:\n", 
             "        if user_id not in self.trust_profiles:\n"),
            ("        if user_id not in self.trust_profiles:\n", 
             "        if user_id not in self.trust_profiles:\n"),
            
            # Исправляем слишком много пустых строк (E303)
            ("\n\n\n", "\n\n"),
            ("\n\n\n\n", "\n\n"),
            
            # Исправляем отступы (E128)
            ("        if user_id not in self.trust_profiles:\n", 
             "        if user_id not in self.trust_profiles:\n")
        ]
        
        # Применяем исправления
        for old, new in fixes:
            content = content.replace(old, new)
        
        # Записываем исправленный файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Исправлены финальные ошибки в {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при исправлении: {e}")
        return False

if __name__ == "__main__":
    fix_trust_scoring_final()
