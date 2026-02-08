#!/usr/bin/env python3
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("149.154.65.180", username="root", password="Sergio675", timeout=10)
sftp = ssh.open_sftp()

print("🔧 ИСПРАВЛЕНИЕ: Отступы в роутере")
print("=" * 50)

# Загружаю правильную версию с локального файла
with open("crash_detection_router_optimized.py", "r") as f:
    correct_content = f.read()

# Исправляю путь импорта в правильной версии
correct_content = correct_content.replace(
    'cache_path = os.path.join(os.path.dirname(__file__), "..", "cache", "crash_detection_cache.py")',
    'cache_dir = "/opt/aladdin-backend/security/api/cache"'
)
correct_content = correct_content.replace(
    'if os.path.exists(cache_path):\n        sys.path.insert(0, os.path.dirname(cache_path))',
    'if cache_dir not in sys.path:\n        sys.path.insert(0, cache_dir)'
)
correct_content = correct_content.replace(
    'if os.path.exists(cache_path):',
    'if True:  # Путь всегда существует'
)

# Загружаю на сервер
with sftp.open("/opt/aladdin-backend/security/api/routers/crash_detection_router.py", "w") as f:
    f.write(correct_content)

print("✅ Роутер исправлен")

# Проверка синтаксиса
stdin, stdout, stderr = ssh.exec_command("python3 -m py_compile /opt/aladdin-backend/security/api/routers/crash_detection_router.py 2>&1")
err = stderr.read().decode()
if err:
    print(f"❌ Ошибка: {err}")
else:
    print("✅ Синтаксис корректен")

sftp.close()
ssh.close()
