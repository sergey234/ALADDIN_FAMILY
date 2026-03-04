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
    """Определить tier на основе количества конверсий"""
    if converted_count >= 10:
        return "gold"
    elif converted_count >= 5:
        return "silver"
    else:
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
    """Получить информацию о наградах и достижениях."""
    try:
        user_id = current_user["id"]
        
        # Посчитать количество оплативших
        stats = count_referrals(db, user_id)
        total_converted = stats["converted"]
        
        # Определить награды на основе total_converted
        rewards = []
        
        # Награда 1: 1 приглашенный оплатил
        if total_converted >= 1:
            rewards.append(ReferralRewardItem(
                reward_id="reward_1",
                title_key="referral_reward_1_title",
                subtitle_key="referral_reward_1_subtitle",
                amount_key="referral_reward_1_amount",
                reward_value="10%",
                icon="percent.circle.fill",
                required_converted=1,
                status="unlocked",
                remaining=0,
                unlocked_at=datetime.now().isoformat()
            ))
        else:
            rewards.append(ReferralRewardItem(
                reward_id="reward_1",
                title_key="referral_reward_1_title",
                subtitle_key="referral_reward_1_subtitle",
                amount_key="referral_reward_1_amount",
                reward_value="10%",
                icon="percent.circle.fill",
                required_converted=1,
                status="locked",
                remaining=1 - total_converted,
                unlocked_at=None
            ))
        
        # Награда 2: 5 приглашенных оплатили
        if total_converted >= 5:
            rewards.append(ReferralRewardItem(
                reward_id="reward_2",
                title_key="referral_reward_2_title",
                subtitle_key="referral_reward_2_subtitle",
                amount_key="referral_reward_2_amount",
                reward_value="20%",
                icon="percent.circle.fill",
                required_converted=5,
                status="unlocked",
                remaining=0,
                unlocked_at=datetime.now().isoformat()
            ))
        else:
            rewards.append(ReferralRewardItem(
                reward_id="reward_2",
                title_key="referral_reward_2_title",
                subtitle_key="referral_reward_2_subtitle",
                amount_key="referral_reward_2_amount",
                reward_value="20%",
                icon="percent.circle.fill",
                required_converted=5,
                status="locked",
                remaining=5 - total_converted,
                unlocked_at=None
            ))
        
        # Награда 3: 10 приглашенных оплатили
        if total_converted >= 10:
            rewards.append(ReferralRewardItem(
                reward_id="reward_3",
                title_key="referral_reward_3_title",
                subtitle_key="referral_reward_3_subtitle",
                amount_key="referral_reward_3_amount",
                reward_value="30%",
                icon="percent.circle.fill",
                required_converted=10,
                status="unlocked",
                remaining=0,
                unlocked_at=datetime.now().isoformat()
            ))
        else:
            rewards.append(ReferralRewardItem(
                reward_id="reward_3",
                title_key="referral_reward_3_title",
                subtitle_key="referral_reward_3_subtitle",
                amount_key="referral_reward_3_amount",
                reward_value="30%",
                icon="percent.circle.fill",
                required_converted=10,
                status="locked",
                remaining=10 - total_converted,
                unlocked_at=None
            ))
        
        return ReferralRewardsResponse(
            total_converted=total_converted,
            rewards=rewards
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка в get_referral_rewards: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
