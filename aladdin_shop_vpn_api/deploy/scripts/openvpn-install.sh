#!/usr/bin/env bash
# Idempotent OpenVPN server (UDP 1194) for ALADDIN single-node fallback. See deploy/VPN06_OPENVPN_FALLBACK_RUNBOOK.md
set -euo pipefail

EASYRSA_DIR="${EASYRSA_DIR:-/etc/openvpn/easy-rsa}"
SERVER_DIR="${OPENVPN_SERVER_DIR:-/etc/openvpn/server}"
OVPN_PORT="${VPN_OVPN_REMOTE_PORT:-1194}"
OVPN_NET="${OPENVPN_TUN_NET:-10.9.0.0}"
OVPN_MASK="${OPENVPN_TUN_MASK:-255.255.255.0}"
WAN_IFACE="${OPENVPN_WAN_IFACE:-ens3}"

mkdir -p "$SERVER_DIR" /var/log/openvpn

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq openvpn easy-rsa

if [[ ! -d "$EASYRSA_DIR/pki" ]]; then
  rm -rf "$EASYRSA_DIR"
  make-cadir "$EASYRSA_DIR"
  cd "$EASYRSA_DIR"
  ./easyrsa --batch init-pki
  EASYRSA_BATCH=1 ./easyrsa --batch build-ca nopass
  EASYRSA_BATCH=1 ./easyrsa --batch gen-req server nopass
  EASYRSA_BATCH=1 ./easyrsa --batch sign-req server server
  ./easyrsa --batch gen-dh
  EASYRSA_BATCH=1 ./easyrsa --batch gen-crl
  openvpn --genkey secret "${SERVER_DIR}/tls-crypt.key"
fi

mkdir -p "$SERVER_DIR" /var/log/openvpn
install -m 0644 "${EASYRSA_DIR}/pki/ca.crt" "${SERVER_DIR}/ca.crt"
install -m 0644 "${EASYRSA_DIR}/pki/issued/server.crt" "${SERVER_DIR}/server.crt"
install -m 0600 "${EASYRSA_DIR}/pki/private/server.key" "${SERVER_DIR}/server.key"
install -m 0644 "${EASYRSA_DIR}/pki/dh.pem" "${SERVER_DIR}/dh.pem"
install -m 0644 "${EASYRSA_DIR}/pki/crl.pem" "${SERVER_DIR}/crl.pem"
[[ -f "${SERVER_DIR}/tls-crypt.key" ]] || openvpn --genkey secret "${SERVER_DIR}/tls-crypt.key"

cat >"${SERVER_DIR}/server.conf" <<EOF
port ${OVPN_PORT}
proto udp
dev tun
user nobody
group nogroup
persist-key
persist-tun

ca ${SERVER_DIR}/ca.crt
cert ${SERVER_DIR}/server.crt
key ${SERVER_DIR}/server.key
dh ${SERVER_DIR}/dh.pem
crl-verify ${SERVER_DIR}/crl.pem
tls-crypt ${SERVER_DIR}/tls-crypt.key

topology subnet
server ${OVPN_NET} ${OVPN_MASK}
ifconfig-pool-persist /var/log/openvpn/ipp.txt

keepalive 10 120
remote-cert-tls client
cipher AES-256-GCM
auth SHA256
tls-version-min 1.2

push "redirect-gateway def1 bypass-dhcp"
push "dhcp-option DNS 1.1.1.1"
push "dhcp-option DNS 2606:4700:4700::1111"

verb 3
explicit-exit-notify 1
script-security 2
up ${SERVER_DIR}/up.sh
down ${SERVER_DIR}/down.sh
EOF

cat >"${SERVER_DIR}/up.sh" <<'UPS'
#!/bin/sh
WAN="${OPENVPN_WAN_IFACE:-ens3}"
iptables -C FORWARD -i tun0 -j ACCEPT 2>/dev/null || iptables -A FORWARD -i tun0 -j ACCEPT
iptables -C FORWARD -o tun0 -j ACCEPT 2>/dev/null || iptables -A FORWARD -o tun0 -j ACCEPT
iptables -t nat -C POSTROUTING -s 10.9.0.0/24 -o "$WAN" -j MASQUERADE 2>/dev/null || iptables -t nat -A POSTROUTING -s 10.9.0.0/24 -o "$WAN" -j MASQUERADE
UPS
cat >"${SERVER_DIR}/down.sh" <<'DOWNS'
#!/bin/sh
WAN="${OPENVPN_WAN_IFACE:-ens3}"
iptables -D FORWARD -i tun0 -j ACCEPT 2>/dev/null || true
iptables -D FORWARD -o tun0 -j ACCEPT 2>/dev/null || true
iptables -t nat -D POSTROUTING -s 10.9.0.0/24 -o "$WAN" -j MASQUERADE 2>/dev/null || true
DOWNS
chmod 0755 "${SERVER_DIR}/up.sh" "${SERVER_DIR}/down.sh"

chmod 0644 "${SERVER_DIR}/server.conf"

if command -v ufw >/dev/null 2>&1; then
  ufw allow "${OVPN_PORT}/udp" comment openvpn-fallback || true
fi

systemctl enable "openvpn-server@server"
systemctl restart "openvpn-server@server"
systemctl is-active "openvpn-server@server"

echo "openvpn-install: ok port=${OVPN_PORT}"
