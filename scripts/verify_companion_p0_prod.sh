#!/usr/bin/env bash
# Полная проверка Companion P0/P1 + Sprint 4–5 на проде (OPS-02 / P1-15).
# После deploy_companion_p0.sh
#
# Политика героев (PO 2026-05-29): 🦄🧑🧞 доступны всем age_band при consent.
#
# Usage: ./scripts/verify_companion_p0_prod.sh [base_url]
set -euo pipefail

BASE="${1:-https://aladdin-ai.ru}"
DEVICE_ID="companion-verify-$(date +%s)"
AUTH=()
THREAD_ID=""
MESSAGE_ID=""
STREAM_GOT_TOKEN=0
THREE_HEROES="unicorn,aladdin,genie"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

ok() {
  echo "OK: $*"
}

# Проверка, что в JSON есть все три canonical id (characters[] или allowed_characters[]).
assert_three_heroes_in_json() {
  local label="$1"
  local payload="$2"
  echo "${payload}" | python3 -c "
import json, sys
label = sys.argv[1]
raw = sys.stdin.read()
d = json.loads(raw)
if 'characters' in d:
    ids = {c.get('id') for c in d.get('characters') or []}
elif 'allowed_characters' in d:
    ids = set(d.get('allowed_characters') or [])
else:
    raise SystemExit(f'{label}: no characters/allowed_characters field')
need = {'unicorn', 'aladdin', 'genie'}
missing = need - ids
if missing:
    raise SystemExit(f'{label}: missing {sorted(missing)} (got {sorted(ids)})')
print(f'{label}:', ','.join(sorted(ids)))
" "${label}" || fail "${label}: expected ${THREE_HEROES}"
}

curl_auth() {
  curl -sS -m "${2:-20}" "${AUTH[@]}" "$@"
}

echo "=== [1/12] Health ==="
HEALTH=$(curl -sS -m 10 "${BASE}/api/health")
echo "${HEALTH}"
echo "${HEALTH}" | grep -q '"status"' || fail "health body"
ok "health"

echo "=== [2/12] Register device + JWT ==="
RESP=$(curl -sS -m 15 -X POST "${BASE}/api/auth/register-device" \
  -H "Content-Type: application/json" \
  -d "{\"deviceId\":\"${DEVICE_ID}\",\"deviceType\":\"ios\"}")
