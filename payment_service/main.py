"""
Aladdin Payment Service - FastAPI Backend
Основной файл приложения для обработки платежей
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Header, Request, Body
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings, verify_webhook_signature
from app.database import get_session, engine
from app.models import Base, Payment, ActivationCode
from app.schemas import PaymentCreateRequest
from app.payment_methods import list_payment_methods, get_payment_method
from app.providers.mock_psp import provider
from app.utils import hash_pin, verify_pin, generate_activation_code, code_expiration, now_utc
from app.rate_limit import get_rate_limiter
from app.config import settings
from fastapi import HTTPException as FastAPIHTTPException

app = FastAPI(title="Aladdin Payment Service", version="1.0.0")


# Инициализация базы данных
@app.on_event("startup")
async def init_db():
    """Создание таблиц при запуске"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Middleware для CORS (если нужно)
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    """Добавляет CORS заголовки"""
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key, X-Signature, X-Admin-Key"
    return response


# Проверка API ключа
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Проверка API ключа из заголовка"""
    if not x_api_key or x_api_key != settings.api_key_public:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


async def verify_admin_key(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    """Проверка админского ключа"""
    if not x_admin_key or x_admin_key != settings.admin_key:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    return x_admin_key


async def finalize_payment(session: AsyncSession, payment: Payment) -> ActivationCode:
    """Помечает платёж оплаченным и создаёт (или возвращает) код активации."""
    payment.status = "paid"
    activation_result = await session.execute(
        select(ActivationCode).where(ActivationCode.payment_id == payment.id)
    )
    activation = activation_result.scalar_one_or_none()
    if activation:
        return activation

    code = generate_activation_code()
    activation = ActivationCode(
        code=code,
        payment_id=payment.id,
        alias=payment.alias,
        tariff_id=payment.tariff_id,
        expires_at=code_expiration(30),
        status="active",
    )
    session.add(activation)
    await session.flush()
    return activation


# Эндпоинты

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"service": "Aladdin Payment Service", "version": "1.0.0", "status": "running"}


@app.get("/api/payment-methods")
async def get_payment_methods(show_all: bool = False):
    """
    Возвращает список доступных методов оплаты
    
    Args:
        show_all: Если True, возвращает все методы (включая скрытые).
                 Если False (по умолчанию), возвращает только видимые методы.
    
    По умолчанию возвращает только видимые методы (ТОП-5):
    - СБП (qr_sbp)
    - SberPay (sberpay)
    - Банковские карты (card_*)
    - Tinkoff Pay (tinkoff_pay)
    - Ручной перевод (manual_transfer)
    """
    if show_all:
        from app.payment_methods import list_all_payment_methods
        methods = list_all_payment_methods()
    else:
        methods = list_payment_methods()
    
    return {
        "methods": methods,
        "total": len(methods),
        "visible_only": not show_all
    }


@app.get("/api/manual-transfer/info")
async def get_manual_transfer_info():
    """Возвращает информацию для ручного перевода (номер карты)"""
    return {
        "card_number": settings.card_number,
        "card_holder_name": settings.card_holder_name
    }


@app.post("/api/payments/create")
async def create_payment(
    request_data: dict = Body(...),
    session: AsyncSession = Depends(get_session),
    api_key: str = Depends(verify_api_key)
):
    # Парсим запрос с поддержкой camelCase
    print(f"🔵 create_payment: Получен запрос")
    print(f"   - Данные: {request_data}")
    try:
        # Конвертируем camelCase в snake_case
        converted_data = {}
        mapping = {
            "tariffId": "tariff_id",
            "userAlias": "user_alias",
            "paymentMethod": "payment_method",
            "periodMonths": "period_months",
            "personalDataConsent": "personal_data_consent",
            "consentTimestamp": "consent_timestamp",
            "consentIP": "consent_ip",
            "referralCode": "referral_code"
        }
        
        for key, value in request_data.items():
            if key in mapping:
                converted_data[mapping[key]] = value
            else:
                converted_data[key] = value
        
        request = PaymentCreateRequest(**converted_data)
        print(f"✅ Запрос успешно распарсен")
        print(f"   - tariff_id: {request.tariff_id}")
        print(f"   - user_alias: {request.user_alias}")
        print(f"   - payment_method: {request.payment_method}")
    except Exception as e:
        print(f"❌ Ошибка парсинга запроса: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=f"Ошибка валидации данных: {str(e)}")
    """
    Создает новый платеж
    
    Требует:
    - X-API-Key заголовок
    - Согласие на обработку ПДн (personal_data_consent: true)
    """
    # Проверка согласия на обработку ПДн
    if not request.personal_data_consent:
        raise HTTPException(
            status_code=400,
            detail="Согласие на обработку персональных данных обязательно (152-ФЗ)"
        )
    
    # Проверка метода оплаты
    method = get_payment_method(request.payment_method)
    if not method:
        raise HTTPException(status_code=400, detail=f"Неизвестный метод оплаты: {request.payment_method}")
    
    # Создание платежа в БД
    payment = Payment(
        alias=request.user_alias,
        pin_hash=hash_pin(request.pin),
        tariff_id=request.tariff_id,
        amount=int(request.amount * 100),  # Конвертируем в копейки
        payment_method=request.payment_method,
        status="created",
        # ✅ Сохранение согласия на обработку ПДн
        personal_data_consent=True,
        consent_timestamp=datetime.fromisoformat(request.consent_timestamp.replace('Z', '+00:00')) if request.consent_timestamp else now_utc(),
        consent_ip=request.consent_ip
    )
    
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    
    # Создание платежа в PSP (провайдере)
    if request.payment_method == "manual_transfer":
        # Для ручного перевода не нужен PSP
        response_data = {
            "payment_id": payment.id,
            "paymentId": payment.id,  # ✅ Поддержка обоих форматов для совместимости
            "status": "pending",
            "method": "manual_transfer",
            "card_number": settings.card_number,
            "cardNumber": settings.card_number,  # ✅ Поддержка обоих форматов
            "card_holder_name": settings.card_holder_name,
            "cardHolderName": settings.card_holder_name,  # ✅ Поддержка обоих форматов
            "amount": request.amount,
            "expires_at": code_expiration(7).isoformat()
        }
    else:
        # Для других методов создаем платеж в PSP
        psp_result = await provider.create_payment(
            amount=int(request.amount * 100),
            currency="RUB"
        )
        
        payment.psp_payment_id = psp_result["payment_id"]
        await session.commit()
        
        response_data = {
            "payment_id": payment.id,
            "paymentId": payment.id,  # ✅ Поддержка обоих форматов для совместимости
            "redirect_url": psp_result["redirect_url"],
            "redirectUrl": psp_result["redirect_url"],  # ✅ Поддержка обоих форматов
            "qr_data": psp_result.get("qr_data"),
            "qrData": psp_result.get("qr_data"),  # ✅ Поддержка обоих форматов
            "expires_at": psp_result["expires_at"].isoformat(),
            "status": "created"
        }
    
    return response_data


@app.get("/api/payments/status/{payment_id}")
async def get_payment_status(
    payment_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Возвращает текущий статус платежа и (если доступно) код активации.
    """
    result = await session.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Нормализуем статус для фронтенда
    normalized_status = payment.status
    if payment.payment_method == "manual_transfer" and payment.status in {"created", "pending"}:
        normalized_status = "awaiting_manual_payment"
    elif payment.payment_method != "manual_transfer" and payment.status in {"created", "pending"}:
        normalized_status = "awaiting_payment"

    # Ищем код активации, если платеж уже оплачен
    activation_code_value = None
    activation_expires_at = None
    if payment.status == "paid":
        activation_result = await session.execute(
            select(ActivationCode).where(ActivationCode.payment_id == payment.id)
        )
        activation = activation_result.scalar_one_or_none()
        if activation:
            activation_code_value = activation.code
            activation_expires_at = activation.expires_at.isoformat()

    amount_rub = payment.amount / 100 if payment.amount is not None else None

    response = {
        "payment_id": payment.id,
        "paymentId": payment.id,
        "status": normalized_status,
        "raw_status": payment.status,
        "amount": amount_rub,
        "alias": payment.alias,
        "method": payment.payment_method,
        "card_number": settings.card_number if payment.payment_method == "manual_transfer" else None,
        "card_holder_name": settings.card_holder_name if payment.payment_method == "manual_transfer" else None,
        "activation_code": activation_code_value,
        "activationCode": activation_code_value,
        "code_expires_at": activation_expires_at,
        "codeExpiresAt": activation_expires_at,
        "updated_at": payment.updated_at.isoformat() if getattr(payment, "updated_at", None) else None,
    }

    return response


