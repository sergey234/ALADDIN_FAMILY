#!/usr/bin/env python3
"""
АНАЛИЗ _execute_sfm_function - ПОЧЕМУ ВОЗВРАЩАЕТ MOCK ДАННЫЕ
"""

import paramiko

def run_command(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8').strip()

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    print('🔍 АНАЛИЗ _execute_sfm_function')
    print('=' * 50)

    # Посмотрим на _execute_sfm_function
    execute_sfm = run_command(ssh, 'cd /opt/aladdin-backend && grep -A 40 "def _execute_sfm_function" sfm_adapter.py')
    print('КОД _execute_sfm_function:')
    print(execute_sfm)

    # Посмотрим на _execute_mock_function
    execute_mock = run_command(ssh, 'cd /opt/aladdin-backend && grep -A 15 "def _execute_mock_function" sfm_adapter.py')
    print('\\nКОД _execute_mock_function:')
    print(execute_mock)

    # Тестируем _execute_sfm_function напрямую
    print('\\n🧪 ТЕСТ _execute_sfm_function:')
    test_cmd = '''cd /opt/aladdin-backend && python3 -c "
from sfm_adapter import sfm_adapter
try:
    # Инициализируем
    sfm_adapter._initialize_sfm_sync()
    print(f'Initialized: available={sfm_adapter.available}')
    print(f'SFM object: {type(sfm_adapter._sfm)}')
    
    # Тестируем _execute_sfm_function
    result = sfm_adapter._execute_sfm_function('get_phishing_sensitivity', {})
    print(f'SFM result: {result}')
    print(f'Result type: {type(result)}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
"'''
    test_result = run_command(ssh, test_cmd)
    print(test_result)

    # Тестируем _execute_mock_function
    print('\\n🧪 ТЕСТ _execute_mock_function:')
    mock_cmd = '''cd /opt/aladdin-backend && python3 -c "
from sfm_adapter import sfm_adapter
try:
    result = sfm_adapter._execute_mock_function('get_phishing_sensitivity', {})
    print(f'Mock result: {result}')
    print(f'Result type: {type(result)}')
except Exception as e:
    print(f'Error: {e}')
"'''
    mock_result = run_command(ssh, mock_cmd)
    print(mock_result)

    ssh.close()

    print('\\n' + '=' * 50)
    print('🎯 ВЫВОД:')
    print('Если _execute_sfm_function возвращает mock данные,')
    print('то проблема в том, что SFM объект не работает правильно.')
    print('Нужно проверить OptimizedSFM или использовать настоящий SafeFunctionManager.')

if __name__ == '__main__':
    main()