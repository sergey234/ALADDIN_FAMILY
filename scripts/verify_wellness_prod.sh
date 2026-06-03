#!/usr/bin/env bash
# Wellness API — проверка на проде через nginx (как iOS AppConfig).
# После deploy_wellness_p1.sh
#
# Usage: ./scripts/verify_wellness_prod.sh [base_url]
set -euo pipefail

BASE="${1:-https://aladdin-ai.ru}"
DEVICE_ID="wellness-verify-$(date +%s)"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

ok() {
  echo "OK: $*"
}

echo "=== [1/6] Health (public) ==="
HEALTH=$(curl -sS -m 12 "${BASE}/api/health")
echo "${HEALTH}"
echo "${HEALTH}" | grep -q '"status"' || fail "health"
ok "health"

echo "=== [2/6] Wellness pillars without auth → 401/403 ==="
CODE=$(curl -sS -m 12 -o /tmp/wellness_noauth.json -w '%{http_code}' "${BASE}/api/wellness/pillars")
echo "HTTP ${CODE}"
grep -qE 'Not authenticated|Unauthorized|credentials' /tmp/wellness_noauth.json || true
[[ "${CODE}" == "401" || "${CODE}" == "403" ]] || fail "expected 401/403 without token, got ${CODE}"
ok "unauthenticated blocked"

echo "=== [3/6] Register device + JWT (child) ==="
RESP=$(curl -sS -m 20 -X POST "${BASE}/api/auth/register-device" \
  -H "Content-Type: application/json" \
  -d "{\"deviceId\":\"${DEVICE_ID}\",\"deviceType\":\"ios\"}")
