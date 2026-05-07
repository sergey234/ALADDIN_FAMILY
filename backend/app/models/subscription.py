"""
ALADDIN Subscription Models
Core models for subscription management system
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from enum import Enum


class SubscriptionLevel(str, Enum):
    """Subscription level enumeration"""
    TRIAL = "trial"
    FREE = "free"
    PERSONAL = "personal"
    FAMILY = "family"
    PREMIUM = "premium"


class TrialInfo(BaseModel):
    """Trial period information"""
    start_date: datetime
    end_date: datetime
    duration_days: int = 14

    @property
    def days_remaining(self) -> int:
        """Calculate remaining days in trial"""
        now = datetime.utcnow()
        if now >= self.end_date:
            return 0
        remaining = self.end_date - now
        return max(0, remaining.days)

    @property
    def is_active(self) -> bool:
        """Check if trial is still active"""
        return datetime.utcnow() < self.end_date


class UsageCounters(BaseModel):
    """Usage counters for subscription limits"""
    ai_messages: int = 0
    scans: int = 0
    reports: int = 0
    devices: int = 0

    def increment(self, resource: str, amount: int = 1):
        """Increment usage counter"""
        if hasattr(self, resource):
            current_value = getattr(self, resource)
            setattr(self, resource, current_value + amount)


class SubscriptionLimits(BaseModel):
    """Subscription limits configuration"""
    max_devices: int
    max_ai_messages: int
    max_scans: int
    max_reports: int
    current_usage: UsageCounters = UsageCounters()

    def is_limit_exceeded(self, resource: str) -> bool:
        """Check if limit exceeded for resource"""
        limit_attr = f"max_{resource}"
        if hasattr(self, limit_attr):
            limit_value = getattr(self, limit_attr)
            current_value = getattr(self.current_usage, resource)
            return current_value >= limit_value
        return False

    @classmethod
    def free_limits(cls) -> 'SubscriptionLimits':
        """Free tier limits"""
        return cls(
            max_devices=1,
            max_ai_messages=10,
            max_scans=5,
            max_reports=2,
            current_usage=UsageCounters()
        )

    @classmethod
    def trial_limits(cls) -> 'SubscriptionLimits':
        """Trial limits"""
        return cls(
            max_devices=3,
            max_ai_messages=50,
            max_scans=100,
            max_reports=10,
            current_usage=UsageCounters()
        )


class SubscriptionPayload(BaseModel):
    """JWT subscription payload"""
    level: SubscriptionLevel
    start_date: datetime
    end_date: Optional[datetime]
    is_active: bool = True
    trial_info: Optional[TrialInfo]
    limits: SubscriptionLimits
    permissions: Dict[str, Any] = {}
    device_id: str
    user_id: Optional[str]


class JWTToken(BaseModel):
    """JWT token structure"""
    token: str
    device_id: str
    subscription_level: SubscriptionLevel
    trial_info: Optional[TrialInfo]
    expires_at: datetime
    issued_at: datetime
    issuer: str = "aladdin-backend"
    limits: SubscriptionLimits
    components: List[str] = []


# API Request/Response Models

class DeviceRegisterRequest(BaseModel):
    """Device registration request"""
    device_id: str = Field(..., alias="deviceId")
    device_type: str = Field("ios", alias="deviceType")

    class Config:
        # Allow population by both field names and aliases (camelCase from iOS)
        allow_population_by_field_name = True


class TrialDeviceRegisterRequest(DeviceRegisterRequest):
    """Trial device registration request"""
    trial_info: TrialInfo = Field(..., alias="trialInfo")
    anti_abuse: Optional[Dict[str, Any]] = Field(default=None, alias="antiAbuse")


class TrialAntiAbuseSignals(BaseModel):
    """Privacy-safe anti-abuse signals from client (no PII)."""
    install_fingerprint_hash: str = Field(..., alias="installFingerprintHash")
    velocity_1h: int = Field(0, alias="velocity1h")
    velocity_24h: int = Field(0, alias="velocity24h")
    cooldown_seconds: int = Field(0, alias="cooldownSeconds")
    app_version: str = Field("unknown", alias="appVersion")
    os_version: str = Field("unknown", alias="osVersion")
    risk_version: str = Field("unknown", alias="riskVersion")


class UpgradeRequest(BaseModel):
    """Subscription upgrade request"""
    level: SubscriptionLevel
    receipt_data: Optional[str]  # App Store receipt


class JWTDeviceRegisterResponse(BaseModel):
    """Device registration response with JWT"""
    token: str
    device_id: str
    expires_at: datetime
    registered_at: datetime
    subscription: SubscriptionPayload


class SubscriptionStatusResponse(BaseModel):
    """Subscription status response"""
    status: SubscriptionPayload
    server_time: datetime


class TrialActivationResponse(BaseModel):
    """Trial activation response"""
    trial_activated: bool
    trial_info: TrialInfo
    new_token: str


class FeatureAccessRequest(BaseModel):
    """Feature access check request"""
    feature_id: str
    device_id: str


class FeatureAccessResponse(BaseModel):
    """Feature access response"""
    feature_id: str
    accessible: bool
    reason: Optional[str]
    subscription_level: SubscriptionLevel
    limits: Optional[SubscriptionLimits]


class UsageUpdateRequest(BaseModel):
    """Usage update request"""
    resource_type: str
    amount: int = 1


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    code: int