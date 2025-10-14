#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание QR-кода для текстового файла с инструкциями
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

def create_file_qr():
    """Создание QR-кода для текстового файла"""
    print("📱 СОЗДАНИЕ QR-КОДА ДЛЯ ТЕКСТОВОГО ФАЙЛА")
    print("=" * 50)
    
    # Получение IP адреса
    local_ip = get_local_ip()
    
    # URL для текстового файла
    file_url = f"http://localhost:8000/VPN_INSTRUCTIONS.txt"
    
    print(f"🌐 Локальный IP: {local_ip}")
    print(f"🔗 URL для файла: {file_url}")
    
    # Создание QR-кода
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(file_url)
    qr.make(fit=True)
    
    # Создание изображения
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Сохранение QR-кода
    qr_filename = f"vpn_qr_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    img.save(qr_filename)
    
    print(f"✅ QR-код для файла сохранен: {qr_filename}")
    print(f"📱 Отсканируйте QR-код камерой телефона для получения инструкций")
    
    return qr_filename, file_url

def main():
    """Основная функция"""
    print("📱 СОЗДАНИЕ QR-КОДА ДЛЯ ТЕКСТОВОГО ФАЙЛА")
    print("=" * 50)
    
    # Создание QR-кода
    qr_filename, file_url = create_file_qr()
    
    print("\n🎯 ВАРИАНТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 30)
    print("1. 📱 QR-код для файла - отсканируйте камерой телефона")
    print(f"   Файл: {qr_filename}")
    print(f"   URL: {file_url}")
    
    print("\n2. 🌐 Прямое подключение к файлу")
    print(f"   URL: {file_url}")
    
    print("\n3. 🔗 Альтернативные URL для файла:")
    print("   • http://localhost:8000/VPN_INSTRUCTIONS.txt")
    print("   • http://127.0.0.1:8000/VPN_INSTRUCTIONS.txt")
    
    print("\n✅ ГОТОВО! Используйте QR-код для получения инструкций!")

if __name__ == "__main__":
    main()
