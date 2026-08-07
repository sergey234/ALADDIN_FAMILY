# AiMonkey VPN — диагностика Happ iOS + план до 100% (handoff ML)

**Дата:** 2026-07-01  
**Сессия:** разбор логов пользователя (Downloads), сверка с journal на MAIN/Contabo, сравнение с Щука VPN  
**Читать первым:** этот файл → `docs/AIMONKEY_ML_HANDOFF_2026-06-30.md` → `aladdin_shop_vpn_api/deploy/VPN_PHONE_DRILL_RUNBOOK.md`

**Бот:** `@AiMonkeyStars_bot`  
**Тестовый TID:** `493897224` (staging vision + ux-auto)  
**SSH-ключ:** `~/.ssh/aladdin_server`  
**Happ (iOS):** App Store id `6783623643` (чёрный квадрат с «H», Happ - Proxy Utility+)

---

## 0. START HERE (2 минуты)

### Вердикт одной фразой

> **В 13:25 сервер и мост отрабатывали gstatic и hop на Contabo; на iPhone Happ перегрузился по памяти (47.91 MB), VPN выключился в 13:24 (`configurationDisabled`); после 13:26 в логах нет активного туннеля. Чинить нужно продукт («Авто» = мост) + клиент (сброс Happ), а не «поднимать сервер заново».**

### Что доказано фактами (не гипотеза)

| Утверждение | Доказательство |
|-------------|----------------|
| Сервер жив | `vpn_prod_smoke.py` **10/10 PASS** (2026-07-01) |
| Мост + hop жив | journal MAIN 13:25: `contabo-hop → 10.10.0.2:8446 → tunneling OK` |
| Round-trip через мост | `VISION_E2E_OK 204` с Contabo (tcp+vision, не xhttp) |
| Подписка отдаётся | HTTP 200, 3 профиля, 1004 байт |
| «Авто» ведёт на зарубеж | `vpn.aladdin-ai.ru:8446` в живой `/sub/` |
| Обрыв у пользователя | `MEMORY WARNING 47.91 MB`, `configurationDisabled`, нет tunnel после 13:26 |

### Что НЕ сделано (блокер UX «работает везде без танцев»)

| # | Задача | Статус |
|---|--------|--------|
| P0 | **«Авто-подключение» = мост** (`149.154.65.180:8444`), не `:8446` Contabo | ✅ 2026-07-01 |
| P0 | **Мост первым** в `/sub/` | ✅ |
| P1 | Бот: убрать «на 4G: Авто → Мост → CDN» | ✅ |
| P1 | `vpn_bridge_reality_e2e_smoke.py` → tcp+vision (сейчас xhttp, ложный FAIL) | ✅ |
| P0+ | **MTU/MSS clamp** wg-bridge MAIN+Contabo (`apply_wg_hop_mss_clamp.sh`) | ✅ 2026-07-01 |
| P0+ | **ux-auto: один профиль** (CDN xhttp убран из `/sub/`) | ✅ 2026-07-01 |
| P2 | Логи успешных сессий по UUID на `:8444` | ⚠️ access.log есть |
| P2 | CDN фаза 3 (CF orange :443) | ❌ после drill |

### Порядок работ следующего агента

1. **Реализовать P0** в `subscription_util.py` + деплой VPN API + проверить `/sub/` на TID 493897224.
2. **Обновить тексты бота** (`vpn_connect_copy.py`) + `deploy_prod.sh`.
3. **Починить e2e smoke** (мониторинг).
4. **Phone drill** по `VPN_PHONE_DRILL_RUNBOOK.md` — только после P0.
5. **Не** включать `VPN_SUBSCRIBE_UX_AUTO_MODE=all` для всех, пока drill на МегаФон ≥1 Мбит/с 5 мин не пройден.

---

## 1. Архитектура (что видит пользователь vs «кухня»)

### Пользователь (только Happ)

```
iPhone (Happ) → один профиль из /sub/ → кнопка «Подключить»
```

### Серверная цепочка (невидима в Happ)

