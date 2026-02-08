#!/usr/bin/env python3
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("149.154.65.180", username="root", password="Sergio675", timeout=10)

print("🔍 Проверка кода роутера на сервере")
print("=" * 50)

# Проверка декоратора кэширования
stdin, stdout, stderr = ssh.exec_command("grep -A 2 '@router.get.*status' /opt/aladdin-backend/security/api/routers/crash_detection_router.py | head -5")
print("Эндпоинт status:")
print(stdout.read().decode())

# Проверка импорта кэширования
stdin, stdout, stderr = ssh.exec_command("grep -A 5 'cache_result\\|from.*cache' /opt/aladdin-backend/security/api/routers/crash_detection_router.py | head -10")
print("\nИмпорты кэширования:")
print(stdout.read().decode())

# Проверка что декоратор применен
stdin, stdout, stderr = ssh.exec_command("grep -B 2 -A 5 'def get_crash_detection_status' /opt/aladdin-backend/security/api/routers/crash_detection_router.py")
print("\nФункция get_crash_detection_status:")
print(stdout.read().decode())

# Проверка CACHE_AVAILABLE
stdin, stdout, stderr = ssh.exec_command("grep 'CACHE_AVAILABLE' /opt/aladdin-backend/security/api/routers/crash_detection_router.py | head -3")
print("\nПеременная CACHE_AVAILABLE:")
print(stdout.read().decode())

ssh.close()
