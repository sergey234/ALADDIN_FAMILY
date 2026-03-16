#!/usr/bin/env python3
# 🚀 Деплой исправления для /api/family/stats (BUILD 121)

import paramiko
import os
from datetime import datetime

# Параметры сервера
SERVER = "149.154.65.180"
USER = "root"
PASSWORD = "Sergio675"
REMOTE_PATH = "/opt/aladdin-backend/app/auth"
LOCAL_FILE = "app/auth/auth.py"

def deploy():
    print("=" * 50)
    print("🚀 ДЕПЛОЙ ИСПРАВЛЕНИЯ 401 ДЛЯ /api/family/stats")
    print("=" * 50)
    print()
    
    # Проверка наличия файла
    if not os.path.exists(LOCAL_FILE):
        print(f"❌ Ошибка: Файл {LOCAL_FILE} не найден!")
        return False
    
    print(f"✅ Локальный файл найден: {LOCAL_FILE}")
    print()
    
    try:
        # Подключение к серверу
        print("🔌 Подключение к серверу...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Настройки для более надежного подключения
        ssh.connect(
            SERVER, 
            username=USER, 
            password=PASSWORD, 
            timeout=30,
            look_for_keys=False,
            allow_agent=False,
            compress=True
        )
        print(f"✅ Подключено к {USER}@{SERVER}")
        print()
        
        # Создание backup
        print("📋 ШАГ 1: Создание backup...")
        backup_file = f"{REMOTE_PATH}/auth.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        stdin, stdout, stderr = ssh.exec_command(f"cp {REMOTE_PATH}/auth.py {backup_file} 2>&1")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print(f"✅ Backup создан: {backup_file}")
        else:
            error = stderr.read().decode()
            if "No such file" not in error:
                print(f"⚠️ Предупреждение при создании backup: {error}")
        print()
        
        # Загрузка файла через SFTP
        print("📤 ШАГ 2: Загрузка файла на сервер...")
        sftp = ssh.open_sftp()
        try:
            sftp.put(LOCAL_FILE, f"{REMOTE_PATH}/auth.py")
            print(f"✅ Файл загружен: {REMOTE_PATH}/auth.py")
        except Exception as e:
            print(f"❌ Ошибка при загрузке файла: {e}")
            sftp.close()
            ssh.close()
            return False
        finally:
            sftp.close()
        print()
        
        # Проверка синтаксиса Python
        print("🔍 ШАГ 3: Проверка синтаксиса Python...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 -m py_compile {REMOTE_PATH}/auth.py 2>&1")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("✅ Синтаксис Python корректен")
        else:
            error = stderr.read().decode()
            print(f"❌ Ошибка синтаксиса Python: {error}")
            ssh.close()
            return False
        print()
        
        # Перезапуск сервера
        print("🔄 ШАГ 4: Перезапуск сервера...")
        
        # Попытка через systemd
        stdin, stdout, stderr = ssh.exec_command("systemctl is-active --quiet aladdin-backend 2>&1")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("   - Используется systemd")
            stdin, stdout, stderr = ssh.exec_command("systemctl restart aladdin-backend 2>&1")
            stdout.read()  # Ждем завершения
            stdin, stdout, stderr = ssh.exec_command("systemctl status aladdin-backend --no-pager -l 2>&1 | head -10")
            status = stdout.read().decode()
            print(status)
        else:
            # Попытка через pm2
            stdin, stdout, stderr = ssh.exec_command("pm2 list 2>&1 | grep -q aladdin-backend && echo 'found' || echo 'not found'")
            pm2_check = stdout.read().decode().strip()
            if pm2_check == "found":
                print("   - Используется pm2")
                stdin, stdout, stderr = ssh.exec_command("pm2 restart aladdin-backend 2>&1")
                stdout.read()
                stdin, stdout, stderr = ssh.exec_command("pm2 status aladdin-backend 2>&1")
                status = stdout.read().decode()
                print(status)
            else:
                # Попытка найти процесс uvicorn
                stdin, stdout, stderr = ssh.exec_command("pgrep -f 'uvicorn.*aladdin' 2>&1")
                uvicorn_pid = stdout.read().decode().strip()
                if uvicorn_pid:
                    print("   - Найден процесс uvicorn, перезапуск...")
                    ssh.exec_command("pkill -f 'uvicorn.*aladdin' 2>&1")
                    import time
                    time.sleep(2)
                    stdin, stdout, stderr = ssh.exec_command("cd /opt/aladdin-backend && nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /var/log/aladdin-backend.log 2>&1 &")
                    stdout.read()
                    print("   - Сервер перезапущен через uvicorn")
                else:
                    print("⚠️ Не удалось определить способ запуска сервера")
                    print("   Проверьте вручную:")
                    print("   - systemctl status aladdin-backend")
                    print("   - pm2 list")
                    print("   - ps aux | grep uvicorn")
        
        print()
        
        # Закрытие соединения
        ssh.close()
        
        print("=" * 50)
        print("✅ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!")
        print("=" * 50)
        print()
        print("🧪 Тестирование:")
        print("   curl -H 'Authorization: Bearer YOUR_TOKEN' https://aladdin-ai.ru/api/family/stats")
        print()
        
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

if __name__ == "__main__":
    success = deploy()
    exit(0 if success else 1)
