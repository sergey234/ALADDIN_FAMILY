#!/usr/bin/env python3
"""
Автоматический поиск всех функций из списка для SFM алгоритма
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


class AutoFunctionFinder:
    """Автоматический поисковик функций"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.sfm_registry_path = os.path.join(base_path, "data/sfm/function_registry.json")
        self.formatting_work_path = os.path.join(base_path, "formatting_work")
        
        # Список функций для поиска
        self.target_functions = [
            "notification_bot.py",
            "threat_intelligence_agent.py", 
            "anti_fraud_master_ai.py",
            "network_monitoring.py",
            "circuit_breaker.py",
            "super_ai_support_assistant.py",
            "super_ai_support_assistant_improved.py",
            "emergency_security_utils.py",
            "natural_language_processor.py"
        ]
        
    def find_function_in_sfm(self, function_name: str) -> List[FunctionVersion]:
        """Поиск функции в SFM реестре"""
        versions = []
        
        try:
            if os.path.exists(self.sfm_registry_path):
                with open(self.sfm_registry_path, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                    
                if 'functions' in registry:
                    for func_id, func_data in registry['functions'].items():
                        if function_name in func_data.get('file_path', ''):
                            version = FunctionVersion(
                                source='sfm',
                                path=func_data.get('file_path', ''),
                                function_id=func_id,
                                name=func_data.get('name', ''),
                                status=func_data.get('status', 'unknown'),
                                lines_of_code=func_data.get('lines_of_code', 0),
                                file_size_kb=func_data.get('file_size_kb', 0),
                                flake8_errors=func_data.get('flake8_errors', 0),
                                quality_score=func_data.get('quality_score', 'unknown'),
                                last_updated=func_data.get('last_updated', ''),
                                description=func_data.get('description', '')
                            )
                            versions.append(version)
        except Exception as e:
            print(f"❌ Ошибка чтения SFM реестра: {e}")
            
        return versions
    
    def find_function_in_formatting_work(self, function_name: str) -> List[FunctionVersion]:
        """Поиск функции в formatting_work"""
        versions = []
        
        if os.path.exists(self.formatting_work_path):
            # Поиск всех файлов с похожим именем
            patterns = [
                f"{self.formatting_work_path}/**/{function_name}",
                f"{self.formatting_work_path}/**/*{function_name.replace('.py', '')}*",
            ]
            
            for pattern in patterns:
                for file_path in glob.glob(pattern, recursive=True):
                    if os.path.isfile(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            version = FunctionVersion(
                                source='formatting_work',
                                path=file_path,
                                function_id=os.path.basename(file_path),
                                name=function_name,
                                status='backup',
                                lines_of_code=len(content.splitlines()),
                                file_size_kb=os.path.getsize(file_path) / 1024,
                                flake8_errors=0,  # Будет проверено позже
                                quality_score='unknown',
                                last_updated=datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
                                description='Backup version'
                            )
                            versions.append(version)
                        except Exception as e:
                            print(f"❌ Ошибка чтения {file_path}: {e}")
                            
        return versions
    
    def find_function_in_active_files(self, function_name: str) -> List[FunctionVersion]:
        """Поиск активных версий функции"""
        versions = []
        
        # Поиск в основных директориях
        search_dirs = [
            "security",
            "core", 
            "ai_agents",
            "bots",
            "scripts"
        ]
        
        for search_dir in search_dirs:
            search_path = os.path.join(self.base_path, search_dir)
            if os.path.exists(search_path):
                patterns = [
                    f"{search_path}/**/{function_name}",
                    f"{search_path}/**/*{function_name.replace('.py', '')}*",
                ]
                
                for pattern in patterns:
                    for file_path in glob.glob(pattern, recursive=True):
                        if os.path.isfile(file_path):
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    
                                version = FunctionVersion(
                                    source='active',
                                    path=file_path,
                                    function_id=os.path.basename(file_path),
                                    name=function_name,
                                    status='active',
                                    lines_of_code=len(content.splitlines()),
                                    file_size_kb=os.path.getsize(file_path) / 1024,
                                    flake8_errors=0,  # Будет проверено позже
                                    quality_score='unknown',
                                    last_updated=datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
                                    description='Active version'
                                )
                                versions.append(version)
                            except Exception as e:
                                print(f"❌ Ошибка чтения {file_path}: {e}")
                                
        return versions
    
    def find_all_versions(self, function_name: str) -> List[FunctionVersion]:
        """Найти все версии функции"""
        all_versions = []
        
        # Поиск в SFM реестре
        sfm_versions = self.find_function_in_sfm(function_name)
        all_versions.extend(sfm_versions)
        
        # Поиск в formatting_work
        formatting_versions = self.find_function_in_formatting_work(function_name)
        all_versions.extend(formatting_versions)
        
        # Поиск активных версий
        active_versions = self.find_function_in_active_files(function_name)
        all_versions.extend(active_versions)
        
        return all_versions
    
    def analyze_all_functions(self):
        """Анализ всех функций из списка"""
        print("🔍 ЭТАП 0: ПРЕДВАРИТЕЛЬНЫЙ ПОИСК И АНАЛИЗ")
        print("=" * 60)
        
        results = {}
        
        for function_name in self.target_functions:
            print(f"\n📋 Анализ функции: {function_name}")
            print("-" * 40)
            
            versions = self.find_all_versions(function_name)
            
            if not versions:
                print(f"❌ Функция '{function_name}' не найдена")
                results[function_name] = {
                    'status': 'not_found',
                    'versions': [],
                    'best_version': None
                }
                continue
            
            # Сравнение версий
            best_version = self.select_best_version(versions)
            
            print(f"✅ Найдено версий: {len(versions)}")
            for version in versions:
                print(f"  📁 {version.source}: {version.path}")
                print(f"     📊 Строк: {version.lines_of_code}, Размер: {version.file_size_kb:.1f}KB")
                print(f"     🏷️  Статус: {version.status}, Обновлен: {version.last_updated}")
            
            if best_version:
                print(f"🎯 ЛУЧШАЯ ВЕРСИЯ: {best_version.source} - {best_version.path}")
            else:
                print("⚠️  Не удалось определить лучшую версию")
            
            results[function_name] = {
                'status': 'found',
                'versions': versions,
                'best_version': best_version
            }
        
        # Сохранение результатов
        self.save_analysis_results(results)
        return results
    
    def select_best_version(self, versions: List[FunctionVersion]) -> Optional[FunctionVersion]:
        """Выбор лучшей версии функции"""
        if not versions:
            return None
            
        # Приоритет: active > sfm > formatting_work
        priority_order = {'active': 3, 'sfm': 2, 'formatting_work': 1}
        
        # Сортировка по приоритету и качеству
        sorted_versions = sorted(versions, key=lambda v: (
            priority_order.get(v.source, 0),
            v.lines_of_code,
            -v.flake8_errors
        ), reverse=True)
        
        return sorted_versions[0] if sorted_versions else None
    
    def save_analysis_results(self, results: Dict):
        """Сохранение результатов анализа"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(self.base_path, f"function_search_report_{timestamp}.json")
        
        # Конвертация в сериализуемый формат
        serializable_results = {}
        for func_name, data in results.items():
            serializable_results[func_name] = {
                'status': data['status'],
                'versions_count': len(data['versions']),
                'best_version': {
                    'source': data['best_version'].source if data['best_version'] else None,
                    'path': data['best_version'].path if data['best_version'] else None,
                    'lines_of_code': data['best_version'].lines_of_code if data['best_version'] else 0,
                    'file_size_kb': data['best_version'].file_size_kb if data['best_version'] else 0,
                    'status': data['best_version'].status if data['best_version'] else None,
                    'last_updated': data['best_version'].last_updated if data['best_version'] else None
                } if data['best_version'] else None
            }
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Отчет сохранен: {report_path}")
        except Exception as e:
            print(f"❌ Ошибка сохранения отчета: {e}")


def main():
    """Основная функция"""
    finder = AutoFunctionFinder()
    results = finder.analyze_all_functions()
    
    print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 40)
    
    found_count = sum(1 for data in results.values() if data['status'] == 'found')
    not_found_count = sum(1 for data in results.values() if data['status'] == 'not_found')
    
    print(f"✅ Найдено функций: {found_count}")
    print(f"❌ Не найдено функций: {not_found_count}")
    print(f"📋 Всего проанализировано: {len(results)}")


if __name__ == "__main__":
    main()