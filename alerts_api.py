#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API для системы алертов ALADDIN
REST API для управления алертами

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-08
"""

import json
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# Импорт системы алертов
try:
    from security.advanced_alerting_system import alerting_system, AlertRule, AlertType, AlertSeverity, AlertChannel
except ImportError as e:
    print(f"Предупреждение: Не удалось импортировать систему алертов: {e}")
    alerting_system = None

app = Flask(__name__)
CORS(app)

@app.route('/api/alerts/health')
def health_check():
    """Проверка состояния API алертов"""
    return jsonify({
        'status': 'healthy',
        'service': 'ALADDIN Alerts API',
        'version': '1.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/alerts/active')
def get_active_alerts():
    """Получение активных алертов"""
    try:
        if not alerting_system:
            return jsonify({'error': 'Система алертов недоступна'}), 500
        
        alerts = alerting_system.get_active_alerts()
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'rule_name': alert.rule_name,
                'alert_type': alert.alert_type.value,
                'severity': alert.severity.value,
                'title': alert.title,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'metadata': alert.metadata,
                'resolved': alert.resolved
            })
        
        return jsonify({
            'success': True,
            'alerts': alerts_data,
            'count': len(alerts_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts/history')
def get_alert_history():
    """Получение истории алертов"""
    try:
        if not alerting_system:
            return jsonify({'error': 'Система алертов недоступна'}), 500
        
        limit = request.args.get('limit', 100, type=int)
        alerts = alerting_system.get_alert_history(limit)
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'rule_name': alert.rule_name,
                'alert_type': alert.alert_type.value,
                'severity': alert.severity.value,
                'title': alert.title,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'resolved': alert.resolved,
                'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
                'metadata': alert.metadata
            })
        
        return jsonify({
            'success': True,
            'alerts': alerts_data,
            'count': len(alerts_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts/resolve/<alert_id>', methods=['POST'])
def resolve_alert(alert_id):
    """Разрешение алерта"""
    try:
        if not alerting_system:
            return jsonify({'error': 'Система алертов недоступна'}), 500
        
        success = alerting_system.resolve_alert(alert_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Алерт {alert_id} разрешен'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Алерт не найден'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts/statistics')
def get_alert_statistics():
    """Получение статистики алертов"""
    try:
        if not alerting_system:
            return jsonify({'error': 'Система алертов недоступна'}), 500
        
        stats = alerting_system.get_alert_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts/rules')
def get_alert_rules():
    """Получение правил алертов"""
    try:
        if not alerting_system:
            return jsonify({'error': 'Система алертов недоступна'}), 500
        
        rules_data = []
        for rule in alerting_system.alert_rules:
            rules_data.append({
                'name': rule.name,
                'description': rule.description,
                'alert_type': rule.alert_type.value,
                'severity': rule.severity.value,
                'condition': rule.condition,
                'channels': [ch.value for ch in rule.channels],
                'cooldown': rule.cooldown,
                'enabled': rule.enabled
            })
        
        return jsonify({
            'success': True,
            'rules': rules_data,
            'count': len(rules_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts/rules/<rule_name>/toggle', methods=['POST'])
def toggle_rule(rule_name):
    """Включение/выключение правила"""
    try:
        if not alerting_system:
            return jsonify({'error': 'Система алертов недоступна'}), 500
        
        success = alerting_system.update_rule(rule_name, enabled=not alerting_system.alert_rules[0].enabled)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Правило {rule_name} переключено'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Правило не найдено'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts/check', methods=['POST'])
def check_alerts():
    """Проверка данных на алерты"""
    try:
        if not alerting_system:
            return jsonify({'error': 'Система алертов недоступна'}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Данные не предоставлены'}), 400
        
        alerts = alerting_system.check_alerts(data)
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'rule_name': alert.rule_name,
                'alert_type': alert.alert_type.value,
                'severity': alert.severity.value,
                'title': alert.title,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'metadata': alert.metadata
            })
        
        return jsonify({
            'success': True,
            'alerts': alerts_data,
            'count': len(alerts_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts/webhook', methods=['POST'])
def webhook_receiver():
    """Получение webhook уведомлений"""
    try:
        data = request.get_json()
        print(f"🔗 Получен webhook: {data}")
        
        return jsonify({
            'success': True,
            'message': 'Webhook получен'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚨 Запуск ALADDIN Alerts API...")
    print("📊 API будет доступно по адресу: http://localhost:5003")
    print("🔧 Документация: http://localhost:5003/api/alerts/health")
    print("🛑 Для остановки нажмите Ctrl+C")
    
    try:
        app.run(host='0.0.0.0', port=5003, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 API остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска API: {e}")