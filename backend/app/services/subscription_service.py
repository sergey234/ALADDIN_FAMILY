"""
Subscription Service for ALADDIN Backend
Manages subscription lifecycle with PostgreSQL persistence
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.subscription import (
    SubscriptionPayload, SubscriptionLevel, TrialInfo,
    SubscriptionLimits, UsageCounters, DeviceRegisterRequest,
    TrialDeviceRegisterRequest
)
from app.repositories import SubscriptionRepository, SubscriptionDB


class SubscriptionService:
    """Main subscription management service with DB persistence"""

    @staticmethod
    def _ensure_user_for_device(db: Session, device_id: str, device_type: Optional[str] = None) -> str:
        """Ensure a real user row exists for a device and return stable user_id (as string for JWT payload compatibility)."""
        # users table exists in prod; we keep this logic DB-driven (no mocks).
        # If device is already registered, reuse same user id.
        row = db.execute(
            text("SELECT id FROM users WHERE device_id = :device_id LIMIT 1"),
            {"device_id": device_id},
        ).fetchone()
        if row and row[0] is not None:
            return str(row[0])

        created = db.execute(
            text(
                """
                INSERT INTO users (device_id, device_type, subscription_level, created_at)
                VALUES (:device_id, :device_type, 'free', NOW())
                RETURNING id
                """
            ),
            {"device_id": device_id, "device_type": device_type},
        ).fetchone()
        db.commit()
        return str(created[0])

    @staticmethod
    def register_device(db: Session, request: DeviceRegisterRequest) -> SubscriptionPayload:
        """Register new device with free subscription in DB"""
        repo = SubscriptionRepository(db)
        
        # Check if already exists
        existing = repo.get_subscription_by_device(request.device_id)
        if existing:
            return SubscriptionService._map_to_payload(existing)

        # Create free subscription data
        real_user_id = SubscriptionService._ensure_user_for_device(db, request.device_id, getattr(request, "device_type", None))

        sub_data = {
            "user_id": real_user_id,
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

        # If we already have a paid tier for this device - trial must not be granted again.
        if existing and existing.level in [
            SubscriptionLevel.PERSONAL.value,
            SubscriptionLevel.FAMILY.value,
            SubscriptionLevel.PREMIUM.value
        ]:
            return SubscriptionService._map_to_payload(existing)

        # If we have an existing trial record (or at least a stored trial_end_date), use it as an anti-abuse ledger.
        if existing and existing.trial_end_date:
            # Trial is still active -> idempotent: do not extend/re-issue.
            if now < existing.trial_end_date:
                return SubscriptionService._map_to_payload(existing)

            # Trial has expired -> downgrade to free, but KEEP trial_end_date as history to prevent re-issuing.
            updates = {
                "level": SubscriptionLevel.FREE.value,
                "status": "active",
                "start_date": now,
                "end_date": None,
                "limits": SubscriptionLimits.free_limits().dict(),
                "features": []
            }
            db_sub = repo.update_subscription(existing, updates)
            return SubscriptionService._map_to_payload(db_sub)

        # No existing trial ledger -> create a new trial (server-side source of truth).
        duration_days = getattr(request.trial_info, "duration_days", 14) or 14
        computed_trial_end = now + timedelta(days=duration_days)

        real_user_id = SubscriptionService._ensure_user_for_device(db, request.device_id, getattr(request, "device_type", None))

        sub_data = {
            "user_id": real_user_id,
            "device_id": request.device_id,
            "level": SubscriptionLevel.TRIAL.value,
            "status": "trial",
            "start_date": now,
            "trial_end_date": computed_trial_end,
            "end_date": computed_trial_end,
            "limits": SubscriptionLimits.trial_limits().dict(),
            "features": ["basic_protection", "ai_assistant_basic"]
        }

        if existing:
            db_sub = repo.update_subscription(existing, sub_data)
        else:
            db_sub = repo.create_subscription(sub_data)

        return SubscriptionService._map_to_payload(db_sub)

    @staticmethod
    def save_refresh_token(db: Session, device_id: str, refresh_token: str, expires_at: datetime) -> None:
        """Persist refresh token for device auth flow compatibility."""
        db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS device_refresh_tokens (
                    id SERIAL PRIMARY KEY,
                    device_id VARCHAR(255) NOT NULL,
                    refresh_token TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )
        db.execute(
            text(
                """
                INSERT INTO device_refresh_tokens (device_id, refresh_token, expires_at)
                VALUES (:device_id, :refresh_token, :expires_at)
                """
            ),
            {"device_id": device_id, "refresh_token": refresh_token, "expires_at": expires_at},
        )
        db.commit()

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
