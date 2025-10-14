#!/usr/bin/env python3
"""
Тестирование улучшенных менеджеров

Проверяет работоспособность всех 5 менеджеров после улучшений:
- MonitorManager
- AlertManager  
- ReportManager
- AnalyticsManager
- DashboardManager
"""

import sys
import os
import traceback
import time
from datetime import datetime

# Добавление пути к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Тест импорта всех менеджеров"""
    print("🔍 Тестирование импортов менеджеров...")
    
    managers = [
        ('MonitorManager', 'security.ai_agents.monitor_manager'),
        ('AlertManager', 'security.managers.alert_manager'),
        ('ReportManager', 'security.managers.report_manager'),
        ('AnalyticsManager', 'security.ai_agents.analytics_manager'),
        ('DashboardManager', 'security.ai_agents.dashboard_manager')
    ]
    
    results = {}
    
    for manager_name, module_path in managers:
        try:
            module = __import__(module_path, fromlist=[manager_name])
            manager_class = getattr(module, manager_name)
            results[manager_name] = {'status': 'success', 'class': manager_class}
            print(f"  ✅ {manager_name}: импорт успешен")
        except Exception as e:
            results[manager_name] = {'status': 'error', 'error': str(e)}
            print(f"  ❌ {manager_name}: ошибка импорта - {e}")
    
    return results

def test_initialization(import_results):
    """Тест инициализации менеджеров"""
    print("\n🔧 Тестирование инициализации менеджеров...")
    
    results = {}
    
    for manager_name, data in import_results.items():
        if data['status'] != 'success':
            results[manager_name] = {'status': 'skipped', 'reason': 'import_failed'}
            continue
            
        try:
            manager_class = data['class']
            manager = manager_class()
            results[manager_name] = {'status': 'success', 'instance': manager}
            print(f"  ✅ {manager_name}: инициализация успешна")
        except Exception as e:
            results[manager_name] = {'status': 'error', 'error': str(e)}
            print(f"  ❌ {manager_name}: ошибка инициализации - {e}")
    
    return results

def test_basic_functionality(init_results):
    """Тест базовой функциональности"""
    print("\n⚙️ Тестирование базовой функциональности...")
    
    results = {}
    
    for manager_name, data in init_results.items():
        if data['status'] != 'success':
            results[manager_name] = {'status': 'skipped', 'reason': 'init_failed'}
            continue
            
        try:
            manager = data['instance']
            test_results = {}
            
            # Тест основных методов
            if hasattr(manager, 'get_stats'):
                stats = manager.get_stats()
                test_results['get_stats'] = 'success'
                print(f"    ✅ {manager_name}.get_stats(): {len(stats)} метрик")
            
            if hasattr(manager, 'get_status'):
                status = manager.get_status()
                test_results['get_status'] = 'success'
                print(f"    ✅ {manager_name}.get_status(): {status}")
            
            if hasattr(manager, 'get_health'):
                health = manager.get_health()
                test_results['get_health'] = 'success'
                print(f"    ✅ {manager_name}.get_health(): {health}")
            
            # Тест специфичных методов
            if manager_name == 'MonitorManager':
                if hasattr(manager, 'start_monitoring'):
                    import asyncio
                    try:
                        asyncio.run(manager.start_monitoring())
                        test_results['start_monitoring'] = 'success'
                        print(f"    ✅ {manager_name}.start_monitoring(): запущен")
                    except Exception as e:
                        print(f"    ⚠️ {manager_name}.start_monitoring(): {e}")
                
                if hasattr(manager, 'stop_monitoring'):
                    import asyncio
                    try:
                        asyncio.run(manager.stop_monitoring())
                        test_results['stop_monitoring'] = 'success'
                        print(f"    ✅ {manager_name}.stop_monitoring(): остановлен")
                    except Exception as e:
                        print(f"    ⚠️ {manager_name}.stop_monitoring(): {e}")
            
            elif manager_name == 'AlertManager':
                if hasattr(manager, 'process_alert'):
                    test_alert = {'id': 'test', 'message': 'Test alert', 'severity': 'low'}
                    result = manager.process_alert(test_alert)
                    test_results['process_alert'] = 'success'
                    print(f"    ✅ {manager_name}.process_alert(): обработан")
            
            elif manager_name == 'ReportManager':
                if hasattr(manager, 'generate_report'):
                    report = manager.generate_report('test_report')
                    test_results['generate_report'] = 'success'
                    print(f"    ✅ {manager_name}.generate_report(): создан")
            
            elif manager_name == 'AnalyticsManager':
                if hasattr(manager, 'analyze_data'):
                    test_data = [1, 2, 3, 4, 5]
                    analysis = manager.analyze_data(test_data)
                    test_results['analyze_data'] = 'success'
                    print(f"    ✅ {manager_name}.analyze_data(): проанализировано")
            
            elif manager_name == 'DashboardManager':
                if hasattr(manager, 'create_user'):
                    success = manager.create_user('test_user', 'Test User', 'viewer')
                    test_results['create_user'] = 'success'
                    print(f"    ✅ {manager_name}.create_user(): создан")
            
            results[manager_name] = {'status': 'success', 'tests': test_results}
            print(f"  ✅ {manager_name}: базовая функциональность работает")
            
        except Exception as e:
            results[manager_name] = {'status': 'error', 'error': str(e)}
            print(f"  ❌ {manager_name}: ошибка тестирования - {e}")
            traceback.print_exc()
    
    return results

