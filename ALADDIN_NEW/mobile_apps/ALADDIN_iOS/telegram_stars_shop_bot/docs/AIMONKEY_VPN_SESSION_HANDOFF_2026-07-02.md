# AiMonkey VPN — полный handoff сессии 2026-07-01…02 (ML)

**Дата документа:** 2026-07-02  
**Сессия:** диагностика Happ iOS, P0–P1 в коде, деплой, MTU/MSS-fix, разбор логов пользователя (2 волны)  
**Читать первым:** этот файл → `AIMONKEY_VPN_DIAGNOSIS_HANDOFF_2026-07-01.md` → `VPN_PHONE_DRILL_RUNBOOK.md`

**Бот:** `@AiMonkeyStars_bot`  
**Тестовый TID:** `493897224`  
**SSH:** `~/.ssh/aladdin_server`  
**Happ iOS:** App Store id `6783623643`

---

## 0. START HERE (вердикт для ML)

### Одна фраза

> **Сервер и мост технически рабочие (smoke 10/10, E2E PASS), но у пользователя на МегаФон 4G VPN «не открывает ни одну страницу» из‑за комбинации: (A) data plane не несёт app TCP на сервер / REALITY handshake нестабилен; (B) когда туннель жив — MTU black hole на WG-hop рвёт ответы (upload ≫ download). Проблема не в «поднять сервер», а в цепочке телефон → REALITY → WG-hop → downlink.**

### Статус продукта на 2026-07-02

| Компонент | Статус |
|-----------|--------|
| Мост `:8444` tcp+vision | ✅ active, E2E PASS |
| WG hop `10.10.0.1↔10.10.0.2` | ✅ ping OK, ⚠️ MTU |
| `/sub/` для TID 493897224 | ✅ 1 профиль «Авто» → `149.154.65.180:8444` |
| P0/P1 код + деплой | ✅ |
| MSS-clamp WG | ✅ применён, ⚠️ 1400 bytes всё ещё loss |
| Phone drill / DoD «VPN 100%» | ❌ не пройден |
| Пользователь: страницы/приложения через VPN | ❌ |

### Что НЕ делать снова

- Переустанавливать xray «на всякий случай» — сервисы active, E2E OK
- Включать CDN xhttp как основной путь на 4G — сломан
- Судить по Happ proxy **upload** — смотреть **download** и серверный `contabo-hop`
- Включать Routing в Happ — «нет профилей маршрутизации» это норма
- `VPN_SUBSCRIBE_UX_AUTO_MODE=all` до phone drill

---

## 1. Архитектура (SSOT)

### Что видит пользователь

```
iPhone (Happ) → подписка /sub/ → профиль «Авто-подключение» → Connect
```

### Серверная цепочка (невидима)

```
Телефон (Happ, VLESS REALITY tcp+vision)
    ↓
MAIN 149.154.65.180:8444  «Мобильный мост»
    ↓  contabo-hop (xray outbound)
WG 10.10.0.1 ↔ 10.10.0.2  (wg-bridge, ~48 ms)
    ↓
Contabo 185.225.233.150:8446  (vision egress)
    ↓
Интернет
```

### Целевое состояние подписки (достигнуто 2026-07-01)

| # | Имя в Happ | Endpoint |
|---|------------|----------|
| 1 | **Авто-подключение** | `149.154.65.180:8444` (мост, tcp+vision) |

CDN (`cdn.aladdin-ai.ru:8445`, xhttp) **убран из ux-auto** — ломал 4G.

### Инфраструктура

| Сервер | IP | Роль |
|--------|-----|------|
| MAIN | `149.154.65.180` | xray-bridge :8444, nginx CDN relay :8445, wg-bridge |
| Contabo | `185.225.233.150` | vpn-api :8091, xray :8443/:8446/:8445 |

**Пути:** VPN API `/opt/aladdin-shop-vpn-api/`, bridge `/opt/xray-bridge/config.json`, DB `vpn.db`

---

## 2. Хронология работ в этой сессии

### 2.1 Анализ handoff 2026-07-01

- Подтверждён баг: «Авто» = Contabo `:8446` (зарубеж) вместо моста
- Согласован план P0–P2 + рекомендации (убрать дубль моста, деплой с ботом, починить smoke)

### 2.2 P0 — код `subscription_util.py`

**Было:** при `ux_auto` профиль «Авто» строился из `subscription_values_mobile()` → `:8446` Contabo.

**Стало:**
- при `ux_auto + bridge` → `subscription_values_bridge()` → `149.154.65.180:8444`
- отдельный профиль «Мобильный мост» **не дублируется**
- порядок: Авто (мост) → (CDN убран позже для ux-auto)

