#!/usr/bin/env python3
# 🚀 РАЗВЕРТЫВАНИЕ API GATEWAY - Python версия

import os
import sys
import subprocess
import time
import json

SERVER = "149.154.65.180"
USER = "root"
PASSWORD = "Sergio675"
REMOTE_PATH = "/opt/aladdin-backend"
LOCAL_PATH = "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS"

print("=" * 60)
print("🚀 РАЗВЕРТЫВАНИЕ API GATEWAY")
print("=" * 60)
print()

def run_command(cmd, description=""):
    """Выполнить команду в системе"""
    if description:
        print(f"📋 {description}")
    print(f"   Команда: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.stdout:
            print(f"   Вывод: {result.stdout[:200]}")
        if result.returncode != 0 and result.stderr:
            print(f"   Ошибка: {result.stderr[:200]}")
        return result.returncode == 0
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def deploy():
    """Основной процесс развертывания"""
    
    # ШАГ 1: Проверка файлов
    print("🧪 ШАГ 1: Проверка файлов...")
    files = [
        f"{LOCAL_PATH}/api_gateway_complete.py",
        f"{LOCAL_PATH}/sfm_adapter.py"
    ]
    
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024
            print(f"   ✅ {os.path.basename(file)} ({size:.1f}K)")
        else:
            print(f"   ❌ {file} не найден!")
            return False
    
    print()
    
    # ШАГ 2: Создание backup
    print("💾 ШАГ 2: Создание backup на сервере...")
    cmd = f'ssh -o StrictHostKeyChecking=no {USER}@{SERVER} "cd {REMOTE_PATH} && cp api_gateway.py api_gateway_backup_$(date +%Y%m%d_%H%M%S).py 2>/dev/null && echo ✅ Backup создан || echo ⚠️ Первый деплой"'
    run_command(cmd)
    
    print()
    
    # ШАГ 3: Загрузка api_gateway_complete.py
    print("📤 ШАГ 3: Загрузка api_gateway_complete.py...")
    cmd = f'scp -o StrictHostKeyChecking=no {LOCAL_PATH}/api_gateway_complete.py {USER}@{SERVER}:{REMOTE_PATH}/'
    if not run_command(cmd):
        print("❌ Ошибка загрузки api_gateway_complete.py")
        return False
    
    print()
    
    # ШАГ 4: Загрузка sfm_adapter.py
    print("📤 ШАГ 4: Загрузка sfm_adapter.py...")
    cmd = f'scp -o StrictHostKeyChecking=no {LOCAL_PATH}/sfm_adapter.py {USER}@{SERVER}:{REMOTE_PATH}/'
    if not run_command(cmd):
        print("❌ Ошибка загрузки sfm_adapter.py")
        return False
    
    print()
    
    # ШАГ 5: Замена API Gateway
    print("🔄 ШАГ 5: Замена API Gateway и перезапуск...")
    commands = [
        f'cd {REMOTE_PATH}',
        'cp api_gateway_complete.py api_gateway.py',
        'python3 -m py_compile api_gateway.py && echo "✅ Синтаксис OK"',
        'systemctl restart aladdin-api-gateway 2>/dev/null || systemctl restart aladdin-main-api-gateway 2>/dev/null',
        'echo "✅ Сервис перезапущен"'
    ]
    
    full_cmd = f'ssh -o StrictHostKeyChecking=no {USER}@{SERVER} "{"; ".join(commands)}"'
    run_command(full_cmd)
    
    print()
    
    # ШАГ 6: Ожидание запуска
    print("⏳ ШАГ 6: Ожидание запуска сервиса (5 сек)...")
    time.sleep(5)
    
    print()
    
    # ШАГ 7: Тестирование
    print("🧪 ШАГ 7: Тестирование health endpoint...")
    cmd = f'ssh -o StrictHostKeyChecking=no {USER}@{SERVER} "curl -s http://127.0.0.1:8002/api/health 2>/dev/null | python3 -m json.tool 2>/dev/null || curl -s http://127.0.0.1:8002/api/health"'
    run_command(cmd)
    
    print()
    print("=" * 60)
    print("✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!")
    print("=" * 60)
    print()
    print("📝 Проверьте:")
    print(f"   • curl http://{SERVER}/api/health")
    print(f"   • https://aladdin-ai.ru/api/health")
    
    return True

if __name__ == "__main__":
    try:
        if deploy():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Развертывание отменено пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)



