from __future__ import annotations

import json

from bot.config import Settings
from bot.handlers import vpn as vpn_mod


def _settings(**kwargs: object) -> Settings:
    base: dict = {
        "BOT_TOKEN": "9:test-vpn-loc",
        "ADMIN_IDS": "1",
        "API_KEY_PEPPER": "k" * 32,
        "USD_RUB_RATE": 80.0,
    }
    base.update(kwargs)
    return Settings(**base)  # type: ignore[arg-type]


def test_resolved_location_bodies_builtin_fallback() -> None:
    s = _settings()
    short, full = vpn_mod._location_bodies_from_local_env(s)
    assert "🇫🇷" in short
    assert "🇺🇸" in full
    assert len(full.splitlines()) > len(short.splitlines())


def test_resolved_location_bodies_json_array() -> None:
    js = json.dumps(["L1", "L2", "L3", "L4"])
    s = _settings(VPN_LOCATIONS_JSON=js, VPN_LOCATIONS_PREVIEW_N=2)
    short, full = vpn_mod._location_bodies_from_local_env(s)
    assert short == "L1\nL2"
    assert full.startswith("L1\nL2\nL3\nL4")
    assert vpn_mod._LOC_DEFAULT_FOOTER in full


def test_resolved_location_bodies_dict_preview_n() -> None:
    js = json.dumps({"preview_n": 1, "lines": ["A", "B"]})
    s = _settings(VPN_LOCATIONS_JSON=js, VPN_LOCATIONS_PREVIEW_N=9)
    short, full = vpn_mod._location_bodies_from_local_env(s)
    assert short == "A"
    assert "A\nB" in full


def test_vpn_locations_html_escapes_pre() -> None:
    js = json.dumps(["<b>x</b>"])
    s = _settings(VPN_LOCATIONS_JSON=js, VPN_LOCATIONS_PREVIEW_N=1)
    short, full = vpn_mod._location_bodies_from_local_env(s)
    html = vpn_mod.vpn_locations_html(expanded=False, short_body=short, full_body=full)
    assert "&lt;b&gt;" in html
