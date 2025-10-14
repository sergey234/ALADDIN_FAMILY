#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск VPN Web Interface для тестирования на телефоне
"""

import sys
import os
import subprocess

# Добавление пути к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    print("🌍 ЗАПУСК VPN WEB INTERFACE")
    print("=" * 50)
    
    # Проверка Flask
    try:
        import flask
        print("✅ Flask установлен")
    except ImportError:
        print("❌ Flask не установлен. Устанавливаем...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'flask'])
        print("✅ Flask установлен")
    
    # Запуск веб-интерфейса
    print("\n🚀 Запуск VPN Web Interface...")
    print("📱 Откройте в браузере: http://localhost:5000")
    print("🌐 Для доступа с телефона: http://[IP_АДРЕС]:5000")
    print("🇸🇬 Для тестирования Singapore: http://localhost:5000/api/test_singapore")
    print("\n⏹️ Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    # Импорт и запуск
    from security.vpn.web.vpn_web_interface import app, init_vpn_system
    
    if init_vpn_system():
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("❌ Ошибка инициализации VPN системы")

if __name__ == "__main__":
    main()
