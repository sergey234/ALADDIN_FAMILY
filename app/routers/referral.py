"""
Реферальная программа: API Endpoints с интеграцией БД
Использует реальную PostgreSQL базу данных
ИСПРАВЛЕНО: Добавлена обработка ошибок для всех endpoint'ов
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging

from app.database.database import get_db
from app.auth.auth import get_current_user

router = APIRouter(tags=["referral"])
logger = logging.getLogger(__name__)

# ============================================
# МОДЕЛИ ОТВЕТОВ
# ============================================

class ReferralFriendResponse(BaseModel):
    friend_id: str
    status: str
    created_at: str
    converted_at: Optional[str] = None
    reward_amount: Optional[float] = None

class ReferralOverviewResponse(BaseModel):
    referral_code: str
    referral_url: str
    qr_code: Optional[str] = None
    invitations_count: int
    earned_bonus: float
    invited_friends: List[ReferralFriendResponse]

class ReferralStatsResponse(BaseModel):
    total_referrals: int
    converted_referrals: int
    pending_referrals: int
    total_rewards: float
    conversion_rate: float
    referral_tier: str
    active_links: int

class ReferralHistoryItem(BaseModel):
    referral_id: str
    friend_id: str
    status: str
    created_at: str
    converted_at: Optional[str] = None
    referral_code: str
    discount_applied: float
    reward_amount: float

class ReferralRewardItem(BaseModel):
    reward_id: str
    title_key: str
    subtitle_key: str
    amount_key: str
    reward_value: str
    icon: str
    required_converted: int
    status: str
    remaining: int
    unlocked_at: Optional[str] = None

class ReferralRewardsResponse(BaseModel):
    total_converted: int
    rewards: List[ReferralRewardItem]

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def get_or_create_referral_code(db: Session, user_id) -> str:
    """Получить или создать реферальный код для пользователя"""
    try:
        # Преобразуем user_id в int, если это строка
        user_id_int = int(user_id) if isinstance(user_id, str) else user_id
        
        # Используем SQL функцию из БД
        result = db.execute(
            text("SELECT get_or_create_referral_code(:user_id) as code"),
            {"user_id": user_id_int}
        )
        code = result.scalar()
        if not code:
            # Если функция не существует, создаем код вручную
            code = f"REF{user_id_int:06d}"
        return code
    except Exception as e:
        logger.error(f"Ошибка в get_or_create_referral_code: {str(e)}")
        # Fallback: создаем код вручную
        user_id_int = int(user_id) if isinstance(user_id, str) else user_id
        return f"REF{user_id_int:06d}"

def count_referrals(db: Session, user_id) -> dict:
    """Посчитать статистику рефералов"""
    try:
        # Преобразуем user_id в int, если это строка
        user_id_int = int(user_id) if isinstance(user_id, str) else user_id
        
        result = db.execute(
            text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'completed') as converted,
                    COUNT(*) FILTER (WHERE status = 'pending') as pending,
                    COALESCE(SUM(reward_amount), 0) as earned_bonus
                FROM referrals
                WHERE referrer_id = :user_id
            """),
            {"user_id": user_id_int}
        )
        row = result.fetchone()
        return {
            "total": row[0] if row else 0,
            "converted": row[1] if row else 0,
            "pending": row[2] if row else 0,
            "earned_bonus": float(row[3]) if row and row[3] else 0.0
        }
    except Exception as e:
        logger.error(f"Ошибка в count_referrals: {str(e)}")
        # Возвращаем пустую статистику
        return {
            "total": 0,
            "converted": 0,
            "pending": 0,
            "earned_bonus": 0.0
        }

def get_invited_friends(db: Session, user_id) -> List[dict]:
    """Получить список приглашенных друзей"""
    try:
        # Преобразуем user_id в int, если это строка
        user_id_int = int(user_id) if isinstance(user_id, str) else user_id
        
        result = db.execute(
            text("""
                SELECT 
                    invited_user_id,
                    status,
                    created_at,
                    converted_at,
                    reward_amount
                FROM referrals
                WHERE referrer_id = :user_id
                ORDER BY created_at DESC
            """),
            {"user_id": user_id_int}
        )
        friends = []
        for row in result:
            friends.append({
                "friend_id": str(row[0]),
                "status": row[1],
                "created_at": row[2].isoformat() if row[2] else "",
                "converted_at": row[3].isoformat() if row[3] else None,
                "reward_amount": float(row[4]) if row[4] else None
            })
        return friends
    except Exception as e:
        logger.error(f"Ошибка в get_invited_friends: {str(e)}")
        return []