```
Телефон (Happ, VLESS)
    ↓
MAIN 149.154.65.180:8444  «Мобильный мост» (первый хоп РФ)
    ↓  contabo-hop (xray outbound на MAIN)
WG туннель 10.10.0.1 ↔ 10.10.0.2  (wg-bridge, ~48 ms)
    ↓
Contabo 185.225.233.150:8446  (vision egress)
    ↓
Интернет (Telegram, Instagram, сайты)
```

**WG hop / contabo-hop** — внутренняя «труба» между MAIN и Contabo. Пользователь её не настраивает. В логах MAIN: `taking detour [contabo-hop] for [tcp:www.gstatic.com:443]`.

### Три профиля в подписке (сейчас на проде, 2026-07-01)

| Порядок | Имя в Happ | Endpoint | Назначение |
|---------|------------|----------|------------|
| **1** | Авто-подключение | `vpn.aladdin-ai.ru:8446` → Contabo EU | **Плохо для МегаФон 4G** — прямой зарубеж |
| 2 | Мобильный мост | `149.154.65.180:8444` | Аналог «белых списков» Щуки — первый хоп РФ |
| 3 | Мобильный CDN | `cdn.aladdin-ai.ru:8445` → MAIN relay | Запас при блокировке IP |

**Критический баг продукта:** Happ по умолчанию цепляет **первый** профиль → пользователь попадает на «Авто» → зарубеж → на 4G «гудки есть, разговора нет».

### Целевое состояние (P0)

| Порядок | Имя | Endpoint |
|---------|-----|----------|
| **1** | **Авто-подключение** | `149.154.65.180:8444` (те же ключи, что «Мобильный мост») |
| 2 | Мобильный CDN | запас |
| (опц.) | Мобильный мост | дубль или убрать после стабилизации |

Один профиль «Авто» = мост → **Wi‑Fi и LTE без переключения** (Happ не умеет сам менять профиль при смене сети).

---

## 2. Инфраструктура SSOT (не ломать)

См. `docs/AIMONKEY_ML_HANDOFF_2026-06-30.md` §1. Кратко:

| Сервер | IP | Роль |
|--------|-----|------|
| MAIN | `149.154.65.180` | nginx :443, xray-bridge :8444, wg-bridge, CDN relay :8445 |
| Contabo | `185.225.233.150` | бот polling, vpn-api :8091, xray :8443/:8446/:8445 |

**Сервисы (проверено 2026-07-01):**

- Contabo: `aladdin-shop-vpn-api` **active**, `xray` **active**
- MAIN: `xray-bridge` **active**, `wg-quick@wg-bridge` **active**
- WG ping `10.10.0.2` с MAIN: **0% loss**, ~48 ms

**Пути:**

| Компонент | Путь |
|-----------|------|
| VPN API env | `/opt/aladdin-shop-vpn-api/env` |
| VPN DB | `/opt/aladdin-shop-vpn-api/var/vpn.db` |
| Xray Contabo | `/opt/xray/config.json` |
| Xray bridge MAIN | `/opt/xray-bridge/config.json` |
| Bot | `/opt/aladdin-telegram-shop-bot/` |

**Критические env (Contabo `/opt/aladdin-shop-vpn-api/env`):**

```bash
VPN_SUBSCRIBE_UX_AUTO_MODE=staging          # staging TID → 3 профиля + «Авто»
VPN_SUBSCRIBE_UX_AUTO_STAGING_TIDS=493897224
VPN_SUBSCRIBE_BRIDGE_ENABLED=true
VPN_BRIDGE_PUBLIC_HOST=149.154.65.180
VPN_BRIDGE_PORT=8444
VPN_SUBSCRIBE_DIRECT_VISION_MODE=staging    # staging → :8446 vision на direct
```

---

## 3. Разбор логов пользователя (2026-07-01)

### Файлы (у пользователя в Downloads)

- `tunnel (3).log`
- `subscriptions (2).log`
- `access (2).log`

### `tunnel (3).log` — жизненный цикл VPN на iPhone

| Время | Событие |
|-------|---------|
| 13:07:49 | Tunnel Start, Happ v4.13.0, `[T2S] skipped (Xray internal TUN path)` |
| 13:07:49 | DNS: DoH → `cloudflare-dns.com` |
| **13:12:49** | **`MEMORY WARNING` — extension memory usage: **47.91** MB** (лимит iOS ~50 MB) |
| 13:15:20 | Stop: `userInitiated` |
| 13:15:32 | Перезапуск туннеля |
| 13:22:12 | Ещё перезапуск |
| **13:24:13** | Stop: **`configurationDisabled`** — VPN выключен системой/пользователем |
| после 13:26 | **Новых сессий нет** |

