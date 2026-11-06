"""
Роутер для авторизации: логин, регистрация, обновление токенов
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
try:
    from pydantic import EmailStr
except ImportError:
    # Для старых версий pydantic используем str
    EmailStr = str
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import os
import hashlib
import logging
import secrets
import re
from urllib.parse import quote_plus

_auth_log = logging.getLogger("aladdin.auth")

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

# PostgreSQL INTEGER max — device pseudo-ids from SHA256 can exceed this.
_PG_INT_MAX = 2_147_483_647


def _normalize_family_id(raw: str) -> str:
    compact = re.sub(r"[^A-Z0-9]", "", (raw or "").strip().upper())
    if compact.startswith("FAM") and len(compact) >= 15:
        return "FAM_" + compact[3:15]
    return (raw or "").strip().upper()


def _compact_invite_value(raw: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", (raw or "").strip().upper())


def _ensure_db_user_for_device(db: Session, device_id: str, device_type: Optional[str] = None) -> int:
    """Return stable users.id for a device; never use oversized hash pseudo-ids in PG INTEGER columns."""
    device_id = device_id.strip()
    if not device_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="device_id is required")

    row = db.execute(
        text("SELECT id FROM users WHERE device_id = :device_id LIMIT 1"),
        {"device_id": device_id},
    ).fetchone()
    if row and row[0] is not None:
        uid = int(row[0])
        if device_type:
            db.execute(
                text("UPDATE users SET device_type = :device_type WHERE id = :id"),
                {"device_type": device_type, "id": uid},
            )
            db.commit()
        return uid

    inserted = db.execute(
        text(
            """
            INSERT INTO users (device_id, device_type)
            VALUES (:device_id, :device_type)
            ON CONFLICT (device_id) DO UPDATE
                SET device_type = COALESCE(EXCLUDED.device_type, users.device_type)
            RETURNING id
            """
        ),
        {"device_id": device_id, "device_type": device_type or "ios"},
    ).fetchone()
    db.commit()
    if not inserted or inserted[0] is None:
        raise HTTPException(status_code=500, detail="Failed to register device user")
    return int(inserted[0])


def _prepare_token_data(raw: dict) -> dict:
    """Companion platform JWT claims (app_id, age_band, limits)."""
    try:
        from security.services.ai_platform.jwt_claims import enrich_access_token_data
        return enrich_access_token_data(raw)
    except ImportError:
        return raw

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


class DeviceRegisterRequest(BaseModel):
    """Anonymous device registration request (supports snake_case and camelCase)."""
    device_id: str = Field(..., alias="deviceId")
    device_type: str = Field("ios", alias="deviceType")

    model_config = {"populate_by_name": True}


class AppleLoginRequest(BaseModel):
    identityToken: str
    authorizationCode: str
    email: Optional[str] = None
    givenName: Optional[str] = None
    familyName: Optional[str] = None


class AuthSessionResponse(BaseModel):
    token: str
    refreshToken: Optional[str] = None
    userId: Optional[str] = None
    expiresAt: Optional[str] = None


class RequestMagicLinkRequest(BaseModel):
    email: str
    redirectUrl: Optional[str] = None


class ConsumeMagicLinkRequest(BaseModel):
    token: str


_magic_links: Dict[str, Dict[str, Any]] = {}

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
        
        access_token = create_access_token(_prepare_token_data(token_data), expires_delta=timedelta(hours=24))
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
        
        access_token = create_access_token(_prepare_token_data(token_data), expires_delta=timedelta(hours=24))
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


@router.post("/auth/register-device", response_model=LoginResponse)
async def register_device(
    request: Request,
    body: DeviceRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Anonymous device registration endpoint expected by mobile app and release gates.
    Returns access/refresh tokens without mock/fallback envelopes.
    """
    try:
        if not body.device_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="device_id is required",
            )

        device_type = (body.device_type or "").lower()
        if device_type == "web":
            from app.services.web_auth_rate_limit import check_web_register_ip_limit

            check_web_register_ip_limit(request)

        # Persist device → users.id (INTEGER-safe). Hash pseudo-ids overflow PG INTEGER.
        db_user_id = _ensure_db_user_for_device(db, body.device_id, body.device_type)
        token_data = {
            "user_id": db_user_id,
            "id": db_user_id,
            "sub": str(db_user_id),
            "device_id": body.device_id,
            "device_type": body.device_type,
            "type": "device_auth",
        }

        ttl = timedelta(hours=2) if device_type == "web" else timedelta(hours=24)
        expires_sec = int(ttl.total_seconds())
        access_token = create_access_token(
            _prepare_token_data(token_data), expires_delta=ttl
        )
        refresh_token = create_refresh_token(token_data)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_sec,
            token_type="Bearer",
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка при регистрации устройства: {e}")
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
            device_id = payload.get("device_id")
            if isinstance(device_id, str) and device_id.strip():
                user_id = _ensure_db_user_for_device(db, device_id, payload.get("device_type"))
            else:
                raw = payload.get("sub") or payload.get("user_id") or payload.get("id")
                user_id = int(raw) if raw is not None and str(raw).isdigit() else raw
            email = None  # Device tokens не имеют email
        else:
            user_id = payload.get("user_id") or payload.get("id")
            email = payload.get("email")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не содержит необходимых данных"
            )

        if token_type == "device_refresh":
            user_id = int(user_id)
            if user_id > _PG_INT_MAX:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid device token subject",
                )
        
        # Создаем новые токены
        token_data = {
            "user_id": user_id,
            "id": user_id,
            "sub": str(user_id),
            "email": email,
            "device_id": payload.get("device_id"),  # ✅ Сохраняем device_id
            "type": "device_auth" if token_type == "device_refresh" else "access"  # ✅ Тип нового токена
        }
        
        access_token = create_access_token(_prepare_token_data(token_data), expires_delta=timedelta(hours=24))
        
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
    http_request: Request,
    body: RecoveryCodeLoginRequest,
    db: Session = Depends(get_db),
):
    """
    Авторизация по Recovery Code БЕЗ персональных данных.

    Product contract (Step A — UX unchanged for iOS 17/18):
    - recovery_code is the family_id (FAM_… or FAM-… forms both ok).
    - Does NOT accept invite_token as owner login (invite = join member, Step B).

    Step A shield: IP rate limit + family must exist + structured journal log.
    """
    from app.services.web_auth_rate_limit import check_recovery_login_ip_limit, client_ip

    ip = client_ip(http_request)
    try:
        attempt_n = check_recovery_login_ip_limit(http_request)
    except HTTPException as exc:
        if exc.status_code == 429:
            _auth_log.warning(
                "SECURITY recovery_login rate_limited ip=%s",
                ip,
            )
        raise

    try:
        if not body.family_id or not body.recovery_code:
            _auth_log.info(
                "SECURITY recovery_login outcome=fail reason=missing_fields ip=%s attempt=%s",
                ip,
                attempt_n,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid family_id or recovery_code",
            )

        canonical_family_id = _normalize_family_id(body.family_id)
        compact_recovery = _compact_invite_value(body.recovery_code)
        compact_family = _compact_invite_value(canonical_family_id)
        family_tag = (canonical_family_id[:8] + "…") if canonical_family_id else "?"

        family_row = db.execute(
            text("SELECT owner_user_id FROM families WHERE id = :family_id LIMIT 1"),
            {"family_id": canonical_family_id},
        ).fetchone()
        if not family_row:
            _auth_log.info(
                "SECURITY recovery_login outcome=fail reason=unknown_family family=%s ip=%s attempt=%s",
                family_tag,
                ip,
                attempt_n,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid family_id or recovery_code",
            )

        # Same product rule as before: code matches family_id (any punctuation).
        # Invite QR token is intentionally NOT accepted here (would widen owner takeover).
        # Plain == : compare_digest raises on unequal length (typos must stay 401, not 500).
        recovery_ok = compact_recovery == compact_family
        if not recovery_ok:
            _auth_log.info(
                "SECURITY recovery_login outcome=fail reason=bad_code family=%s ip=%s attempt=%s",
                family_tag,
                ip,
                attempt_n,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid family_id or recovery_code",
            )

        owner_user_id = None
        try:
            if family_row[0] is not None:
                owner_user_id = int(family_row[0])
        except Exception:
            owner_user_id = None

        resolved_subject = str(owner_user_id) if owner_user_id is not None else canonical_family_id

        token_data = {
            "family_id": canonical_family_id,
            "id": resolved_subject,
            "user_id": resolved_subject,
            "sub": resolved_subject,
        }
        access_token = create_access_token(_prepare_token_data(token_data), expires_delta=timedelta(hours=24))
        refresh_token = create_refresh_token(token_data)

        _auth_log.info(
            "SECURITY recovery_login outcome=ok family=%s ip=%s attempt=%s",
            family_tag,
            ip,
            attempt_n,
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=86400,
            token_type="Bearer",
        )

    except HTTPException:
        raise
    except Exception as e:
        _auth_log.exception(
            "SECURITY recovery_login outcome=error ip=%s err=%s",
            ip,
            type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка авторизации: {str(e)}",
        )


