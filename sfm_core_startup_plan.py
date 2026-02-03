#!/usr/bin/env python3
"""
ПЛАН ЗАПУСКА НАСТОЯЩЕГО SFM CORE
Переход от mock данных к реальным SFM данным
"""

import paramiko
import time

def run_command(ssh, cmd, description=""):
    """Выполнить команду с выводом"""
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
    print('🚀 ПЛАН ЗАПУСКА НАСТОЯЩЕГО SFM CORE')
    print('=' * 60)
    print('Цель: Получить "source": "real_sfm" вместо "source": "sfm_mock"')
    print('=' * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('149.154.65.180', username='root', password='Sergio675')

    # ШАГ 1: Анализ текущего состояния
    print('\n1️⃣ ТЕКУЩЕЕ СОСТОЯНИЕ:')
    stdout, stderr = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/health | jq .sfm_adapter')
    print(f'Текущий SFM статус: {stdout.strip()}')

    # ШАГ 2: Установка зависимостей
    print('\n2️⃣ УСТАНОВКА ЗАВИСИМОСТЕЙ:')
    run_command(ssh, 'cd /opt/aladdin-backend && pip install aiofiles', 'Установка aiofiles (нужен для SFM Core)')

    # ШАГ 3: Проверка импорта SFM
    print('\n3️⃣ ПРОВЕРКА ИМПОРТА SFM КОМПОНЕНТОВ:')
    test_imports = '''
echo "=== ПРОВЕРКА SFM SINGLETON ==="
python3 -c "
try:
    from security.sfm_singleton import SFMManager
    print('✅ SFMManager импортируется')
    sfm = SFMManager()
    print('✅ SFMManager инициализирован')
    print(f'✅ Функций в SFM: {len(sfm.functions) if hasattr(sfm, \"functions\") else \"неизвестно\"}')
except Exception as e:
    print(f'❌ Ошибка: {e}')
"

echo "=== ПРОВЕРКА SFM CORE ==="
python3 -c "
try:
    from security.core.sfm_core import SFMCore
    print('✅ SFMCore импортируется')
    core = SFMCore()
    print('✅ SFMCore инициализирован')
except Exception as e:
    print(f'❌ SFMCore не найден: {e}')
"
'''
    run_command(ssh, f'cd /opt/aladdin-backend && {test_imports}')

    # ШАГ 4: Создание SFM Core сервиса
    print('\n4️⃣ СОЗДАНИЕ SFM CORE СЕРВИСА:')

    service_content = '''[Unit]
Description=ALADDIN SFM Core Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/aladdin-backend
Environment=PYTHONPATH=/opt/aladdin-backend
ExecStart=/usr/bin/python3 -c "
from security.sfm_singleton import SFMManager
import time
print('Starting ALADDIN SFM Core...')
sfm = SFMManager()
print(f'SFM Core loaded with {len(sfm.functions)} functions')
print('SFM Core is running...')
while True:
    time.sleep(10)
    print(f'SFM Core alive at {time.time()}')
"
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
'''

    # Создаем systemd сервис файл
    run_command(ssh, f'cat > /etc/systemd/system/aladdin-sfm-core.service << \'EOF\'\n{service_content}\nEOF', 'Создание systemd сервиса для SFM Core')

    # Перезагрузка systemd
    run_command(ssh, 'systemctl daemon-reload', 'Перезагрузка systemd конфигурации')

    # ШАГ 5: Запуск SFM Core
    print('\n5️⃣ ЗАПУСК SFM CORE:')
    run_command(ssh, 'systemctl enable aladdin-sfm-core', 'Включение автозапуска SFM Core')
    run_command(ssh, 'systemctl start aladdin-sfm-core', 'Запуск SFM Core сервиса')

    # Ждем запуска
    print('⏳ Ожидание запуска SFM Core...')
    time.sleep(5)

    # ШАГ 6: Проверка статуса
    print('\n6️⃣ ПРОВЕРКА СТАТУСА SFM CORE:')
    run_command(ssh, 'systemctl status aladdin-sfm-core --no-pager -l', 'Статус SFM Core сервиса')
    run_command(ssh, 'ps aux | grep python | grep -i sfm | grep -v grep', 'Проверка процессов SFM')

    # ШАГ 7: Проверка API после запуска
    print('\n7️⃣ ПРОВЕРКА API ПОСЛЕ ЗАПУСКА SFM CORE:')
    time.sleep(3)  # Ждем полной инициализации

    stdout, stderr = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/health')
    if stdout:
        try:
            import json
            health = json.loads(stdout)
            sfm_status = health.get('sfm_adapter', 'unknown')
            print(f'Новый SFM статус: {sfm_status}')

            if sfm_status == 'real':
                print('🎉 SFM CORE УСПЕШНО ЗАПУЩЕН!')
                print('✅ Теперь все API будут возвращать real_sfm данные')
            elif sfm_status == 'fallback':
                print('⚠️ SFM Core не запустился, система в fallback режиме')
            else:
                print(f'❓ Неизвестный статус SFM: {sfm_status}')
        except:
            print('❌ Ошибка парсинга health ответа')

    # ШАГ 8: Тест функций с real данными
    print('\n8️⃣ ТЕСТ ФУНКЦИЙ С REAL ДАННЫМИ:')
    stdout, stderr = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/phishing/sensitivity | jq .source')
    if stdout and '"real_sfm"' in stdout:
        print('🎉 УСПЕХ! Функции возвращают real_sfm данные!')
        print('✅ Система полностью готова к продакшену!')
    else:
        print(f'⚠️ Все еще mock данные: {stdout.strip()}')

    print('\n' + '=' * 60)
    print('🎯 РЕЗУЛЬТАТ ЗАПУСКА SFM CORE:')
    print('Если все прошло успешно:')
    print('• systemctl status aladdin-sfm-core покажет "active"')
    print('• API health покажет "sfm_adapter": "real"')
    print('• Все функции вернут "source": "real_sfm"')
    print('')
    print('Если проблемы:')
    print('• Проверить логи: journalctl -u aladdin-sfm-core')
    print('• Проверить зависимости: pip install aiofiles')
    print('• Проверить SFM файлы в security/')

    ssh.close()

if __name__ == '__main__':
    main()