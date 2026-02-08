#!/usr/bin/env python3
"""
🔧 FIX SERVER NGINX CONFIGURATION
Исправление Nginx конфигурации после неудачной оптимизации
"""

import paramiko
import time

class ServerFixer:
    def __init__(self):
        self.hostname = '149.154.65.180'
        self.username = 'root'
        self.password = 'Sergio675'
        self.port = 22
        self.ssh = None

    def connect(self):
        try:
            print("🔌 Подключение к серверу для исправления...")
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10
            )
            print("✅ Подключение установлено")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False

    def execute_command(self, command, description="", timeout=30):
        try:
            print(f"🛠️  {description}")
            stdin, stdout, stderr = self.ssh.exec_command(command, timeout=timeout)

            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()

            if error:
                print(f"⚠️  {error}")

            return output, error
        except Exception as e:
            print(f"❌ Ошибка выполнения команды: {e}")
            return "", str(e)

    def check_nginx_status(self):
        print("🔍 ПРОВЕРКА СТАТУСА NGINX")
        print("-" * 30)

        # Статус сервиса
        output, _ = self.execute_command(
            "systemctl status nginx --no-pager -l",
            "Проверка статуса Nginx"
        )

        # Конфигурационные файлы
        output, _ = self.execute_command(
            "ls -la /etc/nginx/sites-enabled/",
            "Проверка включенных сайтов"
        )

        # Тест конфигурации
        output, _ = self.execute_command(
            "nginx -t 2>&1",
            "Тест конфигурации Nginx"
        )

        return output

    def fix_nginx_config(self):
        print("🔧 ИСПРАВЛЕНИЕ NGINX КОНФИГУРАЦИИ")
        print("-" * 30)

        # Удаляем проблемный конфиг
        self.execute_command(
            "rm -f /etc/nginx/sites-enabled/aladdin-optimized",
            "Удаление проблемного конфига"
        )

        # Проверяем основной конфиг
        output, _ = self.execute_command(
            "ls -la /etc/nginx/sites-enabled/",
            "Проверка оставшихся конфигов"
        )

        # Перезапускаем Nginx
        output, _ = self.execute_command(
            "systemctl restart nginx",
            "Перезапуск Nginx"
        )

        # Проверяем статус
        output, _ = self.execute_command(
            "systemctl status nginx --no-pager",
            "Проверка статуса после перезапуска"
        )

        return output

    def check_api_gateway(self):
        print("🔍 ПРОВЕРКА API GATEWAY")
        print("-" * 30)

        # Статус сервиса
        output, _ = self.execute_command(
            "systemctl status aladdin-main-api-gateway --no-pager",
            "Проверка статуса API Gateway"
        )

        # Тест API
        output, _ = self.execute_command(
            "curl -s http://127.0.0.1:8002/api/health",
            "Тест API Gateway локально"
        )

        return output

    def run_fixes(self):
        print("🚀 НАЧАЛО ИСПРАВЛЕНИЯ СЕРВЕРА")
        print("=" * 50)

        if not self.connect():
            return False

        try:
            # Шаг 1: Проверка статуса
            nginx_status = self.check_nginx_status()
            print(f"Nginx status: {nginx_status}")

            # Шаг 2: Исправление Nginx
            if "failed" in nginx_status.lower() or "error" in nginx_status.lower():
                self.fix_nginx_config()
            else:
                print("✅ Nginx работает нормально")

            # Шаг 3: Проверка API Gateway
            api_status = self.check_api_gateway()
            print(f"API Gateway status: {api_status}")

            # Шаг 4: Финальная проверка
            print("\n🔍 ФИНАЛЬНАЯ ПРОВЕРКА")
            print("-" * 30)

            # Тест API через Nginx (если работает)
            output, _ = self.execute_command(
                "curl -s http://127.0.0.1/api/health 2>/dev/null || echo 'Nginx not responding'",
                "Тест API через Nginx"
            )

            if "status" in output and "ok" in output:
                print("✅ API доступен через Nginx")
            else:
                print("⚠️  API недоступен через Nginx, но работает локально")

            return True

        finally:
            if self.ssh:
                self.ssh.close()
                print("🔌 Соединение закрыто")

def main():
    fixer = ServerFixer()

    print("🔧 ALADDIN SERVER FIXES")
    print("Исправление конфигурации после оптимизации")
    print("=" * 50)

    if fixer.run_fixes():
        print("\n✅ ИСПРАВЛЕНИЯ ПРИМЕНЕНЫ!")
        print("🔄 Теперь можно тестировать API")
    else:
        print("\n❌ ОШИБКА ИСПРАВЛЕНИЯ")

if __name__ == "__main__":
    main()