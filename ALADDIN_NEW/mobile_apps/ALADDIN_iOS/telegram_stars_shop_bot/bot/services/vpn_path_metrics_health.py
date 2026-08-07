"""
Path metrics (CSV) for /vpn_health — Contabo local + RU entry (NEW) via SSH.

Колонки path_host_metrics.csv:
ts_utc,host_role,hostname,cf_bps,cf_mbs,listen_port,sessions,
mem_total_m,mem_used_m,mem_avail_m,swap_total_m,swap_used_m,load1,wg_rtt_ms,wg_tx,wg_rx

host_role: contabo | newru (prod entry) | main149 (legacy entry, rollback).
"""

from __future__ import annotations

import asyncio
import csv
import io
import logging
from dataclasses import dataclass
from pathlib import Path

from bot.config import Settings
from bot.util_html import esc

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class PathRow:
    ts_utc: str
    host_role: str
    cf_mbs: float
    sessions: int
    swap_total_m: int
    swap_used_m: int
    load1: float
    wg_rtt_ms: float | None

    @property
    def swap_ratio(self) -> float | None:
        if self.swap_total_m <= 0:
            return None
        return self.swap_used_m / self.swap_total_m


@dataclass
class PathVerdict:
    lines_html: list[str]
    issue_codes: list[str]
    severity: int  # 0 ok, 1 degraded, 2 critical


def parse_path_csv(text: str) -> list[PathRow]:
    text = (text or "").strip()
    if not text:
        return []
    reader = csv.DictReader(io.StringIO(text))
    rows: list[PathRow] = []
    for raw in reader:
        try:
            rtt_raw = (raw.get("wg_rtt_ms") or "").strip()
            rtt = float(rtt_raw) if rtt_raw else None
            rows.append(
                PathRow(
                    ts_utc=str(raw.get("ts_utc") or "").strip(),
                    host_role=str(raw.get("host_role") or "").strip(),
                    cf_mbs=float(raw.get("cf_mbs") or 0),
                    sessions=int(float(raw.get("sessions") or 0)),
                    swap_total_m=int(float(raw.get("swap_total_m") or 0)),
                    swap_used_m=int(float(raw.get("swap_used_m") or 0)),
                    load1=float(raw.get("load1") or 0),
                    wg_rtt_ms=rtt,
                )
            )
        except (TypeError, ValueError):
            continue
    return rows


def latest_row(rows: list[PathRow]) -> PathRow | None:
    return rows[-1] if rows else None


def _icon(level: str) -> str:
    return {"ok": "🟢", "warn": "🟡", "bad": "🔴", "na": "⚪"}.get(level, "⚪")


def _rtt_level(ms: float | None) -> str:
    if ms is None:
        return "na"
    if ms >= 400:
        return "bad"
    if ms >= 200:
        return "warn"
    return "ok"


def _swap_level(ratio: float | None) -> str:
    if ratio is None:
        return "na"
    if ratio >= 0.85:
        return "bad"
    if ratio >= 0.50:
        return "warn"
    return "ok"


def _cf_level(mbs: float) -> str:
    if mbs < 2.0:
        return "bad"
    if mbs < 5.0:
        return "warn"
    return "ok"


def _cf_float_note(recent_mbs: list[float]) -> tuple[str, str]:
    """Return (level, plain sentence) about Contabo CF variability."""
    if len(recent_mbs) < 2:
        return "na", "Мало замеров — пока рано судить о «плавании» канала."
    lo, hi = min(recent_mbs), max(recent_mbs)
    if hi >= 8 and lo <= 4:
        return (
            "warn",
            f"Канал Contabo <b>плавает</b>: за последние замеры "
            f"<code>{esc(f'{lo:.1f}')}</code>…<code>{esc(f'{hi:.1f}')}</code> MB/s. "
            "Следим, не паника.",
        )
    if hi - lo < 3:
        return "ok", "Замеры Contabo CF относительно стабильны."
    return (
        "warn",
        f"Разброс Contabo CF <code>{esc(f'{lo:.1f}')}</code>…<code>{esc(f'{hi:.1f}')}</code> MB/s.",
    )


