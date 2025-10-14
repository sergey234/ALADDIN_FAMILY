#!/usr/bin/env python3
"""
Улучшенный поисковик функций для SFM алгоритма
Ищет функции в SFM реестре, formatting_work и sleeping функциях
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class FunctionVersion:
    """Класс для хранения информации о версии функции"""
    source: str  # 'sfm', 'formatting_work', 'sleeping'
    path: str
    function_id: str
    name: str
    status: str
    lines_of_code: int
    file_size_kb: float
    flake8_errors: int
    quality_score: str
    last_updated: str
    description: str = ""


class EnhancedFunctionFinder:
    """Улучшенный поисковик функций"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.sfm_registry_path = os.path.join(base_path, "data/sfm/function_registry.json")
        self.formatting_work_path = os.path.join(base_path, "formatting_work")
        
    def find_all_function_versions(self, function_name: str) -> List[FunctionVersion]:
        """Найти все версии функции в системе"""
        print(f"🔍 ПОИСК ВСЕХ ВЕРСИЙ ФУНКЦИИ: {function_name}")
        print("=" * 60)
        
        versions = []
        
        # 1. Поиск в SFM реестре
        sfm_versions = self._find_in_sfm_registry(function_name)
        versions.extend(sfm_versions)
        
        # 2. Поиск в formatting_work
        formatting_versions = self._find_in_formatting_work(function_name)
        versions.extend(formatting_versions)
        
        # 3. Поиск в sleeping функциях
        sleeping_versions = self._find_in_sleeping_functions(function_name)
        versions.extend(sleeping_versions)
        
        return versions
    
    def _find_in_sfm_registry(self, function_name: str) -> List[FunctionVersion]:
        """Поиск в SFM реестре"""
        print("📋 Поиск в SFM реестре...")
        versions = []
        
        try:
            with open(self.sfm_registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            for func_id, func_data in registry['functions'].items():
                if (function_name.lower() in func_id.lower() or 
                    function_name.lower() in func_data.get('name', '').lower()):
                    
                    version = FunctionVersion(
                        source='sfm',
                        path=func_data.get('file_path', ''),
                        function_id=func_id,
                        name=func_data.get('name', ''),
                        status=func_data.get('status', 'unknown'),
                        lines_of_code=func_data.get('lines_of_code', 0),
                        file_size_kb=func_data.get('file_size_kb', 0.0),
                        flake8_errors=func_data.get('flake8_errors', 0),
                        quality_score=func_data.get('quality_score', 'N/A'),
                        last_updated=func_data.get('last_updated', ''),
                        description=func_data.get('description', '')
                    )
                    versions.append(version)
                    print(f"  ✅ Найдена: {func_id} ({func_data.get('status', 'unknown')})")
        
        except Exception as e:
            print(f"  ❌ Ошибка чтения SFM реестра: {e}")
        
        return versions
    
    def _find_in_formatting_work(self, function_name: str) -> List[FunctionVersion]:
        """Поиск в formatting_work"""
        print("📁 Поиск в formatting_work...")
        versions = []
        
        if not os.path.exists(self.formatting_work_path):
            print("  ⚠️ Папка formatting_work не найдена")
            return versions
        
        # Поиск всех Python файлов в formatting_work
        pattern = os.path.join(self.formatting_work_path, "**", "*.py")
        for file_path in glob.glob(pattern, recursive=True):
            filename = os.path.basename(file_path)
            if function_name.lower() in filename.lower():
                try:
                    # Получаем информацию о файле
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines_count = len(content.splitlines())
                    file_size_kb = os.path.getsize(file_path) / 1024
                    
                    version = FunctionVersion(
                        source='formatting_work',
                        path=file_path,
                        function_id=filename.replace('.py', ''),
                        name=filename.replace('.py', ''),
                        status='formatting_work',
                        lines_of_code=lines_count,
                        file_size_kb=file_size_kb,
                        flake8_errors=0,  # Будет определено позже
                        quality_score='N/A',
                        last_updated=datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                        description=f"Файл из formatting_work: {filename}"
                    )
                    versions.append(version)
                    print(f"  ✅ Найдена: {filename} ({lines_count} строк)")
                
                except Exception as e:
                    print(f"  ❌ Ошибка чтения {file_path}: {e}")
        
        return versions
    
    def _find_in_sleeping_functions(self, function_name: str) -> List[FunctionVersion]:
        """Поиск в sleeping функциях"""
        print("💤 Поиск в sleeping функциях...")
        versions = []
        
        try:
            with open(self.sfm_registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            for func_id, func_data in registry['functions'].items():
                if (func_data.get('status') == 'sleeping' and 
                    (function_name.lower() in func_id.lower() or 
                     function_name.lower() in func_data.get('name', '').lower())):
                    
                    version = FunctionVersion(
                        source='sleeping',
                        path=func_data.get('file_path', ''),
                        function_id=func_id,
                        name=func_data.get('name', ''),
                        status='sleeping',
                        lines_of_code=func_data.get('lines_of_code', 0),
                        file_size_kb=func_data.get('file_size_kb', 0.0),
                        flake8_errors=func_data.get('flake8_errors', 0),
                        quality_score=func_data.get('quality_score', 'N/A'),
                        last_updated=func_data.get('last_updated', ''),
                        description=func_data.get('description', '')
                    )
                    versions.append(version)
                    print(f"  ✅ Найдена sleeping: {func_id}")
        
        except Exception as e:
            print(f"  ❌ Ошибка поиска sleeping функций: {e}")
        
        return versions
    
    def compare_versions(self, versions: List[FunctionVersion]) -> Dict:
        """Сравнить все найденные версии"""
        print("\n📊 СРАВНИТЕЛЬНЫЙ АНАЛИЗ ВЕРСИЙ:")
        print("=" * 50)
        
        if not versions:
            print("❌ Версии не найдены")
            return {}
        
        # Сортируем по качеству (меньше ошибок = лучше)
        sorted_versions = sorted(versions, key=lambda v: (v.flake8_errors, -v.lines_of_code))
        
        print(f"Найдено версий: {len(versions)}")
        print()
        
        for i, version in enumerate(sorted_versions, 1):
            print(f"{i}. {version.function_id}")
            print(f"   Источник: {version.source}")
            print(f"   Статус: {version.status}")
            print(f"   Строк кода: {version.lines_of_code}")
            print(f"   Размер: {version.file_size_kb:.1f} KB")
            print(f"   Ошибки flake8: {version.flake8_errors}")
            print(f"   Качество: {version.quality_score}")
            print(f"   Обновлено: {version.last_updated}")
            print(f"   Путь: {version.path}")
            print()
        
        # Рекомендация
        best_version = sorted_versions[0]
        print(f"🏆 РЕКОМЕНДУЕМАЯ ВЕРСИЯ: {best_version.function_id}")
        print(f"   Источник: {best_version.source}")
        print(f"   Причина: {best_version.flake8_errors} ошибок flake8, {best_version.lines_of_code} строк")
        
        return {
            'total_versions': len(versions),
            'best_version': best_version,
            'all_versions': sorted_versions,
            'recommendation': best_version
        }
    
    def analyze_function_quality(self, file_path: str) -> Dict:
        """Анализ качества функции"""
        print(f"\n🔍 АНАЛИЗ КАЧЕСТВА: {file_path}")
        print("=" * 40)
        
        if not os.path.exists(file_path):
            print(f"❌ Файл не найден: {file_path}")
            return {}
        
        try:
            # Получаем информацию о файле
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines_count = len(content.splitlines())
            file_size_kb = os.path.getsize(file_path) / 1024
            
            # Запускаем flake8
            import subprocess
            result = subprocess.run(
                ['python3', '-m', 'flake8', file_path, '--max-line-length=79'],
                capture_output=True, text=True
            )
            
            flake8_errors = len(result.stdout.splitlines()) if result.stdout else 0
            
            # Определяем качество
            if flake8_errors == 0:
                quality = "A+"
            elif flake8_errors <= 5:
                quality = "A"
            elif flake8_errors <= 10:
                quality = "B"
            elif flake8_errors <= 20:
                quality = "C"
            else:
                quality = "D"
            
            analysis = {
                'file_path': file_path,
                'lines_of_code': lines_count,
                'file_size_kb': file_size_kb,
                'flake8_errors': flake8_errors,
                'quality_score': quality,
                'flake8_output': result.stdout,
                'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            }
            
            print(f"✅ Строк кода: {lines_count}")
            print(f"✅ Размер файла: {file_size_kb:.1f} KB")
            print(f"✅ Ошибки flake8: {flake8_errors}")
            print(f"✅ Качество: {quality}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Ошибка анализа: {e}")
            return {}


def main():
    """Основная функция"""
    finder = EnhancedFunctionFinder()
    
    # Пример использования
    function_name = input("Введите название функции для поиска: ").strip()
    
    if not function_name:
        print("❌ Название функции не указано")
        return
    
    # Поиск всех версий
    versions = finder.find_all_function_versions(function_name)
    
    if not versions:
        print(f"❌ Функция '{function_name}' не найдена")
        return
    
    # Сравнение версий
    comparison = finder.compare_versions(versions)
    
    if comparison:
        best_version = comparison['best_version']
        print(f"\n🎯 ГОТОВ К АНАЛИЗУ: {best_version.path}")
        
        # Анализ качества лучшей версии
        if best_version.path and os.path.exists(best_version.path):
            finder.analyze_function_quality(best_version.path)


if __name__ == "__main__":
    main()