**Интерпретация:** Network Extension Happ близок к лимиту iOS → нестабильность → VPN отключён. Иконка VPN может кратковременно врать; после 13:26 тесты «ничего не грузит» при выключенном VPN недействительны.

### `subscriptions (2).log`

```
13:26:29 — Updating subscription AiMonkeyVPN
13:26:30 — HTTP 200, servers count: 3, content length: 1004
VPN connection status: disconnected
```

Подписка **загрузилась**, VPN **не был подключён**.

### `access (2).log` — локальный Xray в Happ

- **2131** строк `accepted [tun >> proxy]` (Telegram `149.154.x`, Instagram `157.240.x`, DNS `1.1.1.1`, Yandex `77.88.8.x`)
- **0** строк `error`, `timeout`, `refused`, `failed`

**Важно:** `accepted [tun >> proxy]` = пакет принят **локальным** Xray на телефоне. Это **не** доказательство, что страница открылась или сервер ответил.

### Сопоставление с сервером (та же минута ~13:25 MSK)

**Contabo :8446** (профиль «Авто»):

```
13:25:03 — www.gstatic.com:443 → freedom → 142.251.20.94:443 OPEN
13:25:13 — cloudflare-dns.com:443 → OPEN
13:25:14 — mzstorekit.itunes.apple.com:443 → OPEN
```

**MAIN :8444** (профиль «Мобильный мост»):

```
13:25:14 — gstatic → contabo-hop → 10.10.0.2:8446 → tunneling OK
13:25:23 — то же
13:25:32 — то же
```

**Вывод:** в окне 13:20–13:25 телефон **достучался до сервера** по обоим путям; сервер **вышел в интернет**. Ошибок EOF/mux/reset на Contabo за 13:07–13:30 **нет**.

### Ранние сессии (контекст из прошлых логов)

| Сессия | Режим | Результат |
|--------|-------|-----------|
| ~10:28 | `socks-in >> proxy` | Работало |
| 11:20–11:39 | `tun >> proxy`, gstatic timeout, Code **-12** | Краш по памяти |
| 13:07–13:25 | tun + MEMORY WARNING | Сервер OK, клиент деградировал |
| 14:28–15:38 (скрины) | «Авто», 0 b | Другая сессия; в access за 14:xx записей не было |

---

## 4. Таблица гипотез (проверено разными способами)

| Гипотеза | Как проверяли | Результат |
|----------|---------------|-----------|
| Сервер мёртв | `systemctl`, `vpn_prod_smoke.py` | **Опровергнута** — 10/10 |
| Мост не поднят | `systemctl xray-bridge`, `ss :8444` | **Опровергнута** — active |
| WG hop мёртв | `ping 10.10.0.2` с MAIN | **Опровергнута** — 0% loss |
| Неверные ключи моста | sub line ↔ `/opt/xray-bridge/config.json` | **Опровергнута** — pbk/sid/sni совпадают |
| Мост не пропускает трафик | journal 13:25 + `VISION_E2E_OK 204` | **Опровергнута** |
| Обрыв на сервере | journal EOF/errors 13:07–13:30 | **Опровергнута** — чисто |
| «Авто» = зарубеж :8446 | `curl /sub/?plain=1` | **Подтверждена** — баг продукта |
| Happ OOM / нестабилен | `tunnel (3).log` 47.91 MB | **Подтверждена** |
| VPN выключен | `configurationDisabled` 13:24 | **Подтверждена** |
| Сканеры ломают мост | 6024× `invalid connection` от `178.178.210.38` | Шум, не сессия 13:25 |
| `vpn_bridge_reality_e2e_smoke` FAIL | скрипт на xhttp | **Ложная тревога** — мост на tcp+vision; ручной vision E2E OK |

---

## 5. Где обрывается (схема)

