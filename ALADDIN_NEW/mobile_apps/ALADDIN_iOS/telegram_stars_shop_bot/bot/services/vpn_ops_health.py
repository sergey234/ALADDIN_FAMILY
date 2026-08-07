"""
Снимок здоровья VPN-стека для /admin и фоновых алертов.

Проверяет: HTTP /health и /ready vpn-api, circuit breaker, vpn.db (jobs/аккаунты).
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite
import httpx

from bot.config import Settings
from bot.services import admin_stats_repo, vpn_api_client
from bot.services import vpn_api_circuit
from bot.services.alerts import send_alert
from bot.util_html import esc

_log = logging.getLogger(__name__)

# Подряд идущие снимки != ok — CRITICAL только после N (см. VPN_OPS_HEALTH_CRITICAL_AFTER).
_bad_streak: int = 0
_last_notified_status: str = "ok"
_last_alert_sent_ts: float = 0.0

_STATUS_RANK = {"ok": 0, "degraded": 1, "critical": 2}

# Дайджест: время последней отправки на диск — иначе каждый restart шлёт снова через ~45 с.
_DIGEST_STATE_CANDIDATES = (
    Path("/var/lib/aladdin-vpn-ops/vpn_path_digest.last_ts"),
    Path("/tmp/aladdin_vpn_path_digest.last_ts"),
)


def _digest_state_path() -> Path:
    preferred = _DIGEST_STATE_CANDIDATES[0]
    try:
        preferred.parent.mkdir(parents=True, exist_ok=True)
        return preferred
    except OSError:
        return _DIGEST_STATE_CANDIDATES[1]


def load_last_digest_sent_ts(path: Path | None = None) -> float:
    p = path or _digest_state_path()
    try:
        raw = p.read_text(encoding="utf-8").strip()
        return float(raw) if raw else 0.0
    except (OSError, ValueError):
        return 0.0


def save_last_digest_sent_ts(ts: float, path: Path | None = None) -> None:
    p = path or _digest_state_path()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(str(float(ts)), encoding="utf-8")
    except OSError:
        _log.warning("vpn_path_digest state write failed path=%s", p, exc_info=True)


def digest_sleep_seconds(*, interval: int, last_sent_ts: float, now_ts: float | None = None) -> float:
    """
    Сколько ждать до следующего дайджеста.
    Первый раз (нет state) — короткий bootstrap 45 с.
    После успешной отправки / после restart — добор до полного interval (не спамить).
    """
    now = float(now_ts if now_ts is not None else time.time())
    iv = max(300, int(interval))
    last = float(last_sent_ts or 0.0)
    if last <= 0:
        return 45.0
    elapsed = now - last
    if elapsed >= iv:
        return 0.0
    return max(0.0, iv - elapsed)


@dataclass
class VpnOpsHealthSnapshot:
    status: str  # ok | degraded | critical
    checked_at_utc: str
    lines_html: list[str] = field(default_factory=list)
    issue_codes: list[str] = field(default_factory=list)

    def summary_html(self) -> str:
        icon = {"ok": "🟢", "degraded": "🟡", "critical": "🔴"}.get(self.status, "⚪")
        head = f"{icon} <b>VPN health</b> — <code>{esc(self.status)}</code> · <i>{esc(self.checked_at_utc)} UTC</i>"
        body = "\n".join(self.lines_html)
        return f"{head}\n{body}" if body else head


async def collect_vpn_ops_health(settings: Settings) -> VpnOpsHealthSnapshot:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    lines: list[str] = []
    issues: list[str] = []
    severity_rank = 0  # 0 ok, 1 degraded, 2 critical

    def bump(level: int, code: str) -> None:
        nonlocal severity_rank
        severity_rank = max(severity_rank, level)
        if code not in issues:
            issues.append(code)

    base = (settings.vpn_api_base_url or "").strip()
    health_ok = False
    if not base:
        lines.append("• VPN API: <i>не настроен (VPN_API_BASE_URL)</i>")
        bump(1, "api_not_configured")
    else:
        h_ok, h_body = await vpn_api_client.get_public_health(settings)
        health_ok = h_ok
        if h_ok:
            lines.append("• API <code>/health</code>: <b>ok</b>")
        else:
            lines.append(f"• API <code>/health</code>: <b>FAIL</b> — <code>{esc(h_body[:120])}</code>")
            bump(2, "api_health_down")

        if health_ok:
            r_ok, r_body, r_code = await vpn_api_client.get_public_ready(settings)
            if r_ok:
                wg = ""
                if isinstance(r_body, dict):
                    wg = str(r_body.get("wg") or "").strip()
                detail = f" ({esc(wg)})" if wg else ""
                lines.append(f"• API <code>/ready</code> (WireGuard): <b>ok</b>{detail}")
            elif r_code == -1:
                lines.append("• API <code>/ready</code>: <i>пропущен (нет VPN_API_BASE_URL)</i>")
            elif r_code == 0:
                lines.append(
                    f"• API <code>/ready</code> (WireGuard): <b>FAIL</b> — "
                    f"<code>{esc(str(r_body)[:120])}</code>"
                )
                bump(1, "api_ready_unreachable")
            else:
                lines.append(
                    f"• API <code>/ready</code> (WireGuard): <b>degraded</b> "
                    f"<code>{esc(r_code)}</code> — <code>{esc(str(r_body)[:120])}</code>"
                )
                bump(1, "api_ready_fail")
                lines.append(
                    "<i>WireGuard — запасной способ; Xray (/sub/) может работать.</i>"
                )
        else:
            lines.append("• API <code>/ready</code>: <i>пропущен — /health недоступен</i>")

    br = vpn_api_circuit.get_breaker(
        failure_threshold=settings.vpn_api_circuit_failure_threshold,
        failure_window_seconds=float(settings.vpn_api_circuit_failure_window_seconds),
        open_seconds=float(settings.vpn_api_circuit_open_seconds),
    )
    snap = br.snapshot()
    if snap.state == vpn_api_circuit.CircuitState.OPEN:
        lines.append("• Circuit breaker: <b>OPEN</b> (бот не зовёт vpn-api)")
        bump(2, "circuit_open")
    elif snap.state == vpn_api_circuit.CircuitState.HALF_OPEN:
        lines.append("• Circuit breaker: <b>HALF_OPEN</b>")
        bump(1, "circuit_half_open")
    else:
        lines.append("• Circuit breaker: <b>closed</b>")

    vpath = settings.resolved_vpn_db_path()
    cp = await admin_stats_repo.fetch_vpn_controlplane_metrics(vpath)
    avail = int(cp.get("vpn_cp_available", 0) or 0)
    if avail == 0:
        lines.append("• <code>vpn.db</code>: <i>VPN_DB_PATH не задан или файл недоступен</i>")
        bump(1, "vpn_db_unavailable")
    elif avail < 0:
        lines.append("• <code>vpn.db</code>: <b>ошибка чтения</b>")
        bump(2, "vpn_db_read_error")
    else:
        pend = int(cp.get("vpn_cp_jobs_pending", 0) or 0)
        fail_j = int(cp.get("vpn_cp_jobs_failed", 0) or 0)
        proc = int(cp.get("vpn_cp_jobs_processing", 0) or 0)
        fail_acc = int(cp.get("vpn_cp_accounts_vpn_failed", 0) or 0)
        prov_acc = int(cp.get("vpn_cp_accounts_vpn_provisioning", 0) or 0)
        stale = await admin_stats_repo.count_vpn_stale_pending_jobs(
            vpath,
            stale_minutes=max(1, int(settings.vpn_ops_health_stale_job_minutes)),
        )
        lines.append(
            f"• Jobs: pending <code>{esc(str(pend))}</code>"
            f" · processing <code>{esc(str(proc))}</code>"
            f" · failed <code>{esc(str(fail_j))}</code>"
        )
        if stale > 0:
            lines.append(
                f"• <b>Зависшие jobs</b> (pending > "
                f"{esc(str(settings.vpn_ops_health_stale_job_minutes))} мин): "
                f"<code>{esc(str(stale))}</code>"
            )
            bump(2, "jobs_stale")
        if fail_j > 0:
            bump(1, "jobs_failed")
        if fail_acc > 0:
            lines.append(f"• Аккаунты <code>vpn_failed</code>: <code>{esc(str(fail_acc))}</code>")
            bump(1, "accounts_failed")
        if prov_acc > int(settings.vpn_ops_health_provisioning_warn_threshold):
            lines.append(
                f"• Долго в <code>vpn_provisioning</code>: <code>{esc(str(prov_acc))}</code>"
            )
            bump(1, "accounts_provisioning_high")

        # Trial / expire data-plane integrity (same defs as vpn_trial_expire_reconcile.py)
        try:
            from pathlib import Path

            from bot.services.vpn_trial_expire_metrics import collect_trial_expire_metrics

            xray_cfg = Path(
                (getattr(settings, "vpn_xray_config_path", None) or "").strip()
                or "/opt/xray/config.json"
            )
            tm = collect_trial_expire_metrics(vpath, xray_cfg)
            lines.append(
                "• Trial: active <code>"
                f"{esc(str(tm.get('trial_active', 0)))}</code>"
                f" · expired <code>{esc(str(tm.get('trial_expired', 0)))}</code>"
                f" · used_at <code>{esc(str(tm.get('trial_used_at', 0)))}</code>"
                f" · paid_after <code>{esc(str(tm.get('paid_after_trial_active', 0)))}</code>"
            )
            od = int(tm.get("overdue_active") or 0)
            exu = int(tm.get("expired_with_uuid") or 0)
            orphan = int(tm.get("xray_orphan_clients") or 0)
            if od or exu or orphan:
                lines.append(
                    "• <b>Expire integrity</b>: overdue <code>"
                    f"{esc(str(od))}</code> · expired+uuid <code>{esc(str(exu))}</code>"
                    f" · xray_orphan <code>{esc(str(orphan))}</code>"
                )
                bump(2 if od or exu else 1, "trial_expire_integrity")
            else:
                lines.append("• Expire integrity: <b>ok</b> (overdue/orphan=0)")
        except Exception:
            _log.exception("vpn_ops_health trial_expire_metrics")
            lines.append("• Expire integrity: <i>ошибка сбора</i>")
            bump(1, "trial_expire_metrics_error")

        # RU-bridge zombies (Happ-cache free VPN after expire) — status JSON from guard cron
        try:
            from bot.services.vpn_bridge_zombie_metrics import collect_bridge_zombie_metrics

            status_path = (
                (getattr(settings, "vpn_bridge_peers_status_path", None) or "").strip()
                or "/opt/aladdin-shop-vpn-api/var/bridge_peers_status.json"
            )
            max_age = int(getattr(settings, "vpn_bridge_status_max_age_sec", None) or 3 * 3600)
            bm = collect_bridge_zombie_metrics(status_path, max_age_sec=max_age)
            zb = int(bm.get("zombie_before") or 0)
            za = int(bm.get("zombie_after") if bm.get("zombie_after") is not None else -1)
            zp = int(bm.get("zombie_pruned") or 0)
            if bm.get("error") == "status_missing":
                lines.append(
                    "• Bridge зомби: <i>нет status JSON</i> "
                    "(cron <code>vpn-bridge-peers-guard</code> / <code>/vpn_zombies</code>)"
                )
                bump(1, "bridge_zombie_status_missing")
            elif bm.get("stale"):
                lines.append(
                    "• <b>Bridge зомби status STALE</b>: age "
                    f"<code>{esc(str(bm.get('age_sec')))}</code> с · after="
                    f"<code>{esc(str(za))}</code>"
                )
                bump(1, "bridge_zombie_status_stale")
            elif za > 0:
                paid_n = int(bm.get("active_paid_real") or 0)
                trial_n = int(bm.get("active_trial_real") or 0)
                lines.append(
                    "• <b>Bridge зомби ОСТАЛИСЬ</b>: after <code>"
                    f"{esc(str(za))}</code> · before <code>{esc(str(zb))}</code>"
                    f" · живые <code>{esc(str(paid_n + trial_n))}</code>"
                    " → <code>/vpn_zombies</code>"
                )
                bump(2, "bridge_zombie_remaining")
            else:
                paid_n = int(bm.get("active_paid_real") or 0)
                trial_n = int(bm.get("active_trial_real") or 0)
                live_n = paid_n + trial_n
                lines.append(
                    "• Bridge: <b>ok</b> · живые <code>"
                    f"{esc(str(live_n))}</code>"
                    f" (оплач. <code>{esc(str(paid_n))}</code>"
                    f" + trial <code>{esc(str(trial_n))}</code>)"
                    f" · зомби сейчас <code>0</code>"
                    f" · отключено всего <code>{esc(str(int(bm.get('zombie_pruned_total') or 0)))}</code>"
                )
                if zb > 0:
                    lines.append(
                        f"• <i>В последнем прогоне снято зомби: <code>{esc(str(zb))}</code></i>"
                    )
        except Exception:
            _log.exception("vpn_ops_health bridge_zombie_metrics")
            lines.append("• Bridge зомби: <i>ошибка сбора</i>")
            bump(1, "bridge_zombie_metrics_error")

        thr = int(settings.vpn_sub_access_alert_per_hour or 0)
        if thr > 0 and vpath is not None and Path(vpath).is_file():
            try:
                from bot.services.sub_access_hot import hot_token_hashes

                async with aiosqlite.connect(vpath) as vdb:
                    vdb.row_factory = aiosqlite.Row
                    hot = await hot_token_hashes(vdb, per_hour_threshold=thr)
                if hot:
                    lead_hash, lead_cnt = hot[0]
                    lines.append(
                        f"• <b>/sub/ возможный шаринг</b>: <code>{esc(str(len(hot)))}</code> "
                        f"токен(ов) &gt; <code>{esc(str(thr))}</code>/ч "
                        f"(макс <code>{esc(str(lead_cnt))}</code>, hash <code>{esc(lead_hash)}</code>)"
                    )
                    bump(1, "sub_access_hot")
            except Exception:
                _log.exception("vpn_ops_health sub_access_hot check")

    bridge_host = (settings.vpn_bridge_health_host or "").strip()
    bridge_port = int(settings.vpn_bridge_health_port or 0)
    if bridge_host and bridge_port > 0:
        bridge_ok = await _tcp_reachable(bridge_host, bridge_port, timeout=5.0)
        if bridge_ok:
            lines.append(
                f"• RU-мост <code>{esc(bridge_host)}:{bridge_port}</code>: <b>TCP ok</b>"
            )
        else:
            lines.append(
                f"• RU-мост <code>{esc(bridge_host)}:{bridge_port}</code>: <b>TCP FAIL</b>"
            )
            bump(1, "bridge_tcp_down")

    mirror_origin = (settings.vpn_subscription_mirror_origin or "").strip().rstrip("/")
    if mirror_origin and settings.vpn_sub_mirror_health_enabled:
        probe = f"{mirror_origin}/sub/__mirror_health_probe__"
        try:
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                r = await client.get(probe)
            if r.status_code in (404, 401, 403):
                lines.append(f"• Зеркало <code>{esc(mirror_origin)}</code>: <b>HTTP ok</b> ({r.status_code})")
            else:
                lines.append(
                    f"• Зеркало <code>{esc(mirror_origin)}</code>: <b>WARN</b> HTTP {r.status_code}"
                )
                bump(1, "sub_mirror_http")
        except Exception as exc:
            lines.append(
                f"• Зеркало <code>{esc(mirror_origin)}</code>: <b>FAIL</b> — "
                f"<code>{esc(str(exc)[:80])}</code>"
            )
            bump(1, "sub_mirror_down")

    try:
        from bot.services.vpn_path_metrics_health import collect_path_metrics_verdict

        path_v = await collect_path_metrics_verdict(settings)
        if path_v.lines_html:
            lines.extend(path_v.lines_html)
        for code in path_v.issue_codes:
            bump(max(1, path_v.severity), code)
    except Exception:
        _log.exception("vpn_ops_health path_metrics")
        lines.append("• Path metrics: <i>ошибка сбора CSV</i>")
        bump(1, "path_metrics_error")

    status = {0: "ok", 1: "degraded", 2: "critical"}[severity_rank]
    return VpnOpsHealthSnapshot(
        status=status,
        checked_at_utc=now,
        lines_html=lines,
        issue_codes=issues,
    )


async def _tcp_reachable(host: str, port: int, *, timeout: float) -> bool:
    try:
        _reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout,
        )
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False


def _effective_alert_status(settings: Settings, snap: VpnOpsHealthSnapshot) -> str:
    """CRITICAL в Telegram только после N подряд плохих проверок."""
    global _bad_streak
    if snap.status == "ok":
        _bad_streak = 0
        return "ok"
    _bad_streak += 1
    need = max(1, int(settings.vpn_ops_health_critical_after))
    if snap.status == "critical" and _bad_streak < need:
        return "degraded"
    return snap.status


_ISSUE_HINT_RU: dict[str, str] = {
    "api_not_configured": "VPN API не настроен",
    "api_health_down": "API /health недоступен",
    "api_ready_unreachable": "API /ready недоступен",
    "api_ready_fail": "WireGuard /ready не готов",
    "circuit_open": "circuit breaker открыт",
    "circuit_half_open": "circuit breaker half-open",
    "vpn_db_unavailable": "vpn.db недоступна",
    "vpn_db_read_error": "ошибка чтения vpn.db",
    "jobs_stale": "зависшие jobs",
    "jobs_failed": "есть failed jobs",
    "accounts_failed": "аккаунты vpn_failed",
    "accounts_provisioning_high": "много vpn_provisioning",
    "trial_expire_integrity": "дыры expire (overdue/uuid/orphan)",
    "trial_expire_metrics_error": "ошибка сбора expire-метрик",
    "bridge_zombie_remaining": "зомби UUID на RU-bridge",
    "bridge_zombie_status_missing": "нет отчёта bridge guard",
    "bridge_zombie_status_stale": "отчёт bridge guard устарел",
    "bridge_zombie_metrics_error": "ошибка метрик bridge зомби",
    "sub_access_hot": "возможный шаринг /sub/",
    "bridge_tcp_down": "RU-мост TCP FAIL",
    "sub_mirror_http": "зеркало /sub/ HTTP warn",
    "sub_mirror_down": "зеркало /sub/ недоступно",
    "path_csv_empty": "нет CSV path-метрик",
    "path_metrics_error": "ошибка сбора path-метрик",
    "path_csv_contabo_missing": "нет CSV Contabo",
    "path_csv_149_missing": "нет CSV 149",
    "swap_149_high": "высокий swap на 149",
    "swap_149_elevated": "повышенный swap на 149",
    "contabo_cf_low": "низкий Contabo CF",
    "contabo_cf_volatile": "плавает Contabo CF",
    "wg_rtt_high": "высокий RTT моста (149→Contabo)",
    "wg_rtt_elevated": "повышенный RTT моста",
    "wg_rtt_back_high": "высокий RTT обратно (Contabo→149)",
}


def _short_ops_alert_body(
    *,
    snap: VpnOpsHealthSnapshot,
    alert_status: str,
    settings: Settings,
    escalated: bool,
    cooldown: int,
) -> str:
    """Короткий алерт без полного отчёта — полный текст только в дайджесте /vpn_health."""
    hints: list[str] = []
    for code in snap.issue_codes:
        hints.append(_ISSUE_HINT_RU.get(code, code))
    if not hints:
        hints.append(alert_status)
    lines = [
        f"Статус: <b>{esc(alert_status)}</b>",
        "Причины:",
        *[f"• {esc(h)}" for h in hints[:12]],
        "",
        "<i>Полный отчёт — в плановом «VPN дайджест» (каждые 5 ч) или /vpn_health. "
        "Это короткое напоминание, не дубль длинного текста.</i>",
    ]
    if alert_status == "degraded" and snap.status == "critical":
        lines.insert(
            0,
            (
                f"<i>Предупреждение {_bad_streak}/{settings.vpn_ops_health_critical_after} "
                f"— повторная проверка через {settings.vpn_ops_health_interval_seconds} сек.</i>"
            ),
        )
    if not escalated and _last_notified_status not in ("ok", ""):
        lines.insert(
            0,
            f"<i>Напоминание (не чаще 1 раза в {cooldown // 3600} ч при том же статусе).</i>",
        )
    return "\n".join(lines)


async def maybe_alert_vpn_ops_health(settings: Settings, snap: VpnOpsHealthSnapshot) -> None:
    """Алерт при смене статуса / эскалации; повтор того же статуса — не чаще cooldown (по умолч. 5 ч)."""
    global _last_notified_status, _last_alert_sent_ts

    alert_status = _effective_alert_status(settings, snap)

    if alert_status == "ok":
        if _last_notified_status in ("degraded", "critical"):
            await send_alert(
                settings,
                severity="info",
                title="VPN ops health: recovered",
                body="Проверка VPN снова <b>ok</b>. Xray (/sub/) и выдача ключей доступны.",
                dedupe_key="vpn_ops_health:recovered",
            )
            _last_alert_sent_ts = time.time()
        _last_notified_status = "ok"
        return

    now = time.time()
    cooldown = max(60, int(settings.vpn_ops_health_alert_cooldown_seconds))
    prev_rank = _STATUS_RANK.get(_last_notified_status, 0)
    new_rank = _STATUS_RANK.get(alert_status, 0)
    escalated = new_rank > prev_rank
    same_or_lower = new_rank <= prev_rank
    if same_or_lower and _last_notified_status != "ok" and (now - _last_alert_sent_ts) < cooldown:
        _log.info(
            "vpn_ops_health alert suppressed status=%s cooldown_left_s=%.0f",
            alert_status,
            cooldown - (now - _last_alert_sent_ts),
        )
        _last_notified_status = alert_status
        return

    sev = "critical" if alert_status == "critical" else "warning"
    body = _short_ops_alert_body(
        snap=snap,
        alert_status=alert_status,
        settings=settings,
        escalated=escalated,
        cooldown=cooldown,
    )
    await send_alert(
        settings,
        severity=sev,
        title=f"VPN ops health: {alert_status}",
        body=body,
        dedupe_key=f"vpn_ops_health:{alert_status}",
    )
    _last_notified_status = alert_status
    _last_alert_sent_ts = now


async def vpn_ops_health_loop(_bot, settings: Settings) -> None:
    interval = int(settings.vpn_ops_health_interval_seconds)
    if interval <= 0:
        return
    interval = max(60, interval)
    while True:
        try:
            snap = await collect_vpn_ops_health(settings)
            _log.info(
                "vpn_ops_health status=%s issues=%s streak=%s",
                snap.status,
                snap.issue_codes,
                _bad_streak,
            )
            await maybe_alert_vpn_ops_health(settings, snap)
        except asyncio.CancelledError:
            raise
        except Exception:
            _log.exception("vpn_ops_health_loop_iteration")
        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            raise


async def vpn_path_digest_loop(_bot, settings: Settings) -> None:
    """
    Полный отчёт метрик простым языком в ops-чат каждые N секунд (по умолч. 1 ч).
    Не зависит от alert-cooldown: это плановый дайджест, не спам-алерт.
    Время последней отправки хранится на диске — restart бота не сбрасывает интервал.
    """
    if not bool(getattr(settings, "vpn_path_digest_enabled", True)):
        return
    interval = int(getattr(settings, "vpn_path_digest_interval_seconds", 3600) or 0)
    if interval <= 0:
        return
    interval = max(300, interval)

    from bot.services.ops_chat import send_ops_chat_html

    while True:
        try:
            last = load_last_digest_sent_ts()
            delay = digest_sleep_seconds(interval=interval, last_sent_ts=last)
            if delay > 0:
                _log.info(
                    "vpn_path_digest wait_s=%.0f interval_s=%s last_age_s=%.0f",
                    delay,
                    interval,
                    (time.time() - last) if last > 0 else -1,
                )
                await asyncio.sleep(delay)
            snap = await collect_vpn_ops_health(settings)
            icon = {"ok": "🟢", "degraded": "🟡", "critical": "🔴"}.get(snap.status, "⚪")
            if interval >= 3600 and interval % 3600 == 0:
                every_lbl = f"каждые {interval // 3600} ч"
            else:
                every_lbl = f"каждые {max(1, interval // 60)} мин"
            head = (
                f"{icon} <b>VPN дайджест</b> ({every_lbl}) — "
                f"<code>{esc(snap.status)}</code> · <i>{esc(snap.checked_at_utc)} UTC</i>\n"
                f"<i>Плановый полный отчёт, не алерт.</i>"
            )
            body = "\n".join(snap.lines_html)
            text = f"{head}\n{body}" if body else head
            if len(text) > 4000:
                text = text[:3900] + "\n…\n<i>обрезано</i>"
            # Стабильный ключ + cooldown=interval: даже при уникальном тексте не чаще 1× / interval
            # после restart (доп. защита рядом с файлом state).
            ok = await send_ops_chat_html(
                settings,
                text,
                dedupe_key="vpn_path_digest",
                cooldown_seconds=interval,
            )
            if ok:
                save_last_digest_sent_ts(time.time())
                _log.info("vpn_path_digest sent status=%s", snap.status)
            else:
                # Дедуп/неуспех — всё равно отметим попытку, чтобы не крутить цикл без паузы.
                if load_last_digest_sent_ts() <= 0:
                    save_last_digest_sent_ts(time.time())
                _log.info("vpn_path_digest skipped_or_failed status=%s", snap.status)
        except asyncio.CancelledError:
            raise
        except Exception:
            _log.exception("vpn_path_digest_loop_iteration")
            try:
                await asyncio.sleep(min(300, interval))
            except asyncio.CancelledError:
                raise
            continue
        # После отправки полный интервал до следующего круга (state уже записан).
        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            raise
