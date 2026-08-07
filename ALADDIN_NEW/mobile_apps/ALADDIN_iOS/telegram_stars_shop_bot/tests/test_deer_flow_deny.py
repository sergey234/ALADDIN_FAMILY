"""P2.1 deer-flow DENY + sandbox write roots."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

IOS_ROOT = Path(__file__).resolve().parents[2]
SANDBOX = IOS_ROOT / "tools" / "deer-flow-sandbox"


def test_assert_deer_safe_pass() -> None:
    r = subprocess.run(
        [sys.executable, str(SANDBOX / "assert_deer_safe.py")],
        cwd=str(IOS_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr or r.stdout
    assert "PASS" in r.stdout


def test_safe_pipeline_writes_only_sandbox() -> None:
    r = subprocess.run(
        [
            sys.executable,
            str(SANDBOX / "safe_docs_pipeline.py"),
            "--title",
            "pytest-sink",
            "--subdir",
            "out",
            "--stdin",
        ],
        cwd=str(IOS_ROOT),
        input="# pytest deer sink\n",
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr or r.stdout
    assert "PASS" in r.stdout
    assert "deer-flow-sandbox/out" in r.stdout.replace("\\", "/")


def test_write_tools_not_in_allowlist() -> None:
    from bot.assistant.tools import ALLOWED_TOOLS

    for banned in (
        "refund_order",
        "reprovision_vpn",
        "revoke_vpn",
        "extend_vpn",
        "force_complete_order",
        "admin_fulfill",
    ):
        assert banned not in ALLOWED_TOOLS
