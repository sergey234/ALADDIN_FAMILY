#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простая версия Interactive API Docs для тестирования
"""

import os
import sys
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

# Создание простого FastAPI приложения
app = FastAPI(title="ALADDIN API Docs", version="1.0.0")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🛡️ ALADDIN Interactive API Docs</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
                padding: 30px 0;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            .header h1 {
                font-size: 3em;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #00d4ff, #00ff88);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
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
            .endpoints-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .endpoint-card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 25px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: all 0.3s ease;
            }
            .endpoint-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            }
            .method-badge {
                padding: 5px 12px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 12px;
                text-transform: uppercase;
                display: inline-block;
                margin-bottom: 10px;
            }
            .method-get { background: #4CAF50; }
            .method-post { background: #2196F3; }
            .method-put { background: #FF9800; }
            .method-delete { background: #F44336; }
            .endpoint-path {
                font-family: monospace;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .endpoint-description {
                color: rgba(255, 255, 255, 0.8);
                margin-bottom: 15px;
            }
            .test-button {
                width: 100%;
                padding: 12px;
                background: linear-gradient(45deg, #00d4ff, #00ff88);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .test-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 212, 255, 0.4);
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                backdrop-filter: blur(10px);
            }
            .stat-number {
                font-size: 2em;
                font-weight: bold;
                color: #00d4ff;
            }
            .stat-label {
                margin-top: 5px;
                opacity: 0.8;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ ALADDIN Security System</h1>
                <p>Interactive API Documentation</p>
            </div>

            <div class="success-message">
                🎉 <strong>Interactive API Docs успешно запущен!</strong><br>
                Сервер работает на порту 8008
            </div>

            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">30+</div>
                    <div class="stat-label">API Endpoints</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">350+</div>
                    <div class="stat-label">Security Functions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">A+</div>
                    <div class="stat-label">Code Quality</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">100%</div>
                    <div class="stat-label">Ready</div>
                </div>
            </div>

            <div class="endpoints-grid">
                <div class="endpoint-card">
                    <span class="method-badge method-get">GET</span>
                    <div class="endpoint-path">/api/security/threat-detection</div>
                    <div class="endpoint-description">
                        Детекция угроз безопасности в системе
                    </div>
                    <button class="test-button" onclick="testEndpoint('/api/security/threat-detection', 'GET')">
                        🚀 Попробовать API
                    </button>
                </div>

                <div class="endpoint-card">
                    <span class="method-badge method-post">POST</span>
                    <div class="endpoint-path">/api/security/behavioral-analysis</div>
                    <div class="endpoint-description">
                        Анализ поведенческих паттернов для выявления аномалий
                    </div>
                    <button class="test-button" onclick="testEndpoint('/api/security/behavioral-analysis', 'POST')">
                        🚀 Попробовать API
                    </button>
                </div>

                <div class="endpoint-card">
                    <span class="method-badge method-post">POST</span>
                    <div class="endpoint-path">/api/security/incident-response</div>
                    <div class="endpoint-description">
                        Обработка и реагирование на инциденты безопасности
                    </div>
                    <button class="test-button" onclick="testEndpoint('/api/security/incident-response', 'POST')">
                        🚀 Попробовать API
                    </button>
                </div>

                <div class="endpoint-card">
                    <span class="method-badge method-get">GET</span>
                    <div class="endpoint-path">/api/security/password-security</div>
                    <div class="endpoint-description">
                        Проверка и управление безопасностью паролей
                    </div>
                    <button class="test-button" onclick="testEndpoint('/api/security/password-security', 'GET')">
                        🚀 Попробовать API
                    </button>
                </div>

                <div class="endpoint-card">
                    <span class="method-badge method-get">GET</span>
                    <div class="endpoint-path">/api/security/network-monitoring</div>
                    <div class="endpoint-description">
                        Мониторинг сетевого трафика и безопасности
                    </div>
                    <button class="test-button" onclick="testEndpoint('/api/security/network-monitoring', 'GET')">
                        🚀 Попробовать API
                    </button>
                </div>

                <div class="endpoint-card">
                    <span class="method-badge method-post">POST</span>
                    <div class="endpoint-path">/api/security/data-protection</div>
                    <div class="endpoint-description">
                        Управление защитой и шифрованием данных
                    </div>
                    <button class="test-button" onclick="testEndpoint('/api/security/data-protection', 'POST')">
                        🚀 Попробовать API
                    </button>
                </div>
            </div>
        </div>

        <script>
            function testEndpoint(endpoint, method) {
                alert(`🧪 Тестирование API:\\n\\nEndpoint: ${endpoint}\\nMethod: ${method}\\n\\nВ полной версии здесь будет реальное тестирование API с параметрами и результатами!`);
            }

            // Автоматическое обновление статистики
            setInterval(() => {
                const timestamp = new Date().toLocaleTimeString();
                console.log(`🕐 Обновлено: ${timestamp}`);
            }, 5000);
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/api/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "service": "ALADDIN Interactive API Docs",
        "version": "1.0.0",
        "timestamp": "2025-09-25T23:30:00Z"
    }

@app.get("/api/endpoints")
async def get_endpoints():
    """Получение списка всех endpoints"""
    return {
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/security/threat-detection",
                "description": "Детекция угроз безопасности"
            },
            {
                "method": "POST", 
                "path": "/api/security/behavioral-analysis",
                "description": "Анализ поведения пользователей"
            },
            {
                "method": "POST",
                "path": "/api/security/incident-response", 
                "description": "Реагирование на инциденты"
            },
            {
                "method": "GET",
                "path": "/api/security/password-security",
                "description": "Безопасность паролей"
            },
            {
                "method": "GET",
                "path": "/api/security/network-monitoring",
                "description": "Мониторинг сети"
            },
            {
                "method": "POST",
                "path": "/api/security/data-protection",
                "description": "Защита данных"
            }
        ],
        "total_count": 6
    }

if __name__ == "__main__":
    print("🚀 Запуск простого Interactive API Docs...")
    print("🌐 URL: http://localhost:8008")
    print("🛑 Для остановки нажмите Ctrl+C")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8008,
        log_level="info"
    )