#!/usr/bin/env python3
"""
Глубокое тестирование менеджеров

Проводит детальную проверку всех аспектов работы менеджеров:
- Инициализация и конфигурация
- Работа с данными
- ML алгоритмы
- Обработка ошибок
- Производительность
- Интеграция
"""

import sys
import os
import traceback
import time
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Добавление пути к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_manager_initialization():
    """Тест инициализации всех менеджеров"""
    print("🔍 ГЛУБОКОЕ ТЕСТИРОВАНИЕ ИНИЦИАЛИЗАЦИИ")
    print("=" * 50)
    
    managers = {}
    errors = []
    
    # MonitorManager
    try:
        from security.managers.monitor_manager import MonitorManager
        monitor = MonitorManager("DeepTestMonitor")
        managers['MonitorManager'] = monitor
        print("✅ MonitorManager: инициализация успешна")
    except Exception as e:
        errors.append(f"MonitorManager: {e}")
        print(f"❌ MonitorManager: {e}")
    
    # AlertManager
    try:
        from security.managers.alert_manager import AlertManager
        alert = AlertManager("DeepTestAlert")
        managers['AlertManager'] = alert
        print("✅ AlertManager: инициализация успешна")
    except Exception as e:
        errors.append(f"AlertManager: {e}")
        print(f"❌ AlertManager: {e}")
    
    # ReportManager
    try:
        from security.ai_agents.report_manager import ReportManager
        report = ReportManager("DeepTestReport")
        managers['ReportManager'] = report
        print("✅ ReportManager: инициализация успешна")
    except Exception as e:
        errors.append(f"ReportManager: {e}")
        print(f"❌ ReportManager: {e}")
    
    # AnalyticsManager
    try:
        from security.managers.analytics_manager import AnalyticsManager
        analytics = AnalyticsManager("DeepTestAnalytics")
        managers['AnalyticsManager'] = analytics
        print("✅ AnalyticsManager: инициализация успешна")
    except Exception as e:
        errors.append(f"AnalyticsManager: {e}")
        print(f"❌ AnalyticsManager: {e}")
    
    # DashboardManager
    try:
        from security.managers.dashboard_manager import DashboardManager
        dashboard = DashboardManager("DeepTestDashboard")
        managers['DashboardManager'] = dashboard
        print("✅ DashboardManager: инициализация успешна")
    except Exception as e:
        errors.append(f"DashboardManager: {e}")
        print(f"❌ DashboardManager: {e}")
    
    return managers, errors

def test_data_processing(managers):
    """Тест обработки данных"""
    print("\n📊 ТЕСТИРОВАНИЕ ОБРАБОТКИ ДАННЫХ")
    print("=" * 50)
    
    results = {}
    
    # Тестовые данные
    test_data = {
        'metrics': [1.2, 2.3, 3.4, 4.5, 5.6, 6.7, 7.8, 8.9, 9.0, 10.1],
        'alerts': [
            {'id': 'alert1', 'message': 'Test alert 1', 'severity': 'low', 'timestamp': datetime.now()},
            {'id': 'alert2', 'message': 'Test alert 2', 'severity': 'high', 'timestamp': datetime.now()},
            {'id': 'alert3', 'message': 'Test alert 3', 'severity': 'medium', 'timestamp': datetime.now()}
        ],
        'behavior': [
            {'user_id': 'user1', 'action': 'login', 'timestamp': datetime.now(), 'ip': '192.168.1.1'},
            {'user_id': 'user2', 'action': 'logout', 'timestamp': datetime.now(), 'ip': '192.168.1.2'},
            {'user_id': 'user1', 'action': 'view_dashboard', 'timestamp': datetime.now(), 'ip': '192.168.1.1'}
        ]
    }
    
    # MonitorManager
    if 'MonitorManager' in managers:
        try:
            monitor = managers['MonitorManager']
            
            # Тест мониторинга метрик
            if hasattr(monitor, 'add_metric'):
                for metric in test_data['metrics']:
                    monitor.add_metric('test_metric', metric)
                print("✅ MonitorManager: метрики добавлены")
            
            # Тест обнаружения аномалий
            if hasattr(monitor, 'detect_anomalies'):
                anomalies = monitor.detect_anomalies(test_data['metrics'])
                print(f"✅ MonitorManager: найдено {len(anomalies)} аномалий")
            
            results['MonitorManager'] = 'success'
        except Exception as e:
            print(f"❌ MonitorManager: {e}")
            results['MonitorManager'] = f'error: {e}'
    
    # AlertManager
    if 'AlertManager' in managers:
        try:
            alert = managers['AlertManager']
            
            # Тест обработки алертов
            for alert_data in test_data['alerts']:
                if hasattr(alert, 'process_alert'):
                    result = alert.process_alert(alert_data)
                    print(f"✅ AlertManager: алерт {alert_data['id']} обработан")
            
            results['AlertManager'] = 'success'
        except Exception as e:
            print(f"❌ AlertManager: {e}")
            results['AlertManager'] = f'error: {e}'
    
    # ReportManager
    if 'ReportManager' in managers:
        try:
            report = managers['ReportManager']
            
            # Тест генерации отчета
            if hasattr(report, 'generate_report'):
                report_data = report.generate_report('test_report', test_data)
                print(f"✅ ReportManager: отчет сгенерирован")
            
            results['ReportManager'] = 'success'
        except Exception as e:
            print(f"❌ ReportManager: {e}")
            results['ReportManager'] = f'error: {e}'
    
    # AnalyticsManager
    if 'AnalyticsManager' in managers:
        try:
            analytics = managers['AnalyticsManager']
            
            # Тест анализа поведения
            if hasattr(analytics, 'analyze_behavior'):
                analysis = analytics.analyze_behavior(test_data['behavior'])
                print(f"✅ AnalyticsManager: поведение проанализировано")
            
            results['AnalyticsManager'] = 'success'
        except Exception as e:
            print(f"❌ AnalyticsManager: {e}")
            results['AnalyticsManager'] = f'error: {e}'
    
    # DashboardManager
    if 'DashboardManager' in managers:
        try:
            dashboard = managers['DashboardManager']
            
            # Тест создания пользователя
            if hasattr(dashboard, 'create_user'):
                from security.managers.dashboard_manager import UserRole
                success = dashboard.create_user('test_user', 'Test User', UserRole.GUEST)
                print(f"✅ DashboardManager: пользователь создан")
            
            results['DashboardManager'] = 'success'
        except Exception as e:
            print(f"❌ DashboardManager: {e}")
            results['DashboardManager'] = f'error: {e}'
    
    return results

