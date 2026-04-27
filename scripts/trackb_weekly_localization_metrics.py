#!/usr/bin/env python3
"""
Track B weekly checkpoint metrics publisher:
1) parity gaps
2) hardcoded violations
3) localization gate pass-rate
"""

from __future__ import annotations

import datetime as dt
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/TRACKB_WEEKLY_LOCALIZATION_METRICS.md"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True)


def main() -> int:
    lint_all = run(["python3", "scripts/localization_lint.py"])
    lint_scope = run(["python3", "scripts/localization_lint.py", "--scope", "elderly60plus"])

    all_text = (lint_all.stdout or "") + "\n" + (lint_all.stderr or "")
    scope_text = (lint_scope.stdout or "") + "\n" + (lint_scope.stderr or "")

    parity_gaps = all_text.count("Keys missing in EN:") + all_text.count("Keys missing in RU:")
    hardcoded_violations = all_text.count("hardcoded '")
    pass_rate = "100%" if lint_scope.returncode == 0 else "0%"

    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    report = f"""# Track B Weekly Localization Metrics

Generated: {now}

- Parity gaps (RU/EN): {parity_gaps}
- Hardcoded violations (global lint output): {hardcoded_violations}
- Localization gate pass-rate (active scope elderly60plus): {pass_rate}

## Raw gate statuses

- `localization_lint.py --scope elderly60plus`: {"PASS" if lint_scope.returncode == 0 else "FAIL"}
- `localization_lint.py` (global baseline): {"PASS" if lint_all.returncode == 0 else "FAIL"}
"""
    OUT.write_text(report, encoding="utf-8")
    print(f"Wrote metrics report: {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"Metrics generation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
