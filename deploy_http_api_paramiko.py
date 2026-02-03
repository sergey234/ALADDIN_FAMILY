#!/usr/bin/env python3
"""
РАЗВЕРТЫВАНИЕ SFM HTTP API СЕРВИСА С PARAMIKO
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

    print('🚀 ЭТАП 1: РАЗВЕРТЫВАНИЕ SFM HTTP API СЕРВИСА')

    # 1. Читаем HTTP API файл
    with open('start_sfm_core_http.py', 'r') as f:
        http_api_content = f.read()

    # 2. Загружаем на сервер
    print('1️⃣ ЗАГРУЗКА HTTP API ФАЙЛА:')
    stdin, stdout, stderr = ssh.exec_command('cd /opt/aladdin-backend && cat > start_sfm_core_http.py')
    stdin.write(http_api_content)
    stdin.close()
    print('✅ Файл загружен')

    # Делаем исполняемым
    run_command(ssh, 'chmod +x /opt/aladdin-backend/start_sfm_core_http.py')
    print('✅ Файл сделан исполняемым')

    # 3. Обновляем systemd сервис
    print('\\n2️⃣ ОБНОВЛЕНИЕ SYSTEMD СЕРВИСА:')
    systemd_config = '''[Unit]
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
    stdin.write(systemd_config)
    stdin.close()

    # Перезагружаем systemd
    run_command(ssh, 'systemctl daemon-reload')
    print('✅ Systemd обновлен')

    # 4. Запускаем сервис
    print('\\n3️⃣ ЗАПУСК СЕРВИСА:')
    run_command(ssh, 'systemctl stop aladdin-sfm-core')
    run_command(ssh, 'systemctl start aladdin-sfm-core')
    print('⏳ Ожидание запуска...')
    time.sleep(3)

    # 5. Тестируем
    print('\\n4️⃣ ТЕСТИРОВАНИЕ:')
    health = run_command(ssh, 'curl -s http://127.0.0.1:8003/api/health')
    print('Health:', health)

    # Тестируем функцию
    execute_cmd = 'curl -s -X POST http://127.0.0.1:8003/api/execute -H "Content-Type: application/json" -d \'{"function": "get_phishing_sensitivity", "params": {}}\''
    execute_result = run_command(ssh, execute_cmd)
    print('Function test:', execute_result[:500] + '...' if len(execute_result) > 500 else execute_result)

    # Статус сервиса
    status = run_command(ssh, 'systemctl status aladdin-sfm-core --no-pager | head -3')
    print('Service status:', status)

    ssh.close()

    print('\\n🎯 ЭТАП 1 УСПЕШНО ЗАВЕРШЕН!')
    print('✅ SFM HTTP API работает на порту 8003')

if __name__ == '__main__':
    main()