"""
Тестовые endpoints для проверки функций реферальной программы
Используется для тестирования до интеграции в основной код платежей
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database.database import get_db
from app.auth.auth import get_current_user
from app.referral_payment_functions import (
    process_referral_code_on_payment,
    process_referral_on_payment_confirmation,
    apply_referral_discount
)

router = APIRouter(prefix="/api/referral/test", tags=["referral-test"])

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
    """
    Тестовый endpoint для проверки обработки referralCode при создании платежа.
    
    Использование:
        POST /api/referral/test/payment/create
        {
            "tariff_id": "premium",
            "period": 1,
            "amount": 800.0,
            "referralCode": "ABC123"
        }
    """
    try:
        # Применить скидку рефереру (если есть активная скидка)
        final_price = apply_referral_discount(db, current_user["id"], payment_data.amount)
        
        # Обработать referralCode
        referral_id = None
        if payment_data.referralCode:
            referral_id = process_referral_code_on_payment(
                db,
                payment_data.referralCode,
                current_user["id"],
                final_price
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
    """
    Тестовый endpoint для проверки обработки реферальной программы при подтверждении оплаты.
    
    Использование:
        POST /api/referral/test/payment/confirm
        {
            "payment_id": "test_payment_123",
            "user_id": 101,
            "amount": 800.0
        }
    """
    try:
        # Обработать реферальную программу
        result = process_referral_on_payment_confirmation(
            db,
            payment_data.user_id,
            payment_data.amount
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

@router.post("/discount/apply")
async def test_apply_discount(
    original_price: float,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Тестовый endpoint для проверки применения скидки рефереру.
    
    Использование:
        POST /api/referral/test/discount/apply?original_price=1000.0
    """
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

