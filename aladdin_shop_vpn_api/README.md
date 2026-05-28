# aladdin_shop_vpn_api

Внутренний **control plane** для VPN магазина (`aladdin-shop-vpn-api` на сервере). Документация: `telegram_stars_shop_bot/docs/VPN_SHOP_INTEGRATION_PLAN.md`, контракт: `telegram_stars_shop_bot/docs/VPN_SHOP_API.md`.

## Локальный запуск

```bash
cd aladdin_shop_vpn_api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export VPN_API_HMAC_SECRET=dev-secret-change-me
export VPN_DB_PATH=./var/vpn.db
mkdir -p var
python3 -m uvicorn aladdin_shop_vpn_api.main:app --host 127.0.0.1 --port 8091
```

## Тесты

Из каталога `ALADDIN_iOS`:

```bash
python3 -m pytest aladdin_shop_vpn_api/tests -q
```

## Воркер (один цикл обработки очереди)

```bash
export VPN_DB_PATH=./var/vpn.db
python3 -m aladdin_shop_vpn_api.worker
```

Публичные тексты (**vpn-02**): `GET /v1/legal/vpn-terms`, `/v1/legal/vpn-aup`, `/v1/legal/vpn-data` (markdown в `aladdin_shop_vpn_api/legal_docs/`). Инфра TLS/UFW — `deploy/VPN03_INFRA_UFW_TLS_RUNBOOK.md`; подписка Xray фаза A — `deploy/VPN05_XRAY_SUBSCRIPTION_RUNBOOK.md` и **`VPN_SUBSCRIBE_BODY_FILE`**.

На проде: реальный WireGuard — `VPN_DEV_STUB_WG=1` оставляет провижининг «логическим» в БД, а `VPN_WG_POST_PROVISION_SCRIPT` / `VPN_WG_POST_EXPIRE_SCRIPT` вызывают `wg` на сервере (см. `deploy/VPN04_WIREGUARD_RUNBOOK.md`). Секреты, sudo, бэкапы — **`deploy/VPN13_SECRETS_SUDOERS_RUNBOOK.md`**. При `VPN_DEV_STUB_WG=0` без нативной реализации в Python джоб `provision` по-прежнему падает, если не настроен другой путь.

