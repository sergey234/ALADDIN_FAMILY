#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание QR-кода для быстрого подключения к VPN
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

def create_vpn_qr():
    """Создание QR-кода для VPN"""
    print("📱 СОЗДАНИЕ QR-КОДА ДЛЯ VPN ТЕСТИРОВАНИЯ")
    print("=" * 50)
    
    # Получение IP адреса
    local_ip = get_local_ip()
    port = 5000
    
    # URL для подключения
    vpn_url = f"http://{local_ip}:{port}"
    
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
    qr_filename = f"vpn_qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    img.save(qr_filename)
    
    print(f"✅ QR-код сохранен: {qr_filename}")
    print(f"📱 Отсканируйте QR-код камерой телефона для подключения")
    
    return qr_filename, vpn_url

def create_simple_test_page():
    """Создание простой тестовой страницы"""
    local_ip = get_local_ip()
    port = 5000
    
    html_content = f'''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VPN Test - Singapore</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }}
        .container {{
            max-width: 400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            text-align: center;
        }}
        h1 {{ font-size: 2em; margin-bottom: 30px; }}
        .button {{
            background: #4CAF50;
            color: white;
            padding: 20px 40px;
            border: none;
            border-radius: 15px;
            cursor: pointer;
            font-size: 18px;
            margin: 20px 0;
            width: 100%;
            transition: background 0.3s;
        }}
        .button:hover {{ background: #45a049; }}
        .info {{ background: rgba(255, 255, 255, 0.2); padding: 15px; border-radius: 10px; margin: 20px 0; }}
        .status {{ font-size: 16px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 VPN Test</h1>
        <div class="info">
            <h3>🇸🇬 Singapore VPN</h3>
            <p>Нажмите кнопку для тестирования подключения к Singapore</p>
        </div>
        
        <button class="button" onclick="testSingapore()">🚀 Тест Singapore</button>
        
        <div class="info">
            <div class="status" id="status">Готов к тестированию</div>
        </div>
        
        <div class="info">
            <h3>📱 Инструкции:</h3>
            <p>1. Нажмите "Тест Singapore"</p>
            <p>2. Дождитесь результата</p>
            <p>3. Проверьте IP адрес</p>
        </div>
    </div>

    <script>
        async function testSingapore() {{
            const status = document.getElementById('status');
            const button = event.target;
            
            status.textContent = '🔄 Тестирование подключения...';
            button.disabled = true;
            button.textContent = '🔄 Тестирование...';
            
            try {{
                const response = await fetch('/api/test_singapore');
                const data = await response.json();
                
                if (data.success) {{
                    status.innerHTML = `
                        <div style="color: #4CAF50;">
                            ✅ Тест Singapore успешен!<br>
                            Подключение: ${{data.connect_message}}<br>
                            Отключение: ${{data.disconnect_message}}<br>
                            Длительность: ${{data.test_duration}}
                        </div>
                    `;
                }} else {{
                    status.innerHTML = `
                        <div style="color: #f44336;">
                            ❌ Ошибка: ${{data.error}}
                        </div>
                    `;
                }}
            }} catch (error) {{
                status.innerHTML = `
                    <div style="color: #f44336;">
                        ❌ Ошибка подключения: ${{error.message}}
                    </div>
                `;
            }} finally {{
                button.disabled = false;
                button.textContent = '🚀 Тест Singapore';
            }}
        }}
    </script>
</body>
</html>
    '''
    
    # Сохранение HTML файла
    html_filename = "vpn_test_simple.html"
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Простая тестовая страница создана: {html_filename}")
    return html_filename

def main():
    """Основная функция"""
    print("📱 СОЗДАНИЕ УДОБНЫХ СПОСОБОВ ТЕСТИРОВАНИЯ VPN")
    print("=" * 60)
    
    # Создание QR-кода
    qr_filename, vpn_url = create_vpn_qr()
    
    # Создание простой тестовой страницы
    html_filename = create_simple_test_page()
    
    print("\n🎯 ВАРИАНТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 30)
    print("1. 📱 QR-код - отсканируйте камерой телефона")
    print(f"   Файл: {qr_filename}")
    print(f"   URL: {vpn_url}")
    
    print("\n2. 🌐 Простая страница - откройте в браузере")
    print(f"   Файл: {html_filename}")
    print(f"   URL: {vpn_url}")
    
    print("\n3. 📱 Прямое подключение - введите URL в браузере")
    print(f"   URL: {vpn_url}")
    
    print("\n4. 🔗 Локальное подключение - если на том же Wi-Fi")
    print(f"   URL: http://localhost:5000")
    
    print("\n✅ ГОТОВО! Выберите любой удобный способ!")

if __name__ == "__main__":
    main()
