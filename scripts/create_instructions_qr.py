#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание QR-кода для страницы с инструкциями
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

def create_instructions_qr():
    """Создание QR-кода для страницы с инструкциями"""
    print("📱 СОЗДАНИЕ QR-КОДА ДЛЯ СТРАНИЦЫ С ИНСТРУКЦИЯМИ")
    print("=" * 60)
    
    # Получение IP адреса
    local_ip = get_local_ip()
    
    # URL для страницы с инструкциями
    instructions_url = f"http://{local_ip}:8000/vpn_instructions.html"
    
    print(f"🌐 Локальный IP: {local_ip}")
    print(f"🔗 URL для инструкций: {instructions_url}")
    
    # Создание QR-кода
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(instructions_url)
    qr.make(fit=True)
    
    # Создание изображения
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Сохранение QR-кода
    qr_filename = f"vpn_qr_instructions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    img.save(qr_filename)
    
    print(f"✅ QR-код для инструкций сохранен: {qr_filename}")
    print(f"📱 Отсканируйте QR-код камерой телефона для получения инструкций")
    
    return qr_filename, instructions_url

def main():
    """Основная функция"""
    print("📱 СОЗДАНИЕ QR-КОДА ДЛЯ ИНСТРУКЦИЙ")
    print("=" * 50)
    
    # Создание QR-кода
    qr_filename, instructions_url = create_instructions_qr()
    
    print("\n🎯 ВАРИАНТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 30)
    print("1. 📱 QR-код для инструкций - отсканируйте камерой телефона")
    print(f"   Файл: {qr_filename}")
    print(f"   URL: {instructions_url}")
    
    print("\n2. 🌐 Прямое подключение к инструкциям")
    print(f"   URL: {instructions_url}")
    
    print("\n3. 🔗 Локальное подключение к инструкциям")
    print(f"   URL: http://localhost:8000/vpn_instructions.html")
    
    print("\n✅ ГОТОВО! Используйте QR-код для получения инструкций!")

if __name__ == "__main__":
    main()
