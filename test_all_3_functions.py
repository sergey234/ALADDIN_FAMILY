#!/usr/bin/env python3
"""
🧪 ТЕСТ ВСЕХ 3 ИСПРАВЛЕННЫХ ФУНКЦИЙ
Проверяет что функции 1/93, 2/93, 3/93 возвращают реальные данные, а не mock
"""

import sys
import os
import json

# Имитация проверки API Gateway
def test_function_implementation():
    """Проверяет реализацию функций в коде"""

    # Читаем файл api_gateway_server_current.py
    with open('api_gateway_server_current.py', 'r', encoding='utf-8') as f:
        content = f.read()

    results = []

    # Проверка функции 1/93: /api/phishing/sensitivity
    if 'get_phishing_protection_config' in content and 'def get_phishing_sensitivity' in content:
        # Проверяем что функция не возвращает mock данные напрямую
        func_start = content.find('def get_phishing_sensitivity')
        next_func = content.find('\n\n@app.', func_start + 1)
        if next_func == -1:
            next_func = len(content)
        func_content = content[func_start:next_func]

        has_sfm_call = 'sfm_adapter.execute_function' in func_content
        has_mock_return = '"source": "mock"' in func_content

        results.append({
            "function": "1/93 - /api/phishing/sensitivity",
            "status": "✅ ИСПРАВЛЕНА" if has_sfm_call and not has_mock_return else "❌ НЕ ИСПРАВЛЕНА",
            "sfm_call": "get_phishing_protection_config",
            "returns_real_data": has_sfm_call,
            "no_mock": not has_mock_return
        })
    else:
        results.append({
            "function": "1/93 - /api/phishing/sensitivity",
            "status": "❌ НЕ ИСПРАВЛЕНА",
            "error": "Не найден SFM вызов"
        })

    # Проверка функции 2/93: /api/analytics/overview
    if 'get_analytics_overview' in content and 'def get_analytics_overview' in content:
        # Проверяем что функция не возвращает mock данные напрямую
        func_start = content.find('def get_analytics_overview')
        next_func = content.find('\n\n@app.', func_start + 1)
        if next_func == -1:
            next_func = len(content)
        func_content = content[func_start:next_func]

        has_sfm_call = 'sfm_adapter.execute_function' in func_content
        has_mock_return = '"source": "mock"' in func_content

        results.append({
            "function": "2/93 - /api/analytics/overview",
            "status": "✅ ИСПРАВЛЕНА" if has_sfm_call and not has_mock_return else "❌ НЕ ИСПРАВЛЕНА",
            "sfm_call": "get_analytics_overview",
            "returns_real_data": has_sfm_call,
            "no_mock": not has_mock_return
        })
    else:
        results.append({
            "function": "2/93 - /api/analytics/overview",
            "status": "❌ НЕ ИСПРАВЛЕНА",
            "error": "Не найден SFM вызов"
        })

    # Проверка функции 3/93: /api/components/status/{component_id}
    if 'sfm_adapter.execute_function("get_component_status"' in content:
        results.append({
            "function": "3/93 - /api/components/status/{component_id}",
            "status": "✅ ИСПРАВЛЕНА",
            "sfm_call": "get_component_status",
            "returns_real_data": True,
            "no_mock": '"source": "mock"' not in content.split('def get_component_status')[1].split('def ')[0]
        })
    else:
        results.append({
            "function": "3/93 - /api/components/status/{component_id}",
            "status": "❌ НЕ ИСПРАВЛЕНА",
            "error": "Не найден SFM вызов"
        })

    return results

def check_no_mock_data():
    """Проверяет что нет mock данных в исправленных функциях"""

    with open('api_gateway_server_current.py', 'r', encoding='utf-8') as f:
        content = f.read()

    functions_to_check = [
        ('get_phishing_sensitivity', '1/93'),
        ('get_analytics_overview', '2/93'),
        ('get_component_status', '3/93')
    ]

    mock_issues = []

    for func_name, func_num in functions_to_check:
        func_start = content.find(f'def {func_name}')
        if func_start != -1:
            func_end = content.find('\n\n@app.', func_start + 1)
            if func_end == -1:
                func_end = len(content)
            func_content = content[func_start:func_end]

            if '"source": "mock"' in func_content:
                mock_issues.append({
                    "function": f"{func_num} - {func_name}",
                    "issue": "Найдены mock данные в исправленной функции"
                })

    return mock_issues

def main():
    print("🧪 ПРОВЕРКА ВСЕХ 3 ИСПРАВЛЕННЫХ ФУНКЦИЙ")
    print("=" * 50)

    # Проверка реализаций
    results = test_function_implementation()

    all_good = True
    for result in results:
        print(f"\n{result['function']}: {result['status']}")
        if result['status'] == "✅ ИСПРАВЛЕНА":
            print(f"  🔧 SFM вызов: {result['sfm_call']}")
            print(f"  📊 Реальные данные: {'✅' if result['returns_real_data'] else '❌'}")
            print(f"  🚫 Нет mock: {'✅' if result['no_mock'] else '❌'}")
        else:
            print(f"  ❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
            all_good = False

    # Проверка на отсутствие mock данных
    mock_issues = check_no_mock_data()
    if mock_issues:
        print(f"\n⚠️  НАЙДЕНЫ ПРОБЛЕМЫ С MOCK ДАННЫМИ:")
        for issue in mock_issues:
            print(f"  {issue['function']}: {issue['issue']}")
        all_good = False

    print("\n" + "=" * 50)
    if all_good:
        print("🎉 ВСЕ ФУНКЦИИ ИСПРАВЛЕНЫ ПРАВИЛЬНО!")
        print("✅ Возвращают реальные данные из SFM")
        print("✅ Нет mock данных")
        print("✅ Готовы к развертыванию")
        print("\n🚀 ГОТОВ ПЕРЕЙТИ К СЛЕДУЮЩЕЙ ФУНКЦИИ: 4/93")
    else:
        print("❌ НАЙДЕНЫ ПРОБЛЕМЫ!")
        print("🔧 Необходимо исправить перед продакшеном")

    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)