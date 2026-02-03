#!/usr/bin/env python3
"""
Запуск SFM Core для получения реальных данных вместо mock
"""

import paramiko
import time

def run_command(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8').strip(), stderr.read().decode('utf-8').strip()

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    print('🚀 ЗАПУСК SFM CORE ДЛЯ РЕАЛЬНЫХ ДАННЫХ')
    print('=' * 50)

    # 1. Проверим структуру проекта
    print('1️⃣ ПРОВЕРКА СТРУКТУРЫ ПРОЕКТА:')
    stdout, stderr = run_command(ssh, 'cd /opt/aladdin-backend && find . -name "*sfm*" -type f | head -10')
    print('SFM файлы:')
    print(stdout)

    # 2. Проверим main модуль SFM
    print('\n2️⃣ ПРОВЕРКА SFM MAIN МОДУЛЯ:')
    stdout, stderr = run_command(ssh, 'cd /opt/aladdin-backend && ls -la sfm_core/ 2>/dev/null || echo "Директория sfm_core не найдена"')
    print(stdout)

    # 3. Попробуем импортировать SFM
    print('\n3️⃣ ТЕСТ ИМПОРТА SFM:')
    test_import = '''
try:
    from sfm_core import SFMCore
    print("✅ SFM Core можно импортировать")
    sfm = SFMCore()
    print("✅ SFM Core инициализирован")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
except Exception as e:
    print(f"❌ Ошибка инициализации: {e}")
'''
    stdout, stderr = run_command(ssh, f'cd /opt/aladdin-backend && python3 -c "{test_import}"')
    print(stdout)
    if stderr:
        print(f'Stderr: {stderr}')

    # 4. Проверим API health до запуска
    print('\n4️⃣ API HEALTH ДО ЗАПУСКА:')
    stdout, stderr = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/health')
    print(stdout)

    # 5. Попробуем запустить SFM как демон
    print('\n5️⃣ ЗАПУСК SFM CORE:')
    start_cmd = '''
cd /opt/aladdin-backend
nohup python3 -c "
from sfm_core import SFMCore
import time
print('Starting SFM Core...')
sfm = SFMCore()
print('SFM Core started successfully')
while True:
    time.sleep(1)
" > sfm_core.log 2>&1 &
echo $! > sfm_core.pid
'''
    stdout, stderr = run_command(ssh, start_cmd)
    print('Результат запуска:')
    print(stdout)
    if stderr:
        print(f'Ошибка: {stderr}')

    # Подождем немного
    time.sleep(3)

    # 6. Проверим что запустилось
    print('\n6️⃣ ПРОВЕРКА ЗАПУСКА:')
    stdout, stderr = run_command(ssh, 'cd /opt/aladdin-backend && ps aux | grep python | grep -v grep')
    print('Python процессы:')
    print(stdout)

    # 7. Проверим логи
    print('\n7️⃣ ЛОГИ SFM CORE:')
    stdout, stderr = run_command(ssh, 'cd /opt/aladdin-backend && tail -5 sfm_core.log 2>/dev/null || echo "Лог файл не найден"')
    print(stdout)

    # 8. Проверим API health после запуска
    print('\n8️⃣ API HEALTH ПОСЛЕ ЗАПУСКА:')
    stdout, stderr = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/health')
    print(stdout)

    print('\n' + '=' * 50)
    print('🎯 РЕЗУЛЬТАТ:')
    print('Если SFM Core запустился, API health должен показать:')
    print('"sfm_adapter": "real" вместо "sfm_adapter": "fallback"')
    print('')
    print('Тогда все наши исправленные функции будут возвращать:')
    print('"source": "real_sfm" вместо "source": "sfm_mock"')

    ssh.close()

if __name__ == '__main__':
    main()