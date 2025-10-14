#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSRF Middleware - Защита от Cross-Site Request Forgery
Версия: 1.0.0
Дата: 2025-10-11

Защищает API от CSRF атак через токены.
Интегрируется с FastAPI для мобильных приложений.

Автор: ALADDIN Security Team
"""

import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Set
from fastapi import Request, HTTPException, Header
from fastapi.responses import JSONResponse

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSRFProtection:
    """
    Защита от CSRF атак
    
    Генерирует и проверяет CSRF токены для каждого пользователя.
    Токены хранятся в памяти (в production использовать Redis).
    
    Использование:
        csrf = CSRFProtection()
        token = csrf.generate_token(user_id="user_123")
        is_valid = csrf.validate_token(user_id="user_123", token=token)
    """
    
    def __init__(self, token_length: int = 32, token_lifetime: int = 3600):
        """
        Инициализация CSRF защиты
        
        Args:
            token_length: Длина токена в байтах (по умолчанию 32)
            token_lifetime: Время жизни токена в секундах (по умолчанию 3600 = 1 час)
        """
        self.token_length = token_length
        self.token_lifetime = token_lifetime
        
        # Хранилище токенов: user_id → (token, expires_at)
        self.tokens: Dict[str, tuple[str, datetime]] = {}
        
        # Использованные токены (для предотвращения replay атак)
        self.used_tokens: Set[str] = set()
        
        logger.info(f"✅ CSRF Protection инициализирована (token_length={token_length}, lifetime={token_lifetime}s)")
    
    def generate_token(self, user_id: str) -> str:
        """
        Генерация CSRF токена для пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            CSRF токен (строка)
        """
        try:
            # Генерируем случайный токен
            token = secrets.token_urlsafe(self.token_length)
            
            # Добавляем хеш user_id для дополнительной безопасности
            token_hash = hashlib.sha256(f"{token}:{user_id}".encode()).hexdigest()
            final_token = f"{token}.{token_hash[:16]}"
            
            # Сохраняем с временем истечения
            expires_at = datetime.now() + timedelta(seconds=self.token_lifetime)
            self.tokens[user_id] = (final_token, expires_at)
            
            logger.info(f"✅ CSRF токен сгенерирован для user_id={user_id}")
            return final_token
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации CSRF токена: {e}")
            raise
    
    def validate_token(
        self,
        user_id: str,
        token: str,
        remove_after_use: bool = True
    ) -> bool:
        """
        Проверка CSRF токена
        
        Args:
            user_id: ID пользователя
            token: CSRF токен
            remove_after_use: Удалить токен после использования (защита от replay)
            
        Returns:
            True если токен валиден, False иначе
        """
        try:
            # Проверяем, что токен не использован (защита от replay атак)
            if token in self.used_tokens:
                logger.warning(f"⚠️ CSRF токен уже использован: user_id={user_id}")
                return False
            
            # Проверяем, что токен существует для пользователя
            if user_id not in self.tokens:
                logger.warning(f"⚠️ CSRF токен не найден для user_id={user_id}")
                return False
            
            stored_token, expires_at = self.tokens[user_id]
            
            # Проверяем, что токен не истек
            if datetime.now() > expires_at:
                logger.warning(f"⚠️ CSRF токен истек для user_id={user_id}")
                del self.tokens[user_id]
                return False
            
            # Проверяем, что токены совпадают
            if stored_token != token:
                logger.warning(f"⚠️ CSRF токен не совпадает для user_id={user_id}")
                return False
            
            # Токен валиден!
            if remove_after_use:
                # Удаляем токен (одноразовое использование)
                del self.tokens[user_id]
                # Добавляем в список использованных
                self.used_tokens.add(token)
                # Очищаем старые использованные токены (храним последние 1000)
                if len(self.used_tokens) > 1000:
                    self.used_tokens = set(list(self.used_tokens)[-1000:])
            
            logger.info(f"✅ CSRF токен валиден для user_id={user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки CSRF токена: {e}")
            return False
    
    def revoke_token(self, user_id: str) -> bool:
        """
        Отозвать CSRF токен пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если токен отозван, False если не найден
        """
        if user_id in self.tokens:
            del self.tokens[user_id]
            logger.info(f"✅ CSRF токен отозван для user_id={user_id}")
            return True
        return False
    
    def cleanup_expired_tokens(self):
        """Очистка истекших токенов"""
        now = datetime.now()
        expired_users = []
        
        for user_id, (token, expires_at) in self.tokens.items():
            if now > expires_at:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del self.tokens[user_id]
        
        if expired_users:
            logger.info(f"✅ Удалено {len(expired_users)} истекших CSRF токенов")
    
    def get_stats(self) -> Dict[str, int]:
        """Получить статистику CSRF защиты"""
        return {
            "active_tokens": len(self.tokens),
            "used_tokens": len(self.used_tokens),
            "token_lifetime_seconds": self.token_lifetime
        }


# Глобальный экземпляр CSRF защиты
csrf_protection = CSRFProtection()


# ═══════════════════════════════════════════════════════════════
# FastAPI Middleware
# ═══════════════════════════════════════════════════════════════

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF Middleware для FastAPI
    
    Автоматически проверяет CSRF токены для всех POST/PUT/DELETE запросов.
    """
    
    def __init__(self, app: FastAPI, csrf_protection: CSRFProtection):
        super().__init__(app)
        self.csrf = csrf_protection
        
        # Методы которые требуют CSRF защиты
        self.protected_methods = {"POST", "PUT", "DELETE", "PATCH"}
        
        # Пути которые не требуют CSRF (например, логин)
        self.exempt_paths = {
            "/api/auth/login",
            "/api/auth/register",
            "/api/health",
            "/docs",
            "/openapi.json"
        }
    
    async def dispatch(self, request: Request, call_next):
        """
        Обработка запроса
        """
        # Проверяем, нужна ли CSRF защита
        if request.method in self.protected_methods:
            if request.url.path not in self.exempt_paths:
                # Получаем user_id из request (в production из JWT токена)
                user_id = request.headers.get("X-User-ID", "anonymous")
                
                # Получаем CSRF токен из заголовка
                csrf_token = request.headers.get("X-CSRF-Token", "")
                
                if not csrf_token:
                    logger.warning(f"⚠️ CSRF токен отсутствует: {request.url.path}")
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "CSRF токен отсутствует"}
                    )
                
                # Проверяем токен
                if not self.csrf.validate_token(user_id, csrf_token):
                    logger.warning(f"⚠️ Неверный CSRF токен: {request.url.path}")
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "Неверный CSRF токен"}
                    )
                
                logger.info(f"✅ CSRF токен валиден для {request.url.path}")
        
        # Продолжаем обработку запроса
        response = await call_next(request)
        return response


