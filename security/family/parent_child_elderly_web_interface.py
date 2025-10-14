#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Family Web Interface - Специализированный веб-интерфейс
для родителей, детей и пожилых людей

Автор: ALADDIN Security Team
Версия: 2.5
Дата: 2025-01-26
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Добавляем путь к проекту

try:
    from security.family.child_protection import ChildProtection

    ALADDIN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ALADDIN modules not available: {e}")
    ALADDIN_AVAILABLE = False

# SFM (опциональный)
try:
    from core.sfm import SafeFunctionManager

    SFM_AVAILABLE = True
except ImportError:
    SFM_AVAILABLE = False

# Дополнительные модули (опциональные)
try:
    from security.ai_agents.elderly_interface_manager import (
        ElderlyInterfaceManager,
    )

    ELDERLY_MANAGER_AVAILABLE = True
except ImportError:
    ELDERLY_MANAGER_AVAILABLE = False

# FamilyCommunicationHub временно отключен
FAMILY_HUB_AVAILABLE = False

# Создание FastAPI приложения
app = FastAPI(
    title="🛡️ ALADDIN Family Web Interface",
    description="Веб-интерфейс для родителей, детей и пожилых людей",
    version="2.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка шаблонов
templates = Jinja2Templates(directory="templates")


# Модели данных
class UserProfile(BaseModel):
    """Профиль пользователя"""

    user_id: str
    name: str
    age: int
    role: str  # parent, child, elderly
    preferences: Dict[str, Any]
    security_level: str


class ChildActivity(BaseModel):
    """Активность ребенка"""

    child_id: str
    activity_type: str
    duration: int
    timestamp: datetime
    content_category: str
    safety_score: float


class ParentNotification(BaseModel):
    """Уведомление для родителей"""

    notification_id: str
    child_id: str
    message: str
    severity: str
    timestamp: datetime
    action_required: bool


class ElderlyAlert(BaseModel):
    """Алерт для пожилых людей"""

    alert_id: str
    user_id: str
    alert_type: str
    message: str
    timestamp: datetime
    location: Optional[str] = None


# Инициализация компонентов
if ALADDIN_AVAILABLE:
    child_protection = ChildProtection()
    # ParentalControls требует дополнительные аргументы, пока отключим
    parental_controls = None
else:
    child_protection = None
    parental_controls = None

if SFM_AVAILABLE:
    sfm = SafeFunctionManager()
else:
    sfm = None

# Дополнительные компоненты (опциональные)
if ELDERLY_MANAGER_AVAILABLE:
    elderly_manager = ElderlyInterfaceManager()
else:
    elderly_manager = None

if FAMILY_HUB_AVAILABLE:
    # FamilyCommunicationHub требует family_id, пока отключим
    family_hub = None
else:
    family_hub = None

# HTML шаблоны
PARENT_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ ALADDIN - Панель родителей</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
               background: #f5f7fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                  color: white; padding: 20px; text-align: center; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .dashboard-grid { display: grid;
                         grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                         gap: 20px; margin-top: 20px; }
        .card { background: white; border-radius: 10px; padding: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .card h3 { color: #333; margin-bottom: 15px; }
        .child-card { border-left: 4px solid #4CAF50; }
        .alert-card { border-left: 4px solid #f44336; }
        .stats-grid { display: grid;
                     grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                     gap: 15px; }
        .stat-item { text-align: center; padding: 15px;
                    background: #f8f9fa; border-radius: 8px; }
        .stat-value { font-size: 24px; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; font-size: 14px; }
        .btn { background: #667eea; color: white; border: none;
               padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #5a6fd8; }
        .notification { background: #fff3cd; border: 1px solid #ffeaa7;
                       padding: 10px; border-radius: 5px; margin: 10px 0; }
        .alert { background: #f8d7da; border: 1px solid #f5c6cb;
                 padding: 10px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ ALADDIN - Панель родителей</h1>
        <p>Безопасность вашей семьи под контролем</p>
    </div>

    <div class="container">
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value" id="total-children">0</div>
                <div class="stat-label">Детей онлайн</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="blocked-threats">0</div>
                <div class="stat-label">Заблокировано угроз</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="screen-time">0ч</div>
                <div class="stat-label">Общее время экрана</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="safety-score">100%</div>
                <div class="stat-label">Уровень безопасности</div>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="card child-card">
                <h3>👶 Дети</h3>
                <div id="children-list">
                    <p>Загрузка данных...</p>
                </div>
            </div>

            <div class="card alert-card">
                <h3>🚨 Уведомления</h3>
                <div id="notifications-list">
                    <p>Загрузка уведомлений...</p>
                </div>
            </div>

            <div class="card">
                <h3>📊 Статистика</h3>
                <div id="statistics">
                    <p>Загрузка статистики...</p>
                </div>
            </div>

            <div class="card">
                <h3>⚙️ Настройки</h3>
                <button class="btn" onclick="openSettings()">Настройки безопасности</button>
                <button class="btn" onclick="openReports()">Отчеты</button>
                <button class="btn" onclick="openEmergency()">Экстренные действия</button>
            </div>
        </div>
    </div>

    <script>
        // Обновление данных каждые 30 секунд
        setInterval(updateDashboard, 30000);

        async function updateDashboard() {
            try {
                const response = await fetch('/api/parent/dashboard');
                const data = await response.json();

                // Обновляем статистику
                document.getElementById('total-children').textContent =
                    data.total_children || 0;
                document.getElementById('blocked-threats').textContent =
                    data.blocked_threats || 0;
                document.getElementById('screen-time').textContent =
                    data.total_screen_time || '0ч';
                document.getElementById('safety-score').textContent =
                    data.safety_score || '100%';

                // Обновляем список детей
                updateChildrenList(data.children || []);

                // Обновляем уведомления
                updateNotifications(data.notifications || []);

            } catch (error) {
                console.error('Ошибка обновления дашборда:', error);
            }
        }

        function updateChildrenList(children) {
            const container = document.getElementById('children-list');
            if (children.length === 0) {
                container.innerHTML = '<p>Нет активных детей</p>';
                return;
            }

            container.innerHTML = children.map(child => `
                <div class="notification">
                    <strong>${child.name}</strong> (${child.age} лет)<br>
                    Статус: ${child.status}<br>
                    Время экрана: ${child.screen_time} мин<br>
                    Уровень защиты: ${child.protection_level}
                </div>
            `).join('');
        }

        function updateNotifications(notifications) {
            const container = document.getElementById('notifications-list');
            if (notifications.length === 0) {
                container.innerHTML = '<p>Нет новых уведомлений</p>';
                return;
            }

            container.innerHTML = notifications.map(notif => `
                <div class="alert">
                    <strong>${notif.severity}</strong><br>
                    ${notif.message}<br>
                    <small>${new Date(notif.timestamp).toLocaleString()}</small>
                </div>
            `).join('');
        }

        function openSettings() {
            window.open('/parent/settings', '_blank');
        }

        function openReports() {
            window.open('/parent/reports', '_blank');
        }

        function openEmergency() {
            window.open('/parent/emergency', '_blank');
        }

        // Загружаем данные при загрузке страницы
        updateDashboard();
    </script>
</body>
</html>
"""

CHILD_INTERFACE_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ ALADDIN - Мой интерфейс</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Comic Sans MS', cursive; background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); color: white; }
        .header { text-align: center; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .game-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px; }
        .game-card { background: rgba(255,255,255,0.2); border-radius: 15px; padding: 20px; text-align: center; cursor: pointer; transition: transform 0.3s; }
        .game-card:hover { transform: scale(1.05); }
        .game-card h3 { margin-bottom: 10px; }
        .progress-bar { background: rgba(255,255,255,0.3); border-radius: 10px; height: 20px; margin: 10px 0; }
        .progress-fill { background: #00b894; height: 100%; border-radius: 10px; transition: width 0.3s; }
        .achievement { background: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; margin: 10px 0; }
        .btn { background: #00b894; color: white; border: none; padding: 15px 30px; border-radius: 25px; cursor: pointer; font-size: 16px; margin: 10px; }
        .btn:hover { background: #00a085; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎮 Добро пожаловать в ALADDIN!</h1>
        <p>Безопасные игры и обучение</p>
    </div>

    <div class="container">
        <div class="achievement">
            <h3>🏆 Мои достижения</h3>
            <p>Очки безопасности: <span id="safety-points">0</span></p>
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
            </div>
        </div>

        <div class="game-grid">
            <div class="game-card" onclick="startGame('security')">
                <h3>🛡️ Игра безопасности</h3>
                <p>Изучай правила безопасности</p>
            </div>

            <div class="game-card" onclick="startGame('learning')">
                <h3>📚 Обучающие игры</h3>
                <p>Развивайся и учись</p>
            </div>

            <div class="game-card" onclick="startGame('art')">
                <h3>🎨 Творчество</h3>
                <p>Рисуй и создавай</p>
            </div>

            <div class="game-card" onclick="startGame('music')">
                <h3>🎵 Музыка</h3>
                <p>Слушай и играй</p>
            </div>
        </div>

        <div style="text-align: center; margin-top: 30px;">
            <button class="btn" onclick="requestParentPermission()">Попросить разрешение</button>
            <button class="btn" onclick="viewMyProgress()">Мой прогресс</button>
        </div>
    </div>

    <script>
        async function startGame(gameType) {
            try {
                const response = await fetch(`/api/child/start-game`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ game_type: gameType })
                });

                if (response.ok) {
                    alert('Игра запущена!');
                    updateProgress();
                } else {
                    alert('Нужно разрешение родителей');
                }
            } catch (error) {
                console.error('Ошибка запуска игры:', error);
            }
        }

        function requestParentPermission() {
            alert('Запрос отправлен родителям!');
        }

        function viewMyProgress() {
            window.open('/child/progress', '_blank');
        }

        function updateProgress() {
            // Обновляем прогресс
            const points = parseInt(document.getElementById('safety-points').textContent) + 10;
            document.getElementById('safety-points').textContent = points;
            document.getElementById('progress-fill').style.width = Math.min(points, 100) + '%';
        }

        // Загружаем начальные данные
        document.getElementById('safety-points').textContent = '50';
        document.getElementById('progress-fill').style.width = '50%';
    </script>
</body>
</html>
"""

ELDERLY_INTERFACE_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ ALADDIN - Помощник для пожилых</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Arial', sans-serif; background: #f8f9fa; font-size: 18px; }
        .header { background: #28a745; color: white; padding: 30px; text-align: center; }
        .container { max-width: 1000px; margin: 0 auto; padding: 30px; }
        .help-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-top: 30px; }
        .help-card { background: white; border-radius: 15px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
        .help-card h3 { color: #28a745; margin-bottom: 20px; font-size: 24px; }
        .help-card p { color: #666; margin-bottom: 20px; line-height: 1.6; }
        .btn { background: #28a745; color: white; border: none; padding: 20px 40px; border-radius: 10px; cursor: pointer; font-size: 18px; margin: 10px; }
        .btn:hover { background: #218838; }
        .btn-large { padding: 25px 50px; font-size: 20px; }
        .emergency-btn { background: #dc3545; }
        .emergency-btn:hover { background: #c82333; }
        .status-indicator { display: inline-block; width: 20px; height: 20px; border-radius: 50%; margin-right: 10px; }
        .status-ok { background: #28a745; }
        .status-warning { background: #ffc107; }
        .status-danger { background: #dc3545; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ ALADDIN - Ваш помощник</h1>
        <p>Безопасность и помощь всегда рядом</p>
    </div>

    <div class="container">
        <div class="help-grid">
            <div class="help-card">
                <h3>🚨 Экстренная помощь</h3>
                <p>Нажмите кнопку, если нужна срочная помощь</p>
                <button class="btn emergency-btn btn-large" onclick="callEmergency()">
                    🚨 ЭКСТРЕННАЯ ПОМОЩЬ
                </button>
            </div>

            <div class="help-card">
                <h3>👨‍⚕️ Медицинская помощь</h3>
                <p>Связь с врачом или вызов скорой</p>
                <button class="btn btn-large" onclick="callMedical()">
                    🏥 Медицинская помощь
                </button>
            </div>

            <div class="help-card">
                <h3>👨‍👩‍👧‍👦 Связь с семьей</h3>
                <p>Позвонить родственникам</p>
                <button class="btn btn-large" onclick="callFamily()">
                    📞 Позвонить семье
                </button>
            </div>

            <div class="help-card">
                <h3>🏠 Умный дом</h3>
                <p>Управление домом и безопасностью</p>
                <button class="btn btn-large" onclick="openSmartHome()">
                    🏠 Управление домом
                </button>
            </div>

            <div class="help-card">
                <h3>📱 Простые приложения</h3>
                <p>Полезные приложения для пожилых</p>
                <button class="btn btn-large" onclick="openApps()">
                    📱 Мои приложения
                </button>
            </div>

            <div class="help-card">
                <h3>📊 Мое здоровье</h3>
                <p>Мониторинг здоровья и активности</p>
                <button class="btn btn-large" onclick="openHealth()">
                    ❤️ Мое здоровье
                </button>
            </div>
        </div>

        <div style="text-align: center; margin-top: 40px;">
            <h3>Статус системы</h3>
            <p><span class="status-indicator status-ok"></span>Система безопасности активна</p>
            <p><span class="status-indicator status-ok"></span>Связь с семьей установлена</p>
            <p><span class="status-indicator status-ok"></span>Медицинский мониторинг работает</p>
        </div>
    </div>

    <script>
        function callEmergency() {
            if (confirm('Вы уверены, что нужна экстренная помощь?')) {
                alert('Экстренная помощь вызвана! Семья уведомлена.');
                // Здесь будет реальный вызов экстренных служб
            }
        }

        function callMedical() {
            alert('Связываемся с врачом...');
        }

        function callFamily() {
            alert('Звоним семье...');
        }

        function openSmartHome() {
            window.open('/elderly/smart-home', '_blank');
        }

        function openApps() {
            window.open('/elderly/apps', '_blank');
        }

        function openHealth() {
            window.open('/elderly/health', '_blank');
        }
    </script>
</body>
</html>
"""


# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница с выбором интерфейса"""
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🛡️ ALADDIN Family Interface</title>
        <style>
            body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 50px; }
            .container { max-width: 800px; margin: 0 auto; }
            .interface-card { background: rgba(255,255,255,0.1); border-radius: 15px; padding: 30px; margin: 20px; cursor: pointer; transition: transform 0.3s; }
            .interface-card:hover { transform: scale(1.05); }
            .interface-card h2 { margin-bottom: 15px; }
            .btn { background: #28a745; color: white; border: none; padding: 15px 30px; border-radius: 10px; cursor: pointer; font-size: 18px; margin: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ ALADDIN Family Interface</h1>
            <p>Выберите ваш интерфейс:</p>

            <div class="interface-card" onclick="window.location.href='/parent'">
                <h2>👨‍👩‍👧‍👦 Для родителей</h2>
                <p>Управление безопасностью детей, мониторинг активности, настройки защиты</p>
            </div>

            <div class="interface-card" onclick="window.location.href='/child'">
                <h2>👶 Для детей</h2>
                <p>Безопасные игры, обучение, развлечения под контролем родителей</p>
            </div>

            <div class="interface-card" onclick="window.location.href='/elderly'">
                <h2>👴👵 Для пожилых</h2>
                <p>Помощь, экстренные вызовы, связь с семьей, простое управление</p>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/parent", response_class=HTMLResponse)
async def parent_interface():
    """Интерфейс для родителей"""
    return PARENT_DASHBOARD_HTML


@app.get("/child", response_class=HTMLResponse)
async def child_interface():
    """Интерфейс для детей"""
    return CHILD_INTERFACE_HTML


@app.get("/elderly", response_class=HTMLResponse)
async def elderly_interface():
    """Интерфейс для пожилых людей"""
    return ELDERLY_INTERFACE_HTML


# API для родителей
@app.get("/api/parent/dashboard")
async def get_parent_dashboard():
    """Получить данные дашборда для родителей"""
    if not ALADDIN_AVAILABLE:
        return {"error": "ALADDIN система недоступна"}

    try:
        # Получаем данные о детях
        children_data = []
        if child_protection:
            family_dashboard = child_protection.get_family_dashboard()
            children_data = family_dashboard.get("children", [])

        # Получаем статистику
        stats = {
            "total_children": len(children_data),
            "blocked_threats": 0,
            "total_screen_time": sum(
                child.get("total_screen_time_today", 0)
                for child in children_data
            ),
            "safety_score": "95%",
            "children": children_data,
            "notifications": [],
        }

        return stats
    except Exception as e:
        return {"error": f"Ошибка получения данных: {str(e)}"}


@app.post("/api/child/start-game")
async def start_child_game(request: Request):
    """Запуск игры для ребенка"""
    data = await request.json()
    game_type = data.get("game_type", "security")

    # Здесь будет логика проверки разрешений и запуска игры
    return {
        "success": True,
        "game_type": game_type,
        "message": "Игра запущена",
    }


# API для пожилых людей
@app.post("/api/elderly/emergency")
async def elderly_emergency():
    """Экстренный вызов для пожилых людей"""
    # Здесь будет логика экстренного вызова
    return {"success": True, "message": "Экстренная помощь вызвана"}


if __name__ == "__main__":
    print("🚀 Запуск ALADDIN Family Web Interface...")
    print("🌐 Веб-интерфейс будет доступен по адресам:")
    print("   - Главная страница: http://localhost:8082")
    print("   - Для родителей: http://localhost:8082/parent")
    print("   - Для детей: http://localhost:8082/child")
    print("   - Для пожилых: http://localhost:8082/elderly")
    uvicorn.run(app, host="0.0.0.0", port=8082)

