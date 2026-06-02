#!/usr/bin/env bash
# p3-17 — upload sleep .m4a to VPS static (nginx /static/wellness/sleep/)
set -euo pipefail

SSH_USER="${1:-root}"
HOST="${2:-149.154.65.180}"
SSH_KEY="${3:-${SSH_KEY_PATH:-}}"
LOCAL_DIR="${4:-$(dirname "$0")/../static/wellness/sleep}"

SSH_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no)
[[ -n "${SSH_KEY}" ]] && SSH_OPTS+=(-i "${SSH_KEY}")

REMOTE="/var/www/aladdin-static/wellness/sleep"
echo ">>> Upload ${LOCAL_DIR} → ${SSH_USER}@${HOST}:${REMOTE}"
ssh "${SSH_OPTS[@]}" "${SSH_USER}@${HOST}" "mkdir -p ${REMOTE}"
scp "${SSH_OPTS[@]}" -r "${LOCAL_DIR}/." "${SSH_USER}@${HOST}:${REMOTE}/"
echo ">>> Test: curl -I https://aladdin-ai.ru/static/wellness/sleep/river_v1.m4a"
