"""Оркестрация пробного дня AiMonkeyVPN (24ч, 1 раз на Telegram ID)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import Settings
from bot.services import users_repo, vpn_admin_support_repo, vpn_api_client
from bot.services.vpn_post_purchase_delivery import schedule_vpn_happ_delivery_after_paid
from bot.services.vpn_trial_copy import vpn_trial_button_text, vpn_trial_period_phrase, vpn_trial_period_title
from bot.services.vpn_screen_nav import VPN_TRIAL_START
from bot.services.vpn_trial_repo import mark_trial_delivered, upsert_trial_request

TRIAL_ORDER_ID_BASE = 9_100_000_000


class TrialEligibility(str, Enum):
    OK = "ok"
    ALREADY_USED = "already_used"
    ACTIVE_SUBSCRIPTION = "active_subscription"
    API_UNCONFIGURED = "api_unconfigured"
    BOT_TOO_YOUNG = "bot_too_young"
    DISABLED = "disabled"


class TrialProvisionError(RuntimeError):
    pass


def trial_order_id(telegram_user_id: int) -> int:
    return TRIAL_ORDER_ID_BASE + int(telegram_user_id)


def _parse_ts(raw: str | None) -> datetime | None:
    if not raw:
        return None
    s = str(raw).strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _is_active_subscription(acc: dict[str, str]) -> bool:
    if (acc.get("status") or "").strip() != "vpn_active":
        return False
    end = _parse_ts(acc.get("paid_until"))
    if end is None:
        return False
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return end > now


async def trial_eligibility(
    settings: Settings,
    conn,
    telegram_user_id: int,
) -> TrialEligibility:
    if not settings.vpn_trial_enabled:
        return TrialEligibility.DISABLED
    if not (settings.vpn_api_base_url or "").strip():
        return TrialEligibility.API_UNCONFIGURED

    min_age_h = int(settings.vpn_trial_min_account_age_hours or 0)
    if min_age_h > 0:
        user = await users_repo.get_user(conn, telegram_user_id)
        created = _parse_ts(str(user["created_at"]) if user and user["created_at"] else None)
        if created is None:
            return TrialEligibility.BOT_TOO_YOUNG
        age = datetime.now(timezone.utc) - created
        if age < timedelta(hours=min_age_h):
            return TrialEligibility.BOT_TOO_YOUNG

    db_path = settings.resolved_vpn_db_path()
    if db_path is None:
        return TrialEligibility.API_UNCONFIGURED

    acc = await vpn_admin_support_repo.fetch_vpn_account_user_facing(db_path, telegram_user_id)
    if acc and (acc.get("trial_used_at") or "").strip():
        return TrialEligibility.ALREADY_USED
    if acc and _is_active_subscription(acc):
        return TrialEligibility.ACTIVE_SUBSCRIPTION
    return TrialEligibility.OK


def trial_feature_visible(settings: Settings) -> bool:
    """Пробный период включён и API настроен — кнопку показываем всем."""
    return bool(settings.vpn_trial_enabled and (settings.vpn_api_base_url or "").strip())


def _is_active_trial_account(acc: dict[str, str] | None) -> bool:
    if not acc or not _is_active_subscription(acc):
        return False
    return (acc.get("account_kind") or "").strip().lower() == "trial"


def trial_button_label(
    settings: Settings,
    elig: TrialEligibility,
    *,
    account: dict[str, str] | None = None,
) -> str:
    """Подпись кнопки: активная для OK, иначе — причина недоступности (только UI)."""
    if elig is TrialEligibility.OK:
        return vpn_trial_button_text(settings)
    if elig is TrialEligibility.ALREADY_USED:
        if _is_active_trial_account(account):
            return "✅ Пробный период активен"
        return "⌛ Пробный период использован"
    if elig is TrialEligibility.ACTIVE_SUBSCRIPTION:
        return "✅ VPN уже активен"
    if elig is TrialEligibility.BOT_TOO_YOUNG:
        return "🎁 Пробный период · позже"
    return "🎁 Пробный период · недоступен"


def trial_eligibility_alert(code: TrialEligibility, settings: Settings | None = None) -> str:
    """Короткий текст для Telegram show_alert (без HTML)."""
    period = vpn_trial_period_phrase(settings) if settings else "3 дня"
    if code == TrialEligibility.ALREADY_USED:
        return (
            f"Пробный период на {period} уже использован на этом Telegram-аккаунте. "
            "Оплатите тариф — подписка продлится на том же аккаунте."
        )
    if code == TrialEligibility.ACTIVE_SUBSCRIPTION:
        return "У вас уже есть активная подписка VPN. Пробный период только без активного VPN."
    if code == TrialEligibility.API_UNCONFIGURED:
        return "VPN временно недоступен. Попробуйте позже."
    if code == TrialEligibility.BOT_TOO_YOUNG:
        return "Пробный период станет доступен чуть позже — подождите и попробуйте снова."
    if code == TrialEligibility.DISABLED:
        return "Пробный период сейчас недоступен."
    return ""


async def append_vpn_trial_row(
    b: InlineKeyboardBuilder,
    settings: Settings,
    conn,
    user_id: int,
) -> None:
    """Добавить строку с кнопкой пробного периода (видна всем при включённом trial)."""
    if not trial_feature_visible(settings):
        return
    elig = await trial_eligibility(settings, conn, user_id)
    account: dict[str, str] | None = None
    db_path = settings.resolved_vpn_db_path()
    if db_path is not None and elig in (
        TrialEligibility.ALREADY_USED,
        TrialEligibility.ACTIVE_SUBSCRIPTION,
    ):
        account = await vpn_admin_support_repo.fetch_vpn_account_user_facing(db_path, user_id)
    b.row(
        InlineKeyboardButton(
            text=trial_button_label(settings, elig, account=account),
            callback_data=VPN_TRIAL_START,
        )
    )


def trial_eligibility_message(code: TrialEligibility, settings: Settings | None = None) -> str:
    period = vpn_trial_period_phrase(settings) if settings else "3 дня"
    if code == TrialEligibility.ALREADY_USED:
        return (
            f"<b>Пробный период на {period} уже использован</b>\n\n"
            "На этом Telegram-аккаунте пробный период доступен один раз. "
            "Оплатите тариф — подписка продлится на том же аккаунте."
        )
    if code == TrialEligibility.ACTIVE_SUBSCRIPTION:
        return (
            "<b>У вас уже есть активная подписка</b>\n\n"
            "Пробный период доступен только без активного VPN."
        )
    if code == TrialEligibility.API_UNCONFIGURED:
        return "VPN временно недоступен. Попробуйте позже."
    if code == TrialEligibility.BOT_TOO_YOUNG:
        return "Пробный период станет доступен чуть позже — подождите и попробуйте снова."
    if code == TrialEligibility.DISABLED:
        return "Пробный период сейчас недоступен."
    return ""


async def start_trial_flow(settings: Settings, conn, *, telegram_user_id: int) -> None:
    elig = await trial_eligibility(settings, conn, telegram_user_id)
    if elig is not TrialEligibility.OK:
        raise TrialProvisionError(trial_eligibility_message(elig) or str(elig.value))

    order_id = trial_order_id(telegram_user_id)
    idem = f"shop-vpn-trial:{telegram_user_id}"
    ok, msg = await vpn_api_client.post_provision_trial(
        settings,
        telegram_user_id=telegram_user_id,
        idempotency_key=idem,
        trial_hours=int(settings.vpn_trial_hours or 72),
    )
    if not ok:
        raise TrialProvisionError(msg or "provision_trial failed")

    await upsert_trial_request(
        conn,
        telegram_user_id=telegram_user_id,
        provision_order_id=order_id,
        status="pending",
    )
    # API принял provision — в shop ledger сразу delivered (ссылка Happ догонит async).
    await mark_trial_delivered(conn, telegram_user_id=telegram_user_id)
    schedule_vpn_happ_delivery_after_paid(
        settings,
        order_id=order_id,
        telegram_user_id=telegram_user_id,
        delivery_kind="trial",
    )
    # Trial-реф: один раз при первой активации по ref_ (пригласившему +1; другу уже trial).
    from bot.services import vpn_referral_extensions, vpn_referral_repo
    from bot.services.vpn_referral_notify import schedule_trial_referral_bonus_messages

    grant_info = await vpn_referral_repo.try_insert_vpn_trial_referral_grant(
        conn,
        telegram_user_id=telegram_user_id,
        settings=settings,
    )
    if grant_info:
        await vpn_referral_extensions.apply_vpn_referral_extensions(conn, grant_info, settings)
        schedule_trial_referral_bonus_messages(settings, grant_info)
