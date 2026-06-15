#!/usr/bin/env python3
"""B-08: cron helper — delete antifake uploads older than TTL (default 15 min)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.antifake_upload_store import cleanup_stale_uploads  # noqa: E402


def main() -> int:
    deleted = cleanup_stale_uploads()
    print(f"deleted={deleted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
