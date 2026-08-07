# ShadowNet → AiMonkey VPN: план переноса (ML handoff)

**Дата:** 2026-07-03  
**Аудитория:** другая ML-система / инженер, продолжающий работу без контекста чата  
**Бот:** `@AiMonkeyStars_bot`  
**Тестовый TID:** `493897224`  
**SSH:** `~/.ssh/aladdin_server`  
**Конкурент (эталон UX):** `@ShadowwNettbot`, подписка `https://subscription.shadownet.pro/LsxgfdrMtgJyZZfQ`

**Связанные документы (читать первым при инцидентах):**
- `AIMONKEY_VPN_SESSION_HANDOFF_2026-07-02.md`
- `AIMONKEY_VPN_DIAGNOSIS_HANDOFF_2026-07-01.md`
- `VPN_INCIDENT_ANNOUNCE_RUNBOOK.md` — инциденты, announce, auto-alert
- `VPN_HAPP_TUNNEL_REPORT_TEMPLATE.md` — шаблон клиентских логов
- `VPN_PHONE_DRILL_RUNBOOK.md` (если есть)

**Статус 2026-07-03 (после obs deploy на Contabo):**
- Код P0–P5 + observability — в репо и на Contabo `185.225.233.150`
- pytest vpn-api **63/63**; prod smoke **10/10**; bundle 3 профиля + observatory
- systemd `vpn-download-alert.timer` — active (каждые 15 мин)
- xray access log: `/var/log/xray/access.log`
- **Осталось:** `p0-phone-drill` (ручной iPhone + МегаФон 4G) → затем `VPN_SUBSCRIBE_UX_AUTO_MODE=all`

---

## 0. START HERE — одна фраза

> ShadowNet выигрывает не «ботом», а **умной подпиской** (JSON-bundle, observatory, split-tunnel, 2 авто-профиля, прямой egress). AiMonkey сейчас отдаёт **одну VLESS-строку** на **цепочку MAIN→WG-hop→Contabo**, которая на МегаФон 4G ломается. План: **сначала починить data plane (P0)**, затем приблизить подписку к ShadowNet (P1–P2), упростить бот (P4).

---

## 1. Что мы узнали о ShadowNet (факты)

### 1.1 HWID-защита
- Без заголовка `X-HWID` и User-Agent Happ → ответ **512 байт**, 2 заглушки: `App not supported`, `Включите HWID в настройках клиента`.
- С HWID → **~602 KB**, **46 JSON-конфигов** Xray.

### 1.2 HTTP-заголовки подписки
| Заголовок | Пример ShadowNet |
|-----------|------------------|
| `content-disposition` | `attachment; filename=user_493897224` |
| `profile-title` | base64: `🥷🏿 ShadowNet - VPN` |
| `profile-update-interval` | `2` (часы) |
| `subscription-userinfo` | `upload=0; download=…; total=32212254720; expire=…` |
| `announce` | base64: инструкция «нажмите 🕓, выберите LTE/4G…» |
| `content-type` (с HWID) | `application/json` |

### 1.3 Формат тела
- Не `vless://` строки, а **массив JSON-конфигов** Xray: `dns`, `routing`, `inbounds`, `outbounds`, **`observatory`**.
- Ключевые профили: `🇪🇺 Авто-поиск WIFI ⚡`, `🇪🇺 Авто-поиск LTE/4G`.

### 1.4 Техника
- **41+ хост**, протоколы: tcp+reality+vision (основной), xhttp+tls, hysteria2.
- **SNI REALITY:** `yandex.ru`, `max.ru`, `eh.vk.com`, `xapi.ozon.ru` (российские сайты).
- **Нет WG-hop** телефон→MAIN→WG→Contabo. Прямой REALITY на edge.
- **Observatory:** probe `https://www.google.com/generate_204`, interval `30s`, авто-выбор лучшего outbound.
- **Split-tunnel:** ~50 RU-доменов → `direct` (не через VPN).

### 1.5 AiMonkey сейчас
- `GET /sub/{token}` → base64, **1 строка** VLESS → `149.154.65.180:8444` (мост).
- Цепочка: телефон → MAIN:8444 → **WG hop** → Contabo:8446 → интернет.
- Заголовки: только `profile-title: AiMonkeyVPN`, `profile-update-interval: 12`.
- На МегаФон 4G у тестового пользователя: upload ≫ download, страницы не открываются.

---

## 2. Явные решения по спорным пунктам

### 2.1 Маскировка под чужие домены (`sprint-agency.pro`, `makeyour.team`, …)

**Решение: НЕТ, не делаем.**

| Что делает ShadowNet | Что делаем мы |
|---------------------|---------------|
| VLESS host = чужой легитимный домен (`crm.sprint-agency.pro`, `s3.makeyour.team`) | Host = **наши** домены/IP: `vpn.aladdin-ai.ru`, `149.154.65.180`, `*.aladdin-ai.ru` |
| SNI REALITY = чужой или RU-сайт | SNI REALITY = **RU-сайты** (`yandex.ru`, `max.ru`) — это **не** маскировка под чужой домен, а стандарт REALITY |

**Почему не копируем чужие домены:**
- Юридический и репутационный риск (чужие домены без договора).
- Зависимость от третьих лиц (домен могут заблокировать/отозвать).
- Не нужно для MVP: достаточно **своих** edge + **RU SNI** на REALITY.

**Что нужно вместо этого (задача `p0-sni-ru`):**
- На bridge и direct outbound сменить `serverName` REALITY с `www.microsoft.com` на `yandex.ru` или `max.ru` (как у ShadowNet).
- Host в URI остаётся наш (`vpn.aladdin-ai.ru` / IP моста).

---

### 2.2 `VPN_SUBSCRIBE_UX_AUTO_MODE=all` до phone drill

**Решение: НЕТ, не включаем до phone drill.**

| Режим | Когда |
|-------|-------|
| `staging` + TID `493897224` (и список staging TIDs) | **Сейчас** — тесты |
| `all` | **Только после** успешного phone drill (DoD ниже) |

**Почему:**
- ux-auto сейчас = один профиль «Авто» → мост → hop; на 4G **не работает** у тестового пользователя.
- `all` раздаст сломанный путь **всем** покупателям VPN.

**DoD для включения `all`:**
1. iPhone + Happ + МегаФон 4G (или целевая сеть).
2. Профиль «Авто 4G» (после P1) или текущий «Авто».
3. `2ip.ru` / `google.com` открываются через VPN.
4. Download в тесте скорости **> 1 MB** (не 3 KB).
5. В server access log за сессию есть трафик egress (не только DNS direct).

**Файлы:** env на Contabo `merge_vpn30_env.py` / `.env` vpn-api, `subscription_util.py` → `ux_auto_enabled_for_user()`.

---

### 2.3 CDN xhttp как основной путь на 4G

**Решение: НЕТ как основной. Опционально — fallback после P2.**

**Почему:**
- Уже тестировали: CDN `cdn.aladdin-ai.ru:8445` xhttp **ломал 4G** (МегаФон).
- Убран из ux-auto подписки 2026-07-01.

| Роль | Решение |
|------|---------|
| Основной 4G | bridge `:8444` tcp+vision **или** direct `:8446` (после A/B без hop) |
| CDN xhttp :8445 | **Не включать** в primary |
| xhttp fallback | Задача `p2-fallback-xhttp` — **отдельный** профиль «Если не работает WiFi», не default |

---

### 2.4 Что ещё явно НЕ в плане

| Пункт | Статус |
|-------|--------|
| LAVA webhook в кабинете | **Не делаем пока** (reconcile 30s достаточно) |
| 46 профилей / 41 сервер | **Не делаем** — MVP: 2 авто + 1 fallback |
| Маскировка под чужие домены | **Не делаем** (см. §2.1) |
| `ux_auto_mode=all` до drill | **Не делаем** (см. §2.2) |
| CDN xhttp primary на 4G | **Не делаем** (см. §2.3) |

---

## 3. Целевая архитектура (после плана)

### 3.1 Что видит пользователь (MVP)

```
Happ → подписка https://aladdin-ai.ru/sub/…
  ├── 🇪🇺 Авто WiFi ⚡      (observatory: edge-8446 + edge-443 на Contabo, split-tunnel RU)
  ├── 🇪🇺 Авто 4G 📶       (observatory: edge-443 + edge-8446, REALITY :443 LTE)
  └── 🇪🇺 Запасной (xhttp)  (только если vision не работает; после P2)
```

