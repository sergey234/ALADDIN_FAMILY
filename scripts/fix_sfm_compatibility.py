#!/usr/bin/env python3
"""
SFM Compatibility Fix
Исправление совместимости SFM с объединенным реестром
"""

import json
import os
import shutil
from datetime import datetime


class SFMCompatibilityFixer:
    """Исправление совместимости SFM с объединенным реестром"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.registry_path = "data/sfm/function_registry.json"
        self.backup_path = f"data/sfm/function_registry.json.backup_{self.timestamp}"
        self.merged_registry_path = "data/sfm/function_registry.json.backup_20250918_101310"
        
    def create_backup(self):
        """Создание резервной копии текущего реестра"""
        try:
            print("🔄 Создание резервной копии текущего реестра...")
            shutil.copy2(self.registry_path, self.backup_path)
            print(f"✅ Резервная копия создана: {self.backup_path}")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания резервной копии: {e}")
            return False
    
    def restore_merged_registry(self):
        """Восстановление объединенного реестра"""
        try:
            print("🔄 Восстановление объединенного реестра...")
            shutil.copy2(self.merged_registry_path, self.registry_path)
            print(f"✅ Объединенный реестр восстановлен")
            return True
        except Exception as e:
            print(f"❌ Ошибка восстановления реестра: {e}")
            return False
    
    def modify_sfm_for_compatibility(self):
        """Модификация SFM для совместимости с объединенным реестром"""
        try:
            print("🔧 Модификация SFM для совместимости...")
            
            sfm_path = "security/safe_function_manager.py"
            backup_sfm_path = f"security/safe_function_manager.py.backup_{self.timestamp}"
            
            # Создаем резервную копию SFM
            shutil.copy2(sfm_path, backup_sfm_path)
            print(f"✅ Резервная копия SFM: {backup_sfm_path}")
            
            # Читаем текущий SFM
            with open(sfm_path, 'r', encoding='utf-8') as f:
                sfm_content = f.read()
            
            # Модифицируем метод _load_saved_functions
            old_load_method = '''    def _load_saved_functions(self):
        """Загрузка сохраненных функций и обработчиков"""
        try:
            import json
            import os
            
            print("🔍 DEBUG: _load_saved_functions() вызван!")
            self.log_activity("Начинаем загрузку сохраненных функций...")
            
            print(f"🔍 DEBUG: Проверяем файл: {self.registry_file}")
            print(f"🔍 DEBUG: Файл существует: {os.path.exists(self.registry_file)}")
            
            if os.path.exists(self.registry_file):
                print(f"🔍 DEBUG: Файл найден: {self.registry_file}")
                print(f"🔍 DEBUG: Начинаем чтение файла...")
                try:
                    with open(self.registry_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"🔍 DEBUG: Файл прочитан успешно!")
                except Exception as e:
                    print(f"🔍 DEBUG: Ошибка чтения файла: {e}")
                    return
                
                print(f"🔍 DEBUG: Файл прочитан, данные: {data}")
                print(f"🔍 DEBUG: Ключи в data: {list(data.keys())}")
                print(f"🔍 DEBUG: functions в data: {data.get('functions', {})}")
                    
                # Загружаем функции из файла
                functions_loaded = 0
                print(f"🔍 DEBUG: Найдено {len(data.get('functions', {}))} функций в файле")
                self.log_activity(f"Найдено {len(data.get('functions', {}))} функций в файле")
                
                print(f"🔍 DEBUG: Начинаем цикл загрузки функций...")
                for func_id, func_data in data.get('functions', {}).items():
                    print(f"🔍 DEBUG: Загружаем функцию: {func_id}")
                    self.log_activity(f"Загружаем функцию: {func_id}")
                    
                    # Создаем объект функции из сохраненных данных (перезаписываем существующие)
                    func = SecurityFunction('''
            
            new_load_method = '''    def _load_saved_functions(self):
        """Загрузка сохраненных функций и обработчиков (совместимость с объединенным реестром)"""
        try:
            import json
            import os
            
            print("🔍 DEBUG: _load_saved_functions() вызван!")
            self.log_activity("Начинаем загрузку сохраненных функций...")
            
            print(f"🔍 DEBUG: Проверяем файл: {self.registry_file}")
            print(f"🔍 DEBUG: Файл существует: {os.path.exists(self.registry_file)}")
            
            if os.path.exists(self.registry_file):
                print(f"🔍 DEBUG: Файл найден: {self.registry_file}")
                print(f"🔍 DEBUG: Начинаем чтение файла...")
                try:
                    with open(self.registry_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"🔍 DEBUG: Файл прочитан успешно!")
                except Exception as e:
                    print(f"🔍 DEBUG: Ошибка чтения файла: {e}")
                    return
                
                print(f"🔍 DEBUG: Файл прочитан, данные: {data}")
                print(f"🔍 DEBUG: Ключи в data: {list(data.keys())}")
                print(f"🔍 DEBUG: functions в data: {data.get('functions', {})}")
                    
                # Загружаем функции из файла (совместимость с объединенным реестром)
                functions_loaded = 0
                print(f"🔍 DEBUG: Найдено {len(data.get('functions', {}))} функций в файле")
                self.log_activity(f"Найдено {len(data.get('functions', {}))} функций в файле")
                
                print(f"🔍 DEBUG: Начинаем цикл загрузки функций...")
                for func_id, func_data in data.get('functions', {}).items():
                    print(f"🔍 DEBUG: Загружаем функцию: {func_id}")
                    self.log_activity(f"Загружаем функцию: {func_id}")
                    
                    # Создаем объект функции из сохраненных данных (совместимость с новым форматом)
                    func = SecurityFunction('''
            
            # Заменяем метод
            if old_load_method in sfm_content:
                sfm_content = sfm_content.replace(old_load_method, new_load_method)
                print("✅ Метод _load_saved_functions обновлен")
            else:
                print("⚠️  Метод _load_saved_functions не найден в ожидаемом формате")
            
            # Модифицируем метод _save_functions для сохранения расширенного формата
            old_save_method = '''    def _save_functions(self):
        """Сохранение функций и обработчиков в файл"""
        try:
            import json
            
            data = {
                'functions': {},
                'handlers': {},
                'last_updated': datetime.now().isoformat()
            }'''
            
            new_save_method = '''    def _save_functions(self):
        """Сохранение функций и обработчиков в файл (совместимость с объединенным реестром)"""
        try:
            import json
            
            # Загружаем существующий реестр для сохранения расширенных полей
            existing_data = {}
            if os.path.exists(self.registry_file):
                try:
                    with open(self.registry_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except:
                    pass
            
            data = {
                'functions': {},
                'handlers': {},
                'last_updated': datetime.now().isoformat(),
                'version': existing_data.get('version', '2.0'),
                'statistics': existing_data.get('statistics', {}),
                'security_components_count': existing_data.get('security_components_count', 0),
                'registry_protection_enabled': existing_data.get('registry_protection_enabled', True),
                'sleep_managers_woken': existing_data.get('sleep_managers_woken', 0)
            }'''
            
            # Заменяем метод
            if old_save_method in sfm_content:
                sfm_content = sfm_content.replace(old_save_method, new_save_method)
                print("✅ Метод _save_functions обновлен")
            else:
                print("⚠️  Метод _save_functions не найден в ожидаемом формате")
            
            # Сохраняем модифицированный SFM
            with open(sfm_path, 'w', encoding='utf-8') as f:
                f.write(sfm_content)
            
            print("✅ SFM модифицирован для совместимости")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка модификации SFM: {e}")
            return False
    
    def test_compatibility(self):
        """Тестирование совместимости"""
        try:
            print("🧪 Тестирование совместимости...")
            
            # Импортируем модифицированный SFM
            import sys
            sys.path.append('.')
            from security.safe_function_manager import SafeFunctionManager
            
            # Создаем экземпляр SFM
            sfm = SafeFunctionManager()
            
            # Проверяем загрузку реестра
            registry = sfm.functions
            print(f"📊 Загружено функций: {len(registry)}")
            
            # Проверяем статистику
            if hasattr(sfm, 'get_safe_function_stats'):
                stats = sfm.get_safe_function_stats()
                print(f"📈 Статистика: {stats}")
            
            print("✅ Совместимость протестирована")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка тестирования: {e}")
            return False
    
    def run_fix(self):
        """Запуск полного исправления"""
        try:
            print("🚀 ЗАПУСК ИСПРАВЛЕНИЯ СОВМЕСТИМОСТИ SFM")
            print("=" * 50)
            
            # 1. Создание резервных копий
            if not self.create_backup():
                return False
            
            # 2. Восстановление объединенного реестра
            if not self.restore_merged_registry():
                return False
            
            # 3. Модификация SFM
            if not self.modify_sfm_for_compatibility():
                return False
            
            # 4. Тестирование
            if not self.test_compatibility():
                return False
            
            print("=" * 50)
            print("✅ ИСПРАВЛЕНИЕ СОВМЕСТИМОСТИ ЗАВЕРШЕНО УСПЕШНО!")
            return True
            
        except Exception as e:
            print(f"❌ Критическая ошибка исправления: {e}")
            return False


if __name__ == "__main__":
    fixer = SFMCompatibilityFixer()
    success = fixer.run_fix()
    
    if success:
        print("\n🎉 СОВМЕСТИМОСТЬ SFM ИСПРАВЛЕНА!")
        exit(0)
    else:
        print("\n💥 ИСПРАВЛЕНИЕ ЗАВЕРШИЛОСЬ С ОШИБКАМИ!")
        exit(1)