#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ФИНАЛЬНЫЙ переместитель оставшихся backup файлов
Переносит последние 9 backup файлов с полной проверкой

Автор: ALADDIN Security Team
Версия: 3.0 Final
Дата: 2025-01-30
Качество: A+
"""

import os
import shutil
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

class FinalBackupMover:
    """Финальный переместитель оставшихся backup файлов"""
    
    def __init__(self):
        self.project_root = Path("/Users/sergejhlystov/ALADDIN_NEW")
        self.backup_dir = self.project_root / "security" / "formatting_work" / "backup_files"
        self.moved_files = []
        self.failed_files = []
        self.log_file = self.backup_dir / "FINAL_MOVEMENT_LOG.json"
        
        # Создаем директорию если не существует
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Загружаем SFM registry для проверки
        self.sfm_registry = self._load_sfm_registry()
        
    def _load_sfm_registry(self) -> Dict[str, Any]:
        """Загрузить SFM registry"""
        try:
            sfm_path = self.project_root / "data" / "sfm" / "function_registry.json"
            with open(sfm_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Не удалось загрузить SFM registry: {e}")
            return {}
    
    def find_remaining_backup_files(self) -> List[Tuple[Path, Path]]:
        """Найти оставшиеся 9 backup файлов"""
        backup_files = [
            # MICROSERVICES (1 файл)
            ("security/microservices/user_interface_manager_extra.py.backup_20250927_031442", "security/microservices/user_interface_manager.py"),
            
            # SECURITY MONITORING (4 файла)
            ("security/security_monitoring.py.backup_20250909_212030", "security/security_monitoring.py"),
            ("security/security_monitoring.py.backup_20250909_212748", "security/security_monitoring.py"),
            ("security/security_monitoring.py.backup_20250909_213215", "security/security_monitoring.py"),
            ("security/security_monitoring_ultimate_a_plus.py.backup_20250927_031440", "security/security_monitoring_ultimate_a_plus.py"),
            
            # MANAGERS (3 файла)
            ("security/managers/compliance_manager.py.backup", "security/managers/compliance_manager.py"),
            ("security/ai_agents/analytics_manager.py.backup_011225", "security/managers/analytics_manager.py"),
            ("security/ai_agents/monitor_manager.py.backup_011225", "security/managers/monitor_manager.py"),
            
            # AI (1 файл)
            ("security/ai/super_ai_support_assistant.py.backup_20250927_231340", "security/ai/super_ai_support_assistant.py"),
        ]
        
        found_files = []
        for backup_path, main_path in backup_files:
            backup_file = self.project_root / backup_path
            main_file = self.project_root / main_path
            
            if backup_file.exists():
                if main_file.exists():
                    found_files.append((backup_file, main_file))
                    print(f"✅ Найден: {backup_path}")
                else:
                    print(f"⚠️  Основной файл не найден для: {backup_path}")
            else:
                print(f"❌ Backup файл не найден: {backup_path}")
        
        return found_files
    
    def move_backup_file(self, backup_file: Path, main_file: Path) -> bool:
        """Переместить backup файл с проверками"""
        try:
            print(f"\n🔄 Обработка: {backup_file.name}")
            print("-" * 50)
            
            # 1. Проверка существования основного файла
            if not main_file.exists():
                print(f"❌ Основной файл не найден: {main_file}")
                return False
            
            print(f"✅ Основной файл читается: {main_file.name}")
            
            # 2. Перемещение backup файла
            destination = self.backup_dir / backup_file.name
            shutil.move(str(backup_file), str(destination))
            print(f"✅ Backup файл перемещен в: {destination}")
            
            # 3. Проверка что основной файл остался
            if not main_file.exists():
                print(f"❌ ОШИБКА: Основной файл исчез после перемещения!")
                # Восстанавливаем backup файл
                shutil.move(str(destination), str(backup_file))
                return False
            
            print(f"✅ Основной файл остался на месте: {main_file.name}")
            
            # 4. Проверка SFM регистрации
            main_name = main_file.stem
            if main_name in self.sfm_registry:
                sfm_info = self.sfm_registry[main_name]
                print(f"✅ Функция найдена в SFM: {main_name}")
                print(f"  - Статус: {sfm_info.get('status', 'unknown')}")
            else:
                print(f"⚠️  Функция не найдена в SFM: {main_name}")
            
            # 5. Запись в лог
            self.moved_files.append({
                'backup_file': str(backup_file),
                'main_file': str(main_file),
                'destination': str(destination),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            })
            
            print(f"✅ УСПЕШНО ПЕРЕМЕЩЕН: {backup_file.name}")
            return True
            
        except Exception as e:
            print(f"❌ ОШИБКА при перемещении {backup_file.name}: {e}")
            self.failed_files.append({
                'backup_file': str(backup_file),
                'main_file': str(main_file),
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'status': 'failed'
            })
            return False
    
    def save_log(self):
        """Сохранить детальный лог"""
        log_data = {
            'execution_info': {
                'timestamp': datetime.now().isoformat(),
                'total_files': len(self.moved_files) + len(self.failed_files),
                'moved_files': len(self.moved_files),
                'failed_files': len(self.failed_files),
                'success_rate': len(self.moved_files) / (len(self.moved_files) + len(self.failed_files)) * 100 if (len(self.moved_files) + len(self.failed_files)) > 0 else 0
            },
            'moved_files': self.moved_files,
            'failed_files': self.failed_files
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Детальный лог сохранен: {self.log_file}")
    
    def run(self):
        """Запустить финальное перемещение"""
        print("🔒 ALADDIN Security System - Final Backup Mover v3.0")
        print("Перенос оставшихся 9 backup файлов с полной проверкой")
        print("=" * 70)
        
        start_time = time.time()
        
        # Найти оставшиеся backup файлы
        print("🔍 Поиск оставшихся backup файлов...")
        backup_files = self.find_remaining_backup_files()
        
        if not backup_files:
            print("❌ Не найдено backup файлов для перемещения")
            return False
        
        print(f"📋 Найдено backup файлов: {len(backup_files)}")
        
        # Переместить файлы
        print(f"\n🔄 Перемещение backup файлов с расширенной проверкой...")
        success_count = 0
        
        for i, (backup_file, main_file) in enumerate(backup_files, 1):
            print(f"\n[{i}/{len(backup_files)}] Обработка файла")
            if self.move_backup_file(backup_file, main_file):
                success_count += 1
        
        # Сохранить лог
        self.save_log()
        
        # Итоги
        end_time = time.time()
        execution_time = end_time - start_time
        
        print("\n" + "=" * 70)
        print("📊 ИТОГИ ФИНАЛЬНОГО ПЕРЕМЕЩЕНИЯ:")
        print(f"⏱️  Время выполнения: {execution_time:.2f} секунд")
        print(f"📁 Всего найдено: {len(backup_files)} файлов")
        print(f"✅ Успешно перемещено: {success_count} файлов")
        print(f"❌ Ошибок: {len(backup_files) - success_count} файлов")
        print(f"📋 Процент успеха: {success_count/len(backup_files)*100:.1f}%")
        print("=" * 70)
        
        if success_count == len(backup_files):
            print("🎉 ФИНАЛЬНОЕ ПЕРЕМЕЩЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
            print(f"📁 Перемещено файлов: {success_count}")
            print(f"⏱️  Время: {execution_time:.2f} секунд")
            print(f"📊 Успешность: 100.0%")
            return True
        else:
            print("⚠️  ФИНАЛЬНОЕ ПЕРЕМЕЩЕНИЕ ЗАВЕРШЕНО С ОШИБКАМИ!")
            print(f"✅ Успешно: {success_count}")
            print(f"❌ Ошибок: {len(backup_files) - success_count}")
            return False

def main():
    """Главная функция"""
    mover = FinalBackupMover()
    success = mover.run()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())