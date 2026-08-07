# VPN P0 — технический handoff для ML-системы (2026-06-28)

**Назначение:** единый документ для другой ML-системы / агента. Содержит всё, что выяснили на инциденте «Connected, 0 speed», что **уже починено на сервере**, что **ещё не сделано**, **как именно делать** каждый шаг, и **что сознательно отложено** (бот/UX).

**Аудитория:** ML-агент с SSH к Contabo + MAIN, доступом к репо `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/`.

**Связанные документы (читать по порядку):**

| # | Файл | Зачем |
|---|------|-------|
| 1 | `.cursor/VPN_RESILIENT_TASK_REGISTRY.md` | Cursor TODO SSOT, vpn-r101…r110 |
| 2 | `docs/VPN_RESILIENT_ARCHITECTURE_PLAN_2026.md` | Канон архитектуры v7 |
| 3 | `docs/VPN_ML_SYSTEM_HANDOFF.md` | Операционный handoff до UX-сессии |
| 4 | `docs/VPN_FULL_SESSION_HANDOFF_ML_2026-06-27.md` | Предыдущий инцидент (OVPN TCP, HitWave кнопки) |
| 5 | `../aladdin_shop_vpn_api/deploy/VPN82_MAIN_BRIDGE_RUNBOOK.md` | Мост MAIN :8444 |
| 6 | `../aladdin_shop_vpn_api/deploy/VPN04_WIREGUARD_RUNBOOK.md` | WireGuard на Contabo |
| 7 | `docs/VPN_PUBLIC_SURFACE_REGISTRY.md` | Публичные URL/порты |

---

## 0. Executive summary (60 секунд)

| Факт | Значение |
|------|----------|
| **Симптом** | iPhone: VPN «Connected», Transfer 1–6 KB, Safari/fast.com/2ip.ru не грузят |
| **Другой VPN на том же телефоне** | Работает → проблема в **нашем стеке**, не в SIM/операторе |
| **Сервер моста (Xray)** | **Работает**: E2E с MAIN ~1.5–3 MB/s после fix REALITY dest |
| **Главный блокер 4G (продукт)** | **HitWave iOS** не маршрутизирует браузер через туннель (DNS/Telegram да, HTTPS/QUIC сайтов — нет) |
| **Главный блокер WG** | Handshake OK, но **return path сломан**: `WG-OUT` есть, **`WG-RET ≈ 0`** |
| **Мост ≠ WireGuard** | Мост `:8444` (TCP/XHTTP) — **основной путь 4G РФ**. WG UDP `:51820` — **запасной**, не anti-DPI |
| **Политика сейчас** | **В боте ничего не менять и не тестировать** до закрытия P0-C…P0-H (техника) |

**Telegram test user:** `493897224` · UUID Xray `bed682e6-1726-419b-b45b-e8e891de7b7b` · WG IP `10.8.0.10` · последний внешний IP в логах `94.231.139.26`

---

