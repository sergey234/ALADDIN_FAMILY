#!/usr/bin/env python3
"""
ПРОСТОЕ ДОБАВЛЕНИЕ SFM_ADAPTER_AVAILABLE
"""

import paramiko

def run_command(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8').strip()

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    print('🔧 ДОБАВЛЕНИЕ SFM_ADAPTER_AVAILABLE')

    # Добавляем переменную перед глобальным инстансом
    add_cmd = 'cd /opt/aladdin-backend && sed -i "/# Global instance/i\\\\n# Global adapter availability flag for API Gateway\\nSFM_ADAPTER_AVAILABLE = True\\n" sfm_adapter.py'
    run_command(ssh, add_cmd)

    # Проверяем добавление
    print('✅ ПРОВЕРКА ДОБАВЛЕНИЯ:')
    check = run_command(ssh, 'cd /opt/aladdin-backend && grep -A 3 -B 1 "SFM_ADAPTER_AVAILABLE" sfm_adapter.py')
    print(check)

    # Тестируем импорт
    print('\\n🧪 ТЕСТ ИМПОРТА:')
    test_cmd = '''cd /opt/aladdin-backend && python3 -c "
try:
    from sfm_adapter import SFM_ADAPTER_AVAILABLE
    print(f'✅ SFM_ADAPTER_AVAILABLE = {SFM_ADAPTER_AVAILABLE}')
except ImportError as e:
    print(f'❌ {e}')
"'''
    test_result = run_command(ssh, test_cmd)
    print(test_result)

    # Перезапускаем API Gateway
    if '✅ SFM_ADAPTER_AVAILABLE' in test_result:
        print('\\n🔄 ПЕРЕЗАПУСК API GATEWAY:')
        run_command(ssh, 'systemctl restart aladdin-main-api-gateway')
        print('✅ API Gateway перезапущен')

        # Тестируем
        print('\\n🧪 ТЕСТ ПОСЛЕ ПЕРЕЗАПУСКА:')
        import time
        time.sleep(3)
        health = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/health')
        print('Health:', health)

    ssh.close()

if __name__ == '__main__':
    main()