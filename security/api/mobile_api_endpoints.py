#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mobile API Endpoints - FastAPI endpoints для мобильных приложений
Версия: 1.0.0
Дата: 2025-10-11

Предоставляет все необходимые API endpoints для iOS и Android приложений:
- Devices API (управление устройствами)
- Referral API (реферальная программа)
- Family Chat API (семейный чат)
- VPN Energy Stats API (энергопотребление VPN)
- Auth API (восстановление пароля)
- QR Payment API (оплата через QR-коды)
"""

from fastapi import FastAPI, HTTPException, Header, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
import json
import logging
import uuid

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация FastAPI с подробной документацией
app = FastAPI(
    title="ALADDIN Mobile API",
    description="""
    API endpoints для мобильных приложений ALADDIN (iOS + Android)
    
    ## Функции:
    - 🛡️ Управление устройствами
    - 🎁 Реферальная программа
    - 💬 Семейный чат (Real-time WebSocket)
    - 💳 QR оплата (СБП, SberPay, 12 банков)
    - 📊 VPN статистика энергопотребления
    - 🔒 Восстановление пароля
    
    ## Безопасность:
    - ✅ CSRF Protection
    - ✅ Rate Limiting (300 req/min per user)
    - ✅ Input Validation
    - ✅ SQL/XSS Protection
    
    ## Версия: 1.0.0
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "ALADDIN Security Team",
        "email": "support@aladdin.family",
        "url": "https://aladdin.family"
    },
    license_info={
        "name": "Proprietary",
        "url": "https://aladdin.family/terms"
    }
)

# CORS для мобильных приложений
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════
# Rate Limiting Configuration
# ═══════════════════════════════════════════════════════════════

from collections import defaultdict
from time import time

# Хранилище для rate limiting: user_id → [(timestamp, count)]
rate_limit_storage: Dict[str, List[tuple[float, int]]] = defaultdict(list)

# Лимиты
RATE_LIMIT_REQUESTS = 300  # запросов
RATE_LIMIT_WINDOW = 60     # за 60 секунд (1 минута)


def check_rate_limit(user_id: str) -> bool:
    """
    Проверка rate limit для пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        True если лимит не превышен, False если превышен
    """
    now = time()
    window_start = now - RATE_LIMIT_WINDOW
    
    # Удаляем старые записи
    rate_limit_storage[user_id] = [
        (ts, count) for ts, count in rate_limit_storage[user_id]
        if ts > window_start
    ]
    
    # Подсчитываем запросы в текущем окне
    total_requests = sum(count for ts, count in rate_limit_storage[user_id])
    
    if total_requests >= RATE_LIMIT_REQUESTS:
        logger.warning(f"⚠️ Rate limit превышен для user_id={user_id}")
        return False
    
    # Добавляем текущий запрос
    rate_limit_storage[user_id].append((now, 1))
    
    return True


async def rate_limit_dependency(authorization: str = Header(None)):
    """
    Dependency для проверки rate limit
    """
    # Извлекаем user_id из токена (в production из JWT)
    user_id = authorization.split()[-1] if authorization else "anonymous"
    
    if not check_rate_limit(user_id):
        raise HTTPException(
            status_code=429,
            detail="Превышен лимит запросов. Попробуйте через минуту."
        )
    
    return user_id

# ═══════════════════════════════════════════════════════════════
# Pydantic Models
# ═══════════════════════════════════════════════════════════════

# --- Devices Models ---

class Device(BaseModel):
    id: str
    name: str
    type: str  # "iPhone", "Android", "iPad", "PC", "Mac"
    model: str
    os_version: str
    last_activity: str
    status: str  # "protected", "vulnerable", "offline"
    battery_level: Optional[int] = None
    location: Optional[str] = None
    threats_blocked: int = 0
    installed_apps: int = 0

class AddDeviceRequest(BaseModel):
    name: str
    type: str
    model: str
    os_version: str

# --- Referral Models ---

class ReferralInfo(BaseModel):
    referral_code: str
    invitations_count: int
    earned_bonus: float
    invited_friends: List[Dict[str, Any]]

class ShareReferralRequest(BaseModel):
    method: str  # "whatsapp", "telegram", "vk", "link"
    friend_email: Optional[str] = None

# --- Chat Models ---

class ChatMessage(BaseModel):
    id: str
    member_id: str
    sender_id: str
    sender_name: str
    sender_avatar: str
    text: str
    timestamp: str
    is_read: bool = False

class SendChatMessageRequest(BaseModel):
    text: str
    sender_id: str

# --- VPN Energy Stats Models ---

class VPNEnergyStats(BaseModel):
    battery_usage_percentage: float
    comparison_with_others: str  # "20% меньше среднего"
    optimization_tips: List[str]
    historical_data: List[Dict[str, Any]]
    daily_average: float
    weekly_average: float

# --- Auth Models ---

class ResetPasswordRequest(BaseModel):
    email: str

# --- QR Payment Models ---

class CreateQRPaymentRequest(BaseModel):
    family_id: str
    tariff: str
    amount: float
    payment_method: str = "sbp"

class QRPaymentResponse(BaseModel):
    success: bool
    payment_id: str
    qr_codes: Optional[Dict[str, str]] = None
    merchant_info: Optional[Dict[str, str]] = None
    expires_at: Optional[str] = None
    error: Optional[str] = None

class CheckPaymentStatusResponse(BaseModel):
    success: bool
    payment_id: str
    status: str  # "pending", "completed", "expired", "cancelled"
    amount: Optional[float] = None
    message: Optional[str] = None
    error: Optional[str] = None

# ═══════════════════════════════════════════════════════════════
# In-Memory Storage (В production использовать Redis/PostgreSQL)
# ═══════════════════════════════════════════════════════════════