@router.post("/auth/apple", response_model=AuthSessionResponse)
async def login_with_apple(request: AppleLoginRequest):
    """
    Sign in with Apple: validates payload shape and issues app session tokens.
    """
    if not request.identityToken.strip() or not request.authorizationCode.strip():
        raise HTTPException(status_code=400, detail="identityToken and authorizationCode are required")

    # Deterministic user id from Apple identity token hash.
    user_hash = hashlib.sha256(request.identityToken.encode()).hexdigest()
    user_id = str(int(user_hash[:12], 16))

    token_data = {
        "user_id": user_id,
        "id": user_id,
        "sub": user_id,
        "email": request.email,
        "auth_provider": "apple",
    }
    access_token = create_access_token(_prepare_token_data(token_data), expires_delta=timedelta(hours=24))
    refresh_token = create_refresh_token(token_data)

    return AuthSessionResponse(
        token=access_token,
        refreshToken=refresh_token,
        userId=user_id,
        expiresAt=(datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z",
    )


@router.post("/auth/magic-link/request", response_model=Dict[str, Any])
async def request_magic_link(request: RequestMagicLinkRequest):
    email = request.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="email is required")

    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=20)
    _magic_links[token] = {
        "email": email,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
    }

    base_redirect = request.redirectUrl or "aladdin://auth/magic-link"
    link = f"{base_redirect}?token={quote_plus(token)}"
    return {
        "success": True,
        "data": True,
        "message": "Magic link generated",
        "magicLink": link,
        "expiresAt": expires_at.isoformat() + "Z",
    }