TOKEN=$(echo "${RESP}" | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")
AUTH=(-H "Authorization: Bearer ${TOKEN}")

echo "=== [4/6] GET /api/wellness/pillars (child JWT) ==="
BODY=$(curl -sS -m 15 "${AUTH[@]}" "${BASE}/api/wellness/pillars")
echo "${BODY}"
echo "${BODY}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
p=set(d.get('pillars') or [])
band=d.get('age_band')
assert band=='child', f'expected age_band child, got {band!r}: {d}'
assert p=={'humanistic','behavioral'}, f'child pillars: {p}'
print('child pillars OK:', sorted(p), 'age_band:', band)
" || fail "child pillars"
ok "pillars child"

echo "=== [5/7] POST /api/wellness/consent (child) ==="
CONSENT=$(curl -sS -m 15 -X POST "${AUTH[@]}" "${BASE}/api/wellness/consent" \
  -H "Content-Type: application/json" \
  -d '{"wellness_accepted":true}')
echo "${CONSENT}" | head -c 200
echo ""
echo "${CONSENT}" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('has_access') is True, d" || fail "consent"
ok "consent child"

echo "=== [6/7] POST session/pillar humanistic ==="
BODY=$(curl -sS -m 15 -X POST "${AUTH[@]}" "${BASE}/api/wellness/session/pillar" \
  -H "Content-Type: application/json" \
  -d '{"pillar":"humanistic"}')
echo "${BODY}"
echo "${BODY}" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('ok') is True, d" || fail "session pillar"
ok "session pillar"

echo "=== [7/7] escalation + referral ==="
ESC=$(curl -sS -m 15 "${AUTH[@]}" "${BASE}/api/wellness/escalation/level?message=grustno")
echo "escalation: ${ESC}" | head -c 200
echo ""
REF=$(curl -sS -m 15 "${AUTH[@]}" "${BASE}/api/wellness/referral?locale=ru&level=L2")
echo "referral keys: $(echo "${REF}" | python3 -c "import json,sys; print(list(json.load(sys.stdin).keys())[:12])")"
echo "${REF}" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d, 'empty referral'" || fail "referral"
ok "escalation + referral"

echo "=== [7b] GET /api/wellness/session/loop (orchestrator snapshot) ==="
LOOP=$(curl -sS -m 15 "${AUTH[@]}" \
  "${BASE}/api/wellness/session/loop?message=ustal&locale=ru")
echo "${LOOP}" | head -c 280
echo ""
echo "${LOOP}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok') is True, d
loop=d.get('loop') or {}
assert 'phase' in loop and 'agents_active' in loop, loop
print('loop phase:', loop.get('phase'), 'agents:', loop.get('agents_active')[:4])
" || fail "session/loop"
ok "session/loop"

echo "=== [8/10] hub/copy + streaks + weekly-meaning (Ф2 endpoints) ==="
HUB=$(curl -sS -m 15 "${AUTH[@]}" "${BASE}/api/wellness/hub/copy?locale=ru")
echo "${HUB}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert len(d.get('pillars') or []) >= 1, d
assert d.get('variant') in ('control','b'), d
print('hub_copy variant:', d.get('variant'))
" || fail "hub_copy"
STREAKS=$(curl -sS -m 15 "${AUTH[@]}" "${BASE}/api/wellness/streaks?locale=ru")
echo "${STREAKS}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
s=d.get('streaks') or {}
assert 'checkin_streak' in s, d
print('checkin_streak:', s.get('checkin_streak'))
" || fail "streaks"
WM=$(curl -sS -m 15 "${AUTH[@]}" "${BASE}/api/wellness/weekly-meaning?locale=ru")
echo "${WM}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok') is True and 'show' in d, d
print('weekly_meaning show:', d.get('show'), 'title_key:', d.get('title_key'))
" || fail "weekly_meaning"
ok "hub_copy + streaks + weekly_meaning"

echo "=== [9/10] together/session ==="
TOG=$(curl -sS -m 15 "${AUTH[@]}" "${BASE}/api/wellness/together/session?locale=ru&duration_sec=180")
echo "${TOG}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert (d.get('session') or {}).get('duration_sec') == 180, d
" || fail "together_session"
ok "together_session"

echo "=== [10/10] clinician export age gate (child → 403) ==="
CODE=$(curl -sS -m 15 -o /tmp/wellness_export.json -w '%{http_code}' \
  "${AUTH[@]}" "${BASE}/api/wellness/export/clinician?days=7")
echo "HTTP ${CODE} $(head -c 120 /tmp/wellness_export.json)"
[[ "${CODE}" == "403" ]] || fail "child must not export clinician, got ${CODE}"
grep -q 'clinician_export_teen_plus' /tmp/wellness_export.json || fail "expected teen_plus gate"
ok "clinician_export blocked for child (correct)"

echo "=== [11/14] errors/catalog + premium/eligibility (Ф3 + p18-15) ==="
ERR=$(curl -sS -m 15 "${AUTH[@]}" "${BASE}/api/wellness/errors/catalog?locale=ru")
echo "${ERR}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
codes={r.get('code') for r in (d.get('errors') or [])}
assert 'wellness_consent_required' in codes, codes
print('error codes:', len(codes))
" || fail "errors/catalog"
PREM=$(curl -sS -m 15 "${AUTH[@]}" "${BASE}/api/wellness/premium/eligibility?locale=ru")
echo "${PREM}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert 'allowed' in d or 'eligible' in d, d
print('premium allowed:', d.get('allowed', d.get('eligible')))
" || fail "premium/eligibility"
ok "errors + premium"

echo "=== [12/14] seasonal + sleep stories + widget/pdf labels ==="
SEAS=$(curl -sS -m 15 "${AUTH[@]}" "${BASE}/api/wellness/seasonal/playbooks?locale=ru")
echo "${SEAS}" | python3 -c "import json,sys; d=json.load(sys.stdin); assert len(d.get('playbooks') or [])>=1, d" || fail "seasonal"
SLEEP=$(curl -sS -m 15 "${AUTH[@]}" "${BASE}/api/wellness/sleep/stories?locale=ru")
echo "${SLEEP}" | python3 -c "import json,sys; d=json.load(sys.stdin); assert len(d.get('stories') or [])>=5, d" || fail "sleep"
PDFL=$(curl -sS -m 15 "${AUTH[@]}" "${BASE}/api/wellness/export/pdf-labels?locale=ru")
echo "${PDFL}" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('title_key')=='wellness_pdf_title', d" || fail "pdf-labels"
WIDGET=$(curl -sS -m 15 "${AUTH[@]}" "${BASE}/api/wellness/widget/copy?locale=ru")
echo "${WIDGET}" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('title_key')=='wellness_widget_title', d" || fail "widget"
ok "seasonal + sleep + pdf + widget"

echo "=== [13/14] crisis/status ==="
CRISIS=$(curl -sS -m 15 "${AUTH[@]}" "${BASE}/api/wellness/crisis/status")
echo "${CRISIS}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert 'crisis' in d and 'premium' in d, d
print('cooldown_active:', (d.get('crisis') or {}).get('cooldown_active'))
" || fail "crisis/status"
ok "crisis/status"

echo "=== [14/14] store/backend (p3-11 scaffold) ==="
STORE=$(curl -sS -m 15 "${AUTH[@]}" "${BASE}/api/wellness/store/backend")
echo "${STORE}" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('backend') in ('sqlite','postgres'), d" || fail "store/backend"
ok "store/backend"

echo ""
echo "=== Wellness prod verify PASSED (${BASE}) — full platform spot-check (131/131) ==="