@app.post("/api/payments/confirm")
async def confirm_payment(
    request: Request,
    session: AsyncSession = Depends(get_session),
    x_signature: Optional[str] = Header(None, alias="X-Signature")
):
    """
    Webhook от банка для подтверждения платежа
    
    Требует:
    - X-Signature заголовок для проверки подписи
    """
    body = await request.body()
    
    # Проверка подписи
    if not verify_webhook_signature(body, x_signature or "", settings.webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Парсинг данных webhook (заглушка - нужно адаптировать под реальный формат)
    import json
    data = await request.json()
    
    payment_id = data.get("payment_id")
    psp_txn_id = data.get("pspTxnId")
    status = data.get("status")
    
    if status != "paid":
        return {"status": "ignored", "reason": f"Status is {status}, not 'paid'"}
    
    # Поиск платежа
    result = await session.execute(
        select(Payment).where(Payment.psp_payment_id == psp_txn_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.status == "paid":
        # Idempotency: уже обработан
        return {"status": "already_processed", "payment_id": payment.id}
    
    # Обновление статуса
    payment.status = "paid"
    await session.commit()
    
    # Генерация кода активации
    code = generate_activation_code()
    activation = ActivationCode(
        code=code,
        payment_id=payment.id,
        expires_at=code_expiration(30)
    )
    session.add(activation)
    await session.commit()
    
    return {
        "status": "confirmed",
        "payment_id": payment.id,
        "activation_code": code
    }


@app.post("/api/admin/payments/{payment_id}/mark-paid")
async def admin_mark_paid(
    payment_id: str,
    session: AsyncSession = Depends(get_session),
    admin_key: str = Depends(verify_admin_key)
):
    """
    Админский endpoint для ручного подтверждения платежа и генерации кода.
    Использовать только для тестов/ручной поддержки.
    """
    result = await session.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    activation = await finalize_payment(session, payment)
    await session.commit()

    return {
        "status": "paid",
        "payment_id": payment.id,
        "activation_code": activation.code,
        "expires_at": activation.expires_at.isoformat()
    }


@app.post("/api/activation/retrieve")
async def retrieve_activation_code(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """
    Получение кода активации по alias и PIN
    
    Защищено rate limiting (5 запросов/минуту)
    Поддерживает query параметры и JSON body
    """
    # Поддерживаем оба формата: query параметры и JSON body
    alias = None
    pin = None
    
    # Пробуем получить из query параметров
    alias = request.query_params.get("alias")
    pin = request.query_params.get("pin")
    
    # Если нет в query, пробуем из JSON body
    if not alias or not pin:
        try:
            if request.headers.get("content-type", "").startswith("application/json"):
                data = await request.json()
                alias = alias or data.get("alias") or data.get("userAlias")
                pin = pin or data.get("pin")
        except Exception as e:
            print(f"⚠️ Не удалось прочитать JSON body: {e}")
    
    if not alias or not pin:
        raise HTTPException(status_code=400, detail="Alias and PIN are required (as query params or JSON body)")
    
    print(f"🔵 retrieve_activation_code: alias={alias}, pin=***")
    
    # Rate limiting
    client_ip = request.client.host
    rate_limiter = get_rate_limiter(
        settings.rate_limit_retrieve_max,
        settings.rate_limit_retrieve_window
    )
    is_allowed, remaining = rate_limiter.is_allowed(f"{alias}:{client_ip}")
    if not is_allowed:
        raise FastAPIHTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later.",
            headers={"X-RateLimit-Remaining": "0"}
        )
    
    # Поиск платежа
    result = await session.execute(
        select(Payment).where(Payment.alias == alias)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Проверка PIN
    if not verify_pin(pin, payment.pin_hash):
        raise HTTPException(status_code=401, detail="Invalid PIN")
    
    if payment.status != "paid":
        raise HTTPException(status_code=400, detail=f"Payment status is {payment.status}, not 'paid'")
    
    # Поиск кода активации
    result = await session.execute(
        select(ActivationCode).where(ActivationCode.payment_id == payment.id)
    )
    activation = result.scalar_one_or_none()
    
    if not activation:
        raise HTTPException(status_code=404, detail="Activation code not found")
    
    if activation.redeemed_at is not None:
        raise HTTPException(status_code=400, detail="Activation code already redeemed")
    
    if activation.expires_at < now_utc():
        raise HTTPException(status_code=400, detail="Activation code expired")
    
    print(f"✅ Код найден: {activation.code}")
    return {
        "code": activation.code,
        "activation_code": activation.code,  # Поддержка обоих форматов
        "activationCode": activation.code,  # Поддержка обоих форматов
        "expires_at": activation.expires_at.isoformat(),
        "expiresAt": activation.expires_at.isoformat(),  # Поддержка обоих форматов
        "tariff_id": payment.tariff_id
    }


@app.post("/api/activation/verify")
async def verify_activation_code(
    code: str,
    session: AsyncSession = Depends(get_session)
):
    """Проверка кода активации без погашения"""
    result = await session.execute(
        select(ActivationCode).where(ActivationCode.code == code)
    )
    activation = result.scalar_one_or_none()
    
    if not activation:
        raise HTTPException(status_code=404, detail="Activation code not found")
    
    if activation.redeemed_at is not None:
        return {"valid": False, "reason": "already_redeemed"}
    
    if activation.expires_at < now_utc():
        return {"valid": False, "reason": "expired"}
    
    return {"valid": True, "expires_at": activation.expires_at.isoformat()}


@app.post("/api/activation/activate")
async def activate_code(
    code: str,
    session: AsyncSession = Depends(get_session)
):
    """Погашение кода активации"""
    result = await session.execute(
        select(ActivationCode).where(ActivationCode.code == code)
    )
    activation = result.scalar_one_or_none()
    
    if not activation:
        raise HTTPException(status_code=404, detail="Activation code not found")
    
    if activation.redeemed_at is not None:
        raise HTTPException(status_code=400, detail="Activation code already redeemed")
    
    if activation.expires_at < now_utc():
        raise HTTPException(status_code=400, detail="Activation code expired")
    
    activation.redeemed_at = now_utc()
    await session.commit()
    
    return {"status": "activated", "code": code}


# ✅ Endpoints для мобильного приложения (с familyId и deviceId)
@app.post("/api/subscription/activation/verify")
async def verify_activation_code_mobile(
    request: Request,
    session: AsyncSession = Depends(get_session),
    api_key: str = Depends(verify_api_key)
):
    """Проверка кода активации для мобильного приложения"""
    import logging
    logger = logging.getLogger(__name__)
    
    data = await request.json()
    code = data.get("code", "").strip().upper()
    family_id = data.get("familyId", "default")
    device_id = data.get("deviceId", "unknown")
    
    print(f"🔵 verify_activation_code_mobile: Запрос на проверку кода")
    print(f"   - code: {code}")
    print(f"   - familyId: {family_id}")
    print(f"   - deviceId: {device_id}")
    
    if not code:
        print("❌ Код не указан")
        raise HTTPException(status_code=400, detail="Code is required")
    
    result = await session.execute(
        select(ActivationCode).where(ActivationCode.code == code)
    )
    activation = result.scalar_one_or_none()
    
    if not activation:
        print(f"❌ Код {code} не найден в базе данных")
        # Проверяем, есть ли вообще коды в базе
        all_codes_result = await session.execute(select(ActivationCode.code))
        all_codes = [row[0] for row in all_codes_result.fetchall()]
        print(f"   - Всего кодов в базе: {len(all_codes)}")
        if all_codes:
            print(f"   - Примеры кодов: {all_codes[:3]}")
        raise HTTPException(status_code=404, detail="Activation code not found")
    
    # Получаем информацию о платеже
    payment_result = await session.execute(
        select(Payment).where(Payment.id == activation.payment_id)
    )
    payment = payment_result.scalar_one_or_none()
    
    redeemed = activation.redeemed_at is not None
    print(f"✅ Код найден: redeemed={redeemed}, expires_at={activation.expires_at}")
    
    if redeemed:
        print(f"⚠️ Код уже активирован")
        return {
            "status": "redeemed",
            "tariffId": payment.tariff_id if payment else "unknown",
            "expiresAt": activation.expires_at.isoformat()
        }
    
    # Сравниваем даты (приводим к UTC если нужно)
    expires_at_utc = activation.expires_at
    if expires_at_utc.tzinfo is None:
        from datetime import timezone
        expires_at_utc = expires_at_utc.replace(tzinfo=timezone.utc)
    
    if expires_at_utc < now_utc():
        print(f"⚠️ Код истек: {expires_at_utc} < {now_utc()}")
        return {
            "status": "expired",
            "tariffId": payment.tariff_id if payment else "unknown",
            "expiresAt": activation.expires_at.isoformat()
        }
    
    print(f"✅ Код валиден, возвращаем статус active")
    return {
        "status": "active",
        "tariffId": payment.tariff_id if payment else "unknown",
        "expiresAt": activation.expires_at.isoformat()
    }


@app.post("/api/subscription/activation/activate")
async def activate_code_mobile(
    request: Request,
    session: AsyncSession = Depends(get_session),
    api_key: str = Depends(verify_api_key)
):
    """Активация кода для мобильного приложения"""
    import logging
    logger = logging.getLogger(__name__)
    
    data = await request.json()
    code = data.get("code", "").strip().upper()
    family_id = data.get("familyId", "default")
    device_id = data.get("deviceId", "unknown")
    
    print(f"🔵 activate_code_mobile: Запрос на активацию кода")
    print(f"   - code: {code}")
    print(f"   - familyId: {family_id}")
    print(f"   - deviceId: {device_id}")
    
    if not code:
        print("❌ Код не указан")
        raise HTTPException(status_code=400, detail="Code is required")
    
    result = await session.execute(
        select(ActivationCode).where(ActivationCode.code == code)
    )
    activation = result.scalar_one_or_none()
    
    if not activation:
        print(f"❌ Код {code} не найден в базе данных")
        raise HTTPException(status_code=404, detail="Activation code not found")
    
    # Получаем информацию о платеже
    payment_result = await session.execute(
        select(Payment).where(Payment.id == activation.payment_id)
    )
    payment = payment_result.scalar_one_or_none()
    
    print(f"✅ Код найден: redeemed_at={activation.redeemed_at}, expires_at={activation.expires_at}")
    
    if activation.redeemed_at is not None:
        print(f"⚠️ Код уже активирован")
        raise HTTPException(status_code=400, detail="Activation code already redeemed")
    
    # Сравниваем даты (приводим к UTC если нужно)
    expires_at_utc = activation.expires_at
    if expires_at_utc.tzinfo is None:
        from datetime import timezone
        expires_at_utc = expires_at_utc.replace(tzinfo=timezone.utc)
    
    if expires_at_utc < now_utc():
        raise HTTPException(status_code=400, detail="Activation code expired")
    
    # Помечаем код как использованный
    activation.redeemed_at = now_utc()
    await session.commit()
    
    # Вычисляем дату истечения подписки (используем expires_at из кода активации)
    expires_at = activation.expires_at
    if expires_at.tzinfo is None:
        from datetime import timezone
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    return {
        "success": True,
        "tariffId": payment.tariff_id if payment else "unknown",
        "expiresAt": expires_at.isoformat()
    }


@app.post("/api/admin/payments/confirm-manual")
async def confirm_manual_payment(
    payment_id: str,
    psp_txn_id: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")
):
    """
    Ручное подтверждение прямого банковского перевода
    
    Требует:
    - X-Admin-Key заголовок
    """
    if not x_admin_key or x_admin_key != settings.admin_key:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    
    # Поиск платежа
    result = await session.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.status == "paid":
        # Idempotency
        result = await session.execute(
            select(ActivationCode).where(ActivationCode.payment_id == payment.id)
        )
        activation = result.scalar_one_or_none()
        return {
            "status": "already_processed",
            "payment_id": payment.id,
            "activation_code": activation.code if activation else None
        }
    
    # Обновление статуса
    payment.status = "paid"
    if psp_txn_id:
        payment.psp_payment_id = psp_txn_id
    await session.commit()
    
    # Генерация кода активации
    code = generate_activation_code()
    activation = ActivationCode(
        code=code,
        payment_id=payment.id,
        expires_at=code_expiration(30)
    )
    session.add(activation)
    await session.commit()
    
    return {
        "status": "confirmed",
        "payment_id": payment.id,
        "activation_code": code
    }


# ✅ АДМИНСКИЕ ENDPOINTS ДЛЯ УПРАВЛЕНИЯ ВИДИМОСТЬЮ МЕТОДОВ ОПЛАТЫ

@app.get("/api/admin/payment-methods/visibility")
async def get_payment_methods_visibility(
    admin_key: str = Depends(verify_admin_key)
):
    """
    Получить текущие настройки видимости методов оплаты
    
    Требует:
    - X-Admin-Key заголовок
    """
    from app.payment_methods import list_all_payment_methods
    
    visible_methods = set(
        method_id.strip() 
        for method_id in settings.visible_payment_methods.split(",") 
        if method_id.strip()
    )
    
    all_methods = list_all_payment_methods()
    
    result = {
        "visible_methods": list(visible_methods),
        "all_methods": [
            {
                "id": method["id"],
                "label": method["label"],
                "type": method["type"],
                "visible": method["id"] in visible_methods
            }
            for method in all_methods
        ]
    }
    
    return result


@app.post("/api/admin/payment-methods/visibility")
async def update_payment_methods_visibility(
    request: Request,
    admin_key: str = Depends(verify_admin_key)
):
    """
    Обновить настройки видимости методов оплаты
    
    Требует:
    - X-Admin-Key заголовок
    - JSON body с полем "visible_methods" (список ID методов через запятую)
    
    Пример запроса:
    {
        "visible_methods": "qr_sbp,sberpay,card_sber,tinkoff_pay,manual_transfer"
    }
    """
    data = await request.json()
    visible_methods = data.get("visible_methods", "")
    
    if not visible_methods:
        raise HTTPException(
            status_code=400,
            detail="visible_methods is required (comma-separated list of method IDs)"
        )
    
    # Валидация: проверяем, что все методы существуют
    from app.payment_methods import PAYMENT_METHOD_MAP
    
    method_ids = [m.strip() for m in visible_methods.split(",") if m.strip()]
    invalid_methods = [m for m in method_ids if m not in PAYMENT_METHOD_MAP]
    
    if invalid_methods:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid method IDs: {', '.join(invalid_methods)}"
        )
    
    # ✅ Обновляем настройки (в реальном проекте это должно быть в БД или файле конфигурации)
    # Для простоты обновляем переменную окружения (в продакшене лучше использовать БД)
    settings.visible_payment_methods = visible_methods
    
    return {
        "status": "updated",
        "visible_methods": method_ids,
        "message": "Payment methods visibility updated. Restart service to apply changes, or use environment variable PAYMENT_VISIBLE_PAYMENT_METHODS for permanent changes."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