@router.post("/auth/magic-link/consume", response_model=AuthSessionResponse)
async def consume_magic_link(request: ConsumeMagicLinkRequest):
    token = request.token.strip()
    if not token:
        raise HTTPException(status_code=400, detail="token is required")

    payload = _magic_links.get(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Magic link token is invalid")

    if datetime.utcnow() > payload["expires_at"]:
        _magic_links.pop(token, None)
        raise HTTPException(status_code=401, detail="Magic link token expired")

    email = payload.get("email")
    user_id = str(int(hashlib.sha256((email or token).encode()).hexdigest()[:12], 16))
    token_data = {
        "user_id": user_id,
        "id": user_id,
        "sub": user_id,
        "email": email,
        "auth_provider": "magic_link",
    }
    access_token = create_access_token(_prepare_token_data(token_data), expires_delta=timedelta(hours=24))
    refresh_token = create_refresh_token(token_data)
    _magic_links.pop(token, None)

    return AuthSessionResponse(
        token=access_token,
        refreshToken=refresh_token,
        userId=user_id,
        expiresAt=(datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z",
    )


@router.post("/auth/logout")
async def logout():
    """
    Выход из системы
    
    В текущей реализации просто возвращает успех.
    В будущем можно добавить blacklist для токенов.
    """
    return {"success": True, "data": True}

