#!/usr/bin/env bash
# Прогрев server-side кэша neuro-TTS (Premium JWT обязателен).
#
# Usage:
#   export PREMIUM_TOKEN="eyJ..."
#   ./scripts/prewarm_companion_tts_cache.sh [base_url] [locale]
#
set -euo pipefail

BASE="${1:-https://aladdin-ai.ru}"
LOCALE="${2:-ru}"
TOKEN="${PREMIUM_TOKEN:-}"

if [[ -z "${TOKEN}" ]]; then
  echo "Set PREMIUM_TOKEN (JWT with subscription.level=premium)" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export PREWARM_BASE="${BASE}"
export PREWARM_TOKEN="${TOKEN}"
export PREWARM_LOCALE="${LOCALE}"

python3 - "${LOCAL_ROOT}" <<'PY'
import json
import os
import sys
import urllib.error
import urllib.request

root = sys.argv[1]
sys.path.insert(0, root)

from security.services.ai_platform.companion_tts_greetings import all_greeting_phrases

base = os.environ["PREWARM_BASE"].rstrip("/")
token = os.environ["PREWARM_TOKEN"]
locale = os.environ["PREWARM_LOCALE"]

ok = fail = skip = 0
for character_id, text in all_greeting_phrases(locale):
    body = json.dumps(
        {"text": text, "character_id": character_id, "locale": locale}
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/api/ai/companion/tts",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode())
            cached = payload.get("cached")
            print(f"OK {character_id}: cached={cached} ({len(text)} chars)")
            ok += 1
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:160]
        if exc.code in (424, 503):
            print(f"SKIP: server neuro_tts not configured ({exc.code}) {detail}")
            skip += 1
            break
        print(f"FAIL {character_id} HTTP {exc.code}: {detail}")
        fail += 1

print(f"\nPrewarm done: ok={ok} fail={fail} skip={skip}")
if fail:
    sys.exit(1)
PY
