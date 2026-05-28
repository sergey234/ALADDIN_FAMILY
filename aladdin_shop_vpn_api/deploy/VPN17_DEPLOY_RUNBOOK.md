# VPN17 — единый RUNBOOK выката (shop-бот + aladdin-shop-vpn-api)

**Назначение:** один чеклист end-to-end для ML/деплоя. Детали по подсистемам — в связанных runbook’ах (не дублировать их целиком).

**Связанные документы:**

| Документ | Тема |
|----------|------|
| `telegram_stars_shop_bot/docs/VPN_ML_SYSTEM_HANDOFF.md` | Post-deploy env, Prometheus, todo |
| `telegram_stars_shop_bot/docs/ML_SYSTEM_HANDOFF_FINAL.md` §2 | rsync бота на `149.154.65.180` |
| `telegram_stars_shop_bot/docs/VPN_SHOP_API.md` | Контракт API |
| `deploy/VPN03_INFRA_UFW_TLS_RUNBOOK.md` | UFW, TLS, nginx |
| `deploy/VPN04_WIREGUARD_RUNBOOK.md` | wg0, NAT, peer scripts |
| `deploy/VPN05_XRAY_SUBSCRIPTION_RUNBOOK.md` | Xray, `/sub/` |
| `deploy/VPN06_OPENVPN_FALLBACK_RUNBOOK.md` | OpenVPN |
| `deploy/VPN13_SECRETS_SUDOERS_RUNBOOK.md` | HMAC, sudoers, бэкапы |
| `deploy/VPN15_OBSERVABILITY_RUNBOOK.md` | Sentry, `/metrics`, Grafana |
| `telegram_stars_shop_bot/docs/VPN14_SUPPORT_ADMIN_RUNBOOK.md` | `/admin_vpn_*` |
| `telegram_stars_shop_bot/docs/VPN34_STATUS_CHANNEL_RUNBOOK.md` | Канал статуса |

**Сервер (канон):** `149.154.65.180` — см. `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`.

---

## 0. Предусловия

- [ ] SSH по ключу (`~/.ssh/aladdin_server` или канон из гайда).
- [ ] Снаружи: `curl -sS -m 8 http://149.154.65.180:8002/api/health` → `{"status":"ok"}`.
- [ ] Рабочий git-корень iOS: `.../mobile_apps/ALADDIN_iOS`.

---

## 1. Каталоги на VPS

| Путь | Сервис |
|------|--------|
| `/opt/aladdin-telegram-shop-bot` | Shop-бот + Partner API `:8090` |
| `/opt/aladdin-shop-vpn-api` | VPN control plane `:8091` (loopback) |
| `/opt/aladdin-backend` | **Не трогать** без отдельной задачи |

---

## 2. Выкат vpn-api

1. **Код:** rsync/git из репо `aladdin_shop_vpn_api/` → `/opt/aladdin-shop-vpn-api/current` (или ваш канал релизов).
2. **venv:** `pip install -r requirements.txt` при изменении зависимостей.
3. **env** `/opt/aladdin-shop-vpn-api/env` (не в git):
   - `VPN_API_HMAC_SECRET` = тот же, что у бота
   - `VPN_DB_PATH=/opt/aladdin-shop-vpn-api/var/vpn.db`
   - `VPN_LOCATIONS_JSON` = как у бота
   - `VPN_WG_ENDPOINT_HOST`, `WG_KEYS_DIR`, `VPN_WG_POST_PROVISION_SCRIPT` — см. **VPN04**, **VPN13**
   - `VPN_JOB_MAX_ATTEMPTS=5` (воркер, backoff)
   - Опционально: `SENTRY_*` — **VPN15**
4. **systemd:**
   - `deploy/aladdin-shop-vpn-api.service.example` → `/etc/systemd/system/aladdin-shop-vpn-api.service`
   - `deploy/aladdin-shop-vpn-worker.service.example` + `.timer.example`
   - `deploy/aladdin-shop-vpn-backup.service.example` + `.timer.example`
   ```bash
   systemctl daemon-reload
   systemctl enable --now aladdin-shop-vpn-api.service
   systemctl enable --now aladdin-shop-vpn-worker.timer
   systemctl enable --now aladdin-shop-vpn-backup.timer
   ```
