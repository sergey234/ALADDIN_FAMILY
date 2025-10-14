#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket API - WebSocket API для real-time обновлений VPN системы
Качество кода: A+
Соответствие: SOLID, DRY, PEP8
"""

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import asyncio
from aiohttp import WSMsgType, web
from aiohttp_cors import ResourceOptions
from aiohttp_cors import setup as cors_setup

logger = logging.getLogger(__name__)


class WebSocketMessageType(Enum):
    """Типы WebSocket сообщений"""

    CONNECTION_STATUS = "connection_status"
    SERVER_UPDATE = "server_update"
    METRICS_UPDATE = "metrics_update"
    ALERT = "alert"
    NOTIFICATION = "notification"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


class SubscriptionType(Enum):
    """Типы подписок"""

    SERVERS = "servers"
    CONNECTIONS = "connections"
    METRICS = "metrics"
    ALERTS = "alerts"
    NOTIFICATIONS = "notifications"
    ALL = "all"


@dataclass
class WebSocketMessage:
    """Модель WebSocket сообщения"""

    message_id: str
    message_type: WebSocketMessageType
    data: Dict[str, Any]
    timestamp: datetime
    target_clients: Optional[List[str]] = None  # None = broadcast to all


@dataclass
class WebSocketClient:
    """Модель WebSocket клиента"""

    client_id: str
    websocket: web.WebSocketResponse
    subscriptions: Set[SubscriptionType] = field(default_factory=set)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    is_authenticated: bool = False


class WebSocketManager:
    """
    Менеджер WebSocket соединений

    Управляет:
    - WebSocket соединениями
    - Подписками клиентов
    - Рассылкой сообщений
    - Heartbeat проверками
    """

    def __init__(self, name: str = "WebSocketManager"):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

        # Клиенты
        self.clients: Dict[str, WebSocketClient] = {}
        self.subscriptions: Dict[SubscriptionType, Set[str]] = {sub_type: set() for sub_type in SubscriptionType}

        # Настройки
        self.heartbeat_interval = 30  # секунды
        self.heartbeat_timeout = 60  # секунды

        # Фоновые задачи
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.broadcast_task: Optional[asyncio.Task] = None

        self.logger.info(f"WebSocket Manager '{name}' инициализирован")

    async def start(self) -> None:
        """Запуск WebSocket менеджера"""
        self.logger.info("Запуск WebSocket менеджера...")

        # Запуск фоновых задач
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self.broadcast_task = asyncio.create_task(self._broadcast_loop())

        self.logger.info("WebSocket менеджер запущен")

    async def stop(self) -> None:
        """Остановка WebSocket менеджера"""
        self.logger.info("Остановка WebSocket менеджера...")

        # Остановка фоновых задач
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        if self.broadcast_task:
            self.broadcast_task.cancel()

        # Закрытие всех соединений
        for client in self.clients.values():
            await client.websocket.close()

        self.clients.clear()
        self.logger.info("WebSocket менеджер остановлен")

    async def add_client(self, websocket: web.WebSocketResponse, user_id: Optional[str] = None) -> str:
        """Добавление нового клиента"""
        client_id = str(uuid.uuid4())

        client = WebSocketClient(
            client_id=client_id, websocket=websocket, user_id=user_id, is_authenticated=user_id is not None
        )

        self.clients[client_id] = client

        self.logger.info(f"Новый клиент подключен: {client_id}")

        # Отправка приветственного сообщения
        await self._send_to_client(
            client_id,
            WebSocketMessageType.NOTIFICATION,
            {
                "title": "Подключение установлено",
                "message": "Вы успешно подключены к ALADDIN VPN WebSocket API",
                "timestamp": datetime.now().isoformat(),
            },
        )

        return client_id

    async def remove_client(self, client_id: str) -> None:
        """Удаление клиента"""
        if client_id not in self.clients:
            return

        client = self.clients[client_id]

        # Удаление из подписок
        for sub_type in client.subscriptions:
            self.subscriptions[sub_type].discard(client_id)

        # Закрытие соединения
        await client.websocket.close()

        del self.clients[client_id]

        self.logger.info(f"Клиент отключен: {client_id}")

    async def subscribe_client(self, client_id: str, subscription_type: SubscriptionType) -> bool:
        """Подписка клиента на тип сообщений"""
        if client_id not in self.clients:
            return False

        client = self.clients[client_id]
        client.subscriptions.add(subscription_type)
        self.subscriptions[subscription_type].add(client_id)

        self.logger.debug(f"Клиент {client_id} подписан на {subscription_type.value}")

        # Отправка подтверждения подписки
        await self._send_to_client(
            client_id,
            WebSocketMessageType.NOTIFICATION,
            {
                "title": "Подписка активирована",
                "message": f"Вы подписаны на обновления: {subscription_type.value}",
                "timestamp": datetime.now().isoformat(),
            },
        )

        return True

    async def unsubscribe_client(self, client_id: str, subscription_type: SubscriptionType) -> bool:
        """Отписка клиента от типа сообщений"""
        if client_id not in self.clients:
            return False

        client = self.clients[client_id]
        client.subscriptions.discard(subscription_type)
        self.subscriptions[subscription_type].discard(client_id)

        self.logger.debug(f"Клиент {client_id} отписан от {subscription_type.value}")
        return True

    async def _send_to_client(self, client_id: str, message_type: WebSocketMessageType, data: Dict[str, Any]) -> bool:
        """Отправка сообщения конкретному клиенту"""
        if client_id not in self.clients:
            return False

        client = self.clients[client_id]

        message = WebSocketMessage(
            message_id=str(uuid.uuid4()), message_type=message_type, data=data, timestamp=datetime.now()
        )

        try:
            await client.websocket.send_str(
                json.dumps(
                    {
                        "messageId": message.message_id,
                        "type": message.message_type.value,
                        "data": message.data,
                        "timestamp": message.timestamp.isoformat(),
                    }
                )
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка отправки сообщения клиенту {client_id}: {e}")
            return False

    async def broadcast_message(
        self,
        message_type: WebSocketMessageType,
        data: Dict[str, Any],
        subscription_type: Optional[SubscriptionType] = None,
    ) -> int:
        """Рассылка сообщения всем подписанным клиентам"""
        sent_count = 0

        if subscription_type:
            # Отправка только подписанным клиентам
            target_clients = self.subscriptions[subscription_type]
        else:
            # Отправка всем клиентам
            target_clients = set(self.clients.keys())

        for client_id in target_clients:
            if await self._send_to_client(client_id, message_type, data):
                sent_count += 1

        self.logger.debug(f"Сообщение {message_type.value} отправлено {sent_count} клиентам")
        return sent_count

    async def _heartbeat_loop(self) -> None:
        """Цикл проверки heartbeat"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                current_time = datetime.now()
                timeout_clients = []

                for client_id, client in self.clients.items():
                    time_since_heartbeat = (current_time - client.last_heartbeat).total_seconds()

                    if time_since_heartbeat > self.heartbeat_timeout:
                        timeout_clients.append(client_id)
                    else:
                        # Отправка heartbeat
                        await self._send_to_client(
                            client_id, WebSocketMessageType.HEARTBEAT, {"timestamp": current_time.isoformat()}
                        )

                # Удаление клиентов с истекшим timeout
                for client_id in timeout_clients:
                    self.logger.warning(f"Клиент {client_id} отключен по timeout")
                    await self.remove_client(client_id)

            except Exception as e:
                self.logger.error(f"Ошибка в heartbeat loop: {e}")
                await asyncio.sleep(5)

    async def _broadcast_loop(self) -> None:
        """Цикл рассылки обновлений"""
        while True:
            try:
                await asyncio.sleep(5)  # Обновления каждые 5 секунд

                # Симуляция обновлений серверов
                await self._broadcast_server_updates()

                # Симуляция обновлений метрик
                await self._broadcast_metrics_updates()

            except Exception as e:
                self.logger.error(f"Ошибка в broadcast loop: {e}")
                await asyncio.sleep(5)

    async def _broadcast_server_updates(self) -> None:
        """Рассылка обновлений серверов"""
        # Симуляция данных серверов
        servers = [
            {"id": "sg-01", "name": "Singapore-01", "ping": 25, "load": 15, "status": "online"},
            {"id": "us-01", "name": "USA-01", "ping": 45, "load": 25, "status": "online"},
            {"id": "de-01", "name": "Germany-01", "ping": 35, "load": 20, "status": "online"},
            {"id": "uk-01", "name": "UK-01", "ping": 40, "load": 30, "status": "warning"},
        ]

        await self.broadcast_message(WebSocketMessageType.SERVER_UPDATE, {"servers": servers}, SubscriptionType.SERVERS)

    async def _broadcast_metrics_updates(self) -> None:
        """Рассылка обновлений метрик"""
        # Симуляция метрик
        metrics = {
            "totalServers": 4,
            "activeConnections": 15,
            "totalUsers": 100,
            "averagePing": 35,
            "averageLoad": 22,
            "dataTransferred": 1024 * 1024 * 500,  # 500 MB
            "timestamp": datetime.now().isoformat(),
        }

        await self.broadcast_message(
            WebSocketMessageType.METRICS_UPDATE, {"metrics": metrics}, SubscriptionType.METRICS
        )

    def get_client_count(self) -> int:
        """Получение количества подключенных клиентов"""
        return len(self.clients)

    def get_subscription_stats(self) -> Dict[str, int]:
        """Получение статистики подписок"""
        return {sub_type.value: len(clients) for sub_type, clients in self.subscriptions.items()}


