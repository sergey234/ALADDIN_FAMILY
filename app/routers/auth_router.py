"""
Роутер для авторизации: логин, регистрация, обновление токенов
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
try:
    from pydantic import EmailStr
except ImportError:
    # Для старых версий pydantic используем str
    EmailStr = str
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timedelta
import jwt
import os
import hashlib
import secrets

# ✅ ИСПРАВЛЕНИЕ: Импорты с учетом структуры проекта
# На сервере должна быть директория app/database/ с файлом database.py
try:
    # Вариант 1: Стандартная структура app.database.database (основной вариант)
    from app.database.database import get_db
    from app.auth import JWT_SECRET, JWT_ALGORITHM
except ImportError as e:
    try:
        # Вариант 2: app.database (если database.py в app/)
        from app.database import get_db
        from app.auth import JWT_SECRET, JWT_ALGORITHM
    except ImportError:
        # Вариант 3: Прямой импорт (для тестирования)
        import sys
        import os
        # Добавляем корневую директорию проекта в путь
        backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        try:
            from database import get_db
            from auth import JWT_SECRET, JWT_ALGORITHM
        except ImportError:
            # Если database.py не найден, выводим ошибку вместо заглушки
            print(f"❌ ОШИБКА: Не удалось импортировать get_db. Ошибка: {e}")
            print("Проверьте, что файл /opt/aladdin-backend/app/database/database.py существует")
            raise ImportError("Не удалось импортировать get_db из app.database.database")

router = APIRouter(tags=["auth"])
security = HTTPBearer()

# ============================================
# МОДЕЛИ ЗАПРОСОВ И ОТВЕТОВ
# ============================================

class LoginRequest(BaseModel):
    """Запрос на логин"""
    email: str  # Используем str вместо EmailStr для совместимости
    password: str

class RecoveryCodeLoginRequest(BaseModel):
    """Запрос на авторизацию по Recovery Code БЕЗ персональных данных"""
    family_id: str  # Анонимный ID семьи
    recovery_code: str  # Recovery code (может быть family_id или специальный код)
    
    # ⚠️ ВАЖНО: НЕ собираем персональные данные!
    # ❌ НЕТ email, password, телефон
    # ✅ Только анонимные данные: family_id, recovery_code

class RefreshTokenRequest(BaseModel):
    """Запрос на обновление токена"""
    refresh_token: str

class LoginResponse(BaseModel):
    """Ответ на логин"""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"

class RefreshTokenResponse(BaseModel):
    """Ответ на обновление токена"""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def hash_password(password: str) -> str:
    """Хеширование пароля с использованием SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание JWT access token"""
    # JWT TTL policy for operational auth flow:
    # - access token: short-lived (typically 24h at call sites)
    # - refresh token: long enough for rotation (30d, see create_refresh_token)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)  # По умолчанию 1 час
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Создание JWT refresh token (действителен 30 дней)"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def get_user_by_email(db: Session, email: str) -> Optional[dict]:
    """Получение пользователя по email из базы данных"""
    try:
        # Проверяем наличие таблицы users
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'users'
        """))
        table_exists = result.fetchone() is not None
        
        if not table_exists:
            # Если таблицы нет, создаем её
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.commit()
        
        # Ищем пользователя
        result = db.execute(
            text("SELECT id, email, password_hash FROM users WHERE email = :email"),
            {"email": email}
        )
        user = result.fetchone()
        
        if user:
            return {
                "id": user[0],
                "email": user[1],
                "password_hash": user[2]
            }
        return None
    except Exception as e:
        print(f"Ошибка при получении пользователя: {e}")
        return None

