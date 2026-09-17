"""Command Center OPS digest — scoring, render, no secrets."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "deploy" / "scripts" / "vpn_ops_command_center.py"


def _load():
    import sys

    spec = importlib.util.spec_from_file_location("vpn_ops_command_center", MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_module_exists():
    assert MODULE.is_file()


def test_score_door_rtt_thresholds():
    cc = _load()
    assert cc.score_door(ok=True, ms=50) == "green"
    assert cc.score_door(ok=True, ms=200) == "yellow"
    assert cc.score_door(ok=False, ms=500) == "red"


def test_median_ms_ignores_single_spike():
    cc = _load()
    # One CPU hiccup (334) must not win over two healthy samples.
    assert cc._median_ms([48.0, 334.0, 55.0]) == 55.0
    assert cc._median_ms([442.0, 50.0, 52.0]) == 52.0
    assert cc._median_ms([100.0]) == 100.0


def test_probe_tcp_uses_median_of_ok_samples(monkeypatch):
    cc = _load()
    seq = iter([(True, 48.0), (True, 334.0), (True, 55.0)])

    def fake_once(host: str, port: int, timeout: float = 3.0):
        return next(seq)

    monkeypatch.setattr(cc, "probe_tcp_once", fake_once)
    monkeypatch.setattr(cc.time, "sleep", lambda _s: None)
    ok, ms = cc.probe_tcp("37.46.134.98", 8444, attempts=3, pause_sec=0.0)
    assert ok is True
    assert ms == 55.0


def test_score_wg_handshake_age():
    cc = _load()
    assert cc.score_wg(age_sec=30) == "green"
    assert cc.score_wg(age_sec=300) == "yellow"
    assert cc.score_wg(age_sec=700) == "red"
    assert cc.score_wg(age_sec=None) == "red"


def test_overall_prefers_red_over_yellow():
    cc = _load()
    assert cc.overall_level(["green", "yellow"]) == "yellow"
    assert cc.overall_level(["green", "red", "yellow"]) == "red"
    assert cc.overall_level(["green", "green"]) == "green"


def test_render_evening_all_green_no_secrets():
    cc = _load()
    snap = cc.Snapshot(
        slot="evening",
        when_msk="12.09.2026 · 21:00 МСК",
        doors=[
            cc.DoorLine("🇩🇪 Brain · Contabo / мозг · …150 :8446", "green", "1ms"),
            cc.DoorLine("🇷🇺 NEW Asia · FirstVDS / мост · …98 :8445", "green", "61ms"),
            cc.DoorLine("🇷🇺 NEW EU · FirstVDS / мост · …98 :8444", "green", "52ms"),
            cc.DoorLine("🇷🇺 Яндекс Обход-ночь · Яндекс / ночь · …20 :443", "green", "staging · 40ms"),
        ],
        wg=[
            cc.WgLine("🇷🇺 NEW · FirstVDS / мост · …98", "green", "связь 1м назад"),
            cc.WgLine("🇸🇬 SG · Contabo / двор · …78", "green", "связь 40с назад"),
        ],
        guard=cc.GuardLine(
            "green", errors=0, active=78, unknown=9, note="fresh", paid=28, trial=24
        ),
        speed=cc.SpeedLine(
            "green",
            "tunnel last OK · 20MB/15m",
            "NEW path ~8.8 MB/s",
        ),
        services=[
            cc.ServiceLine("bot", "green"),
            cc.ServiceLine("vpn-api", "green"),
            cc.ServiceLine("partner", "green"),
        ],
        attention=[],
    )
    text = cc.render_report(snap)
    assert "AiMonkey OPS — вечер" in text
    assert "ALADDIN OPS" not in text
    assert "Итог: 🟢 Штатно" in text
    assert "🟢 🇷🇺 NEW EU · FirstVDS / мост · …98 :8444 · 52ms" in text
    assert "Contabo / мозг" in text
    assert "Яндекс Обход-ночь" in text and "staging" in text
    assert "платные=28" in text and "триал=24" in text and "клиенты=52" in text
    assert "vpn_active=" not in text
    assert "список ок" in text
    assert "связь 1м назад" in text
    assert "🛡 Guard" in text
    assert "⚡ Скорость" in text
    assert "tunnel last OK" in text
    assert "📌 Внимание" in text
    assert "нет" in text.lower() or "спокойно" in text.lower()
    assert "Срочные 🔴 приходят сразу" in text
    for banned in ("BEGIN PRIVATE", "bot_token", "api_key", "xray_client_uuid"):
        assert banned not in text.lower()
    assert "связь 1м назад" in text
    assert "🛡 Guard" in text
    assert "⚡ Скорость" in text
    assert "tunnel last OK" in text
    assert "📌 Внимание" in text
    assert "нет" in text.lower() or "спокойно" in text.lower()
    assert "Срочные 🔴 приходят сразу" in text
    for banned in ("BEGIN PRIVATE", "bot_token", "api_key", "xray_client_uuid"):
        assert banned not in text.lower()


def test_format_handshake_ru_not_speed():
    cc = _load()
    assert cc._format_handshake_ru("1 minute, 24 seconds ago") == "связь 1м 24с назад"
    assert cc._format_handshake_ru("48 seconds ago") == "связь 48с назад"
    assert cc._format_handshake_ru("never") == "связь нет"


def test_guard_plain_desired_mismatch():
    cc = _load()
    g = cc.GuardLine(
        "yellow",
        errors=0,
        active=89,
        unknown=12,
        note="desired≠active",
        paid=28,
        trial=24,
    )
    text = cc._guard_plain(g)
    assert "платные=28" in text
    assert "триал=24" in text
    assert "клиенты=52" in text
    assert "не хватает UUID" in text
    assert "vpn_active=" not in text


def test_collect_client_counts_excludes_friend_seeds(tmp_path):
    cc = _load()
    db = tmp_path / "vpn.db"
    import sqlite3

    conn = sqlite3.connect(db)
    conn.execute(
        """
        CREATE TABLE vpn_accounts (
          telegram_user_id INTEGER,
          status TEXT,
          xray_client_uuid TEXT,
          account_kind TEXT
        )
        """
    )
    rows = [
        (1001, "vpn_active", "u1", "paid"),
        (1002, "vpn_active", "u2", "paid"),
        (1003, "vpn_active", "u3", "trial"),
        (990100024, "vpn_active", "g1", "paid"),  # friend seed — exclude
        (990100025, "vpn_active", "g2", "paid"),
        (-1900000000099, "vpn_active", "neg", "paid"),  # internal — exclude
        (2001, "vpn_expired", "u4", "paid"),
    ]
    conn.executemany("INSERT INTO vpn_accounts VALUES (?,?,?,?)", rows)
    conn.commit()
    conn.close()
    paid, trial = cc.collect_client_counts(db)
    assert paid == 2
    assert trial == 1


def test_default_doors_europe_asia_russia_order():
    cc = _load()
    labels = [row[0] for row in cc.DEFAULT_DOORS]
    assert labels[0].startswith("🇩🇪 Brain · Contabo")
    assert labels[1].startswith("🇫🇷 Mouth · Contabo / рот")
    assert "…12" in labels[1]
    assert labels[2].startswith("🇷🇺 NEW EU · FirstVDS")
    assert any("Аладдин · запас" in x for x in labels)
    assert any("REG.RU / ночь" in x for x in labels)
    assert not any("REG.RU / запас" in x for x in labels)
    assert any("SG · Contabo / двор" in v for v in cc.WG_PEER_LABELS.values())
    door_hosts = {row[1] for row in cc.DEFAULT_DOORS}
    assert "169.58.242.12" in door_hosts
    assert "217.15.166.78" not in door_hosts
    assert cc.SERVERS_COST_RUB_MONTH == 10_000


def test_render_includes_servers_cost():
    cc = _load()
    snap = cc.Snapshot(
        slot="evening",
        when_msk="17.09.2026 · 00:00 МСК",
        doors=[],
        wg=[],
        guard=cc.GuardLine("green", 0, 0, 0, "fresh", paid=28, trial=24),
        speed=cc.SpeedLine("green", "ok", ""),
        services=[cc.ServiceLine("bot", "green")],
        attention=[],
    )
    text = cc.render_report(snap)
    assert "🗺 Флот 7 · Contabo×3 · FirstVDS×2 · REG.RU · Яндекс" in text
    assert "💰 Серверы ≈ 10 000 ₽/мес" in text
    # fleet + cost near top (before doors)
    assert text.index("Флот 7") < text.index("🚪 Двери")
    assert text.index("Серверы ≈") < text.index("🚪 Двери")


def test_render_incident_lists_attention():
    cc = _load()
    snap = cc.Snapshot(
        slot="morning",
        when_msk="12.09.2026 · 09:00 МСК",
        doors=[cc.DoorLine("🇷🇺 NEW EU · FirstVDS / мост · …98 :8444", "red", "TCP fail")],
        wg=[cc.WgLine("🇷🇺 NEW · FirstVDS / мост · …98", "green", "связь 1м назад")],
        guard=cc.GuardLine(
            "yellow",
            errors=0,
            active=78,
            unknown=12,
            note="desired≠active",
            paid=28,
            trial=24,
        ),
        speed=cc.SpeedLine("green", "tunnel OK", ""),
        services=[cc.ServiceLine("bot", "green")],
        attention=["🇷🇺 NEW EU · FirstVDS / мост · …98 :8444 — TCP fail", "Guard: desired≠active"],
    )
    text = cc.render_report(snap)
    assert "AiMonkey OPS — утро" in text
    assert "Итог: 🔴 Инцидент" in text
    assert "🔴 🇷🇺 NEW EU · FirstVDS / мост · …98 :8444" in text
    assert "платные=28" in text and "триал=24" in text and "клиенты=52" in text
    assert "🇷🇺 NEW EU · FirstVDS / мост · …98 :8444 — TCP fail" in text


def test_parse_admin_ids():
    cc = _load()
    ids = cc.parse_admin_ids("493897224, 744254201,854726070\n")
    assert ids == ["493897224", "744254201", "854726070"]
    assert cc.parse_admin_ids("") == []


def test_slot_title():
    cc = _load()
    assert "утро" in cc.slot_title("morning")
    assert "обед" in cc.slot_title("lunch")
    assert "вечер" in cc.slot_title("evening")


def test_emoji():
    cc = _load()
    assert cc.level_emoji("green") == "🟢"
    assert cc.level_emoji("yellow") == "🟡"
    assert cc.level_emoji("red") == "🔴"


def test_build_snapshot_from_fixtures(tmp_path: Path):
    cc = _load()
    guard = tmp_path / "guard.json"
    guard.write_text(
        '{"ok": true, "repair_errors": 0, "active_count": 78, '
        '"desired_count": 78, "unknown_preserved": 9, '
        '"checked_at_utc": "2026-09-12T18:00:00+00:00", "hosts_after": {}}',
        encoding="utf-8",
    )
    tunnel = tmp_path / "tunnel.csv"
    tunnel.write_text(
        "ts_utc,direct_bps,tunnel_bps,tunnel_to_direct_ratio,bytes,rc\n"
        "2026-09-12T18:15:01Z,20089801,,,10000000,0\n",
        encoding="utf-8",
    )
    path_csv = tmp_path / "path.csv"
    # Flexible fixture columns (prod uses host_role/cf_mbs).
    path_csv.write_text(
        "ts_utc,host_role,hostname,cf_bps,cf_mbs,listen_port\n"
        "2026-09-12T18:05:01Z,contabo,vmd,24404321,24.404,8446\n"
        "2026-09-12T18:05:01Z,newru,sergey,8849013,8.849,8444\n",
        encoding="utf-8",
    )

    def fake_probe(host: str, port: int, timeout: float = 3.0):
        return True, 55.0

    def fake_wg():
        return [
            cc.WgLine("NEW", "green", "1m"),
            cc.WgLine("SG", "green", "40s"),
            cc.WgLine("MAIN", "green", "1m"),
            cc.WgLine("REG", "green", "1m"),
            cc.WgLine("P01", "green", "1m"),
        ]

    def fake_svc():
        return [
            cc.ServiceLine("bot", "green"),
            cc.ServiceLine("vpn-api", "green"),
            cc.ServiceLine("partner", "green"),
            cc.ServiceLine("Mouth", "green"),
            cc.ServiceLine("MAIN API", "green"),
        ]

    snap = cc.build_snapshot(
        slot="lunch",
        now_msk_label="12.09.2026 · 14:00 МСК",
        guard_path=guard,
        tunnel_csv=tunnel,
        path_csv=path_csv,
        probe_fn=fake_probe,
        wg_fn=fake_wg,
        services_fn=fake_svc,
        door_specs=cc.DEFAULT_DOORS,
    )
    text = cc.render_report(snap)
    assert "AiMonkey OPS — обед" in text
    assert "ALADDIN OPS" not in text
    assert "🟢" in text
    assert "8.8" in text or "8.849" in text or "NEW path" in text
    assert "🛡 Guard" in text
    assert "⚡ Скорость" in text
    assert "🧩 Сервисы" in text
    assert "Срочные 🔴 приходят сразу" in text
