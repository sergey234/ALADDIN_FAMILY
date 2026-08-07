# AiMonkey Shop + VPN — полный handoff для следующей ML-системы

**Дата:** 2026-06-30  
**Сессия:** Stars UX, SSOT Contabo, Фаза A/B VPN, CDN DNS-фазы, WG internal hop  
**Читать первым:** этот файл → `docs/AIMONKEY_MASTER_PLAN_2026-06-30.md` → `docs/BOT_SINGLE_INSTANCE_CANON.md`

**Бот:** `@AiMonkeyStars_bot`  
**SSH-ключ:** `~/.ssh/aladdin_server`

---

## 0. START HERE (для агента за 2 минуты)

### Что уже сделано (не переделывать без причины)

- Stars: меню 100/500/1000+ + кастом qty + авто-цена
- Один бот polling только на **Contabo** (MAIN бот disabled)
- SSOT: `shop.db`, fx-rate-sync, ops-watchdog на **Contabo**
- VPN Фаза B: Vision (A/B staging), bridge TCP+Vision, WG internal hop, CDN SNI fix
- MAIN shop API (`partner-api`, `webhook-worker`) **остановлены** — не включать на MAIN

### Что делать дальше (Фаза C, порядок)

1. **`vpn-phone-drill`** — G4 drill ×4 оператора (определяет DNS-фазу CDN!)
2. **`vpn-domain-com`** — зеркало `subs.aladdin-ai.com` для `/sub/`
3. **`vpn-ux-auto`** — один Connect + авто-fallback
4. **`vpn-rkn-mitigation`** — мониторинг реестра РКН + playbook

### Критические «НЕ ДЕЛАТЬ»

| Ошибка | Почему |
|--------|--------|
| Включить `aladdin-telegram-bot` на MAIN | `TelegramConflictError`, старое меню |
| `VPN_CDN_PORT=443` без CF orange cloud | CDN-профиль сломается (MAIN :443 = nginx сайт) |
| WG internal на подсети `10.9.0.x` | Конфликт с `tun0` на Contabo (`10.9.0.1/24`) |
| Vision на всех пользователей сразу | Только staging TID или A/B |
| Считать CDN зеркалом скорости | CDN = обход блокировок, не Mbps |

---

## 1. Архитектура SSOT (канон на 2026-06-30)

```
                    ┌─────────────────────────────────────────┐
                    │  MAIN 149.154.65.180 (РФ)               │
                    │  • nginx :443 → proxy aladdin-ai.ru     │
                    │  • xray-bridge :8444 (мост для 4G)    │
                    │  • wg-bridge 10.10.0.1 ↔ Contabo      │
                    │  • CDN relay nginx :8445 → Contabo    │
                    │  • iOS backend :8002 (не shop)        │
                    │  • shop bot DISABLED                    │
                    └──────────────┬──────────────────────────┘
                                   │ WG 10.10.0.0/30
                                   │ bridge hop TCP+Vision
                    ┌──────────────▼──────────────────────────┐
                    │  Contabo 185.225.233.150 (EU egress)    │
                    │  • aladdin-telegram-bot (polling)     │
                    │  • partner-api :8090, vpn-api :8091   │
                    │  • shop.db SSOT, fx-rate-sync timer   │
                    │  • ops-watchdog timer                 │
                    │  • auto-fulfill-worker                │
                    │  • xray :8443 xhttp, :8446 vision     │
                    │  • xray CDN origin :8445              │
                    │  • wg0 клиенты 10.8.0.0/24            │
                    └─────────────────────────────────────────┘
```

