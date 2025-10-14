# -*- coding: utf-8 -*-
"""
Test Lazy Loading - Тестирование системы ленивой загрузки
Проверяет работу lazy wrappers и их интеграцию с SFM
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from lazy_wrappers import (
        LazyWrapper, LazyWrapperManager, create_lazy_wrapper,
        get_lazy_wrapper, load_lazy_wrapper, unload_lazy_wrapper,
        get_lazy_manager, initialize_lazy_system, get_lazy_system_stats
    )
    LAZY_IMPORT_SUCCESS = True
except ImportError as e:
    print(f"❌ Ошибка импорта lazy_wrappers: {e}")
    LAZY_IMPORT_SUCCESS = False

class LazyLoadingTester:
    """Тестер системы ленивой загрузки"""
    
    def __init__(self):
        """Инициализация тестера"""
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        self.start_time = None
        
    def run_test(self, test_name: str, test_func) -> bool:
        """Запуск отдельного теста"""
        self.test_results['total_tests'] += 1
        self.start_time = time.time()
        
        try:
            result = test_func()
            duration = time.time() - self.start_time
            
            if result:
                self.test_results['passed_tests'] += 1
                status = "✅ ПРОЙДЕН"
            else:
                self.test_results['failed_tests'] += 1
                status = "❌ ПРОВАЛЕН"
            
            self.test_results['test_details'].append({
                'test_name': test_name,
                'status': status,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"{status} {test_name} ({duration:.3f}s)")
            return result
            
        except Exception as e:
            self.test_results['failed_tests'] += 1
            duration = time.time() - self.start_time
            
            self.test_results['test_details'].append({
                'test_name': test_name,
                'status': "❌ ОШИБКА",
                'duration': duration,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"❌ ОШИБКА {test_name}: {e} ({duration:.3f}s)")
            return False
    
    def test_lazy_wrapper_creation(self) -> bool:
        """Тест создания lazy wrapper"""
        try:
            wrapper = create_lazy_wrapper(
                "test_wrapper",
                "security.safe_function_manager",
                "SafeFunctionManager"
            )
            
            if wrapper is None:
                return False
            
            info = wrapper.get_info()
            return (
                info['module_path'] == "security.safe_function_manager" and
                info['class_name'] == "SafeFunctionManager" and
                not info['is_loaded']
            )
        except Exception:
            return False
    
    def test_lazy_wrapper_loading(self) -> bool:
        """Тест загрузки lazy wrapper"""
        try:
            wrapper = get_lazy_wrapper("test_wrapper")
            if wrapper is None:
                return False
            
            # Загрузка
            success = load_lazy_wrapper("test_wrapper")
            if not success:
                return False
            
            # Проверка что загружен
            return wrapper.is_loaded()
        except Exception:
            return False
    
    def test_lazy_wrapper_unloading(self) -> bool:
        """Тест выгрузки lazy wrapper"""
        try:
            wrapper = get_lazy_wrapper("test_wrapper")
            if wrapper is None:
                return False
            
            # Выгрузка
            success = unload_lazy_wrapper("test_wrapper")
            if not success:
                return False
            
            # Проверка что выгружен
            return not wrapper.is_loaded()
        except Exception:
            return False
    
    def test_lazy_manager_stats(self) -> bool:
        """Тест статистики lazy manager"""
        try:
            manager = get_lazy_manager()
            if manager is None:
                return False
            
            stats = manager.get_stats()
            return (
                'total_wrappers' in stats and
                'loaded_wrappers' in stats and
                'failed_wrappers' in stats
            )
        except Exception:
            return False
    
    def test_lazy_system_initialization(self) -> bool:
        """Тест инициализации системы"""
        try:
            success = initialize_lazy_system()
            return success
        except Exception:
            return False
    
    def test_lazy_system_stats(self) -> bool:
        """Тест статистики системы"""
        try:
            stats = get_lazy_system_stats()
            return (
                'total_wrappers' in stats and
                'loaded_wrappers' in stats and
                'failed_wrappers' in stats
            )
        except Exception:
            return False
    
    def test_lazy_wrapper_info(self) -> bool:
        """Тест получения информации о wrapper"""
        try:
            wrapper = get_lazy_wrapper("test_wrapper")
            if wrapper is None:
                return False
            
            info = wrapper.get_info()
            return (
                'module_path' in info and
                'class_name' in info and
                'is_loaded' in info
            )
        except Exception:
            return False
    
    def test_lazy_wrapper_error_handling(self) -> bool:
        """Тест обработки ошибок"""
        try:
            # Создание wrapper с несуществующим модулем
            wrapper = create_lazy_wrapper(
                "error_wrapper",
                "nonexistent.module",
                "NonexistentClass"
            )
            
            if wrapper is None:
                return False
            
            # Попытка загрузки
            success = load_lazy_wrapper("error_wrapper")
            
            # Должен вернуть False из-за ошибки
            return not success
        except Exception:
            return False
    
    def test_lazy_wrapper_performance(self) -> bool:
        """Тест производительности lazy loading"""
        try:
            # Создание нескольких wrappers
            wrappers = []
            for i in range(5):
                wrapper = create_lazy_wrapper(
                    f"perf_wrapper_{i}",
                    "security.safe_function_manager",
                    "SafeFunctionManager"
                )
                wrappers.append(wrapper)
            
            # Измерение времени загрузки
            start_time = time.time()
            for wrapper in wrappers:
                wrapper.force_load()
            end_time = time.time()
            
            # Проверка что все загружены
            all_loaded = all(wrapper.is_loaded() for wrapper in wrappers)
            
            # Время должно быть разумным (менее 5 секунд)
            duration = end_time - start_time
            return all_loaded and duration < 5.0
            
        except Exception:
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        print("🧪 ТЕСТИРОВАНИЕ LAZY LOADING СИСТЕМЫ")
        print("=" * 60)
        
        if not LAZY_IMPORT_SUCCESS:
            print("❌ Невозможно импортировать lazy_wrappers модуль")
            return self.test_results
        
        # Список тестов
        tests = [
            ("Создание Lazy Wrapper", self.test_lazy_wrapper_creation),
            ("Загрузка Lazy Wrapper", self.test_lazy_wrapper_loading),
            ("Выгрузка Lazy Wrapper", self.test_lazy_wrapper_unloading),
            ("Статистика Lazy Manager", self.test_lazy_manager_stats),
            ("Инициализация системы", self.test_lazy_system_initialization),
            ("Статистика системы", self.test_lazy_system_stats),
            ("Информация о Wrapper", self.test_lazy_wrapper_info),
            ("Обработка ошибок", self.test_lazy_wrapper_error_handling),
            ("Производительность", self.test_lazy_wrapper_performance)
        ]
        
        # Запуск тестов
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Итоговая статистика
        total_time = sum(test['duration'] for test in self.test_results['test_details'])
        success_rate = (self.test_results['passed_tests'] / self.test_results['total_tests']) * 100
        
        print("\n" + "=" * 60)
        print("📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"   📁 Всего тестов: {self.test_results['total_tests']}")
        print(f"   ✅ Пройдено: {self.test_results['passed_tests']}")
        print(f"   ❌ Провалено: {self.test_results['failed_tests']}")
        print(f"   📈 Успешность: {success_rate:.1f}%")
        print(f"   ⏱️ Общее время: {total_time:.3f}s")
        
        if success_rate >= 80:
            print("🎯 ОЦЕНКА: ОТЛИЧНО!")
        elif success_rate >= 60:
            print("🎯 ОЦЕНКА: ХОРОШО!")
        else:
            print("🎯 ОЦЕНКА: ТРЕБУЕТ УЛУЧШЕНИЯ!")
        
        return self.test_results

def test_lazy_loading_integration():
    """Тест интеграции с SFM"""
    print("\n🔗 ТЕСТ ИНТЕГРАЦИИ С SFM")
    print("=" * 40)
    
    try:
        # Проверка что lazy_wrappers.py существует
        lazy_file = "security/lazy_wrappers.py"
        if os.path.exists(lazy_file):
            print(f"✅ Файл {lazy_file} найден")
        else:
            print(f"❌ Файл {lazy_file} не найден")
            return False
        
        # Проверка что lazy_wrappers директория существует
        lazy_dir = "security/lazy_wrappers"
        if os.path.exists(lazy_dir):
            files = [f for f in os.listdir(lazy_dir) if f.endswith('.py')]
            print(f"✅ Директория {lazy_dir} найдена ({len(files)} файлов)")
        else:
            print(f"❌ Директория {lazy_dir} не найдена")
            return False
        
        # Проверка SFM интеграции
        sfm_file = "security/safe_function_manager.py"
        if os.path.exists(sfm_file):
            with open(sfm_file, 'r', encoding='utf-8') as f:
                sfm_content = f.read()
            
            if 'lazy_wrappers' in sfm_content:
                print("✅ SFM содержит интеграцию с lazy_wrappers")
            else:
                print("⚠️ SFM не содержит интеграцию с lazy_wrappers")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ LAZY LOADING СИСТЕМЫ")
    print("=" * 80)
    
    # Создание тестера
    tester = LazyLoadingTester()
    
    # Запуск тестов
    results = tester.run_all_tests()
    
    # Тест интеграции
    integration_success = test_lazy_loading_integration()
    
    # Сохранение результатов
    report_file = f"lazy_loading_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_results': results,
            'integration_success': integration_success,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Отчет сохранен: {report_file}")
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")

if __name__ == "__main__":
    main()