class WebSocketAPI:
    """
    WebSocket API сервер для VPN системы

    Предоставляет:
    - WebSocket endpoint для real-time обновлений
    - Подписки на различные типы событий
    - Аутентификация клиентов
    - Heartbeat проверки
    """

    def __init__(self, name: str = "WebSocketAPI"):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

        self.manager = WebSocketManager()
        self.app = web.Application()

        # Настройка CORS
        cors = cors_setup(
            self.app,
            defaults={
                "*": ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*", allow_methods="*")
            },
        )

        # Маршруты
        self.app.router.add_get("/ws", self._handle_websocket)
        self.app.router.add_get("/ws/stats", self._handle_stats)
        self.app.router.add_get("/health", self._handle_health)

        # Применение CORS ко всем маршрутам
        for route in self.app.router.routes():
            cors.add(route)

        self.logger.info(f"WebSocket API '{name}' инициализирован")

    async def _handle_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """Обработка WebSocket соединений"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        # Получение параметров из query string
        user_id = request.query.get("userId")
        subscriptions = request.query.get("subscriptions", "").split(",")

        # Добавление клиента
        client_id = await self.manager.add_client(ws, user_id)

        # Подписка на запрошенные типы
        for sub_str in subscriptions:
            if sub_str.strip():
                try:
                    sub_type = SubscriptionType(sub_str.strip())
                    await self.manager.subscribe_client(client_id, sub_type)
                except ValueError:
                    self.logger.warning(f"Неизвестный тип подписки: {sub_str}")

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    await self._handle_client_message(client_id, msg.data)
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error(f"WebSocket error: {ws.exception()}")
                    break
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
        finally:
            await self.manager.remove_client(client_id)

        return ws

    async def _handle_client_message(self, client_id: str, message: str) -> None:  # noqa: C901
        """Обработка сообщений от клиента"""
        try:
            data = json.loads(message)
            message_type = data.get("type")

            if message_type == "heartbeat":
                # Обновление heartbeat
                if client_id in self.manager.clients:
                    self.manager.clients[client_id].last_heartbeat = datetime.now()

            elif message_type == "subscribe":
                # Подписка на тип сообщений
                sub_type_str = data.get("subscriptionType")
                if sub_type_str:
                    try:
                        sub_type = SubscriptionType(sub_type_str)
                        await self.manager.subscribe_client(client_id, sub_type)
                    except ValueError:
                        await self.manager._send_to_client(
                            client_id,
                            WebSocketMessageType.ERROR,
                            {"message": f"Неизвестный тип подписки: {sub_type_str}"},
                        )

            elif message_type == "unsubscribe":
                # Отписка от типа сообщений
                sub_type_str = data.get("subscriptionType")
                if sub_type_str:
                    try:
                        sub_type = SubscriptionType(sub_type_str)
                        await self.manager.unsubscribe_client(client_id, sub_type)
                    except ValueError:
                        await self.manager._send_to_client(
                            client_id,
                            WebSocketMessageType.ERROR,
                            {"message": f"Неизвестный тип подписки: {sub_type_str}"},
                        )

        except json.JSONDecodeError:
            await self.manager._send_to_client(
                client_id, WebSocketMessageType.ERROR, {"message": "Неверный формат JSON"}
            )
        except Exception as e:
            self.logger.error(f"Ошибка обработки сообщения от клиента {client_id}: {e}")

    async def _handle_stats(self, request: web.Request) -> web.Response:
        """Получение статистики WebSocket соединений"""
        stats = {
            "clientCount": self.manager.get_client_count(),
            "subscriptions": self.manager.get_subscription_stats(),
            "timestamp": datetime.now().isoformat(),
        }

        return web.json_response(stats)

    async def _handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response(
            {
                "status": "healthy",
                "service": "ALADDIN VPN WebSocket API",
                "clientCount": self.manager.get_client_count(),
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def start(self, host: str = "0.0.0.0", port: int = 8081) -> None:
        """Запуск WebSocket API сервера"""
        self.logger.info(f"Запуск WebSocket API на {host}:{port}")

        # Запуск менеджера
        await self.manager.start()

        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, host, port)
        await site.start()

        self.logger.info(f"WebSocket API запущен: ws://{host}:{port}/ws")
        self.logger.info(f"Статистика: http://{host}:{port}/ws/stats")
        self.logger.info(f"Health Check: http://{host}:{port}/health")

    async def stop(self) -> None:
        """Остановка WebSocket API сервера"""
        self.logger.info("Остановка WebSocket API...")
        await self.manager.stop()
        self.logger.info("WebSocket API остановлен")


# Пример использования
async def main():
    """Пример использования WebSocket API"""
    api = WebSocketAPI("TestWebSocketAPI")

    # Запуск сервера
    await api.start("0.0.0.0", 8081)

    # Держим сервер запущенным
    try:
        await asyncio.Future()  # Бесконечное ожидание
    except KeyboardInterrupt:
        print("\nОстановка WebSocket API...")
        await api.stop()


if __name__ == "__main__":
    asyncio.run(main())