def get_referral_history(db: Session, user_id) -> List[dict]:
    """Получить полную историю приглашений"""
    try:
        # Преобразуем user_id в int, если это строка
        user_id_int = int(user_id) if isinstance(user_id, str) else user_id
        
        result = db.execute(
            text("""
                SELECT 
                    id,
                    invited_user_id,
                    status,
                    created_at,
                    converted_at,
                    referral_code,
                    discount_applied,
                    reward_amount
                FROM referrals
                WHERE referrer_id = :user_id
                ORDER BY created_at DESC
            """),
            {"user_id": user_id_int}
        )
        history = []
        for row in result:
            history.append({
                "referral_id": str(row[0]),
                "friend_id": str(row[1]),
                "status": row[2],
                "created_at": row[3].isoformat() if row[3] else "",
                "converted_at": row[4].isoformat() if row[4] else None,
                "referral_code": row[5],
                "discount_applied": float(row[6]) if row[6] else 0.0,
                "reward_amount": float(row[7]) if row[7] else 0.0
            })
        return history
    except Exception as e:
        logger.error(f"Ошибка в get_referral_history: {str(e)}")
        return []

def get_active_links_count(db: Session, user_id) -> int:
    """Посчитать активные ссылки за последние 30 дней"""
    try:
        # Преобразуем user_id в int, если это строка
        user_id_int = int(user_id) if isinstance(user_id, str) else user_id
        
        result = db.execute(
            text("""
                SELECT COUNT(DISTINCT referral_code)
                FROM referrals
                WHERE referrer_id = :user_id
                  AND created_at >= NOW() - INTERVAL '30 days'
            """),
            {"user_id": user_id_int}
        )
        return result.scalar() or 0
    except Exception as e:
        logger.error(f"Ошибка в get_active_links_count: {str(e)}")
        return 0

def get_referral_tier(converted_count: int) -> str:
    """Tier Family Invite Pro (A): bronze/silver/gold/platinum."""
    try:
        from app.services.family_referral_a import tier_for_qualified_count

        q = max(0, int(converted_count))
        if q <= 0:
            return "bronze"
        return tier_for_qualified_count(q).tier.value
    except Exception:
        if converted_count >= 10:
            return "platinum"
        if converted_count >= 5:
            return "gold"
        if converted_count >= 3:
            return "silver"
        return "bronze"

# ============================================
# ENDPOINT 1: GET /api/referral/code
# ============================================

