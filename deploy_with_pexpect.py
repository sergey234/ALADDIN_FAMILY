#!/usr/bin/env python3
# Развертывание через pexpect (Python аналог expect)

import pexpect
import sys
import os

os.chdir("/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS")

SERVER = "149.154.65.180"
USER = "root"
PASSWORD = "Sergio675"
REMOTE_PATH = "/opt/aladdin-backend"

print("=" * 60)
print("🚀 РАЗВЕРТЫВАНИЕ ALADDIN API GATEWAY")
print("=" * 60)
print()

# ШАГ 1: Загрузка api_gateway_complete.py
print("📤 ШАГ 1: Загрузка api_gateway_complete.py...")
child = pexpect.spawn(f'scp -o StrictHostKeyChecking=no api_gateway_complete.py {USER}@{SERVER}:{REMOTE_PATH}/')
child.expect(['password:', pexpect.EOF, pexpect.TIMEOUT], timeout=60)
if b'password:' in child.before or 'password:' in str(child.before):
    child.sendline(PASSWORD)
child.expect(pexpect.EOF, timeout=120)
print("✅ api_gateway_complete.py загружен")
print()

# ШАГ 2: Загрузка sfm_adapter.py
print("📤 ШАГ 2: Загрузка sfm_adapter.py...")
child = pexpect.spawn(f'scp -o StrictHostKeyChecking=no sfm_adapter.py {USER}@{SERVER}:{REMOTE_PATH}/')
child.expect(['password:', pexpect.EOF, pexpect.TIMEOUT], timeout=60)
if b'password:' in child.before or 'password:' in str(child.before):
    child.sendline(PASSWORD)
child.expect(pexpect.EOF, timeout=120)
print("✅ sfm_adapter.py загружен")
print()

# ШАГ 3: Развертывание на сервере
print("🔄 ШАГ 3: Развертывание на сервере...")
deploy_cmd = f"""cd {REMOTE_PATH} && cp api_gateway.py api_gateway_backup_$(date +%Y%m%d_%H%M%S).py 2>/dev/null && echo '✅ Backup создан' || echo '⚠️ Первый деплой' && python3 -m py_compile api_gateway_complete.py && echo '✅ Синтаксис OK' && cp api_gateway_complete.py api_gateway.py && echo '✅ API Gateway заменен' && systemctl restart aladdin-api-gateway 2>/dev/null || systemctl restart aladdin-main-api-gateway 2>/dev/null && sleep 10 && curl -s http://127.0.0.1:8002/api/health | python3 -m json.tool 2>/dev/null || curl -s http://127.0.0.1:8002/api/health"""

child = pexpect.spawn(f'ssh -o StrictHostKeyChecking=no {USER}@{SERVER} "{deploy_cmd}"')
child.expect(['password:', pexpect.EOF, pexpect.TIMEOUT], timeout=60)
if b'password:' in child.before or 'password:' in str(child.before):
    child.sendline(PASSWORD)
child.expect(pexpect.EOF, timeout=180)
output = child.before.decode('utf-8', errors='ignore')
print(output)
print()

print("=" * 60)
print("✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!")
print("=" * 60)



