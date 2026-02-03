#!/usr/bin/env python3
"""
УБИРАЕМ TEMPORARY WORKAROUND ИЗ SFM АДАПТЕРА
"""

import paramiko
import time

def run_command(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8').strip()

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    print('🔧 УБИРАЕМ TEMPORARY WORKAROUND')

    # Удалим workaround блок
    remove_cmd = '''cd /opt/aladdin-backend && sed -i '/TEMPORARY WORKAROUND: Return mock data for testing integration/,/return mock_result/d' sfm_adapter.py'''
    run_command(ssh, remove_cmd)

    # Проверим удаление
    check = run_command(ssh, 'cd /opt/aladdin-backend && grep -A 3 "TEMPORARY WORKAROUND" sfm_adapter.py || echo "WORKAROUND УДАЛЕН"')
    print('Проверка:', check)

    # Перезапустим API Gateway
    print('🔄 ПЕРЕЗАПУСК API GATEWAY...')
    run_command(ssh, 'systemctl restart aladdin-main-api-gateway')
    time.sleep(5)

    # Тестируем
    print('🧪 ТЕСТ ПОСЛЕ УДАЛЕНИЯ:')
    health = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/health')
    print('Health:', health)

    func_test = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/phishing/sensitivity | jq .source 2>/dev/null || curl -s http://127.0.0.1:8002/api/phishing/sensitivity | grep source')
    print('Function result:', func_test)

    if 'real_sfm' in func_test:
        print('🎉 УСПЕХ! ПОЛУЧЕНЫ REAL SFM ДАННЫЕ!')
    else:
        print('⚠️ Все еще mock данные')

    ssh.close()

if __name__ == '__main__':
    main()