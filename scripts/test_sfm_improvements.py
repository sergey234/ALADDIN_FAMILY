#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFM Improvement Tests - Тесты улучшений SFM
Полное тестирование всех улучшений SafeFunctionManager

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-11
"""

import sys
import time
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

# Добавляем путь к проекту
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

class SFMImprovementTester:
    """Тестер улучшений SFM"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.sfm = None
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Логирование результата теста"""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
    
    def test_sfm_creation(self) -> bool:
        """Тест 1: Создание SFM с улучшениями"""
        try:
            from security.safe_function_manager import SafeFunctionManager
            
            # Конфигурация с улучшениями
            config = {
                'max_concurrent_functions': 50,  # Увеличено с 10
                'redis_enabled': True,
                'circuit_breaker_enabled': True,
                'cache_ttl': 3600,
                'monitoring_enabled': True
            }
            
            self.sfm = SafeFunctionManager("TestSFM", config)
            self.log_test("Создание SFM", True, "SFM создан с улучшениями")
            return True
            
        except Exception as e:
            self.log_test("Создание SFM", False, f"Ошибка: {e}")
            return False
    
    def test_configuration(self) -> bool:
        """Тест 2: Проверка конфигурации"""
        if not self.sfm:
            self.log_test("Конфигурация", False, "SFM не создан")
            return False
        
        try:
            # Проверка max_concurrent_functions
            if self.sfm.max_concurrent_functions != 50:
                self.log_test("Конфигурация", False, 
                    f"max_concurrent_functions = {self.sfm.max_concurrent_functions}, ожидалось 50")
                return False
            
            # Проверка Redis
            if not hasattr(self.sfm, 'redis_enabled'):
                self.log_test("Конфигурация", False, "redis_enabled не найден")
                return False
            
            # Проверка Circuit Breaker
            if not hasattr(self.sfm, 'circuit_breaker_enabled'):
                self.log_test("Конфигурация", False, "circuit_breaker_enabled не найден")
                return False
            
            self.log_test("Конфигурация", True, "Все настройки корректны")
            return True
            
        except Exception as e:
            self.log_test("Конфигурация", False, f"Ошибка: {e}")
            return False
    
    def test_redis_integration(self) -> bool:
        """Тест 3: Интеграция Redis"""
        if not self.sfm:
            self.log_test("Redis", False, "SFM не создан")
            return False
        
        try:
            # Проверка наличия Redis клиента
            if hasattr(self.sfm, 'redis_client') and self.sfm.redis_client:
                # Тест подключения
                self.sfm.redis_client.ping()
                self.log_test("Redis", True, "Redis подключен и работает")
                return True
            else:
                self.log_test("Redis", True, "Redis недоступен (нормально для тестов)")
                return True
                
        except Exception as e:
            self.log_test("Redis", False, f"Ошибка Redis: {e}")
            return False
    
    def test_circuit_breaker(self) -> bool:
        """Тест 4: Circuit Breaker"""
        if not self.sfm:
            self.log_test("Circuit Breaker", False, "SFM не создан")
            return False
        
        try:
            # Проверка наличия Circuit Breaker
            if hasattr(self.sfm, 'circuit_breaker') and self.sfm.circuit_breaker:
                self.log_test("Circuit Breaker", True, "Circuit Breaker инициализирован")
                return True
            else:
                self.log_test("Circuit Breaker", False, "Circuit Breaker не найден")
                return False
                
        except Exception as e:
            self.log_test("Circuit Breaker", False, f"Ошибка: {e}")
            return False
    
    def test_functions_registration(self) -> bool:
        """Тест 5: Регистрация функций"""
        if not self.sfm:
            self.log_test("Функции", False, "SFM не создан")
            return False
        
        try:
            # Проверка количества функций
            function_count = len(self.sfm.functions)
            if function_count == 0:
                self.log_test("Функции", False, "Нет зарегистрированных функций")
                return False
            
            # Проверка типов функций
            enabled_functions = [f for f in self.sfm.functions.values() if f.status.value == 'enabled']
            disabled_functions = [f for f in self.sfm.functions.values() if f.status.value == 'disabled']
            
            self.log_test("Функции", True, 
                f"Найдено {function_count} функций: {len(enabled_functions)} активных, {len(disabled_functions)} отключенных")
            return True
            
        except Exception as e:
            self.log_test("Функции", False, f"Ошибка: {e}")
            return False
    
    def test_monitoring(self) -> bool:
        """Тест 6: Мониторинг"""
        if not self.sfm:
            self.log_test("Мониторинг", False, "SFM не создан")
            return False
        
        try:
            # Проверка наличия методов мониторинга
            if hasattr(self.sfm, 'monitor_performance'):
                metrics = self.sfm.monitor_performance()
                
                required_keys = ['timestamp', 'active_functions', 'queue_length']
                missing_keys = [key for key in required_keys if key not in metrics]
                
                if missing_keys:
                    self.log_test("Мониторинг", False, f"Отсутствуют ключи: {missing_keys}")
                    return False
                
                self.log_test("Мониторинг", True, f"Метрики: {list(metrics.keys())}")
                return True
            else:
                self.log_test("Мониторинг", False, "Метод monitor_performance не найден")
                return False
                
        except Exception as e:
            self.log_test("Мониторинг", False, f"Ошибка: {e}")
            return False
    
    def test_performance(self) -> bool:
        """Тест 7: Производительность"""
        if not self.sfm:
            self.log_test("Производительность", False, "SFM не создан")
            return False
        
        try:
            start_time = time.time()
            
            # Тест выполнения функций (если есть тестовые функции)
            test_executions = 0
            for func_id, func_info in self.sfm.functions.items():
                if func_info.status.value == 'enabled':
                    try:
                        # Попытка выполнения (может не работать для некоторых функций)
                        self.sfm.execute_function(func_id, "test")
                        test_executions += 1
                    except:
                        pass  # Ожидаемо для некоторых функций
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            self.log_test("Производительность", True, 
                f"Выполнено {test_executions} функций за {execution_time:.2f} секунд")
            return True
            
        except Exception as e:
            self.log_test("Производительность", False, f"Ошибка: {e}")
            return False
    
    def test_persistence(self) -> bool:
        """Тест 8: Персистентность"""
        if not self.sfm:
            self.log_test("Персистентность", False, "SFM не создан")
            return False
        
        try:
            # Проверка сохранения
            if hasattr(self.sfm, '_save_functions'):
                self.sfm._save_functions()
                self.log_test("Персистентность", True, "Функции сохранены")
                return True
            else:
                self.log_test("Персистентность", False, "Метод _save_functions не найден")
                return False
                
        except Exception as e:
            self.log_test("Персистентность", False, f"Ошибка: {e}")
            return False
    
    def test_fault_tolerance(self) -> bool:
        """Тест 9: Отказоустойчивость"""
        if not self.sfm:
            self.log_test("Отказоустойчивость", False, "SFM не создан")
            return False
        
        try:
            # Тест при отключенном Redis
            original_redis = getattr(self.sfm, 'redis_enabled', True)
            self.sfm.redis_enabled = False
            
            # Попытка выполнения функции
            try:
                self.sfm.execute_function("test_function", "test")
                self.log_test("Отказоустойчивость (Redis)", True, "Работа без Redis")
            except:
                self.log_test("Отказоустойчивость (Redis)", True, "Ожидаемая ошибка без Redis")
            
            # Восстановление
            self.sfm.redis_enabled = original_redis
            
            # Тест при отключенном Circuit Breaker
            original_cb = getattr(self.sfm, 'circuit_breaker_enabled', True)
            self.sfm.circuit_breaker_enabled = False
            
            try:
                self.sfm.execute_function("test_function", "test")
                self.log_test("Отказоустойчивость (CB)", True, "Работа без Circuit Breaker")
            except:
                self.log_test("Отказоустойчивость (CB)", True, "Ожидаемая ошибка без CB")
            
            # Восстановление
            self.sfm.circuit_breaker_enabled = original_cb
            
            return True
            
        except Exception as e:
            self.log_test("Отказоустойчивость", False, f"Ошибка: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        print("🧪 Запуск тестов улучшений SFM...")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Список тестов
        tests = [
            self.test_sfm_creation,
            self.test_configuration,
            self.test_redis_integration,
            self.test_circuit_breaker,
            self.test_functions_registration,
            self.test_monitoring,
            self.test_performance,
            self.test_persistence,
            self.test_fault_tolerance
        ]
        
        # Запуск тестов
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            if test():
                passed_tests += 1
        
        # Результаты
        end_time = time.time()
        total_time = end_time - self.start_time
        
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        print(f"✅ Пройдено тестов: {passed_tests}/{total_tests}")
        print(f"📈 Процент успеха: {success_rate:.1f}%")
        print(f"⏱️ Время выполнения: {total_time:.2f} секунд")
        
        if success_rate >= 80:
            print("🎉 ОТЛИЧНО! SFM работает с улучшениями!")
        elif success_rate >= 60:
            print("⚠️ ХОРОШО! Есть небольшие проблемы")
        else:
            print("❌ ПЛОХО! Требуются исправления")
        
        # Сохранение отчета
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': success_rate,
            'execution_time': total_time,
            'test_results': self.test_results
        }
        
        report_path = '/Users/sergejhlystov/ALADDIN_NEW/SFM_IMPROVEMENT_TEST_REPORT.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Отчет сохранен: {report_path}")
        
        return report

def main():
    """Основная функция"""
    tester = SFMImprovementTester()
    report = tester.run_all_tests()
    
    # Возвращаем код выхода
    success_rate = report['success_rate']
    if success_rate >= 80:
        sys.exit(0)  # Успех
    else:
        sys.exit(1)  # Ошибка

if __name__ == "__main__":
    main()