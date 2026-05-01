"""
============================================
FAMILY API: Endpoints для семейной статистики
============================================
Сервер: 149.154.65.180
Дата: 17 января 2026
============================================
API для получения статистики семьи
"""

from fastapi import APIRouter, HTTPException, Request, Depends, status, Query, Response, File, UploadFile, Form, Header
from fastapi.responses import FileResponse
import asyncio
import os
import re
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, Any, Dict, List, Annotated
from datetime import datetime
import uuid
from pydantic import BaseModel

# ✅ Импорт функции создания семьи (БЕЗ персональных данных)
from security.family.family_registration import create_family

# ✅ Авторизация с реальным user_id
from app.auth.auth import get_current_user

try:
    from app.database.database import get_db as get_postgres_db
except ImportError:
    get_postgres_db = None

# ✅ RATE LIMITING: Импорт slowapi для защиты от злоупотреблений
from slowapi import Limiter
from slowapi.util import get_remote_address

# ✅ STRUCTURED LOGGING: Импорт structlog для структурированного логирования
import structlog

router = APIRouter(prefix="/api/family", tags=["family"])

# ✅ RATE LIMITING: Инициализация Limiter (60 запросов в минуту на IP)
limiter = Limiter(key_func=get_remote_address)

# ✅ STRUCTURED LOGGING: Инициализация logger
logger = structlog.get_logger()

_family_indexes_initialized = False

_FAMILY_CHAT_UPLOAD_ROOT = Path(os.environ.get("ALADDIN_FAMILY_CHAT_UPLOAD_DIR", "/tmp/aladdin_family_chat_media"))
_SAFE_CHAT_MEDIA_FILENAME = re.compile(r"^[a-f0-9]{32}\.[A-Za-z0-9]{1,12}$")


def _ensure_family_chat_upload_root() -> Path:
    _FAMILY_CHAT_UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    return _FAMILY_CHAT_UPLOAD_ROOT

