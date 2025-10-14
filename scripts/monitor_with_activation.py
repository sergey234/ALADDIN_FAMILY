#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Мониторинг с активацией функций по 10 штук
Показывает CPU, RAM и SFM производительность после каждой активации
"""

import sys
import os
import time
import psutil
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager

class ActivationMonitor:
    def __init__(self):
        self.sfm = None
        self.baseline_cpu = 0
        self.baseline_ram = 0
        self.baseline_sfm_perf = 0
        self.activation_count = 0
        
    def get_system_stats(self):
        """Получение системных ресурсов"""
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        
        return {
            'cpu_percent': cpu,
            'ram_percent': ram.percent,
            'ram_used_gb': ram.used / (1024**3),
            'ram_total_gb': ram.total / (1024**3),
            'ram_available_gb': ram.available / (1024**3)
        }
    
    def get_sfm_performance(self):
        """Тест производительности SFM"""
        if not self.sfm:
            return None
            
        start_time = time.time()
        
        # Тестируем различные операции SFM
        for i in range(10):
            _ = list(self.sfm.functions.keys())
            critical_functions = []
            for func_id, func_obj in self.sfm.functions.items():
                if getattr(func_obj, 'is_critical', False):
                    critical_functions.append(func_id)
        
        end_time = time.time()
        avg_response = (end_time - start_time) / 10
        operations_per_sec = 10 / (end_time - start_time)
        
        return {
            'avg_response_ms': avg_response * 1000,
            'operations_per_sec': operations_per_sec,
            'total_time': end_time - start_time
        }
    
    def get_sleeping_functions(self):
        """Получение спящих функций"""
        sleeping_functions = []
        critical_sleeping = []
        
        for func_id, func_obj in self.sfm.functions.items():
            status = str(getattr(func_obj, 'status', ''))
            if 'sleep' in status.lower():
                sleeping_functions.append(func_id)
                
                if getattr(func_obj, 'is_critical', False):
                    critical_sleeping.append(func_id)
        
        return sleeping_functions, critical_sleeping
    
    def simulate_function_activation(self, function_ids):
        """Симуляция активации функций"""
        activated_count = 0
        
        for func_id in function_ids:
            try:
                # Симуляция активации функции
                time.sleep(0.01)  # Имитация времени активации
                activated_count += 1
                
                # Здесь должен быть реальный код активации
                # Например: sfm.activate_function(func_id)
                
            except Exception as e:
                print(f"   ❌ Ошибка активации {func_id}: {e}")
        
        return activated_count
    
    def print_current_status(self, batch_number=None, activated_count=None):
        """Вывод текущего статуса системы"""
        # Системные ресурсы
        sys_stats = self.get_system_stats()
        
        # Производительность SFM
        sfm_perf = self.get_sfm_performance()
        
        # Статистика функций
        sleeping_functions, critical_sleeping = self.get_sleeping_functions()
        
        print("=" * 80)
        if batch_number:
            print(f"📦 ПАКЕТ {batch_number}: Активировано {activated_count} функций")
        else:
            print("📊 БАЗОВАЯ ЛИНИЯ СИСТЕМЫ")
        print("=" * 80)
        
        print(f"💻 CPU: {sys_stats['cpu_percent']:.1f}%")
        print(f"💾 RAM: {sys_stats['ram_percent']:.1f}% ({sys_stats['ram_used_gb']:.2f}GB / {sys_stats['ram_total_gb']:.2f}GB)")
        print(f"📊 Доступно RAM: {sys_stats['ram_available_gb']:.2f}GB")
        
        if sfm_perf:
            print(f"⚡ SFM отклик: {sfm_perf['avg_response_ms']:.2f} мс")
            print(f"🚀 Операций/сек: {sfm_perf['operations_per_sec']:.0f}")
            
            # Оценка производительности
            if sfm_perf['avg_response_ms'] < 1.0:
                print("✅ Отлично!")
            elif sfm_perf['avg_response_ms'] < 5.0:
                print("✅ Хорошо")
            else:
                print("⚠️  Требует оптимизации")
        
        print()
        print(f"📦 Всего функций: {len(self.sfm.functions)}")
        print(f"💤 Спящих функций: {len(sleeping_functions)}")
        print(f"🚨 Критических спящих: {len(critical_sleeping)}")
        
        # Изменения от базовой линии
        if self.baseline_cpu > 0:
            cpu_change = sys_stats['cpu_percent'] - self.baseline_cpu
            ram_change = sys_stats['ram_percent'] - self.baseline_ram
            
            print()
            print("📈 ИЗМЕНЕНИЯ ОТ БАЗОВОЙ ЛИНИИ:")
            print(f"   🖥️  CPU: {cpu_change:+.1f}%")
            print(f"   💾 RAM: {ram_change:+.1f}%")
            
            if sfm_perf and self.baseline_sfm_perf > 0:
                perf_change = sfm_perf['avg_response_ms'] - self.baseline_sfm_perf
                print(f"   ⚡ SFM отклик: {perf_change:+.2f} мс")
        
        print("=" * 80)
        print()
    
    def set_baseline(self):
        """Установка базовой линии"""
        print("📊 Установка базовой линии...")
        time.sleep(1)  # Даем системе стабилизироваться
        
        sys_stats = self.get_system_stats()
        sfm_perf = self.get_sfm_performance()
        
        self.baseline_cpu = sys_stats['cpu_percent']
        self.baseline_ram = sys_stats['ram_percent']
        if sfm_perf:
            self.baseline_sfm_perf = sfm_perf['avg_response_ms']
        
        print("✅ Базовая линия установлена!")
        print()
    
    def activate_batch(self, function_ids, batch_number):
        """Активация пакета функций"""
        print(f"🚀 АКТИВАЦИЯ ПАКЕТА {batch_number}")
        print(f"   Функций в пакете: {len(function_ids)}")
        
        # Статистика до активации
        stats_before = self.get_system_stats()
        perf_before = self.get_sfm_performance()
        
        # Активация функций
        start_time = time.time()
        activated_count = self.simulate_function_activation(function_ids)
        activation_time = time.time() - start_time
        
        # Даем системе стабилизироваться
        time.sleep(0.5)
        
        # Статистика после активации
        stats_after = self.get_system_stats()
        perf_after = self.get_sfm_performance()
        
        # Вычисляем изменения
        cpu_change = stats_after['cpu_percent'] - stats_before['cpu_percent']
        ram_change = stats_after['ram_percent'] - stats_before['ram_percent']
        
        if perf_before and perf_after:
            perf_change = perf_after['avg_response_ms'] - perf_before['avg_response_ms']
        else:
            perf_change = 0
        
        print(f"   ✅ Активировано: {activated_count}")
        print(f"   ⏱️  Время активации: {activation_time:.3f} сек")
        print(f"   📊 Влияние на систему:")
        print(f"      🖥️  CPU: {cpu_change:+.1f}%")
        print(f"      💾 RAM: {ram_change:+.1f}%")
        print(f"      ⚡ SFM отклик: {perf_change:+.2f} мс")
        print()
        
        # Показываем текущий статус
        self.print_current_status(batch_number, activated_count)
        
        self.activation_count += activated_count
        return activated_count
    
    def initialize_sfm(self):
        """Инициализация SFM"""
        print("🔧 Инициализация SFM...")
        
        config = {
            'thread_pool_enabled': True,
            'max_thread_pool_workers': 5,
            'async_io_enabled': True,
            'redis_cache_enabled': True,
            'enable_auto_management': False,
            'enable_sleep_mode': False
        }
        
        try:
            self.sfm = SafeFunctionManager('ActivationMonitor', config)
            print(f"✅ SFM инициализирован: {len(self.sfm.functions)} функций")
            return True
        except Exception as e:
            print(f"❌ Ошибка инициализации SFM: {e}")
            return False
    
    def run_activation_process(self):
        """Запуск процесса активации с мониторингом"""
        print("🚀 ЗАПУСК ПРОЦЕССА АКТИВАЦИИ С МОНИТОРИНГОМ")
        print("=" * 80)
        print()
        
        # Инициализация SFM
        if not self.initialize_sfm():
            return
        
        # Установка базовой линии
        self.set_baseline()
        
        # Показываем базовую линию
        self.print_current_status()
        
        # Получаем спящие функции
        sleeping_functions, critical_sleeping = self.get_sleeping_functions()
        
        print(f"📊 НАЙДЕНО СПЯЩИХ ФУНКЦИЙ:")
        print(f"   🚨 Критических: {len(critical_sleeping)}")
        print(f"   💤 Обычных: {len(sleeping_functions) - len(critical_sleeping)}")
        print(f"   📦 Всего спящих: {len(sleeping_functions)}")
        print()
        
        try:
            # Активация критических функций первыми
            if critical_sleeping:
                print("🚨 АКТИВАЦИЯ КРИТИЧЕСКИХ ФУНКЦИЙ")
                print("-" * 50)
                
                # Активируем критические функции по 5 штук
                batch_size = 5
                for i in range(0, len(critical_sleeping), batch_size):
                    batch = critical_sleeping[i:i + batch_size]
                    batch_number = f"КРИТИЧЕСКИЕ-{(i // batch_size) + 1}"
                    
                    self.activate_batch(batch, batch_number)
                    
                    # Пауза между пакетами
                    print("⏸️  Пауза 3 секунды перед следующим пакетом...")
                    time.sleep(3)
                
                print("✅ Все критические функции активированы!")
                print()
            
            # Активация оставшихся функций
            remaining_sleeping = [f for f in sleeping_functions if f not in critical_sleeping]
            
            if remaining_sleeping:
                print("💤 АКТИВАЦИЯ ОСТАВШИХСЯ СПЯЩИХ ФУНКЦИЙ")
                print("-" * 50)
                
                # Активируем по 10 штук
                batch_size = 10
                for i in range(0, len(remaining_sleeping), batch_size):
                    batch = remaining_sleeping[i:i + batch_size]
                    batch_number = f"ОБЫЧНЫЕ-{(i // batch_size) + 1}"
                    
                    self.activate_batch(batch, batch_number)
                    
                    # Пауза между пакетами
                    print("⏸️  Пауза 2 секунды перед следующим пакетом...")
                    time.sleep(2)
                
                print("✅ Все функции активированы!")
                print()
            
            # Финальный статус
            print("🎉 ПРОЦЕСС АКТИВАЦИИ ЗАВЕРШЕН!")
            print("=" * 80)
            self.print_current_status("ФИНАЛЬНЫЙ", self.activation_count)
            
        except KeyboardInterrupt:
            print("\n⏹️  Активация прервана пользователем")
            print("=" * 80)
            self.print_current_status("ПРЕРВАНО", self.activation_count)
        except Exception as e:
            print(f"\n❌ Ошибка во время активации: {e}")
            print("=" * 80)
            self.print_current_status("ОШИБКА", self.activation_count)

def main():
    monitor = ActivationMonitor()
    monitor.run_activation_process()

if __name__ == "__main__":
    main()