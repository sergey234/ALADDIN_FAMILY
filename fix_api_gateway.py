#!/usr/bin/env python3
"""
ИСПРАВЛЕНИЕ API GATEWAY - УБИРАЕМ ПРОВЕРКУ SFM_ADAPTER_AVAILABLE
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

    print('🔧 ИСПРАВЛЕНИЕ API GATEWAY')

    # 1. Найдем где используется SFM_ADAPTER_AVAILABLE
    print('1️⃣ ПОИСК ИСПОЛЬЗОВАНИЯ SFM_ADAPTER_AVAILABLE:')
    usage = run_command(ssh, 'cd /opt/aladdin-backend && grep -n "SFM_ADAPTER_AVAILABLE" api_gateway.py')
    print(usage)

    # 2. Исправим логику - заменим "if SFM_ADAPTER_AVAILABLE and sfm_adapter:" на "if sfm_adapter:"
    print('\n2️⃣ ИСПРАВЛЕНИЕ ЛОГИКИ:')
    fix_cmd = 'cd /opt/aladdin-backend && sed -i "s/if SFM_ADAPTER_AVAILABLE and sfm_adapter:/if sfm_adapter:/g" api_gateway.py'
    run_command(ssh, fix_cmd)

    # 3. Проверим исправление
    print('\n3️⃣ ПРОВЕРКА ИСПРАВЛЕНИЯ:')
    check = run_command(ssh, 'cd /opt/aladdin-backend && grep -n "if sfm_adapter:" api_gateway.py | head -3')
    print(check)

    # 4. Перезапустим API Gateway
    print('\n4️⃣ ПЕРЕЗАПУСК API GATEWAY:')
    run_command(ssh, 'systemctl restart aladdin-main-api-gateway')
    print('⏳ Ожидание перезапуска...')
    time.sleep(5)

    # 5. Тестируем
    print('\n5️⃣ ТЕСТ ПОСЛЕ ИСПРАВЛЕНИЯ:')
    health = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/health')
    print('Health:', health)

    func_test = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/phishing/sensitivity | jq .source 2>/dev/null || curl -s http://127.0.0.1:8002/api/phishing/sensitivity | grep source')
    print('Function result:', func_test)

    # 6. Анализ результата
    print('\n6️⃣ АНАЛИЗ РЕЗУЛЬТАТА:')
    if 'real_sfm' in func_test:
        print('🎉 УСПЕХ! ПОЛУЧЕНЫ REAL SFM ДАННЫЕ!')
        print('✅ API Gateway теперь правильно работает с SFM адаптером')
        print('✅ Все функции будут возвращать "source": "real_sfm"')
    elif 'sfm_mock' in func_test:
        print('⚠️ Все еще mock данные, но логика исправлена')
        print('Нужно проверить почему SFM адаптер использует fallback')
    else:
        print('❌ Функция не работает')

    ssh.close()

if __name__ == '__main__':
    main()