| Роль | Сервер | Порт/сервис |
|------|--------|-------------|
| Telegram bot polling | **Contabo** | `aladdin-telegram-bot` |
| `shop.db` SSOT | **Contabo** | `/opt/aladdin-telegram-shop-bot/data/shop.db` |
| Partner API + webhooks | **Contabo** | `:8090` |
| VPN API `/sub/` | **Contabo** `:8091` | nginx MAIN проксирует `/v1/` и `/sub/` |
| Публичный HTTPS | **MAIN** nginx | → Contabo |
| RU bridge (4G first hop) | **MAIN** | `:8444` TCP+Vision |
| Bridge → Contabo hop | **MAIN** → WG | `10.10.0.2:8446` TCP+Vision (не публичный IP!) |
| FX rate daily 09:00 | **Contabo** | `fx-rate-sync.timer` |
| Ops health 2 min | **Contabo** | `ops-watchdog.timer` |

**Пути на Contabo:**

| Компонент | Путь |
|-----------|------|
| Shop bot | `/opt/aladdin-telegram-shop-bot/` (`current_app`, `shared/.env`, `data/shop.db`) |
| VPN API | `/opt/aladdin-shop-vpn-api/` (`env`, `var/vpn.db`) |
| Xray | `/opt/xray/config.json` |
| WG internal bridge | `/etc/wireguard/wg-bridge.conf`, `10.10.0.2/32` |

**Пути на MAIN:**

| Компонент | Путь |
|-----------|------|
| Xray bridge | `/opt/xray-bridge/config.json` (`:8444` in, hop `10.10.0.2:8446` out) |
| WG internal | `/etc/wireguard/wg-bridge.conf`, `10.10.0.1/32` |
| CDN relay | `/etc/nginx/stream.d/cdn-relay.conf` (`*:8445` → Contabo `:8445`) |

---

## 2. Что сделано в сессии (подробно)

### 2.1 Stars (`stars-ux`, `stars-auto-ff`, `stars-user-guide`)

| Задача | Статус | Детали |
|--------|--------|--------|
| Меню 100/500/1000+ + «Своё кол-во» | ✅ | `products.yaml`, FSM, `pricing.py` |
| Авто-выдача Stars | ✅ код + worker | Worker на Contabo; **блокер:** TON баланс iStar = 0 (порог 20 TON) |
| Инструкция Wi‑Fi/4G после VPN | ✅ | `vpn_post_purchase_delivery.py`, handlers |
| CopyText → callback | ✅ | deploy `20260630` |

**Файлы:** `telegram_stars_shop_bot/bot/handlers/shop.py`, `shop_kb.py`, `pricing.py`, `auto_fulfill_runner.py`

### 2.2 Инфраструктура shop (вне исходного плана, но критично)

Скрипт: `telegram_stars_shop_bot/scripts/apply_shop_ssot_cleanup.sh`

| Действие | Где |
|----------|-----|
| Остановлены `aladdin-partner-api`, `aladdin-webhook-worker` | MAIN |
| `fx-rate-sync.timer` + `ops-watchdog.timer` перенесены | Contabo |
| `USD_RUB_RATE` синхронизирован с ЦБ+markup | Contabo SSOT |

### 2.3 VPN Фаза A (`vpn-ops`)

| Мера | Где |
|------|-----|
| `connIdle: 300` в xray | MAIN bridge + Contabo |
| Ночной restart моста 04:30 MSK | MAIN `xray-bridge-nightly-restart.timer` |
| TCP health bridge в ops-watchdog | `vpn_ops_health.py` |

### 2.4 VPN Фаза B

#### `vpn-vision` — Vision на direct (A/B staging)

- Inbound **`:8446`** TCP+Reality+Vision на Contabo (`direct-vision-in`)
- Env: `VPN_SUBSCRIBE_DIRECT_VISION_MODE=staging`, `VPN_SUBSCRIBE_VISION_STAGING_TIDS=493897224`
- Staging-пользователи: direct-профили (Wi‑Fi + Мобильный интернет) → `:8446` + `flow=xtls-rprx-vision`
- Остальные: `:8443` xhttp (без изменений)

**Код:** `aladdin_shop_vpn_api/aladdin_shop_vpn_api/subscription_util.py`  
**Скрипт:** `deploy/scripts/apply_direct_vision_staging.sh`

