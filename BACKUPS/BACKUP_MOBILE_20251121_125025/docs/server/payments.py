"""
Endpoints для обработки платежей
Интеграция с реферальной программой
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid

from app.database.database import get_db
from app.referral_payment_functions import (
    process_referral_code_on_payment,
    process_referral_on_payment_confirmation,
    apply_referral_discount
)
import secrets
import string

router = APIRouter(tags=["payments"])

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def generate_activation_code() -> str:
    """
    Генерация кода активации в формате ALDN-XXXX-XXXX-XXXX
    """
    # Генерируем 12 случайных символов (буквы и цифры)
    chars = string.ascii_uppercase + string.digits
    code_part = ''.join(secrets.choice(chars) for _ in range(12))
    
    # Форматируем как ALDN-XXXX-XXXX-XXXX
    formatted_code = f"ALDN-{code_part[:4]}-{code_part[4:8]}-{code_part[8:12]}"
    return formatted_code

# ============================================
# МОДЕЛИ ЗАПРОСОВ
# ============================================

class PaymentCreateRequest(BaseModel):
    """Запрос на создание платежа (для лендинга)"""
    tariffId: str
    userAlias: str
    pin: str
    paymentMethod: str
    periodMonths: int
    amount: float
    referralCode: Optional[str] = None
    personalDataConsent: bool = True
    consentTimestamp: Optional[str] = None
    consentIP: Optional[str] = None

class PaymentStatusResponse(BaseModel):
    """Ответ со статусом платежа"""
    paymentId: str
    status: str
    amount: float
    currency: str
    paidAt: Optional[str] = None

class PaymentRecoveryRequest(BaseModel):
    """Запрос на восстановление кода активации"""
    userAlias: str
    pin: str

# ============================================
# ENDPOINTS
# ============================================

@router.post("/api/payments/create")
async def create_payment(
    payment_data: PaymentCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Создание платежа (для лендинга)
    
    Используется сайтом aladdin-ai.ru
    Поддерживает анонимные платежи (без user_id)
    """
    try:
        # 1. Генерируем уникальный payment_id
        payment_id = f"PAY_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8].upper()}"
        
        # 2. Вычисляем expires_at (30 минут)
        expires_at = datetime.now() + timedelta(minutes=30)
        
        # 3. Создаем запись в payments
        db.execute(
            text("""
                INSERT INTO payments (
                    payment_id, user_alias, tariff_id, amount, currency,
                    payment_method, period_months, status, referral_code, expires_at
                )
                VALUES (
                    :payment_id, :user_alias, :tariff_id, :amount, :currency,
                    :payment_method, :period_months, :status, :referral_code, :expires_at
                )
            """),
            {
                "payment_id": payment_id,
                "user_alias": payment_data.userAlias,
                "tariff_id": payment_data.tariffId,
                "amount": payment_data.amount,
                "currency": "RUB",
                "payment_method": payment_data.paymentMethod,
                "period_months": payment_data.periodMonths,
                "status": "pending",
                "referral_code": payment_data.referralCode,
                "expires_at": expires_at
            }
        )
        db.commit()
        
        # 4. ✅ Обработать реферальный код (если есть)
        # Примечание: для анонимных платежей user_id = None, поэтому реферальная программа
        # будет обработана позже, когда пользователь зарегистрируется или при подтверждении платежа
        referral_id = None
        if payment_data.referralCode:
            # Для анонимных платежей (без user_id) реферальная программа будет обработана
            # позже при подтверждении платежа, когда user_id станет известен
            # referral_id останется None до подтверждения платежа
            # Это нормально - реферальная программа обработается в /api/payments/confirm
            pass
        
        # 5. Возвращаем данные для оплаты
        return {
            "paymentId": payment_id,
            "amount": payment_data.amount,
            "currency": "RUB",
            "expiresAt": expires_at.isoformat(),
            "status": "pending",
            "referralCode": payment_data.referralCode,
            "referralId": referral_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка создания платежа: {str(e)}")


@router.get("/api/payments/status/{payment_id}")
async def check_payment_status(
    payment_id: str,
    db: Session = Depends(get_db)
):
    """
    Проверка статуса платежа
    """
    try:
        result = db.execute(
            text("""
                SELECT payment_id, status, amount, currency, paid_at, referral_id, user_id
                FROM payments
                WHERE payment_id = :payment_id
            """),
            {"payment_id": payment_id}
        )
        payment = result.fetchone()
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # ✅ Если платеж оплачен, обработать реферальную программу
        if payment[1] == "paid" and payment[5]:  # status == "paid" and referral_id
            referral_id = payment[5]
            user_id = payment[6]  # user_id
            amount = float(payment[2])
            
            # Проверяем, не обработан ли уже
            referral_check = db.execute(
                text("SELECT status FROM referrals WHERE id = :referral_id"),
                {"referral_id": referral_id}
            ).fetchone()
            
            if referral_check and referral_check[0] == "pending" and user_id:
                # Обрабатываем реферальную программу
                process_referral_on_payment_confirmation(db, user_id, amount)
        
        # ✅ Получить код активации (если есть)
        activation_code_result = db.execute(
            text("""
                SELECT activation_code, expires_at
                FROM activation_codes
                WHERE payment_id = :payment_id AND status = 'active'
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"payment_id": payment_id}
        )
        activation_code_row = activation_code_result.fetchone()
        
        activation_code = None
        code_expires_at = None
        if activation_code_row:
            activation_code = activation_code_row[0]
            code_expires_at = activation_code_row[1].isoformat() if activation_code_row[1] else None
        
        return {
            "paymentId": payment[0],
            "status": payment[1],
            "amount": float(payment[2]),
            "currency": payment[3],
            "paidAt": payment[4].isoformat() if payment[4] else None,
            "activationCode": activation_code,
            "codeExpiresAt": code_expires_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка проверки статуса: {str(e)}")


@router.post("/api/payments/confirm")
async def confirm_payment(
    payment_id: str,
    db: Session = Depends(get_db)
):
    """
    Подтверждение платежа (webhook от платежной системы)
    """
    try:
        # 1. Обновить статус платежа
        result = db.execute(
            text("""
                UPDATE payments
                SET status = 'paid', paid_at = NOW()
                WHERE payment_id = :payment_id AND status = 'pending'
                RETURNING user_id, amount, referral_id
            """),
            {"payment_id": payment_id}
        )
        payment = result.fetchone()
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found or already processed")
        
        user_id = payment[0]  # user_id (может быть None для анонимных платежей)
        amount = float(payment[1])
        referral_id = payment[2]
        
        # 2. ✅ Обработать реферальную программу (если есть user_id и referral_id)
        if referral_id and user_id:
            process_referral_on_payment_confirmation(db, user_id, amount)
        elif referral_id:
            # Если user_id нет, но есть referral_code, попробуем найти пользователя по alias
            # и обработать реферальную программу позже
            # Пока просто логируем
            print(f"⚠️ Платеж {payment_id} имеет referral_code, но user_id отсутствует. Реферальная программа будет обработана позже.")
        
        # 3. ✅ Генерировать код активации (если еще не создан)
        existing_code = db.execute(
            text("SELECT id FROM activation_codes WHERE payment_id = :payment_id"),
            {"payment_id": payment_id}
        ).fetchone()
        
        if not existing_code:
            # Получаем данные платежа для создания кода
            payment_data = db.execute(
                text("SELECT user_alias, tariff_id FROM payments WHERE payment_id = :payment_id"),
                {"payment_id": payment_id}
            ).fetchone()
            
            if payment_data:
                user_alias = payment_data[0]
                tariff_id = payment_data[1]
                
                # Генерируем уникальный код активации
                activation_code = generate_activation_code()
                expires_at = datetime.now() + timedelta(days=30)  # Код действителен 30 дней
                
                # Проверяем уникальность кода
                max_attempts = 10
                attempts = 0
                while attempts < max_attempts:
                    code_check = db.execute(
                        text("SELECT id FROM activation_codes WHERE activation_code = :code"),
                        {"code": activation_code}
                    ).fetchone()
                    
                    if not code_check:
                        break  # Код уникален
                    
                    activation_code = generate_activation_code()
                    attempts += 1
                
                # Создаем запись в activation_codes
                db.execute(
                    text("""
                        INSERT INTO activation_codes (
                            activation_code, payment_id, user_alias, tariff_id, expires_at
                        )
                        VALUES (
                            :activation_code, :payment_id, :user_alias, :tariff_id, :expires_at
                        )
                    """),
                    {
                        "activation_code": activation_code,
                        "payment_id": payment_id,
                        "user_alias": user_alias,
                        "tariff_id": tariff_id,
                        "expires_at": expires_at
                    }
                )
                print(f"✅ Создан код активации: {activation_code} для платежа {payment_id}")
        
        db.commit()
        
        return {"status": "ok", "message": "Payment confirmed"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка подтверждения платежа: {str(e)}")


@router.post("/api/payments/recover")
async def recover_payment_code(
    recovery_data: PaymentRecoveryRequest,
    db: Session = Depends(get_db)
):
    """
    Восстановление кода активации по user_alias и pin
    
    Используется для восстановления кода активации, если пользователь его потерял.
    Ищет платежи в таблице payments по user_alias (pin используется для проверки в будущем).
    """
    try:
        # 1. Ищем платежи по user_alias
        result = db.execute(
            text("""
                SELECT payment_id, tariff_id, amount, status, created_at, paid_at
                FROM payments
                WHERE user_alias = :user_alias
                  AND status = 'paid'
                ORDER BY paid_at DESC
                LIMIT 1
            """),
            {"user_alias": recovery_data.userAlias}
        )
        payment = result.fetchone()
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found or not paid")
        
        payment_id = payment[0]
        
        # 2. Ищем код активации для этого платежа
        activation_result = db.execute(
            text("""
                SELECT activation_code, expires_at
                FROM activation_codes
                WHERE payment_id = :payment_id AND status = 'active'
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"payment_id": payment_id}
        )
        activation_code_row = activation_result.fetchone()
        
        if not activation_code_row:
            raise HTTPException(status_code=404, detail="Activation code not found for this payment")
        
        activation_code = activation_code_row[0]
        expires_at = activation_code_row[1]
        
        # 3. Проверяем, не истек ли код
        if expires_at and expires_at < datetime.now():
            raise HTTPException(status_code=410, detail="Activation code has expired")
        
        # 4. В будущем здесь можно добавить проверку pin
        # Например, сохранить хеш pin в таблице payments или отдельной таблице
        
        return {
            "paymentId": payment_id,
            "tariffId": payment[1],
            "amount": float(payment[2]),
            "status": payment[3],
            "createdAt": payment[4].isoformat() if payment[4] else None,
            "paidAt": payment[5].isoformat() if payment[5] else None,
            "activationCode": activation_code,
            "expiresAt": expires_at.isoformat() if expires_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка восстановления: {str(e)}")


@router.post("/api/activation/retrieve")
async def retrieve_activation_code(
    recovery_data: PaymentRecoveryRequest,
    db: Session = Depends(get_db)
):
    """
    Получение кода активации по user_alias и pin (для success.html)
    
    Алиас для /api/payments/recover
    """
    return await recover_payment_code(recovery_data, db)

