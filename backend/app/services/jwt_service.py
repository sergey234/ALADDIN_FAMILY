"""
JWT Service for ALADDIN Backend
Handles JWT token creation, validation and parsing
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.models.subscription import (
    JWTToken, SubscriptionPayload, TrialInfo,
    SubscriptionLimits, SubscriptionLevel
)

# JWT Configuration
SECRET_KEY = "aladdin-super-secret-key-change-in-production"  # TODO: Move to environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365  # 1 year


class JWTService:
    """JWT token management service"""

    @staticmethod
    def create_subscription_token(subscription: SubscriptionPayload) -> str:
        """Create JWT token with subscription payload"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": subscription.user_id or subscription.device_id,
            "device_id": subscription.device_id,
            "subscription": {
                "level": subscription.level.value,
                "start_date": subscription.start_date.isoformat(),
                "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
                "is_active": subscription.is_active,
                "trial_info": subscription.trial_info.dict() if subscription.trial_info else None,
                "limits": subscription.limits.dict(),
                "permissions": subscription.permissions
            },
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": "aladdin-backend"
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

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

            return {
                "token": token,
                "payload": payload,
                "subscription": subscription,
                "device_id": payload["device_id"],
                "expires_at": datetime.fromtimestamp(payload["exp"]),
                "issued_at": datetime.fromtimestamp(payload["iat"])
            }

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            print(f"JWT decode error: {e}")
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