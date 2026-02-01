#!/usr/bin/env python3
import subprocess
import os
import time

os.chdir("/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS")

def run_expect_command(cmd, description):
    """Выполнить expect команду"""
    print(f"📋 {description}")
    full_cmd = f'/usr/bin/expect -c "{cmd}"'
    process = subprocess.Popen(
        full_cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    output, _ = process.communicate()
    print(output)
    return process.returncode == 0

print("=" * 60)
print("🚀 РАЗВЕРТЫВАНИЕ ALADDIN API GATEWAY")
print("=" * 60)
print()

# ШАГ 1: Загрузка api_gateway_complete.py
cmd1 = '''set timeout 60
spawn scp -o StrictHostKeyChecking=no api_gateway_complete.py root@149.154.65.180:/opt/aladdin-backend/
expect "password:" { send "Sergio675\\r" }
expect eof'''
run_expect_command(cmd1, "Загрузка api_gateway_complete.py")
time.sleep(2)

# ШАГ 2: Загрузка sfm_adapter.py
cmd2 = '''set timeout 60
spawn scp -o StrictHostKeyChecking=no sfm_adapter.py root@149.154.65.180:/opt/aladdin-backend/
expect "password:" { send "Sergio675\\r" }
expect eof'''
run_expect_command(cmd2, "Загрузка sfm_adapter.py")
time.sleep(2)

# ШАГ 3: Развертывание
cmd3 = '''set timeout 180
spawn ssh -o StrictHostKeyChecking=no root@149.154.65.180 "cd /opt/aladdin-backend && cp api_gateway.py api_gateway_backup_$(date +%Y%m%d_%H%M%S).py 2>/dev/null && echo '✅ Backup создан' || echo '⚠️ Первый деплой' && python3 -m py_compile api_gateway_complete.py && echo '✅ Синтаксис OK' && cp api_gateway_complete.py api_gateway.py && echo '✅ API Gateway заменен' && systemctl restart aladdin-api-gateway 2>/dev/null || systemctl restart aladdin-main-api-gateway 2>/dev/null && sleep 10 && curl -s http://127.0.0.1:8002/api/health | python3 -m json.tool 2>/dev/null || curl -s http://127.0.0.1:8002/api/health"
expect "password:" { send "Sergio675\\r" }
expect eof'''
run_expect_command(cmd3, "Развертывание на сервере")

print()
print("=" * 60)
print("✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!")
print("=" * 60)



