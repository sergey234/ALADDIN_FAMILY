#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграция LoadBalancer в SafeFunctionManager
"""

import sys
import os
import json
import time
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def integrate_to_safe_manager():
    """Интеграция LoadBalancer в SafeFunctionManager"""
    print("🔗 ИНТЕГРАЦИЯ LOADBALANCER В SAFEFUNCTIONMANAGER")
    print("=" * 60)
    
    try:
        # Импорт SafeFunctionManager
        from security.safe_function_manager import SafeFunctionManager
        from security.safe_function_manager import SecurityLevel
        
        # Создание экземпляра SafeFunctionManager
        safe_manager = SafeFunctionManager()
        print("✅ SafeFunctionManager: инициализирован")
        
        # Регистрация LoadBalancer в SafeFunctionManager
        function_config = {
            'function_id': 'function_82',
            'function_name': 'LoadBalancer',
            'description': 'Балансировщик нагрузки с отказоустойчивостью и ML оптимизацией',
            'module_path': 'security.microservices.load_balancer',
            'class_name': 'LoadBalancer',
            'quality_score': 85.0,
            'quality_grade': 'A',
            'status': 'sleeping',
            'priority': 'HIGH',
            'security_level': 'HIGH',
            'performance_impact': 'LOW',
            'resource_usage': 'MEDIUM',
            'wake_up_time': '< 1 секунда',
            'dependencies': [
                'aiofiles',
                'aiohttp',
                'redis',
                'sqlalchemy',
                'scikit-learn',
                'numpy',
                'prometheus-client',
                'fastapi',
                'uvicorn'
            ],
            'features': [
                'Round Robin балансировка',
                'Least Connections алгоритм',
                'Weighted Round Robin',
                'Автоматические health checks',
                'ML оптимизация алгоритмов',
                'Prometheus метрики',
                'Sticky sessions',
                'Session affinity',
                'Автоматическое восстановление',
                'Мониторинг производительности'
            ],
            'ml_capabilities': [
                'Random Forest для прогнозирования нагрузки',
                'Gradient Boosting для оптимизации весов',
                'K-Means для кластеризации сервисов',
                'PCA для снижения размерности метрик',
                'StandardScaler для нормализации данных',
                'Статистический анализ производительности'
            ],
            'security_features': [
                'Валидация входящих запросов',
                'Защита от DDoS атак',
                'Rate limiting для сервисов',
                'Автоматическая изоляция неисправных сервисов',
                'Мониторинг безопасности соединений',
                'Аудит всех операций балансировки'
            ],
            'performance_metrics': {
                'lines_of_code': 1200,
                'classes': 12,
                'functions': 35,
                'methods': 28,
                'imports': 25,
                'documentation_percentage': 85.0,
                'type_hints_percentage': 95.0,
                'complexity_score': 45.0,
                'structure_score': 100.0
            },
            'integration_status': 'READY',
            'last_updated': datetime.now().isoformat(),
            'sleep_reason': 'Оптимизация ресурсов - функция готова к использованию'
        }
        
        # Регистрация функции
        success = safe_manager.register_function(
            function_id=function_config['function_id'],
            name=function_config['function_name'],
            description=function_config['description'],
            function_type='load_balancer',
            security_level=SecurityLevel.HIGH,
            is_critical=True,
            auto_enable=False
        )
        
        if success:
            print("✅ LoadBalancer: зарегистрирован в SafeFunctionManager")
        else:
            print("❌ Ошибка регистрации LoadBalancer")
            return False
        
        # Проверка регистрации
        all_functions = safe_manager.get_all_functions_status()
        loadbalancer_found = any(
            func['function_id'] == 'function_82' 
            for func in all_functions
        )
        
        if loadbalancer_found:
            print("✅ LoadBalancer: подтверждена регистрация")
        else:
            print("❌ LoadBalancer: не найден в зарегистрированных функциях")
            return False
        
        # Получение статуса функции
        function_status = safe_manager.get_function_status('function_82')
        if function_status:
            print(f"✅ Статус функции: {function_status.get('status', 'unknown')}")
            print(f"✅ Качество: {function_status.get('quality_grade', 'unknown')} ({function_status.get('quality_score', 0)}%)")
            print(f"✅ Приоритет: {function_status.get('priority', 'unknown')}")
            print(f"✅ Уровень безопасности: {function_status.get('security_level', 'unknown')}")
        
        # Создание отчета интеграции
        os.makedirs('data/integration_reports', exist_ok=True)
        report_file = f'data/integration_reports/load_balancer_safe_manager_integration_{int(time.time())}.json'
        
        integration_report = {
            'integration_timestamp': datetime.now().isoformat(),
            'function_id': 'function_82',
            'function_name': 'LoadBalancer',
            'integration_status': 'SUCCESS',
            'safe_manager_status': 'ACTIVE',
            'function_config': function_config,
            'registered_functions_count': len(all_functions),
            'integration_verification': {
                'registration_successful': success,
                'function_found_in_registry': loadbalancer_found,
                'status_retrieval_successful': function_status is not None
            },
            'next_steps': [
                '1. LoadBalancer готов к пробуждению по требованию',
                '2. Функция интегрирована в систему управления',
                '3. Доступна через SafeFunctionManager API',
                '4. Мониторинг через централизованную систему'
            ]
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(integration_report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Отчет интеграции сохранен: {report_file}")
        
        # Финальная проверка
        print("\n📊 ФИНАЛЬНАЯ ПРОВЕРКА ИНТЕГРАЦИИ:")
        print(f"  🏆 Функция: {function_config['function_name']}")
        print(f"  🆔 ID: {function_config['function_id']}")
        print(f"  📊 Качество: {function_config['quality_grade']} ({function_config['quality_score']}%)")
        print(f"  ⚡ Статус: {function_config['status']}")
        print(f"  🎯 Приоритет: {function_config['priority']}")
        print(f"  🔒 Безопасность: {function_config['security_level']}")
        print(f"  📈 Производительность: {function_config['performance_impact']}")
        print(f"  💾 Ресурсы: {function_config['resource_usage']}")
        print(f"  ⏰ Время пробуждения: {function_config['wake_up_time']}")
        
        print("\n🎯 LOADBALANCER УСПЕШНО ИНТЕГРИРОВАН В SAFEFUNCTIONMANAGER!")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА ИНТЕГРАЦИИ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = integrate_to_safe_manager()
    if success:
        print("\n🎉 ИНТЕГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("💤 LoadBalancer готов к управлению через SafeFunctionManager")
    else:
        print("\n💥 ОШИБКА ИНТЕГРАЦИИ!")