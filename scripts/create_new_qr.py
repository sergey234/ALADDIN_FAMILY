#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание нового QR-кода с правильным URL
"""

import qrcode
import socket
import sys
import os
from datetime import datetime

def get_local_ip():
    """Получение локального IP адреса"""
    try:
        # Подключение к внешнему адресу для определения локального IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "localhost"

def create_new_qr():
    """Создание нового QR-кода"""
    print("📱 СОЗДАНИЕ НОВОГО QR-КОДА ДЛЯ VPN ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    # Получение IP адреса
    local_ip = get_local_ip()
    
    # URL для подключения
    vpn_url = f"http://{local_ip}:8000/vpn_test_fixed.html"
    
    print(f"🌐 Локальный IP: {local_ip}")
    print(f"🔗 URL для подключения: {vpn_url}")
    
    # Создание QR-кода
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(vpn_url)
    qr.make(fit=True)
    
    # Создание изображения
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Сохранение QR-кода
    qr_filename = f"vpn_qr_new_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    img.save(qr_filename)
    
    print(f"✅ Новый QR-код сохранен: {qr_filename}")
    print(f"📱 Отсканируйте QR-код камерой телефона для подключения")
    
    return qr_filename, vpn_url

def main():
    """Основная функция"""
    print("📱 СОЗДАНИЕ НОВОГО QR-КОДА ДЛЯ VPN")
    print("=" * 50)
    
    # Создание QR-кода
    qr_filename, vpn_url = create_new_qr()
    
    print("\n🎯 ВАРИАНТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 30)
    print("1. 📱 Новый QR-код - отсканируйте камерой телефона")
    print(f"   Файл: {qr_filename}")
    print(f"   URL: {vpn_url}")
    
    print("\n2. 🌐 Прямое подключение - введите URL в браузере")
    print(f"   URL: {vpn_url}")
    
    print("\n3. 🔗 Локальное подключение - если на том же Wi-Fi")
    print(f"   URL: http://localhost:8000/vpn_test_fixed.html")
    
    print("\n✅ ГОТОВО! Используйте новый QR-код!")

if __name__ == "__main__":
    main()