#### `vpn-bridge-tcp` — мост TCP+Vision вместо xhttp×2

- MAIN `:8444` inbound: **xhttp → tcp+vision**
- Профиль «Мобильный мост» в `/sub/`: `type=tcp&flow=xtls-rprx-vision`

**Скрипт:** `deploy/scripts/apply_bridge_tcp_vision.sh`, `migrate_bridge_xhttp_to_tcp_vision.py`

#### `vpn-wg-internal` — MAIN↔Contabo через WG

**Проблема:** подсеть `10.9.0.x` конфликтует с `tun0` на Contabo (`10.9.0.1/24`). SYN приходил, SYN-ACK не уходил.

**Решение:** подсеть **`10.10.0.0/30`**

| Узел | WG IP | Порт WG |
|------|-------|---------|
| MAIN | `10.10.0.1/32` | UDP 51821 |
| Contabo | `10.10.0.2/32` | UDP 51821 |

Bridge hop (MAIN outbound): **`10.10.0.2:8446`** TCP+Vision (не `185.225.233.150`).

**Полный путь 4G (мост):**
```
Телефон → TCP+Vision → MAIN:8444 → WG 10.10.0.2:8446 → Contabo xray → egress EU
```

**Скрипт:** `deploy/scripts/apply_wg_internal_bridge.sh`, `install_wg_internal_bridge.py`

#### `vpn-cdn-cf` — CDN (частично)

| Сделано | Не сделано (ждёт drill / CF) |
|---------|------------------------------|
| SNI в подписке: `www.cloudflare.com` | CF orange cloud в DNS |
| `VPN_CDN_PORT=8445` (фаза 2) | `VPN_CDN_PORT=443` |
| Origin `:8445` на Contabo | Legal vpn-54/77 перед фазой 3 |

---

## 3. Четыре профиля VPN в подписке (текущее состояние)

| Профиль | Host:Port | Транспорт | Назначение |
|---------|-----------|-----------|------------|
| Домашний Wi‑Fi | `vpn.aladdin-ai.ru:8443` или `:8446`* | xhttp / vision* | Wi‑Fi direct EU |
| Мобильный интернет | то же | xhttp / vision* | 4G direct EU |
| Мобильный мост | `149.154.65.180:8444` | **TCP+Vision** | 4G, first hop РФ |
| Мобильный CDN | `cdn.aladdin-ai.ru:8445` | xhttp, SNI `cloudflare.com` | 4G авария |

\* `:8446` vision только для staging TID `493897224` (env `VPN_SUBSCRIBE_VISION_STAGING_TIDS`).

**Порядок на 4G для пользователя:** мост → direct → CDN.

---

## 4. CDN: порты 8445 vs 443 — ОБЯЗАТЕЛЬНО ПОНЯТЬ

Это **не** «443 лучше 8445». Порт в `/sub/` **должен совпадать с DNS-фазой**.

Источник истины: `aladdin_shop_vpn_api/deploy/VPN_CDN_DNS_PHASE_CHECKLIST.md`

### Фазы DNS для `cdn.aladdin-ai.ru`

| Фаза | DNS A-запись | Порт в подписке | Сейчас? |
|------|--------------|-----------------|---------|
| **1 grey** | `185.225.233.150` (Contabo) | **8445** | Нет |
| **2 RU relay** | `149.154.65.180` (MAIN) + nginx relay → Contabo | **8445** | **ДА** |
| **3 CF orange** | Cloudflare proxy (orange cloud) | **443** | Нет |

**Текущий DNS (проверка):**
```bash
dig @8.8.8.8 +short cdn.aladdin-ai.ru A
# → 149.154.65.180  (фаза 2)
```

**Почему нельзя поставить 443 сейчас:**
- `cdn.aladdin-ai.ru:443` → MAIN nginx (сайт `aladdin-ai.ru`) ≠ VLESS Reality
- Профиль «Мобильный CDN» перестанет подключаться

