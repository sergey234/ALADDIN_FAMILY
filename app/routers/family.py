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
from typing import Optional, Any, Dict, List, Tuple, Annotated
from datetime import datetime
import uuid
from pydantic import BaseModel

# ✅ Импорт функции создания семьи (БЕЗ персональных данных)
from security.family.family_registration import create_family

# ✅ Авторизация с реальным user_id
from app.auth.auth import get_current_user
from app.routers.family_chat_v2_helpers import (
    ensure_chat_v2_columns,
    build_send_insert_params,
    INSERT_MESSAGE_SQL,
    SELECT_MESSAGES_SQL,
    row_to_api_message,
)
from app.routers.family_chat_v2_pure import build_ws_new_message_payload
from app.services.family_chat_realtime import family_ws_manager

try:
    from app.database.database import get_db as get_postgres_db
except ImportError:
    get_postgres_db = None

try:
    from app.services.family_roster_reconcile import (
        reconcile_sole_child_roster_for_owner,
        max_family_slots_for_subscription_level,
    )
except ImportError:
    reconcile_sole_child_roster_for_owner = None  # type: ignore[misc, assignment]

    def max_family_slots_for_subscription_level(level: Optional[str]) -> int:  # type: ignore[misc]
        return 1

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
_SAFE_CHAT_MEDIA_FILENAME = re.compile(r"^[a-f0-9]{32}\.(?:enc|[A-Za-z0-9]{1,12})$")


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
_PG_INT_MAX = 2_147_483_647


def _lookup_or_create_user_id_for_device(db, device_id: str, device_type: Optional[str] = None) -> Optional[int]:
    """Map device_id → users.id; create row if missing (legacy oversized pseudo JWT subjects)."""
    device_id = device_id.strip()
    if not device_id:
        return None
    row = db.execute(
        text("SELECT id FROM users WHERE device_id = :device_id ORDER BY id DESC LIMIT 1"),
        {"device_id": device_id},
    ).fetchone()
    if row and row[0] is not None:
        return int(row[0])
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
    return int(inserted[0]) if inserted and inserted[0] is not None else None


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

    # Device JWT: always prefer users.device_id → users.id (hash pseudo-ids overflow PG INTEGER).
    claim_device_id = current_user.get("device_id")
    if isinstance(claim_device_id, str) and claim_device_id.strip() and get_postgres_db:
        gen = get_postgres_db()
        db = next(gen)
        try:
            resolved = _lookup_or_create_user_id_for_device(
                db,
                claim_device_id,
                current_user.get("device_type") if isinstance(current_user.get("device_type"), str) else None,
            )
            if resolved is not None:
                return resolved
        finally:
            gen.close()

    if isinstance(raw_id, int):
        if raw_id > _PG_INT_MAX:
            raise HTTPException(status_code=401, detail="Invalid user_id in token")
        return raw_id
    if isinstance(raw_id, str) and raw_id.strip().isdigit():
        parsed = int(raw_id.strip())
        if parsed > _PG_INT_MAX:
            raise HTTPException(status_code=401, detail="Invalid user_id in token")
        return parsed

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


def _actor_can_manage_family_roster(db, user_id: int, family_id: str) -> bool:
    """
    Who may add/remove roster rows for this family.

    - Owner (`families.owner_user_id`) for `family_id`, even without a `family_members` row.
    - Or a `parent` row in `family_members` for this `family_id` and `user_id`.
    """
    fid = str(family_id or "").strip()
    if not fid:
        return False
    o = db.execute(
        text("SELECT 1 FROM families WHERE id = :fid AND owner_user_id = :uid LIMIT 1"),
        {"fid": fid, "uid": user_id},
    ).fetchone()
    if o:
        return True
    p = db.execute(
        text(
            """
            SELECT 1 FROM family_members
            WHERE family_id = :fid AND user_id = :uid AND lower(trim(role)) = 'parent'
            LIMIT 1
            """
        ),
        {"fid": fid, "uid": user_id},
    ).fetchone()
    return bool(p)


