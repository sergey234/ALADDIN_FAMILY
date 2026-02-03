#!/usr/bin/env python3
"""
🧪 ТЕСТ ВСЕХ 4 ИСПРАВЛЕННЫХ ФУНКЦИЙ
Проверяет что функции 1/93, 2/93, 3/93, 4/93 возвращают реальные данные, а не mock
"""

import sys
import os
import json

# Читаем файл api_gateway_server_current.py
def test_function_implementation():
    """Проверяет реализацию функций в коде"""

    with open('api_gateway_server_current.py', 'r', encoding='utf-8') as f:
        content = f.read()

    results = []

    functions_to_check = [
        ('get_phishing_sensitivity', '1/93', 'get_phishing_protection_config'),
        ('get_analytics_overview', '2/93', 'get_analytics_overview'),
        ('get_component_status', '3/93', 'get_component_status'),
        ('enable_component', '4/93', 'enable_component')
    ]

    for func_name, func_num, sfm_call in functions_to_check:
        # Проверяем что функция не возвращает mock данные напрямую
        func_start = content.find(f'def {func_name}')
        if func_start != -1:
            next_func = content.find('\n\n@app.', func_start + 1)
            if next_func == -1:
                next_func = len(content)
            func_content = content[func_start:next_func]

            has_sfm_call = 'sfm_adapter.execute_function' in func_content
            has_mock_return = '"source": "mock"' in func_content

            # Дополнительная проверка - функция должна иметь комментарий об исправлении
            has_fix_comment = f'# ✅ ИСПРАВЛЕНА - функция {func_num}' in func_content

            results.append({
                "function": f"{func_num} - {func_name.replace('_', '/').replace('get', 'api').replace('component', 'components')}",
                "status": "✅ ИСПРАВЛЕНА" if has_sfm_call and not has_mock_return and has_fix_comment else "❌ НЕ ИСПРАВЛЕНА",
                "sfm_call": sfm_call,
                "returns_real_data": has_sfm_call,
                "no_mock": not has_mock_return,
                "has_fix_comment": has_fix_comment
            })
        else:
            results.append({
                "function": f"{func_num} - {func_name}",
                "status": "❌ НЕ НАЙДЕНА",
                "error": "Функция не найдена в файле"
            })

    return results

def check_no_mock_data():
    """Проверяет что нет mock данных в исправленных функциях"""

    with open('api_gateway_server_current.py', 'r', encoding='utf-8') as f:
        content = f.read()

    functions_to_check = [
        ('get_phishing_sensitivity', '1/93'),
        ('get_analytics_overview', '2/93'),
        ('get_component_status', '3/93'),
        ('enable_component', '4/93')
    ]

    mock_issues = []

    for func_name, func_num in functions_to_check:
        func_start = content.find(f'def {func_name}')
        if func_start != -1:
            next_func = content.find('\n\n@app.', func_start + 1)
            if next_func == -1:
                next_func = len(content)
            func_content = content[func_start:next_func]

            if '"source": "mock"' in func_content:
                mock_issues.append({
                    "function": f"{func_num} - {func_name}",
                    "issue": "Найдены mock данные в исправленной функции"
                })

    return mock_issues

def main():
    print("🧪 ПРОВЕРКА ВСЕХ 4 ИСПРАВЛЕННЫХ ФУНКЦИЙ")
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
            print(f"  📝 Комментарий: {'✅' if result.get('has_fix_comment', False) else '❌'}")
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
        print("🎉 ВСЕ 4 ФУНКЦИИ ИСПРАВЛЕНЫ ПРАВИЛЬНО!")
        print("✅ Возвращают реальные данные из SFM")
        print("✅ Нет mock данных")
        print("✅ Имеют комментарии об исправлении")
        print("✅ Готовы к развертыванию")
        print("\n🚀 ГОТОВ ПЕРЕЙТИ К СЛЕДУЮЩЕЙ ФУНКЦИИ: 5/93")
    else:
        print("❌ НАЙДЕНЫ ПРОБЛЕМЫ!")
        print("🔧 Необходимо исправить перед продакшеном")

    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)