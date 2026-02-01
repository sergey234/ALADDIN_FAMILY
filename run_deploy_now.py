#!/usr/bin/env python3
import subprocess
import os

os.chdir("/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS")

# Выполняем expect скрипт напрямую
proc = subprocess.Popen(
    ["/usr/bin/expect", "-f", "deploy_api_gateway_final.exp"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

stdout, stderr = proc.communicate()
print(stdout)
if stderr:
    print("STDERR:", stderr)