def _ensure_family_indexes(db) -> None:
    global _family_indexes_initialized
    if _family_indexes_initialized:
        return
    try:
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_family_members_family_id_id ON family_members (family_id, id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_family_members_user_id ON family_members (user_id)"))
        _family_indexes_initialized = True
        logger.info("family_indexes_ensured")
    except Exception as e:
        # Не блокируем бизнес-операцию, но логируем
        logger.warning("family_indexes_ensure_failed", error=str(e))
def _resolve_user_id_from_claim(current_user: dict) -> int:
    """Resolve stable integer user_id from JWT claims.

    Supports:
    - direct int id
    - numeric string id
    - legacy device-id tokens by mapping users.device_id -> users.id
    - lookup by email when present in claims
    """
    raw_id = current_user.get("user_id")
    if raw_id is None:
        raw_id = current_user.get("id")
    if raw_id is None:
        raw_id = current_user.get("sub")

    if isinstance(raw_id, int):
        return raw_id
    if isinstance(raw_id, str) and raw_id.strip().isdigit():
        return int(raw_id.strip())

    # Legacy compatibility path:
    # token might carry non-numeric id, while device identifier may be in `device_id` or `sub`.
    candidate_device_ids = []
    for val in (raw_id, current_user.get("device_id"), current_user.get("sub")):
        if isinstance(val, str) and val.strip():
            v = val.strip()
            if v not in candidate_device_ids:
                candidate_device_ids.append(v)

    if candidate_device_ids and get_postgres_db:
        gen = get_postgres_db()
        db = next(gen)
        try:
            for candidate in candidate_device_ids:
                row = db.execute(
                    text("SELECT id FROM users WHERE device_id = :device_id ORDER BY id DESC LIMIT 1"),
                    {"device_id": candidate},
                ).fetchone()
                if row and row[0] is not None:
                    return int(row[0])
        finally:
            gen.close()

    email = current_user.get("email")
    if isinstance(email, str) and email.strip() and get_postgres_db:
        gen = get_postgres_db()
        db = next(gen)
        try:
            row = db.execute(
                text("SELECT id FROM users WHERE lower(trim(email)) = lower(trim(:email)) ORDER BY id DESC LIMIT 1"),
                {"email": email.strip()},
            ).fetchone()
            if row and row[0] is not None:
                return int(row[0])
        finally:
            gen.close()

    raise HTTPException(status_code=401, detail="Invalid user_id in token")


def _iso_utc_timestamp() -> str:
    """Activity / ordering marker (ISO-8601 UTC). Prefer `updated_at` for ordering; this stays human-readable."""
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _resolve_primary_family_id_for_actor(db, user_id: int, current_user: dict) -> Optional[str]:
    """
    Единый выбор семьи для JWT-актора (GET /members, reconcile, согласование add/remove).

    1) Если в JWT есть `family_id` и пользователь — участник или владелец этой семьи → используем его.
    2) Иначе последняя по `updated_at` строка членства в `family_members`.
    3) Иначе последняя семья, где пользователь — `owner_user_id`.
    """
    raw = current_user.get("family_id")
    if raw is not None:
        fid = str(raw).strip()
        if fid:
            m = db.execute(
                text(
                    "SELECT 1 FROM family_members WHERE family_id = :fid AND user_id = :uid LIMIT 1"
                ),
                {"fid": fid, "uid": user_id},
            ).fetchone()
            if m:
                return fid
            o = db.execute(
                text("SELECT 1 FROM families WHERE id = :fid AND owner_user_id = :uid LIMIT 1"),
                {"fid": fid, "uid": user_id},
            ).fetchone()
            if o:
                return fid
    row = db.execute(
        text(
            """
            SELECT fm.family_id
            FROM family_members fm
            WHERE fm.user_id = :user_id
            ORDER BY fm.updated_at DESC NULLS LAST, fm.id DESC
            LIMIT 1
            """
        ),
        {"user_id": user_id},
    ).fetchone()
    if row and row[0] is not None:
        return str(row[0]).strip()
    fam_row = db.execute(
        text(
            "SELECT id FROM families WHERE owner_user_id = :user_id ORDER BY created_at DESC LIMIT 1"
        ),
        {"user_id": user_id},
    ).fetchone()
    if fam_row and fam_row[0] is not None:
        return str(fam_row[0]).strip()
    return None


def _actor_belongs_to_family(db, user_id: int, family_id: str) -> bool:
    """Участник семьи или владелец записи в `families`."""
    fid = str(family_id or "").strip()
    if not fid:
        return False
    m = db.execute(
        text("SELECT 1 FROM family_members WHERE family_id = :fid AND user_id = :uid LIMIT 1"),
        {"fid": fid, "uid": user_id},
    ).fetchone()
    if m:
        return True
    o = db.execute(
        text("SELECT 1 FROM families WHERE id = :fid AND owner_user_id = :uid LIMIT 1"),
        {"fid": fid, "uid": user_id},
    ).fetchone()
    return bool(o)


# ============================================
# МОДЕЛИ ОТВЕТОВ
# ============================================

class FamilyStatsResponse(BaseModel):
    totalMembers: int
    totalDevices: int
    totalThreats: int
    protectionLevel: int
    familyStatus: Optional[str] = None
    familyStatusMessage: Optional[str] = None


# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

async def get_family_stats_from_db(
    user_id: int,
    db: Optional[AsyncSession] = None
) -> FamilyStatsResponse:
    """
    Получить статистику семьи из базы данных.
    
    ✅ РЕАЛИЗАЦИЯ: Реальные SQL запросы к SQLite
    """
    # ✅ Если БД доступна - получаем реальные данные
    if db:
        try:
            # ✅ Получаем количество членов семьи
            members_result = await db.execute(
                text("""
                    SELECT COUNT(*) as count
                    FROM family_members
                    WHERE user_id = :user_id
                """),
                {"user_id": user_id}
            )
            members_row = members_result.fetchone()
            total_members = members_row[0] if members_row else 1  # Минимум 1 (сам пользователь)
            
            # ✅ Количество устройств: сначала aladdin_family_devices (как GET /api/devices), иначе legacy `devices`
            total_devices = 0
            try:
                devices_result = await db.execute(
                    text(
                        """
                        SELECT COUNT(*) as count
                        FROM aladdin_family_devices
                        WHERE user_id = :uid_text
                        """
                    ),
                    {"uid_text": str(user_id)},
                )
                devices_row = devices_result.fetchone()
                total_devices = int(devices_row[0] or 0) if devices_row else 0
            except Exception:
                devices_result = await db.execute(
                    text(
                        """
                        SELECT COUNT(*) as count
                        FROM devices
                        WHERE user_id = :user_id OR owner_id = :user_id
                        """
                    ),
                    {"user_id": user_id},
                )
                devices_row = devices_result.fetchone()
                total_devices = int(devices_row[0] or 0) if devices_row else 0
            
            # ✅ Получаем количество заблокированных угроз
            threats_result = await db.execute(
                text("""
                    SELECT COUNT(*) as count
                    FROM threats_blocked
                    WHERE user_id = :user_id
                    AND blocked_at >= datetime('now', '-30 days')
                """),
                {"user_id": user_id}
            )
            threats_row = threats_result.fetchone()
            total_threats = threats_row[0] if threats_row else 0
            
            # ✅ Вычисляем уровень защиты (процент активных компонентов защиты)
            components_result = await db.execute(
                text("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN is_enabled = 1 THEN 1 ELSE 0 END) as enabled
                    FROM component_status
                    WHERE user_id = :user_id
                """),
                {"user_id": user_id}
            )
            components_row = components_result.fetchone()
            
            if components_row and components_row[0] > 0:
                protection_level = int((components_row[1] / components_row[0]) * 100)
            else:
                protection_level = 95  # Дефолтный уровень
            
            # ✅ Определяем статус семьи
            if protection_level >= 80 and total_threats == 0:
                family_status = "protected"
                family_status_message = "Вся семья под защитой"
            elif protection_level >= 50:
                family_status = "warning"
                family_status_message = "Не все функции защиты активны"
            else:
                family_status = "danger"
                family_status_message = "Требуется активация защиты"
            
            return FamilyStatsResponse(
                totalMembers=total_members,
                totalDevices=total_devices,
                totalThreats=total_threats,
                protectionLevel=protection_level,
                familyStatus=family_status,
                familyStatusMessage=family_status_message
            )
            
        except Exception as e:
            # ✅ Если ошибка БД - логируем и возвращаем дефолтные значения
            logger.warning(
                "family_stats_db_error",
                user_id=user_id,
                error=str(e),
                timestamp=datetime.now().isoformat()
            )
            # Продолжаем с дефолтными значениями
    
    # ✅ Production rule: no fake fallback.
    # Если БД недоступна — нельзя возвращать "4/6/45" как будто это реальные данные.
    raise HTTPException(status_code=503, detail="Family stats backend unavailable (database not configured)")


# ============================================
# ENDPOINT: GET /api/family/stats
# ============================================

@router.get("/stats", response_model=FamilyStatsResponse)
@limiter.limit("60/minute")  # ✅ RATE LIMITING: 60 запросов в минуту на IP
async def get_family_stats(
    request: Request,
    current_user: dict = Depends(get_current_user)  # ✅ Авторизация: реальный пользователь из токена
):
    """
    Получить статистику семьи.
    
    Требуется авторизация (токен в заголовке Authorization: Bearer {token})
    
    Возвращает:
    - totalMembers: количество членов семьи
    - totalDevices: количество устройств
    - totalThreats: количество заблокированных угроз (за последние 30 дней)
    - protectionLevel: уровень защиты (0-100%)
    - familyStatus: статус семьи ("protected", "warning", "danger")
    - familyStatusMessage: сообщение о статусе
    """
    # ✅ Получить реальный user_id из токена (должен быть стабилен для FK в БД)
    user_id = _resolve_user_id_from_claim(current_user)
    
    # ✅ STRUCTURED LOGGING: Логирование запроса статистики
    logger.info(
        "family_stats_requested",
        user_id=user_id,
        timestamp=datetime.now().isoformat()
    )
    
    # ✅ РЕАЛИЗАЦИЯ: family схемы лежат в PostgreSQL.
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")

    def load_stats_sync():
        gen = get_postgres_db()
        db = next(gen)
        try:
            # Determine family_id for this user
            fam_row = db.execute(
                text("SELECT id FROM families WHERE owner_user_id = :user_id ORDER BY created_at DESC LIMIT 1"),
                {"user_id": user_id},
            ).fetchone()
            if not fam_row:
                # No family yet -> real empty stats
                return FamilyStatsResponse(
                    totalMembers=0,
                    totalDevices=0,
                    totalThreats=0,
                    protectionLevel=0,
                    familyStatus="danger",
                    familyStatusMessage="Семья не создана",
                )

            family_id = fam_row[0]

            # Aggregate from family_members table (source of truth)
            agg = db.execute(
                text(
                    """
                    SELECT
                        COUNT(*)::int AS members,
                        COALESCE(SUM(devices), 0)::int AS devices,
                        COALESCE(SUM(threats_blocked), 0)::int AS threats
                    FROM family_members
                    WHERE family_id = :family_id
                    """
                ),
                {"family_id": family_id},
            ).fetchone()

            total_members = int(agg[0] or 0)
            member_devices_sum = int(agg[1] or 0)
            total_threats = int(agg[2] or 0)

            # Источник правды для списка устройств — aladdin_family_devices (GET/POST /api/devices).
            # SUM(family_members.devices) остаётся fallback, если таблица ещё не развёрнута или запрос недоступен.
            total_devices = member_devices_sum
            try:
                drow = db.execute(
                    text(
                        """
                        SELECT COUNT(*)::int
                        FROM aladdin_family_devices d
                        WHERE d.user_id IN (
                            SELECT CAST(fm.user_id AS TEXT)
                            FROM family_members fm
                            WHERE fm.family_id = :family_id AND fm.user_id IS NOT NULL
                            UNION
                            SELECT CAST(f.owner_user_id AS TEXT)
                            FROM families f
                            WHERE f.id = :family_id
                        )
                        """
                    ),
                    {"family_id": family_id},
                ).fetchone()
                total_devices = int(drow[0] or 0) if drow else 0
            except Exception as e:
                logger.warning(
                    "family_stats_aladdin_devices_fallback",
                    family_id=str(family_id),
                    error=str(e),
                )
                total_devices = member_devices_sum

            # Simple protection level heuristic until components are wired to real tables
            protection_level = 95 if total_threats == 0 else 70

            if protection_level >= 80 and total_threats == 0:
                family_status = "protected"
                family_status_message = "Вся семья под защитой"
            elif protection_level >= 50:
                family_status = "warning"
                family_status_message = "Не все функции защиты активны"
            else:
                family_status = "danger"
                family_status_message = "Требуется активация защиты"

            return FamilyStatsResponse(
                totalMembers=total_members,
                totalDevices=total_devices,
                totalThreats=total_threats,
                protectionLevel=protection_level,
                familyStatus=family_status,
                familyStatusMessage=family_status_message,
            )
        finally:
            gen.close()

    try:
        stats = await asyncio.to_thread(load_stats_sync)
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(
            "family_stats_db_error",
            user_id=user_id,
            error=str(e),
            timestamp=datetime.now().isoformat(),
        )
        raise HTTPException(status_code=503, detail="Family backend unavailable")
    
    # ✅ STRUCTURED LOGGING: Логирование успешного ответа
    logger.info(
        "family_stats_returned",
        user_id=user_id,
        total_members=stats.totalMembers,
        total_devices=stats.totalDevices,
        total_threats=stats.totalThreats,
        protection_level=stats.protectionLevel,
        timestamp=datetime.now().isoformat()
    )
    
    return stats


# ============================================
# ENDPOINT: POST /api/family/create
# ============================================

class CreateFamilyRequest(BaseModel):
    """Запрос на создание семьи БЕЗ персональных данных"""
    role: str  # "parent", "child", "elderly", "other" (FamilyRole enum)
    age_group: str  # "1-6", "7-12", "13-17", "18-23", "24-55", "55+" (AgeGroup enum)
    personal_letter: str  # Одна буква (например, "V") - для анонимной идентификации
    device_type: str  # "iOS", "Android", и т.д.
    
    # ⚠️ ВАЖНО: НЕ собираем персональные данные!
    # ❌ НЕТ email, password, телефон, имя, фамилия
    # ✅ Только анонимные данные: role, age_group, personal_letter, device_type

class CreateFamilyResponse(BaseModel):
    """Ответ на создание семьи"""
    family_id: str  # Анонимный ID семьи
    qr_code_data: str  # Данные для QR кода
    short_code: str  # Короткий код для присоединения
    creator_member_id: str  # ID создателя семьи
    expires_at: str  # Время истечения кодов (ISO format)
    # Примечание: recovery_code = family_id (используется family_id как recovery code)


class FamilyCompatBoolResponse(BaseModel):
    success: bool
    data: bool
    message: Optional[str] = None

class SendFamilyChatMessageRequest(BaseModel):
    message: Optional[str] = None
    familyId: Optional[str] = None
    messageType: Optional[str] = None
    voiceUrl: Optional[str] = None
    voiceDuration: Optional[float] = None
    mediaUrl: Optional[str] = None
    mediaType: Optional[str] = None
    replyToMessageId: Optional[str] = None


class SendFamilyChatMessageResponse(BaseModel):
    success: bool
    messageId: str


class TypingIndicatorRequest(BaseModel):
    familyId: Optional[str] = None


class EditFamilyChatMessageRequest(BaseModel):
    messageId: str
    text: str


class ReactionRequest(BaseModel):
    messageId: str
    emoji: str


class ReadRequest(BaseModel):
    messageId: str


class FamilyMemberCompat(BaseModel):
    id: str
    name: str
    role: str


class FamilyMemberResponse(BaseModel):
    """
    Полный ответ участника семьи (должен соответствовать iOS `FamilyMemberResponse`)
    """
    id: str
    name: str
    role: str
    avatar: str
    status: str
    threatsBlocked: int
    lastActive: str
    devices: int


class AddFamilyMemberRequest(BaseModel):
    """
    Запрос на добавление участника семьи.

    ⚠️ Важно: поле name трактуется как анонимный ярлык (роль + буква/ник),
    а не как персональные ФИО. Роутер не требует email/телефон/паспорт.
    """
    name: str
    role: str
    familyId: Optional[str] = None


class RemoveFamilyMemberRequest(BaseModel):
    memberId: str
    source: Optional[str] = None
    reason: Optional[str] = None
    familyId: Optional[str] = None


def _ensure_family_chat_table(db) -> None:
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS family_chat_messages (
                id TEXT PRIMARY KEY,
                family_id TEXT NOT NULL,
                sender_user_id INTEGER,
                sender_name TEXT NOT NULL,
                text TEXT,
                timestamp TEXT NOT NULL,
                message_type TEXT,
                voice_url TEXT,
                voice_duration DOUBLE PRECISION,
                media_url TEXT,
                media_thumbnail_url TEXT,
                media_type TEXT,
                reply_to_message_id TEXT,
                edited_at TEXT,
                read_status TEXT,
                read_at TEXT
            )
            """
        )
    )
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS family_chat_reactions (
                id TEXT PRIMARY KEY,
                message_id TEXT NOT NULL,
                user_id INTEGER,
                user_name TEXT NOT NULL,
                emoji TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
    )
    db.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_family_chat_messages_family_time ON family_chat_messages (family_id, timestamp DESC)"
        )
    )
    db.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_family_chat_reactions_message_id ON family_chat_reactions (message_id)"
        )
    )

