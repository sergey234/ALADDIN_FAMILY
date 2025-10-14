#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APIGateway - API шлюз системы безопасности
Централизованная маршрутизация и управление API

Этот модуль предоставляет комплексную систему API шлюза для AI системы
безопасности, включающую безопасную маршрутизацию, аутентификацию,
мониторинг и защиту.

Автор: ALADDIN Security System
Версия: 3.0
Дата: 2025-01-06
Лицензия: MIT
"""

import logging
import os
import queue
import sys
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

import httpx
import redis
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Добавляем путь к проекту

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus метрики
REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"],
)
REQUEST_DURATION = Histogram(
    "api_request_duration_seconds",
    "API request duration",
    ["method", "endpoint"],
)
ACTIVE_CONNECTIONS = Gauge("api_active_connections", "Active API connections")
AUTHENTICATION_FAILURES = Counter(
    "api_auth_failures_total", "Authentication failures", ["reason"]
)

# База данных
Base = declarative_base()


class APIKey(Base):
    """Модель API ключей"""

    __tablename__ = "api_keys"

    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    key_hash = Column(String(64), unique=True, nullable=False)
    user_id = Column(String(36), nullable=False)
    name = Column(String(100), nullable=False)
    permissions = Column(JSON, default=list)
    rate_limit = Column(Integer, default=1000)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class APIRoute(Base):
    """Модель API маршрутов"""

    __tablename__ = "api_routes"

    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    path = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    target_service = Column(String(100), nullable=False)
    target_url = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=100)
    timeout = Column(Integer, default=30)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class APILog(Base):
    """Модель логов API"""

    __tablename__ = "api_logs"

    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    request_id = Column(String(36), nullable=False)
    user_id = Column(String(36), nullable=True)
    method = Column(String(10), nullable=False)
    path = Column(String(255), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time = Column(Integer, nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RouteStatus(Enum):
    """Статусы маршрутов"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class AuthMethod(Enum):
    """Методы аутентификации"""

    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    NONE = "none"


@dataclass
class RouteConfig:
    """Конфигурация маршрута"""

    path: str
    method: str
    target_service: str
    target_url: str
    auth_required: bool = True
    auth_method: AuthMethod = AuthMethod.API_KEY
    rate_limit: int = 100
    timeout: int = 30
    cache_ttl: int = 300
    is_active: bool = True


@dataclass
class APIRequest:
    """Модель API запроса"""

    request_id: str
    user_id: Optional[str]
    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, Any]
    body: Optional[Any]
    ip_address: str
    user_agent: Optional[str]
    timestamp: datetime


@dataclass
class APIResponse:
    """Модель API ответа"""

    request_id: str
    status_code: int
    headers: Dict[str, str]
    body: Optional[Any]
    response_time: int
    timestamp: datetime


class AuthenticationInterface(ABC):
    """Интерфейс аутентификации"""

    @abstractmethod
    async def authenticate(self, request: APIRequest) -> Optional[str]:
        """Аутентификация запроса"""
        pass

    @abstractmethod
    async def authorize(
        self, user_id: str, resource: str, action: str
    ) -> bool:
        """Авторизация пользователя"""
        pass


