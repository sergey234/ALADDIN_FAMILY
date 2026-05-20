# -*- coding: utf-8 -*-
"""E2.4 — unit tests for hybrid retention policy and hash helpers."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from security.services.ai_history_retention import (  # noqa: E402
    ANALYTICS_RETENTION_DAYS,
    LOCAL_DEVICE_RETENTION_DAYS,
    OPERATIONAL_RETENTION_DAYS,
    RETENTION_POLICY_ID,
    content_hash,
    user_id_hash,
)


def test_retention_policy_hybrid_d() -> None:
    assert RETENTION_POLICY_ID == "hybrid_d_v1"
    assert OPERATIONAL_RETENTION_DAYS == 7
    assert ANALYTICS_RETENTION_DAYS == 365
    assert LOCAL_DEVICE_RETENTION_DAYS == 90


def test_user_hash_stable_and_salted() -> None:
    os.environ["AI_HISTORY_USER_SALT"] = "unit-test-salt"
    a = user_id_hash("user-42")
    b = user_id_hash("user-42")
    c = user_id_hash("other")
    assert a == b
    assert a != c
    assert len(a) == 64


def test_content_hash_only_for_non_empty() -> None:
    h1 = content_hash("hello")
    h2 = content_hash("hello")
    assert h1 == h2
    assert content_hash("") is None
    assert content_hash("   ") is None


if __name__ == "__main__":
    test_retention_policy_hybrid_d()
    test_user_hash_stable_and_salted()
    test_content_hash_only_for_non_empty()
    print("OK: test_ai_history_store")