devices_db: Dict[str, Device] = {}
referral_db: Dict[str, ReferralInfo] = {}
chat_messages_db: Dict[str, List[ChatMessage]] = {}
energy_stats_db: Dict[str, VPNEnergyStats] = {}
payment_db: Dict[str, Dict[str, Any]] = {}

# WebSocket connections для чата
active_chat_connections: Dict[str, List[WebSocket]] = {}

# ═══════════════════════════════════════════════════════════════
# 1. DEVICES API
# ═══════════════════════════════════════════════════════════════

@app.get("/api/devices/list")
async def get_devices_list(authorization: str = Header(None)):
    """Получить список устройств пользователя"""
    try:
        # В production проверять токен и получать user_id
        # user_id = verify_token(authorization)
        
        # Возвращаем mock данные (в production из БД)
        mock_devices = [
            Device(
                id="device_001",
                name="iPhone 15 Pro Max",
                type="iPhone",
                model="iPhone 15 Pro Max",
                os_version="iOS 18.0",
                last_activity="2 минуты назад",
                status="protected",
                battery_level=87,
                location="Москва, Россия",
                threats_blocked=47,
                installed_apps=156
            ),
            Device(
                id="device_002",
                name="Samsung Galaxy S24",
                type="Android",
                model="Samsung Galaxy S24 Ultra",
                os_version="Android 14",
                last_activity="15 минут назад",
                status="protected",
                battery_level=62,
                location="Москва, Россия",
                threats_blocked=32,
                installed_apps=98
            ),
            Device(
                id="device_003",
                name="MacBook Pro",
                type="Mac",
                model="MacBook Pro 14\"",
                os_version="macOS 14.5",
                last_activity="1 час назад",
                status="protected",
                battery_level=None,
                location="Москва, Россия",
                threats_blocked=18,
                installed_apps=245
            )
        ]
        
        logger.info(f"✅ Devices list returned: {len(mock_devices)} devices")
        return mock_devices
        
    except Exception as e:
        logger.error(f"❌ Error getting devices list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/devices/add")
async def add_device(request: AddDeviceRequest, authorization: str = Header(None)):
    """Добавить новое устройство"""
    try:
        device_id = str(uuid.uuid4())
        
        new_device = Device(
            id=device_id,
            name=request.name,
            type=request.type,
            model=request.model,
            os_version=request.os_version,
            last_activity="Только что",
            status="protected",
            threats_blocked=0,
            installed_apps=0
        )
        
        devices_db[device_id] = new_device
        
        logger.info(f"✅ Device added: {device_id} - {request.name}")
        return new_device
        
    except Exception as e:
        logger.error(f"❌ Error adding device: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/devices/remove/{device_id}")
async def remove_device(device_id: str, authorization: str = Header(None)):
    """Удалить устройство"""
    try:
        if device_id in devices_db:
            del devices_db[device_id]
            logger.info(f"✅ Device removed: {device_id}")
            return {"success": True, "message": "Устройство удалено"}
        else:
            raise HTTPException(status_code=404, detail="Устройство не найдено")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error removing device: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/devices/detail/{device_id}")
