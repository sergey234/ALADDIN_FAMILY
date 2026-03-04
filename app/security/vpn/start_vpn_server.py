#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN VPN Server Launcher
Запуск VPN сервера для интеграции с iOS приложением
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    """Запуск VPN сервера"""
    
    print("🚀 Запуск ALADDIN VPN Server...")
    print("=" * 50)
    
    # Переходим в директорию с VPN сервером
    vpn_dir = Path(__file__).parent / "web"
    os.chdir(vpn_dir)
    
    print(f"📁 Рабочая директория: {vpn_dir}")
    
    # Проверяем наличие файла сервера
    server_file = vpn_dir / "vpn_web_server.py"
    if not server_file.exists():
        print("❌ Файл vpn_web_server.py не найден!")
        return 1
    
    print("✅ Файл сервера найден")
    
    # Устанавливаем переменные окружения
    env = os.environ.copy()
    env["FLASK_APP"] = "vpn_web_server.py"
    env["FLASK_ENV"] = "development"
    env["FLASK_DEBUG"] = "1"
    
    print("🔧 Настройки окружения:")
    print(f"   FLASK_APP: {env['FLASK_APP']}")
    print(f"   FLASK_ENV: {env['FLASK_ENV']}")
    print(f"   FLASK_DEBUG: {env['FLASK_DEBUG']}")
    
    print("\n🌐 Запуск сервера на http://localhost:8000")
    print("📱 iOS приложение будет подключаться к этому серверу")
    print("\n" + "=" * 50)
    print("Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    try:
        # Запускаем Flask сервер
        subprocess.run([
            sys.executable, "-m", "flask", "run",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--debug"
        ], env=env, check=True)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Сервер остановлен пользователем")
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка запуска сервера: {e}")
        return 1
        
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())


