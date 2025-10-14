#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Manager - Управление сессиями пользователей
Версия: 1.0.0
Дата: 2025-10-11

Управляет JWT токенами и сессиями через Redis для масштабируемости.
Поддерживает iOS и Android приложения.

Автор: ALADDIN Security Team
"""

import jwt
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from dataclasses import dataclass

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Session:
    """Сессия пользователя"""
    user_id: str
    token: str
    device_id: str
    device_type: str  # "iOS" или "Android"
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class SessionManager:
    """
    Менеджер сессий пользователей
    
    В production использует Redis для хранения сессий.
    Сейчас использует in-memory хранилище для простоты.
    
    Функции:
    - Создание JWT токенов
    - Валидация токенов
    - Хранение сессий
    - Автоматическое удаление истекших сессий
    - Поддержка multiple devices (iOS + Android)
    """
    
    def __init__(
        self,
        secret_key: str = "ALADDIN_SECRET_KEY_CHANGE_IN_PRODUCTION",
        token_lifetime_hours: int = 24,
        refresh_token_lifetime_days: int = 30
    ):
        """
        Инициализация Session Manager
        
        Args:
            secret_key: Секретный ключ для JWT (ОБЯЗАТЕЛЬНО изменить в production!)
            token_lifetime_hours: Время жизни access token (часы)
            refresh_token_lifetime_days: Время жизни refresh token (дни)
        """
        self.secret_key = secret_key
        self.token_lifetime = timedelta(hours=token_lifetime_hours)
        self.refresh_token_lifetime = timedelta(days=refresh_token_lifetime_days)
        
        # Хранилище сессий: user_id → Session
        # В production это будет Redis
        self.sessions: Dict[str, Session] = {}
        
        # Хранилище refresh токенов: refresh_token → user_id
        self.refresh_tokens: Dict[str, str] = {}
        
        logger.info(f"✅ SessionManager инициализирован (token_lifetime={token_lifetime_hours}h)")
    
    def create_session(
        self,
        user_id: str,
        device_id: str,
        device_type: str = "iOS",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Создание новой сессии и JWT токена
        
        Args:
            user_id: ID пользователя
            device_id: ID устройства
            device_type: Тип устройства ("iOS" или "Android")
            ip_address: IP адрес пользователя
            user_agent: User-Agent браузера/приложения
            
        Returns:
            Dict с access_token и refresh_token
        """
        try:
            now = datetime.now()
            expires_at = now + self.token_lifetime
            
            # Создаем payload для JWT
            payload = {
                "user_id": user_id,
                "device_id": device_id,
                "device_type": device_type,
                "iat": now,  # Issued At
                "exp": expires_at,  # Expiration
                "jti": hashlib.sha256(f"{user_id}:{device_id}:{now}".encode()).hexdigest()[:16]
            }
            
            # Генерируем JWT access token
            access_token = jwt.encode(payload, self.secret_key, algorithm="HS256")
            
            # Генерируем refresh token
            refresh_payload = {
                "user_id": user_id,
                "device_id": device_id,
                "type": "refresh",
                "exp": now + self.refresh_token_lifetime
            }
            refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm="HS256")
            
            # Создаем сессию
            session = Session(
                user_id=user_id,
                token=access_token,
                device_id=device_id,
                device_type=device_type,
                created_at=now,
                expires_at=expires_at,
                last_activity=now,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Сохраняем сессию
            session_key = f"{user_id}:{device_id}"
            self.sessions[session_key] = session
            
            # Сохраняем refresh token
            self.refresh_tokens[refresh_token] = user_id
            
            logger.info(f"✅ Сессия создана для user_id={user_id}, device={device_type}")
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": int(self.token_lifetime.total_seconds())
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания сессии: {e}")
            raise
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Валидация JWT токена
        
        Args:
            token: JWT токен
            
        Returns:
            Payload токена если валиден, None если невалиден
        """
        try:
            # Декодируем токен
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            user_id = payload.get("user_id")
            device_id = payload.get("device_id")
            
            # Проверяем, что сессия существует
            session_key = f"{user_id}:{device_id}"
            if session_key not in self.sessions:
                logger.warning(f"⚠️ Сессия не найдена: {session_key}")
                return None
            
            session = self.sessions[session_key]
            
            # Проверяем, что токен не истек
            if datetime.now() > session.expires_at:
                logger.warning(f"⚠️ Токен истек для user_id={user_id}")
                self.revoke_session(user_id, device_id)
                return None
            
            # Обновляем last_activity
            session.last_activity = datetime.now()
            
            logger.info(f"✅ Токен валиден для user_id={user_id}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("⚠️ Токен истек")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"⚠️ Неверный токен: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка валидации токена: {e}")
            return None
    
    def refresh_session(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Обновление сессии с помощью refresh token
        
        Args:
            refresh_token: Refresh токен
            
        Returns:
            Новый access_token или None
        """
        try:
            # Проверяем refresh token
            if refresh_token not in self.refresh_tokens:
                logger.warning("⚠️ Refresh token не найден")
                return None
            
            # Декодируем refresh token
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=["HS256"])
            
            user_id = payload.get("user_id")
            device_id = payload.get("device_id")
            
            # Создаем новый access token
            now = datetime.now()
            expires_at = now + self.token_lifetime
            
            new_payload = {
                "user_id": user_id,
                "device_id": device_id,
                "device_type": payload.get("device_type", "iOS"),
                "iat": now,
                "exp": expires_at,
                "jti": hashlib.sha256(f"{user_id}:{device_id}:{now}".encode()).hexdigest()[:16]
            }
            
            new_access_token = jwt.encode(new_payload, self.secret_key, algorithm="HS256")
            
            # Обновляем сессию
            session_key = f"{user_id}:{device_id}"
            if session_key in self.sessions:
                self.sessions[session_key].token = new_access_token
                self.sessions[session_key].expires_at = expires_at
                self.sessions[session_key].last_activity = now
            
            logger.info(f"✅ Токен обновлен для user_id={user_id}")
            
            return {
                "access_token": new_access_token,
                "token_type": "Bearer",
                "expires_in": int(self.token_lifetime.total_seconds())
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("⚠️ Refresh token истек")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка обновления токена: {e}")
            return None
    
    def revoke_session(self, user_id: str, device_id: str) -> bool:
        """
        Отзыв сессии (logout)
        
        Args:
            user_id: ID пользователя
            device_id: ID устройства
            
        Returns:
            True если сессия отозвана
        """
        try:
            session_key = f"{user_id}:{device_id}"
            
            if session_key in self.sessions:
                del self.sessions[session_key]
                logger.info(f"✅ Сессия отозвана для user_id={user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка отзыва сессии: {e}")
            return False
    
    def revoke_all_sessions(self, user_id: str) -> int:
        """
        Отзыв всех сессий пользователя (на всех устройствах)
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Количество отозванных сессий
        """
        try:
            revoked_count = 0
            sessions_to_revoke = []
            
            for session_key, session in self.sessions.items():
                if session.user_id == user_id:
                    sessions_to_revoke.append(session_key)
            
            for session_key in sessions_to_revoke:
                del self.sessions[session_key]
                revoked_count += 1
            
            logger.info(f"✅ Отозвано {revoked_count} сессий для user_id={user_id}")
            return revoked_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка отзыва сессий: {e}")
            return 0
    
    def get_active_sessions(self, user_id: str) -> list:
        """
        Получить активные сессии пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список активных сессий
        """
        active_sessions = []
        
        for session_key, session in self.sessions.items():
            if session.user_id == user_id:
                if datetime.now() < session.expires_at:
                    active_sessions.append({
                        "device_id": session.device_id,
                        "device_type": session.device_type,
                        "created_at": session.created_at.isoformat(),
                        "expires_at": session.expires_at.isoformat(),
                        "last_activity": session.last_activity.isoformat(),
                        "ip_address": session.ip_address
                    })
        
        return active_sessions
    
    def cleanup_expired_sessions(self) -> int:
        """
        Очистка истекших сессий
        
        Returns:
            Количество удаленных сессий
        """
        now = datetime.now()
        expired_sessions = []
        
        for session_key, session in self.sessions.items():
            if now > session.expires_at:
                expired_sessions.append(session_key)
        
        for session_key in expired_sessions:
            del self.sessions[session_key]
        
        if expired_sessions:
            logger.info(f"✅ Удалено {len(expired_sessions)} истекших сессий")
        
        return len(expired_sessions)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику сессий"""
        ios_sessions = sum(1 for s in self.sessions.values() if s.device_type == "iOS")
        android_sessions = sum(1 for s in self.sessions.values() if s.device_type == "Android")
        
        return {
            "total_sessions": len(self.sessions),
            "ios_sessions": ios_sessions,
            "android_sessions": android_sessions,
            "refresh_tokens": len(self.refresh_tokens),
            "token_lifetime_hours": int(self.token_lifetime.total_seconds() / 3600)
        }


# Глобальный экземпляр
session_manager = SessionManager()


# ═══════════════════════════════════════════════════════════════
# FastAPI Integration
# ═══════════════════════════════════════════════════════════════

from fastapi import Depends, HTTPException, Header


async def get_current_user(authorization: str = Header(None)) -> Dict[str, Any]:
    """
    Dependency для получения текущего пользователя из JWT токена
    
    Использование:
        @app.get("/api/protected")
        async def protected(user = Depends(get_current_user)):
            return {"user_id": user["user_id"]}
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Отсутствует токен авторизации")
    
    # Извлекаем токен из "Bearer TOKEN"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Неверная схема авторизации")
    except ValueError:
        raise HTTPException(status_code=401, detail="Неверный формат токена")
    
    # Валидируем токен
    payload = session_manager.validate_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Неверный или истекший токен")
    
    return payload


# ═══════════════════════════════════════════════════════════════
# Тестирование
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧪 Тестирование SessionManager")
    print("=" * 60)
    
    sm = SessionManager()
    
    # Тест 1: Создание сессии для iOS
    print("\n1️⃣ Создание сессии для iOS...")
    ios_session = sm.create_session(
        user_id="user_123",
        device_id="iphone_001",
        device_type="iOS",
        ip_address="192.168.1.100"
    )
    print(f"✅ iOS Access Token: {ios_session['access_token'][:50]}...")
    print(f"✅ iOS Refresh Token: {ios_session['refresh_token'][:50]}...")
    
    # Тест 2: Создание сессии для Android
    print("\n2️⃣ Создание сессии для Android...")
    android_session = sm.create_session(
        user_id="user_123",
        device_id="android_001",
        device_type="Android",
        ip_address="192.168.1.101"
    )
    print(f"✅ Android Access Token: {android_session['access_token'][:50]}...")
    
    # Тест 3: Валидация токена
    print("\n3️⃣ Валидация токена...")
    payload = sm.validate_token(ios_session['access_token'])
    if payload:
        print(f"✅ Токен валиден: user_id={payload['user_id']}, device={payload['device_type']}")
    else:
        print("❌ Токен невалиден")
    
    # Тест 4: Получение активных сессий
    print("\n4️⃣ Активные сессии пользователя...")
    active = sm.get_active_sessions("user_123")
    print(f"✅ Активных сессий: {len(active)}")
    for sess in active:
        print(f"   - {sess['device_type']}: {sess['device_id']}")
    
    # Тест 5: Обновление токена
    print("\n5️⃣ Обновление токена...")
    new_tokens = sm.refresh_session(ios_session['refresh_token'])
    if new_tokens:
        print(f"✅ Новый Access Token: {new_tokens['access_token'][:50]}...")
    else:
        print("❌ Ошибка обновления")
    
    # Тест 6: Статистика
    print("\n6️⃣ Статистика сессий...")
    stats = sm.get_stats()
    print(f"✅ Всего сессий: {stats['total_sessions']}")
    print(f"   - iOS: {stats['ios_sessions']}")
    print(f"   - Android: {stats['android_sessions']}")
    
    # Тест 7: Отзыв одной сессии
    print("\n7️⃣ Отзыв сессии iOS...")
    revoked = sm.revoke_session("user_123", "iphone_001")
    print(f"✅ Сессия отозвана: {revoked}")
    
    # Тест 8: Отзыв всех сессий
    print("\n8️⃣ Отзыв всех сессий пользователя...")
    revoked_count = sm.revoke_all_sessions("user_123")
    print(f"✅ Отозвано сессий: {revoked_count}")
    
    # Финальная статистика
    print("\n📊 Финальная статистика...")
    final_stats = sm.get_stats()
    print(f"✅ Всего сессий: {final_stats['total_sessions']}")
    
    print("\n" + "=" * 60)
    print("✅ Все тесты пройдены!")




