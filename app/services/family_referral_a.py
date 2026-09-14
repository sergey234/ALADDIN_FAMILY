"""Family Invite Pro (Вариант A) — pure rules (no DB).

Канон: docs/REFERRAL_FAMILY_A_PRODUCT_LOCK.md
Не включает вывод ₽ / MLM / VPN-бот.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


FRIEND_DISCOUNT_PERCENT = 20
QUALIFY_ACTIVE_DAYS = 14


class FamilyReferralTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


@dataclass(frozen=True)
class TierBonus:
    tier: FamilyReferralTier
    min_qualified: int
    max_qualified: Optional[int]  # None = open-ended
    referrer_protection_days: int


# Успешные qualify-семьи → дни защиты рефереру
TIER_TABLE: tuple[TierBonus, ...] = (
    TierBonus(FamilyReferralTier.BRONZE, 1, 2, 7),
    TierBonus(FamilyReferralTier.SILVER, 3, 4, 14),
    TierBonus(FamilyReferralTier.GOLD, 5, 9, 30),
    TierBonus(FamilyReferralTier.PLATINUM, 10, None, 30),
)


def tier_for_qualified_count(n: int) -> TierBonus:
    q = max(0, int(n))
    if q <= 0:
        # Ещё нет успешных — формально ниже bronze; бонус 0
        return TierBonus(FamilyReferralTier.BRONZE, 0, 0, 0)
    for row in TIER_TABLE:
        hi = row.max_qualified
        if q < row.min_qualified:
            continue
        if hi is None or q <= hi:
            return row
    return TIER_TABLE[-1]


def referrer_bonus_days_for_count_after_grant(qualified_including_new: int) -> int:
    """Дни, которые даём рефереру за *этот* grant (по уровню после инкремента)."""
    return int(tier_for_qualified_count(qualified_including_new).referrer_protection_days)


@dataclass(frozen=True)
class QualifyInput:
    referrer_family_id: str
    friend_family_id: str
    referrer_has_active_tariff: bool
    friend_has_paid: bool
    friend_active_protection_days: int
    already_rewarded_pair: bool
    is_same_family: bool


@dataclass(frozen=True)
class QualifyResult:
    ok: bool
    reason: str
    friend_discount_percent: int = 0
    referrer_days: int = 0
    tier: Optional[str] = None


def evaluate_qualify(
    inp: QualifyInput,
    *,
    referrer_qualified_count_before: int = 0,
) -> QualifyResult:
    if inp.is_same_family or inp.referrer_family_id == inp.friend_family_id:
        return QualifyResult(False, "anti_self_or_same_family")
    if not inp.referrer_family_id or not inp.friend_family_id:
        return QualifyResult(False, "missing_family_id")
    if inp.already_rewarded_pair:
        return QualifyResult(False, "pair_already_rewarded")
    if not inp.referrer_has_active_tariff:
        return QualifyResult(False, "referrer_inactive_tariff")

    qualified_event = inp.friend_has_paid or (
        inp.friend_active_protection_days >= QUALIFY_ACTIVE_DAYS
    )
    if not qualified_event:
        return QualifyResult(False, "not_yet_qualified")

    after = max(0, int(referrer_qualified_count_before)) + 1
    tier = tier_for_qualified_count(after)
    days = referrer_bonus_days_for_count_after_grant(after)
    return QualifyResult(
        True,
        "ok",
        friend_discount_percent=FRIEND_DISCOUNT_PERCENT,
        referrer_days=days,
        tier=tier.tier.value,
    )
