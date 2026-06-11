#!/usr/bin/env python3
"""Update docs/release/gates/security-l3-report.json from live smoke (B-OPS-10)."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / "docs/release/gates/security-l3-report.json"


def _run_truth() -> dict:
    script = REPO_ROOT / "docs/server/sfm_truth_check.sh"
    if not script.exists():
        return {"overall": "SKIP"}
    proc = subprocess.run(
        ["bash", str(script)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0 and not proc.stdout.strip():
        return {"overall": "FAIL", "stderr": proc.stderr}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"overall": "FAIL", "raw": proc.stdout}


def main() -> int:
    truth = _run_truth()
    data = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    blocks = data.setdefault("blocks", {})
    sfm = blocks.setdefault("SFM-WIRE", {"gate": "GATE-A", "status": "pending", "evidence": []})
    if truth.get("overall") == "PASS":
        sfm["status"] = "pass"
        sfm["evidence"] = [
            f"sfm_truth_check overall PASS registry={truth.get('registry_count')}",
            f"runtime={truth.get('runtime_functions_count')}",
        ]
        data["overall"] = "in_progress"
    else:
        sfm["status"] = "fail"
        sfm["evidence"] = [json.dumps(truth)]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {REPORT}")
    return 0 if sfm["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
