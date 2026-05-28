# vpn-04: WireGuard на VPS (ALADDIN shop VPN API)

Цель: интерфейс `wg0`, NAT в интернет, динамические peer через `wg set`, восстановление после ребута из `vpn.db`, хуки `VPN_WG_POST_PROVISION_SCRIPT` / `VPN_WG_POST_EXPIRE_SCRIPT`.

## Пакеты (Ubuntu 24.04)

```bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y wireguard wireguard-tools iptables sqlite3
```

## IP forwarding

```bash
echo 'net.ipv4.ip_forward=1' > /etc/sysctl.d/99-aladdin-wireguard.conf
sysctl -p /etc/sysctl.d/99-aladdin-wireguard.conf
```

## Определить egress-интерфейс

```bash
ip -4 route get 1.1.1.1
# пример: dev ens3  →  VPN_WG_NAT_DEV=ens3
```

Подставьте его в `PostUp`/`PostDown` ниже вместо `ens3`.

## Ключ сервера и `/etc/wireguard/wg0.conf`

Не перезаписывайте существующий `wg0.conf`, если уже настроен вручную.

```bash
umask 077
wg genkey | tee /etc/wireguard/server_private.key | wg pubkey > /etc/wireguard/server_public.key
chmod 600 /etc/wireguard/server_private.key
```

Пример `wg0.conf` (замените `PrivateKey` содержимым `/etc/wireguard/server_private.key`, `ens3` — ваш NAT dev):

```ini
[Interface]
Address = 10.8.0.1/24
ListenPort = 51820
PrivateKey = <SERVER_PRIVATE_KEY_ONE_LINE>
SaveConfig = false
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o ens3 -j MASQUERADE; /opt/aladdin-shop-vpn-api/scripts/wg-resync-active-peers.sh
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o ens3 -j MASQUERADE
```

```bash
systemctl enable wg-quick@wg0
systemctl restart wg-quick@wg0
```

Откройте UDP `51820` (или ваш `ListenPort`) в облачном security group / при включённом UFW.

## Скрипты из репозитория

Скопируйте каталог `aladdin_shop_vpn_api/deploy/scripts/` на сервер в `/opt/aladdin-shop-vpn-api/scripts/`, права:

```bash
chmod 700 /opt/aladdin-shop-vpn-api/var/wg-keys
chmod 755 /opt/aladdin-shop-vpn-api/scripts/*.sh
```

## Переменные в `/opt/aladdin-shop-vpn-api/env`

Добавьте/проверьте (пути при необходимости поправьте):

```bash
VPN_WG_INTERFACE=wg0
WG_KEYS_DIR=/opt/aladdin-shop-vpn-api/var/wg-keys
VPN_ENV_FILE=/opt/aladdin-shop-vpn-api/env
VPN_WG_POST_PROVISION_SCRIPT=/opt/aladdin-shop-vpn-api/scripts/wg-peer-up.sh
VPN_WG_POST_EXPIRE_SCRIPT=/opt/aladdin-shop-vpn-api/scripts/wg-peer-down.sh
```

Воркер и API должны иметь возможность вызывать `wg` и писать в `VPN_DB_PATH` / `WG_KEYS_DIR`. **Прод:** отдельный пользователь + узкий `sudo` только на `wg-peer-up.sh` / `wg-peer-down.sh` — см. **`VPN13_SECRETS_SUDOERS_RUNBOOK.md`** (обёртки `wg-peer-*-sudo.sh`, переменная **`VPN_SERVICE_USER`** для `chown` клиентских `*.key` под пользователя API).

## Поведение скриптов

| Скрипт | Когда |
|--------|--------|
| `wg-peer-up.sh <tid>` | После `vpn_active`: ключ клиента (если пусто), IP `10.8.0.x` в `wg_client_tunnel_ip`, `wg set peer … allowed-ips`. |
| `wg-peer-down.sh <tid>` | После `vpn_expired` (paid_until или revoke): `wg set peer remove`, удаление `*.key`, очистка WG-полей в БД. |
| `wg-resync-active-peers.sh` | Из `PostUp` wg-quick: все `vpn_active` с pubkey+tunnel_ip. |

Клиентский `PrivateKey` лежит в `WG_KEYS_DIR/<telegram_user_id>.key` (права `600`). Выдача готового `.conf` пользователю — отдельная задача (бот/UI, vpn-05 и т.д.).

## Проверка

```bash
wg show wg0
curl -sS http://127.0.0.1:8091/ready
```

`/ready` возвращает 200 только если задан `VPN_WG_INTERFACE` и интерфейс поднят.
