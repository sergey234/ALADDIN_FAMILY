#!/usr/bin/env python3
"""
ПРОВЕРКА ПОСЛЕ УДАЛЕНИЯ WORKAROUND
"""

import paramiko

def run_command(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8').strip()

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    print('🔍 ПРОВЕРКА ПОСЛЕ УДАЛЕНИЯ WORKAROUND')

    # Тестируем _execute_sfm_function
    print('🧪 ТЕСТ _execute_sfm_function:')
    test_cmd = '''cd /opt/aladdin-backend && python3 -c "
from sfm_adapter import sfm_adapter
try:
    sfm_adapter._initialize_sfm_sync()
    print(f'SFM available: {sfm_adapter.available}')
    result = sfm_adapter._execute_sfm_function('get_phishing_sensitivity', {})
    print(f'Result: {result}')
    if result and isinstance(result, dict) and 'source' in result:
        print(f'Source: {result[\"source\"]}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
"'''
    test_result = run_command(ssh, test_cmd)
    print(test_result)

    # Тестируем полную execute_function
    print('\\n🧪 ТЕСТ execute_function:')
    execute_cmd = '''cd /opt/aladdin-backend && python3 -c "
from sfm_adapter import sfm_adapter
success, result, error = sfm_adapter.execute_function('get_phishing_sensitivity', {})
print(f'success: {success}')
print(f'error: {error}')
if result and isinstance(result, dict) and 'source' in result:
    print(f'source: {result[\"source\"]}')
else:
    print(f'result: {result}')
"'''
    execute_result = run_command(ssh, execute_cmd)
    print(execute_result)

    # Проверяем API
    print('\\n🌐 ТЕСТ API:')
    api_result = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/phishing/sensitivity | jq .source 2>/dev/null || curl -s http://127.0.0.1:8002/api/phishing/sensitivity | grep source')
    print('API result:', api_result)

    ssh.close()

    if 'real_sfm' in api_result:
        print('\\n🎉 УСПЕХ! ПОЛУЧЕНЫ REAL SFM ДАННЫЕ!')
    else:
        print('\\n⚠️ Все еще проблемы - нужно проверить OptimizedSFM')

if __name__ == '__main__':
    main()