**Observatory MVP (P2):** 2 outbounds на **одном хосте** `vpn.aladdin-ai.ru` — порты **443** (LTE) и **8446** (WiFi/direct). Отдельные VPS (`p5-multi-edge`) — позже, не блокер P2.

### 3.2 Серверная цепочка (цель после P0/P1)

**WiFi-профиль:**
```
Телефон → REALITY vision → Contabo :8446 (прямой egress, БЕЗ WG-hop)
```

**4G-профиль (если A/B без hop успешен):**
```
Телефон → REALITY vision → MAIN :8444 → интернет (egress с MAIN, БЕЗ contabo-hop)
```
Если A/B покажет, что hop нужен — оставить hop только для 4G, но с MTU 1280 + MSS-clamp.

---

## 4. Фазы и зависимости

```
P0 (data plane + авто MTU drill) → P1 (подписка 2 профиля + headers + split-tunnel)
                → tests-sub-p1 (pytest, автоматически)
                → P2 (JSON-bundle + observatory 443+8446 + xhttp/hysteria)
                → P3 (HWID gate — без grace, fresh launch)
                → P4 (бот UX + incident runbook)
                → obs-metrics (server + Happ template + alert)
                → tests-sub (полный pytest)
                → P5 (multi-edge, WAF, reality key rotation)
                → p0-phone-drill (ЕДИНСТВЕННАЯ ручная проверка, в самом конце)
```

**Не начинать P2/P3, пока P0 server fixes не применены** (MTU, SNI, port 443, hop A/B).  
**Phone drill (`p0-phone-drill`) — последний шаг** перед `ux_auto_mode=all`; до него только автотесты.

---

## 5. Задачи — подробно по каждой

Формат: **ID** | **Зачем** | **Что сделать** | **Где в коде/сервере** | **Критерий готовности**

---

### P0 — Data plane (блокер)

#### `p0-wg-mtu` — MTU 1280 + MSS-clamp persistent

**Зачем:** На WG-hop пакеты >1380 байт теряются → upload есть, download ~3 KB (как у пользователя 2026-07-02). ShadowNet не использует такой hop.

**Что сделать:**
1. На MAIN (`149.154.65.180`) и Contabo: `wg set wg-bridge mtu 1280` (или в конфиге WG).
2. Применить MSS-clamp: скрипт `aladdin_shop_vpn_api/deploy/scripts/apply_wg_hop_mss_clamp.sh` — сделать **persistent** (systemd unit или netfilter-persistent).
3. Проверка: с MAIN `ping -M do -s 1350 10.10.0.2` и наоборот — без 100% loss.

**Где:** MAIN bridge, Contabo wg-peer.  
**Критерий:** Пакеты 1400 байт не теряются; или стабильно работает при MTU 1280 end-to-end.  
**Автопроверка:** `p0-mtu-drill-script` (ping -M do с MAIN, exit 0).

---

#### `p0-mtu-drill-script` — автоматический MTU drill с MAIN

**Зачем:** Без ручного ping каждый деплой WG — регрессия MTU незаметна до phone drill.

**Что сделать:**
1. Скрипт `deploy/scripts/vpn_mtu_drill.sh`: с MAIN `ping -M do -s 1350 10.10.0.2` и обратно; exit 0 только если loss=0%.
2. Вызов из CI/deploy hook после `apply_wg_hop_mss_clamp.sh`.
3. Опционально: cron на MAIN раз в 6ч, алерт в лог.

**Где:** `aladdin_shop_vpn_api/deploy/scripts/vpn_mtu_drill.sh`.  
**Критерий:** `bash vpn_mtu_drill.sh` → exit 0 на prod после `p0-wg-mtu`.

---

#### `p0-hop-ab` — A/B: прямой egress :8446 без WG-hop

**Зачем:** Проверить гипотезу: основная поломка — hop, а не REALITY. ShadowNet ходит напрямую на edge.

**Что сделать:**
1. Для staging TID `493897224`: в подписке WiFi-профиль → `vpn.aladdin-ai.ru:8446`, tcp+vision, **без** contabo-hop на сервере (трафик с :8446 сразу в freedom/direct).
2. Убедиться, что xray на Contabo :8446 слушает и UUID пользователя активен.
3. Сравнить с текущим мостом на том же телефоне.

**Где:**
- `subscription_util.py` — staging override или env `VPN_SUBSCRIBE_DIRECT_VISION_MODE=staging`
- Contabo xray config `/opt/.../config.json`

**Критерий:** На 4G download > 1 MB при direct :8446; решение зафиксировать в handoff (hop да/нет).

---

#### `p0-sni-ru` — SNI REALITY → yandex.ru / max.ru

**Зачем:** ShadowNet использует RU SNI для обхода DPI; у нас `www.microsoft.com` — хуже на РФ mobile.

**Что сделать:**
1. Bridge REALITY `serverNames` / `dest` → `yandex.ru:443` или `max.ru:443`.
2. Direct :8446 — то же.
3. Обновить шаблоны VLESS в env vpn-api (`pbk`, `sid`, `sni` согласованы с xray config).
4. Перезапуск xray-bridge + xray на Contabo.

**Где:** MAIN `/opt/xray-bridge/config.json`, Contabo xray, `subscription_util.py` templates.  
**Критерий:** Happ подключается; в логах нет массового `REALITY: invalid`.

---

#### `p0-phone-drill` — Phone drill МегаФон 4G (ручной, **последний** шаг)

**Зачем:** Единственная **ручная** приёмка «VPN работает для пользователя». Все остальные проверки — **только pytest/скрипты** до этого шага.

**Когда:** После `tests-sub` (полный автотест), перед `VPN_SUBSCRIBE_UX_AUTO_MODE=all`.

**Что сделать:**
1. TID 493897224, Happ iOS, обновить подписку.
2. WiFi: открыть `https://2ip.ru`, `https://google.com`.
3. 4G МегаФон: то же + speed test (download > 1 MB).
4. Снять `tunnel.log`, `access.log` (Happ) + server access log за интервал (UTC!).
5. Заполнить чеклист в `VPN_PHONE_DRILL_RUNBOOK.md`.
6. Приложить отчёт по шаблону `obs-happ-report` (если готов).

**Критерий:** Все пункты DoD §2.2 зелёные. Это **единственная** ручная проверка в плане.

---

### P1 — Подписка и сервер «как ShadowNet, проще»

#### `p1-sub-headers` — announce, subscription-userinfo, content-disposition

**Зачем:** Пользователь видит срок/трафик и подсказки **в Happ**, без возврата в бот (как ShadowNet).

**Что сделать:**
1. В `GET /sub/{opaque_token}` (`routes/health.py`) добавить заголовки:
   - `content-disposition: attachment; filename=user_{telegram_user_id}`
   - `profile-title: base64:{AiMonkeyVPN 🥷}` (UTF-8 → base64)
   - `subscription-userinfo: upload={u}; download={d}; total={quota}; expire={unix}`
   - `announce: base64:{короткая инструкция на русском}`
2. Данные userinfo брать из vpn DB: `paid_until`, bytes if tracked, quota from product/plan.
3. Текст announce (пример): «Выберите 🇪🇺 Авто 4G на мобильном интернете. WiFi — 🇪🇺 Авто WiFi. Не работает — обновите подписку 🔄»

**Где:** `aladdin_shop_vpn_api/aladdin_shop_vpn_api/routes/health.py`, repo subscription stats.  
**Критерий:** `curl -I /sub/…` показывает все заголовки; Happ отображает announce (если поддерживает).

---

#### `p1-update-interval` — profile-update-interval: 2

**Зачем:** ShadowNet обновляет каждые 2ч — быстрее подхватываются смены серверов.

**Что сделать:** В `health.py` заменить `"profile-update-interval": "12"` → `"2"` (или env `VPN_SUB_PROFILE_UPDATE_INTERVAL_HOURS=2`).

**Критерий:** Заголовок в ответе `/sub/` = 2.

---

#### `p1-split-tunnel` — RU split-tunnel (MVP, уровни 1–2)

**Зачем:** Банки, Госуслуги, Яндекс, VK не через VPN → меньше поломок и latency (как у ShadowNet).

**Стратегия (канон):** не копировать 500 строк ShadowNet — **suffix-first + explicit ~80–120 + блок max.ru**. Эквивалент ~500 у них при ~130 правилах у нас. Подробно — §13.1 и `p1-split-tunnel-expanded`.

