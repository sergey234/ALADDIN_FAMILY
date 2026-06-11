#!/usr/bin/env python3
"""
GATE-D / B1-12 / sec-09 — run all security domain prod smokes + OpenAPI audit.
Exit 0 only when every child script reports pass:true.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = SCRIPT_DIR.parent.parent

DOMAIN_SCRIPTS: list[tuple[str, str]] = [
    ("antifake", "test_antifake_prod_smoke.py"),
    ("darkweb", "test_darkweb_prod_smoke.py"),
    ("identity_theft", "test_identity_theft_prod_smoke.py"),
    ("data_cleanup", "test_data_cleanup_prod_smoke.py"),
    ("location_bubble", "test_location_bubble_prod_smoke.py"),
    ("malware", "test_malware_prod_smoke.py"),
    ("components", "test_components_prod_smoke.py"),
    ("iot", "test_iot_prod_smoke.py"),
    ("mobile_security", "test_mobile_security_prod_smoke.py"),
    ("parental_monitoring", "test_parental_monitoring_prod_smoke.py"),
    ("openapi_security", "test_security_openapi_prod_smoke.py"),
]


SMOKE_SECRET_KEYS = (
    "ANTIFAKE_INTERNAL_SMOKE_SECRET",
    "DARKWEB_INTERNAL_SMOKE_SECRET",
    "IDENTITY_THEFT_INTERNAL_SMOKE_SECRET",
    "DATA_CLEANUP_INTERNAL_SMOKE_SECRET",
    "LOCATION_BUBBLE_INTERNAL_SMOKE_SECRET",
    "MALWARE_INTERNAL_SMOKE_SECRET",
)


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key:
            continue
        cleaned = value.strip().strip('"').strip("'")
        if key not in os.environ or not os.environ.get(key):
            os.environ[key] = cleaned


def _run_child(name: str, script: str) -> dict:
    path = SCRIPT_DIR / script
    if not path.is_file():
        return {"domain": name, "pass": False, "error": f"missing script {script}"}
    env = os.environ.copy()
    env.setdefault("ALADDIN_ENV", "/opt/aladdin-backend/.env")
    _load_dotenv(Path(env["ALADDIN_ENV"]))
    proc = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(SCRIPT_DIR),
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    try:
        body = json.loads(stdout)
        if isinstance(body, dict) and "pass" in body:
            return {
                "domain": name,
                "pass": bool(body.get("pass")),
                "exit_code": proc.returncode,
                "failures": body.get("failures", []),
            }
    except json.JSONDecodeError:
        pass
    return {
        "domain": name,
        "pass": False,
        "exit_code": proc.returncode,
        "stdout_tail": stdout[-500:],
        "stderr_tail": stderr[-500:],
    }


def main() -> int:
    env_path = Path(os.environ.get("ALADDIN_ENV", "/opt/aladdin-backend/.env"))
    _load_dotenv(env_path)
    missing_secrets = [k for k in SMOKE_SECRET_KEYS if not os.environ.get(k)]
    results = [_run_child(name, script) for name, script in DOMAIN_SCRIPTS]
    failures = [r for r in results if not r.get("pass")]
    report = {
        "pass": len(failures) == 0 and not missing_secrets,
        "gate": "GATE-D",
        "batch": "B1-12",
        "domains_total": len(DOMAIN_SCRIPTS),
        "domains_pass": len(results) - len(failures),
        "domains_fail": len(failures),
        "missing_smoke_secrets": missing_secrets,
        "results": results,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
