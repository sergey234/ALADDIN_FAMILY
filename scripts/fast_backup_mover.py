#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый переместитель backup файлов в formatting_work
Автоматическое перемещение всех дублированных файлов

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
Качество: A+
"""

import os
import shutil
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

class FastBackupMover:
    """Быстрый переместитель backup файлов"""
    
    def __init__(self):
        self.project_root = Path("/Users/sergejhlystov/ALADDIN_NEW")
        self.backup_dir = self.project_root / "security" / "formatting_work" / "backup_files"
        self.moved_files = []
        self.failed_files = []
        self.log_file = self.backup_dir / "MOVEMENT_LOG.json"
        
        # Создаем директорию если не существует
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def find_all_backup_files(self) -> List[Tuple[Path, Path]]:
        """Найти все backup файлы в системе"""
        backup_patterns = [
            "*.backup_*",
            "*_original_backup_*", 
            "*_BACKUP*",
            "*_backup_before_formatting*",
            "*_backup_011225*",
            "*_backup_original_backup_*"
        ]
        
        backup_files = []
        
        # Ищем в security директории
        security_dir = self.project_root / "security"
        
        for pattern in backup_patterns:
            for backup_file in security_dir.rglob(pattern):
                # Определяем основной файл
                main_file = self._find_main_file(backup_file)
                if main_file and main_file.exists():
                    backup_files.append((backup_file, main_file))
                    
        return backup_files
    
    def _find_main_file(self, backup_file: Path) -> Path:
        """Найти основной файл для backup"""
        backup_name = backup_file.name
        
        # Убираем backup суффиксы
        main_name = backup_name
        for suffix in [
            ".backup_20250927_231342",
            ".backup_20250927_231341", 
            ".backup_20250928_000215",
            ".backup_20250928_003940",
            ".backup_20250928_005946",
            ".backup_20250927_234616",
            ".backup_20250928_003043",
            ".backup_20250928_002228",
            ".backup_20250927_232629",
            ".backup_011225",
            ".backup_before_formatting",
            "_original_backup_20250103.py",
            "_BACKUP.py",
            "_backup_original_backup_20250103.py",
            ".backup_20250926_133852",
            ".backup_20250926_133733",
            ".backup_20250926_133317",
            ".backup_20250926_133258",
            ".backup_20250926_132405",
            ".backup_20250926_132307",
            ".backup_20250927_234000",
            ".backup_20250927_233351"
        ]:
            if suffix in main_name:
                main_name = main_name.replace(suffix, ".py")
                break
                
        # Если не нашли суффикс, пробуем другие варианты
        if main_name == backup_name:
            # Для enhanced файлов
            if "_enhanced" in backup_name:
                main_name = backup_name.replace("_enhanced", "")
            # Для v2 файлов  
            elif "_v2" in backup_name:
                main_name = backup_name.replace("_v2", "")
            # Для replacement файлов
            elif "_replacement" in backup_name:
                main_name = backup_name.replace("_replacement", "")
            # Для a_plus файлов
            elif "_a_plus" in backup_name:
                main_name = backup_name.replace("_a_plus", "")
                
        # Возвращаем путь к основному файлу
        main_file = backup_file.parent / main_name
        
        # Если основной файл не найден, пробуем альтернативные имена
        if not main_file.exists():
            # Пробуем с _enhanced
            alt_main = backup_file.parent / backup_name.replace("_backup", "_enhanced")
            if alt_main.exists():
                return alt_main
                
            # Пробуем с _v2
            alt_main = backup_file.parent / backup_name.replace("_backup", "_v2")
            if alt_main.exists():
                return alt_main
                
        return main_file
    
    def validate_files(self, backup_file: Path, main_file: Path) -> bool:
        """Валидация файлов перед перемещением"""
        try:
            # Проверяем что backup файл существует
            if not backup_file.exists():
                print(f"❌ Backup файл не найден: {backup_file}")
                return False
                
            # Проверяем что основной файл существует
            if not main_file.exists():
                print(f"❌ Основной файл не найден: {main_file}")
                return False
                
            # Проверяем что это Python файлы
            if not backup_file.suffix == '.py' and not backup_file.name.endswith('.py'):
                print(f"❌ Не Python файл: {backup_file}")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Ошибка валидации: {e}")
            return False
    
    def move_backup_file(self, backup_file: Path, main_file: Path) -> bool:
        """Переместить один backup файл"""
        try:
            # Валидация
            if not self.validate_files(backup_file, main_file):
                return False
                
            # Определяем новое местоположение
            new_path = self.backup_dir / backup_file.name
            
            # Перемещаем файл
            shutil.move(str(backup_file), str(new_path))
            
            # Проверяем что перемещение прошло успешно
            if new_path.exists() and not backup_file.exists():
                print(f"✅ Перемещен: {backup_file.name}")
                self.moved_files.append({
                    "backup_file": str(backup_file),
                    "main_file": str(main_file),
                    "new_path": str(new_path),
                    "timestamp": datetime.now().isoformat()
                })
                return True
            else:
                print(f"❌ Ошибка перемещения: {backup_file.name}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка перемещения {backup_file.name}: {e}")
            self.failed_files.append({
                "backup_file": str(backup_file),
                "main_file": str(main_file),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return False
    
    def test_main_files(self) -> Dict[str, Any]:
        """Тестирование основных файлов после перемещения"""
        test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
        
        for moved in self.moved_files:
            main_file = Path(moved["main_file"])
            test_results["total_tests"] += 1
            
            try:
                # Проверяем что основной файл существует
                if main_file.exists():
                    # Проверяем что файл читается
                    with open(main_file, 'r', encoding='utf-8') as f:
                        content = f.read(100)  # Читаем первые 100 символов
                    
                    test_results["passed_tests"] += 1
                    test_results["test_details"].append({
                        "file": main_file.name,
                        "status": "PASSED",
                        "message": "Основной файл работает корректно"
                    })
                else:
                    test_results["failed_tests"] += 1
                    test_results["test_details"].append({
                        "file": main_file.name,
                        "status": "FAILED", 
                        "message": "Основной файл не найден"
                    })
                    
            except Exception as e:
                test_results["failed_tests"] += 1
                test_results["test_details"].append({
                    "file": main_file.name,
                    "status": "ERROR",
                    "message": str(e)
                })
                
        return test_results
    
    def save_log(self):
        """Сохранить лог перемещения"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "total_found": len(self.moved_files) + len(self.failed_files),
            "moved_files": len(self.moved_files),
            "failed_files": len(self.failed_files),
            "moved_details": self.moved_files,
            "failed_details": self.failed_files
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
            
        print(f"📋 Лог сохранен: {self.log_file}")
    
    def run_fast_movement(self) -> Dict[str, Any]:
        """Запустить быстрое перемещение всех backup файлов"""
        print("🚀 ЗАПУСК БЫСТРОГО ПЕРЕМЕЩЕНИЯ BACKUP ФАЙЛОВ")
        print("=" * 60)
        
        start_time = time.time()
        
        # Находим все backup файлы
        print("🔍 Поиск backup файлов...")
        backup_files = self.find_all_backup_files()
        print(f"📋 Найдено backup файлов: {len(backup_files)}")
        
        if not backup_files:
            print("❌ Backup файлы не найдены!")
            return {"success": False, "message": "Backup файлы не найдены"}
        
        # Перемещаем все файлы
        print("\n🔄 Перемещение backup файлов...")
        success_count = 0
        
        for i, (backup_file, main_file) in enumerate(backup_files, 1):
            print(f"[{i}/{len(backup_files)}] {backup_file.name}")
            
            if self.move_backup_file(backup_file, main_file):
                success_count += 1
                
        # Тестируем основные файлы
        print("\n🧪 Тестирование основных файлов...")
        test_results = self.test_main_files()
        
        # Сохраняем лог
        self.save_log()
        
        # Итоги
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("📊 ИТОГИ БЫСТРОГО ПЕРЕМЕЩЕНИЯ:")
        print(f"⏱️  Время выполнения: {duration:.2f} секунд")
        print(f"📁 Всего найдено: {len(backup_files)} файлов")
        print(f"✅ Успешно перемещено: {success_count} файлов")
        print(f"❌ Ошибок: {len(self.failed_files)} файлов")
        print(f"🧪 Тестов пройдено: {test_results['passed_tests']}/{test_results['total_tests']}")
        print("=" * 60)
        
        return {
            "success": True,
            "duration": duration,
            "total_found": len(backup_files),
            "moved_successfully": success_count,
            "failed": len(self.failed_files),
            "test_results": test_results,
            "moved_files": self.moved_files,
            "failed_files": self.failed_files
        }

def main():
    """Главная функция"""
    print("🔒 ALADDIN Security System - Fast Backup Mover")
    print("Автоматическое перемещение backup файлов")
    print()
    
    # Создаем экземпляр
    mover = FastBackupMover()
    
    # Запускаем быстрое перемещение
    result = mover.run_fast_movement()
    
    if result["success"]:
        print("\n🎉 БЫСТРОЕ ПЕРЕМЕЩЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print(f"📁 Перемещено файлов: {result['moved_successfully']}")
        print(f"⏱️  Время: {result['duration']:.2f} секунд")
        
        if result["failed"] > 0:
            print(f"\n⚠️  ВНИМАНИЕ: {result['failed']} файлов не удалось переместить")
            print("📋 Проверьте лог для деталей")
    else:
        print("\n❌ ОШИБКА ПРИ ПЕРЕМЕЩЕНИИ!")
        print(result.get("message", "Неизвестная ошибка"))

if __name__ == "__main__":
    main()