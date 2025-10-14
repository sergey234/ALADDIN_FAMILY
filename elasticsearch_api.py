#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Elasticsearch API
API для интеграции поиска по логам с дашбордом

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-08
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, request
from flask_cors import CORS

from elasticsearch_simulator import ElasticsearchSimulator, LogLevel, LogEntry

app = Flask(__name__)
CORS(app)

# Глобальный экземпляр симулятора
es_simulator = ElasticsearchSimulator()

@app.route('/api/elasticsearch/health')
def health_check():
    """Проверка здоровья Elasticsearch"""
    try:
        stats = es_simulator.get_statistics()
        return jsonify({
            'status': 'healthy',
            'elasticsearch': 'running',
            'total_logs': stats['total_logs'],
            'indices': len(stats['indices']),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/elasticsearch/search')
def search_logs():
    """Поиск по логам с поддержкой регулярных выражений"""
    try:
        # Параметры запроса
        query = request.args.get('q', '')
        index = request.args.get('index', 'system_logs')
        level = request.args.get('level')
        component = request.args.get('component')
        limit = int(request.args.get('limit', 50))
        use_regex = request.args.get('regex', 'false').lower() == 'true'
        case_sensitive = request.args.get('case_sensitive', 'false').lower() == 'true'
        
        # Преобразование уровня лога
        log_level = None
        if level:
            try:
                log_level = LogLevel(level.upper())
            except ValueError:
                pass
        
        # Выполнение поиска
        results = es_simulator.search(
            query=query,
            index=index,
            level=log_level,
            component=component,
            use_regex=use_regex,
            case_sensitive=case_sensitive,
            limit=limit
        )
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'hits': 0,
            'logs': []
        }), 500

@app.route('/api/elasticsearch/indices')
def list_indices():
    """Список индексов"""
    try:
        stats = es_simulator.get_statistics()
        indices = []
        
        for name, count in stats['indices'].items():
            indices.append({
                'name': name,
                'document_count': count,
                'status': 'open'
            })
        
        return jsonify({
            'indices': indices,
            'total': len(indices)
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'indices': []
        }), 500

@app.route('/api/elasticsearch/stats')
def get_stats():
    """Статистика Elasticsearch"""
    try:
        stats = es_simulator.get_statistics()
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/elasticsearch/logs/recent')
def get_recent_logs():
    """Получение последних логов"""
    try:
        limit = int(request.args.get('limit', 20))
        level = request.args.get('level')
        
        # Преобразование уровня лога
        log_level = None
        if level:
            try:
                log_level = LogLevel(level.upper())
            except ValueError:
                pass
        
        # Поиск без запроса (все логи)
        results = es_simulator.search(
            query='',
            level=log_level,
            limit=limit
        )
        
        return jsonify({
            'logs': results['logs'],
            'total': results['total'],
            'hits': results['hits']
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'logs': []
        }), 500

@app.route('/api/elasticsearch/logs/levels')
def get_log_levels():
    """Получение распределения по уровням логов"""
    try:
        stats = es_simulator.get_statistics()
        return jsonify({
            'levels': stats['level_distribution'],
            'total': stats['total_logs']
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'levels': {}
        }), 500

@app.route('/api/elasticsearch/logs/components')
def get_log_components():
    """Получение распределения по компонентам"""
    try:
        stats = es_simulator.get_statistics()
        return jsonify({
            'components': stats['component_distribution'],
            'total': stats['total_logs']
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'components': {}
        }), 500

@app.route('/api/elasticsearch/index', methods=['POST'])
def index_log():
    """Индексация нового лога"""
    try:
        data = request.get_json()
        
        # Создание записи лога
        log_entry = LogEntry(
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.now(),
            level=LogLevel(data['level'].upper()),
            component=data['component'],
            message=data['message'],
            metadata=data.get('metadata', {}),
            log_id=data.get('log_id', '')
        )
        
        # Индексация
        success = es_simulator.index_log(log_entry)
        
        if success:
            return jsonify({
                'success': True,
                'log_id': log_entry.log_id,
                'message': 'Лог успешно проиндексирован'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Ошибка индексации лога'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/elasticsearch/bulk', methods=['POST'])
def bulk_index():
    """Массовая индексация логов"""
    try:
        data = request.get_json()
        logs_data = data.get('logs', [])
        
        # Создание записей логов
        logs = []
        for log_data in logs_data:
            log_entry = LogEntry(
                timestamp=datetime.fromisoformat(log_data['timestamp']) if 'timestamp' in log_data else datetime.now(),
                level=LogLevel(log_data['level'].upper()),
                component=log_data['component'],
                message=log_data['message'],
                metadata=log_data.get('metadata', {}),
                log_id=log_data.get('log_id', '')
            )
            logs.append(log_entry)
        
        # Массовая индексация
        result = es_simulator.bulk_index(logs)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/elasticsearch/indices/<index_name>', methods=['POST'])
def create_index(index_name):
    """Создание нового индекса"""
    try:
        success = es_simulator.create_index(index_name)
        
        if success:
            return jsonify({
                'success': True,
                'index': index_name,
                'message': f'Индекс {index_name} создан'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Индекс {index_name} уже существует'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/elasticsearch/indices/<index_name>', methods=['DELETE'])
def delete_index(index_name):
    """Удаление индекса"""
    try:
        success = es_simulator.delete_index(index_name)
        
        if success:
            return jsonify({
                'success': True,
                'index': index_name,
                'message': f'Индекс {index_name} удален'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Индекс {index_name} не найден'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🔍 Запуск Elasticsearch API Server...")
    print("📊 API будет доступно по адресу: http://localhost:5001")
    print("🔧 Документация: http://localhost:5001/api/elasticsearch/health")
    print("🛑 Для остановки нажмите Ctrl+C")
    
    try:
        app.run(host='127.0.0.1', port=5001, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Elasticsearch API Server остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")