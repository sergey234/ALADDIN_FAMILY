#!/usr/bin/env python3
"""
АНАЛИЗ ПОРТОВ И СЕРВИСОВ НА СЕРВЕРЕ
"""

import paramiko

def main():
    print('🔍 АНАЛИЗ ПОРТОВ И СЕРВИСОВ НА СЕРВЕРЕ')
    print('=' * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    try:
        # 1. Занятые порты
        print('1️⃣ ЗАНЯТЫЕ ПОРТЫ:')
        stdin, stdout, stderr = ssh.exec_command('netstat -tlnp 2>/dev/null | grep LISTEN | head -10 || ss -tlnp | head -10')
        ports = stdout.read().decode('utf-8').strip()
        print(ports)

        # 2. Статус сервисов
        print('\n2️⃣ СТАТУС СЕРВИСОВ:')
        services = ['aladdin-main-api-gateway', 'aladdin-sfm-core']
        for service in services:
            stdin, stdout, stderr = ssh.exec_command(f'systemctl status {service} --no-pager 2>/dev/null | head -2 || echo "{service}: НЕ НАЙДЕН"')
            status = stdout.read().decode('utf-8').strip()
            print(f'{service}: {status}')

        # 3. Анализ портов 8002 и 8003
        print('\n3️⃣ АНАЛИЗ ПОРТОВ 8002 и 8003:')
        for port in ['8002', '8003']:
            stdin, stdout, stderr = ssh.exec_command(f'lsof -i :{port} 2>/dev/null || echo "Порт {port}: СВОБОДЕН"')
            port_info = stdout.read().decode('utf-8').strip()
            print(f'Порт {port}:')
            print(f'  {port_info}')

        # 4. Конфигурация API Gateway
        print('\n4️⃣ КОНФИГУРАЦИЯ API GATEWAY:')
        stdin, stdout, stderr = ssh.exec_command('cat /etc/systemd/system/aladdin-main-api-gateway.service 2>/dev/null || echo "КОНФИГУРАЦИЯ НЕ НАЙДЕНА"')
        api_config = stdout.read().decode('utf-8').strip()
        print(api_config)

    finally:
        ssh.close()

if __name__ == '__main__':
    main()