#!/usr/bin/env bash
# Отзыв клиентского сертификата OpenVPN по Common Name и обновление CRL.
# Настройте EASYRSA под вашу установку (часто /etc/openvpn/easy-rsa).
set -euo pipefail

CN="${1:?usage: openvpn-revoke-cn.sh <client_common_name>}"
export EASYRSA_BATCH=1
EASYRSA_DIR="${EASYRSA_DIR:-/etc/openvpn/easy-rsa}"
cd "$EASYRSA_DIR"
./easyrsa revoke "$CN"
./easyrsa gen-crl
# Скопируйте pki/crl.pem в путь из server.conf (crl-verify) и перезагрузите openvpn.

exit 0
