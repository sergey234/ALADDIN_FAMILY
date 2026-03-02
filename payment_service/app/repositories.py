from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from .models import Subscription, UsageTracking, AuditLog, PromoCode, Payment
import json

class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- Subscription Operations ---

    def get_subscription_by_user_device(self, user_id: str, device_id: str) -> Optional[Subscription]:
        return self.db.query(Subscription).filter(
            and_(Subscription.user_id == user_id, Subscription.device_id == device_id)
        ).first()

    def get_active_subscription(self, user_id: str, device_id: str) -> Optional[Subscription]:
        return self.db.query(Subscription).filter(
            and_(
                Subscription.user_id == user_id,
                Subscription.device_id == device_id,
                Subscription.status == 'active'
            )
        ).first()

    def create_subscription(self, subscription_data: Dict[str, Any]) -> Subscription:
        db_subscription = Subscription(**subscription_data)
        self.db.add(db_subscription)
        self.db.commit()
        self.db.refresh(db_subscription)
        return db_subscription

    def update_subscription(self, subscription_id: int, updates: Dict[str, Any]) -> Optional[Subscription]:
        db_subscription = self.db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if db_subscription:
            for key, value in updates.items():
                setattr(db_subscription, key, value)
            db_subscription.version += 1
            db_subscription.updated_at = func.now()
            self.db.commit()
            self.db.refresh(db_subscription)
        return db_subscription

    # --- Usage Tracking Operations ---

    def get_usage(self, subscription_id: int, resource_type: str, period_start: date) -> Optional[UsageTracking]:
        return self.db.query(UsageTracking).filter(
            and_(
                UsageTracking.subscription_id == subscription_id,
                UsageTracking.resource_type == resource_type,
                UsageTracking.period_start == period_start
            )
        ).first()

    def increment_usage(self, subscription_id: int, resource_type: str, amount: int = 1) -> UsageTracking:
        # Assuming daily reset for most resources for now
        today = date.today()
        # End of day
        period_end = today
        
        db_usage = self.get_usage(subscription_id, resource_type, today)
        if db_usage:
            db_usage.amount += amount
            db_usage.updated_at = func.now()
        else:
            db_usage = UsageTracking(
                subscription_id=subscription_id,
                resource_type=resource_type,
                amount=amount,
                period_start=today,
                period_end=period_end
            )
            self.db.add(db_usage)
        
        self.db.commit()
        self.db.refresh(db_usage)
        return db_usage

    # --- Audit Log Operations ---

    def create_audit_log(self, audit_data: Dict[str, Any]) -> AuditLog:
        db_log = AuditLog(**audit_data)
        self.db.add(db_log)
        self.db.commit()
        return db_log

    # --- Promo Code Operations ---

    def get_promo_code(self, code: str) -> Optional[PromoCode]:
        return self.db.query(PromoCode).filter(
            and_(
                PromoCode.code == code,
                PromoCode.is_active == True,
                (PromoCode.valid_until == None) | (PromoCode.valid_until > datetime.now())
            )
        ).first()

    def use_promo_code(self, code_id: int) -> bool:
        promo = self.db.query(PromoCode).filter(PromoCode.id == code_id).first()
        if promo and (promo.max_uses is None or promo.used_count < promo.max_uses):
            promo.used_count += 1
            self.db.commit()
            return True
        return False