**Когда переходить на 443:**
1. DNS `cdn` за Cloudflare (orange cloud)
2. CF проксирует на origin Contabo `:8445`
3. Тогда: `VPN_CDN_CF_ORANGE=1 ./deploy/scripts/apply_cdn_cf_orange.sh`

**Почему раньше был SNI `cdn.aladdin-ai.ru`:** ошибка конфигурации Reality (SSL mismatch). Исправлено на `www.cloudflare.com`. Порт **8445** менять не нужно было.

### Метод 6 шляп (вывод по CDN)

| Шляпа | Вывод |
|-------|-------|
| 🤍 Белая | DNS→MAIN; relay 8445; CF не включён |
| ❤️ Красная | 443 без CF = сломанный CDN-профиль |
| 🖤 Чёрная | CF не панацея; нужен drill перед фазой 3 |
| 💛 Жёлтая | 8445+MAIN = РФ first hop для CDN |
| 💚 Зелёная | Порт = f(DNS фаза); авто env по фазе |
| 💙 Синяя | G4 drill → выбор фазы → смена DNS → смена порта |

---

## 5. Что осталось сделать (Фаза C + хвосты)

### 5.1 `vpn-phone-drill` — ПРИОРИТЕТ #1

**Зачем:** без drill нельзя выбрать DNS-фазу CDN (1/2/3) и обосновать CF orange.

**DoD:** 4 оператора × 3 профиля (мост, direct, CDN) × ≥1 Мбит/с 5 мин.

**Шаблон журнала:** `telegram_stars_shop_bot/docs/VPN_QUARTERLY_DRILL_CHECKLIST.md`  
**Чеклист DNS:** `aladdin_shop_vpn_api/deploy/VPN_CDN_DNS_PHASE_CHECKLIST.md`

Таблица для заполнения:

| Оператор | Мост :8444 | Direct :8443 | CDN :8445 | Тип блока (IP/SNI/CF) |
|----------|------------|--------------|-----------|------------------------|
| MegaFon | | | | |
| MTS | | | | |
| Beeline | | | | |
| Tele2 | | | | |

**Команды smoke на сервере:**
```bash
# Полный pre-flight + init журнала (рекомендуется)
bash /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_phone_drill.sh full

# Или по шагам:
bash /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_phone_drill.sh preflight
python3 /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_phone_drill_init_journal.py
python3 /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_cdn_phase_decision.py

# С Mac (rsync + remote run):
./telegram_stars_shop_bot/scripts/run_vpn_phone_drill.sh preflight

# Contabo (legacy)
python3 /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_prod_smoke.py
python3 /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_bridge_hop_smoke.py
python3 /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_cdn_health.py
bash /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_dns_verify.sh

# MAIN
systemctl is-active xray-bridge wg-quick@wg-bridge
```

**Runbook:** `aladdin_shop_vpn_api/deploy/VPN_PHONE_DRILL_RUNBOOK.md`  
**Pre-flight infra (2026-07-01):** ✅ smoke 10/10, bridge+WG active, CDN DNS фаза 2, журнал инициализирован — **ждёт заполнения с телефона**.

### 5.2 `vpn-domain-com` — зеркало подписки

**Зачем:** если заблокируют `aladdin-ai.ru`, пользователь сможет Update подписки по `.com`.

**Не для:** скорости VPN.

**Схема (из master plan):**
```
PRIMARY:  https://aladdin-ai.ru/sub/<token>
MIRROR:   https://subs.aladdin-ai.com/sub/<token>  (в боте — вторая кнопка)
```

**Шаги:**
1. DNS `subs.aladdin-ai.com` → Cloudflare orange → origin Contabo `:8091` или MAIN nginx `/sub/`
2. nginx `location /sub/` proxy_pass (тот же что для `.ru`)
3. Кнопка в боте «Зеркало подписки (.com)»
4. Мониторинг HTTP 200 обоих URL каждые 5 мин

