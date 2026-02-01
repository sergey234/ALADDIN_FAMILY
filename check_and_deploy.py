#!/usr/bin/env python3
"""
Проверка возможностей и развертывание через paramiko
"""
import sys
import os
from pathlib import Path

print("=" * 60)
print("🔍 ПРОВЕРКА ВОЗМОЖНОСТЕЙ ДЛЯ РАЗВЕРТЫВАНИЯ")
print("=" * 60)
print()

# 1. Проверка Python
print("1. Python версия:")
print(f"   {sys.version}")
print()

# 2. Проверка paramiko
print("2. Проверка paramiko:")
try:
    import paramiko
    print("   ✅ paramiko уже установлен")
    paramiko_available = True
except ImportError:
    print("   ⚠️ paramiko не установлен, пытаюсь установить...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'paramiko', '--quiet'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            import paramiko
            print("   ✅ paramiko успешно установлен")
            paramiko_available = True
        else:
            print(f"   ❌ Ошибка установки: {result.stderr}")
            paramiko_available = False
    except Exception as e:
        print(f"   ❌ Не удалось установить paramiko: {e}")
        paramiko_available = False
print()

# 3. Проверка сетевого доступа
print("3. Проверка сетевого доступа к серверу:")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex(('149.154.65.180', 22))
    sock.close()
    if result == 0:
        print("   ✅ Сервер 149.154.65.180:22 доступен")
        network_available = True
    else:
        print(f"   ❌ Сервер недоступен (код: {result})")
        network_available = False
except Exception as e:
    print(f"   ❌ Ошибка проверки: {e}")
    network_available = False
print()

# 4. Проверка доступа к файлам
print("4. Проверка доступа к файлам:")
LOCAL_PATH = Path("/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS")
files = {
    "api_gateway_complete.py": LOCAL_PATH / "api_gateway_complete.py",
    "sfm_adapter.py": LOCAL_PATH / "sfm_adapter.py"
}

files_available = True
for name, path in files.items():
    if path.exists():
        size = path.stat().st_size
        print(f"   ✅ {name} доступен ({size:,} bytes)")
    else:
        print(f"   ❌ {name} не найден: {path}")
        files_available = False
print()

# Итоговая проверка
print("=" * 60)
print("📊 ИТОГОВАЯ ПРОВЕРКА")
print("=" * 60)

if paramiko_available and network_available and files_available:
    print("✅ ВСЕ УСЛОВИЯ ВЫПОЛНЕНЫ - МОЖНО РАЗВЕРТЫВАТЬ!")
    print()
    print("🚀 Запускаю развертывание...")
    print()
    
    # РАЗВЕРТЫВАНИЕ
    SERVER = "149.154.65.180"
    USER = "root"
    PASSWORD = "Sergio675"
    REMOTE_PATH = "/opt/aladdin-backend"
    
    try:
        # Подключение
        print("📡 Подключение к серверу...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=30)
        print("   ✅ Подключено")
        print()
        
        # Загрузка файлов через SFTP
        print("📤 Загрузка файлов...")
        sftp = ssh.open_sftp()
        
        for name, local_path in files.items():
            remote_path = f"{REMOTE_PATH}/{name}"
            print(f"   Загрузка {name}...")
            sftp.put(str(local_path), remote_path)
            print(f"   ✅ {name} загружен")
        
        sftp.close()
        print()
        
        # Развертывание
        print("🔄 Развертывание на сервере...")
        commands = [
            f"cd {REMOTE_PATH}",
            "cp api_gateway.py api_gateway_backup_$(date +%Y%m%d_%H%M%S).py 2>/dev/null && echo '✅ Backup создан' || echo '⚠️ Первый деплой'",
            "python3 -m py_compile api_gateway_complete.py && echo '✅ Синтаксис OK'",
            "cp api_gateway_complete.py api_gateway.py && echo '✅ API Gateway заменен'",
            "systemctl restart aladdin-api-gateway 2>/dev/null || systemctl restart aladdin-main-api-gateway 2>/dev/null && echo '✅ Сервис перезапущен'",
            "sleep 10",
            "curl -s http://127.0.0.1:8002/api/health | python3 -m json.tool 2>/dev/null || curl -s http://127.0.0.1:8002/api/health"
        ]
        
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().decode()
            error = stderr.read().decode()
            if output:
                print(f"   {output.strip()}")
            if error and 'error' in error.lower():
                print(f"   ⚠️ {error.strip()}")
        
        print()
        print("=" * 60)
        print("✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!")
        print("=" * 60)
        print()
        print("📝 Проверьте:")
        print("   curl http://149.154.65.180/api/health")
        print("   curl https://aladdin-ai.ru/api/health")
        
        ssh.close()
        
    except Exception as e:
        print(f"❌ Ошибка развертывания: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
else:
    print("❌ НЕ ВСЕ УСЛОВИЯ ВЫПОЛНЕНЫ")
    print()
    if not paramiko_available:
        print("   - paramiko недоступен")
    if not network_available:
        print("   - Нет сетевого доступа к серверу")
    if not files_available:
        print("   - Файлы недоступны")
    print()
    print("📋 См. SSH_ACCESS_OPTIONS.md для альтернативных методов")
    sys.exit(1)



