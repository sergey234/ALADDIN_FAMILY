#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Очистка SFM Registry от дубликатов
Удаляет записи о перемещенных файлах из function_registry.json
"""

import json
import os
from pathlib import Path
import logging

class SFMRegistryCleaner:
    def __init__(self):
        self.project_root = Path("/Users/sergejhlystov/ALADDIN_NEW")
        self.registry_path = self.project_root / "data" / "sfm" / "function_registry.json"
        self.manifest_path = self.project_root / "security" / "formatting_work" / "duplicates" / "MOVED_FILES_MANIFEST.json"
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SFMRegistryCleaner")
        
        # Список перемещенных файлов
        self.moved_files = [
            "security_analytics.py",
            "security_monitoring_backup.py", 
            "security_monitoring.py",
            "incident_response.py",
            "circuit_breaker_main.py",
            "circuit_breaker.py",
            "circuit_breaker_extra.py",
            "malware_protection_old_backup_20250928_125507.py",
            "intrusion_prevention.py",
            "device_security.py",
            "network_monitoring.py",
            "put_to_sleep.py",
            "user_interface_manager_main.py",
            "parental_control_bot_v2.py",
            "notification_bot_main.py",
            "notification_bot_extra.py",
            "universal_privacy_manager_new.py",
            "elderly_interface_manager_backup.py",
            "family_profile_manager.py",
            "child_protection_new.py",
            "trust_scoring.py",
            "behavioral_analysis.py",
            "mobile_security_agent_backup_20250921_103531.py",
            "mobile_security_agent_extra.py",
            "mobile_security_agent_main.py",
            "phishing_protection_agent_backup_20250921_104040.py",
            "family_communication_hub_backup_20250921_103829.py",
            "family_communication_hub_a_plus.py",
            "behavioral_analytics_engine_extra.py",
            "behavioral_analytics_engine_main.py",
            "financial_protection_hub_backup_20250921_104412.py"
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
            backup_path = self.registry_path.with_suffix('.backup_before_cleanup.json')
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

    def find_functions_to_remove(self, registry_data):
        """Находит функции для удаления по именам файлов"""
        functions_to_remove = []
        
        for func_id, func_data in registry_data.get('functions', {}).items():
            file_path = func_data.get('file_path', '')
            file_name = os.path.basename(file_path)
            
            if file_name in self.moved_files:
                functions_to_remove.append(func_id)
                self.logger.info(f"🔍 Найдена функция для удаления: {func_id} ({file_name})")
        
        return functions_to_remove

    def cleanup_registry(self):
        """Очищает registry от дубликатов"""
        self.logger.info("🚀 Начало очистки SFM registry...")
        
        # Загружаем registry
        registry_data = self.load_registry()
        if not registry_data:
            return False
        
        initial_count = len(registry_data.get('functions', {}))
        self.logger.info(f"📊 Начальное количество функций: {initial_count}")
        
        # Находим функции для удаления
        functions_to_remove = self.find_functions_to_remove(registry_data)
        self.logger.info(f"🔍 Найдено функций для удаления: {len(functions_to_remove)}")
        
        # Удаляем функции
        removed_count = 0
        for func_id in functions_to_remove:
            if func_id in registry_data.get('functions', {}):
                del registry_data['functions'][func_id]
                removed_count += 1
                self.logger.info(f"✅ Удалена функция: {func_id}")
        
        final_count = len(registry_data.get('functions', {}))
        self.logger.info(f"📊 Финальное количество функций: {final_count}")
        self.logger.info(f"📊 Удалено функций: {removed_count}")
        
        # Сохраняем обновленный registry
        if self.save_registry(registry_data):
            self.logger.info("🎉 Очистка SFM registry завершена успешно!")
            return True
        else:
            self.logger.error("❌ Ошибка при сохранении registry")
            return False

    def run(self):
        """Запускает процесс очистки"""
        print("=" * 80)
        print("🧹 ОЧИСТКА SFM REGISTRY ОТ ДУБЛИКАТОВ")
        print("=" * 80)
        
        success = self.cleanup_registry()
        
        if success:
            print("\n🎉 Очистка завершена успешно!")
            print("📊 SFM registry обновлен")
            print("📁 Резервная копия создана")
        else:
            print("\n❌ Ошибка при очистке registry")
        
        print("=" * 80)

if __name__ == "__main__":
    cleaner = SFMRegistryCleaner()
    cleaner.run()