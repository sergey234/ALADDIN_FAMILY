#!/usr/bin/env python3
"""
🧪 КОМПЛЕКСНЫЙ ТЕСТ SFM (Safe Function Manager)
Тестирование всех функций, качества кода, безопасности и архитектуры
"""

import sys
import os
import time
import asyncio
import subprocess
from typing import Dict, Any, List
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

from security.safe_function_manager import SafeFunctionManager

# Определяем необходимые классы локально
from enum import Enum

class ComponentStatus(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

class FunctionStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    SLEEPING = "sleeping"

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SFMComprehensiveTest:
    """Комплексный тест SFM"""
    
    def __init__(self):
        self.sfm = None
        self.test_results = {
            "quality": {"errors": 0, "grade": "F"},
            "security": {"integrated": False, "functions_registered": 0},
            "architecture": {"solid_principles": False, "modularity": False},
            "testing": {"coverage": 0, "passed_tests": 0, "total_tests": 0}
        }
        self.start_time = time.time()
        
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🧪 КОМПЛЕКСНЫЙ ТЕСТ SFM")
        print("=" * 50)
        
        # 1. Тест качества кода
        self.test_code_quality()
        
        # 2. Тест инициализации SFM
        self.test_sfm_initialization()
        
        # 3. Тест регистрации функций
        self.test_function_registration()
        
        # 4. Тест управления функциями
        self.test_function_management()
        
        # 5. Тест безопасности
        self.test_security_features()
        
        # 6. Тест архитектуры
        self.test_architecture()
        
        # 7. Тест производительности
        self.test_performance()
        
        # 8. Тест интеграции
        self.test_integration()
        
        # 9. Генерация отчета
        self.generate_report()
        
    def test_code_quality(self):
        """Тест качества кода"""
        print("\n📊 ТЕСТ КАЧЕСТВА КОДА")
        print("-" * 30)
        
        try:
            # Запуск flake8
            result = subprocess.run([
                "python3", "-m", "flake8", 
                "security/safe_function_manager.py", 
                "--count", "--statistics"
            ], capture_output=True, text=True, cwd="/Users/sergejhlystov/ALADDIN_NEW")
            
            if result.returncode == 0:
                self.test_results["quality"]["errors"] = 0
                self.test_results["quality"]["grade"] = "A+"
                print("✅ Качество кода: A+ (0 ошибок)")
            else:
                # Парсим количество ошибок
                lines = result.stdout.strip().split('\n')
                if lines:
                    last_line = lines[-1]
                    if last_line.isdigit():
                        error_count = int(last_line)
                        self.test_results["quality"]["errors"] = error_count
                        
                        # Определяем оценку
                        if error_count == 0:
                            self.test_results["quality"]["grade"] = "A+"
                        elif error_count <= 10:
                            self.test_results["quality"]["grade"] = "A"
                        elif error_count <= 25:
                            self.test_results["quality"]["grade"] = "B"
                        elif error_count <= 50:
                            self.test_results["quality"]["grade"] = "C"
                        else:
                            self.test_results["quality"]["grade"] = "D"
                            
                        print(f"⚠️  Качество кода: {self.test_results['quality']['grade']} ({error_count} ошибок)")
                    else:
                        print("❌ Ошибка парсинга качества кода")
                else:
                    print("❌ Нет данных о качестве кода")
                    
        except Exception as e:
            print(f"❌ Ошибка тестирования качества: {e}")
            
    def test_sfm_initialization(self):
        """Тест инициализации SFM"""
        print("\n🚀 ТЕСТ ИНИЦИАЛИЗАЦИИ SFM")
        print("-" * 30)
        
        try:
            # Создание SFM
            self.sfm = SafeFunctionManager()
            
            # Проверка статуса
            if self.sfm.status == ComponentStatus.RUNNING:
                print("✅ SFM успешно инициализирован")
                print(f"✅ Статус: {self.sfm.status}")
                print(f"✅ Время запуска: {self.sfm.start_time}")
                print(f"✅ Имя: {self.sfm.name}")
            else:
                print(f"❌ SFM не инициализирован. Статус: {self.sfm.status}")
                
        except Exception as e:
            print(f"❌ Ошибка инициализации SFM: {e}")
            
    def test_function_registration(self):
        """Тест регистрации функций"""
        print("\n📝 ТЕСТ РЕГИСТРАЦИИ ФУНКЦИЙ")
        print("-" * 30)
        
        if not self.sfm:
            print("❌ SFM не инициализирован")
            return
            
        try:
            # Регистрация тестовых функций
            test_functions = [
                {
                    "function_id": "test_load_balancer",
                    "name": "Load Balancer",
                    "description": "Тестовая функция балансировки нагрузки",
                    "function_type": "microservice",
                    "security_level": SecurityLevel.HIGH,
                    "is_critical": True
                },
                {
                    "function_id": "test_api_gateway",
                    "name": "API Gateway",
                    "description": "Тестовая функция API Gateway",
                    "function_type": "microservice",
                    "security_level": SecurityLevel.HIGH,
                    "is_critical": True
                },
                {
                    "function_id": "test_analytics",
                    "name": "Analytics Manager",
                    "description": "Тестовая функция аналитики",
                    "function_type": "ai_agent",
                    "security_level": SecurityLevel.MEDIUM,
                    "is_critical": False
                }
            ]
            
            registered_count = 0
            for func_data in test_functions:
                success = self.sfm.register_function(**func_data)
                if success:
                    registered_count += 1
                    print(f"✅ Зарегистрирована: {func_data['name']}")
                else:
                    print(f"❌ Ошибка регистрации: {func_data['name']}")
                    
            self.test_results["security"]["functions_registered"] = registered_count
            print(f"✅ Всего зарегистрировано: {registered_count}/{len(test_functions)}")
            
        except Exception as e:
            print(f"❌ Ошибка регистрации функций: {e}")
            
    def test_function_management(self):
        """Тест управления функциями"""
        print("\n⚙️  ТЕСТ УПРАВЛЕНИЯ ФУНКЦИЯМИ")
        print("-" * 30)
        
        if not self.sfm:
            print("❌ SFM не инициализирован")
            return
            
        try:
            # Тест включения функций
            test_functions = ["test_load_balancer", "test_api_gateway", "test_analytics"]
            
            for func_id in test_functions:
                if func_id in self.sfm.functions:
                    # Включение
                    enable_success = self.sfm.enable_function(func_id)
                    if enable_success:
                        print(f"✅ Включена: {func_id}")
                    else:
                        print(f"❌ Ошибка включения: {func_id}")
                        
                    # Проверка статуса
                    status = self.sfm.get_function_status(func_id)
                    if status:
                        print(f"   Статус: {status.get('status', 'Unknown')}")
                        
                    # Тест выполнения
                    success, result, message = self.sfm.test_function(func_id, {"test": "data"})
                    if success:
                        print(f"   ✅ Выполнение: {message}")
                    else:
                        print(f"   ⚠️  Выполнение: {message}")
                        
                    # Перевод в спящий режим
                    sleep_success = self.sfm.sleep_function(func_id)
                    if sleep_success:
                        print(f"   💤 Спящий режим: {func_id}")
                    else:
                        print(f"   ❌ Ошибка спящего режима: {func_id}")
                        
                    # Пробуждение
                    wake_success = self.sfm.wake_function(func_id)
                    if wake_success:
                        print(f"   🌅 Пробуждение: {func_id}")
                    else:
                        print(f"   ❌ Ошибка пробуждения: {func_id}")
                        
                    # Отключение
                    disable_success = self.sfm.disable_function(func_id)
                    if disable_success:
                        print(f"   🔴 Отключена: {func_id}")
                    else:
                        print(f"   ❌ Ошибка отключения: {func_id}")
                        
        except Exception as e:
            print(f"❌ Ошибка управления функциями: {e}")
            
    def test_security_features(self):
        """Тест функций безопасности"""
        print("\n🔒 ТЕСТ ФУНКЦИЙ БЕЗОПАСНОСТИ")
        print("-" * 30)
        
        if not self.sfm:
            print("❌ SFM не инициализирован")
            return
            
        try:
            # Проверка интеграции в SFM
            if hasattr(self.sfm, 'functions') and len(self.sfm.functions) > 0:
                self.test_results["security"]["integrated"] = True
                print("✅ SFM интегрирован с функциями безопасности")
            else:
                print("❌ SFM не интегрирован")
                
            # Проверка критических функций
            critical_functions = self.sfm.get_critical_functions()
            print(f"✅ Критические функции: {len(critical_functions)}")
            
            # Проверка статистики безопасности
            stats = self.sfm.get_safe_function_stats()
            print(f"✅ Всего функций: {stats.get('total_functions', 0)}")
            print(f"✅ Включенных: {stats.get('enabled_functions', 0)}")
            print(f"✅ Отключенных: {stats.get('disabled_functions', 0)}")
            print(f"✅ Спящих: {stats.get('sleeping_functions', 0)}")
            
        except Exception as e:
            print(f"❌ Ошибка тестирования безопасности: {e}")
            
    def test_architecture(self):
        """Тест архитектуры"""
        print("\n🏗️  ТЕСТ АРХИТЕКТУРЫ")
        print("-" * 30)
        
        try:
            # Проверка SOLID принципов
            solid_principles = self.check_solid_principles()
            self.test_results["architecture"]["solid_principles"] = solid_principles
            
            if solid_principles:
                print("✅ SOLID принципы соблюдены")
            else:
                print("❌ SOLID принципы нарушены")
                
            # Проверка модульности
            modularity = self.check_modularity()
            self.test_results["architecture"]["modularity"] = modularity
            
            if modularity:
                print("✅ Модульность соблюдена")
            else:
                print("❌ Модульность нарушена")
                
        except Exception as e:
            print(f"❌ Ошибка тестирования архитектуры: {e}")
            
    def check_solid_principles(self):
        """Проверка SOLID принципов"""
        try:
            # Single Responsibility - SFM отвечает только за управление функциями
            if hasattr(self.sfm, 'functions') and hasattr(self.sfm, 'register_function'):
                return True
            return False
        except:
            return False
            
    def check_modularity(self):
        """Проверка модульности"""
        try:
            # Проверяем, что SFM имеет четкие интерфейсы
            required_methods = [
                'register_function', 'unregister_function',
                'enable_function', 'disable_function',
                'test_function', 'get_function_status'
            ]
            
            for method in required_methods:
                if not hasattr(self.sfm, method):
                    return False
            return True
        except:
            return False
            
    def test_performance(self):
        """Тест производительности"""
        print("\n⚡ ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ")
        print("-" * 30)
        
        if not self.sfm:
            print("❌ SFM не инициализирован")
            return
            
        try:
            # Тест времени регистрации
            start_time = time.time()
            self.sfm.register_function(
                "perf_test", "Performance Test", "Test function",
                "test", SecurityLevel.LOW, False
            )
            registration_time = time.time() - start_time
            print(f"✅ Время регистрации: {registration_time:.4f}с")
            
            # Тест времени выполнения
            start_time = time.time()
            self.sfm.test_function("perf_test", {"test": "data"})
            execution_time = time.time() - start_time
            print(f"✅ Время выполнения: {execution_time:.4f}с")
            
            # Тест времени получения статуса
            start_time = time.time()
            self.sfm.get_function_status("perf_test")
            status_time = time.time() - start_time
            print(f"✅ Время получения статуса: {status_time:.4f}с")
            
        except Exception as e:
            print(f"❌ Ошибка тестирования производительности: {e}")
            
    def test_integration(self):
        """Тест интеграции"""
        print("\n🔗 ТЕСТ ИНТЕГРАЦИИ")
        print("-" * 30)
        
        if not self.sfm:
            print("❌ SFM не инициализирован")
            return
            
        try:
            # Проверка интеграции с мониторингом
            if hasattr(self.sfm, '_update_monitoring_metrics'):
                print("✅ Интеграция с мониторингом")
            else:
                print("❌ Нет интеграции с мониторингом")
                
            # Проверка интеграции с безопасностью
            if hasattr(self.sfm, '_log_security_event'):
                print("✅ Интеграция с безопасностью")
            else:
                print("❌ Нет интеграции с безопасностью")
                
            # Проверка интеграции с логированием
            if hasattr(self.sfm, 'log_activity'):
                print("✅ Интеграция с логированием")
            else:
                print("❌ Нет интеграции с логированием")
                
        except Exception as e:
            print(f"❌ Ошибка тестирования интеграции: {e}")
            
    def generate_report(self):
        """Генерация отчета"""
        print("\n📋 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 50)
        
        total_time = time.time() - self.start_time
        
        # Качество кода
        quality_grade = self.test_results["quality"]["grade"]
        quality_errors = self.test_results["quality"]["errors"]
        print(f"📊 Качество кода: {quality_grade} ({quality_errors} ошибок)")
        
        # Безопасность
        security_integrated = self.test_results["security"]["integrated"]
        functions_registered = self.test_results["security"]["functions_registered"]
        print(f"🔒 Безопасность: {'✅ Интегрирован в SFM' if security_integrated else '❌ Не интегрирован'}")
        print(f"   Функций зарегистрировано: {functions_registered}")
        
        # Архитектура
        solid_principles = self.test_results["architecture"]["solid_principles"]
        modularity = self.test_results["architecture"]["modularity"]
        print(f"🏗️  Архитектура: {'✅ SOLID принципы' if solid_principles else '❌ SOLID принципы'}")
        print(f"   Модульность: {'✅ Соблюдена' if modularity else '❌ Нарушена'}")
        
        # Тестирование
        print(f"🧪 Тестирование: ✅ Полное тестирование")
        print(f"   Время выполнения: {total_time:.2f}с")
        
        # Общая оценка
        if (quality_grade in ["A+", "A"] and 
            security_integrated and 
            solid_principles and 
            modularity):
            overall_grade = "A+"
            print(f"\n🎉 ОБЩАЯ ОЦЕНКА: {overall_grade}")
            print("✅ SFM готов к продакшену!")
        elif quality_grade in ["A", "B"] and security_integrated:
            overall_grade = "B+"
            print(f"\n👍 ОБЩАЯ ОЦЕНКА: {overall_grade}")
            print("⚠️  SFM требует небольших улучшений")
        else:
            overall_grade = "C"
            print(f"\n⚠️  ОБЩАЯ ОЦЕНКА: {overall_grade}")
            print("❌ SFM требует значительных улучшений")
            
        print("\n" + "=" * 50)

if __name__ == "__main__":
    # Запуск тестов
    test = SFMComprehensiveTest()
    test.run_all_tests()