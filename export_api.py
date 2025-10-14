#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Export API
API для экспорта данных в различные форматы

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-08
"""

from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from export_manager import ExportManager
from elasticsearch_simulator import ElasticsearchSimulator, LogLevel, LogEntry

app = Flask(__name__)
CORS(app)

# Инициализация компонентов
export_manager = ExportManager()
es_simulator = ElasticsearchSimulator()


@app.route('/api/export/health')
def health_check():
    """Проверка здоровья API экспорта"""
    return jsonify({
        'status': 'healthy',
        'service': 'Export API',
        'timestamp': datetime.now().isoformat(),
        'formats': ['CSV', 'JSON', 'PDF'],
        'export_dir': export_manager.export_dir
    })


@app.route('/api/export/logs/csv')
def export_logs_csv():
    """Экспорт логов в CSV формат"""
    try:
        # Параметры запроса
        query = request.args.get('q', '')
        index = request.args.get('index', 'system_logs')
        level = request.args.get('level')
        component = request.args.get('component')
        limit = int(request.args.get('limit', 1000))
        use_regex = request.args.get('regex', 'false').lower() == 'true'
        case_sensitive = request.args.get('case_sensitive', 'false').lower() == 'true'
        
        # Преобразование уровня лога
        log_level = None
        if level:
            try:
                log_level = LogLevel(level.upper())
            except ValueError:
                pass
        
        # Поиск логов
        results = es_simulator.search(
            query=query,
            index=index,
            level=log_level,
            component=component,
            use_regex=use_regex,
            case_sensitive=case_sensitive,
            limit=limit
        )
        
        # Получаем объекты LogEntry из результатов
        logs = []
        for log_dict in results.get('logs', []):
            # Преобразуем словарь обратно в LogEntry
            log_entry = LogEntry(
                timestamp=datetime.fromisoformat(log_dict['timestamp']),
                level=LogLevel(log_dict['level']),
                component=log_dict['component'],
                message=log_dict['message'],
                metadata=log_dict['metadata'],
                log_id=log_dict['log_id']
            )
            logs.append(log_entry)
        
        # Экспорт в CSV
        filename = f"aladdin_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = export_manager.export_logs_csv(logs, filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'total_logs': len(logs),
            'export_format': 'CSV',
            'download_url': f'/api/export/download/{filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export/logs/json')
def export_logs_json():
    """Экспорт логов в JSON формат"""
    try:
        # Параметры запроса (аналогично CSV)
        query = request.args.get('q', '')
        index = request.args.get('index', 'system_logs')
        level = request.args.get('level')
        component = request.args.get('component')
        limit = int(request.args.get('limit', 1000))
        use_regex = request.args.get('regex', 'false').lower() == 'true'
        case_sensitive = request.args.get('case_sensitive', 'false').lower() == 'true'
        
        # Преобразование уровня лога
        log_level = None
        if level:
            try:
                log_level = LogLevel(level.upper())
            except ValueError:
                pass
        
        # Поиск логов
        results = es_simulator.search(
            query=query,
            index=index,
            level=log_level,
            component=component,
            use_regex=use_regex,
            case_sensitive=case_sensitive,
            limit=limit
        )
        
        # Получаем объекты LogEntry из результатов
        logs = []
        for log_dict in results.get('logs', []):
            log_entry = LogEntry(
                timestamp=datetime.fromisoformat(log_dict['timestamp']),
                level=LogLevel(log_dict['level']),
                component=log_dict['component'],
                message=log_dict['message'],
                metadata=log_dict['metadata'],
                log_id=log_dict['log_id']
            )
            logs.append(log_entry)
        
        # Экспорт в JSON
        filename = f"aladdin_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = export_manager.export_logs_json(logs, filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'total_logs': len(logs),
            'export_format': 'JSON',
            'download_url': f'/api/export/download/{filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export/logs/pdf')
def export_logs_pdf():
    """Экспорт логов в PDF формат"""
    try:
        # Параметры запроса (аналогично CSV)
        query = request.args.get('q', '')
        index = request.args.get('index', 'system_logs')
        level = request.args.get('level')
        component = request.args.get('component')
        limit = int(request.args.get('limit', 1000))
        use_regex = request.args.get('regex', 'false').lower() == 'true'
        case_sensitive = request.args.get('case_sensitive', 'false').lower() == 'true'
        
        # Преобразование уровня лога
        log_level = None
        if level:
            try:
                log_level = LogLevel(level.upper())
            except ValueError:
                pass
        
        # Поиск логов
        results = es_simulator.search(
            query=query,
            index=index,
            level=log_level,
            component=component,
            use_regex=use_regex,
            case_sensitive=case_sensitive,
            limit=limit
        )
        
        # Получаем объекты LogEntry из результатов
        logs = []
        for log_dict in results.get('logs', []):
            log_entry = LogEntry(
                timestamp=datetime.fromisoformat(log_dict['timestamp']),
                level=LogLevel(log_dict['level']),
                component=log_dict['component'],
                message=log_dict['message'],
                metadata=log_dict['metadata'],
                log_id=log_dict['log_id']
            )
            logs.append(log_entry)
        
        # Экспорт в PDF
        filename = f"aladdin_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = export_manager.export_logs_pdf(logs, filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'total_logs': len(logs),
            'export_format': 'PDF',
            'download_url': f'/api/export/download/{filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export/stats')
def export_system_stats():
    """Экспорт статистики системы"""
    try:
        # Получаем статистику из Elasticsearch
        stats = es_simulator.get_statistics()
        
        # Экспорт статистики
        filename = f"aladdin_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = export_manager.export_system_stats(stats, filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'export_format': 'System Statistics JSON',
            'download_url': f'/api/export/download/{filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export/files')
def list_export_files():
    """Список экспортированных файлов"""
    try:
        files = export_manager.get_export_list()
        
        # Добавляем URL для скачивания
        for file_info in files:
            file_info['download_url'] = f'/api/export/download/{file_info["filename"]}'
        
        return jsonify({
            'success': True,
            'files': files,
            'total_files': len(files)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export/download/<filename>')
def download_file(filename):
    """Скачивание экспортированного файла"""
    try:
        return send_from_directory(export_manager.export_dir, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'Файл не найден'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export/delete/<filename>')
def delete_file(filename):
    """Удаление экспортированного файла"""
    try:
        success = export_manager.delete_export(filename)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Файл {filename} удален'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Файл не найден'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("📤 Запуск Export API Server...")
    print("📊 API будет доступно по адресу: http://localhost:5002")
    print("🔧 Документация: http://localhost:5002/api/export/health")
    print("🛑 Для остановки нажмите Ctrl+C")
    
    try:
        app.run(host='127.0.0.1', port=5002, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Export API Server остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")