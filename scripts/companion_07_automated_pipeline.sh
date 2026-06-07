#!/usr/bin/env bash
# HERO-3-07 — максимум без ручной работы в Rive Editor.
# Использует production unicorn.riv (HeroSM) + patch PNG для aladdin/genie.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== HERO-3-07 automated pipeline (no manual Rive draw) ==="

./scripts/companion_07_sync_master_png_to_bundle.sh
./scripts/companion_07_prepare_rive_import.sh

for hero in aladdin genie; do
  python3 scripts/companion_07_patch_riv_hero_image.py "$hero"
  python3 scripts/companion_07_verify_unicorn_riv.py "$hero"
done
python3 scripts/companion_07_verify_unicorn_riv.py unicorn
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion --min-kb 25

echo ""
echo "=== DONE ==="
echo "Bundle: Resources/Companion/{unicorn,aladdin,genie}.riv"
echo "12 distinct mimics in Rive Editor = optional polish (or RiveMCP license)."
echo "Web project ALADDIN_unicorn: export .riv here when/if SM updated manually."
