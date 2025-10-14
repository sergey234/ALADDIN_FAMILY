#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Integrity Check - Проверка целостности SFM скриптов
Проверяет, что все критически важные SFM скрипты на месте
"""

import os
import sys
from datetime import datetime

class SFMIntegrityChecker:
    """Проверка целостности SFM скриптов"""
    
    def __init__(self):
        self.scripts_dir = "scripts"
        self.critical_scripts = {
            # Основные SFM скрипты
            'sfm_quick_stats.py': 'Быстрая статистика SFM',
            'sfm_analyzer.py': 'Детальный анализ SFM',
            'sfm_status': 'Shell скрипт статуса SFM',
            
            # Универсальные решения
            'sfm_stats_universal.py': 'Универсальная статистика с автопоиском',
            'sfm_status.sh': 'Shell скрипт с автопоиском',
            
            # Автоматические инструменты
            'sfm_add_function.py': 'Автоматическое добавление функций',
            'sfm_fix_and_validate.py': 'Валидация и исправление',
            'sfm_structure_validator.py': 'Проверка структуры',
            'sfm_manager.py': 'Главный менеджер SFM'
        }
        
        self.missing_scripts = []
        self.corrupted_scripts = []
        self.healthy_scripts = []
    
    def check_script_exists(self, script_name):
        """Проверка существования скрипта"""
        script_path = os.path.join(self.scripts_dir, script_name)
        return os.path.exists(script_path)
    
    def check_script_integrity(self, script_name):
        """Проверка целостности скрипта"""
        script_path = os.path.join(self.scripts_dir, script_name)
        
        if not os.path.exists(script_path):
            return False, "Файл не найден"
        
        try:
            # Проверка, что файл не пустой
            if os.path.getsize(script_path) == 0:
                return False, "Файл пустой"
            
            # Проверка, что файл читается
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content.strip()) == 0:
                return False, "Файл содержит только пробелы"
            
            # Проверка на наличие SFM ключевых слов
            if 'sfm' not in content.lower() and 'SFM' not in content:
                return False, "Файл не содержит SFM функциональность"
            
            return True, "OK"
            
        except Exception as e:
            return False, f"Ошибка чтения: {e}"
    
    def check_all_scripts(self):
        """Проверка всех критически важных скриптов"""
        print("🔍 ПРОВЕРКА ЦЕЛОСТНОСТИ SFM СКРИПТОВ")
        print("=" * 50)
        
        for script_name, description in self.critical_scripts.items():
            exists = self.check_script_exists(script_name)
            
            if not exists:
                self.missing_scripts.append(script_name)
                print(f"❌ {script_name}: НЕ НАЙДЕН - {description}")
                continue
            
            is_healthy, status = self.check_script_integrity(script_name)
            
            if is_healthy:
                self.healthy_scripts.append(script_name)
                print(f"✅ {script_name}: OK - {description}")
            else:
                self.corrupted_scripts.append((script_name, status))
                print(f"⚠️  {script_name}: ПОВРЕЖДЕН - {status}")
        
        return len(self.missing_scripts) == 0 and len(self.corrupted_scripts) == 0
    
    def generate_report(self):
        """Генерация отчета о целостности"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"data/sfm/integrity_report_{timestamp}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_scripts': len(self.critical_scripts),
            'healthy_scripts': len(self.healthy_scripts),
            'missing_scripts': len(self.missing_scripts),
            'corrupted_scripts': len(self.corrupted_scripts),
            'integrity_status': 'OK' if len(self.missing_scripts) == 0 and len(self.corrupted_scripts) == 0 else 'DEGRADED',
            'healthy_scripts_list': self.healthy_scripts,
            'missing_scripts_list': self.missing_scripts,
            'corrupted_scripts_list': self.corrupted_scripts
        }
        
        try:
            os.makedirs(os.path.dirname(report_file), exist_ok=True)
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Отчет о целостности сохранен: {report_file}")
        except Exception as e:
            print(f"❌ Ошибка сохранения отчета: {e}")
        
        return report
    
    def print_summary(self):
        """Вывод сводки проверки"""
        print("\n📊 СВОДКА ПРОВЕРКИ ЦЕЛОСТНОСТИ")
        print("=" * 50)
        
        total = len(self.critical_scripts)
        healthy = len(self.healthy_scripts)
        missing = len(self.missing_scripts)
        corrupted = len(self.corrupted_scripts)
        
        print(f"Всего скриптов: {total}")
        print(f"Здоровых: {healthy} ({healthy/total*100:.1f}%)")
        print(f"Отсутствующих: {missing} ({missing/total*100:.1f}%)")
        print(f"Поврежденных: {corrupted} ({corrupted/total*100:.1f}%)")
        
        if missing > 0:
            print(f"\n❌ ОТСУТСТВУЮЩИЕ СКРИПТЫ:")
            for script in self.missing_scripts:
                print(f"  - {script}")
        
        if corrupted > 0:
            print(f"\n⚠️  ПОВРЕЖДЕННЫЕ СКРИПТЫ:")
            for script, status in self.corrupted_scripts:
                print(f"  - {script}: {status}")
        
        if missing == 0 and corrupted == 0:
            print("\n🎉 ВСЕ SFM СКРИПТЫ В ПОРЯДКЕ!")
        else:
            print(f"\n⚠️  ОБНАРУЖЕНЫ ПРОБЛЕМЫ С SFM СКРИПТАМИ!")
    
    def suggest_fixes(self):
        """Предложения по исправлению"""
        if len(self.missing_scripts) == 0 and len(self.corrupted_scripts) == 0:
            return
        
        print("\n🔧 ПРЕДЛОЖЕНИЯ ПО ИСПРАВЛЕНИЮ")
        print("=" * 50)
        
        if self.missing_scripts:
            print("Для отсутствующих скриптов:")
            print("1. Проверить, не были ли они случайно удалены")
            print("2. Восстановить из резервной копии")
            print("3. Пересоздать скрипты по документации")
        
        if self.corrupted_scripts:
            print("Для поврежденных скриптов:")
            print("1. Проверить содержимое файлов")
            print("2. Восстановить из резервной копии")
            print("3. Пересоздать поврежденные скрипты")

def main():
    """Главная функция"""
    print("🛡️ SFM INTEGRITY CHECK")
    print("=" * 50)
    
    checker = SFMIntegrityChecker()
    
    # Проверка всех скриптов
    is_healthy = checker.check_all_scripts()
    
    # Вывод сводки
    checker.print_summary()
    
    # Предложения по исправлению
    checker.suggest_fixes()
    
    # Генерация отчета
    checker.generate_report()
    
    if is_healthy:
        print("\n✅ Проверка целостности завершена успешно!")
        sys.exit(0)
    else:
        print("\n❌ Обнаружены проблемы с SFM скриптами!")
        sys.exit(1)

if __name__ == "__main__":
    main()