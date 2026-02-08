#!/usr/bin/env python3
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("149.154.65.180", username="root", password="Sergio675", timeout=10)

print("🔍 ШАГ 1: Проверка логов API Gateway")
print("=" * 50)
stdin, stdout, stderr = ssh.exec_command("tail -30 /opt/aladdin-backend/logs/api.log 2>/dev/null || tail -30 /var/log/syslog | grep -i crash || echo 'Логи не найдены'")
logs = stdout.read().decode()
print(logs[:500] if len(logs) > 500 else logs)

print("\n🔍 ШАГ 2: Проверка импортов роутера")
print("=" * 50)
stdin, stdout, stderr = ssh.exec_command("find /opt/aladdin-backend -name '*.py' -type f -exec grep -l 'crash_detection_router' {} \\; 2>/dev/null | head -5")
imports = stdout.read().decode()
if imports:
    print("Файлы с импортами:")
    for line in imports.strip().split('\n'):
        print(f"  - {line}")
        stdin2, stdout2, stderr2 = ssh.exec_command(f"grep 'crash_detection_router' {line} | head -2")
        print(f"    {stdout2.read().decode().strip()}")
else:
    print("Импорты не найдены")

print("\n🔍 ШАГ 3: Проверка файлов роутеров")
print("=" * 50)
stdin, stdout, stderr = ssh.exec_command("ls -lah /opt/aladdin-backend/security/api/routers/crash_detection_router*.py")
print(stdout.read().decode())

# Проверка содержимого - есть ли кэширование
stdin, stdout, stderr = ssh.exec_command("grep -c 'cache_result\\|get_cached' /opt/aladdin-backend/security/api/routers/crash_detection_router.py 2>/dev/null || echo '0'")
cache_count = stdout.read().decode().strip()
print(f"\nКоличество упоминаний кэширования в роутере: {cache_count}")

print("\n🔍 ШАГ 4: Проверка Redis")
print("=" * 50)
stdin, stdout, stderr = ssh.exec_command("redis-cli ping 2>&1")
redis_ping = stdout.read().decode().strip()
print(f"Redis ping: {redis_ping}")

stdin, stdout, stderr = ssh.exec_command("python3 -c 'import redis; r=redis.Redis(); print(r.ping())' 2>&1")
python_redis = stdout.read().decode().strip()
print(f"Python Redis: {python_redis}")

# Проверка кэша
stdin, stdout, stderr = ssh.exec_command("redis-cli KEYS 'crash_detection:*' 2>&1 | head -5")
cache_keys = stdout.read().decode().strip()
if cache_keys:
    print(f"\nКлючи в кэше: {cache_keys}")
else:
    print("\nКэш пуст (это нормально если не было запросов)")

print("\n🔍 ШАГ 5: Проверка процесса API Gateway")
print("=" * 50)
stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[u]vicorn.*api_gateway'")
process = stdout.read().decode()
if process:
    print(process)
else:
    print("API Gateway процесс не найден")

print("\n🔍 ШАГ 6: Проверка модуля кэширования")
print("=" * 50)
stdin, stdout, stderr = ssh.exec_command("python3 -c 'import sys; sys.path.insert(0, \"/opt/aladdin-backend\"); from security.api.cache.crash_detection_cache import get_redis_client; print(\"OK\")' 2>&1")
cache_import = stdout.read().decode().strip()
print(f"Импорт модуля кэширования: {cache_import}")

ssh.close()
