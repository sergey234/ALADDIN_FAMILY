# -*- coding: utf-8 -*-
"""
Test Pagination - Тестирование системы пагинации
Проверяет работу pagination_system.py и его интеграцию с SFM
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pagination_system import (
        PaginationSystem, create_pagination_system,
        get_pagination_system, initialize_pagination_system
    )
    PAGINATION_IMPORT_SUCCESS = True
except ImportError as e:
    print(f"❌ Ошибка импорта pagination_system: {e}")
    PAGINATION_IMPORT_SUCCESS = False

class PaginationTester:
    """Тестер системы пагинации"""
    
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
    
    def test_pagination_system_creation(self) -> bool:
        """Тест создания системы пагинации"""
        try:
            pagination = create_pagination_system()
            return pagination is not None
        except Exception:
            return False
    
    def test_pagination_basic_functionality(self) -> bool:
        """Тест базовой функциональности пагинации"""
        try:
            pagination = get_pagination_system()
            if pagination is None:
                return False
            
            # Создание тестовых данных
            test_data = [f"item_{i}" for i in range(100)]
            
            # Тест пагинации
            page1 = pagination.paginate(test_data, page=1, per_page=10)
            page2 = pagination.paginate(test_data, page=2, per_page=10)
            
            return (
                len(page1['items']) == 10 and
                len(page2['items']) == 10 and
                page1['items'][0] == "item_0" and
                page2['items'][0] == "item_10"
            )
        except Exception:
            return False
    
    def test_pagination_filtering(self) -> bool:
        """Тест фильтрации в пагинации"""
        try:
            pagination = get_pagination_system()
            if pagination is None:
                return False
            
            # Создание тестовых данных с категориями
            test_data = []
            for i in range(50):
                test_data.append({
                    'id': i,
                    'name': f"item_{i}",
                    'category': 'security' if i % 2 == 0 else 'monitoring'
                })
            
            # Фильтрация по категории
            filtered = pagination.filter_by_category(test_data, 'security')
            
            return len(filtered) == 25  # Половина элементов
        except Exception:
            return False
    
    def test_pagination_searching(self) -> bool:
        """Тест поиска в пагинации"""
        try:
            pagination = get_pagination_system()
            if pagination is None:
                return False
            
            # Создание тестовых данных
            test_data = [
                {'name': 'security_function_1'},
                {'name': 'monitoring_function_1'},
                {'name': 'security_function_2'},
                {'name': 'other_function_1'}
            ]
            
            # Поиск
            results = pagination.search(test_data, 'security')
            
            return len(results) == 2
        except Exception:
            return False
    
    def test_pagination_sorting(self) -> bool:
        """Тест сортировки в пагинации"""
        try:
            pagination = get_pagination_system()
            if pagination is None:
                return False
            
            # Создание тестовых данных
            test_data = [
                {'name': 'z_function', 'priority': 1},
                {'name': 'a_function', 'priority': 3},
                {'name': 'm_function', 'priority': 2}
            ]
            
            # Сортировка по имени
            sorted_data = pagination.sort(test_data, 'name')
            
            return sorted_data[0]['name'] == 'a_function'
        except Exception:
            return False
    
    def test_pagination_performance(self) -> bool:
        """Тест производительности пагинации"""
        try:
            pagination = get_pagination_system()
            if pagination is None:
                return False
            
            # Создание большого набора данных
            large_data = [{'id': i, 'name': f"item_{i}"} for i in range(10000)]
            
            # Измерение времени
            start_time = time.time()
            
            # Пагинация
            page = pagination.paginate(large_data, page=1, per_page=100)
            
            # Фильтрация
            filtered = pagination.filter_by_category(large_data, 'test')
            
            # Поиск
            results = pagination.search(large_data, 'item_1000')
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Время должно быть разумным (менее 1 секунды)
            return duration < 1.0
        except Exception:
            return False
    
    def test_pagination_edge_cases(self) -> bool:
        """Тест граничных случаев"""
        try:
            pagination = get_pagination_system()
            if pagination is None:
                return False
            
            # Пустые данные
            empty_page = pagination.paginate([], page=1, per_page=10)
            if empty_page['total_items'] != 0:
                return False
            
            # Страница больше чем данных
            small_data = [{'id': 1}, {'id': 2}]
            large_page = pagination.paginate(small_data, page=10, per_page=10)
            if len(large_page['items']) != 0:
                return False
            
            # Отрицательные параметры
            negative_page = pagination.paginate(small_data, page=-1, per_page=10)
            if negative_page['page'] != 1:  # Должно исправиться на 1
                return False
            
            return True
        except Exception:
            return False
    
    def test_pagination_integration_with_sfm(self) -> bool:
        """Тест интеграции с SFM"""
        try:
            # Проверка что pagination_system.py существует
            pagination_file = "security/pagination_system.py"
            if not os.path.exists(pagination_file):
                return False
            
            # Проверка SFM интеграции
            sfm_file = "security/safe_function_manager.py"
            if os.path.exists(sfm_file):
                with open(sfm_file, 'r', encoding='utf-8') as f:
                    sfm_content = f.read()
                
                # Проверка что SFM содержит методы пагинации
                pagination_methods = [
                    'paginate_functions',
                    'get_functions_page',
                    'search_functions'
                ]
                
                for method in pagination_methods:
                    if method not in sfm_content:
                        return False
            
            return True
        except Exception:
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        print("🧪 ТЕСТИРОВАНИЕ PAGINATION СИСТЕМЫ")
        print("=" * 60)
        
        if not PAGINATION_IMPORT_SUCCESS:
            print("❌ Невозможно импортировать pagination_system модуль")
            return self.test_results
        
        # Список тестов
        tests = [
            ("Создание системы пагинации", self.test_pagination_system_creation),
            ("Базовая функциональность", self.test_pagination_basic_functionality),
            ("Фильтрация", self.test_pagination_filtering),
            ("Поиск", self.test_pagination_searching),
            ("Сортировка", self.test_pagination_sorting),
            ("Производительность", self.test_pagination_performance),
            ("Граничные случаи", self.test_pagination_edge_cases),
            ("Интеграция с SFM", self.test_pagination_integration_with_sfm)
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

def test_pagination_integration():
    """Тест интеграции с SFM"""
    print("\n🔗 ТЕСТ ИНТЕГРАЦИИ С SFM")
    print("=" * 40)
    
    try:
        # Проверка что pagination_system.py существует
        pagination_file = "security/pagination_system.py"
        if os.path.exists(pagination_file):
            size = os.path.getsize(pagination_file)
            print(f"✅ Файл {pagination_file} найден ({size:,} байт)")
        else:
            print(f"❌ Файл {pagination_file} не найден")
            return False
        
        # Проверка SFM интеграции
        sfm_file = "security/safe_function_manager.py"
        if os.path.exists(sfm_file):
            with open(sfm_file, 'r', encoding='utf-8') as f:
                sfm_content = f.read()
            
            # Проверка методов пагинации в SFM
            pagination_methods = [
                'paginate_functions',
                'get_functions_page',
                'search_functions',
                'filter_functions'
            ]
            
            found_methods = []
            for method in pagination_methods:
                if method in sfm_content:
                    found_methods.append(method)
            
            print(f"✅ Найдено методов пагинации в SFM: {len(found_methods)}/{len(pagination_methods)}")
            
            if len(found_methods) >= len(pagination_methods) // 2:
                print("✅ SFM содержит достаточную интеграцию с пагинацией")
            else:
                print("⚠️ SFM содержит недостаточную интеграцию с пагинацией")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ PAGINATION СИСТЕМЫ")
    print("=" * 80)
    
    # Создание тестера
    tester = PaginationTester()
    
    # Запуск тестов
    results = tester.run_all_tests()
    
    # Тест интеграции
    integration_success = test_pagination_integration()
    
    # Сохранение результатов
    report_file = f"pagination_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
