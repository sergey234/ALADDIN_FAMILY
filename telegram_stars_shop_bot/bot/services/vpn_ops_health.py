"""
Снимок здоровья VPN-стека для /admin и фоновых алертов.

Проверяет: HTTP /health и /ready vpn-api, circuit breaker, vpn.db (jobs/аккаунты).
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

from bot.config import Settings
from bot.services import admin_stats_repo, vpn_api_client
from bot.services import vpn_api_circuit
from bot.services.alerts import send_alert
from bot.util_html import esc

_log = logging.getLogger(__name__)


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
    if not base:
        lines.append("• VPN API: <i>не настроен (VPN_API_BASE_URL)</i>")
        bump(1, "api_not_configured")
    else:
        h_ok, h_body = await vpn_api_client.get_public_health(settings)
        if h_ok:
            lines.append("• API <code>/health</code>: <b>ok</b>")
        else:
            lines.append(f"• API <code>/health</code>: <b>FAIL</b> — <code>{esc(h_body[:120])}</code>")
            bump(2, "api_health_down")

        r_ok, r_body, r_code = await vpn_api_client.get_public_ready(settings)
        if r_ok:
            wg = ""
            if isinstance(r_body, dict):
                wg = str(r_body.get("wg") or "").strip()
            detail = f" ({esc(wg)})" if wg else ""
            lines.append(f"• API <code>/ready</code> (WireGuard): <b>ok</b>{detail}")
        elif r_code == 0:
            lines.append("• API <code>/ready</code>: <i>не проверялся</i>")
        else:
            lines.append(
                f"• API <code>/ready</code> (WireGuard): <b>FAIL</b> "
                f"<code>{esc(r_code)}</code> — <code>{esc(r_body[:120])}</code>"
            )
            bump(2, "api_ready_fail")

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

    status = {0: "ok", 1: "degraded", 2: "critical"}[severity_rank]
    return VpnOpsHealthSnapshot(
        status=status,
        checked_at_utc=now,
        lines_html=lines,
        issue_codes=issues,
    )


async def maybe_alert_vpn_ops_health(settings: Settings, snap: VpnOpsHealthSnapshot) -> None:
    if snap.status == "ok":
        return
    sev = "critical" if snap.status == "critical" else "warning"
    body = "\n".join(snap.lines_html)
    await send_alert(
        settings,
        severity=sev,
        title=f"VPN ops health: {snap.status}",
        body=body or snap.status,
        dedupe_key=f"vpn_ops_health:{snap.status}:{','.join(snap.issue_codes[:5])}",
    )


async def vpn_ops_health_loop(_bot, settings: Settings) -> None:
    interval = int(settings.vpn_ops_health_interval_seconds)
    if interval <= 0:
        return
    interval = max(60, interval)
    while True:
        try:
            snap = await collect_vpn_ops_health(settings)
            _log.info(
                "vpn_ops_health status=%s issues=%s",
                snap.status,
                snap.issue_codes,
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