**Что сделать (MVP, первый коммит):**
1. Создать `routing_ru_direct.json` с **уровнем 1 (suffix)** и **уровнем 2 (max.ru)**:
   - suffix: `domain:mail.ru`, `domain:yandex.ru`, `domain:yandex.net`, `domain:vk.com`, `domain:vk.ru`, `domain:ozon.ru`, `domain:wildberries.ru`, `domain:gov.ru`, `domain:gosuslugi.ru`, `domain:sber.ru`, `domain:rutube.ru`, `domain:dzen.ru`
   - explicit блок max.ru: `max.ru`, `dev.max.ru`, `web.max.ru`, `api.max.ru`, `botapi.max.ru`, … (как §10.1 ShadowNet LTE)
2. Технические правила: `bittorrent` → direct, `geoip:private` → direct.
3. Пока формат vless-only — routing подключается в JSON-bundle (P2); на P1 файл и builder готовы.

**Где:** `aladdin_shop_vpn_api/aladdin_shop_vpn_api/routing_ru_direct.json`, builder в subscription module.  
**Критерий:** Файл валиден; в bundle `gosuslugi.ru` → direct, `google.com` → proxy.

---

#### `p1-dual-profiles` — «Авто WiFi» + «Авто 4G»

**Зачем:** ShadowNet разделяет WiFi и LTE; один профиль «Авто» не покрывает оба сценария.

**Что сделать:**
1. В `build_subscription_lines()` / новом bundle builder: **2 профиля** вместо одного ux-auto:
   - `🇪🇺 Авто WiFi ⚡` → direct :8446 vision, host `vpn.aladdin-ai.ru`
   - `🇪🇺 Авто 4G 📶` → bridge :8444 (или direct после p0-hop-ab)
2. Env: `VPN_SUBSCRIBE_UX_AUTO_PROFILE_WIFI`, `VPN_SUBSCRIBE_UX_AUTO_PROFILE_LTE`.
3. Обновить тесты `test_egress_and_subscription.py`.

**Где:** `subscription_util.py`, `vpn_connect_copy.py`.  
**Критерий:** `/sub/` для staging TID возвращает 2 строки (или 2 JSON в bundle); имена в Happ совпадают.

---

#### `p1-wifi-direct` — WiFi direct :8446 без hop

**Зачем:** WiFi обычно не нуждается в мосте; проще = надёжнее.

**Что сделать:** Серверный egress для UUID на :8446 direct; подписка WiFi-профиль указывает на :8446.

**Критерий:** С WiFi download/upload симметричны на speed test.

---

#### `p1-lte-bridge` — 4G bridge без hop (если A/B OK)

**Зачем:** Убрать contabo-hop с 4G пути после успешного `p0-hop-ab`.

**Что сделать:**
1. На MAIN xray-bridge: outbound `freedom` или direct с MAIN, **не** `contabo-hop`.
2. Либо второй inbound на MAIN с локальным egress.
3. Только если `p0-phone-drill` на 4G прошёл.

**Где:** MAIN `/opt/xray-bridge/config.json`.  
**Критерий:** В access log при 4G-сессии нет обязательного `contabo-hop`; сайты открываются.

---

### P2 — JSON-bundle + observatory

#### `p2-json-bundle` — формат application/json для Happ

**Зачем:** Observatory и routing требуют полного Xray JSON, не vless:// строк.

**Что сделать:**
1. Новый модуль `subscription_bundle.py`: собирает `list[dict]` конфигов.
2. Если запрос с `User-Agent` Happ и/или `Accept: application/json` — отдавать JSON (как ShadowNet).
3. Иначе — legacy base64 vless (обратная совместимость).
4. Content-Type: `application/json; charset=utf-8`.

**Где:** `routes/health.py`, новый builder, тесты.  
**Критерий:** Happ импортирует подписку; отображаются 2+ профиля с routing.

---

#### `p2-observatory` — URL-test 30s, 2 outbounds на одном хосте

**Зачем:** Авто-failover без ручного перебора (ключевая фича ShadowNet). **Не ждать** `p5-multi-edge` — минимальный failover на **одном** Contabo.

**Канон MVP:** 2 outbounds, один host `vpn.aladdin-ai.ru`, разные порты:
| Тег | Порт | Профиль | SNI | FP |
|-----|------|---------|-----|-----|
| `edge-443` | **443** | LTE / 4G | `max.ru` | `firefox` |
| `edge-8446` | **8446** | WiFi / direct | `yandex.ru` | `qq` |

**Что сделать:**
1. В авто-профилях WiFi и 4G добавить `observatory`:
   ```json
   {
     "probeUrl": "https://www.google.com/generate_204",
     "probeInterval": "30s",
     "subjectSelector": ["edge-443", "edge-8446"],
     "enableConcurrency": true
   }
   ```
2. Оба outbound в bundle с тегами `edge-443`, `edge-8446` (один UUID, разные `port`/`serverName`/`fingerprint`).
3. `balancer` / observatory routing: default → лучший по probe.
4. `meta.serverDescription` на русском.

**Проверка (авто):** pytest останавливает xray inbound :443 → bundle всё ещё валиден; smoke `vpn_observatory_smoke.py` (mock probe fail → selector переключается).

**Критерий:** При падении `edge-443` Happ переключается на `edge-8446` без смены подписки (и наоборот). `p5-multi-edge` — расширение на 2–3 IP, не замена MVP.

---

#### `p2-fallback-xhttp` — запасной xhttp

**Зачем:** ShadowNet имеет «Если не работают верхние (WiFi)» с xhttp.

**Что сделать:** Третий профиль в bundle: xhttp на наш домен, **не** primary. Только после стабильного vision.

**Критерий:** Профиль подключается на WiFi; не включать в «Авто 4G» по умолчанию.

---

#### `p2-hysteria` — Hysteria2 (опционально)

**Зачем:** У ShadowNet 2 hysteria outbounds в авто-WiFi как запасной транспорт.

**Решение:** **P2 опционально.** Делать только если vision+xhttp недостаточно после drill.

---

### P3 — HWID gate

#### `p3-hwid-gate` — защита /sub/ (fresh launch, без grace period)

**Зачем:** Анти-шаринг; как ShadowNet — без HWID только заглушки.

**Решение по grace period:** **НЕТ.** Продукт только выходит в prod, legacy-пользователей нет. HWID gate включаем в **первом prod-релизе** вместе с `p3-bot-hwid-copy` (инструкция в боте **до** импорта подписки).

**Что сделать:**
1. Если нет заголовка `X-HWID` (и валидного UA Happ): вернуть base64 с 2 stub vless (как у ShadowNet).
2. С HWID: полный bundle.
3. Опционально: привязка HWID к TID в DB (лимит устройств).

**Где:** `routes/health.py`, middleware.  
**Критерий:** `curl` без HWID → заглушки; Happ с HWID → полная подписка. pytest `tests-sub`.

---

#### `p3-bot-hwid-copy` — инструкция в боте

**Зачем:** Пользователь должен включить HWID в Happ до импорта.

**Что сделать:** Добавить в `vpn_happ_plus_steps_html()` шаг: «Настройки Happ → HWID → включить».

**Где:** `bot/services/vpn_connect_copy.py`.  
**Критерий:** Текст в боте на шаге подключения.

---

### P4 — Бот UX

#### `p4-bot-ux-simple` — онбординг 3 шага

**Зачем:** ShadowNet: открыл → авто-профиль → работает. У нас слишком много кнопок.

**Что сделать:**
1. Экран VPN после оплаты: 3 шага (Happ → вставить `/sub/` → выбрать «Авто 4G» на LTE).
2. Спрятать матрицу клиентов (HitVPN, WireGuard legacy) за «Дополнительно».
3. Один CTA: «📥 Ссылка подписки».

**Где:** `bot/handlers/vpn.py`, `vpn_connect_copy.py`, `vpn_screen_nav.py`.  
**Критерий:** Новый пользователь проходит путь без support.

---

#### `p4-bot-status` — статус при инцидентах

**Зачем:** ShadowNet `announce` + канал новостей снижают панику.

**Что сделать:**
1. Admin-команда или флаг env `VPN_STATUS_ANNOUNCE=…` → попадает в `announce` заголовок `/sub/`.
2. Опционально: пост в новостной канал.

**Критерий:** При инциденте пользователь видит текст в Happ announce.

---

#### `p4-rename-profiles` — имена профилей в копирайте

**Зачем:** Согласованность бот ↔ Happ.

**Что сделать:** Везде в боте: «Авто WiFi ⚡» / «Авто 4G 📶» вместо «Авто-подключение».

