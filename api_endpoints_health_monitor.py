#!/usr/bin/env python3
"""
🚀 ALADDIN API ENDPOINTS HEALTH MONITOR & VALIDATOR
Автоматическая система мониторинга и валидации всех 187 эндпоинтов

Функциональность:
- Полная проверка всех эндпоинтов каждые 5 минут
- Детальный анализ HTTP статусов, времени ответа, SFM интеграции
- Автоматические алерты при обнаружении проблем
- Веб-dashboard для визуального мониторинга
- JSON API для интеграции с внешними системами
- Логирование всех проверок для аудита

Автор: ALADDIN AI Assistant
Версия: 2.1.0
Дата: 2026-02-04
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import sys
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
import threading
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

# Конфигурация
API_BASE_URL = "http://localhost:8002"
MONITORING_INTERVAL = 300  # 5 минут
ALERT_EMAIL = "admin@aladdin.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "alerts@aladdin.com"
SMTP_PASS = "your_password_here"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_health_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class APIHealthMonitor:
    """Основной класс мониторинга API эндпоинтов"""

    def __init__(self):
        self.endpoints = self._load_endpoints_config()
        self.db_path = Path("api_health_monitor.db")
        self._init_database()
        self.last_check_results = {}
        self.alerts_sent = set()

    def _load_endpoints_config(self) -> Dict:
        """Загрузка конфигурации всех эндпоинтов"""
        try:
            with open('ALADDIN_COMPLETE_SYSTEM_ARCHITECTURE_AND_API_REFERENCE.md', 'r', encoding='utf-8') as f:
                content = f.read()

            # Парсим эндпоинты из документации
            endpoints = {}
            current_category = None

            for line in content.split('\n'):
                if line.startswith('## ') and any(keyword in line.upper() for keyword in
                    ['AUTHENTICATION', 'SUBSCRIPTION', 'NOTIFICATIONS', 'PARENTAL', 'IDENTITY',
                     'DARK WEB', 'LOCATION', 'DATA CLEANUP', 'ANTI-TRACKER', 'ROADSIDE',
                     'SYSTEM', 'ANALYTICS', 'AI', 'COMPONENTS', 'ANTI-PHISHING', 'ANTIVIRUS',
                     'MOBILE', 'HEALTH', 'SETTINGS', 'ADDITIONAL']):
                    current_category = line.replace('## ', '').strip()

                if current_category and ('GET /api/' in line or 'POST /api/' in line or 'PUT /api/' in line or 'DELETE /api/' in line):
                    method, path = line.split(' /api/', 1)
                    path = f"/api/{path.split()[0]}"
                    method = method.strip()

                    if current_category not in endpoints:
                        endpoints[current_category] = []

                    endpoints[current_category].append({
                        'method': method,
                        'path': path,
                        'expected_status': 200,
                        'timeout': 5.0
                    })

            return endpoints
        except Exception as e:
            logger.error(f"Error loading endpoints config: {e}")
            # Fallback: базовая конфигурация
            return self._get_fallback_endpoints()

    def _get_fallback_endpoints(self) -> Dict:
        """Базовая конфигурация эндпоинтов если документация недоступна"""
        return {
            "Health Checks": [
                {"method": "GET", "path": "/api/health", "expected_status": 200, "timeout": 2.0},
                {"method": "GET", "path": "/api/system/health", "expected_status": 200, "timeout": 2.0}
            ],
            "Authentication": [
                {"method": "POST", "path": "/api/auth/login", "expected_status": 200, "timeout": 3.0},
                {"method": "GET", "path": "/api/auth/profile", "expected_status": 200, "timeout": 2.0}
            ]
        }

    def _init_database(self):
        """Инициализация базы данных для хранения результатов мониторинга"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS health_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    category TEXT,
                    method TEXT,
                    path TEXT,
                    status_code INTEGER,
                    response_time REAL,
                    sfm_integration BOOLEAN,
                    error_message TEXT,
                    success BOOLEAN
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    endpoint TEXT,
                    alert_type TEXT,
                    message TEXT,
                    resolved BOOLEAN DEFAULT FALSE
                )
            ''')

            conn.commit()

    async def check_endpoint(self, session: aiohttp.ClientSession, category: str,
                           endpoint_config: Dict) -> Dict:
        """Проверка одного эндпоинта"""
        method = endpoint_config['method']
        path = endpoint_config['path']
        expected_status = endpoint_config['expected_status']
        timeout = endpoint_config['timeout']

        url = f"{API_BASE_URL}{path}"
        start_time = time.time()

        try:
            async with session.request(method, url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                response_time = time.time() - start_time
                status_code = response.status

                # Проверяем SFM интеграцию
                response_text = await response.text()
                sfm_integration = '"source": "real_sfm"' in response_text

                success = status_code == expected_status and sfm_integration

                result = {
                    'category': category,
                    'method': method,
                    'path': path,
                    'status_code': status_code,
                    'response_time': round(response_time, 3),
                    'sfm_integration': sfm_integration,
                    'success': success,
                    'error_message': None,
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            response_time = time.time() - start_time
            result = {
                'category': category,
                'method': method,
                'path': path,
                'status_code': None,
                'response_time': round(response_time, 3),
                'sfm_integration': False,
                'success': False,
                'error_message': str(e),
                'timestamp': datetime.now().isoformat()
            }

        # Сохраняем результат в базу данных
        self._save_result(result)

        # Проверяем на алерты
        self._check_alerts(result)

        return result

    async def check_all_endpoints(self) -> Dict:
        """Проверка всех эндпоинтов"""
        logger.info("🔍 Starting full API health check...")

        async with aiohttp.ClientSession() as session:
            tasks = []

            for category, endpoints in self.endpoints.items():
                for endpoint in endpoints:
                    task = self.check_endpoint(session, category, endpoint)
                    tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Обрабатываем результаты
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_endpoints': len(results),
            'successful': 0,
            'failed': 0,
            'average_response_time': 0,
            'categories': {},
            'details': []
        }

        total_response_time = 0

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Task failed with exception: {result}")
                continue

            summary['details'].append(result)

            if result['success']:
                summary['successful'] += 1
            else:
                summary['failed'] += 1

            total_response_time += result['response_time']

            # Статистика по категориям
            cat = result['category']
            if cat not in summary['categories']:
                summary['categories'][cat] = {'total': 0, 'success': 0, 'failed': 0}

            summary['categories'][cat]['total'] += 1
            if result['success']:
                summary['categories'][cat]['success'] += 1
            else:
                summary['categories'][cat]['failed'] += 1

        summary['average_response_time'] = round(total_response_time / len(results), 3)
        summary['success_rate'] = round((summary['successful'] / summary['total_endpoints']) * 100, 2)

        self.last_check_results = summary

        logger.info(f"✅ Health check completed: {summary['successful']}/{summary['total_endpoints']} endpoints OK")

        return summary

    def _save_result(self, result: Dict):
        """Сохранение результата в базу данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO health_checks
                    (category, method, path, status_code, response_time, sfm_integration, error_message, success)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result['category'],
                    result['method'],
                    result['path'],
                    result['status_code'],
                    result['response_time'],
                    result['sfm_integration'],
                    result['error_message'],
                    result['success']
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving result to database: {e}")

    def _check_alerts(self, result: Dict):
        """Проверка и отправка алертов"""
        endpoint_key = f"{result['method']} {result['path']}"

        if not result['success']:
            alert_key = f"failure_{endpoint_key}"

            if alert_key not in self.alerts_sent:
                self._send_alert(
                    f"🚨 API ENDPOINT FAILURE ALERT 🚨\n\n"
                    f"Endpoint: {endpoint_key}\n"
                    f"Category: {result['category']}\n"
                    f"Status: {'DOWN' if result['status_code'] is None else f'HTTP {result['status_code']}'}\n"
                    f"Response Time: {result['response_time']}s\n"
                    f"SFM Integration: {'✅' if result['sfm_integration'] else '❌'}\n"
                    f"Error: {result['error_message'] or 'Unknown'}\n"
                    f"Time: {result['timestamp']}\n\n"
                    f"Please check the API Gateway and SFM Core services."
                )
                self.alerts_sent.add(alert_key)

                # Сохраняем алерт в базу
                self._save_alert(endpoint_key, "FAILURE", result['error_message'] or "Endpoint down")

        elif endpoint_key in [key.replace('failure_', '') for key in self.alerts_sent]:
            # Если эндпоинт восстановился, отправляем алерт восстановления
            alert_key = f"recovery_{endpoint_key}"
            if alert_key not in self.alerts_sent:
                self._send_alert(
                    f"✅ API ENDPOINT RECOVERY ALERT ✅\n\n"
                    f"Endpoint: {endpoint_key}\n"
                    f"Category: {result['category']}\n"
                    f"Status: HTTP {result['status_code']}\n"
                    f"Response Time: {result['response_time']}s\n"
                    f"SFM Integration: ✅\n"
                    f"Time: {result['timestamp']}\n\n"
                    f"Endpoint has been restored to normal operation."
                )
                self.alerts_sent.add(alert_key)

                # Помечаем алерт как разрешенный
                self._resolve_alert(endpoint_key)

    def _send_alert(self, message: str):
        """Отправка email алерта"""
        try:
            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = ALERT_EMAIL
            msg['Subject'] = "ALADDIN API Health Alert"

            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, ALERT_EMAIL, msg.as_string())
            server.quit()

            logger.info(f"Alert sent to {ALERT_EMAIL}")
        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")

    def _save_alert(self, endpoint: str, alert_type: str, message: str):
        """Сохранение алерта в базу данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO alerts (endpoint, alert_type, message)
                    VALUES (?, ?, ?)
                ''', (endpoint, alert_type, message))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving alert to database: {e}")

    def _resolve_alert(self, endpoint: str):
        """Пометка алерта как разрешенного"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE alerts SET resolved = TRUE
                    WHERE endpoint = ? AND resolved = FALSE
                ''', (endpoint,))
                conn.commit()
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")

    def get_health_report(self, hours: int = 24) -> Dict:
        """Получение отчета о здоровье за последние N часов"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Общая статистика
                cursor = conn.execute('''
                    SELECT
                        COUNT(*) as total_checks,
                        SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
                        AVG(response_time) as avg_response_time,
                        MIN(timestamp) as oldest_check,
                        MAX(timestamp) as latest_check
                    FROM health_checks
                    WHERE timestamp >= datetime('now', '-{} hours')
                '''.format(hours))

                stats = cursor.fetchone()

                # Статистика по категориям
                cursor = conn.execute('''
                    SELECT
                        category,
                        COUNT(*) as total,
                        SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
                        AVG(response_time) as avg_time
                    FROM health_checks
                    WHERE timestamp >= datetime('now', '-{} hours')
                    GROUP BY category
                '''.format(hours))

                categories = {}
                for row in cursor.fetchall():
                    categories[row[0]] = {
                        'total': row[1],
                        'successful': row[2],
                        'success_rate': round((row[2] / row[1]) * 100, 2),
                        'avg_response_time': round(row[3], 3)
                    }

                # Недавние алерты
                cursor = conn.execute('''
                    SELECT endpoint, alert_type, message, timestamp
                    FROM alerts
                    WHERE timestamp >= datetime('now', '-{} hours') AND resolved = FALSE
                    ORDER BY timestamp DESC
                    LIMIT 10
                '''.format(hours))

                alerts = []
                for row in cursor.fetchall():
                    alerts.append({
                        'endpoint': row[0],
                        'type': row[1],
                        'message': row[2],
                        'timestamp': row[3]
                    })

                return {
                    'period_hours': hours,
                    'total_checks': stats[0],
                    'successful_checks': stats[1],
                    'success_rate': round((stats[1] / stats[0]) * 100, 2) if stats[0] > 0 else 0,
                    'avg_response_time': round(stats[2], 3) if stats[2] else 0,
                    'oldest_check': stats[3],
                    'latest_check': stats[4],
                    'categories': categories,
                    'recent_alerts': alerts
                }

        except Exception as e:
            logger.error(f"Error generating health report: {e}")
            return {'error': str(e)}

