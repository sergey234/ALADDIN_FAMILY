#!/usr/bin/env bash
# Полная проверка Companion P0/P1 на проде (OPS-02 / P1-15).
# После deploy_companion_p0.sh
#
# Usage: ./scripts/verify_companion_p0_prod.sh [base_url]
set -euo pipefail

BASE="${1:-https://aladdin-ai.ru}"
DEVICE_ID="companion-verify-$(date +%s)"
AUTH=()
THREAD_ID=""
MESSAGE_ID=""
STREAM_GOT_TOKEN=0

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

ok() {
  echo "OK: $*"
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
ok "characters"

echo "=== [4/12] GET /capabilities ==="
CAP=$(curl_auth "${BASE}/api/ai/companion/capabilities")
echo "${CAP}" | head -c 350
echo ""
echo "${CAP}" | grep -q '"streaming":true' || fail "streaming not enabled in capabilities"
ok "capabilities"

echo "=== [5/12] GET /consent ==="
CONSENT=$(curl_auth "${BASE}/api/ai/companion/consent")
echo "${CONSENT}" | head -c 300
echo ""
echo "${CONSENT}" | grep -q '"recorded"' || fail "consent shape"
ok "consent"

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

echo "=== [13/13] HERO-3-10 age_policy (local) ==="
PYTHONPATH=. python3 - <<'PY'
from security.services.ai_platform.age_policy import filter_characters_for_age

CHARACTERS = [
    {"id": "unicorn"},
    {"id": "aladdin"},
    {"id": "genie"},
]
child = filter_characters_for_age(CHARACTERS, "child", {"child_can_use_companion": True})
child_ids = {c["id"] for c in child}
assert child_ids == {"unicorn"}, child_ids
teen = filter_characters_for_age(CHARACTERS, "teen", {"child_can_use_companion": True})
teen_ids = {c["id"] for c in teen}
assert teen_ids == {"unicorn", "aladdin", "genie"}, teen_ids
print("child:", sorted(child_ids), "teen:", sorted(teen_ids))
PY
ok "age_policy child=unicorn only, teen=3 heroes"

echo "=== [14/14] HERO-3-10 prod /characters ids (child JWT) ==="
CHAR_IDS=$(echo "${BODY}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(','.join(c['id'] for c in d.get('characters',[])))
")
echo "character ids: ${CHAR_IDS}"
echo "${CHAR_IDS}" | grep -q unicorn || fail "child missing unicorn"
echo "${CHAR_IDS}" | grep -q genie && fail "child must not see genie" || true
echo "${CHAR_IDS}" | grep -q aladdin && fail "child must not see aladdin" || true
ok "prod child JWT: unicorn only"

echo ""
echo "=== All checks passed (OPS-02 + HERO-3-10 verify) ==="
if [[ "${STREAM_GOT_TOKEN}" -eq 0 ]]; then
  echo "Note: stream token check skipped (LLM 503) — re-run when AI is up."
fi
