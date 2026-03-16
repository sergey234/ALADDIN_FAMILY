# 📱 Device-Based Authentication Endpoints for ALADDIN Server
# These endpoints enable anonymous device registration without personal data collection
# Compatible with mobile app's SubscriptionManager

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import jwt
import uuid

from app.core.config import settings
from app.core.security import create_access_token
from app.models.subscription import SubscriptionLevel, SubscriptionLimits
from app.services.subscription_service import SubscriptionService

# ✅ BUILD 122: Импорт create_refresh_token из auth_router
try:
    from app.routers.auth_router import create_refresh_token
except ImportError:
    # Fallback: если не можем импортировать, создадим локально
    try:
        from app.auth import JWT_SECRET, JWT_ALGORITHM
    except ImportError:
        # Если и это не работает, используем значения по умолчанию
        JWT_SECRET = os.getenv("JWT_SECRET", "aladdin-secret-key")
        JWT_ALGORITHM = "HS256"
    
    def create_refresh_token(data: dict) -> str:
        """Создание JWT refresh token (действителен 30 дней)"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=30)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": to_encode.get("type", "device_refresh")  # ✅ BUILD 122: Используем тип из data или device_refresh
        })
        
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt

router = APIRouter()

# MARK: - Request Models (matching mobile app expectations)

class DeviceRegisterRequest(BaseModel):
    """Device registration request from mobile app"""
    deviceId: str
    deviceType: str

class TrialInfo(BaseModel):
    """Trial information for trial registration"""
    daysRemaining: int
    isActive: bool
    activatedAt: datetime
    expiresAt: datetime

class TrialDeviceRegisterRequest(BaseModel):
    """Trial device registration request"""
    deviceId: str
    deviceType: str
    trialInfo: TrialInfo

# MARK: - Response Models (matching mobile app expectations)

class SubscriptionStatus(BaseModel):
    """Subscription status for response"""
    level: str  # "trial", "free", "personal", "family", "premium"
    limits: dict
    expiresAt: Optional[datetime]
    trialDaysRemaining: Optional[int]

class JWTDeviceRegisterResponse(BaseModel):
    """JWT device registration response for mobile app"""
    token: str
    refresh_token: Optional[str] = None  # ✅ BUILD 122: Опциональный для обратной совместимости
    deviceId: str
    expiresAt: datetime
    registeredAt: datetime
    subscription: SubscriptionStatus

# MARK: - Endpoints

@router.post("/register-device", response_model=JWTDeviceRegisterResponse)
async def register_device_anonymously(
    request: DeviceRegisterRequest,
    subscription_service: SubscriptionService = Depends()
):
    """
    🔐 Device-based anonymous registration
    Creates account based on device ID without collecting personal data
    Returns JWT token with Free subscription level
    """
    try:
        # Validate device ID format
        try:
            uuid.UUID(request.deviceId)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid device ID format")

        # Create or get existing device-based user
        device_user = await subscription_service.get_or_create_device_user(
            device_id=request.deviceId,
            device_type=request.deviceType
        )

        # Create Free subscription for device
        subscription_data = {
            "level": "free",
            "limits": SubscriptionLimits.free_limits(),
            "expiresAt": None,
            "trialDaysRemaining": None
        }

        # Generate JWT token with subscription data embedded
        token_data = {
            "sub": device_user.id,
            "device_id": request.deviceId,
            "subscription": subscription_data,
            "type": "device_auth"
        }

        access_token = create_access_token(token_data)

        # ✅ BUILD 122: Создание refresh token для device tokens
        refresh_token_data = {
            "sub": device_user.id,
            "device_id": request.deviceId,
            "type": "device_refresh"  # ✅ Тип токена для device refresh
        }
        refresh_token = create_refresh_token(refresh_token_data)

        # Prepare response
        response = JWTDeviceRegisterResponse(
            token=access_token,
            refresh_token=refresh_token,  # ✅ BUILD 122: Добавлен refresh token
            deviceId=request.deviceId,
            expiresAt=datetime.utcnow() + timedelta(hours=24),  # 24 hour token
            registeredAt=device_user.created_at,
            subscription=SubscriptionStatus(**subscription_data)
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Device registration failed: {str(e)}")

@router.post("/register-device-trial", response_model=JWTDeviceRegisterResponse)
async def register_device_with_trial(
    request: TrialDeviceRegisterRequest,
    subscription_service: SubscriptionService = Depends()
):
    """
    🎁 Device-based registration with trial activation
    Creates account with 14-day trial period
    """
    try:
        # Validate device ID format
        try:
            uuid.UUID(request.deviceId)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid device ID format")

        # Create or get existing device-based user
        device_user = await subscription_service.get_or_create_device_user(
            device_id=request.deviceId,
            device_type=request.deviceType
        )

        # Activate trial subscription (14 days, 80% of Premium features)
        trial_expires_at = datetime.utcnow() + timedelta(days=14)

        subscription_data = {
            "level": "trial",
            "limits": SubscriptionLimits.trial_limits(),  # 80% of Premium
            "expiresAt": trial_expires_at,
            "trialDaysRemaining": request.trialInfo.daysRemaining
        }

        # Update user subscription to trial
        await subscription_service.activate_trial_for_device(
            device_id=request.deviceId,
            trial_expires_at=trial_expires_at
        )

        # Generate JWT token with trial subscription data
        token_data = {
            "sub": device_user.id,
            "device_id": request.deviceId,
            "subscription": subscription_data,
            "type": "device_auth_trial"
        }

        access_token = create_access_token(token_data)

        # ✅ BUILD 122: Создание refresh token для device tokens (trial)
        refresh_token_data = {
            "sub": device_user.id,
            "device_id": request.deviceId,
            "type": "device_refresh"  # ✅ Тип токена для device refresh
        }
        refresh_token = create_refresh_token(refresh_token_data)

        # Prepare response
        response = JWTDeviceRegisterResponse(
            token=access_token,
            refresh_token=refresh_token,  # ✅ BUILD 122: Добавлен refresh token
            deviceId=request.deviceId,
            expiresAt=datetime.utcnow() + timedelta(hours=24),  # 24 hour token
            registeredAt=device_user.created_at,
            subscription=SubscriptionStatus(**subscription_data)
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trial device registration failed: {str(e)}")

# MARK: - Helper Functions (to be implemented in SubscriptionService)

"""
Required methods to add to SubscriptionService:

async def get_or_create_device_user(self, device_id: str, device_type: str) -> User:
    '''Create or retrieve device-based user account'''
    pass

async def activate_trial_for_device(self, device_id: str, trial_expires_at: datetime) -> None:
    '''Activate trial subscription for device'''
    pass

SubscriptionLimits helper methods:
@classmethod
def free_limits(cls) -> dict:
    return {
        "ai_messages": 5,
        "scan_limit": 3,
        "family_members": 1
    }

@classmethod
def trial_limits(cls) -> dict:
    return {
        "ai_messages": 40,  # 80% of Premium (50)
        "scan_limit": 24,   # 80% of Premium (30)
        "family_members": 3 # 80% of Premium (4)
    }
"""