## 1. Архитектура (Variant 3 — актуальная)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 4G РФ — ОСНОВНОЙ ПУТЬ (не WireGuard!)                                   │
│   iPhone → HitWave/Xray client → MAIN 149.154.65.180:8444 (RU bridge)   │
│          → VLESS hop → Contabo 185.225.233.150:8443 → Internet          │
├─────────────────────────────────────────────────────────────────────────┤
│ Wi‑Fi — прямой Xray                                                     │
│   iPhone → Contabo :8443 (VLESS+REALITY+XHTTP)                          │
├─────────────────────────────────────────────────────────────────────────┤
│ Fallback L3 — CDN                                                         │
│   #mobile-cdn → cdn.aladdin-ai.ru :8445                                   │
├─────────────────────────────────────────────────────────────────────────┤
│ Запасные (бот: «🔀 Запасные способы»)                                     │
│   OpenVPN UDP 1194 / TCP 443 · WireGuard UDP 51820 (→ план 443/udp)       │
└─────────────────────────────────────────────────────────────────────────┘
```

### Зачем делали RU-мост (vpn-r05…r09)

| Проблема | Решение моста |
|----------|----------------|
| Оператор/DPI режет **прямой** трафик на EU IP Contabo | Первый hop на **российский IP** MAIN |
| UDP WireGuard `:51820` часто блокируется на 4G | Xray **TCP :8444** маскируется под HTTPS/cloudflare (REALITY) |
| Пользователь видит «обычное» соединение к RF | SNI `www.cloudflare.com`, dest `cloudflare.com` |

**Вывод:** мост **не бесполезен** — серверная цепочка проверена. Блокер сейчас: **iOS-клиент** (HitWave) + отдельно **WG return path**.

### WG 443/udp — не замена моста

| | Мост `:8444` | WG `:443/udp` |
|---|--------------|---------------|
| Протокол | VLESS+REALITY+XHTTP | WireGuard UDP |
| Хост | MAIN (РФ) | Contabo (EU) |
| Роль | **Primary 4G** | **Backup** если WG 51820 режут |
| Статус | Сервер OK | ⏳ vpn-r105 |

---

## 2. Что уже починено на сервере (2026-06-28)

| ID | Проблема | Fix | Где |
|----|----------|-----|-----|
| vpn-r55 / vpn-96 | REALITY `dest: microsoft.com` — RSA cert, handshake fail | `dest` → `cloudflare.com` | Contabo :8443 + MAIN bridge :8444 |
| vpn-r56 / vpn-97 | OpenVPN return через UFW | `ovpn-fix-forwarding.sh`, tun0/tun1 FORWARD | Contabo |
| vpn-r57 / vpn-98 | HitWave не принимает `/sub/` URL | Кнопки `vless://` в боте (deploy `20260628-161604`) | Contabo bot |
| vpn-r58 / vpn-99 | xhttp `auto` ломал hop (`packet-up mode not allowed`) | **`stream-one`** на Contabo + bridge | MAIN + Contabo |
| vpn-r59 / vpn-100 | SNI рассинхрон в `/sub/` | `VPN_*_REALITY_SNI=cloudflare` | vpn-api env |

**Проверено SSH (28.06):** `xray-bridge.service` active, Contabo Xray :8443 active, bridge hop E2E ~1.5 MB/s с MAIN.

---

## 3. Root cause analysis — три протокола

### 3.1 Xray «Мобильный мост» (HitWave iOS) — **P0-B, vpn-r102**

**Симптом:** HitWave «Connected», fast.com 0, страницы не грузят.

**Доказательства (логи MAIN bridge, IP `94.231.139.26`):**

| Трафик | В логах bridge |
|--------|----------------|
| UDP DNS (53) | ✅ много |
| TCP Telegram | ✅ есть |
| TCP/HTTPS браузер (443) | ❌ почти нет |
| QUIC UDP :443 | ❌ почти нет |

**Серверный контроль:** curl через socks+xray с MAIN на bridge → **~3 MB/s** на Google connectivity check.

**Корневая причина:** **HitWave iOS не проксирует системный трафик браузера** (split tunnel / per-app). Это **не** баг nginx/Xray на сервере.

**Что НЕ поможет:** ещё раз выдать ту же `vless://` ссылку, смена SNI обратно на microsoft, откат `stream-one` → `auto` (ломает hop).

**Что нужно (vpn-r102):**

1. Найти iOS-клиент с **полным system VPN tunnel** и VLESS+REALITY+XHTTP (RU Store предпочтительно).
2. Кандидаты для исследования: v2RayTun (foreign Apple ID), собственный Network Extension, форк HitWave — **решение за продуктом**.
3. Критерий готовности: на 4G в логах bridge видны **`accepted tcp:443`** и **`accepted udp:443`** от IP пользователя при открытии Safari 2ip.ru.

**Файлы:** `telegram_stars_shop_bot/bot/services/vpn_user_links.py` (генерация vless), `/opt/xray-bridge/config.json` на MAIN.

---

### 3.2 WireGuard — **P0-C…F, vpn-r103…r106**

**Симптом:** WireGuard app «Connected», Transfer 1–6 KB, Safari не грузит.

**Конфиг из API корректен** (`POST /internal/v1/wg/conf`, HMAC):

```ini
[Interface]
Address = 10.8.0.10/32
MTU = 1280
DNS = 10.8.0.1

[Peer]
Endpoint = 185.225.233.150:51820
AllowedIPs = 0.0.0.0/0, ::/0    ← убрать ::/0 (vpn-r104)
PersistentKeepalive = 25
```

**Доказательства Contabo:**

