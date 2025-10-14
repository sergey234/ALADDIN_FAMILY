#!/usr/bin/env python3
"""
FINAL SFM Registry Fix
ФИНАЛЬНОЕ решение проблемы SFM с реестром
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List


class FinalSFMRegistryFix:
    """ФИНАЛЬНОЕ решение проблемы SFM с реестром"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.registry_path = "data/sfm/function_registry.json"
        self.sleep_states_dir = "data/sleep_states"
        self.backup_dir = f"backups/final_sfm_fix_backup_{self.timestamp}"
        
    def create_complete_registry(self) -> Dict[str, Any]:
        """Создание полного реестра с 327 функциями"""
        try:
            print("🔄 Создание полного реестра с 327 функциями...")
            
            # Загружаем спящие функции
            sleeping_functions = self._load_sleeping_functions()
            print(f"  📊 Загружено спящих функций: {len(sleeping_functions)}")
            
            # Создаем базовые функции SFM
            basic_functions = self._create_basic_functions()
            print(f"  📊 Создано базовых функций: {len(basic_functions)}")
            
            # Объединяем все функции
            all_functions = {**basic_functions, **sleeping_functions}
            print(f"  📊 Всего функций: {len(all_functions)}")
            
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
    
    def _load_sleeping_functions(self) -> Dict[str, Any]:
        """Загрузка спящих функций"""
        try:
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
            
            return sleeping_functions
            
        except Exception as e:
            print(f"❌ Ошибка загрузки спящих функций: {e}")
            return {}
    
    def _create_basic_functions(self) -> Dict[str, Any]:
        """Создание базовых функций SFM"""
        basic_functions = {
            "core_base": {
                "function_id": "core_base",
                "name": "CoreBase",
                "description": "Базовая архитектура системы",
                "function_type": "core",
                "security_level": "high",
                "status": "enabled",
                "created_at": datetime.now().isoformat(),
                "is_critical": True,
                "auto_enable": True,
                "wake_time": datetime.now().isoformat(),
                "emergency_wake_up": True,
                "features": ["core_architecture"],
                "dependencies": [],
                "file_path": "core/base.py",
                "class_name": "CoreBase",
                "global_instance": "core_base_instance",
                "execution_count": 0,
                "success_count": 0,
                "error_count": 0
            },
            "service_base": {
                "function_id": "service_base",
                "name": "ServiceBase",
                "description": "Базовый сервис",
                "function_type": "core",
                "security_level": "high",
                "status": "enabled",
                "created_at": datetime.now().isoformat(),
                "is_critical": True,
                "auto_enable": True,
                "wake_time": datetime.now().isoformat(),
                "emergency_wake_up": True,
                "features": ["service_architecture"],
                "dependencies": [],
                "file_path": "core/service_base.py",
                "class_name": "ServiceBase",
                "global_instance": "service_base_instance",
                "execution_count": 0,
                "success_count": 0,
                "error_count": 0
            },
            "security_base": {
                "function_id": "security_base",
                "name": "SecurityBase",
                "description": "Базовая безопасность",
                "function_type": "security",
                "security_level": "high",
                "status": "enabled",
                "created_at": datetime.now().isoformat(),
                "is_critical": True,
                "auto_enable": True,
                "wake_time": datetime.now().isoformat(),
                "emergency_wake_up": True,
                "features": ["security_architecture"],
                "dependencies": [],
                "file_path": "security/security_base.py",
                "class_name": "SecurityBase",
                "global_instance": "security_base_instance",
                "execution_count": 0,
                "success_count": 0,
                "error_count": 0
            },
            "database": {
                "function_id": "database",
                "name": "Database",
                "description": "Модуль базы данных",
                "function_type": "core",
                "security_level": "high",
                "status": "enabled",
                "created_at": datetime.now().isoformat(),
                "is_critical": True,
                "auto_enable": True,
                "wake_time": datetime.now().isoformat(),
                "emergency_wake_up": True,
                "features": ["database_management"],
                "dependencies": [],
                "file_path": "core/database.py",
                "class_name": "Database",
                "global_instance": "database_instance",
                "execution_count": 0,
                "success_count": 0,
                "error_count": 0
            },
            "configuration": {
                "function_id": "configuration",
                "name": "Configuration",
                "description": "Управление конфигурацией",
                "function_type": "core",
                "security_level": "medium",
                "status": "enabled",
                "created_at": datetime.now().isoformat(),
                "is_critical": False,
                "auto_enable": True,
                "wake_time": datetime.now().isoformat(),
                "emergency_wake_up": False,
                "features": ["config_management"],
                "dependencies": [],
                "file_path": "core/configuration.py",
                "class_name": "Configuration",
                "global_instance": "configuration_instance",
                "execution_count": 0,
                "success_count": 0,
                "error_count": 0
            },
            "logging_module": {
                "function_id": "logging_module",
                "name": "LoggingModule",
                "description": "Система логирования",
                "function_type": "core",
                "security_level": "medium",
                "status": "enabled",
                "created_at": datetime.now().isoformat(),
                "is_critical": False,
                "auto_enable": True,
                "wake_time": datetime.now().isoformat(),
                "emergency_wake_up": False,
                "features": ["logging_system"],
                "dependencies": [],
                "file_path": "core/logging_module.py",
                "class_name": "LoggingModule",
                "global_instance": "logging_module_instance",
                "execution_count": 0,
                "success_count": 0,
                "error_count": 0
            },
            "authentication": {
                "function_id": "authentication",
                "name": "Authentication",
                "description": "Аутентификация",
                "function_type": "security",
                "security_level": "high",
                "status": "enabled",
                "created_at": datetime.now().isoformat(),
                "is_critical": True,
                "auto_enable": True,
                "wake_time": datetime.now().isoformat(),
                "emergency_wake_up": True,
                "features": ["authentication_system"],
                "dependencies": [],
                "file_path": "security/authentication.py",
                "class_name": "Authentication",
                "global_instance": "authentication_instance",
                "execution_count": 0,
                "success_count": 0,
                "error_count": 0
            },
            "emergencymlanalyzer": {
                "function_id": "emergencymlanalyzer",
                "name": "EmergencyMLAnalyzer",
                "description": "ML анализатор экстренных ситуаций",
                "function_type": "ai_agent",
                "security_level": "high",
                "status": "enabled",
                "created_at": datetime.now().isoformat(),
                "is_critical": True,
                "auto_enable": True,
                "wake_time": datetime.now().isoformat(),
                "emergency_wake_up": True,
                "features": ["ml_analysis", "emergency_detection"],
                "dependencies": [],
                "file_path": "ai_agents/emergency_ml_analyzer.py",
                "class_name": "EmergencyMLAnalyzer",
                "global_instance": "emergencymlanalyzer_instance",
                "execution_count": 0,
                "success_count": 0,
                "error_count": 0
            }
        }
        
        return basic_functions
    
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
    
    def save_registry(self, registry: Dict[str, Any]) -> bool:
        """Сохранение реестра"""
        try:
            print("💾 Сохранение реестра...")
            
            with open(self.registry_path, 'w') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(self.registry_path)
            print(f"  ✅ Реестр сохранен: {self.registry_path}")
            print(f"  📊 Размер файла: {file_size:,} байт")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка сохранения реестра: {e}")
            return False
    
    def run_final_fix(self) -> bool:
        """Запуск финального исправления"""
        try:
            print("🚀 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ SFM РЕЕСТРА")
            print("=" * 50)
            
            # 1. Создание бэкапа
            if not self.create_backup():
                return False
            
            # 2. Создание полного реестра
            registry = self.create_complete_registry()
            if not registry:
                return False
            
            # 3. Сохранение реестра
            if not self.save_registry(registry):
                return False
            
            print("=" * 50)
            print("✅ ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
            print(f"📊 Итоговая статистика:")
            stats = registry["statistics"]
            print(f"  Всего функций: {stats['total_functions']}")
            print(f"  Активных: {stats['active_functions']}")
            print(f"  Спящих: {stats['sleeping_functions']}")
            print(f"  Критических: {stats['critical_functions']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            return False


if __name__ == "__main__":
    fixer = FinalSFMRegistryFix()
    success = fixer.run_final_fix()
    
    if success:
        print("\n🎉 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        exit(0)
    else:
        print("\n💥 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ ЗАВЕРШИЛОСЬ С ОШИБКАМИ!")
        exit(1)