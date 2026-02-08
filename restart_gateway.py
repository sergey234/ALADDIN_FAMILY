#!/usr/bin/env python3
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("149.154.65.180", username="root", password="Sergio675", timeout=10)

print("🔧 Проверка и перезапуск API Gateway")
print("=" * 50)

# Проверка синтаксиса роутера
stdin, stdout, stderr = ssh.exec_command("python3 -m py_compile /opt/aladdin-backend/security/api/routers/crash_detection_router.py 2>&1")
syntax_check = stderr.read().decode()
if syntax_check:
    print(f"❌ Ошибка синтаксиса:\n{syntax_check}")
    # Восстанавливаем из backup
    print("\nВосстановление из backup...")
    ssh.exec_command("cp /opt/aladdin-backend/security/api/routers/crash_detection_router.py.backup /opt/aladdin-backend/security/api/routers/crash_detection_router.py 2>/dev/null || echo 'Backup не найден'")
else:
    print("✅ Синтаксис корректен")

# Остановка всех процессов
print("\nОстановка API Gateway...")
ssh.exec_command("pkill -9 -f 'uvicorn.*api_gateway.*8002'")
time.sleep(2)

# Проверка что остановлено
stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[u]vicorn.*api_gateway.*8002'")
if stdout.read().decode().strip():
    print("⚠️  Процесс все еще работает")
else:
    print("✅ Процессы остановлены")

# Запуск
print("\nЗапуск API Gateway...")
cmd = "cd /opt/aladdin-backend && /opt/aladdin-backend/venvs/main_env/bin/python3 -m uvicorn api_gateway:app --host 0.0.0.0 --port 8002 --workers 4"
stdin, stdout, stderr = ssh.exec_command(f"nohup {cmd} > /tmp/api_gateway.log 2>&1 &")
time.sleep(5)

# Проверка процесса
stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[u]vicorn.*api_gateway.*8002'")
process = stdout.read().decode()
if process:
    print("✅ API Gateway запущен")
    print(process.split('\n')[0])
else:
    print("❌ API Gateway не запустился")
    # Проверка логов
    stdin2, stdout2, stderr2 = ssh.exec_command("tail -20 /tmp/api_gateway.log 2>&1")
    print("\nЛоги ошибок:")
    print(stdout2.read().decode())

# Проверка health
print("\nПроверка health endpoint...")
time.sleep(2)
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8002/api/health 2>&1 | head -3")
health = stdout.read().decode()
if "status" in health or "ok" in health.lower() or health.strip():
    print(f"✅ API Gateway отвечает: {health[:50]}")
else:
    print(f"⚠️  Ответ: {health[:100]}")

ssh.close()
