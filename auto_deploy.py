#!/usr/bin/env python3
import subprocess
import os
import sys
import signal

os.chdir("/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS")

def run_expect_script():
    """Выполнить expect скрипт через subprocess без таймаутов"""
    print("🚀 Запуск развертывания через expect...")
    
    # Используем Popen с правильными параметрами
    process = subprocess.Popen(
        ["/usr/bin/expect", "deploy_api_gateway_final.exp"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        preexec_fn=os.setsid  # Создаем новую группу процессов
    )
    
    # Читаем вывод построчно
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                print(line.rstrip())
        process.wait()
        return process.returncode
    except KeyboardInterrupt:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        return 1

if __name__ == "__main__":
    exit_code = run_expect_script()
    sys.exit(exit_code)