**Где:** `vpn_connect_copy.py`, `vpn_ux_auto_profiles_html()`.  
**Критерий:** Текст бота совпадает с именами в подписке.

---

### P5 — Инфра (после стабилизации)

#### `p5-multi-edge` — 2–3 edge-ноды (расширение observatory)

**Зачем:** Резерв при блокировке IP. **Не блокер P2** — observatory MVP уже работает на 443+8446 одного Contabo.

**Что сделать:** Второй VPS или IP; те же UUID; добавить `edge-2-ip` в `subjectSelector` observatory.

**Критерий:** При остановке Contabo IP авто-профиль переключается на резервный IP.

---

#### `p5-reality-key-rotation` — ротация REALITY без даунтайма

**Зачем:** При смене SNI/spiderX/publicKey — не рвать активных клиентов. Сейчас есть `VPN53_SNI_ROTATION_RUNBOOK.md`, нужна привязка к плану.

**Что сделать:**
1. Dual `serverNames[]` + dual `shortIds[]` на inbound (443 и 8446) — **24–48ч overlap**.
2. Подписка отдаёт **новый** профиль параллельно старому (2 shortId).
3. Runbook: backup config → add SNI → restart xray → `vpn_prod_smoke.py` → через 7–14 дней убрать старый SNI.
4. Документ: `deploy/VPN53_SNI_ROTATION_RUNBOOK.md` + чеклист в `p4-incident-announce-runbook`.

**Где:** Contabo xray, MAIN xray-bridge, `subscription_bundle.py`.  
**Критерий:** Ротация SNI на staging без обрыва сессии > 5 мин; pytest smoke green.

---

#### `p5-ddos-guard` — WAF (опционально)

**Зачем:** ShadowNet использует DDoS-Guard на `subscription.shadownet.pro`.

**Решение:** Опционально после MVP. Наш `/sub/` на `aladdin-ai.ru` — оценить нагрузку.

---

### Тесты, метрики и документация

#### `tests-sub-p1` — ранний pytest (после p1-sub-headers)

**Зачем:** Защита от регрессии на **каждом** деплое vpn-api, не ждать конца плана.

**Что сделать (только автоматически):**
1. pytest: headers (`profile-title`, `subscription-userinfo`, `announce`, `profile-update-interval`).
2. pytest: dual profiles (2 строки / 2 JSON для staging TID).
3. Запуск: `pytest aladdin_shop_vpn_api/tests/test_subscription_p1.py -q` в CI/deploy hook.

**Где:** новый `test_subscription_p1.py` или расширение `test_egress_and_subscription.py`.  
**Критерий:** green на каждом деплое после P1.7.

---

#### `tests-sub` — полный pytest (перед phone drill)

**Что сделать (только автоматически):** pytest для: headers, dual profiles, HWID stub/full, bundle JSON schema, split-tunnel rules present, observatory tags `edge-443`/`edge-8446`, sniffing inbound block.

**Где:** `aladdin_shop_vpn_api/tests/test_egress_and_subscription.py`, новые тесты.  
**Критерий:** `pytest aladdin_shop_vpn_api/tests/ -q` green. **Ручных шагов нет.**

---

#### `obs-bytes-server` — bytes in/out per UUID в access log

**Зачем:** Видеть asymmetry upload≫download без ручного drill.

**Что сделать:**
1. Xray access log format: `email`/`id` (UUID), `uplink`, `downlink` per connection.
2. Скрипт `deploy/scripts/vpn_session_bytes_report.py --uuid UUID --since 1h` → JSON summary.
3. Порог в скрипте: если `downlink < 100KB` при `uplink > 1MB` → exit 2 (для алерта).

**Где:** Contabo + MAIN xray `log.access`, скрипт в deploy.  
**Критерий:** скрипт на staging UUID возвращает bytes; pytest на парсер лога.

---

#### `obs-happ-report` — шаблон отчёта из Happ tunnel.log

**Зачем:** Стандартизировать сбор клиентских логов без ad-hoc инструкций.

**Что сделать:**
1. Markdown-шаблон `docs/VPN_HAPP_TUNNEL_REPORT_TEMPLATE.md`: что копировать из Happ (tunnel.log, access.log, профиль, время UTC).
2. Бот: кнопка «📋 Как прислать лог» → ссылка на шаблон (опционально P4).

**Критерий:** шаблон в репо; ML может заполнить по чеклисту.

---

#### `obs-download-alert` — download < 100 KB → VPN_STATUS_ANNOUNCE

**Зачем:** Авто-флаг инцидента в Happ announce без ручного мониторинга.

**Что сделать:**
1. Cron/systemd timer: `vpn_session_bytes_report.py` каждые 15 мин по активным UUID.
2. При exit 2: записать `VPN_STATUS_ANNOUNCE=base64:…` в env vpn-api (или admin API).
3. Текст announce: «Временные проблемы на 4G. Попробуйте 🇪🇺 Авто WiFi или обновите подписку 🔄».
4. Сброс флага вручную admin-командой.

**Где:** `p4-bot-status` infra, env merge, `health.py` announce.  
**Критерий:** симуляция low-download → announce меняется; pytest на setter.

---

#### `p4-incident-announce-runbook` — runbook инцидентов + announce

**Зачем:** Связать `obs-download-alert`, `p4-bot-status`, ротацию ключей в один процесс.

**Что сделать:**
1. Документ `docs/VPN_INCIDENT_ANNOUNCE_RUNBOOK.md`: триггеры (bytes alert, xray down, SNI rotation), тексты announce, кто сбрасывает.
2. Шаблоны из `VPN34_STATUS_POST_TEMPLATES.md`.
3. Чеклист: announce → статус-канал → fix → снять announce → postmortem в handoff.

**Критерий:** runbook в репо; dry-run на staging.

---

#### `docs-runbook`

**Что сделать:** Обновить `AIMONKEY_VPN_SESSION_HANDOFF` после каждой фазы; держать этот файл актуальным.

---

## 6. Карта файлов репозитория

| Компонент | Путь |
|-----------|------|
| Подписка / профили | `aladdin_shop_vpn_api/aladdin_shop_vpn_api/subscription_util.py` |
| GET /sub/ | `aladdin_shop_vpn_api/aladdin_shop_vpn_api/routes/health.py` |
| Тексты бота VPN | `telegram_stars_shop_bot/bot/services/vpn_connect_copy.py` |
| VPN handlers | `telegram_stars_shop_bot/bot/handlers/vpn.py` |
| MSS-clamp | `aladdin_shop_vpn_api/deploy/scripts/apply_wg_hop_mss_clamp.sh` |
| Тесты подписки | `aladdin_shop_vpn_api/tests/test_egress_and_subscription.py` |
| Env пример | `telegram_stars_shop_bot/env.example` |

**Серверы:**
- MAIN `149.154.65.180` — xray-bridge :8444, wg-bridge
- Contabo `185.225.233.150` — vpn-api :8091, xray :8443/:8446

---

## 7. Порядок выполнения для ML (чеклист)

**Политика тестирования:** всё автоматически (pytest, `vpn_*_smoke.py`, `vpn_mtu_drill.sh`). **Единственная ручная проверка** — `p0-phone-drill` в **самом конце**.

```
[x] 1. p0-wg-mtu + p0-mtu-drill-script
[x] 2. p0-sni-ru + p0-fingerprint-profile + p0-port-443-lte (Contabo :443)
[x] 3. p0-hop-ab
[x] 4. p1-wifi-direct + p1-lte-bridge
[x] 5. p1-dual-profiles
[x] 6. p1-sub-headers + p1-update-interval
[x] 7. tests-sub-p1  ← pytest после headers/dual profiles; каждый деплой
[x] 8. p1-split-tunnel + p1-split-tunnel-expanded + p1-routing-domain-strategy
[x] 9. p1-maxru-direct-lte + p1-spiderx-reality + p1-dns-doh
[x] 10. p4-rename-profiles + p4-bot-ux-simple (параллельно с 8–9)
[x] 11. p2-json-bundle + p1-sniffing-inbound
[x] 12. p2-observatory (edge-443 + edge-8446, один host)
[x] 13. p2-fallback-xhttp + p2-hysteria (опц.)
[x] 14. p3-hwid-gate + p3-bot-hwid-copy (без grace period)
[x] 15. obs-bytes-server + obs-happ-report + obs-download-alert
[x] 16. p4-incident-announce-runbook + p4-bot-status
[x] 17. tests-sub  ← полный pytest, только авто
[x] 18. p5-reality-key-rotation (док + smoke на staging)
[x] 19. p5-multi-edge (код; включить VPN_OBSERVATORY_EXTRA_EDGES_JSON на prod)
[x] 20. docs-runbook
[ ] 21. p0-phone-drill  ← ЕДИНСТВЕННАЯ ручная проверка; STOP если красный
[ ] 22. Только после зелёного drill: VPN_SUBSCRIBE_UX_AUTO_MODE=all
```

