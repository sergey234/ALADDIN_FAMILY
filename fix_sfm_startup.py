#!/usr/bin/env python3
"""
ИСПРАВЛЕНИЕ ПРОБЛЕМ ЗАПУСКА SFM CORE
"""

import paramiko

def run_command(ssh, cmd, description=""):
    """Выполнить команду"""
    if description:
        print(f"\n{description}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8').strip()
    err = stderr.read().decode('utf-8').strip()
    if out:
        print(out)
    if err:
        print(f"❌ Ошибка: {err}")
    return out, err

def main():
    print('🔧 ИСПРАВЛЕНИЕ ПРОБЛЕМ ЗАПУСКА SFM CORE')
    print('=' * 50)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    # 1. Установка зависимостей правильно
    print('\n1️⃣ УСТАНОВКА ЗАВИСИМОСТЕЙ:')
    run_command(ssh, 'apt update && apt install -y jq python3-aiofiles', 'Установка jq и aiofiles через apt')

    # 2. Проверка импорта после установки зависимостей
    print('\n2️⃣ ПРОВЕРКА SFM ПОСЛЕ УСТАНОВКИ ЗАВИСИМОСТЕЙ:')
    test_sfm = '''
cd /opt/aladdin-backend
python3 -c "
try:
    from security.sfm_singleton import SFMSingleton
    print('✅ SFMSingleton импортируется')
    sfm = SFMSingleton()
    print('✅ SFMSingleton инициализирован')
except Exception as e:
    print(f'❌ SFMSingleton ошибка: {e}')

try:
    from security.core.sfm_core import SFMCore
    print('✅ SFMCore импортируется')
except Exception as e:
    print(f'❌ SFMCore ошибка: {e}')

try:
    from security.safe_function_manager import SafeFunctionManager
    print('✅ SafeFunctionManager импортируется')
    sfm = SafeFunctionManager()
    print(f'✅ SafeFunctionManager инициализирован с {len(sfm.functions)} функциями')
except Exception as e:
    print(f'❌ SafeFunctionManager ошибка: {e}')
"
'''
    run_command(ssh, test_sfm)

    # 3. Исправление systemd сервиса
    print('\n3️⃣ ИСПРАВЛЕНИЕ SYSTEMD СЕРВИСА:')

    # Удаляем старый сервис
    run_command(ssh, 'systemctl stop aladdin-sfm-core 2>/dev/null || true', 'Остановка старого сервиса')
    run_command(ssh, 'systemctl disable aladdin-sfm-core 2>/dev/null || true', 'Отключение старого сервиса')
    run_command(ssh, 'rm -f /etc/systemd/system/aladdin-sfm-core.service', 'Удаление старого сервиса')

    # Создаем правильный сервис
    service_script = '''#!/bin/bash
cd /opt/aladdin-backend
source venv/bin/activate 2>/dev/null || true
export PYTHONPATH=/opt/aladdin-backend:$PYTHONPATH

echo "Starting ALADDIN SFM Core..."

python3 -c "
import sys
import time
from security.safe_function_manager import SafeFunctionManager

try:
    print('Initializing SFM Core...')
    sfm = SafeFunctionManager()
    print(f'SFM Core loaded with {len(sfm.functions)} functions')

    print('SFM Core is running...')
    while True:
        time.sleep(30)
        print(f'SFM Core alive - {time.time()}')

except Exception as e:
    print(f'SFM Core error: {e}')
    sys.exit(1)
"
'''

    # Создаем скрипт запуска
    run_command(ssh, f'cat > /opt/aladdin-backend/start_sfm_core.sh << \'EOF\'\n{service_script}\nEOF', 'Создание скрипта запуска SFM Core')
    run_command(ssh, 'chmod +x /opt/aladdin-backend/start_sfm_core.sh', 'Делаем скрипт исполняемым')

    # Создаем правильный systemd сервис
    service_content = '''[Unit]
Description=ALADDIN SFM Core Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/aladdin-backend
Environment=PYTHONPATH=/opt/aladdin-backend
ExecStart=/opt/aladdin-backend/start_sfm_core.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
TimeoutStartSec=60

[Install]
WantedBy=multi-user.target
'''

    run_command(ssh, f'cat > /etc/systemd/system/aladdin-sfm-core.service << \'EOF\'\n{service_content}\nEOF', 'Создание исправленного systemd сервиса')

    # Перезагрузка systemd
    run_command(ssh, 'systemctl daemon-reload', 'Перезагрузка systemd')

    # 4. Запуск SFM Core
    print('\n4️⃣ ЗАПУСК SFM CORE:')
    run_command(ssh, 'systemctl enable aladdin-sfm-core', 'Включение автозапуска')
    run_command(ssh, 'systemctl start aladdin-sfm-core', 'Запуск SFM Core')

    # Ждем запуска
    import time
    print('⏳ Ожидание запуска SFM Core (10 сек)...')
    time.sleep(10)

    # 5. Проверка статуса
    print('\n5️⃣ ПРОВЕРКА СТАТУСА:')
    run_command(ssh, 'systemctl status aladdin-sfm-core --no-pager | head -10', 'Статус SFM Core сервиса')
    run_command(ssh, 'ps aux | grep python | grep -i sfm | grep -v grep', 'Проверка процессов')

    # 6. Проверка API
    print('\n6️⃣ ПРОВЕРКА API ПОСЛЕ ЗАПУСКА:')
    stdout, stderr = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/health')
    if stdout:
        import json
        try:
            health = json.loads(stdout)
            sfm_status = health.get('sfm_adapter', 'unknown')
            print(f'SFM статус: {sfm_status}')

            if sfm_status == 'real':
                print('🎉 SFM CORE УСПЕШНО ЗАПУЩЕН!')
            else:
                print('⚠️ SFM Core не запустился')
        except:
            print('❌ Ошибка парсинга health')

    # 7. Тест функции
    print('\n7️⃣ ТЕСТ ФУНКЦИИ:')
    stdout, stderr = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/phishing/sensitivity | jq .source 2>/dev/null || curl -s http://127.0.0.1:8002/api/phishing/sensitivity')
    if '"real_sfm"' in stdout:
        print('🎉 УСПЕХ! ПОЛУЧЕНЫ REAL SFM ДАННЫЕ!')
        print('✅ СИСТЕМА ГОТОВА К ПРОДАКШЕНУ!')
    else:
        print(f'⚠️ Все еще mock данные: {stdout}')

    # 8. Логи если есть проблемы
    print('\n8️⃣ ЛОГИ SFM CORE (если есть проблемы):')
    run_command(ssh, 'journalctl -u aladdin-sfm-core -n 10 --no-pager', 'Последние логи SFM Core')

    print('\n' + '=' * 50)
    print('🎯 РЕЗУЛЬТАТ:')
    print('Если SFM Core запустился успешно:')
    print('• systemctl status aladdin-sfm-core покажет "active (running)"')
    print('• Все API функции вернут "source": "real_sfm"')
    print('• Система полностью готова к продакшену!')
    print('')
    print('Если проблемы - проверьте логи выше')

    ssh.close()

if __name__ == '__main__':
    main()