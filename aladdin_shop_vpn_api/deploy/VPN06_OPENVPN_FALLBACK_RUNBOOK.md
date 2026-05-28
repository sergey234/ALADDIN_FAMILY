# vpn-06: OpenVPN fallback (TCP 443 / tls-crypt / CRL)

Цель: запасной протокол, когда **WireGuard UDP** или **Reality** недоступны (DPI, Wi‑Fi гостевой и т.д.).

## 1. Конфликт порта 443 на том же хосте, что nginx

На типичном VPS **HTTPS уже занимает TCP 443** (nginx). **OpenVPN не может слушать тот же TCP 443** на том же IP/порту без отдельного мультиплексора (sslh, stream SNI, второй публичный IP).

| Вариант | Когда использовать |
|--------|---------------------|
| **UDP 1194** (классика) | Тот же хост, что HTTPS; не конфликтует с TCP 443. Рекомендуемый **MVP fallback** на одной машине. |
| **TCP 443** | Отдельный публичный IP **или** отдельная VPS (**vpn-30**). |
| **TCP 8444 / 4433** | Тот же хост, если нужен именно TCP (обход UDP-блоков), но не «маскируется» под HTTPS. |

Дальше в runbook **по умолчанию: UDP 1194** на том же хосте, что WG/Xray.

## 2. Пакеты (Ubuntu)

```bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y openvpn easy-rsa
```

PKI (кратко): `make-cadir /etc/openvpn/easy-rsa`, `easyrsa init-pki`, `build-ca`, `gen-req server nopass`, `sign-req server`, `gen-dh` (или `openssl dhparam` отдельно), `openvpn --genkey secret tls-crypt.key`.

## 3. Шаблоны в репозитории

- `deploy/openvpn/server.conf.example` — подставить `remote`, пути к `ca.crt`, `server.crt`, `server.key`, `dh.pem`, `crl.pem`, `tls-crypt.key`.
- `deploy/openvpn/client.ovpn.example` — для выдачи пользователю после оплаты (через поддержку/автоматизацию).

## 4. CRL и отзыв

- Периодически: `easyrsa gen-crl`, копировать `crl.pem` туда, откуда читает `openvpn-server` (**`crl-verify`** в конфиге).
- После обновления CRL: `systemctl reload openvpn-server@server` (имя unit зависит от дистрибутива).

Скрипт-образец: `deploy/scripts/openvpn-revoke-cn.sh` (проверьте пути `EASYRSA_PKI` под вашу установку).

## 5. UFW

```bash
ufw allow 1194/udp comment openvpn-fallback
# или TCP fallback:
# ufw allow 1194/tcp comment openvpn-tcp-fallback
```

Не открывайте лишние порты наружу: политика — минимум.

## 6. Связка с продуктом

- Выдача `.ovpn` — только **после оплаты** (как WG `.conf`); секреты CA — только на сервере.
- В боте: текст «OpenVPN» и порт — см. **vpn-10** (`vpn:fallback:openvpn`).