# ═══════════════════════════════════════════════════════════════
# FastAPI Dependency для генерации токенов
# ═══════════════════════════════════════════════════════════════

async def get_csrf_token(user_id: str = Header(None, alias="X-User-ID")) -> str:
    """
    Dependency для генерации CSRF токена
    
    Использование в FastAPI:
        @app.get("/api/csrf-token")
        async def get_token(token: str = Depends(get_csrf_token)):
            return {"csrf_token": token}
    """
    if not user_id:
        user_id = "anonymous"
    
    return csrf_protection.generate_token(user_id)


async def verify_csrf_token(
    user_id: str = Header(None, alias="X-User-ID"),
    csrf_token: str = Header(None, alias="X-CSRF-Token")
) -> bool:
    """
    Dependency для проверки CSRF токена
    
    Использование в FastAPI:
        @app.post("/api/protected-endpoint")
        async def protected(valid: bool = Depends(verify_csrf_token)):
            if not valid:
                raise HTTPException(403, "Invalid CSRF token")
            ...
    """
    if not user_id or not csrf_token:
        raise HTTPException(status_code=403, detail="CSRF токен или user_id отсутствует")
    
    is_valid = csrf_protection.validate_token(user_id, csrf_token)
    
    if not is_valid:
        raise HTTPException(status_code=403, detail="Неверный CSRF токен")
    
    return True


# ═══════════════════════════════════════════════════════════════
# Endpoint для получения CSRF токена
# ═══════════════════════════════════════════════════════════════

def add_csrf_endpoint(app: FastAPI):
    """
    Добавить endpoint для получения CSRF токена
    
    Использование:
        from security.middleware.csrf_middleware import add_csrf_endpoint
        add_csrf_endpoint(app)
    """
    
    @app.get("/api/csrf-token")
    async def get_csrf_token_endpoint(
        user_id: str = Header(None, alias="X-User-ID")
    ):
        """Получить CSRF токен для дальнейших запросов"""
        if not user_id:
            user_id = "anonymous"
        
        token = csrf_protection.generate_token(user_id)
        
        return {
            "csrf_token": token,
            "expires_in": csrf_protection.token_lifetime,
            "user_id": user_id
        }
    
    @app.get("/api/csrf-stats")
    async def get_csrf_stats():
        """Получить статистику CSRF защиты (только для администраторов)"""
        return csrf_protection.get_stats()


# ═══════════════════════════════════════════════════════════════
# Пример использования
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Тестирование CSRF защиты
    print("🧪 Тестирование CSRF Protection")
    print("=" * 60)
    
    csrf = CSRFProtection()
    
    # 1. Генерация токена
    user_id = "test_user_123"
    token = csrf.generate_token(user_id)
    print(f"✅ Токен сгенерирован: {token[:20]}...")
    
    # 2. Валидация токена (успешная)
    is_valid = csrf.validate_token(user_id, token, remove_after_use=False)
    print(f"✅ Токен валиден: {is_valid}")
    
    # 3. Повторная валидация (должна пройти, т.к. remove_after_use=False)
    is_valid_again = csrf.validate_token(user_id, token, remove_after_use=False)
    print(f"✅ Повторная проверка: {is_valid_again}")
    
    # 4. Валидация с удалением
    is_valid_final = csrf.validate_token(user_id, token, remove_after_use=True)
    print(f"✅ Финальная проверка (с удалением): {is_valid_final}")
    
    # 5. Попытка повторного использования (должна провалиться)
    is_valid_replay = csrf.validate_token(user_id, token, remove_after_use=False)
    print(f"❌ Replay атака предотвращена: {is_valid_replay}")
    
    # 6. Неверный токен
    fake_token = "fake_token_12345"
    is_valid_fake = csrf.validate_token(user_id, fake_token)
    print(f"❌ Фейковый токен отклонен: {is_valid_fake}")
    
    # 7. Статистика
    stats = csrf.get_stats()
    print(f"📊 Статистика: {stats}")
    
    print("=" * 60)
    print("✅ Все тесты пройдены!")




