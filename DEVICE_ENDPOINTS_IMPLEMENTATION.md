# 🚀 Device-Based Endpoints Implementation Guide
## Для сервера ALADDIN (149.154.65.180)

---

## 🎯 ЦЕЛЬ
Добавить device-based authentication endpoints на сервер ALADDIN для полной интеграции с мобильным приложением iOS.

---

## 📋 ЧТО НУЖНО СДЕЛАТЬ

### 1. ДОБАВИТЬ ENDPOINTS В auth_router.py

**Расположение файла:** `/opt/aladdin-backend/app/routers/auth_router.py`

**Добавить в конец файла перед последним `return router`:**

```python
# MARK: - Device-Based Authentication Endpoints
# Compatible with mobile app SubscriptionManager

from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import jwt
import uuid

# Request Models (matching mobile app)
class DeviceRegisterRequest(BaseModel):
    deviceId: str
    deviceType: str

class TrialInfo(BaseModel):
    daysRemaining: int
    isActive: bool
    activatedAt: datetime
    expiresAt: datetime

class TrialDeviceRegisterRequest(BaseModel):
    deviceId: str
    deviceType: str
    trialInfo: TrialInfo

# Response Models (matching mobile app)
class SubscriptionStatus(BaseModel):
    level: str
    limits: dict
    expiresAt: Optional[datetime]
    trialDaysRemaining: Optional[int]

class JWTDeviceRegisterResponse(BaseModel):
    token: str
    deviceId: str
    expiresAt: datetime
    registeredAt: datetime
    subscription: SubscriptionStatus

# Device Registration Endpoint
@router.post("/register-device", response_model=JWTDeviceRegisterResponse)
async def register_device_anonymously(request: DeviceRegisterRequest):
    """
    🔐 Device-based anonymous registration
    Creates account based on device ID without personal data
    """
    try:
        # Validate device ID
        try:
            uuid.UUID(request.deviceId)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid device ID format")

        # Get or create device user
        device_user = await get_or_create_device_user(request.deviceId, request.deviceType)

        # Free subscription data
        subscription_data = {
            "level": "free",
            "limits": get_free_limits(),
            "expiresAt": None,
            "trialDaysRemaining": None
        }

        # Generate JWT with subscription data
        token_data = {
            "sub": device_user.id,
            "device_id": request.deviceId,
            "subscription": subscription_data,
            "type": "device_auth"
        }

        access_token = create_access_token(token_data)

        return JWTDeviceRegisterResponse(
            token=access_token,
            deviceId=request.deviceId,
            expiresAt=datetime.utcnow() + timedelta(hours=24),
            registeredAt=device_user.created_at,
            subscription=SubscriptionStatus(**subscription_data)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

# Trial Registration Endpoint
@router.post("/register-device-trial", response_model=JWTDeviceRegisterResponse)
async def register_device_with_trial(request: TrialDeviceRegisterRequest):
    """
    🎁 Device registration with trial activation (14 days)
    """
    try:
        # Validate device ID
        try:
            uuid.UUID(request.deviceId)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid device ID format")

        # Get or create device user
        device_user = await get_or_create_device_user(request.deviceId, request.deviceType)

        # Trial subscription (14 days, 80% Premium features)
        trial_expires_at = datetime.utcnow() + timedelta(days=14)

        subscription_data = {
            "level": "trial",
            "limits": get_trial_limits(),
            "expiresAt": trial_expires_at,
            "trialDaysRemaining": request.trialInfo.daysRemaining
        }

        # Activate trial for device
        await activate_trial_for_device(request.deviceId, trial_expires_at)

        # Generate JWT
        token_data = {
            "sub": device_user.id,
            "device_id": request.deviceId,
            "subscription": subscription_data,
            "type": "device_auth_trial"
        }

        access_token = create_access_token(token_data)

        return JWTDeviceRegisterResponse(
            token=access_token,
            deviceId=request.deviceId,
            expiresAt=datetime.utcnow() + timedelta(hours=24),
            registeredAt=device_user.created_at,
            subscription=SubscriptionStatus(**subscription_data)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trial registration failed: {str(e)}")
```

---

### 2. ДОБАВИТЬ HELPER FUNCTIONS

**В том же файле или в отдельном сервисе добавить:**

```python
# Helper functions for device management

async def get_or_create_device_user(device_id: str, device_type: str):
    """Create or retrieve device-based user account"""
    # Implementation depends on your user model
    # Should create anonymous user account based on device ID
    pass

async def activate_trial_for_device(device_id: str, trial_expires_at: datetime):
    """Activate trial subscription for device"""
    # Implementation depends on your subscription system
    # Should set trial status and limits for device
    pass

def get_free_limits():
    """Free tier limits"""
    return {
        "ai_messages": 5,
        "scan_limit": 3,
        "family_members": 1
    }

def get_trial_limits():
    """Trial tier limits (80% of Premium)"""
    return {
        "ai_messages": 40,  # 80% of 50
        "scan_limit": 24,   # 80% of 30
        "family_members": 3 # 80% of 4
    }
```

---

### 3. ДОБАВИТЬ В БАЗУ ДАННЫХ

**Создать таблицу для device-based пользователей:**

```sql
CREATE TABLE device_users (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trial_activated BOOLEAN DEFAULT FALSE,
    trial_expires_at TIMESTAMP NULL,
    subscription_level VARCHAR(20) DEFAULT 'free'
);
```

---

### 4. ТЕСТИРОВАНИЕ

**После добавления endpoints протестировать:**

```bash
# Test regular device registration
curl -X POST "http://localhost:8002/api/auth/register-device" \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "12345678-1234-1234-1234-123456789abc",
    "deviceType": "ios"
  }'

# Test trial registration
curl -X POST "http://localhost:8002/api/auth/register-device-trial" \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "12345678-1234-1234-1234-123456789abc",
    "deviceType": "ios",
    "trialInfo": {
      "daysRemaining": 14,
      "isActive": true,
      "activatedAt": "2024-01-01T00:00:00Z",
      "expiresAt": "2024-01-15T00:00:00Z"
    }
  }'
```

---

## 🚨 ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **JWT Payload Structure** должна соответствовать тому, что ожидает мобильное приложение
2. **Subscription limits** должны быть совместимы с SubscriptionModels.swift
3. **Device ID validation** важна для безопасности
4. **Trial logic** должна активировать 14 дней с 80% функциями Premium

---

## 📞 АЛЬТЕРНАТИВНЫЕ СПОСОБЫ ПОДКЛЮЧЕНИЯ

Если SSH не работает:

1. **Через web-интерфейс** (если есть)
2. **Через FTP/SFTP клиент** (FileZilla, Cyberduck)
3. **Через API загрузки файлов** (если есть)
4. **Через git** (если репозиторий доступен)

---

## ✅ ПОСЛЕ РЕАЛИЗАЦИИ

После добавления endpoints:
1. Перезапустить сервер
2. Протестировать endpoints через curl
3. Проверить интеграцию с мобильным приложением
4. Убедиться, что JWT токены корректно парсятся