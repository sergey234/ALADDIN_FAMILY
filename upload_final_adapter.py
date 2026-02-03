#!/usr/bin/env python3
"""
ЗАГРУЗКА ФИНАЛЬНОЙ ВЕРСИИ SFM АДАПТЕРА
"""

import paramiko
from scp import SCPClient
import time

def main():
    print("🔄 ЗАГРУЗКА ФИНАЛЬНОЙ ВЕРСИИ SFM АДАПТЕРА")
    print("=" * 50)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect('149.154.65.180', username='root', password='Sergio675')
        print("✅ Подключено к серверу")

        # Загрузка файла
        print("\n📤 Загрузка sfm_adapter_fixed_final.py...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put('sfm_adapter_fixed_final.py', '/opt/aladdin-backend/sfm_adapter.py')
        print("✅ Файл загружен")

        # Перезапуск
        print("\n🔄 Перезапуск API Gateway...")
        stdin, stdout, stderr = ssh.exec_command('systemctl restart aladdin-main-api-gateway')
        stdout.channel.recv_exit_status()
        print("✅ API Gateway перезапущен")

        # Ожидание
        print("\n⏳ Ожидание запуска (5 сек)...")
        time.sleep(5)

        # Проверка
        print("\n🩺 Проверка результата...")
        stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8002/api/health')
        health = stdout.read().decode().strip()

        if 'available' in health:
            print("✅ SFM адаптер: AVAILABLE")
        else:
            print("❌ SFM адаптер: FALLBACK")

        # Финальный тест
        print("\n🎯 Финальный тест...")
        stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8002/api/phishing/sensitivity')
        result = stdout.read().decode().strip()

        if 'real_sfm' in result:
            print("🎉 УСПЕХ! ALADDIN имеет РЕАЛЬНУЮ ЗАЩИТУ!")
        else:
            print("⚠️ Требуется дополнительная настройка")
            print(f"Результат: {result[:100]}...")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

    finally:
        ssh.close()
        print("\n🔌 Соединение закрыто")

if __name__ == "__main__":
    main()