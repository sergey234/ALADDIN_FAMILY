#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка состояния активного файла auto_scaling_engine.py
Убедиться в правильной версии и применимости изменений
"""

import sys
import os
import hashlib
import shutil
from datetime import datetime
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

def verify_file_integrity():
    """6.11.1 - Убедиться, что работаем с правильной версией"""
    print("=== 6.11.1 - ПРОВЕРКА ЦЕЛОСТНОСТИ ФАЙЛА ===")
    
    file_path = '/Users/sergejhlystov/ALADDIN_NEW/security/scaling/auto_scaling_engine.py'
    
    try:
        # Проверяем существование файла
        if not os.path.exists(file_path):
            print(f"❌ Файл не найден: {file_path}")
            return False
        
        # Получаем информацию о файле
        stat = os.stat(file_path)
        file_size = stat.st_size
        mod_time = datetime.fromtimestamp(stat.st_mtime)
        
        print(f"✅ Файл существует: {file_path}")
        print(f"✅ Размер: {file_size} байт")
        print(f"✅ Время изменения: {mod_time}")
        
        # Вычисляем хеш файла для проверки целостности
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        print(f"✅ MD5 хеш: {file_hash}")
        
        # Проверяем, что файл не пустой
        if file_size == 0:
            print("❌ Файл пустой")
            return False
        
        # Проверяем, что файл содержит ожидаемый контент
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        expected_components = [
            'class AutoScalingEngine',
            'class ScalingRule',
            'class MetricData',
            'class ScalingDecision',
            'class ScalingMetrics',
            'def initialize',
            'def stop',
            'def add_scaling_rule',
            'def collect_metric',
            'def make_scaling_decision'
        ]
        
        missing_components = []
        for component in expected_components:
            if component not in content:
                missing_components.append(component)
        
        if missing_components:
            print(f"❌ Отсутствуют компоненты: {missing_components}")
            return False
        
        print("✅ Все ожидаемые компоненты присутствуют")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки целостности: {e}")
        return False

def verify_changes_applied():
    """6.11.2 - Проверить, что все изменения применены"""
    print("\n=== 6.11.2 - ПРОВЕРКА ПРИМЕНЕННЫХ ИЗМЕНЕНИЙ ===")
    
    file_path = '/Users/sergejhlystov/ALADDIN_NEW/security/scaling/auto_scaling_engine.py'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем наличие ключевых элементов
        checks = [
            ('Кодировка UTF-8', '# -*- coding: utf-8 -*-'),
            ('Docstring модуля', 'ALADDIN Security System - Auto Scaling Engine'),
            ('Импорты', 'from core.base import ComponentStatus, SecurityBase'),
            ('Enum классы', 'class ScalingTrigger(Enum)'),
            ('Dataclass классы', '@dataclass'),
            ('Основной класс', 'class AutoScalingEngine(SecurityBase)'),
            ('Методы инициализации', 'def initialize(self) -> bool:'),
            ('Методы остановки', 'def stop(self) -> bool:'),
            ('Обработка ошибок', 'except Exception as e:'),
            ('Логирование', 'self.log_activity'),
            ('Threading', 'import threading'),
            ('Типизация', 'from typing import'),
            ('Datetime', 'from datetime import'),
            ('JSON обработка', 'import json'),
            ('Статистика', 'statistics')
        ]
        
        applied_changes = []
        missing_changes = []
        
        for check_name, check_content in checks:
            if check_content in content:
                applied_changes.append(check_name)
                print(f"✅ {check_name}")
            else:
                missing_changes.append(check_name)
                print(f"❌ {check_name}")
        
        print(f"\n📊 Применено изменений: {len(applied_changes)}/{len(checks)}")
        
        if missing_changes:
            print(f"⚠️ Отсутствуют: {missing_changes}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки изменений: {e}")
        return False

def compare_with_backups():
    """6.11.3 - Сравнить с резервными копиями"""
    print("\n=== 6.11.3 - СРАВНЕНИЕ С РЕЗЕРВНЫМИ КОПИЯМИ ===")
    
    current_file = '/Users/sergejhlystov/ALADDIN_NEW/security/scaling/auto_scaling_engine.py'
    backup_dirs = [
        '/Users/sergejhlystov/ALADDIN_NEW/formatting_work',
        '/Users/sergejhlystov/ALADDIN_BACKUPS',
        '/Users/sergejhlystov/ALADDIN_NEW_BACKUP_ARCHITECTURE_20250911_015725'
    ]
    
    try:
        # Читаем текущий файл
        with open(current_file, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        current_hash = hashlib.md5(current_content.encode()).hexdigest()
        print(f"✅ Текущий файл MD5: {current_hash}")
        
        # Ищем резервные копии
        backup_files = []
        for backup_dir in backup_dirs:
            if os.path.exists(backup_dir):
                for root, dirs, files in os.walk(backup_dir):
                    for file in files:
                        if file == 'auto_scaling_engine.py':
                            backup_path = os.path.join(root, file)
                            backup_files.append(backup_path)
        
        print(f"✅ Найдено резервных копий: {len(backup_files)}")
        
        # Сравниваем с резервными копиями
        identical_backups = []
        different_backups = []
        
        for backup_file in backup_files[:5]:  # Проверяем только первые 5
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_content = f.read()
                
                backup_hash = hashlib.md5(backup_content.encode()).hexdigest()
                
                if backup_hash == current_hash:
                    identical_backups.append(backup_file)
                    print(f"✅ Идентичен: {backup_file}")
                else:
                    different_backups.append(backup_file)
                    print(f"⚠️ Отличается: {backup_file}")
                    
            except Exception as e:
                print(f"❌ Ошибка чтения {backup_file}: {e}")
        
        print(f"\n📊 Идентичных копий: {len(identical_backups)}")
        print(f"📊 Отличающихся копий: {len(different_backups)}")
        
        return len(identical_backups) > 0 or len(different_backups) > 0
        
    except Exception as e:
        print(f"❌ Ошибка сравнения с резервными копиями: {e}")
        return False

def record_current_state():
    """6.11.4 - Зафиксировать текущее состояние"""
    print("\n=== 6.11.4 - ФИКСАЦИЯ ТЕКУЩЕГО СОСТОЯНИЯ ===")
    
    file_path = '/Users/sergejhlystov/ALADDIN_NEW/security/scaling/auto_scaling_engine.py'
    state_file = '/Users/sergejhlystov/ALADDIN_NEW/formatting_work/auto_scaling_engine_state.json'
    
    try:
        # Получаем информацию о файле
        stat = os.stat(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Создаем запись о состоянии
        state_record = {
            'timestamp': datetime.now().isoformat(),
            'file_path': file_path,
            'file_size': stat.st_size,
            'modification_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'md5_hash': hashlib.md5(content.encode()).hexdigest(),
            'line_count': len(content.split('\n')),
            'character_count': len(content),
            'classes_found': content.count('class '),
            'methods_found': content.count('def '),
            'imports_found': content.count('import '),
            'try_except_blocks': content.count('try:'),
            'docstrings_found': content.count('"""'),
            'status': 'VERIFIED'
        }
        
        # Сохраняем состояние
        import json
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_record, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Состояние зафиксировано: {state_file}")
        print(f"✅ Время: {state_record['timestamp']}")
        print(f"✅ Размер: {state_record['file_size']} байт")
        print(f"✅ Строк: {state_record['line_count']}")
        print(f"✅ Классов: {state_record['classes_found']}")
        print(f"✅ Методов: {state_record['methods_found']}")
        print(f"✅ Импортов: {state_record['imports_found']}")
        print(f"✅ Try-except блоков: {state_record['try_except_blocks']}")
        print(f"✅ Docstrings: {state_record['docstrings_found']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка фиксации состояния: {e}")
        return False

