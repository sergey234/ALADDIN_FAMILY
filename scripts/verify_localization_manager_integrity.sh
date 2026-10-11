#!/usr/bin/env bash
# Fail if LocalizationManager.swift is truncated / structurally broken.
# Usage: ./scripts/verify_localization_manager_integrity.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FILE="$ROOT/Core/Localization/LocalizationManager.swift"

if [[ ! -f "$FILE" ]]; then
  echo "FAIL: missing $FILE"
  exit 1
fi

LINES=$(wc -l < "$FILE" | tr -d ' ')
HEAD_LINES=""
if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  HEAD_LINES=$(git -C "$ROOT" show HEAD:"Core/Localization/LocalizationManager.swift" 2>/dev/null | wc -l | tr -d ' ' || true)
fi

python3 - "$FILE" "$LINES" "$HEAD_LINES" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
lines = int(sys.argv[2])
head_lines = int(sys.argv[3]) if sys.argv[3].isdigit() else None
t = path.read_text(encoding="utf-8")

errors = []
if not t.rstrip().endswith("}"):
    errors.append("file does not end with '}' (likely truncated)")
if t.count("{") != t.count("}"):
    errors.append(f"brace imbalance {{ {t.count('{')} }} {t.count('}')}")
if "func localized(_ key: String)" not in t:
    errors.append("missing func localized(_ key: String)")
if ".russian: [" not in t:
    errors.append("missing .russian: [ block")
if ".english: [" not in t:
    errors.append("missing .english: [ block")
# Hard floor: known healthy size ~21k; truncated incident was ~9k
if lines < 15000:
    errors.append(f"line count too low: {lines} (expected roughly >= 15000)")
if head_lines is not None and head_lines > 0 and lines < head_lines - 500:
    errors.append(f"collapsed vs HEAD: work={lines} HEAD={head_lines} (delta {head_lines - lines})")

if errors:
    print("FAIL: LocalizationManager integrity")
    for e in errors:
        print(" -", e)
    sys.exit(1)

extra = f", HEAD={head_lines}" if head_lines else ""
print(f"OK: LocalizationManager integrity (lines={lines}{extra})")
PY
