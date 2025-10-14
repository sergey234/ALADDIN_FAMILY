#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized Dashboard Server for ALADDIN
Оптимизированный сервер дашборда для ALADDIN
"""

import json
import time
import psutil
import threading
import csv
import os
import gzip
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, jsonify, send_file, request, Response
from flask_cors import CORS
from functools import lru_cache
import sqlite3
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
CORS(app)

# Кэш для часто запрашиваемых данных
@lru_cache(maxsize=100)
def get_cached_metrics():
    """Кэшированные метрики системы"""
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "processes": len(psutil.pids())
    }

# Пулинг соединений к базе данных
class DatabasePool:
    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self.connections = []
        self.lock = threading.Lock()

    def get_connection(self):
        with self.lock:
            if self.connections:
                return self.connections.pop()
            return sqlite3.connect('aladdin_logs.db')

    def return_connection(self, conn):
        with self.lock:
            if len(self.connections) < self.max_connections:
                self.connections.append(conn)
            else:
                conn.close()

db_pool = DatabasePool()

# Асинхронная обработка запросов
executor = ThreadPoolExecutor(max_workers=4)

def compress_response(data):
    """Сжатие ответа"""
    json_data = json.dumps(data, ensure_ascii=False)
    if len(json_data) > 1024:  # Сжимаем только большие ответы
        compressed = gzip.compress(json_data.encode('utf-8'))
        return Response(compressed, mimetype='application/json',
                      headers={'Content-Encoding': 'gzip'})
    return jsonify(data)

@app.route('/api/health')
def health():
    """Проверка здоровья системы"""
    return compress_response({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/data')
def get_data():
    """Получение данных системы с кэшированием"""
    try:
        # Используем кэшированные метрики
        metrics = get_cached_metrics()

        # Добавляем дополнительные метрики
        metrics.update({
            "system_uptime": time.time() - psutil.boot_time(),
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        })

        return compress_response(metrics)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export/csv')
def export_csv():
    """Экспорт данных в CSV с оптимизацией"""
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        # Оптимизированный запрос с лимитом
        cursor.execute("""
            SELECT timestamp, level, component, message, metadata
            FROM logs
            ORDER BY timestamp DESC
            LIMIT 1000
        """)

        results = cursor.fetchall()
        db_pool.return_connection(conn)

        # Создание CSV файла
        filename = f"aladdin_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = f"exports/{filename}"

        os.makedirs("exports", exist_ok=True)

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Level', 'Component', 'Message', 'Metadata'])
            writer.writerows(results)

        return jsonify({"success": True, "filename": filename, "count": len(results)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Запуск оптимизированного ALADDIN Dashboard Server...")
    print("📊 Дашборд будет доступен по адресу: http://localhost:5000")
    print("🔧 API будет доступно по адресу: http://localhost:5000/api/")
    print("🛑 Для остановки нажмите Ctrl+C")

    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
