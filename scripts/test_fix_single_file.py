#!/usr/bin/env python3
"""
Тестирование исправления импортов на одном файле
"""

import os
import re
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class SingleFileFixer:
    def __init__(self, target_file):
        self.target_file = Path(target_file)
        self.backup_file = self.target_file.with_suffix('.py.backup')
        self.stats = {
            "imports_moved": 0,
            "sys_path_removed": 0,
            "errors_before": 0,
            "errors_after": 0
        }
        
    def create_backup(self):
        """Создание резервной копии файла"""
        print(f"🔄 СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ: {self.target_file}")
        print("=" * 60)
        
        shutil.copy2(self.target_file, self.backup_file)
        print(f"✅ Резервная копия создана: {self.backup_file}")
        
    def check_errors_before(self):
        """Проверить ошибки ДО исправления"""
        print(f"\n🔍 ПРОВЕРКА ОШИБОК ДО ИСПРАВЛЕНИЯ")
        print("=" * 60)
        
        cmd = [
            "python3", "-m", "flake8",
            "--max-line-length=120",
            str(self.target_file)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            error_lines = [line for line in result.stdout.split('\n') if line.strip()]
            self.stats["errors_before"] = len(error_lines)
            
            print(f"📊 Найдено ошибок: {len(error_lines)}")
            
            if error_lines:
                print("📋 Первые 10 ошибок:")
                for i, error in enumerate(error_lines[:10]):
                    print(f"   {i+1}. {error}")
                    
                # Подсчет типов ошибок
                error_types = {}
                for line in error_lines:
                    match = re.match(r".*:(\d+):(\d+): ([A-Z]\d+)", line)
                    if match:
                        error_code = match.group(3)
                        error_types[error_code] = error_types.get(error_code, 0) + 1
                
                print(f"\n📊 ТИПЫ ОШИБОК:")
                for code, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                    print(f"   • {code}: {count} ошибок")
                    
            return len(error_lines)
            
        except subprocess.TimeoutExpired:
            print("❌ Flake8 превысил лимит времени")
            return 0
        except Exception as e:
            print(f"❌ Ошибка при запуске flake8: {e}")
            return 0
            
    def fix_imports(self):
        """Исправить импорты в файле"""
        print(f"\n🔧 ИСПРАВЛЕНИЕ ИМПОРТОВ В {self.target_file}")
        print("=" * 60)
        
        try:
            with open(self.target_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            print(f"📄 Исходный файл: {len(lines)} строк")
            
            # Анализируем структуру файла
            imports = []
            sys_path_lines = []
            other_lines = []
            in_header = True
            
            for i, line in enumerate(lines):
                if in_header and (line.strip().startswith('#') or line.strip().startswith('"""') or line.strip().startswith("'''")):
                    other_lines.append((i, line))
                elif in_header and not (line.strip().startswith('#') or line.strip().startswith('"""') or line.strip().startswith("'''")):
                    in_header = False
                    other_lines.append((i, line))
                elif "sys.path.append" in line:
                    sys_path_lines.append((i, line))
                elif "import " in line or "from " in line:
                    imports.append((i, line))
                else:
                    other_lines.append((i, line))
                    
            print(f"📊 Анализ файла:")
            print(f"   • Импорты: {len(imports)}")
            print(f"   • sys.path.append: {len(sys_path_lines)}")
            print(f"   • Остальные строки: {len(other_lines)}")
            
            if not imports and not sys_path_lines:
                print("✅ Файл не требует исправления")
                return False
                
            # Показываем проблемные строки
            if sys_path_lines:
                print(f"\n🚨 НАЙДЕНЫ sys.path.append:")
                for i, line in sys_path_lines:
                    print(f"   Строка {i+1}: {line.strip()}")
                    
            if imports:
                print(f"\n📦 НАЙДЕНЫ ИМПОРТЫ:")
                for i, line in imports[:5]:  # Показываем первые 5
                    print(f"   Строка {i+1}: {line.strip()}")
                if len(imports) > 5:
                    print(f"   ... и еще {len(imports) - 5} импортов")
                    
            # Исправляем файл
            new_lines = []
            
            # Добавляем заголовок
            header_end = 0
            for i, line in other_lines:
                if not (line.strip().startswith('#') or line.strip().startswith('"""') or line.strip().startswith("'''")):
                    header_end = i
                    break
                new_lines.append(line)
                
            # Добавляем импорты (если есть)
            if imports:
                new_lines.extend([line for _, line in imports])
                self.stats["imports_moved"] = len(imports)
                
            # Добавляем остальные строки (исключая sys.path.append)
            for i, line in other_lines:
                if "sys.path.append" not in line:
                    new_lines.append(line)
                else:
                    self.stats["sys_path_removed"] += 1
                    
            # Записываем исправленный файл
            with open(self.target_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
                
            print(f"✅ Файл исправлен:")
            print(f"   • Перемещено импортов: {self.stats['imports_moved']}")
            print(f"   • Удалено sys.path.append: {self.stats['sys_path_removed']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при исправлении файла: {e}")
            return False
            
    def check_errors_after(self):
        """Проверить ошибки ПОСЛЕ исправления"""
        print(f"\n🔍 ПРОВЕРКА ОШИБОК ПОСЛЕ ИСПРАВЛЕНИЯ")
        print("=" * 60)
        
        cmd = [
            "python3", "-m", "flake8",
            "--max-line-length=120",
            str(self.target_file)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            error_lines = [line for line in result.stdout.split('\n') if line.strip()]
            self.stats["errors_after"] = len(error_lines)
            
            print(f"📊 Найдено ошибок: {len(error_lines)}")
            
            if error_lines:
                print("📋 Оставшиеся ошибки:")
                for i, error in enumerate(error_lines[:10]):
                    print(f"   {i+1}. {error}")
                    
                # Подсчет типов ошибок
                error_types = {}
                for line in error_lines:
                    match = re.match(r".*:(\d+):(\d+): ([A-Z]\d+)", line)
                    if match:
                        error_code = match.group(3)
                        error_types[error_code] = error_types.get(error_code, 0) + 1
                
                print(f"\n📊 ТИПЫ ОСТАВШИХСЯ ОШИБОК:")
                for code, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                    print(f"   • {code}: {count} ошибок")
            else:
                print("🎉 ОТЛИЧНО! Ошибок flake8 не найдено!")
                
            return len(error_lines)
            
        except subprocess.TimeoutExpired:
            print("❌ Flake8 превысил лимит времени")
            return 0
        except Exception as e:
            print(f"❌ Ошибка при запуске flake8: {e}")
            return 0
            
    def show_comparison(self):
        """Показать сравнение ДО и ПОСЛЕ"""
        print(f"\n📊 СРАВНЕНИЕ РЕЗУЛЬТАТОВ")
        print("=" * 60)
        
        errors_fixed = self.stats["errors_before"] - self.stats["errors_after"]
        improvement = (errors_fixed / self.stats["errors_before"] * 100) if self.stats["errors_before"] > 0 else 0
        
        print(f"📈 РЕЗУЛЬТАТЫ:")
        print(f"   • Ошибок ДО: {self.stats['errors_before']}")
        print(f"   • Ошибок ПОСЛЕ: {self.stats['errors_after']}")
        print(f"   • Исправлено: {errors_fixed}")
        print(f"   • Улучшение: {improvement:.1f}%")
        print(f"   • Перемещено импортов: {self.stats['imports_moved']}")
        print(f"   • Удалено sys.path.append: {self.stats['sys_path_removed']}")
        
        if self.stats["errors_after"] == 0:
            print("\n🎉 УСПЕХ! Файл полностью исправлен!")
        elif errors_fixed > 0:
            print(f"\n✅ ХОРОШО! Исправлено {errors_fixed} ошибок")
        else:
            print("\n⚠️  Требуется дополнительная работа")
            
    def restore_backup(self):
        """Восстановить файл из резервной копии"""
        print(f"\n🔄 ВОССТАНОВЛЕНИЕ ИЗ РЕЗЕРВНОЙ КОПИИ")
        print("=" * 60)
        
        if self.backup_file.exists():
            shutil.copy2(self.backup_file, self.target_file)
            print(f"✅ Файл восстановлен: {self.target_file}")
        else:
            print(f"❌ Резервная копия не найдена: {self.backup_file}")
            
    def run_test(self):
        """Запустить полный тест на одном файле"""
        print(f"🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ НА ОДНОМ ФАЙЛЕ")
        print("=" * 60)
        print(f"🎯 Целевой файл: {self.target_file}")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Создаем резервную копию
            self.create_backup()
            
            # Проверяем ошибки ДО
            errors_before = self.check_errors_before()
            
            if errors_before == 0:
                print("✅ Файл уже не содержит ошибок flake8")
                return
                
            # Исправляем файл
            if self.fix_imports():
                # Проверяем ошибки ПОСЛЕ
                errors_after = self.check_errors_after()
                
                # Показываем сравнение
                self.show_comparison()
                
            end_time = datetime.now()
            duration = end_time - start_time
            
            print(f"\n⏱️  Время выполнения: {duration}")
            
        except Exception as e:
            print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            print("🔄 Восстановление из резервной копии...")
            self.restore_backup()

if __name__ == "__main__":
    # Тестируем на файле vpn_protocols.py
    target_file = "security/vpn/interfaces/vpn_protocols.py"
    
    if not Path(target_file).exists():
        print(f"❌ Файл не найден: {target_file}")
        print("📁 Доступные файлы в security/vpn/protocols/:")
        protocols_dir = Path("security/vpn/protocols/")
        if protocols_dir.exists():
            for f in protocols_dir.glob("*.py"):
                print(f"   • {f}")
    else:
        fixer = SingleFileFixer(target_file)
        fixer.run_test()