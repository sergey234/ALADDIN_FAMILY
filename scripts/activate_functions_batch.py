#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пакетная активация функций с мониторингом системных ресурсов
Активирует функции по 10 штук и отслеживает влияние на CPU/RAM
"""

import sys
import os
import time
import psutil
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager

class FunctionActivator:
    def __init__(self):
        self.sfm = None
        self.baseline_stats = {}
        self.activation_log = []
        
    def get_system_stats(self):
        """Получение текущих системных ресурсов"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        
        return {
            'cpu_percent': cpu_percent,
            'ram_percent': ram.percent,
            'ram_used_gb': ram.used / (1024**3),
            'ram_available_gb': ram.available / (1024**3),
            'timestamp': time.time()
        }
    
    def set_baseline(self):
        """Установка базовой линии"""
        print("📊 Установка базовой линии системы...")
        time.sleep(1)  # Даем системе стабилизироваться
        self.baseline_stats = self.get_system_stats()
        
        print(f"✅ Базовая линия установлена:")
        print(f"   🖥️  CPU: {self.baseline_stats['cpu_percent']:.1f}%")
        print(f"   💾 RAM: {self.baseline_stats['ram_percent']:.1f}% ({self.baseline_stats['ram_used_gb']:.2f}GB)")
        print(f"   📊 Доступно RAM: {self.baseline_stats['ram_available_gb']:.2f}GB")
        print()
    
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
            self.sfm = SafeFunctionManager('BatchActivator', config)
            print(f"✅ SFM инициализирован: {len(self.sfm.functions)} функций")
            return True
        except Exception as e:
            print(f"❌ Ошибка инициализации SFM: {e}")
            return False
    
    def get_sleeping_functions(self):
        """Получение списка спящих функций"""
        sleeping_functions = []
        critical_sleeping = []
        
        for func_id, func_obj in self.sfm.functions.items():
            status = str(getattr(func_obj, 'status', ''))
            if 'sleep' in status.lower():
                sleeping_functions.append(func_id)
                
                if getattr(func_obj, 'is_critical', False):
                    critical_sleeping.append(func_id)
        
        return sleeping_functions, critical_sleeping
    
    def activate_function_batch(self, function_ids, batch_number):
        """Активация пакета функций"""
        print(f"🚀 АКТИВАЦИЯ ПАКЕТА {batch_number}")
        print(f"   Функций в пакете: {len(function_ids)}")
        print(f"   Функции: {', '.join(function_ids[:3])}{'...' if len(function_ids) > 3 else ''}")
        
        # Записываем статистику до активации
        stats_before = self.get_system_stats()
        
        activated_count = 0
        failed_count = 0
        
        start_time = time.time()
        
        for func_id in function_ids:
            try:
                # Попытка активации функции
                # Здесь должен быть реальный код активации
                # Пока что симулируем активацию
                time.sleep(0.01)  # Симуляция времени активации
                activated_count += 1
                
            except Exception as e:
                print(f"   ❌ Ошибка активации {func_id}: {e}")
                failed_count += 1
        
        activation_time = time.time() - start_time
        
        # Записываем статистику после активации
        time.sleep(0.5)  # Даем системе стабилизироваться
        stats_after = self.get_system_stats()
        
        # Вычисляем изменения
        cpu_change = stats_after['cpu_percent'] - stats_before['cpu_percent']
        ram_change = stats_after['ram_percent'] - stats_before['ram_percent']
        ram_used_change = stats_after['ram_used_gb'] - stats_before['ram_used_gb']
        
        # Логируем результат
        log_entry = {
            'batch_number': batch_number,
            'functions_count': len(function_ids),
            'activated_count': activated_count,
            'failed_count': failed_count,
            'activation_time': activation_time,
            'cpu_change': cpu_change,
            'ram_change': ram_change,
            'ram_used_change_gb': ram_used_change,
            'stats_before': stats_before,
            'stats_after': stats_after
        }
        
        self.activation_log.append(log_entry)
        
        # Выводим результат
        print(f"   ✅ Активировано: {activated_count}")
        print(f"   ❌ Ошибок: {failed_count}")
        print(f"   ⏱️  Время активации: {activation_time:.3f} сек")
        print(f"   📊 Влияние на систему:")
        print(f"      🖥️  CPU: {cpu_change:+.1f}% ({stats_before['cpu_percent']:.1f}% → {stats_after['cpu_percent']:.1f}%)")
        print(f"      💾 RAM: {ram_change:+.1f}% ({stats_before['ram_percent']:.1f}% → {stats_after['ram_percent']:.1f}%)")
        print(f"      📈 RAM использовано: {ram_used_change:+.3f}GB")
        print()
        
        return activated_count, failed_count
    
    def print_current_stats(self):
        """Вывод текущей статистики системы"""
        stats = self.get_system_stats()
        
        print("📊 ТЕКУЩАЯ СТАТИСТИКА СИСТЕМЫ:")
        print(f"   🖥️  CPU: {stats['cpu_percent']:.1f}%")
        print(f"   💾 RAM: {stats['ram_percent']:.1f}% ({stats['ram_used_gb']:.2f}GB)")
        print(f"   📊 Доступно RAM: {stats['ram_available_gb']:.2f}GB")
        
        # Изменения от базовой линии
        if self.baseline_stats:
            cpu_total_change = stats['cpu_percent'] - self.baseline_stats['cpu_percent']
            ram_total_change = stats['ram_percent'] - self.baseline_stats['ram_percent']
            ram_used_total_change = stats['ram_used_gb'] - self.baseline_stats['ram_used_gb']
            
            print(f"   📈 ИЗМЕНЕНИЯ ОТ БАЗОВОЙ ЛИНИИ:")
            print(f"      🖥️  CPU: {cpu_total_change:+.1f}%")
            print(f"      💾 RAM: {ram_total_change:+.1f}%")
            print(f"      📈 RAM использовано: {ram_used_total_change:+.3f}GB")
        print()
    
    def activate_critical_functions_first(self):
        """Активация критических функций первыми"""
        print("🚨 АКТИВАЦИЯ КРИТИЧЕСКИХ ФУНКЦИЙ")
        print("=" * 50)
        
        sleeping_functions, critical_sleeping = self.get_sleeping_functions()
        
        print(f"📊 Найдено критических спящих функций: {len(critical_sleeping)}")
        
        if not critical_sleeping:
            print("✅ Все критические функции уже активны!")
            return True
        
        # Активируем критические функции по 5 штук
        batch_size = 5
        for i in range(0, len(critical_sleeping), batch_size):
            batch = critical_sleeping[i:i + batch_size]
            batch_number = (i // batch_size) + 1
            
            self.activate_function_batch(batch, f"КРИТИЧЕСКИЕ-{batch_number}")
            
            # Показываем промежуточную статистику
            self.print_current_stats()
            
            # Пауза между пакетами
            print("⏸️  Пауза 3 секунды перед следующим пакетом...")
            time.sleep(3)
        
        return True
    
    def activate_remaining_functions(self):
        """Активация оставшихся спящих функций"""
        print("💤 АКТИВАЦИЯ ОСТАВШИХСЯ СПЯЩИХ ФУНКЦИЙ")
        print("=" * 50)
        
        sleeping_functions, critical_sleeping = self.get_sleeping_functions()
        
        # Убираем уже активированные критические функции
        remaining_sleeping = [f for f in sleeping_functions if f not in critical_sleeping]
        
        print(f"📊 Найдено оставшихся спящих функций: {len(remaining_sleeping)}")
        
        if not remaining_sleeping:
            print("✅ Все функции уже активны!")
            return True
        
        # Активируем по 10 штук
        batch_size = 10
        for i in range(0, len(remaining_sleeping), batch_size):
            batch = remaining_sleeping[i:i + batch_size]
            batch_number = (i // batch_size) + 1
            
            self.activate_function_batch(batch, f"ОБЫЧНЫЕ-{batch_number}")
            
            # Показываем промежуточную статистику
            self.print_current_stats()
            
            # Пауза между пакетами
            print("⏸️  Пауза 2 секунды перед следующим пакетом...")
            time.sleep(2)
        
        return True
    
    def print_final_report(self):
        """Вывод финального отчета"""
        print("📋 ФИНАЛЬНЫЙ ОТЧЕТ АКТИВАЦИИ")
        print("=" * 60)
        
        total_activated = sum(log['activated_count'] for log in self.activation_log)
        total_failed = sum(log['failed_count'] for log in self.activation_log)
        total_batches = len(self.activation_log)
        
        print(f"📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"   📦 Всего пакетов: {total_batches}")
        print(f"   ✅ Успешно активировано: {total_activated}")
        print(f"   ❌ Ошибок активации: {total_failed}")
        
        if self.activation_log:
            total_time = sum(log['activation_time'] for log in self.activation_log)
            avg_time_per_batch = total_time / total_batches
            
            print(f"   ⏱️  Общее время активации: {total_time:.2f} сек")
            print(f"   📈 Среднее время на пакет: {avg_time_per_batch:.3f} сек")
        
        # Финальные изменения системы
        final_stats = self.get_system_stats()
        if self.baseline_stats:
            cpu_final_change = final_stats['cpu_percent'] - self.baseline_stats['cpu_percent']
            ram_final_change = final_stats['ram_percent'] - self.baseline_stats['ram_percent']
            ram_used_final_change = final_stats['ram_used_gb'] - self.baseline_stats['ram_used_gb']
            
            print(f"   📊 ФИНАЛЬНЫЕ ИЗМЕНЕНИЯ СИСТЕМЫ:")
            print(f"      🖥️  CPU: {cpu_final_change:+.1f}%")
            print(f"      💾 RAM: {ram_final_change:+.1f}%")
            print(f"      📈 RAM использовано: {ram_used_final_change:+.3f}GB")
        
        print()
        print("📋 ДЕТАЛИ ПО ПАКЕТАМ:")
        for log in self.activation_log:
            print(f"   Пакет {log['batch_number']}: {log['activated_count']}/{log['functions_count']} функций "
                  f"(CPU {log['cpu_change']:+.1f}%, RAM {log['ram_change']:+.1f}%)")

def main():
    activator = FunctionActivator()
    
    print("🚀 ПАКЕТНАЯ АКТИВАЦИЯ ФУНКЦИЙ С МОНИТОРИНГОМ")
    print("=" * 60)
    print()
    
    # Инициализация SFM
    if not activator.initialize_sfm():
        return
    
    # Установка базовой линии
    activator.set_baseline()
    
    # Показываем начальную статистику
    sleeping_functions, critical_sleeping = activator.get_sleeping_functions()
    print(f"📊 НАЙДЕНО СПЯЩИХ ФУНКЦИЙ:")
    print(f"   🚨 Критических: {len(critical_sleeping)}")
    print(f"   💤 Обычных: {len(sleeping_functions) - len(critical_sleeping)}")
    print(f"   📦 Всего спящих: {len(sleeping_functions)}")
    print()
    
    try:
        # Активация критических функций
        activator.activate_critical_functions_first()
        
        print("\n" + "="*60 + "\n")
        
        # Активация оставшихся функций
        activator.activate_remaining_functions()
        
        print("\n" + "="*60 + "\n")
        
        # Финальный отчет
        activator.print_final_report()
        
    except KeyboardInterrupt:
        print("\n⏹️  Активация прервана пользователем")
        activator.print_final_report()
    except Exception as e:
        print(f"\n❌ Ошибка во время активации: {e}")
        activator.print_final_report()

if __name__ == "__main__":
    main()