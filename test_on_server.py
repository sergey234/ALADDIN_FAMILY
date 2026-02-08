#!/usr/bin/env python3
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("149.154.65.180", username="root", password="Sergio675", timeout=10)

print("🧪 ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ НА СЕРВЕРЕ (без сетевой задержки)")
print("=" * 60)

# Создаем тестовый скрипт на сервере
test_script = '''import time
import requests

BASE_URL = "http://localhost:8002"

print("1️⃣ Первый запрос (без кэша):")
start = time.perf_counter()
r1 = requests.get(f"{BASE_URL}/api/crash-detection/status", timeout=5)
time1 = (time.perf_counter() - start) * 1000
print(f"   Время: {time1:.2f}ms")

print("\\n2️⃣ Второй запрос (из кэша):")
time.sleep(0.1)
start = time.perf_counter()
r2 = requests.get(f"{BASE_URL}/api/crash-detection/status", timeout=5)
time2 = (time.perf_counter() - start) * 1000
print(f"   Время: {time2:.2f}ms")

print("\\n3️⃣ Третий запрос (из кэша):")
time.sleep(0.1)
start = time.perf_counter()
r3 = requests.get(f"{BASE_URL}/api/crash-detection/status", timeout=5)
time3 = (time.perf_counter() - start) * 1000
print(f"   Время: {time3:.2f}ms")

print(f"\\n📊 АНАЛИЗ:")
if time2 < time1 * 0.7:
    print(f"✅ КЭШИРОВАНИЕ РАБОТАЕТ! (улучшение: {((time1-time2)/time1*100):.1f}%)")
else:
    print(f"⚠️  Кэширование может не работать")

print(f"Среднее время запросов 2-3: {(time2+time3)/2:.2f}ms")
'''

# Записываем скрипт
stdin, stdout, stderr = ssh.exec_command("cat > /tmp/test_perf.py << 'PYEOF'\n" + test_script + "\nPYEOF\n")
stdout.channel.recv_exit_status()

# Запускаем тест
print("Запуск теста на сервере...\n")
stdin, stdout, stderr = ssh.exec_command("cd /opt/aladdin-backend && /opt/aladdin-backend/venvs/main_env/bin/python3 /tmp/test_perf.py 2>&1")
result = stdout.read().decode()
error = stderr.read().decode()

print(result)
if error:
    print("Ошибки:", error)

# Проверка Redis кэша
print("\n🔍 Проверка Redis кэша:")
stdin, stdout, stderr = ssh.exec_command("redis-cli KEYS 'crash_detection:*' 2>&1")
keys = stdout.read().decode().strip()
if keys:
    print("Ключи в кэше:")
    for key in keys.split('\n')[:5]:
        if key:
            stdin2, stdout2, stderr2 = ssh.exec_command(f"redis-cli TTL {key} 2>&1")
            ttl = stdout2.read().decode().strip()
            print(f"  - {key} (TTL: {ttl}s)")
else:
    print("Кэш пуст")

ssh.close()
