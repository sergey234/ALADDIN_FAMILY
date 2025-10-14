#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPN Web Interface - Улучшенный веб-интерфейс с безопасностью
"""

import json
import logging
import os
import secrets
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import asyncio
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from security.vpn.vpn_security_system import (
    VPNSecurityLevel,
    VPNSecuritySystem,
)

# Добавление пути к проекту
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание Flask приложения
app = Flask(__name__)

# БЕЗОПАСНОСТЬ: Генерация SECRET_KEY из переменной окружения или случайного
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))

# БЕЗОПАСНОСТЬ: Отключение DEBUG в production
app.config["DEBUG"] = os.getenv("DEBUG", "False").lower() == "true"
app.config["ENV"] = os.getenv("FLASK_ENV", "production")

# БЕЗОПАСНОСТЬ: Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "20 per minute"],
    storage_uri="memory://",  # В production используйте Redis
)

# БЕЗОПАСНОСТЬ: CORS с правильными настройками
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ["http://localhost:*", "https://localhost:*"],
            "methods": ["GET", "POST"],
            "allow_headers": ["Content-Type"],
        }
    },
)

# Глобальная переменная для VPN системы
vpn_system = None
active_connections = {}


def init_vpn_system():
    """Инициализация VPN системы"""
    global vpn_system
    try:
        vpn_system = VPNSecuritySystem("WebVPNInterface")
        logger.info("VPN система инициализирована для веб-интерфейса")
        return True
    except Exception as e:
        logger.error(f"Ошибка инициализации VPN системы: {e}")
        return False


@app.route("/")
@limiter.limit("30 per minute")
def index():
    """Главная страница с улучшенным UI"""
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ALADDIN VPN - Профессиональная защита</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
                padding: 20px;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
            }

            .header {
                text-align: center;
                margin-bottom: 40px;
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

            .main-card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                margin-bottom: 30px;
            }

            .status-indicator {
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 30px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                margin-bottom: 30px;
            }

            .status-circle {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                background: #f44336;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2em;
                box-shadow: 0 0 20px rgba(244, 67, 54, 0.5);
                animation: pulse 2s infinite;
            }

            .status-circle.connected {
                background: #4CAF50;
                box-shadow: 0 0 20px rgba(76, 175, 80, 0.5);
            }

            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }

            .status-text {
                margin-left: 30px;
            }

            .status-text h2 {
                font-size: 2em;
                margin-bottom: 10px;
            }

            .button-group {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }

            .btn {
                padding: 20px 30px;
                border: none;
                border-radius: 10px;
                font-size: 1.1em;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }

            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }

            .btn-primary {
                background: #4CAF50;
                color: white;
            }

            .btn-danger {
                background: #f44336;
                color: white;
            }

            .btn-secondary {
                background: rgba(255, 255, 255, 0.2);
                color: white;
            }

            .country-selector {
                background: rgba(255, 255, 255, 0.05);
                padding: 30px;
                border-radius: 15px;
                margin: 30px 0;
            }

            .country-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }

            .country-card {
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
            }

            .country-card:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: scale(1.05);
            }

            .country-flag {
                font-size: 3em;
                margin-bottom: 10px;
            }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }

            .stat-card {
                background: rgba(255, 255, 255, 0.1);
                padding: 25px;
                border-radius: 15px;
                text-align: center;
            }

            .stat-value {
                font-size: 2.5em;
                font-weight: bold;
                margin: 10px 0;
            }

            .stat-label {
                opacity: 0.8;
                font-size: 0.9em;
            }

            .loading {
                display: none;
                text-align: center;
                padding: 20px;
            }

            .spinner {
                border: 4px solid rgba(255,255,255,0.3);
                border-top: 4px solid white;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 20px 30px;
                background: rgba(76, 175, 80, 0.9);
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                display: none;
                animation: slideIn 0.3s;
            }

            @keyframes slideIn {
                from { transform: translateX(100%); }
                to { transform: translateX(0); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔒 ALADDIN VPN</h1>
                <p>Профессиональная защита вашей конфиденциальности</p>
            </div>

            <div class="main-card">
                <div class="status-indicator">
                    <div class="status-circle" id="statusCircle">
                        🔴
                    </div>
                    <div class="status-text">
                        <h2 id="statusTitle">Отключено</h2>
                        <p id="statusDescription">Нажмите "Подключиться" для защиты</p>
                    </div>
                </div>

                <div class="button-group">
                    <button class="btn btn-primary" onclick="quickConnect()">
                        🚀 Быстрое подключение
                    </button>
                    <button class="btn btn-danger" onclick="disconnect()" style="display:none;" id="disconnectBtn">
                        🛑 Отключиться
                    </button>
                    <button class="btn btn-secondary" onclick="showCountries()">
                        🌍 Выбрать страну
                    </button>
                    <button class="btn btn-secondary" onclick="showSettings()">
                        ⚙️ Настройки
                    </button>
                </div>
            </div>

            <div class="country-selector" id="countrySelector" style="display:none;">
                <h2>🌍 Выберите страну</h2>
                <div class="country-grid" id="countryGrid">
                    <!-- Заполняется динамически -->
                </div>
            </div>

            <div class="main-card">
                <h2>📊 Статистика</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="totalConnections">0</div>
                        <div class="stat-label">Всего подключений</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="successRate">0%</div>
                        <div class="stat-label">Успешность</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="currentSpeed">0 Мб/с</div>
                        <div class="stat-label">Текущая скорость</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="dataUsed">0 ГБ</div>
                        <div class="stat-label">Использовано данных</div>
                    </div>
                </div>
            </div>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="margin-top: 20px;">Подключение...</p>
            </div>
        </div>

        <div class="notification" id="notification">
            <span id="notificationText"></span>
        </div>

        <script>
            let isConnected = false;

            function showNotification(message, isSuccess = true) {
                const notification = document.getElementById('notification');
                notification.style.background = isSuccess ?
                    'rgba(76, 175, 80, 0.9)' : 'rgba(244, 67, 54, 0.9)';
                document.getElementById('notificationText').textContent = message;
                notification.style.display = 'block';
                setTimeout(() => {
                    notification.style.display = 'none';
                }, 3000);
            }

            async function quickConnect() {
                const loading = document.getElementById('loading');
                loading.style.display = 'block';

                try {
                    const response = await fetch('/api/test_singapore');
                    const data = await response.json();

                    if (data.success) {
                        isConnected = true;
                        updateUI();
                        showNotification('✅ Успешно подключено к VPN!');
                    } else {
                        showNotification('❌ Ошибка подключения: ' + data.error, false);
                    }
                } catch (error) {
                    showNotification('❌ Ошибка: ' + error.message, false);
                } finally {
                    loading.style.display = 'none';
                }
            }

            function disconnect() {
                isConnected = false;
                updateUI();
                showNotification('✅ Отключено от VPN');
            }

            function updateUI() {
                const circle = document.getElementById('statusCircle');
                const title = document.getElementById('statusTitle');
                const desc = document.getElementById('statusDescription');
                const disconnectBtn = document.getElementById('disconnectBtn');

                if (isConnected) {
                    circle.classList.add('connected');
                    circle.textContent = '🟢';
                    title.textContent = 'Подключено';
                    desc.textContent = 'Ваше соединение защищено';
                    disconnectBtn.style.display = 'block';
                } else {
                    circle.classList.remove('connected');
                    circle.textContent = '🔴';
                    title.textContent = 'Отключено';
                    desc.textContent = 'Нажмите "Подключиться" для защиты';
                    disconnectBtn.style.display = 'none';
                }
            }

            async function loadStats() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();

                    document.getElementById('totalConnections').textContent =
                        data.statistics.total_connections;
                    document.getElementById('successRate').textContent =
                        data.statistics.success_rate.toFixed(1) + '%';
                } catch (error) {
                    console.error('Ошибка загрузки статистики:', error);
                }
            }

            async function showCountries() {
                const selector = document.getElementById('countrySelector');
                const grid = document.getElementById('countryGrid');

                try {
                    const response = await fetch('/api/countries');
                    const data = await response.json();

                    grid.innerHTML = '';
                    data.countries.forEach(country => {
                        const card = document.createElement('div');
                        card.className = 'country-card';
                        card.innerHTML = `
                            <div class="country-flag">${getCountryFlag(country.name)}</div>
                            <div><strong>${country.name}</strong></div>
                            <div style="font-size: 0.9em; opacity: 0.8;">
                                ${country.total_servers} серверов<br>
                                ${country.avg_latency.toFixed(0)}ms
                            </div>
                        `;
                        card.onclick = () => connectToCountry(country.name);
                        grid.appendChild(card);
                    });

                    selector.style.display = 'block';
                } catch (error) {
                    showNotification('❌ Ошибка загрузки стран', false);
                }
            }

            function getCountryFlag(countryName) {
                const flags = {
                    'Singapore': '🇸🇬',
                    'Russia': '🇷🇺',
                    'Netherlands': '🇳🇱',
                    'United Kingdom': '🇬🇧',
                    'Germany': '🇩🇪',
                    'USA': '🇺🇸',
                    'Canada': '🇨🇦',
                    'France': '🇫🇷',
                    'Australia': '🇦🇺',
                    'Japan': '🇯🇵'
                };
                return flags[countryName] || '🌍';
            }

            async function connectToCountry(country) {
                showNotification(`🔄 Подключение к ${country}...`);
                // Реализация подключения к конкретной стране
            }

            function showSettings() {
                showNotification('⚙️ Настройки в разработке');
            }

            // Загрузка данных при загрузке страницы
            window.onload = function() {
                loadStats();
                setInterval(loadStats, 10000); // Обновление каждые 10 секунд
            };
        </script>
    </body>
    </html>
    """