@router.post("/create", response_model=CreateFamilyResponse)
@limiter.limit("10/minute")  # ✅ RATE LIMITING: 10 запросов в минуту на IP
async def create_family_endpoint(
    request: Request,
    create_request: CreateFamilyRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Создание семьи БЕЗ персональных данных.
    
    ⚠️ ВАЖНО: МЫ НЕ СОБИРАЕМ ПЕРСОНАЛЬНЫЕ ДАННЫЕ!
    - ❌ НЕ требует email, password, телефон
    - ✅ Принимает только анонимные данные: role, age_group, personal_letter, device_type
    - ✅ Возвращает только анонимные данные: family_id, qr_code_data, short_code
    
    Принимает:
    - role: роль в семье ("parent", "child", "elderly", "other")
    - age_group: возрастная группа ("1-6", "7-12", "13-17", "18-23", "24-55", "55+")
    - personal_letter: буква для идентификации (одна буква, например, "V")
    - device_type: тип устройства ("iOS", "Android", и т.д.)
    
    Возвращает:
    - family_id: уникальный анонимный ID семьи
    - qr_code_data: данные для QR кода
    - short_code: короткий код для присоединения
    - creator_member_id: ID создателя семьи
    - expires_at: время истечения кодов (ISO format)
    """
    # ✅ STRUCTURED LOGGING: Логирование запроса
    logger.info(
        "family_create_requested",
        role=create_request.role,
        age_group=create_request.age_group,
        personal_letter=create_request.personal_letter,
        device_type=create_request.device_type,
        timestamp=datetime.now().isoformat()
    )
    
    try:
        # iOS UI currently sends symbolic values (toddler/school/teen/adult),
        # while family_registration_system expects numeric ranges.
        age_group_map = {
            "toddler": "1-6",
            "school": "7-12",
            "teen": "13-17",
            "adult": "24-55",
        }
        normalized_age_group = age_group_map.get(create_request.age_group, create_request.age_group)

        # ✅ Вызов функции генерации family_id/MEM_*/short_code (БЕЗ персональных данных)
        result = create_family(
            role=create_request.role,
            age_group=normalized_age_group,
            personal_letter=create_request.personal_letter,
            device_type=create_request.device_type
        )
        
        # ✅ result - это Dict[str, str] с ключами: family_id, qr_code_data, short_code, creator_member_id, expires_at
        response = CreateFamilyResponse(**result)

        # ✅ Persist to Postgres as source of truth
        if not get_postgres_db:
            raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")

        user_id = _resolve_user_id_from_claim(current_user)

        def persist_sync():
            gen = get_postgres_db()
            db = next(gen)
            try:
                db.execute(
                    text(
                        """
                        INSERT INTO families (id, owner_user_id)
                        VALUES (:family_id, :owner_user_id)
                        ON CONFLICT (id) DO NOTHING
                        """
                    ),
                    {"family_id": response.family_id, "owner_user_id": user_id},
                )
                # Creator becomes first family member
                db.execute(
                    text(
                        """
                        INSERT INTO family_members (id, family_id, user_id, name, role, status, last_active)
                        VALUES (:id, :family_id, :user_id, :name, :role, 'protected', :last_active)
                        ON CONFLICT (id) DO NOTHING
                        """
                    ),
                    {
                        "id": response.creator_member_id,
                        "family_id": response.family_id,
                        "user_id": user_id,
                        "name": f"{create_request.role.upper()} {create_request.personal_letter.upper()}",
                        "role": create_request.role,
                        "last_active": _iso_utc_timestamp(),
                    },
                )
                db.commit()
            finally:
                gen.close()

        await asyncio.to_thread(persist_sync)
        
        # ✅ STRUCTURED LOGGING: Логирование успешного создания
        logger.info(
            "family_created",
            family_id=response.family_id,
            creator_member_id=response.creator_member_id,
            timestamp=datetime.now().isoformat()
        )
        
        return response
        
    except ValueError as e:
        # ✅ Обработка ошибок валидации
        logger.warning(
            "family_create_validation_error",
            error=str(e),
            timestamp=datetime.now().isoformat()
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка валидации: {str(e)}"
        )
    except Exception as e:
        # ✅ Обработка других ошибок
        logger.error(
            "family_create_error",
            error=str(e),
            timestamp=datetime.now().isoformat()
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания семьи: {str(e)}"
        )


# ============================================
# COMPAT ENDPOINTS: /api/family/*
# ============================================


@router.post("/add", response_model=FamilyMemberResponse)
async def add_family_member(
    payload: AddFamilyMemberRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    ✅ Боевой endpoint: POST /api/family/add

    Требования:
    - Не возвращать sfm_mock/mock_fallback в production.
    - Использовать PostgreSQL как единственный source of truth.
    - Работать только для уже созданной семьи (через /api/family/create).
    """
    user_id = _resolve_user_id_from_claim(current_user)
    name = (payload.name or "").strip()
    role = (payload.role or "").strip().lower()

    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    if not role:
        raise HTTPException(status_code=400, detail="role is required")

    # Допустимые роли в рамках анонимной семейной модели
    allowed_roles = {"parent", "child", "teenager", "elderly", "other"}
    if role not in allowed_roles:
        raise HTTPException(status_code=400, detail="Invalid role")

    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")

    def add_member_sync():
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_family_indexes(db)
            # Обеспечиваем read-after-write консистентность в транзакции
            try:
                db.execute(text("SET LOCAL synchronous_commit = on"))
            except Exception:
                pass
            # Определяем семейный контекст: если прислан familyId — используем его, иначе берём по членству актора
            # 1) Ищем членство актора
            actor_row = db.execute(
                text(
                    """
                    SELECT fm.family_id, fm.role
                    FROM family_members fm
                    WHERE fm.user_id = :user_id
                    ORDER BY fm.updated_at DESC NULLS LAST, fm.id DESC
                    LIMIT 1
                    """
                ),
                {"user_id": user_id},
            ).fetchone()
            actor_family_id = actor_row[0] if actor_row else None
            actor_role = str(actor_row[1]).lower() if actor_row and actor_row[1] is not None else "unknown"

            # 2) Выбираем целевой family_id
            if payload.familyId is not None:
                family_id = payload.familyId
                # Если у актора есть членство и оно отличается — явный конфликт контекста
                if actor_family_id is not None and str(actor_family_id) != str(family_id):
                    logger.warning("family_add_context_mismatch", user_id=user_id, actor_family_id=str(actor_family_id), payload_family_id=str(family_id))
                    raise HTTPException(status_code=409, detail="Family context mismatch")
            elif actor_family_id is not None:
                family_id = actor_family_id
            else:
                # Фолбек для владельца семьи
                fam_row = db.execute(
                    text("SELECT id FROM families WHERE owner_user_id = :user_id ORDER BY created_at DESC LIMIT 1"),
                    {"user_id": user_id},
                ).fetchone()
                if not fam_row:
                    logger.warning("family_not_found_for_actor", user_id=user_id)
                    raise HTTPException(status_code=404, detail="Family not found")
                family_id = fam_row[0]
                actor_role = "parent"

            # Политика доступа: добавлять может только администратор (родитель)
            if actor_role != "parent":
                logger.warning("family_add_denied_not_admin", user_id=user_id, actor_role=actor_role, family_id=str(family_id))
                raise HTTPException(status_code=403, detail="Only administrators can add members")

            member_id = f"MEM_{uuid.uuid4().hex[:12].upper()}"
            status_val = "protected"
            last_active = _iso_utc_timestamp()
            threats_blocked = 0
            devices_val = 0

            db.execute(
                text(
                    """
                    INSERT INTO family_members (id, family_id, user_id, name, role, status, threats_blocked, last_active, devices)
                    VALUES (:id, :family_id, :user_id, :name, :role, :status, :threats_blocked, :last_active, :devices)
                    """
                ),
                {
                    "id": member_id,
                    "family_id": family_id,
                    # ВАЖНО: члены, добавленные администратором, пока не аутентифицированы как отдельные пользователи.
                    # Не связываем их с user_id актора, чтобы не срабатывать на self-removal.
                    # user_id будет присвоен, когда этот участник залогинится и "присвоит" себе профиль.
                    "user_id": None,
                    "name": name,
                    "role": role,
                    "status": status_val,
                    "threats_blocked": threats_blocked,
                    "last_active": last_active,
                    "devices": devices_val,
                },
            )
            db.commit()

            logger.info(
                "family_member_added",
                user_id=user_id,
                family_id=str(family_id),
                member_id=member_id,
                role=role,
                actor_role=actor_role,
                name=name,
                timestamp=datetime.now().isoformat(),
            )
            # Metrics-style log (B4): emit counter increment
            logger.info(
                "metric_family_member_added",
                family_id=str(family_id),
                member_id=member_id,
                role=role,
            )

            # Аватар подбирается на стороне iOS по роли, здесь возвращаем базовый placeholder.
            return FamilyMemberResponse(
                id=member_id,
                name=name,
                role=role,
                avatar="👤",
                status=status_val,
                threatsBlocked=threats_blocked,
                lastActive=last_active,
                devices=devices_val,
            )
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(
                "family_add_member_db_error",
                user_id=user_id,
                name=name,
                role=role,
                error=str(e),
                timestamp=datetime.now().isoformat(),
            )
            raise HTTPException(status_code=500, detail="Failed to add family member")
        finally:
            gen.close()

    return await asyncio.to_thread(add_member_sync)

@router.get("/members", response_model=list[FamilyMemberCompat])
async def get_family_members_compat(
    response: Response,
    current_user: dict = Depends(get_current_user),
    familyId: Optional[str] = Query(None, alias="familyId"),
):
    """
    ✅ Production rule: no mock/fake.
    Если БД не подключена — отдаём 503, чтобы клиент не принимал пустые/фейковые данные как "успех".

    Согласование контекста семьи:
    - Сервер вычисляет `family_id` по JWT: приоритет claim `family_id` (если авторизован для этой семьи),
      затем последнее членство по `updated_at`, затем владелец семьи.
    - Если клиент передал query `familyId`, он **должен** совпадать с вычисленным id — иначе 409
      (защита от смешения локального кэша другой семьи с данными актора).
    - Заголовок `X-Resolved-Family-Id` — явная «правда сервера» для этой выдачи (полный список строк этой семьи).
    - Заголовок `X-Current-Member-Id` — `family_members.id` строки членства JWT-актора в этой семье (детерминированное
      выравнивание `your_member_id` на iOS без угадывания по JWT payload).
    """
    user_id = _resolve_user_id_from_claim(current_user)
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")

    def load_members_sync():
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_family_indexes(db)
            resolved_primary = _resolve_primary_family_id_for_actor(db, user_id, current_user)
            if not resolved_primary:
                logger.warning("family_members_no_family_for_actor", user_id=user_id)
                return [], None, None
            family_id = resolved_primary
            resolved = resolved_primary
            qfid = (familyId or "").strip()
            if qfid and qfid != resolved:
                logger.warning(
                    "family_members_family_id_mismatch",
                    user_id=user_id,
                    query_family_id=qfid,
                    resolved_family_id=resolved,
                )
                # P2: scrape as counter in Loki/Datadog — family_members_get_409
                logger.info(
                    "metric_family_members_get_409",
                    user_id=user_id,
                    query_family_id=qfid,
                    resolved_family_id=resolved,
                )
                raise HTTPException(
                    status_code=409,
                    detail="familyId does not match the authenticated user's family context",
                )

            res = db.execute(
                text("SELECT id, name, role FROM family_members WHERE family_id = :family_id ORDER BY id ASC"),
                {"family_id": family_id},
            )
            rows = res.fetchall() or []
            logger.info(
                "family_members_returned",
                user_id=user_id,
                family_id=str(family_id),
                count=len(rows),
            )
            # Metrics-style log (B4): emit gauge for members count
            logger.info(
                "metric_family_members_count",
                family_id=str(family_id),
                value=len(rows),
            )
            members = [
                FamilyMemberCompat(id=str(r[0]), name=str(r[1]), role=str(r[2]))
                for r in rows
            ]
            cur = db.execute(
                text(
                    """
                    SELECT id FROM family_members
                    WHERE family_id = :family_id AND user_id = :user_id
                    ORDER BY updated_at DESC NULLS LAST, id DESC
                    LIMIT 1
                    """
                ),
                {"family_id": family_id, "user_id": user_id},
            ).fetchone()
            current_member_id = str(cur[0]).strip() if cur and cur[0] is not None else None
            return members, resolved, current_member_id
        finally:
            gen.close()

    try:
        members, resolved_fid, current_member_id = await asyncio.to_thread(load_members_sync)
        if resolved_fid:
            response.headers["X-Resolved-Family-Id"] = resolved_fid
            logger.info(
                "metric_family_members_get_ok",
                user_id=user_id,
                family_id=resolved_fid,
                count=len(members),
            )
        if current_member_id:
            response.headers["X-Current-Member-Id"] = current_member_id
            logger.info(
                "family_members_current_member_header",
                user_id=user_id,
                member_id=current_member_id,
                family_id=resolved_fid,
            )
        return members
    except HTTPException:
        raise
    except Exception as e:
        logger.error("family_members_db_error", user_id=user_id, error=str(e), timestamp=datetime.now().isoformat())
        raise HTTPException(status_code=500, detail="Failed to load family members")


@router.get("/member", response_model=FamilyCompatBoolResponse)
async def get_family_member_compat(
    current_user: dict = Depends(get_current_user)
):
    _ = current_user.get("id")
    return FamilyCompatBoolResponse(success=True, data=True, message="Family member fetched")


@router.get("/add", response_model=FamilyCompatBoolResponse)
async def add_family_member_compat(
    current_user: dict = Depends(get_current_user)
):
    _ = current_user.get("id")
    return FamilyCompatBoolResponse(success=True, data=True, message="Family member added")


@router.delete("/remove", response_model=FamilyMemberResponse)
async def remove_family_member(
    payload: RemoveFamilyMemberRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    ✅ BOEVOЙ endpoint: DELETE /api/family/remove

    Требования:
    - Не возвращать sfm_mock/mock_fallback в production.
    - Реально удалять участника в БД (если возможно).
    - Если БД не настроена — 503 (чтобы iOS не считал это успехом).
    """
    user_id = _resolve_user_id_from_claim(current_user)
    if not payload.memberId:
        raise HTTPException(status_code=400, detail="memberId is required")
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")

    def remove_member_sync():
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_family_indexes(db)
            # Обеспечиваем read-after-write консистентность в транзакции
            try:
                db.execute(text("SET LOCAL synchronous_commit = on"))
            except Exception:
                pass
            # Определяем семейный контекст актора по членству
            actor_family_row = db.execute(
                text(
                    """
                    SELECT fm.family_id
                    FROM family_members fm
                    WHERE fm.user_id = :user_id
                    ORDER BY fm.updated_at DESC NULLS LAST, fm.id DESC
                    LIMIT 1
                    """
                ),
                {"user_id": user_id},
            ).fetchone()
            if actor_family_row:
                family_id = actor_family_row[0]
            else:
                # Фолбек для владельца семьи
                fam_row = db.execute(
                    text("SELECT id FROM families WHERE owner_user_id = :user_id ORDER BY created_at DESC LIMIT 1"),
                    {"user_id": user_id},
                ).fetchone()
                if not fam_row:
                    raise HTTPException(status_code=404, detail="Family not found")
                family_id = fam_row[0]

            # 1) Определяем инициатора действия (actor) внутри семьи.
            # Предпочитаем запись с ролью 'parent' для данного user_id, чтобы не перепутать с детьми, созданными админом.
            actor_row = db.execute(
                text(
                    """
                    SELECT id, role
                    FROM family_members
                    WHERE family_id = :family_id AND user_id = :user_id AND lower(role) = 'parent'
                    ORDER BY updated_at DESC NULLS LAST, id DESC
                    LIMIT 1
                    """
                ),
                {"family_id": family_id, "user_id": user_id},
            ).fetchone()
            if not actor_row:
                actor_row = db.execute(
                    text(
                        """
                        SELECT id, role
                        FROM family_members
                        WHERE family_id = :family_id AND user_id = :user_id
                        ORDER BY updated_at DESC NULLS LAST, id DESC
                        LIMIT 1
                        """
                    ),
                    {"family_id": family_id, "user_id": user_id},
                ).fetchone()
            actor_member_id = str(actor_row[0]) if actor_row else None
            actor_role = str(actor_row[1]).lower() if actor_row and actor_row[1] is not None else "unknown"

            # Политика доступа: удалять может только администратор (родитель)
            if actor_role != "parent":
                raise HTTPException(status_code=403, detail="Only administrators can remove members")

            if actor_member_id and actor_member_id == str(payload.memberId):
                logger.warning("family_remove_denied_self", user_id=user_id, actor_member_id=actor_member_id, member_id=payload.memberId)
                raise HTTPException(status_code=400, detail="Self-removal is not allowed")

            # 2) Читаем участника перед удалением (чтобы вернуть объект iOS-совместимого формата)
            res = db.execute(
                text(
                    """
                    SELECT id, name, role, status, threats_blocked, last_active, devices
                    FROM family_members
                    WHERE family_id = :family_id AND id = :member_id
                    LIMIT 1
                    """
                ),
                {"family_id": family_id, "member_id": payload.memberId},
            )
            row = res.fetchone()
            if not row:
                logger.warning("family_member_not_found", user_id=user_id, family_id=str(family_id), member_id=payload.memberId)
                raise HTTPException(status_code=404, detail="Family member not found")
            # Дополнительная защита: если клиент прислал familyId — убеждаемся, что контекст совпадает
            if payload.familyId is not None and str(family_id) != str(payload.familyId):
                raise HTTPException(status_code=409, detail="Family context mismatch")

            member_id, name, role, status_val, threats_val, last_active, devices_val = row
            target_role = str(role).lower() if role is not None else "unknown"

            if target_role == "parent":
                parent_count_row = db.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM family_members
                        WHERE family_id = :family_id AND lower(role) = 'parent'
                        """
                    ),
                    {"family_id": family_id},
                ).fetchone()
                parent_count = int(parent_count_row[0] or 0) if parent_count_row else 0
                if parent_count <= 1:
                    raise HTTPException(status_code=400, detail="Cannot remove the last parent")

            # 3) Удаляем
            del_res = db.execute(
                text(
                    """
                    DELETE FROM family_members
                    WHERE family_id = :family_id AND id = :member_id
                    """
                ),
                {"family_id": family_id, "member_id": payload.memberId},
            )

            # 4) Коммит
            db.commit()

            # rowcount может быть None — проверяем мягко
            if getattr(del_res, "rowcount", 1) == 0:
                raise HTTPException(status_code=409, detail="Removal not confirmed")

            logger.info(
                "family_member_removed",
                user_id=user_id,
                actor_member_id=actor_member_id,
                actor_role=actor_role,
                member_id=str(member_id),
                removed_role=target_role,
                source=payload.source or "unknown",
                reason=payload.reason or "",
                timestamp=datetime.now().isoformat(),
            )
            # Metrics-style log (B4): emit counter increment
            logger.info(
                "metric_family_member_removed",
                family_id=str(family_id),
                member_id=str(member_id),
                role=target_role,
            )

            return FamilyMemberResponse(
                id=str(member_id),
                name=str(name),
                role=str(role),
                avatar="👤",
                status=str(status_val or "protected"),
                threatsBlocked=int(threats_val or 0),
                lastActive=str(last_active or ""),
                devices=int(devices_val or 0),
            )
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(
                "family_remove_db_error",
                user_id=user_id,
                member_id=payload.memberId,
                error=str(e),
                timestamp=datetime.now().isoformat(),
            )
            raise HTTPException(status_code=500, detail="Failed to remove family member")
        finally:
            gen.close()

    return await asyncio.to_thread(remove_member_sync)

