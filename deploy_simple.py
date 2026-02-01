#!/usr/bin/env python3
# 🚀 ПРОСТОЕ РАЗВЕРТЫВАНИЕ ALADDIN API GATEWAY через paramiko

import os
import sys
import time
from pathlib import Path

try:
    import paramiko
except ImportError:
    print("❌ paramiko не установлен. Устанавливаю...")
    os.system("pip3 install paramiko")
    import paramiko

SERVER = "149.154.65.180"
USER = "root"
PASSWORD = "Sergio675"
REMOTE_PATH = "/opt/aladdin-backend"
LOCAL_PATH = Path("/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS")

def ssh_execute(ssh, command, description=""):
    """Выполнить команду через SSH"""
    if description:
        print(f"📋 {description}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if output:
        print(f"   {output.strip()}")
    if error and exit_status != 0:
        print(f"   ⚠️ {error.strip()}")
    
    return exit_status == 0

def scp_upload(ssh, local_file, remote_file, description=""):
    """Загрузить файл через SCP"""
    if description:
        print(f"📤 {description}")
    try:
        sftp = ssh.open_sftp()
        sftp.put(str(local_file), remote_file)
        sftp.close()
        print(f"   ✅ {local_file.name} загружен")
        return True
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 РАЗВЕРТЫВАНИЕ ALADDIN API GATEWAY")
    print("=" * 60)
    print()
    
    # Проверка локальных файлов
    print("📋 ШАГ 1: Проверка локальных файлов...")
    api_gateway_file = LOCAL_PATH / "api_gateway_complete.py"
    sfm_adapter_file = LOCAL_PATH / "sfm_adapter.py"
    
    if not api_gateway_file.exists():
        print(f"❌ {api_gateway_file} не найден!")
        return False
    if not sfm_adapter_file.exists():
        print(f"❌ {sfm_adapter_file} не найден!")
        return False
    print("✅ Все файлы найдены")
    print()
    
    # Подключение к серверу
    print("🔌 ШАГ 2: Подключение к серверу...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=30)
        print("✅ Подключено")
        print()
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    
    try:
        # Создание backup
        print("💾 ШАГ 3: Создание backup...")
        ssh_execute(ssh, f"cd {REMOTE_PATH} && if [ -f api_gateway.py ]; then cp api_gateway.py api_gateway_backup_$(date +%Y%m%d_%H%M%S).py && echo '✅ Backup создан'; else echo '⚠️ Первый деплой'; fi")
        print()
        
        # Загрузка файлов
        print("📤 ШАГ 4: Загрузка файлов...")
        scp_upload(ssh, api_gateway_file, f"{REMOTE_PATH}/api_gateway_complete.py", "Загрузка api_gateway_complete.py")
        scp_upload(ssh, sfm_adapter_file, f"{REMOTE_PATH}/sfm_adapter.py", "Загрузка sfm_adapter.py")
        print()
        
        # Проверка синтаксиса
        print("🔍 ШАГ 5: Проверка синтаксиса...")
        ssh_execute(ssh, f"cd {REMOTE_PATH} && python3 -m py_compile api_gateway_complete.py && echo '✅ Синтаксис OK'")
        print()
        
        # Замена api_gateway.py
        print("🔄 ШАГ 6: Замена api_gateway.py...")
        ssh_execute(ssh, f"cd {REMOTE_PATH} && cp api_gateway_complete.py api_gateway.py && echo '✅ API Gateway заменен'")
        print()
        
        # Перезапуск сервиса
        print("🔄 ШАГ 7: Перезапуск сервиса...")
        ssh_execute(ssh, "systemctl restart aladdin-api-gateway 2>/dev/null || systemctl restart aladdin-main-api-gateway 2>/dev/null || echo '⚠️ Сервис не найден'")
        print()
        
        # Ожидание
        print("⏳ ШАГ 8: Ожидание запуска (10 сек)...")
        time.sleep(10)
        print()
        
        # Тест
        print("🧪 ШАГ 9: Тест health endpoint...")
        ssh_execute(ssh, "curl -s http://127.0.0.1:8002/api/health | python3 -m json.tool 2>/dev/null || curl -s http://127.0.0.1:8002/api/health")
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
        
    finally:
        ssh.close()

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



