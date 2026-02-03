#!/usr/bin/env python3
"""
БЫСТРАЯ ЗАГРУЗКА ИСПРАВЛЕННОЙ SFM HTTP API ЧЕРЕЗ PARAMIKO
"""

import paramiko
import time
import os
from scp import SCPClient

# Серверные настройки
SERVER_CONFIG = {
    'hostname': '149.154.65.180',
    'username': 'root',
    'password': 'Sergio675',
    'port': 22
}

def upload_and_restart_sfm():
    """Загрузить исправленную SFM HTTP API и перезапустить"""

    print("🚀 БЫСТРАЯ ЗАГРУЗКА SFM HTTP API")
    print("=" * 40)

    # Подключение
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("🔌 Подключение к серверу...")
        ssh.connect(**SERVER_CONFIG, timeout=10)
        print("✅ Подключено!")

        # 1. Загрузка файла
        print("\n📤 Загрузка start_sfm_core_http_fixed.py...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put('start_sfm_core_http_fixed.py', '/opt/aladdin-backend/start_sfm_core_http.py')
        print("✅ Файл загружен!")

        # 2. Сделать исполняемым
        print("\n🔧 Делаем файл исполняемым...")
        stdin, stdout, stderr = ssh.exec_command('chmod +x /opt/aladdin-backend/start_sfm_core_http.py')
        stdout.channel.recv_exit_status()
        print("✅ Исполняемые права установлены!")

        # 3. Перезапустить сервис
        print("\n🔄 Перезапуск SFM сервиса...")
        stdin, stdout, stderr = ssh.exec_command('systemctl restart aladdin-sfm-core')
        stdout.channel.recv_exit_status()
        print("✅ Сервис перезапущен!")

        # 4. Подождать
        print("\n⏳ Ожидание запуска (5 сек)...")
        time.sleep(5)

        # 5. Проверить здоровье
        print("\n🩺 Проверка здоровья SFM API...")
        stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8003/api/health')
        health = stdout.read().decode().strip()
        print(f"Health check: {health}")

        if 'healthy' in health:
            print("✅ SFM HTTP API работает!")
        else:
            print("❌ SFM HTTP API не отвечает")

        # 6. Тест функции
        print("\n🧪 Тест phishing функции...")
        stdin, stdout, stderr = ssh.exec_command('curl -X POST -s http://127.0.0.1:8003/api/execute -H "Content-Type: application/json" -d \'{"function": "get_phishing_sensitivity", "params": {}}\'')
        result = stdout.read().decode().strip()
        print(f"SFM test result: {result}")

        if 'real_sfm' in result:
            print("✅ SFM возвращает real_sfm данные!")
        else:
            print("❌ SFM не возвращает real_sfm")

        # 7. Тест API Gateway
        print("\n🌐 Тест API Gateway...")
        stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8002/api/health')
        api_health = stdout.read().decode().strip()
        print(f"API Gateway health: {api_health}")

        if 'available' in api_health:
            print("✅ API Gateway видит SFM адаптер!")
        else:
            print("❌ API Gateway не видит SFM адаптер")

        # 8. Финальный тест
        print("\n🎯 Финальный тест через API Gateway...")
        stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8002/api/phishing/sensitivity')
        final_result = stdout.read().decode().strip()
        print(f"Final API test: {final_result[:100]}...")

        if 'real_sfm' in final_result:
            print("\n🎉 УСПЕХ! ALADDIN получил 100% РЕАЛЬНУЮ ЗАЩИТУ!")
            print("🚀 ПРОЕКТ ЗАВЕРШЕН!")
            return True
        else:
            print("\n⚠️ Частичный успех - требуется дополнительная настройка")
            return False

    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return False

    finally:
        ssh.close()
        print("\n🔌 Соединение закрыто")

if __name__ == "__main__":
    success = upload_and_restart_sfm()
    if success:
        print("\n✅ ВСЕ ГОТОВО! ALADDIN с 100% реальной защитой!")
    else:
        print("\n⚠️ Требуется дополнительная настройка")