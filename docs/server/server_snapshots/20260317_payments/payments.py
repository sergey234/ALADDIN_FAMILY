"""
Endpoints для обработки платежей
Интеграция с реферальной программой
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid
import os
import hmac
import hashlib
import json
import base64
from io import BytesIO

from app.database.database import get_db
from app.referral_payment_functions import (
    process_referral_code_on_payment,
    process_referral_on_payment_confirmation,
    apply_referral_discount
)
import secrets
import string

# QR generation (РФ-оплата через банковский QR)
try:
    import qrcode  # type: ignore
except Exception:
    qrcode = None  # type: ignore

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


class PaymentConfirmRequest(BaseModel):
    """
    Подтверждение оплаты (webhook/внутренний callback).

    Важно: этот endpoint должен быть защищён подписью (HMAC) и быть идемпотентным.
    """
    eventId: str
    provider: str  # e.g. "bank_qr_manual" / "sbp" / "sberpay"
    providerTxnId: Optional[str] = None
    paymentId: str
    amount: float
    currency: str = "RUB"
    paidAt: Optional[str] = None  # ISO timestamp (optional)


class PaymentQRCreateRequest(PaymentCreateRequest):
    """
    Создание платежа + возврат QR (РФ: СБП/SberPay).
    """
    # paymentMethod ожидается: "sbp" | "sberpay"
    pass

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


@router.post("/api/payments/qr/create")
async def create_payment_qr(
    payment_data: PaymentQRCreateRequest,
    db: Session = Depends(get_db)
):
    """
    РФ-оплата: создать платеж и вернуть QR для банковского перевода (СБП/SberPay).

    Примечание: подтверждение оплаты НЕ происходит автоматически — оно должно приходить
    через защищённый /api/payments/confirm.
    """
    # Создаем payment как обычно
    base = await create_payment(payment_data, db)

    # Генерируем QR data (СБП/SberPay). Реквизиты берём из env (с дефолтами).
    method = (payment_data.paymentMethod or "").lower().strip() or "sbp"
    merchant_phone = os.getenv("PAYMENT_MERCHANT_PHONE", "+79277020379").strip()
    description = f"ALADDIN subscription {payment_data.tariffId} ({payment_data.periodMonths}m)"

    amount = float(payment_data.amount)
    # NOTE: форматы URL могут отличаться у банков, но это базовый рабочий “deeplink” формат,
    # который используется многими банковскими приложениями для QR-перевода.
    if method == "sberpay":
        qr_code_data = f"sberbank://transfer?phone={merchant_phone}&amount={amount}&comment={description}"
        provider = "SberPay"
    else:
        qr_code_data = f"sbp://{merchant_phone}?sum={amount}&comment={description}"
        provider = "SBP"

    qr_image_b64 = None
    if qrcode is not None:
        img = qrcode.make(qr_code_data)
        buf = BytesIO()
        img.save(buf, format="PNG")
        qr_image_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return {
        **base,
        "qr": {
            "provider": provider,
            "qr_code_data": qr_code_data,
            "qr_code_image_base64": qr_image_b64,
            "instructions": "Отсканируйте QR-код в приложении вашего банка (СБП/SberPay) и выполните перевод.",
            "merchant_info": {"phone": merchant_phone},
        }
    }


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
    request: Request,
    payload: PaymentConfirmRequest,
    db: Session = Depends(get_db)
):
    """
    Подтверждение платежа (webhook/внутренний callback).

    Security:
    - Требует HMAC подпись.
      Заголовки:
        - X-Timestamp: unix seconds
        - X-Signature: hex(hmac_sha256(secret, f\"{ts}.{raw_body}\"))
    - Идемпотентность: eventId/providerTxnId фиксируются в payment_webhook_events.
    """
    try:
        inserted_event = False
        # 0) Verify signature (HMAC)
        secret = os.getenv("PAYMENT_WEBHOOK_SECRET", "").strip()
        if not secret:
            raise HTTPException(status_code=503, detail="PAYMENT_WEBHOOK_SECRET is not configured")

        ts_raw = request.headers.get("X-Timestamp")
        sig = request.headers.get("X-Signature", "")
        if not ts_raw or not sig:
            raise HTTPException(status_code=401, detail="Missing X-Timestamp or X-Signature")

        try:
            ts = int(ts_raw)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid X-Timestamp")

        now = int(datetime.now(tz=timezone.utc).timestamp())
        if abs(now - ts) > 300:
            raise HTTPException(status_code=401, detail="Timestamp skew too large")

        raw_body = await request.body()
        msg = f"{ts_raw}.".encode("utf-8") + raw_body
        expected = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # 1) Ensure idempotency storage exists
        # Note: Using portable SQL for sqlite/postgres via CREATE TABLE/INDEX IF NOT EXISTS.
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS payment_webhook_events (
                event_id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                provider_txn_id TEXT NULL,
                payment_id TEXT NOT NULL,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        db.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_payment_webhook_provider_txn
            ON payment_webhook_events (provider, provider_txn_id)
        """))
        db.commit()

        # 2) Insert event (idempotency). If exists -> return ok.
        try:
            db.execute(
                text("""
                    INSERT INTO payment_webhook_events (event_id, provider, provider_txn_id, payment_id)
                    VALUES (:event_id, :provider, :provider_txn_id, :payment_id)
                """),
                {
                    "event_id": payload.eventId,
                    "provider": payload.provider,
                    "provider_txn_id": payload.providerTxnId,
                    "payment_id": payload.paymentId,
                }
            )
            db.commit()
            inserted_event = True
        except Exception:
            db.rollback()
            # Event already processed (or provider_txn_id conflict) -> idempotent OK
            return {"status": "ok", "message": "Already processed"}

        # 3) Validate payment exists + amount/currency match
        row = db.execute(
            text("SELECT amount, currency, status FROM payments WHERE payment_id = :payment_id"),
            {"payment_id": payload.paymentId},
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Payment not found")

        db_amount = float(row[0])
        db_currency = (row[1] or "").upper()
        db_status = row[2]

        if db_currency != (payload.currency or "").upper():
            raise HTTPException(status_code=400, detail="Currency mismatch")
        if abs(db_amount - float(payload.amount)) > 0.01:
            raise HTTPException(status_code=400, detail="Amount mismatch")
        if db_status != "pending":
            return {"status": "ok", "message": f"Payment already in status={db_status}"}

        # 1. Обновить статус платежа
        result = db.execute(
            text("""
                UPDATE payments
                SET status = 'paid', paid_at = NOW()
                WHERE payment_id = :payment_id AND status = 'pending'
                RETURNING user_id, amount, referral_id
            """),
            {"payment_id": payload.paymentId}
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
            print(f"⚠️ Платеж {payload.paymentId} имеет referral_code, но user_id отсутствует. Реферальная программа будет обработана позже.")
        
        # 3. ✅ Генерировать код активации (если еще не создан)
        existing_code = db.execute(
            text("SELECT id FROM activation_codes WHERE payment_id = :payment_id"),
            {"payment_id": payload.paymentId}
        ).fetchone()
        
        if not existing_code:
            # Получаем данные платежа для создания кода
            payment_data = db.execute(
                text("SELECT user_alias, tariff_id FROM payments WHERE payment_id = :payment_id"),
                {"payment_id": payload.paymentId}
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
                        "payment_id": payload.paymentId,
                        "user_alias": user_alias,
                        "tariff_id": tariff_id,
                        "expires_at": expires_at
                    }
                )
                print(f"✅ Создан код активации: {activation_code} для платежа {payload.paymentId}")
        
        db.commit()
        
        return {"status": "ok", "message": "Payment confirmed"}
        
    except HTTPException:
        # если мы уже записали event, но дальше упали — удаляем event, чтобы можно было повторить
        try:
            if "inserted_event" in locals() and inserted_event:
                db.execute(text("DELETE FROM payment_webhook_events WHERE event_id = :event_id"), {"event_id": payload.eventId})
                db.commit()
        except Exception:
            db.rollback()
        raise
    except Exception as e:
        # если мы уже записали event, но дальше упали — удаляем event, чтобы можно было повторить
        try:
            if "inserted_event" in locals() and inserted_event:
                db.execute(text("DELETE FROM payment_webhook_events WHERE event_id = :event_id"), {"event_id": payload.eventId})
                db.commit()
            else:
                db.rollback()
        except Exception:
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