```
[Телефон Happ]  --✅ пакеты уходят (access accepted)-->
[Сервер РФ или Contabo]  --✅ gstatic, DNS, hop (journal)-->
[Интернет]  --✅ freedom/tunneling OPEN-->
[Ответ обратно на телефон]  --❓ при OOM/битой сессии может не дойти-->
[Happ UI]  --❌ 0 b, страницы не открываются; MEMORY WARNING; VPN off
```

| Уровень | 13:25 | Доказательство |
|---------|-------|----------------|
| `/sub/` | ✅ | HTTP 200, 3 профиля |
| Contabo egress | ✅ | gstatic/apple OPEN |
| Мост + hop | ✅ | contabo-hop tunneling |
| Happ локально | ⚠️ | accepted, но 47.91 MB |
| VPN активен | ❌ с 13:24 | configurationDisabled |

---

## 6. План до 100% — реализация (для ML-агента)

### P0-A. «Авто» = мост в `subscription_util.py`

**Файл:** `aladdin_shop_vpn_api/aladdin_shop_vpn_api/subscription_util.py`

**Сейчас (строки 310–326):** при `use_ux_auto` профиль «Авто» строится из `subscription_values_mobile(..., use_direct_vision=True)` → **Contabo :8446**.

**Нужно:**

1. При `use_ux_auto` и `_bridge_profile_enabled(settings)`:
   - `auto_values = subscription_values_bridge(...)`
   - `bridge_template` для строки «Авто-подключение»
2. **Порядок в `lines`:**
   - сначала «Авто» (= мост)
   - затем CDN (если enabled)
   - «Мобильный мост» — опционально вторым дублем или убрать из UX-текстов
3. Добавить тест в `aladdin_shop_vpn_api/tests/test_egress_and_subscription.py`:
   - ux_auto + bridge enabled → первая строка содержит `149.154.65.180:8444` и `#Авто-подключение`
   - **не** содержит `:8446` в auto-строке

**Псевдокод:**

```python
if use_ux_auto:
    if _bridge_profile_enabled(settings):
        auto_values = subscription_values_bridge(...)
        auto_template = bridge_template or base_template
    else:
        auto_values = subscription_values_mobile(..., use_direct_vision=use_vision)
        auto_template = base_template
    lines.append(_build_profile_line(..., profile_name=auto_name))
# bridge block: не дублировать идентичную строку, или оставить как fallback #2
```

### P0-B. Деплой VPN API

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS/aladdin_shop_vpn_api
# rsync на Contabo (см. deploy/scripts/apply_vpn_ux_auto.sh)
ssh -i ~/.ssh/aladdin_server root@185.225.233.150 \
  'systemctl restart aladdin-shop-vpn-api'
```

**Проверка:**

```bash
TOKEN=$(ssh ... 'sqlite3 /opt/aladdin-shop-vpn-api/var/vpn.db \
  "SELECT opaque_token FROM vpn_accounts WHERE telegram_user_id=493897224"')
ssh ... "curl -s 'http://127.0.0.1:8091/sub/${TOKEN}?plain=1'" | \
  python3 -c "import sys; [print(l.split('#')[-1], '->', l.split('@')[1].split('?')[0]) for l in sys.stdin if l.startswith('vless')]"