def _normalize_client_family_id(raw: Optional[str]) -> str:
    """
    Приводит family_id от клиента (FAM-…, FAM_…, FAM…) к канону `FAM_` + 12 hex,
    как в генераторе create_family / extractFamilyID на iOS.
    """
    s = (raw or "").strip().upper()
    if not s:
        return ""
    alnum = re.sub(r"[^A-Z0-9]", "", s)
    if not alnum.startswith("FAM"):
        return s
    body = alnum[3:]
    if len(body) < 12:
        return ""
    return "FAM_" + body[:12]


def _owner_subscription_level_for_family(db, family_id: str) -> str:
    row = db.execute(
        text(
            """
            SELECT COALESCE(
                NULLIF(lower(trim(u.subscription_level)), ''),
                NULLIF(lower(trim(s.level)), ''),
                'free'
            )
            FROM families f
            LEFT JOIN users u ON u.id = f.owner_user_id
            LEFT JOIN LATERAL (
                SELECT level
                FROM subscriptions
                WHERE user_id = f.owner_user_id::text
                ORDER BY updated_at DESC NULLS LAST, id DESC
                LIMIT 1
            ) s ON TRUE
            WHERE f.id = :fid
            LIMIT 1
            """
        ),
        {"fid": str(family_id)},
    ).fetchone()
    return str(row[0]) if row and row[0] is not None else "free"


def _actor_subscription_level(db, user_id: int) -> str:
    row = db.execute(
        text(
            """
            SELECT COALESCE(subscription_level, 'free')
            FROM users
            WHERE id = :uid
            LIMIT 1
            """
        ),
        {"uid": int(user_id)},
    ).fetchone()
    if not row or row[0] is None:
        return "free"
    return str(row[0]).strip().lower() or "free"


def _count_family_members(db, family_id: str) -> int:
    row = db.execute(
        text("SELECT COUNT(*) FROM family_members WHERE family_id = :fid"),
        {"fid": str(family_id)},
    ).fetchone()
    return int(row[0] or 0) if row else 0


def _acquire_family_roster_write_lock(db, family_id: str) -> None:
    """
    Сериализует конкурентные add/join операции в рамках одной семьи.
    Это закрывает race окно между COUNT(*) и INSERT.
    """
    lock_key = f"family_roster:{str(family_id)}"
    try:
        db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:k, 0))"), {"k": lock_key})
        return
    except Exception:
        # Совместимость с кластерами/версиями без hashtextextended.
        try:
            db.execute(text("SELECT pg_advisory_xact_lock(abs(hashtext(:k)))"), {"k": lock_key})
            return
        except Exception as e:
            logger.error(
                "family_roster_lock_failed",
                family_id=str(family_id),
                lock_key=lock_key,
                error=str(e),
            )
            # Fail-closed: если lock не взяли, не выполняем write path.
            raise HTTPException(status_code=503, detail="family_roster_lock_unavailable")


def _fetch_family_member_rows(db, family_id: str) -> List[Any]:
    res = db.execute(
        text(
            """
            SELECT id, name, role, status, threats_blocked, last_active, devices
            FROM family_members
            WHERE family_id = :family_id
            ORDER BY id ASC
            """
        ),
        {"family_id": str(family_id)},
    )
    return list(res.fetchall() or [])