**Файл:** `aladdin_shop_vpn_api/aladdin_shop_vpn_api/subscription_util.py`

### 2.3 P1 — бот и smoke

- `vpn_connect_copy.py` — канон «один профиль Авто», убраны «Авто → Мост → CDN»
- Тесты: `test_egress_and_subscription.py`, `test_vpn_connect_copy_keys.py`, и др.
- `vpn_bridge_reality_e2e_smoke.py` → tcp+vision (был xhttp, ложный FAIL)

### 2.4 Деплой (2026-07-01)

- VPN API → Contabo, `aladdin-shop-vpn-api` active
- Проверка `/sub/` TID 493897224:
  ```
  Авто-подключение -> 149.154.65.180:8444
  Мобильный CDN -> cdn.aladdin-ai.ru:8445  (позже убран из ux-auto)
  ```
- Бот `deploy_prod.sh` release `20260701-220333` / `20260701-231042`

### 2.5 Диагностика «не работает после сброса Happ»

- Сервер: smoke 10/10, bridge E2E PASS, journal показывал hop + freedom
- Пользователь на **CDN** — TCP к `:8445` сломан (xhttp, retrans, Send-Q)
- Рекомендация: только «Авто», не CDN

### 2.6 MTU black hole WG-hop (критическая находка)

**Проверка на MAIN:**
```
ping 10.10.0.2  ≤1380 bytes → OK
ping 10.10.0.2  1400 bytes  → 100% loss
```

**Симптом:** uplink на сервер есть, downlink к телефону нет → upload 392 KB / download 3 KB в Happ.

**Фикс:** `apply_wg_hop_mss_clamp.sh` — TCPMSS clamp на `wg-bridge` (MAIN + Contabo).

**DNS hotfix на мосте:** UDP/TCP :53 → outbound `direct` (1.1.1.1 / 8.8.8.8), не через hop.

### 2.7 ux-auto: один профиль в `/sub/`

- CDN убран из подписки при `ux_auto` (xhttp на МегаФон нестабилен)
- Живая подписка: **340 bytes, 1 server**

### 2.8 Разбор логов пользователя — две волны

| Волна | Файлы | Дата теста |
|-------|-------|------------|
| 1 | `tunnel (4).log`, `access (3).log`, `subscriptions (3).log` | 01.07.2026 |
| 2 | `tunnel (5).log`, `access (4).log`, `subscriptions (4).log` | 02.07.2026 |

---

## 3. Что доказано фактами (сервер)

| Утверждение | Доказательство |
|-------------|----------------|
| VPN API жив | `systemctl active`, smoke 10/10 |
| Мост :8444 | `xray-bridge active`, ss LISTEN |
| WG hop | ping 10.10.0.2 0% loss ~48 ms |
| Ключи моста = подписка | pbk/sid совпадают с `bridge-meta.json` |
| E2E через мост | `vpn_bridge_reality_e2e_smoke.py` PASS |
| Hop + freedom (01.07) | journal `contabo-hop tunneling`, gstatic/google OPEN |
| MSS-clamp применён | iptables TCPMSS на wg-bridge |
| Подписка P0 | `149.154.65.180:8444` в `/sub/` |

---

## 4. Разбор логов — волна 1 (01.07.2026)

### 4.1 `subscriptions (3).log`

| Время | bytes | servers | Смысл |
|-------|-------|---------|-------|
| 13:26 | 1004 | 3 | Старая подписка (Авто=:8446 + мост + CDN) |
| 18:07 | 668 | 2 | P0: Авто=мост + CDN |
| 19:16 | 340 | 1 | Только «Авто» |

Также: `timedOut` при update в 19:09; дубль подписки `aladdin-ai.ru` в 18:34.

### 4.2 `tunnel (4).log` — ключевые события

| Время | Событие |
|-------|---------|
| 13:12 | MEMORY WARNING **47.91 MB** |
| 13:24 | `configurationDisabled` — iOS убил VPN |
| 18:12–19:24 | Code **-12** ×5, MEMORY 45–48 MB |
| 18:16–19:17 | `gstatic.com/generate_204` **timeout** / TLS handshake timeout |
| 19:15 | `configurationDisabled` |

**Вывод:** Happ iOS нестабилен (память, Code -12); встроенная проверка интернета **всегда FAIL**.

### 4.3 `access (3).log` (6296 строк, локальный Xray)

