#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание QR-кода с локальным URL для обхода прокси
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

def create_local_qr():
    """Создание QR-кода с локальным URL"""
    print("📱 СОЗДАНИЕ QR-КОДА С ЛОКАЛЬНЫМ URL")
    print("=" * 50)
    
    # Получение IP адреса
    local_ip = get_local_ip()
    
    # Создаем несколько вариантов URL
    urls = [
        f"http://{local_ip}:8000/vpn_test_fixed.html",
        f"http://localhost:8000/vpn_test_fixed.html",
        f"http://127.0.0.1:8000/vpn_test_fixed.html",
        f"http://{local_ip}:8000/vpn_test_simple_no_js.html"
    ]
    
    print(f"🌐 Локальный IP: {local_ip}")
    print(f"🔗 Основной URL: {urls[0]}")
    
    # Создание QR-кода для основного URL
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(urls[0])
    qr.make(fit=True)
    
    # Создание изображения
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Сохранение QR-кода
    qr_filename = f"vpn_qr_local_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    img.save(qr_filename)
    
    print(f"✅ QR-код сохранен: {qr_filename}")
    print(f"📱 Отсканируйте QR-код камерой телефона для подключения")
    
    return qr_filename, urls

def create_simple_qr():
    """Создание простого QR-кода с текстом"""
    print("\n📱 СОЗДАНИЕ ПРОСТОГО QR-КОДА С ТЕКСТОМ")
    print("=" * 50)
    
    # Простой текст с инструкциями
    text = """VPN Test Singapore
URL: http://192.168.0.101:8000/vpn_test_fixed.html
Или: http://localhost:8000/vpn_test_fixed.html
Или: http://127.0.0.1:8000/vpn_test_fixed.html

Инструкции:
1. Откройте браузер
2. Введите URL вручную
3. Нажмите "Тест Singapore"
4. Дождитесь результата"""
    
    # Создание QR-кода
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=4,
    )
    
    qr.add_data(text)
    qr.make(fit=True)
    
    # Создание изображения
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Сохранение QR-кода
    qr_filename = f"vpn_qr_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    img.save(qr_filename)
    
    print(f"✅ Простой QR-код сохранен: {qr_filename}")
    print(f"📱 Отсканируйте QR-код для получения инструкций")
    
    return qr_filename

def main():
    """Основная функция"""
    print("📱 СОЗДАНИЕ QR-КОДОВ ДЛЯ VPN (ОБХОД ПРОКСИ)")
    print("=" * 60)
    
    # Создание QR-кода с URL
    qr_filename, urls = create_local_qr()
    
    # Создание простого QR-кода
    text_qr_filename = create_simple_qr()
    
    print("\n🎯 ВАРИАНТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 30)
    print("1. 📱 QR-код с URL - отсканируйте камерой телефона")
    print(f"   Файл: {qr_filename}")
    print(f"   URL: {urls[0]}")
    
    print("\n2. 📱 QR-код с текстом - отсканируйте для инструкций")
    print(f"   Файл: {text_qr_filename}")
    
    print("\n3. 🌐 Прямое подключение - введите URL вручную")
    for i, url in enumerate(urls, 1):
        print(f"   {i}. {url}")
    
    print("\n4. 🔗 Локальное подключение - если на том же Wi-Fi")
    print(f"   URL: http://localhost:8000/vpn_test_fixed.html")
    
    print("\n✅ ГОТОВО! Используйте любой удобный способ!")

if __name__ == "__main__":
    main()
