#!/usr/bin/env bash
# Verify /api/wellness/reflective/modes — hints without «столп»
set -euo pipefail

BASE="${1:-https://aladdin-ai.ru}"
DEVICE_ID="wellness-reflective-$(date +%s)"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

echo "=== Register device ==="
RESP=$(curl -sS -m 20 -X POST "${BASE}/api/auth/register-device" \
  -H "Content-Type: application/json" \
  -d "{\"deviceId\":\"${DEVICE_ID}\",\"deviceType\":\"ios\"}")
TOKEN=$(echo "${RESP}" | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")
AUTH=(-H "Authorization: Bearer ${TOKEN}")

echo "=== GET /api/wellness/reflective/modes?locale=ru ==="
BODY=$(curl -sS -m 15 "${AUTH[@]}" "${BASE}/api/wellness/reflective/modes?locale=ru")
echo "${BODY}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
modes = d.get('modes') or []
assert modes, 'empty modes'
presence = next((m for m in modes if m.get('id') == 'presence'), None)
assert presence, 'no presence mode'
hint = (presence.get('hint') or '').lower()
label_key = presence.get('hint_key') or ''
assert 'столп' not in hint, presence.get('hint')
assert label_key == 'wellness_mode_presence_hint', label_key
print('presence hint:', presence.get('hint'))
print('hint_key:', label_key)
"
ok "reflective modes RU — no столп in API hint"

echo "=== PASSED reflective prod verify (${BASE}) ==="
