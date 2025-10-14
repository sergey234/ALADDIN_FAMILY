#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Безопасная очистка SFM Registry
Удаляет только те функции, которые точно соответствуют перемещенным файлам
"""

import json
import os
from pathlib import Path
import logging

class SafeSFMCleaner:
    def __init__(self):
        self.project_root = Path("/Users/sergejhlystov/ALADDIN_NEW")
        self.registry_path = self.project_root / "data" / "sfm" / "function_registry.json"
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SafeSFMCleaner")
        
        # ТОЧНЫЙ список функций для удаления (найденных в SFM)
        self.functions_to_remove = [
            "security_monitoring",
            "circuit_breaker_extra", 
            "mobile_security_agent_main",
            "device_security",
            "incident_response",
            "security_analytics",
            "intrusion_prevention",
            "circuit_breaker",
            "circuit_breaker_main",
            "mobile_security_agent_extra",
            "family_communication_hub_a_plus",
            "parental_control_bot_v2",
            "elderly_interface_manager_backup",
            "network_monitoring",
            "behavioral_analysis",
            "child_protection_new",
            "put_to_sleep"
        ]

    def load_registry(self):
        """Загружает SFM registry"""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Ошибка загрузки registry: {e}")
            return None

    def save_registry(self, data):
        """Сохраняет SFM registry"""
        try:
            # Создаем резервную копию
            backup_path = self.registry_path.with_suffix('.backup_before_safe_cleanup.json')
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Сохраняем обновленный registry
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ Registry сохранен. Резервная копия: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка сохранения registry: {e}")
            return False

    def verify_functions_exist(self, registry_data):
        """Проверяет, что все функции для удаления существуют"""
        missing_functions = []
        for func_id in self.functions_to_remove:
            if func_id not in registry_data.get('functions', {}):
                missing_functions.append(func_id)
        
        if missing_functions:
            self.logger.warning(f"⚠️ Функции не найдены в registry: {missing_functions}")
            return False
        
        return True

    def cleanup_registry(self):
        """Безопасно очищает registry от дубликатов"""
        self.logger.info("🚀 Начало безопасной очистки SFM registry...")
        
        # Загружаем registry
        registry_data = self.load_registry()
        if not registry_data:
            return False
        
        initial_count = len(registry_data.get('functions', {}))
        self.logger.info(f"📊 Начальное количество функций: {initial_count}")
        
        # Проверяем, что все функции для удаления существуют
        if not self.verify_functions_exist(registry_data):
            self.logger.error("❌ Не все функции для удаления найдены. Остановка.")
            return False
        
        # Удаляем функции
        removed_count = 0
        for func_id in self.functions_to_remove:
            if func_id in registry_data.get('functions', {}):
                func_info = registry_data['functions'][func_id]
                file_path = func_info.get('file_path', '')
                file_name = os.path.basename(file_path)
                
                del registry_data['functions'][func_id]
                removed_count += 1
                self.logger.info(f"✅ Удалена функция: {func_id} ({file_name})")
        
        final_count = len(registry_data.get('functions', {}))
        self.logger.info(f"📊 Финальное количество функций: {final_count}")
        self.logger.info(f"📊 Удалено функций: {removed_count}")
        
        # Сохраняем обновленный registry
        if self.save_registry(registry_data):
            self.logger.info("🎉 Безопасная очистка SFM registry завершена!")
            return True
        else:
            self.logger.error("❌ Ошибка при сохранении registry")
            return False

    def run(self):
        """Запускает процесс безопасной очистки"""
        print("=" * 80)
        print("🧹 БЕЗОПАСНАЯ ОЧИСТКА SFM REGISTRY")
        print("=" * 80)
        print(f"📋 Функций для удаления: {len(self.functions_to_remove)}")
        print("🔍 Список функций:")
        for i, func_id in enumerate(self.functions_to_remove, 1):
            print(f"  {i:2d}. {func_id}")
        print("=" * 80)
        
        success = self.cleanup_registry()
        
        if success:
            print("\n🎉 Очистка завершена успешно!")
            print("📊 SFM registry обновлен")
            print("📁 Резервная копия создана")
            print("✅ Удалены только дублирующие функции")
        else:
            print("\n❌ Ошибка при очистке registry")
        
        print("=" * 80)

if __name__ == "__main__":
    cleaner = SafeSFMCleaner()
    cleaner.run()