---

## 8. Cursor TODO IDs (синхронизация)

Использовать те же id в Cursor Tasks (**38 задач**, §17):

`p0-wg-mtu`, `p0-mtu-drill-script`, `p0-hop-ab`, `p0-phone-drill`, `p0-sni-ru`,  
`p0-fingerprint-profile`, `p0-port-443-lte`,  
`p1-sub-headers`, `p1-update-interval`, `p1-split-tunnel`, `p1-split-tunnel-expanded`,  
`p1-routing-domain-strategy`, `p1-spiderx-reality`, `p1-dns-doh`, `p1-sniffing-inbound`,  
`p1-dual-profiles`, `p1-wifi-direct`, `p1-lte-bridge`, `p1-maxru-direct-lte`,  
`p2-json-bundle`, `p2-observatory`, `p2-fallback-xhttp`, `p2-hysteria`,  
`p3-hwid-gate`, `p3-bot-hwid-copy`,  
`p4-bot-ux-simple`, `p4-bot-status`, `p4-rename-profiles`, `p4-incident-announce-runbook`,  
`p5-multi-edge`, `p5-ddos-guard`, `p5-reality-key-rotation`,  
`obs-bytes-server`, `obs-happ-report`, `obs-download-alert`,  
`tests-sub-p1`, `tests-sub`, `docs-runbook`

---

## 9. Краткие ответы для ML (TL;DR)

| Вопрос | Ответ |
|--------|-------|
| Чужие домены (`sprint-agency.pro`)? | **НЕТ.** Только свои хосты + RU SNI в REALITY. |
| `ux_auto_mode=all` до drill? | **НЕТ.** Только staging TID до зелёного phone drill. |
| CDN xhttp primary на 4G? | **НЕТ.** Только опциональный fallback-профиль после P2. |
| LAVA webhook? | **НЕТ пока.** |
| 46 профилей? | **НЕТ.** MVP = 2 авто + 1 fallback + observatory 443/8446 |
| Главный приоритет? | **P0 data plane**, затем P1 подписка, затем P2 observatory (2 порта, 1 host) |
| Ручные тесты? | **Только** `p0-phone-drill` в конце; остальное pytest/скрипты |
| HWID grace period? | **НЕТ** — fresh launch |

---

## 10. Анализ рабочих конфигов ShadowNet (Happ/Xray, 2026-07-03)

**Источник:** пользователь скопировал активные JSON-конфиги из Happ при **работающем** ShadowNet VPN (не access/tunnel `.log`, а **экспорт runtime-конфига** Xray внутри Happ). Проверено: 2 полных профиля + фрагмент третьего.

**Подтверждение проверки:** все поля `outbounds`, `routing`, `dns`, `inbounds`, `streamSettings.realitySettings` разобраны построчно; сравнение с нашим `subscription_util.py` и xray example configs выполнено.

---

### 10.1 Профиль A: `🇩🇪 LTE/4G FAST | Германия` (мобильный, работает)

| Параметр | Значение ShadowNet | AiMonkey сейчас | Вывод |
|----------|-------------------|-----------------|-------|
| Host | `fast.shadownet.pro` | `149.154.65.180` (мост) | Прямой edge, свой поддомен |
| Port | **443** | **8444** (мост) | LTE на 443 — меньше режут DPI |
| Transport | `tcp` + `reality` + `xtls-rprx-vision` | tcp+vision | Совпадает |
| serverName (SNI) | **`max.ru`** | `www.microsoft.com` | **Критичный gap** |
| fingerprint | **`firefox`** | `chrome` | **Разный FP по профилю** |
| shortId | `89abcdef` | `a1b2c3d4` (наш) | Нужно согласовать с xray |
| spiderX | `/golWLSnJbwnmcDib` | не задан | Добавить в REALITY |
| WG-hop | **нет** | MAIN→WG→Contabo | **Главный structural gap** |
| DNS в конфиге | нет (минимальный профиль) | нет | — |
| Routing | bittorrent→direct; max.ru*→direct | нет routing | Split начинается даже в LTE |

**Как это работает:** телефон на 4G открывает REALITY-сессию к `fast.shadownet.pro:443`, притворяясь TLS к `max.ru`, fingerprint Firefox. Трафик **сразу** выходит в интернет с немецкого edge. Telegram/max.ru идут **мимо** туннеля (direct) — меньше нагрузка и меньше поломок локальных сервисов.

---

### 10.2 Профиль B: `🇪🇺⬇️ WiFi сервера ⬇️` (WiFi, работает)

| Параметр | Значение ShadowNet | AiMonkey сейчас |
|----------|-------------------|-----------------|
| Host | `deb2.shadownet.pro` | `vpn.aladdin-ai.ru` / мост |
| Port | **8443** | 8446 / 8444 |
| serverName | **`yandex.ru`** | `www.microsoft.com` |
| fingerprint | **`qq`** | `chrome` |
| spiderX | `/` | нет |
| publicKey | отдельный от LTE | один на всё |

**DNS (важно):**
```json
"dns": {
  "queryStrategy": "UseIP",
  "servers": ["https://8.8.8.8/dns-query", "https://8.8.8.8/dns-query"]
}
```
DoH на Google — резолв **до** routing; стратегия `UseIP`.

**Inbounds (локально в Happ):**
- SOCKS `127.0.0.1:10808`, HTTP `127.0.0.1:10809`
- **Sniffing включён:** `http`, `tls`, `quic` — Happ определяет домен из TLS ClientHello для routing

**Routing (ключ к стабильности):**
```json
"domainMatcher": "hybrid",
"domainStrategy": "IPIfNonMatch"
```
Правила:
1. `bittorrent` → `direct`
2. `max.ru` и поддомены → `direct`
3. **Огромный список RU** (500+ записей) → `direct`: gov.ru, yandex, vk/userapi CDN, mail.ru дерево, ozon, wildberries, gosuslugi, rutube, kinopoisk, tbank, vtb, rzd, 2gis, …

**Как это работает на WiFi:** VPN туннелирует **только «зарубежный» и не-RU** трафик. Банки, VK, Яндекс, Госуслуги, Ozon — **напрямую**. Поэтому у пользователя «всё открывается»: локальное не ломается, YouTube/Google — через VPN.

**У нас:** full tunnel → весь TCP через hop → MTU/black hole + DPI на каждый пакет.

---

### 10.3 Сравнение outbounds (структура)

ShadowNet (оба профиля):
```
outbounds: [ vless:proxy, freedom:direct, blackhole:block ]
```
Один активный proxy outbound на профиль — **просто**. Нет contabo-hop, нет цепочки.

AiMonkey (ux-auto):
```
одна vless:// строка → мост → hop → egress
```
Нет `direct`/`block` в подписке — Happ добавляет сам, но **routing rules не приходят**.

---

### 10.4 Почему у них работает, у нас нет — итог по логам

| # | Причина (доказательство из конфига) | Наш gap |
|---|-------------------------------------|---------|
| 1 | Прямой egress, нет WG-hop | contabo-hop + MTU loss |
| 2 | LTE на **:443** + SNI **max.ru** + FP **firefox** | :8444 + microsoft + chrome |
| 3 | WiFi на **:8443** + SNI **yandex.ru** + FP **qq** | один профиль на всё |
| 4 | **Split-tunnel** 500+ RU доменов | full tunnel |
| 5 | **domainStrategy: IPIfNonMatch** + hybrid matcher | нет routing |
| 6 | **spiderX** в REALITY | не настроен |
| 7 | JSON-bundle с dns/routing/inbounds | только vless:// |
| 8 | max.ru direct даже на LTE-профиле | Telegram шёл через наш tunnel и умирал |

---

### 10.5 Что НЕ нужно копировать из этих логов

| Элемент | Почему |
|---------|--------|
| Весь список 500+ mail.ru поддоменов сразу | **suffix-first** + explicit ~80–120 (§13.1); расширять по тикетам |
| Разные publicKey на каждый хост | У нас 2–3 edge достаточно с 2–3 ключами |
| Отдельный профиль на каждую страну | Не в MVP |

---

## 11. Дополнительные задачи (из анализа конфигов §10)

