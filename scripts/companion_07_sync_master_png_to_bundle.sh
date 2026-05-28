#!/usr/bin/env bash
# Копирует PO masters из docs/assets → Resources/Companion/*_master.png
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ASSETS="$ROOT/docs/assets"
OUT="$ROOT/Resources/Companion"

cp "$ASSETS/unicorn_master_crop_360x480.png" "$OUT/unicorn_master.png"
cp "$ASSETS/aladdin_master_OB01_crop_360x480.png" "$OUT/aladdin_master.png"
cp "$ASSETS/onboarding_OB03_APP_360x480_FILL_headfix_v1.png" "$OUT/genie_master.png"

echo "OK: synced 3 master PNG → $OUT"
ls -la "$OUT"/*_master.png
