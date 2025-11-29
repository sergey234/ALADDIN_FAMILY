"""
============================================
РЕФЕРАЛЬНАЯ ПРОГРАММА: Обработка оплаты
============================================
Сервер: 149.154.65.180
Дата: 21 ноября 2024
============================================

КРИТИЧНО: Реферал засчитывается при ОПЛАТЕ, а не при регистрации!
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

# Импорты ваших моделей и зависимостей
# from app.database import get_db
# from app.auth import get_current_user
# from app.models import User, Referral, Subscription

router = APIRouter()


# ============================================
# МОДЕЛИ
# ============================================

class ActivationData(BaseModel):
    user_id: str
    code: str  # Код активации подписки


class ActivationResponse(BaseModel):
    success: bool
    subscription: dict
    referral_reward_applied: bool = False
    discount_applied: bool = False


# ============================================
# ОБРАБОТКА ОПЛАТЫ С РЕФЕРАЛЬНЫМ КОДОМ
# ============================================

@router.post("/api/subscription/activate", response_model=ActivationResponse)
async def activate_subscription(
    activation_data: ActivationData,
    # db: Session = Depends(get_db)
):
    """
    Активировать подписку и обработать реферальный код.
    
    ЛОГИКА:
    1. Активировать подписку для пользователя
    2. Проверить, есть ли реферальная запись для этого пользователя
    3. Если есть и status='pending', обновить на 'completed'
    4. Начислить награду рефереру
    5. Применить скидку приглашенному пользователю
    """
    # 1. Активировать подписку для пользователя
    # subscription = activate_user_subscription(activation_data.user_id, activation_data.code)
    # 
    # # 2. Проверить, есть ли реферальная запись для этого пользователя
    # referral = db.query(Referral).filter(
    #     Referral.invited_user_id == activation_data.user_id,
    #     Referral.status == "pending"
    # ).first()
    # 
    # referral_reward_applied = False
    # discount_applied = False
    # 
    # if referral:
    #     # 3. Обновить статус реферала на "completed"
    #     referral.status = "completed"
    #     referral.converted_at = datetime.now()
    #     referral.discount_applied = 500.0  # 20% скидка (пример)
    #     referral.reward_amount = 1000.0  # Награда рефереру (пример)
    #     
    #     # 4. Начислить награду рефереру
    #     referrer = db.query(User).filter(User.id == referral.referrer_id).first()
    #     if referrer:
    #         # Добавить бонус на счет реферера
    #         referrer.bonus_balance = (referrer.bonus_balance or 0) + referral.reward_amount
    #         referral_reward_applied = True
    #     
    #     # 5. Применить скидку к приглашенному пользователю
    #     invited_user = db.query(User).filter(User.id == activation_data.user_id).first()
    #     if invited_user:
    #         # Применить скидку 20% к подписке
    #         apply_discount_to_subscription(invited_user.id, discount_percent=20)
    #         discount_applied = True
    #     
    #     db.commit()
    #     
    #     return ActivationResponse(
    #         success=True,
    #         subscription=subscription,
    #         referral_reward_applied=referral_reward_applied,
    #         discount_applied=discount_applied
    #     )
    
    # Временный ответ для тестирования
    return ActivationResponse(
        success=True,
        subscription={"status": "active"},
        referral_reward_applied=False,
        discount_applied=False
    )


# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def apply_discount_to_subscription(user_id: str, discount_percent: int):
    """
    Применить скидку к подписке пользователя.
    
    Args:
        user_id: ID пользователя
        discount_percent: Процент скидки (например, 20)
    """
    # TODO: Реализовать логику применения скидки
    # Например:
    # - Обновить цену подписки
    # - Сохранить информацию о скидке
    # - Отправить уведомление пользователю
    pass


def add_referral_reward(user_id: str, amount: float):
    """
    Начислить награду рефереру.
    
    Args:
        user_id: ID реферера
        amount: Размер награды
    """
    # TODO: Реализовать логику начисления награды
    # Например:
    # - Добавить бонус на счет
    # - Отправить уведомление
    # - Записать в историю транзакций
    pass


# ============================================
# ИНТЕГРАЦИЯ С СУЩЕСТВУЮЩИМ КОДОМ ОПЛАТЫ
# ============================================

"""
Если у вас уже есть endpoint для активации подписки, 
добавьте эту логику в него:

@app.post("/api/subscription/activate")
async def activate_subscription(activation_data: ActivationData):
    # ... существующий код активации подписки ...
    
    # ДОБАВИТЬ: Обработка реферального кода
    referral = db.query(Referral).filter(
        Referral.invited_user_id == activation_data.user_id,
        Referral.status == "pending"
    ).first()
    
    if referral:
        # Обновить статус и начислить награды
        referral.status = "completed"
        referral.converted_at = datetime.now()
        # ... остальная логика ...
    
    return {"success": True, "subscription": subscription}
"""

