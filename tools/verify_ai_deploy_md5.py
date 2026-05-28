#!/usr/bin/env python3
"""Compare md5 of AI-related files: local repo vs prod (SSH)."""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "security/api/routers/ai_assistant_router.py",
    "security/services/ai_response_helpers.py",
    "security/services/ai_intent_router.py",
    "security/services/ai_capabilities_manifest.py",
    "security/services/ai_prompt_gate.py",
    "security/services/ai_sfm_context_builder.py",
    "security/services/ai_history_store.py",
    "security/services/ai_llm_prompt_builder.py",
    "sfm_adapter.py",
    "start_sfm_core_http.py",
]

HOST = "root@149.154.65.180"
REMOTE_ROOT = "/opt/aladdin-backend"
KEY = Path.home() / ".ssh" / "aladdin_server"


def md5_file(path: Path) -> str:
    h = hashlib.md5()
    h.update(path.read_bytes())
    return h.hexdigest()


def remote_md5(rel: str) -> str | None:
    cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-i",
        str(KEY),
        HOST,
        f"md5sum {REMOTE_ROOT}/{rel} 2>/dev/null | awk '{{print $1}}'",
    ]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
        return out or None
    except subprocess.CalledProcessError:
        return None


def main() -> int:
    print("e2-deploy-verify / ai deploy md5")
    mismatches = 0
    for rel in FILES:
        local = REPO_ROOT / rel
        if not local.is_file():
            print(f"SKIP local missing: {rel}")
            continue
        local_hash = md5_file(local)
        remote_hash = remote_md5(rel)
        if remote_hash is None:
            print(f"FAIL remote missing: {rel}")
            mismatches += 1
            continue
        if local_hash == remote_hash:
            print(f"OK   {rel}")
        else:
            print(f"MISMATCH {rel} local={local_hash} remote={remote_hash}")
            mismatches += 1
    print(f"done mismatches={mismatches}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
