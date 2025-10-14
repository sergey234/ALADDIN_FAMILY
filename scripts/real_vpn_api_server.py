#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Реальный API сервер для VPN тестирования
"""

import asyncio
import logging
import sys
import os
import time
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Добавление пути к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.vpn.vpn_security_system import VPNSecuritySystem, VPNSecurityLevel

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальная переменная для VPN системы
vpn_system = None

class RealVPNAPIHandler(BaseHTTPRequestHandler):
    """Реальный API обработчик для VPN тестирования"""
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            self.serve_main_page()
        elif self.path == '/api/test_singapore':
            self.serve_test_singapore()
        elif self.path == '/api/status':
            self.serve_status()
        elif self.path == '/vpn_test_real.html':
            self.serve_real_test_page()
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
            text-decoration: none;
            display: inline-block;
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
        .demo { color: #2196F3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 VPN Test</h1>
        <div class="info">
            <h3>🇸🇬 Singapore VPN</h3>
            <p>Выберите режим тестирования:</p>
        </div>
        
        <a href="/vpn_test_real.html" class="button">🚀 Реальный тест Singapore</a>
        <a href="/vpn_test_fixed.html" class="button">📱 Демо режим</a>
        
        <div class="info">
            <h3>📱 Инструкции:</h3>
            <p>1. Выберите режим тестирования</p>
            <p>2. Нажмите "Тест Singapore"</p>
            <p>3. Дождитесь результата</p>
            <p>4. Проверьте IP адрес</p>
        </div>
        
        <div class="info">
            <h3>🌐 Подключение:</h3>
            <p>• Локально: http://localhost:8000</p>
            <p>• С телефона: http://192.168.0.101:8000</p>
            <p>• QR-код: отсканируйте камерой</p>
        </div>
    </div>
</body>
</html>
        '''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def serve_real_test_page(self):
        """Страница реального тестирования"""
        html_content = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VPN Test - Singapore (Real)</title>
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
        .real { color: #FF9800; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 VPN Test (Real)</h1>
        <div class="info">
            <h3>🇸🇬 Singapore VPN</h3>
            <p>Нажмите кнопку для реального тестирования подключения к Singapore</p>
        </div>
        
        <button class="button" onclick="testSingaporeReal()">🚀 Реальный тест Singapore</button>
        
        <div class="info">
            <div class="status" id="status">Готов к реальному тестированию</div>
        </div>
        
        <div class="info">
            <h3>📱 Инструкции:</h3>
            <p>1. Нажмите "Реальный тест Singapore"</p>
            <p>2. Дождитесь результата (5-10 секунд)</p>
            <p>3. Проверьте IP адрес</p>
            <p>4. При успехе - VPN работает!</p>
        </div>
        
        <div class="info">
            <h3>🔧 Режим тестирования:</h3>
            <p>• Реальный режим (с API)</p>
            <p>• Настоящее подключение</p>
            <p>• Проверка VPN системы</p>
        </div>
    </div>

    <script>
        async function testSingaporeReal() {
            const status = document.getElementById('status');
            const button = event.target;
            
            status.innerHTML = '<div class="loading">🔄 Реальное тестирование подключения к Singapore...</div>';
            button.disabled = true;
            button.textContent = '�� Тестирование...';
            
            try {
                const response = await fetch('/api/test_singapore');
                const data = await response.json();
                
                if (data.success) {
                    status.innerHTML = `
                        <div class="success">
                            ✅ Реальный тест Singapore успешен!<br><br>
                            <strong>Подключение:</strong> ${data.connect_message}<br>
                            <strong>Отключение:</strong> ${data.disconnect_message}<br>
                            <strong>Длительность:</strong> ${data.test_duration}<br>
                            <strong>Провайдер:</strong> ${data.report.provider}<br>
                            <strong>Время подключения:</strong> ${data.report.connection_time.toFixed(2)}с<br>
                            <strong>Уровень безопасности:</strong> ${data.report.security_level}<br><br>
                            <strong>🎉 VPN работает отлично!</strong><br><br>
                            <div class="real">
                                �� Это реальный тест VPN системы!<br>
                                🔧 Подключение к Singapore успешно!
                            </div>
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
                button.textContent = '🚀 Реальный тест Singapore';
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
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

def init_vpn_system():
    """Инициализация VPN системы"""
    global vpn_system
    try:
        vpn_system = VPNSecuritySystem("RealVPNAPIServer")
        print("✅ VPN система инициализирована")
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации VPN системы: {e}")
        return False

def main():
    """Основная функция"""
    print("🌍 ЗАПУСК РЕАЛЬНОГО VPN API СЕРВЕРА")
    print("=" * 50)
    
    # Инициализация VPN системы
    if not init_vpn_system():
        print("❌ Не удалось инициализировать VPN систему")
        return
    
    # Настройка сервера
    PORT = 8001
    server_address = ('', PORT)
    
    try:
        httpd = HTTPServer(server_address, RealVPNAPIHandler)
        print(f"🌍 Реальный VPN API сервер запущен на порту {PORT}")
        print(f"📱 Локально: http://localhost:{PORT}")
        print(f"🌐 С телефона: http://192.168.0.101:{PORT}")
        print(f"⏹️ Для остановки нажмите Ctrl+C")
        print("=" * 50)
        
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️ Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка сервера: {e}")

if __name__ == "__main__":
    main()