| Наблюдение | Значение |
|------------|----------|
| Handshake | ✅ latest handshake обновляется |
| `WG-OUT` (iptables LOG) | ✅ пакеты уходят (QUIC UDP :443 к CDN) |
| `WG-RET` | ❌ **0** — ответы не возвращаются в туннель |
| dnsmasq | ✅ DNS запросы от `10.8.0.10` (yandex, fast.com) |
| `2ip.ru` в dnsmasq | ❌ **не появлялся** — браузер не дошёл до DNS |
| NAT counters `10.8.0.0/24` | ~128 B → ~2.5 KB после QUIC OUT, без устойчивого роста |

**Корневые причины (комбинация):**

1. **Return path / UFW / conntrack** — форвардинг ответов с `eth0` → `wg0` не работает стабильно.
2. **`::/0` в AllowedIPs** без IPv6 на wg0 — black-hole IPv6, браузеры предпочитают QUIC/AAAA.
3. **UDP 51820** на 4G РФ может резаться оператором (отдельно от return path).

**Частично применено на Contabo (проверить актуальность):**

- `wg-fix-forwarding.sh` — FORWARD, MASQUERADE, rp_filter, UFW before.rules, dnsmasq filter-AAAA
- MTU 1280 на wg0
- iptables LOG `WG-OUT` / `WG-RET`
- dnsmasq log-queries → `/var/log/dnsmasq-wg.log`

---

### 3.3 OpenVPN — запасной, **P1 retest**

**Симптом TCP 443:** `TCP_OVERFLOW`, `BYTES_OUT >> BYTES_IN` — TCP-over-TCP meltdown.

**Симптом UDP 1194:** handshake OK, через ~4 мин `ping-restart` — iOS routing loop / keepalive.

**Уже сделано:** UFW return tun0/tun1; в `.ovpn` push `route 185.225.233.150 net_gateway` (исключить endpoint из tunnel).

**Статус:** retest после UFW-fix; **не primary path**. На 4G предпочитать мост; OVPN UDP на Wi‑Fi.

**Файлы:** `deploy/scripts/openvpn-client-issue.sh`, `/opt/aladdin-shop-vpn-api/var/ovpn-profiles/493897224.ovpn`

---

## 4. Политика работ (важно для ML-агента)

### ❌ НЕ ДЕЛАТЬ сейчас

| Задача | Почему отложено |
|--------|-----------------|
| **p0-bridge-clarify / vpn-r101** — тексты в боте, инструкции «4G = мост» | Пользователь явно: **«в боте пока ничего не тестируем»** — сначала техника |
| **p0-bot-ux / vpn-r107** — одна кнопка WG, «обновление на сервере» | После P0-C…H + retest |
| Phone drill G4 (vpn-r110) | После рабочего iOS-клиента для моста |
| CDN orange / legal sign-off | P2, после drill |

### ✅ ДЕЛАТЬ сейчас (порядок)

```
1. vpn-r103  WG return path (Contabo)     ← без этого WG бесполезен
2. vpn-r104  WG .conf IPv4-only + deploy   ← internal.py + dnsmasq
3. vpn-r105  WG ListenPort 443/udp         ← обход блока 51820 (только WG!)
4. vpn-r106  wg_e2e_smoke.sh + cron        ← автоматическая регрессия
5. vpn-r108  REALITY E2E smoke моста       ← не TCP-open-only
6. vpn-r102  iOS client full tunnel        ← главный продуктовый путь 4G
7. vpn-r109  Retest iPhone 4G+Wi‑Fi        ← ground truth
8. vpn-r101  SSOT/бот/инструкции           ← ПОСЛЕ успешного retest
9. vpn-r107  Bot UX                          ← ПОСЛЕ retest
10. vpn-r110 G4 drill ×4 оператора          ← ПОСЛЕ vpn-r102
```

---

## 5. Как делать — пошаговые runbook

### 5.1 vpn-r103 — WG return path (P0-C)

**Хост:** Contabo `185.225.233.150` · SSH `aladdin-contabo`

**Скрипт в репо:** `aladdin_shop_vpn_api/deploy/scripts/wg-fix-forwarding.sh`

```bash
ssh root@185.225.233.150
cd /opt/aladdin-shop-vpn-api
git pull   # или rsync deploy/scripts/
bash deploy/scripts/wg-fix-forwarding.sh
```

**Дополнительно проверить/добавить если RET всё ещё 0:**