5. **Смоук (на сервере):**
   ```bash
   curl -sS http://127.0.0.1:8091/health
   curl -sS http://127.0.0.1:8091/ready
   ```

Подробно: **VPN04**, **VPN13**, **VPN15**.

---

## 3. Выкат shop-бота

1. Из `.../mobile_apps/ALADDIN_iOS` — rsync `telegram_stars_shop_bot/` по **ML_SYSTEM_HANDOFF_FINAL.md** §2 (исключить `.env`, `data`).
2. **shared/.env** на сервере — merge с `env.example`:
   - `UI_SHOW_VPN=true`
   - `VPN_API_BASE_URL=http://127.0.0.1:8091`
   - `VPN_API_HMAC_SECRET` (общий)
   - `VPN_INSTRUCTIONS_URL=https://aladdin-ai.ru/v1/legal/vpn-instructions`
   - `VPN_LOCATIONS_FROM_API=true` (опционально)
   - `VPN_API_CIRCUIT_*`, `VPN_API_HTTP_MAX_RETRIES` (vpn-25)
   - `SHOP_BOT_USERNAME` для `/r/{code}`
3. **pip** в venv бота при изменении `requirements.txt` (`qrcode` для QR WG).
4. **Рестарт:**
   ```bash
   systemctl restart aladdin-telegram-bot.service aladdin-partner-api.service aladdin-webhook-worker.service
   curl -sS http://127.0.0.1:8090/health
   ```

---

## 4. Nginx (aladdin-ai.ru)

1. Сниппет legal/sub: `deploy/nginx/aladdin-ai.ru-locations-vpn-api.snippet.conf`.
2. **vpn-23:** `deploy/nginx_vpn_sub_rate_limit_snippet.conf.example` — `limit_req` на `/sub/`, `access_log off`.
3. **vpn-15:** `/metrics` не наружу — `nginx_vpn_metrics_allow_local.conf.example`.
4. `nginx -t && systemctl reload nginx`.

См. **VPN03**, **VPN05**.

---

## 5. WireGuard / Xray / OpenVPN (по фазам)

| Фаза | Runbook | Проверка |
|------|---------|----------|
| WG MVP | VPN04 | `wg show`; выдача `.conf` через бот «📥 WireGuard» |
| Xray `/sub/` | VPN05 | `curl` opaque subscription (без секретов в логах) |
| OpenVPN | VPN06 | сервер + ручная/будущая автовыдача `.ovpn` |

---

## 6. Наблюдаемость (post-deploy)

См. **VPN_ML_SYSTEM_HANDOFF.md** §1 и **VPN15**:

- Prometheus scrape `http://127.0.0.1:8091/metrics`
- Grafana: `deploy/grafana/aladdin_shop_vpn_api_dashboard.json`
- Sentry на vpn-api и боте

---

## 7. Приёмочный сценарий (E2E)

1. [ ] Оплата SKU `vpn_*` → job `provision` → `vpn_active` в `vpn.db`.
2. [ ] В боте: **📥 WireGuard (.conf)** — файл приходит.
3. [ ] **📷 QR WireGuard** — PNG с QR.
4. [ ] `/admin_vpn_status` — без секретов в ответе.
5. [ ] Повтор webhook оплаты — идемпотентно, без второго peer.
6. [ ] При остановке vpn-api — circuit breaker в боте (алерт при `ALERTS_ENABLED=true`).

---

## 8. Инцидент: блокировка IP (vpn-33)

Кратко (полный плейбук — отдельная задача **vpn-33**):

1. Симптом с телефона (МТС/Wi‑Fi) + внешний мониторинг (**vpn-32**).
2. Сверка `docs/VPN_PUBLIC_SURFACE_REGISTRY.md` (**vpn-29**).
3. `systemctl`, `wg`, очередь `jobs`, Grafana (**vpn-15**).
4. Меры: смена IP, нода B (**vpn-30**), пост в канал (**vpn-34**).
5. Постмортем с тегом типа блокировки.

---

## 9. Версия

| Дата | Изменение |
|------|-----------|
| 2026-05-15 | Первый VPN17: единый чеклист выката + E2E + ссылки на VPN03–15. |
