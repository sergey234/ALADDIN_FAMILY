#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправленный VPN сервер для тестирования
"""

import http.server
import socketserver
import json
import asyncio
import sys
import os
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Добавление пути к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.vpn.vpn_security_system import VPNSecuritySystem, VPNSecurityLevel

# Глобальная переменная для VPN системы
vpn_system = None

class VPNRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Обработчик запросов для VPN тестирования"""
    
    def do_GET(self):
        """Обработка GET запросов"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_main_page()
        elif parsed_path.path == '/api/test_singapore':
            self.serve_test_singapore()
        elif parsed_path.path == '/api/status':
            self.serve_status()
        else:
            self.send_error(404, "Not Found")
    
    def serve_main_page(self):
        """Главная страница"""
        html_content = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VPN Test - Singapore</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            text-align: center;
        }
        h1 { font-size: 2em; margin-bottom: 30px; }
        .button {
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
        }
        .button:hover { background: #45a049; }
        .info { 
            background: rgba(255, 255, 255, 0.2); 
            padding: 15px; 
            border-radius: 10px; 
            margin: 20px 0; 
            text-align: left;
        }
        .status { font-size: 16px; margin: 10px 0; }
        .success { color: #4CAF50; }
        .error { color: #f44336; }
        .loading { color: #FFC107; }
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
            <p>2. Дождитесь результата (5-10 секунд)</p>
            <p>3. Проверьте IP адрес</p>
            <p>4. При успехе - VPN работает!</p>
        </div>
        
        <div class="info">
            <h3>🌐 Подключение:</h3>
            <p>• Локально: http://localhost:8000</p>
            <p>• С телефона: http://192.168.0.101:8000</p>
            <p>• QR-код: отсканируйте камерой</p>
        </div>
    </div>

    <script>
        async function testSingapore() {
            const status = document.getElementById('status');
            const button = event.target;
            
            status.innerHTML = '<div class="loading">🔄 Тестирование подключения к Singapore...</div>';
            button.disabled = true;
            button.textContent = '🔄 Тестирование...';
            
            try {
                const response = await fetch('/api/test_singapore');
                const data = await response.json();
                
                if (data.success) {
                    status.innerHTML = `
                        <div class="success">
                            ✅ Тест Singapore успешен!<br><br>
                            <strong>Подключение:</strong> ${data.connect_message}<br>
                            <strong>Отключение:</strong> ${data.disconnect_message}<br>
                            <strong>Длительность:</strong> ${data.test_duration}<br><br>
                            <strong>🎉 VPN работает отлично!</strong>
                        </div>
                    `;
                } else {
                    status.innerHTML = `
                        <div class="error">
                            ❌ Ошибка тестирования:<br>
                            ${data.error}
                        </div>
                    `;
                }
            } catch (error) {
                status.innerHTML = `
                    <div class="error">
                        ❌ Ошибка подключения:<br>
                        ${error.message}
                    </div>
                `;
            } finally {
                button.disabled = false;
                button.textContent = '🚀 Тест Singapore';
            }
        }
    </script>
</body>
</html>
        '''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def serve_test_singapore(self):
        """API тестирования Singapore"""
        try:
            if not vpn_system:
                self.send_json_response({'success': False, 'error': 'VPN система не инициализирована'})
                return
            
            test_user = f'test_singapore_{int(time.time())}'
            
            # Подключение к Singapore
            success, message, report = asyncio.run(vpn_system.connect(
                test_user, 
                country='Singapore',
                security_level=VPNSecurityLevel.HIGH
            ))
            
            if success:
                # Ожидание 3 секунды
                time.sleep(3)
                
                # Отключение
                disconnect_success, disconnect_message = asyncio.run(vpn_system.disconnect(test_user))
                
                self.send_json_response({
                    'success': True,
                    'connect_message': message,
                    'disconnect_message': disconnect_message,
                    'report': report,
                    'test_duration': '3 секунды'
                })
            else:
                self.send_json_response({
                    'success': False,
                    'error': message
                })
                
        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            })
    
    def serve_status(self):
        """API статуса системы"""
        try:
            if not vpn_system:
                self.send_json_response({'error': 'VPN система не инициализирована'})
                return
            
            status = vpn_system.get_status()
            stats = vpn_system.get_system_stats()
            
            self.send_json_response({
                'status': status['status'],
                'message': status['message'],
                'statistics': stats
            })
        except Exception as e:
            self.send_json_response({'error': str(e)})
    
    def send_json_response(self, data):
        """Отправка JSON ответа"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

def init_vpn_system():
    """Инициализация VPN системы"""
    global vpn_system
    try:
        vpn_system = VPNSecuritySystem("FixedVPNServer")
        print("✅ VPN система инициализирована")
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации VPN системы: {e}")
        return False

def main():
    """Основная функция"""
    print("🌍 ЗАПУСК ИСПРАВЛЕННОГО VPN СЕРВЕРА")
    print("=" * 40)
    
    # Инициализация VPN системы
    if not init_vpn_system():
        print("❌ Не удалось инициализировать VPN систему")
        return
    
    # Настройка сервера
    PORT = 8000
    Handler = VPNRequestHandler
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"🌍 VPN сервер запущен на порту {PORT}")
            print(f"📱 Локально: http://localhost:{PORT}")
            print(f"🌐 С телефона: http://192.168.0.101:{PORT}")
            print(f"⏹️ Для остановки нажмите Ctrl+C")
            print("=" * 40)
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️ Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка сервера: {e}")

if __name__ == "__main__":
    main()
