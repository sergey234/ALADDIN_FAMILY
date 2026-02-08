#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексная проверка всех эндпоинтов ALADDIN сервера
На основе документации ALADDIN_COMPLETE_SYSTEM_ARCHITECTURE_AND_API_REFERENCE.md
"""

import requests
import time
import json

def test_aladdin_endpoints():
    """Тестирование всех эндпоинтов ALADDIN"""

    base_url = 'http://149.154.65.180:8002'

    # Категории из документации (выборочные эндпоинты для проверки)
    categories = [
        ('Authentication', 12, [
            ('GET', 'api/auth/profile'),
            ('POST', 'api/auth/login'),
            ('POST', 'api/auth/logout')
        ]),
        ('Subscription', 12, [
            ('GET', 'api/subscription/status'),
            ('GET', 'api/subscription/plans'),
            ('GET', 'api/subscription/billing_history')
        ]),
        ('Notifications', 16, [
            ('GET', 'api/notifications/list'),
            ('GET', 'api/notifications/stats'),
            ('GET', 'api/notifications/unread_count')
        ]),
        ('Components', 20, [
            ('GET', 'api/components/health'),
            ('GET', 'api/components/status/sfm_core')
        ]),
        ('Identity Protection', 26, [
            ('GET', 'api/identity/stats'),
            ('GET', 'api/identity/attempts')
        ]),
        ('Dark Web', 7, [
            ('GET', 'api/darkweb/stats'),
            ('POST', 'api/darkweb/scan_start')
        ]),
        ('Location', 15, [
            ('GET', 'api/location/stats'),
            ('GET', 'api/location/requests')
        ]),
        ('System', 17, [
            ('GET', 'api/system/health'),
            ('GET', 'api/system/info')
        ]),
        ('Analytics', 17, [
            ('GET', 'api/analytics/overview'),
            ('GET', 'api/analytics/performance')
        ]),
        ('Health Checks', 2, [
            ('GET', 'api/health'),
            ('GET', 'api/system/health')
        ])
    ]

    print('🔍 КОМПЛЕКСНАЯ ПРОВЕРКА ЭНДПОИНТОВ ALADDIN')
    print('=' * 80)
    print(f'Сервер: {base_url}')
    print(f'Документация обещает: 187 эндпоинтов')
    print()

    total_endpoints = 0
    working_endpoints = 0
    sfm_endpoints = 0
    response_times = []

    for category_name, expected_count, endpoints in categories:
        print(f'📂 {category_name} ({expected_count} эндпоинтов):')

        for method, endpoint in endpoints:
            try:
                url = f'{base_url}/{endpoint}'
                start_time = time.time()

                # Выполняем запрос
                if method == 'POST':
                    if 'login' in endpoint:
                        data = {"username": "test", "password": "test123", "device_fingerprint": "test"}
                    elif 'scan_start' in endpoint:
                        data = {}
                    else:
                        data = {}
                    response = requests.post(url, json=data, timeout=10)
                else:
                    response = requests.get(url, timeout=10)

                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
                total_endpoints += 1

                # Анализ ответа
                if response.status_code == 200:
                    working_endpoints += 1
                    status_icon = '✅'

                    try:
                        data = response.json()
                        if data.get('source') == 'real_sfm':
                            sfm_icon = '🔒 SFM'
                            sfm_endpoints += 1
                        else:
                            sfm_icon = '⚠️ No SFM'
                    except:
                        sfm_icon = '📄 JSON'
                else:
                    status_icon = '❌'
                    sfm_icon = f'HTTP {response.status_code}'

                print(f'   {status_icon} {method} {endpoint} - {sfm_icon} ({response_time:.1f}ms)')
            except Exception as e:
                total_endpoints += 1
                print(f'   ❌ {method} {endpoint} - ОШИБКА: {str(e)[:50]}...')

    # Проверка Crash Detection (которого нет)
    print(f'\\n🚨 CRASH DETECTION (ДОЛЖНО БЫТЬ 6 эндпоинтов):')
    crash_endpoints = [
        'api/crash-detection/setup',
        'api/crash-detection/alert',
        'api/crash-detection/start',
        'api/crash-detection/stop',
        'api/crash-detection/data',
        'api/crash-detection/status'
    ]

    crash_working = 0
    for endpoint in crash_endpoints:
        try:
            response = requests.get(f'{base_url}/{endpoint}', timeout=5)
            total_endpoints += 1
            if response.status_code == 200:
                crash_working += 1
                print(f'   ✅ GET {endpoint} - HTTP 200')
            else:
                print(f'   ❌ GET {endpoint} - HTTP {response.status_code}')
        except:
            total_endpoints += 1
            print(f'   ❌ GET {endpoint} - ОШИБКА')

    print('\\n' + '=' * 80)
    print('📊 ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ:')
    print(f'Всего проверено эндпоинтов: {total_endpoints}')
    print(f'Рабочих эндпоинтов: {working_endpoints} ({working_endpoints/total_endpoints*100:.1f}%)')
    print(f'SFM интеграция: {sfm_endpoints} ({sfm_endpoints/working_endpoints*100:.1f}% от рабочих)')
    print(f'Документация: 187 эндпоинтов (100% должны работать)')

    if crash_working == 0:
        print(f'🚨 CRASH DETECTION: 0/6 эндпоинтов (НУЖЕН ДЕПЛОЙ!)')

    if response_times:
        avg_time = sum(response_times) / len(response_times)
        print(f'\\n⚡ ПРОИЗВОДИТЕЛЬНОСТЬ:')
        print(f'Среднее время ответа: {avg_time:.1f}ms')
        print(f'Цель по документации: <15ms')
        if avg_time > 15:
            print(f'❌ Требуется оптимизация!')

    print(f'\\n🎯 СТАТУС: {working_endpoints}/{total_endpoints} эндпоинтов работают')

if __name__ == "__main__":
    test_aladdin_endpoints()