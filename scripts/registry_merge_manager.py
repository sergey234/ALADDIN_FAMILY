#!/usr/bin/env python3
"""
ALADDIN Registry Merge Manager
Безопасное объединение реестров функций с конвертацией спящих функций
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class RegistryMergeManager:
    """Менеджер объединения реестров функций"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = f"backups/registry_merge_backup_{self.timestamp}"
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
    
    def analyze_conflicts(self) -> Dict[str, Any]:
        """Анализ конфликтов между реестрами"""
        try:
            print("🔍 Анализ конфликтов между реестрами...")
            
            # Загружаем реестры
            with open(self.old_registry_path, 'r') as f:
                old_registry = json.load(f)
            with open(self.new_registry_path, 'r') as f:
                new_registry = json.load(f)
            
            old_functions = set(old_registry['functions'].keys())
            new_functions = set(new_registry['functions'].keys())
            
            # Анализируем пересечения
            common_functions = old_functions & new_functions
            old_only = old_functions - new_functions
            new_only = new_functions - old_functions
            
            analysis = {
                "old_count": len(old_functions),
                "new_count": len(new_functions),
                "common_count": len(common_functions),
                "old_only_count": len(old_only),
                "new_only_count": len(new_only),
                "common_functions": list(common_functions),
                "old_only_functions": list(old_only),
                "new_only_functions": list(new_only),
                "has_conflicts": len(old_only) > 0
            }
            
            print(f"  📊 Старый реестр: {analysis['old_count']} функций")
            print(f"  📊 Новый реестр: {analysis['new_count']} функций")
            print(f"  🔄 Общих функций: {analysis['common_count']}")
            print(f"  ⚠️  Только в старом: {analysis['old_only_count']}")
            print(f"  ➕ Только в новом: {analysis['new_only_count']}")
            
            if analysis['has_conflicts']:
                print("  ⚠️  Обнаружены конфликты!")
            else:
                print("  ✅ Конфликтов не обнаружено")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Ошибка анализа конфликтов: {e}")
            return {}
    
    def convert_sleeping_functions(self) -> List[Dict[str, Any]]:
        """Конвертация спящих функций в формат SFM"""
        try:
            print("🔄 Конвертация спящих функций...")
            
            sleeping_functions = []
            sleep_files = glob.glob(f"{self.sleep_states_dir}/*_state.json")
            
            print(f"  📁 Найдено файлов спящих функций: {len(sleep_files)}")
            
            for sleep_file in sleep_files:
                try:
                    with open(sleep_file, 'r') as f:
                        sleep_data = json.load(f)
                    
                    # Конвертируем в формат SFM
                    converted_func = self._convert_sleep_to_sfm_format(sleep_data)
                    sleeping_functions.append(converted_func)
                    
                except Exception as e:
                    print(f"  ⚠️  Ошибка конвертации {sleep_file}: {e}")
                    continue
            
            print(f"  ✅ Конвертировано функций: {len(sleeping_functions)}")
            return sleeping_functions
            
        except Exception as e:
            print(f"❌ Ошибка конвертации спящих функций: {e}")
            return []
    
    def _convert_sleep_to_sfm_format(self, sleep_data: Dict[str, Any]) -> Dict[str, Any]:
        """Конвертация одной спящей функции в формат SFM"""
        return {
            "function_id": sleep_data["function_id"],
            "name": sleep_data["function_name"],
            "description": f"Спящая функция {sleep_data['function_name']}",
            "function_type": self._determine_function_type(sleep_data["function_name"]),
            "security_level": sleep_data["security_level"],
            "status": "sleeping",
            "created_at": sleep_data["sleep_time"],
            "is_critical": sleep_data["is_critical"],
            "auto_enable": False,
            "wake_time": sleep_data["sleep_time"],
            "emergency_wake_up": sleep_data["is_critical"],
            "features": [],
            "dependencies": [],
            "file_path": self._determine_file_path(sleep_data["function_name"]),
            "class_name": sleep_data["function_name"],
            "global_instance": f"{sleep_data['function_name'].lower()}_instance",
            "sleep_state": {
                "sleep_time": sleep_data["sleep_time"],
                "previous_status": sleep_data["previous_status"],
                "minimal_system_sleep": sleep_data.get("minimal_system_sleep", False)
            }
        }
    
    def _determine_function_type(self, function_name: str) -> str:
        """Определение типа функции по имени"""
        if "bot" in function_name.lower():
            return "bot"
        elif "agent" in function_name.lower():
            return "ai_agent"
        elif "manager" in function_name.lower():
            return "manager"
        elif "service" in function_name.lower():
            return "service"
        else:
            return "unknown"
    
    def _determine_file_path(self, function_name: str) -> str:
        """Определение пути к файлу функции"""
        # Простая эвристика для определения пути
        if "bot" in function_name.lower():
            return f"bots/{function_name.lower()}.py"
        elif "agent" in function_name.lower():
            return f"ai_agents/{function_name.lower()}.py"
        elif "manager" in function_name.lower():
            return f"managers/{function_name.lower()}.py"
        else:
            return f"security/{function_name.lower()}.py"
    
    def merge_registries(self, sleeping_functions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Объединение всех реестров в единый"""
        try:
            print("🔄 Объединение реестров...")
            
            # Загружаем новый реестр (основной)
            with open(self.new_registry_path, 'r') as f:
                merged_registry = json.load(f)
            
            # Добавляем спящие функции
            for func in sleeping_functions:
                func_id = func["function_id"]
                if func_id not in merged_registry["functions"]:
                    merged_registry["functions"][func_id] = func
                    print(f"  ➕ Добавлена спящая функция: {func_id}")
                else:
                    print(f"  ⚠️  Функция {func_id} уже существует, пропускаем")
            
            # Обновляем метаданные
            merged_registry["version"] = "2.0"
            merged_registry["last_updated"] = datetime.now().isoformat()
            merged_registry["security_components_count"] = len(merged_registry["functions"])
            
            # Добавляем статистику
            active_count = sum(1 for f in merged_registry["functions"].values() if f["status"] == "active")
            sleeping_count = sum(1 for f in merged_registry["functions"].values() if f["status"] == "sleeping")
            critical_count = sum(1 for f in merged_registry["functions"].values() if f["is_critical"])
            
            merged_registry["statistics"] = {
                "total_functions": len(merged_registry["functions"]),
                "active_functions": active_count,
                "sleeping_functions": sleeping_count,
                "critical_functions": critical_count,
                "auto_enable_functions": sum(1 for f in merged_registry["functions"].values() if f.get("auto_enable", False))
            }
            
            print(f"  📊 Всего функций: {merged_registry['statistics']['total_functions']}")
            print(f"  🟢 Активных: {merged_registry['statistics']['active_functions']}")
            print(f"  😴 Спящих: {merged_registry['statistics']['sleeping_functions']}")
            print(f"  🔴 Критических: {merged_registry['statistics']['critical_functions']}")
            
            return merged_registry
            
        except Exception as e:
            print(f"❌ Ошибка объединения реестров: {e}")
            return {}
    
    def save_merged_registry(self, merged_registry: Dict[str, Any]) -> bool:
        """Сохранение объединенного реестра"""
        try:
            print("💾 Сохранение объединенного реестра...")
            
            # Создаем резервную копию текущего реестра
            backup_path = f"{self.new_registry_path}.backup_{self.timestamp}"
            os.system(f"cp {self.new_registry_path} {backup_path}")
            
            # Сохраняем объединенный реестр
            with open(self.new_registry_path, 'w') as f:
                json.dump(merged_registry, f, indent=2, ensure_ascii=False)
            
            print(f"  ✅ Резервная копия: {backup_path}")
            print(f"  ✅ Объединенный реестр: {self.new_registry_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка сохранения реестра: {e}")
            return False
    
    def validate_merged_registry(self, registry: Dict[str, Any]) -> bool:
        """Валидация объединенного реестра"""
        try:
            print("🔍 Валидация объединенного реестра...")
            
            # Проверяем обязательные поля
            required_fields = ["version", "last_updated", "functions", "security_components_count"]
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
            
            for func_id, func_data in registry["functions"].items():
                for field in required_func_fields:
                    if field not in func_data:
                        print(f"  ❌ Функция {func_id} не содержит поле {field}")
                        return False
            
            # Проверяем JSON валидность
            json.dumps(registry)
            
            print("  ✅ Валидация пройдена успешно")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка валидации: {e}")
            return False
    
    def cleanup_old_registry(self) -> bool:
        """Удаление старого реестра"""
        try:
            print("🗑️  Удаление старого реестра...")
            
            if os.path.exists(self.old_registry_path):
                # Создаем резервную копию
                backup_path = f"{self.old_registry_path}.backup_{self.timestamp}"
                os.system(f"cp {self.old_registry_path} {backup_path}")
                
                # Удаляем старый реестр
                os.remove(self.old_registry_path)
                
                print(f"  ✅ Резервная копия: {backup_path}")
                print(f"  ✅ Старый реестр удален: {self.old_registry_path}")
                return True
            else:
                print(f"  ⚠️  Старый реестр не найден: {self.old_registry_path}")
                return True
                
        except Exception as e:
            print(f"❌ Ошибка удаления старого реестра: {e}")
            return False
    
    def run_merge_process(self) -> bool:
        """Запуск полного процесса объединения"""
        try:
            print("🚀 ЗАПУСК ПРОЦЕССА ОБЪЕДИНЕНИЯ РЕЕСТРОВ")
            print("=" * 50)
            
            # 1. Создание бэкапа
            if not self.create_backup():
                return False
            
            # 2. Анализ конфликтов
            conflicts = self.analyze_conflicts()
            if not conflicts:
                return False
            
            # 3. Конвертация спящих функций
            sleeping_functions = self.convert_sleeping_functions()
            if not sleeping_functions:
                print("⚠️  Нет спящих функций для конвертации")
                sleeping_functions = []
            
            # 4. Объединение реестров
            merged_registry = self.merge_registries(sleeping_functions)
            if not merged_registry:
                return False
            
            # 5. Валидация
            if not self.validate_merged_registry(merged_registry):
                return False
            
            # 6. Сохранение
            if not self.save_merged_registry(merged_registry):
                return False
            
            # 7. Удаление старого реестра
            if not self.cleanup_old_registry():
                return False
            
            print("=" * 50)
            print("✅ ПРОЦЕСС ОБЪЕДИНЕНИЯ ЗАВЕРШЕН УСПЕШНО!")
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
    manager = RegistryMergeManager()
    success = manager.run_merge_process()
    
    if success:
        print("\n🎉 ОБЪЕДИНЕНИЕ РЕЕСТРОВ ЗАВЕРШЕНО УСПЕШНО!")
        exit(0)
    else:
        print("\n💥 ОБЪЕДИНЕНИЕ РЕЕСТРОВ ЗАВЕРШИЛОСЬ С ОШИБКАМИ!")
        exit(1)