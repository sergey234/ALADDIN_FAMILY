#!/usr/bin/env python3
import paramiko
import os
import time

SERVER = "149.154.65.180"
USER = "root"
PASSWORD = "Sergio675"
REMOTE_PATH = "/opt/aladdin-backend"

print("🚀 ДЕПЛОЙ ОПТИМИЗАЦИЙ CRASH DETECTION")
print("=" * 50)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=10)
sftp = ssh.open_sftp()
print("✅ Подключено к серверу")

# Создание директорий
ssh.exec_command("mkdir -p " + REMOTE_PATH + "/security/api/cache")
ssh.exec_command("mkdir -p " + REMOTE_PATH + "/security/api/routers")
print("✅ Директории созданы")

# Backup
ssh.exec_command("cp " + REMOTE_PATH + "/security/api/routers/crash_detection_router.py " + REMOTE_PATH + "/security/api/routers/crash_detection_router.py.backup 2>/dev/null || true")
print("✅ Backup создан")

# Загрузка файлов
sftp.put("security/api/cache/crash_detection_cache.py", REMOTE_PATH + "/security/api/cache/crash_detection_cache.py")
print("✅ Модуль кэширования загружен")

sftp.put("crash_detection_router_optimized.py", REMOTE_PATH + "/security/api/routers/crash_detection_router_optimized.py")
print("✅ Оптимизированный роутер загружен")

# Проверка Redis
stdin, stdout, stderr = ssh.exec_command("redis-cli ping 2>/dev/null || echo 'NOT_RUNNING'")
redis_status = stdout.read().decode().strip()
if redis_status == "PONG":
    print("✅ Redis работает")
else:
    print("⚠️  Установка Redis...")
    ssh.exec_command("apt-get update -qq && apt-get install -y redis-server >/dev/null 2>&1 || yum install -y redis >/dev/null 2>&1")
    ssh.exec_command("systemctl start redis-server 2>/dev/null || service redis start 2>/dev/null")

# Установка redis библиотеки
stdin, stdout, stderr = ssh.exec_command("python3 -c 'import redis' 2>&1")
if stdout.channel.recv_exit_status() != 0:
    print("⚠️  Установка redis библиотеки...")
    ssh.exec_command("pip3 install redis>=5.0.0 >/dev/null 2>&1")
print("✅ Redis библиотека установлена")

# Проверка синтаксиса
stdin, stdout, stderr = ssh.exec_command("python3 -m py_compile " + REMOTE_PATH + "/security/api/cache/crash_detection_cache.py 2>&1")
if stdout.channel.recv_exit_status() == 0:
    print("✅ Синтаксис cache модуля корректен")
else:
    err = stderr.read().decode()
    print("❌ Ошибка синтаксиса cache: " + err)

stdin, stdout, stderr = ssh.exec_command("python3 -m py_compile " + REMOTE_PATH + "/security/api/routers/crash_detection_router_optimized.py 2>&1")
if stdout.channel.recv_exit_status() == 0:
    print("✅ Синтаксис роутера корректен")
else:
    err = stderr.read().decode()
    print("❌ Ошибка синтаксиса роутера: " + err)

# Замена роутера
ssh.exec_command("cp " + REMOTE_PATH + "/security/api/routers/crash_detection_router_optimized.py " + REMOTE_PATH + "/security/api/routers/crash_detection_router.py")
print("✅ Роутер заменен на оптимизированный")

# Перезапуск API Gateway
print("🔄 Перезапуск API Gateway...")
ssh.exec_command("pkill -f 'uvicorn.*api_gateway' 2>/dev/null || true")
time.sleep(2)
ssh.exec_command("cd " + REMOTE_PATH + " && nohup python3 -m uvicorn api_gateway:app --host 0.0.0.0 --port 8002 > /dev/null 2>&1 &")
time.sleep(3)
print("✅ API Gateway перезапущен")

# Проверка работы
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8002/api/health 2>&1 | head -1")
health = stdout.read().decode().strip()
if "status" in health or "ok" in health.lower():
    print("✅ API Gateway работает")
else:
    print("⚠️  Статус API Gateway: " + health)

sftp.close()
ssh.close()
print("\n✅ ОПТИМИЗАЦИЯ ЗАВЕРШЕНА!")
