#!/usr/bin/env python3
# 🚀 Деплой auth.py через SCPClient (как в deploy_via_paramiko.py)

import paramiko
from scp import SCPClient
import os
from datetime import datetime

SERVER = "149.154.65.180"
USER = "root"
PASSWORD = "Sergio675"
REMOTE_PATH = "/opt/aladdin-backend/app/auth"
LOCAL_FILE = "app/auth/auth.py"

def upload_file(ssh_client, local_path, remote_path, description):
    """Загрузить файл на сервер через SCP"""
    print(f"\n📤 {description}")
    print(f"Локальный: {local_path}")
    print(f"Сервер: {remote_path}")
    
    try:
        with SCPClient(ssh_client.get_transport()) as scp:
            scp.put(local_path, remote_path)
        print(f"✅ Файл загружен: {description}")
        return True
    except Exception as e:
        print(f"❌ Ошибка загрузки: {description} - {e}")
        return False

def execute_command(ssh_client, command, description, timeout=60):
    """Выполнить команду на сервере"""
    print(f"\n🔧 {description}")
    print(f"Команда: {command}")
    
    try:
        stdin, stdout, stderr = ssh_client.exec_command(command, timeout=timeout)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print(f"✅ УСПЕХ: {description}")
            if output:
                print(f"Вывод: {output}")
            return True, output
        else:
            print(f"❌ ОШИБКА: {description}")
            if error:
                print(f"Ошибка: {error}")
            return False, error
    except Exception as e:
        print(f"💥 ИСКЛЮЧЕНИЕ: {description} - {e}")
        return False, str(e)

def deploy():
    print("=" * 60)
    print("🚀 ДЕПЛОЙ ИСПРАВЛЕНИЯ auth.py")
    print("=" * 60)
    print()
    
    if not os.path.exists(LOCAL_FILE):
        print(f"❌ Файл {LOCAL_FILE} не найден!")
        return False
    
    print(f"✅ Локальный файл найден: {LOCAL_FILE}")
    print()
    
    # Подключение к серверу
    print("🔌 ПОДКЛЮЧЕНИЕ К СЕРВЕРУ...")
    print(f"Сервер: {SERVER}")
    print(f"Пользователь: {USER}")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            SERVER,
            username=USER,
            password=PASSWORD,
            timeout=120,
            look_for_keys=False,
            allow_agent=False,
            compress=True,
            banner_timeout=60
        )
        print("✅ ПОДКЛЮЧЕНИЕ УСТАНОВЛЕНО")
    except Exception as e:
        print(f"❌ ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")
        return False
    
    try:
        # ШАГ 1: Backup
        backup_file = f"{REMOTE_PATH}/auth.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        success, _ = execute_command(
            ssh,
            f"cp {REMOTE_PATH}/auth.py {backup_file} 2>&1 || echo 'First deploy'",
            "Создание backup"
        )
        if success:
            print(f"✅ Backup создан: {backup_file}")
        
        # ШАГ 2: Загрузка файла
        success = upload_file(
            ssh,
            LOCAL_FILE,
            f"{REMOTE_PATH}/auth.py",
            "Загрузка auth.py на сервер"
        )
        if not success:
            return False
        
        # ШАГ 3: Проверка синтаксиса
        success, _ = execute_command(
            ssh,
            f"python3 -m py_compile {REMOTE_PATH}/auth.py",
            "Проверка синтаксиса Python"
        )
        if not success:
            return False
        
        # ШАГ 4: Перезапуск сервера
        # Проверка systemd
        success, output = execute_command(
            ssh,
            "systemctl is-active --quiet aladdin-backend 2>&1; echo $?",
            "Проверка systemd сервиса"
        )
        
        if success and output.strip() == "0":
            success, _ = execute_command(
                ssh,
                "systemctl restart aladdin-backend",
                "Перезапуск через systemd"
            )
            if success:
                execute_command(
                    ssh,
                    "systemctl status aladdin-backend --no-pager -l | head -5",
                    "Статус сервиса"
                )
        else:
            # Проверка pm2
            success, output = execute_command(
                ssh,
                "pm2 list 2>&1 | grep -q aladdin-backend && echo 'found' || echo 'not found'",
                "Проверка pm2"
            )
            if success and output.strip() == "found":
                execute_command(
                    ssh,
                    "pm2 restart aladdin-backend",
                    "Перезапуск через pm2"
                )
            else:
                print("⚠️ Не удалось определить способ запуска сервера")
        
        print("\n" + "=" * 60)
        print("✅ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!")
        print("=" * 60)
        return True
        
    finally:
        ssh.close()
        print("\n🔌 СОЕДИНЕНИЕ С СЕРВЕРОМ ЗАКРЫТО")

if __name__ == "__main__":
    try:
        success = deploy()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ ДЕПЛОЙ ПРЕРВАН ПОЛЬЗОВАТЕЛЕМ")
        exit(1)
    except Exception as e:
        print(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        exit(1)