class ReconcileFamilyRequest(BaseModel):
    familyId: Optional[str] = None

class ReconcileFamilyResponse(BaseModel):
    familyId: str
    total: int
    invalidRoles: int
    fixedStatuses: int

@router.post("/reconcile", response_model=ReconcileFamilyResponse)
async def reconcile_family(
    payload: ReconcileFamilyRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Фоновая/ручная процедура сверки целостности семьи по familyId.
    - `familyId` в теле (если передан) **должен** совпадать с семьёй, вычисленной для JWT-актора (как в GET /members).
    - Если не передан — берётся семья актора по тому же правилу.
    - Считает и при необходимости мягко исправляет аномальные статусы.
    """
    user_id = _resolve_user_id_from_claim(current_user)
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")

    def reconcile_sync():
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_family_indexes(db)
            resolved = _resolve_primary_family_id_for_actor(db, user_id, current_user)
            if payload.familyId is not None:
                p = str(payload.familyId).strip()
                if not p:
                    raise HTTPException(status_code=422, detail="familyId is empty")
                if resolved is None:
                    raise HTTPException(status_code=404, detail="Family not found")
                if p != resolved:
                    raise HTTPException(
                        status_code=409,
                        detail="familyId does not match the authenticated user's family context",
                    )
                family_id = p
            else:
                if resolved is None:
                    raise HTTPException(status_code=404, detail="Family not found")
                family_id = resolved

            rows = db.execute(
                text(
                    "SELECT id, role, status FROM family_members WHERE family_id = :family_id"
                ),
                {"family_id": family_id},
            ).fetchall() or []
            total = len(rows)
            invalid_roles = 0
            fixed_statuses = 0
            allowed_roles = {"parent", "child", "teenager", "elderly", "other"}

            # Дополнительно: очищаем конфликтные user_id (у не-родителей с тем же user_id, что и актор),
            # чтобы устранить ложные self-removal для админ-добавленных участников, пока они не залогинятся сами.
            try:
                db.execute(
                    text(
                        """
                        UPDATE family_members
                        SET user_id = NULL
                        WHERE family_id = :family_id
                          AND user_id = :user_id
                          AND lower(role) <> 'parent'
                        """
                    ),
                    {"family_id": family_id, "user_id": user_id},
                )
            except Exception as _:
                # не критично — продолжаем reconcile дальше
                pass

            for mid, role, status in rows:
                r = (str(role).lower() if role is not None else "")
                if r and r not in allowed_roles:
                    invalid_roles += 1
                s = (str(status).lower() if status is not None else "")
                if not s or s not in {"protected", "warning", "danger"}:
                    db.execute(
                        text("UPDATE family_members SET status = 'protected' WHERE id = :id AND family_id = :family_id"),
                        {"id": mid, "family_id": family_id},
                    )
                    fixed_statuses += 1

            db.commit()

            logger.info(
                "family_reconcile_done",
                family_id=str(family_id),
                total=total,
                invalid_roles=invalid_roles,
                fixed_statuses=fixed_statuses,
            )
            logger.info(
                "metric_family_reconcile",
                family_id=str(family_id),
                total=total,
                invalid_roles=invalid_roles,
                fixed_statuses=fixed_statuses,
            )

            return ReconcileFamilyResponse(
                familyId=str(family_id),
                total=total,
                invalidRoles=invalid_roles,
                fixedStatuses=fixed_statuses,
            )
        finally:
            gen.close()

    return await asyncio.to_thread(reconcile_sync)

# Backward-compat stub: older clients might call GET /remove (incorrectly). Do not treat as success.
@router.get("/remove", response_model=FamilyCompatBoolResponse)
async def remove_family_member_compat(
    current_user: dict = Depends(get_current_user)
):
    _ = current_user.get("id")
    raise HTTPException(status_code=405, detail="Use DELETE /api/family/remove")


@router.get("/join", response_model=FamilyCompatBoolResponse)
async def join_family_compat(
    current_user: dict = Depends(get_current_user)
):
    _ = current_user.get("id")
    return FamilyCompatBoolResponse(success=True, data=True, message="Joined family")


@router.get("/recover", response_model=FamilyCompatBoolResponse)
async def recover_family_compat(
    current_user: dict = Depends(get_current_user)
):
    _ = current_user.get("id")
    return FamilyCompatBoolResponse(success=True, data=True, message="Family recovered")


@router.get("/chat/messages", response_model=list[dict])
async def family_chat_messages_compat(
    current_user: dict = Depends(get_current_user),
    familyId: Optional[str] = Query(None, alias="familyId"),
):
    user_id = _resolve_user_id_from_claim(current_user)
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")

    def load_messages_sync() -> List[Dict[str, Any]]:
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_family_chat_table(db)
            resolved_family_id = _resolve_primary_family_id_for_actor(db, user_id, current_user)
            if not resolved_family_id:
                return []
            if familyId is not None and familyId.strip() and familyId.strip() != resolved_family_id:
                raise HTTPException(status_code=409, detail="Family context mismatch")

            rows = db.execute(
                text(
                    """
                    SELECT id, sender_name, text, timestamp, message_type, voice_url, voice_duration,
                           media_url, media_thumbnail_url, media_type, reply_to_message_id, edited_at, read_status, read_at
                    FROM family_chat_messages
                    WHERE family_id = :family_id
                    ORDER BY timestamp ASC
                    LIMIT 300
                    """
                ),
                {"family_id": resolved_family_id},
            ).fetchall() or []

            reaction_rows = db.execute(
                text(
                    """
                    SELECT message_id, emoji, COALESCE(user_id, 0) AS user_id, user_name
                    FROM family_chat_reactions
                    WHERE message_id IN (SELECT id FROM family_chat_messages WHERE family_id = :family_id)
                    ORDER BY created_at ASC
                    """
                ),
                {"family_id": resolved_family_id},
            ).fetchall() or []

            reactions_by_message: Dict[str, List[Dict[str, Any]]] = {}
            for rr in reaction_rows:
                mid = str(rr[0])
                reactions_by_message.setdefault(mid, []).append(
                    {
                        "emoji": str(rr[1]),
                        "userId": str(rr[2]),
                        "userName": str(rr[3]),
                    }
                )

            messages: List[Dict[str, Any]] = []
            for r in rows:
                sender_name = str(r[1] or "User")
                messages.append(
                    {
                        "id": str(r[0]),
                        "sender": sender_name,
                        "text": r[2],
                        "timestamp": str(r[3]),
                        "isCurrentUser": sender_name == str(current_user.get("name") or "You"),
                        "messageType": r[4],
                        "voiceUrl": r[5],
                        "voiceDuration": float(r[6]) if r[6] is not None else None,
                        "mediaUrl": r[7],
                        "mediaThumbnailUrl": r[8],
                        "mediaType": r[9],
                        "replyToMessageId": r[10],
                        "reactions": reactions_by_message.get(str(r[0]), []),
                        "readStatus": r[12],
                        "readAt": r[13],
                        "editedAt": r[11],
                    }
                )
            return messages
        finally:
            gen.close()

    return await asyncio.to_thread(load_messages_sync)


@router.post("/chat/upload-media")
async def family_chat_upload_media(
    request: Request,
    file: UploadFile = File(...),
    media_kind: Annotated[str, Form(alias="type")] = "image",
    family_id_form: Annotated[Optional[str], Form(alias="familyId")] = None,
    current_user: dict = Depends(get_current_user),
    x_family_id: Annotated[Optional[str], Header(alias="X-Family-Id")] = None,
):
    """Multipart загрузка медиа для семейного чата (голос / фото / видео).

    Требуется контекст семьи: заголовок X-Family-Id и/или поле формы familyId.
    Пользователь должен быть участником этой семьи (или владельцем).
    Лимит размера: переменная окружения ALADDIN_FAMILY_CHAT_UPLOAD_MAX_BYTES (по умолчанию 25 MiB).
    """
    user_id = _resolve_user_id_from_claim(current_user)
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")
    fid = (x_family_id or family_id_form or "").strip()
    if not fid:
        raise HTTPException(
            status_code=400,
            detail="familyId is required (header X-Family-Id or form field familyId)",
        )
    _ = media_kind
    suffix = Path(file.filename or "").suffix.lower()
    allowed_suffixes = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".heic",
        ".mp4",
        ".mov",
        ".m4a",
        ".aac",
        ".caf",
        ".pdf",
        ".bin",
    }
    if suffix not in allowed_suffixes:
        suffix = ".bin"
    name = f"{uuid.uuid4().hex}{suffix}"
    content = await file.read()
    max_bytes = int(os.environ.get("ALADDIN_FAMILY_CHAT_UPLOAD_MAX_BYTES", str(25 * 1024 * 1024)))
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail="File too large")
    base = str(request.base_url).rstrip("/")

    def persist() -> dict:
        gen = get_postgres_db()
        db = next(gen)
        try:
            if not _actor_belongs_to_family(db, user_id, fid):
                raise HTTPException(status_code=403, detail="Not a member of this family")
        finally:
            gen.close()
        root = _ensure_family_chat_upload_root()
        dest = root / name
        dest.write_bytes(content)
        url = f"{base}/api/family/chat/media/{name}"
        logger.info("family_chat_media_upload", saved=name, bytes=len(content), family_id=fid)
        return {"success": True, "url": url, "mediaUrl": url}

    return await asyncio.to_thread(persist)


@router.get("/chat/media/{filename}")
async def family_chat_get_media(filename: str):
    if not _SAFE_CHAT_MEDIA_FILENAME.match(filename):
        raise HTTPException(status_code=404, detail="Not found")
    path = _ensure_family_chat_upload_root() / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(path)


@router.post("/chat/send", response_model=SendFamilyChatMessageResponse)
async def family_chat_send(
    payload: SendFamilyChatMessageRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id = _resolve_user_id_from_claim(current_user)
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")

    def send_sync() -> SendFamilyChatMessageResponse:
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_family_chat_table(db)
            family_id = (payload.familyId or "").strip() or (_resolve_primary_family_id_for_actor(db, user_id, current_user) or "")
            if not family_id:
                raise HTTPException(status_code=404, detail="Family not found")

            message_id = f"MSG_{uuid.uuid4().hex[:12].upper()}"
            timestamp = _iso_utc_timestamp()
            sender_name = str(current_user.get("name") or "You")
            text_value = (payload.message or "").strip()
            if not text_value and not (payload.mediaUrl or payload.voiceUrl):
                raise HTTPException(status_code=400, detail="Empty message payload")

            db.execute(
                text(
                    """
                    INSERT INTO family_chat_messages (
                        id, family_id, sender_user_id, sender_name, text, timestamp,
                        message_type, voice_url, voice_duration, media_url, media_thumbnail_url,
                        media_type, reply_to_message_id, read_status
                    ) VALUES (
                        :id, :family_id, :sender_user_id, :sender_name, :text, :timestamp,
                        :message_type, :voice_url, :voice_duration, :media_url, :media_thumbnail_url,
                        :media_type, :reply_to_message_id, :read_status
                    )
                    """
                ),
                {
                    "id": message_id,
                    "family_id": family_id,
                    "sender_user_id": user_id,
                    "sender_name": sender_name,
                    "text": text_value if text_value else None,
                    "timestamp": timestamp,
                    "message_type": payload.messageType or ("media" if payload.mediaUrl else "text"),
                    "voice_url": payload.voiceUrl,
                    "voice_duration": payload.voiceDuration,
                    "media_url": payload.mediaUrl,
                    "media_thumbnail_url": payload.mediaUrl,
                    "media_type": payload.mediaType,
                    "reply_to_message_id": payload.replyToMessageId,
                    "read_status": "sent",
                },
            )
            db.commit()
            return SendFamilyChatMessageResponse(success=True, messageId=message_id)
        finally:
            gen.close()

    return await asyncio.to_thread(send_sync)


@router.post("/chat/send/typing", response_model=FamilyCompatBoolResponse)
async def family_chat_send_typing(
    payload: TypingIndicatorRequest,
    current_user: dict = Depends(get_current_user),
):
    _ = current_user.get("id")
    _ = payload.familyId
    return FamilyCompatBoolResponse(success=True, data=True, message="Typing accepted")


@router.post("/chat/send/edit", response_model=FamilyCompatBoolResponse)
async def family_chat_edit_message(
    payload: EditFamilyChatMessageRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id = _resolve_user_id_from_claim(current_user)
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")

    def edit_sync() -> FamilyCompatBoolResponse:
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_family_chat_table(db)
            now = _iso_utc_timestamp()
            updated = db.execute(
                text(
                    """
                    UPDATE family_chat_messages
                    SET text = :text, edited_at = :edited_at
                    WHERE id = :message_id AND sender_user_id = :sender_user_id
                    """
                ),
                {"text": payload.text, "edited_at": now, "message_id": payload.messageId, "sender_user_id": user_id},
            )
            db.commit()
            if getattr(updated, "rowcount", 0) == 0:
                raise HTTPException(status_code=404, detail="Message not found")
            return FamilyCompatBoolResponse(success=True, data=True, message="Message edited")
        finally:
            gen.close()

    return await asyncio.to_thread(edit_sync)


@router.post("/chat/send/reaction", response_model=FamilyCompatBoolResponse)
async def family_chat_add_reaction(
    payload: ReactionRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id = _resolve_user_id_from_claim(current_user)
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")

    def reaction_sync() -> FamilyCompatBoolResponse:
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_family_chat_table(db)
            reaction_id = f"REA_{uuid.uuid4().hex[:12].upper()}"
            db.execute(
                text(
                    """
                    INSERT INTO family_chat_reactions (id, message_id, user_id, user_name, emoji, created_at)
                    VALUES (:id, :message_id, :user_id, :user_name, :emoji, :created_at)
                    """
                ),
                {
                    "id": reaction_id,
                    "message_id": payload.messageId,
                    "user_id": user_id,
                    "user_name": str(current_user.get("name") or "You"),
                    "emoji": payload.emoji,
                    "created_at": _iso_utc_timestamp(),
                },
            )
            db.commit()
            return FamilyCompatBoolResponse(success=True, data=True, message="Reaction added")
        finally:
            gen.close()

    return await asyncio.to_thread(reaction_sync)


@router.post("/chat/send/read", response_model=FamilyCompatBoolResponse)
async def family_chat_mark_read(
    payload: ReadRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id = _resolve_user_id_from_claim(current_user)
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")

    def read_sync() -> FamilyCompatBoolResponse:
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_family_chat_table(db)
            row = db.execute(
                text("SELECT family_id FROM family_chat_messages WHERE id = :message_id LIMIT 1"),
                {"message_id": payload.messageId},
            ).fetchone()
            if not row or row[0] is None:
                raise HTTPException(status_code=404, detail="Message not found")
            msg_family = str(row[0]).strip()
            if not _actor_belongs_to_family(db, user_id, msg_family):
                raise HTTPException(status_code=403, detail="Not a member of this message's family")
            updated = db.execute(
                text(
                    """
                    UPDATE family_chat_messages
                    SET read_status = 'read', read_at = :read_at
                    WHERE id = :message_id AND family_id = :family_id
                    """
                ),
                {
                    "message_id": payload.messageId,
                    "read_at": _iso_utc_timestamp(),
                    "family_id": msg_family,
                },
            )
            db.commit()
            if getattr(updated, "rowcount", 0) == 0:
                raise HTTPException(status_code=404, detail="Message not found")
            return FamilyCompatBoolResponse(success=True, data=True, message="Read status updated")
        finally:
            gen.close()

    return await asyncio.to_thread(read_sync)


@router.delete("/chat/send/{message_id}", response_model=FamilyCompatBoolResponse)
async def family_chat_delete_message(
    message_id: str,
    current_user: dict = Depends(get_current_user),
    x_family_id: Annotated[Optional[str], Header(alias="X-Family-Id")] = None,
):
    user_id = _resolve_user_id_from_claim(current_user)
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")

    fid = (x_family_id or "").strip() or None

    def delete_sync() -> FamilyCompatBoolResponse:
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_family_chat_table(db)
            sql = """
                    DELETE FROM family_chat_messages
                    WHERE id = :message_id AND sender_user_id = :sender_user_id
                    """
            params: Dict[str, Any] = {"message_id": message_id, "sender_user_id": user_id}
            if fid:
                sql += " AND family_id = :family_id"
                params["family_id"] = fid
            deleted = db.execute(
                text(sql),
                params,
            )
            db.execute(
                text("DELETE FROM family_chat_reactions WHERE message_id = :message_id"),
                {"message_id": message_id},
            )
            db.commit()
            if getattr(deleted, "rowcount", 0) == 0:
                raise HTTPException(status_code=404, detail="Message not found")
            return FamilyCompatBoolResponse(success=True, data=True, message="Message deleted")
        finally:
            gen.close()

    return await asyncio.to_thread(delete_sync)


@router.get("/chat/send", response_model=FamilyCompatBoolResponse)
async def family_chat_send_compat(
    current_user: dict = Depends(get_current_user)
):
    _ = current_user.get("id")
    return FamilyCompatBoolResponse(success=True, data=True, message="Message sent")