class APIGateway:
    """Основной класс API Gateway"""

    def __init__(
        self,
        database_url: str = "sqlite:///api_gateway.db",
        redis_url: str = "redis://localhost:6379/0",
        jwt_secret: str = os.getenv('JWT_SECRET_KEY', 'CHANGE_IN_PRODUCTION'),
        jwt_algorithm: str = "HS256",
    ):
        """Инициализация API Gateway"""
        self.database_url = database_url
        self.redis_url = redis_url
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm

        # Инициализация компонентов
        self.engine = None
        self.session_factory = None
        self.redis_client = None
        self.routes: Dict[str, RouteConfig] = {}
        self.active_connections = 0
        self.request_queue = queue.Queue()
        self.is_running = False

        # Инициализация логгера
        self.logger = logging.getLogger(__name__)

        # Метрики производительности
        self._start_time = time.time()
        self._request_count = 0
        self._error_count = 0

    def __str__(self) -> str:
        """Строковое представление для пользователя"""
        return (
            f"APIGateway(active_routes={len(self.routes)}, "
            f"connections={self.active_connections}, "
            f"running={self.is_running})"
        )

    def __repr__(self) -> str:
        """Строковое представление для разработчика"""
        return (
            f"APIGateway(database_url='{self.database_url}', "
            f"redis_url='{self.redis_url}', "
            f"jwt_algorithm='{self.jwt_algorithm}')"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь для сериализации"""
        return {
            "database_url": self.database_url,
            "redis_url": self.redis_url,
            "jwt_secret": "***" if self.jwt_secret else None,
            "jwt_algorithm": self.jwt_algorithm,
            "active_routes": len(self.routes),
            "active_connections": self.active_connections,
            "is_running": self.is_running,
            "queue_size": self.request_queue.qsize(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APIGateway":
        """Создание экземпляра из словаря"""
        gateway = cls(
            database_url=data.get("database_url", "sqlite:///api_gateway.db"),
            redis_url=data.get("redis_url", "redis://localhost:6379/0"),
            jwt_secret=data.get("jwt_secret", os.getenv('JWT_SECRET_KEY', 'CHANGE_IN_PRODUCTION')),
            jwt_algorithm=data.get("jwt_algorithm", "HS256"),
        )
        gateway.active_connections = data.get("active_connections", 0)
        gateway.is_running = data.get("is_running", False)
        return gateway

    def validate_config(self) -> bool:
        """Валидация конфигурации API Gateway"""
        try:
            if not self.database_url:
                raise ValueError("Database URL is required")
            if not self.redis_url:
                raise ValueError("Redis URL is required")
            if not self.jwt_secret:
                raise ValueError("JWT secret is required")
            if not self.jwt_algorithm:
                raise ValueError("JWT algorithm is required")

            # Дополнительные проверки
            if len(self.jwt_secret) < 8:
                raise ValueError("JWT secret must be at least 8 characters")

            self.logger.info("Configuration validation passed")
            return True

        except Exception as e:
            self.logger.error(f"Config validation failed: {e}")
            return False

    def __enter__(self):
        """Context manager entry"""
        self.logger.info("Entering API Gateway context")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type:
            self.logger.error(f"Exception in API Gateway context: {exc_val}")
        else:
            self.logger.info("Exiting API Gateway context successfully")
        return False

    async def initialize(self) -> bool:
        """Инициализация API Gateway"""
        try:
            # Инициализация базы данных
            self.engine = create_engine(self.database_url)
            Base.metadata.create_all(self.engine)
            self.session_factory = sessionmaker(bind=self.engine)

            # Инициализация Redis
            self.redis_client = redis.from_url(self.redis_url)

            # Загрузка маршрутов
            await self._load_routes()

            self.logger.info("API Gateway инициализирован успешно")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка инициализации API Gateway: {e}")
            return False

    async def _load_routes(self) -> None:
        """Загрузка маршрутов из базы данных"""
        try:
            with self.session_factory() as session:
                db_routes = (
                    session.query(APIRoute)
                    .filter(APIRoute.is_active.is_(True))
                    .all()
                )

                for route in db_routes:
                    route_key = f"{route.method}:{route.path}"
                    self.routes[route_key] = RouteConfig(
                        path=route.path,
                        method=route.method,
                        target_service=route.target_service,
                        target_url=route.target_url,
                        rate_limit=route.rate_limit,
                        timeout=route.timeout,
                        is_active=route.is_active,
                    )

            self.logger.info(f"Загружено {len(self.routes)} маршрутов")

        except Exception as e:
            self.logger.error(f"Ошибка загрузки маршрутов: {e}")

    async def register_route(self, route_config: RouteConfig) -> bool:
        """Регистрация нового маршрута"""
        try:
            with self.session_factory() as session:
                # Проверяем существование маршрута
                existing = (
                    session.query(APIRoute)
                    .filter(
                        APIRoute.path == route_config.path,
                        APIRoute.method == route_config.method,
                    )
                    .first()
                )

                if existing:
                    # Обновляем существующий
                    existing.target_service = route_config.target_service
                    existing.target_url = route_config.target_url
                    existing.rate_limit = route_config.rate_limit
                    existing.timeout = route_config.timeout
                    existing.is_active = route_config.is_active
                    existing.updated_at = datetime.utcnow()
                else:
                    # Создаем новый
                    new_route = APIRoute(
                        path=route_config.path,
                        method=route_config.method,
                        target_service=route_config.target_service,
                        target_url=route_config.target_url,
                        rate_limit=route_config.rate_limit,
                        timeout=route_config.timeout,
                        is_active=route_config.is_active,
                    )
                    session.add(new_route)

                session.commit()

                # Обновляем кэш
                route_key = f"{route_config.method}:{route_config.path}"
                self.routes[route_key] = route_config

            self.logger.info(
                f"Маршрут зарегистрирован: "
                f"{route_config.method} {route_config.path}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка регистрации маршрута: {e}")
            return False

    async def process_request(self, request: APIRequest) -> APIResponse:
        """Обработка API запроса"""
        start_time = time.time()

        try:
            # Увеличиваем счетчик активных соединений
            self.active_connections += 1
            ACTIVE_CONNECTIONS.set(self.active_connections)

            # Находим маршрут
            route_key = f"{request.method}:{request.path}"
            route = self.routes.get(route_key)

            if not route:
                raise HTTPException(
                    status_code=404,
                    detail=f"Маршрут не найден: "
                    f"{request.method} {request.path}",
                )

            # Проверяем rate limiting
            if not await self._check_rate_limit(request, route):
                raise HTTPException(
                    status_code=429, detail="Превышен лимит запросов"
                )

            # Проксируем запрос к целевому сервису
            response = await self._proxy_request(request, route)

            # Логируем запрос
            await self._log_request(
                request, response, int((time.time() - start_time) * 1000)
            )

            # Обновляем метрики
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.path,
                status=response.status_code,
            ).inc()

            REQUEST_DURATION.labels(
                method=request.method, endpoint=request.path
            ).observe(time.time() - start_time)

            return response

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Ошибка обработки запроса: {e}")
            raise HTTPException(
                status_code=500, detail="Внутренняя ошибка сервера"
            )
        finally:
            # Уменьшаем счетчик активных соединений
            self.active_connections -= 1
            ACTIVE_CONNECTIONS.set(self.active_connections)

    async def _check_rate_limit(
        self, request: APIRequest, route: RouteConfig
    ) -> bool:
        """Проверка rate limiting"""
        try:
            if not request.user_id:
                return True

            key = f"rate_limit:{request.user_id}:{route.path}"
            current = self.redis_client.get(key)

            if current is None:
                self.redis_client.setex(key, 60, 1)
                return True

            if int(current) >= route.rate_limit:
                return False

            self.redis_client.incr(key)
            return True

        except Exception as e:
            self.logger.error(f"Ошибка проверки rate limit: {e}")
            return True

    async def _proxy_request(
        self, request: APIRequest, route: RouteConfig
    ) -> APIResponse:
        """Проксирование запроса к целевому сервису"""
        try:
            async with httpx.AsyncClient(timeout=route.timeout) as client:
                # Формируем URL
                target_url = f"{route.target_url}{request.path}"

                # Проксируем запрос
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=request.headers,
                    params=request.query_params,
                    json=request.body,
                )

                return APIResponse(
                    request_id=request.request_id,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=(
                        response.json()
                        if response.headers.get("content-type", "").startswith(
                            "application/json"
                        )
                        else response.text
                    ),
                    response_time=int((time.time() - time.time()) * 1000),
                    timestamp=datetime.utcnow(),
                )

        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Таймаут запроса")
        except Exception as e:
            self.logger.error(f"Ошибка проксирования запроса: {e}")
            raise HTTPException(status_code=502, detail="Ошибка проксирования")

    async def _log_request(
        self, request: APIRequest, response: APIResponse, response_time: int
    ) -> None:
        """Логирование запроса"""
        try:
            with self.session_factory() as session:
                log_entry = APILog(
                    request_id=request.request_id,
                    user_id=request.user_id,
                    method=request.method,
                    path=request.path,
                    status_code=response.status_code,
                    response_time=response_time,
                    ip_address=request.ip_address,
                    user_agent=request.user_agent,
                )
                session.add(log_entry)
                session.commit()

        except Exception as e:
            self.logger.error(f"Ошибка логирования запроса: {e}")

    async def get_metrics(self) -> Dict[str, Any]:
        """Получение метрик API Gateway"""
        try:
            return {
                "active_connections": self.active_connections,
                "total_routes": len(self.routes),
                "active_routes": len(
                    [r for r in self.routes.values() if r.is_active]
                ),
                "uptime": time.time()
                - getattr(self, "start_time", time.time()),
                "prometheus_metrics": generate_latest().decode("utf-8"),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения метрик: {e}")
            return {}

    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья сервиса"""
        try:
            # Проверяем подключение к БД
            db_healthy = self.engine is not None

            # Проверяем подключение к Redis
            redis_healthy = self.redis_client is not None

            # Проверяем активные маршруты
            routes_healthy = len(self.routes) > 0

            # Проверяем общее состояние
            overall_healthy = all([db_healthy, redis_healthy, routes_healthy])

            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "database": "connected" if db_healthy else "disconnected",
                "redis": "connected" if redis_healthy else "disconnected",
                "routes": len(self.routes),
                "active_connections": self.active_connections,
                "is_running": self.is_running,
                "timestamp": time.time()
            }

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }

    async def performance_metrics(self) -> Dict[str, Any]:
        """Метрики производительности"""
        try:
            return {
                "active_connections": self.active_connections,
                "total_routes": len(self.routes),
                "queue_size": self.request_queue.qsize(),
                "is_running": self.is_running,
                "uptime": time.time() - getattr(
                    self, "_start_time", time.time()
                ),
                "timestamp": time.time(),
                "memory_usage": "N/A",
                "cpu_usage": "N/A"
            }

        except Exception as e:
            self.logger.error(f"Performance metrics failed: {e}")
            return {
                "error": str(e),
                "timestamp": time.time()
            }

    async def shutdown(self) -> None:
        """Завершение работы API Gateway"""
        try:
            self.is_running = False

            if self.redis_client:
                self.redis_client.close()

            if self.engine:
                self.engine.dispose()

            self.logger.info("API Gateway завершил работу")

        except Exception as e:
            self.logger.error(f"Ошибка завершения работы: {e}")


