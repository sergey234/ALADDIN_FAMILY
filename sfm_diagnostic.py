#!/usr/bin/env python3
"""
Диагностика SFM статуса - почему возвращается source: "sfm_mock"
"""

import paramiko

def run_ssh_command(ssh, command):
    """Выполнить команду на сервере"""
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode('utf-8').strip(), stderr.read().decode('utf-8').strip()

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    print('🔍 ДИАГНОСТИКА SFM СТАТУСА - ПОЧЕМУ source: "sfm_mock"?')
    print('=' * 60)

    # 1. Проверим статус SFM адаптера
    print('1️⃣ СТАТУС SFM АДАПТЕРА:')
    stdout, stderr = run_ssh_command(ssh, 'cd /opt/aladdin-backend && python3 -c "from sfm_adapter import SFM_ADAPTER_AVAILABLE, sfm_adapter; print(f\'SFM_ADAPTER_AVAILABLE: {SFM_ADAPTER_AVAILABLE}\'); print(f\'sfm_adapter exists: {sfm_adapter is not None}\')"')
    print(stdout)
    if stderr:
        print(f'❌ Ошибка: {stderr}')

    # 2. Проверим SFM процессы
    print('\n2️⃣ ПРОЦЕССЫ SFM CORE:')
    stdout, stderr = run_ssh_command(ssh, 'ps aux | grep -i sfm | grep -v grep')
    if stdout:
        print('✅ Найдены SFM процессы:')
        print(stdout)
    else:
        print('❌ SFM процессы НЕ найдены!')

    # 3. Проверим systemd статус
    print('\n3️⃣ SYSTEMD СЕРВИСЫ:')
    stdout, stderr = run_ssh_command(ssh, 'systemctl status aladdin-sfm-core 2>/dev/null || echo "Сервис aladdin-sfm-core не найден"')
    print(stdout[:300] + '...' if len(stdout) > 300 else stdout)

    # 4. Проверим логи SFM
    print('\n4️⃣ ЛОГИ SFM АДАПТЕРА:')
    stdout, stderr = run_ssh_command(ssh, 'cd /opt/aladdin-backend && tail -10 sfm_adapter.log 2>/dev/null || echo "Лог файл sfm_adapter.log не найден"')
    print(stdout)

    # 5. Проверим API health
    print('\n5️⃣ API HEALTH:')
    stdout, stderr = run_ssh_command(ssh, 'curl -s http://127.0.0.1:8002/api/health')
    print(stdout)

    # 6. Тест прямого вызова SFM функции
    print('\n6️⃣ ТЕСТ ПРЯМОГО ВЫЗОВА SFM:')
    test_code = '''
from sfm_adapter import sfm_adapter
if sfm_adapter:
    success, result, message = sfm_adapter.execute_function("get_phishing_sensitivity", {})
    print(f"Success: {success}")
    print(f"Result: {result}")
    print(f"Message: {message}")
else:
    print("SFM adapter is None")
'''
    stdout, stderr = run_ssh_command(ssh, f'cd /opt/aladdin-backend && python3 -c "{test_code}"')
    print(stdout)
    if stderr:
        print(f'❌ Ошибка выполнения: {stderr}')

    print('\n' + '=' * 60)
    print('🔍 АНАЛИЗ ПРОБЛЕМЫ:')
    print('source: "sfm_mock" означает, что:')
    print('• SFM_ADAPTER_AVAILABLE = True (адаптер загружен)')
    print('• sfm_adapter.execute_function() возвращает success=True')
    print('• НО результат содержит mock данные')
    print('')
    print('Это означает, что SFM Core НЕ запущен или НЕ отвечает!')
    print('SFM адаптер использует mock fallback для поддержания работы API.')
    print('')
    print('РЕШЕНИЕ: Запустить SFM Core или проверить его статус.')

    ssh.close()

if __name__ == '__main__':
    main()