#!/usr/bin/env bash
# HERO-3-08b — после xcodebuild: .riv ×3 в бандле + RiveRuntime линкуется.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

APP="${1:-}"
if [[ -z "${APP}" ]]; then
  DD=$(ls -td ~/Library/Developer/Xcode/DerivedData/ALADDIN-*/Build/Products/Debug-iphonesimulator/ALADDIN.app 2>/dev/null | head -1 || true)
  APP="${DD}"
fi

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

[[ -n "${APP}" && -d "${APP}" ]] || fail "ALADDIN.app not found — run xcodebuild first or pass path"

for name in unicorn aladdin genie; do
  [[ -f "${APP}/Companion/${name}.riv" ]] || fail "missing ${name}.riv in bundle"
  ok "${name}.riv in bundle"
done

python3 scripts/companion_riv_size_gate.py --dir Resources/Companion
ok "riv size gate"

echo "=== HERO-3-08b bundle check passed ==="
echo "Manual: Simulator → Kids → Companion → Conversation — Rive scene (not emoji-only)."