### `p0-fingerprint-profile` — fingerprint по типу сети

**Зачем:** В логах LTE = `firefox`, WiFi = `qq`. Разный TLS fingerprint снижает детект DPI на мобильных сетях. У нас везде `chrome` (`subscription_util.py`).

**Что сделать:**
1. Env: `VPN_BRIDGE_REALITY_FINGERPRINT=firefox` (4G), `VPN_XRAY_REALITY_FINGERPRINT=qq` (WiFi).
2. Согласовать с xray server config (fingerprint клиента должен быть допустим).
3. Обновить VLESS URI `fp=` в шаблонах.

**Где:** `subscription_util.py`, `env.example`, xray bridge + contabo configs.  
**Критерий:** LTE профиль `fp=firefox`, WiFi `fp=qq` в `/sub/`.

---

### `p0-port-443-lte` — LTE на порту 443 (канон: Contabo, не MAIN nginx)

**Зачем:** ShadowNet LTE использует `fast.shadownet.pro:443`. Порт 443 реже блокируют на 4G. На MAIN уже занят nginx `:443` (`aladdin-ai.ru`) — **как у работающего конкурента**, REALITY на 443 поднимаем на **edge (Contabo)**, не ломая сайт.

**Канон (проверенный паттерн):**
| Профиль | Host | Port | Где inbound |
|---------|------|------|-------------|
| Авто 4G 📶 | `vpn.aladdin-ai.ru` | **443** | Contabo xray REALITY |
| Авто WiFi ⚡ | `vpn.aladdin-ai.ru` | **8446** | Contabo xray REALITY |

**Почему Contabo :443, а не MAIN :443:**
- MAIN `149.154.65.180`: nginx `:443` + iOS API `:8002` — не трогаем (`VPN82`).
- Contabo `185.225.233.150`: уже xray `:8443`/`:8446`; добавить REALITY inbound **`:443`** (UFW allow 443/tcp).
- Observatory P2 использует оба порта на **одном** host — как у ShadowNet на одном edge.

**Альтернатива (только если Contabo :443 недоступен):** MAIN nginx **stream** `ssl_preread` → xray `127.0.0.1:10443` — см. `VPN82_MAIN_BRIDGE_RUNBOOK.md` §443 fallback. Не primary.

**Что сделать:**
1. Contabo: второй REALITY inbound на **443** (отдельный shortId/SNI `max.ru`, fp firefox).
2. Подписка «Авто 4G» → `vpn.aladdin-ai.ru:443`.
3. WiFi → `:8446` (SNI `yandex.ru`, fp qq).
4. Firewall Contabo: `ufw allow 443/tcp`.
5. `vpn_prod_smoke.py` + pytest port в bundle.

**Где:** Contabo `/usr/local/etc/xray/config.json`, `subscription_util.py` / bundle builder.  
**Критерий:** 4G-профиль port 443; pytest green; observatory tags `edge-443` + `edge-8446`.

---

### `p1-spiderx-reality` — spiderX в REALITY

**Зачем:** В логах LTE: `spiderX: "/golWLSnJbwnmcDib"`, WiFi: `spiderX: "/"`. Параметр REALITY для имитации HTTP path — часть «маскировки» handshake.

**Что сделать:**
1. Добавить `spiderX` в server realitySettings на xray.
2. Если отдаём JSON-bundle — включить в `realitySettings` клиента.
3. Для vless URI: параметр `spx=` (если поддерживается клиентом).

**Где:** xray configs, bundle builder.  
**Критерий:** REALITY handshake стабилен; нет роста `invalid connection`.

---

### `p1-dns-doh` — DNS over HTTPS в bundle

**Зачем:** WiFi-профиль ShadowNet: DoH `8.8.8.8`, `queryStrategy: UseIP`. Предсказуемый резолв для routing по доменам.

**Что сделать:**
1. В JSON-bundle каждого профиля:
   ```json
   "dns": {
     "servers": ["https://8.8.8.8/dns-query"],
     "queryStrategy": "UseIP"
   }
   ```
2. Опционально: `1.1.1.1/dns-query` как fallback.

**Где:** `subscription_bundle.py` (P2).  
**Критерий:** В экспорте Happ виден dns-блок; `google.com` резолвится при включённом VPN.

---

### `p1-routing-domain-strategy` — domainMatcher + domainStrategy

**Зачем:** Без `IPIfNonMatch` + `hybrid` split-tunnel по доменам работает хуже — правила не матчятся на IP после резолва.

**Что сделать:**
1. В каждом JSON-профиле routing:
   ```json
   "domainMatcher": "hybrid",
   "domainStrategy": "IPIfNonMatch"
   ```
2. Порядок rules: bittorrent → direct; geoip:private → direct; RU domains → direct; default → proxy.

**Где:** bundle builder, `routing_ru_direct.json`.  
**Критерий:** `yandex.ru` → direct, `google.com` → proxy (проверка в Happ или access log).

---

### `p1-split-tunnel-expanded` — полный split: suffix-first + explicit ~80–120

**Зачем:** У ShadowNet в логах WiFi — **500+** explicit-записей, но большая часть — **поддомены**, которые у нас покрываются **suffix rules** (`domain:mail.ru` = все `*.mail.ru`, `e.mail.ru`, `cloud.mail.ru`… без 300 строк).

**Почему не копировать все 500:**
- Один suffix заменяет сотни поддоменов.
- Меньше размер подписки, проще тесты и сопровождение.
- **~15 suffix + ~80–120 explicit ≈ покрытие ~90% кейсов ShadowNet** без копипаста.

**Каноническая структура `routing_ru_direct.json` (4 уровня):**

| Уровень | Что | Пример | Строк |
|---------|-----|--------|-------|
| **1. Suffix** | корневые зоны целиком | `domain:mail.ru`, `domain:yandex.ru`, `domain:vk.com`, `domain:ozon.ru`, `domain:userapi.com`, `domain:vk-portal.net`, `domain:ok.ru` | ~15 |
| **2. max.ru блок** | Telegram ecosystem (WiFi + 4G) | `max.ru`, `dev.max.ru`, `web.max.ru`, `api.max.ru`, `botapi.max.ru`, … | ~12 |
| **3. Explicit** | банки, CDN, гос, то что не suffix | `tbank.ru`, `vtb.ru`, `alfabank.ru`, `gosuslugi.ru`, `voter.gosuslugi.ru`, `2gis.ru`, `rzd.ru`, `pochta.ru`, `auto.ru`, `kinopoisk.ru`, `lemanapro.ru`, … | **~80–120** |
| **4. Технические** | всегда direct | `bittorrent`, `geoip:private` + `domainMatcher: hybrid`, `domainStrategy: IPIfNonMatch` (→ `p1-routing-domain-strategy`) | 3–5 |

**Что сделать:**
1. Дополнить `routing_ru_direct.json` уровнем 3: выбрать из лога ShadowNet **уникальные корневые** домены (не `sun9-47.userapi.com` — достаточно `domain:userapi.com`).
2. Источник explicit-списка: §10.2 лог WiFi ShadowNet → дедупликация по корню → ~80–120 строк.
3. **Не** добавлять сотни `*.mail.ru` / `sun*.userapi.com` поштучно.
4. Итерация **P1.1:** после phone drill — +1 домен на тикет поддержки, не пакетом 500.

**Где:** `aladdin_shop_vpn_api/aladdin_shop_vpn_api/routing_ru_direct.json`, bundle builder.  
**Критерий:** drill: Яндекс, Сбер, Госуслуги, Telegram, Ozon → direct; Google/YouTube → proxy. Размер routing-блока < 150 правил.

---

### `p1-maxru-direct-lte` — max.ru direct на 4G-профиле

**Зачем:** Даже в профиле «LTE/4G FAST» ShadowNet отправляет **max.ru** (Telegram ecosystem) в direct. У нас Telegram шёл через tunnel → нагрузка + обрывы.

**Что сделать:** В 4G JSON-профиле первое правило после bittorrent — список max.ru доменов → direct (скопировать из §10.1).

**Критерий:** Telegram стабилен на 4G при включённом VPN.

---

### `p1-sniffing-inbound` — sniffing http/tls/quic в JSON-bundle

**Зачем:** ShadowNet WiFi-профиль (§10.2): sniffing на локальных inbounds — Happ определяет домен из TLS ClientHello для routing/split-tunnel.

**Что сделать:**
1. В JSON-bundle каждого профиля (inbounds SOCKS/HTTP):
   ```json
   "sniffing": {
     "enabled": true,
     "destOverride": ["http", "tls", "quic"]
   }
   ```
