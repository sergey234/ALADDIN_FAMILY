#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простая версия Real-time Architecture Visualizer для тестирования
"""

import os
import sys
from flask import Flask, render_template_string
import json
from datetime import datetime
import psutil

# Создание простого Flask приложения
app = Flask(__name__)

# HTML шаблон для Real-time Architecture
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏗️ ALADDIN Real-time Architecture</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            color: #ffffff;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 25px 0;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #00d4ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 15px 25px;
            margin-bottom: 25px;
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 15px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #4CAF50;
            animation: pulse 2s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        .metric-title {
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 8px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            background: linear-gradient(45deg, #00d4ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .architecture-container {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
        }
        .architecture-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .architecture-title {
            font-size: 1.5em;
            font-weight: bold;
        }
        .architecture-controls {
            display: flex;
            gap: 10px;
        }
        .control-button {
            padding: 8px 16px;
            background: linear-gradient(45deg, #00d4ff, #00ff88);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
        }
        #architecture-svg {
            width: 100%;
            height: 600px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
        }
        .service-node {
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .service-node:hover {
            transform: scale(1.1);
            filter: brightness(1.2);
        }
        .service-node.running {
            fill: #4CAF50;
            stroke: #388E3C;
        }
        .service-node.warning {
            fill: #FFC107;
            stroke: #FFA000;
        }
        .service-node.error {
            fill: #F44336;
            stroke: #D32F2F;
        }
        .connection-line {
            stroke: rgba(255, 255, 255, 0.6);
            stroke-width: 2;
            fill: none;
            marker-end: url(#arrowhead);
        }
        .details-panel {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 20px;
            margin-top: 25px;
            display: none;
        }
        .details-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #00d4ff;
        }
        .details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .detail-item {
            background: rgba(0, 0, 0, 0.2);
            padding: 12px;
            border-radius: 8px;
            border-left: 3px solid #00d4ff;
        }
        .detail-label {
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 5px;
        }
        .detail-value {
            font-weight: bold;
            font-size: 1.1em;
        }
        .success-message {
            background: rgba(76, 175, 80, 0.2);
            border: 1px solid #4CAF50;
            color: #c8e6c9;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            font-size: 1.2em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ {{ title }}</h1>
            <p>Живая карта системы безопасности ALADDIN в реальном времени</p>
        </div>

        <div class="success-message">
            🎉 <strong>Real-time Architecture Visualizer запущен!</strong><br>
            Сервер работает на порту 8007
        </div>

        <div class="status-bar">
            <div class="status-item">
                <span id="system-status-indicator" class="status-indicator"></span>
                <span id="system-status-text">System Online</span>
            </div>
            <div class="status-item">
                <span>Services: <span id="service-count">{{ services_count }}</span></span>
            </div>
            <div class="status-item">
                <span>Connections: <span id="connection-count">{{ connections_count }}</span></span>
            </div>
            <div class="status-item">
                <span>Last Update: <span id="last-update">{{ current_time }}</span></span>
            </div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">🖥️ CPU Usage</div>
                <div class="metric-value" id="cpu-usage">{{ cpu_usage }}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">💾 Memory Usage</div>
                <div class="metric-value" id="memory-usage">{{ memory_usage }}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">🔄 Running Services</div>
                <div class="metric-value" id="running-services">{{ running_services }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">📊 Total Services</div>
                <div class="metric-value" id="total-services">{{ total_services }}</div>
            </div>
        </div>

        <div class="architecture-container">
            <div class="architecture-header">
                <div class="architecture-title">🗺️ System Architecture</div>
                <div class="architecture-controls">
                    <button class="control-button" onclick="refreshArchitecture()">🔄 Refresh</button>
                    <button class="control-button" onclick="exportArchitecture()">📥 Export</button>
                </div>
            </div>
            
            <svg id="architecture-svg"></svg>
        </div>

        <div class="details-panel" id="details-panel">
            <div class="details-title">📋 Service Details</div>
            <div class="details-grid" id="service-details">
                <!-- Детали сервиса будут загружены динамически -->
            </div>
        </div>
    </div>

    <script>
        // Глобальные переменные
        let svg, width, height, simulation;
        let services = {{ services | safe }};
        let connections = {{ connections | safe }};
        
        // Инициализация D3.js
        function initializeVisualization() {
            svg = d3.select('#architecture-svg');
            width = svg.node().clientWidth;
            height = svg.node().clientHeight;
            
            svg.attr('width', width).attr('height', height);
            
            // Создание симуляции
            simulation = d3.forceSimulation()
                .force('link', d3.forceLink().id(d => d.id).distance(100))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2));
        }
        
        // Рендеринг архитектуры
        function renderArchitecture() {
            if (!services || !connections) return;
            
            // Очистка SVG
            svg.selectAll('*').remove();
            
            // Создание стрелок
            const defs = svg.append('defs');
            const arrowMarker = defs.append('marker')
                .attr('id', 'arrowhead')
                .attr('viewBox', '0 0 10 10')
                .attr('refX', 8)
                .attr('refY', 5)
                .attr('markerUnits', 'strokeWidth')
                .attr('markerWidth', 10)
                .attr('markerHeight', 10)
                .attr('orient', 'auto');
            
            arrowMarker.append('path')
                .attr('d', 'M 0 0 L 10 5 L 0 10 z')
                .attr('fill', 'rgba(255, 255, 255, 0.6)');
            
            // Подготовка данных для D3
            const nodes = services.map(service => ({
                id: service.name,
                name: service.name,
                status: service.status || 'running',
                type: service.type || 'unknown',
                cpu_usage: service.cpu_usage || 0,
                memory_usage: service.memory_usage || 0,
                details: service
            }));
            
            const links = connections.map(conn => ({
                source: conn.source,
                target: conn.target,
                type: conn.type,
                weight: conn.weight || 1
            }));
            
            // Обновление симуляции
            simulation.nodes(nodes);
            simulation.force('link').links(links);
            
            // Рендеринг связей
            const link = svg.append('g')
                .attr('class', 'links')
                .selectAll('line')
                .data(links)
                .enter().append('line')
                .attr('class', 'connection-line')
                .attr('stroke-width', d => Math.sqrt(d.weight) * 2);
            
            // Рендеринг узлов
            const node = svg.append('g')
                .attr('class', 'nodes')
                .selectAll('g')
                .data(nodes)
                .enter().append('g')
                .attr('class', d => `service-node ${d.status}`)
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));
            
            // Круги для узлов
            node.append('circle')
                .attr('r', 20)
                .attr('fill', d => getServiceColor(d.status))
                .attr('stroke', d => getServiceStrokeColor(d.status))
                .attr('stroke-width', 2);
            
            // Текст для узлов
            node.append('text')
                .attr('text-anchor', 'middle')
                .attr('dy', 5)
                .attr('font-size', '12px')
                .attr('font-weight', 'bold')
                .attr('fill', 'white')
                .text(d => d.name.length > 15 ? d.name.substring(0, 15) + '...' : d.name);
            
            // Обработчики событий для узлов
            node.on('click', (event, d) => {
                displayServiceDetails(d);
            });
            
            // Обновление позиций при тиках симуляции
            simulation.on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                node
                    .attr('transform', d => `translate(${d.x},${d.y})`);
            });
            
            // Запуск симуляции
            simulation.alpha(1).restart();
        }
        
        // Получение цвета сервиса
        function getServiceColor(status) {
            const colors = {
                'running': '#4CAF50',
                'warning': '#FFC107',
                'error': '#F44336',
                'stopped': '#9E9E9E',
                'unknown': '#607D8B'
            };
            return colors[status] || colors['unknown'];
        }
        
        // Получение цвета обводки сервиса
        function getServiceStrokeColor(status) {
            const colors = {
                'running': '#388E3C',
                'warning': '#FFA000',
                'error': '#D32F2F',
                'stopped': '#757575',
                'unknown': '#455A64'
            };
            return colors[status] || colors['unknown'];
        }
        
        // Отображение деталей сервиса
        function displayServiceDetails(data) {
            const detailsPanel = document.getElementById('details-panel');
            const serviceDetails = document.getElementById('service-details');
            
            const details = [
                { label: 'Name', value: data.name || 'N/A' },
                { label: 'Status', value: data.status || 'N/A' },
                { label: 'Type', value: data.type || 'N/A' },
                { label: 'CPU Usage', value: `${(data.cpu_usage || 0).toFixed(2)}%` },
                { label: 'Memory Usage', value: `${(data.memory_usage || 0).toFixed(2)} MB` },
                { label: 'Details', value: JSON.stringify(data.details || {}, null, 2) }
            ];
            
            serviceDetails.innerHTML = details.map(detail => `
                <div class="detail-item">
                    <div class="detail-label">${detail.label}</div>
                    <div class="detail-value">${detail.value}</div>
                </div>
            `).join('');
            
            detailsPanel.style.display = 'block';
        }
        
        // Обработчики событий drag для D3
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        // Функции кнопок
        function refreshArchitecture() {
            location.reload();
        }
        
        function exportArchitecture() {
            const data = {
                services: services,
                connections: connections,
                timestamp: new Date().toISOString()
            };
            
            const dataStr = JSON.stringify(data, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `aladdin_architecture_${new Date().toISOString()}.json`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }
        
        // Инициализация при загрузке страницы
        window.addEventListener('load', () => {
            initializeVisualization();
            renderArchitecture();
        });
        
        // Обработка изменения размера окна
        window.addEventListener('resize', () => {
            initializeVisualization();
            renderArchitecture();
        });
        
        // Автоматическое обновление каждые 5 секунд
        setInterval(() => {
            const timestamp = new Date().toLocaleTimeString();
            document.getElementById('last-update').textContent = timestamp;
            console.log(`🕐 Architecture обновлено: ${timestamp}`);
        }, 5000);
        
        console.log('🏗️ Добро пожаловать в ALADDIN Real-time Architecture!');
        console.log('🗺️ Кликайте по узлам для просмотра деталей сервисов');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Главная страница Real-time Architecture"""
    # Получение системных метрик
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    # Симуляция сервисов ALADDIN
    services = [
        {
            "name": "SafeFunctionManager",
            "status": "running",
            "type": "core",
            "cpu_usage": 15.5,
            "memory_usage": 128.3,
            "port": 8006
        },
        {
            "name": "APIGateway",
            "status": "running", 
            "type": "gateway",
            "cpu_usage": 8.2,
            "memory_usage": 64.7,
            "port": 8007
        },
        {
            "name": "SecurityMonitoring",
            "status": "running",
            "type": "monitoring",
            "cpu_usage": 12.1,
            "memory_usage": 89.2,
            "port": 8008
        },
        {
            "name": "AIBehavioralAgent",
            "status": "running",
            "type": "ai_agent",
            "cpu_usage": 25.8,
            "memory_usage": 156.4,
            "port": 8009
        },
        {
            "name": "ThreatDetectionAgent",
            "status": "running",
            "type": "ai_agent", 
            "cpu_usage": 18.3,
            "memory_usage": 112.7,
            "port": 8010
        },
        {
            "name": "MobileSecurityBot",
            "status": "running",
            "type": "bot",
            "cpu_usage": 6.7,
            "memory_usage": 45.9,
            "port": 8011
        },
        {
            "name": "EmergencyResponseBot",
            "status": "running",
            "type": "bot",
            "cpu_usage": 9.4,
            "memory_usage": 67.3,
            "port": 8012
        }
    ]
    
    # Симуляция связей между сервисами
    connections = [
        {
            "source": "SafeFunctionManager",
            "target": "APIGateway",
            "type": "management",
            "weight": 2
        },
        {
            "source": "APIGateway", 
            "target": "AIBehavioralAgent",
            "type": "api",
            "weight": 1
        },
        {
            "source": "APIGateway",
            "target": "ThreatDetectionAgent", 
            "type": "api",
            "weight": 1
        },
        {
            "source": "SafeFunctionManager",
            "target": "SecurityMonitoring",
            "type": "monitoring",
            "weight": 2
        },
        {
            "source": "SecurityMonitoring",
            "target": "MobileSecurityBot",
            "type": "control",
            "weight": 1
        },
        {
            "source": "SecurityMonitoring",
            "target": "EmergencyResponseBot",
            "type": "control", 
            "weight": 1
        },
        {
            "source": "AIBehavioralAgent",
            "target": "ThreatDetectionAgent",
            "type": "data",
            "weight": 1
        }
    ]
    
    # Подсчет метрик
    running_services = len([s for s in services if s['status'] == 'running'])
    total_services = len(services)
    total_connections = len(connections)
    current_time = datetime.now().strftime('%H:%M:%S')
    
    return render_template_string(HTML_TEMPLATE,
        title="ALADDIN Real-time Architecture",
        services_count=total_services,
        connections_count=total_connections,
        current_time=current_time,
        cpu_usage=f"{cpu_percent:.1f}",
        memory_usage=f"{memory.percent:.1f}",
        running_services=running_services,
        total_services=total_services,
        services=json.dumps(services),
        connections=json.dumps(connections)
    )

