#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Мониторинг системных ресурсов и производительности SFM
Отслеживание CPU, RAM и скорости отклика при активации функций
"""

import sys
import os
import time
import psutil
import threading
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager

class SystemMonitor:
    def __init__(self):
        self.monitoring = False
        self.start_time = None
        self.baseline_cpu = 0
        self.baseline_ram = 0
        self.sfm = None
        
    def get_system_stats(self):
        """Получение текущих системных ресурсов"""
        cpu_percent = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        ram_percent = ram.percent
        ram_used_gb = ram.used / (1024**3)
        ram_total_gb = ram.total / (1024**3)
        
        return {
            'cpu_percent': cpu_percent,
            'ram_percent': ram_percent,
            'ram_used_gb': ram_used_gb,
            'ram_total_gb': ram_total_gb,
            'ram_available_gb': ram.available / (1024**3)
        }
    
    def get_sfm_stats(self):
        """Получение статистики SFM"""
        if not self.sfm:
            return None
            
        total_functions = len(self.sfm.functions)
        active_count = 0
        sleeping_count = 0
        critical_count = 0
        critical_sleeping = 0
        
        for func_id, func_obj in self.sfm.functions.items():
            if getattr(func_obj, 'is_critical', False):
                critical_count += 1
                status = str(getattr(func_obj, 'status', ''))
                if 'sleep' in status.lower():
                    critical_sleeping += 1
            
            status = str(getattr(func_obj, 'status', ''))
            if 'active' in status.lower():
                active_count += 1
            elif 'sleep' in status.lower():
                sleeping_count += 1
        
        return {
            'total_functions': total_functions,
            'active_functions': active_count,
            'sleeping_functions': sleeping_count,
            'critical_functions': critical_count,
            'critical_sleeping': critical_sleeping,
            'active_percentage': (active_count / total_functions * 100) if total_functions > 0 else 0
        }
    
    def test_sfm_response_time(self, iterations=10):
        """Тестирование скорости отклика SFM"""
        if not self.sfm:
            return None
            
        start_time = time.time()
        
        # Тестируем различные операции SFM
        for i in range(iterations):
            # Тест 1: Получение списка функций
            _ = list(self.sfm.functions.keys())
            
            # Тест 2: Поиск критических функций
            critical_functions = []
            for func_id, func_obj in self.sfm.functions.items():
                if getattr(func_obj, 'is_critical', False):
                    critical_functions.append(func_id)
            
            # Тест 3: Подсчет активных функций
            active_count = 0
            for func_id, func_obj in self.sfm.functions.items():
                status = str(getattr(func_obj, 'status', ''))
                if 'active' in status.lower():
                    active_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_response_time = total_time / iterations
        
        return {
            'total_time': total_time,
            'avg_response_time': avg_response_time,
            'operations_per_second': iterations / total_time,
            'iterations': iterations
        }
    
    def print_dashboard(self):
        """Вывод информационной панели"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🖥️  МОНИТОРИНГ СИСТЕМЫ ALADDIN")
        print("=" * 60)
        print(f"⏰ Время: {datetime.now().strftime('%H:%M:%S')}")
        print(f"⏱️  Работает: {time.time() - self.start_time:.1f} сек" if self.start_time else "⏱️  Не запущен")
        print()
        
        # Системные ресурсы
        sys_stats = self.get_system_stats()
        print("💻 СИСТЕМНЫЕ РЕСУРСЫ:")
        print(f"   🖥️  CPU: {sys_stats['cpu_percent']:.1f}%")
        print(f"   💾 RAM: {sys_stats['ram_percent']:.1f}% ({sys_stats['ram_used_gb']:.2f}GB / {sys_stats['ram_total_gb']:.2f}GB)")
        print(f"   📊 Доступно RAM: {sys_stats['ram_available_gb']:.2f}GB")
        print()
        
        # SFM статистика
        sfm_stats = self.get_sfm_stats()
        if sfm_stats:
            print("🔧 СТАТИСТИКА SFM:")
            print(f"   📦 Всего функций: {sfm_stats['total_functions']}")
            print(f"   ✅ Активных: {sfm_stats['active_functions']} ({sfm_stats['active_percentage']:.1f}%)")
            print(f"   💤 Спящих: {sfm_stats['sleeping_functions']}")
            print(f"   🚨 Критических: {sfm_stats['critical_functions']}")
            print(f"   ⚠️  Критических спящих: {sfm_stats['critical_sleeping']}")
            print()
            
            # Производительность SFM
            perf_stats = self.test_sfm_response_time(5)
            if perf_stats:
                print("⚡ ПРОИЗВОДИТЕЛЬНОСТЬ SFM:")
                print(f"   🏃 Средний отклик: {perf_stats['avg_response_time']*1000:.2f} мс")
                print(f"   🚀 Операций/сек: {perf_stats['operations_per_second']:.1f}")
                print(f"   ⏱️  Время теста: {perf_stats['total_time']:.3f} сек")
                print()
        
        # Изменения от базовой линии
        if self.baseline_cpu > 0:
            cpu_change = sys_stats['cpu_percent'] - self.baseline_cpu
            ram_change = sys_stats['ram_percent'] - self.baseline_ram
            print("📈 ИЗМЕНЕНИЯ ОТ БАЗОВОЙ ЛИНИИ:")
            print(f"   🖥️  CPU: {cpu_change:+.1f}%")
            print(f"   💾 RAM: {ram_change:+.1f}%")
            print()
    
    def set_baseline(self):
        """Установка базовой линии для сравнения"""
        sys_stats = self.get_system_stats()
        self.baseline_cpu = sys_stats['cpu_percent']
        self.baseline_ram = sys_stats['ram_percent']
        print(f"✅ Базовая линия установлена: CPU {self.baseline_cpu:.1f}%, RAM {self.baseline_ram:.1f}%")
    
    def initialize_sfm(self):
        """Инициализация SFM для мониторинга"""
        print("🔧 Инициализация SFM для мониторинга...")
        
        config = {
            'thread_pool_enabled': True,
            'max_thread_pool_workers': 5,
            'async_io_enabled': True,
            'redis_cache_enabled': True,
            'enable_auto_management': False,
            'enable_sleep_mode': False
        }
        
        try:
            self.sfm = SafeFunctionManager('MonitorSFM', config)
            print(f"✅ SFM инициализирован: {len(self.sfm.functions)} функций")
        except Exception as e:
            print(f"❌ Ошибка инициализации SFM: {e}")
            self.sfm = None
    
    def start_monitoring(self, interval=2):
        """Запуск мониторинга"""
        self.start_time = time.time()
        self.monitoring = True
        
        print("🚀 Запуск мониторинга системы...")
        print("   Нажмите Ctrl+C для остановки")
        print()
        
        try:
            while self.monitoring:
                self.print_dashboard()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n⏹️  Мониторинг остановлен пользователем")
            self.monitoring = False
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.monitoring = False

def main():
    monitor = SystemMonitor()
    
    print("🖥️  МОНИТОРИНГ СИСТЕМЫ ALADDIN")
    print("=" * 50)
    print()
    
    # Инициализация SFM
    monitor.initialize_sfm()
    
    # Установка базовой линии
    print("📊 Установка базовой линии...")
    monitor.set_baseline()
    
    print()
    print("🎯 Готов к мониторингу!")
    print("   Команды:")
    print("   - Enter: Показать текущий статус")
    print("   - 'b': Установить новую базовую линию")
    print("   - 'm': Запустить непрерывный мониторинг")
    print("   - 'q': Выход")
    print()
    
    while True:
        try:
            command = input("Введите команду: ").strip().lower()
            
            if command == '' or command == 's':
                monitor.print_dashboard()
            elif command == 'b':
                monitor.set_baseline()
            elif command == 'm':
                monitor.start_monitoring()
            elif command == 'q':
                print("👋 Выход из мониторинга")
                break
            else:
                print("❓ Неизвестная команда")
                
        except KeyboardInterrupt:
            print("\n👋 Выход из мониторинга")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()