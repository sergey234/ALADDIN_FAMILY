#!/usr/bin/env python3
# 🚀 Деплой auth.py с retry логикой

import paramiko
import os
import time
from datetime import datetime

SERVER = "149.154.65.180"
USER = "root"
PASSWORD = "Sergio675"
REMOTE_PATH = "/opt/aladdin-backend/app/auth"
LOCAL_FILE = "app/auth/auth.py"

def connect_with_retry(max_retries=3, timeout=120):
    """Подключение с повторными попытками"""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔌 Попытка подключения {attempt}/{max_retries}...")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Увеличенные таймауты
            ssh.connect(
                SERVER,
                username=USER,
                password=PASSWORD,
                timeout=timeout,
                look_for_keys=False,
                allow_agent=False,
                compress=True,
                banner_timeout=60
            )
            print(f"✅ Подключено к {USER}@{SERVER}")
            return ssh
        except Exception as e:
            print(f"⚠️ Попытка {attempt} не удалась: {e}")
            if attempt < max_retries:
                wait_time = attempt * 5
                print(f"⏳ Ожидание {wait_time} секунд перед следующей попыткой...")
                time.sleep(wait_time)
            else:
                raise
    return None

def deploy():
    print("=" * 50)
    print("🚀 ДЕПЛОЙ ИСПРАВЛЕНИЯ auth.py")
    print("=" * 50)
    print()
    
    if not os.path.exists(LOCAL_FILE):
        print(f"❌ Файл {LOCAL_FILE} не найден!")
        return False
    
    print(f"✅ Локальный файл найден: {LOCAL_FILE}")
    print()
    
    ssh = None
    try:
        # Подключение с retry
        ssh = connect_with_retry(max_retries=3, timeout=120)
        
        # Backup
        print("💾 ШАГ 1: Создание backup...")
        backup_file = f"{REMOTE_PATH}/auth.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        stdin, stdout, stderr = ssh.exec_command(f"cp {REMOTE_PATH}/auth.py {backup_file} 2>&1")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print(f"✅ Backup создан: {backup_file}")
        else:
            error = stderr.read().decode()
            if "No such file" not in error:
                print(f"⚠️ Предупреждение: {error}")
        print()
        
        # Загрузка файла
        print("📤 ШАГ 2: Загрузка файла на сервер...")
        sftp = ssh.open_sftp()
        try:
            sftp.put(LOCAL_FILE, f"{REMOTE_PATH}/auth.py")
            print(f"✅ Файл загружен: {REMOTE_PATH}/auth.py")
        finally:
            sftp.close()
        print()
        
        # Проверка синтаксиса
        print("🔍 ШАГ 3: Проверка синтаксиса Python...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 -m py_compile {REMOTE_PATH}/auth.py 2>&1")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("✅ Синтаксис Python корректен")
        else:
            error = stderr.read().decode()
            print(f"❌ Ошибка синтаксиса: {error}")
            return False
        print()
        
        # Перезапуск сервера
        print("🔄 ШАГ 4: Перезапуск сервера...")
        
        # Проверка systemd
        stdin, stdout, stderr = ssh.exec_command("systemctl is-active --quiet aladdin-backend 2>&1; echo $?")
        exit_status = stdout.channel.recv_exit_status()
        is_active = stdout.read().decode().strip()
        
        if exit_status == 0 and is_active == "0":
            print("   - Используется systemd")
            stdin, stdout, stderr = ssh.exec_command("systemctl restart aladdin-backend 2>&1")
            stdout.read()
            print("✅ Сервер перезапущен через systemd")
        else:
            # Проверка pm2
            stdin, stdout, stderr = ssh.exec_command("pm2 list 2>&1 | grep -q aladdin-backend && echo 'found' || echo 'not found'")
            pm2_check = stdout.read().decode().strip()
            if pm2_check == "found":
                print("   - Используется pm2")
                stdin, stdout, stderr = ssh.exec_command("pm2 restart aladdin-backend 2>&1")
                stdout.read()
                print("✅ Сервер перезапущен через pm2")
            else:
                print("⚠️ Не удалось определить способ запуска сервера")
                print("   Проверьте вручную:")
                print("   - systemctl status aladdin-backend")
                print("   - pm2 list")
        
        print()
        print("=" * 50)
        print("✅ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!")
        print("=" * 50)
        return True
        
    except paramiko.AuthenticationException:
        print("❌ Ошибка аутентификации! Проверьте пароль.")
        return False
    except paramiko.SSHException as e:
        print(f"❌ Ошибка SSH: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False
    finally:
        if ssh:
            ssh.close()

if __name__ == "__main__":
    success = deploy()
    exit(0 if success else 1)