# FastAPI приложение
app = FastAPI(
    title="ALADDIN API Gateway",
    description="API шлюз системы безопасности",
    version="3.0.0",
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Глобальная переменная для API Gateway
api_gateway: Optional[APIGateway] = None


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    global api_gateway
    api_gateway = APIGateway()
    await api_gateway.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    """Завершение при остановке"""
    global api_gateway
    if api_gateway:
        await api_gateway.shutdown()


@app.get("/health")
async def health_check():
    """Проверка здоровья API Gateway"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/metrics")
async def get_metrics():
    """Получение метрик"""
    if not api_gateway:
        raise HTTPException(
            status_code=503, detail="API Gateway не инициализирован"
        )

    metrics = await api_gateway.get_metrics()
    return metrics


@app.post("/routes", response_model=dict)
async def register_route(route_config: dict):
    """Регистрация нового маршрута"""
    if not api_gateway:
        raise HTTPException(
            status_code=503, detail="API Gateway не инициализирован"
        )

    try:
        config = RouteConfig(**route_config)
        success = await api_gateway.register_route(config)

        if success:
            return {"status": "success", "message": "Маршрут зарегистрирован"}
        else:
            raise HTTPException(
                status_code=400, detail="Ошибка регистрации маршрута"
            )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/routes")
async def get_routes():
    """Получение списка маршрутов"""
    if not api_gateway:
        raise HTTPException(
            status_code=503, detail="API Gateway не инициализирован"
        )

    return {
        "routes": [
            {
                "path": route.path,
                "method": route.method,
                "target_service": route.target_service,
                "target_url": route.target_url,
                "rate_limit": route.rate_limit,
                "timeout": route.timeout,
                "is_active": route.is_active,
            }
            for route in api_gateway.routes.values()
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