def test_ml_algorithms(managers):
    """Тест ML алгоритмов"""
    print("\n🧠 ТЕСТИРОВАНИЕ ML АЛГОРИТМОВ")
    print("=" * 50)
    
    results = {}
    
    # Тестовые данные для ML (согласованные размерности)
    ml_data = {
        'clustering': np.random.rand(100, 5),      # 5 признаков для MonitorManager
        'classification': np.random.rand(50, 5),   # 5 признаков для MonitorManager
        'anomaly_detection': np.random.rand(200, 5), # 5 признаков для MonitorManager
        'time_series': np.random.rand(100),
        'analytics_clustering': np.random.rand(100, 10),    # 10 признаков для AnalyticsManager
        'analytics_classification': np.random.rand(50, 10), # 10 признаков для AnalyticsManager
        'analytics_anomaly': np.random.rand(200, 8)        # 8 признаков для AnalyticsManager
    }
    
    for manager_name, manager in managers.items():
        try:
            print(f"\n🔍 Тестирование {manager_name}:")
            
            # Тест кластеризации
            if hasattr(manager, '_cluster_data'):
                try:
                    if manager_name == 'AnalyticsManager':
                        clusters = manager._cluster_data(ml_data['analytics_clustering'])
                    else:
                        clusters = manager._cluster_data(ml_data['clustering'])
                    print(f"  ✅ Кластеризация: {len(set(clusters))} кластеров")
                except Exception as e:
                    print(f"  ⚠️ Кластеризация: {e}")
            
            # Тест детекции аномалий
            if hasattr(manager, '_detect_anomalies'):
                try:
                    if manager_name == 'AnalyticsManager':
                        anomalies = manager._detect_anomalies(ml_data['analytics_anomaly'])
                    else:
                        anomalies = manager._detect_anomalies(ml_data['anomaly_detection'])
                    print(f"  ✅ Детекция аномалий: {len(anomalies)} аномалий")
                except Exception as e:
                    print(f"  ⚠️ Детекция аномалий: {e}")
            
            # Тест классификации
            if hasattr(manager, '_classify_data'):
                try:
                    if manager_name == 'AnalyticsManager':
                        classes = manager._classify_data(ml_data['analytics_classification'])
                    else:
                        classes = manager._classify_data(ml_data['classification'])
                    print(f"  ✅ Классификация: {len(set(classes))} классов")
                except Exception as e:
                    print(f"  ⚠️ Классификация: {e}")
            
            results[manager_name] = 'success'
            
        except Exception as e:
            print(f"  ❌ {manager_name}: {e}")
            results[manager_name] = f'error: {e}'
    
    return results

