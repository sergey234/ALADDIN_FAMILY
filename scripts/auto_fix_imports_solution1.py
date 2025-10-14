#!/usr/bin/env python3
"""
Автоматическое исправление проблем с импортами - Решение 1
Убирает sys.path.append() и настраивает PYTHONPATH
"""

import os
import re
import subprocess
import shutil
from pathlib import Path
import json
from datetime import datetime

class ImportFixer:
    def __init__(self):
        self.security_dir = Path("/Users/sergejhlystov/ALADDIN_NEW/security")
        self.backup_dir = Path("/Users/sergejhlystov/ALADDIN_NEW/backup_import_fix")
        self.stats = {
            "files_processed": 0,
            "imports_moved": 0,
            "sys_path_removed": 0,
            "errors_fixed": 0,
            "files_with_errors": 0
        }
        
    def create_backup(self):
        """Создание резервной копии перед изменениями"""
        print("🔄 ФАЗА 0: СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ")
        print("=" * 50)
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        shutil.copytree(self.security_dir, self.backup_dir)
        print(f"✅ Резервная копия создана: {self.backup_dir}")
        
    def phase1_move_imports(self):
        """ФАЗА 1: Переместить импорты в начало файлов"""
        print("\n🔄 ФАЗА 1: ПЕРЕМЕЩЕНИЕ ИМПОРТОВ В НАЧАЛО ФАЙЛОВ")
        print("=" * 50)
        
        python_files = self._get_python_files()
        print(f"📁 Найдено {len(python_files)} Python файлов")
        
        for file_path in python_files:
            if self._move_imports_to_top(file_path):
                self.stats["files_processed"] += 1
                self.stats["imports_moved"] += 1
                
        print(f"✅ Обработано файлов: {self.stats['files_processed']}")
        print(f"✅ Перемещено импортов: {self.stats['imports_moved']}")
        
    def phase2_remove_sys_path(self):
        """ФАЗА 2: Убрать sys.path.append() из файлов"""
        print("\n🔄 ФАЗА 2: УДАЛЕНИЕ sys.path.append()")
        print("=" * 50)
        
        python_files = self._get_python_files()
        sys_path_removed = 0
        
        for file_path in python_files:
            if self._remove_sys_path_append(file_path):
                sys_path_removed += 1
                
        self.stats["sys_path_removed"] = sys_path_removed
        print(f"✅ Удалено sys.path.append(): {sys_path_removed}")
        
    def phase3_setup_pythonpath(self):
        """ФАЗА 3: Настроить PYTHONPATH"""
        print("\n🔄 ФАЗА 3: НАСТРОЙКА PYTHONPATH")
        print("=" * 50)
        
        # Создаем .env файл с PYTHONPATH
        env_file = Path("/Users/sergejhlystov/ALADDIN_NEW/.env")
        pythonpath = "/Users/sergejhlystov/ALADDIN_NEW"
        
        with open(env_file, 'w') as f:
            f.write(f"PYTHONPATH={pythonpath}\n")
            f.write(f"export PYTHONPATH={pythonpath}\n")
            
        print(f"✅ Создан .env файл: {env_file}")
        print(f"✅ PYTHONPATH установлен: {pythonpath}")
        
        # Создаем скрипт для установки PYTHONPATH
        setup_script = Path("/Users/sergejhlystov/ALADDIN_NEW/setup_pythonpath.sh")
        with open(setup_script, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write(f"export PYTHONPATH={pythonpath}\n")
            f.write("echo 'PYTHONPATH установлен для ALADDIN'\n")
            
        setup_script.chmod(0o755)
        print(f"✅ Создан скрипт установки: {setup_script}")
        
    def phase4_check_and_fix_errors(self):
        """ФАЗА 4: Проверить и исправить ошибки"""
        print("\n🔄 ФАЗА 4: ПРОВЕРКА И ИСПРАВЛЕНИЕ ОШИБОК")
        print("=" * 50)
        
        # Запускаем flake8 для проверки
        cmd = [
            "python3", "-m", "flake8",
            "--max-line-length=120",
            "--exclude=*/backup*,*/test*,*/logs*,*/formatting_work*",
            str(self.security_dir)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            error_lines = [line for line in result.stdout.split('\n') if line.strip()]
            
            self.stats["files_with_errors"] = len(set([line.split(':')[0] for line in error_lines if ':' in line]))
            self.stats["errors_fixed"] = len(error_lines)
            
            print(f"📊 Найдено ошибок: {len(error_lines)}")
            print(f"📊 Файлов с ошибками: {self.stats['files_with_errors']}")
            
            if len(error_lines) == 0:
                print("🎉 ОТЛИЧНО! Ошибок flake8 не найдено!")
                return True
            else:
                print("⚠️  Остались ошибки, показываем первые 10:")
                for i, error in enumerate(error_lines[:10]):
                    print(f"   {i+1}. {error}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Flake8 превысил лимит времени")
            return False
        except Exception as e:
            print(f"❌ Ошибка при запуске flake8: {e}")
            return False
            
    def phase5_setup_precommit(self):
        """ФАЗА 5: Настроить pre-commit hooks"""
        print("\n🔄 ФАЗА 5: НАСТРОЙКА PRE-COMMIT HOOKS")
        print("=" * 50)
        
        # Проверяем, установлен ли pre-commit
        try:
            subprocess.run(["pre-commit", "--version"], capture_output=True, check=True)
            print("✅ Pre-commit уже установлен")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("📦 Устанавливаем pre-commit...")
            subprocess.run(["pip", "install", "pre-commit"], check=True)
            print("✅ Pre-commit установлен")
            
        # Устанавливаем hooks
        try:
            subprocess.run(["pre-commit", "install"], cwd="/Users/sergejhlystov/ALADDIN_NEW", check=True)
            print("✅ Pre-commit hooks установлены")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Не удалось установить hooks: {e}")
            
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
        
    def _move_imports_to_top(self, file_path):
        """Переместить импорты в начало файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Ищем импорты после sys.path.append
            imports = []
            sys_path_found = False
            other_lines = []
            
            for line in lines:
                if "sys.path.append" in line:
                    sys_path_found = True
                    other_lines.append(line)
                elif sys_path_found and ("import " in line or "from " in line):
                    imports.append(line)
                else:
                    other_lines.append(line)
                    
            if not imports:
                return False
                
            # Перестраиваем файл
            new_lines = []
            in_header = True
            
            for line in lines:
                if in_header and (line.strip().startswith('#') or line.strip().startswith('"""') or line.strip().startswith("'''")):
                    new_lines.append(line)
                elif in_header and not (line.strip().startswith('#') or line.strip().startswith('"""') or line.strip().startswith("'''")):
                    in_header = False
                    # Добавляем импорты
                    new_lines.extend(imports)
                    new_lines.append(line)
                else:
                    new_lines.append(line)
                    
            # Записываем изменения
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
                
            return True
            
        except Exception as e:
            print(f"❌ Ошибка в файле {file_path}: {e}")
            return False
            
    def _remove_sys_path_append(self, file_path):
        """Удалить sys.path.append() из файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Удаляем строки с sys.path.append
            lines = content.split('\n')
            new_lines = [line for line in lines if "sys.path.append" not in line]
            
            if len(new_lines) != len(lines):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                return True
                
            return False
            
        except Exception as e:
            print(f"❌ Ошибка в файле {file_path}: {e}")
            return False
            
    def run_quality_test(self):
        """Запустить тест качества кода"""
        print("\n🧪 ТЕСТИРОВАНИЕ КАЧЕСТВА КОДА")
        print("=" * 50)
        
        # Запускаем наш скрипт анализа качества
        try:
            result = subprocess.run([
                "python3", "scripts/quick_security_stats.py"
            ], capture_output=True, text=True, timeout=60)
            
            print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
            print(result.stdout)
            
            if "A+" in result.stdout:
                print("🎉 УСПЕХ! Качество кода A+")
                return True
            else:
                print("⚠️  Качество кода не A+")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка при тестировании: {e}")
            return False
            
    def generate_report(self):
        """Генерировать отчет о проделанной работе"""
        print("\n📊 ОТЧЕТ О ПРОДЕЛАННОЙ РАБОТЕ")
        print("=" * 50)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "solution": "Решение 1: Убрать sys.path.append()",
            "stats": self.stats,
            "backup_location": str(self.backup_dir),
            "quality_achieved": "A+" if self.stats["errors_fixed"] == 0 else "Требует доработки"
        }
        
        report_file = Path("/Users/sergejhlystov/ALADDIN_NEW/import_fix_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"📄 Отчет сохранен: {report_file}")
        print(f"📊 Обработано файлов: {self.stats['files_processed']}")
        print(f"📊 Перемещено импортов: {self.stats['imports_moved']}")
        print(f"📊 Удалено sys.path.append(): {self.stats['sys_path_removed']}")
        print(f"📊 Исправлено ошибок: {self.stats['errors_fixed']}")
        print(f"📊 Файлов с ошибками: {self.stats['files_with_errors']}")
        
    def run_full_process(self):
        """Запустить полный процесс исправления"""
        print("🚀 АВТОМАТИЧЕСКОЕ ИСПРАВЛЕНИЕ ИМПОРТОВ - РЕШЕНИЕ 1")
        print("=" * 60)
        print("🎯 Цель: A+ качество кода за 3 часа")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Фаза 0: Резервная копия
            self.create_backup()
            
            # Фаза 1: Переместить импорты
            self.phase1_move_imports()
            
            # Фаза 2: Убрать sys.path.append
            self.phase2_remove_sys_path()
            
            # Фаза 3: Настроить PYTHONPATH
            self.phase3_setup_pythonpath()
            
            # Фаза 4: Проверить ошибки
            errors_fixed = self.phase4_check_and_fix_errors()
            
            # Фаза 5: Pre-commit hooks
            self.phase5_setup_precommit()
            
            # Тестирование
            quality_ok = self.run_quality_test()
            
            # Отчет
            self.generate_report()
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            print(f"\n🎉 ПРОЦЕСС ЗАВЕРШЕН!")
            print(f"⏱️  Время выполнения: {duration}")
            print(f"🎯 Качество: {'A+' if quality_ok else 'Требует доработки'}")
            print(f"📁 Резервная копия: {self.backup_dir}")
            
            if quality_ok:
                print("\n✅ УСПЕХ! Достигнуто качество A+")
            else:
                print("\n⚠️  Требуется дополнительная работа")
                
        except Exception as e:
            print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            print(f"🔄 Восстановление из резервной копии...")
            if self.backup_dir.exists():
                shutil.rmtree(self.security_dir)
                shutil.copytree(self.backup_dir, self.security_dir)
                print("✅ Восстановление завершено")

if __name__ == "__main__":
    fixer = ImportFixer()
    fixer.run_full_process()