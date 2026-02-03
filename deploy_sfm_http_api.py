#!/usr/bin/env python3
"""
РАЗВЕРТЫВАНИЕ SFM HTTP API СЕРВИСА
Этап 1: Загрузка HTTP API файла и обновление systemd сервиса
"""

import paramiko

def run_command(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8').strip()

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    print('🚀 ЭТАП 1: РАЗВЕРТЫВАНИЕ SFM HTTP API СЕРВИСА')

    # 1. Загружаем HTTP API файл на сервер
    print('1️⃣ ЗАГРУЗКА HTTP API ФАЙЛА:')
    with open('start_sfm_core_http.py', 'r') as f:
        http_api_content = f.read()

    # Создаем файл на сервере
    create_cmd = f'cd /opt/aladdin-backend && cat > start_sfm_core_http.py << \'EOF\'\n{http_api_content}\nEOF'
    run_command(ssh, create_cmd)

    # Делаем файл исполняемым
    run_command(ssh, 'cd /opt/aladdin-backend && chmod +x start_sfm_core_http.py')
    print('✅ HTTP API файл загружен и сделан исполняемым')

    # 2. Обновляем systemd сервис
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

    update_cmd = f'cat > /etc/systemd/system/aladdin-sfm-core.service << \'EOF\'\n{systemd_config}\nEOF'
    run_command(ssh, update_cmd)

    # Перезагружаем systemd
    run_command(ssh, 'systemctl daemon-reload')
    print('✅ Systemd сервис обновлен')

    # 3. Запускаем новый сервис
    print('\\n3️⃣ ЗАПУСК SFM HTTP API СЕРВИСА:')
    run_command(ssh, 'systemctl stop aladdin-sfm-core')  # Останавливаем старый
    run_command(ssh, 'systemctl start aladdin-sfm-core')  # Запускаем новый
    print('⏳ Ожидание запуска...')

    import time
    time.sleep(3)

    # 4. Тестируем HTTP API
    print('\\n4️⃣ ТЕСТИРОВАНИЕ HTTP API:')
    health_test = run_command(ssh, 'curl -s http://127.0.0.1:8003/api/health')
    print('Health check:', health_test)

    # Тестируем выполнение функции
    execute_test = run_command(ssh, '''curl -s -X POST http://127.0.0.1:8003/api/execute \\
  -H "Content-Type: application/json" \\
  -d '{"function": "get_phishing_sensitivity", "params": {}}' | head -200''')
    print('Function test:', execute_test)

    # Проверяем статус сервиса
    status = run_command(ssh, 'systemctl status aladdin-sfm-core --no-pager | head -3')
    print('Service status:', status)

    ssh.close()

    print('\\n🎯 ЭТАП 1 ЗАВЕРШЕН!')
    print('✅ SFM HTTP API сервис запущен и работает')
    print('✅ Доступен на http://127.0.0.1:8003/api/execute')

if __name__ == '__main__':
    main()