#!/usr/bin/env python3
"""Анализ результатов тестирования endpoints"""
import json
import glob
from collections import defaultdict

# Найти последний JSON файл
files = sorted(glob.glob('endpoints_test_report_*.json'), reverse=True)
if not files:
    print("❌ JSON файл не найден")
    exit(1)

with open(files[0], 'r', encoding='utf-8') as f:
    data = json.load(f)

# Структура может быть разной
if 'endpoints' in data:
    endpoints = data.get('endpoints', [])
    stats = data.get('statistics', {})
elif 'results' in data:
    endpoints = data.get('results', [])
    stats = data.get('stats', {})
else:
    endpoints = []
    stats = {}

print("\n" + "="*80)
print("📋 ВСЕ ENDPOINTS ПО ПУНКТАМ ({} шт.)".format(len(endpoints)))
print("="*80 + "\n")

# Группировка по статусам
by_status = defaultdict(list)
for ep in endpoints:
    code = ep.get('http_code', 'N/A')
    by_status[code].append(ep)

# Вывести все endpoints по порядку
for i, ep in enumerate(endpoints, 1):
    method = ep.get('method', 'GET')
    path = ep.get('path', '')
    status = ep.get('http_code', 'N/A')
    response_time = ep.get('response_time_ms', 0) or 0
    if response_time is None:
        response_time = 0
    
    # Иконки по статусу
    if status == 200:
        icon = '✅'
    elif status == 201:
        icon = '✅'
    elif status == 204:
        icon = '✅'
    elif status == 422:
        icon = '⚠️'
    elif status == 404:
        icon = '❌'
    elif status == 401:
        icon = '🔒'
    elif status == 500:
        icon = '💥'
    else:
        icon = '❓'
    
    print(f"{i:3d}. {icon} {method:6s} {path:60s} [HTTP {status}] ({response_time:.1f}ms)")

print("\n" + "="*80)
print("📊 СТАТИСТИКА")
print("="*80)
print(f"\nВсего endpoints: {len(endpoints)}")
print(f"✅ Успешно (200/201/204): {stats.get('status_200', 0) + stats.get('status_201', 0) + stats.get('status_204', 0)}")
print(f"⚠️  422 Validation Error: {stats.get('status_422', 0)}")
print(f"❌ 404 Not Found: {stats.get('status_404', 0)}")
print(f"🔒 401 Unauthorized: {stats.get('status_401', 0)}")
print(f"💥 500+ Server Error: {stats.get('status_500', 0)}")

print("\n" + "="*80)
print("❌ ENDPOINTS С 404 (Not Found) - {} шт.".format(len(by_status.get(404, []))))
print("="*80)
for i, ep in enumerate(by_status.get(404, []), 1):
    print(f"  {i}. {ep.get('method', 'GET')} {ep.get('path', '')}")

print("\n" + "="*80)
print("✅ УСПЕШНЫЕ ENDPOINTS (200 OK) - {} шт.".format(len(by_status.get(200, []))))
print("="*80)
for i, ep in enumerate(by_status.get(200, []), 1):
    print(f"  {i:3d}. {ep.get('method', 'GET'):6s} {ep.get('path', '')}")
