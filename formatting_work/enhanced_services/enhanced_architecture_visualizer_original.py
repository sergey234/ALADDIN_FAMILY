#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Real-time Architecture Visualizer для ALADDIN Security System
Мониторинг без Docker с реальными данными системы

Автор: ALADDIN Security Team
Версия: 2.0
Дата: 2025-01-06
"""

import os
import sys
import json
import asyncio
import psutil
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Импорты для интеграции с ALADDIN
try:
    from security.safe_function_manager import SafeFunctionManager, FunctionStatus
    from security.microservices.api_gateway import APIGateway
    from security.microservices.load_balancer import LoadBalancer
    from security.microservices.rate_limiter import RateLimiter
    from security.microservices.circuit_breaker import CircuitBreaker
    ALADDIN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ALADDIN modules not available: {e}")
    ALADDIN_AVAILABLE = False

# Создание FastAPI приложения
app = FastAPI(
    title="🏗️ ALADDIN Enhanced Architecture Visualizer",
    description="Real-time мониторинг архитектуры системы безопасности ALADDIN",
    version="2.0.0"
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ArchitectureManager:
    """Менеджер для мониторинга архитектуры ALADDIN"""
    
    def __init__(self):
        self.services: Dict[str, Dict[str, Any]] = {}
        self.connections: List[Dict[str, Any]] = []
        self.metrics: Dict[str, Any] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.db_path = "architecture_monitor.db"
        self.init_database()
        
        # Порты ALADDIN системы
        self.aladdin_ports = {
            "API Gateway": 8006,
            "Load Balancer": 8007,
            "Rate Limiter": 8008,
            "Circuit Breaker": 8009,
            "User Interface Manager": 8010,
            "SafeFunctionManager": 8011,
            "Service Mesh": 8012
        }
        
        # WebSocket соединения
        self.active_connections: List[WebSocket] = []
    
    def init_database(self):
        """Инициализация базы данных для хранения метрик"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS architecture_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp DATETIME NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS architecture_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                timestamp DATETIME NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def scan_architecture(self) -> Dict[str, Any]:
        """Сканирование архитектуры ALADDIN системы"""
        architecture = {
            "services": {},
            "connections": [],
            "metrics": {},
            "alerts": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Сканируем сервисы
        for service_name, port in self.aladdin_ports.items():
            service_info = await self._get_service_info(service_name, port)
            architecture["services"][service_name] = service_info
        
        # Сканируем соединения между сервисами
        architecture["connections"] = await self._scan_connections()
        
        # Получаем метрики системы
        architecture["metrics"] = await self._get_system_metrics()
        
        # Проверяем алерты
        architecture["alerts"] = await self._check_alerts()
        
        return architecture
    
    async def _get_service_info(self, service_name: str, port: int) -> Dict[str, Any]:
        """Получение информации о сервисе"""
        try:
            # Проверяем статус порта
            is_running = self._check_port_status(port)
            
            # Получаем информацию о процессе
            process_info = self._get_process_info(port)
            
            # Получаем метрики производительности
            performance_metrics = self._get_performance_metrics(port)
            
            # Получаем статус из SafeFunctionManager если доступен
            sfm_status = await self._get_sfm_status(service_name)
            
            service_info = {
                "name": service_name,
                "port": port,
                "status": "running" if is_running else "stopped",
                "uptime": process_info.get("uptime", 0),
                "cpu_usage": process_info.get("cpu_percent", 0),
                "memory_usage": process_info.get("memory_percent", 0),
                "memory_mb": process_info.get("memory_mb", 0),
                "pid": process_info.get("pid", None),
                "performance": performance_metrics,
                "sfm_status": sfm_status,
                "last_check": datetime.now().isoformat()
            }
            
            # Сохраняем метрики в базу данных
            self._save_metrics(service_name, performance_metrics)
            
            return service_info
            
        except Exception as e:
            print(f"Error getting service info for {service_name}: {e}")
            return {
                "name": service_name,
                "port": port,
                "status": "error",
                "uptime": 0,
                "cpu_usage": 0,
                "memory_usage": 0,
                "memory_mb": 0,
                "pid": None,
                "performance": {},
                "sfm_status": {},
                "last_check": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _check_port_status(self, port: int) -> bool:
        """Проверка статуса порта"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _get_process_info(self, port: int) -> Dict[str, Any]:
        """Получение информации о процессе по порту"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'create_time', 'cpu_percent', 'memory_percent', 'memory_info']):
                try:
                    connections = proc.connections()
                    for conn in connections:
                        if conn.laddr.port == port:
                            uptime = time.time() - proc.info['create_time']
                            memory_info = proc.info['memory_info']
                            return {
                                "pid": proc.info['pid'],
                                "name": proc.info['name'],
                                "uptime": uptime,
                                "cpu_percent": proc.info['cpu_percent'],
                                "memory_percent": proc.info['memory_percent'],
                                "memory_mb": memory_info.rss / 1024 / 1024 if memory_info else 0
                            }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"Error getting process info for port {port}: {e}")
        
        return {"uptime": 0, "cpu_percent": 0, "memory_percent": 0, "memory_mb": 0}
    
    def _get_performance_metrics(self, port: int) -> Dict[str, Any]:
        """Получение метрик производительности для порта"""
        try:
            # Получаем сетевую статистику
            net_io = psutil.net_io_counters()
            
            # Получаем дисковую статистику
            disk_io = psutil.disk_io_counters()
            
            return {
                "network_bytes_sent": net_io.bytes_sent,
                "network_bytes_recv": net_io.bytes_recv,
                "disk_read_bytes": disk_io.read_bytes if disk_io else 0,
                "disk_write_bytes": disk_io.write_bytes if disk_io else 0,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting performance metrics for port {port}: {e}")
            return {}
    
    async def _get_sfm_status(self, service_name: str) -> Dict[str, Any]:
        """Получение статуса из SafeFunctionManager"""
        if not ALADDIN_AVAILABLE:
            return {}
        
        try:
            # Здесь должна быть интеграция с SafeFunctionManager
            # Для демонстрации возвращаем mock данные
            return {
                "functions_enabled": 15,
                "functions_disabled": 3,
                "functions_testing": 2,
                "last_activity": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting SFM status for {service_name}: {e}")
            return {}
    
    async def _scan_connections(self) -> List[Dict[str, Any]]:
        """Сканирование соединений между сервисами"""
        connections = []
        
        try:
            # Получаем все активные соединения
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    proc_connections = proc.connections()
                    for conn in proc_connections:
                        if conn.laddr.port in self.aladdin_ports.values():
                            # Определяем сервис по порту
                            service_name = None
                            for name, port in self.aladdin_ports.items():
                                if port == conn.laddr.port:
                                    service_name = name
                                    break
                            
                            if service_name:
                                connections.append({
                                    "from": service_name,
                                    "to": f"External:{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "Local",
                                    "status": conn.status,
                                    "type": "tcp"
                                })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"Error scanning connections: {e}")
        
        return connections
    
    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Получение системных метрик"""
        try:
            # CPU метрики
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Память
            memory = psutil.virtual_memory()
            
            # Диск
            disk = psutil.disk_usage('/')
            
            # Сеть
            net_io = psutil.net_io_counters()
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "load_avg": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                },
                "network": {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting system metrics: {e}")
            return {}
    
    async def _check_alerts(self) -> List[Dict[str, Any]]:
        """Проверка алертов системы"""
        alerts = []
        
        try:
            # Проверяем статус сервисов
            for service_name, port in self.aladdin_ports.items():
                if not self._check_port_status(port):
                    alert = {
                        "service": service_name,
                        "type": "service_down",
                        "message": f"Сервис {service_name} недоступен на порту {port}",
                        "severity": "critical",
                        "timestamp": datetime.now().isoformat()
                    }
                    alerts.append(alert)
                    self._save_alert(alert)
            
            # Проверяем использование ресурсов
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                alert = {
                    "service": "System",
                    "type": "high_memory_usage",
                    "message": f"Высокое использование памяти: {memory.percent:.1f}%",
                    "severity": "warning",
                    "timestamp": datetime.now().isoformat()
                }
                alerts.append(alert)
                self._save_alert(alert)
            
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                alert = {
                    "service": "System",
                    "type": "high_cpu_usage",
                    "message": f"Высокое использование CPU: {cpu_percent:.1f}%",
                    "severity": "warning",
                    "timestamp": datetime.now().isoformat()
                }
                alerts.append(alert)
                self._save_alert(alert)
                
        except Exception as e:
            print(f"Error checking alerts: {e}")
        
        return alerts
    
    def _save_metrics(self, service_name: str, metrics: Dict[str, Any]):
        """Сохранение метрик в базу данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for metric_type, value in metrics.items():
                if isinstance(value, (int, float)):
                    cursor.execute('''
                        INSERT INTO architecture_metrics 
                        (service_name, metric_type, value, timestamp)
                        VALUES (?, ?, ?, ?)
                    ''', (service_name, metric_type, value, datetime.now()))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving metrics: {e}")
    
    def _save_alert(self, alert: Dict[str, Any]):
        """Сохранение алерта в базу данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO architecture_alerts 
                (service_name, alert_type, message, severity, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                alert["service"],
                alert["type"],
                alert["message"],
                alert["severity"],
                alert["timestamp"]
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving alert: {e}")
    
    async def broadcast_update(self, data: Dict[str, Any]):
        """Отправка обновления всем подключенным WebSocket клиентам"""
        if self.active_connections:
            message = json.dumps(data)
            disconnected = []
            
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.append(connection)
            
            # Удаляем отключенные соединения
            for connection in disconnected:
                self.active_connections.remove(connection)

# Глобальный экземпляр менеджера
arch_manager = ArchitectureManager()

# API Routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница Enhanced Architecture Visualizer"""
    return await get_enhanced_architecture_page()

@app.get("/api/architecture")
async def get_architecture():
    """Получение текущей архитектуры системы"""
    architecture = await arch_manager.scan_architecture()
    return architecture

@app.get("/api/services")
async def get_services():
    """Получение статуса всех сервисов"""
    architecture = await arch_manager.scan_architecture()
    return {"services": architecture["services"]}

@app.get("/api/metrics")
async def get_metrics():
    """Получение системных метрик"""
    architecture = await arch_manager.scan_architecture()
    return {"metrics": architecture["metrics"]}

@app.get("/api/alerts")
async def get_alerts():
    """Получение активных алертов"""
    architecture = await arch_manager.scan_architecture()
    return {"alerts": architecture["alerts"]}

@app.get("/api/filter")
async def filter_services(status: Optional[str] = None, service_type: Optional[str] = None):
    """Фильтрация сервисов по статусу и типу"""
    architecture = await arch_manager.scan_architecture()
    services = architecture["services"]
    
    filtered_services = {}
    for name, service in services.items():
        if status and service["status"] != status:
            continue
        if service_type and service_type.lower() not in name.lower():
            continue
        filtered_services[name] = service
    
    return {"services": filtered_services, "filters": {"status": status, "service_type": service_type}}

@app.get("/api/history")
async def get_architecture_history(hours: int = 24):
    """Получение истории изменений архитектуры"""
    # В реальной системе здесь должна быть история из базы данных
    # Для демонстрации возвращаем mock данные
    history = []
    current_time = datetime.now()
    
    for i in range(min(hours, 24)):
        timestamp = current_time - timedelta(hours=i)
        history.append({
            "timestamp": timestamp.isoformat(),
            "services_count": len(arch_manager.aladdin_ports),
            "running_services": len([p for p in arch_manager.aladdin_ports.values() if arch_manager._check_port_status(p)]),
            "alerts_count": 0
        })
    
    return {"history": history, "period_hours": hours}

@app.get("/api/export/3d")
async def export_3d_data():
    """Экспорт данных для 3D визуализации"""
    architecture = await arch_manager.scan_architecture()
    
    # Подготавливаем данные для Three.js
    nodes = []
    links = []
    
    for name, service in architecture["services"].items():
        nodes.append({
            "id": name,
            "name": name,
            "status": service["status"],
            "port": service["port"],
            "cpu": service["cpu_usage"],
            "memory": service["memory_usage"],
            "x": 0,  # Будет рассчитано в 3D сцене
            "y": 0,
            "z": 0
        })
    
    for connection in architecture["connections"]:
        links.append({
            "source": connection["from"],
            "target": connection["to"],
            "type": connection["type"]
        })
    
    return {
        "nodes": nodes,
        "links": links,
        "metadata": {
            "total_services": len(nodes),
            "total_connections": len(links),
            "timestamp": architecture["timestamp"]
        }
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для real-time обновлений"""
    await websocket.accept()
    arch_manager.active_connections.append(websocket)
    
    try:
        while True:
            # Отправляем обновления каждые 5 секунд
            architecture = await arch_manager.scan_architecture()
            await websocket.send_text(json.dumps(architecture))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        arch_manager.active_connections.remove(websocket)

async def get_enhanced_architecture_page():
    """Генерация HTML страницы с улучшенным UI"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🏗️ ALADDIN Enhanced Architecture Visualizer</title>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
                color: #ffffff;
                min-height: 100vh;
                overflow-x: hidden;
            }
            
            .container {
                max-width: 1600px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
                padding: 30px 0;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            
            .header h1 {
                font-size: 3em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .header p {
                font-size: 1.2em;
                opacity: 0.9;
            }
            
            .theme-toggle {
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(255, 255, 255, 0.1);
                border: none;
                color: white;
                padding: 10px 15px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1em;
                backdrop-filter: blur(10px);
            }
            
            .theme-toggle:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            
            .view-toggle {
                position: absolute;
                top: 20px;
                right: 120px;
                background: rgba(255, 255, 255, 0.1);
                border: none;
                color: white;
                padding: 10px 15px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1em;
                backdrop-filter: blur(10px);
            }
            
            .view-toggle:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            
            .light-theme {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                color: #333;
            }
            
            .light-theme .card {
                background: rgba(255, 255, 255, 0.9);
                color: #333;
            }
            
            .light-theme .service-card {
                background: rgba(0, 0, 0, 0.05);
            }
            
            .light-theme .alert-item {
                background: rgba(0, 0, 0, 0.05);
            }
            
            .three-container {
                width: 100%;
                height: 500px;
                border-radius: 10px;
                overflow: hidden;
                background: rgba(0, 0, 0, 0.1);
            }
            
            .status-bar {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding: 15px 25px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                backdrop-filter: blur(10px);
            }
            
            .status-item {
                text-align: center;
            }
            
            .status-number {
                font-size: 2em;
                font-weight: bold;
                color: #4CAF50;
            }
            
            .status-label {
                font-size: 0.9em;
                opacity: 0.8;
            }
            
            .main-content {
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 30px;
                margin-bottom: 30px;
            }
            
            .architecture-diagram {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 25px;
                backdrop-filter: blur(10px);
                min-height: 600px;
            }
            
            .services-panel {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 25px;
                backdrop-filter: blur(10px);
            }
            
            .service-card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                border-left: 4px solid #4CAF50;
            }
            
            .service-card.error {
                border-left-color: #F44336;
            }
            
            .service-card.warning {
                border-left-color: #FF9800;
            }
            
            .service-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            
            .service-name {
                font-weight: bold;
                font-size: 1.1em;
            }
            
            .service-status {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.8em;
                font-weight: bold;
            }
            
            .status-running {
                background: #4CAF50;
                color: white;
            }
            
            .status-stopped {
                background: #F44336;
                color: white;
            }
            
            .status-error {
                background: #FF9800;
                color: white;
            }
            
            .service-metrics {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                font-size: 0.9em;
                opacity: 0.8;
            }
            
            .alerts-panel {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 25px;
                backdrop-filter: blur(10px);
                margin-top: 30px;
            }
            
            .alert-item {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                border-left: 4px solid #F44336;
            }
            
            .alert-item.warning {
                border-left-color: #FF9800;
            }
            
            .alert-item.info {
                border-left-color: #2196F3;
            }
            
            .alert-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 5px;
            }
            
            .alert-service {
                font-weight: bold;
            }
            
            .alert-severity {
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 0.8em;
                font-weight: bold;
            }
            
            .severity-critical {
                background: #F44336;
                color: white;
            }
            
            .severity-warning {
                background: #FF9800;
                color: white;
            }
            
            .severity-info {
                background: #2196F3;
                color: white;
            }
            
            .alert-message {
                font-size: 0.9em;
                opacity: 0.9;
            }
            
            .alert-timestamp {
                font-size: 0.8em;
                opacity: 0.7;
                margin-top: 5px;
            }
            
            .connection-line {
                stroke: #4CAF50;
                stroke-width: 2;
                opacity: 0.7;
            }
            
            .service-node {
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .service-node:hover {
                transform: scale(1.1);
            }
            
            .service-node circle {
                fill: #4CAF50;
                stroke: #ffffff;
                stroke-width: 2;
            }
            
            .service-node.running circle {
                fill: #4CAF50;
            }
            
            .service-node.stopped circle {
                fill: #F44336;
            }
            
            .service-node.error circle {
                fill: #FF9800;
            }
            
            .service-node text {
                fill: #ffffff;
                font-size: 12px;
                text-anchor: middle;
                dominant-baseline: middle;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                font-size: 1.2em;
                opacity: 0.7;
            }
            
            .connection-info {
                position: absolute;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 0.9em;
                pointer-events: none;
                z-index: 1000;
            }
            
            @media (max-width: 1200px) {
                .main-content {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <button class="theme-toggle" onclick="toggleTheme()">🌙 Темная тема</button>
            <button class="view-toggle" onclick="toggleView()">🎯 2D вид</button>
            
            <div class="header">
                <h1>🏗️ ALADDIN Enhanced Architecture Visualizer</h1>
                <p>Real-time мониторинг архитектуры системы безопасности</p>
            </div>
            
            <div class="status-bar" id="status-bar">
                <div class="status-item">
                    <div class="status-number" id="total-services">-</div>
                    <div class="status-label">Сервисы</div>
                </div>
                <div class="status-item">
                    <div class="status-number" id="running-services">-</div>
                    <div class="status-label">Активные</div>
                </div>
                <div class="status-item">
                    <div class="status-number" id="total-alerts">-</div>
                    <div class="status-label">Алерты</div>
                </div>
                <div class="status-item">
                    <div class="status-number" id="system-cpu">-</div>
                    <div class="status-label">CPU %</div>
                </div>
                <div class="status-item">
                    <div class="status-number" id="system-memory">-</div>
                    <div class="status-label">RAM %</div>
                </div>
            </div>
            
            <div class="main-content">
                <div class="architecture-diagram">
                    <h2 style="margin-bottom: 20px; color: #4CAF50;">Архитектурная диаграмма</h2>
                    <div id="diagram-container">
                        <div class="loading">Загрузка диаграммы...</div>
                    </div>
                    <div id="3d-container" class="three-container" style="display: none;">
                        <div class="loading">Загрузка 3D визуализации...</div>
                    </div>
                </div>
                
                <div class="services-panel">
                    <h2 style="margin-bottom: 20px; color: #4CAF50;">Статус сервисов</h2>
                    <div id="services-list">
                        <div class="loading">Загрузка сервисов...</div>
                    </div>
                </div>
            </div>
            
            <div class="alerts-panel">
                <h2 style="margin-bottom: 20px; color: #4CAF50;">Активные алерты</h2>
                <div id="alerts-list">
                    <div class="loading">Загрузка алертов...</div>
                </div>
            </div>
        </div>
        
        <script>
            let architecture = {};
            let ws = null;
            let svg = null;
            let scene3d = null;
            let renderer3d = null;
            let camera3d = null;
            let controls3d = null;
            let is3DView = false;
            let isDarkTheme = true;
            
            // Инициализация WebSocket соединения
            function initWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws`;
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    console.log('WebSocket connected');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    architecture = data;
                    updateUI();
                };
                
                ws.onclose = function(event) {
                    console.log('WebSocket disconnected, reconnecting...');
                    setTimeout(initWebSocket, 5000);
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                };
            }
            
            function updateUI() {
                updateStatusBar();
                updateServicesList();
                updateAlertsList();
                updateArchitectureDiagram();
            }
            
            function updateStatusBar() {
                const services = Object.values(architecture.services || {});
                const runningServices = services.filter(s => s.status === 'running').length;
                const alerts = architecture.alerts || [];
                const metrics = architecture.metrics || {};
                
                document.getElementById('total-services').textContent = services.length;
                document.getElementById('running-services').textContent = runningServices;
                document.getElementById('total-alerts').textContent = alerts.length;
                document.getElementById('system-cpu').textContent = (metrics.cpu?.percent || 0).toFixed(1);
                document.getElementById('system-memory').textContent = (metrics.memory?.percent || 0).toFixed(1);
            }
            
            function updateServicesList() {
                const container = document.getElementById('services-list');
                const services = Object.values(architecture.services || {});
                
                if (services.length === 0) {
                    container.innerHTML = '<div class="loading">Сервисы не найдены</div>';
                    return;
                }
                
                container.innerHTML = services.map(service => `
                    <div class="service-card ${service.status}">
                        <div class="service-header">
                            <div class="service-name">${service.name}</div>
                            <div class="service-status status-${service.status}">${service.status}</div>
                        </div>
                        <div class="service-metrics">
                            <div>Порт: ${service.port}</div>
                            <div>PID: ${service.pid || 'N/A'}</div>
                            <div>CPU: ${service.cpu_usage.toFixed(1)}%</div>
                            <div>RAM: ${service.memory_usage.toFixed(1)}%</div>
                            <div>Uptime: ${formatUptime(service.uptime)}</div>
                            <div>Memory: ${service.memory_mb.toFixed(1)} MB</div>
                        </div>
                    </div>
                `).join('');
            }
            
            function updateAlertsList() {
                const container = document.getElementById('alerts-list');
                const alerts = architecture.alerts || [];
                
                if (alerts.length === 0) {
                    container.innerHTML = '<div style="text-align: center; opacity: 0.7;">Нет активных алертов</div>';
                    return;
                }
                
                container.innerHTML = alerts.map(alert => `
                    <div class="alert-item ${alert.severity}">
                        <div class="alert-header">
                            <div class="alert-service">${alert.service}</div>
                            <div class="alert-severity severity-${alert.severity}">${alert.severity}</div>
                        </div>
                        <div class="alert-message">${alert.message}</div>
                        <div class="alert-timestamp">${new Date(alert.timestamp).toLocaleString()}</div>
                    </div>
                `).join('');
            }
            
            function updateArchitectureDiagram() {
                const container = document.getElementById('diagram-container');
                const services = Object.values(architecture.services || {});
                
                if (services.length === 0) {
                    container.innerHTML = '<div class="loading">Сервисы не найдены</div>';
                    return;
                }
                
                // Очищаем предыдущую диаграмму
                d3.select("#diagram-container").selectAll("*").remove();
                
                // Создаем SVG
                const width = container.clientWidth;
                const height = 500;
                
                svg = d3.select("#diagram-container")
                    .append("svg")
                    .attr("width", width)
                    .attr("height", height);
                
                // Создаем узлы для сервисов
                const nodes = services.map((service, index) => ({
                    id: service.name,
                    x: (width / (services.length + 1)) * (index + 1),
                    y: height / 2,
                    service: service
                }));
                
                // Создаем связи между сервисами
                const links = [];
                for (let i = 0; i < nodes.length - 1; i++) {
                    links.push({
                        source: nodes[i].id,
                        target: nodes[i + 1].id
                    });
                }
                
                // Рисуем связи
                svg.selectAll(".connection-line")
                    .data(links)
                    .enter()
                    .append("line")
                    .attr("class", "connection-line")
                    .attr("x1", d => nodes.find(n => n.id === d.source).x)
                    .attr("y1", d => nodes.find(n => n.id === d.source).y)
                    .attr("x2", d => nodes.find(n => n.id === d.target).x)
                    .attr("y2", d => nodes.find(n => n.id === d.target).y);
                
                // Рисуем узлы сервисов
                const nodeGroups = svg.selectAll(".service-node")
                    .data(nodes)
                    .enter()
                    .append("g")
                    .attr("class", d => `service-node ${d.service.status}`)
                    .attr("transform", d => `translate(${d.x}, ${d.y})`);
                
                nodeGroups.append("circle")
                    .attr("r", 30);
                
                nodeGroups.append("text")
                    .text(d => d.service.name.split(' ')[0])
                    .attr("dy", 5);
                
                // Добавляем интерактивность
                nodeGroups.on("mouseover", function(event, d) {
                    const tooltip = d3.select("body")
                        .append("div")
                        .attr("class", "connection-info")
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 10) + "px")
                        .html(`
                            <strong>${d.service.name}</strong><br>
                            Порт: ${d.service.port}<br>
                            Статус: ${d.service.status}<br>
                            CPU: ${d.service.cpu_usage.toFixed(1)}%<br>
                            RAM: ${d.service.memory_usage.toFixed(1)}%
                        `);
                })
                .on("mouseout", function() {
                    d3.selectAll(".connection-info").remove();
                });
            }
            
            function formatUptime(seconds) {
                if (seconds < 60) {
                    return `${Math.round(seconds)}s`;
                } else if (seconds < 3600) {
                    return `${Math.round(seconds / 60)}m`;
                } else {
                    return `${Math.round(seconds / 3600)}h`;
                }
            }
            
            // Функции переключения темы и вида
            function toggleTheme() {
                isDarkTheme = !isDarkTheme;
                const body = document.body;
                const button = document.querySelector('.theme-toggle');
                
                if (isDarkTheme) {
                    body.classList.remove('light-theme');
                    button.textContent = '🌙 Темная тема';
                } else {
                    body.classList.add('light-theme');
                    button.textContent = '☀️ Светлая тема';
                }
            }
            
            function toggleView() {
                is3DView = !is3DView;
                const button = document.querySelector('.view-toggle');
                const diagramContainer = document.getElementById('diagram-container');
                const container3d = document.getElementById('3d-container');
                
                if (is3DView) {
                    diagramContainer.style.display = 'none';
                    container3d.style.display = 'block';
                    button.textContent = '📊 2D вид';
                    init3DVisualization();
                } else {
                    diagramContainer.style.display = 'block';
                    container3d.style.display = 'none';
                    button.textContent = '🎯 3D вид';
                    if (renderer3d) {
                        renderer3d.dispose();
                    }
                }
            }
            
            function init3DVisualization() {
                const container = document.getElementById('3d-container');
                container.innerHTML = '';
                
                // Создаем сцену
                scene3d = new THREE.Scene();
                scene3d.background = new THREE.Color(0x0f0f23);
                
                // Создаем камеру
                camera3d = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
                camera3d.position.set(0, 0, 10);
                
                // Создаем рендерер
                renderer3d = new THREE.WebGLRenderer({ antialias: true });
                renderer3d.setSize(container.clientWidth, container.clientHeight);
                container.appendChild(renderer3d.domElement);
                
                // Создаем контроллеры
                controls3d = new THREE.OrbitControls(camera3d, renderer3d.domElement);
                controls3d.enableDamping = true;
                controls3d.dampingFactor = 0.05;
                
                // Добавляем освещение
                const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
                scene3d.add(ambientLight);
                
                const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                directionalLight.position.set(10, 10, 5);
                scene3d.add(directionalLight);
                
                // Создаем узлы сервисов
                create3DNodes();
                
                // Анимация
                animate3D();
            }
            
            function create3DNodes() {
                const services = Object.values(architecture.services || {});
                const radius = 5;
                
                services.forEach((service, index) => {
                    const angle = (index / services.length) * Math.PI * 2;
                    const x = Math.cos(angle) * radius;
                    const z = Math.sin(angle) * radius;
                    const y = 0;
                    
                    // Создаем геометрию сферы
                    const geometry = new THREE.SphereGeometry(0.5, 32, 32);
                    
                    // Выбираем цвет в зависимости от статуса
                    let color = 0x4CAF50; // зеленый для running
                    if (service.status === 'stopped') color = 0xF44336; // красный
                    if (service.status === 'error') color = 0xFF9800; // оранжевый
                    
                    const material = new THREE.MeshLambertMaterial({ color: color });
                    const sphere = new THREE.Mesh(geometry, material);
                    
                    sphere.position.set(x, y, z);
                    sphere.userData = { service: service };
                    
                    scene3d.add(sphere);
                    
                    // Добавляем текст
                    const canvas = document.createElement('canvas');
                    const context = canvas.getContext('2d');
                    canvas.width = 256;
                    canvas.height = 64;
                    
                    context.fillStyle = 'rgba(0, 0, 0, 0.8)';
                    context.fillRect(0, 0, canvas.width, canvas.height);
                    
                    context.fillStyle = 'white';
                    context.font = '16px Arial';
                    context.textAlign = 'center';
                    context.fillText(service.name, canvas.width / 2, canvas.height / 2 + 5);
                    
                    const texture = new THREE.CanvasTexture(canvas);
                    const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
                    const sprite = new THREE.Sprite(spriteMaterial);
                    sprite.position.set(x, y + 1, z);
                    sprite.scale.set(2, 0.5, 1);
                    
                    scene3d.add(sprite);
                });
            }
            
            function animate3D() {
                if (!is3DView) return;
                
                requestAnimationFrame(animate3D);
                
                if (controls3d) {
                    controls3d.update();
                }
                
                if (renderer3d && scene3d && camera3d) {
                    renderer3d.render(scene3d, camera3d);
                }
            }
            
            // Инициализация при загрузке страницы
            initWebSocket();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    print("🏗️ Запуск ALADDIN Enhanced Architecture Visualizer...")
    print("📊 Мониторинг без Docker через psutil...")
    print("🔧 Подключение к реальным сервисам ALADDIN...")
    print("⚡ WebSocket real-time обновления...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8081,
        log_level="info"
    )