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
)
from typing import Optional
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
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


