#!/usr/bin/env python3
"""
Деплой оптимизаций Crash Detection API на сервер
"""
import paramiko
import os
import sys
from pathlib import Path

SERVER = "149.154.65.180"
USER = "root"
PASSWORD = "Sergio675"
REMOTE_PATH = "/opt/aladdin-backend"

def upload_file(sftp, local_path, remote_path):
    """Загрузка файла на сервер"""
    try:
        print(f"📤 Загрузка {local_path} -> {remote_path}")
        sftp.put(local_path, remote_path)
        print(f"✅ Загружено: {remote_path}")
        return True
    except Exception as e:
        print(f"❌ Ошибка загрузки {local_path}: {e}")
        return False

def execute_command(ssh, command, description):
    """Выполнение команды на сервере"""
    try:
        print(f"🔧 {description}...")
        stdin, stdout, stderr = ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if exit_status == 0:
            if output:
                print(f"✅ {description}: {output.strip()}")
            else:
                print(f"✅ {description}")
            return True
        else:
            print(f"❌ Ошибка: {error}")
            return False
    except Exception as e:
        print(f"❌ Ошибка выполнения команды: {e}")
        return False

def main():
    print("🚀 ДЕПЛОЙ ОПТИМИЗАЦИЙ CRASH DETECTION API")
    print("=" * 50)
    
    # Проверка файлов
    cache_file = "security/api/cache/crash_detection_cache.py"
    router_file = "crash_detection_router_optimized.py"
    
    if not os.path.exists(cache_file):
        print(f"❌ Файл не найден: {cache_file}")
        return False
    
    if not os.path.exists(router_file):
        print(f"❌ Файл не найден: {router_file}")
        return False
    
    print("✅ Локальные файлы найдены")
    
    # Подключение
    print(f"\n🔌 Подключение к {SERVER}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=10)
        sftp = ssh.open_sftp()
        print("✅ Подключено")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    
    try:
        # Создание директорий
        execute_command(ssh, f"mkdir -p {REMOTE_PATH}/security/api/cache", "Создание директорий")
        execute_command(ssh, f"mkdir -p {REMOTE_PATH}/security/api/routers", "Создание директорий")
        
        # Backup существующего роутера
        execute_command(ssh, 
            f"cp {REMOTE_PATH}/security/api/routers/crash_detection_router.py {REMOTE_PATH}/security/api/routers/crash_detection_router.py.backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true",
            "Создание backup")
        
        # Загрузка файлов
        upload_file(sftp, cache_file, f"{REMOTE_PATH}/security/api/cache/crash_detection_cache.py")
        upload_file(sftp, router_file, f"{REMOTE_PATH}/security/api/routers/crash_detection_router_optimized.py")
        
        # Проверка Redis
        execute_command(ssh, "redis-cli ping 2>/dev/null || echo 'Redis не запущен'", "Проверка Redis")
        
        # Установка redis если нужно
        execute_command(ssh, "python3 -c 'import redis' 2>/dev/null || pip3 install redis>=5.0.0", "Проверка/установка redis")
        
        # Проверка синтаксиса
        execute_command(ssh, 
            f"python3 -m py_compile {REMOTE_PATH}/security/api/cache/crash_detection_cache.py",
            "Проверка синтаксиса cache модуля")
        execute_command(ssh,
            f"python3 -m py_compile {REMOTE_PATH}/security/api/routers/crash_detection_router_optimized.py",
            "Проверка синтаксиса роутера")
        
        # Замена роутера
        execute_command(ssh,
            f"cp {REMOTE_PATH}/security/api/routers/crash_detection_router_optimized.py {REMOTE_PATH}/security/api/routers/crash_detection_router.py",
            "Замена роутера на оптимизированный")
        
        print("\n" + "=" * 50)
        print("✅ ДЕПЛОЙ ЗАВЕРШЕН!")
        print("=" * 50)
        print("\n📋 Следующие шаги:")
        print("1. Перезапустите API Gateway:")
        print("   ssh root@149.154.65.180 'pkill -f uvicorn; cd /opt/aladdin-backend && nohup python3 -m uvicorn api_gateway:app --host 0.0.0.0 --port 8002 > /dev/null 2>&1 &'")
        print("\n2. Запустите тест производительности:")
        print("   python3 test_crash_detection_performance.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    finally:
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
