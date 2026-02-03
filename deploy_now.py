#!/usr/bin/env python3
"""
ЭТАП 1: РАЗВЕРТЫВАНИЕ SFM HTTP API СЕРВИСА - СЕЙЧАС!
"""

import paramiko
import time

def main():
    print('🚀 ЭТАП 1: РАЗВЕРТЫВАНИЕ SFM HTTP API СЕРВИСА')
    print('Подключаемся к серверу 149.154.65.180 с паролем Sergio675...')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')
    print('✅ Подключение успешно!')

    try:
        # 1. Загружаем HTTP API файл
        print('\n1️⃣ ЗАГРУЗКА HTTP API ФАЙЛА:')
        with open('start_sfm_core_http.py', 'r') as f:
            content = f.read()

        stdin, stdout, stderr = ssh.exec_command('cat > /opt/aladdin-backend/start_sfm_core_http.py')
        stdin.write(content)
        stdin.close()

        stdin, stdout, stderr = ssh.exec_command('chmod +x /opt/aladdin-backend/start_sfm_core_http.py')
        print('✅ HTTP API файл загружен и сделан исполняемым')

        # 2. Обновляем systemd сервис
        print('\n2️⃣ ОБНОВЛЕНИЕ SYSTEMD СЕРВИСА:')
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
        print('\n3️⃣ ЗАПУСК SFM HTTP API СЕРВИСА:')
        stdin, stdout, stderr = ssh.exec_command('systemctl stop aladdin-sfm-core')
        stdin, stdout, stderr = ssh.exec_command('systemctl start aladdin-sfm-core')
        print('⏳ Ожидание запуска...')
        time.sleep(5)

        # 4. Тестируем
        print('\n4️⃣ ТЕСТИРОВАНИЕ HTTP API:')

        # Health check
        stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8003/api/health')
        health = stdout.read().decode('utf-8').strip()
        print('Health check:', health)

        # Function test
        stdin, stdout, stderr = ssh.exec_command('curl -s -X POST http://127.0.0.1:8003/api/execute -H "Content-Type: application/json" -d \'{"function": "get_phishing_sensitivity", "params": {}}\'')
        func_result = stdout.read().decode('utf-8').strip()
        print('Function test result:', func_result[:300] + '...' if len(func_result) > 300 else func_result)

        # Service status
        stdin, stdout, stderr = ssh.exec_command('systemctl status aladdin-sfm-core --no-pager | head -3')
        status = stdout.read().decode('utf-8').strip()
        print('Service status:', status)

        # 5. Финальная проверка
        print('\n5️⃣ ФИНАЛЬНАЯ ПРОВЕРКА:')

        # Проверяем что порт 8003 слушает
        stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep :8003 || netstat -tlnp | grep :8003 || echo "Порт не найден"')
        port_check = stdout.read().decode('utf-8').strip()
        if '8003' in port_check:
            print('✅ Порт 8003 слушает')
        else:
            print('❌ Порт 8003 не слушает')

        # Проверяем API доступность
        stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8003/api/functions | head -c 100')
        functions = stdout.read().decode('utf-8').strip()
        if functions and ('functions' in functions or '[' in functions):
            print('✅ API functions доступны')
        else:
            print('❌ API functions недоступны')

        print('\n🎯 ЭТАП 1 ЗАВЕРШЕН!')

        if 'real_sfm' in func_result:
            print('🎉 УСПЕХ! SFM возвращает real данные!')
            print('✅ ГОТОВЫ К ЭТАПУ 2!')
        elif 'success' in func_result and 'result' in func_result:
            print('⚠️ SFM API работает, но данные не real_sfm')
            print('✅ Можно переходить к Этапу 2 для исправления')
        else:
            print('❌ SFM API не работает корректно')

    except Exception as e:
        print(f'❌ ОШИБКА: {e}')
        import traceback
        traceback.print_exc()

    finally:
        ssh.close()
        print('🔌 Подключение к серверу закрыто')

if __name__ == '__main__':
    main()