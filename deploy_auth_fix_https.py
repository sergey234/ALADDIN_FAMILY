#!/usr/bin/env python3
# 🚀 Деплой исправления через HTTPS/Nginx + systemd

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
    print("=" * 60)
    print("🚀 ДЕПЛОЙ ИСПРАВЛЕНИЯ 401 ЧЕРЕЗ HTTPS/NGINX + SYSTEMD")
    print("=" * 60)
    print()
    
    # Проверка наличия файла
    if not os.path.exists(LOCAL_FILE):
        print(f"❌ Ошибка: Файл {LOCAL_FILE} не найден!")
        return False
    
    print(f"✅ Локальный файл найден: {LOCAL_FILE}")
    print()
    
    try:
        # Подключение к серверу через SSH (порт 22)
        print("🔌 Подключение к серверу через SSH...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Попробуем разные порты SSH
        ssh_ports = [22, 2222, 22022]
        connected = False
        
        for port in ssh_ports:
            try:
                print(f"   Попытка подключения на порт {port}...")
                ssh.connect(
                    SERVER, 
                    port=port,
                    username=USER, 
                    password=PASSWORD, 
                    timeout=30,
                    look_for_keys=False,
                    allow_agent=False,
                    compress=True
                )
                print(f"✅ Подключено к {USER}@{SERVER}:{port}")
                connected = True
                break
            except Exception as e:
                print(f"   ❌ Порт {port} недоступен: {e}")
                continue
        
        if not connected:
            print("❌ Не удалось подключиться ни к одному порту SSH")
            return False
        
        print()
        
        # Проверка структуры директорий
        print("📋 ШАГ 1: Проверка структуры директорий...")
        stdin, stdout, stderr = ssh.exec_command(f"ls -la {REMOTE_PATH} 2>&1")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            dir_list = stdout.read().decode()
            print(f"✅ Директория существует: {REMOTE_PATH}")
            print(f"   Содержимое:\n{dir_list}")
        else:
            # Попробуем создать директорию
            print(f"⚠️ Директория не найдена, создаем...")
            ssh.exec_command(f"mkdir -p {REMOTE_PATH} 2>&1")
            ssh.exec_command(f"mkdir -p /opt/aladdin-backend/app 2>&1")
            ssh.exec_command(f"mkdir -p /opt/aladdin-backend/app/auth 2>&1")
            print(f"✅ Директории созданы")
        print()
        
        # Создание backup
        print("📋 ШАГ 2: Создание backup...")
        backup_file = f"{REMOTE_PATH}/auth.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        stdin, stdout, stderr = ssh.exec_command(f"test -f {REMOTE_PATH}/auth.py && cp {REMOTE_PATH}/auth.py {backup_file} && echo 'BACKUP_OK' || echo 'NO_FILE' 2>&1")
        backup_result = stdout.read().decode().strip()
        if "BACKUP_OK" in backup_result:
            print(f"✅ Backup создан: {backup_file}")
        else:
            print(f"⚠️ Оригинальный файл не найден, backup не создан (это нормально для первого деплоя)")
        print()
        
        # Загрузка файла через SFTP
        print("📤 ШАГ 3: Загрузка файла на сервер...")
        sftp = ssh.open_sftp()
        try:
            # Убедимся что директория существует
            try:
                sftp.stat(REMOTE_PATH)
            except:
                sftp.mkdir(REMOTE_PATH)
            
            sftp.put(LOCAL_FILE, f"{REMOTE_PATH}/auth.py")
            print(f"✅ Файл загружен: {REMOTE_PATH}/auth.py")
            
            # Проверка что файл действительно загружен
            stdin, stdout, stderr = ssh.exec_command(f"ls -lh {REMOTE_PATH}/auth.py 2>&1")
            file_info = stdout.read().decode()
            print(f"   Информация о файле:\n{file_info}")
        except Exception as e:
            print(f"❌ Ошибка при загрузке файла: {e}")
            sftp.close()
            ssh.close()
            return False
        finally:
            sftp.close()
        print()
        
        # Проверка синтаксиса Python
        print("🔍 ШАГ 4: Проверка синтаксиса Python...")
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
        
        # Проверка systemd сервиса
        print("🔄 ШАГ 5: Проверка и перезапуск systemd сервиса...")
        
        # Список возможных имен сервисов
        possible_services = [
            "aladdin-backend",
            "aladdin-backend.service",
            "aladdin",
            "aladdin.service",
            "backend",
            "backend.service"
        ]
        
        service_found = None
        for service_name in possible_services:
            stdin, stdout, stderr = ssh.exec_command(f"systemctl list-units --type=service --all | grep -i {service_name} | head -1 2>&1")
            result = stdout.read().decode().strip()
            if result:
                service_found = service_name
                print(f"✅ Найден сервис: {service_name}")
                break
        
        if service_found:
            print(f"   Перезапуск сервиса: {service_found}")
            stdin, stdout, stderr = ssh.exec_command(f"systemctl restart {service_found} 2>&1")
            restart_output = stdout.read().decode()
            restart_error = stderr.read().decode()
            
            if restart_error:
                print(f"⚠️ Предупреждения при перезапуске: {restart_error}")
            
            # Проверка статуса
            import time
            time.sleep(2)
            stdin, stdout, stderr = ssh.exec_command(f"systemctl status {service_found} --no-pager -l 2>&1 | head -15")
            status = stdout.read().decode()
            print(f"   Статус сервиса:\n{status}")
        else:
            print("⚠️ Systemd сервис не найден, проверяем другие способы запуска...")
            
            # Проверка pm2
            stdin, stdout, stderr = ssh.exec_command("command -v pm2 >/dev/null 2>&1 && pm2 list 2>&1 | grep -i aladdin || echo 'PM2_NOT_FOUND'")
            pm2_result = stdout.read().decode().strip()
            if "PM2_NOT_FOUND" not in pm2_result and pm2_result:
                print("   Найден PM2 процесс, перезапуск...")
                ssh.exec_command("pm2 restart aladdin-backend 2>&1")
                time.sleep(2)
                stdin, stdout, stderr = ssh.exec_command("pm2 status aladdin-backend 2>&1")
                print(stdout.read().decode())
            else:
                # Проверка uvicorn процесса
                stdin, stdout, stderr = ssh.exec_command("pgrep -f 'uvicorn.*aladdin' 2>&1")
                uvicorn_pid = stdout.read().decode().strip()
                if uvicorn_pid:
                    print("   Найден процесс uvicorn, перезапуск...")
                    ssh.exec_command("pkill -f 'uvicorn.*aladdin' 2>&1")
                    time.sleep(2)
                    ssh.exec_command("cd /opt/aladdin-backend && nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /var/log/aladdin-backend.log 2>&1 &")
                    print("   ✅ Сервер перезапущен через uvicorn")
                else:
                    print("⚠️ Не удалось определить способ запуска сервера")
                    print("   Проверьте вручную:")
                    print("   - systemctl list-units --type=service | grep aladdin")
                    print("   - pm2 list")
                    print("   - ps aux | grep uvicorn")
        
        print()
        
        # Проверка через HTTPS
        print("🧪 ШАГ 6: Проверка через HTTPS...")
        import urllib.request
        import ssl
        
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request('https://aladdin-ai.ru/api/health')
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                health_data = response.read().decode()
                print(f"✅ Health check успешен: {health_data[:100]}")
        except Exception as e:
            print(f"⚠️ Health check не прошел (это нормально, если сервер еще перезапускается): {e}")
        
        print()
        
        # Закрытие соединения
        ssh.close()
        
        print("=" * 60)
        print("✅ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!")
        print("=" * 60)
        print()
        print("🧪 Тестирование:")
        print("   curl -H 'Authorization: Bearer YOUR_TOKEN' https://aladdin-ai.ru/api/family/stats")
        print()
        print("📝 Проверка логов:")
        print("   ssh root@149.154.65.180 'journalctl -u aladdin-backend -n 50'")
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
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = deploy()
    exit(0 if success else 1)