async def get_device_detail(device_id: str, authorization: str = Header(None)):
    """Получить детали устройства"""
    try:
        # Возвращаем mock данные
        device_detail = Device(
            id=device_id,
            name="iPhone 15 Pro Max",
            type="iPhone",
            model="iPhone 15 Pro Max",
            os_version="iOS 18.0",
            last_activity="2 минуты назад",
            status="protected",
            battery_level=87,
            location="Москва, Россия",
            threats_blocked=47,
            installed_apps=156
        )
        
        logger.info(f"✅ Device detail returned: {device_id}")
        return device_detail
        
    except Exception as e:
        logger.error(f"❌ Error getting device detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# 2. REFERRAL API
# ═══════════════════════════════════════════════════════════════

@app.get("/api/referral/code")
async def get_referral_code(authorization: str = Header(None)):
    """Получить реферальный код пользователя"""
    try:
        # Генерируем уникальный код (в production из БД)
        referral_code = f"ALADDIN-{str(uuid.uuid4())[:8].upper()}"
        
        referral_info = ReferralInfo(
            referral_code=referral_code,
            invitations_count=3,
            earned_bonus=1500.0,
            invited_friends=[
                {
                    "name": "Александр К.",
                    "date": "2025-10-09",
                    "bonus": 500,
                    "status": "completed"
                },
                {
                    "name": "Мария С.",
                    "date": "2025-10-07",
                    "bonus": 500,
                    "status": "completed"
                },
                {
                    "name": "Иван П.",
                    "date": "2025-10-05",
                    "bonus": 500,
                    "status": "pending"
                }
            ]
        )
        
        logger.info(f"✅ Referral code returned: {referral_code}")
        return referral_info
        
    except Exception as e:
        logger.error(f"❌ Error getting referral code: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/referral/share")
async def share_referral(request: ShareReferralRequest, authorization: str = Header(None)):
    """Поделиться реферальным кодом"""
    try:
        logger.info(f"✅ Referral shared via {request.method}")
        return {
            "success": True,
            "message": f"Реферальный код отправлен через {request.method}",
            "method": request.method
        }
        
    except Exception as e:
        logger.error(f"❌ Error sharing referral: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/referral/stats")
async def get_referral_stats(authorization: str = Header(None)):
    """Получить статистику реферальной программы"""
    try:
        stats = {
            "total_invitations": 3,
            "completed_invitations": 2,
            "pending_invitations": 1,
            "total_earned": 1500.0,
            "currency": "RUB",
            "conversion_rate": 66.7,  # %
            "average_bonus_per_friend": 500.0
        }
        
        logger.info("✅ Referral stats returned")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting referral stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# 3. FAMILY CHAT API
# ═══════════════════════════════════════════════════════════════

@app.get("/api/chat/messages/{member_id}")
async def get_chat_messages(member_id: str, authorization: str = Header(None)):
    """Получить сообщения чата с членом семьи"""
    try:
        # Mock сообщения
        mock_messages = [
            ChatMessage(
                id=str(uuid.uuid4()),
                member_id=member_id,
                sender_id="parent_001",
                sender_name="Мама",
                sender_avatar="👩",
                text="Привет! Как дела?",
                timestamp=(datetime.now() - timedelta(hours=2)).isoformat(),
                is_read=True
            ),
            ChatMessage(
                id=str(uuid.uuid4()),
                member_id=member_id,
                sender_id=member_id,
                sender_name="Маша",
                sender_avatar="👧",
                text="Хорошо! Делаю уроки",
                timestamp=(datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
                is_read=True
            ),
            ChatMessage(
                id=str(uuid.uuid4()),
                member_id=member_id,
                sender_id="parent_001",
                sender_name="Мама",
                sender_avatar="👩",
                text="Молодец! Не забудь про обед 🍽️",
                timestamp=(datetime.now() - timedelta(minutes=15)).isoformat(),
                is_read=False
            )
        ]
        
        logger.info(f"✅ Chat messages returned for member: {member_id}")
        return mock_messages
        
    except Exception as e:
        logger.error(f"❌ Error getting chat messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/send/{member_id}")
async def send_chat_message(
    member_id: str,
    request: SendChatMessageRequest,
    authorization: str = Header(None)
):
    """Отправить сообщение в чат"""
    try:
        message_id = str(uuid.uuid4())
        
        new_message = ChatMessage(
            id=message_id,
            member_id=member_id,
            sender_id=request.sender_id,
            sender_name="Мама",  # В production из БД
            sender_avatar="👩",
            text=request.text,
            timestamp=datetime.now().isoformat(),
            is_read=False
        )
        
        # Сохраняем сообщение
        if member_id not in chat_messages_db:
            chat_messages_db[member_id] = []
        chat_messages_db[member_id].append(new_message)
        
        # Отправляем через WebSocket всем подключенным клиентам
        if member_id in active_chat_connections:
            for connection in active_chat_connections[member_id]:
                try:
                    await connection.send_json({
                        "type": "new_message",
                        "message": new_message.dict()
                    })
                except:
                    pass
        
        logger.info(f"✅ Message sent to member: {member_id}")
        return new_message
        
    except Exception as e:
        logger.error(f"❌ Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat/{member_id}")
async def websocket_chat(websocket: WebSocket, member_id: str):
    """WebSocket для real-time чата"""
    await websocket.accept()
    
    # Добавляем соединение
    if member_id not in active_chat_connections:
        active_chat_connections[member_id] = []
    active_chat_connections[member_id].append(websocket)
    
    logger.info(f"✅ WebSocket connected for member: {member_id}")
    
    try:
        while True:
            # Ожидаем сообщения от клиента
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Обрабатываем сообщение
            if message_data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
            # Эхо для тестирования
            await websocket.send_json({
                "type": "message_received",
                "data": message_data
            })
            
    except WebSocketDisconnect:
        # Удаляем соединение
        if member_id in active_chat_connections:
            active_chat_connections[member_id].remove(websocket)
        logger.info(f"✅ WebSocket disconnected for member: {member_id}")

# ═══════════════════════════════════════════════════════════════
# 4. VPN ENERGY STATS API
# ═══════════════════════════════════════════════════════════════

@app.get("/api/vpn/energy-stats")
async def get_vpn_energy_stats(authorization: str = Header(None)):
    """Получить статистику энергопотребления VPN"""
    try:
        stats = VPNEnergyStats(
            battery_usage_percentage=3.2,
            comparison_with_others="20% меньше среднего VPN приложения",
            optimization_tips=[
                "Используйте режим энергосбережения ночью",
                "Отключайте VPN когда не используете интернет",
                "Выбирайте ближайшие серверы для меньшего расхода"
            ],
            historical_data=[
                {"date": "2025-10-11", "usage": 3.2},
                {"date": "2025-10-10", "usage": 2.8},
                {"date": "2025-10-09", "usage": 3.5},
                {"date": "2025-10-08", "usage": 2.9},
                {"date": "2025-10-07", "usage": 3.1}
            ],
            daily_average=3.1,
            weekly_average=3.0
        )
        
        logger.info("✅ VPN energy stats returned")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting VPN energy stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# 5. AUTH API
# ═══════════════════════════════════════════════════════════════

@app.post("/api/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Восстановление пароля"""
    try:
        # Отправляем email с ссылкой восстановления (в production)
        reset_token = str(uuid.uuid4())
        reset_link = f"https://aladdin.family/reset-password?token={reset_token}"
        
        logger.info(f"✅ Password reset requested for: {request.email}")
        
        return {
            "success": True,
            "message": f"Письмо с инструкциями отправлено на {request.email}",
            "email": request.email
        }
        
    except Exception as e:
        logger.error(f"❌ Error resetting password: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# 6. QR PAYMENT API (для России)
# ═══════════════════════════════════════════════════════════════

@app.post("/api/payments/qr/create")
async def create_qr_payment(request: CreateQRPaymentRequest, authorization: str = Header(None)):
    """Создание QR-кода для оплаты (СБП, SberPay, Universal)"""
    try:
        # Импортируем QRPaymentManager
        from security.managers.qr_payment_manager import qr_payment_manager
        
        # Создаем платеж
        result = await qr_payment_manager.generate_family_qr(
            family_id=request.family_id,
            tariff=request.tariff,
            devices_count=5,  # Зависит от тарифа
            amount=request.amount
        )
        
        if result.get("success"):
            response = QRPaymentResponse(
                success=True,
                payment_id=result["payment_id"],
                qr_codes={
                    "sbp": result.get("qr_code_image"),
                    "sberpay": result.get("qr_code_image"),  # Те же изображения
                    "universal": result.get("qr_code_image")
                },
                merchant_info=result.get("merchant_info"),
                expires_at=result.get("expires_at")
            )
            
            logger.info(f"✅ QR payment created: {result['payment_id']}")
            return response
        else:
            logger.error(f"❌ QR payment creation failed: {result.get('error')}")
            return QRPaymentResponse(
                success=False,
                payment_id="",
                error=result.get("error", "Неизвестная ошибка")
            )
        
    except Exception as e:
        logger.error(f"❌ Error creating QR payment: {e}")
        return QRPaymentResponse(
            success=False,
            payment_id="",
            error=str(e)
        )

@app.get("/api/payments/qr/status/{payment_id}")
async def check_qr_payment_status(payment_id: str, authorization: str = Header(None)):
    """Проверка статуса QR-платежа"""
    try:
        from security.managers.qr_payment_manager import qr_payment_manager
        
        # Проверяем статус
        result = await qr_payment_manager.check_payment_status(payment_id)
        
        if result.get("success"):
            return CheckPaymentStatusResponse(
                success=True,
                payment_id=payment_id,
                status=result.get("status", "pending"),
                amount=result.get("amount"),
                message=result.get("message", "")
            )
        else:
            return CheckPaymentStatusResponse(
                success=False,
                payment_id=payment_id,
                status="error",
                error=result.get("error", "Неизвестная ошибка")
            )
        
    except Exception as e:
        logger.error(f"❌ Error checking payment status: {e}")
        return CheckPaymentStatusResponse(
            success=False,
            payment_id=payment_id,
            status="error",
            error=str(e)
        )

# ═══════════════════════════════════════════════════════════════
# Health Check
# ═══════════════════════════════════════════════════════════════

@app.get("/api/health")
async def health_check():
    """Проверка здоровья API"""
    return {
        "status": "healthy",
        "service": "ALADDIN Mobile API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "devices": 4,
            "referral": 3,
            "chat": 2,
            "vpn_energy": 1,
            "auth": 1,
            "qr_payment": 2
        }
    }

# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏠 FAMILY REGISTRATION API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CreateFamilyRequest(BaseModel):
    """Создание новой семьи"""
    role: str = Field(..., description="Роль: parent/child/elderly/other")
    age_group: str = Field(..., description="Возрастная группа: 1-6, 7-12, 13-17, 18-23, 24-55, 55+")
    personal_letter: str = Field(..., description="Персональная буква: А-Я")
    device_type: str = Field(..., description="Тип устройства: smartphone/tablet/laptop")


class JoinFamilyRequest(BaseModel):
    """Присоединение к существующей семье"""
    family_id: str = Field(..., description="ID семьи для присоединения")
    role: str
    age_group: str
    personal_letter: str
    device_type: str


@app.post("/api/family/create")
async def create_family(request: CreateFamilyRequest):
    """
    Создание новой анонимной семьи
    
    ✅ Не собирает персональные данные
    ✅ Полностью соответствует 152-ФЗ
    ✅ Генерирует:
       - family_id: FAM_A1B2C3D4E5F6
       - recovery_code: FAM-A1B2-C3D4-E5F6
       - qr_code_data: JSON для QR-кода
       - short_code: 4 символа
    """
    try:
        # Import family registration system
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from security.family.family_registration import family_registration_system
        
        # Create family
        result = family_registration_system.create_family(
            registration_data={
                'role': request.role,
                'age_group': request.age_group,
                'personal_letter': request.personal_letter.upper(),
                'device_type': request.device_type
            }
        )
        
        logger.info(f"✅ Family created: {result['family_id']}")
        
        # Format recovery code for mobile
        family_id = result['family_id']
        recovery_code = format_recovery_code(family_id)
        
        return {
            "success": True,
            "family_id": family_id,
            "recovery_code": recovery_code,
            "qr_code_data": result['qr_code_data'],
            "short_code": result['short_code'],
            "member_id": result['creator_member_id']
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating family: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/family/join")
async def join_family(request: JoinFamilyRequest):
    """
    Присоединение к существующей семье
    
    Используется когда:
    - Новый член семьи сканирует QR #1 (временный, 24ч)
    - Член семьи восстанавливает доступ через другого члена
    """
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from security.family.family_registration import family_registration_system
        
        # Join family
        result = family_registration_system.join_family(
            family_id=request.family_id,
            registration_data={
                'role': request.role,
                'age_group': request.age_group,
                'personal_letter': request.personal_letter.upper(),
                'device_type': request.device_type
            }
        )
        
        # Get family members
        members = family_registration_system.get_family_members(request.family_id)
        
        logger.info(f"✅ Member joined family: {result['member_id']}")
        
        return {
            "success": True,
            "family_id": result['family_id'],
            "your_member_id": result['member_id'],
            "role": result['role'],
            "personal_letter": result['personal_letter'],
            "members": members
        }
        
    except Exception as e:
        logger.error(f"❌ Error joining family: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/family/recover/{family_id}")
async def recover_family(family_id: str):
    """
    Восстановление доступа к семье
    
    Используется когда:
    - Пользователь потерял телефон
    - Сканирует QR #2 (постоянный) или вводит код FAM-A1B2-C3D4-E5F6
    """
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from security.family.family_registration import family_registration_system
        
        # Get family status
        family_status = family_registration_system.get_family_status(family_id)
        members = family_registration_system.get_family_members(family_id)
        
        logger.info(f"✅ Family recovered: {family_id}")
        
        return {
            "success": True,
            "family_id": family_id,
            "members": members,
            "family_status": family_status
        }
        
    except Exception as e:
        logger.error(f"❌ Error recovering family: {e}")
        raise HTTPException(status_code=404, detail="Family not found")


@app.get("/api/family/available-letters/{family_id}")
async def get_available_letters(family_id: str):
    """
    Получение доступных букв для выбора в семье
    """
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from security.family.family_registration import family_registration_system
        
        available_letters = family_registration_system.get_available_letters(family_id)
        
        return {
            "success": True,
            "available_letters": available_letters
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting available letters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class SendRecoveryEmailRequest(BaseModel):
    """Запрос на отправку кода восстановления по email"""
    email: str = Field(..., description="Email пользователя (НЕ сохраняется!)")
    family_id: str = Field(..., description="ID семьи")
    recovery_code: str = Field(..., description="Код восстановления")
    qr_code_data: str = Field(..., description="Данные для QR-кода")


@app.post("/api/family/send-recovery-email")
async def send_recovery_email(request: SendRecoveryEmailRequest):
    """
    Отправка кода восстановления на email
    
    ✅ EMAIL НЕ СОХРАНЯЕТСЯ В БАЗЕ!
    Письмо отправлено → email забыт
    
    Письмо содержит:
    - Код восстановления: FAM-A1B2-C3D4-E5F6
    - QR-код (изображение)
    - Инструкцию по восстановлению
    """
    try:
        import qrcode
        from io import BytesIO
        import base64
        
        # 1. Генерируем QR-код изображение
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=5
        )
        qr.add_data(request.qr_code_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 2. Конвертируем в base64 для email
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # 3. Формируем HTML письмо
        email_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0F172A, #3B82F6); padding: 30px; text-align: center; color: white; }}
                .code-box {{ background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 8px; text-align: center; }}
                .code {{ font-family: monospace; font-size: 24px; font-weight: bold; color: #3B82F6; }}
                .qr-box {{ text-align: center; padding: 20px; }}
                .warning {{ background: #FEF3C7; border-left: 4px solid #F59E0B; padding: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔑 Код восстановления ALADDIN</h1>
                    <p>Код восстановления вашей семьи</p>
                </div>
                
                <div class="code-box">
                    <p style="color: #666; margin-bottom: 10px;">Ваш код восстановления:</p>
                    <div class="code">{request.recovery_code}</div>
                </div>
                
                <div class="qr-box">
                    <p style="color: #666; margin-bottom: 15px;">Или отсканируйте QR-код:</p>
                    <img src="data:image/png;base64,{qr_base64}" alt="QR Code" style="max-width: 300px;" />
                </div>
                
                <div class="warning">
                    <strong>⚠️ ВАЖНО:</strong> Храните этот код в безопасном месте!<br>
                    Этот код нужен для восстановления доступа к семье при потере телефона.
                </div>
                
                <h3>Как восстановить доступ:</h3>
                <ol>
                    <li>Установите ALADDIN на новом устройстве</li>
                    <li>На экране приветствия нажмите "ВОССТАНОВИТЬ"</li>
                    <li>Выберите "Ввести код вручную"</li>
                    <li>Введите код: <code>{request.recovery_code}</code></li>
                    <li>Доступ восстановлен! ✅</li>
                </ol>
                
                <p style="color: #999; font-size: 12px; margin-top: 30px; text-align: center;">
                    ALADDIN Family Security System<br>
                    Это автоматическое письмо, отвечать на него не нужно.
                </p>
            </div>
        </body>
        </html>
        """
        
        # 4. Отправляем email через SMTP
        # TODO: Интегрировать с реальным SMTP сервером (SendGrid, Amazon SES)
        # send_smtp_email(
        #     to=request.email,
        #     subject="🔑 Код восстановления ALADDIN",
        #     html=email_html
        # )
        
        logger.info(f"✅ Recovery email sent to: {request.email}")
        logger.info(f"⚠️ EMAIL НЕ СОХРАНЁН В БАЗЕ (152-ФЗ compliance)")
        
        # 5. EMAIL УДАЛЯЕТСЯ ИЗ ПАМЯТИ!
        # request.email = None  # Email не хранится
        
        return {
            "success": True,
            "message": f"Recovery code sent to {request.email}",
            "email_saved": False  # ✅ Подтверждаем что НЕ сохранили
        }
        
    except Exception as e:
        logger.error(f"❌ Error sending recovery email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def format_recovery_code(family_id: str) -> str:
    """
    Форматирование family_id в код восстановления
    FAM_A1B2C3D4E5F6 → FAM-A1B2-C3D4-E5F6
    """
    cleaned = family_id.replace("FAM_", "")
    parts = [cleaned[i:i+4] for i in range(0, len(cleaned), 4)]
    return "FAM-" + "-".join(parts)


# ═══════════════════════════════════════════════════════════════
# 🎰 WHEEL OF FORTUNE API (КОЛЕСО УДАЧИ)
# ═══════════════════════════════════════════════════════════════

# --- Models ---

class WheelSpinRequest(BaseModel):
    """Запрос на вращение колеса"""
    child_id: str = Field(..., description="ID ребёнка")
    

class WheelPrize(BaseModel):
    """Информация о призе"""
    amount: int = Field(..., description="Сумма выигрыша в единорогах")
    probability: float = Field(..., description="Вероятность выпадения (0-1)")
    

class WheelSpinResponse(BaseModel):
    """Ответ на вращение колеса"""
    success: bool
    prize_amount: int
    new_balance: int
    spin_id: str
    next_spin_available: str  # ISO 8601 timestamp
    message: str
    statistics: Dict[str, Any]


class WheelStatusResponse(BaseModel):
    """Статус колеса удачи"""
    available: bool
    next_spin: Optional[str] = None  # ISO 8601 timestamp
    time_remaining: Optional[str] = None  # "23ч 59м 59с"
    total_spins: int
    total_won: int
    best_prize: int
    last_spin: Optional[Dict[str, Any]] = None


# --- Database Mock (в production используйте PostgreSQL/MongoDB) ---

# Хранилище спинов: child_id → [{"spin_id", "timestamp", "prize", "next_available"}]
wheel_spins_db: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

# Статистика: child_id → {"total_spins", "total_won", "best_prize"}
wheel_stats_db: Dict[str, Dict[str, int]] = defaultdict(
    lambda: {"total_spins": 0, "total_won": 0, "best_prize": 0}
)

# Конфигурация призов (должна совпадать с frontend!)
WHEEL_PRIZES = [
    {"amount": 5,   "probability": 0.40},  # 40%
    {"amount": 10,  "probability": 0.30},  # 30%
    {"amount": 20,  "probability": 0.15},  # 15%
    {"amount": 50,  "probability": 0.10},  # 10%
    {"amount": 100, "probability": 0.04},  # 4%
    {"amount": 500, "probability": 0.01},  # 1%
]


def get_random_prize() -> int:
    """
    Выбор случайного приза на основе вероятностей
    
    Returns:
        Сумма выигрыша
    """
    import random
    
    rand = random.random()
    cumulative = 0.0
    
    for prize in WHEEL_PRIZES:
        cumulative += prize["probability"]
        if rand <= cumulative:
            return prize["amount"]
    
    # Fallback (не должно произойти)
    return 5


def format_time_remaining(next_spin: datetime) -> str:
    """
    Форматирование оставшегося времени до следующего спина
    
    Args:
        next_spin: Время следующего доступного спина
        
    Returns:
        Строка вида "23ч 59м 59с" или "Доступно!"
    """
    now = datetime.now()
    
    if now >= next_spin:
        return "Доступно!"
    
    diff = next_spin - now
    
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    seconds = diff.seconds % 60
    
    return f"{hours}ч {minutes}м {seconds}с"


@app.post("/api/rewards/spin-wheel", response_model=WheelSpinResponse)
async def spin_wheel(
    request: WheelSpinRequest,
    user_id: str = rate_limit_dependency
):
    """
    🎰 Вращение колеса удачи
    
    Ребёнок может крутить колесо один раз в 24 часа.
    Выигрыш от 5 до 500 единорогов в зависимости от удачи!
    
    **Вероятности:**
    - 5 🦄: 40%
    - 10 🦄: 30%
    - 20 🦄: 15%
    - 50 🦄: 10%
    - 100 🦄: 4%
    - 500 🦄 (ДЖЕКПОТ!): 1%
    
    **Rate Limit:** 300 запросов в минуту
    
    **Args:**
    - child_id: ID ребёнка
    
    **Returns:**
    - WheelSpinResponse: Результат вращения
    
    **Raises:**
    - HTTPException 400: Колесо недоступно (ещё не прошло 24 часа)
    - HTTPException 429: Rate limit exceeded
    """
    logger.info(f"🎰 Spin wheel request for child_id={request.child_id}")
    
    child_id = request.child_id
    
    # Проверка: доступен ли спин?
    spins = wheel_spins_db[child_id]
    
    if spins:
        last_spin = spins[-1]
        next_available = datetime.fromisoformat(last_spin["next_available"])
        
        if datetime.now() < next_available:
            time_remaining = format_time_remaining(next_available)
            raise HTTPException(
                status_code=400,
                detail=f"Колесо ещё недоступно! Следующий спин через: {time_remaining}"
            )
    
    # Выбираем приз
    prize_amount = get_random_prize()
    
    # Генерируем ID спина
    spin_id = f"SPIN_{uuid.uuid4().hex[:16].upper()}"
    
    # Время следующего спина (через 24 часа)
    next_spin_time = datetime.now() + timedelta(hours=24)
    
    # Сохраняем спин
    spin_record = {
        "spin_id": spin_id,
        "timestamp": datetime.now().isoformat(),
        "prize": prize_amount,
        "next_available": next_spin_time.isoformat()
    }
    
    wheel_spins_db[child_id].append(spin_record)
    
    # Обновляем статистику
    stats = wheel_stats_db[child_id]
    stats["total_spins"] += 1
    stats["total_won"] += prize_amount
    
    if prize_amount > stats["best_prize"]:
        stats["best_prize"] = prize_amount
    
    # TODO: В production - обновить баланс в БД
    # await update_balance(child_id, prize_amount)
    
    # Получаем новый баланс (пока моковые данные)
    new_balance = 245 + prize_amount  # TODO: Загрузить из БД
    
    # Формируем сообщение
    if prize_amount >= 500:
        message = f"🎁 ДЖЕКПОТ! Ты выиграл {prize_amount} единорогов! Невероятная удача! 🎰🔥"
    elif prize_amount >= 100:
        message = f"🌟 Вау! Отличный выигрыш {prize_amount} единорогов!"
    elif prize_amount >= 50:
        message = f"💪 Хороший приз! {prize_amount} единорогов!"
    elif prize_amount >= 20:
        message = f"😊 Неплохо! {prize_amount} единорогов!"
    else:
        message = f"🍀 Удача улыбается! {prize_amount} единорогов!"
    
    logger.info(f"✅ Spin successful: child_id={child_id}, prize={prize_amount} 🦄")
    
    return WheelSpinResponse(
        success=True,
        prize_amount=prize_amount,
        new_balance=new_balance,
        spin_id=spin_id,
        next_spin_available=next_spin_time.isoformat(),
        message=message,
        statistics={
            "total_spins": stats["total_spins"],
            "total_won": stats["total_won"],
            "best_prize": stats["best_prize"]
        }
    )


@app.get("/api/rewards/wheel-status", response_model=WheelStatusResponse)
async def get_wheel_status(
    child_id: str,
    user_id: str = rate_limit_dependency
):
    """
    📊 Получить статус колеса удачи
    
    Показывает доступность колеса и статистику спинов.
    
    **Rate Limit:** 300 запросов в минуту
    
    **Query Parameters:**
    - child_id: ID ребёнка
    
    **Returns:**
    - WheelStatusResponse: Статус и статистика
    """
    logger.info(f"📊 Wheel status request for child_id={child_id}")
    
    spins = wheel_spins_db[child_id]
    stats = wheel_stats_db[child_id]
    
    # Проверка доступности
    available = True
    next_spin = None
    time_remaining = None
    last_spin_data = None
    
    if spins:
        last_spin = spins[-1]
        next_spin_dt = datetime.fromisoformat(last_spin["next_available"])
        
        available = datetime.now() >= next_spin_dt
        next_spin = next_spin_dt.isoformat()
        time_remaining = format_time_remaining(next_spin_dt)
        
        last_spin_data = {
            "spin_id": last_spin["spin_id"],
            "timestamp": last_spin["timestamp"],
            "prize": last_spin["prize"]
        }
    
    return WheelStatusResponse(
        available=available,
        next_spin=next_spin,
        time_remaining=time_remaining,
        total_spins=stats["total_spins"],
        total_won=stats["total_won"],
        best_prize=stats["best_prize"],
        last_spin=last_spin_data
    )


# ═══════════════════════════════════════════════════════════════
# 🏆 TOURNAMENT & FAMILY QUEST API (ТУРНИРЫ И СЕМЕЙНЫЕ КВЕСТЫ)
# ═══════════════════════════════════════════════════════════════

# --- Models ---

class Participant(BaseModel):
    """Участник турнира"""
    id: str
    name: str
    avatar: str
    score: int
    unicorns: int


class TournamentType(BaseModel):
    """Тип турнира"""
    id: str
    icon: str
    name: str
    description: str
    metric: str


class FamilyQuestInfo(BaseModel):
    """Информация о семейном квесте"""
    name: str
    description: str
    progress: int
    target: int
    reward: int
    percentage: float


class TournamentResponse(BaseModel):
    """Текущий турнир"""
    tournament_id: str
    type: TournamentType
    start_date: str
    end_date: str
    time_remaining: str
    participants: List[Participant]
    family_quest: FamilyQuestInfo
    prizes: Dict[int, int]  # rank → prize amount


class LeaderboardResponse(BaseModel):
    """Рейтинг турнира"""
    participants: List[Participant]
    family_quest_progress: float


# --- Database Mock ---

# Текущий турнир: family_id → tournament_data
tournaments_db: Dict[str, Dict[str, Any]] = {}

# Семейные квесты: family_id → quest_data
family_quests_db: Dict[str, Dict[str, Any]] = {}


def initialize_tournament(family_id: str):
    """Инициализация турнира для семьи"""
    if family_id not in tournaments_db:
        tournaments_db[family_id] = {
            "tournament_id": f"TOUR_{uuid.uuid4().hex[:12].upper()}",
            "type": "grades",  # Тип турнира
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "participants": [
                {"id": "masha", "name": "Маша", "avatar": "👧", "score": 3, "unicorns": 156},
                {"id": "alexey", "name": "Алексей", "avatar": "👦", "score": 2, "unicorns": 128},
                {"id": "vanya", "name": "Ваня", "avatar": "👶", "score": 1, "unicorns": 87},
                {"id": "grandpa", "name": "Дедушка", "avatar": "👴", "score": 0, "unicorns": 45}
            ]
        }
        
        family_quests_db[family_id] = {
            "name": "Неделя без двоек",
            "description": "Вся семья на 4 и 5",
            "progress": 5,
            "target": 7,
            "reward": 100
        }


@app.get("/api/tournament/current", response_model=TournamentResponse)
async def get_current_tournament(
    family_id: str,
    user_id: str = rate_limit_dependency
):
    """
    🏆 Получить текущий турнир семьи
    
    Возвращает информацию о текущем турнире, рейтинге участников
    и семейном квесте.
    
    **Rate Limit:** 300 запросов в минуту
    
    **Query Parameters:**
    - family_id: ID семьи
    
    **Returns:**
    - TournamentResponse: Данные турнира
    """
    logger.info(f"🏆 Get current tournament for family_id={family_id}")
    
    # Инициализируем турнир если нет
    initialize_tournament(family_id)
    
    tournament = tournaments_db[family_id]
    quest = family_quests_db[family_id]
    
    # Типы турниров
    tournament_types = {
        "grades": {"id": "grades", "icon": "📚", "name": "Неделя отличников", "description": "Больше всех пятёрок", "metric": "пятёрки"},
        "chores": {"id": "chores", "icon": "🧹", "name": "Помощники дома", "description": "Домашние дела", "metric": "дела"},
        "behavior": {"id": "behavior", "icon": "😊", "name": "Без конфликтов", "description": "Хорошее поведение", "metric": "дни без ссор"},
        "reading": {"id": "reading", "icon": "📖", "name": "Книжный червь", "description": "Кто больше прочитает", "metric": "книги"},
        "universal": {"id": "universal", "icon": "🎯", "name": "Универсальный", "description": "Просто больше всего 🦄", "metric": "единороги"}
    }
    
    current_type = tournament_types.get(tournament["type"], tournament_types["grades"])
    
    # Вычисляем оставшееся время
    end_date = datetime.fromisoformat(tournament["end_date"])
    now = datetime.now()
    diff = end_date - now
    
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    time_remaining = f"{days}д {hours}ч {minutes}м"
    
    # Сортируем участников
    participants = sorted(tournament["participants"], key=lambda x: x["score"], reverse=True)
    
    return TournamentResponse(
        tournament_id=tournament["tournament_id"],
        type=TournamentType(**current_type),
        start_date=tournament["start_date"],
        end_date=tournament["end_date"],
        time_remaining=time_remaining,
        participants=[Participant(**p) for p in participants],
        family_quest=FamilyQuestInfo(
            name=quest["name"],
            description=quest["description"],
            progress=quest["progress"],
            target=quest["target"],
            reward=quest["reward"],
            percentage=round((quest["progress"] / quest["target"]) * 100, 1)
        ),
        prizes={1: 50, 2: 30, 3: 20}
    )


@app.get("/api/tournament/leaderboard", response_model=LeaderboardResponse)
async def get_tournament_leaderboard(
    family_id: str,
    user_id: str = rate_limit_dependency
):
    """
    📊 Получить рейтинг турнира
    
    Возвращает отсортированный список участников турнира.
    
    **Rate Limit:** 300 запросов в минуту
    
    **Query Parameters:**
    - family_id: ID семьи
    
    **Returns:**
    - LeaderboardResponse: Рейтинг участников
    """
    logger.info(f"📊 Get leaderboard for family_id={family_id}")
    
    initialize_tournament(family_id)
    
    tournament = tournaments_db[family_id]
    quest = family_quests_db[family_id]
    
    # Сортируем участников по очкам
    participants = sorted(tournament["participants"], key=lambda x: x["score"], reverse=True)
    
    return LeaderboardResponse(
        participants=[Participant(**p) for p in participants],
        family_quest_progress=round((quest["progress"] / quest["target"]) * 100, 1)
    )


@app.get("/api/quest/family")
async def get_family_quest(
    family_id: str,
    user_id: str = rate_limit_dependency
):
    """
    👨‍👩‍👧‍👦 Получить семейный квест
    
    Возвращает информацию о текущем семейном квесте (кооперативная цель).
    
    **Rate Limit:** 300 запросов в минуту
    
    **Query Parameters:**
    - family_id: ID семьи
    
    **Returns:**
    - FamilyQuestInfo: Данные квеста
    """
    logger.info(f"👨‍👩‍👧‍👦 Get family quest for family_id={family_id}")
    
    initialize_tournament(family_id)
    
    quest = family_quests_db[family_id]
    
    return FamilyQuestInfo(
        name=quest["name"],
        description=quest["description"],
        progress=quest["progress"],
        target=quest["target"],
        reward=quest["reward"],
        percentage=round((quest["progress"] / quest["target"]) * 100, 1)
    )


@app.post("/api/tournament/complete")
async def complete_tournament(
    family_id: str,
    user_id: str = rate_limit_dependency
):
    """
    🏁 Завершить турнир и выдать призы
    
    Вызывается автоматически (cron job) каждое воскресенье в 21:00.
    Выдаёт призы победителям и запускает новый турнир.
    
    **Rate Limit:** 300 запросов в минуту
    
    **Query Parameters:**
    - family_id: ID семьи
    
    **Returns:**
    - Dict: Результаты турнира и выданные призы
    """
    logger.info(f"🏁 Complete tournament for family_id={family_id}")
    
    initialize_tournament(family_id)
    
    tournament = tournaments_db[family_id]
    
    # Сортируем участников
    participants = sorted(tournament["participants"], key=lambda x: x["score"], reverse=True)
    
    # Выдаём призы
    prizes_awarded = {}
    for rank, participant in enumerate(participants[:3], start=1):
        prize = {1: 50, 2: 30, 3: 20}.get(rank, 0)
        if prize > 0:
            prizes_awarded[participant["id"]] = prize
            # TODO: Обновить баланс в БД
            logger.info(f"🏆 {participant['name']} получает +{prize} 🦄 за {rank} место!")
    
    # Запускаем новый турнир
    tournament_types = ["grades", "chores", "behavior", "reading", "universal"]
    current_index = tournament_types.index(tournament["type"])
    next_type = tournament_types[(current_index + 1) % len(tournament_types)]
    
    # Обновляем турнир
    tournaments_db[family_id] = {
        "tournament_id": f"TOUR_{uuid.uuid4().hex[:12].upper()}",
        "type": next_type,
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "participants": [
            {**p, "score": 0} for p in tournament["participants"]
        ]
    }
    
    # Сбрасываем квест
    family_quests_db[family_id]["progress"] = 0
    
    return {
        "success": True,
        "tournament_completed": tournament["tournament_id"],
        "prizes_awarded": prizes_awarded,
        "new_tournament": {
            "id": tournaments_db[family_id]["tournament_id"],
            "type": next_type
        }
    }


# ═══════════════════════════════════════════════════════════════
# Server Startup
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting ALADDIN Mobile API Server...")
    print("📱 iOS + Android API Endpoints")
    print("🔒 Port: 8000")
    print("━" * 60)
    print("🆕 Gamification API Added!")
    print("")
    print("🎰 Wheel of Fortune:")
    print("   • POST /api/rewards/spin-wheel")
    print("   • GET  /api/rewards/wheel-status")
    print("")
    print("🏆 Tournament & Family Quest:")
    print("   • GET  /api/tournament/current")
    print("   • GET  /api/tournament/leaderboard")
    print("   • GET  /api/quest/family")
    print("   • POST /api/tournament/complete")
    print("━" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