```

**Ожидание после фикса:**

```
Авто-подключение -> 149.154.65.180:8444
Мобильный CDN -> cdn.aladdin-ai.ru:8445
```

### P1-A. Тексты бота

**Файл:** `telegram_stars_shop_bot/bot/services/vpn_connect_copy.py`

**Убрать / заменить:**

- «на 4G пробуйте Авто первым»
- «Авто → Мост → CDN»
- «Wi‑Fi: Авто, 4G: Мост»

**Новый канон:**

```
Один профиль «Авто-подключение» — дома и на улице.
Подключите VPN в Happ. Если не грузит — обновите подписку и перезапустите Happ.
Запас: «Мобильный CDN».
```

**Тесты обновить:**

- `tests/test_vpn_connect_copy_keys.py`
- `tests/test_vpn_onboarding_copy.py`
- `tests/test_vpn_user_links.py`

### P1-B. Починить мониторинг

**Файл:** `aladdin_shop_vpn_api/deploy/scripts/vpn_bridge_reality_e2e_smoke.py`

- Сейчас: xhttp + `flow=""` → **FAIL** при tcp+vision на мосте
- Нужно: `network=tcp`, `flow=xtls-rprx-vision`, как в живой подписке
- Добавить в ops-watchdog только после фикса

### P2. Логи UUID на :8444

- Включить access log на MAIN xray-bridge с email/uuid (если поддерживается версией)
- Или: grep journal по `bed682e6-...` + source IP для корреляции с phone drill

### P2. CDN фаза 3

См. `aladdin_shop_vpn_api/deploy/VPN_CDN_DNS_PHASE_CHECKLIST.md` — CF orange + `VPN_CDN_PORT=443` **только** после drill.

### НЕ делать снова

| Действие | Почему |
|----------|--------|
| «Проверьте мост» без сброса Happ | Сервер уже принимал трафик в 13:25 |
| `mode=all` для ux-auto до phone drill | «Авто» всё ещё :8446 для non-staging |
| Верить `vpn_bridge_reality_e2e_smoke` без правки | Ложный FAIL на xhttp |
| Считать `accepted tun>>proxy` = интернет работает | Только локальный приём |
| Поднимать/переустанавливать xray без доказательства поломки | Сервисы active, E2E OK |

---

## 7. Процедура для пользователя (phone drill, 15 мин)

Выполнять **после** деплоя P0 или **сейчас** с ручным выбором «Мобильный мост».

1. iOS: Настройки → VPN → удалить профиль Happ.
2. Перезагрузить iPhone.
3. Happ: удалить подписку → добавить `/sub/…` → обновить.
4. Выбрать **«Мобильный мост»** (до P0) или **«Авто-подключение»** (после P0).
5. Dev Settings: Xray memory limit **40 MB**; автообновление подписки ON.
6. Подключить VPN → 2 мин → fast.com → **байты ≠ 0**.
7. Экспорт `tunnel.log` + `access.log` **с включённым VPN**.
8. Сообщить точное время теста → агент сверяет на MAIN:

```bash
journalctl -u xray-bridge --since "YYYY-MM-DD HH:MM:00" --until "+5 min" | \
  grep -E "gstatic|contabo-hop|bed682e6"
```

**DoD «VPN 100%»:**

- [ ] fast.com ≥1 Мбит/с, 5 мин, Wi‑Fi
- [ ] fast.com ≥1 Мбит/с, 5 мин, МегаФон 4G
- [ ] Telegram + Instagram открываются
- [ ] В tunnel.log нет MEMORY WARNING / Code -12 за сессию
- [ ] На сервере в то же время: `contabo-hop` + gstatic в journal
- [ ] `/sub/` первый профиль = `149.154.65.180:8444`

---

## 8. Щука VPN — сравнение (почему «у них работает»)

**Источники:**

- [Happ2.0 iOS](https://teletype.in/@morevpn/Happ2.0)
- [Белые списки](https://teletype.in/@morevpn/atlantida_new)
- Канал [@ShukaVPN](https://t.me/ShukaVPN)
- Бот [@ShukaVPN_bot](https://t.me/ShukaVPN_bot)

| | Щука | AiMonkey (сейчас) |
|---|------|-------------------|
| Клиент | **Happ** | **Happ** (тот же) |
| Протокол | VLESS `/sub/` | VLESS `/sub/` |
| Серверов в подписке | Много стран + **«Белые списки»** | 3 техпрофиля |
| 4G при ограничениях оператора | Отдельные локации с пометкой | «Мобильный мост» (без понятного имени) |
| Wi‑Fi | Обычные страны | «Авто» → зарубеж :8446 |
| UX | Бот → Подключиться → выбрал страну | «Авто → Мост → CDN» вручную |
| Обновление подписки | Авто при открытии | Есть, но профили неверные |
| Поддержка | @MoreVPN_sup | Бот + drill |

**Вывод:** Щука не использует другой клиент. У них **больше входных точек**, **понятные имена** («Белые списки» только для мобильного интернета), и **не ведут «авто» на прямой зарубеж** на 4G. Наш аналог белых списков — **мост :8444**, но он не первый и не в «Авто».

---

## 9. Happ iOS — лимиты памяти (для поддержки)

| Лимит | Кто | Что делать |
|-------|-----|------------|
| ~50 MB | **Apple** Network Extension | iOS убивает расширение → Tunnel Error **Code -12** |
| Ползунок в Dev Settings | **Happ** Xray memory limit | Поставить **40 MB** |
| `[T2S] skipped` | Happ 4.13 TUN | Норма для внутреннего TUN Xray |

После Code -12 / MEMORY WARNING: VPN выкл → смахнуть Happ из задач → перезапуск → подключить снова.

---

## 10. Команды быстрой диагностики

```bash
KEY=~/.ssh/aladdin_server
CONTABO=root@185.225.233.150
MAIN=root@149.154.65.180