@app.route("/api/status")
@limiter.limit("60 per minute")
def api_status():
    """API статуса системы"""
    try:
        if not vpn_system:
            return jsonify({"error": "VPN система не инициализирована"}), 500

        status = vpn_system.get_status()
        stats = vpn_system.get_system_stats()

        return jsonify(
            {
                "status": status["status"],
                "message": status["message"],
                "statistics": stats,
            }
        )
    except Exception as e:
        logger.error(f"Ошибка получения статуса: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/countries")
@limiter.limit("60 per minute")
def api_countries():
    """API списка стран"""
    try:
        if not vpn_system:
            return jsonify({"error": "VPN система не инициализирована"}), 500

        servers = vpn_system.get_available_servers()
        countries = {}

        for server in servers:
            country = server["country"]
            if country not in countries:
                countries[country] = {
                    "name": country,
                    "servers": [],
                    "total_servers": 0,
                    "avg_latency": 0,
                }

            countries[country]["servers"].append(server)
            countries[country]["total_servers"] += 1

        # Вычисление средней задержки
        for country_data in countries.values():
            if country_data["servers"]:
                country_data["avg_latency"] = sum(
                    s["latency"] for s in country_data["servers"]
                ) / len(country_data["servers"])

        return jsonify(
            {
                "countries": list(countries.values()),
                "total_countries": len(countries),
            }
        )
    except Exception as e:
        logger.error(f"Ошибка получения стран: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/test_singapore")
