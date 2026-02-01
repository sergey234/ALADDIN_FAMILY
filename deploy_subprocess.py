#!/usr/bin/env python3
# Развертывание через subprocess - самый простой способ

import subprocess
import sys
import os
from pathlib import Path

SERVER = "149.154.65.180"
USER = "root"
PASSWORD = "Sergio675"
REMOTE_PATH = "/opt/aladdin-backend"
LOCAL_PATH = Path("/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS")

def run_cmd(cmd, description=""):
    """Выполнить команду"""
    if description:
        print(f"📋 {description}")
    print(f"   Команда: {cmd[:80]}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        if result.stdout:
            print(f"   {result.stdout.strip()[:200]}")
        if result.stderr and result.returncode != 0:
            print(f"   ⚠️ {result.stderr.strip()[:200]}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("   ❌ Таймаут команды")
        return False
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 РАЗВЕРТЫВАНИЕ ALADDIN API GATEWAY")
    print("=" * 60)
    print()
    
    # Проверка файлов
    print("📋 ШАГ 1: Проверка файлов...")
    api_file = LOCAL_PATH / "api_gateway_complete.py"
    sfm_file = LOCAL_PATH / "sfm_adapter.py"
    
    if not api_file.exists():
        print(f"❌ {api_file} не найден!")
        return False
    if not sfm_file.exists():
        print(f"❌ {sfm_file} не найден!")
        return False
    print("✅ Все файлы найдены")
    print()
    
    # Загрузка файлов
    print("📤 ШАГ 2: Загрузка файлов...")
    if not run_cmd(f'scp -o StrictHostKeyChecking=no "{api_file}" {USER}@{SERVER}:{REMOTE_PATH}/', 
                   "Загрузка api_gateway_complete.py"):
        return False
    
    if not run_cmd(f'scp -o StrictHostKeyChecking=no "{sfm_file}" {USER}@{SERVER}:{REMOTE_PATH}/',
                   "Загрузка sfm_adapter.py"):
        return False
    print()
    
    # Развертывание на сервере
    print("🔄 ШАГ 3: Развертывание на сервере...")
    deploy_script = f"""
cd {REMOTE_PATH}
cp api_gateway.py api_gateway_backup_$(date +%Y%m%d_%H%M%S).py 2>/dev/null && echo '✅ Backup создан' || echo '⚠️ Первый деплой'
python3 -m py_compile api_gateway_complete.py && echo '✅ Синтаксис OK' || exit 1
cp api_gateway_complete.py api_gateway.py && echo '✅ API Gateway заменен'
systemctl restart aladdin-api-gateway 2>/dev/null || systemctl restart aladdin-main-api-gateway 2>/dev/null || echo '⚠️ Сервис не найден'
sleep 10
curl -s http://127.0.0.1:8002/api/health | python3 -m json.tool 2>/dev/null || curl -s http://127.0.0.1:8002/api/health
"""
    
    if not run_cmd(f'ssh -o StrictHostKeyChecking=no {USER}@{SERVER} "{deploy_script}"',
                   "Выполнение развертывания"):
        return False
    print()
    
    print("=" * 60)
    print("✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!")
    print("=" * 60)
    print()
    print("📝 Проверьте:")
    print(f"   curl http://{SERVER}/api/health")
    print("   curl https://aladdin-ai.ru/api/health")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Отменено пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)



