#!/usr/bin/env python3
"""
Скрипт для сравнения endpoint'ов из api_gateway_server_current.py с роутерами на сервере
"""
import re
import json
import os

def extract_endpoints_from_file(filepath):
    """Извлекает все endpoint'ы из файла"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем @app. или @router. декораторы
        pattern = r'@(app|router)\.(get|post|put|delete|patch)\("([^"]+)"'
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        endpoints = []
        for _, method, path in matches:
            endpoints.append(f"{method.upper()} {path}")
        
        return endpoints
    except Exception as e:
        print(f"Ошибка при чтении {filepath}: {e}")
        return []

# Читаем api_gateway_server_current.py
print("=== Чтение api_gateway_server_current.py ===")
old_endpoints = extract_endpoints_from_file('api_gateway_server_current.py')
old_unique = list(set(old_endpoints))
print(f"Всего endpoint'ов: {len(old_endpoints)}")
print(f"Уникальных: {len(old_unique)}")

# Читаем router_endpoints_unique.txt (если есть)
router_endpoints = []
if os.path.exists('router_endpoints_unique.txt'):
    with open('router_endpoints_unique.txt', 'r', encoding='utf-8') as f:
        router_endpoints = [line.strip() for line in f if line.strip()]
    print(f"\n=== Чтение router_endpoints_unique.txt ===")
    print(f"Всего endpoint'ов в роутерах: {len(router_endpoints)}")
else:
    print("\n⚠️ Файл router_endpoints_unique.txt не найден")
    print("Запустите сначала команду для получения списка с сервера")

# Сравнение
old_set = set(old_unique)
router_set = set(router_endpoints)

missing = old_set - router_set
already_migrated = old_set & router_set

print(f"\n=== РЕЗУЛЬТАТЫ СРАВНЕНИЯ ===")
print(f"В api_gateway_server_current.py: {len(old_set)}")
print(f"В роутерах на сервере: {len(router_set)}")
print(f"Уже мигрированы: {len(already_migrated)}")
print(f"Отсутствуют в роутерах: {len(missing)}")

# Группируем отсутствующие по категориям
categories = {
    'components': [],
    'protection': [],
    'monitoring': [],
    'system': [],
    'auth': [],
    'family': [],
    'payments': [],
    'referral': [],
    'other': []
}

for ep in sorted(missing):
    path = ep.split(' ', 1)[1] if ' ' in ep else ep
    if '/components' in path:
        categories['components'].append(ep)
    elif '/protection' in path or '/security' in path or '/phishing' in path or '/malware' in path or '/mobile' in path or '/network' in path:
        categories['protection'].append(ep)
    elif '/monitoring' in path or '/analytics' in path or '/reports' in path or '/ai/categories' in path or '/darkweb' in path or '/identity' in path or '/location' in path or '/antitracker' in path or '/data/cleanup' in path:
        categories['monitoring'].append(ep)
    elif '/system' in path:
        categories['system'].append(ep)
    elif '/auth' in path or '/login' in path or '/register' in path:
        categories['auth'].append(ep)
    elif '/family' in path:
        categories['family'].append(ep)
    elif '/payments' in path or '/payment' in path:
        categories['payments'].append(ep)
    elif '/referral' in path:
        categories['referral'].append(ep)
    else:
        categories['other'].append(ep)

# Выводим по категориям
print(f"\n=== ОТСУТСТВУЮЩИЕ ENDPOINT'Ы ПО КАТЕГОРИЯМ ===")
for cat, endpoints in categories.items():
    if endpoints:
        print(f"\n{cat.upper()}: {len(endpoints)} endpoint'ов")
        for ep in endpoints[:10]:
            print(f"  - {ep}")
        if len(endpoints) > 10:
            print(f"  ... и еще {len(endpoints) - 10}")

# Сохраняем отчет
report = {
    'total_old': len(old_set),
    'total_routers': len(router_set),
    'already_migrated': len(already_migrated),
    'missing_count': len(missing),
    'missing_by_category': {k: len(v) for k, v in categories.items() if v},
    'missing_list': sorted(missing),
    'missing_by_category_detail': {k: sorted(v) for k, v in categories.items() if v}
}

with open('missing_endpoints_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n✅ Детальный анализ сохранен в missing_endpoints_analysis.json")
