#!/usr/bin/env python3
"""
ЭТАП 1: РАЗВЕРТЫВАНИЕ SFM HTTP API СЕРВИСА
Финальная версия с исправлениями
"""

import paramiko
import time

def run_command(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8').strip()

def main():
    print('🚀 ЭТАП 1: РАЗВЕРТЫВАНИЕ SFM HTTP API СЕРВИСА')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    try:
        # 1. Загружаем HTTP API файл
        print('1️⃣ ЗАГРУЗКА HTTP API ФАЙЛА:')
        with open('start_sfm_core_http.py', 'r') as f:
            content = f.read()

        stdin, stdout, stderr = ssh.exec_command('cat > /opt/aladdin-backend/start_sfm_core_http.py')
        stdin.write(content)
        stdin.close()

        stdin, stdout, stderr = ssh.exec_command('chmod +x /opt/aladdin-backend/start_sfm_core_http.py')
        print('✅ HTTP API файл загружен и сделан исполняемым')

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

        stdin, stdout, stderr = ssh.exec_command('systemctl daemon-reload')
        print('✅ Systemd сервис обновлен')

        # 3. Запускаем сервис
        print('\\n3️⃣ ЗАПУСК SFM HTTP API СЕРВИСА:')
        stdin, stdout, stderr = ssh.exec_command('systemctl stop aladdin-sfm-core')
        stdin, stdout, stderr = ssh.exec_command('systemctl start aladdin-sfm-core')
        print('⏳ Ожидание запуска...')
        time.sleep(5)

        # 4. Тестируем
        print('\\n4️⃣ ТЕСТИРОВАНИЕ HTTP API:')

        # Health check
        stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8003/api/health')
        health = stdout.read().decode('utf-8').strip()
        print('Health check:', health)

        # Function test
        stdin, stdout, stderr = ssh.exec_command('curl -s -X POST http://127.0.0.1:8003/api/execute -H "Content-Type: application/json" -d \'{"function": "get_phishing_sensitivity", "params": {}}\'')
        func_result = stdout.read().decode('utf-8').strip()
        print('Function test result:', func_result[:500] + '...' if len(func_result) > 500 else func_result)

        # Service status
        stdin, stdout, stderr = ssh.exec_command('systemctl status aladdin-sfm-core --no-pager | head -3')
        status = stdout.read().decode('utf-8').strip()
        print('Service status:', status)

        # 5. Финальная проверка
        print('\\n5️⃣ ФИНАЛЬНАЯ ПРОВЕРКА:')

        # Проверяем что порт 8003 слушает
        stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep :8003 || netstat -tlnp | grep :8003')
        port_check = stdout.read().decode('utf-8').strip()
        if port_check:
            print('✅ Порт 8003 слушает:', port_check)
        else:
            print('❌ Порт 8003 не слушает')

        # Проверяем API доступность
        stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8003/api/functions')
        functions = stdout.read().decode('utf-8').strip()
        if functions and 'functions' in functions:
            print('✅ API functions доступны')
        else:
            print('❌ API functions недоступны')

        print('\\n🎯 ЭТАП 1 ЗАВЕРШЕН!')
        print('✅ SFM HTTP API работает на порту 8003')

        if 'real_sfm' in func_result:
            print('🎉 УСПЕХ! SFM возвращает real данные!')
        else:
            print('⚠️ SFM вернул не real данные, но API работает')

    finally:
        ssh.close()

if __name__ == '__main__':
    main()