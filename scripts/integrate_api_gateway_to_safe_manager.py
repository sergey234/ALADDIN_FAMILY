#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграция APIGateway в SafeFunctionManager
"""

import sys
import os
import json
import time
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def integrate_to_safe_manager():
    """Интеграция APIGateway в SafeFunctionManager"""
    print("🔗 ИНТЕГРАЦИЯ APIGATEWAY В SAFEFUNCTIONMANAGER")
    print("=" * 60)
    
    try:
        # Импорт SafeFunctionManager
        from security.safe_function_manager import SafeFunctionManager
        
        # Создание экземпляра SafeFunctionManager
        safe_manager = SafeFunctionManager()
        print("✅ SafeFunctionManager: инициализирован")
        
        # Регистрация APIGateway в SafeFunctionManager
        function_config = {
            'function_id': 'function_81',
            'function_name': 'APIGateway',
            'description': 'API шлюз системы безопасности с ML аналитикой',
            'module_path': 'security.microservices.api_gateway',
            'class_name': 'APIGateway',
            'quality_score': 80.3,
            'quality_grade': 'A',
            'status': 'sleeping',
            'priority': 'HIGH',
            'security_level': 'HIGH',
            'performance_impact': 'LOW',
            'resource_usage': 'MEDIUM',
            'wake_up_time': '< 1 секунда',
            'dependencies': [
                'fastapi',
                'uvicorn',
                'PyJWT',
                'redis',
                'sqlalchemy',
                'scikit-learn',
                'numpy',
                'prometheus-client'
            ],
            'features': [
                'JWT аутентификация',
                'API ключи с хешированием',
                'Rate limiting',
                'ML детекция аномалий',
                'Проксирование запросов',
                'Prometheus метрики',
                'CORS защита',
                'Health checks',
                'Circuit breaker',
                'Автоматическое масштабирование'
            ],
            'ml_capabilities': [
                'Isolation Forest для детекции аномалий',
                'Random Forest для классификации запросов',
                'K-Means для кластеризации трафика',
                'PCA для снижения размерности',
                'StandardScaler для нормализации данных'
            ],
            'security_features': [
                'JWT токен аутентификация',
                'API ключи с SHA-256 хешированием',
                'Rate limiting (100 запросов/минуту)',
                'Blacklist/Whitelist IP адресов',
                'CORS защита',
                'Валидация размера запросов',
                'ML детекция подозрительных запросов',
                'Prometheus мониторинг безопасности'
            ],
            'performance_metrics': {
                'lines_of_code': 1693,
                'classes': 17,
                'functions': 27,
                'methods': 24,
                'imports': 44,
                'documentation_percentage': 80.0,
                'type_hints_percentage': 96.3,
                'complexity_score': 37.8,
                'structure_score': 100.0
            },
            'integration_status': 'READY',
            'last_updated': datetime.now().isoformat(),
            'sleep_reason': 'Оптимизация ресурсов - функция готова к использованию'
        }
        
        # Импорт SecurityLevel
        from security.safe_function_manager import SecurityLevel
        
        # Регистрация функции
        success = safe_manager.register_function(
            function_id=function_config['function_id'],
            name=function_config['function_name'],
            description=function_config['description'],
            function_type='api_gateway',
            security_level=SecurityLevel.HIGH,
            is_critical=True,
            auto_enable=False
        )
        
        if success:
            print("✅ APIGateway: зарегистрирован в SafeFunctionManager")
        else:
            print("❌ Ошибка регистрации APIGateway")
            return False
        
        # Проверка регистрации
        all_functions = safe_manager.get_all_functions_status()
        api_gateway_found = any(
            func['function_id'] == 'function_81' 
            for func in all_functions
        )
        
        if api_gateway_found:
            print("✅ APIGateway: подтверждена регистрация")
        else:
            print("❌ APIGateway: не найден в зарегистрированных функциях")
            return False
        
        # Получение статуса функции
        function_status = safe_manager.get_function_status('function_81')
        if function_status:
            print(f"✅ Статус функции: {function_status.get('status', 'unknown')}")
            print(f"✅ Качество: {function_status.get('quality_grade', 'unknown')} ({function_status.get('quality_score', 0)}%)")
            print(f"✅ Приоритет: {function_status.get('priority', 'unknown')}")
            print(f"✅ Уровень безопасности: {function_status.get('security_level', 'unknown')}")
        
        # Создание отчета интеграции
        os.makedirs('data/integration_reports', exist_ok=True)
        report_file = f'data/integration_reports/api_gateway_safe_manager_integration_{int(time.time())}.json'
        
        integration_report = {
            'integration_timestamp': datetime.now().isoformat(),
            'function_id': 'function_81',
            'function_name': 'APIGateway',
            'integration_status': 'SUCCESS',
            'safe_manager_status': 'ACTIVE',
            'function_config': function_config,
            'registered_functions_count': len(all_functions),
            'integration_verification': {
                'registration_successful': success,
                'function_found_in_registry': api_gateway_found,
                'status_retrieval_successful': function_status is not None
            },
            'next_steps': [
                '1. APIGateway готов к пробуждению по требованию',
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
        
        print("\n🎯 APIGATEWAY УСПЕШНО ИНТЕГРИРОВАН В SAFEFUNCTIONMANAGER!")
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
        print("💤 APIGateway готов к управлению через SafeFunctionManager")
    else:
        print("\n💥 ОШИБКА ИНТЕГРАЦИИ!")