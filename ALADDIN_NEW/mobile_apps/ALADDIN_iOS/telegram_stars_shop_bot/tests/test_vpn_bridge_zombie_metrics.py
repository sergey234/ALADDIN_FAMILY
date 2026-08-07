"""Tests for RU-bridge zombie status metrics."""

from __future__ import annotations

import json
import time
from pathlib import Path

from bot.services.vpn_bridge_zombie_metrics import (
    collect_bridge_zombie_metrics,
    format_bridge_zombies_html,
)


def test_status_missing(tmp_path: Path) -> None:
    m = collect_bridge_zombie_metrics(tmp_path / "nope.json")
    assert m["ok"] is False
    assert m["error"] == "status_missing"
    assert "не найден" in format_bridge_zombies_html(m)


def test_clean_status(tmp_path: Path) -> None:
    p = tmp_path / "bridge_peers_status.json"
    now = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    p.write_text(
        json.dumps(
            {
                "ok": True,
                "checked_at_utc": now,
                "active_count": 10,
                "active_paid_real": 8,
                "active_trial_real": 1,
                "active_friend_seed": 1,
                "zombie_before": 2,
                "zombie_pruned": 2,
                "zombie_after": 0,
                "zombie_pruned_total": 15,
                "last_prune_at_utc": "2026-08-05T19:42:00+00:00",
                "last_prune_count": 15,
                "zombies": [
                    {
                        "uuid": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                        "telegram_user_id": 111,
                        "status": "vpn_expired",
                        "account_kind": "trial",
                        "paid_until": "2026-07-01T00:00:00+00:00",
                    }
                ],
                "zombies_remaining": [],
                "hosts_configured": ["root@37.46.134.98"],
            }
        ),
        encoding="utf-8",
    )
    m = collect_bridge_zombie_metrics(p, max_age_sec=10800)
    assert m["ok"] is True
    assert m["zombie_after"] == 0
    assert m["zombie_before"] == 2
    assert m["zombie_pruned_total"] == 15
    html = format_bridge_zombies_html(m)
    assert "Живые" in html
    assert "Отключено всего" in html
    assert "15" in html
    assert "друг" not in html.lower()
    assert "Ссылки" not in html
    assert "всего UUID" not in html
    assert "Active UUID" not in html
    assert "111" in html



def test_remaining_critical(tmp_path: Path) -> None:
    p = tmp_path / "bridge_peers_status.json"
    now = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    p.write_text(
        json.dumps(
            {
                "ok": False,
                "checked_at_utc": now,
                "active_count": 1,
                "zombie_before": 1,
                "zombie_pruned": 0,
                "zombie_after": 1,
                "zombies": [],
                "zombies_remaining": [
                    {
                        "uuid": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                        "telegram_user_id": 222,
                        "status": "vpn_expired",
                        "account_kind": "trial",
                        "paid_until": "2026-07-10T00:00:00+00:00",
                    }
                ],
                "hosts_configured": ["root@37.46.134.98"],
            }
        ),
        encoding="utf-8",
    )
    m = collect_bridge_zombie_metrics(p)
    assert m["ok"] is False
    assert m["zombie_after"] == 1
