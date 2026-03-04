"""
Авторизация: Проверка JWT токенов
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
import jwt
import os

security = HTTPBearer()

# В продакшене использовать переменные окружения
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def decode_token(token: str) -> Optional[Dict]:
    """
    Декодировать JWT токен и вернуть payload
    
    Args:
        token: JWT токен из заголовка Authorization
        
    Returns:
        Dict с данными пользователя (user_id, email, etc.) или None
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
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
    
    # Проверяем что в payload есть user_id
    if "user_id" not in payload and "id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не содержит user_id",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Нормализуем user_id (может быть "user_id" или "id")
    user_id = payload.get("user_id") or payload.get("id")
    
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

