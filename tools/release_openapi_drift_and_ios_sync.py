#!/usr/bin/env python3
import json
import os
import re
import time
from pathlib import Path

import requests


BASE_URL = os.environ.get("ALADDIN_API_BASE", "https://aladdin-ai.ru").rstrip("/")
BASELINE_OPENAPI = Path(
    os.environ.get("ALADDIN_BASELINE_OPENAPI", "docs/release/baseline/openapi.json")
)
IOS_CONFIG = Path(
    os.environ.get("ALADDIN_IOS_CONFIG", "Core/Config/AppConfig.swift")
)
OUT_DRIFT = Path(
    os.environ.get(
        "ALADDIN_OPENAPI_DRIFT_REPORT",
        "docs/release/gates/openapi-drift-report.json",
    )
)
OUT_SYNC = Path(
    os.environ.get(
        "ALADDIN_IOS_SYNC_REPORT",
        "docs/release/gates/ios-endpoint-sync-report.json",
    )
)
OUT_CURRENT_OPENAPI = Path(
    os.environ.get(
        "ALADDIN_CURRENT_OPENAPI_SNAPSHOT",
        "docs/release/current/openapi.json",
    )
)


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_paths_methods(doc: dict):
    paths = {}
    for path, methods in (doc.get("paths") or {}).items():
        paths[path] = sorted(m.upper() for m in methods.keys())
    return paths


def _extract_ios_endpoints(path: Path):
    text = path.read_text(encoding="utf-8")
    # static let name = "/api/..."
    pattern = re.compile(r"static let\s+([A-Za-z0-9_]+)\s*=\s*\"(/api[^\"]*)\"")
    found = []
    for name, endpoint in pattern.findall(text):
        if endpoint.startswith("/api/"):
            found.append({"name": name, "endpoint": endpoint})
    return found


def _exists_in_openapi(endpoint: str, openapi_paths: set):
    if endpoint in openapi_paths:
        return True
    # For constants representing base path with implied /{id}
    # e.g. "/api/gamification/achievements" while OpenAPI has "/api/gamification/achievements/{achievement_id}"
    for p in openapi_paths:
        if p.startswith(endpoint + "/{"):
            return True
    return False


def main():
    resp = requests.get(f"{BASE_URL}/openapi.json", timeout=20)
    resp.raise_for_status()
    current_openapi = resp.json()

    OUT_CURRENT_OPENAPI.parent.mkdir(parents=True, exist_ok=True)
    OUT_CURRENT_OPENAPI.write_text(
        json.dumps(current_openapi, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    baseline_openapi = _load_json(BASELINE_OPENAPI)
    base_map = _canonical_paths_methods(baseline_openapi)
    cur_map = _canonical_paths_methods(current_openapi)

    baseline_paths = set(base_map.keys())
    current_paths = set(cur_map.keys())
    added_paths = sorted(current_paths - baseline_paths)
    removed_paths = sorted(baseline_paths - current_paths)

    methods_changed = []
    for p in sorted(current_paths & baseline_paths):
        if cur_map[p] != base_map[p]:
            methods_changed.append(
                {"path": p, "baseline_methods": base_map[p], "current_methods": cur_map[p]}
            )

    drift_pass = len(removed_paths) == 0
    drift_report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "base_url": BASE_URL,
        "baseline_file": str(BASELINE_OPENAPI),
        "current_snapshot": str(OUT_CURRENT_OPENAPI),
        "baseline_path_count": len(baseline_paths),
        "current_path_count": len(current_paths),
        "added_paths_count": len(added_paths),
        "removed_paths_count": len(removed_paths),
        "methods_changed_count": len(methods_changed),
        "pass": drift_pass,
        "added_paths": added_paths,
        "removed_paths": removed_paths,
        "methods_changed": methods_changed,
    }

    ios_endpoints = _extract_ios_endpoints(IOS_CONFIG)
    openapi_paths = set(current_paths)
    missing_in_openapi = [
        item for item in ios_endpoints if not _exists_in_openapi(item["endpoint"], openapi_paths)
    ]
    sync_pass = len(missing_in_openapi) == 0
    sync_report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "ios_config": str(IOS_CONFIG),
        "openapi_snapshot": str(OUT_CURRENT_OPENAPI),
        "ios_endpoint_count": len(ios_endpoints),
        "missing_in_openapi_count": len(missing_in_openapi),
        "pass": sync_pass,
        "missing_in_openapi": missing_in_openapi,
    }

    OUT_DRIFT.parent.mkdir(parents=True, exist_ok=True)
    OUT_SYNC.parent.mkdir(parents=True, exist_ok=True)
    OUT_DRIFT.write_text(json.dumps(drift_report, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_SYNC.write_text(json.dumps(sync_report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"openapi-drift: {'PASS' if drift_pass else 'FAIL'}")
    print(f"ios-openapi-sync: {'PASS' if sync_pass else 'FAIL'}")
    print(f"drift_report={OUT_DRIFT}")
    print(f"sync_report={OUT_SYNC}")
    if not (drift_pass and sync_pass):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
