from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _vpn_api_env(tmp_path: Path) -> None:
    os.environ["VPN_API_HMAC_SECRET"] = "test-hmac-secret-for-pytest"
    os.environ["VPN_DB_PATH"] = str(tmp_path / "vpn.db")
    os.environ["VPN_WG_INTERFACE"] = ""
    os.environ["VPN_DEV_STUB_WG"] = "1"
