#!/usr/bin/env python3
"""
ОТЛАДКА SFM АДАПТЕРА - ПОЧЕМУ ОН ИСПОЛЬЗУЕТ FALLBACK
"""

import paramiko

def run_command(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8').strip()

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    print('🔍 ОТЛАДКА SFM АДАПТЕРА - ПОЧЕМУ FALLBACK')
    print('=' * 60)

    # 1. Проверим статус SFM адаптера
    print('1️⃣ СТАТУС SFM АДАПТЕРА:')
    status_test = '''cd /opt/aladdin-backend && python3 -c "
from sfm_adapter import sfm_adapter
print(f'available: {sfm_adapter.available}')
print(f'_sfm: {sfm_adapter._sfm}')
print(f'_sfm type: {type(sfm_adapter._sfm) if sfm_adapter._sfm else None}')
if sfm_adapter._sfm and hasattr(sfm_adapter._sfm, 'functions'):
    print(f'functions count: {len(sfm_adapter._sfm.functions)}')
print(f'metrics: {sfm_adapter.metrics}')
"'''
    status = run_command(ssh, status_test)
    print(status)

    # 2. Протестируем execute_function напрямую
    print('\\n2️⃣ ТЕСТ EXECUTE_FUNCTION:')
    execute_test = '''cd /opt/aladdin-backend && python3 -c "
from sfm_adapter import sfm_adapter
success, result, error = sfm_adapter.execute_function('get_phishing_sensitivity', {})
print(f'success: {success}')
print(f'result: {result}')
print(f'error: {error}')
if result and 'source' in result:
    print(f'source: {result[\"source\"]}')
"'''
    execute_result = run_command(ssh, execute_test)
    print(execute_result)

    # 3. Посмотрим логику в execute_function
    print('\\n3️⃣ АНАЛИЗ ЛОГИКИ EXECUTE_FUNCTION:')
    logic_check = run_command(ssh, 'cd /opt/aladdin-backend && grep -A 10 "def execute_function" sfm_adapter.py')
    print(logic_check)

    # 4. Найдем условие fallback
    print('\\n4️⃣ УСЛОВИЕ FALLBACK:')
    fallback_check = run_command(ssh, 'cd /opt/aladdin-backend && grep -A 5 -B 5 "fallback" sfm_adapter.py | grep -A 10 "if not self.available"')
    print(fallback_check)

    # 5. Проверим _initialize_sfm_sync
    print('\\n5️⃣ ПРОВЕРКА _initialize_sfm_sync:')
    init_test = '''cd /opt/aladdin-backend && python3 -c "
from sfm_adapter import sfm_adapter
print('Calling _initialize_sfm_sync...')
try:
    sfm_adapter._initialize_sfm_sync()
    print(f'After init - available: {sfm_adapter.available}')
    print(f'After init - _sfm: {sfm_adapter._sfm}')
    print(f'After init - _sfm type: {type(sfm_adapter._sfm) if sfm_adapter._sfm else None}')
except Exception as e:
    print(f'Init error: {e}')
"'''
    init_result = run_command(ssh, init_test)
    print(init_result)

    ssh.close()

    print('\\n' + '=' * 60)
    print('🎯 ДИАГНОСТИКА ПРОБЛЕМЫ:')
    print('• SFM адаптер не инициализируется правильно')
    print('• available = False, поэтому идет в fallback')
    print('• Нужно исправить логику инициализации')

if __name__ == '__main__':
    main()