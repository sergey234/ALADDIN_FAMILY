#!/usr/bin/env python3
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("149.154.65.180", username="root", password="Sergio675", timeout=10)
sftp = ssh.open_sftp()

print("🔧 ИСПРАВЛЕНИЕ: Путь импорта модуля кэширования")
print("=" * 50)

# Читаем текущий роутер
with sftp.open("/opt/aladdin-backend/security/api/routers/crash_detection_router.py", "r") as f:
    content = f.read().decode()

# Исправляем импорт - используем абсолютный путь
old_import = """try:
    import sys
    cache_path = os.path.join(os.path.dirname(__file__), "..", "cache", "crash_detection_cache.py")
    if os.path.exists(cache_path):
        sys.path.insert(0, os.path.dirname(cache_path))
        from crash_detection_cache import ("""

new_import = """try:
    import sys
    # Используем абсолютный путь для надежности
    cache_dir = "/opt/aladdin-backend/security/api/cache"
    if cache_dir not in sys.path:
        sys.path.insert(0, cache_dir)
    from crash_detection_cache import ("""

if old_import in content:
    content = content.replace(old_import, new_import)
    print("✅ Импорт исправлен")
    
    # Записываем обратно
    with sftp.open("/opt/aladdin-backend/security/api/routers/crash_detection_router.py", "w") as f:
        f.write(content)
    
    print("✅ Роутер обновлен")
    
    # Проверка синтаксиса
    stdin, stdout, stderr = ssh.exec_command("python3 -m py_compile /opt/aladdin-backend/security/api/routers/crash_detection_router.py 2>&1")
    if stdout.channel.recv_exit_status() == 0:
        print("✅ Синтаксис корректен")
    else:
        err = stderr.read().decode()
        print(f"❌ Ошибка синтаксиса: {err}")
    
    # Перезапуск API Gateway
    print("\n🔄 Перезапуск API Gateway...")
    ssh.exec_command("pkill -f 'uvicorn.*api_gateway.*8002'")
    import time
    time.sleep(2)
    ssh.exec_command("cd /opt/aladdin-backend && nohup /opt/aladdin-backend/venvs/main_env/bin/python3 -m uvicorn api_gateway:app --host 0.0.0.0 --port 8002 --workers 4 > /dev/null 2>&1 &")
    time.sleep(3)
    print("✅ API Gateway перезапущен")
else:
    print("⚠️  Импорт не найден в ожидаемом формате")

sftp.close()
ssh.close()
print("\n✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!")
