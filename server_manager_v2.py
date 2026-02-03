#!/usr/bin/env python3
"""
SERVER MANAGER V2 - ИНСТРУМЕНТ УПРАВЛЕНИЯ СЕРВЕРОМ ALADDIN
==========================================================

Полный инструмент для:
- Подключения к серверу
- Управления сервисами
- Загрузки/обновления файлов
- Тестирования API
- Мониторинга состояния
"""

import paramiko
import os
import time
import json
from typing import Dict, List, Optional, Tuple
import subprocess

class AladdinServerManager:
    """Менеджер сервера ALADDIN с полным набором команд"""

    def __init__(self):
        self.host = "149.154.65.180"
        self.username = "root"
        self.password = "Sergio675"
        self.ssh = None
        self.sftp = None
        self.connected = False

    def connect(self) -> bool:
        """Подключение к серверу"""
        try:
            print(f"🔌 Подключение к {self.host}...")
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.host, username=self.username, password=self.password, timeout=10)

            self.sftp = self.ssh.open_sftp()
            self.connected = True
            print("✅ Подключение успешно!")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False

    def disconnect(self):
        """Отключение от сервера"""
        if self.sftp:
            self.sftp.close()
        if self.ssh:
            self.ssh.close()
        self.connected = False
        print("🔌 Отключено от сервера")

    def run_command(self, command: str, show_output: bool = True) -> Tuple[int, str, str]:
        """Выполнение команды на сервере"""
        if not self.connected:
            print("❌ Нет подключения к серверу")
            return -1, "", ""

        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if show_output:
                if output:
                    print(f"📄 Вывод: {output}")
                if error:
                    print(f"⚠️  Ошибка: {error}")

            return exit_code, output, error
        except Exception as e:
            print(f"❌ Ошибка выполнения команды: {e}")
            return -1, "", str(e)

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Загрузка файла на сервер"""
        if not self.connected:
            print("❌ Нет подключения к серверу")
            return False

        try:
            print(f"📤 Загрузка {local_path} → {remote_path}")
            self.sftp.put(local_path, remote_path)
            print("✅ Файл загружен")
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Скачивание файла с сервера"""
        if not self.connected:
            print("❌ Нет подключения к серверу")
            return False

        try:
            print(f"📥 Скачивание {remote_path} → {local_path}")
            self.sftp.get(remote_path, local_path)
            print("✅ Файл скачан")
            return True
        except Exception as e:
            print(f"❌ Ошибка скачивания: {e}")
            return False

    def check_service_status(self, service_name: str) -> Dict:
        """Проверка статуса systemd сервиса"""
        print(f"📊 Проверка статуса {service_name}...")

        exit_code, output, error = self.run_command(f"systemctl is-active {service_name}", show_output=False)

        if exit_code == 0 and output == "active":
            status = "active"
            color = "✅"
        elif output == "inactive":
            status = "inactive"
            color = "❌"
        else:
            status = "unknown"
            color = "⚠️"

        # Получить детальную информацию
        exit_code, detail_output, _ = self.run_command(f"systemctl status {service_name} --no-pager -l | head -3", show_output=False)

        return {
            "service": service_name,
            "status": status,
            "detail": detail_output,
            "color": color
        }

    def restart_service(self, service_name: str) -> bool:
        """Перезапуск systemd сервиса"""
        print(f"🔄 Перезапуск {service_name}...")

        exit_code, output, error = self.run_command(f"systemctl restart {service_name}")

        if exit_code == 0:
            print(f"✅ {service_name} перезапущен")

            # Ждем запуска
            time.sleep(3)

            # Проверяем статус
            status_info = self.check_service_status(service_name)
            return status_info["status"] == "active"
        else:
            print(f"❌ Ошибка перезапуска {service_name}")
            return False

    def install_package(self, package_name: str) -> bool:
        """Установка пакета через pip в виртуальном окружении"""
        venv_path = "/opt/aladdin-backend/venvs/main_env/bin/pip"
        print(f"📦 Установка {package_name}...")

        exit_code, output, error = self.run_command(f"{venv_path} install {package_name}")

        if exit_code == 0:
            print(f"✅ {package_name} установлен")
            return True
        else:
            print(f"❌ Ошибка установки {package_name}")
            return False

    def test_api_endpoint(self, endpoint: str) -> Dict:
        """Тестирование API эндпоинта"""
        print(f"🧪 Тестирование {endpoint}...")

        exit_code, output, error = self.run_command(f"curl -s -w 'HTTPSTATUS:%{{http_code}};TIME:%{{time_total}}' 'http://127.0.0.1:8002{endpoint}'", show_output=False)

        if exit_code == 0 and output:
            # Разбираем ответ
            try:
                body = output.split('HTTPSTATUS:')[0]
                status_match = output.split('HTTPSTATUS:')[1].split(';')[0]
                time_match = output.split('TIME:')[1] if 'TIME:' in output else "0"

                http_status = int(status_match) if status_match.isdigit() else 0
                response_time = float(time_match) if time_match.replace('.', '').isdigit() else 0

                # Проверяем JSON
                try:
                    json_data = json.loads(body)
                    json_valid = True
                    source = json_data.get('source')
                    fallback = json_data.get('fallback')
                except json.JSONDecodeError:
                    json_valid = False
                    source = None
                    fallback = None

                result = {
                    "endpoint": endpoint,
                    "http_status": http_status,
                    "response_time": response_time,
                    "json_valid": json_valid,
                    "source": source,
                    "fallback": fallback,
                    "success": http_status == 200 and json_valid and source == "real_sfm"
                }

                status_emoji = "✅" if result["success"] else "❌"
                print(f"{status_emoji} {endpoint}: HTTP {http_status}, JSON {'✅' if json_valid else '❌'}, Source: {source or 'N/A'}, Fallback: {fallback or 'N/A'}")

                return result

            except Exception as e:
                print(f"❌ Ошибка разбора ответа: {e}")
                return {"endpoint": endpoint, "error": str(e), "success": False}
        else:
            print(f"❌ Ошибка запроса к {endpoint}")
            return {"endpoint": endpoint, "error": "Request failed", "success": False}