@app.route('/api/architecture')
def get_architecture():
    """API endpoint для получения данных архитектуры"""
    return {
        "status": "success",
        "services": [
            {"name": "SafeFunctionManager", "status": "running", "type": "core"},
            {"name": "APIGateway", "status": "running", "type": "gateway"},
            {"name": "SecurityMonitoring", "status": "running", "type": "monitoring"},
            {"name": "AIBehavioralAgent", "status": "running", "type": "ai_agent"},
            {"name": "ThreatDetectionAgent", "status": "running", "type": "ai_agent"},
            {"name": "MobileSecurityBot", "status": "running", "type": "bot"},
            {"name": "EmergencyResponseBot", "status": "running", "type": "bot"}
        ],
        "connections": [
            {"source": "SafeFunctionManager", "target": "APIGateway", "type": "management"},
            {"source": "APIGateway", "target": "AIBehavioralAgent", "type": "api"},
            {"source": "APIGateway", "target": "ThreatDetectionAgent", "type": "api"},
            {"source": "SafeFunctionManager", "target": "SecurityMonitoring", "type": "monitoring"},
            {"source": "SecurityMonitoring", "target": "MobileSecurityBot", "type": "control"},
            {"source": "SecurityMonitoring", "target": "EmergencyResponseBot", "type": "control"}
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.route('/api/health')
def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "service": "ALADDIN Real-time Architecture Visualizer",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Запуск простого Real-time Architecture Visualizer...")
    print("🌐 URL: http://localhost:8007")
    print("🛑 Для остановки нажмите Ctrl+C")
    
    app.run(
        host="0.0.0.0",
        port=8007,
        debug=False
    )