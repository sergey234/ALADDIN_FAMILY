"""
JWT Service for ALADDIN Backend
Handles JWT token creation, validation and parsing
"""

import jwt
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.models.subscription import (
    JWTToken, SubscriptionPayload, TrialInfo,
    SubscriptionLimits, SubscriptionLevel
)

# ✅ JWT-003: Настройка логирования для диагностики JWT
logger = logging.getLogger(__name__)

# ✅ JWT-011: Унифицированный SECRET_KEY (совпадает с app/auth/auth.py)
# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "aladdin-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365  # 1 year


class JWTService:
    """JWT token management service"""

    @staticmethod
    def create_subscription_token(subscription: SubscriptionPayload) -> str:
        """Create JWT token with subscription payload"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        # PyJWT may accept datetime objects for exp/iat, but to avoid any JSON serialization edge-cases
        # we store them as numeric timestamps explicitly.
        exp_ts = int(expire.timestamp())
        iat_ts = int(datetime.utcnow().timestamp())

        payload = {
            "sub": subscription.user_id or subscription.device_id,
            "device_id": subscription.device_id,
            "subscription": {
                "level": subscription.level.value,
                "start_date": subscription.start_date.isoformat(),
                "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
                "is_active": subscription.is_active,
                # PyJWT uses json.dumps under the hood and can't serialize datetime objects.
                # Keep trial_info as ISO-8601 strings for stable JWT payload encoding.
                "trial_info": (
                    {
                        "start_date": subscription.trial_info.start_date.isoformat(),
                        "end_date": subscription.trial_info.end_date.isoformat(),
                        "duration_days": subscription.trial_info.duration_days,
                    }
                    if subscription.trial_info else None
                ),
                "limits": subscription.limits.dict(),
                "permissions": subscription.permissions
            },
            "exp": exp_ts,
            "iat": iat_ts,
            "iss": "aladdin-backend"
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate JWT token"""
        # ✅ JWT-003: Детальное логирование попытки декодирования
        token_preview = token[:20] + "..." + token[-20:] if len(token) > 40 else token
        secret_preview = SECRET_KEY[:10] + "..." if len(SECRET_KEY) > 10 else SECRET_KEY
        
        logger.info(f"🔐 [JWT-003] JWTService.decode_token: Попытка декодирования токена")
        logger.info(f"   - Token preview: {token_preview}")
        logger.info(f"   - Token length: {len(token)} символов")
        logger.info(f"   - SECRET_KEY preview: {secret_preview}")
        logger.info(f"   - SECRET_KEY length: {len(SECRET_KEY)} символов")
        logger.info(f"   - Algorithm: {ALGORITHM}")
        
        try:
            # ✅ JWT-010: Добавлен leeway для защиты от разницы времени между клиентом и сервером
            # Leeway = 60 секунд допуска для синхронизации времени
            payload = jwt.decode(
                token, 
                SECRET_KEY, 
                algorithms=[ALGORITHM],
                options={"verify_exp": True},
                leeway=60  # 60 секунд допуска для разницы времени
            )

            # Convert subscription data back to proper format
            subscription_data = payload.get("subscription", {})

            # Parse trial info if present
            trial_info = None
            if subscription_data.get("trial_info"):
                trial_dict = subscription_data["trial_info"]
                trial_info = TrialInfo(
                    start_date=datetime.fromisoformat(trial_dict["start_date"]),
                    end_date=datetime.fromisoformat(trial_dict["end_date"]),
                    duration_days=trial_dict["duration_days"]
                )

            # Parse limits
            limits_dict = subscription_data.get("limits", {})
            limits = SubscriptionLimits(**limits_dict)

            # Create subscription payload
            subscription = SubscriptionPayload(
                level=SubscriptionLevel(subscription_data["level"]),
                start_date=datetime.fromisoformat(subscription_data["start_date"]),
                end_date=datetime.fromisoformat(subscription_data["end_date"]) if subscription_data.get("end_date") else None,
                is_active=subscription_data.get("is_active", True),
                trial_info=trial_info,
                limits=limits,
                permissions=subscription_data.get("permissions", {}),
                device_id=payload["device_id"],
                user_id=payload.get("sub")
            )

            # ✅ JWT-003: Логирование успешного декодирования
            user_id = payload.get("sub") or payload.get("user_id") or payload.get("device_id", "unknown")
            exp = payload.get("exp", "unknown")
            subscription_level = subscription_data.get("level", "unknown")
            logger.info(f"✅ [JWT-003] JWTService.decode_token: Успешно декодирован токен")
            logger.info(f"   - User/Device ID: {user_id}")
            logger.info(f"   - Subscription level: {subscription_level}")
            logger.info(f"   - Expires at: {exp}")

            return {
                "token": token,
                "payload": payload,
                "subscription": subscription,
                "device_id": payload["device_id"],
                "expires_at": datetime.fromtimestamp(payload["exp"]),
                "issued_at": datetime.fromtimestamp(payload["iat"])
            }

        except jwt.ExpiredSignatureError as e:
            # ✅ JWT-003: Детальное логирование ошибки истечения
            logger.error(f"❌ [JWT-003] JWTService.decode_token: Token expired")
            logger.error(f"   - Error: {str(e)}")
            logger.error(f"   - Token preview: {token_preview}")
            return None
        except jwt.InvalidTokenError as e:
            # ✅ JWT-003: Детальное логирование ошибки невалидного токена
            logger.error(f"❌ [JWT-003] JWTService.decode_token: Invalid token")
            logger.error(f"   - Error: {str(e)}")
            logger.error(f"   - Error type: {type(e).__name__}")
            logger.error(f"   - Token preview: {token_preview}")
            logger.error(f"   - SECRET_KEY preview: {secret_preview}")
            return None
        except Exception as e:
            # ✅ JWT-003: Логирование неожиданных ошибок
            logger.error(f"❌ [JWT-003] JWTService.decode_token: Unexpected error")
            logger.error(f"   - Error: {str(e)}")
            logger.error(f"   - Error type: {type(e).__name__}")
            logger.error(f"   - Token preview: {token_preview}")
            return None

    @staticmethod
    def parse_jwt_token(token: str) -> Optional[JWTToken]:
        """Parse JWT token into JWTToken model"""
        decoded = JWTService.decode_token(token)
        if not decoded:
            return None

        subscription = decoded["subscription"]

        return JWTToken(
            token=token,
            device_id=decoded["device_id"],
            subscription_level=subscription.level,
            trial_info=subscription.trial_info,
            expires_at=decoded["expires_at"],
            issued_at=decoded["issued_at"],
            issuer="aladdin-backend",
            limits=subscription.limits,
            components=[]  # TODO: Add components logic
        )

    @staticmethod
    def validate_token(token: str) -> bool:
        """Validate JWT token"""
        decoded = JWTService.decode_token(token)
        return decoded is not None

    @staticmethod
    def get_subscription_from_token(token: str) -> Optional[SubscriptionPayload]:
        """Extract subscription payload from token"""
        decoded = JWTService.decode_token(token)
        if not decoded:
            return None
        return decoded["subscription"]