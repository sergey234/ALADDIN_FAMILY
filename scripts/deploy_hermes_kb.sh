#!/usr/bin/env bash
# Деплой KB markdown на VPS /opt/aladdin-hermes/knowledge/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SSH_HOST="${SSH_HOST:-root@149.154.65.180}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/aladdin_server}"
KB_LOCAL="${ROOT}/security/hermes_knowledge"
KB_REMOTE="/opt/aladdin-hermes/knowledge"

RSYNC_SSH="ssh -o IdentitiesOnly=yes -o BatchMode=yes -i ${SSH_KEY}"

rsync -az -e "$RSYNC_SSH" \
  "${KB_LOCAL}/" "${SSH_HOST}:${KB_REMOTE}/"

echo "KB deployed to ${SSH_HOST}:${KB_REMOTE}"
ssh -o IdentitiesOnly=yes -o BatchMode=yes -i "$SSH_KEY" "$SSH_HOST" \
  "ls -la ${KB_REMOTE}/*.md | tail -10"
