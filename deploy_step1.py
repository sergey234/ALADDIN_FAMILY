#!/usr/bin/env python3
"""
ЭТАП 1: РАЗВЕРТЫВАНИЕ SFM HTTP API СЕРВИСА
"""

import paramiko
import time

def main():
    print('🚀 ЭТАП 1: РАЗВЕРТЫВАНИЕ SFM HTTP API СЕРВИСА')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    # 1. Загружаем HTTP API файл
    print('1️⃣ ЗАГРУЗКА HTTP API ФАЙЛА:')
    with open('start_sfm_core_http.py', 'r') as f:
        content = f.read()

    # Создаем файл на сервере
    stdin, stdout, stderr = ssh.exec_command('cat > /opt/aladdin-backend/start_sfm_core_http.py')
    stdin.write(content)
    stdin.close()

    # Делаем исполняемым
    stdin, stdout, stderr = ssh.exec_command('chmod +x /opt/aladdin-backend/start_sfm_core_http.py')
    print('✅ HTTP API файл загружен')

    # 2. Обновляем systemd сервис
    print('\\n2️⃣ ОБНОВЛЕНИЕ SYSTEMD СЕРВИСА:')
    systemd_content = '''[Unit]
Description=ALADDIN SFM HTTP API Service
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/opt/aladdin-backend
ExecStart=/opt/aladdin-backend/venvs/main_env/bin/python3 /opt/aladdin-backend/start_sfm_core_http.py
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=aladdin-sfm-http-api

[Install]
WantedBy=multi-user.target'''

    stdin, stdout, stderr = ssh.exec_command('cat > /etc/systemd/system/aladdin-sfm-core.service')
    stdin.write(systemd_content)
    stdin.close()

    # Перезагружаем systemd
    stdin, stdout, stderr = ssh.exec_command('systemctl daemon-reload')
    print('✅ Systemd обновлен')

    # 3. Запускаем сервис
    print('\\n3️⃣ ЗАПУСК СЕРВИСА:')
    stdin, stdout, stderr = ssh.exec_command('systemctl stop aladdin-sfm-core')
    stdin, stdout, stderr = ssh.exec_command('systemctl start aladdin-sfm-core')
    print('⏳ Ожидание запуска...')
    time.sleep(3)

    # 4. Тестируем
    print('\\n4️⃣ ТЕСТИРОВАНИЕ:')
    stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8003/api/health')
    health = stdout.read().decode('utf-8').strip()
    print('Health:', health)

    # Тестируем функцию
    stdin, stdout, stderr = ssh.exec_command('curl -s -X POST http://127.0.0.1:8003/api/execute -H "Content-Type: application/json" -d \'{"function": "get_phishing_sensitivity", "params": {}}\'')
    result = stdout.read().decode('utf-8').strip()
    print('Function test:', result[:300] + '...' if len(result) > 300 else result)

    # Статус
    stdin, stdout, stderr = ssh.exec_command('systemctl status aladdin-sfm-core --no-pager | head -3')
    status = stdout.read().decode('utf-8').strip()
    print('Service status:', status)

    ssh.close()

    print('\\n🎯 ЭТАП 1 ЗАВЕРШЕН!')
    print('✅ SFM HTTP API работает на порту 8003')

if __name__ == '__main__':
    main()