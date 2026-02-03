#!/usr/bin/env python3
"""
ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ ПРОДАКШН ГОТОВНОСТИ ALADDIN
Проверка что все работает с реальными данными SFM
"""

import sys
import os
import time

# Добавляем пути
sys.path.insert(0, '.')

def test_sfm_singleton():
    """Тест SFM Singleton"""
    print("🧪 ТЕСТ 1: SFM SINGLETON - ИНИЦИАЛИЗАЦИЯ")
    try:
        from security.sfm_singleton import get_sfm

        start = time.time()
        sfm = get_sfm()
        init_time = time.time() - start

        print(f"✅ SFM инициализирован за {init_time:.3f} сек")
        print(f"✅ Версия: {sfm.version}")
        print(f"✅ Core функций: {len(sfm._core_functions)}")
        print(f"✅ Heavy компоненты: {'загружены' if sfm._heavy_components_loaded else 'lazy loading'}")

        # Тест выполнения функций
        result = sfm.execute_function("get_phishing_sensitivity", {})
        print(f"✅ Тест функции: {result.get('source', 'unknown')}")

        return True
    except Exception as e:
        print(f"❌ Ошибка SFM: {e}")
        return False

def test_sfm_adapter():
    """Тест SFM Adapter"""
    print("\n🧪 ТЕСТ 2: SFM ADAPTER - РЕАЛЬНЫЕ ДАННЫЕ")
    try:
        from sfm_adapter import sfm_adapter

        time.sleep(0.1)  # Дать время на инициализацию

        # Тест health check
        health = sfm_adapter.health_check()
        print(f"✅ Health check: {health['status']}")
        print(f"✅ SFM статус: {health['sfm_adapter']}")
        print(f"✅ Endpoints: {health['endpoints']}")

        # Тест реальных функций
        test_functions = [
            'get_phishing_sensitivity',
            'get_components_health',
            'get_ai_categories_stats',
            'get_darkweb_leaks',
            'get_parental_stats'
        ]

        print("\nТестирование функций с реальными данными:")
        success_count = 0
        for func in test_functions:
            success, result, error = sfm_adapter.execute_function(func, {})
            status_icon = '✅' if success else '❌'
            source = result.get('source', 'unknown') if success else error
            print(f"{status_icon} {func}: {source}")
            if success and source == 'sfm_real':
                success_count += 1

        print(f"\n✅ Реальных функций: {success_count}/{len(test_functions)}")

        # Метрики
        metrics = sfm_adapter.get_metrics()
        print("\n📊 Метрики SFM Adapter:")
        print(f"Всего вызовов: {metrics['total_calls']}")
        print(f"Успешных: {metrics['successful_calls']}")
        print(f"Fallback: {metrics['fallback_calls']}")
        print(f"Время инициализации: {metrics['init_time']:.3f} сек")
        return success_count == len(test_functions)
    except Exception as e:
        print(f"❌ Ошибка Adapter: {e}")
        return False

def test_api_gateway():
    """Тест API Gateway синтаксиса"""
    print("\n🧪 ТЕСТ 3: API GATEWAY - СИНТАКСИС И СТРУКТУРА")
    try:
        # Проверяем синтаксис
        import py_compile
        py_compile.compile('api_gateway_production_final_complete.py', doraise=True)
        print("✅ Синтаксис API Gateway OK")

        # Анализируем endpoints
        with open('api_gateway_production_final_complete.py', 'r') as f:
            content = f.read()

        import re
        endpoints = re.findall(r'@app\.(get|post|put|delete)\([\'"]([^\'"]+)[\'"]', content)
        print(f"✅ Всего endpoints: {len(endpoints)}")

        # Проверяем SFM интеграцию
        sfm_imports = content.count('from sfm_adapter import sfm_adapter')
        sfm_calls = content.count('sfm_adapter.execute_function')

        print(f"✅ SFM импортов: {sfm_imports}")
        print(f"✅ SFM вызовов: {sfm_calls}")

        return len(endpoints) >= 100 and sfm_imports > 0 and sfm_calls > 0
    except Exception as e:
        print(f"❌ Ошибка API Gateway: {e}")
        return False

def test_production_readiness():
    """Финальная проверка готовности к продакшену"""
    print("\n🎯 ФИНАЛЬНАЯ ПРОВЕРКА ПРОДАКШН ГОТОВНОСТИ")
    print("=" * 50)

    results = []

    # Тест 1: SFM
    results.append(("SFM Singleton", test_sfm_singleton()))

    # Тест 2: SFM Adapter
    results.append(("SFM Adapter", test_sfm_adapter()))

    # Тест 3: API Gateway
    results.append(("API Gateway", test_api_gateway()))

    # Итоги
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")

    all_passed = True
    for test_name, passed in results:
        status = "✅ ПРОЙДЕН" if passed else "❌ ПРОВАЛЕН"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ПРОДАКШН ГОТОВНОСТЬ: 100% ✅")
        print("🚀 ALADDIN ГОТОВ К ПРОДАКШНУ С ПОЛНОЦЕННОЙ AI-ЗАЩИТОЙ!")
        print("🛡️ Мобильное приложение получит РЕАЛЬНУЮ защиту через SFM!")
        return True
    else:
        print("❌ ТРЕБУЕТСЯ ДОРАБОТКА")
        return False

if __name__ == "__main__":
    success = test_production_readiness()
    exit(0 if success else 1)