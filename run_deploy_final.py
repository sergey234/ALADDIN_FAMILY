#!/usr/bin/env python3
import subprocess
import os
import sys

os.chdir("/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS")

print("🚀 Начинаю развертывание через sshpass...")

# ШАГ 1: Загрузка api_gateway_complete.py
print("📤 Загрузка api_gateway_complete.py...")
proc = subprocess.Popen(
    ["sshpass", "-p", "Sergio675", "scp", "-o", "StrictHostKeyChecking=no", 
     "api_gateway_complete.py", "root@149.154.65.180:/opt/aladdin-backend/"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
stdout, stderr = proc.communicate()
if proc.returncode == 0:
    print("✅ api_gateway_complete.py загружен")
else:
    print(f"❌ Ошибка: {stderr.decode()}")
    sys.exit(1)

# ШАГ 2: Загрузка sfm_adapter.py
print("📤 Загрузка sfm_adapter.py...")
proc = subprocess.Popen(
    ["sshpass", "-p", "Sergio675", "scp", "-o", "StrictHostKeyChecking=no",
     "sfm_adapter.py", "root@149.154.65.180:/opt/aladdin-backend/"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
stdout, stderr = proc.communicate()
if proc.returncode == 0:
    print("✅ sfm_adapter.py загружен")
else:
    print(f"❌ Ошибка: {stderr.decode()}")
    sys.exit(1)

# ШАГ 3: Развертывание на сервере
print("🔄 Развертывание на сервере...")
deploy_cmd = """cd /opt/aladdin-backend && cp api_gateway.py api_gateway_backup_$(date +%Y%m%d_%H%M%S).py 2>/dev/null && echo '✅ Backup создан' || echo '⚠️ Первый деплой' && python3 -m py_compile api_gateway_complete.py && echo '✅ Синтаксис OK' && cp api_gateway_complete.py api_gateway.py && echo '✅ API Gateway заменен' && systemctl restart aladdin-api-gateway 2>/dev/null || systemctl restart aladdin-main-api-gateway 2>/dev/null && sleep 10 && curl -s http://127.0.0.1:8002/api/health | python3 -m json.tool 2>/dev/null || curl -s http://127.0.0.1:8002/api/health"""

proc = subprocess.Popen(
    ["sshpass", "-p", "Sergio675", "ssh", "-o", "StrictHostKeyChecking=no",
     "root@149.154.65.180", deploy_cmd],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
stdout, stderr = proc.communicate()
print(stdout.decode())
if stderr:
    print(stderr.decode())

if proc.returncode == 0:
    print("\n✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!")
    sys.exit(0)
else:
    print(f"\n⚠️ Код выхода: {proc.returncode}")
    sys.exit(1)



