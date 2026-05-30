#!/usr/bin/env bash
# Deploy companion STT backend files to VPS (no secrets). Run from repo root on Mac.
set -euo pipefail

KEY="${ALADDIN_SSH_KEY:-$HOME/.ssh/aladdin_server}"
HOST="${ALADDIN_VPS_HOST:-root@149.154.65.180}"
ROOT="${ALADDIN_BACKEND_ROOT:-/opt/aladdin-backend}"
IOS="$(cd "$(dirname "$0")/.." && pwd)"

FILES=(
  security/services/ai_platform/companion_stt.py
  security/services/ai_platform/stt_providers/__init__.py
  security/services/ai_platform/stt_providers/openai_http.py
  security/services/ai_platform/stt_providers/openai_whisper.py
  security/services/ai_platform/stt_providers/yandex_speechkit.py
  security/services/ai_platform/stt_providers/router.py
  security/services/ai_platform/modules/companion_server_stt.py
  security/api/routers/ai_companion_router.py
  scripts/vps_smoke_family_stt.py
)

ssh -o BatchMode=yes -o IdentitiesOnly=yes -i "$KEY" "$HOST" "mkdir -p $ROOT/security/services/ai_platform/stt_providers $ROOT/scripts"

for f in "${FILES[@]}"; do
  scp -o BatchMode=yes -o IdentitiesOnly=yes -i "$KEY" "$IOS/$f" "$HOST:$ROOT/$f"
done

ssh -o BatchMode=yes -o IdentitiesOnly=yes -i "$KEY" "$HOST" bash -s <<REMOTE
set -euo pipefail
ENV=$ROOT/.env
grep -q '^COMPANION_STT_PROVIDER=' "\$ENV" 2>/dev/null || echo 'COMPANION_STT_PROVIDER=auto' >> "\$ENV"
grep -q '^COMPANION_STT_FALLBACK_PROVIDER=' "\$ENV" 2>/dev/null || echo 'COMPANION_STT_FALLBACK_PROVIDER=openai_whisper' >> "\$ENV"
systemctl restart aladdin-backend
sleep 2
systemctl is-active aladdin-backend
python3 $ROOT/scripts/vps_smoke_family_stt.py --mode off
REMOTE

echo "STT code deployed; smoke --mode off should PASS"