def main():
    print("🚀 ALADDIN SERVER MANAGER V2")
    print("=" * 40)

    manager = AladdinServerManager()

    # Подключение
    if not manager.connect():
        print("❌ Невозможно продолжить без подключения")
        return

    try:
        while True:
            print("\n📋 ДОСТУПНЫЕ КОМАНДЫ:")
            print("1. 📊 Проверить статус сервисов")
            print("2. 🔄 Перезапустить API Gateway")
            print("3. 🔄 Перезапустить SFM HTTP API")
            print("4. 📦 Установить requests")
            print("5. 📤 Загрузить sfm_adapter.py")
            print("6. 🧪 Протестировать API")
            print("7. 📋 Показать логи API Gateway")
            print("8. 📋 Показать логи SFM")
            print("9. 🔧 Полное исправление async конфликта")
            print("0. 🚪 Выход")

            try:
                choice = input("\nВыберите команду (0-9): ").strip()

                if choice == "0":
                    break
                elif choice == "1":
                    # Проверка статуса сервисов
                    services = ["aladdin-main-api-gateway", "aladdin-sfm-core"]
                    for service in services:
                        status = manager.check_service_status(service)
                        print(f"{status['color']} {service}: {status['status']}")
                        if status['detail']:
                            print(f"   {status['detail']}")

                elif choice == "2":
                    # Перезапуск API Gateway
                    if manager.restart_service("aladdin-main-api-gateway"):
                        print("✅ API Gateway успешно перезапущен")
                    else:
                        print("❌ Ошибка перезапуска API Gateway")

                elif choice == "3":
                    # Перезапуск SFM HTTP API
                    if manager.restart_service("aladdin-sfm-core"):
                        print("✅ SFM HTTP API успешно перезапущен")
                    else:
                        print("❌ Ошибка перезапуска SFM HTTP API")

                elif choice == "4":
                    # Установка requests
                    if manager.install_package("requests"):
                        print("✅ requests установлен успешно")
                    else:
                        print("❌ Ошибка установки requests")

                elif choice == "5":
                    # Загрузка sfm_adapter.py
                    local_file = "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/sfm_adapter.py"
                    remote_file = "/opt/aladdin-backend/sfm_adapter.py"

                    if os.path.exists(local_file):
                        if manager.upload_file(local_file, remote_file):
                            print("✅ sfm_adapter.py загружен успешно")
                        else:
                            print("❌ Ошибка загрузки sfm_adapter.py")
                    else:
                        print(f"❌ Локальный файл не найден: {local_file}")

                elif choice == "6":
                    # Тестирование API
                    print("🧪 Тестирование ключевых API эндпоинтов:")

                    endpoints = [
                        "/api/health",
                        "/api/components/health",
                        "/api/phishing/sensitivity",
                        "/api/analytics/overview"
                    ]

                    results = []
                    for endpoint in endpoints:
                        result = manager.test_api_endpoint(endpoint)
                        results.append(result)

                    # Итоги
                    successful = sum(1 for r in results if r.get("success", False))
                    total = len(results)

                    print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
                    print(f"   Протестировано: {total}")
                    print(f"   Успешных: {successful}")
                    print(f"   Успешность: {successful}/{total} ({successful*100//total}%)")

                elif choice == "7":
                    # Логи API Gateway
                    print("📋 Последние логи API Gateway:")
                    exit_code, output, error = manager.run_command("journalctl -u aladdin-main-api-gateway -n 10 --no-pager")
                    print(output)

                elif choice == "8":
                    # Логи SFM
                    print("📋 Последние логи SFM HTTP API:")
                    exit_code, output, error = manager.run_command("journalctl -u aladdin-sfm-core -n 10 --no-pager")
                    print(output)

                elif choice == "9":
                    # Полное исправление async конфликта
                    print("🔧 НАЧИНАЕМ ПОЛНОЕ ИСПРАВЛЕНИЕ ASYNC КОНФЛИКТА")
                    print("=" * 50)

                    # Шаг 1: Загрузка файла
                    print("\n📤 ШАГ 1: Загрузка sfm_adapter.py")
                    local_file = "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/sfm_adapter.py"
                    remote_file = "/opt/aladdin-backend/sfm_adapter.py"

                    if os.path.exists(local_file):
                        if manager.upload_file(local_file, remote_file):
                            print("✅ Файл загружен")
                        else:
                            print("❌ Ошибка загрузки файла")
                            continue
                    else:
                        print(f"❌ Локальный файл не найден: {local_file}")
                        continue

                    # Шаг 2: Установка requests
                    print("\n📦 ШАГ 2: Установка requests")
                    if not manager.install_package("requests"):
                        print("⚠️  Продолжаем (requests может уже быть установлен)")

                    # Шаг 3: Перезапуск SFM
                    print("\n🔄 ШАГ 3: Перезапуск SFM HTTP API")
                    manager.restart_service("aladdin-sfm-core")

                    # Шаг 4: Перезапуск API Gateway
                    print("\n🔄 ШАГ 4: Перезапуск API Gateway")
                    manager.restart_service("aladdin-main-api-gateway")

                    # Шаг 5: Тестирование
                    print("\n🧪 ШАГ 5: Тестирование исправления")
                    test_results = []
                    test_endpoints = [
                        "/api/components/health",
                        "/api/phishing/sensitivity",
                        "/api/analytics/overview"
                    ]

                    for endpoint in test_endpoints:
                        result = manager.test_api_endpoint(endpoint)
                        test_results.append(result)

                    # Анализ результатов
                    successful = sum(1 for r in test_results if r.get("success", False))
                    total = len(test_results)

                    print(f"\n🎯 РЕЗУЛЬТАТ ИСПРАВЛЕНИЯ:")
                    print(f"   Тестов: {total}")
                    print(f"   Успешных: {successful}")
                    print(f"   Прямые вызовы SFM: {successful}/{total}")

                    # Проверка на отсутствие fallback
                    fallback_count = sum(1 for r in test_results if r.get("fallback") is True)
                    print(f"   Fallback использован: {fallback_count}/{total}")

                    if successful == total and fallback_count == 0:
                        print("\n🎉 УСПЕХ! ASYNC КОНФЛИКТ ПОЛНОСТЬЮ ИСПРАВЛЕН!")
                        print("✅ Все функции работают напрямую с SFM")
                        print("✅ Fallback механизм не используется")
                        print("✅ Производительность восстановлена")
                    elif successful > 0:
                        print(f"\n⚠️  ЧАСТИЧНЫЙ УСПЕХ: {successful}/{total} функций работают")
                    else:
                        print("\n❌ ИСПРАВЛЕНИЕ НЕ СРАБОТАЛО")

                else:
                    print("❌ Неверный выбор. Попробуйте снова.")

            except KeyboardInterrupt:
                print("\n👋 Выход...")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")

    finally:
        manager.disconnect()

if __name__ == "__main__":
    main()