```bash
# LOG rules (диагностика)
iptables -I FORWARD 1 -i wg0 -j LOG --log-prefix "WG-OUT " --log-level 4
iptables -I FORWARD 1 -o wg0 -j LOG --log-prefix "WG-RET " --log-level 4

# UFW: RELATED,ESTABLISHED must be BEFORE reject
grep -A2 "RELATED,ESTABLISHED" /etc/ufw/before.rules

# Conntrack для UDP (QUIC)
sysctl net.netfilter.nf_conntrack_udp_timeout
sysctl net.netfilter.nf_conntrack_udp_timeout_stream

# Счётчики
iptables -L FORWARD -n -v | head -20
iptables -t nat -L POSTROUTING -n -v | grep 10.8.0
wg show wg0
dmesg | tail -50 | grep WG-
```

**Критерий PASS:**

- При активном Safari у пользователя: **`WG-RET > 0`**, Transfer в WireGuard app **> 100 KB**
- В `/var/log/dnsmasq-wg.log`: `query[A] 2ip.ru from 10.8.0.10`

**Env:** `VPN_WAN_IFACE=eth0`, `VPN_WG_INTERFACE=wg0`, `VPN_WG_SUBNET=10.8.0.0/24`

---

### 5.2 vpn-r104 — WG .conf IPv4-only (P0-D)

**Файл репо:** `aladdin_shop_vpn_api/aladdin_shop_vpn_api/routes/internal.py` (~строки 445–460)

**Изменение:**

```python
# Было:
"AllowedIPs = 0.0.0.0/0, ::/0\n"

# Должно быть:
"AllowedIPs = 0.0.0.0/0\n"
```

**DNS уже:** `DNS = 10.8.0.1` (dnsmasq с `filter-AAAA`).

**Пример dnsmasq:** `deploy/dnsmasq/aladdin-wg.conf.example`

**Деплой:**

```bash
# Contabo: обновить vpn-api код, restart
systemctl restart aladdin-shop-vpn-api
# Проверка для TID 493897224 через HMAC POST /internal/v1/wg/conf
```

**Не требует изменений бота** — конфиг генерируется API.

---

### 5.3 vpn-r105 — WG 443/udp (P0-E)

**Только WireGuard, мост `:8444` не трогать.**

```bash
# /etc/wireguard/wg0.conf — ListenPort = 443
# /opt/aladdin-shop-vpn-api/env:
VPN_WG_LISTEN_PORT=443
VPN_WG_ENDPOINT_IP=185.225.233.150

ufw allow 443/udp comment 'WireGuard backup port'
systemctl restart wg-quick@wg0
systemctl restart aladdin-shop-vpn-api
```

**Endpoint в `.conf`:** `185.225.233.150:443`

**Бот:** обновление Endpoint — **после retest**, в рамках vpn-r107 (не сейчас).

---

### 5.4 vpn-r106 — wg_e2e_smoke + cron (P0-F)

**Создать:** `aladdin_shop_vpn_api/deploy/scripts/wg_e2e_smoke.sh`

**Минимальные проверки:**

1. `wg show wg0` — interface up
2. Тестовый peer или последний активный peer — handshake < 180s
3. С Contabo: `dig @10.8.0.1 2ip.ru` через namespace или от IP тестового peer
4. Парсинг `dmesg`/kern.log: наличие `WG-OUT` **и** `WG-RET` за последние N минут
5. Exit 1 → Telegram ops alert (как в `vpn_external_smoke_cron.sh`)

**Cron:** добавить в Contabo crontab рядом с существующими vpn cron (см. `VPN_S4_OPS_RUNBOOK.md`).

---

### 5.5 vpn-r108 — REALITY E2E smoke моста (P0-H)

**Проблема:** `vpn_bridge_hop_smoke.py` проверяет **только TCP open**:

```python
# deploy/scripts/vpn_bridge_hop_smoke.py — строка 57:
print("PASS (TCP only; full hop needs live xray on bridge)")
```

**Нужно:** расширить или создать `vpn_bridge_reality_e2e_smoke.py`:

1. Поднять локальный socks inbound (xray)
2. Outbound: VLESS к `149.154.65.180:8444` с теми же параметрами, что в `vless://` пользователя
3. `curl --socks5 127.0.0.1:PORT https://www.google.com/generate_204` → 204
4. Измерить скорость > 100 Kbit/s
5. Интегрировать в `vpn_g2_gate.sh` / Contabo cron

