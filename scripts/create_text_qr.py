#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание QR-кода с текстовыми инструкциями для обхода прокси
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

def create_text_qr():
    """Создание QR-кода с текстовыми инструкциями"""
    print("📱 СОЗДАНИЕ QR-КОДА С ТЕКСТОВЫМИ ИНСТРУКЦИЯМИ")
    print("=" * 60)
    
    # Получение IP адреса
    local_ip = get_local_ip()
    
    # Текстовые инструкции
    instructions = f"""VPN TEST SINGAPORE

ИНСТРУКЦИИ ДЛЯ ТЕЛЕФОНА:

1. Откройте браузер на телефоне
2. Введите один из URL ниже:

ОСНОВНЫЕ URL:
• http://{local_ip}:8000/vpn_test_fixed.html
• http://localhost:8000/vpn_test_fixed.html
• http://127.0.0.1:8000/vpn_test_fixed.html

АЛЬТЕРНАТИВНЫЕ URL:
• http://{local_ip}:8000/vpn_test_simple_no_js.html
• http://localhost:8000/vpn_test_simple_no_js.html

3. Нажмите "Тест Singapore"
4. Дождитесь результата
5. Проверьте IP адрес

РЕШЕНИЕ ПРОБЛЕМ:
• Если не открывается - проверьте Wi-Fi
• Если ошибка прокси - используйте localhost
• Если не работает - попробуйте другой URL

VPN СИСТЕМА ГОТОВА К ТЕСТИРОВАНИЮ!"""
    
    print(f"🌐 Локальный IP: {local_ip}")
    print("📝 Создание QR-кода с инструкциями...")
    
    # Создание QR-кода
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=4,
    )
    
    qr.add_data(instructions)
    qr.make(fit=True)
    
    # Создание изображения
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Сохранение QR-кода
    qr_filename = f"vpn_qr_instructions_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    img.save(qr_filename)
    
    print(f"✅ QR-код с инструкциями сохранен: {qr_filename}")
    print(f"📱 Отсканируйте QR-код камерой телефона для получения инструкций")
    
    return qr_filename, instructions

def create_simple_url_qr():
    """Создание простого QR-кода с URL"""
    print("\n📱 СОЗДАНИЕ ПРОСТОГО QR-КОДА С URL")
    print("=" * 50)
    
    # Получение IP адреса
    local_ip = get_local_ip()
    
    # Простой URL
    simple_url = f"http://localhost:8000/vpn_test_fixed.html"
    
    print(f"🌐 Локальный IP: {local_ip}")
    print(f"🔗 Простой URL: {simple_url}")
    
    # Создание QR-кода
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(simple_url)
    qr.make(fit=True)
    
    # Создание изображения
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Сохранение QR-кода
    qr_filename = f"vpn_qr_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    img.save(qr_filename)
    
    print(f"✅ Простой QR-код сохранен: {qr_filename}")
    print(f"📱 Отсканируйте QR-код камерой телефона")
    
    return qr_filename, simple_url

def main():
    """Основная функция"""
    print("📱 СОЗДАНИЕ QR-КОДОВ ДЛЯ ОБХОДА ПРОКСИ")
    print("=" * 60)
    
    # Создание QR-кода с инструкциями
    text_qr_filename, instructions = create_text_qr()
    
    # Создание простого QR-кода
    simple_qr_filename, simple_url = create_simple_url_qr()
    
    print("\n🎯 ВАРИАНТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 30)
    print("1. 📱 QR-код с инструкциями - отсканируйте камерой телефона")
    print(f"   Файл: {text_qr_filename}")
    print("   Содержит: Полные инструкции и все URL")
    
    print("\n2. 📱 Простой QR-код - отсканируйте камерой телефона")
    print(f"   Файл: {simple_qr_filename}")
    print(f"   URL: {simple_url}")
    
    print("\n3. 🌐 Прямое подключение - введите URL вручную")
    print(f"   URL: {simple_url}")
    
    print("\n4. 🔗 Альтернативные URL:")
    print("   • http://localhost:8000/vpn_test_fixed.html")
    print("   • http://127.0.0.1:8000/vpn_test_fixed.html")
    print("   • http://localhost:8000/vpn_test_simple_no_js.html")
    
    print("\n✅ ГОТОВО! Используйте QR-код с инструкциями!")

if __name__ == "__main__":
    main()
