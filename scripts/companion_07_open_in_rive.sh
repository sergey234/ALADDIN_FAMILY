#!/usr/bin/env bash
# HERO-3-07 — открыть Rive Editor с ИСХОДНИКОМ (.rev), не runtime .riv.
# Runtime unicorn/aladdin/genie.riv — для iOS; в Editor они серые / не редактируются.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERO="${1:-unicorn}"
REV="$ROOT/Resources/Companion/${HERO}_source.rev"
DRAFT_REV="$ROOT/Resources/Companion/unicorn_mcp_draft.rev"
PNG="$ROOT/Resources/Companion/${HERO}_master.png"
ASSETS="$ROOT/docs/assets"

if [[ ! -d "/Applications/Rive.app" ]]; then
  echo "Install Rive Editor from https://rive.app"
  exit 1
fi

pick_source() {
  if [[ -f "$REV" ]]; then
    echo "$REV"
  elif [[ "$HERO" == "unicorn" && -f "$DRAFT_REV" ]]; then
    echo "$DRAFT_REV"
  else
    echo ""
  fi
}

SRC="$(pick_source)"

echo "=== HERO-3-07 — Rive Editor ==="
echo "Runtime (iOS bundle, НЕ открывать для правки): $ROOT/Resources/Companion/${HERO}.riv"
echo "PNG для Import: $PNG"
case "$HERO" in
  aladdin) echo "Alt PNG: $ASSETS/aladdin_master_OB01_crop_360x480.png" ;;
  genie)   echo "Alt PNG: $ASSETS/onboarding_OB03_APP_360x480_FILL_headfix_v1.png" ;;
  unicorn) echo "Alt PNG: $ASSETS/unicorn_master_crop_360x480.png" ;;
esac
echo ""
echo "В Rive Editor runtime .riv серые — работайте: New file + Import PNG"
echo "или откройте .rev backup. Export runtime → ${HERO}.riv когда готово."
echo ""

if [[ -n "$SRC" ]]; then
  echo "Opening editor source: $SRC"
  open -a Rive "$SRC"
else
  echo "No ${HERO}_source.rev — launching empty Rive (File → New, artboard 360×480)."
  open -a Rive
fi
