#!/usr/bin/env python3
"""AiMonkey OPS Command Center — credential-free digest for ADMIN_IDS.

Slots: morning (09:00), lunch (14:00), evening (21:00) Europe/Moscow.
No UUIDs, tokens, or private keys in rendered text.
Brand in Telegram: AiMonkey (не ALADDIN).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import socket
import sqlite3
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

MSK = ZoneInfo("Europe/Moscow")

Level = str  # green | yellow | red

RTT_YELLOW_MS = 200.0
WG_YELLOW_SEC = 180
WG_RED_SEC = 600
GUARD_STALE_SEC = 1800

# Order: Europe Contabo → Russia FirstVDS/REG/Yandex
# (Asia Contabo = SG двор — в блоке WG)
DEFAULT_DOORS: list[tuple[str, str, int, bool]] = [
    # Europe — Contabo
    ("🇩🇪 Brain · Contabo / мозг · …150 :8446", "127.0.0.1", 8446, False),
    ("🇫🇷 Mouth · Contabo / рот · …12", "169.58.242.12", 1080, False),
    # Russia — FirstVDS мост (EU/Asia/lab = профили на одном …98)
    ("🇷🇺 NEW EU · FirstVDS / мост · …98 :8444", "37.46.134.98", 8444, False),
    ("🇷🇺 NEW Asia · FirstVDS / мост · …98 :8445", "37.46.134.98", 8445, False),
    ("🇷🇺 NEW lab · FirstVDS / мост · …98 :5443", "37.46.134.98", 5443, False),
    ("🇷🇺 MAIN warm · FirstVDS / Аладдин · …180 :8444", "149.154.65.180", 8444, False),
    ("🇷🇺 REG · REG.RU / запас · …63 :443", "92.242.61.63", 443, False),
    ("🇷🇺 REG · REG.RU / запас · …63 :8443", "92.242.61.63", 8443, False),
    ("🇷🇺 Яндекс Обход-ночь · Яндекс / ночь · …20 :443", "84.201.151.20", 443, True),
]

WG_PEER_LABELS = {
    "37.46.134.98": "🇷🇺 NEW · FirstVDS / мост · …98",
    "149.154.65.180": "🇷🇺 MAIN · FirstVDS / Аладдин · …180",
    "92.242.61.63": "🇷🇺 REG · REG.RU / запас · …63",
    "217.15.166.78": "🇸🇬 SG · Contabo / двор · …78",
    "158.160.24.238": "🇷🇺 Яндекс · Яндекс / ночь · …238",
}


@dataclass(frozen=True)
class DoorLine:
    name: str
    level: Level
    detail: str


@dataclass(frozen=True)
class WgLine:
    name: str
    level: Level
    detail: str


@dataclass(frozen=True)
class GuardLine:
    level: Level
    errors: int
    active: int  # bridge UUID reconcile (includes friend-seed gifts)
    unknown: int
    note: str
    paid: int = 0  # vpn_active paid, excluding friend-seed 9901*
    trial: int = 0  # vpn_active trial


@dataclass(frozen=True)
class SpeedLine:
    level: Level
    primary: str
    secondary: str


@dataclass(frozen=True)
class ServiceLine:
    name: str
    level: Level


@dataclass
class Snapshot:
    slot: str
    when_msk: str
    doors: list[DoorLine]
    wg: list[WgLine]
    guard: GuardLine
    speed: SpeedLine
    services: list[ServiceLine]
    attention: list[str] = field(default_factory=list)


def level_emoji(level: Level) -> str:
    return {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(level, "⚪")


def overall_level(levels: list[Level]) -> Level:
    if any(level == "red" for level in levels):
        return "red"
    if any(level == "yellow" for level in levels):
        return "yellow"
    return "green"


def overall_label(level: Level) -> str:
    return {
        "green": "🟢 Штатно",
        "yellow": "🟡 Внимание",
        "red": "🔴 Инцидент",
    }.get(level, "⚪ Неизвестно")


def slot_title(slot: str) -> str:
    names = {
        "morning": "утро",
        "lunch": "обед",
        "evening": "вечер",
    }
    return names.get(slot, slot)


def score_door(*, ok: bool, ms: float | None) -> Level:
    if not ok:
        return "red"
    if ms is None:
        return "yellow"
    if ms >= RTT_YELLOW_MS:
        return "yellow"
    return "green"


def score_wg(age_sec: float | None) -> Level:
    if age_sec is None:
        return "red"
    if age_sec > WG_RED_SEC:
        return "red"
    if age_sec > WG_YELLOW_SEC:
        return "yellow"
    return "green"


def parse_admin_ids(raw: str) -> list[str]:
    ids: list[str] = []
    for part in raw.replace(";", ",").split(","):
        value = part.strip()
        if value.isdigit() and value not in ids:
            ids.append(value)
    return ids


def _median_ms(values: list[float]) -> float:
    """Median of RTT samples — one CPU hiccup must not paint the door yellow."""
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[mid])
    return (float(ordered[mid - 1]) + float(ordered[mid])) / 2.0


def probe_tcp_once(host: str, port: int, timeout: float = 3.0) -> tuple[bool, float]:
    started = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, (time.monotonic() - started) * 1000.0
    except OSError:
        return False, (time.monotonic() - started) * 1000.0


def probe_tcp(
    host: str,
    port: int,
    timeout: float = 3.0,
    *,
    attempts: int = 3,
    pause_sec: float = 0.15,
) -> tuple[bool, float]:
    """TCP door probe: 3 tries → median ms (report shows only the median)."""
    samples: list[float] = []
    ok_samples: list[float] = []
    n = max(1, int(attempts))
    for i in range(n):
        ok, ms = probe_tcp_once(host, port, timeout=timeout)
        samples.append(ms)
        if ok:
            ok_samples.append(ms)
        if i + 1 < n and pause_sec > 0:
            time.sleep(pause_sec)
    if ok_samples:
        return True, _median_ms(ok_samples)
    return False, _median_ms(samples)


def _parse_handshake_age(text: str) -> float | None:
    text = text.strip().lower()
    if not text or text == "never":
        return None
    if text == "now":
        return 0.0
    total = 0.0
    for amount, unit in re.findall(
        r"(\d+)\s+(second|minute|hour|day)s?", text
    ):
        n = float(amount)
        if unit.startswith("second"):
            total += n
        elif unit.startswith("minute"):
            total += n * 60
        elif unit.startswith("hour"):
            total += n * 3600
        elif unit.startswith("day"):
            total += n * 86400
    return total if total or "second" in text or "minute" in text else None


# Friend-seed pool from vpn_grant_beta_batch («ссылки друзьям») — not commercial KPI.
FRIEND_SEED_TID_LO = 990100001
FRIEND_SEED_TID_HI = 990100099


def _format_handshake_ru(text: str) -> str:
    """Human age of last WG keepalive — not tunnel speed."""
    age = _parse_handshake_age(text)
    if age is None:
        raw = (text or "").strip().lower()
        if not raw or raw == "never":
            return "связь нет"
        return f"связь {text.strip()}"
    if age < 5:
        return "связь только что"
    if age < 60:
        return f"связь {int(age)}с назад"
    if age < 3600:
        mins = int(age // 60)
        secs = int(age % 60)
        body = f"{mins}м {secs}с назад" if secs else f"{mins}м назад"
        return f"связь {body}"
    hours = int(age // 3600)
    mins = int((age % 3600) // 60)
    body = f"{hours}ч {mins}м назад" if mins else f"{hours}ч назад"
    return f"связь {body}"


def _guard_plain(guard: GuardLine) -> str:
    """Guard for admins: commercial clients only (paid+trial), no friend-seed 9901*."""
    note = (guard.note or "").strip()
    if "desired≠active" in note:
        plain = "в конфиге моста не хватает UUID"
    elif note == "fresh":
        plain = "список ок"
    elif "stale" in note.lower():
        plain = "статус устарел"
    elif "missing" in note.lower() or "unreadable" in note.lower():
        plain = note
    else:
        plain = note or "—"
    clients = int(guard.paid) + int(guard.trial)
    return (
        f"платные={guard.paid} · триал={guard.trial} · клиенты={clients} · "
        f"unknown={guard.unknown} · errors={guard.errors} · {plain}"
    )


def collect_client_counts(
    db_path: Path | None = None,
) -> tuple[int, int]:
    """vpn_active paid/trial for OPS report.

    Includes: real Telegram TIDs with account_kind paid|trial.
    Excludes: friend-seed 9901* (ссылки друзьям), lab 9900*, tid<=0.
    """
    path = db_path or Path(
        os.environ.get("VPN_DB_PATH", "/opt/aladdin-shop-vpn-api/var/vpn.db")
    )
    if not path.is_file():
        return 0, 0
    try:
        with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
            rows = db.execute(
                """
                SELECT lower(trim(account_kind)) AS kind, COUNT(*)
                FROM vpn_accounts
                WHERE status = 'vpn_active'
                  AND xray_client_uuid IS NOT NULL
                  AND trim(xray_client_uuid) != ''
                  AND CAST(telegram_user_id AS INTEGER) > 0
                  AND CAST(telegram_user_id AS INTEGER) NOT BETWEEN ? AND ?
                  AND CAST(telegram_user_id AS TEXT) NOT LIKE '9900%'
                GROUP BY 1
                """,
                (FRIEND_SEED_TID_LO, FRIEND_SEED_TID_HI),
            ).fetchall()
    except sqlite3.Error:
        return 0, 0
    paid = 0
    trial = 0
    for kind, count in rows:
        if kind == "paid":
            paid = int(count)
        elif kind == "trial":
            trial = int(count)
    return paid, trial


def collect_wg_bridge(
    *,
    interface: str = "wg-bridge",
    run: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> list[WgLine]:
    runner = run or subprocess.run
    try:
        completed = runner(
            ["wg", "show", interface],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return [WgLine("wg-bridge", "red", "wg show failed")]
    if completed.returncode != 0:
        return [WgLine("wg-bridge", "red", "wg show failed")]

    lines: list[WgLine] = []
    endpoint = ""
    handshake = ""
    for raw in completed.stdout.splitlines():
        line = raw.strip()
        if line.startswith("peer:"):
            if endpoint:
                host = endpoint.split(":")[0]
                label = WG_PEER_LABELS.get(host, host.split(".")[-1] if host else "?")
                age = _parse_handshake_age(handshake)
                level = score_wg(age)
                detail = _format_handshake_ru(handshake) if handshake else "связь нет"
                lines.append(WgLine(label, level, detail))
            endpoint = ""
            handshake = ""
        elif line.startswith("endpoint:"):
            endpoint = line.split(":", 1)[1].strip()
        elif line.startswith("latest handshake:"):
            handshake = line.split(":", 1)[1].strip()
    if endpoint:
        host = endpoint.split(":")[0]
        label = WG_PEER_LABELS.get(host, host.split(".")[-1] if host else "?")
        age = _parse_handshake_age(handshake)
        lines.append(
            WgLine(
                label,
                score_wg(age),
                _format_handshake_ru(handshake) if handshake else "связь нет",
            )
        )
    if not lines:
        return [WgLine("wg-bridge", "yellow", "no peers")]
    # Stable order: NEW (мост) → MAIN → REG → SG (Asia Contabo) → Yandex
    order = {
        "🇷🇺 NEW · FirstVDS / мост · …98": 0,
        "🇷🇺 MAIN · FirstVDS / Аладдин · …180": 1,
        "🇷🇺 REG · REG.RU / запас · …63": 2,
        "🇸🇬 SG · Contabo / двор · …78": 3,
        "🇷🇺 Яндекс · Яндекс / ночь · …238": 4,
        "🇷🇺 NEW": 0,
        "🇷🇺 MAIN": 1,
        "🇷🇺 REG": 2,
        "🇸🇬 SG": 3,
        "🇷🇺 Яндекс": 4,
        "NEW": 0,
        "MAIN": 1,
        "REG": 2,
        "SG": 3,
        "P01": 4,
        "Яндекс": 4,
    }
    lines.sort(key=lambda item: order.get(item.name, 50))
    return lines


def collect_guard(
    path: Path,
    *,
    now: datetime | None = None,
    db_path: Path | None = None,
) -> GuardLine:
    now = now or datetime.now(timezone.utc)
    paid, trial = collect_client_counts(db_path)
    if not path.is_file():
        return GuardLine("red", 0, 0, 0, "status missing", paid=paid, trial=trial)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return GuardLine("red", 0, 0, 0, "status unreadable", paid=paid, trial=trial)

    errors = int(data.get("repair_errors") or 0)
    active = int(data.get("active_count") or 0)
    desired = int(data.get("desired_count") or active)
    unknown = int(data.get("unknown_preserved") or 0)
    ok = bool(data.get("ok"))
    checked = str(data.get("checked_at_utc") or "")
    age_sec = None
    if checked:
        try:
            checked_dt = datetime.fromisoformat(checked.replace("Z", "+00:00"))
            age_sec = (now - checked_dt).total_seconds()
        except ValueError:
            age_sec = None

    notes: list[str] = []
    level: Level = "green"
    if errors or not ok:
        level = "red"
        notes.append(f"errors={errors}")
    if age_sec is not None and age_sec > GUARD_STALE_SEC:
        level = "red" if level == "red" else "yellow"
        notes.append("stale")
    if desired != active:
        if level == "green":
            level = "yellow"
        notes.append("desired≠active")
    if not notes:
        notes.append("fresh" if age_sec is not None else "ok")
    return GuardLine(
        level,
        errors,
        active,
        unknown,
        ", ".join(notes),
        paid=paid,
        trial=trial,
    )


def _last_csv_rows(path: Path, limit: int = 20) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            rows = list(csv.DictReader(handle))
    except OSError:
        return []
    return rows[-limit:]


def collect_speed(
    tunnel_csv: Path,
    path_csv: Path,
    *,
    slot: str,
) -> SpeedLine:
    tunnel_rows = _last_csv_rows(tunnel_csv, 48)
    path_rows = _last_csv_rows(path_csv, 48)

    primary = "tunnel: нет данных"
    level: Level = "yellow"
    if tunnel_rows:
        last = tunnel_rows[-1]
        err = str(last.get("rc") or last.get("err") or last.get("error") or "0").strip()
        bytes_raw = last.get("bytes") or last.get("downloaded") or ""
        if not bytes_raw:
            values = list(last.values())
            bytes_raw = values[4] if len(values) > 4 else (values[1] if len(values) > 1 else "0")
        try:
            nbytes = int(float(str(bytes_raw)))
        except (TypeError, ValueError):
            nbytes = 0
        if err not in {"", "0", "None", "none"} or nbytes <= 0:
            level = "red"
            primary = f"tunnel FAIL · last rc={err or 'empty'}"
        else:
            level = "green"
            mb = nbytes / 1_000_000
            primary = f"tunnel last OK · ~{mb:.0f}MB"

    secondary = ""
    brain_mbs: float | None = None
    new_mbs: float | None = None
    for row in reversed(path_rows):
        host = str(
            row.get("host_role") or row.get("host") or row.get("hostname") or ""
        ).lower()
        raw_mbs = row.get("cf_mbs") or row.get("mbs") or row.get("mb_s") or 0
        try:
            mbs = float(raw_mbs)
        except (TypeError, ValueError):
            mbs = 0.0
        if brain_mbs is None and ("contabo" in host or "brain" in host):
            brain_mbs = mbs
        if new_mbs is None and ("newru" in host or host.startswith("new")):
            new_mbs = mbs
        if brain_mbs is not None and new_mbs is not None:
            break

    if new_mbs is not None:
        secondary = f"NEW path ~{new_mbs:.1f} MB/s"
        if brain_mbs is not None and brain_mbs > 0 and new_mbs < brain_mbs * 0.45:
            if level == "green":
                level = "yellow"
            secondary += " (ниже Brain)"
        if slot == "evening" and brain_mbs is not None:
            secondary += f" · Brain ~{brain_mbs:.1f} MB/s"

    return SpeedLine(level, primary, secondary)


def collect_services(
    *,
    systemctl: Callable[[str], bool] | None = None,
    health_ok: Callable[[str], bool] | None = None,
) -> list[ServiceLine]:
    def _active(unit: str) -> bool:
        if systemctl is not None:
            return systemctl(unit)
        try:
            completed = subprocess.run(
                ["systemctl", "is-active", unit],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return completed.stdout.strip() == "active"
        except (OSError, subprocess.TimeoutExpired):
            return False

    def _health(url: str) -> bool:
        if health_ok is not None:
            return health_ok(url)
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                body = response.read(200).decode("utf-8", errors="replace")
                return response.status == 200 and "ok" in body.lower()
        except (urllib.error.URLError, TimeoutError, ValueError):
            return False

    rows = [
        ServiceLine("bot", "green" if _active("aladdin-telegram-bot") else "red"),
        ServiceLine(
            "vpn-api",
            "green"
            if _active("aladdin-shop-vpn-api") and _health("http://127.0.0.1:8091/health")
            else "red",
        ),
        ServiceLine(
            "partner",
            "green"
            if _active("aladdin-partner-api") and _health("http://127.0.0.1:8090/health")
            else "red",
        ),
        ServiceLine(
            "🇷🇺 MAIN API · FirstVDS",
            "green"
            if _health("http://149.154.65.180:8002/api/health")
            else "red",
        ),
    ]
    return rows


def build_attention(snap_parts: Snapshot) -> list[str]:
    notes: list[str] = []
    for door in snap_parts.doors:
        if door.level != "green":
            notes.append(f"{door.name} — {door.detail}")
    for peer in snap_parts.wg:
        if peer.level != "green":
            notes.append(f"WG {peer.name} — {peer.detail}")
    if snap_parts.guard.level != "green":
        notes.append(f"Guard: {snap_parts.guard.note}")
    if snap_parts.speed.level != "green":
        detail = snap_parts.speed.secondary or snap_parts.speed.primary
        notes.append(f"Скорость: {detail}")
    for service in snap_parts.services:
        if service.level != "green":
            notes.append(f"Сервис {service.name} — проблема")
    # Cap attention list
    return notes[:8]


def build_snapshot(
    *,
    slot: str,
    now_msk_label: str | None = None,
    guard_path: Path | None = None,
    tunnel_csv: Path | None = None,
    path_csv: Path | None = None,
    probe_fn: Callable[[str, int], tuple[bool, float]] | None = None,
    wg_fn: Callable[[], list[WgLine]] | None = None,
    services_fn: Callable[[], list[ServiceLine]] | None = None,
    door_specs: list[tuple[str, str, int, bool]] | None = None,
) -> Snapshot:
    now_msk = datetime.now(MSK)
    when = now_msk_label or now_msk.strftime("%d.%m.%Y · %H:%M МСК")
    guard_path = guard_path or Path(
        os.environ.get(
            "VPN_BRIDGE_PEERS_STATUS_PATH",
            "/opt/aladdin-shop-vpn-api/var/bridge_peers_status.json",
        )
    )
    tunnel_csv = tunnel_csv or Path(
        os.environ.get(
            "VPN_OPS_TUNNEL_CSV",
            "/var/lib/aladdin-vpn-ops/tunnel_speed_timeseries.csv",
        )
    )
    path_csv = path_csv or Path(
        os.environ.get(
            "VPN_OPS_PATH_CSV",
            "/var/lib/aladdin-vpn-ops/path_host_metrics.csv",
        )
    )
    probe = probe_fn or (lambda host, port: probe_tcp(host, port))
    doors: list[DoorLine] = []
    for name, host, port, staging in door_specs or DEFAULT_DOORS:
        ok, ms = probe(host, port)
        level = score_door(ok=ok, ms=ms)
        if ok:
            detail = f"{ms:.0f}ms"
        else:
            detail = "TCP fail"
        if staging:
            detail = f"staging · {detail}"
        doors.append(DoorLine(name, level, detail))

    wg = wg_fn() if wg_fn else collect_wg_bridge()
    guard = collect_guard(guard_path)
    speed = collect_speed(tunnel_csv, path_csv, slot=slot)
    services = services_fn() if services_fn else collect_services()

    snap = Snapshot(
        slot=slot,
        when_msk=when,
        doors=doors,
        wg=wg,
        guard=guard,
        speed=speed,
        services=services,
        attention=[],
    )
    snap.attention = build_attention(snap)
    return snap


def render_report(snap: Snapshot) -> str:
    levels = (
        [door.level for door in snap.doors]
        + [peer.level for peer in snap.wg]
        + [snap.guard.level, snap.speed.level]
        + [service.level for service in snap.services]
    )
    outcome = overall_level(levels)
    lines = [
        f"🛡 AiMonkey OPS — {slot_title(snap.slot)}",
        snap.when_msk,
        f"Итог: {overall_label(outcome)}",
        "",
        "🚪 Двери",
    ]
    for door in snap.doors:
        lines.append(
            f"{level_emoji(door.level)} {door.name} · {door.detail}"
        )
    lines.append("")
    lines.append("🔗 Мост WG")
    for peer in snap.wg:
        lines.append(
            f"{level_emoji(peer.level)} {peer.name} · {peer.detail}"
        )
    lines.append("")
    lines.append("🛡 Guard")
    lines.append(
        f"{level_emoji(snap.guard.level)} {_guard_plain(snap.guard)}"
    )
    lines.append("")
    lines.append("⚡ Скорость")
    lines.append(f"{level_emoji(snap.speed.level)} {snap.speed.primary}")
    if snap.speed.secondary:
        lines.append(f"   {snap.speed.secondary}")
    lines.append("")
    lines.append("🧩 Сервисы")
    service_bits = [
        f"{level_emoji(service.level)} {service.name}"
        for service in snap.services
    ]
    lines.append(" · ".join(service_bits))
    lines.append("")
    lines.append("📌 Внимание")
    if snap.attention:
        for item in snap.attention:
            lines.append(f"• {item}")
    else:
        lines.append("• нет — всё спокойно")
    lines.append("")
    lines.append("Срочные 🔴 приходят сразу (всем админам)")
    text = "\n".join(lines)
    if len(text) > 3500:
        text = text[:3490] + "\n…"
    return text


def resolve_slot(value: str | None = None) -> str:
    if value in {"morning", "lunch", "evening"}:
        return value
    hour = datetime.now(MSK).hour
    if hour < 12:
        return "morning"
    if hour < 18:
        return "lunch"
    return "evening"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AiMonkey OPS Command Center")
    parser.add_argument(
        "--slot",
        choices=("morning", "lunch", "evening", "auto"),
        default="auto",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="print report to stdout (no Telegram)",
    )
    args = parser.parse_args(argv)
    slot = resolve_slot(None if args.slot == "auto" else args.slot)
    snap = build_snapshot(slot=slot)
    text = render_report(snap)
    print(text)
    return 0 if overall_level(
        [door.level for door in snap.doors]
        + [peer.level for peer in snap.wg]
        + [snap.guard.level, snap.speed.level]
        + [service.level for service in snap.services]
    ) != "red" else 1


if __name__ == "__main__":
    raise SystemExit(main())
