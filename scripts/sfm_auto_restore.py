#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Auto Restore - Автоматическое восстановление SFM скриптов
Восстанавливает отсутствующие или поврежденные SFM скрипты
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path

class SFMAutoRestore:
    """Автоматическое восстановление SFM скриптов"""
    
    def __init__(self):
        self.scripts_dir = "scripts"
        self.backup_dir = "data/sfm/backups"
        self.restore_log = []
        
        # Шаблоны для восстановления скриптов
        self.script_templates = {
            'sfm_quick_stats.py': self._get_quick_stats_template(),
            'sfm_stats_universal.py': self._get_universal_stats_template(),
            'sfm_add_function.py': self._get_add_function_template(),
            'sfm_fix_and_validate.py': self._get_fix_validate_template(),
            'sfm_manager.py': self._get_manager_template(),
            'sfm_integrity_check.py': self._get_integrity_check_template()
        }
    
    def _get_quick_stats_template(self):
        """Шаблон для sfm_quick_stats.py"""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Quick Stats - Быстрая статистика SFM
"""

import json
import os
from datetime import datetime

def get_sfm_stats():
    """Получение быстрой статистики SFM"""
    try:
        with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        functions = registry.get('functions', {})
        total = len(functions)
        active = sum(1 for f in functions.values() if isinstance(f, dict) and f.get('status') == 'active')
        sleeping = sum(1 for f in functions.values() if isinstance(f, dict) and f.get('status') == 'sleeping')
        critical = sum(1 for f in functions.values() if isinstance(f, dict) and f.get('is_critical', False))
        
        print("📊 АКТУАЛЬНАЯ СТАТИСТИКА SFM")
        print("=" * 40)
        print(f"Обновлено: {registry.get('last_updated', 'unknown')}")
        print()
        print("Параметр                Значение        Процент")
        print("-" * 40)
        print(f"{'Всего функций':<25} {total:<15} 100.0%")
        
        if total > 0:
            print(f"{'Активные':<25} {active:<15} {active/total*100:.1f}%")
            print(f"{'Спящие':<25} {sleeping:<15} {sleeping/total*100:.1f}%")
            print(f"{'Критические':<25} {critical:<15} {critical/total*100:.1f}%")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    get_sfm_stats()
'''
    
    def _get_universal_stats_template(self):
        """Шаблон для sfm_stats_universal.py"""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Universal Statistics - Универсальная статистика SFM
"""

import json
import os
import sys
from datetime import datetime