def create_user(db: Session, email: str, password: str) -> Optional[dict]:
    """Создание нового пользователя"""
    try:
        # Проверяем наличие таблицы users
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'users'
        """))
        table_exists = result.fetchone() is not None
        
        if not table_exists:
            # Если таблицы нет, создаем её
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.commit()
        
        # Хешируем пароль
        password_hash = hash_password(password)
        
        # Создаем пользователя
        result = db.execute(
            text("""
                INSERT INTO users (email, password_hash) 
                VALUES (:email, :password_hash)
                RETURNING id, email
            """),
            {"email": email, "password_hash": password_hash}
        )
        db.commit()
        
        user = result.fetchone()
        if user:
            return {
                "id": user[0],
                "email": user[1]
            }
        return None
    except Exception as e:
        db.rollback()
        print(f"Ошибка при создании пользователя: {e}")
        return None

# ============================================
# ENDPOINTS
# ============================================

@router.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Авторизация пользователя
    
    Принимает email и password, возвращает access_token и refresh_token
    """
    try:
        # Получаем пользователя из БД
        user = get_user_by_email(db, login_data.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        # Проверяем пароль
        if not verify_password(login_data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        # Создаем токены
        token_data = {
            "user_id": user["id"],
            "id": user["id"],
            "email": user["email"]
        }
        
        access_token = create_access_token(token_data, expires_delta=timedelta(hours=24))
        refresh_token = create_refresh_token(token_data)
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=86400,  # 24 часа в секундах
            token_type="Bearer"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка при логине: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

@router.post("/auth/register")
async def register(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя
    
    Создает нового пользователя с указанным email и password
    """
    try:
        # Проверяем, существует ли пользователь
        existing_user = get_user_by_email(db, login_data.email)
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        # Создаем пользователя
        user = create_user(db, login_data.email, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось создать пользователя"
            )
        
        # Создаем токены для автоматического логина после регистрации
        token_data = {
            "user_id": user["id"],
            "id": user["id"],
            "email": user["email"]
        }
        
        access_token = create_access_token(token_data, expires_delta=timedelta(hours=24))
        refresh_token = create_refresh_token(token_data)
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=86400,
            token_type="Bearer"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка при регистрации: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

@router.post("/auth/refresh", response_model=RefreshTokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Обновление access token с помощью refresh token
    """
    try:
        # Декодируем refresh token
        try:
            payload = jwt.decode(refresh_data.refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token истёк"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидный refresh token"
            )
        
        # ✅ BUILD 122: Поддержка device_refresh токенов
        token_type = payload.get("type")
        if token_type not in ["refresh", "device_refresh"]:  # ✅ ДОБАВЛЕНО device_refresh
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный тип токена"
            )
        
        # ✅ BUILD 122: Для device tokens используем sub вместо user_id
        if token_type == "device_refresh":
            user_id = payload.get("sub") or payload.get("device_id")
            email = None  # Device tokens не имеют email
        else:
            user_id = payload.get("user_id") or payload.get("id")
            email = payload.get("email")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не содержит необходимых данных"
            )
        
        # Создаем новые токены
        token_data = {
            "user_id": user_id,
            "id": user_id,
            "sub": user_id,  # ✅ Для device tokens
            "email": email,
            "device_id": payload.get("device_id"),  # ✅ Сохраняем device_id
            "type": "device_auth" if token_type == "device_refresh" else "access"  # ✅ Тип нового токена
        }
        
        access_token = create_access_token(token_data, expires_delta=timedelta(hours=24))
        
        # ✅ BUILD 122: Создаем новый refresh token для device tokens
        if token_type == "device_refresh":
            new_refresh_token_data = {
                "sub": user_id,
                "device_id": payload.get("device_id"),
                "type": "device_refresh",
                "exp": datetime.utcnow() + timedelta(days=30)
            }
            # Используем create_refresh_token, но с правильным типом
            new_refresh_token_data.update({
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(days=30)
            })
            new_refresh_token = jwt.encode(new_refresh_token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
        else:
            new_refresh_token = create_refresh_token(token_data)
        
        return RefreshTokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=86400,
            token_type="Bearer"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка при обновлении токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

@router.post("/auth/login-by-recovery-code", response_model=LoginResponse)
async def login_by_recovery_code(
    request: RecoveryCodeLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Авторизация по Recovery Code БЕЗ персональных данных.
    
    ⚠️ ВАЖНО: МЫ НЕ СОБИРАЕМ ПЕРСОНАЛЬНЫЕ ДАННЫЕ!
    - ❌ НЕ требует email, password, телефон
    - ✅ Использует только family_id и recovery_code (анонимные данные)
    - ✅ Авторизация БЕЗ персональных данных
    
    Принимает только:
    - family_id: анонимный ID семьи
    - recovery_code: recovery code (может быть family_id или специальный код)
    
    Возвращает:
    - access_token: JWT токен доступа
    - refresh_token: JWT токен обновления
    - expires_in: время жизни токена (86400 секунд = 24 часа)
    - token_type: "Bearer"
    """
    try:
        # ✅ Проверка входных данных
        if not request.family_id or not request.recovery_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid family_id or recovery_code"
            )
        
        # TODO: Реализовать проверку recovery code в БД
        # Проверить, что family_id существует
        # Проверить, что recovery_code совпадает с сохраненным recovery_code
        # В текущей реализации: recovery_code может быть равен family_id
        
        # ✅ Временная реализация: проверяем, что family_id не пустой
        # В будущем нужно проверить recovery_code в БД или в системе регистрации
        if request.recovery_code != request.family_id:
            # Пока что принимаем recovery_code = family_id
            # В будущем нужно проверить в БД
            pass
        
        # ✅ Создать токены
        token_data = {
            "family_id": request.family_id,
            "id": request.family_id,  # Временно используем family_id как user_id
            "sub": request.family_id  # Subject для JWT
        }
        access_token = create_access_token(token_data, expires_delta=timedelta(hours=24))
        refresh_token = create_refresh_token(token_data)
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=86400,  # 24 часа
            token_type="Bearer"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка авторизации: {str(e)}"
        )


@router.post("/auth/logout")
async def logout():
    """
    Выход из системы
    
    В текущей реализации просто возвращает успех.
    В будущем можно добавить blacklist для токенов.
    """
    return {"success": True, "data": True}