def build_plain_language_report(
    *,
    row_149: PathRow | None,
    row_contabo: PathRow | None,
    contabo_recent_cf: list[float] | None = None,
) -> PathVerdict:
    """Полный отчёт простым языком (для /vpn_health и дайджеста раз в 5 ч)."""
    lines: list[str] = [
        "",
        "<b>📊 VPN — полный отчёт (простым языком)</b>",
        "<i>Путь: телефон → Россия (NEW) → мост → Contabo → интернет</i>",
    ]
    issues: list[str] = []
    sev = 0

    if row_149 is None and row_contabo is None:
        lines.append("• <i>CSV ещё нет — cron path-metrics не успел</i>")
        return PathVerdict(lines_html=lines, issue_codes=["path_csv_empty"], severity=1)

    # --- 1) RTT NEW → Contabo (from entry CSV; var name row_149 = remote entry) ---
    lines.append("")
    lines.append("<b>1) Мост RTT (NEW → Contabo)</b>")
    lines.append(
        "<i>Что это:</i> время «туда» по трубе Россия→Европа (как пинг в игре)."
    )
    lines.append("<i>Норма:</i> обычно &lt; 120 ms, иногда до 200. Плохо: часто &gt; 200 / пики 400+.")
    if row_149 and row_149.wg_rtt_ms is not None:
        lvl = _rtt_level(row_149.wg_rtt_ms)
        lines.append(
            f"{_icon(lvl)} <b>Сейчас:</b> <code>{esc(f'{row_149.wg_rtt_ms:.0f}')}</code> ms "
            f"(замер <code>{esc(row_149.ts_utc)}</code>)"
        )
        if lvl == "bad":
            issues.append("wg_rtt_high")
            sev = max(sev, 1)
            lines.append("→ Мост сейчас сильно тормозит.")
        elif lvl == "warn":
            issues.append("wg_rtt_elevated")
            sev = max(sev, 1)
            lines.append("→ Терпимо, но выше комфорта — следить.")
        else:
            lines.append("→ Нормально для double-hop.")
    else:
        lines.append(f"{_icon('na')} Нет замера RTT с NEW.")

    # --- 2) RTT Contabo → NEW ---
    lines.append("")
    lines.append("<b>2) Мост обратно (Contabo → NEW)</b>")
    lines.append("<i>Что это:</i> то же, в обратную сторону.")
    if row_contabo and row_contabo.wg_rtt_ms is not None:
        lvl = _rtt_level(row_contabo.wg_rtt_ms)
        lines.append(
            f"{_icon(lvl)} <b>Сейчас:</b> <code>{esc(f'{row_contabo.wg_rtt_ms:.0f}')}</code> ms "
            f"(<code>{esc(row_contabo.ts_utc)}</code>)"
        )
        if lvl in ("warn", "bad"):
            issues.append("wg_rtt_back_high")
            sev = max(sev, 1)
    else:
        lines.append(f"{_icon('na')} Нет замера RTT с Contabo.")

    # --- 3) Contabo CF ---
    lines.append("")
    lines.append("<b>3) Contabo CF (скорость европейского выхода)</b>")
    lines.append(
        "<i>Что это:</i> как быстро Contabo качает тест Cloudflare <b>без телефона</b> — "
        "потолок выхода в интернет."
    )
    lines.append("<i>Норма:</i> устойчиво &gt; ~5 MB/s, хорошо 10–25. Плохо: долго &lt; 2–3.")
    if row_contabo:
        lvl = _cf_level(row_contabo.cf_mbs)
        lines.append(
            f"{_icon(lvl)} <b>Сейчас:</b> <code>{esc(f'{row_contabo.cf_mbs:.2f}')}</code> MB/s · "
            f"sessions <code>{esc(str(row_contabo.sessions))}</code>"
        )
        if lvl == "bad":
            issues.append("contabo_cf_low")
            sev = max(sev, 1)
            lines.append("→ Uplink Contabo сейчас слабый (не путать с Happ).")
        elif lvl == "warn":
            issues.append("contabo_cf_low")
            sev = max(sev, 1)
            lines.append("→ Слабовато, но не «ноль».")
        else:
            lines.append("→ Для снимка хорошо.")
    else:
        lines.append(f"{_icon('na')} Нет CSV Contabo.")
        issues.append("path_csv_contabo_missing")
        sev = max(sev, 1)

    # --- 4) Float ---
    lines.append("")
    lines.append("<b>4) Плавает ли Contabo CF?</b>")
    lines.append(
        "<i>Что это:</i> сравниваем несколько последних замеров — то ок, то душно."
    )
    recent = list(contabo_recent_cf or [])
    if not recent and row_contabo:
        recent = [row_contabo.cf_mbs]
    flvl, fnote = _cf_float_note(recent)
    lines.append(f"{_icon(flvl)} {fnote}")
    if flvl == "warn":
        issues.append("contabo_cf_volatile")

    # --- 5) Swap на RU entry (NEW) ---
    lines.append("")
    lines.append("<b>5) Swap на NEW (память российского входа)</b>")
    lines.append(
        "<i>Что это:</i> серверу в РФ не хватило быстрой RAM — пишет на диск "
        "(как телефон с забитой памятью)."
    )
    lines.append("<i>Норма:</i> &lt; 50% (лучше &lt; 20%). Плохо &gt; 85%, критично ~95%+.")
    if row_149 and row_149.swap_total_m > 0:
        ratio = row_149.swap_ratio or 0.0
        pct = int(round(ratio * 100))
        lvl = _swap_level(ratio)
        lines.append(
            f"{_icon(lvl)} <b>Сейчас:</b> "
            f"<code>{esc(str(row_149.swap_used_m))}/{esc(str(row_149.swap_total_m))}</code> MiB "
            f"(<code>{esc(str(pct))}%</code>) · CF NEW "
            f"<code>{esc(f'{row_149.cf_mbs:.2f}')}</code> MB/s · "
            f"sessions <code>{esc(str(row_149.sessions))}</code>"
        )
        if lvl == "bad":
            issues.append("swap_149_high")
            sev = max(sev, 2 if ratio >= 0.95 else 1)
            lines.append("→ <b>Главная причина тормозов входа</b> — лечить RAM на NEW.")
        elif lvl == "warn":
            issues.append("swap_149_elevated")
            sev = max(sev, 1)
            lines.append("→ Ещё высоко — память NEW в приоритете.")
        else:
            lines.append("→ Память входа в норме.")
    else:
        lines.append(f"{_icon('na')} Нет данных swap с NEW.")
        issues.append("path_csv_149_missing")
        sev = max(sev, 1)

    # --- summary ---
    lines.append("")
    if sev >= 2 or "swap_149_high" in issues:
        summary = (
            "Итог: Contabo часто ок; <b>узкое место — память (swap) на NEW</b>. "
            "Потом мост RTT, потом CF Contabo."
        )
    elif "contabo_cf_low" in issues:
        summary = "Итог: смотреть uplink Contabo; swap/мост проверить рядом."
    elif sev == 0:
        summary = "Итог: по серверным метрикам сейчас спокойно. Happ Mbps — отдельно с телефона."
    else:
        summary = (
            "Итог: есть жёлтые зоны. Порядок: 1) swap NEW → 2) RTT → 3) Contabo CF → 4) Xray."
        )
    lines.append(f"<b>{summary}</b>")
    lines.append(
        "<i>Happ Mbps с телефона в этот отчёт не входит — замерьте рядом с этим снимком.</i>"
    )
    return PathVerdict(lines_html=lines, issue_codes=issues, severity=sev)


