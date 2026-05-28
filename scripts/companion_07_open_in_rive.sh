#!/usr/bin/env bash
# Открыть placeholder .riv в Rive Editor для доработки (HERO-3-07).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERO="${1:-unicorn}"
RIV="$ROOT/Resources/Companion/${HERO}.riv"
PNG="$ROOT/Resources/Companion/${HERO}_master.png"

if [[ ! -f "$RIV" ]]; then
  echo "Missing: $RIV"
  exit 1
fi
if [[ ! -d "/Applications/Rive.app" ]]; then
  echo "Install Rive Editor (Production, Mac) from https://rive.app"
  exit 1
fi

echo "Opening in Rive: $RIV"
echo "Master PNG (import): $PNG"
open -a Rive "$RIV"