@router.get("/code", response_model=ReferralOverviewResponse)
async def get_referral_code(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить реферальный код пользователя и статистику."""
    try:
        user_id = current_user["id"]
        
        # Получить или создать реферальный код
        referral_code = get_or_create_referral_code(db, user_id)
        
        # Посчитать статистику
        stats = count_referrals(db, user_id)
        
        # Получить список приглашенных друзей
        friends = get_invited_friends(db, user_id)
        
        invited_friends = [
            ReferralFriendResponse(**friend) for friend in friends
        ]
        
        return ReferralOverviewResponse(
            referral_code=referral_code,
            referral_url=f"https://aladdin-ai.ru/invite/{referral_code}",
            qr_code=None,
            invitations_count=stats["total"],
            earned_bonus=stats["earned_bonus"],
            invited_friends=invited_friends
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка в get_referral_code: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

# ============================================
# ENDPOINT 2: GET /api/referral/stats
# ============================================

@router.get("/stats", response_model=ReferralStatsResponse)
async def get_referral_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить статистику реферальной программы."""
    try:
        user_id = current_user["id"]
        
        # Посчитать статистику
        stats = count_referrals(db, user_id)
        
        total_referrals = stats["total"]
        converted_referrals = stats["converted"]
        pending_referrals = stats["pending"]
        total_rewards = stats["earned_bonus"]
        
        # Вычислить конверсию
        conversion_rate = (converted_referrals / total_referrals * 100) if total_referrals > 0 else 0.0
        
        # Определить tier
        referral_tier = get_referral_tier(converted_referrals)
        
        # Активные ссылки
        active_links = get_active_links_count(db, user_id)
        
        return ReferralStatsResponse(
            total_referrals=total_referrals,
            converted_referrals=converted_referrals,
            pending_referrals=pending_referrals,
            total_rewards=total_rewards,
            conversion_rate=conversion_rate,
            referral_tier=referral_tier,
            active_links=active_links
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка в get_referral_stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

# ============================================
# ENDPOINT 3: GET /api/referral/history
# ============================================

@router.get("/history", response_model=List[ReferralHistoryItem])
async def get_referral_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить историю всех приглашенных пользователей."""
    try:
        user_id = current_user["id"]
        
        # Получить историю
        history = get_referral_history(db, user_id)
        
        return [ReferralHistoryItem(**item) for item in history]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка в get_referral_history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

# ============================================
# ENDPOINT 4: GET /api/referral/rewards
# ============================================

@router.get("/rewards", response_model=ReferralRewardsResponse)
async def get_referral_rewards(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Награды Family Invite Pro: другу −20%; рефереру дни защиты по уровню."""
    try:
        user_id = current_user["id"]
        stats = count_referrals(db, user_id)
        total_converted = stats["converted"]

        def row(reward_id, title_key, subtitle_key, amount_key, value, icon, need, unlocked_at=None):
            unlocked = total_converted >= need if need > 0 else True
            return ReferralRewardItem(
                reward_id=reward_id,
                title_key=title_key,
                subtitle_key=subtitle_key,
                amount_key=amount_key,
                reward_value=value,
                icon=icon,
                required_converted=need,
                status="unlocked" if unlocked else "locked",
                remaining=0 if unlocked else max(0, need - total_converted),
                unlocked_at=unlocked_at if unlocked else None,
            )

        now = datetime.now().isoformat()
        rewards = [
            row("friend", "referral_a_reward_friend_title", "referral_a_reward_friend_subtitle",
                "referral_a_reward_friend_value", "-20%", "tag.fill", 0, now),
            row("bronze", "referral_a_reward_bronze_title", "referral_a_reward_bronze_subtitle",
                "referral_a_reward_bronze_value", "+7d", "shield.fill", 1, now),
            row("silver", "referral_a_reward_silver_title", "referral_a_reward_silver_subtitle",
                "referral_a_reward_silver_value", "+14d", "shield.lefthalf.filled", 3, now),
            row("gold", "referral_a_reward_gold_title", "referral_a_reward_gold_subtitle",
                "referral_a_reward_gold_value", "+30d", "crown.fill", 5, now),
            row("platinum", "referral_a_reward_platinum_title", "referral_a_reward_platinum_subtitle",
                "referral_a_reward_platinum_value", "+30d", "star.fill", 10, now),
        ]

        return ReferralRewardsResponse(
            total_converted=total_converted,
            rewards=rewards
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка в get_referral_rewards: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


# ============================================
# FAMILY INVITE PRO (Вариант A) — ledger / apply / attach
# ============================================

class FamilyReferralApplyRequest(BaseModel):
    referrer_family_id: str
    friend_family_id: str
    friend_user_id: int
    referral_code: Optional[str] = None
    referrer_has_active_tariff: bool = True
    friend_has_paid: bool = False
    friend_active_protection_days: int = 0
    device_soft: Optional[str] = None


class FamilyReferralApplyResponse(BaseModel):
    ok: bool
    reason: str
    friend_discount_percent: int = 0
    referrer_protection_days: int = 0
    tier: Optional[str] = None
    qualified_count: Optional[int] = None


class FamilyReferralLedgerItem(BaseModel):
    id: str
    status: str
    reason: str
    friend_discount_percent: int
    referrer_protection_days: int
    tier: Optional[str] = None
    created_at: Optional[str] = None
    referrer_family_id: str
    friend_family_id: str


class FamilyReferralAOverviewResponse(BaseModel):
    qualified_families: int
    tier: str
    referrer_protection_days_current_tier: int
    friend_discount_percent: int
    progress: dict
    ledger: List[FamilyReferralLedgerItem]
    program: str = "family_invite_pro_a"


@router.get("/a/overview", response_model=FamilyReferralAOverviewResponse)
async def family_referral_a_overview(
    family_id: str = "",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Обзор Family Invite Pro: уровень, прогресс, ledger."""
    from app.services import family_referral_ledger as frl

    user_id = current_user["id"]
    fid = (family_id or "").strip()
    data = frl.overview_for_referrer(db, user_id=int(user_id), family_id=fid)
    ledger_items = [
        FamilyReferralLedgerItem(
            id=x["id"],
            status=x["status"],
            reason=x["reason"],
            friend_discount_percent=x["friend_discount_percent"],
            referrer_protection_days=x["referrer_protection_days"],
            tier=x.get("tier"),
            created_at=x.get("created_at"),
            referrer_family_id=x["referrer_family_id"],
            friend_family_id=x["friend_family_id"],
        )
        for x in data.get("ledger", [])
    ]
    return FamilyReferralAOverviewResponse(
        qualified_families=data["qualified_families"],
        tier=data["tier"],
        referrer_protection_days_current_tier=data["referrer_protection_days_current_tier"],
        friend_discount_percent=data["friend_discount_percent"],
        progress=data["progress"],
        ledger=ledger_items,
    )


@router.get("/a/ledger", response_model=List[FamilyReferralLedgerItem])
async def family_referral_a_ledger(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    from app.services import family_referral_ledger as frl

    rows = frl.list_ledger_for_user(db, int(current_user["id"]), limit=50)
    return [
        FamilyReferralLedgerItem(
            id=x["id"],
            status=x["status"],
            reason=x["reason"],
            friend_discount_percent=x["friend_discount_percent"],
            referrer_protection_days=x["referrer_protection_days"],
            tier=x.get("tier"),
            created_at=x.get("created_at"),
            referrer_family_id=x["referrer_family_id"],
            friend_family_id=x["friend_family_id"],
        )
        for x in rows
    ]


@router.post("/a/apply", response_model=FamilyReferralApplyResponse)
async def family_referral_a_apply(
    body: FamilyReferralApplyRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Начисление по qualify (оплата или 14+ дней защиты)."""
    from app.services import family_referral_ledger as frl

    referrer_uid = int(current_user["id"])
    out = frl.apply_family_referral_a(
        db,
        referrer_user_id=referrer_uid,
        friend_user_id=int(body.friend_user_id),
        referrer_family_id=body.referrer_family_id.strip(),
        friend_family_id=body.friend_family_id.strip(),
        referral_code=body.referral_code,
        referrer_has_active_tariff=bool(body.referrer_has_active_tariff),
        friend_has_paid=bool(body.friend_has_paid),
        friend_active_protection_days=int(body.friend_active_protection_days or 0),
        device_raw=body.device_soft,
    )
    return FamilyReferralApplyResponse(
        ok=bool(out.get("ok")),
        reason=str(out.get("reason") or ""),
        friend_discount_percent=int(out.get("friend_discount_percent") or 0),
        referrer_protection_days=int(out.get("referrer_protection_days") or 0),
        tier=out.get("tier"),
        qualified_count=out.get("qualified_count"),
    )


@router.post("/a/attach")
async def family_referral_a_attach_code(
    code: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Привязка invite-кода к текущему пользователю (pending)."""
    user_id = int(current_user["id"])
    c = (code or "").strip().upper()
    if len(c) < 4 or len(c) > 20:
        raise HTTPException(status_code=400, detail="invalid_code")
    try:
        owner = db.execute(
            text("SELECT user_id FROM referral_codes WHERE UPPER(code) = :c"),
            {"c": c},
        ).fetchone()
        if not owner:
            raise HTTPException(status_code=404, detail="code_not_found")
        referrer_id = int(owner[0])
        if referrer_id == user_id:
            raise HTTPException(status_code=400, detail="anti_self")
        existing = db.execute(
            text(
                """
                SELECT id FROM referrals
                WHERE referrer_id = :r AND invited_user_id = :u
                LIMIT 1
                """
            ),
            {"r": referrer_id, "u": user_id},
        ).fetchone()
        if existing:
            return {"ok": True, "status": "already_attached", "referral_code": c}
        db.execute(
            text(
                """
                INSERT INTO referrals (referrer_id, invited_user_id, referral_code, status, discount_applied)
                VALUES (:r, :u, :c, 'pending', 0)
                """
            ),
            {"r": referrer_id, "u": user_id, "c": c},
        )
        db.commit()
        return {"ok": True, "status": "attached", "referral_code": c}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("family_referral_a_attach: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="attach_failed")
