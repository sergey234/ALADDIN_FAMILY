#!/usr/bin/env python3
import os
import subprocess
import sys

os.chdir("/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS")

# Выполняем готовый expect скрипт
print("🚀 Запуск развертывания...")
result = os.system("/usr/bin/expect deploy_api_gateway_final.exp")
sys.exit(0 if result == 0 else 1)



