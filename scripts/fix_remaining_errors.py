#!/usr/bin/env python3
"""
Исправление оставшихся ошибок форматирования
"""

import os
import re
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class RemainingErrorsFixer:
    def __init__(self, target_file):
        self.target_file = Path(target_file)
        self.backup_file = self.target_file.with_suffix('.py.backup2')
        self.stats = {
            "e302_fixed": 0,  # expected 2 blank lines
            "f401_fixed": 0,  # unused imports
            "e128_fixed": 0,  # continuation line indentation
            "e305_fixed": 0,  # expected 2 blank lines before class
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
                print("📋 Все ошибки:")
                for i, error in enumerate(error_lines):
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
            
    def fix_remaining_errors(self):
        """Исправить оставшиеся ошибки"""
        print(f"\n🔧 ИСПРАВЛЕНИЕ ОСТАВШИХСЯ ОШИБОК")
        print("=" * 60)
        
        try:
            with open(self.target_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            print(f"📄 Исходный файл: {len(lines)} строк")
            
            new_lines = []
            i = 0
            
            while i < len(lines):
                line = lines[i]
                
                # E302: expected 2 blank lines before function/class
                if re.match(r'^(def |class )', line.strip()):
                    # Проверяем, сколько пустых строк перед функцией/классом
                    blank_count = 0
                    j = i - 1
                    while j >= 0 and lines[j].strip() == '':
                        blank_count += 1
                        j -= 1
                    
                    # Если перед функцией/классом есть код (не пустые строки)
                    if j >= 0 and lines[j].strip() != '':
                        if blank_count < 2:
                            # Добавляем недостающие пустые строки
                            for _ in range(2 - blank_count):
                                new_lines.append('\n')
                            self.stats["e302_fixed"] += 1
                
                # E305: expected 2 blank lines before class (в конце файла)
                if i == len(lines) - 1 and re.match(r'^class ', line.strip()):
                    # Проверяем, сколько пустых строк перед классом
                    blank_count = 0
                    j = i - 1
                    while j >= 0 and lines[j].strip() == '':
                        blank_count += 1
                        j -= 1
                    
                    if j >= 0 and lines[j].strip() != '':
                        if blank_count < 2:
                            # Добавляем недостающие пустые строки
                            for _ in range(2 - blank_count):
                                new_lines.append('\n')
                            self.stats["e305_fixed"] += 1
                
                # E128: continuation line indentation
                if re.match(r'^\s+[^#\s]', line) and i > 0:
                    prev_line = lines[i-1].rstrip()
                    if prev_line.endswith('\\') or prev_line.endswith(','):
                        # Проверяем отступ
                        expected_indent = len(prev_line) - len(prev_line.lstrip()) + 4
                        current_indent = len(line) - len(line.lstrip())
                        if current_indent != expected_indent:
                            new_lines.append(' ' * expected_indent + line.lstrip())
                            self.stats["e128_fixed"] += 1
                            i += 1
                            continue
                
                new_lines.append(line)
                i += 1
            
            # F401: unused imports - удаляем неиспользуемые импорты
            self._remove_unused_imports(new_lines)
            
            # Записываем исправленный файл
            with open(self.target_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
                
            print(f"✅ Файл исправлен:")
            print(f"   • E302 (недостаточно пустых строк): {self.stats['e302_fixed']}")
            print(f"   • F401 (неиспользуемые импорты): {self.stats['f401_fixed']}")
            print(f"   • E128 (неправильный отступ): {self.stats['e128_fixed']}")
            print(f"   • E305 (пустые строки перед классом): {self.stats['e305_fixed']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при исправлении файла: {e}")
            return False
            
    def _remove_unused_imports(self, lines):
        """Удалить неиспользуемые импорты"""
        # Простая проверка - если импорт не используется в коде
        import_lines = []
        for i, line in enumerate(lines):
            if re.match(r'^(from .* import|import )', line.strip()):
                import_lines.append((i, line.strip()))
        
        for i, import_line in import_lines:
            # Извлекаем имя импорта
            if 'from' in import_line:
                match = re.match(r'from .* import (.+)', import_line)
                if match:
                    imported_names = [name.strip() for name in match.group(1).split(',')]
                else:
                    continue
            else:
                match = re.match(r'import (.+)', import_line)
                if match:
                    imported_names = [name.strip() for name in match.group(1).split(',')]
                else:
                    continue
            
            # Проверяем, используется ли импорт
            used = False
            for line in lines:
                if line != lines[i]:  # Не проверяем саму строку импорта
                    for name in imported_names:
                        if name in line and not line.strip().startswith('#'):
                            used = True
                            break
                    if used:
                        break
            
            if not used:
                # Удаляем неиспользуемый импорт
                lines[i] = ''
                self.stats["f401_fixed"] += 1
                
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
                for i, error in enumerate(error_lines):
                    print(f"   {i+1}. {error}")
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
        
        total_fixes = sum([
            self.stats["e302_fixed"],
            self.stats["f401_fixed"],
            self.stats["e128_fixed"],
            self.stats["e305_fixed"]
        ])
        
        print(f"\n🔧 ИСПРАВЛЕНИЯ ПО ТИПАМ:")
        print(f"   • E302 (недостаточно пустых строк): {self.stats['e302_fixed']}")
        print(f"   • F401 (неиспользуемые импорты): {self.stats['f401_fixed']}")
        print(f"   • E128 (неправильный отступ): {self.stats['e128_fixed']}")
        print(f"   • E305 (пустые строки перед классом): {self.stats['e305_fixed']}")
        print(f"   • ВСЕГО ИСПРАВЛЕНИЙ: {total_fixes}")
        
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
        print(f"🧪 ИСПРАВЛЕНИЕ ОСТАВШИХСЯ ОШИБОК")
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
            if self.fix_remaining_errors():
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
    else:
        fixer = RemainingErrorsFixer(target_file)
        fixer.run_test()