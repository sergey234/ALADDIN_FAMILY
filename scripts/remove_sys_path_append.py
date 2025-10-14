#!/usr/bin/env python3
"""
ФАЗА 2: Убрать sys.path.append() из файлов
Простой и надежный скрипт только для удаления sys.path.append()
"""

import os
import re
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class SysPathRemover:
    def __init__(self):
        self.security_dir = Path("/Users/sergejhlystov/ALADDIN_NEW/security")
        self.backup_dir = Path("/Users/sergejhlystov/ALADDIN_NEW/backup_sys_path_removal")
        self.stats = {
            "files_processed": 0,
            "sys_path_removed": 0,
            "files_with_sys_path": 0
        }
        
    def create_backup(self):
        """Создание резервной копии перед изменениями"""
        print("🔄 ФАЗА 0: СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ")
        print("=" * 50)
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        shutil.copytree(self.security_dir, self.backup_dir)
        print(f"✅ Резервная копия создана: {self.backup_dir}")
        
    def find_files_with_sys_path(self):
        """Найти все файлы с sys.path.append()"""
        print("\n🔍 ПОИСК ФАЙЛОВ С sys.path.append()")
        print("=" * 50)
        
        python_files = self._get_python_files()
        files_with_sys_path = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "sys.path.append" in content:
                        files_with_sys_path.append(file_path)
                        self.stats["files_with_sys_path"] += 1
            except Exception as e:
                print(f"⚠️  Ошибка чтения файла {file_path}: {e}")
                
        print(f"📊 Найдено файлов с sys.path.append(): {len(files_with_sys_path)}")
        
        if files_with_sys_path:
            print("📋 Файлы с sys.path.append():")
            for i, file_path in enumerate(files_with_sys_path[:10]):  # Показываем первые 10
                print(f"   {i+1}. {file_path}")
            if len(files_with_sys_path) > 10:
                print(f"   ... и еще {len(files_with_sys_path) - 10} файлов")
                
        return files_with_sys_path
        
    def remove_sys_path_from_file(self, file_path):
        """Удалить sys.path.append() из одного файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            new_lines = []
            removed_count = 0
            
            for line in lines:
                if "sys.path.append" in line:
                    # Удаляем строку с sys.path.append()
                    removed_count += 1
                    print(f"   🗑️  Удалено: {line.strip()}")
                else:
                    new_lines.append(line)
                    
            if removed_count > 0:
                # Записываем файл без sys.path.append()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                    
                self.stats["sys_path_removed"] += removed_count
                return True
                
            return False
            
        except Exception as e:
            print(f"❌ Ошибка при обработке файла {file_path}: {e}")
            return False
            
    def remove_sys_path_from_all_files(self):
        """Удалить sys.path.append() из всех файлов"""
        print("\n🔧 УДАЛЕНИЕ sys.path.append() ИЗ ВСЕХ ФАЙЛОВ")
        print("=" * 50)
        
        files_with_sys_path = self.find_files_with_sys_path()
        
        if not files_with_sys_path:
            print("✅ Файлов с sys.path.append() не найдено")
            return
            
        for file_path in files_with_sys_path:
            print(f"\n📄 Обработка: {file_path}")
            if self.remove_sys_path_from_file(file_path):
                self.stats["files_processed"] += 1
                print(f"   ✅ Обработан успешно")
            else:
                print(f"   ⚠️  Не требует изменений")
                
    def verify_removal(self):
        """Проверить, что sys.path.append() удален"""
        print("\n🔍 ПРОВЕРКА УДАЛЕНИЯ sys.path.append()")
        print("=" * 50)
        
        python_files = self._get_python_files()
        remaining_files = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "sys.path.append" in content:
                        remaining_files.append(file_path)
            except Exception as e:
                print(f"⚠️  Ошибка чтения файла {file_path}: {e}")
                
        if remaining_files:
            print(f"⚠️  Остались файлы с sys.path.append(): {len(remaining_files)}")
            for file_path in remaining_files:
                print(f"   • {file_path}")
        else:
            print("✅ Все sys.path.append() успешно удалены!")
            
    def _get_python_files(self):
        """Получить список Python файлов для обработки"""
        exclude_patterns = [
            "*/backup*", "*/test*", "*/logs*", "*/formatting_work*",
            "*_backup_*.py", "*_original_backup_*.py", "*_BACKUP.py",
            "test_*.py"
        ]
        
        python_files = []
        for p in self.security_dir.rglob("*.py"):
            if not any(re.search(pattern.replace('*', '.*'), str(p)) for pattern in exclude_patterns):
                python_files.append(p)
                
        return python_files
        
    def generate_report(self):
        """Генерировать отчет о проделанной работе"""
        print("\n📊 ОТЧЕТ О ПРОДЕЛАННОЙ РАБОТЕ")
        print("=" * 50)
        
        print(f"📈 РЕЗУЛЬТАТЫ:")
        print(f"   • Обработано файлов: {self.stats['files_processed']}")
        print(f"   • Удалено sys.path.append(): {self.stats['sys_path_removed']}")
        print(f"   • Файлов с sys.path.append(): {self.stats['files_with_sys_path']}")
        print(f"   • Резервная копия: {self.backup_dir}")
        
        if self.stats["sys_path_removed"] > 0:
            print(f"\n✅ УСПЕХ! Удалено {self.stats['sys_path_removed']} строк с sys.path.append()")
        else:
            print(f"\nℹ️  Файлов с sys.path.append() не найдено")
            
    def run_phase2(self):
        """Запустить ФАЗУ 2: Убрать sys.path.append() из файлов"""
        print("🚀 ФАЗА 2: УДАЛЕНИЕ sys.path.append() ИЗ ФАЙЛОВ")
        print("=" * 60)
        print("🎯 Цель: Убрать все sys.path.append() из кода")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Создаем резервную копию
            self.create_backup()
            
            # Удаляем sys.path.append() из всех файлов
            self.remove_sys_path_from_all_files()
            
            # Проверяем результат
            self.verify_removal()
            
            # Генерируем отчет
            self.generate_report()
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            print(f"\n⏱️  Время выполнения: {duration}")
            print(f"\n🎯 ФАЗА 2 ЗАВЕРШЕНА!")
            print(f"📋 СЛЕДУЮЩИЕ ШАГИ (ВРУЧНУЮ):")
            print(f"   • ФАЗА 1: Переместить импорты в начало файлов")
            print(f"   • ФАЗА 3: Настроить PYTHONPATH")
            print(f"   • ФАЗА 4: Проверить и исправить ошибки")
            print(f"   • ФАЗА 5: Настроить pre-commit hooks")
            
        except Exception as e:
            print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            print(f"🔄 Восстановление из резервной копии...")
            if self.backup_dir.exists():
                shutil.rmtree(self.security_dir)
                shutil.copytree(self.backup_dir, self.security_dir)
                print("✅ Восстановление завершено")

if __name__ == "__main__":
    remover = SysPathRemover()
    remover.run_phase2()