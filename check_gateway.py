#!/usr/bin/env python3
import os
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ✅ Security: never hardcode secrets in repo. Use SSH key or env var for password.
host = os.environ.get("ALADDIN_SSH_HOST", "149.154.65.180")
username = os.environ.get("ALADDIN_SSH_USER", "root")
password = os.environ.get("ALADDIN_SSH_PASSWORD")  # optional; prefer SSH keys/agent
ssh.connect(host, username=username, password=password, timeout=10)

# Проверка процесса
stdin, stdout, stderr = ssh.exec_command("ps aux | grep '[u]vicorn.*8002'")
print("Процессы uvicorn на порту 8002:")
proc = stdout.read().decode()
print(proc if proc else "Не найдено")

# Проверка порта
stdin, stdout, stderr = ssh.exec_command("ss -tlnp 2>/dev/null | grep 8002 || netstat -tlnp 2>/dev/null | grep 8002")
print("\nПорт 8002:")
port = stdout.read().decode()
print(port if port else "Порт не слушается")

# Логи
stdin, stdout, stderr = ssh.exec_command("tail -40 /tmp/api_gateway.log 2>&1")
print("\nПоследние логи:")
logs = stdout.read().decode()
print(logs if logs else "Логи пусты")

# Проверка импорта
stdin, stdout, stderr = ssh.exec_command("cd /opt/aladdin-backend && /opt/aladdin-backend/venvs/main_env/bin/python3 -c 'from security.api.routers.crash_detection_router import router; print(\"OK\")' 2>&1")
import_result = stdout.read().decode() + stderr.read().decode()
if "Error" in import_result or "Traceback" in import_result:
    print("\n❌ Ошибка импорта:")
    print(import_result)
else:
    print("\n✅ Импорт работает:", import_result.strip())

ssh.close()