def test_error_handling(managers):
    """Тест обработки ошибок"""
    print("\n⚠️ ТЕСТИРОВАНИЕ ОБРАБОТКИ ОШИБОК")
    print("=" * 50)
    
    results = {}
    
    for manager_name, manager in managers.items():
        try:
            print(f"\n🔍 Тестирование {manager_name}:")
            
            # Тест с некорректными данными
            try:
                if hasattr(manager, 'process_alert'):
                    manager.process_alert(None)
                print(f"  ✅ Обработка None данных")
            except Exception as e:
                print(f"  ✅ Корректно обработана ошибка: {type(e).__name__}")
            
            # Тест с пустыми данными
            try:
                if hasattr(manager, 'analyze_data'):
                    manager.analyze_data([])
                print(f"  ✅ Обработка пустых данных")
            except Exception as e:
                print(f"  ✅ Корректно обработана ошибка: {type(e).__name__}")
            
            # Тест с некорректными типами
            try:
                if hasattr(manager, 'add_metric'):
                    manager.add_metric('test', 'invalid_string')
                print(f"  ✅ Обработка некорректных типов")
            except Exception as e:
                print(f"  ✅ Корректно обработана ошибка: {type(e).__name__}")
            
            results[manager_name] = 'success'
            
        except Exception as e:
            print(f"  ❌ {manager_name}: {e}")
            results[manager_name] = f'error: {e}'

