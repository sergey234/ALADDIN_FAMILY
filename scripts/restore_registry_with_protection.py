#!/usr/bin/env python3
"""
Registry Restore with Protection
Восстановление реестра с защитой от перезаписи SFM
"""

import json
import os
import shutil
from datetime import datetime


class RegistryRestorer:
    """Восстановление реестра с защитой"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.registry_path = "data/sfm/function_registry.json"
        self.merged_registry_path = "data/sfm/function_registry.json.backup_20250918_101310"
        self.protection_file = "data/sfm/.registry_protected"
        
    def create_protection(self):
        """Создание защиты от перезаписи"""
        try:
            print("🛡️  Создание защиты от перезаписи...")
            
            # Создаем файл защиты
            with open(self.protection_file, 'w') as f:
                f.write(f"Registry protected at {datetime.now().isoformat()}\n")
                f.write("DO NOT DELETE - Prevents SFM from overwriting merged registry\n")
            
            print("✅ Защита создана")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания защиты: {e}")
            return False
    
    def restore_merged_registry(self):
        """Восстановление объединенного реестра"""
        try:
            print("🔄 Восстановление объединенного реестра...")
            
            # Проверяем наличие объединенного реестра
            if not os.path.exists(self.merged_registry_path):
                print(f"❌ Объединенный реестр не найден: {self.merged_registry_path}")
                return False
            
            # Создаем резервную копию текущего реестра
            if os.path.exists(self.registry_path):
                backup_path = f"{self.registry_path}.backup_{self.timestamp}"
                shutil.copy2(self.registry_path, backup_path)
                print(f"✅ Резервная копия: {backup_path}")
            
            # Восстанавливаем объединенный реестр
            shutil.copy2(self.merged_registry_path, self.registry_path)
            print("✅ Объединенный реестр восстановлен")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка восстановления: {e}")
            return False
    
    def verify_registry(self):
        """Проверка восстановленного реестра"""
        try:
            print("🔍 Проверка восстановленного реестра...")
            
            with open(self.registry_path, 'r') as f:
                registry = json.load(f)
            
            print(f"📊 Версия: {registry.get('version', 'неизвестно')}")
            print(f"📊 Всего функций: {len(registry.get('functions', {}))}")
            
            if 'statistics' in registry:
                stats = registry['statistics']
                print(f"📈 Статистика:")
                print(f"  Активных: {stats.get('active_functions', 0)}")
                print(f"  Спящих: {stats.get('sleeping_functions', 0)}")
                print(f"  Критических: {stats.get('critical_functions', 0)}")
            
            # Проверяем, что реестр содержит ожидаемые функции
            functions = registry.get('functions', {})
            expected_functions = ['anti_fraud_master_ai', 'threat_detection_agent', 'advanced_monitoring_manager']
            
            found_expected = 0
            for func_id in expected_functions:
                if func_id in functions:
                    found_expected += 1
                    print(f"✅ Найдена функция: {func_id}")
                else:
                    print(f"❌ Не найдена функция: {func_id}")
            
            if found_expected == len(expected_functions):
                print("✅ Все ожидаемые функции найдены")
                return True
            else:
                print(f"⚠️  Найдено только {found_expected}/{len(expected_functions)} ожидаемых функций")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка проверки: {e}")
            return False
    
    def create_sfm_wrapper(self):
        """Создание обертки для SFM с защитой реестра"""
        try:
            print("🔧 Создание обертки SFM с защитой...")
            
            wrapper_code = '''#!/usr/bin/env python3
"""
SFM Wrapper with Registry Protection
Обертка SFM с защитой реестра от перезаписи
"""

import os
import json
from datetime import datetime

class SFMRegistryProtector:
    """Защита реестра от перезаписи SFM"""
    
    def __init__(self):
        self.registry_path = "data/sfm/function_registry.json"
        self.protection_file = "data/sfm/.registry_protected"
        self.backup_dir = "data/sfm/backups"
        
    def is_protected(self):
        """Проверка защиты реестра"""
        return os.path.exists(self.protection_file)
    
    def backup_registry(self):
        """Создание резервной копии реестра"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"registry_backup_{timestamp}.json")
        
        if os.path.exists(self.registry_path):
            import shutil
            shutil.copy2(self.registry_path, backup_path)
            return backup_path
        return None
    
    def protect_registry(self):
        """Защита реестра от перезаписи"""
        if self.is_protected():
            print("🛡️  Реестр уже защищен")
            return True
        
        # Создаем файл защиты
        with open(self.protection_file, 'w') as f:
            f.write(f"Registry protected at {datetime.now().isoformat()}\\n")
            f.write("DO NOT DELETE - Prevents SFM from overwriting merged registry\\n")
        
        print("✅ Реестр защищен от перезаписи")
        return True
    
    def restore_registry_if_needed(self):
        """Восстановление реестра при необходимости"""
        if not os.path.exists(self.registry_path):
            print("⚠️  Реестр не найден, восстановление невозможно")
            return False
        
        # Проверяем размер реестра
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        functions_count = len(registry.get('functions', {}))
        
        if functions_count < 100:  # Если меньше 100 функций, возможно реестр был перезаписан
            print(f"⚠️  Обнаружено мало функций ({functions_count}), возможно реестр был перезаписан")
            
            # Ищем последнюю резервную копию
            if os.path.exists(self.backup_dir):
                backup_files = [f for f in os.listdir(self.backup_dir) if f.startswith('registry_backup_')]
                if backup_files:
                    latest_backup = max(backup_files)
                    backup_path = os.path.join(self.backup_dir, latest_backup)
                    
                    print(f"🔄 Восстанавливаем из резервной копии: {latest_backup}")
                    import shutil
                    shutil.copy2(backup_path, self.registry_path)
                    return True
        
        return True

# Глобальный экземпляр защитника
registry_protector = SFMRegistryProtector()

# Защищаем реестр при импорте
registry_protector.protect_registry()
registry_protector.restore_registry_if_needed()
'''
            
            wrapper_path = "security/sfm_registry_protector.py"
            with open(wrapper_path, 'w') as f:
                f.write(wrapper_code)
            
            print(f"✅ Обертка создана: {wrapper_path}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания обертки: {e}")
            return False
    
    def run_restore(self):
        """Запуск восстановления с защитой"""
        try:
            print("🚀 ВОССТАНОВЛЕНИЕ РЕЕСТРА С ЗАЩИТОЙ")
            print("=" * 50)
            
            # 1. Создание защиты
            if not self.create_protection():
                return False
            
            # 2. Восстановление реестра
            if not self.restore_merged_registry():
                return False
            
            # 3. Проверка реестра
            if not self.verify_registry():
                return False
            
            # 4. Создание обертки SFM
            if not self.create_sfm_wrapper():
                return False
            
            print("=" * 50)
            print("✅ ВОССТАНОВЛЕНИЕ С ЗАЩИТОЙ ЗАВЕРШЕНО УСПЕШНО!")
            print("🛡️  Реестр защищен от перезаписи SFM")
            return True
            
        except Exception as e:
            print(f"❌ Критическая ошибка восстановления: {e}")
            return False


if __name__ == "__main__":
    restorer = RegistryRestorer()
    success = restorer.run_restore()
    
    if success:
        print("\n🎉 РЕЕСТР ВОССТАНОВЛЕН И ЗАЩИЩЕН!")
        exit(0)
    else:
        print("\n💥 ВОССТАНОВЛЕНИЕ ЗАВЕРШИЛОСЬ С ОШИБКАМИ!")
        exit(1)