**Документы:** `AIMONKEY_MASTER_PLAN_2026-06-30.md` §5.1, `VPN_PUBLIC_SURFACE_REGISTRY.md`

### 5.3 `vpn-ux-auto` (vpn-78)

**Цель:** одна кнопка Connect; клиент/сервер выбирает профиль.

| Сеть | Логика |
|------|--------|
| Wi‑Fi | direct (vision когда rollout) |
| 4G | direct → fallback мост → fallback CDN |

**Файлы:** `subscription_util.py`, бот `vpn.py`, `vpn_user_links.py`  
**Зависимость:** стабильные профили после drill + vision rollout decision

### 5.4 `vpn-rkn-mitigation`

| Часть | Статус | Действие |
|-------|--------|----------|
| ч.1 Мониторинг реестра | ⏳ | Cron/check реестра РКН + алерт в ops |
| ч.2 Playbook | ⏳ | Runbook при блокировке `.ru` / `vpn.*` |

**Связь с `vpn-domain-com`:** зеркало `.com` — страховка при блокировке primary.

### 5.5 Хвосты (не забыть)

| Хвост | Действие |
|-------|----------|
| Stars auto-fulfill TON | Пополнить iStar wallet (порог 20 TON) |
| Vision rollout | После drill: `VPN_SUBSCRIBE_DIRECT_VISION_MODE=all` или расширить staging TIDs |
| `BOT_SINGLE_INSTANCE_CANON.md` | Устарел про MAIN partner-api — на MAIN они **disabled** |
| Phase A п.5 RKN monitor | Не начат |

---

## 6. Скрипты деплоя (шпаргалка)

### Shop bot (Contabo)

```bash
cd telegram_stars_shop_bot
./scripts/deploy_prod.sh
./scripts/verify_single_bot.sh
./scripts/apply_shop_ssot_cleanup.sh   # если снова разъехались MAIN/Contabo
```

### VPN API (Contabo)

```bash
rsync -az --exclude venv --exclude var --exclude env \
  aladdin_shop_vpn_api/ root@185.225.233.150:/opt/aladdin-shop-vpn-api/
ssh root@185.225.233.150 'systemctl restart aladdin-shop-vpn-api'
python3 /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_prod_smoke.py
```

### VPN фичи (уже применены, для повтора)

| Скрипт | Что делает |
|--------|------------|
| `apply_direct_vision_staging.sh` | Vision :8446 + staging env |
| `apply_bridge_tcp_vision.sh` | Мост TCP+Vision MAIN+env |
| `apply_wg_internal_bridge.sh` | WG 10.10.0.x + hop internal |
| `apply_cdn_sni_fix.sh` | SNI cloudflare.com в CDN |
| `apply_cdn_cf_orange.sh` | Только при `VPN_CDN_CF_ORANGE=1` |

### MAIN bridge

```bash
ssh root@149.154.65.180 'systemctl is-active xray-bridge wg-quick@wg-bridge'
# hop должен быть 10.10.0.2:8446
python3 -c "import json; c=json.load(open('/opt/xray-bridge/config.json')); print(c['outbounds'][0]['settings']['vnext'][0])"
```

---

## 7. Тестовый пользователь

| Поле | Значение |
|------|----------|
| Telegram ID | `493897224` |
| WG IP | `10.8.0.10` |
| Xray UUID | `bed682e6-1726-419b-b45b-e8e891de7b7b` |
| Vision staging | Да (direct → :8446) |

**Проверка подписки:**
```bash
ssh root@185.225.233.150
TOKEN=$(sqlite3 /opt/aladdin-shop-vpn-api/var/vpn.db \
  "SELECT opaque_token FROM vpn_accounts WHERE telegram_user_id=493897224")
curl -s "http://127.0.0.1:8091/sub/${TOKEN}?plain=1"
```

---

## 8. Репозиторий — ключевые файлы

### Shop bot
`ALADDIN_NEW/mobile_apps/ALADDIN_iOS/telegram_stars_shop_bot/`

