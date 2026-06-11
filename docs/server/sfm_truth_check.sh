#!/usr/bin/env bash
# SFM Truth Check — единая проверка для всех ML-систем
# Usage: ssh root@149.154.65.180 'bash /opt/aladdin-backend/docs/server/sfm_truth_check.sh'
set -euo pipefail

BACKEND="/opt/aladdin-backend"
SFM_CODE="${BACKEND}/app/security/safe_function_manager.py"
SFM_STUB="${BACKEND}/safe_function_manager.py"
REGISTRY="${BACKEND}/app/data/sfm/function_registry.json"
REGISTRY_LEGACY="${BACKEND}/data/sfm/function_registry.json"
AGENTS_DIR="${BACKEND}/app/security/ai_agents"

code_lines=0
if [[ -f "$SFM_CODE" ]]; then
  code_lines=$(wc -l < "$SFM_CODE" | tr -d ' ')
fi

registry_count=0
if [[ -f "$REGISTRY" ]]; then
  registry_count=$(python3 -c "
import json
d=json.load(open('${REGISTRY}'))
f=d.get('functions', d)
print(len(f) if hasattr(f, '__len__') else 0)
" 2>/dev/null || echo 0)
fi

agents_count=0
if [[ -d "$AGENTS_DIR" ]]; then
  agents_count=$(find "$AGENTS_DIR" -maxdepth 1 -name '*.py' ! -name '__init__.py' 2>/dev/null | wc -l | tr -d ' ')
fi

# Runtime via HTTP status endpoint (preferred after B-OPS-13)
sfm_loaded="unknown"
fallback_mode="unknown"
runtime_count="unknown"
if curl -sf -m 3 http://127.0.0.1:8003/api/sfm/status >/tmp/sfm_status.json 2>/dev/null; then
  sfm_loaded=$(python3 -c "import json; print(json.load(open('/tmp/sfm_status.json')).get('sfm_loaded','unknown'))")
  fallback_mode=$(python3 -c "import json; print(json.load(open('/tmp/sfm_status.json')).get('fallback_mode','unknown'))")
  runtime_count=$(python3 -c "import json; print(json.load(open('/tmp/sfm_status.json')).get('runtime_functions_count','unknown'))")
else
  # Fallback probe: old health + execute unknown fn
  health=$(curl -sf -m 3 http://127.0.0.1:8003/api/health 2>/dev/null || echo '{}')
  unknown=$(curl -sf -m 3 -X POST http://127.0.0.1:8003/api/execute \
    -H 'Content-Type: application/json' \
    -d '{"function":"__sfm_truth_probe__","params":{}}' 2>/dev/null || echo '{}')
  if echo "$unknown" | grep -q '"status":"success"'; then
    fallback_mode="true"
    sfm_loaded="false"
  fi
fi

stub_present="false"
[[ -f "$SFM_STUB" ]] && stub_present="true"

overall="FAIL"
sfm_loaded_lc=$(printf '%s' "$sfm_loaded" | tr '[:upper:]' '[:lower:]')
fallback_mode_lc=$(printf '%s' "$fallback_mode" | tr '[:upper:]' '[:lower:]')

if [[ "$code_lines" -gt 1000 ]] && [[ "$registry_count" -ge 1000 ]]; then
  if [[ "$sfm_loaded_lc" == "true" ]] && [[ "$fallback_mode_lc" == "false" ]]; then
    overall="PASS"
  elif [[ "$sfm_loaded_lc" == "unknown" ]]; then
    overall="WIRE_NEEDED"
  else
    overall="WIRE_NEEDED"
  fi
elif [[ "$code_lines" -gt 1000 ]]; then
  overall="REGISTRY_NEEDED"
else
  overall="CODE_MISSING"
fi

cat <<EOF
{
  "truth_version": "1.0",
  "overall": "${overall}",
  "code_path": "${SFM_CODE}",
  "code_exists": $([ -f "$SFM_CODE" ] && echo true || echo false),
  "code_lines": ${code_lines},
  "stub_at_root": ${stub_present},
  "registry_path": "${REGISTRY}",
  "registry_count": ${registry_count},
  "agents_on_disk": ${agents_count},
  "sfm_loaded": "${sfm_loaded}",
  "fallback_mode": "${fallback_mode}",
  "runtime_functions_count": "${runtime_count}",
  "interpretation": "$(case "$overall" in PASS) echo "SFM truth OK — proceed to next batch";; REGISTRY_NEEDED) echo "Run B-SFM-W06 rebuild registry";; WIRE_NEEDED) echo "Run B-SFM-W03..W08 connect runtime";; CODE_MISSING) echo "SFM source not at app/security/";; *) echo "Check forensic report";; esac)",
  "next_doc": "docs/SFM_SINGLE_SOURCE_OF_TRUTH.md"
}
EOF

[[ "$overall" == "PASS" ]] && exit 0
exit 1
