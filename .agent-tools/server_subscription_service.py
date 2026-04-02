"""
Subscription Service for ALADDIN Backend
Manages subscription lifecycle with PostgreSQL persistence
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.subscription import (
    SubscriptionPayload, SubscriptionLevel, TrialInfo,
    SubscriptionLimits, UsageCounters, DeviceRegisterRequest,
    TrialDeviceRegisterRequest
)
from app.repositories import SubscriptionRepository, SubscriptionDB


class SubscriptionService:
    """Main subscription management service with DB persistence"""

    @staticmethod
    def register_device(db: Session, request: DeviceRegisterRequest) -> SubscriptionPayload:
        """Register new device with free subscription in DB"""
        repo = SubscriptionRepository(db)
        
        # Check if already exists
        existing = repo.get_subscription_by_device(request.device_id)
        if existing:
            return SubscriptionService._map_to_payload(existing)

        # Create free subscription data
        sub_data = {
            "user_id": "anonymous",
            "device_id": request.device_id,
            "level": SubscriptionLevel.FREE.value,
            "status": "active",
            "start_date": datetime.utcnow(),
            "limits": SubscriptionLimits.free_limits().dict(),
            "features": []
        }

        db_sub = repo.create_subscription(sub_data)
        return SubscriptionService._map_to_payload(db_sub)

    @staticmethod
    def register_device_with_trial(db: Session, request: TrialDeviceRegisterRequest) -> SubscriptionPayload:
        """Register device with trial period in DB"""
        repo = SubscriptionRepository(db)
        
        now = datetime.utcnow()
        existing = repo.get_subscription_by_device(request.device_id)

        # Если у устройства уже есть платный tier — trial больше не выдаём.
        if existing and existing.level in [
            SubscriptionLevel.PERSONAL.value,
            SubscriptionLevel.FAMILY.value,
            SubscriptionLevel.PREMIUM.value,
        ]:
            return SubscriptionService._map_to_payload(existing)

        # Если ledger trial_end_date уже есть — это источник истины для анти-абьюза.
        if existing and existing.trial_end_date:
            # Trial ещё активен -> идемпотентно возвращаем текущую запись.
            if now < existing.trial_end_date:
                return SubscriptionService._map_to_payload(existing)

            # Trial истёк -> даунгрейдим на free, но trial_end_date НЕ трогаем (чтобы не выдать trial заново).
            updates = {
                "level": SubscriptionLevel.FREE.value,
                "status": "active",
                "start_date": now,
                "end_date": None,
                "limits": SubscriptionLimits.free_limits().dict(),
                "features": [],
            }
            db_sub = repo.update_subscription(existing, updates)
            return SubscriptionService._map_to_payload(db_sub)

        # Нет ledger -> создаём новый trial.
        duration_days = getattr(request.trial_info, "duration_days", 14) or 14
        trial_end_date = request.trial_info.end_date or (now + timedelta(days=duration_days))

        sub_data = {
            "user_id": "anonymous",
            "device_id": request.device_id,
            "level": SubscriptionLevel.TRIAL.value,
            "status": "trial",
            "start_date": now,
            "trial_end_date": trial_end_date,
            "end_date": trial_end_date,
            "limits": SubscriptionLimits.trial_limits().dict(),
            "features": ["basic_protection", "ai_assistant_basic"],
        }

        if existing:
            db_sub = repo.update_subscription(existing, sub_data)
        else:
            db_sub = repo.create_subscription(sub_data)

        return SubscriptionService._map_to_payload(db_sub)

    @staticmethod
    def upgrade_subscription(db: Session, device_id: str, new_level: SubscriptionLevel) -> Optional[SubscriptionPayload]:
        """Upgrade subscription to new level in DB"""
        repo = SubscriptionRepository(db)
        db_sub = repo.get_subscription_by_device(device_id)
        if not db_sub:
            return None

        # Calculate new limits
        limits = SubscriptionLimits.free_limits()
        features = []
        
        if new_level == SubscriptionLevel.PERSONAL:
            limits = SubscriptionLimits(max_devices=3, max_ai_messages=100, max_scans=50, max_reports=10)
            features = ["advanced_scanning", "ai_assistant"]
        elif new_level == SubscriptionLevel.FAMILY:
            limits = SubscriptionLimits(max_devices=5, max_ai_messages=200, max_scans=100, max_reports=20)
            features = ["advanced_scanning", "ai_assistant", "family_controls", "parental_monitoring"]
        elif new_level == SubscriptionLevel.PREMIUM:
            limits = SubscriptionLimits(max_devices=10, max_ai_messages=1000, max_scans=1000, max_reports=100)
            features = ["advanced_scanning", "ai_assistant", "family_controls", "parental_monitoring", "deepfake_detection", "iot_security"]

        updates = {
            "level": new_level.value,
            "status": "active",
            "limits": limits.dict(),
            "features": features,
            "updated_at": datetime.utcnow()
        }

        updated_db_sub = repo.update_subscription(db_sub, updates)
        return SubscriptionService._map_to_payload(updated_db_sub)

    @staticmethod
    def get_subscription(db: Session, device_id: str) -> Optional[SubscriptionPayload]:
        """Get subscription from DB"""
        repo = SubscriptionRepository(db)
        db_sub = repo.get_subscription_by_device(device_id)
        if not db_sub:
            return None
        return SubscriptionService._map_to_payload(db_sub)

    @staticmethod
    def _map_to_payload(db_sub: SubscriptionDB) -> SubscriptionPayload:
        """Map DB model to Pydantic payload"""
        trial_info = None
        if db_sub.trial_end_date:
            trial_info = TrialInfo(
                start_date=db_sub.start_date,
                end_date=db_sub.trial_end_date,
                duration_days=14
            )

        return SubscriptionPayload(
            level=SubscriptionLevel(db_sub.level),
            start_date=db_sub.start_date,
            end_date=db_sub.end_date,
            is_active=db_sub.status in ["active", "trial"],
            trial_info=trial_info,
            limits=SubscriptionLimits(**db_sub.limits) if db_sub.limits else SubscriptionLimits.free_limits(),
            permissions={f: True for f in db_sub.features} if db_sub.features else {},
            device_id=db_sub.device_id,
            user_id=db_sub.user_id
        )
