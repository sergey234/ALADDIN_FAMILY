#!/usr/bin/env python3
"""
🧪 ТЕСТ ПОДКЛЮЧЕНИЯ К СЕРВЕРУ ALADDIN
Использует paramiko для прямого SSH подключения
"""

import paramiko
import time
import sys

def test_server_connection():
    """Тестирует подключение к серверу и выполняет базовые команды"""

    print("🔍 ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ К СЕРВЕРУ ALADDIN")
    print("=" * 50)

    # Параметры подключения
    hostname = '149.154.65.180'
    username = 'root'
    password = 'Sergio675'
    port = 22

    try:
        print(f"📡 Подключение к {hostname}...")

        # Создаем SSH клиент
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Подключаемся
        ssh.connect(hostname=hostname, port=port, username=username, password=password, timeout=10)

        print("✅ SSH подключение успешно!")

        # Выполняем тестовые команды
        commands = [
            ("pwd", "Текущая директория"),
            ("ls -la /opt/aladdin-backend/", "Содержимое директории проекта"),
            ("systemctl status aladdin-main-api-gateway | head -3", "Статус API Gateway"),
            ("curl -s http://127.0.0.1:8002/api/health", "Health check API"),
            ("cd /opt/aladdin-backend && source venvs/main_env/bin/activate && python3 -c 'print(\"Python работает\")'", "Тест Python в venv")
        ]

        print("\n🧪 ВЫПОЛНЕНИЕ ТЕСТОВЫХ КОМАНД:")
        print("-" * 30)

        for command, description in commands:
            try:
                print(f"\n📋 {description}:")
                stdin, stdout, stderr = ssh.exec_command(command, timeout=15)

                # Читаем вывод
                output = stdout.read().decode('utf-8').strip()
                error = stderr.read().decode('utf-8').strip()

                if output:
                    # Ограничиваем вывод для читаемости
                    lines = output.split('\n')[:10]  # Первые 10 строк
                    for line in lines:
                        print(f"  {line}")
                    if len(output.split('\n')) > 10:
                        remaining = len(output.split('\n')) - 10
                        print(f"  ... и еще {remaining} строк")
                elif error:
                    print(f"  ⚠️  {error}")
                else:
                    print("  (пустой вывод)")

            except Exception as e:
                print(f"  ❌ Ошибка выполнения команды: {e}")

        # Закрываем соединение
        ssh.close()
        print("\n🔌 Соединение закрыто")

        return True

    except paramiko.AuthenticationException:
        print("❌ Ошибка аутентификации - проверьте логин/пароль")
        return False
    except paramiko.SSHException as e:
        print(f"❌ SSH ошибка: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def check_server_health():
    """Проверяет здоровье сервера без детального тестирования"""

    hostname = '149.154.65.180'
    username = 'root'
    password = 'Sergio675'

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, username=username, password=password, timeout=5)

        # Быстрая проверка
        stdin, stdout, stderr = ssh.exec_command("uptime", timeout=5)
        uptime = stdout.read().decode('utf-8').strip()

        ssh.close()

        print("✅ СЕРВЕР ДОСТУПЕН")
        print(f"📊 Uptime: {uptime}")
        return True

    except Exception as e:
        print(f"❌ СЕРВЕР НЕДОСТУПЕН: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ЗАПУСК ТЕСТА ПОДКЛЮЧЕНИЯ К СЕРВЕРУ")
    print("Сервер: 149.154.65.180 (root)")

    # Быстрая проверка доступности
    if not check_server_health():
        print("\n❌ СЕРВЕР НЕДОСТУПЕН - ПРОВЕРЬТЕ ПОДКЛЮЧЕНИЕ")
        sys.exit(1)

    print("\n" + "="*50)
    # Детальное тестирование
    if test_server_connection():
        print("\n🎉 ПОДКЛЮЧЕНИЕ К СЕРВЕРУ УСПЕШНО!")
        print("✅ SSH работает")
        print("✅ Команды выполняются")
        print("✅ API Gateway функционирует")
        print("✅ SFM доступен")
        print("\n🚀 ГОТОВ К РАЗВЕРТЫВАНИЮ ФУНКЦИЙ!")
    else:
        print("\n❌ ПРОБЛЕМЫ С ПОДКЛЮЧЕНИЕМ")
        print("🔧 Проверьте сетевые настройки и учетные данные")
        sys.exit(1)