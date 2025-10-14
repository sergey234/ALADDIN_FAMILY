#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Simple Export API
Упрощенный API для экспорта данных

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-08
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import sys
import csv
import json
from datetime import datetime
from typing import List, Dict, Any

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from elasticsearch_simulator import ElasticsearchSimulator, LogLevel

app = Flask(__name__)
CORS(app)

# Инициализация компонентов
es_simulator = ElasticsearchSimulator()
export_dir = "exports"
os.makedirs(export_dir, exist_ok=True)

@app.route('/api/export/health')
def health_check():
    """Проверка состояния API"""
    return jsonify({
        'status': 'healthy',
        'service': 'Simple Export API',
        'timestamp': datetime.now().isoformat(),
        'export_dir': export_dir,
        'formats': ['CSV', 'JSON']
    })

@app.route('/api/export/logs/csv')
def export_logs_csv():
    """Экспорт логов в CSV формат"""
    try:
        # Получаем параметры
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 50))
        level = request.args.get('level')
        component = request.args.get('component')
        
        # Поиск логов
        log_level = None
        if level:
            try:
                log_level = LogLevel(level.upper())
            except ValueError:
                pass
        
        results = es_simulator.search(
            query=query,
            level=log_level,
            component=component,
            limit=limit
        )
        
        # Создаем CSV файл
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aladdin_logs_{timestamp}.csv"
        filepath = os.path.join(export_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Level', 'Component', 'Message', 'Metadata'])
            
            for log in results.get('logs', []):
                writer.writerow([
                    log.get('timestamp', ''),
                    log.get('level', ''),
                    log.get('component', ''),
                    log.get('message', ''),
                    json.dumps(log.get('metadata', {}), ensure_ascii=False)
                ])
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'records': len(results.get('logs', [])),
            'message': f'CSV файл создан: {filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Ошибка при создании CSV файла'
        }), 500

@app.route('/api/export/logs/json')
def export_logs_json():
    """Экспорт логов в JSON формат"""
    try:
        # Получаем параметры
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 50))
        level = request.args.get('level')
        component = request.args.get('component')
        
        # Поиск логов
        log_level = None
        if level:
            try:
                log_level = LogLevel(level.upper())
            except ValueError:
                pass
        
        results = es_simulator.search(
            query=query,
            level=log_level,
            component=component,
            limit=limit
        )
        
        # Создаем JSON файл
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aladdin_logs_{timestamp}.json"
        filepath = os.path.join(export_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(results, jsonfile, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'records': len(results.get('logs', [])),
            'message': f'JSON файл создан: {filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Ошибка при создании JSON файла'
        }), 500

@app.route('/api/export/stats')
def export_stats():
    """Экспорт статистики системы"""
    try:
        # Получаем статистику
        stats = es_simulator.get_stats()
        
        # Создаем JSON файл
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aladdin_stats_{timestamp}.json"
        filepath = os.path.join(export_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(stats, jsonfile, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'message': f'Статистика экспортирована: {filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Ошибка при экспорте статистики'
        }), 500

@app.route('/api/export/files')
def list_exported_files():
    """Список экспортированных файлов"""
    try:
        files = []
        for filename in os.listdir(export_dir):
            filepath = os.path.join(export_dir, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                files.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Сортируем по дате создания (новые сверху)
        files.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            'success': True,
            'files': files,
            'count': len(files)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Ошибка при получении списка файлов'
        }), 500

@app.route('/api/export/download/<filename>')
def download_file(filename):
    """Скачивание экспортированного файла"""
    try:
        filepath = os.path.join(export_dir, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({
                'success': False,
                'error': 'Файл не найден',
                'message': f'Файл {filename} не существует'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Ошибка при скачивании файла'
        }), 500

if __name__ == '__main__':
    print("⚠️ ReportLab не установлен. PDF экспорт будет недоступен.")
    print("📤 Запуск Simple Export API Server...")
    print("📊 API будет доступно по адресу: http://localhost:5002")
    print("🔧 Документация: http://localhost:5002/api/export/health")
    print("🛑 Для остановки нажмите Ctrl+C")
    
    app.run(host='127.0.0.1', port=5002, debug=False, threaded=True)