2. Без sniffing split по доменам работает хуже (только IP).

**Где:** `subscription_bundle.py` (P2), шаблон inbound.  
**Критерий:** экспорт Happ показывает sniffing; pytest на наличие блока в bundle.

---

## 12. Обновлённый TL;DR (после анализа конфигов)

| Вопрос | Ответ |
|--------|-------|
| Fingerprint chrome везде? | **НЕТ.** LTE=firefox, WiFi=qq (задача `p0-fingerprint-profile`) |
| Порт 8444 для 4G? | **Сменить на 443** на Contabo (`p0-port-443-lte`), не MAIN nginx |
| Observatory без 2 VPS? | **ДА** — 2 outbounds 443+8446 на одном host (`p2-observatory`) |
| Split-tunnel как у ShadowNet? | **suffix-first + explicit ~80–120 + max.ru** (`p1-split-tunnel` + `p1-split-tunnel-expanded`), не копипаст 500 |
| max.ru через VPN? | **НЕТ** — direct даже на 4G (`p1-maxru-direct-lte`) |
| spiderX нужен? | **ДА** (`p1-spiderx-reality`) |
| DoH в подписке? | **ДА** в JSON-bundle (`p1-dns-doh`) |
| Sniffing в bundle? | **ДА** (`p1-sniffing-inbound`) |
| HWID grace period? | **НЕТ** — fresh launch, gate с первого prod (`p3-hwid-gate`) |
| Ручные тесты? | **Только** `p0-phone-drill` в самом конце; остальное pytest/скрипты |

---

## 13. Что такое Split-tunnel (простыми словами)

**Split-tunnel** = «разделённый туннель». Не весь интернет идёт через VPN.

| Без split-tunnel (у нас сейчас) | С split-tunnel (как ShadowNet) |
|--------------------------------|------------------------------|
| Включил VPN → **весь** трафик через сервер | Включил VPN → **только нужное** через сервер |
| Яндекс, банки, Telegram → через VPN → hop → ломается | Яндекс, банки, Telegram → **напрямую** с телефона |
| Google, YouTube → через VPN | Google, YouTube → **через VPN** |

**«Сотни RU-доменов direct»** = в конфиге список правил: «эти сайты **не** пускать в туннель». Примеры: `yandex.ru`, `vk.com`, `ozon.ru`, `gosuslugi.ru`, `sber.ru`, `max.ru` (Telegram).

**Зачем нам:** меньше нагрузка на наш сервер, банки и госуслуги не ломаются, Telegram стабильнее на 4G. Зарубежные сайты всё равно идут через VPN.

### 13.1 Почему не «топ‑500» и как делаем лучше

| Подход | Строк в конфиге | Покрытие | Для AiMonkey |
|--------|-----------------|----------|--------------|
| Копипаст 500 из ShadowNet | 500+ | ~98% | ❌ избыточно, сложно сопровождать |
| Только топ‑10 explicit | ~10 | ~50% | ❌ мало |
| **suffix-first + explicit ~80–120** | **~130** | **~90%** | ✅ **канон плана** |
| Только suffix без explicit | ~15 | ~70% | ⚠️ только MVP (`p1-split-tunnel`) |

**Правило для ML:** один `domain:mail.ru` = все поддомены mail.ru. Не добавлять `e.mail.ru`, `cloud.mail.ru`, … по отдельности.

**Порядок внедрения:**
1. `p1-split-tunnel` — suffix (~15) + max.ru блок + bittorrent/geoip.
2. `p1-split-tunnel-expanded` — explicit ~80–120 из дедуплицированного лога ShadowNet.
3. `p1-routing-domain-strategy` — hybrid + IPIfNonMatch (иначе split не сработает).
4. Phone drill → **P1.1:** +1 домен на реальный тикет, не пакетом 500.

---

## 14. Будет ли «идеально»? — честный ответ

**Нет гарантии «100% идеально»** ни у одного VPN в РФ на 4G. DPI и блокировки меняются.

**Что план даёт:**
- Убираем **известные** причины поломки (hop/MTU, wrong SNI, full tunnel, один профиль).
- Копируем **проверенные** паттерны ShadowNet, у которых у вас **работало** на том же телефоне.

**Критерий успеха (не «идеал», а «работает как у них»):**
1. `tests-sub` green (авто).
2. Phone drill зелёный (ручной, последний): сайты открываются, download > 1 MB на 4G.
3. Telegram не падает при включённом VPN.
4. `obs-download-alert` не в состоянии инцидента.

**Если tests-sub красный** — не делать phone drill, итерировать код/сервер.

---

## 15. Полная карта файлов (для ML)

### Главный документ (этот файл)
`telegram_stars_shop_bot/docs/SHADOWNET_ADOPTION_PLAN_ML_HANDOFF.md` ← **START HERE**

### Handoff и диагностика (читать при инцидентах)
| Файл | Зачем |
|------|-------|
| `telegram_stars_shop_bot/docs/AIMONKEY_VPN_SESSION_HANDOFF_2026-07-02.md` | Итог сессии 01–02.07: MTU, логи Happ, P0/P1 статус |
| `telegram_stars_shop_bot/docs/AIMONKEY_VPN_DIAGNOSIS_HANDOFF_2026-07-01.md` | Первая диагностика VPN |
| `telegram_stars_shop_bot/docs/VPN_P0_TECH_FIX_ML_HANDOFF_2026-06-28.md` | Ранний P0 tech fix |

### Код — подписка и API
| Файл | Зачем |
|------|-------|
| `aladdin_shop_vpn_api/aladdin_shop_vpn_api/subscription_util.py` | Профили, VLESS, ux-auto, build_subscription_lines |
| `aladdin_shop_vpn_api/aladdin_shop_vpn_api/routes/health.py` | GET `/sub/{token}`, HTTP-заголовки |
| `aladdin_shop_vpn_api/tests/test_egress_and_subscription.py` | Тесты подписки |
| `aladdin_shop_vpn_api/env.example` | Env VPN (SNI, порты, шаблоны) |

### Код — бот
| Файл | Зачем |
|------|-------|
| `telegram_stars_shop_bot/bot/handlers/vpn.py` | Экран VPN, кнопки, /sub/ ссылка |
| `telegram_stars_shop_bot/bot/services/vpn_connect_copy.py` | Тексты Happ, инструкции |
| `telegram_stars_shop_bot/bot/services/vpn_user_links.py` | Кнопки подписки, URL |
| `telegram_stars_shop_bot/bot/services/vpn_nav.py` | Навигация VPN |
| `telegram_stars_shop_bot/env.example` | Env бота (не LAVA webhook — не трогаем) |

### Сервер — deploy и xray
| Файл | Зачем |
|------|-------|
| `aladdin_shop_vpn_api/deploy/scripts/apply_wg_hop_mss_clamp.sh` | MSS-clamp WG |
| `aladdin_shop_vpn_api/deploy/scripts/install_ru_bridge_main.py` | Bridge на MAIN |
| `aladdin_shop_vpn_api/deploy/xray/ru_bridge_config.example.json` | Пример xray bridge |
| `aladdin_shop_vpn_api/deploy/VPN82_MAIN_BRIDGE_RUNBOOK.md` | Runbook моста |
| `aladdin_shop_vpn_api/deploy/VPN53_SNI_ROTATION_RUNBOOK.md` | Ротация SNI |
| `aladdin_shop_vpn_api/deploy/VPN17_DEPLOY_RUNBOOK.md` | Деплой vpn-api |

### Создать в рамках плана (ещё нет)
| Файл | Задача |
|------|--------|
| `aladdin_shop_vpn_api/.../subscription_bundle.py` | p2-json-bundle |
| `aladdin_shop_vpn_api/.../routing_ru_direct.json` | p1-split-tunnel + p1-split-tunnel-expanded |
| `aladdin_shop_vpn_api/deploy/scripts/vpn_mtu_drill.sh` | p0-mtu-drill-script |
| `aladdin_shop_vpn_api/deploy/scripts/vpn_session_bytes_report.py` | obs-bytes-server |
| `aladdin_shop_vpn_api/deploy/scripts/vpn_download_alert_check.py` | obs-download-alert |
| `aladdin_shop_vpn_api/deploy/scripts/apply_obs_contabo_deploy.sh` | obs deploy Contabo |
| `aladdin_shop_vpn_api/deploy/VPN_P5_DDOS_GUARD.md` | p5-ddos-guard |
| `aladdin_shop_vpn_api/tests/test_subscription_p1.py` | tests-sub-p1 |
| `telegram_stars_shop_bot/docs/VPN_HAPP_TUNNEL_REPORT_TEMPLATE.md` | obs-happ-report |
| `telegram_stars_shop_bot/docs/VPN_INCIDENT_ANNOUNCE_RUNBOOK.md` | p4-incident-announce-runbook |