| Файл | Назначение |
|------|------------|
| `docs/AIMONKEY_MASTER_PLAN_2026-06-30.md` | Сводный план |
| `docs/BOT_SINGLE_INSTANCE_CANON.md` | Один бот (частично устарел про MAIN API) |
| `bot/products.yaml` | Stars витрина |
| `bot/services/vpn_ops_health.py` | Ops алерты |
| `scripts/deploy_prod.sh` | Деплой |
| `scripts/apply_shop_ssot_cleanup.sh` | SSOT cleanup |

### VPN API
`ALADDIN_NEW/mobile_apps/ALADDIN_iOS/aladdin_shop_vpn_api/`

| Файл | Назначение |
|------|------------|
| `aladdin_shop_vpn_api/subscription_util.py` | Генерация 4 профилей `/sub/` |
| `aladdin_shop_vpn_api/settings.py` | Env VPN |
| `deploy/VPN_CDN_DNS_PHASE_CHECKLIST.md` | **CDN фазы DNS↔порт** |
| `deploy/scripts/vpn_prod_smoke.py` | Smoke 10/10 |
| `deploy/scripts/vpn_phone_drill.sh` | G4 drill pre-flight + journal |
| `deploy/VPN_PHONE_DRILL_RUNBOOK.md` | Пошаговый drill с телефона |

---

## 9. Верификация после любых изменений

```bash
# 1. Один бот
./telegram_stars_shop_bot/scripts/verify_single_bot.sh

# 2. VPN smoke
ssh root@185.225.233.150 'python3 /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_prod_smoke.py'

# 3. Bridge + WG
ssh root@149.154.65.180 'systemctl is-active xray-bridge wg-quick@wg-bridge; wg show wg-bridge'

# 4. Курс (Contabo)
ssh root@185.225.233.150 'grep USD_RUB_RATE /opt/aladdin-telegram-shop-bot/shared/.env'

# 5. Нет ConflictError
ssh root@185.225.233.150 'journalctl -u aladdin-telegram-bot -n 50 --no-pager | grep -i conflict || echo OK'
```

---

## 10. Связанные документы (читать по задаче)

| Задача | Документ |
|--------|----------|
| CDN фазы | `aladdin_shop_vpn_api/deploy/VPN_CDN_DNS_PHASE_CHECKLIST.md` |
| CDN CF | `aladdin_shop_vpn_api/deploy/VPN51_CLOUDFLARE_CDN_SPRINT3.md` |
| Мост/CDN инциденты | `aladdin_shop_vpn_api/deploy/VPN70_BRIDGE_CDN_PLAYBOOK.md` |
| Один бот | `telegram_stars_shop_bot/docs/BOT_SINGLE_INSTANCE_CANON.md` |
| Старый VPN UX handoff | `telegram_stars_shop_bot/docs/VPN_FULL_SESSION_HANDOFF_ML_2026-06-27.md` |
| Архитектура VPN | `telegram_stars_shop_bot/docs/VPN_RESILIENT_ARCHITECTURE_PLAN_2026.md` |

---

## 11. Резюме для следующего агента (одним абзацем)

Продукт **AiMonkey** — Telegram shop bot + VPN на двух серверах: **Contabo (EU, SSOT)** и **MAIN (РФ, мост + nginx)**. Бот polling **только Contabo**. VPN: 4 профиля в подписке; мост уже **TCP+Vision** с hop через **WG internal `10.10.0.2:8446`** (не использовать `10.9.0.x`!). CDN сейчас **фаза 2**: DNS→MAIN, порт **8445** — **не менять на 443** без Cloudflare orange. Vision на direct — **staging** для TID 493897224. **Следующий шаг:** G4 drill на 4 операторах → решение по CDN DNS → `vpn-domain-com` → `vpn-ux-auto`. Stars auto-fulfill ждёт пополнения TON.

---

*Обновлять этот файл при закрытии каждой задачи Фазы C.*