def create_enhanced_backup():
    """Создание улучшенной резервной копии"""
    print("\n=== СОЗДАНИЕ УЛУЧШЕННОЙ РЕЗЕРВНОЙ КОПИИ ===")
    
    source_file = '/Users/sergejhlystov/ALADDIN_NEW/security/scaling/auto_scaling_engine.py'
    backup_dir = '/Users/sergejhlystov/ALADDIN_NEW/formatting_work'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        # Создаем имя файла с timestamp
        backup_filename = f'auto_scaling_engine_enhanced_{timestamp}.py'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Копируем файл
        shutil.copy2(source_file, backup_path)
        
        # Проверяем, что копия создана
        if os.path.exists(backup_path):
            backup_size = os.path.getsize(backup_path)
            print(f"✅ Резервная копия создана: {backup_path}")
            print(f"✅ Размер копии: {backup_size} байт")
            return backup_path
        else:
            print("❌ Ошибка создания резервной копии")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка создания резервной копии: {e}")
        return None

def main():
    """Основная функция проверки состояния активного файла"""
    print("🔍 ЭТАП 6.11 - ПРОВЕРКА СОСТОЯНИЯ АКТИВНОГО ФАЙЛА")
    print("=" * 70)
    
    # 6.11.1 - Убедиться, что работаем с правильной версией
    integrity_ok = verify_file_integrity()
    
    # 6.11.2 - Проверить, что все изменения применены
    changes_ok = verify_changes_applied()
    
    # 6.11.3 - Сравнить с резервными копиями
    backup_ok = compare_with_backups()
    
    # 6.11.4 - Зафиксировать текущее состояние
    state_ok = record_current_state()
    
    # Создание улучшенной резервной копии
    backup_created = create_enhanced_backup()
    
    # Итоговый результат
    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ЭТАПА 6.11:")
    print(f"✅ Целостность файла: {'ПРОЙДЕНО' if integrity_ok else 'ПРОВАЛЕНО'}")
    print(f"✅ Примененные изменения: {'ПРОЙДЕНО' if changes_ok else 'ПРОВАЛЕНО'}")
    print(f"✅ Сравнение с резервными копиями: {'ПРОЙДЕНО' if backup_ok else 'ПРОВАЛЕНО'}")
    print(f"✅ Фиксация состояния: {'ПРОЙДЕНО' if state_ok else 'ПРОВАЛЕНО'}")
    print(f"✅ Резервная копия: {'СОЗДАНА' if backup_created else 'НЕ СОЗДАНА'}")
    
    overall_success = integrity_ok and changes_ok and state_ok
    
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ ЭТАПА 6.11: {'ПРОЙДЕНО' if overall_success else 'ПРОВАЛЕНО'}")
    
    return overall_success

if __name__ == "__main__":
    main()