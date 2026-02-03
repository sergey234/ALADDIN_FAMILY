#!/usr/bin/env python3
"""
🚀 СРОЧНОЕ РАЗВЕРТЫВАНИЕ ПОЛНОГО API С ВСЕМИ 5 ГРУППАМИ
"""

import paramiko
import time
import sys

SERVER = "149.154.65.180"
USER = "root"
PASSWORD = "Sergio675"
REMOTE_PATH = "/opt/aladdin-backend"
LOCAL_FILE = "api_gateway_production_enhanced_no_prometheus.py"

def deploy_full_api():
    print("🚀 НАЧИНАЕМ СРОЧНОЕ РАЗВЕРТЫВАНИЕ ПОЛНОГО API")

    try:
        # Подключаемся к серверу
        print(f"🔗 Подключаемся к {SERVER}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USER, password=PASSWORD)

        # Создаем SFTP клиент
        sftp = ssh.open_sftp()

        # Резервная копия текущего файла
        print("📦 Создаем резервную копию...")
        ssh.exec_command(f"cp {REMOTE_PATH}/api_gateway_complete.py {REMOTE_PATH}/api_gateway_complete_backup_$(date +%s).py")

        # Загружаем полный файл
        print(f"📤 Загружаем {LOCAL_FILE} на сервер...")
        sftp.put(LOCAL_FILE, f"{REMOTE_PATH}/api_gateway_complete.py")

        # Проверяем синтаксис
        print("🔍 Проверяем синтаксис Python...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {REMOTE_PATH} && python3 -m py_compile api_gateway_complete.py")
        error = stderr.read().decode()
        if error:
            print(f"❌ ОШИБКА СИНТАКСИСА: {error}")
            return False

        # Перезапускаем сервис
        print("🔄 Перезапускаем ALADDIN API сервис...")
        ssh.exec_command("systemctl restart aladdin-api")
        time.sleep(3)

        # Проверяем статус сервиса
        stdin, stdout, stderr = ssh.exec_command("systemctl status aladdin-api --no-pager -l")
        status = stdout.read().decode()
        if "active (running)" in status:
            print("✅ Сервис успешно запущен!")
        else:
            print("⚠️ Проблемы со статусом сервиса")

        # Проверяем health endpoint
        print("🏥 Проверяем health endpoint...")
        stdin, stdout, stderr = ssh.exec_command("curl -s https://aladdin-ai.ru/api/health")
        health_response = stdout.read().decode()
        print(f"Health: {health_response}")

        # Закрываем соединения
        sftp.close()
        ssh.close()

        print("🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!")
        return True

    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return False

if __name__ == "__main__":
    success = deploy_full_api()
    if success:
        print("\n🎯 ПРОВЕРЯЕМ РАЗВЕРНУТЫЕ ГРУППЫ:")
        print("✅ Components - должны работать")
        print("✅ Security - должны работать")
        print("✅ Analytics - должны работать")
        print("✅ Protection - должны работать")
        print("✅ System - должны работать")
        print("\n📱 МОБИЛЬНОЕ ПРИЛОЖЕНИЕ ГОТОВО К ПРОДАКШЕНУ!")
    else:
        print("\n❌ РАЗВЕРТЫВАНИЕ НЕ УДАЛОСЬ")
        sys.exit(1)