"""Двухкошелёчный spend: основной + бонусный (реф)."""

from __future__ import annotations

from dataclasses import dataclass

MSG_BONUS_FORBIDDEN = (
    "❌ Реферальный баланс нельзя использовать для покупки Telegram Stars и Premium.\n"
    "Пополните основной баланс или используйте реферальный баланс для оплаты VPN."
)

MSG_INSUFFICIENT_MAIN = "❌ Недостаточно средств на основном балансе."
MSG_INSUFFICIENT_TOTAL = "❌ Недостаточно средств на балансах магазина."


@dataclass(frozen=True)
class WalletPlan:
    main_use: float
    bonus_use: float


def split_bonus_first(due: float, main: float, bonus: float) -> tuple[float, float]:
    """Bonus-first: returns (main_use, bonus_use)."""
    due_r = round(float(due), 2)
    bonus_r = round(max(0.0, float(bonus)), 2)
    bonus_use = round(min(bonus_r, due_r), 2)
    main_use = round(due_r - bonus_use, 2)
    return main_use, bonus_use


# backward-compatible alias
split_vpn_payment = split_bonus_first


def _norm_kind(kind: str) -> str:
    return (kind or "").strip().lower()


def wallet_plan_for_kind(
    kind: str,
    due: float,
    main: float,
    bonus: float,
    *,
    ref_bonus_vpn_only: bool = True,
    try_use_bonus: bool = False,
) -> WalletPlan:
    """
    Pure spend plan. Raises ValueError with codes:
    insufficient_main | bonus_forbidden_for_product | insufficient_total
    """
    due_r = round(float(due), 2)
    main_r = round(max(0.0, float(main)), 2)
    bonus_r = round(max(0.0, float(bonus)), 2)
    pk = _norm_kind(kind)

    # Shop-wide bonus: bonus-first на любой товар.
    if not ref_bonus_vpn_only:
        if main_r + bonus_r + 1e-6 < due_r:
            raise ValueError("insufficient_total")
        main_use, bonus_use = split_bonus_first(due_r, main_r, bonus_r)
        if main_use > main_r + 1e-6:
            raise ValueError("insufficient_main")
        return WalletPlan(main_use=main_use, bonus_use=bonus_use)

    if try_use_bonus and pk != "vpn":
        raise ValueError("bonus_forbidden_for_product")

    if pk == "vpn":
        if main_r + bonus_r + 1e-6 < due_r:
            raise ValueError("insufficient_total")
        main_use, bonus_use = split_bonus_first(due_r, main_r, bonus_r)
        if main_use > main_r + 1e-6:
            raise ValueError("insufficient_main")
        return WalletPlan(main_use=main_use, bonus_use=bonus_use)

    if main_r + 1e-6 < due_r:
        raise ValueError("insufficient_main")
    return WalletPlan(main_use=due_r, bonus_use=0.0)


def wallet_plan_partial_apply(
    kind: str,
    apply_amount: float,
    main: float,
    bonus: float,
    *,
    ref_bonus_vpn_only: bool = True,
) -> WalletPlan:
    """Allocate up to apply_amount from wallets (bonus-first when allowed)."""
    apply_r = round(float(apply_amount), 2)
    if apply_r <= 0:
        raise ValueError("invalid_balance_apply")
    main_r = round(max(0.0, float(main)), 2)
    bonus_r = round(max(0.0, float(bonus)), 2)
    pk = _norm_kind(kind)

    allow_bonus = (not ref_bonus_vpn_only) or pk == "vpn"
    if not allow_bonus:
        if main_r + 1e-6 < apply_r:
            raise ValueError("insufficient_main")
        return WalletPlan(main_use=apply_r, bonus_use=0.0)

    max_apply = round(main_r + bonus_r, 2)
    if apply_r > max_apply + 1e-6:
        raise ValueError("insufficient_total")
    bonus_use = round(min(bonus_r, apply_r), 2)
    main_use = round(apply_r - bonus_use, 2)
    if main_use > main_r + 1e-6:
        raise ValueError("insufficient_main")
    return WalletPlan(main_use=main_use, bonus_use=bonus_use)


def user_message_for_wallet_error(code: str) -> str:
    if code == "bonus_forbidden_for_product":
        return MSG_BONUS_FORBIDDEN
    if code == "insufficient_total":
        return MSG_INSUFFICIENT_TOTAL
    if code in ("insufficient_main", "insufficient_balance"):
        return MSG_INSUFFICIENT_MAIN
    return MSG_INSUFFICIENT_MAIN
