"""
Упрощенная версия referral endpoints для тестирования
Использует mock данные вместо реальной БД
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(tags=["referral"])

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
async def get_referral_code(request: Request):
    """Получить реферальный код пользователя и статистику."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Mock данные для тестирования
    return ReferralOverviewResponse(
        referral_code="ABC123",
        referral_url="https://aladdin-ai.ru/invite/ABC123",
        qr_code=None,
        invitations_count=0,
        earned_bonus=0.0,
        invited_friends=[]
    )

# ============================================
# ENDPOINT 2: GET /api/referral/stats
# ============================================

@router.get("/stats", response_model=ReferralStatsResponse)
async def get_referral_stats(request: Request):
    """Получить статистику реферальной программы."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Mock данные
    return ReferralStatsResponse(
        total_referrals=0,
        converted_referrals=0,
        pending_referrals=0,
        total_rewards=0.0,
        conversion_rate=0.0,
        referral_tier="bronze",
        active_links=0
    )

# ============================================
# ENDPOINT 3: GET /api/referral/history
# ============================================

@router.get("/history", response_model=List[ReferralHistoryItem])
async def get_referral_history(request: Request):
    """Получить историю приглашений."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Mock данные
    return []

# ============================================
# ENDPOINT 4: GET /api/referral/rewards
# ============================================

@router.get("/rewards", response_model=ReferralRewardsResponse)
async def get_referral_rewards(request: Request):
    """Получить информацию о наградах."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Mock данные
    return ReferralRewardsResponse(
        total_converted=0,
        rewards=[
            ReferralRewardItem(
                reward_id="reward_1",
                title_key="referral_reward_1_title",
                subtitle_key="referral_reward_1_subtitle",
                amount_key="referral_reward_1_amount",
                reward_value="10%",
                icon="percent.circle.fill",
                required_converted=1,
                status="locked",
                remaining=1,
                unlocked_at=None
            )
        ]
    )