TOKEN=$(echo "${RESP}" | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")
AUTH=(-H "Authorization: Bearer ${TOKEN}")
PAYLOAD_B64=$(echo "${TOKEN}" | cut -d. -f2 | tr '_-' '/+')
PAYLOAD=$(echo "${PAYLOAD_B64}" | python3 -c "import sys,base64; s=sys.stdin.read().strip(); s+=('='*((4-len(s)%4)%4)); print(base64.b64decode(s).decode())")
echo "${PAYLOAD}" | python3 -m json.tool 2>/dev/null | head -20
echo "${PAYLOAD}" | python3 -c "import json,sys; p=json.load(sys.stdin); assert p.get('age_band')=='child', p.get('age_band')" \
  || fail "expected age_band=child in JWT"
ok "register + JWT child"

echo "=== [3/12] GET /characters (not SFM mock) ==="
BODY=$(curl_auth "${BASE}/api/ai/companion/characters")
echo "${BODY}" | head -c 300
echo ""
if echo "${BODY}" | grep -q 'mock-real-protection\|get_ai_companion_characters'; then
  fail "still old SFM/mock gateway — run deploy_companion_p0.sh"
fi
echo "${BODY}" | grep -q '"characters"' || fail "characters shape"
assert_three_heroes_in_json "GET /characters (child JWT)" "${BODY}"
ok "characters (3 heroes for child)"

echo "=== [4/18] GET /capabilities ==="
CAP=$(curl_auth "${BASE}/api/ai/companion/capabilities")
echo "${CAP}" | head -c 350
echo ""
echo "${CAP}" | grep -q '"streaming":true' || fail "streaming not enabled in capabilities"
echo "${CAP}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
feat = (d.get('features') or {})
neuro = feat.get('companion_neuro_tts') or {}
ui = neuro.get('ui') or {}
# child JWT = free → neuro off, module present after deploy
assert 'companion_neuro_tts' in feat, 'missing companion_neuro_tts module (deploy neuro TTS?)'
assert ui.get('hero_visual_tier') == 'all', ui.get('hero_visual_tier')
assert ui.get('neuro_tts_premium') is False, 'child/free must not get premium TTS'
print('companion_neuro_tts: neuro_tts_premium=', ui.get('neuro_tts_premium'), 'visual=', ui.get('hero_visual_tier'))
" || fail "companion_neuro_tts capabilities shape"
ok "capabilities (+ neuro_tts module, free gate)"

echo "=== [5/12] GET /consent ==="
CONSENT=$(curl_auth "${BASE}/api/ai/companion/consent")
echo "${CONSENT}" | head -c 300
echo ""
echo "${CONSENT}" | grep -q '"recorded"' || fail "consent shape"
assert_three_heroes_in_json "GET /consent allowed_characters" "${CONSENT}"
ok "consent (3 heroes in allowed_characters)"

echo "=== [6/12] GET /profile ==="
PROFILE=$(curl_auth "${BASE}/api/ai/companion/profile")
echo "${PROFILE}" | head -c 300
echo ""
echo "${PROFILE}" | grep -q '"personality_preset"' || fail "profile shape"
ok "profile"

echo "=== [7/12] GET /memory ==="
MEM=$(curl_auth "${BASE}/api/ai/companion/memory")
echo "${MEM}" | head -c 300
echo ""
echo "${MEM}" | grep -q '"items"' || fail "memory shape"
ok "memory"

echo "=== [8/12] GET /cosmetics?character_id=unicorn ==="
COS=$(curl_auth "${BASE}/api/ai/companion/cosmetics?character_id=unicorn")
echo "${COS}" | head -c 300
echo ""
echo "${COS}" | grep -q '"cosmetics"' || fail "cosmetics shape"
ok "cosmetics"

echo "=== [8b] GET /state usage + /legal (P1-11, P1-09) ==="
STATE=$(curl_auth "${BASE}/api/ai/companion/state?character_id=unicorn")
echo "${STATE}" | head -c 280
echo ""
echo "${STATE}" | grep -q '"usage"' || fail "state.usage missing"
echo "${STATE}" | grep -q '"messages_usage_percent"' || fail "usage percent missing"
LEGAL=$(curl_auth "${BASE}/api/ai/companion/legal?locale=ru")
echo "${LEGAL}" | head -c 220
echo ""
echo "${LEGAL}" | grep -q 'coppa_152fz' || fail "legal sections"
ok "state.usage + legal"

echo "=== [9/12] POST /chat (creates thread) ==="
CHAT_JSON=$(python3 - <<'PY'
import json
print(json.dumps({
    "message": "Привет! Расскажи коротко, чем можешь поболтать?",
    "character_id": "unicorn",
    "context": "companion",
    "session_id": "verify-thread-1",
}))
PY
)
CHAT_CODE=$(curl -sS -m 60 -o /tmp/companion_verify_chat.json -w "%{http_code}" \
  -X POST "${BASE}/api/ai/companion/chat" \
  "${AUTH[@]}" -H "Content-Type: application/json" -d "${CHAT_JSON}")
CHAT_BODY=$(cat /tmp/companion_verify_chat.json)
echo "HTTP ${CHAT_CODE}: ${CHAT_BODY}" | head -c 500
echo ""
if [[ "${CHAT_CODE}" == "200" ]]; then
  echo "${CHAT_BODY}" | grep -q '"response"' || fail "chat missing response"
  echo "${CHAT_BODY}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for k in ('companion_domain','companion_mood','emotion'):
    if k not in d:
        raise SystemExit(f'missing {k}')
print('domain=', d.get('companion_domain'), 'mood=', d.get('companion_mood'), 'emotion=', d.get('emotion'))
" || fail "chat missing P1-27/30 meta fields"
  ok "chat 200 + domain/mood/emotion meta"
elif [[ "${CHAT_CODE}" == "503" ]] && echo "${CHAT_BODY}" | grep -q 'ai_unavailable'; then
  echo "WARN: LLM unavailable (503) — stream/threads may be limited; continuing"
else
  fail "chat unexpected HTTP ${CHAT_CODE}"
fi

echo "=== [10/12] GET /threads + messages ==="
THREADS=$(curl_auth "${BASE}/api/ai/companion/threads")
echo "${THREADS}" | head -c 400
echo ""
echo "${THREADS}" | grep -q '"threads"' || fail "threads shape"
THREAD_ID=$(echo "${THREADS}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
ts=d.get('threads') or []
print(ts[0]['thread_id'] if ts else '')
" 2>/dev/null || true)
if [[ -n "${THREAD_ID}" ]]; then
  MSGS=$(curl_auth "${BASE}/api/ai/companion/threads/${THREAD_ID}/messages")
  echo "${MSGS}" | head -c 400
  echo ""
  echo "${MSGS}" | grep -q '"messages"' || fail "thread messages shape"
  ok "threads + messages (${THREAD_ID})"
else
  ok "threads list (empty — chat may have been skipped)"
fi

echo "=== [11/12] POST /feedback ==="
FB_JSON='{"vote":"up","character_id":"unicorn","thread_id":"verify-thread-1","assistant_text":"ok"}'
FB=$(curl -sS -m 20 -X POST "${BASE}/api/ai/companion/feedback" \
  "${AUTH[@]}" -H "Content-Type: application/json" -d "${FB_JSON}")
echo "${FB}" | head -c 300
echo ""
echo "${FB}" | grep -q '"recorded":true' || fail "feedback not recorded"
ok "feedback"

echo "=== [12/12] POST /stream + resume (SSE) ==="
STREAM_JSON=$(python3 - <<'PY'
import json
print(json.dumps({
    "message": "Скажи одно короткое приветствие.",
    "character_id": "unicorn",
    "context": "companion",
    "session_id": "verify-stream-1",
    "stream": True,
    "resumeFromIndex": 0,
}))
PY
)
STREAM_OUT=/tmp/companion_verify_stream.sse
STREAM_CODE=$(curl -sS -m 90 -o "${STREAM_OUT}" -w "%{http_code}" \
  -X POST "${BASE}/api/ai/companion/stream" \
  "${AUTH[@]}" -H "Content-Type: application/json" -d "${STREAM_JSON}")
echo "stream HTTP ${STREAM_CODE}"
head -c 600 "${STREAM_OUT}"
echo ""

if [[ "${STREAM_CODE}" != "200" ]]; then
  if [[ "${STREAM_CODE}" == "503" ]]; then
    echo "WARN: stream 503 (LLM) — skip resume check"
  else
    fail "stream HTTP ${STREAM_CODE}"
  fi
else
  if grep -q '"token"' "${STREAM_OUT}"; then
    STREAM_GOT_TOKEN=1
    ok "stream emits data token lines"
  else
    fail "stream missing token payload (expected data: {\"token\":...})"
  fi
  if grep -q 'event: emotion' "${STREAM_OUT}" && ! grep -q '"token"' "${STREAM_OUT}"; then
    fail "old stream format (event: emotion without token)"
  fi
  MESSAGE_ID=$(python3 - <<'PY'
import json, re
text=open("/tmp/companion_verify_stream.sse").read()
for line in text.splitlines():
    if not line.startswith("data:"):
        continue
    payload=line[5:].strip()
    if payload=="[DONE]":
        continue
    try:
        o=json.loads(payload)
    except json.JSONDecodeError:
        continue
    mid=o.get("messageId")
    if mid:
        print(mid)
        break
PY
)
  if [[ -z "${MESSAGE_ID}" ]]; then
    fail "could not parse messageId from stream"
  fi
  ok "stream messageId=${MESSAGE_ID}"

  RESUME_JSON=$(python3 - <<PY
import json
print(json.dumps({
    "message": "",
    "character_id": "unicorn",
    "context": "resume",
    "stream": True,
    "resumeFromIndex": 1,
    "messageId": "${MESSAGE_ID}",
}))
PY
)
  RESUME_OUT=/tmp/companion_verify_stream_resume.sse
  RESUME_CODE=$(curl -sS -m 30 -o "${RESUME_OUT}" -w "%{http_code}" \
    -X POST "${BASE}/api/ai/companion/stream" \
    "${AUTH[@]}" -H "Content-Type: application/json" -d "${RESUME_JSON}")
  echo "resume HTTP ${RESUME_CODE}"
  head -c 400 "${RESUME_OUT}"
  echo ""
  [[ "${RESUME_CODE}" == "200" ]] || fail "resume HTTP ${RESUME_CODE}"
  grep -q '"token"' "${RESUME_OUT}" || fail "resume missing token"
  ok "stream resume (resumeFromIndex)"
fi

echo "=== [12b/17] POST /stream with chat_mode (Sprint 5 stream fields) ==="
STREAM_MODE_JSON=$(python3 - <<'PY'
import json
print(json.dumps({
    "message": "Одно слово: привет.",
    "character_id": "unicorn",
    "context": "companion",
    "session_id": "verify-stream-mode-1",
    "stream": True,
    "chat_mode": "fast",
    "resumeFromIndex": 0,
}))
PY
)
STREAM_MODE_CODE=$(curl -sS -m 60 -o /tmp/companion_verify_stream_mode.sse -w "%{http_code}" \
  -X POST "${BASE}/api/ai/companion/stream" \
  "${AUTH[@]}" -H "Content-Type: application/json" -d "${STREAM_MODE_JSON}")
echo "stream+chat_mode HTTP ${STREAM_MODE_CODE}"
if [[ "${STREAM_MODE_CODE}" == "200" ]]; then
  head -c 200 /tmp/companion_verify_stream_mode.sse
  echo ""
  ok "stream accepts chat_mode=fast"
elif [[ "${STREAM_MODE_CODE}" == "503" ]]; then
  echo "WARN: stream+chat_mode 503 (LLM) — field accepted at gateway"
  ok "stream chat_mode body (LLM skipped)"
else
  fail "stream+chat_mode HTTP ${STREAM_MODE_CODE}"
fi

echo "=== [13/17] HERO-3-10 age_policy (local, 3 heroes all bands) ==="
PYTHONPATH=. python3 - <<'PY'
from security.services.ai_platform.age_policy import filter_characters_for_age

CHARACTERS = [
    {"id": "unicorn"},
    {"id": "aladdin"},
    {"id": "genie"},
]
ALL = {"unicorn", "aladdin", "genie"}
consent = {
    "child_can_use_companion": True,
    "allowed_characters": ["unicorn", "aladdin", "genie"],
}
for band in ("child", "teen", "parent", "senior"):
    got = {c["id"] for c in filter_characters_for_age(CHARACTERS, band, consent)}
    assert got == ALL, (band, got)
print("bands OK:", "child teen parent senior ->", sorted(ALL))
empty = filter_characters_for_age(CHARACTERS, "child", {"child_can_use_companion": False})
assert empty == [], empty
print("consent gate OK: child_can_use_companion=False -> []")
PY
ok "age_policy: 3 heroes for child/teen/parent/senior; blocked without consent"

echo "=== [14/17] HERO-3-10 prod /characters (child JWT, 3 heroes) ==="
CHAR_IDS=$(echo "${BODY}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(','.join(c['id'] for c in d.get('characters',[])))
")
echo "character ids: ${CHAR_IDS}"
for hero in unicorn aladdin genie; do
  echo "${CHAR_IDS}" | grep -q "${hero}" || fail "child JWT missing ${hero} on /characters"
done
ok "prod child JWT: unicorn + aladdin + genie"

echo "=== [15/17] GET /domains (Sprint 4 P2-12 life topics) ==="
DOMAINS=$(curl_auth "${BASE}/api/ai/companion/domains?locale=ru")
echo "${DOMAINS}" | head -c 320
echo ""
echo "${DOMAINS}" | grep -q '"domains"' || fail "domains shape"
echo "${DOMAINS}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
domains=d.get('domains') or []
assert len(domains) >= 3, len(domains)
ids={x.get('id') for x in domains}
for need in ('school','friends','family'):
    assert need in ids, ids
print('domain ids:', sorted(ids)[:8], '… total', len(domains))
" || fail "domains content"
ok "domains chips API"

echo "=== [16/17] GET /workspaces (Sprint 5 P3-03) ==="
WS=$(curl_auth "${BASE}/api/ai/companion/workspaces")
echo "${WS}" | head -c 200
echo ""
echo "${WS}" | grep -q '"workspaces"' || fail "workspaces shape"
ok "workspaces list"

echo "=== [17/17] GET /cogs (Sprint 5 P2-08 COGS estimate) ==="
COGS=$(curl_auth "${BASE}/api/ai/companion/cogs")
echo "${COGS}" | head -c 200
echo ""
echo "${COGS}" | grep -q '"daily_usd"' || fail "cogs shape"
echo "${COGS}" | grep -q '"month_usd"' || fail "cogs month_usd"
ok "cogs dashboard"

echo "=== [18/18] Sprint 4 P2-13 social bridge (2× loneliness → meta) ==="
SOCIAL_THREAD="social-bridge-${DEVICE_ID}"
for LONELY_MSG in "мне одиноко" "я чувствую себя одиноким"; do
  SOCIAL_RESP=$(curl -sS -m 45 "${AUTH[@]}" -X POST "${BASE}/api/ai/companion/chat" \
    -H "Content-Type: application/json" \
    -d "{\"message\":\"${LONELY_MSG}\",\"character_id\":\"unicorn\",\"session_id\":\"${SOCIAL_THREAD}\",\"chat_mode\":\"fast\"}")
  echo "${SOCIAL_RESP}" | head -c 120
  echo ""
done
echo "${SOCIAL_RESP}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
bridge = d.get('show_social_bridge')
domain = d.get('companion_domain')
assert bridge is True, f'show_social_bridge={bridge!r} domain={domain!r}'
print('show_social_bridge=True domain=', domain)
" || fail "social bridge E2E (2× lonely messages)"
ok "social bridge E2E"

echo ""
echo "=== All checks passed (OPS-02 + HERO-3-10 + Sprint 4–5 verify) ==="
if [[ "${STREAM_GOT_TOKEN}" -eq 0 ]]; then
  echo "Note: stream token check skipped (LLM 503) — re-run when AI is up."
fi