**Шаблон конфига:** уже есть в сессии на MAIN `/tmp/xray-direct-test.json` — использовать как базу.

---

### 5.6 vpn-r102 — iOS client full tunnel (P0-B) — **главный продуктовый блокер**

**Цель:** один tap на 4G РФ → браузер через мост.

**Acceptance criteria:**

| # | Критерий |
|---|----------|
| 1 | Safari открывает 2ip.ru — IP ≠ операторский RF |
| 2 | fast.com > 1 Mbps на 4G |
| 3 | В `/var/log/xray-bridge/access.log` — TCP/UDP :443 от IP клиента |
| 4 | Приложение доступно пользователю без foreign Apple ID (RU Store — жёсткое требование продукта) |

**Ограничения продукта:**

- Hiddify / v2RayTun — **не подходят** для RU Store positioning
- HitWave — есть в RU Store, но **не full tunnel для браузера**

**Направления:**

1. Исследовать HitWave settings (global vs per-app) — быстрая проверка
2. Network Extension в ALADDIN iOS app (долгий путь)
3. Альтернативный RU Store клиент с VLESS+REALITY+XHTTP

---

### 5.7 vpn-r109 — Retest iPhone (P0-I)

**После** vpn-r103…108 и vpn-r102.

**Чеклист (4G, SIM пользователя):**

| # | Действие | Ожидание |
|---|----------|----------|
| 1 | HitWave/новый клиент + vless мост | 2ip.ru, fast.com |
| 2 | WireGuard новый `.conf` без `::/0` | Transfer > 100 KB |
| 3 | OpenVPN UDP `.ovpn` на Wi‑Fi | страницы грузят |
| 4 | SSH: логи bridge + dnsmasq + WG-RET | совпадают с UX |

---

### 5.8 vpn-r101 / vpn-r107 — бот и UX (**ПОСЛЕ техники**)

**vpn-r101:** обновить `legal_docs/vpn-instructions.md`, SSOT — 4G primary = мост, WG = запасной.

**vpn-r107:** упростить бот до одной кнопки WG после fix; до fix — не обещать «работает из коробки».

**Файлы бота:** `telegram_stars_shop_bot/bot/services/vpn_user_links.py`, handlers VPN funnel.

---

## 6. Серверы и пути (шпаргалка)

| Роль | IP | Сервисы |
|------|-----|---------|
| **MAIN (RU bridge)** | `149.154.65.180` | `xray-bridge.service` :8444, nginx :443, iOS backend :8002 |
| **Contabo (egress)** | `185.225.233.150` | Xray :8443, CDN origin :8445, vpn-api :8091, bot :8090, WG :51820, OVPN :1194/:443 |

| Путь на Contabo | Назначение |
|-----------------|------------|
| `/opt/aladdin-shop-vpn-api/env` | env vpn-api |
| `/opt/aladdin-shop-vpn-api/var/wg-keys/` | WG client keys |
| `/etc/wireguard/wg0.conf` | WG server |
| `/var/log/dnsmasq-wg.log` | DNS queries WG clients |
| `/opt/xray/config.json` | Contabo Xray |

| Путь на MAIN | Назначение |
|--------------|------------|
| `/opt/xray-bridge/config.json` | Bridge Xray |
| `/var/log/xray-bridge/access.log` | Bridge access log |

**SSH aliases (типично):** `aladdin-contabo`, `aladdin-server` (MAIN)

---

## 7. Покрытие плана — всё ли предусмотрено?

### ✅ Предусмотрено в P0/P1

| Область | Задачи |
|---------|--------|
| WG return path + IPv4 + 443/udp | vpn-r103…r105 |
| Авто-smoke WG + bridge REALITY E2E | vpn-r106, r108 |
| iOS full tunnel для моста | vpn-r102 |
| Retest + G4 drill | vpn-r109, r110 |
| SSOT/бот (отложено) | vpn-r101, r107 |

### ⏳ Уже в реестре, но не P0 блокеры

