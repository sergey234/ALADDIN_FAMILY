#!/usr/bin/env python3

# 🔍 ПРОВЕРКА МИГРАЦИИ ГРУППЫ 3 ЧЕРЕЗ PYTHON + PARAMIKO
# Полная автоматизация без интерактивного ввода

import paramiko
import json
import sys

# Настройки подключения
SERVER = "149.154.65.180"
USER = "root"
PASSWORD = "Sergio675"

def execute_command(ssh_client, command, description=""):
    """Выполняет команду на сервере и возвращает результат"""
    print(f"📡 {description}")
    print(f"   Команда: {command}")

    try:
        stdin, stdout, stderr = ssh_client.exec_command(command)

        # Читаем вывод
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()

        if error:
            print(f"   Ошибка: {error}")

        print(f"   Результат: {output[:200]}{'...' if len(output) > 200 else ''}")
        print()
        return output, error
    except Exception as e:
        print(f"   Ошибка выполнения: {e}")
        print()
        return "", str(e)

def main():
    print("🔍 ПРОВЕРКА МИГРАЦИИ ГРУППЫ 3")
    print("=" * 50)
    print(f"Сервер: {SERVER}")
    print(f"Пользователь: {USER}")
    print()

    # Создаем SSH клиент
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Подключаемся к серверу
        print("🔗 Подключение к серверу...")
        ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=10)
        print("✅ Подключение установлено")
        print()

        # Проверка 1: Файл миграции
        output, error = execute_command(
            ssh,
            "ls -la /opt/aladdin-backend/migrate_group3.py",
            "1. ПРОВЕРКА ФАЙЛА МИГРАЦИИ"
        )

        file_exists = "/opt/aladdin-backend/migrate_group3.py" in output

        # Проверка 2: Код Группы 3
        output, error = execute_command(
            ssh,
            "grep -n 'Группа 3' /opt/aladdin-backend/api_gateway.py | head -3",
            "2. ПРОВЕРКА КОДА ГРУППЫ 3"
        )

        code_exists = "Группа 3" in output

        # Проверка 3: Статус API Gateway
        output, error = execute_command(
            ssh,
            "systemctl status aladdin-api-gateway --no-pager | head -5",
            "3. СТАТУС API GATEWAY"
        )

        service_active = "active (running)" in output

        # Проверка 4: Health endpoint
        output, error = execute_command(
            ssh,
            "curl -s http://127.0.0.1:8002/api/health",
            "4. HEALTH ENDPOINT"
        )

        try:
            health_data = json.loads(output)
            health_ok = health_data.get("status") == "ok"
        except:
            health_ok = False

        # Проверка 5: Endpoints Группы 3
        print("5. ТЕСТИРОВАНИЕ ENDPOINTS ГРУППЫ 3")
        print("-" * 40)

        endpoints = [
            "/api/ai/categories/stats",
            "/api/data/cleanup/stats",
            "/api/location/stats",
            "/api/darkweb/stats",
            "/api/identity/stats"
        ]

        endpoints_working = 0
        for endpoint in endpoints:
            output, error = execute_command(
                ssh,
                f"curl -s -w '%{{http_code}}' http://127.0.0.1:8002{endpoint} -o /dev/null",
                f"Тестирование {endpoint}"
            )
            if "200" in output:
                endpoints_working += 1

        # Проверка 6: Статистика endpoints
        output, error = execute_command(
            ssh,
            "grep -c 'app\.' /opt/aladdin-backend/api_gateway.py",
            "6. ПОДСЧЕТ ОБЩЕГО КОЛИЧЕСТВА ENDPOINTS"
        )

        try:
            total_endpoints = int(output.strip())
        except:
            total_endpoints = 0

        output, error = execute_command(
            ssh,
            "grep -c 'Группа 3\|api/ai\|api/data/cleanup\|api/location\|api/darkweb\|api/identity' /opt/aladdin-backend/api_gateway.py",
            "КОЛИЧЕСТВО ENDPOINTS ГРУППЫ 3"
        )

        try:
            group3_endpoints = int(output.strip())
        except:
            group3_endpoints = 0

        # Финальный вердикт
        print("7. ФИНАЛЬНЫЙ РЕЗУЛЬТАТ")
        print("=" * 40)

        checks = [
            ("Файл миграции присутствует", file_exists),
            ("Код Группы 3 добавлен", code_exists),
            ("API Gateway работает", service_active),
            ("Health endpoint отвечает", health_ok),
            (f"Endpoints Группы 3 работают ({endpoints_working}/5)", endpoints_working >= 3)
        ]

        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}")
            if not passed:
                all_passed = False

        print()
        print("📊 СТАТИСТИКА:")
        print(f"• Всего endpoints: {total_endpoints}")
        print(f"• Endpoints Группы 3: {group3_endpoints}")
        print(".1f"        print()

        if all_passed:
            print("🎉 МИГРАЦИЯ ГРУППЫ 3 ЗАВЕРШЕНА УСПЕШНО!")
            print("=" * 50)
            print("✅ Все проверки пройдены")
            print("✅ Группа 3 готова к использованию")
            print("✅ Мобильное приложение может использовать новые endpoints")
            print()
            print("🚀 ГОТОВО К ПРОДОЛЖЕНИЮ МИГРАЦИИ ГРУПП 4-5!")
        else:
            print("❌ МИГРАЦИЯ ГРУППЫ 3 НЕ ЗАВЕРШЕНА!")
            print("=" * 50)
            print("🔧 НУЖНО ВЫПОЛНИТЬ МИГРАЦИЮ:")
            print(f"ssh {USER}@{SERVER}")
            print("cd /opt/aladdin-backend")
            print("python3 migrate_group3.py --apply")

    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        print()
        print("🔧 ВОЗМОЖНЫЕ РЕШЕНИЯ:")
        print("1. Проверьте доступность сервера")
        print("2. Проверьте правильность пароля")
        print("3. Проверьте подключение: ping 149.154.65.180")
        return False

    finally:
        ssh.close()
        print()
        print("🔌 Подключение закрыто")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