- Период: ~13:03–19:20 (метки UTC, +3ч = MSK)
- **2211+ строк** — Telegram `149.154.x`, Instagram в отдельные периоды
- **0 строк** — gstatic, google.com, 2ip.ru, fast.com
- `188.40.167.82` — **4 раза на :443** (не :80)
- `rejected` — **0**

**Сверка с сервером (19:17 MSK):** `188.40.167.82:443 accepted → contabo-hop` — запрос **дошёл**, страница у пользователя **не открылась** → проблема **return path / downlink**.

---

## 5. Разбор логов — волна 2 (02.07.2026) — чистый тест после фиксов

### 5.1 Показатели Happ от пользователя

```
proxy upload:   ~392 KB  (~392 KB/s пик)
proxy download: ~3 KB    (~1 KB/s)
Соотношение:    ~130:1 upload/download
```

**Интерпретация:** телефон шлёт много, получает почти ничего — классика **сломанного downlink** или **мёртвого data plane**.

### 5.2 `subscriptions (4).log`

- 07:25 и 09:47 — создание подписки: **340 bytes, 1 server** ✅
- 09:25 — обновление OK

### 5.3 `tunnel (5).log` (16 строк)

| Время MSK | Событие |
|-----------|---------|
| 09:48:16 | Старт VPN |
| 09:53:57 | Стоп `userInitiated` (переподключение) |
| 09:53:57 | Новый старт |
| 09:56:45 | Стоп `configurationDisabled` |

**Улучшение vs 01.07:** нет MEMORY WARNING, нет Code -12, нет gstatic timeout в файле.  
**Но:** страницы всё равно не открывались (по отчёту пользователя).

### 5.4 `access (4).log` (2658 строк, 09:48–09:56 UTC)

| Минута UTC | Строк |
|------------|-------|
| 09:49 | 835 |
| 09:54 | 893 |
| 09:55 | 766 |

**Топ хостов:** Telegram `149.154.x`, `91.108.x` (~83%), DNS `1.1.1.1`, Yandex.  
**Ноль:** gstatic, google, 2ip, 188.40, instagram, cdn.

### 5.5 Сверка с сервером (критично)

**Окно теста:** 09:48–09:56 UTC = **12:48–12:56 MSK**

| Метрика на мосте | 01.07 | **02.07** |
|------------------|-------|-----------|
| `contabo-hop` (рабочий VPN) | сотни | **0** |
| Telegram на сервере | есть | **0** |
| Только DNS → `direct` | мало | **50 строк — всё** |
| REALITY invalid | редко | **12:53:57 от 94.231.139.26** (момент рестарта) |

**Вывод волны 2:** локально Happ пишет `accepted [tun >> proxy]` тысячи раз, но на сервер **не приходит ни одного** TCP через `contabo-hop`. Data plane для приложений/сайтов **мёртв**. Только UDP DNS доходит до моста (и уходит в `direct`).

---

## 6. Сравнительная таблица гипотез

| # | Гипотеза | 01.07 | 02.07 | Вердикт |
|---|----------|-------|-------|---------|
| 1 | Сервер мёртв | ❌ smoke OK | ❌ smoke OK | **Опровергнута** |
| 2 | Неверная подписка (Авто=:8446) | ✅ была | ❌ 340B/1 профиль | **Исправлена** |
| 3 | CDN xhttp на 4G | ✅ ломал | ❌ убран | **Исправлена** |
| 4 | MTU WG-hop black hole | ✅ 1400 fail | ⚠️ 1380 ok | **Подтверждена** (когда туннель жив) |
| 5 | Return path / downlink | ✅ upload≫download | ✅ 392:3 KB | **Подтверждена** |
| 6 | Happ OOM / Code -12 | ✅ 47 MB | ❌ нет в новых | **Смягчилась** |
| 7 | Data plane не несёт TCP | частично | ✅ 0 hop | **Главная на 02.07** |
| 8 | Routing в Happ | — | не причина | **Опровергнута** |
| 9 | gstatic/сайты не в туннеле | ✅ 0 в access | ✅ 0 в access | **Подтверждена** |
| 10 | Telegram через наш сервер | ✅ на 01.07 | ❌ 0 на 02.07 | **Нестабильно** |

---

## 7. Истинная причина (два уровня)

### Уровень A — Data plane мёртв / нестабилен (доминирует 02.07)

- VLESS REALITY с телефона **не доставляет** прикладной TCP на мост (`contabo-hop = 0`)
- REALITY `invalid connection / failed to read client hello` при рестарте
- Локальный `access.log` **вводит в заблуждение** — `tun >> proxy` ≠ трафик на сервере
- Возможные механизмы:
  - Megafon 4G режет/портит REALITY+Vision на `:8444`
  - Happ iOS не держит outbound TCP vision
  - «Белый список» Telegram — трафик к `149.154.x` идёт **мимо** туннеля, VPN иконка при этом «вкл»

