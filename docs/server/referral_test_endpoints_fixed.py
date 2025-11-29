"""
Тестовые endpoints для проверки функций реферальной программы
Используется для тестирования до интеграции в основной код платежей
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

from app.database.database import get_db
from app.auth.auth import get_current_user

router = APIRouter(prefix="/api/referral/test", tags=["referral-test"])

# ============================================
# ВСТРОЕННЫЕ ФУНКЦИИ (чтобы не зависеть от импорта)
# ============================================

def process_referral_code_on_payment(
    db: Session,
    referral_code: Optional[str],
    payment_user_id: int,
    payment_amount: float
) -> Optional[int]:
    """Обработать реферальный код при создании платежа."""
    if not referral_code:
        return None
    
    try:
        result = db.execute(
            text("SELECT user_id, code FROM referral_codes WHERE code = :code"),
            {"code": referral_code}
        )
        referral_code_obj = result.fetchone()
        
        if not referral_code_obj:
            return None
        
        referrer_id = referral_code_obj[0]
        
        if referrer_id == payment_user_id:
            return None
        
        original_price = payment_amount / 0.8
        discount_applied = original_price - payment_amount
        
        result = db.execute(
            text("""
                INSERT INTO referrals (referrer_id, invited_user_id, referral_code, status, discount_applied)
                VALUES (:referrer_id, :invited_user_id, :referral_code, 'pending', :discount_applied)
                ON CONFLICT (referrer_id, invited_user_id) DO NOTHING
                RETURNING id
            """),
            {
                "referrer_id": referrer_id,
                "invited_user_id": payment_user_id,
                "referral_code": referral_code,
                "discount_applied": discount_applied
            }
        )
        
        referral_id_row = result.fetchone()
        if referral_id_row:
            db.commit()
            return referral_id_row[0]
        else:
            existing = db.execute(
                text("SELECT id FROM referrals WHERE referrer_id = :referrer_id AND invited_user_id = :invited_user_id"),
                {"referrer_id": referrer_id, "invited_user_id": payment_user_id}
            ).fetchone()
            return existing[0] if existing else None
            
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        return None

def process_referral_on_payment_confirmation(
    db: Session,
    payment_user_id: int,
    payment_amount: float
) -> bool:
    """Обработать реферальную программу при подтверждении оплаты."""
    try:
        result = db.execute(
            text("""
                SELECT id, referrer_id, referral_code, status, discount_applied
                FROM referrals
                WHERE invited_user_id = :user_id AND status = 'pending'
                LIMIT 1
            """),
            {"user_id": payment_user_id}
        )
        referral = result.fetchone()
        
        if not referral or referral[3] != "pending":
            return False
        
        referral_id = referral[0]
        referrer_id = referral[1]
        original_price = payment_amount / 0.8
        reward_amount = original_price * 0.2
        
        db.execute(
            text("""
                UPDATE referrals
                SET status = 'completed', converted_at = NOW(), reward_amount = :reward_amount
                WHERE id = :referral_id
            """),
            {"referral_id": referral_id, "reward_amount": reward_amount}
        )
        
        now = datetime.now()
        if now.month == 12:
            next_month_start = datetime(now.year + 1, 1, 1)
            next_month_end = datetime(now.year + 1, 2, 1) - timedelta(days=1)
        else:
            next_month_start = datetime(now.year, now.month + 1, 1)
            if now.month + 1 == 12:
                next_month_end = datetime(now.year + 1, 1, 1) - timedelta(days=1)
            else:
                next_month_end = datetime(now.year, now.month + 2, 1) - timedelta(days=1)
        
        db.execute(
            text("""
                INSERT INTO referral_discounts (user_id, discount_percent, valid_from, valid_until, referral_id)
                VALUES (:user_id, 20.0, :valid_from, :valid_until, :referral_id)
            """),
            {
                "user_id": referrer_id,
                "valid_from": next_month_start,
                "valid_until": next_month_end,
                "referral_id": referral_id
            }
        )
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        return False

def apply_referral_discount(
    db: Session,
    user_id: int,
    original_price: float
) -> float:
    """Применить реферальную скидку -20% к цене для реферера."""
    try:
        result = db.execute(
            text("""
                SELECT id, discount_percent
                FROM referral_discounts
                WHERE user_id = :user_id AND valid_until >= NOW() AND used_at IS NULL
                ORDER BY valid_until ASC LIMIT 1
            """),
            {"user_id": user_id}
        )
        discount = result.fetchone()
        
        if not discount:
            return original_price
        
        discount_percent = float(discount[1])
        discount_amount = original_price * (discount_percent / 100)
        final_price = original_price - discount_amount
        
        db.execute(
            text("UPDATE referral_discounts SET used_at = NOW() WHERE id = :discount_id"),
            {"discount_id": discount[0]}
        )
        db.commit()
        
        return final_price
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        return original_price

# ============================================
# МОДЕЛИ
# ============================================

class TestPaymentCreate(BaseModel):
    tariff_id: str
    period: int
    amount: float
    referralCode: Optional[str] = None

class TestPaymentConfirm(BaseModel):
    payment_id: str
    user_id: int
    amount: float

# ============================================
# ENDPOINT 1: Тест создания платежа с referralCode
# ============================================

@router.post("/payment/create")
async def test_create_payment(
    payment_data: TestPaymentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Тестовый endpoint для проверки обработки referralCode при создании платежа."""
    try:
        final_price = apply_referral_discount(db, current_user["id"], payment_data.amount)
        
        referral_id = None
        if payment_data.referralCode:
            referral_id = process_referral_code_on_payment(
                db, payment_data.referralCode, current_user["id"], final_price
            )
        
        return {
            "success": True,
            "user_id": current_user["id"],
            "original_amount": payment_data.amount,
            "final_amount": final_price,
            "referral_id": referral_id,
            "referral_code": payment_data.referralCode,
            "message": "Платеж создан успешно (тест)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

# ============================================
# ENDPOINT 2: Тест подтверждения платежа
# ============================================

@router.post("/payment/confirm")
async def test_confirm_payment(
    payment_data: TestPaymentConfirm,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Тестовый endpoint для проверки обработки реферальной программы при подтверждении оплаты."""
    try:
        result = process_referral_on_payment_confirmation(
            db, payment_data.user_id, payment_data.amount
        )
        
        return {
            "success": result,
            "payment_id": payment_data.payment_id,
            "user_id": payment_data.user_id,
            "amount": payment_data.amount,
            "message": "Платеж подтвержден, реферальная программа обработана" if result else "Реферальная программа не обработана (нет pending referral)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

# ============================================
# ENDPOINT 3: Тест применения скидки
# ============================================

@router.get("/discount/apply")
async def test_apply_discount(
    original_price: float,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Тестовый endpoint для проверки применения скидки рефереру."""
    try:
        final_price = apply_referral_discount(db, current_user["id"], original_price)
        discount_applied = original_price - final_price
        
        return {
            "success": True,
            "user_id": current_user["id"],
            "original_price": original_price,
            "final_price": final_price,
            "discount_applied": discount_applied,
            "discount_percent": (discount_applied / original_price * 100) if original_price > 0 else 0,
            "has_active_discount": discount_applied > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


