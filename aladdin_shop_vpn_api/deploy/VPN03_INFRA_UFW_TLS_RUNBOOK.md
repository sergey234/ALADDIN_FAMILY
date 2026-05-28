# vpn-03: VPS — UFW, TLS, домен (минимальная поверхность)

Цель: сократить открытые порты, вынести VPN API за **TLS** и (по возможности) **не публиковать** `8091` в интернет без reverse proxy.

## 1. UFW (пример для Ubuntu)

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
# HTTPS для partner / лендинга / прокси к vpn-api
ufw allow 443/tcp
# WireGuard (если слушаете на этом хосте)
ufw allow 51820/udp
ufw enable
ufw status verbose
```

Порты **8090/8091** наружу не открывать: доступ только с `127.0.0.1` или через **nginx** на `443`.

## 2. Nginx → `aladdin-shop-vpn-api` (127.0.0.1:8091)

Пример `location` (TLS-терминация на nginx; сертификаты — certbot или хостер):

```nginx
# Публичный subscription: без query; логи не писать или access_log off
# Готовый фрагмент с комментариями: deploy/nginx_vpn_sub_rate_limit_snippet.conf.example
location ^~ /sub/ {
    access_log off;
    proxy_pass http://127.0.0.1:8091;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    limit_req zone=vpn_sub_limit burst=20 nodelay;
}

# Только markdown VPN (vpn-terms / vpn-aup / vpn-data). НЕ использовать общий /v1/legal/ —
# иначе Partner API потеряет /v1/legal/privacy и /v1/legal/terms (обычно :8090).
location ^~ /v1/legal/vpn- {
    proxy_pass http://127.0.0.1:8091;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
}

location /internal/ {
    return 404;
}
```

Зона `limit_req` задаётся в `http {}`: `limit_req_zone $binary_remote_addr zone=vpn_sub:10m rate=2r/s;` (подберите rate под политику).

## 3. TLS

- **Let’s Encrypt** (`certbot --nginx -d vpn-api.example.com`) или сертификат хостера.  
- Внутренние вызовы с HMAC — только с **loopback** или через **mTLS** между машинами (см. `VPN_SHOP_API.md`).

## 4. SSH

- Ключи вместо пароля, `PermitRootLogin prohibit-password` или отдельный sudo-пользователь.  
- При необходимости **fail2ban** / rate limit на уровне облака.

## 5. Скрипт hardening (без снятия ispmanager)

На проде (идемпотентно):

```bash
bash /opt/aladdin-shop-vpn-api/deploy/scripts/ufw_vpn_harden.sh
```

- Гарантирует: 22, 80, 443, 51820/udp, 8443/tcp, 1194/udp.
- Убирает **дубликаты** `443` / `Nginx Full`.
- **Не** удаляет ispmanager/mail без `ALADDIN_UFW_REMOVE_PANEL=1` (риск для панели хостера).

Бэкап правил: `/var/backups/ufw-status-*.txt`.

## 6. Проверка

```bash
curl -fsS https://<host>/v1/legal/vpn-terms | head
curl -fsS -o /dev/null -w '%{http_code}\n' https://<host>/health
```

Внутренние `POST /internal/...` не должны отвечать с публичного vhost (см. `return 404` выше или отдельный server только на `127.0.0.1`).
