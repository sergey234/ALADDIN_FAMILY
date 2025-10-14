#!/usr/bin/env python3
"""
FIXED Registry Merge Manager
ИСПРАВЛЕННЫЙ скрипт объединения реестров с правильной конвертацией спящих функций
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class FixedRegistryMergeManager:
    """ИСПРАВЛЕННЫЙ менеджер объединения реестров функций"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = f"backups/fixed_registry_merge_backup_{self.timestamp}"
        self.old_registry_path = "data/functions_registry.json"
        self.new_registry_path = "data/sfm/function_registry.json"
        self.sleep_states_dir = "data/sleep_states"
        
    def create_backup(self) -> bool:
        """Создание полного бэкапа системы"""
        try:
            print("🔄 Создание полного бэкапа системы...")
            
            # Создаем директорию бэкапа
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # Копируем критические компоненты
            critical_dirs = ["data/sfm", "data/sleep_states", "security", "core", "ai"]
            for dir_name in critical_dirs:
                if os.path.exists(dir_name):
                    os.system(f"cp -r {dir_name} {self.backup_dir}/")
                    print(f"  ✅ Скопирован {dir_name}")
                else:
                    print(f"  ⚠️  Директория {dir_name} не найдена")
            
            print(f"✅ Бэкап создан: {self.backup_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания бэкапа: {e}")
            return False
    
    def convert_sleeping_functions(self) -> List[Dict[str, Any]]:
        """ИСПРАВЛЕННАЯ конвертация спящих функций в формат SFM"""
        try:
            print("🔄 ИСПРАВЛЕННАЯ конвертация спящих функций...")
            
            sleeping_functions = []
            sleep_files = glob.glob(f"{self.sleep_states_dir}/*_state.json")
            
            print(f"  📁 Найдено файлов спящих функций: {len(sleep_files)}")
            
            for sleep_file in sleep_files:
                try:
                    with open(sleep_file, 'r') as f:
                        sleep_data = json.load(f)
                    
                    # ИСПРАВЛЕННАЯ конвертация в формат SFM
                    converted_func = self._convert_sleep_to_sfm_format_fixed(sleep_data)
                    sleeping_functions.append(converted_func)
                    
                    if len(sleeping_functions) % 50 == 0:
                        print(f"  📊 Конвертировано: {len(sleeping_functions)} функций...")
                    
                except Exception as e:
                    print(f"  ⚠️  Ошибка конвертации {sleep_file}: {e}")
                    continue
            
            print(f"  ✅ ИСПРАВЛЕННАЯ конвертация завершена: {len(sleeping_functions)} функций")
            return sleeping_functions
            
        except Exception as e:
            print(f"❌ Ошибка конвертации спящих функций: {e}")
            return []
    
    def _convert_sleep_to_sfm_format_fixed(self, sleep_data: Dict[str, Any]) -> Dict[str, Any]:
        """ИСПРАВЛЕННАЯ конвертация одной спящей функции в формат SFM"""
        function_name = sleep_data["function_name"]
        function_id = sleep_data["function_id"]
        
        return {
            "function_id": function_id,
            "name": function_name,
            "description": f"Спящая функция {function_name}",
            "function_type": self._determine_function_type_fixed(function_name),
            "security_level": sleep_data["security_level"],
            "status": "sleeping",
            "created_at": sleep_data["sleep_time"],
            "is_critical": sleep_data["is_critical"],
            "auto_enable": False,
            "wake_time": sleep_data["sleep_time"],
            "emergency_wake_up": sleep_data["is_critical"],
            "features": [],
            "dependencies": [],
            "file_path": self._determine_file_path_fixed(function_name),
            "class_name": function_name,
            "global_instance": f"{function_name.lower()}_instance",
            "sleep_state": {
                "sleep_time": sleep_data["sleep_time"],
                "previous_status": sleep_data["previous_status"],
                "minimal_system_sleep": sleep_data.get("minimal_system_sleep", False)
            },
            # Добавляем поля для совместимости с SFM
            "execution_count": 0,
            "success_count": 0,
            "error_count": 0
        }
    
    def _determine_function_type_fixed(self, function_name: str) -> str:
        """ИСПРАВЛЕННОЕ определение типа функции по имени"""
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
    
    def _determine_file_path_fixed(self, function_name: str) -> str:
        """ИСПРАВЛЕННОЕ определение пути к файлу функции"""
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
    
    def merge_registries_fixed(self, sleeping_functions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ИСПРАВЛЕННОЕ объединение всех реестров в единый"""
        try:
            print("🔄 ИСПРАВЛЕННОЕ объединение реестров...")
            
            # Загружаем новый реестр (основной)
            with open(self.new_registry_path, 'r') as f:
                merged_registry = json.load(f)
            
            print(f"  📊 Исходный реестр: {len(merged_registry.get('functions', {}))} функций")
            
            # Добавляем спящие функции
            added_count = 0
            skipped_count = 0
            
            for func in sleeping_functions:
                func_id = func["function_id"]
                if func_id not in merged_registry["functions"]:
                    merged_registry["functions"][func_id] = func
                    added_count += 1
                    if added_count % 50 == 0:
                        print(f"  📊 Добавлено: {added_count} функций...")
                else:
                    skipped_count += 1
            
            print(f"  ✅ Добавлено функций: {added_count}")
            print(f"  ⚠️  Пропущено функций: {skipped_count}")
            
            # Обновляем метаданные
            merged_registry["version"] = "2.0"
            merged_registry["last_updated"] = datetime.now().isoformat()
            merged_registry["security_components_count"] = len(merged_registry["functions"])
            
            # Добавляем статистику
            active_count = sum(1 for f in merged_registry["functions"].values() 
                             if f.get("status") in ["active", "enabled", "running"])
            sleeping_count = sum(1 for f in merged_registry["functions"].values() 
                               if f.get("status") == "sleeping")
            critical_count = sum(1 for f in merged_registry["functions"].values() 
                               if f.get("is_critical", False))
            
            merged_registry["statistics"] = {
                "total_functions": len(merged_registry["functions"]),
                "active_functions": active_count,
                "sleeping_functions": sleeping_count,
                "critical_functions": critical_count,
                "auto_enable_functions": sum(1 for f in merged_registry["functions"].values() 
                                           if f.get("auto_enable", False))
            }
            
            # Добавляем поля для совместимости с SFM
            merged_registry["handlers"] = {}
            merged_registry["registry_protection_enabled"] = True
            merged_registry["sleep_managers_woken"] = 0
            
            print(f"  📊 ИТОГОВАЯ СТАТИСТИКА:")
            print(f"    Всего функций: {merged_registry['statistics']['total_functions']}")
            print(f"    Активных: {merged_registry['statistics']['active_functions']}")
            print(f"    Спящих: {merged_registry['statistics']['sleeping_functions']}")
            print(f"    Критических: {merged_registry['statistics']['critical_functions']}")
            
            return merged_registry
            
        except Exception as e:
            print(f"❌ Ошибка объединения реестров: {e}")
            return {}
    
    def save_merged_registry_fixed(self, merged_registry: Dict[str, Any]) -> bool:
        """ИСПРАВЛЕННОЕ сохранение объединенного реестра"""
        try:
            print("💾 ИСПРАВЛЕННОЕ сохранение объединенного реестра...")
            
            # Создаем резервную копию текущего реестра
            backup_path = f"{self.new_registry_path}.backup_{self.timestamp}"
            if os.path.exists(self.new_registry_path):
                os.system(f"cp {self.new_registry_path} {backup_path}")
                print(f"  ✅ Резервная копия: {backup_path}")
            
            # Сохраняем объединенный реестр
            with open(self.new_registry_path, 'w') as f:
                json.dump(merged_registry, f, indent=2, ensure_ascii=False)
            
            print(f"  ✅ Объединенный реестр сохранен: {self.new_registry_path}")
            
            # Проверяем размер файла
            file_size = os.path.getsize(self.new_registry_path)
            print(f"  📊 Размер файла: {file_size:,} байт")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка сохранения реестра: {e}")
            return False
    
    def validate_merged_registry_fixed(self, registry: Dict[str, Any]) -> bool:
        """ИСПРАВЛЕННАЯ валидация объединенного реестра"""
        try:
            print("🔍 ИСПРАВЛЕННАЯ валидация объединенного реестра...")
            
            # Проверяем обязательные поля
            required_fields = ["version", "last_updated", "functions", "statistics"]
            for field in required_fields:
                if field not in registry:
                    print(f"  ❌ Отсутствует обязательное поле: {field}")
                    return False
            
            # Проверяем уникальность function_id
            function_ids = list(registry["functions"].keys())
            if len(function_ids) != len(set(function_ids)):
                print("  ❌ Найдены дублирующиеся function_id")
                return False
            
            # Проверяем структуру функций
            required_func_fields = ["function_id", "name", "description", "function_type", 
                                  "security_level", "status", "created_at", "is_critical"]
            
            validation_errors = 0
            for func_id, func_data in registry["functions"].items():
                for field in required_func_fields:
                    if field not in func_data:
                        print(f"  ❌ Функция {func_id} не содержит поле {field}")
                        validation_errors += 1
                        if validation_errors > 10:  # Ограничиваем вывод ошибок
                            print("  ... и еще ошибки ...")
                            break
                
                if validation_errors > 10:
                    break
            
            if validation_errors > 0:
                print(f"  ❌ Найдено {validation_errors} ошибок валидации")
                return False
            
            # Проверяем JSON валидность
            json.dumps(registry)
            
            print("  ✅ ИСПРАВЛЕННАЯ валидация пройдена успешно")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка валидации: {e}")
            return False
    
    def run_fixed_merge_process(self) -> bool:
        """Запуск ИСПРАВЛЕННОГО процесса объединения"""
        try:
            print("🚀 ЗАПУСК ИСПРАВЛЕННОГО ПРОЦЕССА ОБЪЕДИНЕНИЯ РЕЕСТРОВ")
            print("=" * 60)
            
            # 1. Создание бэкапа
            if not self.create_backup():
                return False
            
            # 2. ИСПРАВЛЕННАЯ конвертация спящих функций
            sleeping_functions = self.convert_sleeping_functions()
            if not sleeping_functions:
                print("❌ Нет спящих функций для конвертации")
                return False
            
            # 3. ИСПРАВЛЕННОЕ объединение реестров
            merged_registry = self.merge_registries_fixed(sleeping_functions)
            if not merged_registry:
                return False
            
            # 4. ИСПРАВЛЕННАЯ валидация
            if not self.validate_merged_registry_fixed(merged_registry):
                return False
            
            # 5. ИСПРАВЛЕННОЕ сохранение
            if not self.save_merged_registry_fixed(merged_registry):
                return False
            
            print("=" * 60)
            print("✅ ИСПРАВЛЕННЫЙ ПРОЦЕСС ОБЪЕДИНЕНИЯ ЗАВЕРШЕН УСПЕШНО!")
            print(f"📊 Итоговая статистика:")
            print(f"  Всего функций: {merged_registry['statistics']['total_functions']}")
            print(f"  Активных: {merged_registry['statistics']['active_functions']}")
            print(f"  Спящих: {merged_registry['statistics']['sleeping_functions']}")
            print(f"  Критических: {merged_registry['statistics']['critical_functions']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Критическая ошибка процесса объединения: {e}")
            return False


if __name__ == "__main__":
    manager = FixedRegistryMergeManager()
    success = manager.run_fixed_merge_process()
    
    if success:
        print("\n🎉 ИСПРАВЛЕННОЕ ОБЪЕДИНЕНИЕ РЕЕСТРОВ ЗАВЕРШЕНО УСПЕШНО!")
        exit(0)
    else:
        print("\n💥 ИСПРАВЛЕННОЕ ОБЪЕДИНЕНИЕ РЕЕСТРОВ ЗАВЕРШИЛОСЬ С ОШИБКАМИ!")
        exit(1)