### Серверы (prod)
| Сервер | IP | Роль |
|--------|-----|------|
| MAIN | `149.154.65.180` | xray-bridge :8444, wg-bridge, nginx :443 (не трогать) |
| Contabo | `185.225.233.150` | vpn-api :8091, xray :8443/:8446/**:443** |
| SSH | `~/.ssh/aladdin_server` | доступ |
| Тест TID | `493897224` | staging |

---

## 16. Инструкция для ML: включить все задачи в Cursor TODO

**Первое действие в новом чате:** вызвать инструмент `TodoWrite` с `merge: false` и списком всех **38 задач** ниже (id + content + status: pending). Отмечать `completed` по мере выполнения через `merge: true`. Не пропускать id — они синхронизированы с §8 и §17.

**Политика:** обновлять TODO при закрытии задачи; синхронизировать §7 чеклист.

Пример для ML:
```
TodoWrite merge=false, todos=[{id:"p0-wg-mtu", content:"...", status:"pending"}, ...]
```

---

## 17. ВСЕ ЗАДАЧИ — коротко и ясно (для людей и ML)

**Всего: 38 задач.** Ручная — только `p0-phone-drill` (последняя).

### P0 — сначала это (без этого VPN не заработает)

| ID | Что делаем | Зачем нам |
|----|------------|-----------|
| **p0-wg-mtu** | MTU 1280 на WG + MSS-clamp persistent | Чтобы ответы от сервера не терялись (upload есть, download 3 KB) |
| **p0-mtu-drill-script** | Авто `ping -M do` с MAIN, exit 0 | MTU-регрессия ловится без ручного drill |
| **p0-hop-ab** | Тест: трафик напрямую на Contabo, без WG-hop | Проверить: hop — главная причина поломки |
| **p0-phone-drill** | **Ручной** тест iPhone + МегаФон 4G (**последний шаг**) | Единственная ручная приёмка «VPN работает» |
| **p0-sni-ru** | SNI REALITY: yandex.ru / max.ru вместо microsoft.com | Лучше проходит DPI в РФ (как у ShadowNet) |
| **p0-fingerprint-profile** | 4G = firefox, WiFi = qq (не chrome везде) | Меньше блокировок на мобильной сети |
| **p0-port-443-lte** | 4G на Contabo :443 (не MAIN nginx), WiFi :8446 | Порт 443 реже режут; нет конфликта с сайтом |

### P1 — подписка и сервер (как у ShadowNet, проще)

| ID | Что делаем | Зачем нам |
|----|------------|-----------|
| **p1-wifi-direct** | WiFi → прямо на :8446, без hop | Проще путь = надёжнее дома |
| **p1-lte-bridge** | 4G → мост без hop (если A/B OK) | Убрать сломанную цепочку на LTE |
| **p1-dual-profiles** | Два профиля: «Авто WiFi ⚡» + «Авто 4G 📶» | Разные сети = разные настройки |
| **p1-sub-headers** | announce, срок, трафик в заголовках /sub/ | Подсказки и срок прямо в Happ |
| **p1-update-interval** | Обновление подписки каждые 2 часа | Быстрее подхват изменений сервера |
| **p1-split-tunnel** | **MVP:** suffix ~15 + блок max.ru + bittorrent/geoip/private | База split; 4 уровня §13.1, без копипаста 500 |
| **p1-split-tunnel-expanded** | Explicit ~80–120 **корневых** доменов (дедуп лога) | ~90% ShadowNet при ~130 правилах; не `sun9-47.userapi.com` поштучно |
| **p1-maxru-direct-lte** | Telegram/max.ru мимо VPN даже на 4G | Telegram не умирает в туннеле |
| **p1-routing-domain-strategy** | hybrid + IPIfNonMatch в routing | Правила split реально срабатывают |
| **p1-spiderx-reality** | spiderX в REALITY | Маскировка handshake (из логов ShadowNet) |
| **p1-dns-doh** | DNS через HTTPS 8.8.8.8 в подписке | Правильный резолв для routing |
| **p1-sniffing-inbound** | sniffing http/tls/quic в bundle inbounds | Routing по домену из TLS (как ShadowNet §10.2) |

**P1.1 (после drill):** +1 домен в split на тикет поддержки, не пакетом 500.

### P2 — автоматика

| ID | Что делаем | Зачем нам |
|----|------------|-----------|
| **p2-json-bundle** | Подписка JSON для Happ, не vless-строка | Нужно для routing, dns, observatory |
| **p2-observatory** | 2 outbounds **edge-443 + edge-8446**, один host, probe 30s | Failover без 2 VPS; как у работающего конкурента |
| **p2-fallback-xhttp** | Запасной профиль xhttp | Если vision не работает |
| **p2-hysteria** | Hysteria2 (опционально, P2) | Ещё один запасной транспорт UDP |

### P3 — защита (fresh launch)

| ID | Что делаем | Зачем нам |
|----|------------|-----------|
| **p3-hwid-gate** | Без HWID в Happ — заглушка, не ключ (**без grace period**) | Нельзя украсть подписку; legacy пользователей нет |
| **p3-bot-hwid-copy** | Текст в боте: включите HWID **до** импорта | Чтобы пользователь не видел заглушку |

### P4 — простота для пользователя

| ID | Что делаем | Зачем нам |
|----|------------|-----------|
| **p4-bot-ux-simple** | 3 шага: Happ → ссылка → Авто 4G | Как ShadowNet: просто |
| **p4-bot-status** | Сообщение в announce при поломках | Меньше паники и тикетов |
| **p4-rename-profiles** | Имена в боте = имена в Happ | Не путать пользователя |
| **p4-incident-announce-runbook** | Runbook: триггеры → announce → fix → снять | Связь obs-alert, статус, ротация ключей |

### P5 — масштаб (после стабилизации)

| ID | Что делаем | Зачем нам |
|----|------------|-----------|
| **p5-multi-edge** | 2–3 сервера/IP для observatory (расширение) | Failover при блокировке IP; не блокер P2 |
| **p5-ddos-guard** | WAF перед подпиской (опц.) | Защита от DDoS |
| **p5-reality-key-rotation** | Ротация SNI/keys: dual serverName 24–48h overlap | Без даунтайма при смене REALITY |

### Observability (метрики)

| ID | Что делаем | Зачем нам |
|----|------------|-----------|
| **obs-bytes-server** | bytes in/out per UUID в access log + скрипт отчёта | Видеть asymmetry без ручного drill |
| **obs-happ-report** | Шаблон отчёта из Happ tunnel.log | Стандартный сбор клиентских логов |
| **obs-download-alert** | download < 100 KB за сессию → auto `VPN_STATUS_ANNOUNCE` | Авто-флаг инцидента в Happ |

### Тесты и доки (только автоматически)

| ID | Что делаем | Зачем нам |
|----|------------|-----------|
| **tests-sub-p1** | pytest после p1-sub-headers (headers, dual profiles) | Регрессия на каждом деплое |
| **tests-sub** | Полный pytest: split, HWID, bundle, observatory tags | Перед phone drill |
| **docs-runbook** | Обновлять handoff после каждой фазы | Следующая ML понимает контекст |

---

## 18. Что НЕ делаем (напоминание)

- LAVA webhook — **нет**
- 46 профилей / 41 сервер — **нет**
- Чужие домены (`sprint-agency.pro`) — **нет**
- `ux_auto_mode=all` до зелёного phone drill — **нет**
- CDN xhttp как основной 4G — **нет**
- HWID grace period 2 недели — **нет** (fresh launch)
- Копипаст 500 split-tunnel строк — **нет** (suffix-first §13.1)
- Ручные тесты кроме финального phone drill — **нет**

---

## 19. Порядок для ML (одной строкой)

**P0 сервер+MTU script → P1 подписка/split/sniffing → tests-sub-p1 → P2 JSON+observatory(443+8446) → P3 HWID → obs-metrics → tests-sub → P4 бот+runbook → P5 rotation/edge → docs → p0-phone-drill (ручной) → ux_auto_mode=all.**

---

*Конец handoff. Главный файл для передачи другой ML: этот документ целиком. При изменениях обновлять §17 и Cursor TODO.*
