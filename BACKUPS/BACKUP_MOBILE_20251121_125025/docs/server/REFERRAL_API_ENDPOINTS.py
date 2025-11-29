"""
============================================
РЕФЕРАЛЬНАЯ ПРОГРАММА: API Endpoints
============================================
Сервер: 149.154.65.180
Дата: 21 ноября 2024
============================================
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

# Импорты ваших моделей и зависимостей
# from app.database import get_db
# from app.auth import get_current_user
# from app.models import User, ReferralCode, Referral

router = APIRouter(prefix="/api/referral", tags=["referral"])


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
# ENDPOINT 1: GET /api/referral/code
# ============================================

@router.get("/code", response_model=ReferralOverviewResponse)
async def get_referral_code(
    request: Request,
    # current_user: User = Depends(get_current_user),
    # db: Session = Depends(get_db)
):
    """
    Получить реферальный код пользователя и статистику.
    
    Требуется авторизация (токен в заголовке Authorization: Bearer {token})
    """
    # ✅ РЕАЛИЗАЦИЯ: Проверка токена
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # TODO: Раскомментировать после настройки авторизации
    # user = verify_token(token)  # Ваша функция проверки токена
    # if not user:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    # user_id = user["id"]
    
    # Временная заглушка для тестирования
    user_id = 1  # Заменить на реальный user_id из токена
    
    # ✅ РЕАЛИЗАЦИЯ: Получить или создать реферальный код
    referral_code = db.execute(
        "SELECT get_or_create_referral_code(:user_id) as code",
        {"user_id": user_id}
    ).scalar()
    
    # ✅ РЕАЛИЗАЦИЯ: Посчитать статистику
    stats = db.execute(
        """
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE status = 'completed') as converted,
            COALESCE(SUM(reward_amount), 0) as earned_bonus
        FROM referrals
        WHERE referrer_id = :user_id
        """,
        {"user_id": user_id}
    ).fetchone()
    
    invitations_count = stats.total if stats else 0
    earned_bonus = float(stats.earned_bonus) if stats else 0.0
    
    # ✅ РЕАЛИЗАЦИЯ: Получить список приглашенных друзей
    friends = db.execute(
        """
        SELECT 
            invited_user_id as friend_id,
            status,
            created_at,
            converted_at,
            reward_amount
        FROM referrals
        WHERE referrer_id = :user_id
        ORDER BY created_at DESC
        """,
        {"user_id": user_id}
    ).fetchall()
    
    invited_friends = [
        ReferralFriendResponse(
            friend_id=str(friend.friend_id),
            status=friend.status,
            created_at=friend.created_at.isoformat() if friend.created_at else "",
            converted_at=friend.converted_at.isoformat() if friend.converted_at else None,
            reward_amount=float(friend.reward_amount) if friend.reward_amount else None
        )
        for friend in friends
    ]
    
    return ReferralOverviewResponse(
        referral_code=referral_code,
        referral_url=f"https://aladdin-ai.ru/invite/{referral_code}",
        qr_code=None,  # Опционально: сгенерировать QR код
        invitations_count=invitations_count,
        earned_bonus=earned_bonus,
        invited_friends=invited_friends
    )


# ============================================
# ENDPOINT 2: GET /api/referral/stats
# ============================================

@router.get("/stats", response_model=ReferralStatsResponse)
async def get_referral_stats(
    request: Request,
    # current_user: User = Depends(get_current_user),
    # db: Session = Depends(get_db)
):
    """
    Получить статистику реферальной программы пользователя.
    
    Требуется авторизация.
    """
    # ✅ РЕАЛИЗАЦИЯ: Проверка токена
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # TODO: Раскомментировать после настройки авторизации
    # user = verify_token(token)
    # if not user:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    # user_id = user["id"]
    
    user_id = 1  # Заменить на реальный user_id из токена
    
    # ✅ РЕАЛИЗАЦИЯ: Посчитать статистику
    stats = db.execute(
        """
        SELECT 
            COUNT(*) as total_referrals,
            COUNT(*) FILTER (WHERE status = 'completed') as converted_referrals,
            COUNT(*) FILTER (WHERE status = 'pending') as pending_referrals,
            COALESCE(SUM(reward_amount), 0) as total_rewards
        FROM referrals
        WHERE referrer_id = :user_id
        """,
        {"user_id": user_id}
    ).fetchone()
    
    total_referrals = stats.total_referrals if stats else 0
    converted_referrals = stats.converted_referrals if stats else 0
    pending_referrals = stats.pending_referrals if stats else 0
    total_rewards = float(stats.total_rewards) if stats else 0.0
    
    # Вычислить конверсию
    conversion_rate = (converted_referrals / total_referrals * 100) if total_referrals > 0 else 0.0
    
    # Определить tier
    if converted_referrals >= 10:
        referral_tier = "gold"
    elif converted_referrals >= 5:
        referral_tier = "silver"
    else:
        referral_tier = "bronze"
    
    # Активные ссылки (за последние 30 дней) - упрощенная версия
    active_links = db.execute(
        """
        SELECT COUNT(DISTINCT referral_code)
        FROM referrals
        WHERE referrer_id = :user_id
          AND created_at >= NOW() - INTERVAL '30 days'
        """,
        {"user_id": user_id}
    ).scalar() or 0
    
    return ReferralStatsResponse(
        total_referrals=total_referrals,
        converted_referrals=converted_referrals,
        pending_referrals=pending_referrals,
        total_rewards=total_rewards,
        conversion_rate=conversion_rate,
        referral_tier=referral_tier,
        active_links=active_links
    )


# ============================================
# ENDPOINT 3: GET /api/referral/history
# ============================================

@router.get("/history", response_model=List[ReferralHistoryItem])
async def get_referral_history(
    request: Request,
    # current_user: User = Depends(get_current_user),
    # db: Session = Depends(get_db)
):
    """
    Получить историю всех приглашенных пользователей.
    
    Требуется авторизация.
    """
    # ✅ РЕАЛИЗАЦИЯ: Проверка токена
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # TODO: Раскомментировать после настройки авторизации
    # user = verify_token(token)
    # if not user:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    # user_id = user["id"]
    
    user_id = 1  # Заменить на реальный user_id из токена
    
    # ✅ РЕАЛИЗАЦИЯ: Получить историю
    referrals = db.execute(
        """
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
        """,
        {"user_id": user_id}
    ).fetchall()
    
    return [
        ReferralHistoryItem(
            referral_id=str(ref.id),
            friend_id=str(ref.invited_user_id),
            status=ref.status,
            created_at=ref.created_at.isoformat() if ref.created_at else "",
            converted_at=ref.converted_at.isoformat() if ref.converted_at else None,
            referral_code=ref.referral_code,
            discount_applied=float(ref.discount_applied) if ref.discount_applied else 0.0,
            reward_amount=float(ref.reward_amount) if ref.reward_amount else 0.0
        )
        for ref in referrals
    ]


# ============================================
# ENDPOINT 4: GET /api/referral/rewards
# ============================================

@router.get("/rewards", response_model=ReferralRewardsResponse)
async def get_referral_rewards(
    request: Request,
    # current_user: User = Depends(get_current_user),
    # db: Session = Depends(get_db)
):
    """
    Получить информацию о наградах и достижениях.
    
    Требуется авторизация.
    """
    # ✅ РЕАЛИЗАЦИЯ: Проверка токена
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # TODO: Раскомментировать после настройки авторизации
    # user = verify_token(token)
    # if not user:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    # user_id = user["id"]
    
    user_id = 1  # Заменить на реальный user_id из токена
    
    # ✅ РЕАЛИЗАЦИЯ: Посчитать количество оплативших
    total_converted = db.execute(
        """
        SELECT COUNT(*)
        FROM referrals
        WHERE referrer_id = :user_id AND status = 'completed'
        """,
        {"user_id": user_id}
    ).scalar() or 0
    
    # ✅ РЕАЛИЗАЦИЯ: Определить награды на основе total_converted
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


# ============================================
# ИНСТРУКЦИИ ПО ИСПОЛЬЗОВАНИЮ
# ============================================

"""
1. Скопируйте этот файл в ваш проект FastAPI
2. Раскомментируйте импорты и зависимости
3. Настройте авторизацию (get_current_user)
4. Настройте подключение к базе данных (get_db)
5. Реализуйте логику в каждом endpoint
6. Протестируйте все endpoints

Пример использования:
- GET /api/referral/code
  Headers: Authorization: Bearer {token}
  Response: ReferralOverviewResponse

- GET /api/referral/stats
  Headers: Authorization: Bearer {token}
  Response: ReferralStatsResponse

- GET /api/referral/history
  Headers: Authorization: Bearer {token}
  Response: List[ReferralHistoryItem]

- GET /api/referral/rewards
  Headers: Authorization: Bearer {token}
  Response: ReferralRewardsResponse
"""

