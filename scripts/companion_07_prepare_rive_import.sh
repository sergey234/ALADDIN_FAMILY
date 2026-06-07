#!/usr/bin/env bash
# HERO-3-07 — проверка PNG masters + gate placeholder перед заменой .riv
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
ASSETS="$ROOT/docs/assets"
RIV_DIR="$ROOT/Resources/Companion"

echo "=== HERO-3-07 — prepare Rive import ==="
echo "Repo: $ROOT"
echo ""

check_png() {
  local f="$1"
  if [[ -f "$f" ]]; then
    local bytes
    bytes=$(wc -c <"$f" | tr -d ' ')
    echo "OK  $f ($bytes bytes)"
  else
    echo "MISSING  $f"
    return 1
  fi
}

failed=0
check_png "$ASSETS/unicorn_master_crop_360x480.png" || failed=1
check_png "$ASSETS/aladdin_master_OB01_crop_360x480.png" || failed=1
check_png "$ASSETS/onboarding_OB03_APP_360x480_FILL_headfix_v1.png" || failed=1
echo ""

echo "Figma Companion (verify on Mac):"
echo "  https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes"
echo "  01_Unicorn · 02_Aladdin_Human · 03_Genie (36 frames)"
echo ""

echo "Rive Editor — import order (Day 1→3):"
echo "  1) unicorn.riv  ← unicorn_master_crop_360x480.png"
echo "  2) aladdin.riv   ← aladdin_master_OB01_crop_360x480.png"
echo "  3) genie.riv     ← onboarding_OB03_APP_360x480_FILL_headfix_v1.png"
echo "  Artboard 360×480 · 13 triggers + mouth_open"
echo "  Docs: docs/COMPANION_RIVE_ANIMATOR_PLAN_SUPPLEMENT.md"
echo ""

echo "Current bundle (max 500 KB, production min 25 KB):"
python3 scripts/companion_riv_size_gate.py --dir "$RIV_DIR" --min-kb 25 || failed=1
./scripts/verify_companion_rive_ios_bundle.sh || failed=1

echo ""
if [[ $failed -eq 0 ]]; then
  echo "=== Ready for Rive Editor export (replace .riv in $RIV_DIR) ==="
else
  echo "=== Fix missing assets before export ==="
  exit 1
fi
