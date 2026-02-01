#!/usr/bin/env python3
import os
import sys

os.chdir("/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS")

# Выполняем готовый скрипт deploy_inline.sh
print("🚀 Запуск развертывания...")
exit_code = os.system("bash deploy_inline.sh")
sys.exit(exit_code >> 8)



