import datetime as dt
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    Numeric,
)
from typing import Optional, List
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

Base = declarative_base()


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    device_id = Column(String(255), nullable=False, index=True)
    level = Column(String(50), nullable=False, index=True)  # free, personal, family, premium
    status = Column(String(50), nullable=False, default="active", index=True)  # active, expired, cancelled, pending, trial
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True, index=True)
    trial_end_date = Column(DateTime, nullable=True, index=True)
    auto_renew = Column(Boolean, default=False)
    limits = Column(JSONB, default={
        "devices": 1,
        "scans_per_day": 10,
        "ai_messages_per_day": 0,
        "reports_per_month": 3,
        "storage_gb": 1
    })
    features = Column(ARRAY(Text), default=[])
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    version = Column(Integer, default=1)

    usage = relationship("UsageTracking", back_populates="subscription", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="subscription")
    payments = relationship("Payment", back_populates="subscription")


class UsageTracking(Base):
    __tablename__ = "usage_tracking"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)  # ai_messages, scans, reports, etc.
    amount = Column(Integer, nullable=False, default=0)
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    subscription = relationship("Subscription", back_populates="usage")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    user_id = Column(String(255), nullable=True, index=True)
    device_id = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    subscription = relationship("Subscription", back_populates="audit_logs")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True, index=True)
    alias = Column(String(64), nullable=False, index=True)
    pin_hash = Column(String(128), nullable=False)
    tariff_id = Column(String(32), nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String(32), nullable=False, default="created")
    payment_method = Column(String(32), nullable=False)
    psp_payment_id = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    
    # ✅ Поля согласия на обработку ПДн (152-ФЗ)
    personal_data_consent = Column(Boolean, default=False, nullable=False)
    consent_timestamp = Column(DateTime(timezone=True), nullable=True)
    consent_ip = Column(String(45), nullable=True)  # IPv6 support

    activation_code = relationship(
        "ActivationCode", back_populates="payment", uselist=False
    )
    subscription = relationship("Subscription", back_populates="payments")


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    discount_type = Column(String(50), nullable=False)  # percentage, fixed_amount
    discount_value = Column(Numeric(10, 2), nullable=False)
    max_uses = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True, index=True)
    applicable_plans = Column(ARRAY(Text), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)


class ActivationCode(Base):
    __tablename__ = "activation_codes"

    code = Column(String(32), primary_key=True)
    payment_id = Column(
        String(36), ForeignKey("payments.id", ondelete="CASCADE"), nullable=False
    )
    alias = Column(String(64), nullable=False, index=True)
    tariff_id = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False, default="active")
    expires_at = Column(DateTime(timezone=True), nullable=False)
    redeemed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    payment = relationship("Payment", back_populates="activation_code")


class ComponentStatusModel(Base):
    __tablename__ = "component_status"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    component_id = Column(String(255), nullable=False)
    user_id = Column(Integer, nullable=False)
    is_enabled = Column(Boolean, default=False, nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class ComponentConfigurationModel(Base):
    __tablename__ = "component_configuration"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    component_id = Column(String(255), nullable=False)
    user_id = Column(Integer, nullable=False)
    settings = Column(Text, default='{}', nullable=False)  # JSON as string for SQLite
    version = Column(String(50), default='1.0.0', nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )