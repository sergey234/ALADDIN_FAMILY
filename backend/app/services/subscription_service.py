"""
Subscription Service for ALADDIN Backend
Manages subscription lifecycle, feature access, and usage tracking
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from app.models.subscription import (
    SubscriptionPayload, SubscriptionLevel, TrialInfo,
    SubscriptionLimits, UsageCounters, DeviceRegisterRequest,
    TrialDeviceRegisterRequest
)
from app.services.jwt_service import JWTService


class SubscriptionService:
    """Main subscription management service"""

    # In-memory storage for demo (replace with database)
    _subscriptions: Dict[str, SubscriptionPayload] = {}

    @classmethod
    def register_device(cls, request: DeviceRegisterRequest) -> SubscriptionPayload:
        """Register new device with free subscription"""
        device_id = request.device_id

        # Create free subscription
        subscription = SubscriptionPayload(
            level=SubscriptionLevel.FREE,
            start_date=datetime.utcnow(),
            end_date=None,  # Free tier doesn't expire
            is_active=True,
            trial_info=None,
            limits=SubscriptionLimits.free_limits(),
            permissions={},
            device_id=device_id,
            user_id=None
        )

        # Store subscription
        cls._subscriptions[device_id] = subscription

        return subscription

    @classmethod
    def register_device_with_trial(cls, request: TrialDeviceRegisterRequest) -> SubscriptionPayload:
        """Register device with trial period"""
        device_id = request.device_id

        # Create trial subscription
        subscription = SubscriptionPayload(
            level=SubscriptionLevel.TRIAL,
            start_date=datetime.utcnow(),
            end_date=request.trial_info.end_date,
            is_active=True,
            trial_info=request.trial_info,
            limits=SubscriptionLimits.trial_limits(),
            permissions={},
            device_id=device_id,
            user_id=None
        )

        # Store subscription
        cls._subscriptions[device_id] = subscription

        return subscription

    @classmethod
    def get_subscription(cls, device_id: str) -> Optional[SubscriptionPayload]:
        """Get subscription by device ID"""
        return cls._subscriptions.get(device_id)

    @classmethod
    def update_subscription(cls, device_id: str, subscription: SubscriptionPayload) -> bool:
        """Update subscription for device"""
        cls._subscriptions[device_id] = subscription
        return True

    @classmethod
    def upgrade_subscription(cls, device_id: str, new_level: 'SubscriptionLevel') -> Optional[SubscriptionPayload]:
        """Upgrade subscription to new level"""
        subscription = cls.get_subscription(device_id)
        if not subscription:
            return None

        # Update subscription level
        subscription.level = new_level

        # Set new limits based on level
        if new_level == SubscriptionLevel.PERSONAL:
            subscription.limits = SubscriptionLimits(
                max_devices=3,
                max_ai_messages=100,
                max_scans=50,
                max_reports=10
            )
        elif new_level == SubscriptionLevel.FAMILY:
            subscription.limits = SubscriptionLimits(
                max_devices=5,
                max_ai_messages=200,
                max_scans=100,
                max_reports=20
            )
        elif new_level == SubscriptionLevel.PREMIUM:
            subscription.limits = SubscriptionLimits(
                max_devices=10,
                max_ai_messages=-1,  # Unlimited
                max_scans=-1,       # Unlimited
                max_reports=-1      # Unlimited
            )

        # Update permissions based on level
        subscription.permissions = cls._get_permissions_for_level(new_level)

        cls._subscriptions[device_id] = subscription
        return subscription

    @classmethod
    def cancel_subscription(cls, device_id: str) -> bool:
        """Cancel subscription (downgrade to free)"""
        subscription = cls.get_subscription(device_id)
        if not subscription:
            return False

        # Downgrade to free
        subscription.level = SubscriptionLevel.FREE
        subscription.limits = SubscriptionLimits.free_limits()
        subscription.permissions = {}

        cls._subscriptions[device_id] = subscription
        return True

    @classmethod
    def check_feature_access(cls, device_id: str, feature_id: str) -> Dict[str, Any]:
        """Check if device can access specific feature"""
        subscription = cls.get_subscription(device_id)

        if not subscription:
            return {
                "accessible": False,
                "reason": "no_subscription",
                "subscription_level": SubscriptionLevel.FREE.value
            }

        # Check if feature is available for current level
        accessible = cls._is_feature_available_for_level(feature_id, subscription.level)

        return {
            "accessible": accessible,
            "reason": None if accessible else "insufficient_level",
            "subscription_level": subscription.level.value,
            "limits": subscription.limits.dict() if not accessible else None
        }

    @classmethod
    def track_usage(cls, device_id: str, resource_type: str, amount: int = 1) -> bool:
        """Track resource usage"""
        subscription = cls.get_subscription(device_id)
        if not subscription:
            return False

        # Increment usage counter
        subscription.limits.current_usage.increment(resource_type, amount)

        # Check if limit exceeded
        if subscription.limits.is_limit_exceeded(resource_type):
            return False

        cls._subscriptions[device_id] = subscription
        return True

    @classmethod
    def reset_monthly_usage(cls, device_id: str) -> bool:
        """Reset monthly usage counters"""
        subscription = cls.get_subscription(device_id)
        if not subscription:
            return False

        subscription.limits.current_usage = UsageCounters()
        cls._subscriptions[device_id] = subscription
        return True

    @classmethod
    def get_trial_status(cls, device_id: str) -> Optional[Dict[str, Any]]:
        """Get trial status for device"""
        subscription = cls.get_subscription(device_id)
        if not subscription or not subscription.trial_info:
            return None

        trial = subscription.trial_info
        return {
            "is_active": trial.is_active,
            "days_remaining": trial.days_remaining,
            "start_date": trial.start_date.isoformat(),
            "end_date": trial.end_date.isoformat()
        }

    @staticmethod
    def _is_feature_available_for_level(feature_id: str, level: SubscriptionLevel) -> bool:
        """Check if feature is available for subscription level"""
        # Basic feature mapping (simplified)
        feature_requirements = {
            # Trial features (80% of basic)
            "basic_scan": [SubscriptionLevel.TRIAL, SubscriptionLevel.FREE, SubscriptionLevel.PERSONAL, SubscriptionLevel.FAMILY, SubscriptionLevel.PREMIUM],
            "ai_assistant_basic": [SubscriptionLevel.TRIAL, SubscriptionLevel.PERSONAL, SubscriptionLevel.FAMILY, SubscriptionLevel.PREMIUM],

            # Personal+ features
            "advanced_scanning": [SubscriptionLevel.PERSONAL, SubscriptionLevel.FAMILY, SubscriptionLevel.PREMIUM],
            "family_controls": [SubscriptionLevel.FAMILY, SubscriptionLevel.PREMIUM],
            "parental_monitoring": [SubscriptionLevel.FAMILY, SubscriptionLevel.PREMIUM],

            # Premium features
            "deepfake_detection": [SubscriptionLevel.PREMIUM],
            "iot_security": [SubscriptionLevel.PREMIUM],
            "advanced_analytics": [SubscriptionLevel.PREMIUM],
            "unlimited_scans": [SubscriptionLevel.PREMIUM]
        }

        required_levels = feature_requirements.get(feature_id, [SubscriptionLevel.FREE])
        return level in required_levels

    @staticmethod
    def _get_permissions_for_level(level: SubscriptionLevel) -> Dict[str, Any]:
        """Get permissions dictionary for subscription level"""
        base_permissions = {
            "basic_scanning": True,
            "basic_protection": True
        }

        if level in [SubscriptionLevel.PERSONAL, SubscriptionLevel.FAMILY, SubscriptionLevel.PREMIUM]:
            base_permissions.update({
                "advanced_scanning": True,
                "ai_assistant": True
            })

        if level in [SubscriptionLevel.FAMILY, SubscriptionLevel.PREMIUM]:
            base_permissions.update({
                "family_controls": True,
                "parental_monitoring": True,
                "multi_device": True
            })

        if level == SubscriptionLevel.PREMIUM:
            base_permissions.update({
                "deepfake_detection": True,
                "iot_security": True,
                "advanced_analytics": True,
                "unlimited_usage": True
            })

        return base_permissions

    @classmethod
    def get_all_subscriptions(cls) -> List[SubscriptionPayload]:
        """Get all subscriptions (for admin/debug)"""
        return list(cls._subscriptions.values())