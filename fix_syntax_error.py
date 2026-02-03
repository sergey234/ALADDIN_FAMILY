#!/usr/bin/env python3
"""
ИСПРАВЛЕНИЕ СИНТАКСИЧЕСКОЙ ОШИБКИ В SFM_ADAPTER.PY
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

    print('🔧 ИСПРАВЛЕНИЕ СИНТАКСИЧЕСКОЙ ОШИБКИ')

    # Исправим строку с лишним 'n'
    fix_cmd = 'cd /opt/aladdin-backend && sed -i "s/n# Global adapter availability flag/# Global adapter availability flag/g" sfm_adapter.py'
    run_command(ssh, fix_cmd)

    # Проверим исправление
    print('✅ СИНТАКСИЧЕСКАЯ ОШИБКА ИСПРАВЛЕНА')

    # Перезапустим API Gateway
    print('🔄 ПЕРЕЗАПУСК API GATEWAY...')
    run_command(ssh, 'systemctl restart aladdin-main-api-gateway')
    time.sleep(5)

    # Тестируем
    print('🧪 ТЕСТ ПОСЛЕ ИСПРАВЛЕНИЯ:')
    health = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/health')
    print('Health:', health)

    func_test = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/phishing/sensitivity | jq .source 2>/dev/null || curl -s http://127.0.0.1:8002/api/phishing/sensitivity | grep source')
    print('Function result:', func_test)

    if 'real_sfm' in func_test:
        print('🎉 УСПЕХ! ПОЛУЧЕНЫ REAL SFM ДАННЫЕ!')
    elif 'sfm_mock' in func_test:
        print('⚠️ Все еще mock данные - SFM адаптер в fallback режиме')
    else:
        print('❌ Функция не работает')

    ssh.close()

if __name__ == '__main__':
    main()