# FastAPI приложение для веб-интерфейса
app = FastAPI(title="ALADDIN API Health Monitor", version="2.1.0")

monitor = APIHealthMonitor()

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Главная dashboard страница"""
    report = monitor.get_health_report()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ALADDIN API Health Monitor</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.plotly.com/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .metric-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
            .status-good {{ color: #28a745; font-weight: bold; }}
            .status-warning {{ color: #ffc107; font-weight: bold; }}
            .status-error {{ color: #dc3545; font-weight: bold; }}
            .alert {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 ALADDIN API Health Monitor</h1>
            <p>Real-time monitoring of all 187 API endpoints</p>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="metric-grid">
            <div class="metric-card">
                <h3>Overall Health</h3>
                <div class="status-{'good' if report.get('success_rate', 0) > 95 else 'warning' if report.get('success_rate', 0) > 80 else 'error'}">
                    {report.get('success_rate', 0)}% Success Rate
                </div>
                <p>{report.get('successful_checks', 0)} / {report.get('total_checks', 0)} checks passed</p>
            </div>

            <div class="metric-card">
                <h3>Response Time</h3>
                <p>{report.get('avg_response_time', 0)}s average</p>
                <p>Target: <0.02s</p>
            </div>

            <div class="metric-card">
                <h3>Categories Monitored</h3>
                <p>{len(report.get('categories', {}))} categories</p>
                <p>187 total endpoints</p>
            </div>

            <div class="metric-card">
                <h3>Active Alerts</h3>
                <p>{len(report.get('recent_alerts', []))} alerts</p>
                <p>Monitoring: 24/7</p>
            </div>
        </div>

        <div class="metric-card">
            <h3>Categories Status</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #f8f9fa;">
                    <th style="padding: 10px; border: 1px solid #dee2e6;">Category</th>
                    <th style="padding: 10px; border: 1px solid #dee2e6;">Success Rate</th>
                    <th style="padding: 10px; border: 1px solid #dee2e6;">Total Checks</th>
                    <th style="padding: 10px; border: 1px solid #dee2e6;">Avg Response</th>
                </tr>
    """

    for category, stats in report.get('categories', {}).items():
        success_rate = stats.get('success_rate', 0)
        status_class = 'good' if success_rate > 95 else 'warning' if success_rate > 80 else 'error'

        html += f"""
                <tr>
                    <td style="padding: 10px; border: 1px solid #dee2e6;">{category}</td>
                    <td style="padding: 10px; border: 1px solid #dee2e6;" class="status-{status_class}">{success_rate}%</td>
                    <td style="padding: 10px; border: 1px solid #dee2e6;">{stats.get('total', 0)}</td>
                    <td style="padding: 10px; border: 1px solid #dee2e6;">{stats.get('avg_response_time', 0)}s</td>
                </tr>
        """

    html += """
            </table>
        </div>

        <div class="metric-card">
            <h3>Recent Alerts</h3>
    """

    if report.get('recent_alerts'):
        for alert in report['recent_alerts'][:5]:
            html += f"""
            <div class="alert">
                <strong>{alert['type']}</strong> - {alert['endpoint']}<br>
                <small>{alert['timestamp']} - {alert['message']}</small>
            </div>
            """
    else:
        html += "<p>No active alerts ✅</p>"

    html += """
        </div>

        <div style="text-align: center; margin-top: 20px; color: #666;">
            <p>ALADDIN API Health Monitor v2.1.0 | Real-time monitoring every 5 minutes</p>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=html)

@app.get("/api/health")
async def get_health_api():
    """JSON API для получения статуса здоровья"""
    return JSONResponse(content=monitor.get_health_report())

@app.post("/api/check-now")
async def trigger_check():
    """Принудительная проверка всех эндпоинтов"""
    results = await monitor.check_all_endpoints()
    return JSONResponse(content=results)

@app.get("/api/endpoints")
async def get_endpoints():
    """Получение списка всех эндпоинтов"""
    return JSONResponse(content=monitor.endpoints)

def start_monitoring_loop():
    """Запуск цикла мониторинга в отдельном потоке"""
    async def monitoring_loop():
        while True:
            try:
                await monitor.check_all_endpoints()
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")

            await asyncio.sleep(MONITORING_INTERVAL)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(monitoring_loop())

def main():
    """Главная функция"""
    logger.info("🚀 Starting ALADDIN API Health Monitor...")

    # Запуск мониторинга в фоне
    monitoring_thread = threading.Thread(target=start_monitoring_loop, daemon=True)
    monitoring_thread.start()

    # Запуск веб-сервера
    logger.info("🌐 Starting web dashboard on http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()