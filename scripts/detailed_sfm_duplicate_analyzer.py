#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Detailed SFM Duplicate Analyzer
Детальный анализ всех 404 функций в SFM и их дубликатов
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import re

class DetailedSFMDuplicateAnalyzer:
    def __init__(self):
        self.project_root = Path("/Users/sergejhlystov/ALADDIN_NEW")
        self.sfm_registry = self.project_root / "data" / "sfm" / "function_registry.json"
        self.security_dir = self.project_root / "security"
        
        # Результаты анализа
        self.sfm_functions = {}
        self.file_analysis = {}
        self.duplicate_groups = defaultdict(list)
        self.deletion_candidates = []
        self.keep_candidates = []
        
    def load_sfm_functions(self):
        """Загружает все функции из SFM registry"""
        try:
            with open(self.sfm_registry, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.sfm_functions = data
                print(f"✅ Загружено {len(data)} функций из SFM registry")
                return True
        except Exception as e:
            print(f"❌ Ошибка загрузки SFM registry: {e}")
            return False
            
    def analyze_file_content(self, file_path):
        """Детальный анализ содержимого файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Базовые метрики
            lines = len(content.splitlines())
            size = len(content.encode('utf-8'))
            
            # Анализ функций
            functions = re.findall(r'def\s+(\w+)\s*\(', content)
            classes = re.findall(r'class\s+(\w+)', content)
            
            # Анализ импортов
            imports = re.findall(r'^(?:from\s+\S+\s+)?import\s+([^\n]+)', content, re.MULTILINE)
            
            # Анализ зависимостей
            dependencies = set()
            for imp in imports:
                if 'from' in imp:
                    deps = re.findall(r'from\s+(\S+)', imp)
                    dependencies.update(deps)
                else:
                    deps = re.findall(r'import\s+(\S+)', imp)
                    dependencies.update(deps)
            
            # Хеш содержимого для сравнения
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Анализ функциональности
            functionality_score = self.calculate_functionality_score(content, functions, classes)
            
            return {
                "path": str(file_path),
                "name": file_path.name,
                "lines": lines,
                "size_bytes": size,
                "functions": functions,
                "classes": classes,
                "imports": list(imports),
                "dependencies": list(dependencies),
                "content_hash": content_hash,
                "functionality_score": functionality_score,
                "is_backup": any(suffix in file_path.name.lower() for suffix in ['_backup', '_original', '_old']),
                "is_main": 'main' in file_path.name.lower(),
                "is_extra": 'extra' in file_path.name.lower(),
                "is_v2": 'v2' in file_path.name.lower(),
                "is_a_plus": 'a_plus' in file_path.name.lower(),
                "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
        except Exception as e:
            print(f"❌ Ошибка анализа файла {file_path}: {e}")
            return None
            
    def calculate_functionality_score(self, content, functions, classes):
        """Вычисляет оценку функциональности файла"""
        score = 0
        
        # Базовые очки
        score += len(functions) * 10  # 10 очков за функцию
        score += len(classes) * 20    # 20 очков за класс
        
        # Очки за ключевые слова функциональности
        functionality_keywords = [
            'async', 'await', 'ml', 'ai', 'machine_learning', 'neural_network',
            'database', 'redis', 'sql', 'api', 'http', 'websocket',
            'security', 'encryption', 'authentication', 'authorization',
            'monitoring', 'logging', 'metrics', 'analytics', 'detection',
            'prevention', 'response', 'analysis', 'prediction', 'learning'
        ]
        
        for keyword in functionality_keywords:
            if keyword in content.lower():
                score += 5
                
        # Очки за сложность
        if 'try:' in content and 'except:' in content:
            score += 10  # Обработка ошибок
        if 'threading' in content or 'asyncio' in content:
            score += 15  # Многопоточность
        if 'json' in content and 'load' in content:
            score += 5   # Работа с данными
        if 'logging' in content:
            score += 5   # Логирование
            
        return score
        
    def find_duplicate_groups(self):
        """Находит группы дублирующихся файлов"""
        print("🔍 Поиск дублирующихся компонентов...")
        
        # Сканируем все Python файлы
        for py_file in self.security_dir.rglob("*.py"):
            file_info = self.analyze_file_content(py_file)
            if file_info:
                # Извлекаем базовое имя
                base_name = self.extract_base_name(py_file.name)
                self.duplicate_groups[base_name].append(file_info)
                
        # Фильтруем только группы с дубликатами
        duplicate_groups = {k: v for k, v in self.duplicate_groups.items() if len(v) > 1}
        
        print(f"✅ Найдено {len(duplicate_groups)} групп дубликатов")
        return duplicate_groups
        
    def extract_base_name(self, filename):
        """Извлекает базовое имя файла"""
        name = filename.replace('.py', '')
        
        # Убираем суффиксы
        suffixes = [
            r'_backup_\d{8}_\d{6}',
            r'_backup',
            r'_original_backup_\d{8}_\d{6}',
            r'_original',
            r'_extra',
            r'_main',
            r'_v2',
            r'_a_plus',
            r'_enhanced',
            r'_old',
            r'_new'
        ]
        
        for suffix in suffixes:
            name = re.sub(suffix, '', name)
            
        return name
        
    def analyze_duplicate_group(self, group_name, files):
        """Детальный анализ группы дубликатов"""
        # Сортируем по функциональности (убывание)
        files.sort(key=lambda x: x['functionality_score'], reverse=True)
        
        analysis = {
            "group_name": group_name,
            "total_files": len(files),
            "files": files,
            "main_file": files[0],  # Самый функциональный
            "deletion_candidates": [],
            "keep_candidates": [],
            "reasoning": []
        }
        
        main_file = files[0]
        main_functions = set(main_file['functions'])
        main_classes = set(main_file['classes'])
        
        for file_info in files[1:]:
            file_functions = set(file_info['functions'])
            file_classes = set(file_info['classes'])
            
            # Анализ дублирования
            function_overlap = len(file_functions.intersection(main_functions)) / len(main_functions) if main_functions else 0
            class_overlap = len(file_classes.intersection(main_classes)) / len(main_classes) if main_classes else 0
            
            # Критерии для удаления
            should_delete = False
            reason = ""
            
            # 1. Идентичное содержимое
            if file_info['content_hash'] == main_file['content_hash']:
                should_delete = True
                reason = f"100% идентичное содержимое с {main_file['name']}"
                
            # 2. Бэкап файл
            elif file_info['is_backup']:
                should_delete = True
                reason = f"Бэкап файл: {file_info['name']}"
                
            # 3. Значительно меньше функциональности
            elif file_info['functionality_score'] < main_file['functionality_score'] * 0.5:
                should_delete = True
                ratio = main_file['functionality_score'] / max(file_info['functionality_score'], 1)
                reason = f"Функциональность в {ratio:.1f} раз меньше ({file_info['functionality_score']} vs {main_file['functionality_score']})"
                
            # 4. Высокое перекрытие функций без уникальных
            elif function_overlap > 0.8 and not (file_functions - main_functions):
                should_delete = True
                reason = f"Высокое перекрытие функций ({function_overlap:.1%}) без уникальных"
                
            # 5. Старая версия (main vs полная)
            elif file_info['is_main'] and not main_file['is_main'] and file_info['lines'] < main_file['lines'] * 0.7:
                should_delete = True
                reason = f"Базовая версия заменена полной ({file_info['lines']} vs {main_file['lines']} строк)"
                
            else:
                # Проверяем уникальные функции
                unique_functions = file_functions - main_functions
                unique_classes = file_classes - main_classes
                
                if unique_functions or unique_classes:
                    analysis["keep_candidates"].append({
                        "file": file_info,
                        "unique_functions": list(unique_functions),
                        "unique_classes": list(unique_classes),
                        "reason": f"Содержит {len(unique_functions)} уникальных функций и {len(unique_classes)} уникальных классов"
                    })
                else:
                    should_delete = True
                    reason = f"Нет уникальной функциональности"
            
            if should_delete:
                analysis["deletion_candidates"].append({
                    "file": file_info,
                    "reason": reason,
                    "functionality_score": file_info['functionality_score'],
                    "lines": file_info['lines'],
                    "function_overlap": function_overlap,
                    "class_overlap": class_overlap
                })
            else:
                analysis["keep_candidates"].append({
                    "file": file_info,
                    "reason": "Уникальная функциональность",
                    "functionality_score": file_info['functionality_score'],
                    "lines": file_info['lines']
                })
        
        return analysis
        
    def generate_deletion_report(self):
        """Генерирует отчет о файлах для удаления"""
        duplicate_groups = self.find_duplicate_groups()
        
        total_deletable = 0
        total_keepable = 0
        total_space_savings = 0
        
        print("\n" + "="*100)
        print("📋 ДЕТАЛЬНЫЙ ОТЧЕТ О ФАЙЛАХ ДЛЯ УДАЛЕНИЯ")
        print("="*100)
        
        for group_name, files in duplicate_groups.items():
            if len(files) <= 1:
                continue
                
            analysis = self.analyze_duplicate_group(group_name, files)
            
            print(f"\n🔍 ГРУППА: {group_name.upper()}")
            print(f"📊 Всего файлов: {len(files)}")
            print(f"📌 Основной файл: {analysis['main_file']['name']} ({analysis['main_file']['lines']} строк, {analysis['main_file']['functionality_score']} очков)")
            
            if analysis['deletion_candidates']:
                print(f"\n🗑️ ФАЙЛЫ ДЛЯ УДАЛЕНИЯ ({len(analysis['deletion_candidates'])}):")
                for candidate in analysis['deletion_candidates']:
                    file_info = candidate['file']
                    print(f"  ❌ {file_info['name']}")
                    print(f"     📊 Строк: {file_info['lines']}, Очков: {file_info['functionality_score']}")
                    print(f"     📝 Причина: {candidate['reason']}")
                    print(f"     📈 Перекрытие функций: {candidate.get('function_overlap', 0):.1%}")
                    print()
                    total_deletable += 1
                    total_space_savings += file_info['lines']
            
            if analysis['keep_candidates']:
                print(f"\n✅ ФАЙЛЫ ДЛЯ СОХРАНЕНИЯ ({len(analysis['keep_candidates'])}):")
                for candidate in analysis['keep_candidates']:
                    file_info = candidate['file']
                    print(f"  ✅ {file_info['name']}")
                    print(f"     📊 Строк: {file_info['lines']}, Очков: {file_info['functionality_score']}")
                    print(f"     📝 Причина: {candidate['reason']}")
                    if 'unique_functions' in candidate and candidate['unique_functions']:
                        print(f"     🔧 Уникальные функции: {', '.join(candidate['unique_functions'][:5])}{'...' if len(candidate['unique_functions']) > 5 else ''}")
                    print()
                    total_keepable += 1
            
            print("-" * 80)
        
        print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"🗑️ Файлов для удаления: {total_deletable}")
        print(f"✅ Файлов для сохранения: {total_keepable}")
        print(f"💾 Экономия места: {total_space_savings:,} строк")
        print(f"📦 Экономия в MB: {total_space_savings * 50 / 1024 / 1024:.2f} MB")
        
        return {
            "total_deletable": total_deletable,
            "total_keepable": total_keepable,
            "space_savings": total_space_savings,
            "duplicate_groups": duplicate_groups
        }
        
    def run_analysis(self):
        """Запускает полный анализ"""
        print("🚀 Запуск детального анализа SFM дубликатов...")
        print("="*100)
        
        if not self.load_sfm_functions():
            return None
            
        return self.generate_deletion_report()

if __name__ == "__main__":
    analyzer = DetailedSFMDuplicateAnalyzer()
    analyzer.run_analysis()