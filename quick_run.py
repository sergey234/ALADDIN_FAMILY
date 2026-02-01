#!/usr/bin/env python3
import subprocess
import os
os.chdir("/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS")
p = subprocess.Popen(["expect", "deploy_api_gateway_final.exp"], 
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL,
                     start_new_session=True)
print(f"Запущено PID: {p.pid}")