# backward-compatible name
def verdict_from_rows(
    *,
    row_149: PathRow | None,
    row_contabo: PathRow | None,
    contabo_recent_cf: list[float] | None = None,
    **_kwargs,
) -> PathVerdict:
    return build_plain_language_report(
        row_149=row_149,
        row_contabo=row_contabo,
        contabo_recent_cf=contabo_recent_cf,
    )


def _read_local_csv(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


async def _ssh_cat_csv(
    *,
    host: str,
    user: str,
    key_path: str,
    remote_csv: str,
    timeout: float = 12.0,
    tail_n: int = 8,
) -> str:
    key = Path(key_path)
    if not key.is_file():
        _log.warning("path_metrics ssh key missing: %s", key_path)
        return ""
    cmd = [
        "ssh",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        f"ConnectTimeout={max(3, int(timeout))}",
        "-i",
        str(key),
        f"{user}@{host}",
        f"tail -n {int(tail_n)} {remote_csv}",
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout + 2)
        if proc.returncode != 0:
            _log.warning(
                "path_metrics ssh fail rc=%s err=%s",
                proc.returncode,
                (stderr or b"")[:200].decode("utf-8", errors="replace"),
            )
            return ""
        body = stdout.decode("utf-8", errors="replace")
        # ensure header for DictReader if tail skipped it
        if body and not body.lstrip().startswith("ts_utc"):
            hdr = (
                "ts_utc,host_role,hostname,cf_bps,cf_mbs,listen_port,sessions,"
                "mem_total_m,mem_used_m,mem_avail_m,swap_total_m,swap_used_m,"
                "load1,wg_rtt_ms,wg_tx,wg_rx\n"
            )
            body = hdr + body
        return body
    except Exception:
        _log.exception("path_metrics ssh error host=%s", host)
        return ""


async def collect_path_metrics_verdict(settings: Settings) -> PathVerdict:
    if not bool(getattr(settings, "vpn_path_metrics_enabled", True)):
        return PathVerdict(lines_html=[], issue_codes=[], severity=0)

    local_path = Path(
        (getattr(settings, "vpn_path_metrics_csv", None) or "").strip()
        or "/var/lib/aladdin-vpn-ops/path_host_metrics.csv"
    )
    remote_host = (
        (getattr(settings, "vpn_path_metrics_remote_host", None) or "").strip()
        or (settings.vpn_bridge_health_host or "").strip()
        or "37.46.134.98"
    )
    ssh_key = (
        (getattr(settings, "vpn_path_metrics_ssh_key", None) or "").strip()
        or "/root/.ssh/id_ed25519"
    )
    ssh_user = (getattr(settings, "vpn_path_metrics_ssh_user", None) or "").strip() or "root"

    local_text = await asyncio.to_thread(_read_local_csv, local_path)
    remote_text = ""
    if remote_host:
        remote_text = await _ssh_cat_csv(
            host=remote_host,
            user=ssh_user,
            key_path=ssh_key,
            remote_csv=str(local_path),
            tail_n=8,
        )

    local_rows = parse_path_csv(local_text)
    remote_rows = parse_path_csv(remote_text)

    row_contabo = latest_row(local_rows)
    row_149 = latest_row(remote_rows)

    # Remote entry roles after cutover: newru (prod) or main149 (legacy).
    if row_contabo and row_contabo.host_role in ("main149", "newru") and row_149 is None:
        row_149, row_contabo = row_contabo, None
        local_rows, remote_rows = remote_rows, local_rows
    if row_149 and row_149.host_role == "contabo" and row_contabo is None:
        row_contabo, row_149 = row_149, None

    recent_cf = [r.cf_mbs for r in local_rows[-12:]]

    return build_plain_language_report(
        row_149=row_149,
        row_contabo=row_contabo,
        contabo_recent_cf=recent_cf,
    )
