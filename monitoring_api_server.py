#!/usr/bin/env python3
"""
ALADDIN Security System - Monitoring API Server
API сервер для расширенного мониторинга системы
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from security.advanced_monitoring_manager import advanced_monitoring_manager, MetricType, AlertSeverity, MonitoringRule
from core.logging_module import LoggingManager
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)
logger = LoggingManager(name="MonitoringAPIServer")

@app.route('/api/monitoring/health', methods=['GET'])
def health_check():
    """Проверка здоровья API мониторинга"""
    logger.log("INFO", "Health check запрошен для Monitoring API Server")
    try:
        status = advanced_monitoring_manager.get_status()
        return jsonify({
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "manager_status": status
        }), 200
    except Exception as e:
        logger.log("ERROR", f"Ошибка health check: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/monitoring/metrics', methods=['GET'])
def get_metrics():
    """Получение метрик"""
    try:
        metric_name = request.args.get('metric_name')
        limit = int(request.args.get('limit', 100))
        
        metrics = advanced_monitoring_manager.get_metrics(metric_name, limit)
        
        logger.log("INFO", f"Запрошены метрики: {metric_name or 'all'}, limit={limit}")
        return jsonify({
            "status": "success",
            "data": metrics,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.log("ERROR", f"Ошибка получения метрик: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/monitoring/alerts', methods=['GET'])
def get_alerts():
    """Получение алертов"""
    try:
        severity = request.args.get('severity')
        limit = int(request.args.get('limit', 50))
        
        if severity:
            severity = AlertSeverity(severity)
        
        alerts = advanced_monitoring_manager.get_alerts(severity, limit)
        
        logger.log("INFO", f"Запрошены алерты: severity={severity}, limit={limit}")
        return jsonify({
            "status": "success",
            "data": alerts,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.log("ERROR", f"Ошибка получения алертов: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/monitoring/dashboard', methods=['GET'])
def get_dashboard():
    """Получение данных для дашборда"""
    try:
        dashboard_data = advanced_monitoring_manager.get_dashboard_data()
        
        logger.log("INFO", "Запрошены данные дашборда")
        return jsonify({
            "status": "success",
            "data": dashboard_data,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.log("ERROR", f"Ошибка получения данных дашборда: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/monitoring/rules', methods=['GET'])
def get_rules():
    """Получение правил мониторинга"""
    try:
        rules = []
        for rule in advanced_monitoring_manager.monitoring_rules.values():
            rules.append({
                "rule_id": rule.rule_id,
                "name": rule.name,
                "metric_name": rule.metric_name,
                "condition": rule.condition,
                "threshold": rule.threshold,
                "severity": rule.severity.value,
                "enabled": rule.enabled,
                "cooldown": rule.cooldown,
                "last_triggered": rule.last_triggered.isoformat() if rule.last_triggered else None
            })
        
        logger.log("INFO", f"Запрошены правила мониторинга: {len(rules)} правил")
        return jsonify({
            "status": "success",
            "data": rules,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.log("ERROR", f"Ошибка получения правил: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/monitoring/rules', methods=['POST'])
def add_rule():
    """Добавление правила мониторинга"""
    try:
        data = request.get_json()
        
        rule = MonitoringRule(
            rule_id=data['rule_id'],
            name=data['name'],
            metric_name=data['metric_name'],
            condition=data['condition'],
            threshold=float(data['threshold']),
            severity=AlertSeverity(data['severity']),
            enabled=data.get('enabled', True),
            cooldown=data.get('cooldown', 300)
        )
        
        success = advanced_monitoring_manager.add_monitoring_rule(rule)
        
        if success:
            logger.log("INFO", f"Добавлено правило мониторинга: {rule.name}")
            return jsonify({
                "status": "success",
                "message": f"Правило '{rule.name}' добавлено",
                "timestamp": datetime.now().isoformat()
            }), 201
        else:
            return jsonify({
                "status": "error",
                "message": "Ошибка добавления правила"
            }), 400
            
    except Exception as e:
        logger.log("ERROR", f"Ошибка добавления правила: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/monitoring/rules/<rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    """Удаление правила мониторинга"""
    try:
        success = advanced_monitoring_manager.remove_monitoring_rule(rule_id)
        
        if success:
            logger.log("INFO", f"Удалено правило мониторинга: {rule_id}")
            return jsonify({
                "status": "success",
                "message": f"Правило '{rule_id}' удалено",
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Правило не найдено"
            }), 404
            
    except Exception as e:
        logger.log("ERROR", f"Ошибка удаления правила: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/monitoring/custom-metric', methods=['POST'])
def add_custom_metric():
    """Добавление пользовательской метрики"""
    try:
        data = request.get_json()
        
        metric_name = data['metric_name']
        value = float(data['value'])
        metric_type = MetricType(data.get('metric_type', 'custom'))
        unit = data.get('unit', '')
        tags = data.get('tags', {})
        
        advanced_monitoring_manager._add_metric(metric_name, value, metric_type, unit, tags)
        
        logger.log("INFO", f"Добавлена пользовательская метрика: {metric_name} = {value}")
        return jsonify({
            "status": "success",
            "message": f"Метрика '{metric_name}' добавлена",
            "timestamp": datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        logger.log("ERROR", f"Ошибка добавления пользовательской метрики: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/monitoring/status', methods=['GET'])
def get_status():
    """Получение статуса мониторинга"""
    try:
        status = advanced_monitoring_manager.get_status()
        
        logger.log("INFO", "Запрошен статус мониторинга")
        return jsonify({
            "status": "success",
            "data": status,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.log("ERROR", f"Ошибка получения статуса: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/monitoring/test', methods=['POST'])
def test_monitoring():
    """Тестирование мониторинга"""
    try:
        # Добавляем тестовые метрики
        advanced_monitoring_manager._add_metric(
            "test.cpu_high", 85.0, MetricType.SYSTEM, "percent", {"test": "true"}
        )
        advanced_monitoring_manager._add_metric(
            "test.memory_high", 90.0, MetricType.SYSTEM, "percent", {"test": "true"}
        )
        advanced_monitoring_manager._add_metric(
            "test.custom_metric", 42.0, MetricType.CUSTOM, "units", {"test": "true"}
        )
        
        # Принудительная проверка правил
        advanced_monitoring_manager._check_monitoring_rules()
        
        logger.log("INFO", "Выполнен тест мониторинга")
        return jsonify({
            "status": "success",
            "message": "Тест мониторинга выполнен",
            "test_metrics_added": 3,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.log("ERROR", f"Ошибка тестирования мониторинга: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Запуск Monitoring API Server...")
    print("📊 API будет доступно по адресу: http://localhost:5006")
    print("🔧 Health check: http://localhost:5006/api/monitoring/health")
    print("📈 Dashboard: http://localhost:5006/api/monitoring/dashboard")
    print("🛑 Для остановки нажмите Ctrl+C")
    
    try:
        app.run(host='0.0.0.0', port=5006, debug=False, threaded=True)
    except KeyboardInterrupt:
        logger.log("CRITICAL", "\n🛑 Monitoring API Server остановлен")
    except Exception as e:
        logger.log("ERROR", f"❌ Ошибка запуска Monitoring API Server: {e}")