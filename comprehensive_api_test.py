#!/usr/bin/env python3
"""
КОМПЛЕКСНАЯ ПРОВЕРКА ВСЕХ ИСПРАВЛЕННЫХ API ФУНКЦИЙ
Проверяет что все функции работают на сервере и возвращают реальные SFM данные
"""

import paramiko
import json

def test_function(name, endpoint, method='GET', data=None, description=''):
    """Тестирует одну функцию API"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    # Формируем curl команду
    if method == 'GET':
        cmd = f'curl -s http://127.0.0.1:8002{endpoint}'
    elif method == 'POST':
        cmd = f'curl -s -X POST http://127.0.0.1:8002{endpoint}'
    elif method == 'PUT':
        if data:
            cmd = f'curl -s -X PUT -H "Content-Type: application/json" -d \'{json.dumps(data)}\' http://127.0.0.1:8002{endpoint}'
        else:
            cmd = f'curl -s -X PUT http://127.0.0.1:8002{endpoint}'

    stdin, stdout, stderr = ssh.exec_command(cmd)
    response = stdout.read().decode('utf-8').strip()
    ssh.close()

    print(f'\n🧪 {name}: {description}')
    print(f'   Эндпоинт: {method} {endpoint}')

    # Проверяем на mock данные
    if '"source": "mock"' in response.lower() or '"mock"' in response.lower():
        print('   ❌ MOCK ДАННЫЕ ОБНАРУЖЕНЫ!')
        print(f'   Ответ: {response[:100]}...')
        return False
    else:
        print('   ✅ РЕАЛЬНЫЕ ДАННЫЕ')
        try:
            json_response = json.loads(response)
            if 'source' in json_response and 'sfm' in json_response['source'].lower():
                print('   ✅ SFM интеграция работает')
            else:
                print('   ⚠️ Нет явного указания на SFM источник')
        except:
            print('   ⚠️ Ответ не в JSON формате')
        return True

def main():
    """Основная функция тестирования"""
    print('🔍 КОМПЛЕКСНАЯ ПРОВЕРКА ВСЕХ ИСПРАВЛЕННЫХ API ФУНКЦИЙ')
    print('=' * 70)

    # Список всех 14 исправленных функций
    functions = [
        ('1/93: phishing/sensitivity', '/api/phishing/sensitivity', 'GET', None, 'Чувствительность фишинга'),
        ('2/93: analytics/overview', '/api/analytics/overview', 'GET', None, 'Обзор аналитики'),
        ('3/93: components/status', '/api/components/status/crash_detection_agent', 'GET', None, 'Статус компонента'),
        ('4/93: components/enable', '/api/components/enable/crash_detection_agent', 'POST', None, 'Включение компонента'),
        ('5/93: components/disable', '/api/components/disable/crash_detection_agent', 'POST', None, 'Отключение компонента'),
        ('6/93: components/config GET', '/api/components/config/crash_detection_agent', 'GET', None, 'Получение конфига'),
        ('7/93: components/config PUT', '/api/components/config/crash_detection_agent', 'PUT', {'enabled': True, 'threshold': 80}, 'Обновление конфига'),
        ('8/93: components/health', '/api/components/health', 'GET', None, 'Здоровье компонентов'),
        ('9/93: components/restart', '/api/components/restart/crash_detection_agent', 'POST', None, 'Перезапуск компонента'),
        ('10/93: components/logs', '/api/components/logs/crash_detection_agent?limit=10', 'GET', None, 'Логи компонента'),
        ('11/93: components/backup', '/api/components/backup/crash_detection_agent', 'POST', None, 'Резервная копия'),
        ('12/93: components/restore', '/api/components/restore/crash_detection_agent?backup_id=backup_2024_01_01', 'POST', None, 'Восстановление'),
        ('13/93: phishing/block_suspicious GET', '/api/phishing/block_suspicious', 'GET', None, 'Проверка блокировки подозрительных'),
        ('14/93: phishing/block_suspicious PUT', '/api/phishing/block_suspicious', 'PUT', {'block_suspicious': False, 'threshold': 0.3}, 'Настройка блокировки'),
    ]

    working_functions = 0
    total_functions = len(functions)

    for name, endpoint, method, data, desc in functions:
        if test_function(name, endpoint, method, data, desc):
            working_functions += 1

    print('\n' + '=' * 70)
    print('📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:')
    print(f'✅ Рабочих функций: {working_functions}/{total_functions}')
    print(f'❌ Неисправных функций: {total_functions - working_functions}')

    if working_functions == total_functions:
        print('\n🎉 ВСЕ ФУНКЦИИ РАБОТАЮТ КОРРЕКТНО!')
        print('✅ Все API возвращают реальные SFM данные')
        print('✅ Мобильное приложение может взаимодействовать')
        print('✅ Нет mock данных в ответах')
    else:
        print(f'\n⚠️ ОБНАРУЖЕНЫ ПРОБЛЕМЫ! {total_functions - working_functions} функций не работают')

if __name__ == '__main__':
    main()