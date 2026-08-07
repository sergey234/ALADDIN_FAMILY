# VPN — полный handoff для ML-системы (сессия 2026-06-25 … 2026-06-27)

**Назначение:** единый документ для другой ML-системы / агента: что выяснили, что сломалось у пользователей, что исправили на сервере и в боте, как **правильно** настроить VPN для конечных пользователей, что ещё сделать для «идеального» UX.

**Бот в проде:** `@AiMonkeyStars_bot`  
**Канон миграции:** `docs/SHOP_VPN_MIGRATION_CONTABO_MASTER_PLAN.md` (v2.2)  
**Предыдущий handoff:** `docs/VPN_ML_SYSTEM_HANDOFF.md` (операционный, до UX-сессии)  
**Публичные URL/порты:** `docs/VPN_PUBLIC_SURFACE_REGISTRY.md` (нужно дополнить OpenVPN TCP 443)

---

## 0. Executive summary (30 секунд)

| Факт | Значение |
|------|----------|
| Сервер VPN | **Contabo** `185.225.233.150`, endpoint `vpn.aladdin-ai.ru` |
| Публичный HTTPS (подписка, legal) | **MAIN** `149.154.65.180` → nginx proxy на Contabo `:8091` |
| Три способа подключения | **Xray** (VLESS+Reality) · **OpenVPN** · **WireGuard** — один тариф |
| Лучший на 4G в РФ | **Xray** + клиент с VLESS (v2rayNG на Android; на iOS — проблема App Store) |
| Лучший без Xray-клиента | **OpenVPN Connect** + файл `.ovpn` (**TCP 443**, затем UDP 1194) |
| WireGuard | Работает чаще на **Wi‑Fi**; на **4G в РФ** часто блокируется |
| Главная ошибка пользователей | Путать **v2RayVPN** (RU Store) с **v2RayTun**; вставлять `/sub/` в WireGuard/OpenVPN |
| Критичные прод-фиксы сессии | QR-кнопка (v2raytun://), дубликат бота на MAIN, OpenVPN TCP 443, кнопка выдачи `.ovpn` |

---

## 1. Архитектура (два сервера)

```
Пользователь
    │
    ├─ Telegram ──► Contabo :8090  Shop Bot + Partner API
    │
    ├─ https://aladdin-ai.ru/sub/<token>  ──► MAIN nginx ──► Contabo :8091  vpn-api
    │
    └─ VPN трафик ──► vpn.aladdin-ai.ru (185.225.233.150)
            ├─ Xray VLESS+Reality     TCP 8443
            ├─ OpenVPN UDP            UDP 1194
            ├─ OpenVPN TCP (NEW)        TCP 443   ← добавлено 2026-06-27
            └─ WireGuard                UDP 51820
```

**Shop Bot (systemd):** только на **Contabo** — `aladdin-telegram-bot.service`  
**Важно:** на **MAIN** (`149.154.65.180`) бот **должен быть остановлен и disabled** — иначе `TelegramConflictError` и кнопки работают «через раз».

Проверка:
```bash
ssh aladdin-contabo 'systemctl is-active aladdin-telegram-bot && pgrep -af bot.main'
ssh aladdin-server 'systemctl is-active aladdin-telegram-bot; pgrep -af bot.main || echo OK:none'
```

---

## 2. Три «VPN-провайдера» внутри продукта (протоколы)

Это **не** внешние провайдеры — три транспорта **на одном** Contabo-сервере.

### 2.1 Xray (VLESS + Reality) — профиль B, **№1 для 4G**

| Параметр | Значение |
|----------|----------|
| Порт | TCP **8443** на `vpn.aladdin-ai.ru` |
| Подписка | `https://aladdin-ai.ru/sub/<opaque_token>` (base64 тело, профили `#default`, `#mobile-rf`) |
| Выдача | После оплаты `opaque_token` в `vpn.db`; бот — кнопки CopyText + QR |
| Профиль для 4G | **`mobile-rf`** в подписке (отдельная VLESS-строка) |

**Проверено на сервере (OK):**
- `GET /sub/<token>` → 200, base64, две vless-линии
- Xray active, Reality public key совпадает с подпиской

**Клиенты (матрица):**

| Приложение | Платформа | Работает? | Комментарий |
|------------|-----------|-----------|-------------|
| **v2rayNG** | Android | ✅ Да | Google Play, Import / subscription URL |
| **v2RayTun** | iOS | ⚠️ Зависит | Часто **нет в RU App Store** — нужен Apple ID другого региона |
| **Happ** | iOS/Android | ⚠️ У части пользователей | В RU Store удалён; у кого уже стоит — может работать |
| **V2Box, Streisand, Shadowrocket** | iOS | ⚠️ Редко в RU Store | Shadowrocket — платный, foreign Apple ID |
| **v2RayVPN** | Android (RU Store) | ❌ **Нет** | `unsupported URL`, `fail to parse` — **не поддерживает VLESS/Reality** |
| **OpenVPN Connect** | iOS/Android | ❌ для `/sub/` | Нужен **файл `.ovpn`**, не ссылка подписки |
| **WireGuard** | iOS/Android | ❌ для `/sub/` | Нужен **`.conf` / WG-QR** |

**Типичные ошибки пользователя:**

| Действие | Ошибка | Причина |
|----------|--------|---------|
| Вставить `https://aladdin-ai.ru/sub/…` в v2RayVPN | fail to parse | Не тот клиент |
| Вставить `vless://…#mobile-rf` в v2RayVPN | Network error unsupported URL | Нет схемы `vless://` |
| Вставить `t.me/…?start=ref_…` | не VPN | Реферальная ссылка |
| Вставить `/sub/` в OpenVPN / WireGuard | не работает | Другой формат ключей |

---

### 2.2 OpenVPN — профиль B fallback, **№2 (без Xray-клиента)**

| Параметр | Значение |
|----------|----------|
| Сервер UDP | `openvpn-server@server` — UDP **1194** |
| Сервер TCP (**NEW 2026-06-27**) | `openvpn-server@server-tcp` — TCP **443** |
| Endpoint в `.ovpn` | `vpn.aladdin-ai.ru` |
| Пул | UDP: `10.9.0.0/24` (tun0), TCP: `10.9.1.0/24` (tun1) |
| Выдача | `POST /internal/v1/ovpn/conf` → `openvpn-client-issue.sh` → `var/ovpn-profiles/{telegram_user_id}.ovpn` |
| Приложение | **OpenVPN Connect** (App Store / Google Play — **есть в РФ**) |

**Что выяснили на проде (пользователь tid `493897224`):**

Симптом: файл `.ovpn` загружается, в OpenVPN Connect — **`Connection timeout`**, `lost connection to server`.

Логи сервера (`journalctl -u openvpn-server@server`):
```
VERIFY OK: CN=aladdin-vpn-493897224
TLS Error: TLS key negotiation failed to occur within 60 seconds
TLS handshake failed
```

**Интерпретация:** клиент **достучался** до сервера (сертификат проверен), но **UDP 1194 на 4G в РФ** режется/блокируется оператором — handshake не завершается. Это **не** битый `.ovpn` и **не** ошибка CA.

**Исправление 2026-06-27:**
1. Поднят второй инстанс OpenVPN: **`server-tcp.conf`**, `proto tcp`, `port 443`, unit `openvpn-server@server-tcp`.
2. UFW: `443/tcp` allow.
3. Скрипт выдачи клиента обновлён: в `.ovpn` два блока `<connection>` — **сначала TCP 443**, потом UDP 1194.
4. Исправлен WAN в `up.sh`: `ens3` → **`eth0`** (на Contabo интерфейс `eth0`).
5. Generic up/down scripts для tun1 с subnet `10.9.1.0/24`.

**Файл `.ovpn` (актуальный формат):**
```
<connection>
proto tcp-client
remote vpn.aladdin-ai.ru 443
</connection>
<connection>
proto udp
remote vpn.aladdin-ai.ru 1194
</connection>
```

**Инструкция пользователю:** удалить старый профиль в OpenVPN Connect → скачать `.ovpn` заново из бота.

---

### 2.3 WireGuard — профиль A, **№3**

| Параметр | Значение |
|----------|----------|
| Порт | UDP **51820** на `vpn.aladdin-ai.ru` |
| Выдача | `POST /internal/v1/wg/conf` → `.conf`; QR через `wg_qr_util` |
| DNS в конфиге | `10.8.0.1, 8.8.8.8` (dnsmasq на wg0) |
| MTU | 1280 (настраиваемо) |

**Ранее в сессии:** «подключается, но страницы не грузятся» — фиксы NAT, dnsmasq на `10.8.0.1`, DNS в клиентском conf.

**Ограничение:** на **4G в РФ** WireGuard часто **не проходит DPI** — в боте явно указано «лучше на Wi‑Fi».

---

## 3. Telegram-бот: UX и изменения кода

### 3.1 Приоритет способов (продуктовое решение)

1. **Xray** — «📱 iPhone» / «🤖 Android», «📋 Ссылка VPN», «📷 QR + v2RayTun»
2. **OpenVPN** — «🧱 OpenVPN (файл)»
3. **WireGuard** — «📥 WireGuard — файл» / «📷 WireGuard — QR»

Меню: `/vpn` → «🔀 Способы подключения».

### 3.2 Ключевые файлы бота

| Файл | Назначение |
|------|------------|
| `bot/services/vpn_connect_copy.py` | Все HTML-тексты инструкций |
| `bot/services/vpn_user_links.py` | CopyText «📋 Ссылка VPN», кнопка QR |
| `bot/services/vpn_xray_delivery.py` | QR фото + VLESS текст |
| `bot/handlers/vpn.py` | Callbacks, выдача WG/OVPN |
| `bot/services/vpn_ops_health.py` | Алерты ops (false positive fix) |
| `bot/services/vpn_api_client.py` | HMAC к vpn-api |

### 3.3 Баги бота — найдено и исправлено

| # | Симптом | Root cause | Fix | Деплой |
|---|---------|------------|-----|--------|
| 1 | «📷 QR + v2RayTun» — нажатие, ничего не приходит | Inline-кнопка `v2raytun://import/…` → Telegram `Unsupported URL protocol` → `answer_photo` падает | Убрать URL-кнопки; CopyText + QR только | `20260627-015740` |
| 2 | Кнопки VPN «то есть, то нет» | Два процесса `bot.main`: Contabo + **MAIN** | `systemctl stop/disable aladdin-telegram-bot` на MAIN | ops 2026-06-27 |
| 3 | «🧱 OpenVPN» — только текст, файла нет | Callback `vpn:fallback:openvpn` = инструкция; `vpn:ovpn:download` не был на кнопке | Кнопка → `vpn:ovpn:download` | `20260627-022603` |
| 4 | CRITICAL VPN ops health каждые ~5 мин | `/ready` transient fail = critical сразу | Retries, streak, degraded vs critical | `20260627-010803` |

### 3.4 Кнопка «📷 QR + v2RayTun» — когда видна

Только при **`vpn_active`** и наличии subscription URL:
- `append_vpn_copy_link_rows()` в главном `/vpn`
- `subscription_link_reply_kb()` после выдачи ссылки

Callback: `vpn:xray:qr` → `send_xray_import_pack()`.

**Ожидаемое поведение после фикса:**
1. Toast «Отправляю QR…»
2. Фото QR подписки `/sub/…`
3. Текст VLESS `mobile-rf` + второй QR
4. Кнопки CopyText (не v2raytun://)

---

## 4. VPN API — изменения

| Файл | Изменение |
|------|-----------|
| `subscription_util.py` | Base64 тело `/sub/` по умолчанию |
| `routes/health.py` | `/sub/` headers `profile-title`, `profile-update-interval`; `?plain=1` |
| `settings.py` | `VPN_SUBSCRIBE_BODY_BASE64=true` |
| `deploy/scripts/openvpn-client-issue.sh` | Dual `<connection>` TCP 443 + UDP 1194 |

**Подписка (пример admin test user):**
- tid: `493897224`
- token: `9R8T1iCLEULlrGmdTw4IQm2dFXfE8zOx`
- URL: `https://aladdin-ai.ru/sub/9R8T1iCLEULlrGmdTw4IQm2dFXfE8zOx`

---

## 5. Состояние прод-сервисов (2026-06-27)

Contabo — все **active**:
- `aladdin-telegram-bot`
- `aladdin-shop-vpn-api`
- `openvpn-server@server` (UDP 1194)
- `openvpn-server@server-tcp` (TCP 443)
- `xray` (8443)
- `wg0` (51820)

MAIN:
- `aladdin-telegram-bot` — **inactive** (правильно)

**Последние релизы бота:** `20260627-015740` (QR fix), `20260627-022603` (OpenVPN button + caption).

---

## 6. Рекомендуемые пути для пользователя (playbook)

### 6.1 iPhone, только RU App Store (без v2RayTun/Happ)

**Рекомендация №1:** OpenVPN Connect + `.ovpn` из бота (TCP 443).

Шаги:
1. `/vpn` → 🔀 Способы → 🧱 OpenVPN (файл)
2. Удалить старый профиль в OpenVPN Connect
3. Открыть новый `.ovpn` → Connect
4. Проверка: `https://ifconfig.me` — IP не RU

**Рекомендация №2 (Wi‑Fi):** WireGuard файл или QR.

### 6.2 Android

**Рекомендация №1:** v2rayNG + «📋 Ссылка VPN» или QR.  
**Рекомендация №2:** OpenVPN Connect (как iPhone).  
**Не рекомендовать:** v2RayVPN из RU Store.

### 6.3 На 4G vs Wi‑Fi

| Сеть | Предпочтительно | Запасное |
|------|-----------------|----------|
| **4G/5G РФ** | Xray + v2rayNG / foreign iOS client | **OpenVPN TCP 443** |
| **Wi‑Fi** | Xray или WireGuard | OpenVPN UDP/TCP |

---

## 7. Что сделать для «идеального» UX (backlog для ML)

### P0 — критично для пользователей

| ID | Задача | Детали |
|----|--------|--------|
| P0-1 | **Smoke OpenVPN TCP 443 с 4G** | Ручной тест iPhone + Android; зафиксировать в `VPN_QUARTERLY_DRILL_CHECKLIST.md` |
| P0-2 | **Закрепить MAIN bot stopped** | Ansible/cron или документ «после любого деплоя MAIN — bot inactive» |
| P0-3 | **Обновить `VPN_PUBLIC_SURFACE_REGISTRY.md`** | Добавить OpenVPN TCP 443, unit `server-tcp` |
| P0-4 | **Тексты бота без v2RayTun/Happ для RU-only** | Отдельная ветка copy: «OpenVPN первый для iPhone RU» — продуктовое решение |
| P0-5 | **Переименовать кнопку QR** | «📷 QR + v2RayTun» вводит в заблуждение → «📷 QR подписки (Xray)» |

### P1 — качество и поддержка

| ID | Задача |
|----|--------|
| P1-1 | Автотест: `xray_import_reply_kb` без `url=` кнопок |
| P1-2 | Интеграционный smoke: `post_ovpn_conf` + проверка `<connection>` TCP 443 |
| P1-3 | `openvpn-install.sh` — включить TCP 443 и `eth0` по умолчанию (сейчас hotfix только на проде) |
| P1-4 | Ops: алерт если на MAIN снова `bot.main` |
| P1-5 | Legal `vpn-instructions.md` — OpenVPN TCP 443, матрица клиентов |

### P2 — стратегия обхода блокировок

| ID | Задача |
|----|--------|
| P2-1 | **vpn-30** — egress VPS вне РФ (`VPN_EGRESS_NODES_JSON`) |
| P2-2 | Xray на 443 / xHTTP transport если mobile-rf перестанет работать |
| P2-3 | Внешний мониторинг с 4G (`VPN32`) |
| P2-4 | Clash/sing-box форматы подписки — только при спросе |

---

## 8. Деплой (канон для агента)

```bash
# Bot → Contabo
TS=$(date +%Y%m%d-%H%M%S)
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
ssh aladdin-contabo "mkdir -p /opt/aladdin-telegram-shop-bot/releases/${TS}/telegram_stars_shop_bot"
rsync -az --delete -e "ssh -i ~/.ssh/aladdin_server" \
  --exclude '__pycache__' --exclude 'data' --exclude '.env' \
  telegram_stars_shop_bot/ aladdin-contabo:/opt/aladdin-telegram-shop-bot/releases/${TS}/telegram_stars_shop_bot/
ssh aladdin-contabo "
  ln -sfn /opt/aladdin-telegram-shop-bot/releases/${TS} /opt/aladdin-telegram-shop-bot/current_release
  ln -sfn /opt/aladdin-telegram-shop-bot/releases/${TS}/telegram_stars_shop_bot /opt/aladdin-telegram-shop-bot/current_app
  systemctl restart aladdin-telegram-bot aladdin-partner-api aladdin-webhook-worker
"

# VPN API + openvpn scripts
rsync -az -e "ssh -i ~/.ssh/aladdin_server" \
  aladdin_shop_vpn_api/deploy/scripts/openvpn-client-issue.sh \
  aladdin-contabo:/opt/aladdin-shop-vpn-api/deploy/scripts/
```

Полный канон: `docs/ML_SYSTEM_HANDOFF_FINAL.md`.

---

## 9. Диагностика (шпаргалка)

### Пользователь: «ссылка не работает»
1. Какое приложение? (v2RayVPN → сразу объяснить несовместимость)
2. Какая ссылка? (`/sub/` vs `vless://` vs `ref_` vs `.ovpn`)
3. iPhone/Android, 4G или Wi‑Fi?

### Пользователь: OpenVPN timeout
```bash
ssh aladdin-contabo 'journalctl -u openvpn-server@server -u openvpn-server@server-tcp -n 30 --no-pager'
ssh aladdin-contabo 'systemctl is-active openvpn-server@server-tcp && ss -tlnp | grep :443'
```
- VERIFY OK + TLS timeout 60s → блокировка UDP → нужен **новый .ovpn с TCP 443**
- Нет строк в логе → DNS/firewall клиента или неверный host

### Бот не отвечает на callback
```bash
ssh aladdin-contabo 'grep -E "Conflict|TelegramBadRequest|vpn_xray" /opt/aladdin-telegram-shop-bot/logs/bot.log | tail -20'
ssh aladdin-server 'pgrep -af bot.main || echo OK'
```

### Health VPN API
```bash
ssh aladdin-contabo 'curl -sS http://127.0.0.1:8091/health; echo; curl -sS http://127.0.0.1:8091/ready'
```

---

## 10. Связанные документы

| Документ | Зачем |
|----------|-------|
| `docs/SHOP_VPN_MIGRATION_CONTABO_MASTER_PLAN.md` | 36 задач mig-00…mig-35 |
| `docs/VPN_PUBLIC_SURFACE_REGISTRY.md` | Порты, домены |
| `docs/VPN_SHOP_API.md` | HMAC API |
| `docs/VPN_TASKS_STATUS.md` | Статус vpn-00… |
| `docs/VPN_UX_SMOKE_CHECKLIST.md` | Ручной smoke |
| `aladdin_shop_vpn_api/deploy/VPN06_OPENVPN_FALLBACK_RUNBOOK.md` | OpenVPN (обновить TCP 443) |
| `aladdin_shop_vpn_api/deploy/VPN05B_MOBILE_RF_RUNBOOK.md` | mobile-rf профиль |
| `docs/VPN_ML_SYSTEM_HANDOFF.md` | Операционный handoff (metrics, env) |

---

## 11. Версия

| Дата | Автор / контекст | Изменение |
|------|------------------|-----------|
| 2026-06-27 | UX + prod incident session | Первый полный handoff: клиенты, баги бота, OpenVPN TCP 443, playbook пользователя, backlog P0–P2 |

**Следующий агент:** начать с **§7 P0-1** (smoke OpenVPN 4G) и **§6** (playbook под платформу пользователя). Не предлагать v2RayVPN. На iPhone без foreign Apple ID — **OpenVPN Connect первым**.
