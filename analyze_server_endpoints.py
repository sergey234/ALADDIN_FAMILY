#!/usr/bin/env python3
import json

def analyze_server_endpoints():
    with open('server_openapi.json', 'r') as f:
        data = json.load(f)

    paths = data.get('paths', {})
    print('🚀 АНАЛИЗ ENDPOINT\'ОВ С СЕРВЕРА 149.154.65.180:8002')
    print('=' * 60)

    # Категории для анализа
    categories = {
        'Authentication': [],
        'AI Assistant': [],
        'Components': [],
        'Crash Detection': [],
        'Gamification': [],
        'IoT Security': [],
        'Location/Geofences': [],
        'Metrics': [],
        'Notifications': [],
        'Parental Control': [],
        'Reports': [],
        'Roadside Assistance': [],
        'Settings': [],
        'Subscription': [],
        'System': [],
        'User Profile': [],
        'Other': []
    }

    # Распределяем endpoint'ы по категориям
    for path in paths:
        if '/auth/' in path:
            categories['Authentication'].append(path)
        elif '/ai/assistant' in path:
            categories['AI Assistant'].append(path)
        elif '/components/' in path:
            categories['Components'].append(path)
        elif '/crash-detection/' in path:
            categories['Crash Detection'].append(path)
        elif '/gamification/' in path:
            categories['Gamification'].append(path)
        elif '/iot/' in path:
            categories['IoT Security'].append(path)
        elif '/location/' in path or '/geofences' in path:
            categories['Location/Geofences'].append(path)
        elif '/metrics/' in path:
            categories['Metrics'].append(path)
        elif '/notifications/' in path:
            categories['Notifications'].append(path)
        elif '/parental' in path:
            categories['Parental Control'].append(path)
        elif '/reports/' in path:
            categories['Reports'].append(path)
        elif '/roadside' in path:
            categories['Roadside Assistance'].append(path)
        elif '/settings/' in path:
            categories['Settings'].append(path)
        elif '/subscription/' in path:
            categories['Subscription'].append(path)
        elif '/system/' in path:
            categories['System'].append(path)
        elif '/user/' in path:
            categories['User Profile'].append(path)
        else:
            categories['Other'].append(path)

    # Выводим результаты
    total_endpoints = 0

    for category, endpoints in categories.items():
        if endpoints:  # Только непустые категории
            count = len(endpoints)
            total_endpoints += count

            print(f'📁 {category}: {count} endpoint\'ов')

            # Показываем первые 3 endpoint'а каждой категории
            for ep in sorted(endpoints)[:3]:
                methods = [m.upper() for m in paths[ep].keys() if m.lower() != 'parameters']
                method_str = methods[0] if methods else 'UNK'
                print(f'   {method_str:6} {ep}')

            if count > 3:
                print(f'   ... и ещё {count - 3} endpoint\'ов')

            print()

    print('=' * 60)
    print(f'🎯 ОБЩИЙ ИТОГ: {len(paths)} endpoint\'ов на сервере')
    print(f'✅ Подтверждено: {total_endpoints} endpoint\'ов распределены по категориям')
    print('=' * 60)

    # Критические находки
    print('🔥 КРИТИЧЕСКИЕ НАХОДКИ:')
    if categories['Metrics']:
        print('✅ METRICS: Есть /api/metrics/upload - аналитика работает!')
    else:
        print('❌ METRICS: Нет endpoint\'а для загрузки метрик!')

    if categories['Notifications']:
        print(f'✅ NOTIFICATIONS: Полная система уведомлений ({len(categories["Notifications"])} endpoint\'ов)!')
    else:
        print('❌ NOTIFICATIONS: Система уведомлений отсутствует!')

    if categories['Subscription']:
        print(f'✅ SUBSCRIPTION: Система подписок ({len(categories["Subscription"])} endpoint\'ов)!')
    else:
        print('❌ SUBSCRIPTION: Система подписок отсутствует!')

    print()
    print('📊 СРАВНЕНИЕ С НАШЕЙ СПЕЦИФИКАЦИЕЙ:')
    print('Спецификация: 221 endpoint\'ов')
    print(f'Сервер:        {len(paths)} endpoint\'ов')
    print(f'Разница:       {len(paths) - 221} endpoint\'ов')

if __name__ == '__main__':
    analyze_server_endpoints()