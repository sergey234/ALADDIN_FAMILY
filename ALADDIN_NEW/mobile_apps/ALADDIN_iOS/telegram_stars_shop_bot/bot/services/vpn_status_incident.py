"""p4-bot-status: инцидентный announce → Happ /sub/."""

from __future__ import annotations

from bot.services.vpn_connect_copy import VPN_PROFILE_BRIDGE

PRESET_4G = (
    f"Временные проблемы на 4G. Профиль <b>{VPN_PROFILE_BRIDGE}</b> — обновите подписку 🔄"
)
PRESET_GENERAL = (
    f"Ведутся работы. Профиль <b>{VPN_PROFILE_BRIDGE}</b>. Обновите подписку 🔄"
)

PRESETS: dict[str, str] = {
    "4g": PRESET_4G,
    "lte": PRESET_4G,
    "general": PRESET_GENERAL,
    "work": PRESET_GENERAL,
}


def resolve_preset(name: str) -> str | None:
    return PRESETS.get((name or "").strip().lower())


def vpn_incident_status_html(text: str) -> str:
    body = (text or "").strip()
    if not body:
        return ""
    return (
        "<b>⚠️ Статус VPN</b>\n"
        f"{body}\n"
        "<i>Текст также в Happ (announce) после обновления подписки.</i>"
    )