### Уровень B — Return path сломан (доминирует 01.07 когда hop жив)

- Запросы доходили до Contabo (`188.40:443`, gstatic, freedom OPEN)
- Ответы **не возвращались** на iPhone
- WG-hop: пакеты >~1380 bytes теряются (MTU black hole)
- MSS-clamp **частично** помог (1380 OK, 1400 fail)
- Happ: `gstatic/generate_204` timeout, download ≈ 0

### Схема обрыва

```
[Телефон Happ]
    │  ✅ локально accepted tun>>proxy (НЕ гарантия работы VPN)
    ▼
[REALITY :8444]  ⚠️ handshake invalid ИЛИ только DNS UDP
    ▼
[WG hop]         ❌ MTU black hole на больших ответах
    ▼
[Contabo]        ✅ freedom OPEN (когда hop жив)
    ▼
[Ответ → телефон] ❌ download ~3 KB
[Happ UI]         ❌ страницы не открываются
```

---

## 8. Анализ «6 шляп» (кратко)

| Шляпа | Вывод |
|-------|-------|
| 🤍 Факты | Сервер OK; подписка OK; пользователь 4G МегаФон; download≪upload |
| ❤️ Эмоции | Много переподключений, другие VPN — ожидаемо |
| 🖤 Риски | Megafon+REALITY; MTU; Happ iOS; ложные метрики upload |
| 💛 Плюсы | P0/P1 сделаны; E2E PASS; MSS-clamp; 1 профиль |
| 💚 Решения | MTU 1280; bypass WG-hop; Wi‑Fi тест; Shadowrocket A/B |
| 🔵 Процесс | DoD = contabo-hop на сервере + download >100KB в Happ |

---

## 9. Что сделано в коде и на сервере (чеклист)

| ID | Задача | Статус |
|----|--------|--------|
| P0 | Авто = мост `:8444` в `subscription_util.py` | ✅ |
| P0 | Мост первым, без дубля «Мобильный мост» | ✅ |
| P0 | Деплой VPN API | ✅ |
| P1 | Тексты бота `vpn_connect_copy.py` | ✅ |
| P1 | `vpn_bridge_reality_e2e_smoke.py` tcp+vision | ✅ |
| P1 | Тесты subscription + bot copy | ✅ |
| + | DNS direct на мосте (:53 → direct) | ✅ |
| + | MSS-clamp WG (`apply_wg_hop_mss_clamp.sh`) | ✅ |
| + | ux-auto: убрать CDN из `/sub/` | ✅ |
| P2 | CDN фаза 3 (CF orange :443) | ❌ после drill |
| P2 | Persistent iptables MSS (пережить reboot) | ❌ |
| P2 | WG MTU 1280 на обоих концах | ❌ |
| P2 | Bypass WG-hop (direct egress MAIN) — эксперимент | ❌ |
| — | Phone drill DoD | ❌ |
| — | `VPN_SUBSCRIBE_UX_AUTO_MODE=all` | ❌ не включать |

---

## 10. Рекомендации для ML-агента

### 10.1 Следующие серверные шаги (приоритет)

1. **WG MTU 1280** на MAIN и Contabo (`wg-bridge.conf`), рестарт `wg-quick@wg-bridge`
2. **Persistent MSS-clamp** (systemd unit или `iptables-save`)
3. **A/B: egress с MAIN без hop** — тестовый inbound на мосте с `freedom` direct (обход Contabo для диагностики)
4. **A/B: профиль без vision** на `:8443` xhttp для staging TID — только если Wi‑Fi тест покажет проблему Megafon+Vision

### 10.2 Процедура для пользователя

1. Перезагрузка iPhone
2. Удалить все подписки в Happ → добавить только `/sub/` из бота
3. **1 профиль** «Авто-подключение»
4. Memory limit **32 MB** (не 40 — всё равно было 47 MB)
5. **Не включать** Routing в Happ
6. iOS: Private Relay **ВЫКЛ**
7. Тесты:
   - **Wi‑Fi:** `https://2ip.ru` — отделить Megafon от Happ
   - **4G:** то же
   - **Shadowrocket** с той же `/sub/` — отделить Happ от протокола
8. Метрика успеха: **download в Happ > 100 KB**, не upload

### 10.3 DoD «VPN работает»

- [ ] На сервере за сессию есть строки `contabo-hop` + `freedom` к google/2ip/yandex
- [ ] Happ download > 100 KB за 5 мин
- [ ] `https://2ip.ru` открывается на 4G МегаФон ≥1 Мбит/с 5 мин
- [ ] Нет `configurationDisabled` / Code -12 за сессию

