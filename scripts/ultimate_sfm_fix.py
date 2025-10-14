#!/usr/bin/env python3
"""
Ultimate SFM Fix
ОКОНЧАТЕЛЬНОЕ решение проблемы SFM с реестром
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List


class UltimateSFMFix:
    """ОКОНЧАТЕЛЬНОЕ решение проблемы SFM"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.registry_path = "data/sfm/function_registry.json"
        self.sleep_states_dir = "data/sleep_states"
        self.original_merged_path = "data/sfm/function_registry.json.backup_20250918_101310"
        self.backup_dir = f"backups/ultimate_sfm_fix_backup_{self.timestamp}"
        
    def create_backup(self) -> bool:
        """Создание бэкапа"""
        try:
            print("🔄 Создание бэкапа...")
            os.makedirs(self.backup_dir, exist_ok=True)
            
            if os.path.exists(self.registry_path):
                shutil.copy2(self.registry_path, f"{self.backup_dir}/function_registry.json")
                print(f"  ✅ Бэкап реестра: {self.backup_dir}/function_registry.json")
            
            print(f"✅ Бэкап создан: {self.backup_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания бэкапа: {e}")
            return False
    
    def load_complete_registry(self) -> Dict[str, Any]:
        """Загрузка полного реестра из всех источников"""
        try:
            print("🔄 Загрузка полного реестра...")
            
            # Загружаем активные функции из оригинального реестра
            with open(self.original_merged_path, 'r') as f:
                original_registry = json.load(f)
            
            active_functions = {}
            for func_id, func_data in original_registry.get('functions', {}).items():
                status = func_data.get('status', 'unknown')
                if status in ['active', 'enabled', 'running']:
                    active_functions[func_id] = func_data
                    print(f"  ✅ Активная функция: {func_id}")
            
            print(f"  📊 Активных функций: {len(active_functions)}")
            
            # Загружаем спящие функции
            import glob
            sleeping_functions = {}
            sleep_files = glob.glob(f"{self.sleep_states_dir}/*_state.json")
            
            for sleep_file in sleep_files:
                try:
                    with open(sleep_file, 'r') as f:
                        sleep_data = json.load(f)
                    
                    func_id = sleep_data["function_id"]
                    function_name = sleep_data["function_name"]
                    
                    sleeping_functions[func_id] = {
                        "function_id": func_id,
                        "name": function_name,
                        "description": f"Спящая функция {function_name}",
                        "function_type": self._determine_function_type(function_name),
                        "security_level": sleep_data["security_level"],
                        "status": "sleeping",
                        "created_at": sleep_data["sleep_time"],
                        "is_critical": sleep_data["is_critical"],
                        "auto_enable": False,
                        "wake_time": sleep_data["sleep_time"],
                        "emergency_wake_up": sleep_data["is_critical"],
                        "features": [],
                        "dependencies": [],
                        "file_path": self._determine_file_path(function_name),
                        "class_name": function_name,
                        "global_instance": f"{function_name.lower()}_instance",
                        "execution_count": 0,
                        "success_count": 0,
                        "error_count": 0,
                        "sleep_state": {
                            "sleep_time": sleep_data["sleep_time"],
                            "previous_status": sleep_data["previous_status"],
                            "minimal_system_sleep": sleep_data.get("minimal_system_sleep", False)
                        }
                    }
                    
                except Exception as e:
                    print(f"  ⚠️  Ошибка загрузки {sleep_file}: {e}")
                    continue
            
            print(f"  📊 Спящих функций: {len(sleeping_functions)}")
            
            # Объединяем все функции
            all_functions = {**active_functions, **sleeping_functions}
            print(f"  📊 Всего функций: {len(all_functions)}")
            
            return all_functions
            
        except Exception as e:
            print(f"❌ Ошибка загрузки реестра: {e}")
            return {}
    
    def _determine_function_type(self, function_name: str) -> str:
        """Определение типа функции"""
        name_lower = function_name.lower()
        
        if "bot" in name_lower:
            return "bot"
        elif "agent" in name_lower:
            return "ai_agent"
        elif "manager" in name_lower:
            return "manager"
        elif "service" in name_lower:
            return "service"
        elif "security" in name_lower:
            return "security"
        else:
            return "unknown"
    
    def _determine_file_path(self, function_name: str) -> str:
        """Определение пути к файлу"""
        name_lower = function_name.lower()
        
        if "bot" in name_lower:
            return f"bots/{name_lower}.py"
        elif "agent" in name_lower:
            return f"ai_agents/{name_lower}.py"
        elif "manager" in name_lower:
            return f"managers/{name_lower}.py"
        elif "service" in name_lower:
            return f"services/{name_lower}.py"
        else:
            return f"security/{name_lower}.py"
    
    def create_ultimate_registry(self, all_functions: Dict[str, Any]) -> Dict[str, Any]:
        """Создание окончательного реестра"""
        try:
            print("🔄 Создание окончательного реестра...")
            
            # Создаем полный реестр
            registry = {
                "version": "2.0",
                "last_updated": datetime.now().isoformat(),
                "functions": all_functions,
                "handlers": {},
                "statistics": self._calculate_statistics(all_functions),
                "security_components_count": len(all_functions),
                "registry_protection_enabled": True,
                "sleep_managers_woken": 0
            }
            
            return registry
            
        except Exception as e:
            print(f"❌ Ошибка создания реестра: {e}")
            return {}
    
    def _calculate_statistics(self, functions: Dict[str, Any]) -> Dict[str, int]:
        """Расчет статистики"""
        active_count = sum(1 for f in functions.values() 
                          if f.get("status") in ["active", "enabled", "running"])
        sleeping_count = sum(1 for f in functions.values() 
                           if f.get("status") == "sleeping")
        critical_count = sum(1 for f in functions.values() 
                           if f.get("is_critical", False))
        
        return {
            "total_functions": len(functions),
            "active_functions": active_count,
            "sleeping_functions": sleeping_count,
            "critical_functions": critical_count,
            "auto_enable_functions": sum(1 for f in functions.values() 
                                       if f.get("auto_enable", False))
        }
    
    def save_registry(self, registry: Dict[str, Any]) -> bool:
        """Сохранение реестра"""
        try:
            print("💾 Сохранение окончательного реестра...")
            
            with open(self.registry_path, 'w') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(self.registry_path)
            print(f"  ✅ Реестр сохранен: {self.registry_path}")
            print(f"  📊 Размер файла: {file_size:,} байт")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка сохранения реестра: {e}")
            return False
    
    def create_sfm_protection(self) -> bool:
        """Создание защиты от перезаписи SFM"""
        try:
            print("🛡️  Создание защиты от перезаписи SFM...")
            
            # Создаем файл защиты
            protection_file = "data/sfm/.registry_protected"
            with open(protection_file, 'w') as f:
                f.write(f"Registry protected at {datetime.now().isoformat()}\n")
                f.write("DO NOT DELETE - Prevents SFM from overwriting registry\n")
            
            print(f"  ✅ Файл защиты создан: {protection_file}")
            
            # Создаем скрипт мониторинга
            monitor_script = """#!/usr/bin/env python3
import json
import os
import time
from datetime import datetime

def monitor_registry():
    registry_path = "data/sfm/function_registry.json"
    expected_functions = 327
    
    while True:
        try:
            with open(registry_path, 'r') as f:
                registry = json.load(f)
            
            current_functions = len(registry.get('functions', {}))
            
            if current_functions < expected_functions:
                print(f"🚨 ALERT: Registry was overwritten! Expected {expected_functions}, got {current_functions}")
                # Здесь можно добавить логику восстановления
                
        except Exception as e:
            print(f"❌ Error monitoring registry: {e}")
        
        time.sleep(60)  # Проверяем каждую минуту

if __name__ == "__main__":
    monitor_registry()
"""
            
            with open("scripts/registry_monitor.py", 'w') as f:
                f.write(monitor_script)
            
            print(f"  ✅ Скрипт мониторинга создан: scripts/registry_monitor.py")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания защиты: {e}")
            return False
    
    def run_ultimate_fix(self) -> bool:
        """Запуск окончательного исправления"""
        try:
            print("🚀 ОКОНЧАТЕЛЬНОЕ ИСПРАВЛЕНИЕ SFM")
            print("=" * 50)
            
            # 1. Создание бэкапа
            if not self.create_backup():
                return False
            
            # 2. Загрузка полного реестра
            all_functions = self.load_complete_registry()
            if not all_functions:
                return False
            
            # 3. Создание окончательного реестра
            registry = self.create_ultimate_registry(all_functions)
            if not registry:
                return False
            
            # 4. Сохранение реестра
            if not self.save_registry(registry):
                return False
            
            # 5. Создание защиты
            if not self.create_sfm_protection():
                return False
            
            print("=" * 50)
            print("✅ ОКОНЧАТЕЛЬНОЕ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
            print(f"📊 Итоговая статистика:")
            stats = registry["statistics"]
            print(f"  Всего функций: {stats['total_functions']}")
            print(f"  Активных: {stats['active_functions']}")
            print(f"  Спящих: {stats['sleeping_functions']}")
            print(f"  Критических: {stats['critical_functions']}")
            print(f"  Автовключение: {stats['auto_enable_functions']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            return False


if __name__ == "__main__":
    fixer = UltimateSFMFix()
    success = fixer.run_ultimate_fix()
    
    if success:
        print("\n🎉 ОКОНЧАТЕЛЬНОЕ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        exit(0)
    else:
        print("\n💥 ОКОНЧАТЕЛЬНОЕ ИСПРАВЛЕНИЕ ЗАВЕРШИЛОСЬ С ОШИБКАМИ!")
        exit(1)