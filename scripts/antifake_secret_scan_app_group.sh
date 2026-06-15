#!/usr/bin/env bash
# M-05 — scan App Group / antifake Swift for accidental secrets (CI gate).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PATTERN='(api[_-]?key|secret|password|Bearer [A-Za-z0-9._-]{20,}|sk-[A-Za-z0-9]{16,}|BEGIN (RSA )?PRIVATE KEY)'

TARGETS=(
  "Shared/AntifakeCallDirectory"
  "Shared/AntifakeShare"
  "ALADDINAntifakeShare"
  "Core/Security"
)

scan_file() {
  local file="$1"
  if command -v rg >/dev/null 2>&1; then
    rg -n -i "$PATTERN" "$file"
  else
    grep -n -E -i "$PATTERN" "$file"
  fi
}

search_repo() {
  local needle="$1"
  shift
  if command -v rg >/dev/null 2>&1; then
    rg -l "$needle" "$@"
  else
    grep -R -l "$needle" "$@"
  fi
}

fail=0
for dir in "${TARGETS[@]}"; do
  if [[ ! -d "$dir" ]]; then
    continue
  fi
  find_args=(-name '*.swift' -print0)
  if [[ "$dir" == "Core/Security" ]]; then
    find_args=(-name 'Antifake*.swift' -print0)
  fi
  while IFS= read -r -d '' file; do
    if scan_file "$file" >/tmp/antifake_secret_hits.txt 2>/dev/null; then
      echo "FAIL secret pattern in $file"
      cat /tmp/antifake_secret_hits.txt
      fail=1
    fi
  done < <(find "$dir" "${find_args[@]}")
done

# App Group keys must stay limited to documented payloads only
ALLOWED_KEYS=(
  "antifake_call_directory_v1"
  "antifake_share_payload_v1"
)
for key in "${ALLOWED_KEYS[@]}"; do
  count="$(search_repo "$key" Shared ALADDINAntifakeShare Core/Security 2>/dev/null | wc -l | tr -d ' ')"
  if [[ "$count" -lt 1 ]]; then
    echo "WARN: expected App Group key $key not found in repo"
  fi
done

if [[ "$fail" -ne 0 ]]; then
  echo "antifake_secret_scan_app_group: FAIL"
  exit 1
fi

echo "antifake_secret_scan_app_group: PASS"
exit 0