---

## 11. Команды быстрой диагностики

```bash
# Подписка тестового пользователя
ssh -i ~/.ssh/aladdin_server root@185.225.233.150 \
  'curl -s "http://127.0.0.1:8091/sub/9R8T1iCLEULlrGmdTw4IQm2dFXfE8zOx?plain=1"'

# Smoke
ssh root@185.225.233.150 'python3 /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_prod_smoke.py'
ssh root@185.225.233.150 'python3 /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_bridge_reality_e2e_smoke.py'

# Мост — последние сессии (искать contabo-hop vs direct)
ssh root@149.154.65.180 'tail -30 /var/log/xray-bridge/access.log'

# MTU WG
ssh root@149.154.65.180 'ping -c1 -M do -s 1380 10.10.0.2; ping -c1 -M do -s 1400 10.10.0.2'

# MSS rules
ssh root@149.154.65.180 'iptables -t mangle -L -n | grep TCPMSS'

# MSS clamp deploy
bash aladdin_shop_vpn_api/deploy/scripts/apply_wg_hop_mss_clamp.sh
```

---

## 12. Ключевые файлы репозитория

| Назначение | Путь |
|------------|------|
| Сборка `/sub/` | `aladdin_shop_vpn_api/aladdin_shop_vpn_api/subscription_util.py` |
| Тесты subscription | `aladdin_shop_vpn_api/tests/test_egress_and_subscription.py` |
| Bridge E2E smoke | `aladdin_shop_vpn_api/deploy/scripts/vpn_bridge_reality_e2e_smoke.py` |
| MSS clamp | `aladdin_shop_vpn_api/deploy/scripts/apply_wg_hop_mss_clamp.sh` |
| Тексты бота | `telegram_stars_shop_bot/bot/services/vpn_connect_copy.py` |
| Деплой бота | `telegram_stars_shop_bot/scripts/deploy_prod.sh` |
| Handoff 01.07 | `telegram_stars_shop_bot/docs/AIMONKEY_VPN_DIAGNOSIS_HANDOFF_2026-07-01.md` |
| Phone drill | `aladdin_shop_vpn_api/deploy/VPN_PHONE_DRILL_RUNBOOK.md` |
| **Этот документ** | `telegram_stars_shop_bot/docs/AIMONKEY_VPN_SESSION_HANDOFF_2026-07-02.md` |

---

## 13. Логи пользователя (пути для сверки)

### Волна 1 (01.07.2026)

- `~/Downloads/tunnel (4).log`
- `~/Downloads/access (3).log`
- `~/Downloads/subscriptions (3).log`

### Волна 2 (02.07.2026)

- `~/Downloads/tunnel (5).log`
- `~/Downloads/access (4).log`
- `~/Downloads/subscriptions (4).log`

**Важно:** метки в `access (*.log)` — **UTC** (+3ч = MSK). `tunnel` и `subscriptions` — локальное время iPhone (MSK).

---

## 14. IP пользователя в логах сервера

| IP | Период | Заметки |
|----|--------|---------|
| `178.178.210.38` | 01.07 | Megafon, hop работал |
| `94.231.139.26` | 01–02.07 | hop + invalid REALITY 02.07 12:53 |
| `178.176.85.51` | 02.07 | только DNS direct |

---

## 15. Резюме для следующей ML-системы

**Проблема не в отсутствии моста.** Инфраструктура прошла E2E. Продуктовые баги (Авто=:8446, CDN xhttp, тексты бота) **исправлены в коде и задеплоены**.

**Почему у пользователя не работает:**

1. **02.07:** data plane не доставляет app TCP на сервер (0 `contabo-hop` при 2658 local accepted); REALITY handshake fails.
2. **01.07:** когда hop жив — **MTU/downlink** рвёт ответы (upload 392 KB / download 3 KB; gstatic timeout; 188.40 дошёл до сервера — страница нет).
3. **Happ iOS** (01.07): OOM 47 MB, Code -12, configurationDisabled — усугубляет.
4. **Локальный access.log** не является доказательством работы VPN — всегда сверять с `/var/log/xray-bridge/access.log` и `contabo-hop`.

**Следующий агент:** MTU 1280 + persistent MSS → Wi‑Fi/Shadowrocket A/B → при необходимости bypass WG-hop → phone drill.

---

*Документ собран по сессии чата 2026-07-01…02. При расхождении с продом — перепроверить живую `/sub/` и journal, не полагаться только на этот файл.*