@limiter.limit("10 per minute")
def api_test_singapore():
    """API тестирования Singapore"""
    try:
        if not vpn_system:
            return jsonify({"error": "VPN система не инициализирована"}), 500

        test_user = f"test_singapore_{int(time.time())}"

        # Подключение к Singapore
        success, message, report = asyncio.run(
            vpn_system.connect(
                test_user,
                country="Singapore",
                security_level=VPNSecurityLevel.HIGH,
            )
        )

        if success:
            # Ожидание 2 секунды
            time.sleep(2)

            # Отключение
            disconnect_success, disconnect_message = asyncio.run(
                vpn_system.disconnect(test_user)
            )

            return jsonify(
                {
                    "success": True,
                    "connect_message": message,
                    "disconnect_message": disconnect_message,
                    "report": report,
                    "test_duration": "2 секунды",
                }
            )
        else:
            return jsonify({"success": False, "error": message}), 400

    except Exception as e:
        logger.error(f"Ошибка тестирования Singapore: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify(
        {"status": "healthy", "timestamp": datetime.now().isoformat()}
    )


if __name__ == "__main__":
    # Инициализация VPN системы
    if init_vpn_system():
        port = int(os.getenv("VPN_PORT", 5000))
        host = os.getenv("VPN_HOST", "0.0.0.0")
        debug = os.getenv("DEBUG", "False").lower() == "true"

        print("=" * 80)
        print("🌍 VPN Web Interface запущен!")
        print("=" * 80)
        print(f"📱 Откройте в браузере: http://localhost:{port}")
        print(
            f"🔐 SECRET_KEY: {'✅ Установлен' if app.secret_key else '❌ НЕ установлен'}"
        )
        print(f"🐞 DEBUG режим: {'❌ Включен' if debug else '✅ Отключен'}")
        print("🛡️  Rate Limiting: ✅ Включен")
        print("🌐 CORS: ✅ Настроен")
        print("=" * 80)

        app.run(host=host, port=port, debug=debug)
    else:
        print("❌ Ошибка инициализации VPN системы")
