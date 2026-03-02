from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from .models.subscription import SubscriptionLevel
# We'll use the models defined in models.py on the server, but for now we'll define the persistence logic
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from .database.database import Base

class SubscriptionDB(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    device_id = Column(String(255), nullable=False, index=True)
    level = Column(String(50), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="active", index=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True, index=True)
    trial_end_date = Column(DateTime, nullable=True, index=True)
    auto_renew = Column(Boolean, default=False)
    limits = Column(JSONB)
    features = Column(ARRAY(Text), default=[])
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    version = Column(Integer, default=1)

class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_subscription_by_device(self, device_id: str) -> Optional[SubscriptionDB]:
        return self.db.query(SubscriptionDB).filter(SubscriptionDB.device_id == device_id).first()

    def create_subscription(self, data: Dict[str, Any]) -> SubscriptionDB:
        db_sub = SubscriptionDB(**data)
        self.db.add(db_sub)
        self.db.commit()
        self.db.refresh(db_sub)
        return db_sub

    def update_subscription(self, db_sub: SubscriptionDB, updates: Dict[str, Any]) -> SubscriptionDB:
        for key, value in updates.items():
            setattr(db_sub, key, value)
        db_sub.version += 1
        self.db.commit()
        self.db.refresh(db_sub)
        return db_sub
