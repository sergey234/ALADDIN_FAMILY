#!/usr/bin/env python3
"""
🔒 МЕНЕДЖЕР СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN
========================================

Главный скрипт для управления всеми анализаторами системы безопасности.
Объединяет все инструменты анализа в одном месте.

Автор: AI Assistant
Дата: 2024
Версия: 1.0
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

class SecuritySystemManager:
    """Менеджер системы безопасности"""
    
    def __init__(self):
        self.scripts_dir = Path("scripts")
        self.analyzers = {
            'comprehensive': 'comprehensive_security_analyzer.py',
            'quick_finder': 'quick_function_finder.py',
            'sfm_scanner': 'sfm_function_scanner.py'
        }
        self.results_dir = Path("analysis_results")
        self.results_dir.mkdir(exist_ok=True)

    def print_menu(self) -> None:
        """Выводит главное меню"""
        print("\n🔒 МЕНЕДЖЕР СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN")
        print("=" * 50)
        print("Выберите действие:")
        print("1. 🔍 Полный анализ системы безопасности")
        print("2. ⚡ Быстрый поиск функций")
        print("3. 🔧 Сканирование SFM функций")
        print("4. 📊 Показать статистику")
        print("5. 🚀 Запустить все анализаторы")
        print("6. 📁 Показать результаты")
        print("7. 🧹 Очистить результаты")
        print("0. ❌ Выход")
        print("-" * 50)

    def run_analyzer(self, analyzer_name: str) -> bool:
        """Запускает анализатор"""
        if analyzer_name not in self.analyzers:
            print(f"❌ Анализатор {analyzer_name} не найден!")
            return False
        
        script_path = self.scripts_dir / self.analyzers[analyzer_name]
        
        if not script_path.exists():
            print(f"❌ Скрипт {script_path} не найден!")
            return False
        
        print(f"🚀 Запускаю {analyzer_name}...")
        
        try:
            # Переходим в директорию результатов
            os.chdir(self.results_dir)
            
            # Запускаем скрипт
            result = subprocess.run([
                sys.executable, 
                str(script_path.absolute())
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                print("✅ Анализатор выполнен успешно!")
                if result.stdout:
                    print("📄 Вывод:")
                    print(result.stdout)
                return True
            else:
                print("❌ Ошибка выполнения анализатора!")
                if result.stderr:
                    print("📄 Ошибки:")
                    print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Исключение при запуске: {e}")
            return False
        finally:
            # Возвращаемся в исходную директорию
            os.chdir("..")

    def show_statistics(self) -> None:
        """Показывает статистику системы"""
        print("\n📊 СТАТИСТИКА СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN")
        print("=" * 50)
        
        # Подсчитываем файлы
        total_files = 0
        python_files = 0
        directories = {}
        
        for root, dirs, files in os.walk("."):
            # Исключаем ненужные директории
            dirs[:] = [d for d in dirs if d.lower() not in {
                'backups', 'tests', 'logs', 'formatting_work', 
                '__pycache__', '.git', '.pytest_cache', 'node_modules',
                'venv', 'env', '.env', 'temp', 'tmp', 'analysis_results'
            }]
            
            for file in files:
                total_files += 1
                if file.endswith('.py'):
                    python_files += 1
                
                # Подсчитываем по директориям
                rel_path = Path(root).relative_to(".")
                if str(rel_path) not in directories:
                    directories[str(rel_path)] = 0
                directories[str(rel_path)] += 1
        
        print(f"📄 Всего файлов: {total_files}")
        print(f"🐍 Python файлов: {python_files}")
        print(f"📁 Директорий: {len(directories)}")
        
        print(f"\n📁 Топ директорий по количеству файлов:")
        sorted_dirs = sorted(directories.items(), key=lambda x: x[1], reverse=True)
        for dir_path, count in sorted_dirs[:10]:
            if count > 0:
                print(f"   {dir_path}: {count} файлов")

    def show_results(self) -> None:
        """Показывает результаты анализа"""
        print("\n📁 РЕЗУЛЬТАТЫ АНАЛИЗА")
        print("=" * 30)
        
        if not self.results_dir.exists():
            print("❌ Директория результатов не найдена!")
            return
        
        files = list(self.results_dir.glob("*"))
        if not files:
            print("📭 Результаты не найдены!")
            return
        
        print(f"📄 Найдено файлов: {len(files)}")
        for file in sorted(files):
            size = file.stat().st_size
            print(f"   {file.name} ({size:,} байт)")

    def clear_results(self) -> None:
        """Очищает результаты анализа"""
        if not self.results_dir.exists():
            print("📭 Результаты уже очищены!")
            return
        
        try:
            import shutil
            shutil.rmtree(self.results_dir)
            self.results_dir.mkdir(exist_ok=True)
            print("✅ Результаты очищены!")
        except Exception as e:
            print(f"❌ Ошибка при очистке: {e}")

    def run_all_analyzers(self) -> None:
        """Запускает все анализаторы"""
        print("\n🚀 ЗАПУСК ВСЕХ АНАЛИЗАТОРОВ")
        print("=" * 40)
        
        success_count = 0
        total_count = len(self.analyzers)
        
        for analyzer_name in self.analyzers:
            print(f"\n🔍 Запускаю {analyzer_name}...")
            if self.run_analyzer(analyzer_name):
                success_count += 1
            print("-" * 30)
        
        print(f"\n📊 РЕЗУЛЬТАТЫ:")
        print(f"   ✅ Успешно: {success_count}/{total_count}")
        print(f"   ❌ Ошибок: {total_count - success_count}/{total_count}")

    def run(self) -> None:
        """Главный цикл программы"""
        while True:
            self.print_menu()
            
            try:
                choice = input("\nВведите номер действия: ").strip()
                
                if choice == "0":
                    print("👋 До свидания!")
                    break
                elif choice == "1":
                    self.run_analyzer('comprehensive')
                elif choice == "2":
                    self.run_analyzer('quick_finder')
                elif choice == "3":
                    self.run_analyzer('sfm_scanner')
                elif choice == "4":
                    self.show_statistics()
                elif choice == "5":
                    self.run_all_analyzers()
                elif choice == "6":
                    self.show_results()
                elif choice == "7":
                    self.clear_results()
                else:
                    print("❌ Неверный выбор! Попробуйте снова.")
                
                input("\nНажмите Enter для продолжения...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Программа прервана пользователем!")
                break
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")
                input("Нажмите Enter для продолжения...")

def main():
    """Главная функция"""
    print("🔒 МЕНЕДЖЕР СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN")
    print("=" * 50)
    print("Версия: 1.0")
    print("Дата:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Проверяем, что мы в правильной директории
    if not Path("scripts").exists():
        print("❌ Ошибка: Запустите скрипт из корневой директории ALADDIN_NEW!")
        return
    
    # Создаем менеджер и запускаем
    manager = SecuritySystemManager()
    manager.run()

if __name__ == "__main__":
    main()