def find_sfm_registry():
    """Поиск SFM реестра"""
    possible_paths = [
        'data/sfm/function_registry.json',
        '../data/sfm/function_registry.json',
        '../../data/sfm/function_registry.json'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def main():
    """Главная функция"""
    print("🚀 SFM UNIVERSAL STATISTICS")
    print("=" * 50)
    
    registry_path = find_sfm_registry()
    if not registry_path:
        print("❌ SFM реестр не найден!")
        sys.exit(1)
    
    print(f"✅ SFM реестр найден: {registry_path}")
    
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        functions = registry.get('functions', {})
        print(f"📊 Всего функций: {len(functions)}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
'''
    
    def _get_add_function_template(self):
        """Шаблон для sfm_add_function.py"""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Add Function - Добавление функций в SFM реестр
"""

import json
import os
import sys
from datetime import datetime

def add_function_interactive():
    """Интерактивное добавление функции"""
    print("🔧 ДОБАВЛЕНИЕ НОВОЙ ФУНКЦИИ")
    print("=" * 50)
    
    func_data = {
        'function_id': input("Function ID: ").strip(),
        'name': input("Name: ").strip(),
        'description': input("Description: ").strip(),
        'function_type': input("Type (ai_agent/security/bot/manager): ").strip(),
        'status': input("Status (active/sleeping): ").strip(),
        'is_critical': input("Critical? (y/N): ").strip().lower() == 'y',
        'created_at': datetime.now().isoformat()
    }
    
    try:
        with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        if 'functions' not in registry:
            registry['functions'] = {}
        
        registry['functions'][func_data['function_id']] = func_data
        
        with open('data/sfm/function_registry.json', 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        print("✅ Функция успешно добавлена!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    add_function_interactive()
'''
    
    def _get_fix_validate_template(self):
        """Шаблон для sfm_fix_and_validate.py"""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Fix and Validate - Валидация и исправление SFM
"""

import json
import os
from datetime import datetime

def validate_and_fix():
    """Валидация и исправление SFM реестра"""
    print("🔧 ВАЛИДАЦИЯ И ИСПРАВЛЕНИЕ SFM")
    print("=" * 50)
    
    try:
        with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        functions = registry.get('functions', {})
        print(f"✅ Найдено функций: {len(functions)}")
        
        # Обновление статистики
        stats = {
            'total_functions': len(functions),
            'active_functions': sum(1 for f in functions.values() if isinstance(f, dict) and f.get('status') == 'active'),
            'sleeping_functions': sum(1 for f in functions.values() if isinstance(f, dict) and f.get('status') == 'sleeping'),
            'critical_functions': sum(1 for f in functions.values() if isinstance(f, dict) and f.get('is_critical', False))
        }
        
        registry['statistics'] = stats
        registry['last_updated'] = datetime.now().isoformat()
        
        with open('data/sfm/function_registry.json', 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        print("✅ SFM реестр исправлен и обновлен!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    validate_and_fix()
'''
    
    def _get_manager_template(self):
        """Шаблон для sfm_manager.py"""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Manager - Главный менеджер SFM
"""

import os
import sys
import subprocess

def run_command(command):
    """Запуск команды"""
    try:
        result = subprocess.run([sys.executable, f"scripts/{command}"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Главная функция"""
    print("🚀 SFM MANAGER")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Использование: python3 scripts/sfm_manager.py <command>")
        print("Доступные команды: stats, validate, fix, add")
        return
    
    command = sys.argv[1]
    
    if command == 'stats':
        run_command('sfm_quick_stats.py')
    elif command == 'validate':
        print("🔍 Валидация SFM...")
        # Простая валидация
        try:
            import json
            with open('data/sfm/function_registry.json', 'r') as f:
                json.load(f)
            print("✅ SFM реестр корректен")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    elif command == 'fix':
        run_command('sfm_fix_and_validate.py')
    elif command == 'add':
        run_command('sfm_add_function.py')
    else:
        print(f"❌ Неизвестная команда: {command}")

if __name__ == "__main__":
    main()
'''
    
    def _get_integrity_check_template(self):
        """Шаблон для sfm_integrity_check.py"""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Integrity Check - Проверка целостности SFM скриптов
"""

import os
from datetime import datetime

def check_sfm_scripts():
    """Проверка SFM скриптов"""
    print("🔍 ПРОВЕРКА SFM СКРИПТОВ")
    print("=" * 50)
    
    required_scripts = [
        'sfm_quick_stats.py',
        'sfm_analyzer.py',
        'sfm_add_function.py',
        'sfm_fix_and_validate.py',
        'sfm_manager.py'
    ]
    
    missing = []
    present = []
    
    for script in required_scripts:
        if os.path.exists(f"scripts/{script}"):
            present.append(script)
            print(f"✅ {script}")
        else:
            missing.append(script)
            print(f"❌ {script}")
    
    print(f"\\nВсего: {len(required_scripts)}")
    print(f"Найдено: {len(present)}")
    print(f"Отсутствует: {len(missing)}")
    
    if missing:
        print("\\n⚠️  Обнаружены отсутствующие скрипты!")
        return False
    else:
        print("\\n🎉 Все SFM скрипты на месте!")
        return True

if __name__ == "__main__":
    check_sfm_scripts()
'''
    
    def restore_script(self, script_name):
        """Восстановление конкретного скрипта"""
        if script_name not in self.script_templates:
            print(f"❌ Шаблон для {script_name} не найден")
            return False
        
        script_path = os.path.join(self.scripts_dir, script_name)
        
        try:
            # Создание директории, если не существует
            os.makedirs(self.scripts_dir, exist_ok=True)
            
            # Запись скрипта
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(self.script_templates[script_name])
            
            # Установка прав на выполнение
            os.chmod(script_path, 0o755)
            
            self.restore_log.append(f"✅ {script_name} восстановлен")
            print(f"✅ {script_name} восстановлен")
            return True
            
        except Exception as e:
            self.restore_log.append(f"❌ {script_name}: ошибка - {e}")
            print(f"❌ {script_name}: ошибка - {e}")
            return False
    
    def restore_all_missing_scripts(self):
        """Восстановление всех отсутствующих скриптов"""
        print("🔄 ВОССТАНОВЛЕНИЕ SFM СКРИПТОВ")
        print("=" * 50)
        
        restored_count = 0
        
        for script_name in self.script_templates:
            script_path = os.path.join(self.scripts_dir, script_name)
            
            if not os.path.exists(script_path):
                if self.restore_script(script_name):
                    restored_count += 1
            else:
                print(f"✅ {script_name} уже существует")
        
        print(f"\\n📊 Восстановлено скриптов: {restored_count}")
        return restored_count > 0
    
    def create_backup(self):
        """Создание резервной копии перед восстановлением"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{self.backup_dir}/sfm_scripts_backup_{timestamp}"
        
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            shutil.copytree(self.scripts_dir, backup_path)
            print(f"✅ Резервная копия создана: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"⚠️  Не удалось создать резервную копию: {e}")
            return None
    
    def generate_restore_report(self):
        """Генерация отчета о восстановлении"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"data/sfm/restore_report_{timestamp}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'restore_log': self.restore_log,
            'total_restored': len([log for log in self.restore_log if log.startswith('✅')]),
            'total_errors': len([log for log in self.restore_log if log.startswith('❌')])
        }
        
        try:
            os.makedirs(os.path.dirname(report_file), exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"✅ Отчет о восстановлении сохранен: {report_file}")
        except Exception as e:
            print(f"❌ Ошибка сохранения отчета: {e}")

def main():
    """Главная функция"""
    print("🔄 SFM AUTO RESTORE")
    print("=" * 50)
    
    restorer = SFMAutoRestore()
    
    # Создание резервной копии
    restorer.create_backup()
    
    # Восстановление скриптов
    restored = restorer.restore_all_missing_scripts()
    
    # Генерация отчета
    restorer.generate_restore_report()
    
    if restored:
        print("\\n🎉 Восстановление завершено!")
    else:
        print("\\n✅ Все скрипты уже на месте!")

if __name__ == "__main__":
    main()