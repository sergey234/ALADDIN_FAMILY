#!/usr/bin/env python3
import subprocess
import os
import sys

os.chdir("/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS")

# Выполняем expect скрипт через subprocess с detach
process = subprocess.Popen(
    ["expect", "deploy_api_gateway_final.exp"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    stdin=subprocess.DEVNULL,
    start_new_session=True
)

# Не ждем завершения, просто запускаем
print(f"🚀 Развертывание запущено (PID: {process.pid})")
print("✅ Команда выполнена в фоне")
sys.exit(0)



