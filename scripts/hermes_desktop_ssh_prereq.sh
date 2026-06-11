#!/usr/bin/env bash
# Проверка SSH перед настройкой tunnel в Hermes One (задача 1.2).
set -euo pipefail

SSH_KEY="${SSH_KEY:-$HOME/.ssh/aladdin_server}"
HOST="${SSH_HOST:-root@149.154.65.180}"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

[[ -f "$SSH_KEY" ]] || fail "SSH key missing: $SSH_KEY"

ssh -o IdentitiesOnly=yes -o BatchMode=yes -i "$SSH_KEY" "$HOST" \
  'test -x /opt/aladdin-backend/venv/bin/hermes && test -f /root/.hermes/config.yaml' \
  || fail "hermes binary or config missing on VPS"

VER=$(ssh -o IdentitiesOnly=yes -o BatchMode=yes -i "$SSH_KEY" "$HOST" \
  '/opt/aladdin-backend/venv/bin/hermes --version 2>/dev/null | head -1' || true)
ok "SSH + hermes on VPS (${VER:-unknown})"
echo "Next: Hermes One.app → SSH tunnel → host 149.154.65.180, user root, key ${SSH_KEY}"