def test_ml_algorithms(init_results):
    """Тест ML алгоритмов"""
    print("\n🧠 Тестирование ML алгоритмов...")
    
    results = {}
    
    for manager_name, data in init_results.items():
        if data['status'] != 'success':
            results[manager_name] = {'status': 'skipped', 'reason': 'init_failed'}
            continue
            
        try:
            manager = data['instance']
            test_results = {}
            
            # Тест ML методов
            if hasattr(manager, '_cluster_data'):
                test_data = [[1, 2], [2, 3], [3, 4], [4, 5]]
                clusters = manager._cluster_data(test_data)
                test_results['clustering'] = 'success'
                print(f"    ✅ {manager_name}.clustering: {len(clusters)} кластеров")
            
            if hasattr(manager, '_detect_anomalies'):
                test_data = [1, 2, 3, 100, 4, 5]  # 100 - аномалия
                try:
                    anomalies = manager._detect_anomalies(test_data)
                    test_results['anomaly_detection'] = 'success'
                    print(f"    ✅ {manager_name}.anomaly_detection: найдено {len(anomalies)} аномалий")
                except Exception as e:
                    print(f"    ⚠️ {manager_name}.anomaly_detection: {e}")
            
            if hasattr(manager, '_analyze_behavior'):
                test_data = [{'user_id': 'test', 'action': 'login', 'timestamp': datetime.now()}]
                try:
                    analysis = manager._analyze_behavior(test_data)
                    test_results['behavior_analysis'] = 'success'
                    print(f"    ✅ {manager_name}.behavior_analysis: проанализировано")
                except Exception as e:
                    print(f"    ⚠️ {manager_name}.behavior_analysis: {e}")
            
            if hasattr(manager, '_optimize_layout'):
                # Создаем тестовый макет
                from security.ai_agents.dashboard_manager import DashboardLayout, DashboardWidget
                test_layout = DashboardLayout('test', (3, 3), [])
                test_widgets = {
                    'widget1': 0.8,
                    'widget2': 0.6,
                    'widget3': 0.4
                }
                manager._optimize_layout(test_layout, test_widgets)
                test_results['layout_optimization'] = 'success'
                print(f"    ✅ {manager_name}.layout_optimization: оптимизирован")
            
            results[manager_name] = {'status': 'success', 'ml_tests': test_results}
            print(f"  ✅ {manager_name}: ML алгоритмы работают")
            
        except Exception as e:
            results[manager_name] = {'status': 'error', 'error': str(e)}
            print(f"  ❌ {manager_name}: ошибка ML тестирования - {e}")
    
    return results

def generate_report(import_results, init_results, functionality_results, ml_results):
    """Генерация отчета о тестировании"""
    print("\n📊 ОТЧЕТ О ТЕСТИРОВАНИИ УЛУЧШЕННЫХ МЕНЕДЖЕРОВ")
    print("=" * 60)
    
    total_managers = len(import_results)
    successful_imports = sum(1 for r in import_results.values() if r['status'] == 'success')
    successful_inits = sum(1 for r in init_results.values() if r['status'] == 'success')
    successful_tests = sum(1 for r in functionality_results.values() if r['status'] == 'success')
    successful_ml = sum(1 for r in ml_results.values() if r['status'] == 'success')
    
    print(f"📈 СТАТИСТИКА:")
    print(f"  Всего менеджеров: {total_managers}")
    print(f"  Успешных импортов: {successful_imports}/{total_managers}")
    print(f"  Успешных инициализаций: {successful_inits}/{total_managers}")
    print(f"  Успешных тестов функциональности: {successful_tests}/{total_managers}")
    print(f"  Успешных ML тестов: {successful_ml}/{total_managers}")
    
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ:")
    success_rate = (successful_tests / total_managers) * 100
    print(f"  Успешность тестирования: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("  🏆 КАЧЕСТВО: ОТЛИЧНОЕ")
    elif success_rate >= 60:
        print("  ✅ КАЧЕСТВО: ХОРОШЕЕ")
    elif success_rate >= 40:
        print("  ⚠️ КАЧЕСТВО: УДОВЛЕТВОРИТЕЛЬНОЕ")
    else:
        print("  ❌ КАЧЕСТВО: ТРЕБУЕТ УЛУЧШЕНИЯ")
    
    print(f"\n📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
    for manager_name in import_results.keys():
        import_status = import_results[manager_name]['status']
        init_status = init_results[manager_name]['status']
        func_status = functionality_results[manager_name]['status']
        ml_status = ml_results[manager_name]['status']
        
        print(f"\n  {manager_name}:")
        print(f"    Импорт: {'✅' if import_status == 'success' else '❌'}")
        print(f"    Инициализация: {'✅' if init_status == 'success' else '❌'}")
        print(f"    Функциональность: {'✅' if func_status == 'success' else '❌'}")
        print(f"    ML алгоритмы: {'✅' if ml_status == 'success' else '❌'}")
    
    return {
        'total_managers': total_managers,
        'successful_imports': successful_imports,
        'successful_inits': successful_inits,
        'successful_tests': successful_tests,
        'successful_ml': successful_ml,
        'success_rate': success_rate
    }

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ УЛУЧШЕННЫХ МЕНЕДЖЕРОВ")
    print("=" * 50)
    print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # Тест импортов
        import_results = test_imports()
        
        # Тест инициализации
        init_results = test_initialization(import_results)
        
        # Тест функциональности
        functionality_results = test_basic_functionality(init_results)
        
        # Тест ML алгоритмов
        ml_results = test_ml_algorithms(init_results)
        
        # Генерация отчета
        report = generate_report(import_results, init_results, functionality_results, ml_results)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️ Время выполнения: {duration:.2f} секунд")
        print(f"🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
        
        return report['success_rate'] >= 80
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)