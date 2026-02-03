#!/usr/bin/env python3
"""
🔄 СИНХРОНИЗАЦИЯ ФАЙЛА С СЕРВЕРОМ
Просто загружает текущий api_gateway_server_current.py на сервер
"""

import paramiko
import time
import base64

def sync_file():
    """Синхронизирует файл с сервером"""

    print("🔄 СИНХРОНИЗАЦИЯ API GATEWAY С СЕРВЕРОМ")
    print("=" * 45)

    # Параметры сервера
    hostname = '149.154.65.180'
    username = 'root'
    password = 'Sergio675'

    try:
        # Подключаемся к серверу
        print("📡 Подключение к серверу...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, username=username, password=password, timeout=10)
        print("✅ Подключение успешно!")

        # Создание backup
        print("\n📦 Создание backup...")
        backup_cmd = "cd /opt/aladdin-backend && cp api_gateway.py api_gateway_backup_sync_$(date +%Y%m%d_%H%M%S).py"
        stdin, stdout, stderr = ssh.exec_command(backup_cmd)
        error = stderr.read().decode('utf-8').strip()
        if error:
            print(f"⚠️  Предупреждение backup: {error}")
        else:
            print("✅ Backup создан")

        # Загрузка файла
        print("\n📤 Загрузка файла...")
        with open('api_gateway_server_current.py', 'rb') as f:
            content = f.read()

        content_b64 = base64.b64encode(content).decode('utf-8')
        upload_cmd = f"echo '{content_b64}' | base64 -d > /opt/aladdin-backend/api_gateway.py && chmod 644 /opt/aladdin-backend/api_gateway.py"

        stdin, stdout, stderr = ssh.exec_command(upload_cmd)
        error = stderr.read().decode('utf-8').strip()
        if error:
            print(f"❌ Ошибка загрузки: {error}")
            return False
        else:
            print("✅ Файл загружен")

        # Перезапуск сервиса
        print("\n🔄 Перезапуск API Gateway...")
        restart_cmd = "systemctl restart aladdin-main-api-gateway"
        stdin, stdout, stderr = ssh.exec_command(restart_cmd)

        time.sleep(3)

        # Проверка статуса
        status_cmd = "systemctl status aladdin-main-api-gateway | head -3"
        stdin, stdout, stderr = ssh.exec_command(status_cmd)
        status_output = stdout.read().decode('utf-8').strip()
        print(f"📊 Статус сервиса:\n{status_output}")

        ssh.close()
        print("\n🔌 Соединение закрыто")
        print("\n🎉 СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА!")

        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    if sync_file():
        print("✅ Файл синхронизирован с сервером")
    else:
        print("❌ Ошибка синхронизации")
        exit(1)