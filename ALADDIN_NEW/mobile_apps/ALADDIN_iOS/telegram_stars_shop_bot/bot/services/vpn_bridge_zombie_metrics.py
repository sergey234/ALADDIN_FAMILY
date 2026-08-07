"""Метрики зомби UUID на RU-bridge для /vpn_health и /vpn_zombies.

Читает JSON, который пишет vpn_bridge_peers_guard.py (cron hourly).
В отчёте только: живые реальные (оплаченные + trial) и зомби.
Ссылки друзьям/лаб в отчёт не входят.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_STATUS_PATH = Path("/opt/aladdin-shop-vpn-api/var/bridge_peers_status.json")
DEFAULT_MAX_AGE_SEC = 3 * 3600

# Тот же пул, что admin_stats_repo / vpn_grant_beta_batch — не показываем в отчёте.
FRIEND_SEED_TID_LO = 990100001
FRIEND_SEED_TID_HI = 990100099


def _is_friend_or_lab_tid(tid: Any) -> bool:
    try:
        t = int(tid)
    except (TypeError, ValueError):
        return False
    if t <= 0:
        return True
    if FRIEND_SEED_TID_LO <= t <= FRIEND_SEED_TID_HI:
        return True
    return str(t).startswith("9900")


def _parse_iso(raw: str | None) -> float | None:
    if not raw:
        return None
    s = str(raw).strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except ValueError:
        return None


def _filter_real_zombies(items: list[Any]) -> list[dict]:
    out: list[dict] = []
    for z in items:
        if not isinstance(z, dict):
            continue
        tid = z.get("telegram_user_id")
        if tid is not None and _is_friend_or_lab_tid(tid):
            continue
        out.append(z)
    return out


def collect_bridge_zombie_metrics(
    status_path: Path | str | None = None,
    *,
    max_age_sec: int = DEFAULT_MAX_AGE_SEC,
    now_ts: float | None = None,
) -> dict[str, Any]:
    path = Path(status_path or DEFAULT_STATUS_PATH)
    now = float(now_ts if now_ts is not None else time.time())
    empty = {
        "ok": False,
        "error": "status_missing",
        "path": str(path),
        "zombie_before": 0,
        "zombie_after": -1,
        "zombie_pruned": 0,
        "stale": True,
        "age_sec": None,
        "zombies": [],
        "zombies_remaining": [],
        "hosts_configured": [],
        "checked_at_utc": None,
        "active_paid_real": 0,
        "active_trial_real": 0,
    }
    if not path.is_file():
        return empty
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        out = dict(empty)
        out["error"] = f"status_unreadable:{e}"
        return out

    checked = data.get("checked_at_utc")
    ts = _parse_iso(checked if isinstance(checked, str) else None)
    age = (now - ts) if ts is not None else None
    stale = age is None or age > max(60, int(max_age_sec))
    zombie_after = int(data.get("zombie_after") if data.get("zombie_after") is not None else -1)
    guard_ok = bool(data.get("ok"))
    ok = guard_ok and zombie_after == 0 and not stale and not data.get("error")

    zombies = _filter_real_zombies(list(data.get("zombies") or []))
    remaining = _filter_real_zombies(list(data.get("zombies_remaining") or []))

    return {
        "ok": ok,
        "error": data.get("error"),
        "path": str(path),
        "checked_at_utc": checked,
        "active_paid_real": int(data.get("active_paid_real") or 0),
        "active_trial_real": int(data.get("active_trial_real") or 0),
        "zombie_before": int(data.get("zombie_before") or 0),
        "zombie_pruned": int(data.get("zombie_pruned") or 0),
        "zombie_after": zombie_after,
        "zombie_pruned_total": int(data.get("zombie_pruned_total") or 0),
        "last_prune_at_utc": data.get("last_prune_at_utc"),
        "last_prune_count": int(data.get("last_prune_count") or 0),
        "stale": stale,
        "age_sec": int(age) if age is not None else None,
        "zombies": zombies,
        "zombies_remaining": remaining,
        "hosts_configured": list(data.get("hosts_configured") or []),
        "hosts_after": data.get("hosts_after") or {},
        "raw_ok": guard_ok,
    }


def format_bridge_zombies_html(m: dict[str, Any], *, limit: int = 25) -> str:
    from bot.util_html import esc

    if m.get("error") == "status_missing":
        return (
            "👻 <b>Bridge зомби</b>\n"
            f"• Файл статуса не найден: <code>{esc(str(m.get('path')))}</code>\n"
            "• Запусти guard или дождись cron (<code>vpn-bridge-peers-guard</code>)."
        )

    icon = "🟢" if m.get("ok") else "🔴"
    paid = int(m.get("active_paid_real") or 0)
    trial = int(m.get("active_trial_real") or 0)
    live_real = paid + trial
    zb = int(m.get("zombie_before") or 0)
    zp = int(m.get("zombie_pruned") or 0)
    za = int(m.get("zombie_after") if m.get("zombie_after") is not None else -1)
    total_pruned = int(m.get("zombie_pruned_total") or 0)
    lines = [
        f"{icon} <b>Bridge: живые + зомби</b>",
        f"• Проверка: <code>{esc(str(m.get('checked_at_utc') or '—'))}</code> UTC"
        + (
            f" · возраст <code>{esc(str(m.get('age_sec')))}</code> с"
            if m.get("age_sec") is not None
            else ""
        ),
        f"• <b>Живые</b>: <code>{esc(str(live_real))}</code>"
        f" = оплаченные <code>{esc(str(paid))}</code>"
        f" + trial <code>{esc(str(trial))}</code>",
        f"• <b>Зомби сейчас</b> (осталось на bridge): <code>{esc(str(za))}</code>",
        f"• <b>Отключено всего</b> (накопительно): <code>{esc(str(total_pruned))}</code>",
        f"• Последний прогон: найдено <code>{esc(str(zb))}</code>"
        f" · снято <code>{esc(str(zp))}</code>"
        + (
            f" · <code>{esc(str(m.get('last_prune_at_utc')))}</code>"
            if m.get("last_prune_at_utc")
            else ""
        ),
    ]
    if m.get("stale"):
        lines.append("• <b>STATUS STALE</b> — cron/guard давно не писал файл")
    if m.get("error"):
        lines.append(f"• Ошибка guard: <code>{esc(str(m.get('error')))}</code>")

    zombies = list(m.get("zombies_remaining") or []) or list(m.get("zombies") or [])
    show = zombies[: max(0, int(limit))]
    if show and int(m.get("zombie_after") or 0) > 0:
        lines.append("• <b>Оставшиеся зомби:</b>")
    elif show and int(m.get("zombie_before") or 0) > 0:
        lines.append("• Последние пойманные (уже сняты, если осталось=0):")
    for z in show:
        tid = z.get("telegram_user_id")
        uid = str(z.get("uuid") or "")
        st = z.get("status") or "?"
        kind = z.get("account_kind") or "?"
        until = z.get("paid_until") or "—"
        lines.append(
            f"  — TID <code>{esc(str(tid) if tid is not None else '—')}</code>"
            f" · {esc(str(kind))}/{esc(str(st))}"
            f" · until <code>{esc(str(until))}</code>"
            f" · uuid <code>{esc(uid[:13])}…</code>"
        )
    if len(zombies) > len(show):
        lines.append(f"  … ещё {len(zombies) - len(show)}")

    return "\n".join(lines)
