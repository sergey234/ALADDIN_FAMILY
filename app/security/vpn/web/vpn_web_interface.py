"""
Веб-интерфейс VPN для ALADDIN
Красивый и функциональный веб-интерфейс для управления VPN
"""

import logging as std_logging
import threading
import time

import asyncio
import os
import sys

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit

# Добавляем путь для импорта VPN модулей

try:
    from integration.aladdin_vpn_integration import ALADDINVPNIntegration
    from protocols.shadowsocks_client import ALADDINShadowsocksClient
    from protocols.v2ray_client import ALADDINV2RayClient
    from ui.vpn_interface import ALADDINVPNInterface
    VPN_MODULES_AVAILABLE = True
except ImportError:
    VPN_MODULES_AVAILABLE = False
    # Создаем mock классы для совместимости

    class ALADDINVPNIntegration:
        pass

    class ALADDINShadowsocksClient:
        pass

    class ALADDINV2RayClient:
        pass

    class ALADDINVPNInterface:
        pass

# Настройка логирования
std_logging.basicConfig(level=std_logging.INFO)
logger = std_logging.getLogger(__name__)

# VPN модули уже импортированы выше

app = Flask(__name__)
app.config["SECRET_KEY"] = "aladdin_vpn_secret_key_2025"
socketio = SocketIO(app, cors_allowed_origins="*")

# Инициализируем VPN компоненты
vpn_interface = ALADDINVPNInterface()
vpn_integration = ALADDINVPNIntegration()
shadowsocks_client = ALADDINShadowsocksClient()
v2ray_client = ALADDINV2RayClient()

# Глобальные переменные для состояния
vpn_status = {
    "is_connected": False,
    "current_server": None,
    "connection_time": 0,
    "bytes_sent": 0,
    "bytes_received": 0,
    "speed": {"download": 0, "upload": 0},
}


@app.route("/")
def index():
    """Главная страница VPN"""
    return render_template("vpn_dashboard.html")


@app.route("/settings")
def settings():
    """Страница настроек VPN"""
    return render_template("vpn_settings.html")


@app.route("/statistics")
def statistics():
    """Страница статистики VPN"""
    return render_template("vpn_statistics.html")


@app.route("/api/status")
def api_status():
    """API получения статуса VPN"""
    try:
        status = vpn_interface.get_status()
        return jsonify({"success": True, "data": status})
    except Exception as e:
        logger.error(f"Ошибка получения статуса: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/servers")
def api_servers():
    """API получения списка серверов"""
    try:
        servers = vpn_interface.get_servers()
        return jsonify({"success": True, "data": servers})
    except Exception as e:
        logger.error(f"Ошибка получения серверов: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/connect", methods=["POST"])
def api_connect():
    """API подключения к VPN"""
    try:
        data = request.get_json()
        server_id = data.get("server_id")

        if server_id:
            # Выбираем конкретный сервер
            if not vpn_interface.select_server(server_id):
                return jsonify(
                    {"success": False, "error": "Ошибка выбора сервера"}
                )

        # Подключаемся
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(vpn_interface.connect())
        loop.close()

        if success:
            # Обновляем глобальное состояние
            vpn_status["is_connected"] = True
            vpn_status["current_server"] = vpn_interface.current_server

            # Уведомляем клиентов через WebSocket
            socketio.emit(
                "vpn_status_update",
                {
                    "is_connected": True,
                    "server": (
                        vpn_interface.current_server.name
                        if vpn_interface.current_server
                        else None
                    ),
                },
            )

            return jsonify(
                {"success": True, "message": "VPN подключен успешно"}
            )
        else:
            return jsonify(
                {"success": False, "error": "Ошибка подключения к VPN"}
            )

    except Exception as e:
        logger.error(f"Ошибка подключения VPN: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/disconnect", methods=["POST"])
def api_disconnect():
    """API отключения от VPN"""
    try:
        # Отключаемся
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(vpn_interface.disconnect())
        loop.close()

        if success:
            # Обновляем глобальное состояние
            vpn_status["is_connected"] = False
            vpn_status["current_server"] = None

            # Уведомляем клиентов через WebSocket
            socketio.emit(
                "vpn_status_update", {"is_connected": False, "server": None}
            )

            return jsonify(
                {"success": True, "message": "VPN отключен успешно"}
            )
        else:
            return jsonify(
                {"success": False, "error": "Ошибка отключения от VPN"}
            )

    except Exception as e:
        logger.error(f"Ошибка отключения VPN: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/family_stats")
def api_family_stats():
    """API получения статистики семьи"""
    try:
        stats = vpn_integration.get_family_vpn_stats()
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        logger.error(f"Ошибка получения статистики семьи: {e}")
        return jsonify({"success": False, "error": str(e)})


@socketio.on("connect")
def handle_connect():
    """Обработка подключения WebSocket"""
    logger.info("Клиент подключен к WebSocket")
    emit("vpn_status_update", vpn_status)


@socketio.on("disconnect")
def handle_disconnect():
    """Обработка отключения WebSocket"""
    logger.info("Клиент отключен от WebSocket")


def start_vpn_monitoring():
    """Запуск мониторинга VPN в фоновом режиме"""
    while True:
        try:
            if vpn_status["is_connected"]:
                # Обновляем статистику
                status = vpn_interface.get_status()
                vpn_status.update(status)

                # Отправляем обновления клиентам
                socketio.emit(
                    "vpn_stats_update",
                    {
                        "connection_time": status["connection_time"],
                        "bytes_sent": status["bytes_sent"],
                        "bytes_received": status["bytes_received"],
                        "speed": status["speed"],
                    },
                )

            time.sleep(1)  # Обновляем каждую секунду

        except Exception as e:
            logger.error(f"Ошибка мониторинга VPN: {e}")
            time.sleep(5)


if __name__ == "__main__":
    # Запускаем мониторинг в фоновом режиме
    monitoring_thread = threading.Thread(
        target=start_vpn_monitoring, daemon=True
    )
    monitoring_thread.start()

    # Запускаем веб-сервер
    logger.info("Запуск VPN веб-интерфейса на http://localhost:5001")
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