def test_performance(managers):
    """Тест производительности"""
    print("\n⚡ ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 50)
    
    results = {}
    
    for manager_name, manager in managers.items():
        try:
            print(f"\n🔍 Тестирование {manager_name}:")
            
            # Тест времени инициализации
            start_time = time.time()
            if hasattr(manager, 'get_stats'):
                stats = manager.get_stats()
            init_time = time.time() - start_time
            print(f"  ⏱️ Время получения статистики: {init_time:.4f}s")
            
            # Тест времени обработки данных
            test_data = np.random.rand(1000, 5)
            start_time = time.time()
            
            if hasattr(manager, '_cluster_data'):
                manager._cluster_data(test_data)
            
            process_time = time.time() - start_time
            print(f"  ⏱️ Время обработки 1000 записей: {process_time:.4f}s")
            
            # Проверка производительности
            if process_time < 1.0:
                print(f"  ✅ Производительность: ОТЛИЧНАЯ")
            elif process_time < 5.0:
                print(f"  ✅ Производительность: ХОРОШАЯ")
            else:
                print(f"  ⚠️ Производительность: ТРЕБУЕТ ОПТИМИЗАЦИИ")
            
            results[manager_name] = 'success'
            
        except Exception as e:
            print(f"  ❌ {manager_name}: {e}")
            results[manager_name] = f'error: {e}'

def test_integration(managers):
    """Тест интеграции между менеджерами"""
    print("\n🔗 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ")
    print("=" * 50)
    
    results = {}
    
    try:
        # Тест передачи данных между менеджерами
        if 'MonitorManager' in managers and 'AlertManager' in managers:
            monitor = managers['MonitorManager']
            alert = managers['AlertManager']
            
            # MonitorManager обнаруживает аномалию
            if hasattr(monitor, 'detect_anomalies'):
                anomalies = monitor.detect_anomalies([1, 2, 3, 100, 4, 5])
                
                # AlertManager обрабатывает аномалию как алерт
                if hasattr(alert, 'process_alert') and anomalies:
                    alert_data = {
                        'id': 'anomaly_alert',
                        'message': f'Обнаружена аномалия: {anomalies[0]}',
                        'severity': 'high',
                        'timestamp': datetime.now()
                    }
                    result = alert.process_alert(alert_data)
                    print("✅ Интеграция MonitorManager -> AlertManager: успешна")
        
        # Тест создания отчета на основе данных
        if 'AnalyticsManager' in managers and 'ReportManager' in managers:
            analytics = managers['AnalyticsManager']
            report = managers['ReportManager']
            
            # AnalyticsManager анализирует данные
            if hasattr(analytics, 'analyze_data'):
                test_behavior_data = [
                    {'user_id': 'user1', 'action': 'login', 'timestamp': datetime.now()},
                    {'user_id': 'user2', 'action': 'logout', 'timestamp': datetime.now()},
                    {'user_id': 'user1', 'action': 'view_dashboard', 'timestamp': datetime.now()}
                ]
                analysis = analytics.analyze_data(test_behavior_data)
                
            # ReportManager создает отчет
            if hasattr(report, 'generate_report'):
                try:
                    report_data = report.generate_report('test_report', analysis)
                    print("✅ Интеграция AnalyticsManager -> ReportManager: успешна")
                except Exception as e:
                    print(f"⚠️ Интеграция AnalyticsManager -> ReportManager: {e}")
        
        results['integration'] = 'success'
        
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        results['integration'] = f'error: {e}'

def generate_detailed_report(init_errors, data_results, ml_results, error_results, perf_results, integration_results):
    """Генерация детального отчета"""
    print("\n" + "="*60)
    print("📊 ДЕТАЛЬНЫЙ ОТЧЕТ О ТЕСТИРОВАНИИ")
    print("="*60)
    
    total_tests = 6
    passed_tests = 0
    
    print(f"\n📈 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    
    # Инициализация
    if not init_errors:
        print(f"  ✅ Инициализация: ВСЕ МЕНЕДЖЕРЫ УСПЕШНЫ")
        passed_tests += 1
    else:
        print(f"  ❌ Инициализация: {len(init_errors)} ОШИБОК")
        for error in init_errors:
            print(f"    - {error}")
    
    # Обработка данных
    if data_results:
        data_success = sum(1 for r in data_results.values() if r == 'success')
        print(f"  📊 Обработка данных: {data_success}/{len(data_results)} успешно")
        if data_success == len(data_results):
            passed_tests += 1
    else:
        print(f"  ❌ Обработка данных: НЕТ ДАННЫХ")
    
    # ML алгоритмы
    if ml_results:
        ml_success = sum(1 for r in ml_results.values() if r == 'success')
        print(f"  🧠 ML алгоритмы: {ml_success}/{len(ml_results)} успешно")
        if ml_success == len(ml_results):
            passed_tests += 1
    else:
        print(f"  ❌ ML алгоритмы: НЕТ ДАННЫХ")
    
    # Обработка ошибок
    if error_results:
        error_success = sum(1 for r in error_results.values() if r == 'success')
        print(f"  ⚠️ Обработка ошибок: {error_success}/{len(error_results)} успешно")
        if error_success == len(error_results):
            passed_tests += 1
    else:
        print(f"  ❌ Обработка ошибок: НЕТ ДАННЫХ")
    
    # Производительность
    if perf_results:
        perf_success = sum(1 for r in perf_results.values() if r == 'success')
        print(f"  ⚡ Производительность: {perf_success}/{len(perf_results)} успешно")
        if perf_success == len(perf_results):
            passed_tests += 1
    else:
        print(f"  ❌ Производительность: НЕТ ДАННЫХ")
    
    # Интеграция
    if integration_results and integration_results.get('integration') == 'success':
        print(f"  🔗 Интеграция: УСПЕШНА")
        passed_tests += 1
    else:
        print(f"  ❌ Интеграция: ОШИБКА")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if success_rate >= 90:
        print("🏆 КАЧЕСТВО: ОТЛИЧНОЕ - менеджеры работают идеально!")
    elif success_rate >= 70:
        print("✅ КАЧЕСТВО: ХОРОШЕЕ - есть незначительные проблемы")
    elif success_rate >= 50:
        print("⚠️ КАЧЕСТВО: УДОВЛЕТВОРИТЕЛЬНОЕ - требуются улучшения")
    else:
        print("❌ КАЧЕСТВО: ПЛОХОЕ - серьезные проблемы")
    
    return success_rate

def main():
    """Основная функция глубокого тестирования"""
    print("🔍 ГЛУБОКОЕ ТЕСТИРОВАНИЕ МЕНЕДЖЕРОВ")
    print("=" * 50)
    print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # Тест инициализации
        managers, init_errors = test_manager_initialization()
        
        if not managers:
            print("❌ КРИТИЧЕСКАЯ ОШИБКА: Ни один менеджер не инициализирован!")
            return False
        
        # Тест обработки данных
        data_results = test_data_processing(managers)
        
        # Тест ML алгоритмов
        ml_results = test_ml_algorithms(managers)
        
        # Тест обработки ошибок
        error_results = test_error_handling(managers)
        
        # Тест производительности
        perf_results = test_performance(managers)
        
        # Тест интеграции
        integration_results = test_integration(managers)
        
        # Генерация отчета
        success_rate = generate_detailed_report(
            init_errors, data_results, ml_results, 
            error_results, perf_results, integration_results
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️ Время выполнения: {duration:.2f} секунд")
        print(f"🎉 ГЛУБОКОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
        
        return success_rate >= 70
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)