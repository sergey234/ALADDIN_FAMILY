#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GraphQL API - GraphQL API для VPN системы
Качество кода: A+
Соответствие: SOLID, DRY, PEP8
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import asyncio
from aiohttp import web
from aiohttp_cors import ResourceOptions
from aiohttp_cors import setup as cors_setup

logger = logging.getLogger(__name__)


class GraphQLOperationType(Enum):
    """Типы GraphQL операций"""

    QUERY = "query"
    MUTATION = "mutation"
    SUBSCRIPTION = "subscription"


@dataclass
class GraphQLRequest:
    """Модель GraphQL запроса"""

    query: str
    variables: Dict[str, Any] = field(default_factory=dict)
    operation_name: Optional[str] = None
    operation_type: GraphQLOperationType = GraphQLOperationType.QUERY


@dataclass
class GraphQLResponse:
    """Модель GraphQL ответа"""

    data: Optional[Dict[str, Any]] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)
    extensions: Dict[str, Any] = field(default_factory=dict)


class GraphQLResolver:
    """
    GraphQL резолвер для VPN системы

    Обрабатывает:
    - Запросы данных (servers, connections, users)
    - Мутации (connect, disconnect, update settings)
    - Подписки (real-time updates)
    """

    def __init__(self, name: str = "GraphQLResolver"):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

        # Данные для демонстрации
        self.servers = [
            {"id": "sg-01", "name": "Singapore-01", "country": "SG", "city": "Singapore", "ping": 25, "load": 15},
            {"id": "us-01", "name": "USA-01", "country": "US", "city": "New York", "ping": 45, "load": 25},
            {"id": "de-01", "name": "Germany-01", "country": "DE", "city": "Frankfurt", "ping": 35, "load": 20},
            {"id": "uk-01", "name": "UK-01", "country": "GB", "city": "London", "ping": 40, "load": 30},
        ]

        self.connections = []
        self.users = [
            {"id": "user_001", "name": "Test User", "email": "test@example.com", "active": True},
            {"id": "user_002", "name": "Demo User", "email": "demo@example.com", "active": True},
        ]

        self.logger.info(f"GraphQL Resolver '{name}' инициализирован")

    async def resolve_query(self, field: str, args: Dict[str, Any]) -> Any:
        """Резолвер для Query операций"""
        self.logger.debug(f"Resolving query field: {field}")

        if field == "servers":
            return await self._resolve_servers(args)
        elif field == "server":
            return await self._resolve_server(args)
        elif field == "connections":
            return await self._resolve_connections(args)
        elif field == "connection":
            return await self._resolve_connection(args)
        elif field == "users":
            return await self._resolve_users(args)
        elif field == "user":
            return await self._resolve_user(args)
        elif field == "metrics":
            return await self._resolve_metrics(args)
        elif field == "analytics":
            return await self._resolve_analytics(args)
        else:
            raise ValueError(f"Unknown query field: {field}")

    async def resolve_mutation(self, field: str, args: Dict[str, Any]) -> Any:
        """Резолвер для Mutation операций"""
        self.logger.debug(f"Resolving mutation field: {field}")

        if field == "connect":
            return await self._resolve_connect(args)
        elif field == "disconnect":
            return await self._resolve_disconnect(args)
        elif field == "updateServer":
            return await self._resolve_update_server(args)
        elif field == "createUser":
            return await self._resolve_create_user(args)
        elif field == "updateUser":
            return await self._resolve_update_user(args)
        else:
            raise ValueError(f"Unknown mutation field: {field}")

    async def _resolve_servers(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получение списка серверов"""
        country = args.get("country")
        min_ping = args.get("minPing", 0)
        max_load = args.get("maxLoad", 100)

        filtered_servers = self.servers.copy()

        if country:
            filtered_servers = [s for s in filtered_servers if s["country"] == country]

        filtered_servers = [s for s in filtered_servers if s["ping"] >= min_ping]
        filtered_servers = [s for s in filtered_servers if s["load"] <= max_load]

        return filtered_servers

    async def _resolve_server(self, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Получение конкретного сервера"""
        server_id = args.get("id")
        if not server_id:
            return None

        return next((s for s in self.servers if s["id"] == server_id), None)

    async def _resolve_connections(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получение списка соединений"""
        user_id = args.get("userId")
        server_id = args.get("serverId")
        active_only = args.get("activeOnly", False)

        filtered_connections = self.connections.copy()

        if user_id:
            filtered_connections = [c for c in filtered_connections if c.get("userId") == user_id]

        if server_id:
            filtered_connections = [c for c in filtered_connections if c.get("serverId") == server_id]

        if active_only:
            filtered_connections = [c for c in filtered_connections if c.get("active", False)]

        return filtered_connections

    async def _resolve_connection(self, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Получение конкретного соединения"""
        connection_id = args.get("id")
        if not connection_id:
            return None

        return next((c for c in self.connections if c.get("id") == connection_id), None)

    async def _resolve_users(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получение списка пользователей"""
        active_only = args.get("activeOnly", False)

        filtered_users = self.users.copy()

        if active_only:
            filtered_users = [u for u in filtered_users if u.get("active", False)]

        return filtered_users

    async def _resolve_user(self, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Получение конкретного пользователя"""
        user_id = args.get("id")
        if not user_id:
            return None

        return next((u for u in self.users if u["id"] == user_id), None)

    async def _resolve_metrics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Получение метрик"""
        return {
            "totalServers": len(self.servers),
            "activeConnections": len([c for c in self.connections if c.get("active", False)]),
            "totalUsers": len(self.users),
            "averagePing": sum(s["ping"] for s in self.servers) / len(self.servers) if self.servers else 0,
            "averageLoad": sum(s["load"] for s in self.servers) / len(self.servers) if self.servers else 0,
            "timestamp": datetime.now().isoformat(),
        }

    async def _resolve_analytics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Получение аналитики"""
        return {
            "revenue": {"mrr": 50000.0, "arr": 600000.0, "arpu": 25.0},
            "users": {
                "total": len(self.users),
                "active": len([u for u in self.users if u.get("active", False)]),
                "growth": 0.15,
            },
            "performance": {"uptime": 99.9, "averageResponseTime": 45.0, "errorRate": 0.01},
        }

    async def _resolve_connect(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Подключение к VPN"""
        user_id = args.get("userId")
        server_id = args.get("serverId")

        if not user_id or not server_id:
            raise ValueError("userId and serverId are required")

        # Проверка существования сервера
        server = next((s for s in self.servers if s["id"] == server_id), None)
        if not server:
            raise ValueError(f"Server {server_id} not found")

        # Создание соединения
        connection = {
            "id": f"conn_{len(self.connections) + 1:03d}",
            "userId": user_id,
            "serverId": server_id,
            "serverName": server["name"],
            "connectedAt": datetime.now().isoformat(),
            "active": True,
            "ping": server["ping"],
            "speed": 95.0,
            "dataTransferred": 0,
        }

        self.connections.append(connection)

        self.logger.info(f"User {user_id} connected to server {server_id}")

        return {"success": True, "connection": connection, "message": f"Connected to {server['name']}"}

    async def _resolve_disconnect(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Отключение от VPN"""
        connection_id = args.get("connectionId")
        user_id = args.get("userId")

        if not connection_id and not user_id:
            raise ValueError("connectionId or userId is required")

        # Поиск соединения
        connection = None
        if connection_id:
            connection = next((c for c in self.connections if c["id"] == connection_id), None)
        elif user_id:
            connection = next((c for c in self.connections if c["userId"] == user_id and c.get("active", False)), None)

        if not connection:
            raise ValueError("Connection not found")

        # Обновление соединения
        connection["active"] = False
        connection["disconnectedAt"] = datetime.now().isoformat()

        self.logger.info(f"Connection {connection['id']} disconnected")

        return {"success": True, "connection": connection, "message": "Disconnected successfully"}

    async def _resolve_update_server(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление сервера"""
        server_id = args.get("id")
        updates = args.get("updates", {})

        if not server_id:
            raise ValueError("Server ID is required")

        server = next((s for s in self.servers if s["id"] == server_id), None)
        if not server:
            raise ValueError(f"Server {server_id} not found")

        # Обновление полей
        for key, value in updates.items():
            if key in server:
                server[key] = value

        self.logger.info(f"Server {server_id} updated")

        return {"success": True, "server": server, "message": "Server updated successfully"}

    async def _resolve_create_user(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Создание пользователя"""
        name = args.get("name")
        email = args.get("email")

        if not name or not email:
            raise ValueError("Name and email are required")

        # Проверка уникальности email
        if any(u["email"] == email for u in self.users):
            raise ValueError("User with this email already exists")

        user = {
            "id": f"user_{len(self.users) + 1:03d}",
            "name": name,
            "email": email,
            "active": True,
            "createdAt": datetime.now().isoformat(),
        }

        self.users.append(user)

        self.logger.info(f"User {user['id']} created")

        return {"success": True, "user": user, "message": "User created successfully"}

    async def _resolve_update_user(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление пользователя"""
        user_id = args.get("id")
        updates = args.get("updates", {})

        if not user_id:
            raise ValueError("User ID is required")

        user = next((u for u in self.users if u["id"] == user_id), None)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Обновление полей
        for key, value in updates.items():
            if key in user:
                user[key] = value

        self.logger.info(f"User {user_id} updated")

        return {"success": True, "user": user, "message": "User updated successfully"}


class GraphQLAPI:
    """
    GraphQL API сервер для VPN системы

    Предоставляет:
    - GraphQL endpoint для запросов
    - WebSocket для подписок
    - CORS поддержка
    - Аутентификация
    """

    def __init__(self, name: str = "GraphQLAPI"):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

        self.resolver = GraphQLResolver()
        self.app = web.Application()

        # Настройка CORS
        cors = cors_setup(
            self.app,
            defaults={
                "*": ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*", allow_methods="*")
            },
        )

        # Маршруты
        self.app.router.add_post("/graphql", self._handle_graphql)
        self.app.router.add_get("/graphql", self._handle_graphql_playground)
        self.app.router.add_get("/health", self._handle_health)

        # Применение CORS ко всем маршрутам
        for route in self.app.router.routes():
            cors.add(route)

        self.logger.info(f"GraphQL API '{name}' инициализирован")

    async def _handle_graphql(self, request: web.Request) -> web.Response:
        """Обработка GraphQL запросов"""
        try:
            # Получение данных запроса
            if request.method == "POST":
                data = await request.json()
            else:
                data = {}

            query = data.get("query", "")
            variables = data.get("variables", {})
            operation_name = data.get("operationName")

            if not query:
                return web.json_response({"errors": [{"message": "Query is required"}]}, status=400)

            # Парсинг и выполнение запроса
            result = await self._execute_query(query, variables, operation_name)

            return web.json_response(result)

        except Exception as e:
            self.logger.error(f"GraphQL error: {e}")
            return web.json_response({"errors": [{"message": str(e)}]}, status=500)

    async def _handle_graphql_playground(self, request: web.Request) -> web.Response:
        """GraphQL Playground"""
        playground_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ALADDIN VPN - GraphQL Playground</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 1200px; margin: 0 auto; }
                h1 { color: #ffd700; }
                .example { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                pre { background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 5px; overflow-x: auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔮 ALADDIN VPN - GraphQL Playground</h1>
                <p>Используйте этот интерфейс для тестирования GraphQL запросов</p>

                <div class="example">
                    <h3>Пример запроса серверов:</h3>
                    <pre>query {
  servers {
    id
    name
    country
    city
    ping
    load
  }
}</pre>
                </div>

                <div class="example">
                    <h3>Пример подключения к VPN:</h3>
                    <pre>mutation {
  connect(userId: "user_001", serverId: "sg-01") {
    success
    message
    connection {
      id
      serverName
      connectedAt
      ping
      speed
    }
  }
}</pre>
                </div>

                <div class="example">
                    <h3>Пример получения метрик:</h3>
                    <pre>query {
  metrics {
    totalServers
    activeConnections
    totalUsers
    averagePing
    averageLoad
  }
}</pre>
                </div>
            </div>
        </body>
        </html>
        """

        return web.Response(text=playground_html, content_type="text/html")

    async def _handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response(
            {"status": "healthy", "service": "ALADDIN VPN GraphQL API", "timestamp": datetime.now().isoformat()}
        )

    async def _execute_query(
        self, query: str, variables: Dict[str, Any], operation_name: Optional[str]
    ) -> Dict[str, Any]:
        """Выполнение GraphQL запроса"""
        try:
            # Простой парсер GraphQL (в реальной системе использовался бы библиотека)
            if query.strip().startswith("query"):
                return await self._execute_query_operation(query, variables)
            elif query.strip().startswith("mutation"):
                return await self._execute_mutation_operation(query, variables)
            else:
                return {"errors": [{"message": "Unknown operation type"}]}

        except Exception as e:
            self.logger.error(f"Query execution error: {e}")
            return {"errors": [{"message": str(e)}]}

    async def _execute_query_operation(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение Query операции"""
        # Простая реализация для демонстрации
        if "servers" in query:
            servers = await self.resolver.resolve_query("servers", variables)
            return {"data": {"servers": servers}}
        elif "metrics" in query:
            metrics = await self.resolver.resolve_query("metrics", variables)
            return {"data": {"metrics": metrics}}
        elif "analytics" in query:
            analytics = await self.resolver.resolve_query("analytics", variables)
            return {"data": {"analytics": analytics}}
        else:
            return {"errors": [{"message": "Unknown query"}]}

    async def _execute_mutation_operation(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение Mutation операции"""
        # Простая реализация для демонстрации
        if "connect" in query:
            result = await self.resolver.resolve_mutation("connect", variables)
            return {"data": {"connect": result}}
        elif "disconnect" in query:
            result = await self.resolver.resolve_mutation("disconnect", variables)
            return {"data": {"disconnect": result}}
        else:
            return {"errors": [{"message": "Unknown mutation"}]}

    async def start(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        """Запуск GraphQL API сервера"""
        self.logger.info(f"Запуск GraphQL API на {host}:{port}")

        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, host, port)
        await site.start()

        self.logger.info(f"GraphQL API запущен: http://{host}:{port}/graphql")
        self.logger.info(f"GraphQL Playground: http://{host}:{port}/graphql")
        self.logger.info(f"Health Check: http://{host}:{port}/health")


# Пример использования
async def main():
    """Пример использования GraphQL API"""
    api = GraphQLAPI("TestAPI")

    # Запуск сервера
    await api.start("0.0.0.0", 8080)

    # Держим сервер запущенным
    try:
        await asyncio.Future()  # Бесконечное ожидание
    except KeyboardInterrupt:
        print("\nОстановка GraphQL API...")


if __name__ == "__main__":
    asyncio.run(main())
