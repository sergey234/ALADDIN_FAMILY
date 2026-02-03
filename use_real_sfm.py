#!/usr/bin/env python3
"""
ИСПРАВЛЯЕМ SFM АДАПТЕР - ИСПОЛЬЗУЕМ НАСТОЯЩИЙ SafeFunctionManager
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

    print('🔧 ИСПОЛЬЗУЕМ НАСТОЯЩИЙ SafeFunctionManager')

    # 1. Изменим импорт
    run_command(ssh, 'cd /opt/aladdin-backend && sed -i "s/from security.sfm_singleton import get_sfm/from security.safe_function_manager import SafeFunctionManager/g" sfm_adapter.py')

    # 2. Изменим инициализацию (заменим get_sfm() на SafeFunctionManager())
    run_command(ssh, 'cd /opt/aladdin-backend && sed -i "s/self._sfm = get_sfm()/self._sfm = SafeFunctionManager()/g" sfm_adapter.py')

    # 3. Проверим изменения
    print('✅ ПРОВЕРКА ИЗМЕНЕНИЙ:')
    changes = run_command(ssh, 'cd /opt/aladdin-backend && grep -A 2 -B 2 "SafeFunctionManager" sfm_adapter.py')
    print(changes)

    # 4. Перезапустим API Gateway
    print('🔄 ПЕРЕЗАПУСК API GATEWAY...')
    run_command(ssh, 'systemctl restart aladdin-main-api-gateway')
    time.sleep(5)

    # 5. Тестируем
    print('🧪 ТЕСТ С НАСТОЯЩИМ SFM:')
    health = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/health')
    print('Health:', health)

    func_test = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/phishing/sensitivity | jq .source 2>/dev/null || curl -s http://127.0.0.1:8002/api/phishing/sensitivity | grep source')
    print('Function result:', func_test)

    if 'real_sfm' in func_test:
        print('🎉 УСПЕХ! ПОЛУЧЕНЫ REAL SFM ДАННЫЕ!')
        print('✅ SFM адаптер теперь использует настоящий SafeFunctionManager!')
    else:
        print('❌ Все еще mock данные')

    ssh.close()

if __name__ == '__main__':
    main()