def _resolve_effective_family_id_for_chat(
    db,
    user_id: int,
    current_user: dict,
    requested_family_id: Optional[str],
) -> Optional[str]:
    """Единый выбор семьи для чата: как GET /chat/messages — query/body учитывается только при членстве."""
    family_query = (requested_family_id or "").strip() or None
    effective: Optional[str] = None
    if family_query and _actor_belongs_to_family(db, user_id, family_query):
        effective = family_query
    if not effective:
        effective = _resolve_primary_family_id_for_actor(db, user_id, current_user)
    return effective


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
    # Roster cap aligned with POST /api/family/add (owner `users.subscription_level` + max_family_slots_for_subscription_level).
    familyRosterUsed: int = 0
    familyRosterMax: int = 0
    ownerSubscriptionTier: str = "free"


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
                familyStatusMessage=family_status_message,
                familyRosterUsed=0,
                familyRosterMax=0,
                ownerSubscriptionTier="free",
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
    response: Response,
    x_family_id: Annotated[Optional[str], Header(alias="X-Family-Id")] = None,
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
        x_family_id_header_present=bool((x_family_id or "").strip()),
        timestamp=datetime.now().isoformat()
    )
    
    # ✅ РЕАЛИЗАЦИЯ: family схемы лежат в PostgreSQL.
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")

    header_fid = (x_family_id or "").strip() or None

    def load_stats_sync():
        gen = get_postgres_db()
        db = next(gen)
        try:
            # Тот же выбор семьи, что и GET /api/family/members (`_resolve_primary_family_id_for_actor`),
            # с опциональным override из заголовка X-Family-Id (канонический id клиента из UserDefaults).
            _ensure_family_indexes(db)
            family_id: Optional[str] = None
            if header_fid and _actor_belongs_to_family(db, user_id, header_fid):
                family_id = header_fid
            if not family_id:
                family_id = _resolve_primary_family_id_for_actor(db, user_id, current_user)
            if not family_id:
                tier = _actor_subscription_level(db, user_id)
                cap = max_family_slots_for_subscription_level(tier)
                return (
                    FamilyStatsResponse(
                        totalMembers=0,
                        totalDevices=0,
                        totalThreats=0,
                        protectionLevel=0,
                        familyStatus="danger",
                        familyStatusMessage="Семья не создана",
                        familyRosterUsed=0,
                        familyRosterMax=cap,
                        ownerSubscriptionTier=tier,
                    ),
                    None,
                )

            # Агрегат по тем же строкам, что отдаёт GET /members:
            # COUNT(*) по family_id == len(GET /api/family/members).
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

            # Источник правды для числа устройств = тот же фильтр, что GET /api/devices (строка user_id владельца токена).
            # Так `family/stats.totalDevices` совпадает по смыслу с длиной списка устройств на главном экране.
            total_devices = member_devices_sum
            try:
                drow = db.execute(
                    text(
                        """
                        SELECT COUNT(*)::int
                        FROM aladdin_family_devices d
                        WHERE d.user_id = :uid_text
                        """
                    ),
                    {"uid_text": str(user_id)},
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

            owner_tier = _owner_subscription_level_for_family(db, str(family_id))
            roster_cap = max_family_slots_for_subscription_level(owner_tier)

            logger.info(
                "family_stats_aligned_with_members",
                user_id=user_id,
                family_id=str(family_id),
                total_members=total_members,
                roster_cap=roster_cap,
                owner_subscription_tier=owner_tier,
                note="totalMembers equals COUNT(family_members) for same family_id as GET /members",
            )

            return (
                FamilyStatsResponse(
                    totalMembers=total_members,
                    totalDevices=total_devices,
                    totalThreats=total_threats,
                    protectionLevel=protection_level,
                    familyStatus=family_status,
                    familyStatusMessage=family_status_message,
                    familyRosterUsed=total_members,
                    familyRosterMax=roster_cap,
                    ownerSubscriptionTier=owner_tier,
                ),
                str(family_id),
            )
        finally:
            gen.close()

    try:
        stats, resolved_family_id = await asyncio.to_thread(load_stats_sync)
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

    if resolved_family_id:
        response.headers["X-Resolved-Family-Id"] = resolved_family_id
    
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
    envelope_version: Optional[int] = None
    envelopeVersion: Optional[int] = None
    sender_device_id: Optional[str] = None
    senderDeviceId: Optional[str] = None
    ciphertext: Optional[str] = None
    ciphertext_content_type: Optional[int] = 0
    ciphertextContentType: Optional[int] = None
    media_ciphertext_url: Optional[str] = None
    mediaCiphertextUrl: Optional[str] = None
    media_ciphertext_hash: Optional[str] = None
    mediaCiphertextHash: Optional[str] = None


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


def _row_to_family_member_response(row: Any) -> FamilyMemberResponse:
    member_id, name, role, status_val, threats_val, last_active, devices_val = row
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


class JoinFamilyRequest(BaseModel):
    """Тело POST /api/family/join — как `JoinFamilyRequest` в iOS."""

    family_id: str
    role: str
    age_group: str
    personal_letter: str
    device_type: str


class FamilyJoinInnerResponse(BaseModel):
    """Поле `data` в `APIResponse<FamilyResponse>` на клиенте."""

    success: bool
    family_id: str
    members: List[FamilyMemberResponse]
    your_member_id: str


class FamilyJoinAPIResponse(BaseModel):
    success: bool
    data: Optional[FamilyJoinInnerResponse] = None
    message: Optional[str] = None
    error: Optional[str] = None


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

            # Политика доступа: владелец семьи или parent-строка в этой семье (не «последняя роль в другой семье»).
            if not _actor_can_manage_family_roster(db, user_id, str(family_id)):
                if payload.familyId is not None:
                    in_target = db.execute(
                        text(
                            """
                            SELECT 1 FROM family_members
                            WHERE family_id = :fid AND user_id = :uid
                            LIMIT 1
                            """
                        ),
                        {"fid": str(family_id), "uid": user_id},
                    ).fetchone()
                    if in_target is None:
                        logger.warning(
                            "family_add_stale_context",
                            user_id=user_id,
                            family_id=str(family_id),
                            actor_family_id=str(actor_family_id) if actor_family_id is not None else None,
                        )
                        raise HTTPException(status_code=409, detail="family_context_stale")
                logger.warning(
                    "family_add_denied_not_admin",
                    user_id=user_id,
                    family_id=str(family_id),
                    actor_family_id=str(actor_family_id) if actor_family_id is not None else None,
                )
                raise HTTPException(status_code=403, detail="Only administrators can add members")

            owner_level = _owner_subscription_level_for_family(db, str(family_id))
            _acquire_family_roster_write_lock(db, str(family_id))
            max_slots = max_family_slots_for_subscription_level(owner_level)
            current_slots = _count_family_members(db, str(family_id))
            if current_slots >= max_slots:
                logger.info(
                    "family_roster_gate_decision",
                    endpoint="/api/family/add",
                    decision="deny",
                    reason="family_roster_full",
                    family_id=str(family_id),
                    roster_used=current_slots,
                    roster_max=max_slots,
                    owner_subscription_level=owner_level,
                    user_id=user_id,
                )
                logger.warning(
                    "family_add_roster_full",
                    user_id=user_id,
                    family_id=str(family_id),
                    current_slots=current_slots,
                    max_slots=max_slots,
                    owner_subscription_level=owner_level,
                )
                raise HTTPException(status_code=409, detail="family_roster_full")
            logger.info(
                "family_roster_gate_decision",
                endpoint="/api/family/add",
                decision="allow",
                reason="within_limit",
                family_id=str(family_id),
                roster_used=current_slots,
                roster_max=max_slots,
                owner_subscription_level=owner_level,
                user_id=user_id,
            )

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


@router.post("/join", response_model=FamilyJoinAPIResponse)
@limiter.limit("10/minute")
async def join_family_post(
    request: Request,
    body: JoinFamilyRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    POST /api/family/join — контракт iOS `JoinFamilyRequest` / `APIResponse<FamilyResponse>`.
    """
    user_id = _resolve_user_id_from_claim(current_user)
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")

    def join_sync() -> FamilyJoinAPIResponse:
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_family_indexes(db)
            try:
                db.execute(text("SET LOCAL synchronous_commit = on"))
            except Exception:
                pass

            canonical_fid = _normalize_client_family_id(body.family_id)
            if not canonical_fid:
                raise HTTPException(status_code=400, detail="invalid family_id")

            fam_exists = db.execute(
                text("SELECT 1 FROM families WHERE id = :fid LIMIT 1"),
                {"fid": canonical_fid},
            ).fetchone()
            if not fam_exists:
                logger.warning("family_join_unknown_family", user_id=user_id, family_id=canonical_fid)
                raise HTTPException(status_code=404, detail="family_not_found")

            existing_same = db.execute(
                text(
                    """
                    SELECT id FROM family_members
                    WHERE family_id = :fid AND user_id = :uid
                    ORDER BY updated_at DESC NULLS LAST, id DESC
                    LIMIT 1
                    """
                ),
                {"fid": canonical_fid, "uid": user_id},
            ).fetchone()
            if existing_same and existing_same[0] is not None:
                your_mid = str(existing_same[0])
                rows = _fetch_family_member_rows(db, canonical_fid)
                members = [_row_to_family_member_response(r) for r in rows]
                return FamilyJoinAPIResponse(
                    success=True,
                    data=FamilyJoinInnerResponse(
                        success=True,
                        family_id=canonical_fid,
                        members=members,
                        your_member_id=your_mid,
                    ),
                    message=None,
                    error=None,
                )

            other_f = db.execute(
                text(
                    """
                    SELECT family_id FROM family_members
                    WHERE user_id = :uid AND family_id <> :fid
                    LIMIT 1
                    """
                ),
                {"uid": user_id, "fid": canonical_fid},
            ).fetchone()
            if other_f and other_f[0] is not None:
                logger.warning(
                    "family_join_already_in_another_family",
                    user_id=user_id,
                    target_family_id=canonical_fid,
                    existing_family_id=str(other_f[0]),
                )
                raise HTTPException(status_code=409, detail="already_in_another_family")

            role = (body.role or "").strip().lower()
            allowed_roles = {"parent", "child", "teenager", "elderly", "other"}
            if role not in allowed_roles:
                raise HTTPException(status_code=400, detail="Invalid role")

            letter = (body.personal_letter or "").strip().upper()
            if len(letter) != 1 or not letter.isalpha():
                raise HTTPException(status_code=400, detail="personal_letter must be a single letter")

            display_name = f"{role.upper()} {letter}"

            dup_name = db.execute(
                text(
                    """
                    SELECT 1 FROM family_members
                    WHERE family_id = :fid AND lower(trim(name)) = lower(:name)
                    LIMIT 1
                    """
                ),
                {"fid": canonical_fid, "name": display_name},
            ).fetchone()
            if dup_name:
                raise HTTPException(status_code=409, detail="personal_letter_taken")

            owner_level = _owner_subscription_level_for_family(db, canonical_fid)
            _acquire_family_roster_write_lock(db, canonical_fid)
            max_slots = max_family_slots_for_subscription_level(owner_level)
            current_slots = _count_family_members(db, canonical_fid)
            if current_slots >= max_slots:
                logger.info(
                    "family_roster_gate_decision",
                    endpoint="/api/family/join",
                    decision="deny",
                    reason="family_roster_full",
                    family_id=canonical_fid,
                    roster_used=current_slots,
                    roster_max=max_slots,
                    owner_subscription_level=owner_level,
                    user_id=user_id,
                )
                logger.warning(
                    "family_join_roster_full",
                    user_id=user_id,
                    family_id=canonical_fid,
                    current_slots=current_slots,
                    max_slots=max_slots,
                )
                raise HTTPException(status_code=409, detail="family_roster_full")
            logger.info(
                "family_roster_gate_decision",
                endpoint="/api/family/join",
                decision="allow",
                reason="within_limit",
                family_id=canonical_fid,
                roster_used=current_slots,
                roster_max=max_slots,
                owner_subscription_level=owner_level,
                user_id=user_id,
            )

            member_id = f"MEM_{uuid.uuid4().hex[:12].upper()}"
            last_active = _iso_utc_timestamp()
            db.execute(
                text(
                    """
                    INSERT INTO family_members (id, family_id, user_id, name, role, status, threats_blocked, last_active, devices)
                    VALUES (:id, :family_id, :user_id, :name, :role, 'protected', 0, :last_active, 0)
                    """
                ),
                {
                    "id": member_id,
                    "family_id": canonical_fid,
                    "user_id": user_id,
                    "name": display_name,
                    "role": role,
                    "last_active": last_active,
                },
            )
            db.commit()

            logger.info(
                "family_joined",
                user_id=user_id,
                family_id=canonical_fid,
                member_id=member_id,
                role=role,
                timestamp=datetime.now().isoformat(),
            )

            rows = _fetch_family_member_rows(db, canonical_fid)
            members = [_row_to_family_member_response(r) for r in rows]
            return FamilyJoinAPIResponse(
                success=True,
                data=FamilyJoinInnerResponse(
                    success=True,
                    family_id=canonical_fid,
                    members=members,
                    your_member_id=member_id,
                ),
                message=None,
                error=None,
            )
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(
                "family_join_db_error",
                user_id=user_id,
                error=str(e),
                timestamp=datetime.now().isoformat(),
            )
            raise HTTPException(status_code=500, detail="Failed to join family")
        finally:
            gen.close()

    return await asyncio.to_thread(join_sync)


@router.get("/members", response_model=list[FamilyMemberCompat])
async def get_family_members_compat(
    response: Response,
    current_user: dict = Depends(get_current_user),
    familyId: Optional[str] = Query(None, alias="familyId"),
):
    """
    ✅ Production rule: no mock/fake.
    Если БД не подключена — отдаём 503, чтобы клиент не принимал пустые/фейковые данные как "успех".

    Согласование контекста семьи (матрица ответов):
    - Есть primary family для JWT → 200, тело = ростер, заголовок `X-Resolved-Family-Id`.
    - Нет primary, query `familyId` **не** передан → 200 `[]`, заголовок `X-Family-Context: none` (клиент сбрасывает локальный кэш).
    - Нет primary, query `familyId` передан (устаревший/чужой кэш) → **404** `No family registered for this account (invalid familyId query)`.
    - Primary есть, query не совпадает с primary → **409** `familyId does not match...`.
    - Заголовок `X-Current-Member-Id` — `family_members.id` JWT-актора в этой семье (если есть строка членства).
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
                qfid_early = (familyId or "").strip()
                if qfid_early:
                    logger.warning(
                        "family_members_invalid_query_no_primary",
                        user_id=user_id,
                        query_family_id=qfid_early,
                    )
                    raise HTTPException(
                        status_code=404,
                        detail="No family registered for this account (invalid familyId query)",
                    )
                logger.warning("family_members_no_family_for_actor", user_id=user_id)
                return [], None, None, False, 0, 0
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

            if reconcile_sole_child_roster_for_owner is not None:
                try:
                    reconcile_sole_child_roster_for_owner(
                        db,
                        family_id=str(family_id),
                        actor_user_id=user_id,
                        log=logger,
                    )
                except Exception as exc:
                    logger.warning(
                        "family_roster_reconcile_failed",
                        error=str(exc),
                        family_id=str(family_id),
                        user_id=user_id,
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
            can_manage = _actor_can_manage_family_roster(db, user_id, str(family_id))
            owner_level = _owner_subscription_level_for_family(db, str(family_id))
            roster_used = _count_family_members(db, str(family_id))
            roster_max = max_family_slots_for_subscription_level(owner_level)
            return members, resolved, current_member_id, can_manage, roster_used, roster_max
        finally:
            gen.close()

    try:
        members, resolved_fid, current_member_id, can_manage, roster_used, roster_max = await asyncio.to_thread(load_members_sync)
        if resolved_fid:
            response.headers["X-Resolved-Family-Id"] = resolved_fid
            response.headers["X-Actor-Can-Manage-Roster"] = "true" if can_manage else "false"
            response.headers["X-Family-Roster-Used"] = str(roster_used)
            response.headers["X-Family-Roster-Max"] = str(roster_max)
            response.headers["X-Family-Limit"] = str(roster_max)
            response.headers["X-Family-Remaining"] = str(max(0, roster_max - roster_used))
            logger.info(
                "metric_family_members_get_ok",
                user_id=user_id,
                family_id=resolved_fid,
                count=len(members),
                can_manage_roster=can_manage,
                roster_used=roster_used,
                roster_max=roster_max,
            )
        elif not (familyId or "").strip():
            # Явный сигнал клиенту: у аккаунта нет семьи в БД — не интерпретировать `[]` как «неизвестно».
            response.headers["X-Family-Context"] = "none"
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

            if not _actor_can_manage_family_roster(db, user_id, str(family_id)):
                logger.warning(
                    "family_remove_denied_not_admin",
                    user_id=user_id,
                    family_id=str(family_id),
                    actor_role=actor_role,
                )
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

            if reconcile_sole_child_roster_for_owner is not None:
                try:
                    reconcile_sole_child_roster_for_owner(
                        db,
                        family_id=str(family_id),
                        actor_user_id=user_id,
                        log=logger,
                    )
                except Exception as exc:
                    logger.warning(
                        "family_roster_reconcile_post_failed",
                        error=str(exc),
                        family_id=str(family_id),
                        user_id=user_id,
                    )

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
    response: Response,
    current_user: dict = Depends(get_current_user),
    familyId: Optional[str] = Query(None, alias="familyId"),
):
    user_id = _resolve_user_id_from_claim(current_user)
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")

    def load_messages_sync() -> Tuple[List[Dict[str, Any]], Optional[str]]:
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_family_chat_table(db)
            effective_family_id = _resolve_effective_family_id_for_chat(db, user_id, current_user, familyId)
            fq = (familyId or "").strip()
            if fq and not effective_family_id:
                raise HTTPException(
                    status_code=404,
                    detail="No family context for requested familyId",
                )
            if not effective_family_id:
                return [], None

            ensure_chat_v2_columns(db)
            rows = db.execute(
                text(SELECT_MESSAGES_SQL),
                {"family_id": effective_family_id},
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
                {"family_id": effective_family_id},
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
                item = row_to_api_message(r, current_user)
                item["reactions"] = reactions_by_message.get(str(r[0]), [])
                messages.append(item)
            return messages, effective_family_id
        finally:
            gen.close()

    messages, eff_fid = await asyncio.to_thread(load_messages_sync)
    if eff_fid:
        response.headers["X-Resolved-Family-Id"] = str(eff_fid)
    return messages


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
    Пользователь должен быть участником выбранной семьи (или владельцем); выбор семьи согласован с GET /stats:
    при членстве в переданной семье используем её, иначе primary из JWT/БД (как при неверном X-Family-Id в stats).
    Лимит размера: переменная окружения ALADDIN_FAMILY_CHAT_UPLOAD_MAX_BYTES (по умолчанию 25 MiB).

    Nginx: для этого пути нужен `client_max_body_size` не ниже лимита (по умолчанию 25 MiB); иначе возможен не-JSON 413/502, не путать с 403 JSON от FastAPI.
    """
    user_id = _resolve_user_id_from_claim(current_user)
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")
    requested_fid = (x_family_id or family_id_form or "").strip()
    if not requested_fid:
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
            effective: Optional[str] = None
            if requested_fid and _actor_belongs_to_family(db, user_id, requested_fid):
                effective = requested_fid
            if not effective:
                effective = _resolve_primary_family_id_for_actor(db, user_id, current_user)
            if not effective or not _actor_belongs_to_family(db, user_id, effective):
                logger.warning(
                    "family_chat_upload_denied",
                    user_id=user_id,
                    requested_fid=requested_fid,
                    effective=str(effective or ""),
                )
                raise HTTPException(status_code=403, detail="Not a member of this family")
            family_id_used = effective
        finally:
            gen.close()
        root = _ensure_family_chat_upload_root()
        dest = root / name
        dest.write_bytes(content)
        url = f"{base}/api/family/chat/media/{name}"
        logger.info(
            "family_chat_media_upload",
            saved=name,
            bytes=len(content),
            family_id=family_id_used,
            requested_fid=requested_fid,
        )
        return {"success": True, "url": url, "mediaUrl": url}

    return await asyncio.to_thread(persist)


@router.post("/chat/upload-media-ciphertext")
async def family_chat_upload_media_ciphertext(
    request: Request,
    current_user: dict = Depends(get_current_user),
    x_family_id: Annotated[Optional[str], Header(alias="X-Family-Id")] = None,
    x_content_hash: Annotated[Optional[str], Header(alias="X-Content-Sha256")] = None,
):
    """E1.6 — загрузка только ciphertext blob (application/octet-stream)."""
    user_id = _resolve_user_id_from_claim(current_user)
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")
    requested_fid = (x_family_id or "").strip()
    if not requested_fid:
        raise HTTPException(status_code=400, detail="X-Family-Id is required")
    content = await request.body()
    if not content:
        raise HTTPException(status_code=400, detail="Empty body")
    max_bytes = int(os.environ.get("ALADDIN_FAMILY_CHAT_UPLOAD_MAX_BYTES", str(25 * 1024 * 1024)))
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail="File too large")
    base = str(request.base_url).rstrip("/")
    name = f"{uuid.uuid4().hex}.enc"

    def persist() -> dict:
        gen = get_postgres_db()
        db = next(gen)
        try:
            effective: Optional[str] = None
            if requested_fid and _actor_belongs_to_family(db, user_id, requested_fid):
                effective = requested_fid
            if not effective:
                effective = _resolve_primary_family_id_for_actor(db, user_id, current_user)
            if not effective or not _actor_belongs_to_family(db, user_id, effective):
                raise HTTPException(status_code=403, detail="Not a member of this family")
        finally:
            gen.close()
        root = _ensure_family_chat_upload_root()
        dest = root / name
        dest.write_bytes(content)
        url = f"{base}/api/family/chat/media/{name}"
        logger.info(
            "family_chat_media_ciphertext_upload",
            saved=name,
            bytes=len(content),
            family_id=effective,
            hash=(x_content_hash or "")[:16],
        )
        return {
            "success": True,
            "url": url,
            "mediaCiphertextUrl": url,
            "mediaUrl": url,
            "contentHash": (x_content_hash or "").strip() or None,
            "mediaCiphertextHash": (x_content_hash or "").strip() or None,
        }

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

    def send_sync():
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_family_chat_table(db)
            family_id = _resolve_effective_family_id_for_chat(db, user_id, current_user, payload.familyId)
            if not family_id:
                raise HTTPException(status_code=404, detail="Family not found")

            ensure_chat_v2_columns(db)
            message_id = f"MSG_{uuid.uuid4().hex[:12].upper()}"
            timestamp = _iso_utc_timestamp()
            sender_name = str(current_user.get("name") or "You")
            insert_params = build_send_insert_params(
                payload,
                message_id=message_id,
                family_id=family_id,
                user_id=user_id,
                sender_name=sender_name,
                timestamp=timestamp,
            )
            db.execute(text(INSERT_MESSAGE_SQL), insert_params)
            db.commit()
            return SendFamilyChatMessageResponse(success=True, messageId=message_id), family_id, insert_params
        finally:
            gen.close()

    response, family_id, insert_params = await asyncio.to_thread(send_sync)
    try:
        ws_payload = build_ws_new_message_payload(
            message_id=response.messageId,
            family_id=family_id,
            user_id=user_id,
            insert_params=insert_params,
        )
        await family_ws_manager.broadcast(family_id, ws_payload)
    except Exception as exc:
        logger.warning("family_chat_send ws broadcast skipped", error=str(exc))
    return response


@router.post("/chat/send/typing", response_model=FamilyCompatBoolResponse)
async def family_chat_send_typing(
    payload: TypingIndicatorRequest,
    current_user: dict = Depends(get_current_user),
):
    """Тот же резолв семьи, что и `POST /chat/send` — без фиктивного 200 при отсутствии семьи."""
    user_id = _resolve_user_id_from_claim(current_user)
    if not get_postgres_db:
        raise HTTPException(status_code=503, detail="Family backend unavailable (database not configured)")

    def typing_sync() -> None:
        gen = get_postgres_db()
        db = next(gen)
        try:
            _ensure_family_chat_table(db)
            family_id = _resolve_effective_family_id_for_chat(db, user_id, current_user, payload.familyId)
            if not family_id:
                raise HTTPException(status_code=404, detail="Family not found")
        finally:
            gen.close()

    await asyncio.to_thread(typing_sync)
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
            ensure_chat_v2_columns(db)
            env_row = db.execute(
                text("SELECT envelope_version FROM family_chat_messages WHERE id = :mid LIMIT 1"),
                {"mid": payload.messageId},
            ).fetchone()
            if env_row and int(env_row[0] or 1) == 2:
                raise HTTPException(
                    status_code=400,
                    detail="E2EE messages cannot be edited via plaintext; update ciphertext in client",
                )
            now = _iso_utc_timestamp()
            updated = db.execute(
                text(
                    """
                    UPDATE family_chat_messages
                    SET text = :text, edited_at = :edited_at
                    WHERE id = :message_id AND sender_user_id = :sender_user_id
                      AND COALESCE(envelope_version, 1) = 1
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

