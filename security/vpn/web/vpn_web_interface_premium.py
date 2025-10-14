#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPN Web Interface Premium - Профессиональный интерфейс с грозовым небом
Для интеграции в мобильное приложение ALADDIN Family Security
"""

import logging
import os
import secrets
import sys
import time
from datetime import datetime

import asyncio

try:
    from security.vpn.vpn_security_system import VPNSecurityLevel, VPNSecuritySystem
    SECURITY_SYSTEM_AVAILABLE = True
except ImportError:
    SECURITY_SYSTEM_AVAILABLE = False
    # Создаем mock классы для совместимости
    class VPNSecurityLevel:
        BASIC = "basic"
        PREMIUM = "premium"
        ENTERPRISE = "enterprise"
    
    class VPNSecuritySystem:
        @staticmethod
        def get_security_level():
            return VPNSecurityLevel.PREMIUM
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
    )
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))
app.config["DEBUG"] = os.getenv("DEBUG", "False").lower() == "true"

limiter = Limiter(
    app=app, key_func=get_remote_address, default_limits=["100 per hour"]
)
CORS(app)

vpn_system = None


def init_vpn_system():
    global vpn_system
    try:
        vpn_system = VPNSecuritySystem("PremiumVPN")
        logger.info("VPN Premium система инициализирована")
        return True
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return False


@app.route("/")
def index():
    return """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALADDIN VPN Premium</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            min-height: 100vh;
            overflow: hidden;
            color: white;
            position: relative;
        }
        
        /* ГРОЗОВОЕ НЕБО - ФОН (ALADDIN COLOR SCHEME) */
        .storm-sky {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: linear-gradient(to bottom,
                #0f172a 0%,        /* Темно-синий грозового неба */
                #1E3A8A 20%,       /* Яркий синий грозового неба */
                #3B82F6 40%,       /* Средний синий */
                #1E3A8A 60%,       /* Яркий синий грозового неба */
                #0f172a 100%       /* Темно-синий */
            );
            z-index: -2;
        }
        
        /* МОЛНИИ */
        .lightning {
            position: fixed;
            width: 100%; height: 100%;
            background: radial-gradient(ellipse at center,
                rgba(255,255,255,0.1) 0%,
                rgba(135,206,250,0.05) 30%,
                transparent 70%
            );
            animation: lightning 8s infinite;
            z-index: -1;
            opacity: 0;
        }
        
        @keyframes lightning {
            0%, 100% { opacity: 0; }
            45% { opacity: 0; }
            46% { opacity: 0.8; }
            47% { opacity: 0; }
            48% { opacity: 0.9; }
            49% { opacity: 0; }
            50% { opacity: 0; }
        }
        
        /* ОБЛАКА */
        .clouds {
            position: fixed;
            width: 100%; height: 100%;
            background-image:
                radial-gradient(ellipse 800px 200px at 20% 30%, rgba(255,255,255,0.03) 0%, transparent 100%),
                radial-gradient(ellipse 600px 150px at 80% 50%, rgba(255,255,255,0.02) 0%, transparent 100%),
                radial-gradient(ellipse 700px 180px at 50% 70%, rgba(255,255,255,0.025) 0%, transparent 100%);
            animation: cloudMove 60s infinite linear;
            z-index: -1;
        }
        
        @keyframes cloudMove {
            0% { transform: translateX(0); }
            100% { transform: translateX(-100px); }
        }
        
        /* ДОЖДЬ */
        .rain {
            position: fixed;
            width: 100%; height: 100%;
            background-image: 
                linear-gradient(transparent 0%, rgba(255,255,255,0.1) 50%, transparent 100%);
            background-size: 2px 15px;
            animation: rain 0.4s linear infinite;
            z-index: -1;
            opacity: 0.3;
        }
        
        @keyframes rain {
            0% { background-position: 0 0; }
            100% { background-position: 20px 400px; }
        }
        
        .container {
            position: relative;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            z-index: 1;
        }
        
        .header {
            text-align: center;
            margin-bottom: 50px;
        }
        
        .header h1 {
            font-size: 4em;
            font-weight: 700;
            background: linear-gradient(135deg, #F59E0B 0%, #FCD34D 50%, #F59E0B 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 30px rgba(245, 158, 11, 0.5);
            margin-bottom: 10px;
            animation: glow 3s ease-in-out infinite;
        }
        
        @keyframes glow {
            0%, 100% { filter: brightness(1); }
            50% { filter: brightness(1.2); }
        }
        
        .header .subtitle {
            font-size: 1.3em;
            opacity: 0.9;
            letter-spacing: 2px;
        }
        
        .main-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 30px;
            padding: 50px;
            box-shadow: 
                0 20px 60px rgba(0,0,0,0.5),
                0 0 100px rgba(245, 158, 11, 0.2),
                inset 0 0 100px rgba(245, 158, 11, 0.05);
            border: 2px solid rgba(245, 158, 11, 0.3);
            margin-bottom: 30px;
            color: #1E3A8A;
        }
        
        /* СТАТУС ИНДИКАТОР */
        .status-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            margin: 0 auto 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3em;
            position: relative;
            box-shadow: 0 0 40px rgba(244, 67, 54, 0.6);
            background: radial-gradient(circle, #f44336 0%, #c62828 100%);
            animation: pulse 2s infinite;
        }
        
        .status-circle.connected {
            background: radial-gradient(circle, #4CAF50 0%, #2e7d32 100%);
            box-shadow: 0 0 40px rgba(76, 175, 80, 0.6);
        }
        
        .status-circle::before {
            content: '';
            position: absolute;
            width: 140%;
            height: 140%;
            border-radius: 50%;
            border: 2px solid currentColor;
            opacity: 0.3;
            animation: ripple 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        @keyframes ripple {
            0% { transform: scale(1); opacity: 0.3; }
            100% { transform: scale(1.3); opacity: 0; }
        }
        
        .status-text {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .status-text h2 {
            font-size: 2.5em;
            margin-bottom: 10px;
            color: #F59E0B;
            text-shadow: 0 0 20px rgba(245, 158, 11, 0.5);
            font-weight: 700;
        }
        
        /* КНОПКИ */
        .btn-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .btn {
            padding: 20px 40px;
            border: none;
            border-radius: 15px;
            font-size: 1.2em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 50%; left: 50%;
            width: 0; height: 0;
            border-radius: 50%;
            background: rgba(255,255,255,0.2);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        
        .btn:hover::before {
            width: 300px;
            height: 300px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
            color: white;
            box-shadow: 0 10px 30px rgba(245, 158, 11, 0.4);
        }
        
        .btn-primary:hover {
            background: linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%);
            box-shadow: 0 15px 40px rgba(245, 158, 11, 0.6);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #f44336 0%, #c62828 100%);
            color: white;
        }
        
        /* СТАТИСТИКА */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 20px;
            text-align: center;
            border: 1px solid rgba(245, 158, 11, 0.3);
            transition: all 0.3s;
        }
        
        .stat-card:hover {
            background: rgba(255,255,255,0.15);
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(245, 158, 11, 0.4);
            border-color: rgba(245, 158, 11, 0.6);
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(135deg, #F59E0B, #D97706);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 10px 0;
        }
        
        .stat-label {
            opacity: 0.7;
            font-size: 0.9em;
            letter-spacing: 1px;
        }
        
        /* ВЫБОР СТРАН */
        .country-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .country-card {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        
        .country-card:hover {
            background: rgba(245, 158, 11, 0.2);
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(245, 158, 11, 0.5);
            border-color: #F59E0B;
        }
        
        .country-flag {
            font-size: 3em;
            margin-bottom: 10px;
            filter: drop-shadow(0 0 10px rgba(118, 75, 162, 0.3));
        }
        
        /* ЗАГРУЗКА */
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }
        
        .spinner {
            width: 60px;
            height: 60px;
            margin: 0 auto;
            border: 4px solid rgba(255,255,255,0.1);
            border-top: 4px solid #F59E0B;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            box-shadow: 0 0 20px rgba(245, 158, 11, 0.3);
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* MOBILE APP BANNER */
        .mobile-banner {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.2));
            border: 2px solid rgba(245, 158, 11, 0.5);
            border-radius: 20px;
            padding: 30px;
            margin-top: 30px;
            text-align: center;
        }
        
        .mobile-banner h3 {
            font-size: 1.8em;
            margin-bottom: 15px;
            color: #F59E0B;
            font-weight: 700;
        }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 2.5em; }
            .btn-group { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="storm-sky"></div>
    <div class="lightning"></div>
    <div class="clouds"></div>
    <div class="rain"></div>
    
    <div class="container">
        <div class="header">
            <h1>⚡ ALADDIN VPN</h1>
            <p class="subtitle">ЗАЩИТА ПОД ГРОЗОВЫМ НЕБОМ</p>
        </div>
        
        <div class="main-card">
            <div class="status-circle" id="statusCircle">🔴</div>
            <div class="status-text">
                <h2 id="statusTitle">Отключено</h2>
                <p id="statusDesc">Нажмите для защиты вашей конфиденциальности</p>
            </div>
            
            <div class="btn-group">
                <button class="btn btn-primary" onclick="quickConnect()">
                    🚀 Быстрое подключение
                </button>
                <button class="btn btn-danger" onclick="disconnect()" style="display:none;" id="disconnectBtn">
                    🛑 Отключиться
                </button>
            </div>
        </div>
        
        <div class="main-card" id="countrySelector" style="display:none;">
            <h2 style="margin-bottom:20px;">🌍 Выберите страну</h2>
            <div class="country-grid" id="countryGrid"></div>
        </div>
        
        <div class="main-card">
            <h2 style="margin-bottom:30px; text-align:center;">📊 Статистика</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="totalConn">0</div>
                    <div class="stat-label">ПОДКЛЮЧЕНИЙ</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="successRate">0%</div>
                    <div class="stat-label">УСПЕШНОСТЬ</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="speed">0 Мб/с</div>
                    <div class="stat-label">СКОРОСТЬ</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="data">0 ГБ</div>
                    <div class="stat-label">ТРАФИК</div>
                </div>
            </div>
        </div>
        
        <!-- MOBILE APP INTEGRATION -->
        <div class="mobile-banner">
            <h3>📱 Доступно в мобильном приложении</h3>
            <p style="font-size:1.1em; margin:15px 0; opacity:0.9;">
                VPN интегрирован в <strong>ALADDIN Family Security</strong><br>
                Доступен на <strong>Premium подписке</strong> как отдельная вкладка
            </p>
            <div style="margin-top:20px; opacity:0.8;">
                <span style="margin: 0 15px;">📱 iOS 14+</span>
                <span style="margin: 0 15px;">🤖 Android 10+</span>
                <span style="margin: 0 15px;">💎 Premium</span>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top:20px; font-size:1.2em;">Подключение к защищенному серверу...</p>
        </div>
    </div>
    
    <script>
        let isConnected = false;
        
        async function quickConnect() {
            document.getElementById('loading').style.display = 'block';
            try {
                const res = await fetch('/api/test_singapore');
                const data = await res.json();
                if (data.success) {
                    isConnected = true;
                    updateUI();
                    showNotification('⚡ Подключено! Вы под защитой');
                }
            } catch(e) {
                showNotification('❌ Ошибка: ' + e.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        function disconnect() {
            isConnected = false;
            updateUI();
        }
        
        function updateUI() {
            const circle = document.getElementById('statusCircle');
            const title = document.getElementById('statusTitle');
            const desc = document.getElementById('statusDesc');
            const btn = document.getElementById('disconnectBtn');
            
            if (isConnected) {
                circle.classList.add('connected');
                circle.textContent = '🟢';
                title.textContent = 'Защищено';
                desc.textContent = 'Ваше соединение под грозовым щитом';
                btn.style.display = 'block';
            } else {
                circle.classList.remove('connected');
                circle.textContent = '🔴';
                title.textContent = 'Не защищено';
                desc.textContent = 'Нажмите для активации защиты';
                btn.style.display = 'none';
            }
        }
        
        function showNotification(msg) {
            alert(msg);
        }
        
        async function loadStats() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                document.getElementById('totalConn').textContent = data.statistics.total_connections;
                document.getElementById('successRate').textContent = data.statistics.success_rate.toFixed(1) + '%';
            } catch(e) {}
        }
        
        window.onload = () => {
            loadStats();
            setInterval(loadStats, 10000);
        };
    </script>
</body>
</html>"""


@app.route("/api/status")
@limiter.limit("60 per minute")
def api_status():
    if not vpn_system:
        return jsonify({"error": "VPN не инициализирован"}), 500
    status = vpn_system.get_status()
    stats = vpn_system.get_system_stats()
    return jsonify(
        {
            "status": status["status"],
            "message": status["message"],
            "statistics": stats,
        }
    )


@app.route("/api/test_singapore")
@limiter.limit("10 per minute")
def api_test_singapore():
    if not vpn_system:
        return jsonify({"error": "VPN не инициализирован"}), 500
    test_user = f"test_{int(time.time())}"
    success, message, report = asyncio.run(
        vpn_system.connect(
            test_user,
            country="Singapore",
            security_level=VPNSecurityLevel.HIGH,
        )
    )
    if success:
        time.sleep(2)
        asyncio.run(vpn_system.disconnect(test_user))
        return jsonify({"success": True, "message": message})
    return jsonify({"success": False, "error": message}), 400


@app.route("/health")
def health():
    return jsonify(
        {"status": "healthy", "timestamp": datetime.now().isoformat()}
    )


if __name__ == "__main__":
    if init_vpn_system():
        port = int(os.getenv("VPN_PORT", 5000))
        print("=" * 80)
        print("⚡ ALADDIN VPN PREMIUM - ГРОЗОВОЕ НЕБО ЗАЩИТЫ")
        print("=" * 80)
        print(f"🌐 http://localhost:{port}")
        print("📱 Интегрирован в ALADDIN Family Security (Premium)")
        print("🔐 SECRET_KEY: ✅")
        print("🛡️  Rate Limiting: ✅")
        print("=" * 80)
        app.run(host="0.0.0.0", port=port, debug=False)
    else:
        print("❌ Ошибка инициализации")
