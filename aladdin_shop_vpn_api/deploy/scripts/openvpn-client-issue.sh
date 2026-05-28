#!/usr/bin/env bash
# Issue per-user .ovpn (client cert + inline ca/tls-crypt). argv1 = telegram_user_id
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_env="${VPN_ENV_FILE:-/opt/aladdin-shop-vpn-api/env}"

_read_env() {
  local key="$1"
  if [[ ! -f "$_env" ]]; then
    return 1
  fi
  grep -m1 "^${key}=" "$_env" 2>/dev/null | cut -d= -f2- | sed 's/^"\(.*\)"$/\1/'
}

if [[ -z "${VPN_WG_ENDPOINT_HOST:-}" ]]; then
  VPN_WG_ENDPOINT_HOST="$(_read_env VPN_WG_ENDPOINT_HOST || true)"
fi
if [[ -z "${VPN_OVPN_REMOTE_PORT:-}" ]]; then
  VPN_OVPN_REMOTE_PORT="$(_read_env VPN_OVPN_REMOTE_PORT || true)"
fi
if [[ -z "${VPN_SERVICE_USER:-}" ]]; then
  VPN_SERVICE_USER="$(_read_env VPN_SERVICE_USER || true)"
fi
if [[ -z "${OVPN_PROFILES_DIR:-}" ]]; then
  OVPN_PROFILES_DIR="$(_read_env VPN_OVPN_PROFILES_DIR || true)"
fi

TID="${1:?usage: openvpn-client-issue.sh <telegram_user_id>}"
[[ "$TID" =~ ^[0-9]+$ ]] || {
  echo "invalid telegram_user_id" >&2
  exit 1
}

EASYRSA_DIR="${EASYRSA_DIR:-/etc/openvpn/easy-rsa}"
SERVER_DIR="${OPENVPN_SERVER_DIR:-/etc/openvpn/server}"
OUT_DIR="${OVPN_PROFILES_DIR:-/opt/aladdin-shop-vpn-api/var/ovpn-profiles}"
REMOTE_HOST="${VPN_WG_ENDPOINT_HOST:-aladdin-ai.ru}"
REMOTE_PORT="${VPN_OVPN_REMOTE_PORT:-1194}"
CN="aladdin-vpn-${TID}"

mkdir -p "$OUT_DIR"
chmod 700 "$OUT_DIR"

cd "$EASYRSA_DIR"
if [[ ! -f "pki/issued/${CN}.crt" ]]; then
  EASYRSA_BATCH=1 ./easyrsa --batch gen-req "$CN" nopass
  EASYRSA_BATCH=1 ./easyrsa --batch sign-req client "$CN"
fi

out="${OUT_DIR}/${TID}.ovpn"
umask 077
{
  echo "client"
  echo "dev tun"
  echo "proto udp"
  echo "remote ${REMOTE_HOST} ${REMOTE_PORT}"
  echo "resolv-retry infinite"
  echo "nobind"
  echo "persist-key"
  echo "persist-tun"
  echo "remote-cert-tls server"
  echo "cipher AES-256-GCM"
  echo "auth SHA256"
  echo "verb 3"
  echo "key-direction 1"
  echo "<ca>"
  cat "${SERVER_DIR}/ca.crt"
  echo "</ca>"
  echo "<cert>"
  sed -n '/BEGIN CERTIFICATE/,/END CERTIFICATE/p' "pki/issued/${CN}.crt"
  echo "</cert>"
  echo "<key>"
  cat "pki/private/${CN}.key"
  echo "</key>"
  echo "<tls-crypt>"
  cat "${SERVER_DIR}/tls-crypt.key"
  echo "</tls-crypt>"
} >"$out"
chmod 600 "$out"

if [[ -n "${VPN_SERVICE_USER:-}" ]]; then
  chown "${VPN_SERVICE_USER}:${VPN_SERVICE_USER}" "$out" || true
fi

echo "issued ${out}"
