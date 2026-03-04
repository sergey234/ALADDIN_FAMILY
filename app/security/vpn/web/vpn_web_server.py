"""
Flask сервер для VPN веб-интерфейса ALADDIN
Магический дашборд с глубоким синим и золотыми блестками
"""

import json
import os
import sys
import time
from datetime import datetime

import asyncio
from flask import Flask, jsonify, render_template, request

# Добавляем путь к VPN модулям

try:
    from integration.aladdin_vpn_integration import ALADDINVPNIntegration
    from ui.vpn_interface import ALADDINVPNInterface
except ImportError:
    # Создаем mock классы для совместимости
    class ALADDINVPNIntegration:
        def integrate_with_aladdin(self):
            print("Mock VPN Integration")
    
    class ALADDINVPNInterface:
        def get_status(self):
            return {"connected": False, "server": "None"}
        def get_servers(self):
            return [{"name": "Test Server", "country": "Test"}]
        def connect(self, server=None):
            return {"success": True, "message": "Connected to Test Server"}
        def disconnect(self):
            return {"success": True, "message": "Disconnected"}
        def select_server(self, server_id):
            return True

app = Flask(__name__)

# Инициализация VPN компонентов
vpn_interface = ALADDINVPNInterface()
vpn_integration = ALADDINVPNIntegration()

# Интеграция с ALADDIN
vpn_integration.integrate_with_aladdin()


@app.route("/")
def dashboard():
    """Главная страница дашборда"""
    return render_template("vpn_dashboard.html")


@app.route("/api/status")
def get_status():
    """Получение статуса VPN"""
    try:
        status = vpn_interface.get_status()
        return jsonify({"success": True, "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/servers")
def get_servers():
    """Получение списка серверов"""
    try:
        servers = vpn_interface.get_servers()
        return jsonify({"success": True, "data": servers})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/connect", methods=["POST"])
def connect_vpn():
    """Подключение к VPN"""
    try:
        data = request.get_json()
        server_id = data.get("server_id")

        if server_id:
            # Выбираем сервер
            if not vpn_interface.select_server(server_id):
                return (
                    jsonify(
                        {"success": False, "error": "Ошибка выбора сервера"}
                    ),
                    400,
                )

        # Подключаемся
        result = vpn_interface.connect()
        success = result.get("success", False)

        if success:
            return jsonify(
                {"success": True, "message": "VPN подключен успешно"}
            )
        else:
            return (
                jsonify(
                    {"success": False, "error": "Ошибка подключения к VPN"}
                ),
                500,
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/disconnect", methods=["POST"])
def disconnect_vpn():
    """Отключение от VPN"""
    try:
        result = vpn_interface.disconnect()
        success = result.get("success", False)

        if success:
            return jsonify(
                {"success": True, "message": "VPN отключен успешно"}
            )
        else:
            return (
                jsonify(
                    {"success": False, "error": "Ошибка отключения от VPN"}
                ),
                500,
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/family-stats")
def get_family_stats():
    """Получение статистики семьи"""
    try:
        stats = vpn_integration.get_family_vpn_stats()
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/quick-connect", methods=["POST"])
def quick_connect():
    """Быстрое подключение к лучшему серверу"""
    try:
        # Выбираем лучший сервер автоматически
        best_server = vpn_interface._select_best_server()
        if not best_server:
            return (
                jsonify({"success": False, "error": "Нет доступных серверов"}),
                400,
            )

        # Подключаемся
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(vpn_interface.connect())
        loop.close()

        if success:
            return jsonify(
                {
                    "success": True,
                    "message": f"Подключен к {best_server.name}",
                    "server": {
                        "id": best_server.id,
                        "name": best_server.name,
                        "country": best_server.country,
                        "flag": best_server.flag,
                        "ping": best_server.ping,
                    },
                }
            )
        else:
            return (
                jsonify(
                    {"success": False, "error": "Ошибка подключения к VPN"}
                ),
                500,
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/settings", methods=["GET", "POST"])
def vpn_settings():
    """Настройки VPN"""
    if request.method == "GET":
        try:
            # Получаем текущие настройки
            settings = {
                "auto_connect": True,
                "preferred_protocol": "wireguard",
                "family_mode": True,
                "child_safe_mode": True,
                "content_filtering": True,
            }
            return jsonify({"success": True, "data": settings})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    elif request.method == "POST":
        try:
            data = request.get_json()
            # Обновляем настройки семьи
            if "family_settings" in data:
                vpn_integration.update_family_settings(data["family_settings"])

            return jsonify({"success": True, "message": "Настройки обновлены"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/check-permission", methods=["POST"])
def check_permission():
    """Проверка разрешения на VPN для члена семьи"""
    try:
        data = request.get_json()
        member_type = data.get("member_type", "parent")

        permission = vpn_integration.check_vpn_permission(member_type)
        recommendations = vpn_integration.get_vpn_recommendations(member_type)

        return jsonify(
            {
                "success": True,
                "data": {
                    "permission": permission,
                    "recommendations": recommendations,
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/content-filter", methods=["POST"])
def check_content_filter():
    """Проверка URL через фильтр контента"""
    try:
        data = request.get_json()
        url = data.get("url", "")

        allowed = vpn_integration.check_content_filter(url)

        return jsonify(
            {"success": True, "data": {"url": url, "allowed": allowed}}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("🔮 Запуск магического VPN дашборда ALADDIN...")
    print("🌐 Откройте: http://localhost:5001")
    print("✨ Цвета: Глубокий синий + золотые блестки")

    app.run(host="0.0.0.0", port=5001, debug=True, threaded=True)
