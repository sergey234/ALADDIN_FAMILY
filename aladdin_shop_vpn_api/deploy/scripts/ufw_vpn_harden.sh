#!/usr/bin/env bash
# vpn-03: VPN-порты в UFW + убрать дубликаты 443/Nginx Full. ispmanager/mail — только с ALADDIN_UFW_REMOVE_PANEL=1
set -euo pipefail

REMOVE_DUP="${ALADDIN_UFW_REMOVE_DUPLICATES:-1}"
BACKUP="/var/backups/ufw-status-$(date +%Y%m%d-%H%M%S).txt"

mkdir -p /var/backups
ufw status numbered >"$BACKUP" 2>&1 || true
echo "backup: $BACKUP"

ensure_rule() {
  local spec="$1"
  local comment="$2"
  if ufw status | grep -qF "$comment"; then
    echo "ok: $comment"
  else
    ufw allow "$spec" comment "$comment"
    echo "added: $comment ($spec)"
  fi
}

ensure_rule "22/tcp" "ssh-aladdin"
ensure_rule "80/tcp" "http-acme"
ensure_rule "443/tcp" "https"
ensure_rule "51820/udp" "wireguard-wg0"
ensure_rule "8443/tcp" "xray-reality"
ensure_rule "1194/udp" "openvpn-fallback"

if ufw status | grep -qE '(8090|8091)/'; then
  echo "WARN: ports 8090/8091 in UFW — API should be 127.0.0.1 only" >&2
else
  echo "ok: 8090/8091 not exposed in UFW"
fi

delete_rule_matching() {
  local pattern="$1"
  local n
  n=$(ufw status numbered 2>/dev/null | grep -F "$pattern" | head -1 | sed -n 's/^\[\s*\([0-9]*\)\].*/\1/p')
  if [[ -n "${n:-}" ]]; then
    echo "delete [$n] $pattern"
    ufw --force delete "$n" || true
    return 0
  fi
  return 1
}

if [[ "$REMOVE_DUP" == "1" ]]; then
  for _ in 1 2 3 4 5 6; do
    delete_rule_matching "Nginx Full" || true
    delete_rule_matching "] 443  " || delete_rule_matching "] 443 " || true
  done
fi

if [[ "${ALADDIN_UFW_REMOVE_PANEL:-0}" == "1" ]]; then
  echo "Panel removal not automated — edit UFW manually after review" >&2
fi

echo "--- ufw status (head) ---"
ufw status numbered | head -30
echo "ufw_vpn_harden: done"
