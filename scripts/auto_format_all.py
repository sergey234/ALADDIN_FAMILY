#!/usr/bin/env python3
"""
Автоматическое форматирование всех Python файлов в системе ALADDIN
Исправляет ошибки длины строк, импорты и стиль кода
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

class AutoFormatter:
    def __init__(self, project_root="/Users/sergejhlystov/ALADDIN_NEW"):
        self.project_root = Path(project_root)
        self.security_dir = self.project_root / "security"
        self.scripts_dir = self.project_root / "scripts"
        self.core_dir = self.project_root / "core"
        self.config_dir = self.project_root / "config"
        
        # Исключаемые директории
        self.exclude_dirs = {
            "backup", "backups", "test", "tests", "logs", 
            "formatting_work", "__pycache__", ".git"
        }
        
        self.stats = {
            "files_processed": 0,
            "files_fixed": 0,
            "errors_fixed": 0,
            "start_time": datetime.now()
        }

    def find_python_files(self):
        """Найти все Python файлы для форматирования"""
        python_files = []
        
        for directory in [self.security_dir, self.scripts_dir, self.core_dir, self.config_dir]:
            if directory.exists():
                for file_path in directory.rglob("*.py"):
                    # Проверить, не в исключаемой директории
                    if not any(exclude in str(file_path) for exclude in self.exclude_dirs):
                        python_files.append(file_path)
        
        return python_files

    def run_black(self, file_path):
        """Запустить black для форматирования"""
        try:
            result = subprocess.run([
                "black", 
                "--line-length=120",
                "--quiet",
                str(file_path)
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0, result.stderr
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)

    def run_autopep8(self, file_path):
        """Запустить autopep8 для исправления PEP8 ошибок"""
        try:
            result = subprocess.run([
                "autopep8",
                "--in-place",
                "--max-line-length=120",
                "--aggressive",
                "--aggressive",
                str(file_path)
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0, result.stderr
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)

    def run_isort(self, file_path):
        """Запустить isort для сортировки импортов"""
        try:
            result = subprocess.run([
                "isort",
                "--profile=black",
                "--line-length=120",
                str(file_path)
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0, result.stderr
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)

    def check_flake8_errors(self, file_path):
        """Проверить ошибки flake8"""
        try:
            result = subprocess.run([
                "flake8",
                "--max-line-length=120",
                "--exclude=*/backup*,*/test*,*/logs*,*/formatting_work*",
                str(file_path)
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode, result.stdout
        except subprocess.TimeoutExpired:
            return 1, "Timeout"
        except Exception as e:
            return 1, str(e)

    def format_file(self, file_path):
        """Отформатировать один файл"""
        print(f"🔧 Форматирование: {file_path.relative_to(self.project_root)}")
        
        # Проверить ошибки до форматирования
        exit_code, errors_before = self.check_flake8_errors(file_path)
        error_count_before = len(errors_before.split('\n')) if errors_before else 0
        
        # Применить форматирование
        tools = [
            ("isort", self.run_isort),
            ("autopep8", self.run_autopep8),
            ("black", self.run_black)
        ]
        
        for tool_name, tool_func in tools:
            success, error = tool_func(file_path)
            if not success:
                print(f"⚠️  {tool_name} ошибка: {error}")
        
        # Проверить ошибки после форматирования
        exit_code, errors_after = self.check_flake8_errors(file_path)
        error_count_after = len(errors_after.split('\n')) if errors_after else 0
        
        errors_fixed = error_count_before - error_count_after
        self.stats["files_processed"] += 1
        
        if errors_fixed > 0:
            self.stats["files_fixed"] += 1
            self.stats["errors_fixed"] += errors_fixed
            print(f"✅ Исправлено {errors_fixed} ошибок")
        else:
            print("✅ Файл уже отформатирован")
        
        return errors_fixed

    def format_all(self, dry_run=False):
        """Отформатировать все файлы"""
        print("🚀 АВТОМАТИЧЕСКОЕ ФОРМАТИРОВАНИЕ ALADDIN")
        print("=" * 50)
        
        python_files = self.find_python_files()
        print(f"📁 Найдено {len(python_files)} Python файлов")
        
        if dry_run:
            print("🔍 РЕЖИМ ПРЕДВАРИТЕЛЬНОГО ПРОСМОТРА")
            for file_path in python_files:
                exit_code, errors = self.check_flake8_errors(file_path)
                if exit_code != 0:
                    print(f"⚠️  {file_path.relative_to(self.project_root)}: {len(errors.split())} ошибок")
            return
        
        print("🔧 Начинаем форматирование...")
        
        for file_path in python_files:
            try:
                self.format_file(file_path)
            except Exception as e:
                print(f"❌ Ошибка при форматировании {file_path}: {e}")
        
        self.print_summary()

    def print_summary(self):
        """Вывести сводку результатов"""
        duration = datetime.now() - self.stats["start_time"]
        
        print("\n" + "=" * 50)
        print("📊 СВОДКА ФОРМАТИРОВАНИЯ")
        print("=" * 50)
        print(f"⏱️  Время выполнения: {duration.total_seconds():.2f} сек")
        print(f"📁 Файлов обработано: {self.stats['files_processed']}")
        print(f"✅ Файлов исправлено: {self.stats['files_fixed']}")
        print(f"🔧 Ошибок исправлено: {self.stats['errors_fixed']}")
        
        if self.stats['files_processed'] > 0:
            success_rate = (self.stats['files_fixed'] / self.stats['files_processed']) * 100
            print(f"📈 Процент успеха: {success_rate:.1f}%")
        
        print("=" * 50)

    def setup_precommit(self):
        """Настроить pre-commit hooks"""
        print("🔧 Настройка pre-commit hooks...")
        
        try:
            # Установить pre-commit hooks
            result = subprocess.run([
                "pre-commit", "install"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Pre-commit hooks установлены")
            else:
                print(f"❌ Ошибка установки pre-commit: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def main():
    parser = argparse.ArgumentParser(description="Автоматическое форматирование ALADDIN")
    parser.add_argument("--dry-run", action="store_true", help="Только показать файлы с ошибками")
    parser.add_argument("--setup-precommit", action="store_true", help="Настроить pre-commit hooks")
    parser.add_argument("--project-root", default="/Users/sergejhlystov/ALADDIN_NEW", 
                       help="Корневая директория проекта")
    
    args = parser.parse_args()
    
    formatter = AutoFormatter(args.project_root)
    
    if args.setup_precommit:
        formatter.setup_precommit()
    else:
        formatter.format_all(dry_run=args.dry_run)

if __name__ == "__main__":
    main()