#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Comprehensive Duplicate Analyzer
Полный анализ дублирующихся компонентов в системе безопасности
Анализирует все 405 функций в SFM и находит дубликаты
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import hashlib

class ComprehensiveDuplicateAnalyzer:
    def __init__(self):
        self.project_root = Path("/Users/sergejhlystov/ALADDIN_NEW")
        self.security_dir = self.project_root / "security"
        self.sfm_registry = self.project_root / "data" / "sfm" / "function_registry.json"
        
        # Результаты анализа
        self.duplicate_groups = defaultdict(list)
        self.function_analysis = {}
        self.sfm_functions = {}
        self.analysis_results = {
            "total_files_analyzed": 0,
            "duplicate_groups_found": 0,
            "total_duplicates": 0,
            "potential_space_savings": 0,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    def load_sfm_functions(self):
        """Загружает все функции из SFM registry"""
        try:
            with open(self.sfm_registry, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.sfm_functions = data
                print(f"✅ Загружено {len(data)} функций из SFM registry")
        except Exception as e:
            print(f"❌ Ошибка загрузки SFM registry: {e}")
            
    def analyze_file(self, file_path):
        """Анализирует отдельный файл"""
        try:
            stat = file_path.stat()
            size = stat.st_size
            lines = 0
            functions = []
            classes = []
            
            # Подсчет строк и функций
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = len(content.splitlines())
                
                # Поиск функций
                func_matches = re.findall(r'def\s+(\w+)\s*\(', content)
                functions = func_matches
                
                # Поиск классов
                class_matches = re.findall(r'class\s+(\w+)', content)
                classes = class_matches
                
            return {
                "path": str(file_path),
                "name": file_path.name,
                "size_bytes": size,
                "lines": lines,
                "functions": functions,
                "classes": classes,
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "content_hash": hashlib.md5(content.encode()).hexdigest()[:16]
            }
        except Exception as e:
            print(f"❌ Ошибка анализа файла {file_path}: {e}")
            return None
            
    def find_duplicate_groups(self):
        """Находит группы дублирующихся файлов"""
        print("🔍 Поиск дублирующихся компонентов...")
        
        # Словарь для группировки по базовому имени
        name_groups = defaultdict(list)
        
        # Сканируем все Python файлы в security
        for py_file in self.security_dir.rglob("*.py"):
            if self.analyze_file(py_file):
                file_info = self.analyze_file(py_file)
                if file_info:
                    self.analysis_results["total_files_analyzed"] += 1
                    
                    # Извлекаем базовое имя (без суффиксов)
                    base_name = self.extract_base_name(py_file.name)
                    name_groups[base_name].append(file_info)
        
        # Анализируем группы
        for base_name, files in name_groups.items():
            if len(files) > 1:
                self.analyze_duplicate_group(base_name, files)
                
        self.analysis_results["duplicate_groups_found"] = len(self.duplicate_groups)
        
    def extract_base_name(self, filename):
        """Извлекает базовое имя файла без суффиксов"""
        # Убираем расширение
        name = filename.replace('.py', '')
        
        # Убираем суффиксы backup, extra, main, v2, original
        suffixes_to_remove = [
            r'_backup_\d{8}_\d{6}',
            r'_backup',
            r'_extra',
            r'_main',
            r'_v2',
            r'_original_backup_\d{8}_\d{6}',
            r'_original',
            r'_a_plus',
            r'_enhanced',
            r'_old',
            r'_new'
        ]
        
        for suffix in suffixes_to_remove:
            name = re.sub(suffix, '', name)
            
        return name
        
    def analyze_duplicate_group(self, base_name, files):
        """Анализирует группу дублирующихся файлов"""
        # Сортируем по дате модификации (новые первыми)
        files.sort(key=lambda x: x['modified_time'], reverse=True)
        
        # Анализируем функциональность
        functionality_analysis = self.compare_functionality(files)
        
        # Определяем основной файл
        main_file = self.determine_main_file(files)
        
        group_info = {
            "base_name": base_name,
            "total_files": len(files),
            "main_file": main_file,
            "files": files,
            "functionality_analysis": functionality_analysis,
            "recommendations": self.generate_recommendations(files, main_file, functionality_analysis)
        }
        
        self.duplicate_groups[base_name] = group_info
        self.analysis_results["total_duplicates"] += len(files) - 1
        
    def compare_functionality(self, files):
        """Сравнивает функциональность файлов в группе"""
        analysis = {
            "identical_files": [],
            "similar_files": [],
            "unique_files": [],
            "function_overlap": {},
            "class_overlap": {}
        }
        
        # Сравниваем хеши содержимого
        content_hashes = [f['content_hash'] for f in files]
        unique_hashes = set(content_hashes)
        
        for file_info in files:
            hash_count = content_hashes.count(file_info['content_hash'])
            if hash_count > 1:
                analysis["identical_files"].append(file_info['name'])
            else:
                analysis["unique_files"].append(file_info['name'])
        
        # Анализируем перекрытие функций
        all_functions = set()
        for file_info in files:
            all_functions.update(file_info['functions'])
            
        for file_info in files:
            file_functions = set(file_info['functions'])
            overlap = len(file_functions.intersection(all_functions)) / len(all_functions) if all_functions else 0
            analysis["function_overlap"][file_info['name']] = overlap
            
        return analysis
        
    def determine_main_file(self, files):
        """Определяет основной файл в группе"""
        # Критерии для определения основного файла:
        # 1. Самый новый
        # 2. Самый большой
        # 3. Содержит "main" в имени
        # 4. Не содержит "backup" в имени
        
        main_candidates = []
        
        for file_info in files:
            score = 0
            
            # Бонус за отсутствие backup в имени
            if 'backup' not in file_info['name'].lower():
                score += 100
                
            # Бонус за "main" в имени
            if 'main' in file_info['name'].lower():
                score += 50
                
            # Бонус за "a_plus" в имени
            if 'a_plus' in file_info['name'].lower():
                score += 75
                
            # Бонус за размер (больше = лучше)
            score += file_info['lines'] / 100
            
            # Бонус за новизну (более новые файлы)
            try:
                mod_time = datetime.fromisoformat(file_info['modified_time'])
                days_old = (datetime.now() - mod_time).days
                score += max(0, 30 - days_old)
            except:
                pass
                
            main_candidates.append((score, file_info))
            
        # Сортируем по score и возвращаем лучший
        main_candidates.sort(key=lambda x: x[0], reverse=True)
        return main_candidates[0][1] if main_candidates else files[0]
        
    def generate_recommendations(self, files, main_file, functionality_analysis):
        """Генерирует рекомендации по обработке дубликатов"""
        recommendations = {
            "keep": [main_file['name']],
            "delete": [],
            "merge": [],
            "reasoning": []
        }
        
        main_functions = set(main_file['functions'])
        
        for file_info in files:
            if file_info['name'] == main_file['name']:
                continue
                
            file_functions = set(file_info['functions'])
            
            # Если файл идентичен по содержимому
            if file_info['content_hash'] == main_file['content_hash']:
                recommendations["delete"].append(file_info['name'])
                recommendations["reasoning"].append(f"{file_info['name']} идентичен {main_file['name']}")
                
            # Если файл имеет уникальные функции
            elif file_functions - main_functions:
                unique_funcs = file_functions - main_functions
                recommendations["merge"].append({
                    "file": file_info['name'],
                    "unique_functions": list(unique_funcs),
                    "reasoning": f"Содержит {len(unique_funcs)} уникальных функций"
                })
                
            # Если файл значительно меньше и не имеет уникальных функций
            elif file_info['lines'] < main_file['lines'] * 0.7:
                recommendations["delete"].append(file_info['name'])
                recommendations["reasoning"].append(f"{file_info['name']} меньше и не содержит уникальных функций")
                
            else:
                recommendations["keep"].append(file_info['name'])
                recommendations["reasoning"].append(f"{file_info['name']} имеет значительную функциональность")
                
        return recommendations
        
    def analyze_sfm_functions(self):
        """Анализирует функции в SFM registry"""
        print("🔍 Анализ функций в SFM registry...")
        
        if not self.sfm_functions:
            print("❌ SFM registry не загружен")
            return
            
        # Группируем функции по именам
        function_groups = defaultdict(list)
        
        for func_name, func_data in self.sfm_functions.items():
            if isinstance(func_data, dict):
                base_name = self.extract_base_name(func_name)
                function_groups[base_name].append({
                    "name": func_name,
                    "data": func_data
                })
        
        # Анализируем дублирующиеся функции
        sfm_duplicates = {}
        for base_name, functions in function_groups.items():
            if len(functions) > 1:
                sfm_duplicates[base_name] = functions
                
        print(f"✅ Найдено {len(sfm_duplicates)} групп дублирующихся функций в SFM")
        return sfm_duplicates
        
    def generate_report(self):
        """Генерирует полный отчет"""
        report = {
            "analysis_summary": self.analysis_results,
            "duplicate_groups": dict(self.duplicate_groups),
            "sfm_analysis": self.analyze_sfm_functions(),
            "recommendations": self.generate_overall_recommendations()
        }
        
        return report
        
    def generate_overall_recommendations(self):
        """Генерирует общие рекомендации"""
        total_deletable = 0
        total_space_savings = 0
        
        for group_name, group_info in self.duplicate_groups.items():
            for file_info in group_info["files"]:
                if file_info['name'] != group_info["main_file"]['name']:
                    total_deletable += 1
                    total_space_savings += file_info['lines']
                    
        return {
            "total_files_to_delete": total_deletable,
            "estimated_space_savings_lines": total_space_savings,
            "estimated_space_savings_mb": total_space_savings * 50 / 1024 / 1024,  # Примерно 50 байт на строку
            "priority_actions": [
                "Удалить все backup файлы",
                "Удалить identical файлы",
                "Объединить функции из merge файлов в основные",
                "Очистить SFM registry от дубликатов"
            ]
        }
        
    def run_analysis(self):
        """Запускает полный анализ"""
        print("🚀 Запуск комплексного анализа дублирующихся компонентов...")
        print("=" * 80)
        
        # Загружаем SFM функции
        self.load_sfm_functions()
        
        # Находим дублирующиеся группы
        self.find_duplicate_groups()
        
        # Генерируем отчет
        report = self.generate_report()
        
        # Сохраняем отчет
        report_path = self.project_root / "backups" / f"DUPLICATE_ANALYSIS_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Отчет сохранен: {report_path}")
        
        # Выводим краткую сводку
        self.print_summary(report)
        
        return report
        
    def print_summary(self, report):
        """Выводит краткую сводку результатов"""
        print("\n" + "=" * 80)
        print("📊 СВОДКА АНАЛИЗА ДУБЛИРУЮЩИХСЯ КОМПОНЕНТОВ")
        print("=" * 80)
        
        summary = report["analysis_summary"]
        print(f"📁 Файлов проанализировано: {summary['total_files_analyzed']}")
        print(f"🔍 Групп дубликатов найдено: {summary['duplicate_groups_found']}")
        print(f"🗑️ Дубликатов для удаления: {summary['total_duplicates']}")
        
        recommendations = report["recommendations"]
        print(f"💾 Потенциальная экономия места: {recommendations['estimated_space_savings_lines']:,} строк")
        print(f"📦 Экономия в MB: {recommendations['estimated_space_savings_mb']:.2f} MB")
        
        print("\n🏆 ТОП-10 ГРУПП ДУБЛИКАТОВ:")
        duplicate_groups = report["duplicate_groups"]
        sorted_groups = sorted(duplicate_groups.items(), 
                             key=lambda x: len(x[1]["files"]), reverse=True)[:10]
        
        for i, (group_name, group_info) in enumerate(sorted_groups, 1):
            print(f"{i:2d}. {group_name.upper()}: {len(group_info['files'])} файлов")
            main_file = group_info["main_file"]
            print(f"    📌 Основной: {main_file['name']} ({main_file['lines']} строк)")
            
            for file_info in group_info["files"]:
                if file_info['name'] != main_file['name']:
                    status = "🗑️ УДАЛИТЬ" if file_info['name'] in group_info["recommendations"]["delete"] else "⚠️ ПРОВЕРИТЬ"
                    print(f"    {status}: {file_info['name']} ({file_info['lines']} строк)")
            print()

if __name__ == "__main__":
    analyzer = ComprehensiveDuplicateAnalyzer()
    analyzer.run_analysis()