| Область | ID | Когда |
|---------|-----|-------|
| CDN DNS ф1/ф3 (orange CF) | vpn-r10, r26, r36 | После G4 drill |
| Legal sign-off RU bridge + CF | vpn-r13, r36 | Параллельно, не блокирует технику |
| OpenVPN retest UDP | P1 в аудите | После WG fix |
| Reserve EU IP | vpn-r35 / vpn-76 | Post-GA |
| Auto transport «один Connect» | vpn-r37 / vpn-78 | Post-GA |
| SNI rotation runbook | vpn-r39 | При инциденте DPI |
| Landing `/i/{code}` | vpn-r54 | Post-GA |

### ⚠️ Пробелы / риски (осознанные)

| Риск | Митигация |
|------|-----------|
| Нет RU Store клиента с full tunnel + VLESS REALITY XHTTP | vpn-r102 — может потребовать **свой Network Extension** |
| Smoke «PASS» при сломанном UX | vpn-r108 |
| Оператор режет Contabo IP целиком | мост MAIN; CDN ф3; vpn-76 reserve IP |
| HitWave обновление ломает routing | Pin версии + мониторинг bridge logs |

**Вывод:** для инцидента «0 speed» план **полный**. Единственный **продуктово-критичный** нез закрытый пункт — **vpn-r102 (iOS client)**, не сервер.

---

## 8. Cursor TODO ↔ vpn-r mapping

| Cursor TODO id | vpn-r | Статус | Делать сейчас? |
|----------------|-------|--------|----------------|
| p0-bridge-clarify | vpn-r101 | ⏳ | **Нет** — после retest |
| p0-xray-client | vpn-r102 | ⏳ | **Да** — primary 4G |
| p0-wg-return | vpn-r103 | ⏳ | **Да** — первый |
| p0-wg-conf | vpn-r104 | ⏳ | **Да** |
| p0-wg-443 | vpn-r105 | ⏳ | **Да** |
| p0-wg-smoke | vpn-r106 | ⏳ | **Да** |
| p0-bot-ux | vpn-r107 | ⏳ | **Нет** — после retest |
| p0-bridge-smoke | vpn-r108 | ⏳ | **Да** |
| p0-retest | vpn-r109 | ⏳ | После 103–108, 102 |
| p1-g4-drill | vpn-r110 | ⏳ | После 102 |

---

## 9. Команды быстрой диагностики

```bash
# Bridge — последние подключения пользователя
ssh aladdin-server 'grep "94.231.139.26" /var/log/xray-bridge/access.log | tail -20'

# Bridge — ratio tcp vs udp
ssh aladdin-server 'grep "accepted" /var/log/xray-bridge/access.log | tail -200 | grep -oE "accepted (tcp|udp)" | sort | uniq -c'

# WG peer
ssh aladdin-contabo 'wg show wg0; iptables -L FORWARD -n -v | head -15; dmesg | grep WG- | tail -10'

# DNS WG
ssh aladdin-contabo 'tail -30 /var/log/dnsmasq-wg.log'

# Xray Contabo health
ssh aladdin-contabo 'systemctl is-active xray aladdin-shop-vpn-api wg-quick@wg0'

# Bridge smoke (текущий — только TCP!)
python3 aladdin_shop_vpn_api/deploy/scripts/vpn_bridge_hop_smoke.py
```

---

## 10. Definition of Done (весь P0)

**Техника закрыта когда:**

- [ ] vpn-r103: WG-OUT **и** WG-RET в kern log; Transfer iPhone > 100 KB
- [ ] vpn-r104: `.conf` без `::/0`, `2ip.ru` в dnsmasq from 10.8.0.10
- [ ] vpn-r105: WG работает на `:443/udp` если `:51820` blocked
- [ ] vpn-r106: cron smoke PASS + alert на FAIL
- [ ] vpn-r108: REALITY E2E smoke PASS (не TCP-only)
- [ ] vpn-r102: iOS 4G Safari/fast.com через **мост**
- [ ] vpn-r109: retest checklist PASS на TID 493897224

**Продукт/UX закрыт когда (после техники):**

- [ ] vpn-r101: инструкции/SSOT обновлены
- [ ] vpn-r107: бот UX упрощён
- [ ] vpn-r110: G4 drill ×4 оператора

---

*Документ SSOT для ML-handoff инцидента 2026-06-28. При изменениях синхронизировать `.cursor/VPN_RESILIENT_TASK_REGISTRY.md` и `docs/VPN_TASKS_STATUS.md`.*
