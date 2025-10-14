#!/usr/bin/env python3
"""
Простой HTTP сервер для веб-интерфейса мониторинга
"""

import http.server
import socketserver
import webbrowser
import os
from threading import Timer

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Добавляем CORS заголовки для работы с API
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def open_browser():
    """Открыть браузер через 2 секунды"""
    webbrowser.open(f'http://localhost:{PORT}/monitoring_dashboard.html')

if __name__ == '__main__':
    # Проверяем, что файл дашборда существует
    if not os.path.exists('monitoring_dashboard.html'):
        print("❌ Файл monitoring_dashboard.html не найден!")
        exit(1)
    
    # Проверяем, что Monitoring API Server запущен
    try:
        import requests
        response = requests.get('http://localhost:5006/api/monitoring/health', timeout=2)
        if response.status_code != 200:
            raise Exception("Monitoring API Server не отвечает")
    except Exception as e:
        print(f"⚠️ Предупреждение: Monitoring API Server не запущен ({e})")
        print("Запустите: python3 monitoring_api_server.py")
    
    # Запускаем сервер
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🌐 Веб-сервер мониторинга запущен на порту {PORT}")
        print(f"📊 Дашборд доступен по адресу: http://localhost:{PORT}/monitoring_dashboard.html")
        print(f"🔧 API мониторинга: http://localhost:5006/api/monitoring/dashboard")
        print("🛑 Для остановки нажмите Ctrl+C")
        
        # Открываем браузер через 2 секунды
        Timer(2.0, open_browser).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Веб-сервер остановлен")