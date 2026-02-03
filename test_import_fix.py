#!/usr/bin/env python3
"""
ПРОСТОЙ ТЕСТ ИМПОРТА SFM_ADAPTER_AVAILABLE
"""

import paramiko

def run_command(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8').strip()

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    print('🧪 ТЕСТ ИМПОРТА SFM_ADAPTER_AVAILABLE')

    # Тестируем импорт
    test_cmd = 'cd /opt/aladdin-backend && python3 -c "from sfm_adapter import SFM_ADAPTER_AVAILABLE; print(f\'SFM_ADAPTER_AVAILABLE = {SFM_ADAPTER_AVAILABLE}\')"'
    result = run_command(ssh, test_cmd)
    print('Результат:', result)

    if 'SFM_ADAPTER_AVAILABLE = True' in result:
        print('✅ ПЕРЕМЕННАЯ ДОСТУПНА!')

        # Перезапускаем API Gateway
        print('\\n🔄 ПЕРЕЗАПУСК API GATEWAY...')
        run_command(ssh, 'systemctl restart aladdin-main-api-gateway')

        import time
        time.sleep(5)

        # Тестируем API
        print('\\n🧪 ТЕСТ API:')
        health = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/health')
        print('Health:', health)

        func_test = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/phishing/sensitivity | jq .source 2>/dev/null || curl -s http://127.0.0.1:8002/api/phishing/sensitivity | grep source')
        print('Function test:', func_test)

        if 'real_sfm' in func_test:
            print('\\n🎉 УСПЕХ! ПОЛУЧЕНЫ REAL SFM ДАННЫЕ!')
        elif 'sfm_mock' in func_test:
            print('\\n⚠️ Все еще mock данные, но переменная исправлена')
        else:
            print('\\n❓ Неизвестный результат')

    else:
        print('❌ ПЕРЕМЕННАЯ НЕ ДОСТУПНА')

    ssh.close()

if __name__ == '__main__':
    main()