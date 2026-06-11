#!/usr/bin/env python3
"""Pre-deploy SFM gate — block deploy if code or registry unhealthy."""
from __future__ import annotations

import json
import os
import sys

APP_PATH = os.environ.get("ALADDIN_APP_PATH", "/opt/aladdin-backend/app")
BACKEND_PATH = os.environ.get("ALADDIN_BACKEND_PATH", "/opt/aladdin-backend")
REGISTRY = os.path.join(APP_PATH, "data/sfm/function_registry.json")
SFM_CODE = os.path.join(APP_PATH, "security/safe_function_manager.py")
MIN_REGISTRY = int(os.environ.get("SFM_MIN_REGISTRY", "1000"))


def main() -> int:
    errors: list[str] = []

    if not os.path.isfile(SFM_CODE):
        errors.append(f"missing SFM code: {SFM_CODE}")
    elif os.path.getsize(SFM_CODE) < 50_000:
        errors.append(f"SFM code too small: {SFM_CODE}")

    try:
        with open(REGISTRY, encoding="utf-8") as fh:
            data = json.load(fh)
        functions = data.get("functions", data)
        count = len(functions) if hasattr(functions, "__len__") else 0
        if count < MIN_REGISTRY:
            errors.append(f"registry count {count} < {MIN_REGISTRY}")
    except OSError as exc:
        errors.append(f"registry unreadable: {exc}")

    if BACKEND_PATH not in sys.path:
        sys.path.append(BACKEND_PATH)
    if APP_PATH not in sys.path:
        sys.path.insert(0, APP_PATH)

    try:
        from security.safe_function_manager import SafeFunctionManager  # noqa: F401
    except Exception as exc:
        errors.append(f"import SafeFunctionManager failed: {exc}")

    if errors:
        print("PREFLIGHT_SFM FAIL:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("PREFLIGHT_SFM OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
