#!/usr/bin/env python3
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("149.154.65.180", username="root", password="Sergio675", timeout=10)

print("🔧 ИСПРАВЛЕНИЕ 1: Установка Redis в виртуальное окружение")
print("=" * 50)

# API Gateway использует venvs/main_env
venv_python = "/opt/aladdin-backend/venvs/main_env/bin/python3"
venv_pip = "/opt/aladdin-backend/venvs/main_env/bin/pip3"

# Проверка что venv существует
stdin, stdout, stderr = ssh.exec_command(f"test -f {venv_python} && echo 'OK' || echo 'NOT_FOUND'")
if stdout.read().decode().strip() != 'OK':
    print("❌ Виртуальное окружение не найдено, используем системный pip3")
    venv_pip = "pip3"

# Установка redis
print(f"Установка redis через {venv_pip}...")
stdin, stdout, stderr = ssh.exec_command(f"{venv_pip} install redis>=5.0.0 2>&1")
output = stdout.read().decode()
error = stderr.read().decode()
if "Successfully installed" in output or "Requirement already satisfied" in output:
    print("✅ Redis установлен")
else:
    print(f"⚠️  Вывод: {output}")
    if error:
        print(f"Ошибки: {error}")

# Проверка установки
print("\nПроверка установки...")
stdin, stdout, stderr = ssh.exec_command(f"{venv_python} -c 'import redis; r=redis.Redis(); print(\"Redis OK:\", r.ping())' 2>&1")
result = stdout.read().decode().strip()
print(result)
if "Redis OK: True" in result:
    print("✅ Redis работает в виртуальном окружении!")
else:
    print("❌ Проблема с Redis")

print("\n🔧 ИСПРАВЛЕНИЕ 2: Перезапуск API Gateway")
print("=" * 50)

# Остановка
print("Остановка API Gateway...")
ssh.exec_command("pkill -f 'uvicorn.*api_gateway.*8002'")
time.sleep(2)

# Запуск
print("Запуск API Gateway...")
ssh.exec_command("cd /opt/aladdin-backend && nohup /opt/aladdin-backend/venvs/main_env/bin/python3 -m uvicorn api_gateway:app --host 0.0.0.0 --port 8002 --workers 4 > /dev/null 2>&1 &")
time.sleep(3)

# Проверка
stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[u]vicorn.*api_gateway.*8002'")
process = stdout.read().decode()
if process:
    print("✅ API Gateway запущен")
    print(process.split('\n')[0])
else:
    print("❌ API Gateway не запустился")

# Проверка health
print("\nПроверка health endpoint...")
time.sleep(2)
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8002/api/health 2>&1 | head -3")
health = stdout.read().decode()
if "status" in health or "ok" in health.lower():
    print("✅ API Gateway отвечает")
else:
    print(f"⚠️  Ответ: {health[:100]}")

ssh.close()
print("\n✅ ИСПРАВЛЕНИЯ ЗАВЕРШЕНЫ!")
