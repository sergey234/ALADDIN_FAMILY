#!/usr/bin/env bash
# Enable companion STT on VPS AFTER Yandex keys + smoke --mode stt PASS.
# Usage: fill YANDEX_* in .env first, then run on VPS:
#   python3 scripts/vps_smoke_family_stt.py --mode stt && bash scripts/vps_enable_stt.sh
set -euo pipefail

ROOT="${ALADDIN_BACKEND_ROOT:-/opt/aladdin-backend}"
ENV="$ROOT/.env"
cd "$ROOT"

if ! grep -q '^YANDEX_SPEECHKIT_API_KEY=.' "$ENV" 2>/dev/null; then
  echo "STOP: YANDEX_SPEECHKIT_API_KEY missing in $ENV"
  exit 1
fi

if grep -q '^FEATURE_COMPANION_SERVER_STT=' "$ENV"; then
  sed -i 's/^FEATURE_COMPANION_SERVER_STT=.*/FEATURE_COMPANION_SERVER_STT=1/' "$ENV"
else
  echo 'FEATURE_COMPANION_SERVER_STT=1' >> "$ENV"
fi

systemctl restart aladdin-backend
sleep 2
python3 scripts/vps_smoke_family_stt.py --mode stt
echo "STT enabled; smoke --mode stt PASS"