# Smoke
ssh -i $KEY $CONTABO 'python3 /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_prod_smoke.py'

# Живая подписка staging
ssh -i $KEY $CONTABO 'TOKEN=$(sqlite3 /opt/aladdin-shop-vpn-api/var/vpn.db \
  "SELECT opaque_token FROM vpn_accounts WHERE telegram_user_id=493897224"); \
  curl -s "http://127.0.0.1:8091/sub/${TOKEN}?plain=1"'

# Bridge E2E vision (ручной, работает)
ssh -i $KEY $CONTABO 'python3 - <<PY
# см. сессию 2026-07-01: VISION_E2E_OK 204 через /tmp/xbt.json
PY'

# MAIN bridge + WG
ssh -i $KEY $MAIN 'systemctl is-active xray-bridge wg-quick@wg-bridge; ping -c2 10.10.0.2'

# Логи моста за окно теста пользователя
ssh -i $KEY $MAIN 'journalctl -u xray-bridge --since "2026-07-01 13:20:00" \
  --until "2026-07-01 13:30:00" | grep -E "gstatic|contabo-hop"'
```

---

## 11. Ключевые файлы репозитория

| Задача | Файл |
|--------|------|
| Сборка `/sub/` | `aladdin_shop_vpn_api/aladdin_shop_vpn_api/subscription_util.py` |
| Settings / env aliases | `aladdin_shop_vpn_api/aladdin_shop_vpn_api/settings.py` |
| Деплой ux-auto | `aladdin_shop_vpn_api/deploy/scripts/apply_vpn_ux_auto.sh` |
| Тесты subscription | `aladdin_shop_vpn_api/tests/test_egress_and_subscription.py` |
| E2E bridge (починить) | `aladdin_shop_vpn_api/deploy/scripts/vpn_bridge_reality_e2e_smoke.py` |
| Phone drill | `aladdin_shop_vpn_api/deploy/VPN_PHONE_DRILL_RUNBOOK.md` |
| Тексты бота Happ | `telegram_stars_shop_bot/bot/services/vpn_connect_copy.py` |
| Happ App Store SSOT | `telegram_stars_shop_bot/bot/services/vpn_happ_constants.py` |
| Handoff инфра (старше) | `telegram_stars_shop_bot/docs/AIMONKEY_ML_HANDOFF_2026-06-30.md` |

---

## 12. Резюме для следующей ML-системы

**Проблема не в «отсутствии моста».** Мост поднят, WG hop жив, в 13:25 сервер обработал gstatic через оба пути. Пользователь видел «не грузит» из‑за:

1. **Неверного продукта:** «Авто» → зарубеж `:8446` (первый в списке).
2. **Нестабильного Happ на iOS:** MEMORY WARNING 47.91 MB, VPN выключен.
3. **Неверных инструкций в боте:** «на 4G пробуй Авто первым».

**Чтобы VPN работал на 100%:**

1. Код: **Авто = мост, мост первым в `/sub/`**.
2. Бот: **одна кнопка, без танцев с профилями**.
3. Пользователь: **сброс Happ + memory 40 MB** (один раз).
4. Верификация: **phone drill** Wi‑Fi + МегаФон 4G, journal correlation.
5. Мониторинг: **починить e2e smoke** на tcp+vision.

**Не тратить время на:** переустановку xray, «поднятие моста», смену UUID без доказательства — инфраструктура уже прошла E2E.

---

*Документ подготовлен по сессии диагностики 2026-07-01. При расхождении с продом — перепроверить живую `/sub/` и journal, не полагаться только на этот файл.*
