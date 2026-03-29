"""
Авторизация: Проверка JWT токенов
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
import jwt
import os
import logging

# ✅ JWT-003: Настройка логирования для диагностики JWT
logger = logging.getLogger(__name__)

security = HTTPBearer()

# ✅ JWT-011: Унифицированный JWT_SECRET (совпадает с jwt_service.py)
# В продакшене использовать переменные окружения
JWT_SECRET = os.getenv("JWT_SECRET", "aladdin-super-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def decode_token(token: str) -> Optional[Dict]:
    """
    Декодировать JWT токен и вернуть payload
    
    Args:
        token: JWT токен из заголовка Authorization
        
    Returns:
        Dict с данными пользователя (user_id, email, etc.) или None
    """
    # Security hardening: never log token content or secret material.
    logger.info("🔐 [JWT-003] decode_token: token decode attempt")
    logger.info("   - token_length: %s", len(token))
    logger.info("   - algorithm: %s", JWT_ALGORITHM)
    
    try:
        # ✅ JWT-010: Добавлен leeway для защиты от разницы времени между клиентом и сервером
        # Leeway = 60 секунд допуска для синхронизации времени
        payload = jwt.decode(
            token, 
            JWT_SECRET, 
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": True},
            leeway=60  # 60 секунд допуска для разницы времени
        )
        
        # ✅ JWT-003: Логирование успешного декодирования
        user_id = payload.get("sub") or payload.get("user_id") or payload.get("id", "unknown")
        exp = payload.get("exp", "unknown")
        logger.info(f"✅ [JWT-003] decode_token: Успешно декодирован токен")
        logger.info(f"   - User ID: {user_id}")
        logger.info(f"   - Expires at: {exp}")
        logger.info(f"   - Leeway: 60 секунд (JWT-010)")
        
        return payload
    except jwt.ExpiredSignatureError as e:
        # ✅ JWT-003: Детальное логирование ошибки истечения
        logger.error("❌ [JWT-003] decode_token: Token expired")
        logger.error("   - error: %s", str(e))
        return None
    except jwt.InvalidTokenError as e:
        # ✅ JWT-003: Детальное логирование ошибки невалидного токена
        logger.error("❌ [JWT-003] decode_token: Invalid token")
        logger.error("   - error: %s", str(e))
        logger.error("   - error_type: %s", type(e).__name__)
        return None
    except Exception as e:
        # ✅ JWT-003: Логирование неожиданных ошибок
        logger.error("❌ [JWT-003] decode_token: Unexpected error")
        logger.error("   - error: %s", str(e))
        logger.error("   - error_type: %s", type(e).__name__)
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Зависимость для получения текущего пользователя из JWT токена
    
    Использование:
        @router.get("/endpoint")
        async def endpoint(current_user: dict = Depends(get_current_user)):
            user_id = current_user["id"]
            ...
    
    Raises:
        HTTPException: Если токен невалиден или отсутствует
    """
    token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не предоставлен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или истекший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ✅ BUILD 121: Проверяем что в payload есть user_id, id или sub (для device tokens)
    # Device tokens используют "sub" (subject), а user tokens используют "user_id" или "id"
    if "user_id" not in payload and "id" not in payload and "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не содержит user_id, id или sub",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ✅ BUILD 121: Нормализуем user_id (может быть "user_id", "id" или "sub")
    # Приоритет: user_id > id > sub (для обратной совместимости)
    user_id = payload.get("user_id") or payload.get("id") or payload.get("sub")
    
    return {
        "id": user_id,
        "email": payload.get("email"),
        **payload  # Включаем все остальные поля из токена
    }


# Альтернативная версия для случаев, когда токен может быть необязательным
def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict]:
    """
    Опциональная версия get_current_user
    
    Возвращает None если токен отсутствует или невалиден
    """
    if credentials is None:
        return None
    
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None

