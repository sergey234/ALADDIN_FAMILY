#!/usr/bin/env python3
import os
import sys

os.chdir("/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS")

# Выполняем развертывание через expect скрипт
os.system("chmod +x deploy_inline.sh")
os.system("bash deploy_inline.sh")



