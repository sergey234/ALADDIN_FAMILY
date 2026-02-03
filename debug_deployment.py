#!/usr/bin/env python3
"""
ОТЛАДКА РАЗВЕРТЫВАНИЯ ALADDIN
Проверка логов и исправление проблем
"""

import paramiko
import time

# Серверные настройки
SERVER_CONFIG = {
    'hostname': '149.154.65.180',
    'username': 'root',
    'password': 'Sergio675',
    'port': 22
}

def execute_command(ssh_client, command, description):
    """Выполнить команду на сервере"""
    print(f"\n🔧 {description}")
    print(f"Команда: {command}")

    try:
        stdin, stdout, stderr = ssh_client.exec_command(command, timeout=30)

        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()

        exit_code = stdout.channel.recv_exit_status()

        if exit_code == 0:
            print(f"✅ УСПЕХ: {description}")
            if output:
                print(f"Вывод:\n{output}")
            return True, output
        else:
            print(f"❌ ОШИБКА (код {exit_code}): {description}")
            if error:
                print(f"Ошибка:\n{error}")
            return False, error

    except Exception as e:
        print(f"💥 ИСКЛЮЧЕНИЕ: {description} - {e}")
        return False, str(e)

def main():
    """Отладка развертывания"""
    print("🔍 ОТЛАДКА РАЗВЕРТЫВАНИЯ ALADDIN")
    print("=" * 50)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(**SERVER_CONFIG)
        print("✅ ПОДКЛЮЧЕНИЕ К СЕРВЕРУ УСТАНОВЛЕНО")
    except Exception as e:
        print(f"❌ ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")
        return

    try:
        # 1. Проверить статус сервисов
        print("\n📊 ПРОВЕРКА СТАТУСА СЕРВИСОВ")
        execute_command(ssh, "systemctl status aladdin-sfm-core --no-pager", "Статус SFM HTTP API сервиса")
        execute_command(ssh, "systemctl status aladdin-main-api-gateway --no-pager", "Статус API Gateway")

        # 2. Проверить логи SFM сервиса
        print("\n📋 ЛОГИ SFM HTTP API СЕРВИСА")
        execute_command(ssh, "journalctl -u aladdin-sfm-core -n 20", "Последние 20 строк логов SFM")

        # 3. Проверить логи API Gateway
        print("\n📋 ЛОГИ API GATEWAY")
        execute_command(ssh, "journalctl -u aladdin-main-api-gateway -n 20", "Последние 20 строк логов API Gateway")

        # 4. Проверить, запущен ли SFM HTTP API
        print("\n🔍 ПРОВЕРКА ПРОЦЕССОВ")
        execute_command(ssh, "ps aux | grep start_sfm_core_http", "Поиск процесса SFM HTTP API")
        execute_command(ssh, "netstat -tlnp | grep :8003", "Проверка порта 8003")

        # 5. Проверить файлы
        print("\n📁 ПРОВЕРКА ФАЙЛОВ")
        execute_command(ssh, "ls -la /opt/aladdin-backend/start_sfm_core_http.py", "Проверка SFM HTTP API файла")
        execute_command(ssh, "ls -la /opt/aladdin-backend/sfm_adapter.py", "Проверка SFM адаптера")

        # 6. Попытаться запустить SFM вручную
        print("\n🧪 РУЧНОЙ ЗАПУСК SFM HTTP API")
        execute_command(ssh, "cd /opt/aladdin-backend && /opt/aladdin-backend/venvs/main_env/bin/python3 start_sfm_core_http.py", "Ручной запуск SFM HTTP API")

        # 7. Тестирование после ручного запуска
        print("\n🧪 ТЕСТИРОВАНИЕ ПОСЛЕ РУЧНОГО ЗАПУСКА")
        time.sleep(5)
        execute_command(ssh, "curl -s http://127.0.0.1:8003/api/health", "Тест health check SFM HTTP API")
        execute_command(ssh, 'curl -X POST http://127.0.0.1:8003/api/execute -H "Content-Type: application/json" -d \'{"function": "get_phishing_sensitivity", "params": {}}\'', "Тест выполнения функции")

        # 8. Проверка Python зависимостей
        print("\n🐍 ПРОВЕРКА PYTHON ЗАВИСИМОСТЕЙ")
        execute_command(ssh, "cd /opt/aladdin-backend && source venvs/main_env/bin/activate && python3 -c 'import aiohttp; print(\"aiohttp OK\")' && deactivate", "Проверка aiohttp")

        # 9. Проверка импортов в SFM HTTP API
        print("\n🔍 ПРОВЕРКА ИМПОРТОВ SFM HTTP API")
        execute_command(ssh, "cd /opt/aladdin-backend && source venvs/main_env/bin/activate && python3 -c 'from security.safe_function_manager import SafeFunctionManager; sfm = SafeFunctionManager(); print(f\"SFM OK: {len(sfm.functions)} functions\")' && deactivate", "Тест импорта SFM")

        # 10. Проверка синтаксиса файлов
        print("\n📝 ПРОВЕРКА СИНТАКСИСА")
        execute_command(ssh, "cd /opt/aladdin-backend && source venvs/main_env/bin/activate && python3 -m py_compile start_sfm_core_http.py && echo 'SFM HTTP API синтаксис OK' && deactivate", "Проверка синтаксиса SFM HTTP API")
        execute_command(ssh, "cd /opt/aladdin-backend && source venvs/main_env/bin/activate && python3 -m py_compile sfm_adapter.py && echo 'SFM адаптер синтаксис OK' && deactivate", "Проверка синтаксиса SFM адаптера")

    finally:
        ssh.close()
        print("\n🔌 СОЕДИНЕНИЕ ЗАКРЫТО")

if __name__ == "__main__":
    main()